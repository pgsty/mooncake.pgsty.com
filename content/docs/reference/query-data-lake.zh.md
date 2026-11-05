---
title: "在 Postgres 中直接查询外部数据湖"
linkTitle: "查询外部数据湖"
description: "通过 pg_duckdb 在 PostgreSQL 内直接查询外部 Parquet、CSV、JSON、Apache Iceberg、Delta Lake 及 HuggingFace 数据集，并与本地表关联。"
weight: 40
icon: fa-solid fa-folder-open
upstream_link: https://web.archive.org/web/20251207105427/https://docs.mooncake.dev/pg/reference/query-data-lake
aliases:
  - "/zh/pg/reference/query-data-lake/"
  - "/zh/reference/query-data-lake/"
  - "/zh/reference/query-external-files/"
---

由于 `pg_mooncake`（`v0.3.0`）通过 **`pg_duckdb 1.2.0`** 内嵌了 **DuckDB `v2.0.0`** 引擎，你可以在不将数据事先导入本地堆表的情况下，直接从 PostgreSQL 查询外部数据湖（本地磁盘、AWS S3、Cloudflare R2、GCS、HTTP 或 HuggingFace `hf://` 数据集）中的文件。

## 支持的外部文件与表格式 {#formats}

- **Apache Parquet**（`duckdb.read_parquet`）
- **CSV / TSV**（`duckdb.read_csv`）
- **JSON / NDJSON**（`duckdb.read_json`）
- **Apache Iceberg**（`duckdb.iceberg_scan`）
- **Delta Lake**（`duckdb.delta_scan`）

> [!NOTE] `v0.2` / `v0.3`（`duckdb.*`）与旧版 `v0.1`（`mooncake.*`）函数区别
> 在 `pg_mooncake v0.2` 与 `v0.3.0` 中，外部文件读取函数由 `pg_duckdb` 直接提供（即 `duckdb.read_parquet`、`duckdb.read_csv`、`duckdb.iceberg_scan`、`duckdb.delta_scan`）。如果你需要查阅旧版 `v0.1` 的 `mooncake.read_parquet` 语法，请参阅 [v0.1 查询外部文件](/zh/docs/v0.1/query-external-files/)。

## 1. 查询 Parquet 文件（`duckdb.read_parquet`） {#parquet}

调用 `duckdb.read_parquet` 并在 `AS (...)` 子句中声明返回的列结构：

```sql
-- 直接查询 S3 上的单个 Parquet 文件或通配符路径
SELECT
    user_id,
    event_type,
    created_at
FROM duckdb.read_parquet('s3://my-bucket/events/*.parquet') AS (
    user_id INT,
    event_type TEXT,
    created_at TIMESTAMP
)
WHERE created_at >= '2026-01-01';
```

也支持直接扫描按 Hive 分区目录组织的文件集合：

```sql
SELECT *
FROM duckdb.read_parquet('s3://my-bucket/events/year=2026/month=*/day=*/*.parquet') AS (
    user_id INT,
    event_type TEXT,
    created_at TIMESTAMP
);
```

## 2. 查询 CSV 文件（`duckdb.read_csv`） {#csv}

```sql
SELECT
    user_id,
    event_type,
    created_at
FROM duckdb.read_csv('s3://my-bucket/events.csv') AS (
    user_id INT,
    event_type TEXT,
    created_at TIMESTAMP
)
WHERE created_at >= '2026-01-01';
```

## 3. 查询外部 Iceberg 与 Delta Lake 表 {#iceberg-delta}

首先通过 `duckdb.install_extension` 安装并启用 DuckDB 的 `iceberg` 或 `delta` 扩展：

```sql
SELECT duckdb.install_extension('iceberg');
SELECT duckdb.install_extension('delta');

-- 直接查询外部 Apache Iceberg 表
SELECT
    user_id,
    event_type,
    created_at
FROM duckdb.iceberg_scan('s3://my-bucket/iceberg_events/metadata/v1.metadata.json') AS (
    user_id INT,
    event_type TEXT,
    created_at TIMESTAMP
)
WHERE created_at >= '2026-01-01';

-- 直接查询外部 Delta Lake 表
SELECT
    user_id,
    event_type,
    created_at
FROM duckdb.delta_scan('s3://my-bucket/delta_events') AS (
    user_id INT,
    event_type TEXT,
    created_at TIMESTAMP
)
WHERE created_at >= '2026-01-01';
```

## 4. 将外部数据湖文件与 PostgreSQL 本地表关联（JOIN） {#joins}

你可以在单条 SQL 查询中将外部 Parquet、Iceberg 或 Delta Lake 数据集与 PostgreSQL 普通行存表或 `USING mooncake` 列存镜像表直接 `JOIN`：

```sql
SELECT
    u.username,
    u.email,
    e.event_type,
    e.created_at
FROM users u
JOIN duckdb.read_parquet('s3://my-bucket/events.parquet') AS e(
    user_id INT,
    event_type TEXT,
    created_at TIMESTAMP
) ON u.id = e.user_id
WHERE e.created_at >= '2026-01-01';
```

## 5. 直接查询 HuggingFace 数据集（`hf://`） {#huggingface}

DuckDB 原生支持通过 `hf://datasets/<org>/<repo>/<path>` 协议直接流式读取公开的 HuggingFace 数据集：

```sql
SELECT id, message, timestamp
FROM duckdb.read_parquet(
    'hf://datasets/OpenLeecher/lmsys_chat_1m_clean/data/train-00000-of-00004.parquet'
) AS (
    id INT,
    message TEXT,
    timestamp TIMESTAMP
)
LIMIT 20;
```
