---
title: "可是，我的 Postgres（+ 数据湖仓）是免费的呀"
date: 2025-06-13
description: "Snowflake 和 Databricks 斥资数十亿美元收购各自的 Postgres。为什么说开源免费的 Postgres + Apache Iceberg 才是现代应用与 AI 智能体的终极技术栈？"
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
  - "/zh/blog/postgres-lakehouse-free/"
images: ["/blog/covers/postgres-lakehouse-free.svg"]
---

**友情提示：** 你的 Postgres 和数据湖仓（Lakehouse）同样是自由且开源的——你完全不需要成为（或者像巨头一样挥霍数亿美金）才能拥有它们。

## 为什么是 Postgres + Lakehouse？ {#why-postgres--lakehouse}

### 原因一：如果你相信 AI，这就是智能体（Agent）的标准技术栈 {#reason-1-if-you-believe-in-ai-this-is-the-agent-stack}

AI 智能体需要记忆——既需要即时响应的**工作记忆（Working Memory）**，也需要海量的**长期知识（Long-Term Knowledge）**。

工作记忆必须像应用状态一样瞬时可达、可靠且精确。存放它的最佳位置是哪里？**Postgres**。无论是传统应用还是 AI 智能体皆是如此。这类状态通常与单个用户、租户或智能体会话紧密绑定。

而长期知识则截然不同：原始输入规模庞大、结构繁杂，并且需要跨用户、跨租户、跨智能体共享——包括全量运行日志、LLM 输入输出轨迹与交互反馈。它的核心目标是让系统“变得更聪明”。

存放这些海量原始输入的最佳方式是什么？**数据湖仓（Lakehouse）**。它以对象存储为中心、具备无限扩展能力，并且向所有最优秀的计算、分析、搜索与 MLOps 引擎完全开放——同一份数据可供所有工具直接读取，且只需按实际使用量付费。

经典的数据工程管道旨在从应用业务数据中提炼洞察并反哺应用：

`App 业务数据 → Bronze（原始层）→ Silver（清洗层）→ Gold（建模层）→ 将洞察服务于 App`

而在 AI 智能体时代，完全相同的闭环正在重演：

`Agent 上下文 → 原始记忆（Raw Memory）→ 提炼知识（Knowledge）→ 更精准的上下文`

**Postgres → Lake → Postgres**：一个完美的闭环。

### 原因二：巨头们亟需新的 OLTP 增长故事 {#reason-2-the-industry-needs-a-new-oltp-winner-theres-a-lot-of-shareholder-value-at-stake}

OLTP 正在成为数据巨头与超大规模云厂商争夺的全新主战场。

十年前 Snowflake 刚问世时，所有人都为之惊叹：一个无论查询多复杂、数据量多大都能直接跑出结果的云原生数据仓库，真正做到了开箱即用。

但十年后的今天，支撑 Snowflake 的两大核心技术已经高度商品化：

1. **存算分离**——如今只需对象存储配合智能缓存即可实现；
2. **向量化执行**——如今在你的笔记本电脑上跑一个 DuckDB 就能轻松拥有。

这使得新一代湖仓架构（Lakehouse）成为必然：将数据与元数据放在开放对象存储中，用任意向量化引擎直接查询。单纯的云数仓市场已不再是暴利蓝海，正在变得同质化。

那么，作为一家估值数百亿的分析型数据巨头，如何向资本市场讲出下一个 10 倍增长故事？答案是：**把目光投向隔壁的 OLTP 市场。**

过去 40 年里，Oracle、SQL Server 和 DB2 统治着核心 Tier-1 负载，MySQL 占据着互联网 Tier-3 负载。但风向已经彻底改变：

1. 单机硬件性能突飞猛进；
2. 云基础设施日益成熟；
3. MySQL 被 Oracle 收购后步履放缓；
4. PostgreSQL 社区以惊人的速度持续进化；
5. 绝大多数企业的 OLTP 数据规模并没有无限膨胀。

转眼间，开源、可靠、可扩展且迭代飞快的 Postgres 已经成为 Tier-2 乃至许多 Tier-1 核心负载的首选。

## 这难道只是 Zhou 的一家之言吗？ {#this-is-just-another-zhou-opinion-right}

看看各大巨头正在做什么就清楚了：

- **Microsoft：** Fabric（数据湖仓）已经内置了 SQL Server [实时镜像（Mirroring）](https://learn.microsoft.com/en-us/fabric/database/mirrored-database/overview)，猜猜下一个接入的是谁？当然是 Postgres。
- **Google：** [AlloyDB (Postgres) + BigQuery](https://cloud.google.com/blog/products/data-analytics/enhancing-biglake-for-iceberg-lakehouses)，两者正通过 Apache Iceberg 实现底层数据互通。
- **Amazon：** Aurora 与 RDS 配合 S3 Tables、Glue 与 SageMaker——S3 本身正在变成一座原生的 Iceberg 湖仓。
- **Supabase：** 推荐阅读他们近期发布的博文 [Open Data Standards: Postgres, OTel, Iceberg](https://supabase.com/blog/open-data-standards-postgres-otel-iceberg)。
- **ClickHouse：** 在收购 PeerDB 后，Postgres 已成为 ClickPipes 的第一大输入源，同时他们也在大力推进深度 Iceberg 集成。

**Postgres + Iceberg** 是所有玩家共同押注的赛道。而决定胜负的关键，在于能否在这两者之间打造出极致的开发者体验——不再像传统单体 [HTAP 数据库](/zh/blog/post/htap-is-dead/)那样把分析强行塞进事务引擎而让双方同时妥协，而是让**最优秀的 OLTP（Postgres）**与**最优秀的 OLAP（Iceberg 湖仓）**各自独立发挥极致，又无缝协同得如同同一个系统。

![htap-vs-today](/images/blog/htap-vs-today.svg)

## Postgres + Lakehouse 永远属于开源社区 {#postgres--lakehouse-will-always-stay-free}

当巨头们先砸下数十亿美元买下一家 Postgres 公司、再试图把它粘进自家的商业湖仓护城河时，[`pg_mooncake`](/zh/docs/intro/) 已经为你提供了亚秒级延迟的 Postgres 到 Iceberg 实时同步——而且采用 MIT 开源许可，完全免费 🙂
