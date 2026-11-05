---
title: "SBOM & Security Audit"
linkTitle: "SBOM & Audit"
description: "Software Bill of Materials (versions.json), submodule pin matrix, and the 2026-11-05 Cargo RustSec dependency audit for pg_mooncake 0.3.0."
weight: 50
icon: "fa-solid fa-boxes-stacked"
---

This page documents the exact submodule pin matrix (`versions.json`) and the dependency security audit performed for **`pg_mooncake v0.3.0`**, **`duckdb_mooncake v0.0.2`**, and **`moonlink v0.0.1`**.

---

## Component & Submodule Pin Matrix (`versions.json`)

`pgsty/pg_mooncake` records its exact submodule and upstream dependency pins in [`versions.json`](https://github.com/pgsty/pg_mooncake/blob/main/versions.json):

| Component | Path | Repository | Tag / Branch | Commit SHA | License |
|:---|:---|:---|:---|:---|:---|
| **`pg_mooncake`** | `/` | [`pgsty/pg_mooncake`](https://github.com/pgsty/pg_mooncake) | `v0.3.0` | `1a9cbfd65be9a6486d020120acb49ef0c6800d68` | `MIT` |
| **`duckdb_mooncake`** | `duckdb_mooncake` | [`pgsty/duckdb_mooncake`](https://github.com/pgsty/duckdb_mooncake) | `v0.0.2` | `49765a369ad88986916ce53c969ed2ce4ba66fac` | `MIT` |
| **`duckdb`** (nested) | `duckdb_mooncake/duckdb` | [`duckdb/duckdb`](https://github.com/duckdb/duckdb) | `v2.0.0` | `d54cbbe3df17e8e5ce68312f483b4155836112aa` | `MIT` |
| **`moonlink`** | `moonlink` (`duckdb_mooncake/moonlink`) | [`pgsty/moonlink`](https://github.com/pgsty/moonlink) | `v0.0.1` | `b298ef7444890e3c8af5544e350232518bcfd8e5` | `BSL-1.1` + Exception (`MIT` client crates) |
| **`pg_duckdb`** | `pg_duckdb` | [`pgsty/pg_duckdb`](https://github.com/pgsty/pg_duckdb) | `v1.2.0` | `8756099e267c47f0b86c24de4cf995327f1f4279` | `MIT` |
| **`rust-postgres`** | `rust-postgres` | [`sfackler/rust-postgres`](https://github.com/sfackler/rust-postgres) | `master` | `14c8e599f5551a8caa96ff5023685a6f537a1455` | `Apache-2.0 OR MIT` |
{.wide .expand}

---

## Core Rust Toolchain & Framework Pins

| Dependency | Version | Role |
|:---|:---|:---|
| **`pgrx`** / **`cargo-pgrx`** | `0.19.3` | PostgreSQL extension framework for Rust (PostgreSQL 14–18). |
| **`iceberg`** | `0.6.0` | Apache Iceberg table metadata and catalog client in `moonlink`. |
| **`arrow`** / **`parquet`** | `55.2.0` | Columnar memory format and Parquet writer in `moonlink`. |
| **`datafusion`** | `48.0.1` | Expression evaluation and pruning in `moonlink`. |
| **`opendal`** | `0.53.1` | Unified object storage abstraction (`fs`, `s3`, `gcs`, `azblob`). |
| **`tonic`** / **`prost`** | `0.14.5` / `0.14.3` | gRPC / IPC protocol serialization between `pg_mooncake` and `moonlink`. |
| **`tokio`** | `1.53.0` | Async runtime for background ingestion and object store I/O. |

---

## 2026-11-05 Cargo Dependency Security Audit

All three Cargo workspaces were audited using `cargo-audit 0.22.2` against the RustSec Advisory Database (commit `965bf9ad083b58e6340d65829d85217b18be9290`, 927 advisories loaded).

### Before vs. After Remediation Summary

| Lockfile | Before Audit | After Remediation | Reduction |
|:---|:---|:---|:---|
| `pg_mooncake/Cargo.lock` | 33 vulnerabilities, 1 unsound, 19 warnings | **6 vulnerabilities, 0 unsound**, 15 warnings | **-27 vulnerabilities (-82%), -100% unsound** |
| `moonlink/Cargo.lock` | 46 vulnerabilities, 1 unsound, 28 warnings | **15 vulnerabilities, 0 unsound**, 24 warnings | **-31 vulnerabilities (-67%), -100% unsound** |
| `duckdb_mooncake/moonlink_ffi/Cargo.lock` | 1 vulnerability, 0 unsound, 0 warnings | **0 vulnerabilities, 0 unsound, 0 warnings** | **-100% (Clean)** |
{.wide .expand}

### Resolved Vulnerabilities

- **Direct / Major Upgrades**:
  - `tonic 0.12 -> 0.14.5`, `prost 0.13 -> 0.14.3` (resolved `RUSTSEC-2026-0001` DoS via `rkyv` OOM and `RUSTSEC-2024-0436` `paste` unmaintained in `duckdb_mooncake`).
  - `bincode 1.3.3 -> 2.1.0` (`serde` compatibility path, resolved `RUSTSEC-2025-0141`).
  - `opentelemetry 0.27 -> 0.31.0`, `opentelemetry-otlp 0.27 -> 0.31.1`, `tracing-opentelemetry 0.28 -> 0.32.1`.
  - `reqwest 0.12.20 -> 0.12.28`, `tokio-tar` replaced via `testcontainers 0.23.3 -> 0.27.2` (resolved `RUSTSEC-2025-0065` PAX header parsing vulnerability).
- **Transitive Security Upgrades**:
  - `bytes 1.10.1 -> 1.11.1` (`RUSTSEC-2026-0007`: integer overflow in `BytesMut::reserve`).
  - `quinn-proto 0.11.12 -> 0.11.14` (`RUSTSEC-2026-0037`: DoS in Quinn endpoints).
  - `rustls 0.23.28 -> 0.23.37` and `rustls-webpki 0.103.3 -> 0.103.12` (`RUSTSEC-2026-0049`, `RUSTSEC-2026-0098`, `RUSTSEC-2026-0099`: CRL distribution point and wildcard name constraint validation fixes).
  - `aws-lc-rs 1.13.1 -> 1.16.3` and `aws-lc-sys 0.29.0 -> 0.39.1` (7 PKCS7 / AES-CCM / X.509 timing and logic advisories).
  - `lz4_flex 0.11.4 -> 0.11.6` (`RUSTSEC-2026-0041`: memory information leak).
  - `tar 0.4.44 -> 0.4.45` (`RUSTSEC-2026-0067` & `RUSTSEC-2026-0068`: PAX size header and symlink chmod vulnerabilities).
  - `time 0.3.41 -> 0.3.47` (`RUSTSEC-2026-0009`: RFC 2822 stack exhaustion DoS).
  - `wasmtime 29.0.1 -> 43.0.1` (`df-wasm` pinned to `43.0.1`, eliminating 12 WASI/Wasmtime guest sandbox advisories and the `regalloc2` unsoundness warning).
  - `glib 0.20.12 -> 0.22.4` (resolved `RUSTSEC-2026-0097` `VariantStrIter` unsoundness).

### Remaining Transitive Advisories (Upstream-Blocked by `iceberg 0.6.0` / `arrow 55`)

The remaining 6 advisories in `pg_mooncake/Cargo.lock` are transitive dependencies pulled in by `iceberg 0.6.0` (which pins `arrow 55`, `parquet 55`, `avro-schema 0.3`, and `reqwest 0.12`) and `deltalake-core 0.26.0` in `moonlink`:

1. `rsa 0.9.10` (`RUSTSEC-2023-0071`, Marvin Attack): pulled in transitively via `iceberg-catalog-sql -> sqlx-mysql`. Not used at runtime because `moonlink` disables default SQLx MySQL TLS features and only initializes PostgreSQL/REST Iceberg catalogs.
2. `md5 0.7.0` (`RUSTSEC-2025-0146`, crate renamed to `md-5`): pulled in by `avro-schema 0.3.0`.
3. `snappy 0.4.0` (`RUSTSEC-2026-0046`, integer truncation on >4 GiB buffers): pulled in by `avro-schema 0.3.0`; Avro metadata manifests in Iceberg are kilobytes to megabytes in size.
4. `rustls-webpki 0.102.8` (`RUSTSEC-2026-0049`, `0098`, `0099`): legacy `0.102` branch pulled in via `reqwest 0.11` in `iceberg 0.6` transitive tree; primary TLS connections use patched `rustls-webpki 0.103.12`.
