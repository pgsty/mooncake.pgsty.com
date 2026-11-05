---
title: "Mooncake 技术文档"
linkTitle: "文档"
description: "PostgreSQL 实时列存与 Apache Iceberg v2 湖仓套件统一技术文档中心：涵盖 pg_mooncake (v0.3.0)、moonlink (v0.0.1) 与 duckdb_mooncake (v0.0.2)。"
weight: 10
icon: fa-solid fa-book
type: docs
sidebar_root_for: self
upstream_source: docs
upstream_link: https://web.archive.org/web/20251207085834/https://docs.mooncake.dev/pg/intro/
upstream_modified: true
no_list: true
cascade:
  type: docs
  upstream_source: docs
  upstream_modified: true
---

## 核心文档导航

{{< cards >}}
{{< card title="简介与核心架构" icon="fa-solid fa-compass" badge="v0.3.0" link="/zh/docs/intro/" >}}
全面了解 Mooncake 架构：解析 `pg_mooncake`、`moonlink`、`duckdb_mooncake` 与 `pg_duckdb 1.2.0` 的协同机制，以及从 `v0.1` 到 `v0.2` / `v0.3` 的演进。
{{< /card >}}
{{< card title="快速开始与安装" icon="fa-solid fa-rocket" badge="PG 14–18" link="/zh/docs/getting-started/" >}}
通过 Pigsty 软件包或从源码安装 `pg_mooncake` 与 `pg_duckdb`，跟随 Hello World 教程创建第一张列存镜像表，并了解当前已知限制。
{{< /card >}}
{{< card title="SQL 与配置参考手册" icon="fa-solid fa-code" badge="API" link="/zh/docs/reference/" >}}
完整查阅 `mooncake.create_table`、`create_snapshot`、`optimize_table`、`list_tables` 存储过程、支持的查询形态、Iceberg S3/R2 配置与外部数据湖扫描。
{{< /card >}}
{{< card title="应用场景与架构模式" icon="fa-solid fa-diagram-project" link="/zh/docs/use-cases/" >}}
实时操作分析（HTAP）、时间分区大表冷热归档、零 ETL Postgres 湖仓一体以及 OpenTelemetry 日志分析的架构与 SQL 实践。
{{< /card >}}
{{< card title="v0.1 历史归档 (Delta Lake)" icon="fa-solid fa-box-archive" badge="Deprecated" link="/zh/docs/v0.1/" >}}
完整保留 `pg_mooncake v0.1`（`USING columnstore` + Delta Lake 存储）历史技术文档，供旧版存量部署参考并兼容 Wayback 历史链接。
{{< /card >}}
{{< card title="关于、开源许可与 SBOM" icon="fa-solid fa-circle-info" badge="PGSTY" link="/zh/docs/about/" >}}
PGSTY 社区维护说明、`MIT` 与 `BSL-1.1` 链接豁免许可证条款、Wayback Machine 历史文档恢复来源以及 Cargo 依赖安全审计报告。
{{< /card >}}
{{< /cards >}}

## 核心组件与专题深入

{{< cards >}}
{{< card title="系统架构剖析" icon="fa-solid fa-sitemap" link="/zh/docs/intro/architecture/" >}}
深入解析写入路径（`Logical WAL` -> `Moonlink`）、读取路径（`pg_duckdb` -> `duckdb_mooncake`）以及双层列存格式（内存 Arrow + Parquet + Apache Iceberg v2）。
{{< /card >}}
{{< card title="Moonlink 实时摄取引擎" icon="fa-solid fa-arrows-rotate" link="/zh/docs/intro/moonlink/" >}}
实时逻辑复制 CDC、Arrow 内存写缓冲、Roaring Bitmap 删除向量、LSN 快照一致性屏障，以及独立 `moonlink_service` REST/RPC 服务部署。
{{< /card >}}
{{< card title="duckdb_mooncake 与 DuckDB 2.0" icon="fa-solid fa-database" link="/zh/docs/intro/duckdb-mooncake/" >}}
了解 `duckdb_mooncake v0.0.2` 如何连接 DuckDB 2.0 与 Moonlink 元数据，并利用多文件 Parquet 统计信息接口实现高效分段跳过。
{{< /card >}}
{{< card title="创建列存镜像表" icon="fa-solid fa-table-columns" link="/zh/docs/reference/create-columnstore/" >}}
使用 `CALL mooncake.create_table(...)` 将本地或远程（`src_uri`）PostgreSQL 普通表及分区表复制为 `USING mooncake` 实时列存镜像表。
{{< /card >}}
{{< card title="Apache Iceberg 与对象存储" icon="fa-solid fa-cloud" link="/zh/docs/reference/iceberg/" >}}
配置 `mooncake.default_bucket` 指向 AWS S3 或 Cloudflare R2，调用 `mooncake.create_snapshot` 物化快照，并通过外部引擎直接读取。
{{< /card >}}
{{< card title="在 Postgres 中查询外部数据湖" icon="fa-solid fa-magnifying-glass-chart" link="/zh/docs/reference/query-data-lake/" >}}
在 PostgreSQL 内直接查询外部 Parquet、CSV、JSON、Apache Iceberg、Delta Lake 及 HuggingFace 数据集，并与本地行存表直接关联。
{{< /card >}}
{{< /cards >}}
