---
title: "Apache Iceberg v2 与对象存储配置"
linkTitle: "Iceberg 与对象存储"
description: "为 pg_mooncake 配置 AWS S3、Cloudflare R2 或本地存储，调用 mooncake.create_snapshot 生成 Apache Iceberg v2 快照，并从外部计算引擎直接读取。"
weight: 30
icon: fa-solid fa-cloud
upstream_link: https://web.archive.org/web/20251207105746/https://docs.mooncake.dev/pg/reference/iceberg
aliases:
  - "/zh/pg/reference/iceberg/"
  - "/zh/reference/iceberg/"
---

`pg_mooncake`（`v0.3.0`）中的每一张列存镜像表均由 [`moonlink`](/zh/docs/intro/moonlink/) 驱动，底层数据存储为标准的 **Parquet** 文件，并自动维护 **Apache Iceberg v2** 表元数据。

默认情况下，Moonlink 将文件保存在本地数据目录 `$PGDATA/pg_mooncake/` 下。你可以配置 `pg_mooncake` 直接将数据写入 **Amazon S3**、**Cloudflare R2**、**MinIO** 或 **Google Cloud Storage (GCS)**，从而让外部数据湖计算引擎（DuckDB、Apache Spark、Trino、Snowflake、PyIceberg）直接从对象存储读取你的 PostgreSQL 表数据。

## 1. 配置对象存储访问凭据（`duckdb.secrets`） {#secrets}

`pg_mooncake` 从 `pg_duckdb` 的 `duckdb.secrets` 表中读取对象存储凭据，并自动将其同步提供给 Moonlink 与 DuckDB。

### 配置 Amazon S3 {#s3}

```sql
INSERT INTO duckdb.secrets (name, type, key_id, secret, region, scope)
VALUES (
    's3_warehouse',
    'S3',
    '<AWS_ACCESS_KEY_ID>',
    '<AWS_SECRET_ACCESS_KEY>',
    'us-east-1',
    's3://my-mooncake-bucket'
);
```

### 配置 Cloudflare R2 / S3 兼容存储（MinIO） {#r2}

```sql
INSERT INTO duckdb.secrets (name, type, key_id, secret, endpoint, scope)
VALUES (
    'r2_warehouse',
    'S3',
    '<R2_ACCESS_KEY_ID>',
    '<R2_SECRET_ACCESS_KEY>',
    '<ACCOUNT_ID>.r2.cloudflarestorage.com',
    's3://my-r2-bucket'
);
```

## 2. 配置表的对象存储后端（`table_config` 与 `mooncake.default_bucket`） {#default-bucket}

在 `pg_mooncake v0.3.0` 中，你可以通过 [`mooncake.create_table`](/zh/docs/reference/create-columnstore/#table-config) 的第四个参数 `table_config` 直接为表指定 S3 / R2 / GCS 存储后端（或参考上游 `v0.1`/`v0.2` 文档中的 `mooncake.default_bucket` 设置）：

```sql
-- 方式 A（v0.2 / v0.3 Moonlink 表级 storage_config 配置）：
CALL mooncake.create_table(
    dst => 'orders_analytics',
    src => 'orders',
    src_uri => NULL,
    table_config => '{
        "iceberg": {
            "storage_config": {
                "s3": {
                    "region": "us-east-1",
                    "bucket": "my-mooncake-bucket",
                    "access_key_id": "<AWS_ACCESS_KEY_ID>",
                    "secret_access_key": "<AWS_SECRET_ACCESS_KEY>",
                    "endpoint": "https://s3.us-east-1.amazonaws.com"
                }
            }
        }
    }'::json
);

-- 方式 B（默认使用本地文件系统仓库 $PGDATA/pg_mooncake）：
CALL mooncake.create_table('orders_analytics', 'orders');
```

## 3. 物化生成 Apache Iceberg v2 快照 {#create-snapshot}

在 PostgreSQL 数据库内部查询 `orders_analytics` 时，会自动融合扫描已刷盘的 Parquet 文件与 Moonlink 内存中的 Arrow 写缓冲区；但外部 Iceberg 计算引擎只能看到已刷盘写入 Iceberg 元数据快照的数据。

如需强制将当前 PostgreSQL WAL LSN 之前所有已提交的数据刷盘，并生成新的 `v*.metadata.json` 快照文件，请调用：

```sql
CALL mooncake.create_snapshot('orders_analytics');
```

> [!NOTE] `v0.3.0`（`moonlink v0.0.1`）非阻塞快照修复
> 在 `pg_mooncake 0.3.0` 中，即使自上一次对 `orders` 表写入之后，数据库因**其他无关表**的写入推进了全局 WAL LSN，调用 `CALL mooncake.create_snapshot('orders_analytics')` 也能立即完成刷盘并返回，不会发生阻塞挂起。

## 4. 查看 Iceberg 仓库路径并从外部引擎查询 {#external-query}

使用 `mooncake.list_tables()` 查看当前的提交 LSN、刷盘 LSN 以及准确的 `iceberg_warehouse_location` 路径：

```sql
SELECT * FROM mooncake.list_tables();
```

示例输出：

```text
          table          | commit_lsn | flush_lsn  |              iceberg_warehouse_location
-------------------------+------------+------------+-------------------------------------------------------
 public.orders_analytics | 0/1A4F890  | 0/1A4F890  | s3://my-mooncake-bucket/warehouse/postgres/public/orders_analytics
```

### 使用外部 DuckDB / PyIceberg / Spark 直接读取 {#duckdb-iceberg}

在 `iceberg_warehouse_location` 目录下，Moonlink 会维护标准的 Apache Iceberg v2 元数据（`metadata/v1.metadata.json`、`v2.metadata.json` 等）：

```sql
-- 在任意外部 DuckDB 实例中直接查询：
INSTALL iceberg;
LOAD iceberg;

SELECT *
FROM iceberg_scan('s3://my-mooncake-bucket/warehouse/postgres/public/orders_analytics/metadata/v2.metadata.json');
```

## 5. 合并文件与清理删除向量（`mooncake.optimize_table`） {#optimize}

如需将多个小 Parquet 文件合并为大文件，并将 Roaring Bitmap 删除向量重写合并至基础数据文件中，可调用：

```sql
-- 对列存镜像表执行全量合并优化
CALL mooncake.optimize_table('orders_analytics', 'full');
```
