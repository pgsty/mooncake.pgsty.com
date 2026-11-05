---
title: "v0.1 在 Neon Postgres 上使用"
linkTitle: "v0.1 在 Neon 上运行"
description: "在 Neon Serverless PostgreSQL 上启用 pg_mooncake v0.1 的历史配置说明。"
weight: 35
icon: fa-solid fa-server
upstream_link: https://web.archive.org/web/20251207100421/https://docs.mooncake.dev/pg/0.1/get-started/Neon-postgres
aliases:
  - "/zh/pg/0.1/get-started/Neon-postgres/"
  - "/zh/0.1/get-started/Neon-postgres/"
  - "/zh/pg/0.1/get-started/neon-postgres/"
  - "/zh/0.1/get-started/neon-postgres/"
---

> [!WARNING] `pg_mooncake v0.1` 历史归档文档（Delta Lake 引擎）
> 本页归档的是早期 **`pg_mooncake v0.1`** 版本文档（采用直接 `CREATE TABLE ... USING columnstore` DDL 与 Delta Lake 存储）。从 `v0.2` 及 PGSTY 维护的 **`v0.3.0`** 版本起，`pg_mooncake` 已全面转向基于 [`moonlink`](/zh/docs/intro/moonlink/) 的实时列存镜像架构（`CALL mooncake.create_table` + `USING mooncake`）与 Apache Iceberg v2。最新文档请参阅[简介](/zh/docs/intro/)与 [v0.1 与 v0.2 / v0.3 架构演进对比](/zh/docs/intro/0.1-vs-0.2/)。

`pg_mooncake v0.1` 曾作为实验性扩展提供在 [Neon](https://neon.tech) 托管平台上。

## 在 Neon 上启用扩展（`v0.1`）

```sql
SET neon.allow_unstable_extensions = 'true';
CREATE EXTENSION pg_mooncake;
```

## 对象存储与计算节点要求

由于 Neon 计算节点不支持将列存文件持久化在本地磁盘，在 Neon 上使用 `pg_mooncake v0.1` 必须按 [v0.1 对象存储配置](/zh/docs/v0.1/cloud-storage/) 绑定外部 S3 或 R2 存储桶，并建议关闭 Scale-to-Zero 以保留本地缓存。
