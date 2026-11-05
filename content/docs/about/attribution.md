---
title: "Attribution"
linkTitle: "Attribution"
description: "Upstream credits to Mooncake Labs, Wayback Machine documentation recovery provenance, and repository lineage."
weight: 30
icon: "fa-solid fa-users"
---

## Upstream Creators

**`pg_mooncake`**, **`duckdb_mooncake`**, and **`moonlink`** were created by [**Mooncake Labs**](https://github.com/Mooncake-Labs). All core architectural credit — including the hybrid rowstore + columnstore design, the Moonlink real-time Iceberg buffer engine, logical replication WAL ingestion, and the DuckDB execution bridge — belongs to the original Mooncake Labs authors and contributors.

---

## Repository Lineage

| PGSTY Repository | Upstream Source | Upstream Baseline Commit | PGSTY Release Tag |
|:---|:---|:---|:---|
| [`pgsty/pg_mooncake`](https://github.com/pgsty/pg_mooncake) | [`Mooncake-Labs/pg_mooncake`](https://github.com/Mooncake-Labs/pg_mooncake) | `v0.2.0` (`be17cd0`) + post-0.2 upstream commits | `v0.3.0` (`1a9cbfd65be9a6486d020120acb49ef0c6800d68`) |
| [`pgsty/duckdb_mooncake`](https://github.com/pgsty/duckdb_mooncake) | [`Mooncake-Labs/duckdb_mooncake`](https://github.com/Mooncake-Labs/duckdb_mooncake) | `ba79184` | `v0.0.2` (`49765a369ad88986916ce53c969ed2ce4ba66fac`) |
| [`pgsty/moonlink`](https://github.com/pgsty/moonlink) | [`Mooncake-Labs/moonlink`](https://github.com/Mooncake-Labs/moonlink) | `f2e1715` | `v0.0.1` (`b298ef7444890e3c8af5544e350232518bcfd8e5`) |
| [`pgsty/pg_duckdb`](https://github.com/pgsty/pg_duckdb) | [`duckdb/pg_duckdb`](https://github.com/duckdb/pg_duckdb) | `v1.2.0` | `v1.2.0` (`8756099e267c47f0b86c24de4cf995327f1f4279`) |
{.wide .expand}

---

## Documentation Provenance & Recovery

The original upstream documentation website (`https://docs.mooncake.dev/`) was taken offline after the upstream project transitioned direction, and no public documentation source repository remained available on GitHub.

To preserve the reference manuals for both `v0.2` (Moonlink + Iceberg) and `v0.1` (Delta Lake):

1. **Wayback Machine Snapshot Extraction**: All 34 canonical documentation pages (17 `v0.2` pages, 16 `v0.1` pages, and 1 Moonlink overview page) plus 30 historical alias routes and 4 original architecture diagrams were recovered from the [Internet Archive Wayback Machine snapshot (`2025-12-07`)](https://web.archive.org/web/20251207085834/https://docs.mooncake.dev/pg/intro/).
2. **Verification Against `v0.3.0` Source**: Every SQL function signature, configuration GUC, environment variable, and error code was cross-checked against the `pgsty/pg_mooncake v0.3.0` source tree (`pgrx 0.19.3`, `pg_duckdb 1.2.0`, `duckdb_mooncake v0.0.2`, `moonlink v0.0.1`).
3. **Bilingual Translation & Engineering Reports**: PGSTY added full Simplified Chinese translations (`/zh/docs/`) and published engineering reports covering the DuckDB 2.0 adaptation, `pgrx 0.19.3` migration, and the 2026-11-05 RustSec dependency audit.

Every page adapted from the historical upstream documentation includes `upstream_source` and `upstream_link` metadata in its front matter.
