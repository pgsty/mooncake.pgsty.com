---
title: "pg_mooncake + Neon: serverless analytics in Postgres"
date: 2025-01-07
description: "How we accidentally built the best serverless database for analytics by combining Neon's storage engine with pg_mooncake's lakehouse architecture."
author: "[Pranav Aurora](https://github.com/paurora17) · [Mooncake Labs](https://github.com/Mooncake-Labs)"
authors: ["pranav-aurora"]
tags:
  - "postgresql"
  - "pg_mooncake"
  - "analytics"
  - "lakehouse"
upstream_link: "https://www.mooncake.dev/blog/pgmooncake-neon"
upstream_copyright: "© 2025 Pranav Aurora (Mooncake Labs Inc.)"
aliases:
  - "/blog/pgmooncake-neon/"
images: ["/blog/covers/pgmooncake-neon.svg"]
---

[`pg_mooncake`](/docs/intro/) launched in beta two months ago. It adds columnar storage and a vectorized engine to Postgres.

Over the last two months, with our customers, we've realized we accidentally built the best serverless database for analytics. Here's the story:

## 1. pg_mooncake 🤝 Neon storage engine

Neon innovated significantly on its [storage engine](https://neon.tech/blog/get-page-at-lsn).

There's a great [thread](https://x.com/nikitabase/status/1723579854266966399) by Nikita on this. This storage engine is how Neon can achieve true separation of storage & compute. This leads to an exceptional DX around branching, scale-to-zero, read replicas, instant provisioning... All of these are goodies of a true serverless Postgres.

![Neon Storage engine](/images/blog/blog5-neon.svg)

[`pg_mooncake`'s architecture](/blog/post/how-we-built-pgmooncake/) also involves true separation of storage and compute. Data is stored in object store (local file system or S3), and only metadata is stored in Postgres.

![pg_mooncake architecture](/images/blog/blog5-arc.svg)

This is the [Lakehouse architecture](https://www.cidrdb.org/cidr2021/papers/cidr2021_paper17.pdf). The Lakehouse is how data in some of the largest companies in the world is stored and analyzed in a cost-efficient and serverless manner.

> TL;DR on the Lakehouse: store all data in object store in a universal format. Query this data directly as a Pandas dataframe, with Spark, or with DuckDB in a serverless way.

`pg_mooncake`'s goal is to bring this flexibility, scalability, and 'serverless' analytics to every Postgres application.

## 2. Scale everything to zero

Combining Neon's storage and our analytics architecture –– you get complete separation of storage and compute for transactional and analytical workloads, while keeping all table metadata in Postgres.

![separation](/images/blog/blog5-separation.svg)

With this serverless architecture, and combining analytical and transactional tables in one system, we've seen customers do cool things like:

1. Separate and scale analytical workloads separately from transactional workloads.
2. Sync changes from heap tables into columnstore tables using a separate compute.
3. Join columnstore tables with heap tables for BI and dashboards.
4. And finally, run entire analytics services that scale to zero.

Customers like [Inkeep](https://www.inkeep.com/) ship their application, fast BI dashboards, and their [analytics services](https://docs.inkeep.com/analytics/usage-reports) entirely in Postgres. Each of their services scales independently, while all data and table metadata stays in Postgres. It's pretty neat.

## 3. 'Scale to zero' analytics with Python

This is where it gets fun.

`pg_mooncake` writes data in the *standard* analytics formats [Iceberg](https://iceberg.apache.org/) and [Delta](https://delta.io/) to your object store. These act as metadata layers over Parquet files that make data files 'feel' like a table to any query engine (Pandas, Polars, Spark, DuckDB).

A common workload we've seen is `pg_mooncake` customers querying and transforming columnstore tables using Python. It's very simple to create a dataframe from your columnstore table (see [Cloud Storage](/docs/v0.1/cloud-storage/) and [Iceberg Export](/docs/reference/iceberg/) for more info).

We've also seen requests for running semantic query engines like [LOTUS](https://github.com/guestrin-lab/lotus) on Postgres.

![Lotus on PG](/images/blog/blog5-lotus.svg)

## 4. Get started today!

Read our [Getting Started guide](/docs/getting-started/) for creating your first columnstore table in Postgres.

> Hint: it's easy :)
