---
title: "已知限制说明"
linkTitle: "已知限制"
description: "pg_mooncake (v0.3.0) 的运行要求与当前已知限制，涵盖主键与复制标识、分区表、TRUNCATE、DDL 变更以及未实现接口说明。"
weight: 20
icon: fa-solid fa-triangle-exclamation
upstream_link: https://web.archive.org/web/20251207100516/https://docs.mooncake.dev/pg/get-started/known-limitations
aliases:
  - "/zh/pg/get-started/known-limitations/"
  - "/zh/get-started/known-limitations/"
---

在生产环境部署使用 `pg_mooncake`（`v0.3.0`）之前，请仔细阅读以下架构约束与当前已知限制。

## 1. 列存镜像表为只读副本 {#read-only-mirror}

通过 `CALL mooncake.create_table(dst, src)` 创建的表采用 `USING mooncake` 表访问方法，本质上是**只读列存镜像表**：

- 不能直接对 `USING mooncake` 列存表执行 `INSERT`、`UPDATE`、`DELETE` 或 `COPY`（PostgreSQL 将直接拒绝修改）。
- 所有数据写入和修改必须针对源行存表（`src`）执行，变更会通过 [`moonlink`](/zh/docs/intro/moonlink/) 逻辑复制自动同步至列存镜像。

## 2. 主键与 `REPLICA IDENTITY FULL` 要求 {#replica-identity}

为了通过 PostgreSQL 逻辑复制准确同步 `UPDATE` 与 `DELETE` 操作，源表必须在 WAL 日志中提供完整的旧行标识：

- **包含主键（Primary Key）的源表**：开箱即用，直接利用主键标识行。
- **不包含主键的普通源表**：`CALL mooncake.create_table(dst, src)` 会在启动复制前自动对源表执行 `ALTER TABLE src REPLICA IDENTITY FULL`。
- **分区源表（`v0.3.0` 行为说明）**：
  - 在 `pg_mooncake 0.3.0` 中，对没有主键的分区表调用 `mooncake.create_table` 时，会自动为**分区父表**以及**所有现有叶子子分区**设置 `REPLICA IDENTITY FULL`（修复了早期版本中子分区 `UPDATE` 事件缺少完整旧元组导致复制工作进程 Panic 的缺陷）。
  - **重要提示**：如果在 `mooncake.create_table` 创建镜像**之后**又新增了子分区（`CREATE TABLE ... PARTITION OF ...`），在向该新分区执行 `UPDATE` 或 `DELETE` 之前，**必须**手动执行 `ALTER TABLE <new_partition> REPLICA IDENTITY FULL;`。

## 3. `TRUNCATE` 行为说明 {#truncate}

- **普通堆表**：对已建立镜像的普通堆表执行 `TRUNCATE` **不会**同步清空列存镜像表。
- **分区表（冷热分层归档模式）**：对分区源表的单个旧子分区执行 `TRUNCATE` 或 `DROP TABLE` 会被列存镜像表**有意忽略**。这一设计使你可以安全地从 PostgreSQL 行存中删除历史冷分区以释放本地磁盘，同时在列存镜像中完整保留全部历史数据。详见[大表分区归档指南](/zh/docs/use-cases/archiving/)。

## 4. 表结构变更（`ALTER TABLE`） {#schema-evolution}

目前仅以下针对源行存表的 `ALTER TABLE` 操作会自动同步至列存镜像表：

- `ALTER TABLE <src> ADD COLUMN <col> <type>`（新增列）
- `ALTER TABLE <src> DROP COLUMN <col>`（删除列）

其他 DDL 变更（例如修改列类型 `ALTER COLUMN ... TYPE` 或重命名列 `RENAME COLUMN`）不会自动同步；如需执行复杂表结构变更，建议删除并重建列存镜像表（`DROP TABLE <dst>; CALL mooncake.create_table('<dst>', '<src>');`）。

## 5. 不支持的数据类型 {#data-types}

`pg_mooncake` 支持所有常见的 PostgreSQL 数值、文本、布尔、日期/时间、UUID、JSON/JSONB 及常见数组类型，但以下类型暂不支持或存在限制：

- PostgreSQL 自定义枚举类型（`ENUM`）、复合类型与域类型（`DOMAIN`）
- `pg_duckdb` 尚未映射的几何类型与网络地址类型
- 超出 DuckDB `DECIMAL(38, s)` 精度上限的超高精度 `NUMERIC` 值

## 6. `mooncake.load_files` 显式报错说明（`SQLSTATE 0A000`） {#load-files}

在 `pg_mooncake 0.3.0` 中，调用 `CALL mooncake.load_files(dst, files)` 会显式返回 `SQLSTATE 0A000`（`ERRCODE_FEATURE_NOT_SUPPORTED`：`"mooncake.load_files is not implemented by the bundled Moonlink version"`）。

- 在早期上游版本中，内嵌 Moonlink 服务的 `import_data` 处理器是一个空实现（no-op），会在未导入任何数据的情况下静默返回成功。
- 如需导入外部 Parquet 或 CSV 文件，请通过 `COPY` 或 `INSERT INTO ... SELECT * FROM duckdb.read_parquet(...)` 写入源行存表，或者参考[在 Postgres 中查询外部数据湖](/zh/docs/reference/query-data-lake/)直接就地查询外部文件。
