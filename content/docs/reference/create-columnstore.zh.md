---
title: "创建列存镜像表"
linkTitle: "创建列存表"
description: "使用 CALL mooncake.create_table 从本地或远程 PostgreSQL 表创建实时同步的 USING mooncake 列存镜像表。"
weight: 10
icon: fa-solid fa-table-columns
upstream_link: https://web.archive.org/web/20260124121942/https://docs.mooncake.dev/pg/reference/create-columnstore
aliases:
  - "/zh/pg/reference/create-columnstore/"
  - "/zh/reference/create-columnstore/"
---

在 `pg_mooncake` 中，列存表通过 `mooncake.create_table` 存储过程创建，作为现有 PostgreSQL 行存表（普通堆表或分区表）的**实时同步镜像（Columnstore Mirror）**运行。

## 存储过程签名 {#signature}

```sql
CALL mooncake.create_table(
    dst text,
    src text,
    src_uri text DEFAULT NULL,
    table_config json DEFAULT NULL
);
```

| 参数名称 | 类型 | 默认值 | 参数说明 |
|:---|:---:|:---:|:---|
| `dst` | `text` | *（必填）* | 要创建的目标列存镜像表名称（支持 `schema.table` 格式，未指定 Schema 时默认为 `public`）。 |
| `src` | `text` | *（必填）* | 作为复制源的 PostgreSQL 行存表或分区父表名称（支持 `schema.table` 格式）。 |
| `src_uri` | `text` | `NULL` | 当从外部远程 PostgreSQL 实例复制时，指定远程连接串（`postgresql://user:pass@host:port/dbname`）。为 `NULL` 时默认从当前本地数据库复制。 |
| `table_config` | `json` | `NULL` | 可选的 JSON 配置对象，用于定制 Moonlink 表级摄取与存储参数（例如 `write_buffer_size`）。 |
{.wide .expand}

> [!IMPORTANT] 参数名勘误说明：请使用 `src_uri`（而非 `source_uri`）
> 上游早期 v0.2 文档中存在一处笔误，将远程连接参数写成了 `source_uri => 'postgresql://...'`。在 `pg_mooncake` 的真实 SQL 定义（`src/functions.rs`）中，该参数的准确名称为 **`src_uri`**。使用命名参数调用时请务必传入 `src_uri => 'postgresql://...'`。

## 1. 为当前数据库中的本地表创建镜像 {#local}

省略 `src_uri`（或传 `NULL`）时，`pg_mooncake` 直接镜像当前数据库内的 `src` 表：

```sql
-- 创建源 OLTP 业务行存表
CREATE TABLE orders (
    order_id BIGSERIAL PRIMARY KEY,
    customer_id INT NOT NULL,
    amount NUMERIC(12, 2) NOT NULL,
    status TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 创建实时列存镜像表
CALL mooncake.create_table('orders_analytics', 'orders');
```

执行 `CALL mooncake.create_table('orders_analytics', 'orders')` 时后台完成的步骤：

1. `pg_mooncake` 读取 `orders` 的列结构，并创建 `CREATE TABLE orders_analytics (...) USING mooncake`。
2. 如果 `orders` 没有主键，`pg_mooncake` 会自动执行 `ALTER TABLE orders REPLICA IDENTITY FULL`（在 `v0.3.0` 中，若 `orders` 是分区表，还会自动为所有现有叶子子分区设置 `REPLICA IDENTITY FULL`）。
3. `moonlink` 建立逻辑复制槽（`pgoutput`），完成 `orders` 存量行的初始快照拷贝，并开始实时流式同步后续的 `INSERT`、`UPDATE` 与 `DELETE` 变更。

## 2. 从远程 PostgreSQL 实例镜像表（`src_uri`） {#remote}

你可以在独立的分析型 PostgreSQL 节点上部署 `pg_mooncake`，并通过 `src_uri` 实时镜像远程生产 PostgreSQL 数据库（包括自建实例、AWS RDS、Aurora、Supabase 或 Neon）中的业务表：

```sql
CALL mooncake.create_table(
    dst => 'orders_analytics',
    src => 'public.orders',
    src_uri => 'postgresql://replicator:secret@prod-db.example.com:5432/appdb'
);
```

远程源数据库需满足以下条件：
- 已开启逻辑复制：`wal_level = logical`。
- `src_uri` 中的数据库用户具备 `REPLICATION` 权限以及源表 `src` 的 `SELECT` 权限。
- 若源表没有主键，需在源表上设置 `REPLICA IDENTITY FULL`。

## 3. 为分区表创建列存镜像 {#partitioned}

`mooncake.create_table` 原生支持 PostgreSQL 声明式分区表（`PARTITION BY RANGE`、`LIST` 或 `HASH`）。调用时只需将**分区父表**名称作为 `src` 传入：

```sql
CREATE TABLE events (
    id BIGINT,
    event_type TEXT,
    payload JSONB,
    created_at TIMESTAMPTZ
) PARTITION BY RANGE (created_at);

CREATE TABLE events_2026_10 PARTITION OF events
    FOR VALUES FROM ('2026-10-01') TO ('2026-11-01');

CREATE TABLE events_2026_11 PARTITION OF events
    FOR VALUES FROM ('2026-11-01') TO ('2026-12-01');

-- 对分区父表创建列存镜像
CALL mooncake.create_table('events_analytics', 'events');
```

> [!WARNING] 在 `create_table` 之后新增子分区的注意事项
> 在 `pg_mooncake 0.3.0` 中，`mooncake.create_table` 会自动为创建镜像时已存在的所有叶子子分区设置 `REPLICA IDENTITY FULL`。如果在创建镜像**之后**又新增了子分区（例如 `CREATE TABLE events_2026_12 PARTITION OF events ...`）且表没有主键，请在对新分区执行 `UPDATE` 或 `DELETE` 前手动执行 `ALTER TABLE events_2026_12 REPLICA IDENTITY FULL;`。

## 4. 高级 `table_config` 参数配置 {#table-config}

你可以通过 `table_config` 传入 JSON 对象来定制单表级 Moonlink 行为（对应 `moonlink_backend/src/table_config.rs` 中的 `TableConfig` 结构），包括纯追加（Append-Only）模式、后台合并开关，以及自定义本地文件系统 / S3 / GCS 存储后端：

```sql
-- 示例 1：纯追加表（跳过构建主键删除哈希索引，适合日志与事件流）
CALL mooncake.create_table(
    dst => 'events_analytics',
    src => 'events',
    src_uri => NULL,
    table_config => '{
        "mooncake": {
            "append_only": true,
            "skip_index_merge": false,
            "skip_data_compaction": false
        }
    }'::json
);

-- 示例 2：为单表指定自定义 S3 Iceberg 仓库存储后端
CALL mooncake.create_table(
    dst => 'orders_analytics',
    src => 'orders',
    src_uri => NULL,
    table_config => '{
        "iceberg": {
            "storage_config": {
                "s3": {
                    "region": "us-east-1",
                    "bucket": "my-mooncake-warehouse",
                    "access_key_id": "<AWS_ACCESS_KEY_ID>",
                    "secret_access_key": "<AWS_SECRET_ACCESS_KEY>"
                }
            }
        }
    }'::json
);
```

| JSON 字段路径 | 类型 | 默认值 | 参数说明 |
|:---|:---:|:---:|:---|
| `mooncake.append_only` | `bool` | `false` | 设为 `true` 时将表视为纯追加模式，跳过维护主键哈希索引以提升写入吞吐。 |
| `mooncake.skip_index_merge` | `bool` | `false` | 设为 `true` 时禁用后台 Puffin 哈希索引 LSM 树合并。 |
| `mooncake.skip_data_compaction` | `bool` | `false` | 设为 `true` 时禁用后台 Parquet 数据文件自动合并（Compaction）。 |
| `iceberg.storage_config` | `object` | `{"fs": {"root_directory": "$PGDATA/pg_mooncake"}}` | Apache Iceberg v2 元数据与 Parquet 数据文件的存储后端（支持 `fs`、`s3` 或 `gcs`）。 |
| `wal.storage_config` | `object` | `{"fs": {"root_directory": "$PGDATA/pg_mooncake"}}` | Moonlink 内部 WAL 日志段的存储后端（支持 `fs`、`s3` 或 `gcs`）。 |
{.wide .expand}

## 5. 删除列存镜像表 {#drop}

如需删除列存镜像表并自动清理其 Moonlink 元数据与逻辑复制槽，直接执行标准的 `DROP TABLE` 即可：

```sql
DROP TABLE orders_analytics;
```
