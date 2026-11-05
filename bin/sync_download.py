#!/usr/bin/env python3
"""Synchronize package availability matrices and download tables from pgext into content/download.{md,zh.md}."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

EXTENSIONS = ("pg_mooncake",)
RELEASE_VERSIONS = {
    "pg_mooncake": "0.3.0",
    "duckdb_mooncake": "0.0.2",
    "moonlink": "0.0.1",
    "pg_duckdb": "1.2.0",
}


def table_reader_attributes(match: re.Match[str]) -> str:
    """Preserve source table attributes and add missing reader opt-ins."""
    attributes = match.group(1)
    classes = set(re.findall(r"(?:^|\s)\.([\w-]+)", attributes))
    missing = [name for name in ("wide", "expand") if name not in classes]
    return "{" + attributes.rstrip() + "".join(" ." + name for name in missing) + "}"


def parse_pgext_markdown(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")

    version_match = re.search(r"\|\s*\*\*EXT\*\*\s*\|[^|]+\|\s*`([^`]+)`\s*\|", text)
    version = version_match.group(1) if version_match else ""
    target_version = RELEASE_VERSIONS.get(path.stem, version)
    if version and target_version and version != target_version:
        text = re.sub(
            rf"{re.escape(version)}-\d+PIGSTY",
            f"{target_version}-1PIGSTY",
            text,
        )
        text = text.replace(f"PIGSTY {version}", f"PIGSTY {target_version}")
        text = text.replace(f"`{version}`", f"`{target_version}`")
        version = target_version

    matrix_match = re.search(
        r"(\| \*\*Linux\*\* / \*\*PG\*\* \|.*?\n\{\.matrix(?:\s+[^{}\n]*)?\})",
        text,
        re.S,
    )
    if not matrix_match:
        raise ValueError(f"Could not find {{.matrix}} table in {path}")
    matrix_en = re.sub(r"\{(\.matrix\b[^{}\n]*)\}", table_reader_attributes, matrix_match.group(1))
    matrix_zh = matrix_en.replace(
        "| **Linux** / **PG** |", "| **系统平台 / PG 版本** |", 1
    )

    packages_match = re.search(
        r'(\{\{< tabs group="pgmajor" >\}\}.*?\{\{< /tabs >\}\})',
        text,
        re.S,
    )
    if not packages_match:
        raise ValueError(f"Could not find pgmajor tabs in {path}")

    packages_en = packages_match.group(1)
    packages_en = re.sub(
        r"\[([a-z0-9_.-]+)\]\(/os/\1\)",
        r'{{< os "\1" >}}',
        packages_en,
    )
    packages_en = re.sub(r"\{(\.downloads\b[^{}\n]*)\}", table_reader_attributes, packages_en)

    packages_zh = re.sub(
        r"\| \*\*Package\*\* \| \*\*Version\*\* \| \*\*OS\*\* \| \*\*ORG\*\* \| \*\*SIZE\*\* \| \*\*File URL\*\* \|",
        "| **软件包名称** | **版本** | **系统与架构** | **软件源** | **体积** | **软件包下载直链** |",
        packages_en,
        flags=re.I,
    )

    return {
        "version": version,
        "matrix_en": matrix_en,
        "matrix_zh": matrix_zh,
        "packages_en": packages_en,
        "packages_zh": packages_zh,
    }


def build_en(data: dict[str, dict[str, str]]) -> str:
    mc = data["pg_mooncake"]
    return f"""---
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

{{{{< cards >}}}}
{{{{< card title="pg_mooncake" link="#pg_mooncake" icon="fa-solid fa-table-columns" badge="v{RELEASE_VERSIONS['pg_mooncake']}" >}}}}
PostgreSQL Table Access Method (`USING mooncake`) and columnstore mirror procedures (`mooncake.create_table`, `create_snapshot`, `optimize_table`, `list_tables`), built with `pgrx 0.19.3` for PostgreSQL 14–18.
{{{{< /card >}}}}
{{{{< card title="moonlink" link="/docs/intro/moonlink/" icon="fa-solid fa-arrows-rotate" badge="v{RELEASE_VERSIONS['moonlink']}" >}}}}
Rust real-time ingestion engine embedded inside `pg_mooncake`'s background worker (and available as a standalone HTTP/RPC server), managing logical replication, Arrow write buffers, Roaring deletion vectors, and Apache Iceberg v2 snapshots.
{{{{< /card >}}}}
{{{{< card title="duckdb_mooncake" link="/docs/intro/duckdb-mooncake/" icon="fa-solid fa-database" badge="v{RELEASE_VERSIONS['duckdb_mooncake']}" >}}}}
DuckDB 2.0 storage extension bundled with `pg_mooncake` into a local extension repository (`mooncake.extension_repository`), enabling `pg_duckdb {RELEASE_VERSIONS['pg_duckdb']}` to scan Moonlink tables with multi-file Parquet statistics pruning.
{{{{< /card >}}}}
{{{{< /cards >}}}}

---

## Quick Installation {{#install}}

### 1 · Install with PIG Package Manager (Recommended) {{#pig}}

We recommend installing `pg_mooncake` and its required companion extension `pg_duckdb` with [**`pig`**](https://pig.pgsty.com/) — the PostgreSQL package manager maintained by [PGSTY](https://pigsty.io/). `pig` automatically detects your Linux distribution and CPU architecture, configures the upstream PGDG and Pigsty repositories, and installs both extensions in one command.

{{{{< tabs >}}}}
{{{{< tab label="Global (Default)" >}}}}

```bash
# 1. Install the pig CLI package manager
curl -fsSL https://repo.pigsty.io/pig | bash

# 2. Configure PGDG + Pigsty PGSQL repositories and update repo cache
pig repo add pgsql -u

# 3. Install pg_duckdb and pg_mooncake (auto-detects active PG version, or pass -v 18)
pig install pg_duckdb pg_mooncake
```

{{{{< /tab >}}}}
{{{{< tab label="Mainland China Mirror" >}}}}

```bash
# 1. Install the pig CLI via the mainland China mirror
curl -fsSL https://repo.pigsty.cc/pig | bash

# 2. Configure repositories using the China CDN mirror (-r china)
pig repo add pgsql -u -r china

# 3. Install pg_duckdb and pg_mooncake (or specify PG major version with -v 18)
pig install pg_duckdb pg_mooncake
```

{{{{< /tab >}}}}
{{{{< tab label="Native APT (Debian / Ubuntu)" >}}}}

```bash
# Once the Pigsty APT repository is configured, install for your PostgreSQL major version (e.g. PG 18):
sudo apt-get update
sudo apt-get install -y \\
  postgresql-18-pg-duckdb \\
  postgresql-18-pg-mooncake
```

{{{{< /tab >}}}}
{{{{< tab label="Native DNF / YUM (EL 8 / 9 / 10)" >}}}}

```bash
# Once the Pigsty YUM repository is configured, install for your PostgreSQL major version (e.g. PG 18):
sudo dnf install -y \\
  pg_duckdb_18 \\
  pg_mooncake_18
```

{{{{< /tab >}}}}
{{{{< /tabs >}}}}

### 2 · Configure `postgresql.conf` & Enable Extension {{#enable}}

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

### 3 · Container Images (Obsolete) {{#docker}}

> [!WARNING]
> **Obsolete — pending updates and maintenance.** PGSTY has not yet published Docker or Kubernetes images for `pg_mooncake 0.3.0`. The historical upstream image below (`mooncakelabs/pg_mooncake`) shipped an older pre-0.3 build and is retained for reference only.

```bash
# Historical upstream container (PostgreSQL 17 + legacy pg_mooncake)
docker run --name mooncake-demo \\
  -e POSTGRES_HOST_AUTH_METHOD=trust \\
  -p 5432:5432 -d \\
  mooncakelabs/pg_mooncake
```

### 4 · Component Repositories & Releases {{#releases}}

| **Component** | **Release Tag** | **Role in Suite** | **License** | **Documentation** | **GitHub Repository & Releases** |
|:---|:---:|:---|:---:|:---|:---|
| **`pg_mooncake`** | `v{RELEASE_VERSIONS['pg_mooncake']}` | PostgreSQL TAM (`USING mooncake`), procedures, & bgworker | `MIT` | [Overview](/docs/intro/) | [pgsty/pg_mooncake](https://github.com/pgsty/pg_mooncake/releases) |
| **`duckdb_mooncake`** | `v{RELEASE_VERSIONS['duckdb_mooncake']}` | DuckDB 2.0 storage extension for Moonlink & Parquet scans | `MIT` | [duckdb_mooncake](/docs/intro/duckdb-mooncake/) | [pgsty/duckdb_mooncake](https://github.com/pgsty/duckdb_mooncake/releases) |
| **`moonlink`** | `v{RELEASE_VERSIONS['moonlink']}` | Real-time CDC, Arrow buffer, deletion vectors, & Iceberg writer | `BSL-1.1` (Exception) | [Moonlink Engine](/docs/intro/moonlink/) | [pgsty/moonlink](https://github.com/pgsty/moonlink/releases) |
| **`pg_duckdb`** | `v{RELEASE_VERSIONS['pg_duckdb']}` | Required embedded DuckDB 2.0 execution engine for PostgreSQL | `MIT` | [Getting Started](/docs/getting-started/) | [pgext.cloud/e/pg_duckdb](https://pgext.cloud/e/pg_duckdb) |
{{.wide .expand}}

---

## `pg_mooncake` — Real-Time Columnstore & Iceberg Lakehouse {{#pg_mooncake}}

**`pg_mooncake`** (`v{RELEASE_VERSIONS['pg_mooncake']}`) adds real-time columnstore mirror tables (`USING mooncake`) to PostgreSQL, bundling `moonlink v{RELEASE_VERSIONS['moonlink']}` and `duckdb_mooncake v{RELEASE_VERSIONS['duckdb_mooncake']}` alongside `pg_duckdb v{RELEASE_VERSIONS['pg_duckdb']}`.

| **Type** | **Name / Pattern** | **Version** | **PostgreSQL** | **Dependencies** | **Repository** | **License / Lang** |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|
| {{{{< bg "EXT" "PostgreSQL Extension" "blue" >}}}} | [`pg_mooncake`](/docs/intro/) | `{RELEASE_VERSIONS['pg_mooncake']}` | {{{{< pgver "18,17,16,15,14" "g,g,g,g,g" >}}}} | `pg_duckdb` (`1.2.0`) | [PGEXT #2440](https://pgext.cloud/e/pg_mooncake) | {{{{< bg "MIT" "License: MIT (with BSL-1.1 Exception for Moonlink)" "green" >}}}} |
| {{{{< bg "RPM" "EL 8 / 9 / 10 RPM Package" "orange" >}}}} | `pg_mooncake_$v` | `{mc['version']}` | {{{{< pgver "18,17,16,15,14" "g,g,g,g,g" >}}}} | `pg_duckdb_$v` | {{{{< bg "PIGSTY" "Pigsty PGSQL YUM Repository" "green" >}}}} | {{{{< bg "Rust" "Implemented in Rust (pgrx 0.19.3) & C++" "orange" >}}}} |
| {{{{< bg "DEB" "Debian & Ubuntu DEB Package" "purple" >}}}} | `postgresql-$v-pg-mooncake` | `{mc['version']}` | {{{{< pgver "18,17,16,15,14" "g,g,g,g,g" >}}}} | `postgresql-$v-pg-duckdb` | {{{{< bg "PIGSTY" "Pigsty PGSQL APT Repository" "green" >}}}} | {{{{< bg "Rust" "Implemented in Rust (pgrx 0.19.3) & C++" "orange" >}}}} |
{{.packages .wide .expand}}

### Availability Matrix (`pg_mooncake`) {{#pg_mooncake-matrix}}

{mc['matrix_en']}

### Package Downloads (`pg_mooncake`) {{#pg_mooncake-packages}}

{mc['packages_en']}

---

## Verification & Build Repositories {{#source}}

All RPM and DEB packages in the Pigsty PGSQL repository are GPG-signed and verified automatically by `dnf` / `apt` once configured via `pig repo add pgsql`. Every package is built transparently from open-source build specs:

| **Repository** | **Description** |
|:---|:---|
| [pgsty/pig](https://github.com/pgsty/pig) | The `pig` CLI package manager for PostgreSQL and 600+ extensions |
| [pgsty/rpm](https://github.com/pgsty/rpm) | RPM build specifications for EL 8 / 9 / 10 (`x86_64` & `aarch64`) |
| [pgsty/deb](https://github.com/pgsty/deb) | DEB build specifications for Debian 12 / 13 & Ubuntu 22.04 / 24.04 / 26.04 (`x86_64` & `aarch64`) |
| [pgext.cloud](https://pgext.cloud/e/pg_mooncake) | Full PostgreSQL extension catalog, availability matrix, and repository mirrors |
{{.wide .expand}}
"""


def build_zh(data: dict[str, dict[str, str]]) -> str:
    mc = data["pg_mooncake"]
    return f"""---
title: 下载与安装
linkTitle: 下载
description: 使用 pig 包管理器、源码编译或原生 RPM / DEB 软件包，在 16 个 Linux 发行版平台与 PostgreSQL 14–18 上安装 pg_mooncake（内置 moonlink 与 duckdb_mooncake）及 pg_duckdb。
weight: 30
icon: fa-solid fa-download
type: docs
sidebar_enabled: false
breadcrumb: false
page_width: wide
body_class: td-download-page
---

**`pg_mooncake`**（内嵌 **`moonlink`** 实时摄取引擎与 **`duckdb_mooncake`** DuckDB 扩展）已面向 **16 个 Linux 发行版与 CPU 架构目标**（`el8`、`el9`、`el10`、`d12`、`d13`、`u22`、`u24`、`u26` × `x86_64` / `aarch64`）以及 **PostgreSQL 14、15、16、17、18** 五个大版本构建并发布原生 RPM 与 DEB 软件包（共计 80 个预编译二进制包）。

{{{{< cards >}}}}
{{{{< card title="pg_mooncake" link="#pg_mooncake" icon="fa-solid fa-table-columns" badge="v{RELEASE_VERSIONS['pg_mooncake']}" >}}}}
PostgreSQL 实时列存表访问方法（`USING mooncake`）与列存管理存储过程（`mooncake.create_table`、`create_snapshot`、`optimize_table`、`list_tables`），基于 `pgrx 0.19.3` 构建，全面支持 PostgreSQL 14–18。
{{{{< /card >}}}}
{{{{< card title="moonlink" link="/zh/docs/intro/moonlink/" icon="fa-solid fa-arrows-rotate" badge="v{RELEASE_VERSIONS['moonlink']}" >}}}}
内嵌于 `pg_mooncake` 后台工作进程（亦可作为独立 HTTP/RPC 服务运行）的 Rust 实时摄取引擎，负责逻辑复制 CDC、Arrow 内存写缓冲、Roaring 删除向量与 Apache Iceberg v2 快照生成。
{{{{< /card >}}}}
{{{{< card title="duckdb_mooncake" link="/zh/docs/intro/duckdb-mooncake/" icon="fa-solid fa-database" badge="v{RELEASE_VERSIONS['duckdb_mooncake']}" >}}}}
随 `pg_mooncake` 一同打包安装至本地扩展仓库（`mooncake.extension_repository`）的 DuckDB 2.0 存储扩展，供 `pg_duckdb {RELEASE_VERSIONS['pg_duckdb']}` 扫描 Moonlink 表并执行多文件 Parquet 统计信息剪枝。
{{{{< /card >}}}}
{{{{< /cards >}}}}

---

## 快速安装指南 {{#install}}

### 1 · 使用 PIG 包管理器安装（推荐） {{#pig}}

我们强烈推荐使用由 [PGSTY](https://pigsty.cc/) 社区维护的 PostgreSQL 专属包管理器 [**`pig`**](https://pig.pgsty.com/zh/) 安装 `pg_mooncake` 及其依赖的 `pg_duckdb`。`pig` 能够自动识别当前 Linux 发行版与 CPU 架构、一键配置 PGDG 与 Pigsty 软件源（内置中国大陆镜像加速），并自动处理扩展依赖关系。

{{{{< tabs >}}}}
{{{{< tab label="中国大陆镜像（推荐）" >}}}}

```bash
# 1. 使用中国大陆镜像安装 pig 命令行包管理器
curl -fsSL https://repo.pigsty.cc/pig | bash

# 2. 添加 PGDG + Pigsty PGSQL 软件仓库（自动启用中国大陆 CDN 镜像）并刷新缓存
pig repo add pgsql -u -r china

# 3. 安装 pg_duckdb 与 pg_mooncake（自动匹配当前 PG 版本，或通过 -v 18 指定）
pig install pg_duckdb pg_mooncake
```

{{{{< /tab >}}}}
{{{{< tab label="全球默认源" >}}}}

```bash
# 1. 安装 pig 命令行包管理器
curl -fsSL https://repo.pigsty.io/pig | bash

# 2. 添加 PGDG + Pigsty PGSQL 软件仓库并刷新缓存
pig repo add pgsql -u

# 3. 安装 pg_duckdb 与 pg_mooncake（可通过 -v 18 显式指定 PostgreSQL 大版本）
pig install pg_duckdb pg_mooncake
```

{{{{< /tab >}}}}
{{{{< tab label="原生 APT 安装 (Debian / Ubuntu)" >}}}}

```bash
# 配置好 Pigsty APT 软件源后，按 PostgreSQL 大版本直接安装（以 PG 18 为例）：
sudo apt-get update
sudo apt-get install -y \\
  postgresql-18-pg-duckdb \\
  postgresql-18-pg-mooncake
```

{{{{< /tab >}}}}
{{{{< tab label="原生 DNF / YUM 安装 (EL 8 / 9 / 10)" >}}}}

```bash
# 配置好 Pigsty YUM 软件源后，按 PostgreSQL 大版本直接安装（以 PG 18 为例）：
sudo dnf install -y \\
  pg_duckdb_18 \\
  pg_mooncake_18
```

{{{{< /tab >}}}}
{{{{< /tabs >}}}}

### 2 · 配置 `postgresql.conf` 并启用扩展 {{#enable}}

`pg_mooncake` 需要开启逻辑复制（`wal_level = logical`），并在 `shared_preload_libraries` 中同时预加载 `pg_duckdb` 与 `pg_mooncake`：

```sql
-- 1. 配置逻辑复制、预加载动态库以及 DuckDB 本地扩展加载权限
ALTER SYSTEM SET wal_level = 'logical';
ALTER SYSTEM SET shared_preload_libraries = 'pg_duckdb,pg_mooncake';
ALTER SYSTEM SET duckdb.allow_community_extensions = 'true';
ALTER SYSTEM SET duckdb.allow_unsigned_extensions = 'true';
```

重启 PostgreSQL 实例（例如 `sudo systemctl restart postgresql-18` 或 `pig pg restart`），随后连接目标数据库启用扩展：

```sql
-- 2. 在目标数据库中创建扩展（CASCADE 会自动启用 pg_duckdb 1.2.0 依赖）
CREATE EXTENSION IF NOT EXISTS pg_mooncake CASCADE;
```

### 3 · Docker 容器镜像（Obsolete） {{#docker}}

> [!WARNING]
> **Obsolete（过时，待更新维护）**：PGSTY 尚未发布 `pg_mooncake 0.3.0` 的 Docker 与 Kubernetes 镜像。以下上游历史镜像（`mooncakelabs/pg_mooncake`）内置的是早期版本，仅供历史参考。

```bash
# 上游历史容器镜像（PostgreSQL 17 + 旧版 pg_mooncake）
docker run --name mooncake-demo \\
  -e POSTGRES_HOST_AUTH_METHOD=trust \\
  -p 5432:5432 -d \\
  mooncakelabs/pg_mooncake
```

### 4 · 组件仓库与 GitHub 发行版 {{#releases}}

| **组件名称** | **当前版本** | **组件定位** | **开源许可证** | **技术文档** | **GitHub 仓库与发行版** |
|:---|:---:|:---|:---:|:---|:---|
| **`pg_mooncake`** | `v{RELEASE_VERSIONS['pg_mooncake']}` | PostgreSQL 表访问方法（`USING mooncake`）、存储过程与后台工作进程 | `MIT` | [概览与架构](/zh/docs/intro/) | [pgsty/pg_mooncake](https://github.com/pgsty/pg_mooncake/releases) |
| **`duckdb_mooncake`** | `v{RELEASE_VERSIONS['duckdb_mooncake']}` | 面向 Moonlink 与 Parquet 统计剪枝的 DuckDB 2.0 存储扩展 | `MIT` | [duckdb_mooncake](/zh/docs/intro/duckdb-mooncake/) | [pgsty/duckdb_mooncake](https://github.com/pgsty/duckdb_mooncake/releases) |
| **`moonlink`** | `v{RELEASE_VERSIONS['moonlink']}` | 实时 CDC 摄取、Arrow 写缓冲、删除向量与 Iceberg 快照引擎 | `BSL-1.1`（含豁免） | [Moonlink 引擎](/zh/docs/intro/moonlink/) | [pgsty/moonlink](https://github.com/pgsty/moonlink/releases) |
| **`pg_duckdb`** | `v{RELEASE_VERSIONS['pg_duckdb']}` | 依赖的 PostgreSQL 内嵌 DuckDB 2.0 向量化执行扩展 | `MIT` | [快速开始](/zh/docs/getting-started/) | [pgext.cloud/e/pg_duckdb](https://pgext.cloud/e/pg_duckdb) |
{{.wide .expand}}

---

## `pg_mooncake` —— 实时列存与 Iceberg 湖仓扩展 {{#pg_mooncake}}

**`pg_mooncake`**（`v{RELEASE_VERSIONS['pg_mooncake']}`）为 PostgreSQL 提供实时列存镜像表（`USING mooncake`），内嵌 `moonlink v{RELEASE_VERSIONS['moonlink']}` 与 `duckdb_mooncake v{RELEASE_VERSIONS['duckdb_mooncake']}`，并依赖 `pg_duckdb v{RELEASE_VERSIONS['pg_duckdb']}`。

| **类型** | **名称 / 命名模式** | **版本** | **PG 版本** | **依赖项** | **软件仓库** | **许可证 / 语言** |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|
| {{{{< bg "EXT" "PostgreSQL 扩展" "blue" >}}}} | [`pg_mooncake`](/zh/docs/intro/) | `{RELEASE_VERSIONS['pg_mooncake']}` | {{{{< pgver "18,17,16,15,14" "g,g,g,g,g" >}}}} | `pg_duckdb` (`1.2.0`) | [PGEXT #2440](https://pgext.cloud/e/pg_mooncake) | {{{{< bg "MIT" "许可证: MIT (Moonlink 含 BSL-1.1 链接豁免)" "green" >}}}} |
| {{{{< bg "RPM" "EL 8 / 9 / 10 RPM 软件包" "orange" >}}}} | `pg_mooncake_$v` | `{mc['version']}` | {{{{< pgver "18,17,16,15,14" "g,g,g,g,g" >}}}} | `pg_duckdb_$v` | {{{{< bg "PIGSTY" "Pigsty PGSQL YUM 软件源" "green" >}}}} | {{{{< bg "Rust" "使用 Rust (pgrx 0.19.3) 与 C++ 编写" "orange" >}}}} |
| {{{{< bg "DEB" "Debian & Ubuntu DEB 软件包" "purple" >}}}} | `postgresql-$v-pg-mooncake` | `{mc['version']}` | {{{{< pgver "18,17,16,15,14" "g,g,g,g,g" >}}}} | `postgresql-$v-pg-duckdb` | {{{{< bg "PIGSTY" "Pigsty PGSQL APT 软件源" "green" >}}}} | {{{{< bg "Rust" "使用 Rust (pgrx 0.19.3) 与 C++ 编写" "orange" >}}}} |
{{.packages .wide .expand}}

### 可用性矩阵 (`pg_mooncake`) {{#pg_mooncake-matrix}}

{mc['matrix_zh']}

### 软件包下载列表 (`pg_mooncake`) {{#pg_mooncake-packages}}

{mc['packages_zh']}

---

## 签名校验与构建仓库 {{#source}}

Pigsty PGSQL 软件仓库中的所有 RPM 与 DEB 软件包均使用 GPG 密钥签名；通过 `pig repo add pgsql` 完成配置后，`dnf` 与 `apt` 会自动校验签名完整性。所有软件包均由开源构建规范透明构建：

| **构建仓库** | **说明** |
|:---|:---|
| [pgsty/pig](https://github.com/pgsty/pig) | `pig` 命令行包管理器（支持管理 PostgreSQL 内核与 600+ 扩展） |
| [pgsty/rpm](https://github.com/pgsty/rpm) | 面向 EL 8 / 9 / 10（`x86_64` 与 `aarch64`）的 RPM 软件包构建规范仓库 |
| [pgsty/deb](https://github.com/pgsty/deb) | 面向 Debian 12 / 13 与 Ubuntu 22.04 / 24.04 / 26.04（`x86_64` 与 `aarch64`）的 DEB 软件包构建规范仓库 |
| [pgext.cloud](https://pgext.cloud/e/pg_mooncake) | PostgreSQL 扩展目录、全局可用性矩阵与软件源镜像导航 |
{{.wide .expand}}
"""


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--pgext-dir",
        type=Path,
        default=root.parent / "pgext" / "content" / "e",
        help="Path to pgext/content/e directory",
    )
    args = parser.parse_args()

    data: dict[str, dict[str, str]] = {}
    for ext in EXTENSIONS:
        md_path = args.pgext_dir / f"{ext}.md"
        if not md_path.is_file():
            raise FileNotFoundError(f"Missing pgext source file: {md_path}")
        data[ext] = parse_pgext_markdown(md_path)

    en_out = root / "content" / "download.md"
    zh_out = root / "content" / "download.zh.md"
    en_out.write_text(build_en(data), encoding="utf-8")
    zh_out.write_text(build_zh(data), encoding="utf-8")
    print(f"Synced {en_out} and {zh_out} from {args.pgext_dir}")


if __name__ == "__main__":
    main()
