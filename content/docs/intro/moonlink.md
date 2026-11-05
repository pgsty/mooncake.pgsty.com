---
title: "Moonlink Ingestion Engine"
linkTitle: "Moonlink Engine"
description: "Deep dive into Moonlink (v0.0.1): real-time CDC ingestion, Arrow buffers, Roaring deletion vectors, LSN snapshot barriers, and standalone HTTP/RPC deployment."
weight: 20
icon: fa-solid fa-arrows-rotate
upstream_source: moonlink
upstream_link: https://github.com/Mooncake-Labs/moonlink
aliases:
  - "/moonlink/intro/"
  - "/intro/moonlink/"
  - "/moonlink/"
---

**Moonlink** ([`pgsty/moonlink`](https://github.com/pgsty/moonlink), current release **`v0.0.1`**) is a Rust library and standalone service designed to write and maintain real-time **Apache Iceberg v2** and **Delta Lake** tables for operational systems and event streams without Apache Spark or Kafka.

Inside [`pg_mooncake`](/docs/intro/), Moonlink runs as an embedded PostgreSQL background worker (`mooncake_bgworker`) communicating over a local Unix domain socket (`$PGDATA/pg_mooncake/moonlink.sock`). It can also be compiled and deployed as a standalone HTTP REST and gRPC ingestion server (`moonlink_service`).

> [!NOTE] Licensing (`BSL-1.1` with `pg_mooncake` Linking Exception)
> The core `moonlink` server engine is licensed under **BSL-1.1** (converting automatically to **Apache-2.0** on `2029-05-05`) with an explicit **`PG_MOONCAKE LINKING & DISTRIBUTION EXCEPTION`** granting unrestricted linking, modification, and redistribution when embedded in or distributed as part of `pg_mooncake`. Its protocol and client crates (`moonlink_rpc`, `moonlink_proto`, `moonlink_error`, `moonlink_table_metadata`) are licensed under **MIT**. See [Licensing](/docs/about/license/) for full text.

## Core Design Principles {#design}

Traditional data lake writers face a fundamental trade-off between **data freshness** and **query performance**: flushing every row mutation immediately creates thousands of tiny Parquet files, whereas batching writes for 5–15 minutes introduces unacceptable latency for operational analytics.

Moonlink resolves this trade-off with a multi-tiered storage architecture:

1. **In-Memory Apache Arrow Write Buffer**: Incoming `INSERT` and `UPDATE` rows are appended to an active in-memory Arrow `RecordBatch` buffer (`write_buffer_size`, default `32 MB`). Readers (`duckdb_mooncake`) can scan this buffer directly with zero-copy Arrow integration before it is ever flushed to Parquet.
2. **Equality & Position Deletion Vectors (Roaring Bitmaps)**: Instead of rewriting Parquet files on every `UPDATE` or `DELETE`, Moonlink indexes primary/replica keys via a B-tree index (`moonlink_btree`) and marks deleted row offsets in compressed **Roaring Bitmaps**.
3. **LSN-Tracked Commits & Non-Blocking Snapshots**: Every mutation ingested from PostgreSQL WAL is tagged with its commit `lsn`. Readers pass their target LSN to `scan_table_begin`, waiting only if the replication stream has not yet reached that LSN.
4. **Asynchronous Compaction & Iceberg v2 Metadata**: Background compaction merges flushed Parquet segments, reconciles deletion vectors, and writes standard **Apache Iceberg v2** `metadata.json` and Avro manifest files to local disk or S3/R2 object storage.

## What's Fixed in `moonlink v0.0.1` {#v001-fixes}

In PGSTY's **`moonlink v0.0.1`** (`b298ef7444890e3c8af5544e350232518bcfd8e5`) release:

- **Non-blocking `create_snapshot(lsn)` under unrelated WAL progress**: Previously, calling `CALL mooncake.create_snapshot('table')` when the PostgreSQL database WAL had advanced due to writes on *unrelated* tables caused Moonlink's snapshot waiter to hang indefinitely waiting for a table-level commit at the latest database LSN. In `v0.0.1`, replication progress notifications advance the table's safe LSN watermark and flush older committed data immediately, even when no new commits arrive for that specific table.
- **58/58 Table Handler Unit Tests**: Verified across append, update, delete, rollback, compaction, and snapshot barrier scenarios on Rocky Linux 10 (`aarch64`) and Ubuntu 24.04 (`aarch64`).
- **Security Dependency Audit Updates**: Patched `bytes`, `crossbeam-epoch`, `h2`, `lz4_flex`, `quinn-proto`, `rustls`, `rustls-webpki`, `webpki-roots`, `time`, `zstd`, `anyhow`, `event-listener`, `lru` (`0.18.5`), `memmap2`, `rand`, `tokio` (`1.51.6`), `aws-lc-rs`, and `serial_test`.

## Standalone Deployment (`moonlink_service`) {#standalone}

While `pg_mooncake` embeds Moonlink automatically, you can also run `moonlink_service` as a standalone ingestion server for direct HTTP REST or gRPC streaming into Iceberg tables.

### Building `moonlink_service` from Source {#build}

```bash
git clone https://github.com/pgsty/moonlink.git
cd moonlink
cargo build --release -p moonlink_service
./target/release/moonlink_service
```

### Standalone REST API Workflow {#rest-api}

The standalone service listens on port `3030` by default and exposes JSON endpoints for table creation, row ingestion, and Iceberg snapshot generation:

```python
import json
import requests

BASE_URL = "http://localhost:3030"

# 1. Create a Moonlink Iceberg table
create_payload = {
    "database": "default",
    "table": "events",
    "schema": {
        "fields": [
            {"name": "id", "data_type": "Int64", "nullable": False},
            {"name": "service", "data_type": "Utf8", "nullable": False},
            {"name": "latency_ms", "data_type": "Float64", "nullable": True},
        ],
        "primary_key": ["id"],
    },
    "table_config": {
        "write_buffer_size": 33554432,
        "iceberg_warehouse_location": "/tmp/moonlink_warehouse",
    },
}
resp = requests.post(f"{BASE_URL}/tables", json=create_payload)
resp.raise_for_status()

# 2. Insert or upsert rows in real time
insert_payload = {
    "database": "default",
    "table": "events",
    "row": {"id": 1, "service": "checkout", "latency_ms": 12.4},
}
resp = requests.post(f"{BASE_URL}/insert", json=insert_payload)
resp.raise_for_status()

# 3. Trigger an Iceberg v2 snapshot flush
snapshot_payload = {
    "database": "default",
    "table": "events",
    "lsn": resp.json().get("lsn", 1),
}
requests.post(f"{BASE_URL}/snapshot", json=snapshot_payload).raise_for_status()
```

### Querying the Iceberg Snapshot from DuckDB {#query-iceberg}

Once a snapshot is created, any Iceberg-compatible engine (DuckDB, Spark, Trino, Snowflake, PyIceberg) can read the table directly:

```sql
INSTALL iceberg;
LOAD iceberg;

SELECT service, COUNT(*), AVG(latency_ms)
FROM iceberg_scan('/tmp/moonlink_warehouse/default/events/metadata/v2.metadata.json')
GROUP BY service;
```
