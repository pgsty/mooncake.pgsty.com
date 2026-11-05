---
title: "Query Your Data Lake in Postgres"
linkTitle: "Query Data Lake"
description: "Query external Parquet, CSV, JSON, Apache Iceberg, Delta Lake, and HuggingFace datasets directly inside PostgreSQL via pg_duckdb and join them with Postgres tables."
weight: 40
icon: fa-solid fa-folder-open
upstream_link: https://web.archive.org/web/20251207105427/https://docs.mooncake.dev/pg/reference/query-data-lake
aliases:
  - "/pg/reference/query-data-lake/"
  - "/reference/query-data-lake/"
  - "/reference/query-external-files/"
---

Because `pg_mooncake` (`v0.3.0`) embeds **DuckDB `v2.0.0`** via **`pg_duckdb 1.2.0`**, you can query external files in your data lake (local disk, S3, Cloudflare R2, GCS, HTTP, or HuggingFace `hf://` datasets) directly from PostgreSQL without loading them into heap tables first.

## Supported External Formats {#formats}

- **Apache Parquet** (`duckdb.read_parquet`)
- **CSV / TSV** (`duckdb.read_csv`)
- **JSON / NDJSON** (`duckdb.read_json`)
- **Apache Iceberg** (`duckdb.iceberg_scan`)
- **Delta Lake** (`duckdb.delta_scan`)

> [!NOTE] `v0.2` / `v0.3` (`duckdb.*`) vs Legacy `v0.1` (`mooncake.*`) Functions
> In `pg_mooncake v0.2` and `v0.3.0`, external file readers are provided directly by `pg_duckdb` (`duckdb.read_parquet`, `duckdb.read_csv`, `duckdb.iceberg_scan`, `duckdb.delta_scan`). For the legacy `v0.1` `mooncake.read_parquet` syntax, see [v0.1 Query External Files](/docs/v0.1/query-external-files/).

## 1. Querying Parquet Files (`duckdb.read_parquet`) {#parquet}

Use `duckdb.read_parquet` and specify the expected output columns in the `AS (...)` clause:

```sql
-- Query a single Parquet file or wildcard glob pattern on S3
SELECT
    user_id,
    event_type,
    created_at
FROM duckdb.read_parquet('s3://my-bucket/events/*.parquet') AS (
    user_id INT,
    event_type TEXT,
    created_at TIMESTAMP
)
WHERE created_at >= '2026-01-01';
```

You can also query Hive-partitioned directory structures:

```sql
SELECT *
FROM duckdb.read_parquet('s3://my-bucket/events/year=2026/month=*/day=*/*.parquet') AS (
    user_id INT,
    event_type TEXT,
    created_at TIMESTAMP
);
```

## 2. Querying CSV Files (`duckdb.read_csv`) {#csv}

```sql
SELECT
    user_id,
    event_type,
    created_at
FROM duckdb.read_csv('s3://my-bucket/events.csv') AS (
    user_id INT,
    event_type TEXT,
    created_at TIMESTAMP
)
WHERE created_at >= '2026-01-01';
```

## 3. Querying External Iceberg & Delta Lake Tables {#iceberg-delta}

First install and load the `iceberg` or `delta` DuckDB extension via `duckdb.install_extension`:

```sql
SELECT duckdb.install_extension('iceberg');
SELECT duckdb.install_extension('delta');

-- Query an external Apache Iceberg table
SELECT
    user_id,
    event_type,
    created_at
FROM duckdb.iceberg_scan('s3://my-bucket/iceberg_events/metadata/v1.metadata.json') AS (
    user_id INT,
    event_type TEXT,
    created_at TIMESTAMP
)
WHERE created_at >= '2026-01-01';

-- Query an external Delta Lake table
SELECT
    user_id,
    event_type,
    created_at
FROM duckdb.delta_scan('s3://my-bucket/delta_events') AS (
    user_id INT,
    event_type TEXT,
    created_at TIMESTAMP
)
WHERE created_at >= '2026-01-01';
```

## 4. Joining External Files with PostgreSQL Tables {#joins}

You can join external Parquet, Iceberg, or Delta Lake datasets directly with regular PostgreSQL heap tables or `USING mooncake` columnstore mirrors in a single SQL query:

```sql
SELECT
    u.username,
    u.email,
    e.event_type,
    e.created_at
FROM users u
JOIN duckdb.read_parquet('s3://my-bucket/events.parquet') AS e(
    user_id INT,
    event_type TEXT,
    created_at TIMESTAMP
) ON u.id = e.user_id
WHERE e.created_at >= '2026-01-01';
```

## 5. Querying HuggingFace Datasets (`hf://`) {#huggingface}

DuckDB supports reading public HuggingFace datasets directly via the `hf://datasets/<org>/<repo>/<path>` URI scheme:

```sql
SELECT id, message, timestamp
FROM duckdb.read_parquet(
    'hf://datasets/OpenLeecher/lmsys_chat_1m_clean/data/train-00000-of-00004.parquet'
) AS (
    id INT,
    message TEXT,
    timestamp TIMESTAMP
)
LIMIT 20;
```
