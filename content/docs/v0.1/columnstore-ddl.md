---
title: "v0.1 Columnstore DDL (USING columnstore)"
linkTitle: "v0.1 Columnstore DDL"
description: "Creating and dropping USING columnstore tables in pg_mooncake v0.1, supported data types, constraints, and default_table_access_method."
weight: 45
icon: fa-solid fa-code
upstream_link: https://web.archive.org/web/20260124114208/https://docs.mooncake.dev/pg/0.1/reference/columnstore-ddl
aliases:
  - "/pg/0.1/reference/columnstore-ddl/"
  - "/0.1/reference/columnstore-ddl/"
---

> [!WARNING] Legacy `pg_mooncake v0.1` Archive (Delta Lake Engine)
> This page documents **`pg_mooncake v0.1`**, which used direct `CREATE TABLE ... USING columnstore` DDL and Delta Lake storage. Starting in `v0.2` and PGSTY's **`v0.3.0`** release, `pg_mooncake` uses [`moonlink`](/docs/intro/moonlink/) real-time columnstore mirrors (`CALL mooncake.create_table` + `USING mooncake`) and Apache Iceberg v2. For current documentation, see [Introduction](/docs/intro/) and [v0.1 vs v0.2 & v0.3](/docs/intro/0.1-vs-0.2/).

## Create Columnstore Table (`v0.1`)

In `v0.1`, columnstore tables were created directly with the `USING columnstore` clause:

```sql
CREATE TABLE users_columnstore (
    id INT,
    name TEXT,
    created_at TIMESTAMP
) USING columnstore;

-- Or via CREATE TABLE ... AS SELECT
CREATE TABLE users_columnstore USING columnstore AS
    SELECT * FROM users_rowstore;
```

## Drop Columnstore Table

```sql
DROP TABLE users_columnstore;
```

## Supported Features & Limitations in `v0.1`

- **Supported**: `INSERT`, `UPDATE`, `DELETE`, ACID transactions, `NOT NULL` constraints, default values, and joins with heap tables.
- **Unsupported Data Types in `v0.1`**: `ENUM`, `uhugeint`, `JSONB` (partial), and complex arrays.
- **Unsupported Constraints in `v0.1`**: Primary keys, foreign keys, unique constraints, indexes, and partitioned tables (`ALTER TABLE` schema changes required recreating the table).

## Setting `columnstore` as Default Table Access Method (`v0.1`)

```sql
SET default_table_access_method = 'columnstore';
```
