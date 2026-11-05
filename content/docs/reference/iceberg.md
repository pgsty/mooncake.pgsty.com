---
title: "Apache Iceberg v2 & Object Storage Configuration"
linkTitle: "Iceberg & Cloud Storage"
description: "Configure AWS S3, Cloudflare R2, or local storage for pg_mooncake, create Apache Iceberg v2 snapshots with mooncake.create_snapshot, and query from external engines."
weight: 30
icon: fa-solid fa-cloud
upstream_link: https://web.archive.org/web/20251207105746/https://docs.mooncake.dev/pg/reference/iceberg
aliases:
  - "/pg/reference/iceberg/"
  - "/reference/iceberg/"
---

Every columnstore mirror table in `pg_mooncake` (`v0.3.0`) is backed by [`moonlink`](/docs/intro/moonlink/), which writes data as standard **Parquet** files and maintains **Apache Iceberg v2** table metadata.

By default, Moonlink writes files to the local filesystem under `$PGDATA/pg_mooncake/`. You can configure `pg_mooncake` to write directly to **Amazon S3**, **Cloudflare R2**, **MinIO**, or **Google Cloud Storage (GCS)** so external engines (DuckDB, Apache Spark, Trino, Snowflake, PyIceberg) can query your PostgreSQL tables directly from object storage.

## 1. Configure Object Storage Credentials (`duckdb.secrets`) {#secrets}

`pg_mooncake` reads object storage credentials from `pg_duckdb`'s `duckdb.secrets` table and passes them to both Moonlink and DuckDB.

### Amazon S3 {#s3}

```sql
INSERT INTO duckdb.secrets (name, type, key_id, secret, region, scope)
VALUES (
    's3_warehouse',
    'S3',
    '<AWS_ACCESS_KEY_ID>',
    '<AWS_SECRET_ACCESS_KEY>',
    'us-east-1',
    's3://my-mooncake-bucket'
);
```

### Cloudflare R2 / S3-Compatible (MinIO) {#r2}

```sql
INSERT INTO duckdb.secrets (name, type, key_id, secret, endpoint, scope)
VALUES (
    'r2_warehouse',
    'S3',
    '<R2_ACCESS_KEY_ID>',
    '<R2_SECRET_ACCESS_KEY>',
    '<ACCOUNT_ID>.r2.cloudflarestorage.com',
    's3://my-r2-bucket'
);
```

## 2. Configure Table Storage (`table_config` & `mooncake.default_bucket`) {#default-bucket}

In `pg_mooncake v0.3.0`, you can configure S3 / R2 / GCS storage directly in the `table_config` JSON parameter of [`mooncake.create_table`](/docs/reference/create-columnstore/#table-config) (or set `mooncake.default_bucket` as documented in upstream `v0.1`/`v0.2` guides):

```sql
-- Option A (v0.2 / v0.3 Moonlink per-table storage_config):
CALL mooncake.create_table(
    dst => 'orders_analytics',
    src => 'orders',
    src_uri => NULL,
    table_config => '{
        "iceberg": {
            "storage_config": {
                "s3": {
                    "region": "us-east-1",
                    "bucket": "my-mooncake-bucket",
                    "access_key_id": "<AWS_ACCESS_KEY_ID>",
                    "secret_access_key": "<AWS_SECRET_ACCESS_KEY>",
                    "endpoint": "https://s3.us-east-1.amazonaws.com"
                }
            }
        }
    }'::json
);

-- Option B (Default local filesystem warehouse under $PGDATA/pg_mooncake):
CALL mooncake.create_table('orders_analytics', 'orders');
```

## 3. Materialize an Apache Iceberg v2 Snapshot {#create-snapshot}

While in-database queries on `orders_analytics` automatically read both flushed Parquet files and Moonlink's in-memory Arrow write buffer, external Iceberg readers only see data that has been flushed into an Iceberg metadata snapshot.

To force-flush all committed rows up to the current PostgreSQL WAL LSN and write a new `v*.metadata.json` file:

```sql
CALL mooncake.create_snapshot('orders_analytics');
```

> [!NOTE] Non-Blocking Snapshot Fix in `v0.3.0` (`moonlink v0.0.1`)
> In `pg_mooncake 0.3.0`, `CALL mooncake.create_snapshot('orders_analytics')` completes immediately even if the database WAL has advanced due to writes on *other, unrelated* tables since the last write to `orders`.

## 4. Locate the Iceberg Warehouse & Query Externally {#external-query}

Use `mooncake.list_tables()` to inspect the commit LSN, flushed LSN, and exact `iceberg_warehouse_location`:

```sql
SELECT * FROM mooncake.list_tables();
```

Example output:

```text
          table          | commit_lsn | flush_lsn  |              iceberg_warehouse_location
-------------------------+------------+------------+-------------------------------------------------------
 public.orders_analytics | 0/1A4F890  | 0/1A4F890  | s3://my-mooncake-bucket/warehouse/postgres/public/orders_analytics
```

### Querying from External DuckDB / PyIceberg / Spark {#duckdb-iceberg}

Inside the `iceberg_warehouse_location` directory, Moonlink writes standard Apache Iceberg v2 metadata (`metadata/v1.metadata.json`, `v2.metadata.json`, etc.):

```sql
-- From any external DuckDB instance:
INSTALL iceberg;
LOAD iceberg;

SELECT *
FROM iceberg_scan('s3://my-mooncake-bucket/warehouse/postgres/public/orders_analytics/metadata/v2.metadata.json');
```

## 5. Compacting Files (`mooncake.optimize_table`) {#optimize}

To compact small Parquet files and reconcile Roaring Bitmap deletion vectors into clean base files:

```sql
-- Run full compaction on the table
CALL mooncake.optimize_table('orders_analytics', 'full');
```
