---
title: "Get Started & Installation"
linkTitle: "Getting Started"
description: "Install pg_mooncake (v0.3.0) and pg_duckdb (1.2.0) with Pigsty packages or build from source on PostgreSQL 14–18, configure postgresql.conf, and enable the extension."
weight: 20
icon: fa-solid fa-rocket
upstream_link: https://web.archive.org/web/20260124103940/https://docs.mooncake.dev/pg/get-started/
aliases:
  - "/pg/get-started/"
  - "/get-started/"
---

This guide covers installing **`pg_mooncake` (`v0.3.0`)** (which bundles [`moonlink` (`v0.0.1`)](/docs/intro/moonlink/) and [`duckdb_mooncake` (`v0.0.2`)](/docs/intro/duckdb-mooncake/)) alongside **`pg_duckdb` (`v1.2.0`)** on **PostgreSQL 14, 15, 16, 17, and 18**.

## 1. Install Binary Packages via Pigsty (Recommended) {#pigsty}

The fastest way to install `pg_mooncake` on Linux (`el8`, `el9`, `el10`, `d12`, `d13`, `u22`, `u24`, `u26` across `x86_64` and `aarch64`) is with the [**`pig`**](https://pig.pgsty.com/) package manager maintained by [PGSTY](https://pigsty.io/). See the [Download & Availability Matrix](/download/) for direct package links.

{{< tabs >}}
{{< tab label="Global (Default)" >}}

```bash
# 1. Install the pig CLI package manager
curl -fsSL https://repo.pigsty.io/pig | bash

# 2. Configure PGDG + Pigsty PGSQL repositories
pig repo add pgsql -u

# 3. Install pg_duckdb and pg_mooncake (or pass -v 18 for a specific PG version)
pig install pg_duckdb pg_mooncake
```

{{< /tab >}}
{{< tab label="Mainland China Mirror" >}}

```bash
# 1. Install the pig CLI via the mainland China mirror
curl -fsSL https://repo.pigsty.cc/pig | bash

# 2. Configure repositories using the China CDN mirror (-r china)
pig repo add pgsql -u -r china

# 3. Install pg_duckdb and pg_mooncake
pig install pg_duckdb pg_mooncake
```

{{< /tab >}}
{{< tab label="Native APT / DNF" >}}

```bash
# Debian / Ubuntu (APT) — example for PostgreSQL 18:
sudo apt-get update
sudo apt-get install -y postgresql-18-pg-duckdb postgresql-18-pg-mooncake

# RHEL / Rocky / AlmaLinux (DNF) — example for PostgreSQL 18:
sudo dnf install -y pg_duckdb_18 pg_mooncake_18
```

{{< /tab >}}
{{< /tabs >}}

## 2. Configure `postgresql.conf` & Enable Extension {#configure}

`pg_mooncake` uses PostgreSQL logical replication to stream rowstore changes into Moonlink and uses `pg_duckdb` to load the bundled `mooncake.duckdb_extension` binary. Add the following settings to `postgresql.conf` (or via `ALTER SYSTEM`):

```ini
# Required for Moonlink logical replication
wal_level = logical
max_replication_slots = 32
max_wal_senders = 32
max_worker_processes = 16

# Preload both pg_duckdb and pg_mooncake
shared_preload_libraries = 'pg_duckdb,pg_mooncake'

# Allow pg_duckdb to load the local mooncake.duckdb_extension
duckdb.allow_community_extensions = true
duckdb.allow_unsigned_extensions = true

# Optional: override only if mooncake.duckdb_extension is outside $(pg_config --sharedir)/extension/pg_mooncake
# mooncake.extension_repository = '/usr/pgsql-18/share/extension/pg_mooncake'
```

Restart PostgreSQL (`sudo systemctl restart postgresql-18` or `pig pg restart`), then connect with `psql` and create the extension:

```sql
-- CASCADE automatically creates the required pg_duckdb (1.2.0) extension
CREATE EXTENSION IF NOT EXISTS pg_mooncake CASCADE;
```

> [!IMPORTANT] `pg_duckdb 1.2.0` Version Guard
> During `CREATE EXTENSION pg_mooncake`, the bootstrap SQL script explicitly verifies that `pg_duckdb` version `1.2.0` is installed in `pg_extension`. Attempting to install `pg_mooncake 0.3.0` against an incompatible `pg_duckdb` release (such as `1.1.x` or `1.3.x`) will fail immediately with a clear error message. Always upgrade `pg_duckdb` and `pg_mooncake` together.

## 3. Build from Source (`v0.3.0`) {#source}

To build `pg_mooncake 0.3.0`, `pg_duckdb 1.2.0`, `duckdb_mooncake v0.0.2`, and `moonlink v0.0.1` from source:

### Prerequisites {#prerequisites}

- **PostgreSQL development packages**: `postgresql-server-dev-14` through `18` (or `postgresql17-devel` / `postgresql18-devel`)
- **C/C++ build toolchain**: `cmake`, `ninja-build`, `g++` or `clang`, `libssl-dev`, `libcurl4-openssl-dev`, `liblz4-dev`, `libzstd-dev`, `protobuf-compiler` (`protoc`)
- **Rust toolchain**: Rust `1.99.0+` (`stable`) and `cargo-pgrx` **`0.19.3`**:
  ```bash
  cargo install --locked cargo-pgrx --version 0.19.3
  ```

### Clone, Verify Pins & Compile {#compile}

```bash
# 1. Clone pg_mooncake with all submodules (pg_duckdb, duckdb_mooncake, moonlink)
git clone --recurse-submodules https://github.com/pgsty/pg_mooncake.git
cd pg_mooncake
git fetch --tags --force moonlink
git fetch --tags --force duckdb_mooncake

# 2. Verify all submodule commit SHAs, tags, and cargo-pgrx 0.19.3
make check-versions

# 3. Build and install pg_duckdb 1.2.0 (with DuckDB v2.0.0)
export PGRX_PG_CONFIG_PATH=/usr/pgsql-18/bin/pg_config
make pg_duckdb PG_CONFIG="$PGRX_PG_CONFIG_PATH" PG_VERSION=pg18 JOBS=$(nproc)

# 4. Build and install pg_mooncake 0.3.0 + duckdb_mooncake v0.0.2 + moonlink v0.0.1
make install PG_CONFIG="$PGRX_PG_CONFIG_PATH" PG_VERSION=pg18 JOBS=$(nproc)
```

## 4. Docker Image (Obsolete) {#docker}

> [!WARNING]
> **Obsolete — pending updates and maintenance.** PGSTY has not yet published Docker or Kubernetes container images for `pg_mooncake 0.3.0`. The upstream command below uses the historical `mooncakelabs/pg_mooncake` image (PostgreSQL 17 with pre-0.3 `pg_mooncake`) and is retained for reference only.

```bash
# Pull and start the historical upstream container
docker pull mooncakelabs/pg_mooncake
docker run --name mooncake-demo \
  -e POSTGRES_HOST_AUTH_METHOD=trust \
  -p 5432:5432 -d \
  mooncakelabs/pg_mooncake

# Connect with psql
docker exec -it mooncake-demo psql -U postgres
```

## Next Steps {#next-steps}

{{< cards >}}
{{< card title="Hello World Tutorial" icon="fa-solid fa-terminal" link="/docs/getting-started/hello-world/" >}}
Create your first `USING mooncake` columnstore mirror table, run transactional DML, and execute vectorized joins.
{{< /card >}}
{{< card title="Known Limitations" icon="fa-solid fa-triangle-exclamation" link="/docs/getting-started/known-limitations/" >}}
Review operational requirements around primary keys, partitioned tables, `TRUNCATE`, and supported DDL operations.
{{< /card >}}
{{< /cards >}}
