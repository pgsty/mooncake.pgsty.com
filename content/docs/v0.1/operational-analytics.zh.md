---
title: "v0.1 操作型分析（触发器 + pg_cron 暂存表方案）"
linkTitle: "v0.1 操作型分析"
description: "在 Moonlink 推出之前，pg_mooncake v0.1 使用触发器、暂存表与 pg_cron 定时批处理实现准实时分析的历史方案。"
weight: 85
icon: fa-solid fa-bolt
upstream_link: https://web.archive.org/web/20251207100042/https://docs.mooncake.dev/pg/0.1/Use-cases/OperationalAnalytics
aliases:
  - "/zh/pg/0.1/Use-cases/OperationalAnalytics/"
  - "/zh/0.1/Use-cases/OperationalAnalytics/"
  - "/zh/pg/0.1/use-cases/operationalanalytics/"
  - "/zh/0.1/use-cases/operationalanalytics/"
---

> [!WARNING] `pg_mooncake v0.1` 历史归档文档（Delta Lake 引擎）
> 本页归档的是早期 **`pg_mooncake v0.1`** 版本文档（采用直接 `CREATE TABLE ... USING columnstore` DDL 与 Delta Lake 存储）。从 `v0.2` 及 PGSTY 维护的 **`v0.3.0`** 版本起，`pg_mooncake` 已全面转向基于 [`moonlink`](/zh/docs/intro/moonlink/) 的实时列存镜像架构（`CALL mooncake.create_table` + `USING mooncake`）与 Apache Iceberg v2。最新文档请参阅[简介](/zh/docs/intro/)与 [v0.1 与 v0.2 / v0.3 架构演进对比](/zh/docs/intro/0.1-vs-0.2/)。

> [!TIP] 在 `v0.2` / `v0.3.0` 中已由 `mooncake.create_table` 彻底取代
> 在 `v0.1` 中，将行存表同步至 `USING columnstore` 表需要手动维护触发器、暂存表与 `pg_cron` 定时任务。在 `v0.2` 与 `v0.3.0` 中，只需一行 `CALL mooncake.create_table('orders_analytics', 'orders');` 即可实现亚秒级逻辑复制。详见[实时操作分析 (HTAP)](/zh/docs/use-cases/real-time-analytics/)。

## `v0.1` 历史暂存表与触发器同步模式

```sql
-- 1. 创建暂存表
CREATE TABLE orders_staging (
    order_id INT PRIMARY KEY,
    customer_id INT,
    quantity INT,
    unit_price DECIMAL(10, 2),
    order_date TIMESTAMP
);

-- 2. 创建列存表
CREATE TABLE orders_analytics (
    order_id INT,
    customer_id INT,
    quantity INT,
    unit_price DECIMAL(10, 2),
    order_date TIMESTAMP,
    last_updated TIMESTAMP
) USING columnstore;

-- 3. 通过 pg_cron 定期将暂存表批量写入列存表
CREATE OR REPLACE FUNCTION sync_to_columnstore() RETURNS void AS $$
BEGIN
    INSERT INTO orders_analytics
    SELECT s.*, NOW() FROM orders_staging s;
    TRUNCATE orders_staging;
END;
$$ LANGUAGE plpgsql;
```
