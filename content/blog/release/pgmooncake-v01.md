---
title: "The easiest way to Analytics in Postgres: pg_mooncake v0.1"
date: 2025-01-11
description: "pg_mooncake comes out of beta, bringing native columnstore tables and DuckDB vectorized execution to Postgres."
author: "[Mooncake Labs Team](https://github.com/Mooncake-Labs)"
authors: ["mooncake-labs", "zhou-sun", "cheng-chen", "pranav-aurora"]
tags:
  - "release"
  - "pg_mooncake"
  - "duckdb"
upstream_link: "https://www.mooncake.dev/blog/pgmooncake-v01"
upstream_copyright: "© 2025 Mooncake Labs Inc."
aliases:
  - "/blog/pgmooncake-v01/"
  - "/blog/post/pgmooncake-v01/"
images: ["/blog/covers/pgmooncake-v01.svg"]
---

We [announced](/blog/post/how-we-built-pgmooncake/) `pg_mooncake` to the world on Day 60.

Today, Day 131, `pg_mooncake` comes out of [beta](https://github.com/Mooncake-Labs/pg_mooncake/releases/tag/v0.1.0).

`pg_mooncake` wins on **ease** and **performance**. So, we doubled down for v0.1. That's it.

## The Easiest Way to Fast Analytics in Postgres

With a native columnstore table in Postgres, `pg_mooncake` brings familiar table semantics to the way you run analytics. Columnstore tables support transactional operations like `INSERT`, `SELECT`, `UPDATE`, `DELETE`, and `COPY`, alongside joins with regular Postgres heap tables.

In v0.1, we've made it even easier to [load data](/docs/v0.1/load-data/) into columnstore tables:

1. From Parquet, CSV, and JSON files:

```sql
SELECT * FROM mooncake.read_parquet('<file_path>');
```

2. From Hugging Face datasets:

```sql
COPY reddit_comments FROM 'hf://datasets/fddemarco/pushshift-reddit-comments/data/RC_2012-01.parquet';
```

3. From existing Iceberg and Delta Lake tables:

```sql
SELECT * FROM mooncake.iceberg_scan('s3://bucket/table');
```

## Better performance for time-series workloads

`pg_mooncake` is the only Postgres extension that adds columnar storage and vectorized execution.

In v0.1, we added file statistics and skipping. Customers run time-series and analytics workloads without traditional sharding.

Our [ClickBench](https://github.com/ClickHouse/ClickBench/pull/284) results land next week. (Hint: [top 10](/blog/post/clickbench-v0.1/) 🙂). Perhaps Postgres is indeed a Great Real-Time Analytics Database.

## Looking Ahead to v0.2

We will double down on two areas: DevEx and time-series workloads. Planned improvements include:

1. Enhanced support for small writes, updates, and deletes
2. Syncing rowstore tables to columnstore tables
3. Indexes (secondary indexes and sort keys)
4. Time-series functions

## To our community, thank you

It takes a village. Thank you to our community, customers, contributors, and Postgres partners like [Neon](https://neon.tech/) and [Supabase](https://supabase.com/). Your support has been invaluable.

Our favorite metric is the number of contributors to `pg_mooncake` growing.

The momentum behind `pg_mooncake` is clear. Analytics in Postgres is indeed a reality 🥮
