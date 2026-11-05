---
title: "pg_mooncake 0.3.0: First PGSTY Release with DuckDB 2.0, pgrx 0.19.3, and PostgreSQL 14–18 Support"
date: 2026-11-05
description: "pg_mooncake 0.3.0 (together with duckdb_mooncake v0.0.2 and moonlink v0.0.1) is the first release maintained by PGSTY, delivering DuckDB 2.0 / pg_duckdb 1.2.0 compatibility, pgrx 0.19.3 across PostgreSQL 14–18, LSN-consistent columnstore snapshots, and a full RustSec dependency security audit."
author: "[Ruohang Feng](https://vonng.com/en/) · [PGSTY](https://pgsty.com)"
authors:
  - "vonng"
images:
  - "/blog/covers/pg-mooncake-0.3.0.svg"
tags:
  - "release"
  - "pg_mooncake"
  - "duckdb_mooncake"
  - "moonlink"
  - "iceberg"
upstream_source: ""
upstream_link: ""
---

**`pg_mooncake 0.3.0`** — released alongside **`duckdb_mooncake v0.0.2`** and **`moonlink v0.0.1`** — is the first release of the Mooncake real-time analytics suite maintained by [**PGSTY**](https://github.com/pgsty):

- **[`pgsty/pg_mooncake v0.3.0`](https://github.com/pgsty/pg_mooncake/releases/tag/v0.3.0)** (`MIT`)
- **[`pgsty/duckdb_mooncake v0.0.2`](https://github.com/pgsty/duckdb_mooncake/releases/tag/v0.0.2)** (`MIT`)
- **[`pgsty/moonlink v0.0.1`](https://github.com/pgsty/moonlink/releases/tag/v0.0.1)** (`BSL-1.1` with `PG_MOONCAKE LINKING & DISTRIBUTION EXCEPTION`, client crates `MIT`)

Binary RPM and DEB packages for **PostgreSQL 14, 15, 16, 17, and 18** across **RHEL / Rocky / AlmaLinux 8, 9, 10** and **Debian 12/13, Ubuntu 22.04/24.04** (`x86_64` and `aarch64`) are available through the [PGEXT repository](/download/) and [Pigsty](https://pigsty.io/ext/e/pg_mooncake).

---

## Highlights of `pg_mooncake 0.3.0`

### 1. Upgraded to `pgrx 0.19.3` & PostgreSQL 14–18

`pg_mooncake` has been migrated to **`pgrx = 0.19.3`** (`cargo-pgrx 0.19.3`), bringing first-class support for **PostgreSQL 18** alongside PostgreSQL 14, 15, 16, and 17:

- Updated extension metadata in `pg_mooncake.control` (`default_version = '0.3.0'`) and added the upgrade script `sql/pg_mooncake--0.2.0--0.3.0.sql`.
- Replaced legacy C string literals with Rust native `CStr` (`c"..."`) across GUC definitions (`mooncake.timeline_id`, `mooncake.enable_local_bucket`, `mooncake.default_bucket`, `mooncake.enable_memory_metadata`).

### 2. DuckDB `2.0.0` & `pg_duckdb 1.2.0` Adaptation

`pg_mooncake 0.3.0` embeds **`pg_duckdb v1.2.0`** and **`duckdb_mooncake v0.0.2`**, built against **DuckDB `v2.0.0`** (`d54cbbe3df17e8e5ce68312f483b4155836112aa`):

- Ported `duckdb_mooncake` to the DuckDB 2.0 `TableCatalogEntry`, `StorageExtensionInfo`, and `TableFilterSet` iterator APIs.
- Fixed column-index remapping for `IS NULL` and `IS NOT NULL` filter pushdown in `MooncakeScanFunction`, preventing segmentation faults when multi-column filters are pushed down to Moonlink Parquet scans.
- Added a **runtime `pg_duckdb` version check** during worker initialization that enforces `pg_duckdb = 1.2.0` (accepting `1.2.0` or `1.2.0-*` pre-release suffixes and failing fast with a clear diagnostic message on mismatched versions such as `1.1.3` or `1.3.0`).

### 3. LSN-Consistent Snapshot Reads (`pg_current_wal_flush_lsn`)

Previously, `duckdb_mooncake` constructed Moonlink table scan descriptors with `lsn = 0`, returning immediately without waiting for recently committed PostgreSQL transactions to be ingested by the background logical replication worker.

In `v0.3.0`, `pg_mooncake` exports `mooncake_get_postgres_lsn()` (calling `pg_current_wal_flush_lsn()` when in a normal backend session and `0` during recovery), and `duckdb_mooncake` resolves that symbol via `dlsym(RTLD_DEFAULT, "mooncake_get_postgres_lsn")`. Every analytical query against a `columnstore` table now waits until Moonlink has caught up to the PostgreSQL WAL flush LSN before scanning.

### 4. Partitioned Table Hierarchy Support (`REPLICA IDENTITY FULL`)

When calling [`mooncake.create_table(dst, src)`](/docs/reference/create-columnstore/) on a partitioned PostgreSQL table, `pg_mooncake 0.3.0` now walks the inheritance tree (`find_all_inheritors`) and sets `REPLICA IDENTITY FULL` on both the parent table and every leaf partition before adding the root table to the logical replication publication.

### 5. Explicit `0A000` Error for Deprecated `mooncake.load_files`

The legacy `v0.1` helper `mooncake.load_files(dst TEXT, files TEXT[])` now raises `ERRCODE_FEATURE_NOT_SUPPORTED` (`0A000`) with a clear migration message instead of silently panicking (`todo!()`).

### 6. Cargo Dependency Security Audit (RustSec)

All three Cargo workspaces (`pg_mooncake`, `moonlink`, `duckdb_mooncake/moonlink_ffi`) underwent a comprehensive security remediation against the RustSec Advisory Database (`2026-11-05`):

- **`pg_mooncake/Cargo.lock`**: reduced vulnerabilities from **33 to 6 (-82%)** and eliminated all unsoundness warnings (`1 -> 0`).
- **`moonlink/Cargo.lock`**: reduced vulnerabilities from **46 to 15 (-67%)** and eliminated all unsoundness warnings (`1 -> 0`).
- **`duckdb_mooncake/moonlink_ffi/Cargo.lock`**: **0 vulnerabilities, 0 unsound, 0 warnings**.
- Upgraded `tonic 0.14.5`, `prost 0.14.3`, `bincode 2.1.0`, `opentelemetry 0.31.0`, `wasmtime 43.0.1`, `rustls 0.23.37`, `aws-lc-rs 1.16.3`, `bytes 1.11.1`, `tar 0.4.45`, and `lz4_flex 0.11.6`. See the [SBOM & Security Audit](/docs/about/sbom/) page for full details.

---

## Validation Summary

`pg_mooncake 0.3.0` was validated end-to-end on both **Ubuntu 24.04.5 LTS ARM64 (`PostgreSQL 18.6`)** and **Rocky Linux 10.2 ARM64 (`PostgreSQL 17.11`)**:

- **58/58** Moonlink `table_handler` unit tests passed.
- **3/3** `pg_Regression` SQL suites (`small`, `partition`, `unsupported`) passed (`0` failures).
- **Runtime version check** verified: rejected `pg_duckdb 1.1.3` and `1.3.0`, accepted `1.2.0`.
- **11/11** real-time replication, `UPDATE`/`DELETE`, partition, Iceberg metadata, and crash-restart persistence checkpoints passed.
