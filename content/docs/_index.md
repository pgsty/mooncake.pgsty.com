---
title: "Mooncake Documentation"
linkTitle: "Documentation"
description: "Unified documentation hub for the PostgreSQL real-time columnstore and Apache Iceberg v2 lakehouse suite: pg_mooncake (v0.3.0), moonlink (v0.0.1), and duckdb_mooncake (v0.0.2)."
weight: 10
icon: fa-solid fa-book
type: docs
sidebar_root_for: self
upstream_source: docs
upstream_link: https://web.archive.org/web/20251207085834/https://docs.mooncake.dev/pg/intro/
upstream_modified: true
no_list: true
cascade:
  type: docs
  upstream_source: docs
  upstream_modified: true
---

## Core Documentation

{{< cards >}}
{{< card title="Introduction & Architecture" icon="fa-solid fa-compass" badge="v0.3.0" link="/docs/intro/" >}}
Explore the Mooncake architecture: how `pg_mooncake`, `moonlink`, `duckdb_mooncake`, and `pg_duckdb 1.2.0` work together, and how `v0.2` / `v0.3` evolved from `v0.1`.
{{< /card >}}
{{< card title="Getting Started" icon="fa-solid fa-rocket" badge="PG 14–18" link="/docs/getting-started/" >}}
Install `pg_mooncake` and `pg_duckdb` via Pigsty packages or build from source, run the Hello World columnstore mirror tutorial, and review known limitations.
{{< /card >}}
{{< card title="SQL & Config Reference" icon="fa-solid fa-code" badge="API" link="/docs/reference/" >}}
Complete reference for `mooncake.create_table`, `create_snapshot`, `optimize_table`, `list_tables`, query shapes, Iceberg S3/R2 configuration, and external data lake scans.
{{< /card >}}
{{< card title="Use Cases & Patterns" icon="fa-solid fa-diagram-project" link="/docs/use-cases/" >}}
Architectural patterns for real-time operational analytics (HTAP), time-partitioned table archiving, the zero-ETL Postgres lakehouse, and OpenTelemetry log analytics.
{{< /card >}}
{{< card title="v0.1 Archive (Delta Lake)" icon="fa-solid fa-box-archive" badge="Deprecated" link="/docs/v0.1/" >}}
Complete historical reference archive for `pg_mooncake v0.1` (`USING columnstore` + Delta Lake storage), preserved for legacy deployments and Wayback URL compatibility.
{{< /card >}}
{{< card title="About, Licensing & SBOM" icon="fa-solid fa-circle-info" badge="PGSTY" link="/docs/about/" >}}
PGSTY community stewardship, `MIT` and `BSL-1.1` linking exception licensing, Wayback Machine recovery provenance, and Cargo security dependency audit reports.
{{< /card >}}
{{< /cards >}}

## Component Deep Dives

{{< cards >}}
{{< card title="System Architecture" icon="fa-solid fa-sitemap" link="/docs/intro/architecture/" >}}
Write path (`Logical WAL` -> `Moonlink`), read path (`pg_duckdb` -> `duckdb_mooncake`), and dual-format storage (in-memory Arrow + Parquet + Apache Iceberg v2).
{{< /card >}}
{{< card title="Moonlink Ingestion Engine" icon="fa-solid fa-arrows-rotate" link="/docs/intro/moonlink/" >}}
Real-time CDC streaming, Arrow write buffers, Roaring Bitmap deletion vectors, LSN snapshot barriers, and standalone `moonlink_service` REST/RPC deployment.
{{< /card >}}
{{< card title="duckdb_mooncake & DuckDB 2.0" icon="fa-solid fa-database" link="/docs/intro/duckdb-mooncake/" >}}
How `duckdb_mooncake v0.0.2` connects DuckDB 2.0 and `pg_duckdb 1.2.0` to Moonlink metadata and performs multi-file Parquet statistics pruning.
{{< /card >}}
{{< card title="Create Columnstore Mirror" icon="fa-solid fa-table-columns" link="/docs/reference/create-columnstore/" >}}
Replicate local or remote (`src_uri`) PostgreSQL heap and partitioned tables into `USING mooncake` columnstore mirrors with `CALL mooncake.create_table(...)`.
{{< /card >}}
{{< card title="Apache Iceberg & Object Storage" icon="fa-solid fa-cloud" link="/docs/reference/iceberg/" >}}
Configure `mooncake.default_bucket` for AWS S3 or Cloudflare R2, materialize snapshots with `mooncake.create_snapshot`, and query from external engines.
{{< /card >}}
{{< card title="Query External Data Lakes" icon="fa-solid fa-magnifying-glass-chart" link="/docs/reference/query-data-lake/" >}}
Query external Parquet, CSV, JSON, Apache Iceberg, Delta Lake, and HuggingFace datasets directly inside PostgreSQL and join them with heap tables.
{{< /card >}}
{{< /cards >}}
