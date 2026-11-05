---
title: "pg_mooncake 🤝 drizzle: typed SDKs for your analytic workloads"
date: 2025-01-08
description: "Use your favorite TypeScript ORM (Drizzle) for analytical workloads on pg_mooncake columnstore tables in PostgreSQL."
author: "[Pranav Aurora](https://github.com/paurora17) · [Mooncake Labs](https://github.com/Mooncake-Labs)"
authors: ["pranav-aurora"]
tags:
  - "postgresql"
  - "pg_mooncake"
  - "analytics"
  - "drizzle"
upstream_link: "https://www.mooncake.dev/blog/pgmooncake-drizzle"
upstream_copyright: "© 2025 Pranav Aurora (Mooncake Labs Inc.)"
aliases:
  - "/blog/pgmooncake-drizzle/"
images: ["/blog/covers/pgmooncake-drizzle.jpg"]
---

A thing that surprised us in the [`pg_mooncake`](/docs/intro/) [launch](/blog/post/how-we-built-pgmooncake/) was how much developers cared about ORMs for their analytical workloads. We saw two typical requests:

1. *"I have a bunch of Parquet files. I want full ORM support over them."*
2. *"I use Drizzle/Prisma for my transactional database. I also want to use it for my analytics and dashboards."*

![slack](/images/blog/blog6-slack.jpg)

We've always believed that columnar storage in Postgres must look and feel like a regular heap table. It's where we innovated with `pg_mooncake` columnstore tables; you can run transactions, updates, deletes, and joins with heap tables.

A nice bonus of native columnstore in Postgres is your favorite ORM works out of the box. In this blog post, we'll use [Drizzle](https://orm.drizzle.team).

Let's build a simple analytics app on a Reddit dataset, and run all analytics queries using Drizzle.

## 1. Create a pg_mooncake columnstore table

We'll be using a Reddit dataset from [Hugging Face](https://huggingface.co/datasets/fddemarco/pushshift-reddit-comments). First, create a `pg_mooncake` columnstore table (see the [v0.1 syntax](/docs/v0.1/load-data/) and [v0.3 `mooncake.create_table` reference](/docs/reference/create-columnstore/)):

```sql
CREATE TABLE reddit_comments (
    author TEXT,
    body TEXT,
    controversiality BIGINT,
    created_utc BIGINT,
    link_id TEXT,
    score BIGINT,
    subreddit TEXT,
    subreddit_id TEXT,
    id TEXT
) USING columnstore;
```

Next, copy the data from Hugging Face into `reddit_comments` ([v0.1 Load Data guide](/docs/v0.1/load-data/)). Here we just copy 1 Parquet file (15M rows):

```sql
COPY reddit_comments FROM 'hf://datasets/fddemarco/pushshift-reddit-comments/data/RC_2012-01.parquet';
```

Great. Loading data from Hugging Face in Postgres is pretty simple now. And fast too.

## 2. Set up Drizzle schema for the columnstore table

After we set up the [Drizzle PostgreSQL driver](https://orm.drizzle.team/docs/get-started-postgresql) for our Postgres instance, we can set up the schema for our columnstore table:

```typescript
// schema.ts
export const redditComments = pgTable("reddit_comments", {
  id: text("id").primaryKey(),
  author: text("author"),
  body: text("body"),
  controversiality: bigint("controversiality", { mode: "number" }),
  created_utc: bigint("created_utc", { mode: "number" }),
  link_id: text("link_id"),
  score: bigint("score", { mode: "number" }),
  subreddit: text("subreddit"),
  subreddit_id: text("subreddit_id")
});
```

## 3. Start querying your data model with full type safety

For example, to get subreddit statistics:

```typescript
// routes.ts
const stats = db
  .select({
    subreddit: redditComments.subreddit,
    commentCount: sql<number>`count(${redditComments.id})`,
    avgScore: sql<number>`avg(${redditComments.score})::float`,
    avgControversiality: sql<number>`avg(${redditComments.controversiality})::float`,
    totalScore: sql<number>`sum(${redditComments.score})`
  })
  .from(redditComments)
  .groupBy(redditComments.subreddit)
  .orderBy(desc(sql`count(${redditComments.id})`))
  .limit(10);
```

You can write fast analytics queries with syntax you're comfortable with.

## 4. Get started with pg_mooncake today

Check out our friends at [Drizzle](https://orm.drizzle.team). It's never been easier to use your ORM for your analytics.

We're now an official Drizzle sponsor:

![sponsor](/images/blog/blog6-sponsor.jpg)

We're excited to take on projects like [One Dollar Stats](https://onedollarstats.com/) together. Stay tuned for more.
