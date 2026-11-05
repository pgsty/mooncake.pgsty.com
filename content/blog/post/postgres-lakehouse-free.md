---
title: "but, my Postgres (+ lakehouse) is free"
date: 2025-06-13
description: "Snowflake and Databricks paid billions for their Postgres. Why Postgres + Apache Iceberg is the open, free stack for modern apps and AI agents."
author: "[Zhou Sun](https://github.com/zhousun) · [Mooncake Labs](https://github.com/Mooncake-Labs)"
authors: ["zhou-sun"]
tags:
  - "postgresql"
  - "iceberg"
  - "lakehouse"
  - "pg_mooncake"
upstream_link: "https://www.mooncake.dev/blog/postgres-lakehouse-free"
upstream_copyright: "© 2025 Zhou Sun (Mooncake Labs Inc.)"
aliases:
  - "/blog/postgres-lakehouse-free/"
images: ["/blog/covers/postgres-lakehouse-free.svg"]
---

**Disclaimer:** Your Postgres and Lakehouse are free and open too. You don't need to be (or spend like) a giant to use them.

## Why Postgres + Lakehouse?

### Reason #1: If you believe in AI, this is the agent stack

Agents need memory. Both working memory and longer-term knowledge.

Working memory has to be instant, reliable, and accurate, just like app state. What's the best place to store it? Postgres. That's true for both apps and agents. This state is typically tied to an individual user, tenant, or agent.

Longer-term knowledge is different. The raw inputs are massive, messy, and shared across users, tenants, and agents—logs, LLM inputs and outputs, interactions. The goal is to 'get smarter'.

What's the best way to store these raw inputs? A lakehouse. Infinitely scalable, object-store-centric, and open to the best tools/engines for processing, analytics, search, MLOps, all available on the same data. And you're only paying for what you're using.

The classic "data engineering" pipeline was about extracting insights and intelligence from app data to make apps smarter, stickier, and better. The modern data stack was built around this flow:

`App data → Bronze (raw) → Silver (processed) → Gold (modelled) → Serve the insight/intelligence to Apps`

Turns out, the same flow applies to agents:

`Agent context → Raw memory → Knowledge → Better context`

**Postgres → Lake → Postgres**; it's full circle.

### Reason #2: The industry needs a new OLTP winner... there's A LOT of shareholder value at stake

OLTP is the new battlefield, and differentiator, for the giants and the hyperscalers.

When Snowflake first came out, everyone was pretty amazed: a cloud-native data warehouse where, no matter how complex the query or how large the dataset, you got results. It just worked.

But 10 years later, much of the tech behind Snowflake is being commoditized:

1. Separation of storage and compute, now table stakes with object stores and smart caching.
2. Vectorized execution, now runnable on your laptop with DuckDB.

This made the new lakehouse architecture inevitable: put data and metadata in object storage, and query it with a vectorized engine.

Sure, it's not as fast as Snowflake. Not as fancy. Not the same magical out-of-the-box experience. But the DIY-Snowflake tradeoffs are real.

The analytics market is no longer black and white—where warehousing either worked or didn't, and there was clear value to capture as a provider. Now, it feels incremental. Commoditized.

So how do you 10x shareholder value as an analytics company? You look next door—at OLTP.

For 40 years, Oracle, SQL Server, and DB2 seemed unbeatable for tier-1 workloads, while MySQL dominated tier-3. But things are slowly changing:

1. Hardware is getting better
2. The cloud is getting better
3. MySQL got bought by Oracle
4. Postgres is improving at a rapid pace
5. OLTP workloads aren't getting bigger

Suddenly, Postgres is good enough for tier-2—even some tier-1 workloads. It's easy to get behind: open-source, reliable, extensible, and fast-shipping compared to the MySQL crowd.

## This is just another 'Zhou opinion', right?

Err, let's see about that:

- **Microsoft:** Fabric (lakehouse) has SQL Server database in it with [mirroring](https://learn.microsoft.com/en-us/fabric/database/mirrored-database/overview) already; guess what will come next? A Postgres.
- **Google:** [AlloyDB (Postgres) + BigQuery](https://cloud.google.com/blog/products/data-analytics/enhancing-biglake-for-iceberg-lakehouses). Both will connect through data in Iceberg.
- **Amazon:** Aurora (increasingly Postgres-native) and RDS, with S3 Tables, Glue, SageMaker. S3 is becoming an Iceberg-backed lakehouse itself. Firehose is already connecting them.
- **Supabase:** Check their recent (great) blog: [Open Data Standards: Postgres, OTel, Iceberg](https://supabase.com/blog/open-data-standards-postgres-otel-iceberg).
- **ClickHouse:** After acquiring PeerDB, Postgres is now the #1 source for ClickPipes, and they're working on deep Iceberg integration where ClickHouse becomes an execution engine.

Postgres + Iceberg is everyone's horse in the race. And the win comes from a great developer experience between the two. This isn't so much about bolting analytics (lakehouse) onto operational systems, sacrificing both. We've learnt this from the [HTAP market](/blog/post/htap-is-dead/).

This is more about getting the best-in-class OLTP (likely Postgres), and the best-in-class OLAP (likely lakehouse) to work independently (not sacrificing each other), but together. And the combined OLTP + OLAP market is to win. Play ball.

![htap-vs-today](/images/blog/htap-vs-today.svg)

## Postgres + Lakehouse will always stay free

While the giants first spend billions getting a Postgres, and then gluing it into their fortress (lakehouse), [`pg_mooncake`](/docs/intro/) is already on the shelf with a sub-second Postgres-to-Iceberg sync.

It's also MIT licensed 🙂
