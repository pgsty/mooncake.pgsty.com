---
title: "v0.1 Supported Queries & Query Shapes"
linkTitle: "v0.1 Supported Queries"
description: "Analytical query patterns, unsupported PostgreSQL functions, and DuckDB function placeholders in pg_mooncake v0.1."
weight: 70
icon: fa-solid fa-magnifying-glass-chart
upstream_link: https://web.archive.org/web/20251207085301/https://docs.mooncake.dev/pg/0.1/reference/query-shapes
aliases:
  - "/pg/0.1/reference/query-shapes/"
  - "/0.1/reference/query-shapes/"
---

> [!WARNING] Legacy `pg_mooncake v0.1` Archive (Delta Lake Engine)
> This page documents **`pg_mooncake v0.1`**, which used direct `CREATE TABLE ... USING columnstore` DDL and Delta Lake storage. Starting in `v0.2` and PGSTY's **`v0.3.0`** release, `pg_mooncake` uses [`moonlink`](/docs/intro/moonlink/) real-time columnstore mirrors (`CALL mooncake.create_table` + `USING mooncake`) and Apache Iceberg v2. For current documentation, see [Introduction](/docs/intro/) and [v0.1 vs v0.2 & v0.3](/docs/intro/0.1-vs-0.2/).

For the updated `v0.3.0` guide on query shapes and DuckDB 2.0 execution, see [Query Columnstore & Query Shapes](/docs/reference/query-columnstore/).

## Analytical Aggregations & Time-Series (`v0.1`)

```sql
SELECT
    region,
    date_trunc('quarter', sale_date) AS quarter,
    SUM(amount) AS total_sales,
    COUNT(*) AS num_transactions,
    AVG(amount) AS avg_sale
FROM sales_columnstore
WHERE sale_date BETWEEN '2023-01-01' AND '2023-12-31'
GROUP BY region, quarter
ORDER BY region, quarter;
```

## Exposing DuckDB Functions in Postgres (`v0.1`)

```sql
CREATE OR REPLACE FUNCTION time_bucket(interval, timestamp)
RETURNS timestamp AS $$
BEGIN
    RAISE EXCEPTION 'this is a placeholder for columnstore';
END;
$$ LANGUAGE plpgsql;
```
