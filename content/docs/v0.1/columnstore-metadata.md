---
title: "v0.1 Querying Columnstore Outside Postgres"
linkTitle: "v0.1 Metadata & Polars"
description: "Inspecting mooncake.columnstore_tables and mooncake.data_files in pg_mooncake v0.1 and querying Delta Lake tables from Python Polars."
weight: 50
icon: fa-solid fa-table-list
upstream_link: https://web.archive.org/web/20260124111848/https://docs.mooncake.dev/pg/0.1/reference/columnstore-metadata
aliases:
  - "/pg/0.1/reference/columnstore-metadata/"
  - "/0.1/reference/columnstore-metadata/"
---

> [!WARNING] Legacy `pg_mooncake v0.1` Archive (Delta Lake Engine)
> This page documents **`pg_mooncake v0.1`**, which used direct `CREATE TABLE ... USING columnstore` DDL and Delta Lake storage. Starting in `v0.2` and PGSTY's **`v0.3.0`** release, `pg_mooncake` uses [`moonlink`](/docs/intro/moonlink/) real-time columnstore mirrors (`CALL mooncake.create_table` + `USING mooncake`) and Apache Iceberg v2. For current documentation, see [Introduction](/docs/intro/) and [v0.1 vs v0.2 & v0.3](/docs/intro/0.1-vs-0.2/).

> [!NOTE] Current `v0.3.0` Metadata Function
> In `v0.2` and `v0.3.0`, use `SELECT * FROM mooncake.list_tables();` to inspect table LSNs and Apache Iceberg v2 warehouse locations.

## Finding Table Locations (`v0.1`)

In `v0.1`, `mooncake.columnstore_tables` listed the Delta Lake directory path for each `USING columnstore` table:

```sql
SELECT * FROM mooncake.columnstore_tables;
```

Example output:

```text
    table_name     |                                          path
-------------------+----------------------------------------------------------------------------------------
 users_columnstore | /usr/local/pgsql/data/mooncake_local_tables/mooncake_postgres_users_columnstore_16446/
 events            | s3://my-bucket/mooncake_postgres_events_16459/
```

## Viewing Data Files (`v0.1`)

```sql
SELECT * FROM mooncake.data_files;
```

## Accessing `v0.1` Delta Lake Tables with Polars

```python
import polars as pl

local_path = "/usr/local/pgsql/data/mooncake_local_tables/mooncake_postgres_users_columnstore_16446/"
df = pl.scan_delta(local_path)
print(df.collect())
```
