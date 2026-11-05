---
title: "What does Analytics in Postgres really mean?"
date: 2025-03-23
description: "From Level 0 SQL tuning to Level 3 real-time OLTP-to-columnstore sync: what developers actually want from Analytics in Postgres."
author: "[Zhou Sun](https://github.com/zhousun) · [Mooncake Labs](https://github.com/Mooncake-Labs)"
authors: ["zhou-sun"]
tags:
  - "postgresql"
  - "pg_mooncake"
  - "analytics"
  - "musings"
upstream_link: "https://www.mooncake.dev/blog/why-postgres-analytics"
upstream_copyright: "© 2025 Zhou Sun (Mooncake Labs Inc.)"
aliases:
  - "/blog/why-postgres-analytics/"
images: ["/blog/covers/why-postgres-analytics.jpg"]
---

Few areas in databases are hotter right now than extending Postgres to support analytics queries. This isn't a particularly novel area either –– there have been plenty of attempts in the last decade:

![Timelines](/images/blog/pganalytics-timeline.jpg)

Here is what it means to our customers –– and why the problem remains largely unsolved, despite our first attempt with [`pg_mooncake`](/docs/intro/).

## Level 0: I just run analytics queries on my Postgres tables

You'll be surprised how far this can go with proper indexes, statistics, query tuning, and materialized views—people really overthink this.

However, as data volume and query complexity grow, the system starts to fall apart—indexes hurt write performance, materialized views can't keep up, and certain queries become too slow to execute.

Eventually, you reach a point where you just need to store data in a columnar format. Lucky you.

## Level 1: I want to use psql to query my columnar data

This resonates with product engineers because it simplifies their life. They can manage a familiar client and leverage an [ORM](/blog/post/pgmooncake-drizzle/) that's already set up. Plus, they can join analytics tables with operational tables directly in Postgres. There are two schools of thought here:

**1. `pg_duckdb`** (embedded [DuckDB](https://github.com/duckdb/pg_duckdb) in Postgres)

Query columnar files (Parquet, CSV, etc.) with the embedded DuckDB execution, then stream the results back to Postgres.

**2. Postgres FDW** (often the [ClickHouse](https://supabase.com/docs/guides/database/extensions/wrappers/clickhouse) FDW)

Query ClickHouse tables from Postgres, but queries execute in ClickHouse itself.

In both cases, queries are executed by a vectorized query engine. The key difference lies in where the analytic query is executed—either within your Postgres instance or on external compute.

There's also an assumption here: your data already exists in a columnar format (e.g., Parquet files or ClickHouse tables).

Spoiler: It doesn't.

## Level 2: I want to write and manage my columnar data with Postgres

Instead of setting up an ETL tool and introducing a specialized analytics database as the destination, I just want to use Postgres.

This is what we solved with `pg_mooncake` v0.1 by introducing [columnstore tables](/blog/post/how-we-built-pgmooncake/). You can create and transactionally write, delete, and update rows in columnstore tables using Postgres just like with a regular table. Queries on these tables are executed with DuckDB. The [2024 Pavlo review](https://www.cs.cmu.edu/~pavlo/blog/2025/01/2024-databases-retrospective.html) highlights our innovation here.

This approach is similar to that of [Crunchy Data Warehouse](https://www.crunchydata.com/products/warehouse). Both use open data formats (Iceberg, Delta Lake, Parquet) for columnar storage, enabling elite performance ([Top 10 in ClickBench](/blog/post/clickbench-v0.1/)) without any vendor lock-in on data.

We were very happy with the [initial version](/blog/release/pgmooncake-v01/) of `pg_mooncake`. But it's not enough.

## Level 3: I need the columnstore to be up-to-date with my Postgres heap table

The user story here is *"My app does all kinds of inserts, updates, deletes; and I need to serve analytics on up-to-date data."* This request is very common amongst app-facing analytics. There are two approaches here:

**1. A magical 'operational columnstore' in Postgres.**

A columnstore table that handles ACID transactions, indexing, updates, deletes, prepared statements, triggers, and arbitrary query shapes may sound like magic, but it's possible.

At SingleStore, we built a hybrid transactional-analytical processing (HTAP) system where the columnstore was the source of truth. The reality is, it took us a decade of work –– and still wasn't 'OLTP' enough.

We thought `pg_mooncake` could do the same in Postgres, but adding full operational capabilities as an extension proved tough. Ultimately, we'd be competing with Postgres itself—its native heap tables are too powerful, with so many features and extensions already built around them (see the discussion on [Hacker News](https://news.ycombinator.com/item?id=43270712)).

**2. Replicate Postgres tables into a specialized analytics system.**

For example: [ClickPipes + ClickHouse](https://clickhouse.com/cloud/clickpipes).

Postgres provides robust and efficient CDC (change data capture) at the WAL level, ensuring reliable, low-latency updates. These changes can be applied to an OLAP system like ClickHouse.

ClickHouse handles the append-only case by buffering inserts in memory and periodically flushing them. Great.

But it's still not enough. With concurrent updates and deletes, ClickHouse ends up storing multiple versions of the same row. Now, it's on you to define deduplication logic to clean up these duplicates at merge time. Good luck with that.

## You really need a columnstore that can keep up with Postgres-like OLTP as the source

So far, it's still an unsolved problem.

You want the properties of a modern columnstore—open formats on object storage—but you also need it to handle OLTP concurrency and data updates. And you'll want to write to it and manage it directly in Postgres.

Think about it—this is a crazy requirement… a list of immutable files on disk or blob store that needs to be rapidly updated.

That is exactly what we built in [`pg_mooncake` v0.2 / v0.3](/docs/intro/architecture/) with [Moonlink](/docs/intro/moonlink/). 🥮⭐
