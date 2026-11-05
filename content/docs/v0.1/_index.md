---
title: "v0.1 Archive: Welcome to pg_mooncake (Delta Lake)"
linkTitle: "v0.1 Archive (Delta Lake)"
description: "Historical documentation archive for pg_mooncake v0.1 (USING columnstore + Delta Lake storage engine)."
weight: 50
icon: fa-solid fa-box-archive
upstream_link: https://web.archive.org/web/20251207094131/https://docs.mooncake.dev/pg/0.1/intro/
aliases:
  - "/pg/0.1/"
  - "/pg/0.1/intro/"
  - "/0.1/"
  - "/0.1/intro/"
---

> [!WARNING] Legacy `pg_mooncake v0.1` Archive (Delta Lake Engine)
> This page documents **`pg_mooncake v0.1`**, which used direct `CREATE TABLE ... USING columnstore` DDL and Delta Lake storage. Starting in `v0.2` and PGSTY's **`v0.3.0`** release, `pg_mooncake` uses [`moonlink`](/docs/intro/moonlink/) real-time columnstore mirrors (`CALL mooncake.create_table` + `USING mooncake`) and Apache Iceberg v2. For current documentation, see [Introduction](/docs/intro/) and [v0.1 vs v0.2 & v0.3](/docs/intro/0.1-vs-0.2/).

`pg_mooncake v0.1` is the first-generation PostgreSQL extension that added `USING columnstore` tables backed by Delta Lake and DuckDB (`pg_duckdb`) for analytical workloads.

![pg_mooncake Venn Diagram](/img/mooncake/pg_mooncake_intro.jpg)

## Key Features of `v0.1`

1. Transactional `INSERT`, `UPDATE`, and `DELETE` directly on `USING columnstore` tables
2. Columnar Parquet + Delta Lake metadata stored on local disk or S3 / R2 object storage
3. Vectorized analytical execution via embedded DuckDB
4. Seamless joins between regular PostgreSQL heap tables and `USING columnstore` tables

## `v0.1` Archive Contents

| Section | Pages |
|:---|:---|
| **Introduction** | [v0.1 Architecture](/docs/v0.1/architecture/) |
| **Getting Started** | [Get Started](/docs/v0.1/get-started/) · [Hello World](/docs/v0.1/hello-world/) · [Cloud Storage](/docs/v0.1/cloud-storage/) · [Neon Postgres](/docs/v0.1/neon-postgres/) |
| **Reference** | [Reference Overview](/docs/v0.1/reference/) · [Columnstore DDL](/docs/v0.1/columnstore-ddl/) · [Querying Outside Postgres](/docs/v0.1/columnstore-metadata/) · [Configurations](/docs/v0.1/configurations/) · [Load Data](/docs/v0.1/load-data/) · [Query External Files](/docs/v0.1/query-external-files/) · [Supported Queries](/docs/v0.1/query-shapes/) |
| **Use Cases** | [Data Archiving](/docs/v0.1/archiving/) · [Operational Analytics](/docs/v0.1/operational-analytics/) · [Data Warehousing](/docs/v0.1/warehousing/) |
{.wide .expand}
