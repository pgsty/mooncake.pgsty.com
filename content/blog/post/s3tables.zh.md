---
title: "S3 Tables 究竟是个啥？"
date: 2025-01-12
description: "我替你啃完了 AWS S3 Tables 的文档：剖析 S3 表存储桶如何让 Apache Iceberg 摆脱外部 Catalog，以及它对 Postgres 意味着什么。"
author: "[Zhou Sun](https://github.com/zhousun) · [Mooncake Labs](https://github.com/Mooncake-Labs)"
authors: ["zhou-sun"]
tags:
  - "s3"
  - "iceberg"
  - "lakehouse"
upstream_link: "https://www.mooncake.dev/blog/s3tables"
upstream_copyright: "© 2025 Zhou Sun (Mooncake Labs Inc.)"
aliases:
  - "/zh/blog/s3tables/"
images: ["/blog/covers/s3tables.jpg"]
---

亚马逊在去年的 re:Invent 大会上发布了 [S3 Table Buckets（S3 表存储桶）](https://aws.amazon.com/s3/features/tables/)。一个既是 S3 存储桶、同时又是一张数据库表的东西？这到底是什么意思？

**太长不看版（TL;DR）：** S3 Tables 让 Apache Iceberg 表可以脱离外部 Catalog（目录服务）独立存在。下面听我详细拆解。

## Iceberg vs Delta Lake {#iceberg-vs-delta-lake}

等等，Iceberg 和 Delta Lake 不都是开放表格式吗？为什么要比较它们的底层元数据实现方式？

原因在于，由于元数据设计的根本差异，Iceberg 与 Delta Lake 之间有一个至关重要的区别：**“Delta 表可以脱离 Catalog 独立存在，而 Iceberg 表不行”**：

**1. Delta Lake 依赖底层文件系统在元数据层实现 ACID。**

`_delta_log` 目录中的元数据层本质上是一个不断追加的 JSON 文件有序列表。只要一个目录下包含 Delta 表，你只需要按照文件名顺序逐个读取 `_delta_log` 中的文件，就能还原出整张表的当前状态。

你不需要任何额外信息或外部“Catalog”就能直接读写 Delta 表。

**2. 相反，Iceberg 与存储层解耦，依赖外部 Catalog 来实现 ACID。**

Iceberg 的元数据层是一个由快照节点（Snapshot Nodes）构成的**反向链表**（从 `SNAPSHOT N+1` 可以找到 `SNAPSHOT N`，但反过来不行）。

因此，你必须依赖一个外部“Catalog”来原子性地写入并获取最新快照指针（Metadata Location）。

那么问题来了：如果底层对象存储系统自己就能一致地“记住”当前快照指针，并提供原子交换（Atomic Swap）接口呢？Bingo，这就是 **S3 Table Bucket**！

## 向 S3 Table Buckets 写入数据究竟是如何工作的？ {#how-does-writing-to-s3-table-buckets-actually-work}

我花了不少时间啃完了 [S3 Tables 官方文档](https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-tables.html)，这样你就不用再去受罪了（顺便吐槽一句，这文档写得极其晦涩，连 DeepSeek 读起来都费劲）。

我们来对比一下向“普通 Iceberg Catalog”与向“S3 Table”写入数据的流程差异：

1. **[两者相同]** 计算引擎写入数据文件（Parquet）
2. **[两者相同]** 计算引擎写入 Iceberg 元数据文件（Manifest / Metadata JSON）
3. **[仅普通 Catalog]** 请求外部 Catalog 提交新快照
4. **[仅 S3 Table]** 调用 S3 API `update-table-metadata-location` 完成原子提交

没错，这就是唯一的区别。

## 那么 S3 Tables 的核心优势是什么？ {#what-are-the-benefits-of-s3-tables-then}

我确信亚马逊在底层性能（包括自动 Compaction 和存储桶物理布局）上做了大量优化工作。

但在功能语义上，最核心的区别在于：

**S3 Tables 允许你按路径读写存储桶中的任意文件，但禁止执行 `LIST`（列举文件）操作。**

第一眼看到这个限制时我觉得很蠢，但仔细一想却非常精妙：

这意味着“探测”一个表存储桶的唯一途径，就是先读取该存储桶维护的 `metadata-location` 元数据指针。因此在设计上，任何用户都只能读取属于当前有效表快照的数据文件，因为你根本没有办法通过列举目录去发现任何其他孤儿文件或未提交文件。

## 谁最适合使用 S3 Tables？ {#so-who-should-use-s3-tables}

我认为它的真正用武之地可能和大多数人想的完全不同。

对于超大规模企业级湖仓（Enterprise Lakehouse）而言，维护一套集中式的外部 Catalog（如 Unity Catalog、Polaris）和统一的表维护服务本来就是顺理成章的事；更何况 S3 Tables 的单价依然比普通 S3 贵不少。因此我并不认为大型企业湖仓会是它的主力场景。

在我看来，S3 Tables 最适合**中小规模团队与轻量级分析场景**，尤其是嵌入到现有应用工作流中——它让你无需运维任何外部 Catalog 就能直接用上标准的 Iceberg 表。

最后给出我的一个预言：***第一个支持写入 S3 Tables 的计算引擎是 Spark，而第二个将会是 Postgres。***

🥮
