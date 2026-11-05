---
title: "快速开始与安装指南"
linkTitle: "快速开始"
description: "在 PostgreSQL 14–18 上通过 Pigsty 软件包或从源码编译安装 pg_mooncake (v0.3.0) 与 pg_duckdb (1.2.0)，配置 postgresql.conf 并启用扩展。"
weight: 20
icon: fa-solid fa-rocket
upstream_link: https://web.archive.org/web/20260124103940/https://docs.mooncake.dev/pg/get-started/
aliases:
  - "/zh/pg/get-started/"
  - "/zh/get-started/"
---

本指南介绍如何在 **PostgreSQL 14、15、16、17 与 18** 上安装 **`pg_mooncake`（`v0.3.0`）**（内嵌 [`moonlink`（`v0.0.1`）](/zh/docs/intro/moonlink/) 与 [`duckdb_mooncake`（`v0.0.2`）](/zh/docs/intro/duckdb-mooncake/)）及其依赖的 **`pg_duckdb`（`v1.2.0`）**。

## 1. 使用 Pigsty 安装二进制软件包（推荐） {#pigsty}

在主流 Linux 发行版（`el8`、`el9`、`el10`、`d12`、`d13`、`u22`、`u24`、`u26` × `x86_64` / `aarch64`）上，最快、最可靠的安装方式是使用由 [PGSTY](https://pigsty.cc/) 维护的 [**`pig`**](https://pig.pgsty.com/zh/) 包管理器。完整的各平台直链下载表请参阅[下载与可用性矩阵](/zh/download/)。

{{< tabs >}}
{{< tab label="中国大陆镜像（推荐）" >}}

```bash
# 1. 使用中国大陆镜像安装 pig 命令行工具
curl -fsSL https://repo.pigsty.cc/pig | bash

# 2. 配置 PGDG + Pigsty PGSQL 软件仓库（启用中国大陆 CDN 镜像）
pig repo add pgsql -u -r china

# 3. 安装 pg_duckdb 与 pg_mooncake（或通过 -v 18 指定 PostgreSQL 大版本）
pig install pg_duckdb pg_mooncake
```

{{< /tab >}}
{{< tab label="全球默认源" >}}

```bash
# 1. 安装 pig 命令行工具
curl -fsSL https://repo.pigsty.io/pig | bash

# 2. 配置 PGDG + Pigsty PGSQL 软件仓库
pig repo add pgsql -u

# 3. 安装 pg_duckdb 与 pg_mooncake
pig install pg_duckdb pg_mooncake
```

{{< /tab >}}
{{< tab label="原生 APT / DNF 安装" >}}

```bash
# Debian / Ubuntu (APT) —— 以 PostgreSQL 18 为例：
sudo apt-get update
sudo apt-get install -y postgresql-18-pg-duckdb postgresql-18-pg-mooncake

# RHEL / Rocky / AlmaLinux (DNF) —— 以 PostgreSQL 18 为例：
sudo dnf install -y pg_duckdb_18 pg_mooncake_18
```

{{< /tab >}}
{{< /tabs >}}

## 2. 配置 `postgresql.conf` 并启用扩展 {#configure}

`pg_mooncake` 依赖 PostgreSQL 逻辑复制将行存表的增量变更实时同步至 Moonlink，并通过 `pg_duckdb` 加载本地打包的 `mooncake.duckdb_extension`。请在 `postgresql.conf`（或通过 `ALTER SYSTEM`）中配置以下参数：

```ini
# Moonlink 逻辑复制所需配置
wal_level = logical
max_replication_slots = 32
max_wal_senders = 32
max_worker_processes = 16

# 预加载 pg_duckdb 与 pg_mooncake 动态库
shared_preload_libraries = 'pg_duckdb,pg_mooncake'

# 允许 pg_duckdb 加载本地未签名的 mooncake.duckdb_extension 扩展
duckdb.allow_community_extensions = true
duckdb.allow_unsigned_extensions = true

# 可选：仅当 mooncake.duckdb_extension 不在默认的 $(pg_config --sharedir)/extension/pg_mooncake 路径下时指定
# mooncake.extension_repository = '/usr/pgsql-18/share/extension/pg_mooncake'
```

重启 PostgreSQL 服务（例如 `sudo systemctl restart postgresql-18` 或 `pig pg restart`），随后使用 `psql` 连接目标数据库并创建扩展：

```sql
-- CASCADE 会自动启用所依赖的 pg_duckdb (1.2.0) 扩展
CREATE EXTENSION IF NOT EXISTS pg_mooncake CASCADE;
```

> [!IMPORTANT] `pg_duckdb 1.2.0` 版本守卫说明
> 在执行 `CREATE EXTENSION pg_mooncake` 时，扩展初始化 SQL 脚本会显式校验 `pg_extension` 中的 `pg_duckdb` 版本必须为 `1.2.0`。如果当前环境安装了不兼容的 `pg_duckdb` 版本（例如 `1.1.x` 或 `1.3.x`），安装将立即报错中止。请始终同步升级 `pg_duckdb` 与 `pg_mooncake`。

## 3. 从源码编译构建（`v0.3.0`） {#source}

如果你需要从源码构建 `pg_mooncake 0.3.0`、`pg_duckdb 1.2.0`、`duckdb_mooncake v0.0.2` 与 `moonlink v0.0.1`：

### 编译前置依赖 {#prerequisites}

- **PostgreSQL 开发头文件**：`postgresql-server-dev-14` 至 `18`（或 `postgresql17-devel` / `postgresql18-devel`）
- **C/C++ 构建工具链**：`cmake`、`ninja-build`、`g++` 或 `clang`、`libssl-dev`、`libcurl4-openssl-dev`、`liblz4-dev`、`libzstd-dev`、`protobuf-compiler`（`protoc`）
- **Rust 工具链**：Rust `1.99.0+`（`stable`）以及严格匹配版本的 `cargo-pgrx` **`0.19.3`**：
  ```bash
  cargo install --locked cargo-pgrx --version 0.19.3
  ```

### 克隆仓库、校验版本锁并编译安装 {#compile}

```bash
# 1. 递归克隆 pg_mooncake 及其子模块（pg_duckdb、duckdb_mooncake、moonlink）
git clone --recurse-submodules https://github.com/pgsty/pg_mooncake.git
cd pg_mooncake
git fetch --tags --force moonlink
git fetch --tags --force duckdb_mooncake

# 2. 校验所有子模块提交哈希、标签及 cargo-pgrx 0.19.3 版本
make check-versions

# 3. 编译并安装 pg_duckdb 1.2.0（内嵌 DuckDB v2.0.0）
export PGRX_PG_CONFIG_PATH=/usr/pgsql-18/bin/pg_config
make pg_duckdb PG_CONFIG="$PGRX_PG_CONFIG_PATH" PG_VERSION=pg18 JOBS=$(nproc)

# 4. 编译并安装 pg_mooncake 0.3.0 + duckdb_mooncake v0.0.2 + moonlink v0.0.1
make install PG_CONFIG="$PGRX_PG_CONFIG_PATH" PG_VERSION=pg18 JOBS=$(nproc)
```

## 4. Docker 容器镜像（Obsolete） {#docker}

> [!WARNING]
> **Obsolete（过时，待更新维护）**：PGSTY 尚未发布 `pg_mooncake 0.3.0` 的 Docker 与 Kubernetes 镜像。以下上游历史命令使用的是旧版 `mooncakelabs/pg_mooncake` 镜像（内置 PostgreSQL 17 与早期版本 `pg_mooncake`），仅供历史参考。

```bash
# 拉取并启动上游历史容器镜像
docker pull mooncakelabs/pg_mooncake
docker run --name mooncake-demo \
  -e POSTGRES_HOST_AUTH_METHOD=trust \
  -p 5432:5432 -d \
  mooncakelabs/pg_mooncake

# 使用 psql 连接容器内数据库
docker exec -it mooncake-demo psql -U postgres
```

## 下一步 {#next-steps}

{{< cards >}}
{{< card title="Hello World 上手教程" icon="fa-solid fa-terminal" link="/zh/docs/getting-started/hello-world/" >}}
亲手创建你的第一张 `USING mooncake` 列存镜像表，体验事务写入、更新、回滚与跨表关联查询。
{{< /card >}}
{{< card title="已知限制说明" icon="fa-solid fa-triangle-exclamation" link="/zh/docs/getting-started/known-limitations/" >}}
了解关于主键 / 复制标识、分区表行为、`TRUNCATE` 以及受支持 DDL 变更的工程约束。
{{< /card >}}
{{< /cards >}}
