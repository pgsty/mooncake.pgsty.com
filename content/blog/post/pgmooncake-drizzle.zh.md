---
title: "pg_mooncake 🤝 Drizzle：用强类型 ORM 驱动分析查询"
date: 2025-01-08
description: "在 PostgreSQL 的 pg_mooncake 列存表上直接使用你最喜爱的 TypeScript ORM（Drizzle）编写强类型分析查询。"
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
  - "/zh/blog/pgmooncake-drizzle/"
images: ["/blog/covers/pgmooncake-drizzle.jpg"]
---

在 [`pg_mooncake`](/zh/docs/intro/) [发布之初](/zh/blog/post/how-we-built-pgmooncake/)，有一件事出乎我们的意料：开发者们非常关心能否在分析型负载中继续使用熟悉的 ORM。我们经常收到两类典型需求：

1. *“我手头有一堆 Parquet 文件，我希望能在它们之上获得完整的 ORM 类型支持。”*
2. *“我在事务数据库里用了 Drizzle / Prisma，我也希望能直接用它来写分析报表和仪表盘查询。”*

![slack](/images/blog/blog6-slack.jpg)

我们始终坚信，Postgres 中的列式存储在外观和使用体验上必须像一张普通堆表。这正是 `pg_mooncake` 列存表的核心创新所在：你可以对它执行事务、更新、删除，并与普通堆表直接关联（JOIN）。

在 Postgres 中提供原生列存表的一大额外红利在于：你最喜爱的 ORM 可以直接开箱即用。在本文中，我们将使用 [Drizzle ORM](https://orm.drizzle.team) 来演示这一点。

下面让我们基于一份 Reddit 评论数据集构建一个简单的分析应用，并全部使用 Drizzle 编写分析查询。

## 1. 创建 pg_mooncake 列存表 {#1-create-a-pg_mooncake-columnstore-table}

我们将使用来自 [Hugging Face](https://huggingface.co/datasets/fddemarco/pushshift-reddit-comments) 的 Reddit 评论数据集。首先创建一张 `pg_mooncake` 列存表（参见 [v0.1 数据导入语法](/zh/docs/v0.1/load-data/) 与 [v0.3 `mooncake.create_table` 参考](/zh/docs/reference/create-columnstore/)）：

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

接着，将 Hugging Face 上的 Parquet 数据直接复制到 `reddit_comments` 表中（这里我们导入单个包含 1500 万行的 Parquet 文件）：

```sql
COPY reddit_comments FROM 'hf://datasets/fddemarco/pushshift-reddit-comments/data/RC_2012-01.parquet';
```

非常棒！现在从 Hugging Face 往 Postgres 导入海量数据既简单又飞快。

## 2. 为列存表定义 Drizzle Schema {#2-set-up-drizzle-schema-for-the-columnstore-table}

配置好连接 Postgres 实例的 [Drizzle 驱动](https://orm.drizzle.team/docs/get-started-postgresql)后，我们可以像定义普通表一样为列存表编写 Schema：

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

## 3. 以完整的类型安全查询数据模型 {#3-start-querying-your-data-model-with-full-type-safety}

例如，按板块聚合统计评论数与平均得分：

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

你可以用自己最熟悉的 TypeScript 语法编写极速分析查询。

## 4. 立即开始使用 pg_mooncake {#4-get-started-with-pg_mooncake-today}

欢迎了解我们在 [Drizzle](https://orm.drizzle.team) 的伙伴们——用 ORM 驱动分析查询从未如此轻松。我们现已成为 Drizzle 的官方赞助商：

![sponsor](/images/blog/blog6-sponsor.jpg)

我们非常期待与社区一起推进诸如 [One Dollar Stats](https://onedollarstats.com/) 这样的项目，敬请期待更多精彩内容。
