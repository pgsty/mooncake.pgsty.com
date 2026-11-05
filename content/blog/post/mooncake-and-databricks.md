---
title: "Mooncake is joining Databricks!"
date: 2025-10-01
description: "Unifying the operational (Postgres / Lakebase) and intelligence (Lakehouse) data estates. The right way."
author: "[Mooncake Labs Team](https://github.com/Mooncake-Labs)"
authors: ["mooncake-labs", "zhou-sun", "cheng-chen", "pranav-aurora"]
tags:
  - "announcement"
  - "pg_mooncake"
  - "lakehouse"
  - "postgresql"
upstream_link: "https://www.mooncake.dev/blog/mooncake-and-databricks"
upstream_copyright: "© 2025 Mooncake Labs Inc."
aliases:
  - "/blog/mooncake-and-databricks/"
images: ["/blog/covers/mooncake-and-databricks.svg"]
---

Thirteen months ago, we started Mooncake to bring the data intelligence stack that powers giants like OpenAI to every vibe-coded app and developer. From first prompt to IPO.

Today, we're joining forces with Databricks.
The mission continues: make [Lakebase](https://www.databricks.com/product/lakebase) and the Lakehouse feel like one.

---

For a decade, we thought the final form of a database was one that could do it all. Fast updates, transactions, analytics. For database people, this was HTAP. It never quite landed. Zhou and Cheng built it. Pranav tried to sell it. It was hard.

Rebuild both sides, and the end product compromises on both.

## Well, what if you didn't? 🥮

People (and now agents) already have a default OLTP: Postgres. And they love it.

They already have a Lakehouse. And they know how to pull intelligence from it with their engines of choice (Apache Spark, Snowflake, DuckDB, Trino) or their agents ([Databricks Agent Bricks](https://www.databricks.com/product/artificial-intelligence/agent-bricks)).

On both sides, the winners are clear. The architecture is cloud-first. The community is behind it. For the first time in databases, the two estates have clear anchors.

So… what if they just worked together?

## For the developer

Your apps start on Postgres. As soon as you hit PMF, that same data is ready for analytics and AI with best-in-class Lakehouse tools... No extra pipelines, no CDC. Postgres is just synced to your Lakehouse.

And all that intelligence can be served with your apps with just Postgres and the [`pg_mooncake`](/docs/intro/) extension.

## For the enterprise

For modern enterprises, Postgres + Lakehouse is already the stack. Data engineers move data between them (ETL, rETL); and more engineers manage and optimize the Lakehouse.

With Mooncake, the whole stack just works out of the box; without needing a Debezium + Kafka + Flink stack. 🙂

## For the agent

We see two kinds of data <-> agent interactions:

1. Agents that build apps on Postgres (Lovable, Replit).
2. Agents that analyze and understand data (Agent Bricks).

Now, they can work together:

- On the same data.
- At agent scale, with 10,000s running at the same time.
- Without manual & human ETL pipelines connecting the two 🙂

## Thank you, and Day 0 again for us

To everyone who believed (users, design partners, investors, open source contributors): thank you.

`pg_mooncake` will stay open source, alive, and a core part of the community. We'll keep pushing to get it into every Postgres.

With Databricks, Mooncake now holds both estates: Postgres (Lakebase) and the Lakehouse. And we're fired up for the experience we can deliver to customers and agents.

At last, the two sides feel like one.

-- Zhou, Cheng, Pranav, Nolan, Hao, Paul.
🥮
