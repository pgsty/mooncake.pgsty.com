---
title: "v0.1 架构说明 (Delta Lake 与 USING columnstore)"
linkTitle: "v0.1 架构说明"
description: "pg_mooncake v0.1 架构解析：USING columnstore 表访问方法、Parquet + Delta Lake 元数据以及 DuckDB 读写路径。"
weight: 10
icon: fa-solid fa-sitemap
upstream_link: https://web.archive.org/web/20260124120319/https://docs.mooncake.dev/pg/0.1/intro/architecture
aliases:
  - "/zh/pg/0.1/intro/architecture/"
  - "/zh/0.1/intro/architecture/"
---

> [!WARNING] `pg_mooncake v0.1` 历史归档文档（Delta Lake 引擎）
> 本页归档的是早期 **`pg_mooncake v0.1`** 版本文档（采用直接 `CREATE TABLE ... USING columnstore` DDL 与 Delta Lake 存储）。从 `v0.2` 及 PGSTY 维护的 **`v0.3.0`** 版本起，`pg_mooncake` 已全面转向基于 [`moonlink`](/zh/docs/intro/moonlink/) 的实时列存镜像架构（`CALL mooncake.create_table` + `USING mooncake`）与 Apache Iceberg v2。最新文档请参阅[简介](/zh/docs/intro/)与 [v0.1 与 v0.2 / v0.3 架构演进对比](/zh/docs/intro/0.1-vs-0.2/)。

在 `pg_mooncake v0.1` 中，表级事务元数据保存在 PostgreSQL 系统目录中以保证事务一致性，而列存数据本身则以 **Parquet** 文件与 **Delta Lake** 元数据形式存储在本地文件系统或云端对象存储中。

列存表作为 PostgreSQL 表访问方法（`USING columnstore`）暴露给用户，查询通过 `pg_duckdb` 路由至 DuckDB 执行。

## 读取路径（Read Path）

涉及 `USING columnstore` 表的查询由 PostgreSQL 路由至 DuckDB 执行，并在内部自动处理轻微的 SQL 语法差异转换。

![v0.1 架构示意图](/img/mooncake/architecture.jpg)

`pg_mooncake v0.1` 将 Parquet 文件元数据与列级统计信息缓存在 PostgreSQL 表（`mooncake.data_files`）中，并在扫描时利用统计信息实现**分段跳过（Segment Elimination）**。

## 写入路径（Write Path）

在 `v0.1` 中，用户直接在 `USING columnstore` 表上运行事务型 `INSERT`、`UPDATE` 与 `DELETE`。为了支持更新与删除，表扫描期间会填充由 `(file_id, row_offset)` 组成的隐式 `row_id` 列。

每次写入操作都会生成一个新的 Parquet 文件，因此 `v0.1` 更适合大批量写入（单批次 `100,000`–`1,000,000` 行），而不适合高频小事务写入。

### 本地磁盘缓存

写入时数据默认缓存在本地磁盘（`mooncake.enable_local_cache = true`），从而显著加速对近期写入热数据的分析查询。
