---
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

{{< cards >}}
{{< card title="pg_mooncake" link="#pg_mooncake" icon="fa-solid fa-table-columns" badge="v0.3.0" >}}
PostgreSQL 实时列存表访问方法（`USING mooncake`）与列存管理存储过程（`mooncake.create_table`、`create_snapshot`、`optimize_table`、`list_tables`），基于 `pgrx 0.19.3` 构建，全面支持 PostgreSQL 14–18。
{{< /card >}}
{{< card title="moonlink" link="/zh/docs/intro/moonlink/" icon="fa-solid fa-arrows-rotate" badge="v0.0.1" >}}
内嵌于 `pg_mooncake` 后台工作进程（亦可作为独立 HTTP/RPC 服务运行）的 Rust 实时摄取引擎，负责逻辑复制 CDC、Arrow 内存写缓冲、Roaring 删除向量与 Apache Iceberg v2 快照生成。
{{< /card >}}
{{< card title="duckdb_mooncake" link="/zh/docs/intro/duckdb-mooncake/" icon="fa-solid fa-database" badge="v0.0.2" >}}
随 `pg_mooncake` 一同打包安装至本地扩展仓库（`mooncake.extension_repository`）的 DuckDB 2.0 存储扩展，供 `pg_duckdb 1.2.0` 扫描 Moonlink 表并执行多文件 Parquet 统计信息剪枝。
{{< /card >}}
{{< /cards >}}

---

## 快速安装指南 {#install}

### 1 · 使用 PIG 包管理器安装（推荐） {#pig}

我们强烈推荐使用由 [PGSTY](https://pigsty.cc/) 社区维护的 PostgreSQL 专属包管理器 [**`pig`**](https://pig.pgsty.com/zh/) 安装 `pg_mooncake` 及其依赖的 `pg_duckdb`。`pig` 能够自动识别当前 Linux 发行版与 CPU 架构、一键配置 PGDG 与 Pigsty 软件源（内置中国大陆镜像加速），并自动处理扩展依赖关系。

{{< tabs >}}
{{< tab label="中国大陆镜像（推荐）" >}}

```bash
# 1. 使用中国大陆镜像安装 pig 命令行包管理器
curl -fsSL https://repo.pigsty.cc/pig | bash

# 2. 添加 PGDG + Pigsty PGSQL 软件仓库（自动启用中国大陆 CDN 镜像）并刷新缓存
pig repo add pgsql -u -r china

# 3. 安装 pg_duckdb 与 pg_mooncake（自动匹配当前 PG 版本，或通过 -v 18 指定）
pig install pg_duckdb pg_mooncake
```

{{< /tab >}}
{{< tab label="全球默认源" >}}

```bash
# 1. 安装 pig 命令行包管理器
curl -fsSL https://repo.pigsty.io/pig | bash

# 2. 添加 PGDG + Pigsty PGSQL 软件仓库并刷新缓存
pig repo add pgsql -u

# 3. 安装 pg_duckdb 与 pg_mooncake（可通过 -v 18 显式指定 PostgreSQL 大版本）
pig install pg_duckdb pg_mooncake
```

{{< /tab >}}
{{< tab label="原生 APT 安装 (Debian / Ubuntu)" >}}

```bash
# 配置好 Pigsty APT 软件源后，按 PostgreSQL 大版本直接安装（以 PG 18 为例）：
sudo apt-get update
sudo apt-get install -y \
  postgresql-18-pg-duckdb \
  postgresql-18-pg-mooncake
```

{{< /tab >}}
{{< tab label="原生 DNF / YUM 安装 (EL 8 / 9 / 10)" >}}

```bash
# 配置好 Pigsty YUM 软件源后，按 PostgreSQL 大版本直接安装（以 PG 18 为例）：
sudo dnf install -y \
  pg_duckdb_18 \
  pg_mooncake_18
```

{{< /tab >}}
{{< /tabs >}}

### 2 · 配置 `postgresql.conf` 并启用扩展 {#enable}

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

### 3 · Docker 容器镜像（Obsolete） {#docker}

> [!WARNING]
> **Obsolete（过时，待更新维护）**：PGSTY 尚未发布 `pg_mooncake 0.3.0` 的 Docker 与 Kubernetes 镜像。以下上游历史镜像（`mooncakelabs/pg_mooncake`）内置的是早期版本，仅供历史参考。

```bash
# 上游历史容器镜像（PostgreSQL 17 + 旧版 pg_mooncake）
docker run --name mooncake-demo \
  -e POSTGRES_HOST_AUTH_METHOD=trust \
  -p 5432:5432 -d \
  mooncakelabs/pg_mooncake
```

### 4 · 组件仓库与 GitHub 发行版 {#releases}

| **组件名称** | **当前版本** | **组件定位** | **开源许可证** | **技术文档** | **GitHub 仓库与发行版** |
|:---|:---:|:---|:---:|:---|:---|
| **`pg_mooncake`** | `v0.3.0` | PostgreSQL 表访问方法（`USING mooncake`）、存储过程与后台工作进程 | `MIT` | [概览与架构](/zh/docs/intro/) | [pgsty/pg_mooncake](https://github.com/pgsty/pg_mooncake/releases) |
| **`duckdb_mooncake`** | `v0.0.2` | 面向 Moonlink 与 Parquet 统计剪枝的 DuckDB 2.0 存储扩展 | `MIT` | [duckdb_mooncake](/zh/docs/intro/duckdb-mooncake/) | [pgsty/duckdb_mooncake](https://github.com/pgsty/duckdb_mooncake/releases) |
| **`moonlink`** | `v0.0.1` | 实时 CDC 摄取、Arrow 写缓冲、删除向量与 Iceberg 快照引擎 | `BSL-1.1`（含豁免） | [Moonlink 引擎](/zh/docs/intro/moonlink/) | [pgsty/moonlink](https://github.com/pgsty/moonlink/releases) |
| **`pg_duckdb`** | `v1.2.0` | 依赖的 PostgreSQL 内嵌 DuckDB 2.0 向量化执行扩展 | `MIT` | [快速开始](/zh/docs/getting-started/) | [pgext.cloud/e/pg_duckdb](https://pgext.cloud/e/pg_duckdb) |
{.wide .expand}

---

## `pg_mooncake` —— 实时列存与 Iceberg 湖仓扩展 {#pg_mooncake}

**`pg_mooncake`**（`v0.3.0`）为 PostgreSQL 提供实时列存镜像表（`USING mooncake`），内嵌 `moonlink v0.0.1` 与 `duckdb_mooncake v0.0.2`，并依赖 `pg_duckdb v1.2.0`。

| **类型** | **名称 / 命名模式** | **版本** | **PG 版本** | **依赖项** | **软件仓库** | **许可证 / 语言** |
|:---:|:---|:---:|:---:|:---:|:---:|:---:|
| {{< bg "EXT" "PostgreSQL 扩展" "blue" >}} | [`pg_mooncake`](/zh/docs/intro/) | `0.3.0` | {{< pgver "18,17,16,15,14" "g,g,g,g,g" >}} | `pg_duckdb` (`1.2.0`) | [PGEXT #2440](https://pgext.cloud/e/pg_mooncake) | {{< bg "MIT" "许可证: MIT (Moonlink 含 BSL-1.1 链接豁免)" "green" >}} |
| {{< bg "RPM" "EL 8 / 9 / 10 RPM 软件包" "orange" >}} | `pg_mooncake_$v` | `0.3.0` | {{< pgver "18,17,16,15,14" "g,g,g,g,g" >}} | `pg_duckdb_$v` | {{< bg "PIGSTY" "Pigsty PGSQL YUM 软件源" "green" >}} | {{< bg "Rust" "使用 Rust (pgrx 0.19.3) 与 C++ 编写" "orange" >}} |
| {{< bg "DEB" "Debian & Ubuntu DEB 软件包" "purple" >}} | `postgresql-$v-pg-mooncake` | `0.3.0` | {{< pgver "18,17,16,15,14" "g,g,g,g,g" >}} | `postgresql-$v-pg-duckdb` | {{< bg "PIGSTY" "Pigsty PGSQL APT 软件源" "green" >}} | {{< bg "Rust" "使用 Rust (pgrx 0.19.3) 与 C++ 编写" "orange" >}} |
{.packages .wide .expand}

### 可用性矩阵 (`pg_mooncake`) {#pg_mooncake-matrix}

| **系统平台 / PG 版本** |                  **PG18**                   |                  **PG17**                   |                  **PG16**                   |                  **PG15**                   |                  **PG14**                   |
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

### 软件包下载列表 (`pg_mooncake`) {#pg_mooncake-packages}

{{< tabs group="pgmajor" >}}
{{< tab label="PG18" value="pg18" >}}

| **软件包名称** | **版本** | **系统与架构** | **软件源** | **体积** | **软件包下载直链** |
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

| **软件包名称** | **版本** | **系统与架构** | **软件源** | **体积** | **软件包下载直链** |
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

| **软件包名称** | **版本** | **系统与架构** | **软件源** | **体积** | **软件包下载直链** |
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

| **软件包名称** | **版本** | **系统与架构** | **软件源** | **体积** | **软件包下载直链** |
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

| **软件包名称** | **版本** | **系统与架构** | **软件源** | **体积** | **软件包下载直链** |
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

## 签名校验与构建仓库 {#source}

Pigsty PGSQL 软件仓库中的所有 RPM 与 DEB 软件包均使用 GPG 密钥签名；通过 `pig repo add pgsql` 完成配置后，`dnf` 与 `apt` 会自动校验签名完整性。所有软件包均由开源构建规范透明构建：

| **构建仓库** | **说明** |
|:---|:---|
| [pgsty/pig](https://github.com/pgsty/pig) | `pig` 命令行包管理器（支持管理 PostgreSQL 内核与 600+ 扩展） |
| [pgsty/rpm](https://github.com/pgsty/rpm) | 面向 EL 8 / 9 / 10（`x86_64` 与 `aarch64`）的 RPM 软件包构建规范仓库 |
| [pgsty/deb](https://github.com/pgsty/deb) | 面向 Debian 12 / 13 与 Ubuntu 22.04 / 24.04 / 26.04（`x86_64` 与 `aarch64`）的 DEB 软件包构建规范仓库 |
| [pgext.cloud](https://pgext.cloud/e/pg_mooncake) | PostgreSQL 扩展目录、全局可用性矩阵与软件源镜像导航 |
{.wide .expand}
