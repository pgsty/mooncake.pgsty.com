---
title: "duckdb_mooncake & DuckDB 2.0 Integration"
linkTitle: "duckdb_mooncake"
description: "How duckdb_mooncake (v0.0.2) connects DuckDB 2.0 and pg_duckdb 1.2.0 to Moonlink tables, performs multi-file Parquet statistics pruning, and installs via a local extension repository."
weight: 30
icon: fa-solid fa-database
upstream_source: duckdb_mooncake
upstream_link: https://github.com/Mooncake-Labs/duckdb_mooncake
---

**`duckdb_mooncake`** ([`pgsty/duckdb_mooncake`](https://github.com/pgsty/duckdb_mooncake), current release **`v0.0.2`**, `MIT` license) is a C++ and Rust FFI storage extension for **DuckDB `v2.0.0`**. It allows DuckDB (both standalone and embedded inside PostgreSQL via `pg_duckdb 1.2.0`) to attach directly to a [`moonlink`](/docs/intro/moonlink/) metadata directory and execute vectorized scans over Moonlink tables.

## Role Inside `pg_mooncake 0.3.0` {#role}

When `pg_mooncake` executes a query against a `USING mooncake` table inside PostgreSQL, `pg_duckdb` delegates the table scan to DuckDB. `pg_mooncake` automatically initializes the DuckDB session by running:

```sql
-- Executed automatically by pg_mooncake when initializing the DuckDB connection
SET extension_directory = '<mooncake.extension_repository>';
LOAD mooncake;
ATTACH '' AS mooncake (TYPE mooncake, METADATA '<pgdata>/pg_mooncake');
```

### Local Extension Repository (`mooncake.extension_repository`) {#extension-repository}

Rather than downloading an unsigned binary from a remote community S3 bucket at runtime, `pg_mooncake 0.3.0` builds and packages `mooncake.duckdb_extension` (`v0.0.2`) directly alongside the PostgreSQL extension into a local DuckDB extension repository:

```text
$(pg_config --sharedir)/extension/pg_mooncake/
└── v2.0.0/
    └── <duckdb_platform>/          # e.g., linux_amd64, linux_arm64, osx_arm64
        └── mooncake.duckdb_extension
```

The PostgreSQL GUC `mooncake.extension_repository` points to this directory (or can be overridden in `postgresql.conf` when installing to a custom path), ensuring offline, deterministic, byte-for-byte reproducible loading with `duckdb.allow_unsigned_extensions = true`.

## DuckDB 2.0 Adaptation in `v0.0.2` {#duckdb-2}

In PGSTY's **`duckdb_mooncake v0.0.2`** (`49765a369ad88986916ce53c969ed2ce4ba66fac`) release, the extension was ported to **DuckDB `v2.0.0`** (`d54cbbe3df17e8e5ce68312f483b4155836112aa`) and **`pg_duckdb 1.2.0`**:

1. **DuckDB 2.0 Storage & Catalog APIs**: Updated storage extension registration, catalog entry lookup, Arrow schema conversion (`nanoarrow 0.7`), table function binding, multi-file lists, and table filter pushdown to match DuckDB 2.0 signatures.
2. **Exported Multi-File Parquet Statistics Interface**: Earlier builds depended on internal `ParquetReader` symbols that are no longer exported by `libduckdb.so` in DuckDB 2.0. `duckdb_mooncake v0.0.2` reads column statistics through DuckDB 2.0's exported multi-file reader interface (`MultiFileReader`), verifying zero unresolved dynamic symbols (`ldd -r`) against `pg_duckdb`'s `libduckdb.so`.
3. **Object-Cache Deadlock Elimination**: Previously, constructing cached statistics entries inside the object-cache mutex could trigger a reentrant lock deadlock when loading Parquet file metadata also accessed the DuckDB object cache. `v0.0.2` constructs statistics entries outside the object-cache mutex before inserting them into the cache.
4. **CRoaring & Corrosion Build Hardening**: Links against `Corrosion v0.5`, `nanoarrow 0.7`, and `CRoaring v5.5.4` (with SHA-256 verification when a system `libroaring` is absent), and builds the Rust `moonlink_ffi` client with `--locked` Cargo dependencies (`0` RustSec vulnerability matches).

## Standalone Usage in DuckDB CLI {#standalone}

You can also load `duckdb_mooncake` directly in a standalone DuckDB `v2.0.0` CLI (`duckdb -unsigned`) to inspect or query a Moonlink directory:

```sql
-- Point DuckDB to the local extension repository
SET extension_directory = '/usr/pgsql-18/share/extension/pg_mooncake';
LOAD mooncake;

-- Attach to a Moonlink metadata directory
ATTACH '' AS mooncake (TYPE mooncake, METADATA '/var/lib/pgsql/18/data/pg_mooncake');

-- Run vectorized analytical queries directly from DuckDB
SELECT * FROM mooncake.public.trades_analytics LIMIT 10;
```
