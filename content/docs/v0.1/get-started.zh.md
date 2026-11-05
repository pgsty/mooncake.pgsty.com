---
title: "v0.1 快速开始"
linkTitle: "v0.1 快速开始"
description: "pg_mooncake v0.1 历史安装指南（Docker 容器与源码构建）。"
weight: 20
icon: fa-solid fa-rocket
upstream_link: https://web.archive.org/web/20251207105139/https://docs.mooncake.dev/pg/0.1/get-started/
aliases:
  - "/zh/pg/0.1/get-started/"
  - "/zh/0.1/get-started/"
---

> [!WARNING] `pg_mooncake v0.1` 历史归档文档（Delta Lake 引擎）
> 本页归档的是早期 **`pg_mooncake v0.1`** 版本文档（采用直接 `CREATE TABLE ... USING columnstore` DDL 与 Delta Lake 存储）。从 `v0.2` 及 PGSTY 维护的 **`v0.3.0`** 版本起，`pg_mooncake` 已全面转向基于 [`moonlink`](/zh/docs/intro/moonlink/) 的实时列存镜像架构（`CALL mooncake.create_table` + `USING mooncake`）与 Apache Iceberg v2。最新文档请参阅[简介](/zh/docs/intro/)与 [v0.1 与 v0.2 / v0.3 架构演进对比](/zh/docs/intro/0.1-vs-0.2/)。

## 历史 Docker 镜像（Obsolete）

```bash
docker pull mooncakelabs/pg_mooncake
docker run --name mooncake-demo -e POSTGRES_HOST_AUTH_METHOD=trust -p 5432:5432 -d mooncakelabs/pg_mooncake
docker run -it --rm --link mooncake-demo:postgres mooncakelabs/pg_mooncake psql -h postgres -U postgres
```

## 从源码编译 `v0.1`

```bash
git submodule update --init --recursive
make release -j$(nproc)
make install
```

## 创建扩展

```sql
CREATE EXTENSION pg_mooncake;
```
