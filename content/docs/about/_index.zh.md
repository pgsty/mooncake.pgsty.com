---
title: "关于"
linkTitle: "关于"
description: "PGSTY Mooncake 生态的项目维护说明、历史路线图、许可证、上游致谢、商标政策与软件物料清单（SBOM）。"
weight: 60
icon: "fa-solid fa-circle-info"
upstream_link: ""
cascade:
  upstream_link: ""
aliases:
  - /zh/about/
---

**`mooncake.pgsty.com`** 是 [**PGSTY**](https://github.com/pgsty) 维护的 **Mooncake**（面向 PostgreSQL 与 DuckDB 的实时分析生态）分支项目的伴生文档与工程站点：

| 代码仓库 | 当前标签 | 许可证 | 上游来源 | 说明 |
|:---|:---|:---|:---|:---|
| [`pgsty/pg_mooncake`](https://github.com/pgsty/pg_mooncake) | [`v0.3.0`](https://github.com/pgsty/pg_mooncake/releases/tag/v0.3.0) | `MIT` | [`Mooncake-Labs/pg_mooncake`](https://github.com/Mooncake-Labs/pg_mooncake) | PostgreSQL 列存表扩展（基于 `pgrx 0.19.3` 与 `pg_duckdb 1.2.0`）。 |
| [`pgsty/duckdb_mooncake`](https://github.com/pgsty/duckdb_mooncake) | [`v0.0.2`](https://github.com/pgsty/duckdb_mooncake/releases/tag/v0.0.2) | `MIT` | [`Mooncake-Labs/duckdb_mooncake`](https://github.com/Mooncake-Labs/duckdb_mooncake) | 挂载 Moonlink 实时 Iceberg 表的 DuckDB `2.0.0` 存储扩展。 |
| [`pgsty/moonlink`](https://github.com/pgsty/moonlink) | [`v0.0.1`](https://github.com/pgsty/moonlink/releases/tag/v0.0.1) | `BSL-1.1` + 链接豁免（客户端 crate 为 `MIT`） | [`Mooncake-Labs/moonlink`](https://github.com/Mooncake-Labs/moonlink) | 将实时流式更新与 CDC 摄入 Apache Iceberg 与 Parquet 的 Rust 引擎。 |
{.wide .expand}

---

## 章节导航

{{< cards >}}
{{< card link="/zh/docs/about/roadmap/" title="路线图" icon="fa-solid fa-road" >}}
上游 `v0.2` 历史特性路线图与当前 PGSTY 分支的工程维护重点（`v0.3.0+`）。
{{< /card >}}
{{< card link="/zh/docs/about/license/" title="开源许可" icon="fa-solid fa-scale-balanced" >}}
`MIT`、带 `pg_mooncake` 链接与分发豁免的 `BSL-1.1`，以及 `CC-BY-4.0` 文档许可协议。
{{< /card >}}
{{< card link="/zh/docs/about/attribution/" title="致谢与来源" icon="fa-solid fa-users" >}}
Mooncake Labs 原始团队致谢、Wayback Machine 文档恢复说明与代码仓库演进脉络。
{{< /card >}}
{{< card link="/zh/docs/about/trademark/" title="商标声明" icon="fa-solid fa-registered" >}}
商标归属说明与 PGSTY 分支的独立维护声明。
{{< /card >}}
{{< card link="/zh/docs/about/sbom/" title="SBOM 与安全审计" icon="fa-solid fa-boxes-stacked" >}}
子模块版本矩阵（`versions.json`）与 2026-11-05 Cargo RustSec 依赖安全审计报告。
{{< /card >}}
{{< /cards >}}
