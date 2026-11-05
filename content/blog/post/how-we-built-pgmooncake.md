---
title: "pg_mooncake: Fast Analytics in Postgres with Columnstore Tables and DuckDB"
date: 2024-11-06
description: "pg_mooncake brings columnstore tables with DuckDB execution to Postgres for fast analytics, supporting transactional inserts, updates, and deletes."
author: "[Cheng Chen](https://github.com/dpxcc) · [Mooncake Labs](https://github.com/Mooncake-Labs)"
authors: ["cheng-chen"]
tags:
  - "postgresql"
  - "duckdb"
  - "pg_mooncake"
  - "iceberg"
upstream_link: "https://www.mooncake.dev/blog/how-we-built-pgmooncake"
upstream_copyright: "© 2024 Cheng Chen (Mooncake Labs Inc.)"
aliases:
  - "/blog/how-we-built-pgmooncake/"
images: ["/blog/covers/how-we-built-pgmooncake.jpg"]
---

[`pg_mooncake`](/docs/intro/) brings columnstore tables with DuckDB execution to Postgres for fast analytics.

It supports transactional inserts, updates, and deletes, just like regular Postgres tables. Data is written with Delta Lake (and Apache Iceberg in v0.2+) table metadata, allowing it to be queried outside of Postgres.

## Why another Postgres analytics extension?

Postgres is the most popular database these days, but it's bad at analytics. Numerous attempts have been made to address this, but with limited success so far. Fast analytics require a distinct set of techniques, such as columnar storage, vectorized execution, and late materialization, etc. Early projects like Citus & Timescale added columnar storage, but there was no good vectorized execution to leverage the format.

A decade ago, this would have been a massive project, but today we have DuckDB.

For the unfamiliar, think of DuckDB as SQLite for analytics. It is designed to be embedded in a host process, in our case, Postgres. It's incredibly fast for analytics, ranking among the tops on ClickBench. It has extensions to use external compute to scale beyond a single node. Even better, its SQL syntax follows Postgres closely, making the integration easier.

Recently, we've seen a trend to embed DuckDB inside Postgres. Extensions like `pg_duckdb` and `pg_analytics` are designed for querying external columnar storage in Postgres, but they can't write out data in those formats via transactional insert/update/deletes.

`pg_mooncake` brings a columnstore table with both storage and compute that can leverage the format.

![Mooncake Venn Diagram](/images/blog/blog_4venn.jpg)

## How pg_mooncake was built

The first decision to make is the choice of storage format. While a proprietary format could be optimized for best performance, an open format allows sharing across engines - like a mooncake meant to be shared with friends. `pg_mooncake` chooses Parquet as its file format, with added table metadata from open formats like Iceberg and Delta Lake. This ensures that a mooncake table is directly readable by most engines.

![Parquet File Format](/images/blog/blog_4parquet.jpg)

Table operations can be viewed as operations on these Parquet files. `INSERT` and `COPY` will create new Parquet files, `UPDATE` and `DELETE` will remove corresponding Parquet files and create new ones with modifications. Yes, deleting one row from a table with a one million row Parquet file could mean writing a new one with 999,999 rows. In the future we will introduce deletion vectors to solve it by marking rows as deleted without actually rewriting the file.

At its core, `pg_mooncake` is a TAM for columnstore table interface within Postgres + a storage extension for Parquet files within DuckDB. Table metadata, including addition and deletion of Parquet files, is stored inside a Postgres table for transactional consistency. Queries involving columnstore tables are routed from Postgres to DuckDB and the results are streamed back to Postgres via `pg_duckdb`.

This integration is made possible because both DuckDB and Postgres are highly extensible, allowing users to implement their own storage, planner, and executor. Even their native tables are implemented using the same mechanisms, enabling third-party tables to achieve the same functionality with minimal overhead.

## Query Lifetime

Let's walk through the lifetime of a query.

When a SQL query comes to Postgres, Postgres parses it and generates a plan for it. When the query involves columnstore tables, it is treated as an analytics query and will be executed entirely using DuckDB and the results will be streamed back to Postgres. Minor query rewrites are applied to bridge the SQL syntax differences.

A DuckDB storage extension is added to interact with our storage format, implemented similarly to DuckDB's own storage. Physical operators like `TableScan`, `Insert`, `Update`, `Delete` are implemented for our storage format. Moreover, `pg_duckdb` implements read from Postgres regular tables, allowing our columnstore tables to join with Postgres regular tables within DuckDB.

![Query Lifetime Diagram](/images/blog/blog_4query.jpg)

## Transactional Updates

To support `DELETE` and `UPDATE`, an implicit `row_id` column is populated during the `TableScan`, consisting of `(file_id, row_offset)` to identify the rows efficiently. The physical delete operator tracks all the `row_ids` marked for deletion and, upon completion, reads all undeleted rows from affected Parquet files and writes them to new Parquet files. The physical update operator follows a similar approach: it streams the updated rows to a new Parquet file, remembers the `row_ids` to delete, and deletes the original rows.

All the table metadata, including addition and deletion of Parquet files, are stored inside a Postgres table. This allows for transactional insert/update/delete. DuckDB takes a Postgres snapshot in addition to the SQL query to run, and reads all metadata from that snapshot to ensure consistency.

## What's Next

We commit to make `pg_mooncake` better and production-ready. Features like compaction, secondary index and constraints, and partitioned tables are on our roadmap.

As a company, Mooncake Labs aims to build a lakehouse for developers. Our goal is to simplify the data stack with clean Postgres and Python interfaces and `pg_mooncake` is a start in this direction.

🥮
