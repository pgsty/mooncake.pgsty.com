---
title: "v0.1 查询外部数据文件"
linkTitle: "v0.1 查询外部文件"
description: "在 pg_mooncake v0.1 中使用 mooncake.read_parquet、mooncake.read_csv 与 mooncake.read_json 直接查询外部数据文件。"
weight: 65
icon: fa-solid fa-folder-open
upstream_link: https://web.archive.org/web/20251207090831/https://docs.mooncake.dev/pg/0.1/reference/query-external-files
aliases:
  - "/zh/pg/0.1/reference/query-external-files/"
  - "/zh/0.1/reference/query-external-files/"
---

> [!WARNING] `pg_mooncake v0.1` 历史归档文档（Delta Lake 引擎）
> 本页归档的是早期 **`pg_mooncake v0.1`** 版本文档（采用直接 `CREATE TABLE ... USING columnstore` DDL 与 Delta Lake 存储）。从 `v0.2` 及 PGSTY 维护的 **`v0.3.0`** 版本起，`pg_mooncake` 已全面转向基于 [`moonlink`](/zh/docs/intro/moonlink/) 的实时列存镜像架构（`CALL mooncake.create_table` + `USING mooncake`）与 Apache Iceberg v2。最新文档请参阅[简介](/zh/docs/intro/)与 [v0.1 与 v0.2 / v0.3 架构演进对比](/zh/docs/intro/0.1-vs-0.2/)。

> [!NOTE] 当前 `v0.3.0` 外部文件读取方式
> 在 `v0.2` 与 `v0.3.0` 中，请使用 `duckdb.read_parquet`、`duckdb.read_csv`、`duckdb.iceberg_scan` 与 `duckdb.delta_scan`，详见[在 Postgres 中查询外部数据湖](/zh/docs/reference/query-data-lake/)。

## 查询 Parquet、CSV 与 JSON 文件（`v0.1`）

```sql
-- Parquet
SELECT user_id, event_type, created_at
FROM mooncake.read_parquet('s3://bucket/events.parquet') AS (
    user_id INT,
    event_type TEXT,
    created_at TIMESTAMP
)
WHERE created_at > '2023-01-01';

-- CSV
SELECT r['user_id']::INT, r['event_type'], r['created_at']::TIMESTAMP
FROM mooncake.read_csv('s3://bucket/events.csv', AUTO_DETECT=TRUE) r
WHERE r['created_at']::TIMESTAMP > '2023-01-01';

-- JSON
SELECT
    json_extract_path_text(data, 'user_id')::INT AS user_id,
    json_extract_path_text(data, 'event_type') AS event_type
FROM mooncake.read_json('s3://bucket/events.json') AS (data JSONB);
```

## 查询 Iceberg 与 Delta Lake 表（`v0.1`）

```sql
SELECT * FROM iceberg_scan('s3://bucket/iceberg_table') AS (
    user_id INT, event_type TEXT, created_at TIMESTAMP
);

SELECT * FROM delta_scan('s3://bucket/delta_table') AS (
    user_id INT, event_type TEXT, created_at TIMESTAMP
);
```
