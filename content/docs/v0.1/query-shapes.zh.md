---
title: "v0.1 支持的查询形态"
linkTitle: "v0.1 支持的查询形态"
description: "pg_mooncake v0.1 中的分析型查询模式、不支持的 PostgreSQL 函数及 DuckDB 占位函数说明。"
weight: 70
icon: fa-solid fa-magnifying-glass-chart
upstream_link: https://web.archive.org/web/20251207085301/https://docs.mooncake.dev/pg/0.1/reference/query-shapes
aliases:
  - "/zh/pg/0.1/reference/query-shapes/"
  - "/zh/0.1/reference/query-shapes/"
---

> [!WARNING] `pg_mooncake v0.1` 历史归档文档（Delta Lake 引擎）
> 本页归档的是早期 **`pg_mooncake v0.1`** 版本文档（采用直接 `CREATE TABLE ... USING columnstore` DDL 与 Delta Lake 存储）。从 `v0.2` 及 PGSTY 维护的 **`v0.3.0`** 版本起，`pg_mooncake` 已全面转向基于 [`moonlink`](/zh/docs/intro/moonlink/) 的实时列存镜像架构（`CALL mooncake.create_table` + `USING mooncake`）与 Apache Iceberg v2。最新文档请参阅[简介](/zh/docs/intro/)与 [v0.1 与 v0.2 / v0.3 架构演进对比](/zh/docs/intro/0.1-vs-0.2/)。

关于 `v0.3.0` 与 DuckDB 2.0 的最新查询形态指南，请参阅[查询列存表与查询形态](/zh/docs/reference/query-columnstore/)。

## 分析聚合与时序查询（`v0.1`）

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

## 在 Postgres 中暴露 DuckDB 函数（`v0.1`）

```sql
CREATE OR REPLACE FUNCTION time_bucket(interval, timestamp)
RETURNS timestamp AS $$
BEGIN
    RAISE EXCEPTION 'this is a placeholder for columnstore';
END;
$$ LANGUAGE plpgsql;
```
