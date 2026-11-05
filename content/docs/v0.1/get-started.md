---
title: "v0.1 Get Started"
linkTitle: "v0.1 Get Started"
description: "Historical v0.1 installation guide using Docker or source builds for PostgreSQL 14–17."
weight: 20
icon: fa-solid fa-rocket
upstream_link: https://web.archive.org/web/20251207105139/https://docs.mooncake.dev/pg/0.1/get-started/
aliases:
  - "/pg/0.1/get-started/"
  - "/0.1/get-started/"
---

> [!WARNING] Legacy `pg_mooncake v0.1` Archive (Delta Lake Engine)
> This page documents **`pg_mooncake v0.1`**, which used direct `CREATE TABLE ... USING columnstore` DDL and Delta Lake storage. Starting in `v0.2` and PGSTY's **`v0.3.0`** release, `pg_mooncake` uses [`moonlink`](/docs/intro/moonlink/) real-time columnstore mirrors (`CALL mooncake.create_table` + `USING mooncake`) and Apache Iceberg v2. For current documentation, see [Introduction](/docs/intro/) and [v0.1 vs v0.2 & v0.3](/docs/intro/0.1-vs-0.2/).

## Historical Docker Image (Obsolete)

```bash
docker pull mooncakelabs/pg_mooncake
docker run --name mooncake-demo -e POSTGRES_HOST_AUTH_METHOD=trust -p 5432:5432 -d mooncakelabs/pg_mooncake
docker run -it --rm --link mooncake-demo:postgres mooncakelabs/pg_mooncake psql -h postgres -U postgres
```

## Building `v0.1` from Source

```bash
git submodule update --init --recursive
make release -j$(nproc)
make install
```

## Create the Extension

```sql
CREATE EXTENSION pg_mooncake;
```
