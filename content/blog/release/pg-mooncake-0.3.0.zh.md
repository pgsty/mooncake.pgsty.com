---
title: "pg_mooncake 0.3.0 发布：PGSTY 首版发布，全面适配 DuckDB 2.0、pgrx 0.19.3 与 PostgreSQL 14–18"
date: 2026-11-05
description: "pg_mooncake 0.3.0（偕同 duckdb_mooncake v0.0.2 与 moonlink v0.0.1）是 PGSTY 维护的首个正式版本，带来 DuckDB 2.0 / pg_duckdb 1.2.0 适配、跨 PostgreSQL 14–18 的 pgrx 0.19.3 支持、列存表 LSN 一致性快照读取以及完整的 RustSec 依赖安全加固。"
author: "[冯若航](https://vonng.com/) · [PGSTY](https://pgsty.com)"
authors:
  - "vonng"
images:
  - "/blog/covers/pg-mooncake-0.3.0.svg"
tags:
  - "release"
  - "pg_mooncake"
  - "duckdb_mooncake"
  - "moonlink"
  - "iceberg"
upstream_source: ""
upstream_link: ""
---

**`pg_mooncake 0.3.0`**（随同 **`duckdb_mooncake v0.0.2`** 与 **`moonlink v0.0.1`** 同步发布）是由 [**PGSTY**](https://github.com/pgsty) 维护的 Mooncake 实时分析套件的首个正式版本：

- **[`pgsty/pg_mooncake v0.3.0`](https://github.com/pgsty/pg_mooncake/releases/tag/v0.3.0)**（`MIT` 许可证）
- **[`pgsty/duckdb_mooncake v0.0.2`](https://github.com/pgsty/duckdb_mooncake/releases/tag/v0.0.2)**（`MIT` 许可证）
- **[`pgsty/moonlink v0.0.1`](https://github.com/pgsty/moonlink/releases/tag/v0.0.1)**（附带 `PG_MOONCAKE LINKING & DISTRIBUTION EXCEPTION` 的 `BSL-1.1` 许可证，客户端 crate 为 `MIT`）

面向 **PostgreSQL 14、15、16、17、18**，覆盖 **RHEL / Rocky / AlmaLinux 8、9、10** 与 **Debian 12/13、Ubuntu 22.04/24.04**（`x86_64` 与 `aarch64`）的 RPM 与 DEB 二进制软件包现已通过 [PGEXT 软件源](/zh/download/)与 [Pigsty](https://pigsty.io/ext/e/pg_mooncake) 正式提供。

---

## `pg_mooncake 0.3.0` 核心亮点

### 1. 升级至 `pgrx 0.19.3`，全面支持 PostgreSQL 14–18

`pg_mooncake` 已完成向 **`pgrx = 0.19.3`**（`cargo-pgrx 0.19.3`）的迁移，在支持 PostgreSQL 14、15、16、17 的基础上正式引入对 **PostgreSQL 18** 的原生支持：

- 更新 `pg_mooncake.control` 中的扩展元数据（`default_version = '0.3.0'`），并新增升级脚本 `sql/pg_mooncake--0.2.0--0.3.0.sql`。
- 将所有 GUC 参数定义（`mooncake.timeline_id`、`mooncake.enable_local_bucket`、`mooncake.default_bucket`、`mooncake.enable_memory_metadata`）全面迁移至 Rust 原生 `CStr` 字面量（`c"..."`）。

### 2. 适配 DuckDB `2.0.0` 与 `pg_duckdb 1.2.0`

`pg_mooncake 0.3.0` 内嵌 **`pg_duckdb v1.2.0`** 与 **`duckdb_mooncake v0.0.2`**，基于 **DuckDB `v2.0.0`**（`d54cbbe3df17e8e5ce68312f483b4155836112aa`）构建：

- 将 `duckdb_mooncake` 完整迁移至 DuckDB 2.0 的 `TableCatalogEntry`、`StorageExtensionInfo` 与 `TableFilterSet` 迭代器接口。
- 修复了 `MooncakeScanFunction` 中针对 `IS NULL` 与 `IS NOT NULL` 谓词下推的列索引重映射缺陷，消除了多列混合过滤条件下推至 Moonlink Parquet 扫描时的段错误（SIGSEGV）。
- 在后台工作进程初始化阶段新增 **`pg_duckdb` 运行时版本校验**，强制要求 `pg_duckdb = 1.2.0`（支持 `1.2.0` 或 `1.2.0-*` 预发布后缀；当检测到 `1.1.3` 或 `1.3.0` 等不匹配版本时立即快速失败并给出明确提示）。

### 3. 列存表 LSN 一致性快照读取（`pg_current_wal_flush_lsn`）

在旧版本中，`duckdb_mooncake` 以 `lsn = 0` 构造 Moonlink 表扫描描述符，导致查询不会等待刚刚提交的 PostgreSQL 事务被后台逻辑复制工作进程消费完毕。

在 `v0.3.0` 中，`pg_mooncake` 导出了 C 符号 `mooncake_get_postgres_lsn()`（在常规后端会话中调用 `pg_current_wal_flush_lsn()`，在恢复模式下返回 `0`），由 `duckdb_mooncake` 通过 `dlsym(RTLD_DEFAULT, "mooncake_get_postgres_lsn")` 动态解析。现在，对 `columnstore` 表的每一次分析查询都会自动等待 Moonlink 同步至当前 PostgreSQL WAL 刷盘 LSN 后再执行扫描。

### 4. 分区表层级自动支持（`REPLICA IDENTITY FULL`）

在对 PostgreSQL 分区表调用 [`mooncake.create_table(dst, src)`](/zh/docs/reference/create-columnstore/) 时，`pg_mooncake 0.3.0` 会自动遍历继承树（`find_all_inheritors`），在将主表加入逻辑复制发布之前，自动为父表及所有叶子分区表设置 `REPLICA IDENTITY FULL`。

### 5. 对已弃用的 `mooncake.load_files` 显式返回 `0A000` 错误

旧版 `v0.1` 遗留的辅助函数 `mooncake.load_files(dst TEXT, files TEXT[])` 现在会显式抛出标准 PostgreSQL 错误码 `ERRCODE_FEATURE_NOT_SUPPORTED`（`0A000`）并给出清晰的迁移提示，而不再触发未捕获的 Rust `todo!()` 崩溃。

### 6. Cargo 依赖安全审计与加固（RustSec）

全部三个 Cargo 工作区（`pg_mooncake`、`moonlink`、`duckdb_mooncake/moonlink_ffi`）均对照 RustSec 漏洞数据库（`2026-11-05`）完成了系统性安全升级：

- **`pg_mooncake/Cargo.lock`**：已知漏洞从 **33 个降至 6 个（-82%）**，unsound 警告清零（`1 -> 0`）。
- **`moonlink/Cargo.lock`**：已知漏洞从 **46 个降至 15 个（-67%）**，unsound 警告清零（`1 -> 0`）。
- **`duckdb_mooncake/moonlink_ffi/Cargo.lock`**：**0 个漏洞、0 个 unsound、0 条警告**。
- 升级了 `tonic 0.14.5`、`prost 0.14.3`、`bincode 2.1.0`、`opentelemetry 0.31.0`、`wasmtime 43.0.1`、`rustls 0.23.37`、`aws-lc-rs 1.16.3`、`bytes 1.11.1`、`tar 0.4.45` 与 `lz4_flex 0.11.6`。完整审计详情请参阅 [SBOM 与安全审计](/zh/docs/about/sbom/)。

---

## 验证总结

`pg_mooncake 0.3.0` 已在 **Ubuntu 24.04.5 LTS ARM64（`PostgreSQL 18.6`）** 与 **Rocky Linux 10.2 ARM64（`PostgreSQL 17.11`）** 双平台上完成端到端实机验证：

- **58/58** 项 Moonlink `table_handler` 单元测试全部通过。
- **3/3** 组 `pg_Regression` SQL 回归测试集（`small`、`partition`、`unsupported`）全部通过（`0` 失败）。
- **运行时版本门禁**实测验证：准确拦截 `pg_duckdb 1.1.3` 与 `1.3.0`，放行 `1.2.0`。
- **11/11** 项实时逻辑复制、`UPDATE`/`DELETE`、分区表同步、Iceberg 元数据访问及数据库快速重启持久化检查点全部通过。
