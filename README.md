# mooncake.pgsty.com

Companion documentation and engineering blog for the [**PGSTY**](https://github.com/pgsty) forks of the **Mooncake** real-time analytics ecosystem for PostgreSQL and DuckDB:

| Project | Version | License | Repository | Local Checkout | Role |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **`pg_mooncake`** | `v0.3.0` | `MIT` | [`pgsty/pg_mooncake`](https://github.com/pgsty/pg_mooncake) | `../pg_mooncake` | PostgreSQL columnstore table extension (`pgrx 0.19.3`, `pg_duckdb 1.2.0`) |
| **`duckdb_mooncake`** | `v0.0.2` | `MIT` | [`pgsty/duckdb_mooncake`](https://github.com/pgsty/duckdb_mooncake) | `../duckdb_mooncake` | DuckDB `2.0.0` storage extension attaching to Moonlink tables |
| **`moonlink`** | `v0.0.1` | `BSL-1.1` + Exception (`MIT` client crates) | [`pgsty/moonlink`](https://github.com/pgsty/moonlink) | `../moonlink` | Real-time Iceberg & Parquet buffer engine |

---

## Site Architecture

Built with **Hugo Extended `0.168.0`**, **Go `1.27.3`**, and **[`github.com/pgsty/oink v1.5.0`](https://github.com/pgsty/oink)** (`GOWORK=off HUGO_MODULE_WORKSPACE=off`).

Unlike multi-extension portals that split `/docs/` into separate sidebar roots, `mooncake.pgsty.com` presents a single unified documentation tree directly under `content/docs/` (`sidebar_root_for: self` on `content/docs/_index.{md,zh.md}`):

- **`/docs/intro/`**: Overview, architecture (`v0.2` / `v0.3.0`), Moonlink engine, `duckdb_mooncake`, and `v0.1` vs `v0.2` comparison.
- **`/docs/getting-started/`**: Installation & quick start, first columnstore table walkthrough, and known limitations.
- **`/docs/reference/`**: `mooncake.create_table` DDL, querying columnstore tables, reading Iceberg metadata, and object store (`s3://`, `gs://`, `R2`) configuration.
- **`/docs/use-cases/`**: Real-time operational analytics (HTAP), active table archiving, Zero-ETL Postgres-to-Iceberg lakehouse, and time-series / log analytics.
- **`/docs/v0.1/`**: Complete 16-page archive of the legacy `v0.1` (Delta Lake) documentation.
- **`/docs/about/`**: Roadmap, license (`MIT` & `BSL-1.1` with `PG_MOONCAKE LINKING & DISTRIBUTION EXCEPTION`), upstream attribution, trademark policy, and SBOM / RustSec dependency audit.
- **`/blog/`**: Release announcements (`pg_mooncake 0.3.0`) and engineering deep-dives (DuckDB `2.0.0` & `pgrx 0.19.3` adaptation).
- **`/download/`**: Pre-built RPM and DEB package availability matrix generated via `bin/sync_download.py`.

---

## Development & Verification

```bash
make dev            # Serve locally at http://localhost:1313
make check          # Run go mod verify, hugo build, and check_internal_links.py
make sync-download  # Refresh content/download.{md,zh.md} from PGEXT metadata
```

`make check` builds into `/tmp/mooncake-check-public` and verifies `0` missing internal targets and `0` missing HTML fragments.

---

## License & Attribution

See [LICENSE](LICENSE) (`CC-BY-4.0` for documentation content) and [NOTICE.md](NOTICE.md) for upstream Mooncake Labs attribution and software license notices.
