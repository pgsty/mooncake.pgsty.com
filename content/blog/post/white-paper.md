---
title: "Mooncake: a real-time storage engine for Apache Iceberg"
date: 2025-08-11
description: "Technical whitepaper on Mooncake and Moonlink: Arrow write buffers, positional deletion vectors, conflict-free compaction remapping, Puffin indexes, and NVMe caching for real-time Apache Iceberg."
author: "[Mooncake Labs Team](https://github.com/Mooncake-Labs)"
authors: ["mooncake-labs", "zhou-sun", "cheng-chen", "pranav-aurora"]
tags:
  - "whitepaper"
  - "moonlink"
  - "iceberg"
  - "architecture"
  - "pg_mooncake"
upstream_link: "https://www.mooncake.dev/whitepaper"
upstream_copyright: "© 2025 Mooncake Labs Inc."
aliases:
  - "/whitepaper/"
  - "/blog/white-paper/"
  - "/blog/white_paper/"
images: ["/blog/covers/white-paper.svg"]
---

This technical overview assumes familiarity with [Apache Iceberg](https://iceberg.apache.org/), an open table format for analytical datasets. Iceberg is part of the general "Lakehouse" movement, where users:

1. Store large datasets using open file formats (Parquet + Metadata) in Object Storage
2. Query them directly by engines like Spark, Trino, Flink, and DuckDB using SQL
3. Get the benefits of 'database features' like schema evolution & time-travel
4. Scale practically infinitely, and aren't locked into a vendor

Iceberg was built for slow-changing data + batch analytics & processing. That world is pretty clear and only improving with engines getting better at reading open formats.

Real-time workloads (user-facing analytics, stream-processing) typically require a separate purpose-built system altogether—e.g., ClickHouse, Druid, SingleStore—so users maintain two pipelines and manually move data between them.

What if we brought the openness and flexibility of the Lakehouse to real-time? There are two key requirements:

1. Don't sacrifice any part of the Lakehouse: the integrations, the ecosystem.
2. Bring real-time data + fast queries, without destroying Iceberg performance / state.

## Introduction

Mooncake is a real-time storage engine built on Iceberg for real-time workloads. It brings high-rate ingest, fast queries, and indexing into Iceberg without giving up the openness & flexibility of the Lakehouse:

1. **Fast ingest:** streaming writes with sub-second mirroring from relational databases.
2. **Fast queries:** continuous table optimization with smart caching.
3. **Indexing:** low-latency search and primary key lookups.

Mooncake's architecture, indexing layer, and write-aware optimizations turn Iceberg into a platform capable of powering user-facing analytics, search, serving, and HTAP workloads—things that previously required purpose-built real-time systems.

## Architecture

```
                         DuckDB
                         Spark
                       Snowflake
                    (Iceberg-rest)
                    ▲              ▲
                    │              │
                    │              │
             ┌──────┴───moonlink───┴───────┐
             │  ┌───────────────────────┐  │
             │  │                       │  │
Postgres ───►│  │┌ ─ ─ ─ ─ ┐ ┌ ─ ─ ─ ─ ┐│  │
             │  │                       │  │
Kafka    ───►│  ││  index  │ │  cache  ││  │
             │  │                       │  │
Events   ───►│  │└ ─ ─ ─ ─ ┘ └ ─ ─ ─ ─ ┘│  │
             │  │                  nvme │  │
             │  └───────────────────────┘  │
             └─────────┬─────────┬─────────┘
                       ▼         ▼
                 ┌───────Iceberg───────┐
                 │         s3          │
                 │┌───────┐ ┌─────────┐│
                 ││       │ │         ││
                 ││ index │ │ parquet ││
                 ││       │ │         ││
                 │└───────┘ └─────────┘│
                 │                     │
                 └─────────────────────┘
```

The core of Mooncake is [`moonlink`](/docs/intro/moonlink/), a Rust library designed for real-time CDC and streaming into Iceberg.

Moonlink augments an Iceberg table with an in-memory Arrow buffer, a positional delete log, and hybrid in-memory / NVMe-resident / object-store indexes to absorb high-frequency updates. Execution engines read the union of buffer + Iceberg for a fully up-to-date view—without waiting for Iceberg metadata commits.

### Inserts

- Rows are written to an Arrow buffer; data is efficiently flushed to Parquet when enough rows have accumulated.
- In-memory indices are built during insertion and flushed as an object-store-native version on Parquet flush.

### Deletions

- Moonlink maintains primary key indexes for all rows.
- Deletions update the positional deletion log using these indexes.
- Periodically, deletion logs are converted to Iceberg deletion vectors (Puffin).

### Reads

- Moonlink writes Iceberg for any engine to read.
- Moonlink exposes a union-read interface ([`duckdb_mooncake`](/docs/intro/duckdb-mooncake/)) that combines its in-memory state with Iceberg files so engines can access the most current table state.
- Mooncake exposes an index-read interface to execute index lookup queries for key lookup and search.

## Core Technology Deep Dive

### 3.1 Write-aware table optimization

**Union-read of up-to-date version**
Iceberg forces a trade-off between freshness and write-amplification: to get fresher data, users write snapshots very frequently, creating too many small Parquet and metadata/manifest files. Compactions add even more snapshots, and the spec makes it hard to prune intermediate versions and recycle unused files.

Mooncake solves this by writing Iceberg metadata periodically, while exposing an Iceberg-compatible API to "read the latest version" before it's committed—generating up-to-date metadata and data files on the fly. Result: sub-second freshness for reading the table.

**Index + Deletion Vector for update/delete**
Iceberg wasn't optimized for high-throughput update/delete (CDC) or upserts (streams). Prior approaches batch into expensive global merges or rely on equality deletes (hurting read performance and causing small files).
Moonlink maintains an index that covers both the in-memory buffer and Iceberg to locate positions of deleted records, then applies deletions via Iceberg deletion vectors.

**Gracefully handling write vs. compaction conflicts**
Open table formats handle conflicting commits naively—streaming updates often collide with background maintenance (sort/compaction). Mooncake builds mapping structures from old files to new files during maintenance and remaps in-flight updates/deletes, so no transaction needs to fail.

### 3.2 Iceberg-native indexing

**Index storage**

- Index file metadata stored as Iceberg Puffin files.
- Index files stored with or near the table's data.
- Each index file covers one or more data files.
- Background merges form an LSM of indexes.

**Query interface & integration**

- Indexes point to data via `(file_id, offset)`—no extra primary key needed.
- APIs:
  - `Build(DataFile) -> IndexFile`
  - `Merge([IndexFiles]) -> IndexFile(s)`
  - `Query(IndexFile, query) -> [(DataFile, offset, [optional payload])]`

**Index implementations**

- **Bucket hash table:** high-cardinality hash index used to turn raw deletes into positional deletes. Immutable, hash-ordered SSTable-like format mapping 64-bit hashes to storage locations; partitions via high-order bits; space-efficient, cache-friendly, fast streaming merges.
- **Bucket hash table + inverted index:** low-cardinality hash index powering GIN/full-text search (inverted index per data file; mergeable bucket table to inverted-index offsets).
- **Vector index:** built per data file and merged across files; clustered/IVF variants for object-store-native performance.

### 3.3 Managed buffer and cache

Mooncake is object-store-native with efficient use of local memory & NVMe (similar philosophy to SlateDB, Turbopuffer, and WarpStream).

**Object-store-native WAL**
The object store is the source of truth. Mooncake nodes are mostly stateless: they write WALs directly to the object store and use them on recovery—no multi-replica Raft/Paxos clusters. You can view Mooncake as a database that writes its snapshots as Iceberg snapshots.

**Streaming writes to Arrow buffer**
For low-latency writes, the latest data is buffered before Parquet. An in-memory Arrow buffer lets us append rows and modify fields, flush directly to Parquet/Iceberg, and also send uncompressed Arrow/Parquet over the network for real-time engines. Combining buffer + index, Mooncake can handle ~1M updates on a single machine.

**Read & write-through cache**
Caching matters for both performance and S3 cost. Fresh Parquet, deletion vectors, and indexes land on NVMe before async upload to the object store, yielding `<5 ms` local writes and reads.

## Deployment & Solutions

### 4.1 [`pg_mooncake`](/docs/intro/)

HTAP, real-time analytics, and sync to Iceberg, all inside Postgres. A Postgres extension that runs Moonlink in a background worker and embeds DuckDB as the execution engine (MIT licensed).

[`CALL mooncake.create_table('T_mooncake', 'T_heap')`](/docs/reference/create-columnstore/) creates a columnar version of a Postgres table that stays in sync with the heap with sub-second delay and strong consistency.

### 4.2 [Stand-alone `moonlink`](/docs/intro/moonlink/)

Fast & simple replication from Postgres to Iceberg. Stateless Rust engine that reads logical replication or HTTP/RPC ingestion and writes directly to Iceberg, keeping query-ready tables with sub-second latency and minimal overhead.

**TL;DR:** Mooncake enables workloads that traditionally require specialized databases (like Elasticsearch for search, ClickHouse for analytics, or vector databases for AI) to run directly on your Iceberg data lake—unifying real-time and analytical workloads on a single storage layer.
