---
title: "Query Columnstore Table & Supported Query Shapes"
linkTitle: "Query Columnstore"
description: "How pg_mooncake executes vectorized analytical queries via DuckDB 2.0, supported SQL query shapes, hybrid joins, and exposing DuckDB functions in PostgreSQL."
weight: 20
icon: fa-solid fa-magnifying-glass-chart
upstream_link: https://web.archive.org/web/20251207105427/https://docs.mooncake.dev/pg/reference/query-columnstore
aliases:
  - "/pg/reference/query-columnstore/"
  - "/reference/query-columnstore/"
  - "/reference/query-shapes/"
---

Columnstore mirror tables created with `CALL mooncake.create_table(dst, src)` are queried using standard PostgreSQL `SELECT` syntax. Behind the scenes, `pg_mooncake` and `pg_duckdb 1.2.0` translate and route analytical scans to the embedded **DuckDB `v2.0.0`** vectorized execution engine.

## How Queries Work {#how-it-works}

When you query a `USING mooncake` table:

1. **LSN Synchronization**: `duckdb_mooncake` checks PostgreSQL's current WAL write LSN and waits for [`moonlink`](/docs/intro/moonlink/) to ingest all committed transactions up to that LSN.
2. **Segment Elimination**: DuckDB 2.0 inspects multi-file Parquet column min/max statistics to skip files and row groups that cannot match your `WHERE` predicates.
3. **Zero-Copy Hybrid Scan**: Flushed Parquet files, Roaring Bitmap deletion vectors, and the in-memory Apache Arrow write buffer are scanned in parallel across DuckDB worker threads (`duckdb.threads`).

You can verify that DuckDB is executing your query by running `EXPLAIN`:

```sql
EXPLAIN SELECT customer_id, SUM(amount)
FROM orders_analytics
WHERE created_at >= '2026-01-01'
GROUP BY customer_id;
```

## Analytical Query Shapes (Recommended) {#analytical}

Columnstore tables excel at analytical workloads that scan large numbers of rows across a subset of columns, often delivering **10× to 1000× speedups** over heap tables.

### 1. Multi-Dimensional Aggregations {#aggregations}

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

### 2. High-Selectivity Filtering & Top-N Ranking {#filtering}

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

### 3. Time-Series Rollups & Window Functions {#time-series}

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

### 4. Hybrid Joins with Regular PostgreSQL Heap Tables {#hybrid-joins}

You can join a `USING mooncake` columnstore mirror directly with regular PostgreSQL rowstore tables (such as dimension tables or lookup tables):

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

## Operational Point Lookups (Use the Rowstore Table) {#operational}

While `pg_mooncake` supports arbitrary `SELECT` queries, single-row point lookups (`WHERE id = 12345`) and tiny index range scans should be routed to your **source rowstore table**, where PostgreSQL's B-tree indexes provide sub-millisecond lookup latency.

```sql
-- Point lookup -> query the primary rowstore table (uses B-tree index)
SELECT * FROM orders WHERE order_id = 12345;

-- Large analytical scan -> query the columnstore mirror (uses DuckDB 2.0)
SELECT status, COUNT(*), SUM(amount) FROM orders_analytics GROUP BY status;
```

## Query Translation & DuckDB Functions {#query-translation}

Because queries on `USING mooncake` tables are executed by DuckDB (`pg_duckdb`), certain PostgreSQL-specific functions that lack a direct DuckDB equivalent (such as `to_char()`, certain `regexp_*` overloads, or specific `jsonb_*` operators) may require DuckDB-compatible expressions.

### Exposing DuckDB Functions in PostgreSQL {#duckdb-functions}

You can expose native DuckDB analytical functions (such as `time_bucket`) inside PostgreSQL by defining a placeholder PL/pgSQL function with the matching signature. When a query targets a columnstore table, `pg_duckdb` intercepts the call and executes DuckDB's native vectorized implementation:

```sql
CREATE OR REPLACE FUNCTION time_bucket(interval, timestamp)
RETURNS timestamp AS $$
BEGIN
    RAISE EXCEPTION 'placeholder function for DuckDB columnstore execution';
END;
$$ LANGUAGE plpgsql;

-- Executed natively by DuckDB when querying a columnstore table
SELECT
    time_bucket(INTERVAL '5 minutes', created_at) AS five_min_bucket,
    COUNT(*) AS requests
FROM events_analytics
WHERE created_at >= NOW() - INTERVAL '6 hours'
GROUP BY five_min_bucket
ORDER BY five_min_bucket DESC;
```
