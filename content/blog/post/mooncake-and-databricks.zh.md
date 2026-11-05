---
title: "Mooncake 正式加入 Databricks！"
date: 2025-10-01
description: "以正确的方式统一操作型数据疆域（Postgres / Lakebase）与智能分析数据疆域（Lakehouse）。"
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
  - "/zh/blog/mooncake-and-databricks/"
images: ["/blog/covers/mooncake-and-databricks.svg"]
---

十三个月前，我们创立了 Mooncake，旨在将支撑 OpenAI 等科技巨头的数据智能技术栈带给每一个现代应用与每一位开发者——从第一行 Prompt 直到公司上市（IPO）。

今天，我们正式加入 Databricks。
我们的使命一如既往：让 [Lakebase](https://www.databricks.com/product/lakebase)（Postgres）与数据湖仓（Lakehouse）融为一体。

---

在过去整整十年里，我们曾以为数据库的终极形态是一个能包揽一切的单体系统——同时兼顾高频更新、分布式事务与极速分析。在数据库行业里，这被称为 HTAP。但它始终未能真正普及。Zhou 和 Cheng 亲手构建了它，Pranav 竭力向市场推销它——这条路走得异常艰难。

因为当你试图在一套系统里同时重造 OLTP 和 OLAP 两端时，最终造出来的产品往往在两端都不得不做出妥协。

## 那么，如果不去重造两端呢？🥮 {#well-what-if-you-didnt-}

开发者（以及如今的 AI 智能体）早就已经选出了默认的 OLTP 赢家：**Postgres**，而且大家都深爱着它。

与此同时，企业也已经拥有了默认的数据湖仓（**Lakehouse**），并且非常熟悉如何用自己钟爱的计算引擎（Apache Spark、Snowflake、DuckDB、Trino）或智能体框架（[Databricks Agent Bricks](https://www.databricks.com/product/artificial-intelligence/agent-bricks)）从中提炼数据智能。

在天平的两端，赢家都已经尘埃落定：云原生架构、庞大的开源社区拥护。在数据库历史上，操作型（Operational）与分析型（Analytical）两大疆域第一次同时拥有了如此清晰的标准锚点。

既然如此……**如果让它们无缝协同工作呢？**

## 面向开发者 {#for-the-developer}

你的应用从第一天起就跑在 Postgres 上。一旦你的产品找到市场契合点（PMF），同一份数据立刻就能直接供最顶尖的湖仓工具进行深度分析与 AI 训练——不需要搭建脆弱的数据管道，也不需要手工折腾 CDC，Postgres 数据天然与你的湖仓实时同步。

而所有的分析洞察与智能，只需借助 Postgres 与 [`pg_mooncake`](/zh/docs/intro/) 扩展即可直接服务于线上应用。

## 面向企业 {#for-the-enterprise}

对于现代企业而言，Postgres + Lakehouse 早已是既定的标准技术栈。成群的数据工程师每天在两者之间搬运数据（ETL、Reverse ETL），还有更多工程师在维护和调优数据湖仓。

有了 Mooncake，整套技术栈直接开箱即用——再也不需要为了同步一张表而维护一套沉重的 `Debezium + Kafka + Flink` 集群 🙂

## 面向 AI 智能体（Agents） {#for-the-agent}

我们看到智能体与数据的交互主要分为两类：

1. 在 Postgres 上自动构建应用的智能体（如 Lovable、Replit）；
2. 分析并理解企业数据的智能体（如 Agent Bricks）。

现在，这两类智能体终于可以在同一份数据上并肩协作了：

- 共享同一份实时数据；
- 支撑上万个并发智能体同时运行的规模；
- 无需人工编写和维护连接两端的 ETL 管道 🙂

## 衷心感谢，以及属于我们的又一个 Day 0 {#thank-you-and-day-0-again-for-us}

感谢所有一路支持和相信我们的人——用户、早期设计合作伙伴、投资人以及开源社区贡献者。

`pg_mooncake` 将继续保持开源与社区活力（注：现由 [PGSTY 社区](/zh/docs/about/) 持续维护并发布 [`v0.3.0`](/zh/blog/release/pg-mooncake-0.3.0/)）。

加入 Databricks 后，Mooncake 同时连接起了两大核心数据疆域：Postgres（Lakebase）与 Lakehouse。终于，天平的两端真正融为了一体。

—— Zhou, Cheng, Pranav, Nolan, Hao, Paul.
🥮
