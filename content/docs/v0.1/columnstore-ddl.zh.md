---
title: "v0.1 列存表 DDL (USING columnstore)"
linkTitle: "v0.1 列存 DDL"
description: "在 pg_mooncake v0.1 中使用 USING columnstore 创建与删除列存表、支持的数据类型与约束说明。"
weight: 45
icon: fa-solid fa-code
upstream_link: https://web.archive.org/web/20260124114208/https://docs.mooncake.dev/pg/0.1/reference/columnstore-ddl
aliases:
  - "/zh/pg/0.1/reference/columnstore-ddl/"
  - "/zh/0.1/reference/columnstore-ddl/"
---

> [!WARNING] `pg_mooncake v0.1` 历史归档文档（Delta Lake 引擎）
> 本页归档的是早期 **`pg_mooncake v0.1`** 版本文档（采用直接 `CREATE TABLE ... USING columnstore` DDL 与 Delta Lake 存储）。从 `v0.2` 及 PGSTY 维护的 **`v0.3.0`** 版本起，`pg_mooncake` 已全面转向基于 [`moonlink`](/zh/docs/intro/moonlink/) 的实时列存镜像架构（`CALL mooncake.create_table` + `USING mooncake`）与 Apache Iceberg v2。最新文档请参阅[简介](/zh/docs/intro/)与 [v0.1 与 v0.2 / v0.3 架构演进对比](/zh/docs/intro/0.1-vs-0.2/)。

## 创建列存表（`v0.1`）

在 `v0.1` 中，列存表通过在 `CREATE TABLE` 时附加 `USING columnstore` 子句直接创建：

```sql
CREATE TABLE users_columnstore (
    id INT,
    name TEXT,
    created_at TIMESTAMP
) USING columnstore;

-- 或通过 CREATE TABLE ... AS SELECT 创建
CREATE TABLE users_columnstore USING columnstore AS
    SELECT * FROM users_rowstore;
```

## 删除列存表

```sql
DROP TABLE users_columnstore;
```

## `v0.1` 支持的特性与限制

- **支持**：`INSERT`、`UPDATE`、`DELETE`、ACID 事务、`NOT NULL` 约束、默认值以及与行存表的关联查询。
- **`v0.1` 不支持的数据类型**：`ENUM`、`uhugeint`、`JSONB`（早期受限）以及部分数组类型。
- **`v0.1` 不支持的约束**：主键、外键、唯一约束、索引以及分区表（修改表结构需重建表）。

## 将 `columnstore` 设为默认表访问方法（`v0.1`）

```sql
SET default_table_access_method = 'columnstore';
```
