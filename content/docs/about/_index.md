---
title: "About"
linkTitle: "About"
description: "Project stewardship, historical roadmap, licensing, upstream attribution, trademark policy, and SBOM for the PGSTY Mooncake ecosystem."
weight: 60
icon: "fa-solid fa-circle-info"
upstream_link: ""
cascade:
  upstream_link: ""
aliases:
  - /about/
---

**`mooncake.pgsty.com`** is the companion documentation and engineering site for the [**PGSTY**](https://github.com/pgsty) forks of the **Mooncake** real-time analytics ecosystem for PostgreSQL and DuckDB:

| Repository | Current Tag | License | Upstream Origin | Description |
|:---|:---|:---|:---|:---|
| [`pgsty/pg_mooncake`](https://github.com/pgsty/pg_mooncake) | [`v0.3.0`](https://github.com/pgsty/pg_mooncake/releases/tag/v0.3.0) | `MIT` | [`Mooncake-Labs/pg_mooncake`](https://github.com/Mooncake-Labs/pg_mooncake) | Columnstore table extension for PostgreSQL (`pgrx 0.19.3`, `pg_duckdb 1.2.0`). |
| [`pgsty/duckdb_mooncake`](https://github.com/pgsty/duckdb_mooncake) | [`v0.0.2`](https://github.com/pgsty/duckdb_mooncake/releases/tag/v0.0.2) | `MIT` | [`Mooncake-Labs/duckdb_mooncake`](https://github.com/Mooncake-Labs/duckdb_mooncake) | DuckDB `2.0.0` storage extension attaching to Moonlink real-time Iceberg tables. |
| [`pgsty/moonlink`](https://github.com/pgsty/moonlink) | [`v0.0.1`](https://github.com/pgsty/moonlink/releases/tag/v0.0.1) | `BSL-1.1` + Exception (`MIT` client crates) | [`Mooncake-Labs/moonlink`](https://github.com/Mooncake-Labs/moonlink) | Rust engine ingesting real-time streaming updates and CDC into Apache Iceberg and Parquet. |
{.wide .expand}

---

## Sections

{{< cards >}}
{{< card link="/docs/about/roadmap/" title="Roadmap" icon="fa-solid fa-road" >}}
Historical upstream `v0.2` feature roadmap and current PGSTY maintenance focus (`v0.3.0+`).
{{< /card >}}
{{< card link="/docs/about/license/" title="License" icon="fa-solid fa-scale-balanced" >}}
`MIT`, `BSL-1.1` with the `PG_MOONCAKE LINKING & DISTRIBUTION EXCEPTION`, and `CC-BY-4.0` documentation terms.
{{< /card >}}
{{< card link="/docs/about/attribution/" title="Attribution" icon="fa-solid fa-users" >}}
Mooncake Labs origins, Wayback Machine documentation recovery provenance, and repository lineage.
{{< /card >}}
{{< card link="/docs/about/trademark/" title="Trademark Policy" icon="fa-solid fa-registered" >}}
Trademark acknowledgments and independence statement for the PGSTY distribution.
{{< /card >}}
{{< card link="/docs/about/sbom/" title="SBOM & Security Audit" icon="fa-solid fa-boxes-stacked" >}}
Submodule pin matrix (`versions.json`) and the 2026-11-05 Cargo RustSec dependency security audit.
{{< /card >}}
{{< /cards >}}
