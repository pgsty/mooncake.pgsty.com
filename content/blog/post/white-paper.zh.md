---
title: "Mooncake 技术白皮书：面向 Apache Iceberg 的实时存储引擎"
date: 2025-08-11
description: "Mooncake 与 Moonlink 架构技术白皮书：深入解析 Arrow 内存写缓冲、位置删除向量、无冲突 Compaction 重映射、Puffin 原生索引与 NVMe 缓存。"
author: "[Mooncake Labs Team](https://github.com/Mooncake-Labs)"
authors: ["mooncake-labs", "zhou-sun", "cheng-chen", "pranav-aurora"]
tags:
  - "whitepaper"
  - "moonlink"
  - "iceberg"
  - "architecture"
  - "pg_mooncake"
upstream_link: "https://www.mooncake.dev/whitepaper"
upstream_copyright: "© 2025 Mooncake Labs Inc."
aliases:
  - "/zh/whitepaper/"
  - "/zh/blog/white-paper/"
  - "/zh/blog/white_paper/"
images: ["/blog/covers/white-paper.svg"]
---

这篇技术白皮书假设读者已对开放分析表格式 [Apache Iceberg](https://iceberg.apache.org/) 有所了解。Iceberg 是现代“数据湖仓（Lakehouse）”运动的核心基石，它允许用户：

1. 将大规模数据集以开放文件格式（Parquet + 元数据）存储在廉价对象存储中；
2. 使用 Spark、Trino、Flink、DuckDB 等多种计算引擎通过 SQL 直接查询；
3. 获得 Schema 演进与时间旅行（Time Travel）等数据库级特性；
4. 实现近乎无限的弹性扩展，彻底摆脱单一供应商锁定。

然而，Iceberg 生来是为低频变更数据与批量分析处理而设计的。在批处理领域，随着各大引擎对开放格式读取能力的持续优化，这套体系已经非常成熟。

但对于**实时工作负载**（面向用户的实时分析、高频 CDC 同步、流处理），企业往往不得不额外部署一套专门的实时系统（如 ClickHouse、Druid、SingleStore），并同时维护两条数据管道，在两套系统之间来回搬运数据。

如果我们能将湖仓一体的开放性与灵活性带入实时领域呢？这需要同时满足两大核心要求：

1. **绝不牺牲湖仓一体的任何生态优势**：完全兼容标准 Iceberg 生态与多引擎互操作；
2. **引入亚秒级实时数据与极速查询**：同时绝不破坏底层 Iceberg 表的读取性能与元数据整洁度（避免小文件爆炸）。

## 1. 简介 {#introduction}

**Mooncake** 是构建在 Apache Iceberg 之上的实时存储引擎。它在不牺牲数据湖仓开放性的前提下，为 Iceberg 注入了三大核心能力：

1. **高速流式摄取（Fast Ingest）**：支持流式写入与来自关系型数据库的亚秒级实时镜像同步；
2. **极速分析查询（Fast Queries）**：持续后台表优化与智能缓存；
3. **原生索引层（Indexing）**：支持低延迟搜索与主键点查。

Mooncake 的架构、索引层与写感知（Write-Aware）优化将 Iceberg 转变为一个能够直接承载面向用户的实时分析、全文检索、在线服务与 HTAP 负载的统一平台。

## 2. 整体架构 {#architecture}

```
                         DuckDB
                         Spark
                       Snowflake
                    (Iceberg-rest)
                    ▲              ▲
                    │              │
                    │              │
             ┌──────┴───moonlink───┴───────┐
             │  ┌───────────────────────┐  │
             │  │                       │  │
Postgres ───►│  │┌ ─ ─ ─ ─ ┐ ┌ ─ ─ ─ ─ ┐│  │
             │  │                       │  │
Kafka    ───►│  ││  index  │ │  cache  ││  │
             │  │                       │  │
Events   ───►│  │└ ─ ─ ─ ─ ┘ └ ─ ─ ─ ─ ┘│  │
             │  │                  nvme │  │
             │  └───────────────────────┘  │
             └─────────┬─────────┬─────────┘
                       ▼         ▼
                 ┌───────Iceberg───────┐
                 │         s3          │
                 │┌───────┐ ┌─────────┐│
                 ││       │ │         ││
                 ││ index │ │ parquet ││
                 ││       │ │         ││
                 │└───────┘ └─────────┘│
                 │                     │
                 └─────────────────────┘
```

Mooncake 的核心引擎是 [`moonlink`](/zh/docs/intro/moonlink/)——一个专为实时 CDC 与流式写入 Iceberg 而设计的 Rust 存储库。

Moonlink 为每一张 Iceberg 表配备了**内存 Arrow 写缓冲区（Arrow Buffer）**、**位置删除日志（Positional Delete Log）**以及跨越内存 / 本地 NVMe / 对象存储的**混合索引层**，用以吸收高频增删改操作。计算引擎通过联合读取（Union Read）同时扫描内存缓冲与已固化的 Iceberg 文件，从而无需等待高开销的 Iceberg 元数据提交即可获得亚秒级最新视图。

### 写入（Inserts） {#inserts}

- 新插入的行首先写入内存中的 Arrow 写缓冲区；当累积到设定阈值后，高效刷盘生成紧凑的 Parquet 文件；
- 在写入过程中同步构建内存索引，并在 Parquet 刷盘时将其持久化为对象存储原生的索引文件。

### 删除与更新（Deletions） {#deletions}

- Moonlink 为所有行维护主键哈希索引；
- 当收到 `DELETE` 或 `UPDATE` 时，利用主键索引快速定位目标行的 `(file_id, row_offset)` 并更新位置删除日志；
- 定期将位置删除日志转换为符合 Iceberg 规范的 Puffin 删除向量（Deletion Vectors）。

### 读取（Reads） {#reads}

- Moonlink 生成标准的 Iceberg 表快照，供任何外部引擎直接读取；
- 同时，Moonlink 暴露了实时联合读取接口（由 [`duckdb_mooncake`](/zh/docs/intro/duckdb-mooncake/) 调用），将内存缓冲状态与底层 Parquet/Puffin 文件无缝合并，提供强一致的亚秒级实时读取。

## 3. 核心技术深度剖析 {#core-technology-deep-dive}

### 3.1 写感知的表优化（Write-Aware Table Optimization） {#31-write-aware-table-optimization}

**最新版本的实时联合读取（Union-Read）**
传统 Iceberg 迫使用户在“数据新鲜度”与“写放大”之间做痛苦权衡：为了获得更新鲜的数据，用户必须频繁提交快照，结果产生海量微小的 Parquet 文件和 Manifest 清单文件。Mooncake 通过周期性提交 Iceberg 快照、同时在两次快照之间提供实时合并读取接口，彻底打破了这一桎梏——既保持了对象存储上 Iceberg 文件的紧凑整洁，又实现了亚秒级读取新鲜度。

**主键索引 + 位置删除向量（Deletion Vectors）处理高频更新/删除**
传统 Iceberg 在处理高频 CDC 更新时，要么依赖极其昂贵的全局 Merge-on-Read（Equality Deletes，严重拖慢读取性能并产生小文件），要么只能做高延迟批处理合并。Moonlink 维护了同时覆盖内存缓冲区与已刷盘 Parquet 文件的哈希索引，能够在微秒级定位被删改行的物理行号，并通过位图形式的 Puffin 删除向量（Roaring Bitmap）高效屏蔽旧行。

**优雅化解实时写入与后台 Compaction 的并发冲突**
在传统开放表格式中，后台 Compaction 任务与前台流式写入极易发生乐观锁冲突导致事务失败重试。Moonlink 在后台执行文件合并与重排序时，会精确维护旧文件行偏移量到新文件行偏移量的重映射表（Remapping State），自动将合并期间并发到达的删除与更新重定向到新文件上，从而实现**零事务冲突、无锁在线合并**。

### 3.2 Iceberg 原生索引架构 {#32-iceberg-native-indexing}

**索引存储格式**

- 索引元数据以标准 Iceberg Puffin 文件形式存储；
- 每个索引文件对应一个或多个底层 Parquet 数据文件，并由后台以 LSM 树方式分层合并（Index Merge）。

**索引类型实现**

- **分桶哈希表（Bucket Hash Table）**：面向高基数主键的不可变、按哈希序排列的類 SSTable 索引结构（`mooncake_hash_index`），将 64 位哈希值映射至 `(file_id, row_offset)`，将按值删除高效转化为位置删除。
- **分桶哈希表 + 倒排索引**：面向低基数列与全文检索（GIN）的合并式倒排索引。
- **向量索引**：面向 AI 检索的对象存储原生分块 IVF 向量索引。

### 3.3 托管缓冲区与多级缓存 {#33-managed-buffer-and-cache}

- **对象存储原生 WAL**：对象存储是唯一的持久事实来源，节点恢复时可直接重放 WAL；
- **Arrow 内存流式写缓冲**：支持单机百万级更新吞吐，并可直接向实时计算引擎零拷贝传输 Arrow/Parquet 数据；
- **NVMe 读写穿透缓存**：最新生成的 Parquet、删除向量与索引文件先落盘本地 NVMe，再异步上传至 S3，使本地读写延迟稳定在 `<5 ms`。

## 4. 部署形态与解决方案 {#deployment--solutions}

### 4.1 [`pg_mooncake`](/zh/docs/intro/) {#41-pg_mooncake}

在 PostgreSQL 内部一站式实现 HTAP、实时分析与 Iceberg 湖仓同步。`pg_mooncake` 在 Postgres 后台工作进程中运行内嵌的 Moonlink 引擎，并通过 `pg_duckdb` 嵌入 DuckDB 作为向量化执行引擎（MIT 许可）。

只需调用 [`CALL mooncake.create_table('T_mooncake', 'T_heap')`](/zh/docs/reference/create-columnstore/)，即可为任意 Postgres 堆表创建亚秒级实时同步、支持 LSN 强一致快照读取的列存镜像表。

### 4.2 [独立运行的 `moonlink` 服务](/zh/docs/intro/moonlink/) {#42-stand-alone-moonlink}

无状态的 Rust 实时同步与流式摄取服务，支持通过逻辑复制或 HTTP/gRPC 接口摄取变更并直接写入 Apache Iceberg，以极低开销维护随时可查的实时湖仓表。
