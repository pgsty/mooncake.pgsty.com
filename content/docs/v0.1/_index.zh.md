---
title: "v0.1 历史归档：欢迎使用 pg_mooncake (Delta Lake)"
linkTitle: "v0.1 历史归档 (Delta Lake)"
description: "pg_mooncake v0.1（USING columnstore + Delta Lake 存储引擎）完整历史技术文档归档。"
weight: 50
icon: fa-solid fa-box-archive
upstream_link: https://web.archive.org/web/20251207094131/https://docs.mooncake.dev/pg/0.1/intro/
aliases:
  - "/zh/pg/0.1/"
  - "/zh/pg/0.1/intro/"
  - "/zh/0.1/"
  - "/zh/0.1/intro/"
---

> [!WARNING] `pg_mooncake v0.1` 历史归档文档（Delta Lake 引擎）
> 本页归档的是早期 **`pg_mooncake v0.1`** 版本文档（采用直接 `CREATE TABLE ... USING columnstore` DDL 与 Delta Lake 存储）。从 `v0.2` 及 PGSTY 维护的 **`v0.3.0`** 版本起，`pg_mooncake` 已全面转向基于 [`moonlink`](/zh/docs/intro/moonlink/) 的实时列存镜像架构（`CALL mooncake.create_table` + `USING mooncake`）与 Apache Iceberg v2。最新文档请参阅[简介](/zh/docs/intro/)与 [v0.1 与 v0.2 / v0.3 架构演进对比](/zh/docs/intro/0.1-vs-0.2/)。

`pg_mooncake v0.1` 是第一代 PostgreSQL 列存扩展，通过 `USING columnstore` 表访问方法与底层的 Delta Lake + DuckDB（`pg_duckdb`）提供分析加速。

![pg_mooncake 定位图](/img/mooncake/pg_mooncake_intro.jpg)

## `v0.1` 版本核心特性

1. 支持直接在 `USING columnstore` 表上执行事务型 `INSERT`、`UPDATE` 与 `DELETE`
2. 数据以 Parquet + Delta Lake 元数据格式存储在本地磁盘或 S3 / R2 对象存储上
3. 通过内嵌 DuckDB 提供向量化查询执行
4. 支持普通 PostgreSQL 堆表与 `USING columnstore` 表之间的直接关联查询

## `v0.1` 历史归档目录

| 章节 | 包含页面 |
|:---|:---|
| **架构简介** | [v0.1 架构说明](/zh/docs/v0.1/architecture/) |
| **快速开始** | [安装与启动](/zh/docs/v0.1/get-started/) · [Hello World](/zh/docs/v0.1/hello-world/) · [对象存储配置](/zh/docs/v0.1/cloud-storage/) · [在 Neon 上运行](/zh/docs/v0.1/neon-postgres/) |
| **参考手册** | [参考总览](/zh/docs/v0.1/reference/) · [列存 DDL](/zh/docs/v0.1/columnstore-ddl/) · [外部引擎查询元数据](/zh/docs/v0.1/columnstore-metadata/) · [GUC 配置参数](/zh/docs/v0.1/configurations/) · [数据导入](/zh/docs/v0.1/load-data/) · [查询外部文件](/zh/docs/v0.1/query-external-files/) · [支持的查询形态](/zh/docs/v0.1/query-shapes/) |
| **应用场景** | [数据归档](/zh/docs/v0.1/archiving/) · [操作型分析](/zh/docs/v0.1/operational-analytics/) · [数据仓库与 dbt](/zh/docs/v0.1/warehousing/) |
{.wide .expand}
