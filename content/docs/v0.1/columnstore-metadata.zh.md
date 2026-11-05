---
title: "v0.1 在 Postgres 外部查询列存表"
linkTitle: "v0.1 元数据与外部查询"
description: "在 pg_mooncake v0.1 中查看 mooncake.columnstore_tables 与 mooncake.data_files，并通过 Python Polars 读取 Delta Lake 表。"
weight: 50
icon: fa-solid fa-table-list
upstream_link: https://web.archive.org/web/20260124111848/https://docs.mooncake.dev/pg/0.1/reference/columnstore-metadata
aliases:
  - "/zh/pg/0.1/reference/columnstore-metadata/"
  - "/zh/0.1/reference/columnstore-metadata/"
---

> [!WARNING] `pg_mooncake v0.1` 历史归档文档（Delta Lake 引擎）
> 本页归档的是早期 **`pg_mooncake v0.1`** 版本文档（采用直接 `CREATE TABLE ... USING columnstore` DDL 与 Delta Lake 存储）。从 `v0.2` 及 PGSTY 维护的 **`v0.3.0`** 版本起，`pg_mooncake` 已全面转向基于 [`moonlink`](/zh/docs/intro/moonlink/) 的实时列存镜像架构（`CALL mooncake.create_table` + `USING mooncake`）与 Apache Iceberg v2。最新文档请参阅[简介](/zh/docs/intro/)与 [v0.1 与 v0.2 / v0.3 架构演进对比](/zh/docs/intro/0.1-vs-0.2/)。

> [!NOTE] 当前 `v0.3.0` 元数据查询函数
> 在 `v0.2` 与 `v0.3.0` 中，请使用 `SELECT * FROM mooncake.list_tables();` 查看表 LSN 进度与 Apache Iceberg v2 仓库路径。

## 查找表物理路径（`v0.1`）

在 `v0.1` 中，`mooncake.columnstore_tables` 目录表记录了每张 `USING columnstore` 表的 Delta Lake 存储路径：

```sql
SELECT * FROM mooncake.columnstore_tables;
```

## 查看底层 Parquet 数据文件（`v0.1`）

```sql
SELECT * FROM mooncake.data_files;
```

## 使用 Python Polars 直接读取 `v0.1` Delta Lake 表

```python
import polars as pl

local_path = "/usr/local/pgsql/data/mooncake_local_tables/mooncake_postgres_users_columnstore_16446/"
df = pl.scan_delta(local_path)
print(df.collect())
```
