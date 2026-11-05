---
title: "How to improve DuckDB performance on Parquet"
date: 2025-01-22
description: "How we made DuckDB run faster on Parquet files in ClickBench with the help of PostgreSQL system tables, row-group min/max pruning, and metadata caching."
author: "[Pranav Aurora](https://github.com/paurora17) · [Mooncake Labs](https://github.com/Mooncake-Labs)"
authors: ["pranav-aurora"]
tags:
  - "duckdb"
  - "parquet"
  - "pg_mooncake"
  - "benchmark"
upstream_link: "https://www.mooncake.dev/blog/duckdb-parquet"
upstream_copyright: "© 2025 Pranav Aurora (Mooncake Labs Inc.)"
aliases:
  - "/blog/duckdb-parquet/"
images: ["/blog/covers/duckdb-parquet.jpg"]
---

Last week, we ran ClickBench on Postgres and ranked in the [top 10](/blog/post/clickbench-v0.1/). We showed that Postgres can be extended with [`pg_mooncake`](/docs/intro/) to support serious analytics workloads.

In the announcement, we got a lot of questions on how `pg_mooncake` outperforms DuckDB on Parquet files even though internally, it embeds DuckDB in Postgres and stores data in Parquet format.

> See also the discussion on [X / Twitter](https://x.com/mooncake_dev/status/1881844188905709880).

The best part: `pg_mooncake` does not modify DuckDB at all...

## A quick recap of the pg_mooncake design

`pg_mooncake` is a Postgres extension that adds column-oriented storage and vectorized execution for fast analytics:

1. Data in columnstore tables is stored in Parquet files
2. Table metadata (which Parquet files are present) is stored in Postgres with transactional guarantees
3. Queries on columnstore tables are executed using DuckDB

We recommend the [full architecture read](/blog/post/how-we-built-pgmooncake/).

## How can an Elephant catch a Duck?

At first glance, it seems unlikely that a system which routes Postgres queries through DuckDB to scan Parquet files could outperform DuckDB scanning those files directly.

And on [ClickBench](https://benchmark.clickhouse.com/), this holds true for plain wrappers: **`pg_duckdb` (10.21x)** exhibits significant overhead compared to **DuckDB (Parquet, partitioned) (6.76x)**.

Surprisingly, despite relying on `pg_duckdb`, **`pg_mooncake` (6.03x)** is approximately 1.5x faster than `pg_duckdb` and even outperforms **DuckDB (Parquet, partitioned)** itself.

## So, Why Does pg_mooncake Outperform DuckDB?

`pg_mooncake` leverages Postgres to store table metadata, eliminating the need to query an external catalog (as DuckDB would require when scanning external Iceberg or Delta Lake tables). Instead, it directly queries the Postgres table to identify which Parquet files to scan, reducing overhead.

Additionally, `pg_mooncake` stores detailed Parquet metadata for each file in Postgres, including column statistics for every row group. These statistics, such as `MIN`/`MAX` values for each column, are aggregated to optimize scans. When querying a columnstore table, `pg_mooncake` uses these statistics to filter out data files and row groups that cannot produce matches.

For instance, in a query like:

```sql
... WHERE order_date BETWEEN '2023-01-01' AND '2023-01-31' ...
```

any row groups or segments outside this date range are skipped. By avoiding unnecessary I/O, this optimization dramatically enhances query performance.

Since parsing Parquet metadata is computationally expensive, `pg_mooncake` further minimizes overhead by maintaining an in-memory cache for Parquet metadata, resulting in an additional 5% speedup in query execution.

## Why still stick to Parquet?

We're often asked this question. If raw performance were the only consideration, using a custom memory format would allow us to squeeze out the last bit of performance.

However, we believe in the openness that the Lakehouse architecture brings. Postgres isn't designed to manage every aspect of your data lifecycle, and this approach enables seamless multi-engine interoperability.

Most importantly, we demonstrated that you can achieve great performance even with Postgres and Parquet.

## There are plenty of optimizations left for DuckDB (and pg_mooncake)

While running ClickBench, we identified [several areas of improvement](https://github.com/Mooncake-Labs/pg_mooncake/issues/82) for both DuckDB and `pg_mooncake`.

We're excited to work on these optimizations with our community, contribute upstream changes to DuckDB, or implement them as DuckDB `OptimizerExtension` hooks.

We'd love to make DuckDB on Parquet even faster; making open formats even more a reality.

🥮
