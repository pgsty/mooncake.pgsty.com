---
title: "No, Iceberg won’t fix your data stack."
date: 2025-07-21
description: "Apache Iceberg is great for Netflix-scale batch lakes, but painful for real-time apps unless we give it true RDBMS ergonomics: concurrent writes, online compaction, and native indexing."
author: "[Zhou Sun](https://github.com/zhousun) · [Mooncake Labs](https://github.com/Mooncake-Labs)"
authors: ["zhou-sun"]
tags:
  - "iceberg"
  - "moonlink"
  - "lakehouse"
  - "musings"
upstream_link: "https://www.mooncake.dev/blog/iceberg-is-terrible"
upstream_copyright: "© 2025 Zhou Sun (Mooncake Labs Inc.)"
aliases:
  - "/blog/iceberg-is-terrible/"
images: ["/blog/covers/iceberg-is-terrible.svg"]
---

Life is expectations vs reality. Here is one for Apache [Iceberg](https://iceberg.apache.org/) – a favorite amongst the data community.

## Expectations: Iceberg is the solution to all my data pains

See, the core of Iceberg is pretty neat:

1. Keep all data in object storage in open file formats like Parquet.
2. Fool any execution engine (DuckDB, ClickHouse, Spark, Snowflake, etc.) into thinking these files are a table and query them with SQL directly.
3. *[Ongoing progress]* Get exceptional performance on these tables, without having to load data into a system-specific format.

And with clever design you get:

1. Interoperability across execution engines. You don't need to load data into a proprietary format to get great performance.
2. ACID transactions + schema evolution.
3. True separation of storage and compute.
4. Time travel + versioning.

Iceberg was initially built by/for BIG DATA teams at Netflix, Apple, et al. More recently, it's being built for you and me (see Supabase [Analytics Buckets](https://supabase.com/blog/analytics-buckets) + [Tiger Lake](https://www.tigerdata.com/blog/tiger-lake-a-new-architecture-for-real-time-analytical-systems-and-agents)). Vendors are now putting in the work to create a great experience within their platforms.

Great. So I, the user, (1) own data in object store, (2) am not locked into any vendor, and (3) can query it without loading data into a specific system. That should be it.

## Reality: Iceberg is only cool if you're willing to build your own Snowflake (BYOS)

For Apple and Netflix, it's WELL worth the hundreds of engineers to build their own Snowflake or Databricks on raw cloud storage. For you and me, I'm really not sure.

See, you and I start on Iceberg and expect it to JUST work, like Postgres or ClickHouse. I insert/upsert data, load files, and query it. It's not that simple:

**1. Metadata overhead:** Iceberg tracks snapshots, manifests, manifest lists, and table-metadata JSONs. A one-row update triggers four S3 writes (each hundreds of ms). A regular RDBMS on SSD handles this in `<1 ms`. The result of all these metadata updates is commonly known as the "small file explosion". And it's up to the user to manage the maintenance of these files. This is a WILD concept for users coming from the RDBMS world where all of this is on 'auto-pilot'.

**2. Limited write concurrency:** Iceberg uses optimistic concurrency. Each writer tries to commit new metadata, assuming no conflict. If two collide, one fails and retries. This guarantees serializability, but at the cost of write throughput. To contrast: Iceberg handles a few commits per minute on the same table without collisions. An RDBMS can handle thousands of transactions per second: each with full isolation, indexing, and durability.

**3. Read / Write performance tradeoffs:** From the Snowflake Iceberg [docs](https://docs.snowflake.com/en/user-guide/tables-iceberg): *"performance primarily depends on how efficiently the Parquet files are written"*. If another engine writes sub-optimally, Snowflake's query speed suffers. Investing in Iceberg requires investing in partitioning, sorting, and compaction jobs to get good performance. The classic is the `OPTIMIZE` operation (e.g., via Spark or Trino) to merge small files, at additional compute cost. This extra maintenance tax is well worth it at Netflix scale. But for you and me – we're just used to a cloud DW that just works.

**4. Batch + stale data:** Iceberg was built for slow-changing datasets. Think huge fact tables with heavy batch writes, not high-concurrency row updates. It lacks real indexes / streaming. You still need a separate real-time columnar system.

## So, who's fixing Iceberg, and how?

- **AWS / R2:** *"We'll host your files. The rest is your problem."* They give you CDC connectors, a basic catalog, and occasional compaction if you pay for it. That's it. File explosion? Your bill. You want fast queries? Run your own optimization jobs.
- **Snowflake:** *"It's Iceberg-compatible — as long as we own it."* You can read external Iceberg tables. But if you want write access, performance, or optimizations? Convert it to a Snowflake-managed Iceberg table — which is basically Snowflake with an Iceberg API skin. For example, Snowflake writes 16MB Parquet files, which works perfectly with their storage nodes and disk cache. Imagine the performance without them (the recommended size for other engines is usually 256MB to 1GB).
- **DuckLake (DuckDB devs):** *"The spec is wrong. Let's rethink metadata."* Instead of dozens of JSON/Avro files in S3, store metadata in an actual embedded database (DuckDB, SQLite). Way faster planning, better concurrency. Essentially it is challenging the Iceberg design so the engine can just read from object store.
- **Hudi / Paimon:** *"The whole Iceberg format is too broken. We built a new one."* Event-stream-driven companies like Uber and Alibaba have different use cases, so they introduced these new formats. They bake compaction, indexing, and streaming ingest into the format. Hudi has table services; Paimon uses LSM trees.

## What if Iceberg just had regular database ergonomics?

To the outsider, database and big data engineers might look 'same-same'; but we look at the same spec very differently.

Big data people (the Iceberg OGs) see 'table' and think JSON metadata files, compaction pipelines, eventually consistent catalog state, maybe Spark will clean it up later.

As a database kernel person, I immediately think indexing, concurrency, transaction isolation, hot writes, query optimization. I keep wondering.... What if we just 'copied' the obvious stuff from real databases and layered it around Iceberg? What if we stopped treating it like a format to worship, and started treating it like a backend storage layer for a proper RDBMS?

Let's set some bare-minimum expectations, things even SQLite does without breaking a sweat:

**1. Concurrent Writes + Streaming Ingest That Works**

Stop the "single writer" nonsense. No more retry storms. No more fear of write conflicts on concurrent jobs. Let multiple writers append, update, and even delete data — without overwriting each other or bloating S3 with metadata garbage.

**2. Automatic Optimization, That Never Conflicts with Writes**

Background compaction should just happen. And it should never require a lock or cause a conflict with a user query or write. Optimizing a table shouldn't be a "maintenance window" — it should be invisible, online, constant.

**3. Built-in Indexing and Caching, Not an Afterthought**

Not everything needs to be a billion-row scan. Let me define an index — zonemap, Bloom, bitmap, anything — and store it with the table, queryable by any engine.

## The Crazy Part? It's Actually Not That Hard.

This isn't impossible. It's not even particularly original. We've been doing this for decades in RDBMS land:

- We can have a simple WAL to mark committed logs.
- We can have a primary key index to apply updates and deletes instead of full scans.
- We can save the 'compaction' operation state, and remap the deletions that happened in between.
- We can also just index the Parquet files and write them as Puffin blobs.

You keep the open format, the decoupled compute, the time travel, the engine interoperability. But you get actual database ergonomics. You get performance without handholding. You get operations that make sense.

Iceberg doesn't need to be replaced. It just needs help thinking like a database.

That's 🥮. Starting with [Moonlink](/docs/intro/moonlink/): sub-second Postgres-to-Iceberg sync that just works :).
