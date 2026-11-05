---
title: "PostgreSQL 中最简单的极速分析方式：pg_mooncake v0.1 正式发布"
date: 2025-01-11
description: "pg_mooncake 结束 Beta 测试正式发布 v0.1，为 PostgreSQL 带来原生列存表与 DuckDB 向量化执行。"
author: "[Mooncake Labs Team](https://github.com/Mooncake-Labs)"
authors: ["mooncake-labs", "zhou-sun", "cheng-chen", "pranav-aurora"]
tags:
  - "release"
  - "pg_mooncake"
  - "duckdb"
upstream_link: "https://www.mooncake.dev/blog/pgmooncake-v01"
upstream_copyright: "© 2025 Mooncake Labs Inc."
aliases:
  - "/zh/blog/pgmooncake-v01/"
  - "/zh/blog/post/pgmooncake-v01/"
images: ["/blog/covers/pgmooncake-v01.svg"]
---

我们在创业第 60 天向世界[首次宣布了](/zh/blog/post/how-we-built-pgmooncake/) `pg_mooncake`。

今天（第 131 天），`pg_mooncake` 正式结束 Beta 阶段，发布 [v0.1.0](https://github.com/Mooncake-Labs/pg_mooncake/releases/tag/v0.1.0)。

`pg_mooncake` 的核心竞争力在于**极致易用性**与**强悍性能**。在 v0.1 中，我们在这两个方向上全力加码。

## 在 Postgres 中运行极速分析最简单的方式 {#the-easiest-way-to-fast-analytics-in-postgres}

凭借 Postgres 原生列存表，`pg_mooncake` 将开发者最熟悉的表语义带入分析场景。列存表不仅支持事务性的 `INSERT`、`SELECT`、`UPDATE`、`DELETE` 和 `COPY`，还能直接与普通 Postgres 堆表执行关联查询（JOIN）。

在 v0.1 中，我们让向列存表[导入数据](/zh/docs/v0.1/load-data/)变得更加简单：

1. 直接读取 Parquet、CSV 与 JSON 文件：

```sql
SELECT * FROM mooncake.read_parquet('<file_path>');
```

2. 直接从 Hugging Face 数据集导入：

```sql
COPY reddit_comments FROM 'hf://datasets/fddemarco/pushshift-reddit-comments/data/RC_2012-01.parquet';
```

3. 直接查询外部现有的 Iceberg 与 Delta Lake 表：

```sql
SELECT * FROM mooncake.iceberg_scan('s3://bucket/table');
```

## 时序与分析负载性能大幅跃升 {#better-performance-for-time-series-workloads}

`pg_mooncake` 是唯一同时为 Postgres 提供列式存储与向量化执行的扩展。

在 v0.1 中，我们引入了文件级统计信息与数据块跳过（File Skipping / Segment Elimination），让用户无需传统分片即可轻松承载大规模时序与分析负载。

我们的 [ClickBench](https://github.com/ClickHouse/ClickBench/pull/284) 官方基准测试成绩将于下周揭晓（剧透：[闯入全球前十](/zh/blog/post/clickbench-v0.1/) 🙂）。事实证明，PostgreSQL 完全可以成为一流水准的实时分析数据库。

## 展望 v0.2 {#looking-ahead-to-v02}

接下来我们将重点聚焦在开发者体验（DevEx）与实时同步能力上，规划中的改进包括：

1. 增强对高频小批量写入、更新与删除的支持
2. 将行存堆表（Rowstore）实时同步至列存表（Columnstore）
3. 索引支持（二级索引与排序键）
4. 时序分析函数

## 致谢社区 {#to-our-community-thank-you}

独行快，众行远。衷心感谢我们的社区用户、代码贡献者以及 [Neon](https://neon.tech/)、[Supabase](https://supabase.com/) 等 Postgres 生态伙伴的鼎力支持。

我们最珍视的指标，就是 `pg_mooncake` 开源贡献者人数的持续增长。`pg_mooncake` 的势头已经势不可挡，Postgres 原生分析时代已然到来 🥮
