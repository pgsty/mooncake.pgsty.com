---
title: "v0.1 GUC 配置参数"
linkTitle: "v0.1 配置参数"
description: "pg_mooncake v0.1 历史 GUC 配置变量（mooncake.default_bucket、maximum_memory、maximum_threads 等）。"
weight: 55
icon: fa-solid fa-sliders
upstream_link: https://web.archive.org/web/20251207095602/https://docs.mooncake.dev/pg/0.1/reference/configurations
aliases:
  - "/zh/pg/0.1/reference/configurations/"
  - "/zh/0.1/reference/configurations/"
---

> [!WARNING] `pg_mooncake v0.1` 历史归档文档（Delta Lake 引擎）
> 本页归档的是早期 **`pg_mooncake v0.1`** 版本文档（采用直接 `CREATE TABLE ... USING columnstore` DDL 与 Delta Lake 存储）。从 `v0.2` 及 PGSTY 维护的 **`v0.3.0`** 版本起，`pg_mooncake` 已全面转向基于 [`moonlink`](/zh/docs/intro/moonlink/) 的实时列存镜像架构（`CALL mooncake.create_table` + `USING mooncake`）与 Apache Iceberg v2。最新文档请参阅[简介](/zh/docs/intro/)与 [v0.1 与 v0.2 / v0.3 架构演进对比](/zh/docs/intro/0.1-vs-0.2/)。

## `v0.1` GUC 参数一览

```sql
-- 默认对象存储桶
ALTER DATABASE <database_name> SET mooncake.default_bucket = 's3://my-bucket';

-- 分配给 DuckDB 的内存上限（v0.1.1+，默认 4GB）
ALTER DATABASE <database_name> SET mooncake.maximum_memory = '6GB';
CALL mooncake.reset_duckdb();

-- DuckDB 并行工作线程数（v0.1.1+，默认 -1 表示使用全部核心）
ALTER DATABASE <database_name> SET mooncake.maximum_threads = -1;

-- 本地磁盘写缓存（默认 true）
ALTER DATABASE <database_name> SET mooncake.enable_local_cache = false;

-- Parquet 元数据内存缓存（默认 true）
ALTER DATABASE <database_name> SET mooncake.enable_memory_metadata_cache = false;
```
