---
title: "将 pg_mooncake 与 duckdb_mooncake 迁移至 DuckDB 2.0、pg_duckdb 1.2.0 与 pgrx 0.19.3"
date: 2026-11-05
description: "深度解析 duckdb_mooncake v0.0.2 与 pg_mooncake v0.3.0 适配 DuckDB 2.0 C++ 目录与过滤器接口、通过 dlsym 打通 LSN 一致性快照读取，以及修复 NULL 谓词下推列索引映射的工程实践。"
author: "[冯若航](https://vonng.com/) · [PGSTY](https://pgsty.com)"
authors:
  - "vonng"
images:
  - "/blog/covers/duckdb-2-adaptation.svg"
tags:
  - "engineering"
  - "duckdb"
  - "pg_mooncake"
  - "duckdb_mooncake"
  - "pgrx"
upstream_source: ""
upstream_link: ""
---

当 Mooncake Labs 在发布 `v0.2.0` 后暂停对 [`pg_mooncake`](https://github.com/Mooncake-Labs/pg_mooncake) 的公开更新时，该扩展停留在早期的 DuckDB `1.3.x` / `pg_duckdb` 快照与 `pgrx 0.12` 上。与此同时，PostgreSQL 社区已经演进至 **PostgreSQL 18**、**`pgrx 0.19.3`** 以及基于 **DuckDB `v2.0.0`** 的 **`pg_duckdb 1.2.0`**。

本文将深入介绍我们将整个 Mooncake 技术栈——**`pg_mooncake v0.3.0`**、**`duckdb_mooncake v0.0.2`** 与 **`moonlink v0.0.1`**——全面迁移至 **DuckDB `2.0.0`**、**`pg_duckdb 1.2.0`** 与 **`pgrx 0.19.3`** 的工程改造过程。

---

## 架构回顾：三大代码仓库如何协同工作

理解这三个仓库在编译期与运行时的边界，有助于看清为什么升级 DuckDB 会同时涉及跨多个 crate 的 C++ 与 Rust 代码改造：

```
┌──────────────────────────────────────────────────────────────────────┐
│                         PostgreSQL 进程空间                          │
│                                                                      │
│  ┌─────────────────────────┐          ┌───────────────────────────┐  │
│  │    pg_mooncake.so       │          │      pg_duckdb.so         │  │
│  │  (Rust / pgrx 0.19.3)   │          │  (C++ / DuckDB v2.0.0)    │  │
│  │                         │          │                           │  │
│  │  • mooncake_worker      │          │  • DuckDB 优化器与执行器  │  │
│  │    (逻辑复制消费端 +    │          │  • 加载                   │  │
│  │     内嵌 moonlink 引擎) │◄────────►│    duckdb_mooncake        │  │
│  │  • 导出                 │  dlsym   │    存储扩展               │  │
│  │    mooncake_get_        │  + IPC   │  • 扫描 Iceberg Parquet   │  │
│  │    postgres_lsn()       │  套接字  │    + Moonlink Puffin 缓冲 │  │
│  └─────────────────────────┘          └───────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────┘
```

1. **`pg_mooncake`** 是基于 `pgrx` 的 Rust 扩展，负责提供 `mooncake.create_table(dst, src)` 接口、拉起 `mooncake_worker` 后台进程、将逻辑复制变更流式写入内嵌的 **`moonlink`** 引擎，并将 **`duckdb_mooncake`** 编译进同一个动态库中。
2. **`pg_duckdb`** 在 PostgreSQL 进程内嵌了 `libduckdb`（`v2.0.0`），负责拦截并接管涉及 `columnstore` 表的分析查询。
3. **`duckdb_mooncake`** 注册了名为 `mooncake` 的 DuckDB `StorageExtension`（存储扩展），通过 Moonlink 的 UNIX 域套接字（`mooncake.sock`）解析列存表元数据，等待目标 PostgreSQL WAL LSN 同步完成，并将底层文件扫描委托给 DuckDB 的并行 `parquet_scan` 读取器以及内存态 Puffin 删除向量读取器。

---

## 1. 将 `duckdb_mooncake` 适配至 DuckDB `2.0.0` C++ 接口

DuckDB `2.0.0`（`d54cbbe3df17e8e5ce68312f483b4155836112aa`）在目录管理（Catalog）、存储扩展（StorageExtension）以及谓词下推（TableFilterSet）层引入了多项不兼容的 C++ API 变更：

### `StorageExtension` 注册方式（`StorageExtension::Register`）

在 DuckDB 1.x 中，扩展直接修改 `config.storage_extensions["mooncake"]` 字典；而在 DuckDB 2.0 中，存储扩展统一通过 `StorageExtension::Register(config, "mooncake", make_shared_ptr<MooncakeStorageExtension>())` 注册，且 `StorageExtensionInfo` 结构体的虚表与回调签名也随之更新。

### `TableCatalogEntry::GetColumns()` 与 `GetTypes()`

`MooncakeTableEntry` 继承自 `TableCatalogEntry`。我们将其构造函数与列投影辅助方法对齐至 DuckDB 2.0 的 `ColumnList` 与 `LogicalType` 接口，同时保留了供 Moonlink 删除向量使用的虚拟伪列 `__row_id`（`UBIGINT`）。

### `TableFilterSet` 迭代器重构与 `IS NULL` 谓词下推修复

在 DuckDB 1.x 中，`TableFilterSet` 直接暴露了 `std::unordered_map<idx_t, unique_ptr<TableFilter>> filters` 成员变量；而在 DuckDB 2.0 中，`TableFilterSet` 封装了内部映射，改为提供返回 `(FilterIndex, const TableFilter &)` 的迭代器接口。

在将 `MooncakeScanFunction::mooncake_scan_bind` 迁移至新迭代器接口的过程中，我们定位并修复了一个隐藏在 `IS NULL` / `IS NOT NULL` 谓词下推中的列索引重映射缺陷：

- 当查询只投影部分列（例如 `SELECT b FROM t_col WHERE a IS NOT NULL AND b > 10`）时，`CONJUNCTION_AND` 与比较谓词都会将列索引从**扫描投影下标**重映射为**底层 Parquet 物理表列下标**（`column_ids[filter_col_idx]`），但原先的 `IS_NULL` 与 `IS_NOT_NULL` 分支却直接将未映射的投影下标传给了底层 Parquet 过滤器集合。
- 在 DuckDB 2.0 下，当执行 `SELECT count(*) FROM (SELECT DISTINCT c, a, b FROM t WHERE c IS NULL AND b > 2)` 时，错位的列索引会导致 `parquet_scan` 触发段错误（`SIGSEGV`）。
- 通过 `column_ids` 统一重映射 `IS_NULL` 与 `IS_NOT_NULL` 的列索引后，该崩溃问题彻底消除。

---

## 2. 跨 `pg_mooncake` 与 `duckdb_mooncake` 打通 LSN 一致性快照读取

由于 `pg_mooncake` 通过 PostgreSQL 逻辑复制异步消费行存表写入，紧跟在 `INSERT` 或 `COMMIT` 之后执行的 `SELECT` 必须等待 `moonlink` 消费完当前已刷盘的 WAL 位置，才能保证“读己之所写（Read-Your-Own-Writes）”。

在 `v0.3.0` 中，我们打通了跨动态库的 LSN 桥接机制：

1. 在 `pg_mooncake`（`src/lib.rs`）中导出 C 符号：
   ```rust
   #[no_mangle]
   pub extern "C-unwind" fn mooncake_get_postgres_lsn() -> u64 {
       unsafe {
           if pg_sys::RecoveryInProgress() {
               0
           } else {
               pg_sys::GetXLogFlushRecPtr()
           }
       }
   }
   ```
2. 在 `duckdb_mooncake` 中，存储扩展在运行时通过 `dlsym(RTLD_DEFAULT, "mooncake_get_postgres_lsn")` 解析该符号（若 `duckdb_mooncake` 运行在 PostgreSQL 进程之外的独立 DuckDB CLI 中，则自动回退至 `0`）。
3. 当绑定 `columnstore` 表扫描时，`duckdb_mooncake` 将获取到的 LSN 传入 `moonlink_scan_table_begin(...)`，由 Moonlink 阻塞等待直至逻辑复制消费进度追上目标 LSN。

---

## 3. 分区表层级自动设置 `REPLICA IDENTITY FULL`

PostgreSQL 逻辑复制要求无主键表（或需要获取更新/删除前完整旧元组的表）启用 `REPLICA IDENTITY FULL`。当用户对分区表执行 `CALL mooncake.create_table('sales_col', 'sales')` 时，仅在父分区表上设置 `REPLICA IDENTITY FULL` 并不会自动向下传播到已有的叶子分区。

`pg_mooncake 0.3.0` 在 `mooncake.create_table` 中调用 `pg_sys::find_all_inheritors(relid, pg_sys::AccessExclusiveLock as i32, std::ptr::null_mut())`，在单次原子操作中为父表及所有现有子分区统一设置 `REPLICA IDENTITY FULL`。

---

## 4. 端到端实机验证

完成适配的技术栈已在两套纯净的 Linux ARM64 环境中通过完整验证：

1. **Ubuntu 24.04.5 LTS ARM64（`mooncake-u24a-pg18`，PostgreSQL `18.6`）**
2. **Rocky Linux 10.2 ARM64（`mooncake-el10a-pg17`，PostgreSQL `17.11`）**

全部 58 项 Moonlink `table_handler` 单元测试、3 组 SQL 回归测试集（`small`、`partition`、`unsupported`）、`pg_duckdb 1.2.0` 运行时版本校验门禁以及 13 项数据库重启持久化与 Iceberg 元数据检查点均零失败通过。
