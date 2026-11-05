---
title: "HTAP is Dead"
date: 2025-05-05
description: "I spent the last 10 years building, and then rescuing HTAP databases. Their spirit lives on in the Lakehouse today."
author: "[Zhou Sun](https://github.com/zhousun) · [Mooncake Labs](https://github.com/Mooncake-Labs)"
authors: ["zhou-sun"]
tags:
  - "htap"
  - "lakehouse"
  - "postgresql"
  - "musings"
upstream_link: "https://www.mooncake.dev/blog/htap-is-dead"
upstream_copyright: "© 2025 Zhou Sun (Mooncake Labs Inc.)"
aliases:
  - "/blog/htap-is-dead/"
images: ["/blog/covers/htap-is-dead.jpg"]
---

This blog is inspired by Jordan Tigani's blog titled ["Big Data is Dead"](https://motherduck.com/blog/big-data-is-dead/). Jordan and I actually spent some time building an HTAP database at SingleStore.

## The good old days ('80s)

Back in the '80s, one relational database did everything. Transactions (OLTP) during the day and reports after hours (OLAP). Databases like Oracle V2 and IBM DB2 ran OLTP and OLAP on the same system; largely because data sets still fit on a few disks and compute was costly.

Nobody called it Hybrid Transactional/Analytical Processing (HTAP); it was simply the **database.**

## The great divide ('90s)

As businesses had more data and asked tougher questions, the database began to show its limits.

See, transactional and analytical workloads pull in opposite directions. OLTP requires microsecond inserts and single-row lookups, while OLAP demands full-table scans and large-scale aggregates. This created constant contention; analytics consuming I/O and cache needed for latency-sensitive transactions, and vice versa.

The solution? Isolate the workloads. By the early 2000s, the Great Divide had begun.

## The storage split (2000s)

A key technical driver behind this divide was storage architecture. OLTP systems optimized for row-based storage (fast writes + point queries). While OLAP systems chose columnar storage for efficient scans and aggregations.

By the mid-2000s, this split had become industry standard. Database pioneer Michael Stonebraker marked this shift in his [paper](https://dl.acm.org/doi/abs/10.1145/3226595.3226636), *"One Size Fits All": An Idea Whose Time Has Come and Gone*. The database started breaking up into specialized engines.

## OLTP and OLAP both ditched SQL (2000s–2010s)

Horizontal scaling pushed OLTP and OLAP even further apart.

Early distributed OLTP databases (NoSQL engines like MongoDB) dropped SQL and analytical capabilities entirely. On the analytics side, we saw the adoption of MapReduce and Data Lake architectures (Hadoop/HDFS): trading traditional RDBMS properties like strict consistency for massive throughput.

## The unexpected reconciliation (2010s)

In the 2010s, two distinct database movements gained momentum:

1. **NewSQL** (Spanner, CockroachDB, Vitess). OLTP should remain SQL-based.
2. **Cloud Data Warehouses** (Redshift, Snowflake). OLAP should be on SQL systems with stronger consistency guarantees.

On paper, these systems served very different workloads. But under the hood, they shared a lot: distributed, MPP-style execution, and SQL. OLTP and OLAP systems, in isolation, had converged on many of the same architectural principles. There was one big difference: storage engines.

We asked ourselves: what if you could combine both row and columnstore storage engines in a single database?

## Voilà, HTAP (2014)

In 2014, Gartner [introduced](https://www.gartner.com/en/documents/2657815) the term HTAP (Hybrid Transactional and Analytical Processing): the next big DB architecture.

The goal was to close the gap between operational and analytical systems. This was a necessity for emerging workloads like pricing, fraud detection, and personalization. Even at the business level, decision makers wanted now's data. Early HTAP systems showed it could be done. Well, mostly…

[SingleStoreDB](https://dl.acm.org/doi/10.1145/3514221.3526055) combined an in-memory rowstore, a disk-based columnstore, and a vectorized execution engine—supporting fast scans, seeks, filters, aggregations, and updates in a single system. Over time, we found that with modern hardware, the columnstore alone could handle a surprising number of OLTP-style queries, including point lookups and low-latency access patterns.

[TiDB](https://docs.pingcap.com/tidb/stable/tidb-architecture) took a different route, pairing its TiKV rowstore with a separate columnar engine based on ClickHouse—maintaining two copies of the data to serve both workloads.

So that should be it, right? '70s data nirvana, alas.

## The Cloud Data Warehouse was the only winner (2020s)

Cloud data warehouses have clearly won. The NewSQL movement stalled… And HTAP? It never got the attention it deserved. Despite real technical progress, it remained pre-product market fit.

**1. It's really, really hard to replace someone's OLTP system.** Take [DB-Engines'](https://db-engines.com/en/ranking) word for this: Oracle and SQL Server still sit at #1 and #3.

**2. Most workloads don't need distributed OLTP.** Hardware got faster and cheaper. A single beefy machine can handle the majority of transactional workloads. [Cursor](https://www.youtube.com/watch?v=4jDQi9P9UIw) and [OpenAI](https://www.pixelstech.net/article/1747708863-openai%3a-scaling-postgresql-to-the-next-level) are powered by a single-box Postgres instance. You'll be just fine.

**3. Cloud-native architectures favored shared-disk, not shared-nothing.** While NewSQL systems demanded fast local storage (and even in-memory durability), cloud platforms pushed toward object storage and elastic compute.

**4. OLTP and OLAP are owned by different teams.** OLTP is owned by product engineering; OLAP belongs to the data team. The incentives rarely align. No one gets promoted for "consolidating the stack".

## Your data stack forms the HTAP database (Today)

The cloud also started the move away from tightly coupled warehouses toward modular lakes built on object storage. In trying to escape the traditional warehouse/database, data teams started assembling their own custom systems, made of 'best-in-class' building blocks:

1. OLTP systems and stream processors as the WAL
2. Open table formats like Iceberg serve as the storage engine
3. Query engines like Spark and Trino for execution
4. Real-time systems like ClickHouse or Elastic function as indexes

Even in today's disaggregated data stack, the need remains the same: fast OLAP queries on fresh transactional data. This now happens through a web of streaming pipelines, cloud data lakes, and real-time query layers.

It's still HTAP; but through composition instead of consolidation of databases. It comes down to questions like:

**1. How do I apply the WAL to my storage engine?**
AKA: How do I CDC from my OLTP system to the data lake efficiently?

**2. Can I build a lower-cost index on my data lake, and keep it in sync?**
AKA: How do I ingest real-time data into the lake? Or how do I query Lake data with Postgres or Elastic functionality?

The HTAP challenge of our time comes down to making the lakehouse real-time ready.

After spending my best 10 years first starting and then rescuing it, HTAP as a monolithic database is dead.
But let the spirit live on. 🥮
