---
title: "致谢与来源"
linkTitle: "致谢与来源"
description: "对 Mooncake Labs 原始团队的致谢、Wayback Machine 文档恢复说明与代码仓库演进脉络。"
weight: 30
icon: "fa-solid fa-users"
---

## 上游原作者致谢

**`pg_mooncake`**、**`duckdb_mooncake`** 与 **`moonlink`** 由 [**Mooncake Labs**](https://github.com/Mooncake-Labs) 团队创建。所有核心架构设计——包括行存 + 列存混合表模型、Moonlink 实时 Iceberg 缓冲引擎、逻辑复制 WAL 摄入流水线以及 DuckDB 向量化执行桥接——均归属于 Mooncake Labs 原作者与社区贡献者。

---

## 代码仓库演进脉络

| PGSTY 代码仓库 | 上游源仓库 | 上游基线提交 | PGSTY 发布标签 |
|:---|:---|:---|:---|
| [`pgsty/pg_mooncake`](https://github.com/pgsty/pg_mooncake) | [`Mooncake-Labs/pg_mooncake`](https://github.com/Mooncake-Labs/pg_mooncake) | `v0.2.0` (`be17cd0`) 及后续上游提交 | `v0.3.0` (`1a9cbfd65be9a6486d020120acb49ef0c6800d68`) |
| [`pgsty/duckdb_mooncake`](https://github.com/pgsty/duckdb_mooncake) | [`Mooncake-Labs/duckdb_mooncake`](https://github.com/Mooncake-Labs/duckdb_mooncake) | `ba79184` | `v0.0.2` (`49765a369ad88986916ce53c969ed2ce4ba66fac`) |
| [`pgsty/moonlink`](https://github.com/pgsty/moonlink) | [`Mooncake-Labs/moonlink`](https://github.com/Mooncake-Labs/moonlink) | `f2e1715` | `v0.0.1` (`b298ef7444890e3c8af5544e350232518bcfd8e5`) |
| [`pgsty/pg_duckdb`](https://github.com/pgsty/pg_duckdb) | [`duckdb/pg_duckdb`](https://github.com/duckdb/pg_duckdb) | `v1.2.0` | `v1.2.0` (`8756099e267c47f0b86c24de4cf995327f1f4279`) |
{.wide .expand}

---

## 文档来源与历史快照恢复

上游原文档站点（`https://docs.mooncake.dev/`）在项目转型后已下线，且 GitHub 上未公开原始文档源码仓库。

为了完整保留 `v0.2`（Moonlink + Iceberg 架构）与 `v0.1`（Delta Lake 架构）的参考手册：

1. **Wayback Machine 历史快照提取**：我们从 [Internet Archive Wayback Machine 历史快照（`2025-12-07`）](https://web.archive.org/web/20251207085834/https://docs.mooncake.dev/pg/intro/)中完整恢复了全部 34 个规范文档路径（17 页 `v0.2` 文档、16 页 `v0.1` 文档与 1 页 Moonlink 概览）、30 个早期历史路径别名以及 4 幅原始架构图。
2. **对照 `v0.3.0` 源码逐项核验**：所有 SQL 函数签名、GUC 配置参数、环境变量与错误码均已对照 `pgsty/pg_mooncake v0.3.0` 源码树（`pgrx 0.19.3`、`pg_duckdb 1.2.0`、`duckdb_mooncake v0.0.2`、`moonlink v0.0.1`）完成核验与修正。
3. **中英双语翻译与工程报告**：PGSTY 补充了完整的简体中文文档（`/zh/docs/`），并发布了涵盖 DuckDB 2.0 适配、`pgrx 0.19.3` 升级以及 2026-11-05 RustSec 依赖安全审计的工程报告。

所有改编自上游历史文档的页面均在 Front Matter 中标注了 `upstream_source` 与 `upstream_link` 元数据。
