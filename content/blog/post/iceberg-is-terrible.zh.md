---
title: "不，单靠 Iceberg 拯救不了你的数据栈"
date: 2025-07-21
description: "Apache Iceberg 非常适合 Netflix 规模的批处理数据湖，但要想真正服务于实时业务，我们必须赋予它真正的数据库内核工程学：并发写入、无锁在线合并与原生索引。"
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
  - "/zh/blog/iceberg-is-terrible/"
images: ["/blog/covers/iceberg-is-terrible.svg"]
---

人生总是充满了“理想与现实的落差”。今天我们就来聊聊数据社区的新宠——[Apache Iceberg](https://iceberg.apache.org/) 的理想与现实。

## 理想：Iceberg 能解决我所有的数据痛点 {#expectations-iceberg-is-the-solution-to-all-my-data-pains}

平心而论，Iceberg 的核心设计理念非常漂亮：

1. 将所有数据以 Parquet 等开放文件格式存放在对象存储中；
2. 让任何计算引擎（DuckDB、ClickHouse、Spark、Snowflake 等）把这些文件当作一张真正的数据库表，直接用 SQL 查询；
3. *[持续演进中]* 无需将数据导入特定系统的私有格式，就能直接获得优异的查询性能。

凭借精巧的元数据层设计，你还能获得：

1. 跨执行引擎的互操作性，彻底摆脱存储层供应商锁定；
2. ACID 事务与 Schema 演进；
3. 真正的存算分离；
4. 时间旅行（Time Travel）与多版本快照管理。

Iceberg 最初是由 Netflix、Apple 等硅谷巨头的超大规模大数据团队构建的；而最近，越来越多的云平台开始尝试将它推向普通开发者（例如 Supabase 的 [Analytics Buckets](https://supabase.com/blog/analytics-buckets) 与 [Tiger Lake](https://www.tigerdata.com/blog/tiger-lake-a-new-architecture-for-real-time-analytical-systems-and-agents)）。

听起来简直完美：作为用户，我（1）在自己的对象存储桶里掌控全部数据，（2）不被任何数据库厂商锁定，（3）无需导数据就能用任意引擎直接查询。剧本本该到此圆满落幕。

## 现实：只有当你愿意“自己动手造一个 Snowflake（BYOS）”时，Iceberg 才很酷 {#reality-iceberg-is-only-cool-if-youre-willing-to-build-your-own-snowflake-byos}

对于 Apple 和 Netflix 而言，雇佣几百名顶尖基础设施工程师，在裸对象存储之上自己造一套 Snowflake 或 Databricks 绝对物超所值。但对于你我这样的普通团队，我对此深表怀疑。

当你我满怀期待地用上 Iceberg 时，我们以为它会像 Postgres 或 ClickHouse 一样“开箱即用”——直接 `INSERT` / `UPSERT` 数据、导入文件、然后发起查询。然而现实远没有那么简单：

**1. 沉重的元数据开销：** Iceberg 需要追踪快照（Snapshots）、清单（Manifests）、清单列表（Manifest Lists）以及表元数据 JSON。哪怕只更新一行数据，也会触发 4 次 S3 写入（每次耗时数百毫秒），而跑在 SSD 上的普通关系型数据库只需不到 `1 ms`。高频更新带来的直接恶果就是臭名昭著的**“小文件爆炸（Small File Explosion）”**——而且这些碎文件的治理完全丢给了用户自己。对于习惯了 RDBMS 全自动巡航（Auto-Pilot）的开发者来说，这简直匪夷所思。

**2. 极其有限的写入并发：** Iceberg 采用乐观并发控制（OCC）。每个写入端都假设没有冲突并尝试提交新元数据；一旦两个写入任务撞车，其中一个就会失败并重试。这虽然保证了可串行化隔离，却牺牲了写入吞吐——同一张 Iceberg 表每分钟只能承受寥寥数次无冲突提交，而关系型数据库每秒可以轻松处理数千个并发事务。

**3. 读写性能的艰难权衡：** 正如 Snowflake 的 [Iceberg 官方文档](https://docs.snowflake.com/en/user-guide/tables-iceberg)所坦承的：*“查询性能主要取决于底层 Parquet 文件写得有多高效。”* 如果外部引擎写出的文件不够规整，查询速度就会一落千丈。要想用好 Iceberg，你必须持续投入计算资源去跑分区、排序和 `OPTIMIZE` 合并任务。这笔维护税在 Netflix 规模下完全值得，但普通开发者早已习惯了无需操心的托管数据库。

**4. 面向批处理与延迟数据：** Iceberg 生来就是为低频变更的大规模事实表设计的，缺乏真正的流式摄取与实时索引能力——你最终依然不得不额外部署一套实时列存系统。

## 那么，各方都在如何尝试“修补” Iceberg？ {#so-whos-fixing-iceberg-and-how}

- **AWS / Cloudflare R2：** *“我只负责托管你的文件，剩下的都是你自己的问题。”* 给你提供基础的 CDC 连接器和按量计费的后台 Compaction，但小文件爆炸的账单与查询调优依然由你买单。
- **Snowflake：** *“它完全兼容 Iceberg——只要你把管理权交给我。”* 读取外部 Iceberg 表没问题；但如果你想要高性能写入和自动优化？请把它转换成 Snowflake 托管的 Iceberg 表——本质上就是披了一层 Iceberg 外壳的 Snowflake（例如 Snowflake 会写出最契合自家缓存节点的 16MB Parquet 文件，而外部引擎通常推荐 256MB–1GB）。
- **DuckLake（DuckDB 团队）：** *“Iceberg 的元数据规范从根上就错了，我们重写一套吧。”* 不再往 S3 里塞几十个 JSON/Avro 清单文件，而是直接把元数据存在真正的嵌入式关系型数据库（DuckDB / SQLite / Postgres）里，从而实现极速规划与高并发事务。
- **Apache Hudi / Paimon：** *“Iceberg 格式本身太难支持流式更新了，我们造个新格式。”* 面向事件流驱动场景（如 Uber、阿里巴巴），将 Compaction、索引和 LSM 树直接内建到表格式规范中。

## 如果直接赋予 Iceberg 真正的数据库工程学（Database Ergonomics）呢？ {#what-if-iceberg-just-had-regular-database-ergonomics}

在外人看来，“大数据工程师”和“数据库内核工程师”似乎差不多；但我们看待同一份规范的视角截然不同。

大数据背景的工程师看到“表（Table）”时，想到的是 JSON 元数据文件、定时 Compaction 管道、最终一致的 Catalog 状态——“脏数据留给晚上的 Spark 任务去清理就好了”。

而作为一名写了十年数据库内核的工程师，我脑海里第一反应是：**索引、并发控制、事务隔离、热数据写入缓冲、查询优化**。我一直在想：如果我们把关系型数据库里最成熟、最天经地义的内核机制提取出来，作为一层实时引擎包裹在 Iceberg 之上呢？如果我们不再把 Iceberg 当成供在神坛上的文件规范，而是把它视为现代 RDBMS 的开放后端存储层呢？

让我们设定几条连 SQLite 都能轻松做到的基本底线：

**1. 真正可用的高并发写入与流式摄取**
告别“单写入端”限制与重试风暴，允许多个写入端并发追加、更新甚至删除数据，且不会互相覆盖或往 S3 里倾倒海量元数据垃圾。

**2. 永远不会阻塞或中断写入的后台自动优化**
后台 Compaction 应当全自动、无锁、持续在线运行，永远不会与正在进行的业务查询或实时写入发生冲突回滚。

**3. 原生内建的索引与智能缓存**
不是所有查询都应该退化为十亿行全表扫描。支持在表上定义主键哈希索引、倒排索引或向量索引，并与表数据一同持久化，供任意计算引擎加速检索。

## 最不可思议的是：这其实并不难实现 {#the-crazy-part-its-actually-not-that-hard}

这既不是天方夜谭，甚至都不算什么全新发明——我们在关系型数据库内核里已经把这套机制锤炼了几十年：

- 用轻量级 WAL 记录已提交的实时变更；
- 维护主键哈希索引，将按值更新/删除直接转化为精准的位置删除向量（Positional Deletion Vectors），告别全表扫描；
- 记录后台 Compaction 的文件映射状态，在合并期间自动重映射（Remap）并发到达的删除与更新，实现零冲突提交；
- 将构建好的索引打包为符合标准的 Iceberg Puffin 文件，随表一同存储在对象存储上。

这样一来，你完整保留了开放格式、存算分离、时间旅行与跨引擎互操作；同时你又获得了真正关系型数据库般的丝滑体验与实时性能。

**Apache Iceberg 不需要被推翻重来——它只需要一点帮助，学会像真正的数据库一样思考。**

这就是 🥮 的使命——从 [Moonlink](/zh/docs/intro/moonlink/) 开始，提供开箱即用、亚秒级延迟的 Postgres 到 Iceberg 实时同步。
