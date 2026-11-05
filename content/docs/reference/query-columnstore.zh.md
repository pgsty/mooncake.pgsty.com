---
title: "查询列存表与支持的查询形态"
linkTitle: "查询列存表"
description: "解析 pg_mooncake 如何通过 DuckDB 2.0 执行向量化分析查询、支持的 SQL 查询形态、行存混合关联，以及在 PostgreSQL 中暴露 DuckDB 函数。"
weight: 20
icon: fa-solid fa-magnifying-glass-chart
upstream_link: https://web.archive.org/web/20251207105427/https://docs.mooncake.dev/pg/reference/query-columnstore
aliases:
  - "/zh/pg/reference/query-columnstore/"
  - "/zh/reference/query-columnstore/"
  - "/zh/reference/query-shapes/"
---

通过 `CALL mooncake.create_table(dst, src)` 创建的列存镜像表可以直接使用标准 PostgreSQL `SELECT` 语法进行查询。在底层，`pg_mooncake` 与 `pg_duckdb 1.2.0` 会将分析型查询自动转换并下推至内嵌的 **DuckDB `v2.0.0`** 向量化执行引擎。

## 查询执行机制 {#how-it-works}

当你查询一张 `USING mooncake` 列存镜像表时：

1. **LSN 强一致性同步屏障**：`duckdb_mooncake` 检查当前 PostgreSQL 的 WAL 写入 LSN，并等待 [`moonlink`](/zh/docs/intro/moonlink/) 将该 LSN 之前所有已提交的事务摄取完毕。
2. **Parquet 分段跳过（Segment Elimination）**：DuckDB 2.0 通过多文件读取器接口检查 Parquet 文件的列级最小/最大值统计信息，直接跳过不可能命中 `WHERE` 过滤条件的文件与行组。
3. **零拷贝混合并行扫描**：利用 DuckDB 的多线程工作池（`duckdb.threads`），并行融合扫描磁盘上的 Parquet 数据文件、Roaring Bitmap 删除向量以及内存中的 Apache Arrow 写缓冲区。

你可以通过 `EXPLAIN` 验证查询是否已由 DuckDB 接管执行：

```sql
EXPLAIN SELECT customer_id, SUM(amount)
FROM orders_analytics
WHERE created_at >= '2026-01-01'
GROUP BY customer_id;
```

## 推荐的分析型查询形态 {#analytical}

列存镜像表专为扫描海量行、读取部分列的 OLAP 分析负载设计，相比传统 PostgreSQL 堆表通常可获得 **10× 至 1000× 的查询加速**。

### 1. 多维分组聚合（Aggregations） {#aggregations}

```sql
SELECT
    region,
    date_trunc('quarter', sale_date) AS quarter,
    SUM(amount) AS total_sales,
    COUNT(*) AS num_transactions,
    AVG(amount) AS avg_sale
FROM sales_analytics
WHERE sale_date BETWEEN '2025-01-01' AND '2025-12-31'
GROUP BY region, quarter
ORDER BY region, quarter;
```

### 2. 大数据集过滤与 Top-N 排序 {#filtering}

```sql
SELECT
    customer_id,
    SUM(amount) AS total_spent
FROM sales_analytics
WHERE sale_date >= CURRENT_DATE - INTERVAL '1 year'
GROUP BY customer_id
HAVING SUM(amount) > 10000
ORDER BY total_spent DESC
LIMIT 50;
```

### 3. 时序聚合与窗口分析 {#time-series}

```sql
SELECT
    date_trunc('day', event_time) AS day,
    COUNT(*) AS num_events,
    SUM(CASE WHEN event_type = 'purchase' THEN 1 ELSE 0 END) AS purchases
FROM events_analytics
WHERE event_time >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY day
ORDER BY day;
```

### 4. 与常规 PostgreSQL 行存表混合关联（Hybrid Joins） {#hybrid-joins}

你可以在同一条 SQL 中将 `USING mooncake` 列存镜像表与常规 PostgreSQL 行存表（如维度表、字典表）直接关联：

```sql
SELECT
    u.tier,
    COUNT(o.order_id) AS order_count,
    SUM(o.amount) AS total_revenue
FROM users u
JOIN orders_analytics o ON u.id = o.customer_id
WHERE o.created_at >= NOW() - INTERVAL '7 days'
GROUP BY u.tier;
```

## 点查与短事务查询（请路由至原行存表） {#operational}

虽然 `pg_mooncake` 支持任意 `SELECT` 语句，但针对单行主键点查（`WHERE id = 12345`）或极小范围索引扫描，应当直接查询**源行存表**（利用 PostgreSQL 的 B-Tree 索引获得亚毫秒级响应）：

```sql
-- 单行点查 -> 查询原行存表（走 B-Tree 索引）
SELECT * FROM orders WHERE order_id = 12345;

-- 大规模聚合扫描 -> 查询列存镜像表（走 DuckDB 2.0 向量化扫描）
SELECT status, COUNT(*), SUM(amount) FROM orders_analytics GROUP BY status;
```

## 查询转换与调用 DuckDB 原生函数 {#query-translation}

由于针对 `USING mooncake` 表的查询由 DuckDB（`pg_duckdb`）执行，部分没有 DuckDB 直接对应实现的 PostgreSQL 特有函数（例如 `to_char()`、部分 `regexp_*` 重载或特定 `jsonb_*` 操作符）可能需要改写为兼容表达式。

### 在 PostgreSQL 中暴露 DuckDB 向量化函数 {#duckdb-functions}

如果你希望在查询列存镜像表时调用 DuckDB 内置的分析函数（例如时序分桶函数 `time_bucket`），只需在 PostgreSQL 中定义一个同签名的占位 PL/pgSQL 函数。当查询下推至 DuckDB 时，`pg_duckdb` 会自动将其绑定到 DuckDB 的原生向量化实现：

```sql
CREATE OR REPLACE FUNCTION time_bucket(interval, timestamp)
RETURNS timestamp AS $$
BEGIN
    RAISE EXCEPTION 'placeholder function for DuckDB columnstore execution';
END;
$$ LANGUAGE plpgsql;

-- 查询列存镜像表时由 DuckDB 原生执行 time_bucket
SELECT
    time_bucket(INTERVAL '5 minutes', created_at) AS five_min_bucket,
    COUNT(*) AS requests
FROM events_analytics
WHERE created_at >= NOW() - INTERVAL '6 hours'
GROUP BY five_min_bucket
ORDER BY five_min_bucket DESC;
```
