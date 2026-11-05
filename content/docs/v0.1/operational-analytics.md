---
title: "v0.1 Operational Analytics (Trigger + pg_cron Staging)"
linkTitle: "v0.1 Operational Analytics"
description: "Historical v0.1 staging-table trigger and pg_cron pattern for near-real-time analytics before Moonlink was introduced."
weight: 85
icon: fa-solid fa-bolt
upstream_link: https://web.archive.org/web/20251207100042/https://docs.mooncake.dev/pg/0.1/Use-cases/OperationalAnalytics
aliases:
  - "/pg/0.1/Use-cases/OperationalAnalytics/"
  - "/0.1/Use-cases/OperationalAnalytics/"
  - "/pg/0.1/use-cases/operationalanalytics/"
  - "/0.1/use-cases/operationalanalytics/"
---

> [!WARNING] Legacy `pg_mooncake v0.1` Archive (Delta Lake Engine)
> This page documents **`pg_mooncake v0.1`**, which used direct `CREATE TABLE ... USING columnstore` DDL and Delta Lake storage. Starting in `v0.2` and PGSTY's **`v0.3.0`** release, `pg_mooncake` uses [`moonlink`](/docs/intro/moonlink/) real-time columnstore mirrors (`CALL mooncake.create_table` + `USING mooncake`) and Apache Iceberg v2. For current documentation, see [Introduction](/docs/intro/) and [v0.1 vs v0.2 & v0.3](/docs/intro/0.1-vs-0.2/).

> [!TIP] Replaced by `mooncake.create_table` in `v0.2` / `v0.3.0`
> In `v0.1`, syncing a rowstore table to a `USING columnstore` table required triggers, a staging table, and a `pg_cron` job. In `v0.2` and `v0.3.0`, all of this is replaced by a single `CALL mooncake.create_table('orders_analytics', 'orders');`. See [Real-Time Operational Analytics](/docs/use-cases/real-time-analytics/).

## Historical `v0.1` Staging & Trigger Pattern

```sql
-- 1. Staging table
CREATE TABLE orders_staging (
    order_id INT PRIMARY KEY,
    customer_id INT,
    quantity INT,
    unit_price DECIMAL(10, 2),
    order_date TIMESTAMP
);

-- 2. Columnstore table
CREATE TABLE orders_analytics (
    order_id INT,
    customer_id INT,
    quantity INT,
    unit_price DECIMAL(10, 2),
    order_date TIMESTAMP,
    last_updated TIMESTAMP
) USING columnstore;

-- 3. Periodic batch sync function scheduled via pg_cron
CREATE OR REPLACE FUNCTION sync_to_columnstore() RETURNS void AS $$
BEGIN
    INSERT INTO orders_analytics
    SELECT s.*, NOW() FROM orders_staging s;
    TRUNCATE orders_staging;
END;
$$ LANGUAGE plpgsql;
```
