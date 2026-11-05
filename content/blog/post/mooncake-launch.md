---
title: "Mooncake: next-gen search and analytic systems"
date: 2024-10-30
description: "We are Zhou, Cheng, and Pranav, and we've spent the last decade building databases. Here are our principles for the next generation of data systems."
author: "[Mooncake Labs Team](https://github.com/Mooncake-Labs)"
authors: ["mooncake-labs", "zhou-sun", "cheng-chen", "pranav-aurora"]
tags:
  - "launch"
  - "postgresql"
  - "pg_mooncake"
  - "lakehouse"
upstream_link: "https://www.mooncake.dev/blog/mooncake-launch"
upstream_copyright: "© 2024 Mooncake Labs Inc."
aliases:
  - "/blog/mooncake-launch/"
  - "/blog/postgres-and-python/"
  - "/blog/3/"
images: ["/blog/covers/mooncake-launch.svg"]
---

We are Zhou, Cheng, and Pranav. And we've spent the last decade building databases at MemSQL (now SingleStore).

We love complex systems, deep-tech engineering, and naturally – physics 🙂 Data systems, much like physics, are built on certain principles. The principles need to be unanimous and durable.

Building systems that are simply 'technically' better is futile. The success of a data system depends on the principles it embodies, and changing them along the way is extremely difficult. Closed-source companies can't go to open source and expect adoption. Databases can't just abandon their storage format and be effective stateless engines.

We have strong beliefs about what is happening and what is correct. These principles make the Mooncake.

We're grateful for the support from Khosla Ventures, Nikita Shamgunov, Jordan Tigani, Barry McCardel, Amir Haghighat, Paul Copplestone, Roger Luo, and many others.

Thank you for believing in us and our principles.

## 1. Software is built by the 'product engineer'

There is a disconnect between the interfaces, jargon, and stack built by the data community, and how teams actually ship software today. And this is our opportunity. There are two types of teams today:

### a. Teams that have overengineered their stack (more pipelines than customers)

These teams have built a lot of infrastructure to ship some product. Each piece introduces specific APIs, schemas, and types. The flow often resides in the mind of a single engineer.

A common setup we've seen is Postgres + PostHog + Dagster + Fivetran + dbt + BigQuery for some very basic insights on product usage.

Despite our decade in databases, we'd struggle to set this up—how will your SWE agent handle it? Also, when are you actually working on your product instead of your stack?

![Team A Setup](/images/blog/blog3_tea.svg)

### b. Teams that would benefit from some data sanity

These teams have shipped a lot of product on shoestring infrastructure—typically a Postgres table, ad-hoc files (CSV, Parquet, JSONL), Python scripts, and Lambda functions to hold it all together.

I like these teams, but they would benefit from storing data in tables (Iceberg and Delta) instead of ad-hoc files. They wouldn't have to sift through hundreds of time-stamped Parquet files to find missing values or wrangle with dataframes to stitch their files and tables together.

Unfortunately, these teams often don't know that this technology exists, and it's hard to blame them. There is so much jargon, it's hard to get started, and there is opportunity cost of setting up all this infra. Also, have you tried writing to an Iceberg table? Good luck!

![Team B Setup](/images/blog/blog3_ship.svg)

## 2. Database engines are on the path to being commoditized

We've seen every database implement the same optimizations, mimicking one another. The database pie has been sliced so thin that we're left with generic marketing terms like 'real-time!' and 'analytics!'

![Database Diagram](/images/blog/blog3_db.svg)

This is why we strongly believe in open table formats like Iceberg and Delta. A single copy of data with stateless execution engines aligns incentives and creates a positive-sum game.

## 3. Agents need separation of storage and compute

Separation of storage and compute has historically created delightful 'for human' experiences: serverless, branching, read replicas, scale to 0, lower costs.

It's also compelling for agents. With chain-of-thought / o1-type reasoning, you'll expect LLMs to do more than just make function calls with fixed knowledge bases. Agents will write and update tables, run complex transformations with Python.

![Mooncake Diagram](/images/blog/blog3_mooncake.svg)

## There are three pieces to the Mooncake; Postgres and Python are all you will need

First, get 1000x faster analytics directly in Postgres with [`pg_mooncake`](/docs/intro/) columnstore tables. These columnstore tables are just like a regular Postgres table.

> "We're really excited about Mooncake bringing easy-to-use columnstore tables to Postgres... Mooncake is exactly what we needed to modernize our data infrastructure all while staying within Postgres."
>
> — Max Muoto

Next, you can query these tables outside of Postgres with Polars, DuckDB, and Pandas with 0 dataframe wrangling or formatting.

## It's day 61, and there are a lot of systems to beat 🙂

We have a long journey ahead, but the principles won't change (hopefully).

🥮
