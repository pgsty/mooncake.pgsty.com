---
title: "pg_mooncake v0.2 架构前瞻：开箱即用的实时列存与逻辑复制"
date: 2025-02-11
description: "让开箱即用的 Postgres 实时分析成为现实：基于逻辑复制的堆表到列存表同步、高频小批量写入缓冲与 Apache Iceberg 集成。"
author: "[Pranav Aurora](https://github.com/paurora17) · [Mooncake Labs](https://github.com/Mooncake-Labs)"
authors: ["pranav-aurora"]
tags:
  - "release"
  - "pg_mooncake"
  - "moonlink"
  - "iceberg"
upstream_link: "https://www.mooncake.dev/blog/pgmooncake-v02discussion"
upstream_copyright: "© 2025 Pranav Aurora (Mooncake Labs Inc.)"
aliases:
  - "/zh/blog/pgmooncake-v02discussion/"
  - "/zh/blog/post/pgmooncake-v02discussion/"
images: ["/blog/covers/pgmooncake-v02discussion.svg"]
---

在 v0.1 中，我们证明了 PostgreSQL 完全能够提供顶级的分析性能。通过将 DuckDB 向量化执行引擎与列存表相结合，[`pg_mooncake`](/zh/docs/intro/) 成为了 Postgres 生态中唯一同时集成这两大能力的扩展。

实测成绩说明了一切：`pg_mooncake` 闯入了 [ClickBench 全球前十](/zh/blog/post/clickbench-v0.1/)，并打造出了最快的基于 Parquet 的执行引擎。

现在，在 v0.2 中，我们正在攻克下一个核心挑战——我们称之为**“开箱即用的分析（Out-of-the-Box Analytics）”**。

## 为什么要在 Postgres 内部直接做分析？ {#first-why-in-postgres-analytics}

绝大多数应用在真正拥有第一套数据仓库或专用分析系统之前，早就已经产生了迫切的分析查询需求。

我们见过无数次相同的故事：团队不得不推迟产品路线图、搭建通往外部系统的数据同步管道、招聘专职数据工程师维护 ETL——同时还要在应用层把 Postgres 里的实时业务数据与外部系统里的分析数据手工拼凑在一起。

`pg_mooncake` 彻底消除了这种复杂性。借助列存表，开发者可以在同一个 Postgres 数据库中同时处理事务型（OLTP）与分析型（OLAP）负载——没有外部系统，没有脆弱的 ETL 管道，只有纯粹的 Postgres。

在 v0.2 中，我们重点围绕以下几个核心方向展开架构演进：

### 1. 完善的 Postgres 表访问方法（TAM）与兼容性 [(#80)](https://github.com/Mooncake-Labs/pg_mooncake/issues/80) {#1-full-postgres-table-access-method-tam-for-columnstore-tables-80}

在 v0.1 中，所有针对列存表的读写都直接穿透到 DuckDB 执行，虽然带来了极高的扫描性能，但也导致部分 Postgres 原生特性（如数据修改 CTE、触发器等）受限。在 v0.2 中，我们将源表的写入完全交回给 Postgres 原生堆表，由 DuckDB 专注于高速列存扫描与计算下推。

### 2. 基于逻辑复制（Logical Replication）的列存镜像同步 [(#90)](https://github.com/Mooncake-Labs/pg_mooncake/issues/90) {#2-logical-replication-into-columnstore-tables-90}

许多用户都是在现有 Postgres 业务表遇到慢查询瓶颈后开始引入 `pg_mooncake` 的。通过引入逻辑复制架构（参见 [`mooncake.create_table`](/zh/docs/reference/create-columnstore/)），用户无需修改任何业务端写入代码，只需一条命令即可将现有 Postgres 堆表（或远程 RDS / Cloud SQL / Neon / Supabase 表）的数据实时同步至列存镜像表中。

### 3. 面向高频小写入的内存/行存写缓冲 [(#89)](https://github.com/Mooncake-Labs/pg_mooncake/issues/89) {#3-small-inserts-with-an-in-memory--rowstore-buffer-89}

逻辑复制带来了一个核心工程挑战：如何在高频小事务写入下，避免每个事务都生成一个零碎的 Parquet 小文件和元数据日志？

在 v0.2（基于 [Moonlink](/zh/docs/intro/moonlink/) 引擎）中，高频小批量写入会首先进入内存中的 Arrow 写缓冲区（Write Buffer），达到阈值后再由后台异步刷盘生成紧凑的 Parquet 文件。当查询列存表时，`duckdb_mooncake` 会自动合并读取内存缓冲区与底层 Parquet 文件（Union Read）。这一机制将 Parquet 文件写入与 OLTP 事务彻底解耦，大幅消除了写放大。

这一突破使得列存表无需业务层手工攒批（Batching）即可直接对接高并发 OLTP 负载，非常适合实时 HTAP、日志分析与时序数据场景。

## 这为我们带来了什么？ {#so-where-does-that-put-us}

`pg_mooncake` 是获取 Postgres 原生极速分析最简单的方式。随着 v0.2（以及 PGSTY 维护的 [`v0.3.0` 版本](/zh/blog/release/pg-mooncake-0.3.0/)）的落地，三大核心场景得到了全面增强：

1. **面向用户的实时分析（User-Facing Analytics）** —— 完整的 ORM 支持、与普通 Postgres 表直接 JOIN、只需运维一套数据库；
2. **日志、对话历史与时序数据** —— 针对高频追加写入深度优化，兼具 Parquet 高压缩率与低存储成本；
3. **开箱即用的开放数据湖仓** —— 将 Postgres 变身为实时生成 Apache Iceberg 快照的引擎，并配合具备[文件跳过与行组裁剪能力](/zh/blog/post/duckdb-parquet/)的极速 Parquet 执行引擎。
