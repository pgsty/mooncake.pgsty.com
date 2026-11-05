---
title: "Create Columnstore Table"
linkTitle: "Create Columnstore"
description: "Create a real-time USING mooncake columnstore mirror from a local or remote PostgreSQL table using CALL mooncake.create_table."
weight: 10
icon: fa-solid fa-table-columns
upstream_link: https://web.archive.org/web/20260124121942/https://docs.mooncake.dev/pg/reference/create-columnstore
aliases:
  - "/pg/reference/create-columnstore/"
  - "/reference/create-columnstore/"
---

In `pg_mooncake`, columnstore tables are created as **real-time mirrors** of existing PostgreSQL rowstore (heap or partitioned) tables using the `mooncake.create_table` procedure.

## Procedure Signature {#signature}

```sql
CALL mooncake.create_table(
    dst text,
    src text,
    src_uri text DEFAULT NULL,
    table_config json DEFAULT NULL
);
```

| Parameter | Type | Default | Description |
|:---|:---:|:---:|:---|
| `dst` | `text` | *(Required)* | Name of the destination columnstore mirror table to create (supports `schema.table`, defaults to `public` if unqualified). |
| `src` | `text` | *(Required)* | Name of the source PostgreSQL rowstore or partitioned table to replicate from (supports `schema.table`). |
| `src_uri` | `text` | `NULL` | Connection URI (`postgresql://user:pass@host:port/dbname`) of a remote PostgreSQL instance when replicating from an external database. When `NULL`, replicates from the current local database. |
| `table_config` | `json` | `NULL` | Optional JSON object configuring Moonlink storage and ingestion settings (such as `write_buffer_size` or initial data copy behavior). |
{.wide .expand}

> [!IMPORTANT] Parameter Name: `src_uri` (Not `source_uri`)
> Earlier upstream documentation contained a typo showing `source_uri => 'postgresql://...'`. The actual parameter name in `pg_mooncake`'s SQL definition (`src/functions.rs`) is **`src_uri`**. Always use `src_uri => 'postgresql://...'` when calling `mooncake.create_table` with named arguments.

## 1. Mirror a Table in the Same Database {#local}

When `src_uri` is omitted (or `NULL`), `pg_mooncake` replicates directly from `src` in the current database:

```sql
-- Create a source OLTP table
CREATE TABLE orders (
    order_id BIGSERIAL PRIMARY KEY,
    customer_id INT NOT NULL,
    amount NUMERIC(12, 2) NOT NULL,
    status TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create the columnstore mirror table
CALL mooncake.create_table('orders_analytics', 'orders');
```

What happens when `CALL mooncake.create_table('orders_analytics', 'orders')` runs:

1. `pg_mooncake` inspects the columns of `orders` and creates `CREATE TABLE orders_analytics (...) USING mooncake`.
2. If `orders` does not have a primary key, `pg_mooncake` runs `ALTER TABLE orders REPLICA IDENTITY FULL` (and in `v0.3.0`, automatically applies `REPLICA IDENTITY FULL` to all existing leaf partitions if `orders` is partitioned).
3. `moonlink` creates a logical replication slot (`pgoutput`), copies all existing rows from `orders`, and begins streaming ongoing `INSERT`, `UPDATE`, and `DELETE` changes in real time.

## 2. Mirror a Table from a Remote PostgreSQL Instance (`src_uri`) {#remote}

You can run `pg_mooncake` on a dedicated analytical PostgreSQL node and mirror tables from a remote production PostgreSQL database (including self-hosted PostgreSQL, AWS RDS, Aurora, Supabase, or Neon):

```sql
CALL mooncake.create_table(
    dst => 'orders_analytics',
    src => 'public.orders',
    src_uri => 'postgresql://replicator:secret@prod-db.example.com:5432/appdb'
);
```

Requirements on the remote source database:
- `wal_level = logical` must be enabled.
- The user in `src_uri` must have `REPLICATION` privileges and `SELECT` permission on `src`.
- If `src` has no primary key, `REPLICA IDENTITY FULL` must be set on `src`.

## 3. Mirror a Partitioned Table {#partitioned}

`mooncake.create_table` supports declarative PostgreSQL partitioned tables (`PARTITION BY RANGE`, `LIST`, or `HASH`). Specify the **root partitioned table** as `src`:

```sql
CREATE TABLE events (
    id BIGINT,
    event_type TEXT,
    payload JSONB,
    created_at TIMESTAMPTZ
) PARTITION BY RANGE (created_at);

CREATE TABLE events_2026_10 PARTITION OF events
    FOR VALUES FROM ('2026-10-01') TO ('2026-11-01');

CREATE TABLE events_2026_11 PARTITION OF events
    FOR VALUES FROM ('2026-11-01') TO ('2026-12-01');

-- Mirror the partitioned root table
CALL mooncake.create_table('events_analytics', 'events');
```

> [!WARNING] Adding New Partitions After `create_table`
> In `pg_mooncake 0.3.0`, `mooncake.create_table` automatically sets `REPLICA IDENTITY FULL` on all partitions that exist at the time the mirror is created. If you attach or create a **new** partition later (`CREATE TABLE events_2026_12 PARTITION OF events ...`) and the partitioned table does not have a primary key, run `ALTER TABLE events_2026_12 REPLICA IDENTITY FULL;` before executing `UPDATE` or `DELETE` statements on that partition.

## 4. Advanced `table_config` Options {#table-config}

You can pass a JSON object via `table_config` to customize Moonlink's per-table behavior (`TableConfig` in `moonlink_backend/src/table_config.rs`), including append-only optimization, background compaction flags, and custom filesystem / S3 / GCS storage backends for Iceberg data and WAL:

```sql
-- Example 1: Append-only table (skips primary-key delete hash index)
CALL mooncake.create_table(
    dst => 'events_analytics',
    src => 'events',
    src_uri => NULL,
    table_config => '{
        "mooncake": {
            "append_only": true,
            "skip_index_merge": false,
            "skip_data_compaction": false
        }
    }'::json
);

-- Example 2: Custom S3 storage backend for Iceberg warehouse and WAL
CALL mooncake.create_table(
    dst => 'orders_analytics',
    src => 'orders',
    src_uri => NULL,
    table_config => '{
        "iceberg": {
            "storage_config": {
                "s3": {
                    "region": "us-east-1",
                    "bucket": "my-mooncake-warehouse",
                    "access_key_id": "<AWS_ACCESS_KEY_ID>",
                    "secret_access_key": "<AWS_SECRET_ACCESS_KEY>"
                }
            }
        }
    }'::json
);
```

| JSON Path | Type | Default | Description |
|:---|:---:|:---:|:---|
| `mooncake.append_only` | `bool` | `false` (or `true` if no PK/replica identity) | When `true`, treats the table as append-only and skips building primary-key hash indexes. |
| `mooncake.skip_index_merge` | `bool` | `false` | When `true`, disables background Puffin hash-index LSM compaction. |
| `mooncake.skip_data_compaction` | `bool` | `false` | When `true`, disables background Parquet data file compaction. |
| `iceberg.storage_config` | `object` | `{"fs": {"root_directory": "$PGDATA/pg_mooncake"}}` | Storage backend (`fs`, `s3`, or `gcs`) for Apache Iceberg v2 metadata and Parquet data files. |
| `wal.storage_config` | `object` | `{"fs": {"root_directory": "$PGDATA/pg_mooncake"}}` | Storage backend (`fs`, `s3`, or `gcs`) for Moonlink's internal WAL segments. |
{.wide .expand}

## 5. Dropping a Columnstore Mirror Table {#drop}

To remove a columnstore mirror table and automatically clean up its Moonlink metadata and logical replication slot, simply run `DROP TABLE`:

```sql
DROP TABLE orders_analytics;
```
