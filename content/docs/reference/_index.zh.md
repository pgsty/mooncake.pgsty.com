---
title: "SQL 接口、视图与配置参数参考手册"
linkTitle: "参考手册"
description: "pg_mooncake (v0.3.0) 完整 SQL 存储过程、元数据函数与 GUC 配置参数参考手册，涵盖 mooncake.create_table、create_snapshot、optimize_table、list_tables 与 DuckDB 参数。"
weight: 30
icon: fa-solid fa-code
upstream_link: https://web.archive.org/web/20251207105147/https://docs.mooncake.dev/pg/reference/
aliases:
  - "/zh/pg/reference/"
  - "/zh/reference/"
---

本节提供 **`pg_mooncake`（`v0.3.0`）** 暴露的全部 SQL 存储过程、表状态查询函数、表访问方法（TAM）以及 PostgreSQL GUC 配置参数的完整参考。

## SQL 存储过程与函数（`mooncake` Schema） {#sql-api}

| 对象名称 | 完整函数签名 | 功能说明 |
|:---|:---|:---|
| **`mooncake.create_table`** | `CALL mooncake.create_table(dst text, src text, src_uri text DEFAULT NULL, table_config json DEFAULT NULL)` | 创建只读的 `USING mooncake` 列存镜像表（`dst`），从当前本地数据库或远程 PostgreSQL URI（`src_uri`）中的源表（`src`）实时复制数据。 |
| **`mooncake.create_snapshot`** | `CALL mooncake.create_snapshot(dst text)` | 等待 Moonlink 追平当前 PostgreSQL WAL 写入 LSN，将内存 Arrow 写缓冲区刷盘为 Parquet，并写入新的 Apache Iceberg v2 元数据快照。 |
| **`mooncake.optimize_table`** | `CALL mooncake.optimize_table(dst text, mode text)` | 对目标列存镜像表 `dst` 执行文件合并（Compaction）与删除向量清理（`mode` 支持 `'full'` 或 `'minor'`）。 |
| **`mooncake.list_tables`** | `SELECT * FROM mooncake.list_tables()` | 表值函数，返回当前数据库中所有活跃 Moonlink 表的 `(table text, commit_lsn pg_lsn, flush_lsn pg_lsn, iceberg_warehouse_location text)`。 |
| **`mooncake.load_files`** | `CALL mooncake.load_files(dst text, files text[])` | 在 `v0.3.0` 中未实现；调用时会显式抛出 `SQLSTATE 0A000`（`FEATURE_NOT_SUPPORTED`），避免旧版静默空操作造成的误导。 |
{.wide .expand}

### `mooncake.list_tables()` 返回列说明 {#list-tables}

```sql
SELECT * FROM mooncake.list_tables();
```

| 列名 | 数据类型 | 说明 |
|:---|:---:|:---|
| `table` | `text` | 列存镜像表的带 Schema 完整名称（例如 `public.orders_analytics`）。 |
| `commit_lsn` | `pg_lsn` | 已摄取进入 Moonlink 内存 Arrow 写缓冲区的最新 PostgreSQL WAL LSN。 |
| `flush_lsn` | `pg_lsn` | 已持久化刷盘至 Parquet / Iceberg 快照存储的最新 PostgreSQL WAL LSN。 |
| `iceberg_warehouse_location` | `text` | 存放该表 Apache Iceberg v2 元数据与 Parquet 数据文件的本地目录（`$PGDATA/pg_mooncake/...`）或云端路径（`s3://...`）。 |
{.wide .expand}

## 表访问方法与事件触发器 {#tam}

- **表访问方法（`USING mooncake`）**：由 `mooncake.create_table` 自动创建，并在扩展加载时通过 `RegisterDuckdbTableAm("mooncake")` 注册至 `pg_duckdb 1.2.0`。
- **删表清理触发器（`mooncake_drop_trigger`）**：当对列存镜像表执行 `DROP TABLE <dst>;` 时，`ON sql_drop` 事件触发器（`mooncake_drop_trigger_func`）会自动从 Moonlink 注销该表并清理对应的逻辑复制订阅。

## GUC 配置参数参考 {#guc}

| 参数名称 | 类型 | 默认值 | 上下文 | 参数说明 |
|:---|:---:|:---:|:---:|:---|
| `mooncake.default_bucket` | `string` | `''`（本地 `$PGDATA/pg_mooncake`） | `USERSET` / `SUSET` | 新创建的 Mooncake 表写入 Parquet 数据文件与 Apache Iceberg v2 元数据的默认对象存储桶路径（例如 `'s3://my-bucket/warehouse'`）。 |
| `mooncake.extension_repository` | `string` | `$(pg_config --sharedir)/extension/pg_mooncake` | `SUSET` | 存放随包安装的 `v2.0.0/<platform>/mooncake.duckdb_extension` 二进制文件的本地扩展仓库目录。 |
| `mooncake.enable_local_cache` | `bool` | `true` | `SUSET` | 写入云端对象存储时是否启用本地磁盘缓存。 |
| `duckdb.allow_community_extensions` | `bool` | `false`（必须设为 `true`） | `SUSET` | `pg_duckdb` 要求开启此项以允许 `pg_mooncake` 加载 `mooncake` 存储扩展。 |
| `duckdb.allow_unsigned_extensions` | `bool` | `false`（必须设为 `true`） | `SUSET` | 允许 `pg_duckdb` 从本地 `mooncake.extension_repository` 加载编译生成的 `mooncake.duckdb_extension`。 |
| `duckdb.max_memory` | `string` | `4GB`（或可用内存 80%） | `SUSET` | 分配给内嵌 DuckDB 2.0 向量化执行引擎的最大内存上限。 |
| `duckdb.threads` | `int` | `-1`（全部 CPU 核心） | `SUSET` | DuckDB 2.0 用于并行向量化查询执行的工作线程数。 |
{.wide .expand}

## 专题参考指南 {#guides}

{{< cards >}}
{{< card title="创建列存镜像表" icon="fa-solid fa-table-columns" link="/zh/docs/reference/create-columnstore/" >}}
详解本地与远程（`src_uri`）复制、初始快照拷贝选项、分区表支持以及 `table_config` JSON 参数。
{{< /card >}}
{{< card title="查询列存表与查询形态" icon="fa-solid fa-magnifying-glass-chart" link="/zh/docs/reference/query-columnstore/" >}}
支持的分析型 SQL 查询形态、聚合与过滤、行存混合关联，以及在 PostgreSQL 中暴露 DuckDB 原生函数。
{{< /card >}}
{{< card title="Iceberg 与对象存储配置" icon="fa-solid fa-cloud" link="/zh/docs/reference/iceberg/" >}}
配置 AWS S3 与 Cloudflare R2 密钥、生成 Iceberg v2 快照，并从外部计算引擎直接读取 Mooncake 表。
{{< /card >}}
{{< card title="在 Postgres 中查询外部数据湖" icon="fa-solid fa-folder-open" link="/zh/docs/reference/query-data-lake/" >}}
在 PostgreSQL 内直接扫描外部 Parquet、CSV、JSON、Iceberg、Delta Lake 及 HuggingFace 数据集。
{{< /card >}}
{{< /cards >}}
