---
title: "实时操作分析 (HTAP)"
linkTitle: "实时 HTAP 分析"
description: "保持现有 PostgreSQL OLTP 写入路径不变，通过将分析查询路由至 USING mooncake 实时列存镜像表，实现百倍级分析提速。"
weight: 10
icon: fa-solid fa-bolt
upstream_link: https://web.archive.org/web/20260124122604/https://docs.mooncake.dev/pg/use-cases/real-time-analytics
aliases:
  - "/zh/pg/use-cases/real-time-analytics/"
---

如果你正在 PostgreSQL 业务表上运行缓慢的分析查询（例如实时报表看板、面向客户的统计指标、多维聚合查询），`pg_mooncake` 提供了一条极简的加速路径：

1. **保持业务应用写入路径 100% 不变。**
2. **使用 `CALL mooncake.create_table(dst, src)` 创建实时列存镜像表。**
3. **将分析型 `SELECT` 查询路由至列存镜像表（往往无需修改 SQL 语句本身）。**

## 核心优势 {#advantages}

- **支持在线增删列**：源行存表上的 `ALTER TABLE ... ADD COLUMN` 与 `DROP COLUMN` 操作会自动同步至列存镜像表。
- **高效支持高频 `UPDATE` 与 `DELETE`**：[`moonlink`](/zh/docs/intro/moonlink/) 结合内存 Apache Arrow 写缓冲区与 Roaring Bitmap 删除向量，处理高频更新与删除的性能远超传统 Parquet / Iceberg 写入方案。
- **零 ETL 架构（Zero-ETL）**：无需部署运维 Debezium + Kafka 集群，直接复用 PostgreSQL 内置逻辑复制。
- **强事务一致性**：分析查询在扫描前会自动同步等待当前 PostgreSQL WAL LSN 屏障，确保始终读取到最新已提交的一致性视图。

## 标准模式：写入行存表，查询列存镜像表 {#pattern}

```sql
-- 1. 现有的 OLTP 业务表（承载事务写入与主键点查）
CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    total_amount DECIMAL(10, 2) NOT NULL,
    order_status TEXT NOT NULL DEFAULT 'pending',
    order_date TIMESTAMP NOT NULL DEFAULT NOW()
);

-- 2. 创建实时列存镜像表（专用于分析查询）
CALL mooncake.create_table('orders_analytics', 'orders');

-- 3. 写入操作：始终针对原始行存表执行
INSERT INTO orders (customer_id, total_amount) VALUES (123, 99.99);
UPDATE orders SET total_amount = 149.99, order_status = 'shipped' WHERE order_id = 1;

-- 4. 分析读取操作：查询列存镜像表
SELECT
    customer_id,
    COUNT(*) AS order_count,
    SUM(total_amount) AS lifetime_value
FROM orders_analytics
WHERE order_date >= CURRENT_DATE
GROUP BY customer_id;
```

## 显式查询路由说明 {#routing}

> [!IMPORTANT] 需手动指定查询目标表
> `pg_mooncake` 不会自动拦截针对 `orders` 的查询并将其改写到 `orders_analytics`。请根据查询负载类型显式选择目标表：

```sql
-- 事务增删改与单行索引点查 -> 访问原始行存表 (orders)
INSERT INTO orders (customer_id, total_amount) VALUES (123, 99.99);
UPDATE orders SET order_status = 'shipped' WHERE order_id = 1;
DELETE FROM orders WHERE order_id = 1;
SELECT * FROM orders WHERE order_id = 1;

-- 大规模分析扫描与聚合计算 -> 访问列存镜像表 (orders_analytics)
SELECT customer_id, SUM(total_amount) FROM orders_analytics GROUP BY customer_id;
SELECT COUNT(*) FROM orders_analytics WHERE order_date >= CURRENT_DATE;
SELECT * FROM orders_analytics ORDER BY total_amount DESC LIMIT 10;
```

这种显式读写分离让你能够完全掌控数据库性能：事务操作在拥有 B-Tree 索引的行存堆表上保持亚毫秒级响应，而大吞吐分析扫描则充分发挥 DuckDB 2.0 在列存上的向量化执行优势。
