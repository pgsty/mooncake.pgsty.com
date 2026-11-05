---
title: "SQL Procedures, Views & Configuration Reference"
linkTitle: "Reference"
description: "Complete SQL API and GUC configuration reference for pg_mooncake (v0.3.0), including mooncake.create_table, create_snapshot, optimize_table, list_tables, and DuckDB settings."
weight: 30
icon: fa-solid fa-code
upstream_link: https://web.archive.org/web/20251207105147/https://docs.mooncake.dev/pg/reference/
aliases:
  - "/pg/reference/"
  - "/reference/"
---

This section provides the complete reference for all SQL procedures, catalog inspection functions, table access methods, and PostgreSQL GUC configuration parameters exposed by **`pg_mooncake` (`v0.3.0`)**.

## SQL Procedures & Functions (`mooncake` schema) {#sql-api}

| Object | Signature | Description |
|:---|:---|:---|
| **`mooncake.create_table`** | `CALL mooncake.create_table(dst text, src text, src_uri text DEFAULT NULL, table_config json DEFAULT NULL)` | Creates a read-only `USING mooncake` columnstore mirror table (`dst`) replicating from local or remote (`src_uri`) PostgreSQL table (`src`). |
| **`mooncake.create_snapshot`** | `CALL mooncake.create_snapshot(dst text)` | Waits for Moonlink to reach the current PostgreSQL WAL write LSN, flushes buffered Arrow data to Parquet, and writes a new Apache Iceberg v2 metadata snapshot. |
| **`mooncake.optimize_table`** | `CALL mooncake.optimize_table(dst text, mode text)` | Runs compaction and deletion-vector reconciliation on `dst` (`mode` can be `'full'` or `'minor'`). |
| **`mooncake.list_tables`** | `SELECT * FROM mooncake.list_tables()` | Set-returning function returning `(table text, commit_lsn pg_lsn, flush_lsn pg_lsn, iceberg_warehouse_location text)` for every active Moonlink table in the current database. |
| **`mooncake.load_files`** | `CALL mooncake.load_files(dst text, files text[])` | Unimplemented in `v0.3.0`; explicitly raises `SQLSTATE 0A000` (`FEATURE_NOT_SUPPORTED`) instead of silently returning as a no-op. |
{.wide .expand}

### `mooncake.list_tables()` Output Columns {#list-tables}

```sql
SELECT * FROM mooncake.list_tables();
```

| Column | Type | Description |
|:---|:---:|:---|
| `table` | `text` | Schema-qualified name of the columnstore mirror table (e.g. `public.orders_analytics`). |
| `commit_lsn` | `pg_lsn` | Latest PostgreSQL WAL LSN ingested into Moonlink's in-memory Arrow buffer. |
| `flush_lsn` | `pg_lsn` | Latest PostgreSQL WAL LSN flushed to durable Parquet / Iceberg snapshot storage. |
| `iceberg_warehouse_location` | `text` | Local filesystem directory (`$PGDATA/pg_mooncake/...`) or cloud URI (`s3://...`) containing the Apache Iceberg v2 metadata and Parquet data files. |
{.wide .expand}

## Table Access Method & Event Triggers {#tam}

- **Table Access Method (`USING mooncake`)**: Created automatically by `mooncake.create_table` and registered with `pg_duckdb 1.2.0` via `RegisterDuckdbTableAm("mooncake")`.
- **Drop Cleanup Trigger (`mooncake_drop_trigger`)**: An `ON sql_drop` event trigger (`mooncake_drop_trigger_func`) automatically unregisters the table from Moonlink and cleans up its logical replication subscription when you execute `DROP TABLE <dst>;`.

## GUC Configuration Parameters {#guc}

| Parameter | Type | Default | Context | Description |
|:---|:---:|:---:|:---:|:---|
| `mooncake.default_bucket` | `string` | `''` (local `$PGDATA/pg_mooncake`) | `USERSET` / `SUSET` | Default object storage bucket URI (e.g. `'s3://my-bucket/warehouse'`) where newly created Mooncake tables write Parquet files and Apache Iceberg v2 metadata. |
| `mooncake.extension_repository` | `string` | `$(pg_config --sharedir)/extension/pg_mooncake` | `SUSET` | Local filesystem path containing the bundled `v2.0.0/<platform>/mooncake.duckdb_extension` binary loaded into `pg_duckdb`. |
| `mooncake.enable_local_cache` | `bool` | `true` | `SUSET` | Enables local disk caching when writing to cloud object storage. |
| `duckdb.allow_community_extensions` | `bool` | `false` (must set `true`) | `SUSET` | Required by `pg_duckdb` so `pg_mooncake` can load the `mooncake` DuckDB storage extension. |
| `duckdb.allow_unsigned_extensions` | `bool` | `false` (must set `true`) | `SUSET` | Required so `pg_duckdb` can load the locally built `mooncake.duckdb_extension` binary from `mooncake.extension_repository`. |
| `duckdb.max_memory` | `string` | `4GB` (or 80% RAM) | `SUSET` | Maximum memory allocated to the embedded DuckDB 2.0 analytical execution engine. |
| `duckdb.threads` | `int` | `-1` (all cores) | `SUSET` | Number of worker threads used by DuckDB 2.0 for vectorized query execution. |
{.wide .expand}

## Detailed Reference Guides {#guides}

{{< cards >}}
{{< card title="Create Columnstore Table" icon="fa-solid fa-table-columns" link="/docs/reference/create-columnstore/" >}}
Local and remote (`src_uri`) replication, initial copy options, partitioned tables, and `table_config` JSON parameters.
{{< /card >}}
{{< card title="Query Columnstore & Query Shapes" icon="fa-solid fa-magnifying-glass-chart" link="/docs/reference/query-columnstore/" >}}
Supported analytical query shapes, aggregations, joins with Postgres heap tables, and exposing DuckDB functions in SQL.
{{< /card >}}
{{< card title="Iceberg & Object Storage" icon="fa-solid fa-cloud" link="/docs/reference/iceberg/" >}}
Configure S3 and Cloudflare R2 secrets, materialize Iceberg v2 snapshots, and query Mooncake tables from external engines.
{{< /card >}}
{{< card title="Query Your Data Lake in Postgres" icon="fa-solid fa-folder-open" link="/docs/reference/query-data-lake/" >}}
Scan external Parquet, CSV, JSON, Iceberg, Delta Lake, and HuggingFace datasets directly inside PostgreSQL.
{{< /card >}}
{{< /cards >}}
