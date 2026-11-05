---
title: "v0.1 Architecture (Delta Lake & USING columnstore)"
linkTitle: "v0.1 Architecture"
description: "Architecture of pg_mooncake v0.1: Table Access Method (USING columnstore), Parquet + Delta Lake metadata, and DuckDB read/write paths."
weight: 10
icon: fa-solid fa-sitemap
upstream_link: https://web.archive.org/web/20260124120319/https://docs.mooncake.dev/pg/0.1/intro/architecture
aliases:
  - "/pg/0.1/intro/architecture/"
  - "/0.1/intro/architecture/"
---

> [!WARNING] Legacy `pg_mooncake v0.1` Archive (Delta Lake Engine)
> This page documents **`pg_mooncake v0.1`**, which used direct `CREATE TABLE ... USING columnstore` DDL and Delta Lake storage. Starting in `v0.2` and PGSTY's **`v0.3.0`** release, `pg_mooncake` uses [`moonlink`](/docs/intro/moonlink/) real-time columnstore mirrors (`CALL mooncake.create_table` + `USING mooncake`) and Apache Iceberg v2. For current documentation, see [Introduction](/docs/intro/) and [v0.1 vs v0.2 & v0.3](/docs/intro/0.1-vs-0.2/).

In `pg_mooncake v0.1`, table metadata is stored inside PostgreSQL catalogs for transactional consistency, while columnstore data is written as **Parquet** files with **Delta Lake** metadata on local disk or object storage.

Columnstore tables are exposed as a PostgreSQL Table Access Method (`USING columnstore`). Queries involving columnstore tables are routed from PostgreSQL to DuckDB and streamed back via `pg_duckdb`.

## Read Path

Queries involving `USING columnstore` tables are routed from PostgreSQL to DuckDB, with minor SQL query rewrites applied to bridge syntax differences.

![v0.1 Architecture Diagram](/img/mooncake/architecture.jpg)

`pg_mooncake v0.1` caches Parquet metadata and column statistics inside PostgreSQL (`mooncake.data_files`) and uses them for **segment elimination** during table scans.

## Write Path

In `v0.1`, transactional `INSERT`, `UPDATE`, and `DELETE` statements run directly on `USING columnstore` tables. To support `DELETE` and `UPDATE`, an implicit `row_id` column consisting of `(file_id, row_offset)` identifies rows during table scans.

Each write transaction creates a new Parquet file. Because of this, `pg_mooncake v0.1` is designed for batched writes (`100,000`–`1,000,000` rows) rather than small, frequent OLTP transactions.

### Local Disk Caching

On writes, data is cached on local disk (`mooncake.enable_local_cache = true`) to accelerate queries on recently written data before or alongside cloud object storage uploads.
