---
title: "HTAP 已死，精神长存"
date: 2025-05-05
description: "过去十年我一直在构建并拯救 HTAP 数据库。今天，单体 HTAP 数据库已经落幕，但它的精神正在实时数据湖仓（Lakehouse）中延续。"
author: "[Zhou Sun](https://github.com/zhousun) · [Mooncake Labs](https://github.com/Mooncake-Labs)"
authors: ["zhou-sun"]
tags:
  - "htap"
  - "lakehouse"
  - "postgresql"
  - "musings"
upstream_link: "https://www.mooncake.dev/blog/htap-is-dead"
upstream_copyright: "© 2025 Zhou Sun (Mooncake Labs Inc.)"
aliases:
  - "/zh/blog/htap-is-dead/"
images: ["/blog/covers/htap-is-dead.jpg"]
---

本文的灵感源自 Jordan Tigani 的经典博文[《Big Data is Dead（大数据已死）》](https://motherduck.com/blog/big-data-is-dead/)。事实上，Jordan 和我曾一起在 SingleStore 共事，联手打造过一套 HTAP 数据库。

## 黄金年代（1980 年代） {#the-good-old-days-80s}

回到 80 年代，一套关系型数据库包揽了一切：白天跑在线事务（OLTP），下班后跑分析报表（OLAP）。像 Oracle V2 和 IBM DB2 这样的系统在同一台机器上同时承载 OLTP 和 OLAP——主要是因为当时的数据集还能装进几块磁盘里，而且计算硬件极其昂贵。

那时候没人把这叫做“混合事务/分析处理（HTAP）”，它就叫**数据库（Database）**。

## 大分裂（1990 年代） {#the-great-divide-90s}

随着企业数据量暴增、分析问题越来越复杂，单一数据库开始捉襟见肘。

事务型负载与分析型负载在物理资源诉求上背道而驰：OLTP 需要微秒级单行写入与点查，而 OLAP 需要全表扫描与大规模聚合。两者在同一个实例里不断发生资源争抢——大查询吞噬了延迟敏感型事务所需的磁盘 I/O 与缓冲池缓存，反之亦然。

怎么解决？把两类负载彻底拆开。到 2000 年代初，数据库领域的“大分裂”正式拉开帷幕。

## 存储层的分野（2000 年代） {#the-storage-split-2000s}

推动这场分裂的核心技术驱动力是存储引擎架构：OLTP 系统针对行式存储（Row-Based Storage）做极致优化以加速写入与点查；而 OLAP 系统则转向列式存储（Columnar Storage）以实现高速扫描与聚合压缩。

到 2000 年代中期，这种行/列分治已成为行业标准。图灵奖得主、数据库先驱 Michael Stonebraker 在其著名[论文](https://dl.acm.org/doi/abs/10.1145/3226595.3226636)《“One Size Fits All”: An Idea Whose Time Has Come and Gone》中为这一时代变革定下了基调——数据库开始裂变为各种专用引擎。

## OLTP 与 OLAP 双双抛弃 SQL（2000–2010 年代） {#oltp-and-olap-both-ditched-sql-2000s2010s}

水平扩展（Scale-Out）的需求把 OLTP 与 OLAP 推得更远了。

早期的分布式 OLTP 数据库（如 MongoDB 等 NoSQL 引擎）彻底抛弃了 SQL 和分析能力；而在分析领域，MapReduce 与 Hadoop/HDFS 数据湖架构席卷业界——用牺牲传统 RDBMS 严格一致性与 SQL 体验的代价，换取海量吞吐。

## 意料之外的殊途同归（2010 年代） {#the-unexpected-reconciliation-2010s}

进入 2010 年代，两股数据库思潮同时兴起：

1. **NewSQL**（Spanner、CockroachDB、Vitess）：分布式 OLTP 依然应当构建在 SQL 与强一致性之上；
2. **云数据仓库**（Redshift、Snowflake）：大规模 OLAP 同样应当回归具备事务保证的 SQL 系统。

表面上看，这两类系统服务于截然不同的负载；但在底层引擎上，它们却惊人地趋同：分布式架构、MPP 并行执行以及标准 SQL。孤立演进的 OLTP 与 OLAP 系统在几乎所有架构原则上都重新交汇了——只剩下一个核心差异：**存储引擎**。

于是我们不禁自问：**如果能把行存引擎与列存引擎融合进同一个数据库里呢？**

## Voilà，HTAP 诞生（2014） {#voilà-htap-2014}

2014 年，Gartner 正式[提出了](https://www.gartner.com/en/documents/2657815) **HTAP（Hybrid Transactional and Analytical Processing，混合事务/分析处理）** 这一术语，将其视为下一代数据库架构的皇冠。

HTAP 的目标是弥合操作型系统与分析型系统之间的鸿沟，满足实时定价、反欺诈、个性化推荐等新兴场景的需求。早期的 HTAP 系统证明了这一构想在技术上的可行性：

- **[SingleStoreDB](https://dl.acm.org/doi/10.1145/3514221.3526055)** 将内存行存（Rowstore）、磁盘列存（Columnstore）与向量化执行引擎融为一体，在单个系统内同时支持高速扫描、点查、过滤、聚合与高频更新。
- **[TiDB](https://docs.pingcap.com/tidb/stable/tidb-architecture)** 走了另一条路线：将基于行存的 TiKV 与基于 ClickHouse 演进的独立列存引擎（TiFlash）配对，通过维护两份数据副本来同时服务两类负载。

按理说，这应该就是终局了吧？重返 80 年代“一套数据库搞定一切”的极乐世界？然而现实并非如此。

## 2020 年代唯一的赢家是云数据仓库 {#the-cloud-data-warehouse-was-the-only-winner-2020s}

云数据仓库毫无疑问赢下了市场。NewSQL 运动陷入停滞……而 HTAP 呢？它从未获得与其技术难度相匹配的市场普及度。尽管在内核工程上取得了实质性突破，单体 HTAP 数据库在商业上始终未能真正跨越 PMF（产品市场契合点）。原因有四：

**1. 替换企业现有的核心 OLTP 系统难如登天。** 看看 [DB-Engines 排行榜](https://db-engines.com/en/ranking)就知道了：Oracle 和 SQL Server 至今仍稳居前三位。

**2. 绝大多数业务根本不需要分布式 OLTP。** 现代硬件越来越快、越来越便宜，一台高配单机实例足以扛住绝大多数公司的全部事务负载——就连 [Cursor](https://www.youtube.com/watch?v=4jDQi9P9UIw) 和 [OpenAI](https://www.pixelstech.net/article/1747708863-openai%3a-scaling-postgresql-to-the-next-level) 的核心业务也是跑在单主架构的 PostgreSQL 实例上的。

**3. 云原生架构青睐存算分离（Shared-Disk），而非无共享（Shared-Nothing）。** 分布式 NewSQL 依赖昂贵的本地 NVMe 甚至内存持久化，而云平台的演进方向则是廉价对象存储加弹性无状态计算。

**4. OLTP 与 OLAP 归属于不同的部门与团队。** OLTP 归业务研发团队管，OLAP 归数据平台团队管。两边的 KPI 与激励机制极少对齐——没有任何人会因为“把两套数据库合并成一套”而获得晋升。

## 今天：你的整个现代数据栈共同构成了“解耦式 HTAP 数据库” {#your-data-stack-forms-the-htap-database-today}

云时代推动数据架构从紧耦合的单体仓库走向基于对象存储的模块化数据湖仓。数据团队开始用各个领域的“最佳组件（Best-in-Class）”拼装出自己的系统：

1. **OLTP 数据库与流处理系统**充当系统的 **WAL（预写日志）**；
2. **Apache Iceberg 等开放表格式**充当底层的**列式存储引擎**；
3. **Spark、Trino、DuckDB 等计算引擎**充当**查询执行器**；
4. **ClickHouse 或 Elasticsearch 等实时系统**充当面向特定查询的**二级索引**。

即便在今天这套高度解耦的数据栈中，用户的核心诉求依然从未改变：**在最新鲜的事务数据上跑极速 OLAP 分析查询。**

这依然是 HTAP——只不过它是通过**开放组件的组合（Composition）**，而非**单体数据库的吞并（Consolidation）**来实现的。今天的核心命题变成了：

**1. 我该如何把 WAL 高效应用到开放存储引擎上？**
换言之：如何以亚秒级延迟、极低写放大地将 OLTP 数据库的变更（CDC）同步进 Iceberg 数据湖？

**2. 我能否在数据湖之上直接构建低成本索引并保持实时同步？**
换言之：如何让数据湖具备实时写入能力，并直接通过 Postgres 或搜索引擎的接口查询湖中的数据？

我们这个时代的 HTAP 挑战，归根结底就是**让数据湖仓（Lakehouse）真正具备实时能力（Real-Time Ready）**。

在我把人生最宝贵的十年献给创建和拯救 HTAP 数据库之后，我可以坦然地说：**作为单体数据库的 HTAP 已经死了；但 HTAP 的精神，正在实时数据湖仓中获得新生。** 🥮
