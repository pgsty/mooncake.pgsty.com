---
title: "应用场景与架构模式"
linkTitle: "应用场景"
description: "pg_mooncake (v0.3.0) 四大核心生产架构模式：实时操作分析（HTAP）、时间分区大表冷热归档、零 ETL Postgres 湖仓一体以及 OpenTelemetry 日志分析。"
weight: 40
icon: fa-solid fa-diagram-project
upstream_link: https://web.archive.org/web/20260124111154/https://docs.mooncake.dev/pg/use-cases/
aliases:
  - "/zh/pg/use-cases/"
---

无需引入 Kafka、Debezium 或外部独立数仓，`pg_mooncake` 即可在 PostgreSQL 内部直接支撑以下四种高价值分析架构模式：

{{< cards >}}
{{< card title="实时操作分析 (HTAP)" icon="fa-solid fa-bolt" link="/zh/docs/use-cases/real-time-analytics/" >}}
业务继续写入主 OLTP 行存表，将慢速聚合报表查询路由至亚秒级同步的 `USING mooncake` 列存镜像表。
{{< /card >}}
{{< card title="大表分区冷热归档" icon="fa-solid fa-box-archive" link="/zh/docs/use-cases/archiving/" >}}
为按时间分区的 PostgreSQL 大表创建列存镜像，定期从行存中 `DROP` 旧分区释放昂贵磁盘空间，同时在列存中完整保留可随时查询的全部历史数据。
{{< /card >}}
{{< card title="Postgres 湖仓一体 (Lakehouse)" icon="fa-solid fa-cloud" link="/zh/docs/use-cases/lakehouse/" >}}
自动将 PostgreSQL 业务表导出为 S3 或 Cloudflare R2 上的标准 Apache Iceberg v2 表，并在 Postgres 内直接查询外部 Iceberg / Delta Lake 数据集。
{{< /card >}}
{{< card title="日志分析与 OpenTelemetry" icon="fa-solid fa-file-waveform" link="/zh/docs/use-cases/logging/" >}}
在 PostgreSQL 中承载海量应用日志与链路追踪事件，基于对象存储 Parquet 文件实现低成本、高吞吐的向量化聚合查询。
{{< /card >}}
{{< /cards >}}
