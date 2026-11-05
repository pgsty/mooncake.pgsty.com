---
title: "v0.1 on Neon Postgres"
linkTitle: "v0.1 on Neon"
description: "Historical guide for enabling pg_mooncake v0.1 on Neon serverless PostgreSQL."
weight: 35
icon: fa-solid fa-server
upstream_link: https://web.archive.org/web/20251207100421/https://docs.mooncake.dev/pg/0.1/get-started/Neon-postgres
aliases:
  - "/pg/0.1/get-started/Neon-postgres/"
  - "/0.1/get-started/Neon-postgres/"
  - "/pg/0.1/get-started/neon-postgres/"
  - "/0.1/get-started/neon-postgres/"
---

> [!WARNING] Legacy `pg_mooncake v0.1` Archive (Delta Lake Engine)
> This page documents **`pg_mooncake v0.1`**, which used direct `CREATE TABLE ... USING columnstore` DDL and Delta Lake storage. Starting in `v0.2` and PGSTY's **`v0.3.0`** release, `pg_mooncake` uses [`moonlink`](/docs/intro/moonlink/) real-time columnstore mirrors (`CALL mooncake.create_table` + `USING mooncake`) and Apache Iceberg v2. For current documentation, see [Introduction](/docs/intro/) and [v0.1 vs v0.2 & v0.3](/docs/intro/0.1-vs-0.2/).

`pg_mooncake v0.1` was offered as an experimental extension on [Neon](https://neon.tech).

## Enable the Extension on Neon (`v0.1`)

```sql
SET neon.allow_unstable_extensions = 'true';
CREATE EXTENSION pg_mooncake;
```

## Cloud Storage Requirement

Because Neon does not allow extensions to persist columnstore files on local compute disk, using `pg_mooncake v0.1` on Neon required configuring an external S3 or Cloudflare R2 bucket as described in [v0.1 Cloud Storage](/docs/v0.1/cloud-storage/), and disabling Neon's scale-to-zero feature to preserve local metadata caches.
