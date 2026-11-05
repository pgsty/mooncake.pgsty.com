---
title: "v0.1 参考手册总览"
linkTitle: "v0.1 参考总览"
description: "pg_mooncake v0.1 DDL 语法、Delta Lake 元数据表、GUC 配置参数、数据导入与外部文件查询参考索引。"
weight: 40
icon: fa-solid fa-book-open
upstream_link: https://web.archive.org/web/20251207093616/https://docs.mooncake.dev/pg/0.1/reference/
aliases:
  - "/zh/pg/0.1/reference/"
  - "/zh/0.1/reference/"
---

> [!WARNING] `pg_mooncake v0.1` 历史归档文档（Delta Lake 引擎）
> 本页归档的是早期 **`pg_mooncake v0.1`** 版本文档（采用直接 `CREATE TABLE ... USING columnstore` DDL 与 Delta Lake 存储）。从 `v0.2` 及 PGSTY 维护的 **`v0.3.0`** 版本起，`pg_mooncake` 已全面转向基于 [`moonlink`](/zh/docs/intro/moonlink/) 的实时列存镜像架构（`CALL mooncake.create_table` + `USING mooncake`）与 Apache Iceberg v2。最新文档请参阅[简介](/zh/docs/intro/)与 [v0.1 与 v0.2 / v0.3 架构演进对比](/zh/docs/intro/0.1-vs-0.2/)。

- [v0.1 列存表 DDL（`USING columnstore`）](/zh/docs/v0.1/columnstore-ddl/)
- [v0.1 在 Postgres 外部查询列存表（`mooncake.columnstore_tables`）](/zh/docs/v0.1/columnstore-metadata/)
- [v0.1 GUC 配置参数（`mooncake.maximum_memory`、`mooncake.maximum_threads`）](/zh/docs/v0.1/configurations/)
- [v0.1 数据导入（`COPY` 与 `mooncake.read_parquet`）](/zh/docs/v0.1/load-data/)
- [v0.1 查询外部文件（`mooncake.read_parquet`、`mooncake.read_csv`、`iceberg_scan`、`delta_scan`）](/zh/docs/v0.1/query-external-files/)
- [v0.1 支持的查询形态](/zh/docs/v0.1/query-shapes/)
