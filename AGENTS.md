# AGENTS.md — `mooncake.pgsty.com`

## 1. Mission & Identity

This repository builds **`https://mooncake.pgsty.com/`**, the companion documentation and engineering blog website for **`pgsty/pg_mooncake`** (`v0.3.0`), **`pgsty/duckdb_mooncake`** (`v0.0.2`), and **`pgsty/moonlink`** (`v0.0.1`).

- **Framework**: Hugo Extended `0.168.0` + Go `1.27.3` + `github.com/pgsty/oink v1.5.0`
- **Upstream Docs Source**: Historical `https://docs.mooncake.dev/` snapshot (`https://web.archive.org/web/20251207085834/https://docs.mooncake.dev/pg/intro/`)
- **Code Repositories**:
  - `https://github.com/pgsty/pg_mooncake` (`/Users/vonng/pgsty/pg_mooncake`, tag `v0.3.0`, `MIT`)
  - `https://github.com/pgsty/duckdb_mooncake` (`/Users/vonng/pgsty/duckdb_mooncake`, tag `v0.0.2`, `MIT`)
  - `https://github.com/pgsty/moonlink` (`/Users/vonng/pgsty/moonlink`, tag `v0.0.1`, `BSL-1.1` + `PG_MOONCAKE LINKING & DISTRIBUTION EXCEPTION`, client crates `MIT`)
- **Unified Docs Layout**: All documentation lives directly under `content/docs/` (`intro/`, `getting-started/`, `reference/`, `use-cases/`, `v0.1/`, `about/`) with a single `sidebar_root_for: self` on `content/docs/_index.{md,zh.md}`. Do not split `/docs/` into multiple separate extension sub-roots.

---

## 2. Hard Rules

1. **Pure OINK 1.5.0**:
   - Rely on `github.com/pgsty/oink v1.5.0` layouts, shortcodes, and `data/home/en.yaml` sections. Do not copy or fork OINK templates into `layouts/` unless strictly necessary.
   - Always run Hugo with `GOWORK=off HUGO_MODULE_WORKSPACE=off`.
   - Never enable `--panicOnWarning` or `HUGO_PANICONWARNING`.

2. **Clean Git Tree**:
   - Never commit `public/`, `resources/`, `.hugo_build.lock`, `.venv-check/`, or temporary build directories.
   - Keep raw scrape/import artifacts in `/tmp/`, never inside the repository.

3. **Markdown & Component Conventions**:
   - **Callouts**: Use OINK GitHub-style blockquotes (`> [!NOTE]`, `> [!TIP]`, `> [!IMPORTANT]`, `> [!WARNING]`, `> [!CAUTION]`, `> [!DETAILS] Title`), never VitePress `:::` fences.
   - **Math**: Goldmark passthrough is configured with `inline: [['\(', '\)']]` and `block: [['$$', '$$'], ['\[', '\]']]` so currency values (`$1`, `$250`) are never swallowed as math. Pages using math must set `math: true` in front matter.
   - **Headings**: Never put shortcodes (`{{< badge ... >}}`) inside Markdown headings.
   - **Provenance**: Pages adapted from upstream must carry `upstream_source` (or inherit it via `cascade`) and `upstream_link`.

4. **Verification Gate**:
   - Every change must pass `make check`:
     ```bash
     make check
     ```
   - `make check` runs `go mod verify`, `hugo build --minify --cleanDestinationDir --printPathWarnings --printI18nWarnings -d /tmp/mooncake-check-public`, and `python3 bin/check_internal_links.py /tmp/mooncake-check-public` (requiring 0 missing internal targets and 0 missing HTML fragments).
