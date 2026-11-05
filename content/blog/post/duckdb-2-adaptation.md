---
title: "Porting pg_mooncake and duckdb_mooncake to DuckDB 2.0, pg_duckdb 1.2.0, and pgrx 0.19.3"
date: 2026-11-05
description: "An engineering walkthrough of adapting duckdb_mooncake v0.0.2 and pg_mooncake v0.3.0 to DuckDB 2.0 C++ catalog/filter APIs, wiring LSN-consistent snapshot reads via dlsym, and fixing NULL filter pushdown index remapping."
author: "[Ruohang Feng](https://vonng.com/en/) · [PGSTY](https://pgsty.com)"
authors:
  - "vonng"
images:
  - "/blog/covers/duckdb-2-adaptation.svg"
tags:
  - "engineering"
  - "duckdb"
  - "pg_mooncake"
  - "duckdb_mooncake"
  - "pgrx"
upstream_source: ""
upstream_link: ""
---

When Mooncake Labs paused public updates to [`pg_mooncake`](https://github.com/Mooncake-Labs/pg_mooncake) after `v0.2.0`, the extension was pinned to an earlier DuckDB `1.3.x` / `pg_duckdb` snapshot and `pgrx 0.12`. Meanwhile, the PostgreSQL ecosystem moved forward to **PostgreSQL 18**, **`pgrx 0.19.3`**, and **`pg_duckdb 1.2.0`** (which embeds **DuckDB `v2.0.0`**).

This article walks through the engineering changes required to bring the entire Mooncake stack — **`pg_mooncake v0.3.0`**, **`duckdb_mooncake v0.0.2`**, and **`moonlink v0.0.1`** — onto **DuckDB `2.0.0`**, **`pg_duckdb 1.2.0`**, and **`pgrx 0.19.3`**.

---

## Architecture Recap: How the Three Repositories Fit Together

Understanding the build and runtime boundaries between the three repositories explains why upgrading DuckDB touches both C++ and Rust across multiple crates:

```
┌──────────────────────────────────────────────────────────────────────┐
│                         PostgreSQL Process                           │
│                                                                      │
│  ┌─────────────────────────┐          ┌───────────────────────────┐  │
│  │    pg_mooncake.so       │          │      pg_duckdb.so         │  │
│  │  (Rust / pgrx 0.19.3)   │          │  (C++ / DuckDB v2.0.0)    │  │
│  │                         │          │                           │  │
│  │  • mooncake_worker      │          │  • DuckDB planner/engine  │  │
│  │    (walsender +         │          │  • Loads                  │  │
│  │     embedded moonlink)  │◄────────►│    duckdb_mooncake        │  │
│  │  • Exports              │  dlsym   │    storage extension      │  │
│  │    mooncake_get_        │  + IPC   │  • Scans Iceberg Parquet  │  │
│  │    postgres_lsn()       │  socket  │    + Moonlink Puffin      │  │
│  └─────────────────────────┘          └───────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────┘
```

1. **`pg_mooncake`** is a `pgrx` Rust extension that manages `mooncake.create_table(dst, src)`, spawns the `mooncake_worker` background process, streams logical replication changes into an embedded **`moonlink`** engine, and compiles **`duckdb_mooncake`** into the same shared library.
2. **`pg_duckdb`** embeds `libduckdb` (`v2.0.0`) inside PostgreSQL and intercepts queries referencing `columnstore` tables.
3. **`duckdb_mooncake`** registers a DuckDB `StorageExtension` (`mooncake`) that resolves columnstore tables via Moonlink's UNIX domain socket (`mooncake.sock`), waits for the target PostgreSQL WAL LSN, and delegates file scans to DuckDB's parallel `parquet_scan` reader alongside an in-memory Puffin deletion-vector reader.

---

## 1. Adapting `duckdb_mooncake` to DuckDB `2.0.0` C++ APIs

DuckDB `2.0.0` (`d54cbbe3df17e8e5ce68312f483b4155836112aa`) introduced several breaking C++ API changes across its catalog, storage extension, and filter pushdown layers:

### `StorageExtension` Registration (`StorageExtension::Register`)

In DuckDB 1.x, extensions mutated `config.storage_extensions["mooncake"]` directly. In DuckDB 2.0, storage extensions are registered via `StorageExtension::Register(config, "mooncake", make_shared_ptr<MooncakeStorageExtension>())`.

### `TableCatalogEntry::GetColumns()` & `GetTypes()`

`MooncakeTableEntry` inherits from `TableCatalogEntry`. We aligned its constructor and column projection helpers with DuckDB 2.0's `ColumnList` and `LogicalType` APIs while preserving the virtual `__row_id` (`UBIGINT`) pseudo-column used by Moonlink deletion vectors.

### `TableFilterSet` Iterator Refactoring

In DuckDB 1.x, `TableFilterSet` exposed a direct `std::unordered_map<idx_t, unique_ptr<TableFilter>> filters` member. In DuckDB 2.0, `TableFilterSet` encapsulates its filter map and provides range-based iteration yielding `(FilterIndex, const TableFilter &)` entries.

While porting `MooncakeScanFunction::mooncake_scan_bind` to the new iterator API, we uncovered and fixed a subtle bug in `IS NULL` / `IS NOT NULL` filter pushdown:

- When a query projected a subset of columns (for example, `SELECT b FROM t_col WHERE a IS NOT NULL AND b > 10`), `CONJUNCTION_AND` and comparison filters remapped their column index from the **scan projection index** to the **physical Parquet table column index** (`column_ids[filter_col_idx]`), but `IS_NULL` and `IS_NOT_NULL` filters previously passed the unmapped scan index directly to the underlying Parquet filter set.
- Under DuckDB 2.0, an out-of-bounds or mismatched filter column index on `parquet_scan` caused a segmentation fault (`SIGSEGV`) during `SELECT count(*) FROM (SELECT DISTINCT c, a, b FROM t WHERE c IS NULL AND b > 2)`.
- Remapping `IS_NULL` and `IS_NOT_NULL` filter indices through `column_ids` resolved the crash completely.

---

## 2. Wiring LSN-Consistent Snapshot Reads Across `pg_mooncake` and `duckdb_mooncake`

Because `pg_mooncake` ingests heap writes asynchronously via PostgreSQL logical replication, a `SELECT` issued immediately after an `INSERT` or `COMMIT` must wait until `moonlink` has ingested WAL up to the current flush position.

In `v0.3.0`, we completed the cross-library LSN bridge:

1. In `pg_mooncake` (`src/lib.rs`), we exported an `extern "C"` symbol:
   ```rust
   #[no_mangle]
   pub extern "C-unwind" fn mooncake_get_postgres_lsn() -> u64 {
       unsafe {
           if pg_sys::RecoveryInProgress() {
               0
           } else {
               pg_sys::GetXLogFlushRecPtr()
           }
       }
   }
   ```
2. In `duckdb_mooncake`, the storage extension resolves `mooncake_get_postgres_lsn` at runtime via `dlsym(RTLD_DEFAULT, "mooncake_get_postgres_lsn")` (falling back to `0` when `duckdb_mooncake` is loaded inside a standalone DuckDB CLI session outside PostgreSQL).
3. When binding a scan on a `columnstore` table, `duckdb_mooncake` passes that LSN to `moonlink_scan_table_begin(...)`, which blocks until Moonlink's WAL consumer reaches the target LSN.

---

## 3. Automatic `REPLICA IDENTITY FULL` on Partitioned Tables

PostgreSQL logical replication requires `REPLICA IDENTITY FULL` on tables that do not have a primary key (or where Moonlink needs the full before-image of updated/deleted tuples). When a user mirrors a partitioned table via `CALL mooncake.create_table('sales_col', 'sales')`, setting `REPLICA IDENTITY FULL` only on the parent partitioned table does not propagate to existing leaf partitions.

`pg_mooncake 0.3.0` now uses `pg_sys::find_all_inheritors(relid, pg_sys::AccessExclusiveLock as i32, std::ptr::null_mut())` during `mooncake.create_table` to set `REPLICA IDENTITY FULL` on the root table and all existing child partitions in a single atomic operation.

---

## 4. End-to-End Verification

The adapted stack was validated across two clean Linux ARM64 environments:

1. **Ubuntu 24.04.5 LTS ARM64 (`mooncake-u24a-pg18`, PostgreSQL `18.6`)**
2. **Rocky Linux 10.2 ARM64 (`mooncake-el10a-pg17`, PostgreSQL `17.11`)**

All 58 Moonlink `table_handler` unit tests, all 3 SQL regression suites (`small`, `partition`, `unsupported`), the runtime `pg_duckdb 1.2.0` version guard, and 13 post-restart persistence and Iceberg metadata checks passed with zero failures.
