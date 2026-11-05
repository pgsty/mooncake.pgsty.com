---
title: Download & Install
linkTitle: Download
description: Install pg_mooncake (with bundled moonlink and duckdb_mooncake) and pg_duckdb using the pig package manager, source builds, or native RPM/DEB packages across 16 Linux distributions and PostgreSQL 14–18.
weight: 30
icon: fa-solid fa-download
type: docs
sidebar_enabled: false
breadcrumb: false
page_width: wide
body_class: td-download-page
---

Pre-built native RPM and DEB packages for **`pg_mooncake`** (including the embedded **`moonlink`** ingestion engine and **`duckdb_mooncake`** DuckDB extension) are published across **16 Linux OS / CPU architecture targets** (`el8`, `el9`, `el10`, `d12`, `d13`, `u22`, `u24`, `u26` × `x86_64` / `aarch64`) for **PostgreSQL 14, 15, 16, 17, and 18** (80 binary packages across 5 PostgreSQL major versions).

{{< cards >}}
{{< card title="pg_mooncake" link="#pg_mooncake" icon="fa-solid fa-table-columns" badge="v0.3.0" >}}
PostgreSQL Table Access Method (`USING mooncake`) and columnstore mirror procedures (`mooncake.create_table`, `create_snapshot`, `optimize_table`, `list_tables`), built with `pgrx 0.19.3` for PostgreSQL 14–18.
{{< /card >}}
{{< card title="moonlink" link="/docs/intro/moonlink/" icon="fa-solid fa-arrows-rotate" badge="v0.0.1" >}}
Rust real-time ingestion engine embedded inside `pg_mooncake`'s background worker (and available as a standalone HTTP/RPC server), managing logical replication, Arrow write buffers, Roaring deletion vectors, and Apache Iceberg v2 snapshots.
{{< /card >}}
{{< card title="duckdb_mooncake" link="/docs/intro/duckdb-mooncake/" icon="fa-solid fa-database" badge="v0.0.2" >}}
DuckDB 2.0 storage extension bundled with `pg_mooncake` into a local extension repository (`mooncake.extension_repository`), enabling `pg_duckdb 1.2.0` to scan Moonlink tables with multi-file Parquet statistics pruning.
{{< /card >}}
{{< /cards >}}

---

## Quick Installation {#install}

### 1 · Install with PIG Package Manager (Recommended) {#pig}

We recommend installing `pg_mooncake` and its required companion extension `pg_duckdb` with [**`pig`**](https://pig.pgsty.com/) — the PostgreSQL package manager maintained by [PGSTY](https://pigsty.io/). `pig` automatically detects your Linux distribution and CPU architecture, configures the upstream PGDG and Pigsty repositories, and installs both extensions in one command.

{{< tabs >}}
{{< tab label="Global (Default)" >}}

```bash
# 1. Install the pig CLI package manager
curl -fsSL https://repo.pigsty.io/pig | bash

# 2. Configure PGDG + Pigsty PGSQL repositories and update repo cache
pig repo add pgsql -u

# 3. Install pg_duckdb and pg_mooncake (auto-detects active PG version, or pass -v 18)
pig install pg_duckdb pg_mooncake
```

{{< /tab >}}
{{< tab label="Mainland China Mirror" >}}

```bash
# 1. Install the pig CLI via the mainland China mirror
curl -fsSL https://repo.pigsty.cc/pig | bash

# 2. Configure repositories using the China CDN mirror (-r china)
pig repo add pgsql -u -r china

# 3. Install pg_duckdb and pg_mooncake (or specify PG major version with -v 18)
pig install pg_duckdb pg_mooncake
```

{{< /tab >}}
{{< tab label="Native APT (Debian / Ubuntu)" >}}

```bash
# Once the Pigsty APT repository is configured, install for your PostgreSQL major version (e.g. PG 18):
sudo apt-get update
sudo apt-get install -y \
  postgresql-18-pg-duckdb \
  postgresql-18-pg-mooncake
```

{{< /tab >}}
{{< tab label="Native DNF / YUM (EL 8 / 9 / 10)" >}}

```bash
# Once the Pigsty YUM repository is configured, install for your PostgreSQL major version (e.g. PG 18):
sudo dnf install -y \
  pg_duckdb_18 \
  pg_mooncake_18
```

{{< /tab >}}
{{< /tabs >}}

### 2 · Configure `postgresql.conf` & Enable Extension {#enable}

`pg_mooncake` requires `wal_level = logical` (for Moonlink logical replication) and preloading both `pg_duckdb` and `pg_mooncake` in `shared_preload_libraries`:

```sql
-- 1. Configure logical replication, shared_preload_libraries, and DuckDB extension loading
ALTER SYSTEM SET wal_level = 'logical';
ALTER SYSTEM SET shared_preload_libraries = 'pg_duckdb,pg_mooncake';
ALTER SYSTEM SET duckdb.allow_community_extensions = 'true';
ALTER SYSTEM SET duckdb.allow_unsigned_extensions = 'true';
```

Restart PostgreSQL (`sudo systemctl restart postgresql-18` or `pig pg restart`), then connect to your target database and enable the extension:

```sql
-- 2. Enable pg_mooncake (CASCADE automatically enables pg_duckdb 1.2.0)
CREATE EXTENSION IF NOT EXISTS pg_mooncake CASCADE;
```

### 3 · Container Images (Obsolete) {#docker}

> [!WARNING]
> **Obsolete — pending updates and maintenance.** PGSTY has not yet published Docker or Kubernetes images for `pg_mooncake 0.3.0`. The historical upstream image below (`mooncakelabs/pg_mooncake`) shipped an older pre-0.3 build and is retained for reference only.

```bash
# Historical upstream container (PostgreSQL 17 + legacy pg_mooncake)
docker run --name mooncake-demo \
  -e POSTGRES_HOST_AUTH_METHOD=trust \
  -p 5432:5432 -d \
  mooncakelabs/pg_mooncake
```

### 4 · Component Repositories & Releases {#releases}

| **Component** | **Release Tag** | **Role in Suite** | **License** | **Documentation** | **GitHub Repository & Releases** |
|:---|:---:|:---|:---:|:---|:---|
| **`pg_mooncake`** | `v0.3.0` | PostgreSQL TAM (`USING mooncake`), procedures, & bgworker | `MIT` | [Overview](/docs/intro/) | [pgsty/pg_mooncake](https://github.com/pgsty/pg_mooncake/releases) |
| **`duckdb_mooncake`** | `v0.0.2` | DuckDB 2.0 storage extension for Moonlink & Parquet scans | `MIT` | [duckdb_mooncake](/docs/intro/duckdb-mooncake/) | [pgsty/duckdb_mooncake](https://github.com/pgsty/duckdb_mooncake/releases) |
| **`moonlink`** | `v0.0.1` | Real-time CDC, Arrow buffer, deletion vectors, & Iceberg writer | `BSL-1.1` (Exception) | [Moonlink Engine](/docs/intro/moonlink/) | [pgsty/moonlink](https://github.com/pgsty/moonlink/releases) |
| **`pg_duckdb`** | `v1.2.0` | Required embedded DuckDB 2.0 execution engine for PostgreSQL | `MIT` | [Getting Started](/docs/getting-started/) | [pgext.cloud/e/pg_duckdb](https://pgext.cloud/e/pg_duckdb) |
{.wide .expand}

---

## `pg_mooncake` — Real-Time Columnstore & Iceberg Lakehouse {#pg_mooncake}

**`pg_mooncake`** (`v0.3.0`) adds real-time columnstore mirror tables (`USING mooncake`) to PostgreSQL, bundling `moonlink v0.0.1` and `duckdb_mooncake v0.0.2` alongside `pg_duckdb v1.2.0`.

| **Type** | **Name / Pattern** | **Version** | **PostgreSQL** | **Dependencies** | **Repository** | **License / Lang** |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|
| {{< bg "EXT" "PostgreSQL Extension" "blue" >}} | [`pg_mooncake`](/docs/intro/) | `0.3.0` | {{< pgver "18,17,16,15,14" "g,g,g,g,g" >}} | `pg_duckdb` (`1.2.0`) | [PGEXT #2440](https://pgext.cloud/e/pg_mooncake) | {{< bg "MIT" "License: MIT (with BSL-1.1 Exception for Moonlink)" "green" >}} |
| {{< bg "RPM" "EL 8 / 9 / 10 RPM Package" "orange" >}} | `pg_mooncake_$v` | `0.3.0` | {{< pgver "18,17,16,15,14" "g,g,g,g,g" >}} | `pg_duckdb_$v` | {{< bg "PIGSTY" "Pigsty PGSQL YUM Repository" "green" >}} | {{< bg "Rust" "Implemented in Rust (pgrx 0.19.3) & C++" "orange" >}} |
| {{< bg "DEB" "Debian & Ubuntu DEB Package" "purple" >}} | `postgresql-$v-pg-mooncake` | `0.3.0` | {{< pgver "18,17,16,15,14" "g,g,g,g,g" >}} | `postgresql-$v-pg-duckdb` | {{< bg "PIGSTY" "Pigsty PGSQL APT Repository" "green" >}} | {{< bg "Rust" "Implemented in Rust (pgrx 0.19.3) & C++" "orange" >}} |
{.packages .wide .expand}

### Availability Matrix (`pg_mooncake`) {#pg_mooncake-matrix}

| **Linux** / **PG** |                  **PG18**                   |                  **PG17**                   |                  **PG16**                   |                  **PG15**                   |                  **PG14**                   |
|:------------------:|:-------------------------------------------:|:-------------------------------------------:|:-------------------------------------------:|:-------------------------------------------:|:-------------------------------------------:|
| {{< os "el8.x86_64" >}} | {{< bg "PIGSTY 0.3.0" "pg_mooncake_18 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 0.3.0" "pg_mooncake_17 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 0.3.0" "pg_mooncake_16 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 0.3.0" "pg_mooncake_15 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 0.3.0" "pg_mooncake_14 : AVAIL 1" "green" >}} |
| {{< os "el8.aarch64" >}} | {{< bg "PIGSTY 0.3.0" "pg_mooncake_18 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 0.3.0" "pg_mooncake_17 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 0.3.0" "pg_mooncake_16 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 0.3.0" "pg_mooncake_15 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 0.3.0" "pg_mooncake_14 : AVAIL 1" "green" >}} |
| {{< os "el9.x86_64" >}} | {{< bg "PIGSTY 0.3.0" "pg_mooncake_18 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 0.3.0" "pg_mooncake_17 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 0.3.0" "pg_mooncake_16 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 0.3.0" "pg_mooncake_15 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 0.3.0" "pg_mooncake_14 : AVAIL 1" "green" >}} |
| {{< os "el9.aarch64" >}} | {{< bg "PIGSTY 0.3.0" "pg_mooncake_18 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 0.3.0" "pg_mooncake_17 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 0.3.0" "pg_mooncake_16 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 0.3.0" "pg_mooncake_15 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 0.3.0" "pg_mooncake_14 : AVAIL 1" "green" >}} |
| {{< os "el10.x86_64" >}} | {{< bg "PIGSTY 0.3.0" "pg_mooncake_18 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 0.3.0" "pg_mooncake_17 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 0.3.0" "pg_mooncake_16 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 0.3.0" "pg_mooncake_15 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 0.3.0" "pg_mooncake_14 : AVAIL 1" "green" >}} |
| {{< os "el10.aarch64" >}} | {{< bg "PIGSTY 0.3.0" "pg_mooncake_18 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 0.3.0" "pg_mooncake_17 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 0.3.0" "pg_mooncake_16 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 0.3.0" "pg_mooncake_15 : AVAIL 1" "green" >}} | {{< bg "PIGSTY 0.3.0" "pg_mooncake_14 : AVAIL 1" "green" >}} |
| {{< os "d12.x86_64" >}} | {{< bg "PIGSTY 0.3.0" "postgresql-18-pg-mooncake : AVAIL 1" "green" >}} | {{< bg "PIGSTY 0.3.0" "postgresql-17-pg-mooncake : AVAIL 1" "green" >}} | {{< bg "PIGSTY 0.3.0" "postgresql-16-pg-mooncake : AVAIL 1" "green" >}} | {{< bg "PIGSTY 0.3.0" "postgresql-15-pg-mooncake : AVAIL 1" "green" >}} | {{< bg "PIGSTY 0.3.0" "postgresql-14-pg-mooncake : AVAIL 1" "green" >}} |
| {{< os "d12.aarch64" >}} | {{< bg "PIGSTY 0.3.0" "postgresql-18-pg-mooncake : AVAIL 1" "green" >}} | {{< bg "PIGSTY 0.3.0" "postgresql-17-pg-mooncake : AVAIL 1" "green" >}} | {{< bg "PIGSTY 0.3.0" "postgresql-16-pg-mooncake : AVAIL 1" "green" >}} | {{< bg "PIGSTY 0.3.0" "postgresql-15-pg-mooncake : AVAIL 1" "green" >}} | {{< bg "PIGSTY 0.3.0" "postgresql-14-pg-mooncake : AVAIL 1" "green" >}} |
| {{< os "d13.x86_64" >}} | {{< bg "PIGSTY 0.3.0" "postgresql-18-pg-mooncake : AVAIL 1" "green" >}} | {{< bg "PIGSTY 0.3.0" "postgresql-17-pg-mooncake : AVAIL 1" "green" >}} | {{< bg "PIGSTY 0.3.0" "postgresql-16-pg-mooncake : AVAIL 1" "green" >}} | {{< bg "PIGSTY 0.3.0" "postgresql-15-pg-mooncake : AVAIL 1" "green" >}} | {{< bg "PIGSTY 0.3.0" "postgresql-14-pg-mooncake : AVAIL 1" "green" >}} |
| {{< os "d13.aarch64" >}} | {{< bg "PIGSTY 0.3.0" "postgresql-18-pg-mooncake : AVAIL 1" "green" >}} | {{< bg "PIGSTY 0.3.0" "postgresql-17-pg-mooncake : AVAIL 1" "green" >}} | {{< bg "PIGSTY 0.3.0" "postgresql-16-pg-mooncake : AVAIL 1" "green" >}} | {{< bg "PIGSTY 0.3.0" "postgresql-15-pg-mooncake : AVAIL 1" "green" >}} | {{< bg "PIGSTY 0.3.0" "postgresql-14-pg-mooncake : AVAIL 1" "green" >}} |
| {{< os "u22.x86_64" >}} | {{< bg "PIGSTY 0.3.0" "postgresql-18-pg-mooncake : AVAIL 1" "green" >}} | {{< bg "PIGSTY 0.3.0" "postgresql-17-pg-mooncake : AVAIL 1" "green" >}} | {{< bg "PIGSTY 0.3.0" "postgresql-16-pg-mooncake : AVAIL 1" "green" >}} | {{< bg "PIGSTY 0.3.0" "postgresql-15-pg-mooncake : AVAIL 1" "green" >}} | {{< bg "PIGSTY 0.3.0" "postgresql-14-pg-mooncake : AVAIL 1" "green" >}} |
| {{< os "u22.aarch64" >}} | {{< bg "PIGSTY 0.3.0" "postgresql-18-pg-mooncake : AVAIL 1" "green" >}} | {{< bg "PIGSTY 0.3.0" "postgresql-17-pg-mooncake : AVAIL 1" "green" >}} | {{< bg "PIGSTY 0.3.0" "postgresql-16-pg-mooncake : AVAIL 1" "green" >}} | {{< bg "PIGSTY 0.3.0" "postgresql-15-pg-mooncake : AVAIL 1" "green" >}} | {{< bg "PIGSTY 0.3.0" "postgresql-14-pg-mooncake : AVAIL 1" "green" >}} |
| {{< os "u24.x86_64" >}} | {{< bg "PIGSTY 0.3.0" "postgresql-18-pg-mooncake : AVAIL 1" "green" >}} | {{< bg "PIGSTY 0.3.0" "postgresql-17-pg-mooncake : AVAIL 1" "green" >}} | {{< bg "PIGSTY 0.3.0" "postgresql-16-pg-mooncake : AVAIL 1" "green" >}} | {{< bg "PIGSTY 0.3.0" "postgresql-15-pg-mooncake : AVAIL 1" "green" >}} | {{< bg "PIGSTY 0.3.0" "postgresql-14-pg-mooncake : AVAIL 1" "green" >}} |
| {{< os "u24.aarch64" >}} | {{< bg "PIGSTY 0.3.0" "postgresql-18-pg-mooncake : AVAIL 1" "green" >}} | {{< bg "PIGSTY 0.3.0" "postgresql-17-pg-mooncake : AVAIL 1" "green" >}} | {{< bg "PIGSTY 0.3.0" "postgresql-16-pg-mooncake : AVAIL 1" "green" >}} | {{< bg "PIGSTY 0.3.0" "postgresql-15-pg-mooncake : AVAIL 1" "green" >}} | {{< bg "PIGSTY 0.3.0" "postgresql-14-pg-mooncake : AVAIL 1" "green" >}} |
| {{< os "u26.x86_64" >}} | {{< bg "PIGSTY 0.3.0" "postgresql-18-pg-mooncake : AVAIL 1" "green" >}} | {{< bg "PIGSTY 0.3.0" "postgresql-17-pg-mooncake : AVAIL 1" "green" >}} | {{< bg "PIGSTY 0.3.0" "postgresql-16-pg-mooncake : AVAIL 1" "green" >}} | {{< bg "PIGSTY 0.3.0" "postgresql-15-pg-mooncake : AVAIL 1" "green" >}} | {{< bg "PIGSTY 0.3.0" "postgresql-14-pg-mooncake : AVAIL 1" "green" >}} |
| {{< os "u26.aarch64" >}} | {{< bg "PIGSTY 0.3.0" "postgresql-18-pg-mooncake : AVAIL 1" "green" >}} | {{< bg "PIGSTY 0.3.0" "postgresql-17-pg-mooncake : AVAIL 1" "green" >}} | {{< bg "PIGSTY 0.3.0" "postgresql-16-pg-mooncake : AVAIL 1" "green" >}} | {{< bg "PIGSTY 0.3.0" "postgresql-15-pg-mooncake : AVAIL 1" "green" >}} | {{< bg "PIGSTY 0.3.0" "postgresql-14-pg-mooncake : AVAIL 1" "green" >}} |
{.matrix .wide .expand}

### Package Downloads (`pg_mooncake`) {#pg_mooncake-packages}

{{< tabs group="pgmajor" >}}
{{< tab label="PG18" value="pg18" >}}

| **Package** | **Version** | **OS** | **ORG** | **SIZE** | **File URL** |
|:------------|:-----------:|:------:|:-------:|:--------:|:--------------|
| `pg_mooncake_18` | `0.3.0` | {{< os "el8.x86_64" >}} | pigsty | 19.1 MiB | [pg_mooncake_18-0.3.0-1PIGSTY.el8.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el8.x86_64/pg_mooncake_18-0.3.0-1PIGSTY.el8.x86_64.rpm) |
| `pg_mooncake_18` | `0.3.0` | {{< os "el8.aarch64" >}} | pigsty | 17.6 MiB | [pg_mooncake_18-0.3.0-1PIGSTY.el8.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el8.aarch64/pg_mooncake_18-0.3.0-1PIGSTY.el8.aarch64.rpm) |
| `pg_mooncake_18` | `0.3.0` | {{< os "el9.x86_64" >}} | pigsty | 17.8 MiB | [pg_mooncake_18-0.3.0-1PIGSTY.el9.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el9.x86_64/pg_mooncake_18-0.3.0-1PIGSTY.el9.x86_64.rpm) |
| `pg_mooncake_18` | `0.3.0` | {{< os "el9.aarch64" >}} | pigsty | 17.6 MiB | [pg_mooncake_18-0.3.0-1PIGSTY.el9.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el9.aarch64/pg_mooncake_18-0.3.0-1PIGSTY.el9.aarch64.rpm) |
| `pg_mooncake_18` | `0.3.0` | {{< os "el10.x86_64" >}} | pigsty | 17.6 MiB | [pg_mooncake_18-0.3.0-1PIGSTY.el10.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el10.x86_64/pg_mooncake_18-0.3.0-1PIGSTY.el10.x86_64.rpm) |
| `pg_mooncake_18` | `0.3.0` | {{< os "el10.aarch64" >}} | pigsty | 17.4 MiB | [pg_mooncake_18-0.3.0-1PIGSTY.el10.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el10.aarch64/pg_mooncake_18-0.3.0-1PIGSTY.el10.aarch64.rpm) |
| `postgresql-18-pg-mooncake` | `0.3.0` | {{< os "d12.x86_64" >}} | pigsty | 15.0 MiB | [postgresql-18-pg-mooncake_0.3.0-1PIGSTY~bookworm_amd64.deb](https://repo.pigsty.io/apt/pgsql/bookworm/pool/main/p/pg-mooncake/postgresql-18-pg-mooncake_0.3.0-1PIGSTY~bookworm_amd64.deb) |
| `postgresql-18-pg-mooncake` | `0.3.0` | {{< os "d12.aarch64" >}} | pigsty | 13.2 MiB | [postgresql-18-pg-mooncake_0.3.0-1PIGSTY~bookworm_arm64.deb](https://repo.pigsty.io/apt/pgsql/bookworm/pool/main/p/pg-mooncake/postgresql-18-pg-mooncake_0.3.0-1PIGSTY~bookworm_arm64.deb) |
| `postgresql-18-pg-mooncake` | `0.3.0` | {{< os "d13.x86_64" >}} | pigsty | 15.0 MiB | [postgresql-18-pg-mooncake_0.3.0-1PIGSTY~trixie_amd64.deb](https://repo.pigsty.io/apt/pgsql/trixie/pool/main/p/pg-mooncake/postgresql-18-pg-mooncake_0.3.0-1PIGSTY~trixie_amd64.deb) |
| `postgresql-18-pg-mooncake` | `0.3.0` | {{< os "d13.aarch64" >}} | pigsty | 13.2 MiB | [postgresql-18-pg-mooncake_0.3.0-1PIGSTY~trixie_arm64.deb](https://repo.pigsty.io/apt/pgsql/trixie/pool/main/p/pg-mooncake/postgresql-18-pg-mooncake_0.3.0-1PIGSTY~trixie_arm64.deb) |
| `postgresql-18-pg-mooncake` | `0.3.0` | {{< os "u22.x86_64" >}} | pigsty | 16.2 MiB | [postgresql-18-pg-mooncake_0.3.0-1PIGSTY~jammy_amd64.deb](https://repo.pigsty.io/apt/pgsql/jammy/pool/main/p/pg-mooncake/postgresql-18-pg-mooncake_0.3.0-1PIGSTY~jammy_amd64.deb) |
| `postgresql-18-pg-mooncake` | `0.3.0` | {{< os "u22.aarch64" >}} | pigsty | 15.4 MiB | [postgresql-18-pg-mooncake_0.3.0-1PIGSTY~jammy_arm64.deb](https://repo.pigsty.io/apt/pgsql/jammy/pool/main/p/pg-mooncake/postgresql-18-pg-mooncake_0.3.0-1PIGSTY~jammy_arm64.deb) |
| `postgresql-18-pg-mooncake` | `0.3.0` | {{< os "u24.x86_64" >}} | pigsty | 16.2 MiB | [postgresql-18-pg-mooncake_0.3.0-1PIGSTY~noble_amd64.deb](https://repo.pigsty.io/apt/pgsql/noble/pool/main/p/pg-mooncake/postgresql-18-pg-mooncake_0.3.0-1PIGSTY~noble_amd64.deb) |
| `postgresql-18-pg-mooncake` | `0.3.0` | {{< os "u24.aarch64" >}} | pigsty | 15.5 MiB | [postgresql-18-pg-mooncake_0.3.0-1PIGSTY~noble_arm64.deb](https://repo.pigsty.io/apt/pgsql/noble/pool/main/p/pg-mooncake/postgresql-18-pg-mooncake_0.3.0-1PIGSTY~noble_arm64.deb) |
| `postgresql-18-pg-mooncake` | `0.3.0` | {{< os "u26.x86_64" >}} | pigsty | 16.2 MiB | [postgresql-18-pg-mooncake_0.3.0-1PIGSTY~resolute_amd64.deb](https://repo.pigsty.io/apt/pgsql/resolute/pool/main/p/pg-mooncake/postgresql-18-pg-mooncake_0.3.0-1PIGSTY~resolute_amd64.deb) |
| `postgresql-18-pg-mooncake` | `0.3.0` | {{< os "u26.aarch64" >}} | pigsty | 15.5 MiB | [postgresql-18-pg-mooncake_0.3.0-1PIGSTY~resolute_arm64.deb](https://repo.pigsty.io/apt/pgsql/resolute/pool/main/p/pg-mooncake/postgresql-18-pg-mooncake_0.3.0-1PIGSTY~resolute_arm64.deb) |
{.downloads .wide .expand}

{{< /tab >}}
{{< tab label="PG17" value="pg17" >}}

| **Package** | **Version** | **OS** | **ORG** | **SIZE** | **File URL** |
|:------------|:-----------:|:------:|:-------:|:--------:|:--------------|
| `pg_mooncake_17` | `0.3.0` | {{< os "el8.x86_64" >}} | pigsty | 19.1 MiB | [pg_mooncake_17-0.3.0-1PIGSTY.el8.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el8.x86_64/pg_mooncake_17-0.3.0-1PIGSTY.el8.x86_64.rpm) |
| `pg_mooncake_17` | `0.3.0` | {{< os "el8.aarch64" >}} | pigsty | 17.6 MiB | [pg_mooncake_17-0.3.0-1PIGSTY.el8.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el8.aarch64/pg_mooncake_17-0.3.0-1PIGSTY.el8.aarch64.rpm) |
| `pg_mooncake_17` | `0.3.0` | {{< os "el9.x86_64" >}} | pigsty | 17.8 MiB | [pg_mooncake_17-0.3.0-1PIGSTY.el9.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el9.x86_64/pg_mooncake_17-0.3.0-1PIGSTY.el9.x86_64.rpm) |
| `pg_mooncake_17` | `0.3.0` | {{< os "el9.aarch64" >}} | pigsty | 17.6 MiB | [pg_mooncake_17-0.3.0-1PIGSTY.el9.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el9.aarch64/pg_mooncake_17-0.3.0-1PIGSTY.el9.aarch64.rpm) |
| `pg_mooncake_17` | `0.3.0` | {{< os "el10.x86_64" >}} | pigsty | 17.6 MiB | [pg_mooncake_17-0.3.0-1PIGSTY.el10.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el10.x86_64/pg_mooncake_17-0.3.0-1PIGSTY.el10.x86_64.rpm) |
| `pg_mooncake_17` | `0.3.0` | {{< os "el10.aarch64" >}} | pigsty | 17.3 MiB | [pg_mooncake_17-0.3.0-1PIGSTY.el10.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el10.aarch64/pg_mooncake_17-0.3.0-1PIGSTY.el10.aarch64.rpm) |
| `postgresql-17-pg-mooncake` | `0.3.0` | {{< os "d12.x86_64" >}} | pigsty | 15.0 MiB | [postgresql-17-pg-mooncake_0.3.0-1PIGSTY~bookworm_amd64.deb](https://repo.pigsty.io/apt/pgsql/bookworm/pool/main/p/pg-mooncake/postgresql-17-pg-mooncake_0.3.0-1PIGSTY~bookworm_amd64.deb) |
| `postgresql-17-pg-mooncake` | `0.3.0` | {{< os "d12.aarch64" >}} | pigsty | 13.2 MiB | [postgresql-17-pg-mooncake_0.3.0-1PIGSTY~bookworm_arm64.deb](https://repo.pigsty.io/apt/pgsql/bookworm/pool/main/p/pg-mooncake/postgresql-17-pg-mooncake_0.3.0-1PIGSTY~bookworm_arm64.deb) |
| `postgresql-17-pg-mooncake` | `0.3.0` | {{< os "d13.x86_64" >}} | pigsty | 15.0 MiB | [postgresql-17-pg-mooncake_0.3.0-1PIGSTY~trixie_amd64.deb](https://repo.pigsty.io/apt/pgsql/trixie/pool/main/p/pg-mooncake/postgresql-17-pg-mooncake_0.3.0-1PIGSTY~trixie_amd64.deb) |
| `postgresql-17-pg-mooncake` | `0.3.0` | {{< os "d13.aarch64" >}} | pigsty | 13.2 MiB | [postgresql-17-pg-mooncake_0.3.0-1PIGSTY~trixie_arm64.deb](https://repo.pigsty.io/apt/pgsql/trixie/pool/main/p/pg-mooncake/postgresql-17-pg-mooncake_0.3.0-1PIGSTY~trixie_arm64.deb) |
| `postgresql-17-pg-mooncake` | `0.3.0` | {{< os "u22.x86_64" >}} | pigsty | 16.2 MiB | [postgresql-17-pg-mooncake_0.3.0-1PIGSTY~jammy_amd64.deb](https://repo.pigsty.io/apt/pgsql/jammy/pool/main/p/pg-mooncake/postgresql-17-pg-mooncake_0.3.0-1PIGSTY~jammy_amd64.deb) |
| `postgresql-17-pg-mooncake` | `0.3.0` | {{< os "u22.aarch64" >}} | pigsty | 15.4 MiB | [postgresql-17-pg-mooncake_0.3.0-1PIGSTY~jammy_arm64.deb](https://repo.pigsty.io/apt/pgsql/jammy/pool/main/p/pg-mooncake/postgresql-17-pg-mooncake_0.3.0-1PIGSTY~jammy_arm64.deb) |
| `postgresql-17-pg-mooncake` | `0.3.0` | {{< os "u24.x86_64" >}} | pigsty | 16.2 MiB | [postgresql-17-pg-mooncake_0.3.0-1PIGSTY~noble_amd64.deb](https://repo.pigsty.io/apt/pgsql/noble/pool/main/p/pg-mooncake/postgresql-17-pg-mooncake_0.3.0-1PIGSTY~noble_amd64.deb) |
| `postgresql-17-pg-mooncake` | `0.3.0` | {{< os "u24.aarch64" >}} | pigsty | 15.4 MiB | [postgresql-17-pg-mooncake_0.3.0-1PIGSTY~noble_arm64.deb](https://repo.pigsty.io/apt/pgsql/noble/pool/main/p/pg-mooncake/postgresql-17-pg-mooncake_0.3.0-1PIGSTY~noble_arm64.deb) |
| `postgresql-17-pg-mooncake` | `0.3.0` | {{< os "u26.x86_64" >}} | pigsty | 16.2 MiB | [postgresql-17-pg-mooncake_0.3.0-1PIGSTY~resolute_amd64.deb](https://repo.pigsty.io/apt/pgsql/resolute/pool/main/p/pg-mooncake/postgresql-17-pg-mooncake_0.3.0-1PIGSTY~resolute_amd64.deb) |
| `postgresql-17-pg-mooncake` | `0.3.0` | {{< os "u26.aarch64" >}} | pigsty | 15.5 MiB | [postgresql-17-pg-mooncake_0.3.0-1PIGSTY~resolute_arm64.deb](https://repo.pigsty.io/apt/pgsql/resolute/pool/main/p/pg-mooncake/postgresql-17-pg-mooncake_0.3.0-1PIGSTY~resolute_arm64.deb) |
{.downloads .wide .expand}

{{< /tab >}}
{{< tab label="PG16" value="pg16" >}}

| **Package** | **Version** | **OS** | **ORG** | **SIZE** | **File URL** |
|:------------|:-----------:|:------:|:-------:|:--------:|:--------------|
| `pg_mooncake_16` | `0.3.0` | {{< os "el8.x86_64" >}} | pigsty | 19.1 MiB | [pg_mooncake_16-0.3.0-1PIGSTY.el8.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el8.x86_64/pg_mooncake_16-0.3.0-1PIGSTY.el8.x86_64.rpm) |
| `pg_mooncake_16` | `0.3.0` | {{< os "el8.aarch64" >}} | pigsty | 17.6 MiB | [pg_mooncake_16-0.3.0-1PIGSTY.el8.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el8.aarch64/pg_mooncake_16-0.3.0-1PIGSTY.el8.aarch64.rpm) |
| `pg_mooncake_16` | `0.3.0` | {{< os "el9.x86_64" >}} | pigsty | 17.8 MiB | [pg_mooncake_16-0.3.0-1PIGSTY.el9.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el9.x86_64/pg_mooncake_16-0.3.0-1PIGSTY.el9.x86_64.rpm) |
| `pg_mooncake_16` | `0.3.0` | {{< os "el9.aarch64" >}} | pigsty | 17.6 MiB | [pg_mooncake_16-0.3.0-1PIGSTY.el9.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el9.aarch64/pg_mooncake_16-0.3.0-1PIGSTY.el9.aarch64.rpm) |
| `pg_mooncake_16` | `0.3.0` | {{< os "el10.x86_64" >}} | pigsty | 17.6 MiB | [pg_mooncake_16-0.3.0-1PIGSTY.el10.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el10.x86_64/pg_mooncake_16-0.3.0-1PIGSTY.el10.x86_64.rpm) |
| `pg_mooncake_16` | `0.3.0` | {{< os "el10.aarch64" >}} | pigsty | 17.3 MiB | [pg_mooncake_16-0.3.0-1PIGSTY.el10.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el10.aarch64/pg_mooncake_16-0.3.0-1PIGSTY.el10.aarch64.rpm) |
| `postgresql-16-pg-mooncake` | `0.3.0` | {{< os "d12.x86_64" >}} | pigsty | 15.0 MiB | [postgresql-16-pg-mooncake_0.3.0-1PIGSTY~bookworm_amd64.deb](https://repo.pigsty.io/apt/pgsql/bookworm/pool/main/p/pg-mooncake/postgresql-16-pg-mooncake_0.3.0-1PIGSTY~bookworm_amd64.deb) |
| `postgresql-16-pg-mooncake` | `0.3.0` | {{< os "d12.aarch64" >}} | pigsty | 13.2 MiB | [postgresql-16-pg-mooncake_0.3.0-1PIGSTY~bookworm_arm64.deb](https://repo.pigsty.io/apt/pgsql/bookworm/pool/main/p/pg-mooncake/postgresql-16-pg-mooncake_0.3.0-1PIGSTY~bookworm_arm64.deb) |
| `postgresql-16-pg-mooncake` | `0.3.0` | {{< os "d13.x86_64" >}} | pigsty | 15.0 MiB | [postgresql-16-pg-mooncake_0.3.0-1PIGSTY~trixie_amd64.deb](https://repo.pigsty.io/apt/pgsql/trixie/pool/main/p/pg-mooncake/postgresql-16-pg-mooncake_0.3.0-1PIGSTY~trixie_amd64.deb) |
| `postgresql-16-pg-mooncake` | `0.3.0` | {{< os "d13.aarch64" >}} | pigsty | 13.2 MiB | [postgresql-16-pg-mooncake_0.3.0-1PIGSTY~trixie_arm64.deb](https://repo.pigsty.io/apt/pgsql/trixie/pool/main/p/pg-mooncake/postgresql-16-pg-mooncake_0.3.0-1PIGSTY~trixie_arm64.deb) |
| `postgresql-16-pg-mooncake` | `0.3.0` | {{< os "u22.x86_64" >}} | pigsty | 16.2 MiB | [postgresql-16-pg-mooncake_0.3.0-1PIGSTY~jammy_amd64.deb](https://repo.pigsty.io/apt/pgsql/jammy/pool/main/p/pg-mooncake/postgresql-16-pg-mooncake_0.3.0-1PIGSTY~jammy_amd64.deb) |
| `postgresql-16-pg-mooncake` | `0.3.0` | {{< os "u22.aarch64" >}} | pigsty | 15.5 MiB | [postgresql-16-pg-mooncake_0.3.0-1PIGSTY~jammy_arm64.deb](https://repo.pigsty.io/apt/pgsql/jammy/pool/main/p/pg-mooncake/postgresql-16-pg-mooncake_0.3.0-1PIGSTY~jammy_arm64.deb) |
| `postgresql-16-pg-mooncake` | `0.3.0` | {{< os "u24.x86_64" >}} | pigsty | 16.2 MiB | [postgresql-16-pg-mooncake_0.3.0-1PIGSTY~noble_amd64.deb](https://repo.pigsty.io/apt/pgsql/noble/pool/main/p/pg-mooncake/postgresql-16-pg-mooncake_0.3.0-1PIGSTY~noble_amd64.deb) |
| `postgresql-16-pg-mooncake` | `0.3.0` | {{< os "u24.aarch64" >}} | pigsty | 15.4 MiB | [postgresql-16-pg-mooncake_0.3.0-1PIGSTY~noble_arm64.deb](https://repo.pigsty.io/apt/pgsql/noble/pool/main/p/pg-mooncake/postgresql-16-pg-mooncake_0.3.0-1PIGSTY~noble_arm64.deb) |
| `postgresql-16-pg-mooncake` | `0.3.0` | {{< os "u26.x86_64" >}} | pigsty | 16.2 MiB | [postgresql-16-pg-mooncake_0.3.0-1PIGSTY~resolute_amd64.deb](https://repo.pigsty.io/apt/pgsql/resolute/pool/main/p/pg-mooncake/postgresql-16-pg-mooncake_0.3.0-1PIGSTY~resolute_amd64.deb) |
| `postgresql-16-pg-mooncake` | `0.3.0` | {{< os "u26.aarch64" >}} | pigsty | 15.5 MiB | [postgresql-16-pg-mooncake_0.3.0-1PIGSTY~resolute_arm64.deb](https://repo.pigsty.io/apt/pgsql/resolute/pool/main/p/pg-mooncake/postgresql-16-pg-mooncake_0.3.0-1PIGSTY~resolute_arm64.deb) |
{.downloads .wide .expand}

{{< /tab >}}
{{< tab label="PG15" value="pg15" >}}

| **Package** | **Version** | **OS** | **ORG** | **SIZE** | **File URL** |
|:------------|:-----------:|:------:|:-------:|:--------:|:--------------|
| `pg_mooncake_15` | `0.3.0` | {{< os "el8.x86_64" >}} | pigsty | 19.1 MiB | [pg_mooncake_15-0.3.0-1PIGSTY.el8.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el8.x86_64/pg_mooncake_15-0.3.0-1PIGSTY.el8.x86_64.rpm) |
| `pg_mooncake_15` | `0.3.0` | {{< os "el8.aarch64" >}} | pigsty | 17.5 MiB | [pg_mooncake_15-0.3.0-1PIGSTY.el8.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el8.aarch64/pg_mooncake_15-0.3.0-1PIGSTY.el8.aarch64.rpm) |
| `pg_mooncake_15` | `0.3.0` | {{< os "el9.x86_64" >}} | pigsty | 17.8 MiB | [pg_mooncake_15-0.3.0-1PIGSTY.el9.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el9.x86_64/pg_mooncake_15-0.3.0-1PIGSTY.el9.x86_64.rpm) |
| `pg_mooncake_15` | `0.3.0` | {{< os "el9.aarch64" >}} | pigsty | 17.6 MiB | [pg_mooncake_15-0.3.0-1PIGSTY.el9.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el9.aarch64/pg_mooncake_15-0.3.0-1PIGSTY.el9.aarch64.rpm) |
| `pg_mooncake_15` | `0.3.0` | {{< os "el10.x86_64" >}} | pigsty | 17.6 MiB | [pg_mooncake_15-0.3.0-1PIGSTY.el10.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el10.x86_64/pg_mooncake_15-0.3.0-1PIGSTY.el10.x86_64.rpm) |
| `pg_mooncake_15` | `0.3.0` | {{< os "el10.aarch64" >}} | pigsty | 17.3 MiB | [pg_mooncake_15-0.3.0-1PIGSTY.el10.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el10.aarch64/pg_mooncake_15-0.3.0-1PIGSTY.el10.aarch64.rpm) |
| `postgresql-15-pg-mooncake` | `0.3.0` | {{< os "d12.x86_64" >}} | pigsty | 15.0 MiB | [postgresql-15-pg-mooncake_0.3.0-1PIGSTY~bookworm_amd64.deb](https://repo.pigsty.io/apt/pgsql/bookworm/pool/main/p/pg-mooncake/postgresql-15-pg-mooncake_0.3.0-1PIGSTY~bookworm_amd64.deb) |
| `postgresql-15-pg-mooncake` | `0.3.0` | {{< os "d12.aarch64" >}} | pigsty | 13.2 MiB | [postgresql-15-pg-mooncake_0.3.0-1PIGSTY~bookworm_arm64.deb](https://repo.pigsty.io/apt/pgsql/bookworm/pool/main/p/pg-mooncake/postgresql-15-pg-mooncake_0.3.0-1PIGSTY~bookworm_arm64.deb) |
| `postgresql-15-pg-mooncake` | `0.3.0` | {{< os "d13.x86_64" >}} | pigsty | 15.0 MiB | [postgresql-15-pg-mooncake_0.3.0-1PIGSTY~trixie_amd64.deb](https://repo.pigsty.io/apt/pgsql/trixie/pool/main/p/pg-mooncake/postgresql-15-pg-mooncake_0.3.0-1PIGSTY~trixie_amd64.deb) |
| `postgresql-15-pg-mooncake` | `0.3.0` | {{< os "d13.aarch64" >}} | pigsty | 13.2 MiB | [postgresql-15-pg-mooncake_0.3.0-1PIGSTY~trixie_arm64.deb](https://repo.pigsty.io/apt/pgsql/trixie/pool/main/p/pg-mooncake/postgresql-15-pg-mooncake_0.3.0-1PIGSTY~trixie_arm64.deb) |
| `postgresql-15-pg-mooncake` | `0.3.0` | {{< os "u22.x86_64" >}} | pigsty | 16.2 MiB | [postgresql-15-pg-mooncake_0.3.0-1PIGSTY~jammy_amd64.deb](https://repo.pigsty.io/apt/pgsql/jammy/pool/main/p/pg-mooncake/postgresql-15-pg-mooncake_0.3.0-1PIGSTY~jammy_amd64.deb) |
| `postgresql-15-pg-mooncake` | `0.3.0` | {{< os "u22.aarch64" >}} | pigsty | 15.4 MiB | [postgresql-15-pg-mooncake_0.3.0-1PIGSTY~jammy_arm64.deb](https://repo.pigsty.io/apt/pgsql/jammy/pool/main/p/pg-mooncake/postgresql-15-pg-mooncake_0.3.0-1PIGSTY~jammy_arm64.deb) |
| `postgresql-15-pg-mooncake` | `0.3.0` | {{< os "u24.x86_64" >}} | pigsty | 16.2 MiB | [postgresql-15-pg-mooncake_0.3.0-1PIGSTY~noble_amd64.deb](https://repo.pigsty.io/apt/pgsql/noble/pool/main/p/pg-mooncake/postgresql-15-pg-mooncake_0.3.0-1PIGSTY~noble_amd64.deb) |
| `postgresql-15-pg-mooncake` | `0.3.0` | {{< os "u24.aarch64" >}} | pigsty | 15.4 MiB | [postgresql-15-pg-mooncake_0.3.0-1PIGSTY~noble_arm64.deb](https://repo.pigsty.io/apt/pgsql/noble/pool/main/p/pg-mooncake/postgresql-15-pg-mooncake_0.3.0-1PIGSTY~noble_arm64.deb) |
| `postgresql-15-pg-mooncake` | `0.3.0` | {{< os "u26.x86_64" >}} | pigsty | 16.2 MiB | [postgresql-15-pg-mooncake_0.3.0-1PIGSTY~resolute_amd64.deb](https://repo.pigsty.io/apt/pgsql/resolute/pool/main/p/pg-mooncake/postgresql-15-pg-mooncake_0.3.0-1PIGSTY~resolute_amd64.deb) |
| `postgresql-15-pg-mooncake` | `0.3.0` | {{< os "u26.aarch64" >}} | pigsty | 15.5 MiB | [postgresql-15-pg-mooncake_0.3.0-1PIGSTY~resolute_arm64.deb](https://repo.pigsty.io/apt/pgsql/resolute/pool/main/p/pg-mooncake/postgresql-15-pg-mooncake_0.3.0-1PIGSTY~resolute_arm64.deb) |
{.downloads .wide .expand}

{{< /tab >}}
{{< tab label="PG14" value="pg14" >}}

| **Package** | **Version** | **OS** | **ORG** | **SIZE** | **File URL** |
|:------------|:-----------:|:------:|:-------:|:--------:|:--------------|
| `pg_mooncake_14` | `0.3.0` | {{< os "el8.x86_64" >}} | pigsty | 19.1 MiB | [pg_mooncake_14-0.3.0-1PIGSTY.el8.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el8.x86_64/pg_mooncake_14-0.3.0-1PIGSTY.el8.x86_64.rpm) |
| `pg_mooncake_14` | `0.3.0` | {{< os "el8.aarch64" >}} | pigsty | 17.5 MiB | [pg_mooncake_14-0.3.0-1PIGSTY.el8.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el8.aarch64/pg_mooncake_14-0.3.0-1PIGSTY.el8.aarch64.rpm) |
| `pg_mooncake_14` | `0.3.0` | {{< os "el9.x86_64" >}} | pigsty | 17.8 MiB | [pg_mooncake_14-0.3.0-1PIGSTY.el9.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el9.x86_64/pg_mooncake_14-0.3.0-1PIGSTY.el9.x86_64.rpm) |
| `pg_mooncake_14` | `0.3.0` | {{< os "el9.aarch64" >}} | pigsty | 17.6 MiB | [pg_mooncake_14-0.3.0-1PIGSTY.el9.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el9.aarch64/pg_mooncake_14-0.3.0-1PIGSTY.el9.aarch64.rpm) |
| `pg_mooncake_14` | `0.3.0` | {{< os "el10.x86_64" >}} | pigsty | 17.6 MiB | [pg_mooncake_14-0.3.0-1PIGSTY.el10.x86_64.rpm](https://repo.pigsty.io/yum/pgsql/el10.x86_64/pg_mooncake_14-0.3.0-1PIGSTY.el10.x86_64.rpm) |
| `pg_mooncake_14` | `0.3.0` | {{< os "el10.aarch64" >}} | pigsty | 17.3 MiB | [pg_mooncake_14-0.3.0-1PIGSTY.el10.aarch64.rpm](https://repo.pigsty.io/yum/pgsql/el10.aarch64/pg_mooncake_14-0.3.0-1PIGSTY.el10.aarch64.rpm) |
| `postgresql-14-pg-mooncake` | `0.3.0` | {{< os "d12.x86_64" >}} | pigsty | 15.0 MiB | [postgresql-14-pg-mooncake_0.3.0-1PIGSTY~bookworm_amd64.deb](https://repo.pigsty.io/apt/pgsql/bookworm/pool/main/p/pg-mooncake/postgresql-14-pg-mooncake_0.3.0-1PIGSTY~bookworm_amd64.deb) |
| `postgresql-14-pg-mooncake` | `0.3.0` | {{< os "d12.aarch64" >}} | pigsty | 13.2 MiB | [postgresql-14-pg-mooncake_0.3.0-1PIGSTY~bookworm_arm64.deb](https://repo.pigsty.io/apt/pgsql/bookworm/pool/main/p/pg-mooncake/postgresql-14-pg-mooncake_0.3.0-1PIGSTY~bookworm_arm64.deb) |
| `postgresql-14-pg-mooncake` | `0.3.0` | {{< os "d13.x86_64" >}} | pigsty | 15.0 MiB | [postgresql-14-pg-mooncake_0.3.0-1PIGSTY~trixie_amd64.deb](https://repo.pigsty.io/apt/pgsql/trixie/pool/main/p/pg-mooncake/postgresql-14-pg-mooncake_0.3.0-1PIGSTY~trixie_amd64.deb) |
| `postgresql-14-pg-mooncake` | `0.3.0` | {{< os "d13.aarch64" >}} | pigsty | 13.2 MiB | [postgresql-14-pg-mooncake_0.3.0-1PIGSTY~trixie_arm64.deb](https://repo.pigsty.io/apt/pgsql/trixie/pool/main/p/pg-mooncake/postgresql-14-pg-mooncake_0.3.0-1PIGSTY~trixie_arm64.deb) |
| `postgresql-14-pg-mooncake` | `0.3.0` | {{< os "u22.x86_64" >}} | pigsty | 16.2 MiB | [postgresql-14-pg-mooncake_0.3.0-1PIGSTY~jammy_amd64.deb](https://repo.pigsty.io/apt/pgsql/jammy/pool/main/p/pg-mooncake/postgresql-14-pg-mooncake_0.3.0-1PIGSTY~jammy_amd64.deb) |
| `postgresql-14-pg-mooncake` | `0.3.0` | {{< os "u22.aarch64" >}} | pigsty | 15.4 MiB | [postgresql-14-pg-mooncake_0.3.0-1PIGSTY~jammy_arm64.deb](https://repo.pigsty.io/apt/pgsql/jammy/pool/main/p/pg-mooncake/postgresql-14-pg-mooncake_0.3.0-1PIGSTY~jammy_arm64.deb) |
| `postgresql-14-pg-mooncake` | `0.3.0` | {{< os "u24.x86_64" >}} | pigsty | 16.2 MiB | [postgresql-14-pg-mooncake_0.3.0-1PIGSTY~noble_amd64.deb](https://repo.pigsty.io/apt/pgsql/noble/pool/main/p/pg-mooncake/postgresql-14-pg-mooncake_0.3.0-1PIGSTY~noble_amd64.deb) |
| `postgresql-14-pg-mooncake` | `0.3.0` | {{< os "u24.aarch64" >}} | pigsty | 15.4 MiB | [postgresql-14-pg-mooncake_0.3.0-1PIGSTY~noble_arm64.deb](https://repo.pigsty.io/apt/pgsql/noble/pool/main/p/pg-mooncake/postgresql-14-pg-mooncake_0.3.0-1PIGSTY~noble_arm64.deb) |
| `postgresql-14-pg-mooncake` | `0.3.0` | {{< os "u26.x86_64" >}} | pigsty | 16.2 MiB | [postgresql-14-pg-mooncake_0.3.0-1PIGSTY~resolute_amd64.deb](https://repo.pigsty.io/apt/pgsql/resolute/pool/main/p/pg-mooncake/postgresql-14-pg-mooncake_0.3.0-1PIGSTY~resolute_amd64.deb) |
| `postgresql-14-pg-mooncake` | `0.3.0` | {{< os "u26.aarch64" >}} | pigsty | 15.5 MiB | [postgresql-14-pg-mooncake_0.3.0-1PIGSTY~resolute_arm64.deb](https://repo.pigsty.io/apt/pgsql/resolute/pool/main/p/pg-mooncake/postgresql-14-pg-mooncake_0.3.0-1PIGSTY~resolute_arm64.deb) |
{.downloads .wide .expand}

{{< /tab >}}{{< /tabs >}}

---

## Verification & Build Repositories {#source}

All RPM and DEB packages in the Pigsty PGSQL repository are GPG-signed and verified automatically by `dnf` / `apt` once configured via `pig repo add pgsql`. Every package is built transparently from open-source build specs:

| **Repository** | **Description** |
|:---|:---|
| [pgsty/pig](https://github.com/pgsty/pig) | The `pig` CLI package manager for PostgreSQL and 600+ extensions |
| [pgsty/rpm](https://github.com/pgsty/rpm) | RPM build specifications for EL 8 / 9 / 10 (`x86_64` & `aarch64`) |
| [pgsty/deb](https://github.com/pgsty/deb) | DEB build specifications for Debian 12 / 13 & Ubuntu 22.04 / 24.04 / 26.04 (`x86_64` & `aarch64`) |
| [pgext.cloud](https://pgext.cloud/e/pg_mooncake) | Full PostgreSQL extension catalog, availability matrix, and repository mirrors |
{.wide .expand}
