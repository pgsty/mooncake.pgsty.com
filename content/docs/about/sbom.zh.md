---
title: "SBOM 与安全审计"
linkTitle: "SBOM 与安全审计"
description: "pg_mooncake 0.3.0 的软件物料清单（versions.json）、子模块版本矩阵以及 2026-11-05 Cargo RustSec 依赖安全审计报告。"
weight: 50
icon: "fa-solid fa-boxes-stacked"
---

本页记录了 **`pg_mooncake v0.3.0`**、**`duckdb_mooncake v0.0.2`** 与 **`moonlink v0.0.1`** 的精确子模块版本矩阵（`versions.json`）以及 Cargo 依赖安全审计结果。

---

## 组件与子模块版本矩阵（`versions.json`）

`pgsty/pg_mooncake` 在仓库根目录的 [`versions.json`](https://github.com/pgsty/pg_mooncake/blob/main/versions.json) 中记录了所有子模块与上游依赖的精确提交哈希：

| 组件 | 路径 | 代码仓库 | 标签 / 分支 | Commit SHA | 许可证 |
|:---|:---|:---|:---|:---|:---|
| **`pg_mooncake`** | `/` | [`pgsty/pg_mooncake`](https://github.com/pgsty/pg_mooncake) | `v0.3.0` | `1a9cbfd65be9a6486d020120acb49ef0c6800d68` | `MIT` |
| **`duckdb_mooncake`** | `duckdb_mooncake` | [`pgsty/duckdb_mooncake`](https://github.com/pgsty/duckdb_mooncake) | `v0.0.2` | `49765a369ad88986916ce53c969ed2ce4ba66fac` | `MIT` |
| **`duckdb`**（嵌套子模块） | `duckdb_mooncake/duckdb` | [`duckdb/duckdb`](https://github.com/duckdb/duckdb) | `v2.0.0` | `d54cbbe3df17e8e5ce68312f483b4155836112aa` | `MIT` |
| **`moonlink`** | `moonlink` (`duckdb_mooncake/moonlink`) | [`pgsty/moonlink`](https://github.com/pgsty/moonlink) | `v0.0.1` | `b298ef7444890e3c8af5544e350232518bcfd8e5` | `BSL-1.1` + 豁免（客户端 crate 为 `MIT`） |
| **`pg_duckdb`** | `pg_duckdb` | [`pgsty/pg_duckdb`](https://github.com/pgsty/pg_duckdb) | `v1.2.0` | `8756099e267c47f0b86c24de4cf995327f1f4279` | `MIT` |
| **`rust-postgres`** | `rust-postgres` | [`sfackler/rust-postgres`](https://github.com/sfackler/rust-postgres) | `master` | `14c8e599f5551a8caa96ff5023685a6f537a1455` | `Apache-2.0 OR MIT` |
{.wide .expand}

---

## 核心 Rust 工具链与框架版本

| 依赖项 | 版本 | 职责说明 |
|:---|:---|:---|
| **`pgrx`** / **`cargo-pgrx`** | `0.19.3` | Rust PostgreSQL 扩展开发框架（支持 PostgreSQL 14–18）。 |
| **`iceberg`** | `0.6.0` | `moonlink` 中的 Apache Iceberg 表元数据与 Catalog 客户端。 |
| **`arrow`** / **`parquet`** | `55.2.0` | `moonlink` 中的列式内存格式与 Parquet 文件写入器。 |
| **`datafusion`** | `48.0.1` | `moonlink` 中的表达式求值与谓词裁剪引擎。 |
| **`opendal`** | `0.53.1` | 统一对象存储抽象层（支持 `fs`、`s3`、`gcs`、`azblob`）。 |
| **`tonic`** / **`prost`** | `0.14.5` / `0.14.3` | `pg_mooncake` 与 `moonlink` 之间的 gRPC / IPC 协议序列化。 |
| **`tokio`** | `1.53.0` | 后台数据摄入与对象存储 I/O 的异步运行时。 |

---

## 2026-11-05 Cargo 依赖安全审计报告

我们使用 `cargo-audit 0.22.2` 对照 RustSec 漏洞数据库（commit `965bf9ad083b58e6340d65829d85217b18be9290`，共加载 927 条安全公告）对全部三个 Cargo 工作区进行了审计与修复。

### 修复前后对比汇总

| 锁文件 | 修复前 | 修复后 | 降幅 |
|:---|:---|:---|:---|
| `pg_mooncake/Cargo.lock` | 33 个漏洞、1 个 unsound、19 条警告 | **6 个漏洞、0 个 unsound**、15 条警告 | **漏洞减少 27 个（-82%），unsound 清零** |
| `moonlink/Cargo.lock` | 46 个漏洞、1 个 unsound、28 条警告 | **15 个漏洞、0 个 unsound**、24 条警告 | **漏洞减少 31 个（-67%），unsound 清零** |
| `duckdb_mooncake/moonlink_ffi/Cargo.lock` | 1 个漏洞、0 个 unsound、0 条警告 | **0 个漏洞、0 个 unsound、0 条警告** | **-100%（完全清零）** |
{.wide .expand}

### 已修复的关键安全漏洞

- **直接依赖跨大版本升级**：
  - `tonic 0.12 -> 0.14.5`、`prost 0.13 -> 0.14.3`（消除了 `RUSTSEC-2026-0001` `rkyv` 内存耗尽 DoS 以及 `duckdb_mooncake` 中的 `RUSTSEC-2024-0436` `paste` 停更警告）。
  - `bincode 1.3.3 -> 2.1.0`（启用 `serde` 兼容路径，修复 `RUSTSEC-2025-0141`）。
  - `opentelemetry 0.27 -> 0.31.0`、`opentelemetry-otlp 0.27 -> 0.31.1`、`tracing-opentelemetry 0.28 -> 0.32.1`。
  - `reqwest 0.12.20 -> 0.12.28`；通过升级 `testcontainers 0.23.3 -> 0.27.2` 彻底移除存在 PAX 头解析漏洞（`RUSTSEC-2025-0065`）的 `tokio-tar`。
- **传递依赖安全升级**：
  - `bytes 1.10.1 -> 1.11.1`（`RUSTSEC-2026-0007`：`BytesMut::reserve` 整数溢出）。
  - `quinn-proto 0.11.12 -> 0.11.14`（`RUSTSEC-2026-0037`：Quinn 端点拒绝服务漏洞）。
  - `rustls 0.23.28 -> 0.23.37` 与 `rustls-webpki 0.103.3 -> 0.103.12`（`RUSTSEC-2026-0049`、`RUSTSEC-2026-0098`、`RUSTSEC-2026-0099`：CRL 分发点与通配符名称约束校验修复）。
  - `aws-lc-rs 1.13.1 -> 1.16.3` 与 `aws-lc-sys 0.29.0 -> 0.39.1`（修复 7 项 PKCS7 / AES-CCM / X.509 侧信道与逻辑漏洞）。
  - `lz4_flex 0.11.4 -> 0.11.6`（`RUSTSEC-2026-0041`：内存信息泄露）。
  - `tar 0.4.44 -> 0.4.45`（`RUSTSEC-2026-0067` 与 `RUSTSEC-2026-0068`：PAX 大小头处理与符号链接权限漏洞）。
  - `time 0.3.41 -> 0.3.47`（`RUSTSEC-2026-0009`：RFC 2822 解析栈耗尽 DoS）。
  - `wasmtime 29.0.1 -> 43.0.1`（修复 12 项 WASI/Wasmtime 沙箱漏洞及 `regalloc2` 内存安全问题）。
  - `glib 0.20.12 -> 0.22.4`（消除 `RUSTSEC-2026-0097` `VariantStrIter` unsound 问题）。

### 剩余受上游锁定的传递依赖说明

`pg_mooncake/Cargo.lock` 中剩余的 6 条通告均来自 `iceberg 0.6.0`（锁定了 `arrow 55`、`parquet 55`、`avro-schema 0.3` 与旧版传递依赖）以及 `moonlink` 中的 `deltalake-core 0.26.0`：

1. `rsa 0.9.10`（`RUSTSEC-2023-0071`）：由 `iceberg-catalog-sql -> sqlx-mysql` 传递引入，`moonlink` 运行时仅初始化 PostgreSQL/REST Iceberg Catalog，不触发 MySQL RSA 握手机制。
2. `md5 0.7.0`（`RUSTSEC-2025-0146`，已更名为 `md-5`）：由 `avro-schema 0.3.0` 引入。
3. `snappy 0.4.0`（`RUSTSEC-2026-0046`，超大缓冲区 >4 GiB 时的整数截断）：由 `avro-schema 0.3.0` 引入，而 Iceberg Avro 清单文件通常仅为 KB 到 MB 级别。
4. `rustls-webpki 0.102.8`（`RUSTSEC-2026-0049`、`0098`、`0099`）：由 `iceberg 0.6` 传递树中的旧版依赖引入，主 TLS 链路已全部使用修复后的 `rustls-webpki 0.103.12`。
