---
title: "v0.1 Query External Files"
linkTitle: "v0.1 Query External Files"
description: "Querying external Parquet, CSV, JSON, Iceberg, and Delta Lake files in pg_mooncake v0.1 using mooncake.read_parquet, mooncake.read_csv, and mooncake.read_json."
weight: 65
icon: fa-solid fa-folder-open
upstream_link: https://web.archive.org/web/20251207090831/https://docs.mooncake.dev/pg/0.1/reference/query-external-files
aliases:
  - "/pg/0.1/reference/query-external-files/"
  - "/0.1/reference/query-external-files/"
---

> [!WARNING] Legacy `pg_mooncake v0.1` Archive (Delta Lake Engine)
> This page documents **`pg_mooncake v0.1`**, which used direct `CREATE TABLE ... USING columnstore` DDL and Delta Lake storage. Starting in `v0.2` and PGSTY's **`v0.3.0`** release, `pg_mooncake` uses [`moonlink`](/docs/intro/moonlink/) real-time columnstore mirrors (`CALL mooncake.create_table` + `USING mooncake`) and Apache Iceberg v2. For current documentation, see [Introduction](/docs/intro/) and [v0.1 vs v0.2 & v0.3](/docs/intro/0.1-vs-0.2/).

> [!NOTE] Current `v0.3.0` External File Readers
> In `v0.2` and `v0.3.0`, use `duckdb.read_parquet`, `duckdb.read_csv`, `duckdb.iceberg_scan`, and `duckdb.delta_scan` as documented in [Query Your Data Lake in Postgres](/docs/reference/query-data-lake/).

## Querying Parquet, CSV, and JSON (`v0.1`)

```sql
-- Parquet
SELECT user_id, event_type, created_at
FROM mooncake.read_parquet('s3://bucket/events.parquet') AS (
    user_id INT,
    event_type TEXT,
    created_at TIMESTAMP
)
WHERE created_at > '2023-01-01';

-- CSV
SELECT r['user_id']::INT, r['event_type'], r['created_at']::TIMESTAMP
FROM mooncake.read_csv('s3://bucket/events.csv', AUTO_DETECT=TRUE) r
WHERE r['created_at']::TIMESTAMP > '2023-01-01';

-- JSON
SELECT
    json_extract_path_text(data, 'user_id')::INT AS user_id,
    json_extract_path_text(data, 'event_type') AS event_type
FROM mooncake.read_json('s3://bucket/events.json') AS (data JSONB);
```

## Querying Iceberg and Delta Lake (`v0.1`)

```sql
SELECT * FROM iceberg_scan('s3://bucket/iceberg_table') AS (
    user_id INT, event_type TEXT, created_at TIMESTAMP
);

SELECT * FROM delta_scan('s3://bucket/delta_table') AS (
    user_id INT, event_type TEXT, created_at TIMESTAMP
);
```
