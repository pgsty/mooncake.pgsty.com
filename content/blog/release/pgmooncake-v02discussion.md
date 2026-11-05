---
title: "pg_mooncake v0.2: what we're cooking"
date: 2025-02-11
description: "The release where out-of-the-box analytics becomes reality: logical replication into columnstore tables, rowstore write buffering, and Apache Iceberg."
author: "[Pranav Aurora](https://github.com/paurora17) · [Mooncake Labs](https://github.com/Mooncake-Labs)"
authors: ["pranav-aurora"]
tags:
  - "release"
  - "pg_mooncake"
  - "moonlink"
  - "iceberg"
upstream_link: "https://www.mooncake.dev/blog/pgmooncake-v02discussion"
upstream_copyright: "© 2025 Pranav Aurora (Mooncake Labs Inc.)"
aliases:
  - "/blog/pgmooncake-v02discussion/"
  - "/blog/post/pgmooncake-v02discussion/"
images: ["/blog/covers/pgmooncake-v02discussion.svg"]
---

With v0.1, we proved that Postgres can deliver great analytics performance. Our approach combined two key pieces—DuckDB vectorized engine and a columnstore table—making [`pg_mooncake`](/docs/intro/) the only extension in Postgres that integrates both.

The results speak for themselves: `pg_mooncake` ranks in [ClickBench's top 10](/blog/post/clickbench-v0.1/), and we built the fastest Parquet-based engine along the way.

Now, with v0.2, we're tackling the next big challenge; we call it **out-of-the-box analytics**.

## First, why in-Postgres analytics?

Applications often have their first analytics needs far before they have their first data warehouse or analytics system.

We've seen this story over and over again. The typical path involves delaying the roadmap, setting up data replication into a separate system, hiring engineers to maintain the pipeline—all while stitching Postgres data with analytics data at the application level.

`pg_mooncake` eliminates this complexity. With columnstore tables, developers get a native Postgres experience for both transactional and analytical workloads. No separate systems, no complex pipelines—just Postgres.

In v0.2, we are focused on making columnstore tables easier to get started for more workloads. In this blog, we cover the areas under active development:

### 1. Full Postgres Table Access Method (TAM) for Columnstore Tables [(#80)](https://github.com/Mooncake-Labs/pg_mooncake/issues/80)

In v0.1, all columnstore queries ran through DuckDB. This delivered performance, but meant missing Postgres features like data-modifying CTEs (e.g., deleting rows, returning results, and inserting them into another table) and triggers.

In v0.2, we explore exposing columnstore tables through a Postgres table access method and logical replication architecture, allowing DuckDB to serve as the fast execution engine while preserving full Postgres table compatibility.

### 2. Logical Replication into columnstore tables [(#90)](https://github.com/Mooncake-Labs/pg_mooncake/issues/90)

Users often adopt `pg_mooncake` after encountering slow queries on their existing Postgres tables. With logical replication, we make it even easier to accelerate analytics without changing application write patterns—simply replicate data from heap tables into columnstore tables via [`mooncake.create_table`](/docs/reference/create-columnstore/).

This significantly enhances `pg_mooncake`'s deployability, no matter where your Postgres is hosted. You can run `pg_mooncake` alongside your existing Postgres deployments and seamlessly replicate data from heap tables into columnstore tables.

### 3. Small Inserts with an In-Memory / Rowstore Buffer [(#89)](https://github.com/Mooncake-Labs/pg_mooncake/issues/89)

Logical replication introduces a challenge: how do we handle frequent small inserts without generating a new Parquet file and metadata log for every transaction?

In v0.2 (powered by [Moonlink](/docs/intro/moonlink/)), small inserts go into an Arrow write buffer, while background flushes write compacted Parquet files. When querying a columnstore table, `duckdb_mooncake` scans both the buffered data and Parquet files. Once the buffer exceeds a threshold, it flushes to Parquet. This approach decouples Parquet writes from OLTP transactions, significantly reducing write amplification.

This is a major unlock, making columnstore tables viable for high-concurrency OLTP mirroring without requiring batched inserts—especially for logging, HTAP, and time-series workloads.

## So, where does that put us?

`pg_mooncake` is the easiest way to get fast analytics inside Postgres. With v0.2 (and PGSTY's [`v0.3.0` release](/blog/release/pg-mooncake-0.3.0/)), key use cases improve even further:

1. **User-facing analytics with Postgres** – Full ORM support, joins with regular Postgres tables, and only 1 system to manage.
2. **Logs, chat history, time series** – Optimized for high-rate ingest with the benefits of Parquet compression and low storage costs.
3. **Complete Data Lake out of the box** – Postgres + `pg_mooncake` writing data transactionally to Apache Iceberg, combined with the fastest Parquet-based execution with [file skipping and segment elimination](/blog/post/duckdb-parquet/).
