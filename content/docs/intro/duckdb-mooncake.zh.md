---
title: "duckdb_mooncake 与 DuckDB 2.0 集成"
linkTitle: "duckdb_mooncake"
description: "解析 duckdb_mooncake (v0.0.2) 如何连接 DuckDB 2.0 与 pg_duckdb 1.2.0 至 Moonlink 表、执行多文件 Parquet 统计剪枝，并通过本地扩展仓库加载。"
weight: 30
icon: fa-solid fa-database
upstream_source: duckdb_mooncake
upstream_link: https://github.com/Mooncake-Labs/duckdb_mooncake
---

**`duckdb_mooncake`**（[`pgsty/duckdb_mooncake`](https://github.com/pgsty/duckdb_mooncake)，当前正式版本 **`v0.0.2`**，`MIT` 许可证）是面向 **DuckDB `v2.0.0`** 的 C++ 与 Rust FFI 存储扩展。它使 DuckDB（无论是独立运行还是通过 `pg_duckdb 1.2.0` 内嵌在 PostgreSQL 中）能够直接挂载 [`moonlink`](/zh/docs/intro/moonlink/) 元数据目录，并对 Moonlink 表执行高性能向量化扫描。

## 在 `pg_mooncake 0.3.0` 中的核心角色 {#role}

当 `pg_mooncake` 在 PostgreSQL 内执行针对 `USING mooncake` 列存表的查询时，`pg_duckdb` 会将表扫描算子委托给 DuckDB 执行。`pg_mooncake` 在初始化 DuckDB 会话时会自动执行以下命令：

```sql
-- 由 pg_mooncake 在初始化 DuckDB 会话时自动执行
SET extension_directory = '<mooncake.extension_repository>';
LOAD mooncake;
ATTACH '' AS mooncake (TYPE mooncake, METADATA '<pgdata>/pg_mooncake');
```

### 本地扩展仓库（`mooncake.extension_repository`） {#extension-repository}

不同于早期版本在运行时从远程社区存储桶下载扩展二进制文件，`pg_mooncake 0.3.0` 在编译和打包阶段即直接构建 `mooncake.duckdb_extension`（`v0.0.2`），并随 PostgreSQL 扩展一同安装至本地 DuckDB 扩展目录：

```text
$(pg_config --sharedir)/extension/pg_mooncake/
└── v2.0.0/
    └── <duckdb_platform>/          # 例如 linux_amd64, linux_arm64, osx_arm64
        └── mooncake.duckdb_extension
```

PostgreSQL 配置参数 `mooncake.extension_repository` 默认指向该目录（也可在 `postgresql.conf` 中显式指定自定义路径），配合 `duckdb.allow_unsigned_extensions = true` 实现完全离线、确定性、字节级一致的本地扩展加载。

## `v0.0.2` 对 DuckDB 2.0 的关键适配 {#duckdb-2}

在 PGSTY 发布的 **`duckdb_mooncake v0.0.2`**（`49765a369ad88986916ce53c969ed2ce4ba66fac`）版本中，完成了面向 **DuckDB `v2.0.0`**（`d54cbbe3df17e8e5ce68312f483b4155836112aa`）与 **`pg_duckdb 1.2.0`** 的深度适配：

1. **适配 DuckDB 2.0 存储与目录 API**：更新了存储扩展注册、Catalog 条目查找、Arrow Schema 转换（`nanoarrow 0.7`）、表函数绑定、多文件列表（Multi-File Lists）以及表过滤条件（Table Filter）下推接口。
2. **改用导出的多文件 Parquet 统计信息接口**：旧版代码直接依赖 `ParquetReader` 的内部符号，而这些符号在 DuckDB 2.0 的 `libduckdb.so` 中已不再导出。`duckdb_mooncake v0.0.2` 改用 DuckDB 2.0 公开导出的多文件读取器接口（`MultiFileReader`）读取 Parquet 列级最小/最大值统计信息，并通过 `ldd -r` 验证与 `pg_duckdb` 的 `libduckdb.so` 之间零未解析动态符号。
3. **消除对象缓存（Object Cache）重入死锁**：此前在持有对象缓存互斥锁期间构造统计信息条目，若加载 Parquet 元数据时再次访问 DuckDB 对象缓存，会导致互斥锁重入死锁。`v0.0.2` 改为在对象缓存互斥锁外部完成统计信息条目的构造，再原子写入缓存。
4. **CRoaring 与 Corrosion 构建加固**：使用 `Corrosion v0.5`、`nanoarrow 0.7` 与 `CRoaring v5.5.4`（当系统缺少 `libroaring` 时执行 SHA-256 校验构建），并以 `--locked` 模式锁定 `moonlink_ffi` Rust 客户端依赖（RustSec 漏洞匹配数为 `0`）。

## 在独立 DuckDB CLI 中使用 {#standalone}

你也可以在独立的 DuckDB `v2.0.0` 命令行（`duckdb -unsigned`）中直接加载 `duckdb_mooncake`，用于检查或查询 Moonlink 数据目录：

```sql
-- 指定本地扩展仓库路径并加载 mooncake 扩展
SET extension_directory = '/usr/pgsql-18/share/extension/pg_mooncake';
LOAD mooncake;

-- 挂载 Moonlink 元数据目录
ATTACH '' AS mooncake (TYPE mooncake, METADATA '/var/lib/pgsql/18/data/pg_mooncake');

-- 在 DuckDB 中直接对 Moonlink 表执行向量化查询
SELECT * FROM mooncake.public.trades_analytics LIMIT 10;
```
