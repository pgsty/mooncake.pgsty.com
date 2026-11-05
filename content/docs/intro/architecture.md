---
title: "Architecture"
linkTitle: "Architecture"
description: "How pg_mooncake (v0.3.0), pg_duckdb (1.2.0), duckdb_mooncake (v0.0.2), and moonlink (v0.0.1) work together to deliver real-time columnar analytics in PostgreSQL."
weight: 10
icon: fa-solid fa-sitemap
upstream_link: https://web.archive.org/web/20260124104610/https://docs.mooncake.dev/pg/intro/architecture
aliases:
  - "/pg/intro/architecture/"
  - "/intro/architecture/"
---

`pg_mooncake` (`v0.3.0`) combines three specialized components inside a single PostgreSQL deployment:

1. **[`pg_duckdb`](https://github.com/duckdb/pg_duckdb) (`v1.2.0`)**: Embeds the **DuckDB `v2.0.0`** vectorized analytical execution engine inside PostgreSQL and routes queries against non-heap table access methods.
2. **[`moonlink`](/docs/intro/moonlink/) (`v0.0.1`)**: A Rust library and background worker embedded inside `pg_mooncake` that ingests PostgreSQL logical replication streams, maintains an in-memory **Apache Arrow** write buffer and **Roaring Bitmap** deletion vectors, flushes **Parquet** files, and emits **Apache Iceberg v2** table metadata.
3. **[`duckdb_mooncake`](/docs/intro/duckdb-mooncake/) (`v0.0.2`)**: A DuckDB 2.0 C++/Rust storage extension loaded automatically by `pg_mooncake` from a local extension repository (`mooncake.extension_repository`). It connects to Moonlink over a local Unix domain socket RPC (`pg_mooncake/moonlink.sock`) to read consistent snapshots across both flushed Parquet files and buffered Arrow batches.

Together, they expose a native PostgreSQL Table Access Method (`USING mooncake`) managed through `CALL mooncake.create_table(dst, src)`.

![pg_mooncake v0.2 / v0.3 Architecture Diagram](/img/mooncake/v0.2architecture.jpg)

## Component Pinning in `pg_mooncake 0.3.0` {#components}

| Component | Version / Tag | Pinned Commit (`versions.json`) | Role |
|:---|:---:|:---|:---|
| **`pg_mooncake`** | `v0.3.0` | `1a9cbfd65be9a6486d020120acb49ef0c6800d68` | PostgreSQL extension (`pgrx 0.19.3`), SQL procedures, `USING mooncake` TAM, and background worker launcher |
| **`moonlink`** | `v0.0.1` | `b298ef7444890e3c8af5544e350232518bcfd8e5` | Embedded Rust CDC ingestion engine, Arrow buffer, deletion vectors, and Iceberg v2 snapshot writer |
| **`duckdb_mooncake`** | `v0.0.2` | `49765a369ad88986916ce53c969ed2ce4ba66fac` | DuckDB 2.0 extension (`mooncake.duckdb_extension`) scanning Moonlink tables and Parquet statistics |
| **`pg_duckdb`** | `v1.2.0` | `8756099e267c47f0b86c24de4cf995327f1f4279` | Embedded DuckDB execution bridge inside PostgreSQL (enforced by SQL installation guard) |
| **`duckdb`** | `v2.0.0` | `d54cbbe3df17e8e5ce68312f483b4155836112aa` | Underlying C++ vectorized analytical query engine |
{.wide .expand}

## Write Path {#write-path}

In `pg_mooncake`, you never write directly to the `USING mooncake` columnstore table. Instead, you write to your regular PostgreSQL rowstore (heap or partitioned) table:

1. **Initial Table Copy & Slot Creation**: When you execute `CALL mooncake.create_table('dst', 'src')`, `pg_mooncake`:
   - Inspects the source table's schema and creates the destination table with `USING mooncake`.
   - Sets `REPLICA IDENTITY FULL` on the source table (and, in `v0.3.0`, automatically on all existing leaf partitions if the source is a partitioned table) if the source table does not have a primary key.
   - Creates a PostgreSQL publication and logical replication slot (`pgoutput`), copies existing rows from `src` into Moonlink, and records the starting WAL LSN.
2. **Continuous Logical Replication**: A background worker (`mooncake_bgworker`) continuously consumes WAL changes (`INSERT`, `UPDATE`, `DELETE`) from the logical replication slot and streams them to `moonlink`.
3. **Buffered Arrow + Deletion Vectors**:
   - **Inserts** are appended to an in-memory **Apache Arrow** write buffer (`write_buffer_size`, default `32 MB`), making new rows immediately visible to analytical queries without writing a tiny Parquet file per transaction.
   - **Deletes** record the target row's location in an in-memory/on-disk **Roaring Bitmap deletion vector**, avoiding expensive full-file Parquet rewrites on every `DELETE`.
   - **Updates** are processed atomically as a deletion vector entry for the old tuple plus an append to the Arrow buffer for the new tuple.
4. **Background Compaction & Parquet Flush**: Once the write buffer reaches its threshold or when `CALL mooncake.create_snapshot('dst')` / `CALL mooncake.optimize_table('dst', 'full')` is invoked, Moonlink flushes the buffered Arrow records into compressed Parquet files and updates the Apache Iceberg v2 metadata.

## Read Path {#read-path}

When you run a `SELECT` query that references a `USING mooncake` columnstore table:

1. **Query Routing via `pg_duckdb`**: PostgreSQL's planner recognizes the `mooncake` table access method (registered with `pg_duckdb` via `RegisterDuckdbTableAm("mooncake")`) and hands the query plan over to the embedded DuckDB 2.0 engine.
2. **Automatic Extension Attachment**: On the first scan in a backend session, `pg_mooncake` configures `SET extension_directory = '<mooncake.extension_repository>'`, loads the `mooncake` DuckDB extension (`duckdb_mooncake v0.0.2`), and executes `ATTACH '' AS mooncake (TYPE mooncake, METADATA '<pgdata>/pg_mooncake')`.
3. **LSN Synchronization Barrier**: Before scanning a table, `duckdb_mooncake` queries PostgreSQL's current WAL write/insert LSN and instructs Moonlink via RPC (`scan_table_begin`) to wait until the replication stream has ingested up to that LSN—guaranteeing **read-your-own-writes transactional consistency**.
4. **Hybrid Arrow + Parquet Scan with Segment Elimination**:
   - Moonlink returns the list of active Parquet data files, active deletion vectors, and a pointer to the current in-memory Arrow buffer.
   - `duckdb_mooncake` reads Parquet column min/max statistics through DuckDB 2.0's exported multi-file reader interface to skip irrelevant files and row groups (**segment elimination**), applies deletion vectors, and streams the combined results back to PostgreSQL.

## Storage Layout {#storage}

By default (`mooncake.default_bucket = ''`), Moonlink stores table metadata, deletion vectors, and Parquet data files under your PostgreSQL data directory at `$PGDATA/pg_mooncake/`.

When `mooncake.default_bucket` is set to an `s3://` or `r2://` URI (with credentials configured in `duckdb.secrets`), Moonlink writes Parquet data files and **Apache Iceberg v2** metadata (`metadata/*.metadata.json` and Avro manifest lists) directly to object storage. You can inspect the active warehouse path and LSN progress for every mirrored table at any time with:

```sql
SELECT * FROM mooncake.list_tables();
```
