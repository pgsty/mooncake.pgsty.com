---
title: "v0.1 数据仓库与 dbt 集成"
linkTitle: "v0.1 数据仓库与 dbt"
description: "pg_mooncake v0.1 每日聚合流水线与通过 default_table_access_method = 'columnstore' 集成 dbt 的历史指南。"
weight: 90
icon: fa-solid fa-warehouse
upstream_link: https://web.archive.org/web/20251207103729/https://docs.mooncake.dev/pg/0.1/Use-cases/Warehousing
aliases:
  - "/zh/pg/0.1/Use-cases/Warehousing/"
  - "/zh/0.1/Use-cases/Warehousing/"
  - "/zh/pg/0.1/use-cases/warehousing/"
  - "/zh/0.1/use-cases/warehousing/"
---

> [!WARNING] `pg_mooncake v0.1` 历史归档文档（Delta Lake 引擎）
> 本页归档的是早期 **`pg_mooncake v0.1`** 版本文档（采用直接 `CREATE TABLE ... USING columnstore` DDL 与 Delta Lake 存储）。从 `v0.2` 及 PGSTY 维护的 **`v0.3.0`** 版本起，`pg_mooncake` 已全面转向基于 [`moonlink`](/zh/docs/intro/moonlink/) 的实时列存镜像架构（`CALL mooncake.create_table` + `USING mooncake`）与 Apache Iceberg v2。最新文档请参阅[简介](/zh/docs/intro/)与 [v0.1 与 v0.2 / v0.3 架构演进对比](/zh/docs/intro/0.1-vs-0.2/)。

## 每日聚合数仓流水线（`v0.1`）

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

## 与 dbt 集成（`v0.1`）

在 `v0.1` 中，可以通过在 dbt 的 `on-run-start` 钩子中设置 `default_table_access_method = 'columnstore'` 让 dbt 模型默认创建列存表：

```sql
{% macro on_run_start() %}
  {% set query %}
    SET default_table_access_method = 'columnstore';
  {% endset %}
  {% do run_query(query) %}
{% endmacro %}
```
