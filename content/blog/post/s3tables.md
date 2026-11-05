---
title: "wth are S3 tables"
date: 2025-01-12
description: "I studied AWS S3 Tables so you don't have to: how S3 table buckets enable catalog-free Apache Iceberg commits and what they mean for Postgres."
author: "[Zhou Sun](https://github.com/zhousun) · [Mooncake Labs](https://github.com/Mooncake-Labs)"
authors: ["zhou-sun"]
tags:
  - "s3"
  - "iceberg"
  - "lakehouse"
upstream_link: "https://www.mooncake.dev/blog/s3tables"
upstream_copyright: "© 2025 Zhou Sun (Mooncake Labs Inc.)"
aliases:
  - "/blog/s3tables/"
images: ["/blog/covers/s3tables.jpg"]
---

Amazon announced [table buckets](https://aws.amazon.com/s3/features/tables/) during re:Invent last year. An S3 bucket that's also a table? What does that mean?

**TL;DR:** S3 tables allow Iceberg tables to exist without a catalog. Let me explain.

## Iceberg vs Delta Lake

What? I thought Iceberg and Delta are just table formats? Why are we comparing the way they're implemented?

A key difference between Iceberg and Delta Lake is *"Delta tables can exist without a catalog, but Iceberg cannot"*, due to their metadata design:

**1. Delta Lake relies on the file system to get ACID in the metadata layer.**

The metadata layer in `_delta_log` is an infinite list of JSON files. If a directory contains a Delta table, you just need to read the files (based on file names) in `_delta_log`, one by one, to get the current state of the table.

You don't need any extra information or 'catalog' to read/write to them.

**2. Iceberg, on the other hand, is storage agnostic, and relies on a catalog to get ACID.**

The metadata layer is a reversed linked list of snapshot nodes (from `SNAPSHOT N+1`, you can find `SNAPSHOT N`, but not vice versa).

You need an external 'catalog' to atomically insert and retrieve the last snapshot.

Wait, what if the file system can consistently 'remember' the snapshot pointer and atomically swap it? Bingo, we got an S3 table bucket.

## How does writing to S3 table buckets actually work?

I spent some time on S3 table [docs](https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-tables.html) so you don't have to. P.S. it's hard to understand, even DeepSeek struggles.

We'll compare writing to an S3 Table with a 'normal' Iceberg catalog:

1. **[Both]** Engine writes `data_files` (Parquet)
2. **[Both]** Engine writes Iceberg metadata files
3. **[Catalog Only]** Request the catalog to commit
4. **[S3 Table Only]** Call S3 API `UpdateTableMetadataLocation` to perform the commit

Yep, that's the only difference.

## What are the benefits of S3 tables then?

I am sure Amazon is doing a lot of work on performance (both on compaction and bucket layout).

But the functionality difference is:

**S3 tables allow you to read and write any file to the bucket, but not list files.**

I thought it was dumb at first, but it actually makes sense.

It means the only way to 'probe' a table bucket is to read the `metadata-location` specified by the bucket. So by design, any user can only read files that are part of the table, because there is no way to find any other file.

## So, who should use S3 tables?

I think the use cases might be very different from what people think.

For the enterprise-scale lakehouse, it actually makes sense to have a proper centralized external catalog and table maintenance services. And S3 Tables are still more expensive than regular S3.

I don't see much use of S3 tables there.

To me, S3 Tables are great for smaller teams and lightweight analytics, potentially embedded into other workflows. It gives you Iceberg without managing an external catalog.

Here's my take: ***the first engine to write S3 Tables is Spark, and the second will be Postgres.***

🥮
