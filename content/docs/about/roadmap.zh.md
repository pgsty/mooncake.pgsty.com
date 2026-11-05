---
title: "路线图"
linkTitle: "路线图"
description: "Mooncake Labs v0.2 历史特性路线图与当前 PGSTY 分支的工程维护重点。"
weight: 10
icon: "fa-solid fa-road"
upstream_source: "docs"
upstream_link: "https://web.archive.org/web/20251207085834/https://docs.mooncake.dev/pg/roadmap"
aliases:
  - /zh/pg/roadmap/
  - /zh/roadmap/
---

> [!NOTE]
> 下方路线图保留了上游 `docs.mooncake.dev/pg/roadmap` 发布的 `pg_mooncake v0.2` 历史设计规划，并补充了当前 `pgsty/pg_mooncake`（`v0.3.0`）分支的长期工程维护重点。

---

## PGSTY 维护重点（`v0.3.0+`）

[**PGSTY**](https://github.com/pgsty) 维护的 Mooncake 套件（`pg_mooncake v0.3.0`、`duckdb_mooncake v0.0.2`、`moonlink v0.0.1`）专注于生产环境长期可用性、PostgreSQL 大版本覆盖与依赖安全加固：

1. **PostgreSQL 14–18 全版本支持**：保持 `pg_mooncake` 与最新 `pgrx`（`0.19.3`）同步，覆盖 Linux（`x86_64` 与 `aarch64`、RHEL/Rocky EL8–EL10、Debian 12/13、Ubuntu 22.04/24.04）上的 PostgreSQL 14、15、16、17 与 18。
2. **DuckDB `2.0.0` 与 `pg_duckdb 1.2.0` 同步演进**：随着 DuckDB 的 `TableCatalogEntry`、`TableFilterSet` 与 `StorageExtension` C++ 接口演进，持续维护 `pg_mooncake`、`pg_duckdb` 与 `duckdb_mooncake` 之间的 ABI 兼容性。
3. **正确性与快速失败（Fail-Fast）保护**：强制执行 `pg_duckdb` 运行时版本校验、列存表 LSN 一致性快照读取、分区表层级自动设置 `REPLICA IDENTITY FULL`，以及对已弃用辅助函数显式抛出 `0A000` 错误。
4. **依赖项安全治理**：定期对照 RustSec 漏洞库审计并升级全部三个锁文件（`pg_mooncake`、`moonlink`、`duckdb_mooncake/moonlink_ffi`）中的 Rust 依赖项。

---

## 上游历史路线图（`v0.2`）

以下四项特性是 Mooncake Labs 针对 `v0.2` 架构规划的演进方向：

### 1. 面向日志与事件流的列存表（Columnstore Table for Logs / Events）

为 `columnstore` 表引入**仅追加（append-only）**模式：

- 针对流式写入与乱序插入进行专门优化；
- 内置基于时间的分区与数据保留（Retention）策略；
- 面向可观测性、遥测指标与高吞吐事件管道场景。

### 2. 无需底层行存表的原生列存表（Native Columnstore Tables）

直接创建并写入 `columnstore` 表，而无需依赖配套的 PostgreSQL 行存堆表：

```sql
CREATE TABLE table_name (
    ...
) USING columnstore;
```

- 直接对 `columnstore` 表访问方法执行标准 `INSERT`、`SELECT`、`UPDATE`、`DELETE` 与 `COPY`；
- 注：原生 `USING columnstore` 表在 [`v0.1`（Delta Lake 架构）](/zh/docs/v0.1/columnstore-ddl/)中可用，而 `v0.2` 与 `v0.3.0` 采用 [`mooncake.create_table(dst, src)`](/zh/docs/reference/create-columnstore/) 通过逻辑复制镜像 PostgreSQL 行存表。

### 3. 写入现有 Iceberg 表（Write to Existing Iceberg Tables）

在 PostgreSQL 中创建能够直接写入外部现有 Apache Iceberg 表（由 REST 或 JDBC Catalog 管理）的 `columnstore` 镜像表，实现与 Spark、Trino、Flink 写入端的双向互通。

### 4. 查询路由与分区表透明整合（Query Routing & Partitioned Tables）

在行存 + 列存混合分区表层级上透明路由分析查询，无需手写 `UNION ALL` 或显式引用双表名称。
