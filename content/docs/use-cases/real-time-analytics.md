---
title: "Real-Time Operational Analytics (HTAP)"
linkTitle: "Real-Time Analytics"
description: "Speed up slow analytical queries on PostgreSQL tables by routing reads to a real-time USING mooncake columnstore mirror while keeping your OLTP write path unchanged."
weight: 10
icon: fa-solid fa-bolt
upstream_link: https://web.archive.org/web/20260124122604/https://docs.mooncake.dev/pg/use-cases/real-time-analytics
aliases:
  - "/pg/use-cases/real-time-analytics/"
---

If you are running slow analytical queries (dashboards, customer-facing metrics, multi-table aggregations) on PostgreSQL tables, `pg_mooncake` gives you a straightforward route to accelerate them:

1. **Keep your application write path 100% unchanged.**
2. **Create a real-time columnstore mirror** with `CALL mooncake.create_table(dst, src)`.
3. **Route analytical `SELECT` queries** to the columnstore mirror table.

## Key Advantages {#advantages}

- **Schema changes supported**: `ALTER TABLE ... ADD COLUMN` and `DROP COLUMN` on the source table automatically sync to the columnstore mirror.
- **Fast `UPDATE` and `DELETE` handling**: [`moonlink`](/docs/intro/moonlink/) uses in-memory Apache Arrow buffers and Roaring Bitmap deletion vectors, handling high-frequency OLTP updates and deletes far more efficiently than traditional Parquet/Iceberg writers.
- **Zero-ETL**: No Debezium, Kafka, or Flink clusters to operate—`pg_mooncake` uses PostgreSQL's built-in logical replication.
- **Transactional consistency**: Analytical queries wait for the current PostgreSQL WAL LSN barrier before scanning, guaranteeing a consistent view of committed data.

## Implementation Pattern: Write to Rowstore, Read from Columnstore {#pattern}

```sql
-- 1. Your existing OLTP table (for transactional writes and point lookups)
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    order_status TEXT NOT NULL DEFAULT 'pending',
    order_date TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 2. Create the real-time columnstore mirror (for analytics)
CALL mooncake.create_table('orders_analytics', 'orders');

-- 3. Write operations: always use the original rowstore table
INSERT INTO orders (customer_id, total_amount) VALUES (123, 99.99);
UPDATE orders SET total_amount = 149.99, order_status = 'shipped' WHERE order_id = 1;

-- 4. Analytical read operations: query the columnstore mirror
SELECT
    customer_id,
    COUNT(*) AS order_count,
    SUM(total_amount) AS lifetime_value
FROM orders_analytics
WHERE order_date >= CURRENT_DATE
GROUP BY customer_id;
```

## Manual Query Routing {#routing}

> [!IMPORTANT] Explicit Table Routing
> `pg_mooncake` does not automatically rewrite queries targeting `orders` to target `orders_analytics`. You choose which table to query based on your workload:

```sql
-- Transactional DML & indexed point lookups -> Original rowstore table (orders)
INSERT INTO orders (customer_id, total_amount) VALUES (123, 99.99);
UPDATE orders SET order_status = 'shipped' WHERE order_id = 1;
DELETE FROM orders WHERE order_id = 1;
SELECT * FROM orders WHERE order_id = 1;

-- Large analytical scans & aggregations -> Columnstore mirror (orders_analytics)
SELECT customer_id, SUM(total_amount) FROM orders_analytics GROUP BY customer_id;
SELECT COUNT(*) FROM orders_analytics WHERE order_date >= CURRENT_DATE;
SELECT * FROM orders_analytics ORDER BY total_amount DESC LIMIT 10;
```

This explicit separation gives you predictable performance: transactional operations stay fast on the B-tree-indexed heap table, while analytical scans leverage DuckDB 2.0's vectorized execution over columnar storage.
