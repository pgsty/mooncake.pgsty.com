---
title: "v0.1 Load Data"
linkTitle: "v0.1 Load Data"
description: "Loading data into pg_mooncake v0.1 USING columnstore tables from Postgres tables, Parquet/CSV/JSON files, Iceberg/Delta tables, and HuggingFace."
weight: 60
icon: fa-solid fa-file-import
upstream_link: https://web.archive.org/web/20260124103442/https://docs.mooncake.dev/pg/0.1/reference/load-data
aliases:
  - "/pg/0.1/reference/load-data/"
  - "/0.1/reference/load-data/"
---

> [!WARNING] Legacy `pg_mooncake v0.1` Archive (Delta Lake Engine)
> This page documents **`pg_mooncake v0.1`**, which used direct `CREATE TABLE ... USING columnstore` DDL and Delta Lake storage. Starting in `v0.2` and PGSTY's **`v0.3.0`** release, `pg_mooncake` uses [`moonlink`](/docs/intro/moonlink/) real-time columnstore mirrors (`CALL mooncake.create_table` + `USING mooncake`) and Apache Iceberg v2. For current documentation, see [Introduction](/docs/intro/) and [v0.1 vs v0.2 & v0.3](/docs/intro/0.1-vs-0.2/).

## From PostgreSQL Heap Tables (`v0.1`)

```sql
INSERT INTO users_columnstore
SELECT * FROM users_rowstore;
```

## From Parquet, CSV, or JSON Files (`v0.1`)

```sql
-- Using COPY
COPY users_columnstore FROM 's3://bucket/file.parquet';
COPY users_columnstore FROM 's3://bucket/folder/*.parquet';
COPY users_columnstore FROM 's3://bucket/data.csv' WITH (FORMAT 'csv', HEADER true);

-- Using INSERT with mooncake.read_parquet
INSERT INTO users_columnstore
SELECT * FROM mooncake.read_parquet('s3://bucket/file.parquet') AS (
    id INT,
    name TEXT,
    created_at TIMESTAMP
);
```

## From Iceberg, Delta Lake, or HuggingFace (`v0.1`)

```sql
-- Iceberg
INSERT INTO users_columnstore
SELECT * FROM iceberg_scan('s3://bucket/table') AS (id INT, name TEXT, created_at TIMESTAMP);

-- Delta Lake
INSERT INTO users_columnstore
SELECT * FROM delta_scan('s3://bucket/table') AS (id INT, name TEXT, created_at TIMESTAMP);

-- HuggingFace
COPY users_columnstore FROM 'hf://datasets/OpenLeecher/lmsys_chat_1m_clean/data/train-00000-of-00004.parquet';
```
