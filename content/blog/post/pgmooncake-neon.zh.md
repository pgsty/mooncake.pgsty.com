---
title: "pg_mooncake + Neon：PostgreSQL 中的 Serverless 实时分析"
date: 2025-01-07
description: "通过将 Neon 的存算分离存储引擎与 pg_mooncake 的湖仓架构相结合，我们无意间打造出了最优秀的 Serverless 分析数据库。"
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
  - "/zh/blog/pgmooncake-neon/"
images: ["/blog/covers/pgmooncake-neon.svg"]
---

[`pg_mooncake`](/zh/docs/intro/) 在两个月前发布了 Beta 版，为 PostgreSQL 带来了列式存储与向量化查询执行引擎。

在过去两个月与早期用户的打磨过程中，我们突然意识到：我们无意间打造出了最优秀的 Serverless 分析数据库。故事是这样的：

## 1. pg_mooncake 🤝 Neon 存储引擎 {#1-pg_mooncake--neon-storage-engine}

Neon 在其[底层存储引擎](https://neon.tech/blog/get-page-at-lsn)上做出了重大创新（推荐阅读 Nikita 关于这一架构的[技术长帖](https://x.com/nikitabase/status/1723579854266966399)）。正是依靠这套存储引擎，Neon 实现了真正的存算分离，进而带来了数据库分支（Branching）、缩容至零（Scale-to-Zero）、秒级只读副本与即时实例拉起等极致的 Serverless Postgres 开发者体验。

![Neon Storage engine](/images/blog/blog5-neon.svg)

与此同时，[`pg_mooncake` 的架构](/zh/blog/post/how-we-built-pgmooncake/)同样基于真正的存算分离：列存数据以 Parquet 格式存放在对象存储（或本地文件系统）中，而 Postgres 内部仅保存轻量级元数据。

![pg_mooncake architecture](/images/blog/blog5-arc.svg)

这正是经典的[湖仓一体（Lakehouse）架构](https://www.cidrdb.org/cidr2021/papers/cidr2021_paper17.pdf)——全球规模最大的科技公司正是利用这种架构，以高性价比、Serverless 的方式存储并分析海量数据的。

> 一句话总结 Lakehouse：将所有数据以通用开放格式存放在对象存储中，随后通过 Pandas DataFrame、Spark 或 DuckDB 以无状态方式直接查询。

`pg_mooncake` 的目标，就是将这种灵活性、可扩展性与 Serverless 分析体验带给每一个 Postgres 应用。

## 2. 一切皆可缩容至零（Scale to Zero） {#2-scale-everything-to-zero}

将 Neon 的存算分离存储与我们的分析架构结合在一起——你就能在同一个数据库体系内，同时为事务型（OLTP）与分析型（OLAP）负载实现彻底的存算分离，并且所有表元数据依然统一保存在 Postgres 中。

![separation](/images/blog/blog5-separation.svg)

借助这套把分析表与事务表融为一体的 Serverless 架构，我们的用户实现了许多令人惊艳的用法：

1. 将分析负载与事务负载完全隔离，并分别独立弹性扩缩容；
2. 使用独立的计算节点将堆表（Heap Tables）的变更实时同步至列存表；
3. 在 BI 报表与仪表盘查询中直接将列存表与堆表关联（JOIN）；
4. 运行在空闲时可自动缩容至零（Scale-to-Zero）的完整分析服务。

例如 [Inkeep](https://www.inkeep.com/) 团队完全基于 Postgres 交付了他们的核心应用、高速 BI 仪表盘以及[分析报表服务](https://docs.inkeep.com/analytics/usage-reports)。各个服务的计算资源独立扩缩，而全部数据与表元数据始终留在 Postgres 之中，极其干净利落。

## 3. 基于 Python 的 Scale-to-Zero 分析 {#3-scale-to-zero-analytics-with-python}

更有趣的部分来了。

`pg_mooncake` 将数据以标准的开放分析格式（[Apache Iceberg](https://iceberg.apache.org/) 与 [Delta Lake](https://delta.io/)）写入对象存储。这些元数据层覆盖在 Parquet 文件之上，使得任何查询引擎（Pandas、Polars、Spark、DuckDB）都能把对象存储上的文件当作一张完整的数据库表来直接读取。

我们看到许多 `pg_mooncake` 用户直接使用 Python 读取并转换列存表数据——从列存表构建 DataFrame 易如反掌（参见 [云对象存储配置](/zh/docs/v0.1/cloud-storage/) 与 [Iceberg 对象存储参考](/zh/docs/reference/iceberg/)）。

此外，还有用户在 Postgres 列存表之上直接运行诸如 [LOTUS](https://github.com/guestrin-lab/lotus) 这样的 AI 语义查询引擎：

![Lotus on PG](/images/blog/blog5-lotus.svg)

## 4. 立即开始体验！ {#4-get-started-today}

请阅读我们的[快速开始指南](/zh/docs/getting-started/)，在 PostgreSQL 中创建你的第一张实时列存表。
