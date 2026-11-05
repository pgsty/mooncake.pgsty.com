---
title: "v0.1 GUC Configurations"
linkTitle: "v0.1 Configurations"
description: "Historical PostgreSQL GUC variables in pg_mooncake v0.1 (mooncake.default_bucket, maximum_memory, maximum_threads, enable_local_cache, enable_memory_metadata_cache)."
weight: 55
icon: fa-solid fa-sliders
upstream_link: https://web.archive.org/web/20251207095602/https://docs.mooncake.dev/pg/0.1/reference/configurations
aliases:
  - "/pg/0.1/reference/configurations/"
  - "/0.1/reference/configurations/"
---

> [!WARNING] Legacy `pg_mooncake v0.1` Archive (Delta Lake Engine)
> This page documents **`pg_mooncake v0.1`**, which used direct `CREATE TABLE ... USING columnstore` DDL and Delta Lake storage. Starting in `v0.2` and PGSTY's **`v0.3.0`** release, `pg_mooncake` uses [`moonlink`](/docs/intro/moonlink/) real-time columnstore mirrors (`CALL mooncake.create_table` + `USING mooncake`) and Apache Iceberg v2. For current documentation, see [Introduction](/docs/intro/) and [v0.1 vs v0.2 & v0.3](/docs/intro/0.1-vs-0.2/).

## `v0.1` GUC Parameters

```sql
-- Default cloud storage bucket
ALTER DATABASE <database_name> SET mooncake.default_bucket = 's3://my-bucket';

-- Memory allocated to DuckDB (v0.1.1+, default 4GB)
ALTER DATABASE <database_name> SET mooncake.maximum_memory = '6GB';
CALL mooncake.reset_duckdb();

-- Number of threads for DuckDB (v0.1.1+, default -1 = all cores)
ALTER DATABASE <database_name> SET mooncake.maximum_threads = -1;

-- Local write cache (default true)
ALTER DATABASE <database_name> SET mooncake.enable_local_cache = false;

-- Memory cache for Parquet metadata (default true)
ALTER DATABASE <database_name> SET mooncake.enable_memory_metadata_cache = false;
```
