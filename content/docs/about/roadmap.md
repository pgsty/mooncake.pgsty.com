---
title: "Roadmap"
linkTitle: "Roadmap"
description: "Historical v0.2 feature roadmap from Mooncake Labs and current PGSTY maintenance focus."
weight: 10
icon: "fa-solid fa-road"
upstream_source: "docs"
upstream_link: "https://web.archive.org/web/20251207085834/https://docs.mooncake.dev/pg/roadmap"
aliases:
  - /pg/roadmap/
  - /roadmap/
---

> [!NOTE]
> The roadmap items below reflect the historical upstream `pg_mooncake v0.2` design goals published at `docs.mooncake.dev/pg/roadmap`, together with the current maintenance scope of the `pgsty/pg_mooncake` fork (`v0.3.0`).

---

## PGSTY Maintenance Focus (`v0.3.0+`)

The [**PGSTY**](https://github.com/pgsty) fork of the Mooncake suite (`pg_mooncake v0.3.0`, `duckdb_mooncake v0.0.2`, `moonlink v0.0.1`) prioritizes long-term production stability, PostgreSQL version coverage, and security hardening:

1. **PostgreSQL 14–18 Compatibility**: Keeping `pg_mooncake` synchronized with current `pgrx` (`0.19.3`) across PostgreSQL 14, 15, 16, 17, and 18 on Linux (`x86_64` and `aarch64`, RHEL/Rocky EL8–EL10, Debian 12/13, Ubuntu 22.04/24.04).
2. **DuckDB `2.0.0` & `pg_duckdb 1.2.0` Alignment**: Maintaining ABI compatibility between `pg_mooncake`, `pg_duckdb`, and `duckdb_mooncake` as DuckDB evolves its `TableCatalogEntry`, `TableFilterSet`, and `StorageExtension` APIs.
3. **Correctness & Fail-Fast Guards**: Enforcing runtime `pg_duckdb` version checks, LSN-consistent snapshot reads on columnstore tables, automatic `REPLICA IDENTITY FULL` propagation across partitioned table hierarchies, and explicit `0A000` errors on deprecated helpers.
4. **Dependency Security Hygiene**: Regularly auditing and upgrading Rust dependencies across all three lockfiles (`pg_mooncake`, `moonlink`, `duckdb_mooncake/moonlink_ffi`) against the RustSec Advisory Database.

---

## Historical Upstream Roadmap (`v0.2`)

The following four capabilities were outlined by Mooncake Labs for the `v0.2` architecture:

### 1. Columnstore Table for Logs / Events

Introduce an **append-only** mode for `columnstore` tables:

- Optimized for streaming ingestion and out-of-order inserts.
- Built-in time-based partitioning and retention policies.
- Targeted at observability, telemetry, and high-throughput event pipelines.

### 2. Native Columnstore Tables (Without a Backing Rowstore)

Create and write directly to a `columnstore` table without requiring a companion PostgreSQL heap table:

```sql
CREATE TABLE table_name (
    ...
) USING columnstore;
```

- Supports standard `INSERT`, `SELECT`, `UPDATE`, `DELETE`, and `COPY` directly against the columnstore access method.
- Note: Native `USING columnstore` tables were available in [`v0.1` (Delta Lake)](/docs/v0.1/columnstore-ddl/), whereas `v0.2` and `v0.3.0` use [`mooncake.create_table(dst, src)`](/docs/reference/create-columnstore/) to mirror a PostgreSQL heap table via logical replication.

### 3. Write to Existing Iceberg Tables

Create a `columnstore` mirror in PostgreSQL that writes into an existing external Apache Iceberg table managed by a REST or JDBC catalog, allowing bilateral interoperability with Spark, Trino, and Flink writers.

### 4. Query Routing & Partitioned Tables

Transparently route analytical queries across hybrid rowstore + columnstore partitioned hierarchies without requiring manual `UNION ALL` queries or explicit dual-table references.
