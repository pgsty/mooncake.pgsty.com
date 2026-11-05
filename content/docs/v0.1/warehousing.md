---
title: "v0.1 Data Warehousing & dbt"
linkTitle: "v0.1 Data Warehousing"
description: "Historical v0.1 guide for daily aggregation pipelines and dbt integration using default_table_access_method = 'columnstore'."
weight: 90
icon: fa-solid fa-warehouse
upstream_link: https://web.archive.org/web/20251207103729/https://docs.mooncake.dev/pg/0.1/Use-cases/Warehousing
aliases:
  - "/pg/0.1/Use-cases/Warehousing/"
  - "/0.1/Use-cases/Warehousing/"
  - "/pg/0.1/use-cases/warehousing/"
  - "/0.1/use-cases/warehousing/"
---

> [!WARNING] Legacy `pg_mooncake v0.1` Archive (Delta Lake Engine)
> This page documents **`pg_mooncake v0.1`**, which used direct `CREATE TABLE ... USING columnstore` DDL and Delta Lake storage. Starting in `v0.2` and PGSTY's **`v0.3.0`** release, `pg_mooncake` uses [`moonlink`](/docs/intro/moonlink/) real-time columnstore mirrors (`CALL mooncake.create_table` + `USING mooncake`) and Apache Iceberg v2. For current documentation, see [Introduction](/docs/intro/) and [v0.1 vs v0.2 & v0.3](/docs/intro/0.1-vs-0.2/).

## Daily Aggregation Pipeline (`v0.1`)

```sql
CREATE TABLE daily_sales_summary (
    date DATE,
    product_id INT,
    category_id INT,
    region_id INT,
    total_quantity INT,
    total_revenue DECIMAL(18, 2)
) USING columnstore;
```

## Integration with dbt (`v0.1`)

In `v0.1`, dbt models could target `USING columnstore` by setting `default_table_access_method` in an `on-run-start` hook:

```sql
{% macro on_run_start() %}
  {% set query %}
    SET default_table_access_method = 'columnstore';
  {% endset %}
  {% do run_query(query) %}
{% endmacro %}
```
