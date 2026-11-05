---
title: "v0.1 Data Archiving"
linkTitle: "v0.1 Data Archiving"
description: "Historical v0.1 pattern for moving old rows from heap tables into a USING columnstore archive table."
weight: 80
icon: fa-solid fa-box-archive
upstream_link: https://web.archive.org/web/20251207093226/https://docs.mooncake.dev/pg/0.1/Use-cases/Archiving
aliases:
  - "/pg/0.1/Use-cases/Archiving/"
  - "/0.1/Use-cases/Archiving/"
  - "/pg/0.1/use-cases/archiving/"
  - "/0.1/use-cases/archiving/"
---

> [!WARNING] Legacy `pg_mooncake v0.1` Archive (Delta Lake Engine)
> This page documents **`pg_mooncake v0.1`**, which used direct `CREATE TABLE ... USING columnstore` DDL and Delta Lake storage. Starting in `v0.2` and PGSTY's **`v0.3.0`** release, `pg_mooncake` uses [`moonlink`](/docs/intro/moonlink/) real-time columnstore mirrors (`CALL mooncake.create_table` + `USING mooncake`) and Apache Iceberg v2. For current documentation, see [Introduction](/docs/intro/) and [v0.1 vs v0.2 & v0.3](/docs/intro/0.1-vs-0.2/).

> [!TIP] Current `v0.3.0` Partition Archiving Pattern
> In `v0.2` and `v0.3.0`, you no longer need manual `INSERT INTO ... DELETE FROM` batch scripts—simply mirror a partitioned table with `CALL mooncake.create_table` and `DROP` old partitions. See [Archiving Large Postgres Tables](/docs/use-cases/archiving/).

## How Archiving Worked in `v0.1`

```sql
-- Create columnstore archive table
CREATE TABLE orders_archive (
    order_id INT,
    customer_id INT,
    order_date TIMESTAMP,
    amount NUMERIC(10, 2)
) USING columnstore;

-- Move old data to archive
INSERT INTO orders_archive
SELECT * FROM orders
WHERE order_date < CURRENT_DATE - INTERVAL '1 year';

-- Delete from source and reclaim space
DELETE FROM orders
WHERE order_date < CURRENT_DATE - INTERVAL '1 year';
VACUUM FULL orders;
```
