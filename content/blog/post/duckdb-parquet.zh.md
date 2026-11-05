---
title: "如何让 DuckDB 在 Parquet 文件上的查询性能再上一个台阶"
date: 2025-01-22
description: "揭秘 pg_mooncake 如何借助 PostgreSQL 系统表、行组 MIN/MAX 裁剪与内存元数据缓存，在 ClickBench 上跑赢原生 DuckDB Parquet 扫描。"
author: "[Pranav Aurora](https://github.com/paurora17) · [Mooncake Labs](https://github.com/Mooncake-Labs)"
authors: ["pranav-aurora"]
tags:
  - "duckdb"
  - "parquet"
  - "pg_mooncake"
  - "benchmark"
upstream_link: "https://www.mooncake.dev/blog/duckdb-parquet"
upstream_copyright: "© 2025 Pranav Aurora (Mooncake Labs Inc.)"
aliases:
  - "/zh/blog/duckdb-parquet/"
images: ["/blog/covers/duckdb-parquet.jpg"]
---

上周，我们在 PostgreSQL 上运行了 ClickBench 基准测试并成功闯入[全球前十](/zh/blog/post/clickbench-v0.1/)，证明了通过 [`pg_mooncake`](/zh/docs/intro/) 扩展，Postgres 完全能够胜任严肃的大规模分析负载。

在成绩公布后，我们收到了许多开发者的提问：既然 `pg_mooncake` 内部嵌入了 DuckDB 并将数据存储为 Parquet 格式，**为什么它在 Parquet 文件上的查询速度反而比直接使用 DuckDB 扫描还要快？**

> 参见 [X / Twitter 上的相关讨论](https://x.com/mooncake_dev/status/1881844188905709880)。

最酷的地方在于：`pg_mooncake` 甚至一行 DuckDB 内核代码都没有修改……

## 快速回顾 pg_mooncake 的架构设计 {#a-quick-recap-of-the-pg_mooncake-design}

`pg_mooncake` 是一个为 Postgres 增加列式存储与向量化执行的扩展：

1. 列存表中的数据存储在 Parquet 文件中；
2. 表的元数据（当前有效快照包含哪些 Parquet 文件）存储在 Postgres 内部并具备事务一致性保证；
3. 针对列存表的查询交由内嵌的 DuckDB 引擎执行。

建议先阅读我们的[完整架构解析](/zh/blog/post/how-we-built-pgmooncake/)。

## “大象”是如何跑赢“鸭子”的？ {#how-can-an-elephant-catch-a-duck}

乍看之下，一个把 Postgres 查询通过 `pg_duckdb` 路由给 DuckDB 去扫描 Parquet 文件的系统，似乎不可能比 DuckDB 直接扫描那些 Parquet 文件更快。

在 [ClickBench](https://benchmark.clickhouse.com/) 榜单上，普通包装器确实存在明显开销：**`pg_duckdb`（10.21x）** 相比 **DuckDB (Parquet, partitioned)（6.76x）** 有着不小的性能损耗。

然而令人惊讶的是，尽管底层同样依赖 `pg_duckdb`，**`pg_mooncake`（6.03x）** 不仅比 `pg_duckdb` 快了约 1.5 倍，甚至反超了原生 **DuckDB (Parquet, partitioned)** 本身！

## 为什么 pg_mooncake 能跑赢原生 DuckDB Parquet？ {#so-why-does-pg_mooncake-outperform-duckdb}

首先，`pg_mooncake` 直接利用 Postgres 存储表元数据，省去了像外部 Iceberg 或 Delta Lake 表那样访问外部 Catalog 并解析多层清单文件的开销，能够直接定位当前快照需要扫描的 Parquet 文件集合。

更重要的是，`pg_mooncake` 将每个 Parquet 文件的详细元数据（包括每个行组 Row Group 的列级统计信息，如每列的 `MIN` / `MAX` 值）预先提取并维护在 Postgres（以及 `v0.2` / `v0.3` 的 Moonlink 元数据层）中。当查询列存表时，`pg_mooncake` 会利用这些统计信息在扫描前直接裁剪掉不可能包含匹配行的数据文件与行组（Segment Elimination）。

例如，对于下面这样的查询：

```sql
... WHERE order_date BETWEEN '2023-01-01' AND '2023-01-31' ...
```

任何 `order_date` 范围落在该区间之外的文件和行组都会被直接跳过。通过避免不必要的磁盘与对象存储 I/O，查询性能得到了大幅提升。

此外，由于反序列化和解析 Parquet Footer 元数据本身具有一定 CPU 开销，`pg_mooncake` 还在内存中维护了 Parquet 元数据缓存，从而额外带来了约 5% 的查询加速。

## 为什么依然坚持使用 Parquet？ {#why-still-stick-to-parquet}

我们也经常被问到这个问题：如果只追求单机极限性能，设计一种私有的内存/磁盘列存格式无疑能榨干最后一滴性能。

但我们始终坚信湖仓一体（Lakehouse）架构所带来的开放性价值。Postgres 并非为了独自包揽数据生命周期的每一个环节而设计，而采用标准 Parquet + Iceberg 格式能够实现无缝的多引擎互操作。

最重要的是，我们已经用实测数据证明：**即便坚持使用 Postgres 与开放的 Parquet 格式，你依然能够获得世界顶级的分析性能。**

## DuckDB 与 pg_mooncake 还有巨大的优化空间 {#there-are-plenty-of-optimizations-left-for-duckdb-and-pg_mooncake}

在运行 ClickBench 的过程中，我们还梳理出了针对 DuckDB 与 `pg_mooncake` 的[一系列后续优化点](https://github.com/Mooncake-Labs/pg_mooncake/issues/82)。我们非常期待与社区一起推进这些优化，将其回馈至 DuckDB 上游或以 DuckDB `OptimizerExtension` 的形式实现，让开放格式上的分析查询越来越快。

🥮
