---
title: "v0.1 数据导入指南"
linkTitle: "v0.1 数据导入"
description: "在 pg_mooncake v0.1 中从 PostgreSQL 表、Parquet/CSV/JSON 文件、Iceberg/Delta 表及 HuggingFace 导入数据。"
weight: 60
icon: fa-solid fa-file-import
upstream_link: https://web.archive.org/web/20260124103442/https://docs.mooncake.dev/pg/0.1/reference/load-data
aliases:
  - "/zh/pg/0.1/reference/load-data/"
  - "/zh/0.1/reference/load-data/"
---

> [!WARNING] `pg_mooncake v0.1` 历史归档文档（Delta Lake 引擎）
> 本页归档的是早期 **`pg_mooncake v0.1`** 版本文档（采用直接 `CREATE TABLE ... USING columnstore` DDL 与 Delta Lake 存储）。从 `v0.2` 及 PGSTY 维护的 **`v0.3.0`** 版本起，`pg_mooncake` 已全面转向基于 [`moonlink`](/zh/docs/intro/moonlink/) 的实时列存镜像架构（`CALL mooncake.create_table` + `USING mooncake`）与 Apache Iceberg v2。最新文档请参阅[简介](/zh/docs/intro/)与 [v0.1 与 v0.2 / v0.3 架构演进对比](/zh/docs/intro/0.1-vs-0.2/)。

## 从 PostgreSQL 行存表导入（`v0.1`）

```sql
INSERT INTO users_columnstore
SELECT * FROM users_rowstore;
```

## 从 Parquet、CSV 或 JSON 文件导入（`v0.1`）

```sql
-- 使用 COPY 命令
COPY users_columnstore FROM 's3://bucket/file.parquet';
COPY users_columnstore FROM 's3://bucket/folder/*.parquet';
COPY users_columnstore FROM 's3://bucket/data.csv' WITH (FORMAT 'csv', HEADER true);

-- 使用 INSERT + mooncake.read_parquet
INSERT INTO users_columnstore
SELECT * FROM mooncake.read_parquet('s3://bucket/file.parquet') AS (
    id INT,
    name TEXT,
    created_at TIMESTAMP
);
```

## 从 Iceberg、Delta Lake 或 HuggingFace 导入（`v0.1`）

```sql
-- Iceberg
INSERT INTO users_columnstore
SELECT * FROM iceberg_scan('s3://bucket/table') AS (id INT, name TEXT, created_at TIMESTAMP);

-- Delta Lake
INSERT INTO users_columnstore
SELECT * FROM delta_scan('s3://bucket/table') AS (id INT, name TEXT, created_at TIMESTAMP);

-- HuggingFace
COPY users_columnstore FROM 'hf://datasets/OpenLeecher/lmsys_chat_1m_clean/data/train-00000-of-00004.parquet';
```
