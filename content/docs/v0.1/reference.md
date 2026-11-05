---
title: "v0.1 Reference Overview"
linkTitle: "v0.1 Reference"
description: "Reference index for pg_mooncake v0.1 DDL, Delta Lake metadata catalogs, GUC parameters, data loading, and external file queries."
weight: 40
icon: fa-solid fa-book-open
upstream_link: https://web.archive.org/web/20251207093616/https://docs.mooncake.dev/pg/0.1/reference/
aliases:
  - "/pg/0.1/reference/"
  - "/0.1/reference/"
---

> [!WARNING] Legacy `pg_mooncake v0.1` Archive (Delta Lake Engine)
> This page documents **`pg_mooncake v0.1`**, which used direct `CREATE TABLE ... USING columnstore` DDL and Delta Lake storage. Starting in `v0.2` and PGSTY's **`v0.3.0`** release, `pg_mooncake` uses [`moonlink`](/docs/intro/moonlink/) real-time columnstore mirrors (`CALL mooncake.create_table` + `USING mooncake`) and Apache Iceberg v2. For current documentation, see [Introduction](/docs/intro/) and [v0.1 vs v0.2 & v0.3](/docs/intro/0.1-vs-0.2/).

- [v0.1 Columnstore DDL (`USING columnstore`)](/docs/v0.1/columnstore-ddl/)
- [v0.1 Querying Columnstore Outside Postgres (`mooncake.columnstore_tables`)](/docs/v0.1/columnstore-metadata/)
- [v0.1 GUC Configurations (`mooncake.maximum_memory`, `mooncake.maximum_threads`)](/docs/v0.1/configurations/)
- [v0.1 Load Data (`COPY` & `mooncake.read_parquet`)](/docs/v0.1/load-data/)
- [v0.1 Query External Files (`mooncake.read_parquet`, `mooncake.read_csv`, `iceberg_scan`, `delta_scan`)](/docs/v0.1/query-external-files/)
- [v0.1 Supported Queries & Query Shapes](/docs/v0.1/query-shapes/)
