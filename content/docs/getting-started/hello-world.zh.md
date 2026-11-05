---
title: "Hello World 快速上手教程"
linkTitle: "Hello World"
description: "手把手教程：创建 PostgreSQL 行存表，通过 mooncake.create_table 创建实时列存镜像表，并执行增删改、回滚与跨表关联分析查询。"
weight: 10
icon: fa-solid fa-terminal
upstream_link: https://web.archive.org/web/20251207105427/https://docs.mooncake.dev/pg/get-started/Hello-world
aliases:
  - "/zh/pg/get-started/Hello-world/"
  - "/zh/get-started/Hello-world/"
  - "/zh/pg/get-started/hello-world/"
  - "/zh/get-started/hello-world/"
---

本教程将带你体验 `pg_mooncake` 的核心操作流程：创建标准的 PostgreSQL 行存表，创建实时同步的列存镜像表（`USING mooncake`），执行事务级 `INSERT`、`UPDATE`、`DELETE` 与 `ROLLBACK`，以及在列存镜像表与常规行存表之间执行混合 `JOIN` 查询。

## 1. 启用扩展 {#enable}

连接目标 PostgreSQL 数据库，确保已启用 `pg_mooncake`（及依赖的 `pg_duckdb`）：

```sql
CREATE EXTENSION IF NOT EXISTS pg_mooncake CASCADE;
```

## 2. 创建行存表与实时列存镜像表 {#create-mirror}

首先创建一张标准的 PostgreSQL 行存表（`user_activity`）用于承载业务写入，随后调用 `mooncake.create_table` 创建它的实时列存镜像表（`user_activity_columnstore`）：

```sql
-- 1. 创建标准的 PostgreSQL 行存（堆）表
CREATE TABLE user_activity (
    user_id BIGINT PRIMARY KEY,
    activity_type TEXT,
    activity_timestamp TIMESTAMP,
    duration INT
);

-- 2. 为 user_activity 创建实时列存镜像表
CALL mooncake.create_table('user_activity_columnstore', 'user_activity');
```

在后台，`mooncake.create_table` 会自动创建 `user_activity_columnstore USING mooncake` 表，为 `user_activity` 建立逻辑复制槽，并将表元数据注册到 [`moonlink`](/zh/docs/intro/moonlink/) 引擎中。

## 3. 执行插入、更新与删除操作 {#dml}

所有写操作（`INSERT`、`UPDATE`、`DELETE`）均针对原始行存表（`user_activity`）执行，而分析型 `SELECT` 查询则针对列存镜像表（`user_activity_columnstore`）执行：

```sql
-- 向行存表插入数据
INSERT INTO user_activity VALUES
    (1, 'login', '2024-01-01 08:00:00', 120),
    (2, 'page_view', '2024-01-01 08:05:00', 30),
    (3, 'logout', '2024-01-01 08:30:00', 60),
    (4, 'error', '2024-01-01 08:13:00', 60);

-- 在行存表上更新一行
UPDATE user_activity SET duration = 180 WHERE user_id = 1;

-- 从行存表中删除一行
DELETE FROM user_activity WHERE user_id = 2;

-- 查询列存镜像表（会自动等待最新 WAL LSN 同步完成）
SELECT * FROM user_activity_columnstore ORDER BY user_id;
```

查询输出：

```text
 user_id | activity_type | activity_timestamp  | duration
---------+---------------+---------------------+----------
       1 | login         | 2024-01-01 08:00:00 |      180
       3 | logout        | 2024-01-01 08:30:00 |       60
       4 | error         | 2024-01-01 08:13:00 |       60
(3 rows)
```

## 4. 事务一致性与回滚验证 {#transactions}

Moonlink 仅从逻辑复制流中摄取已提交的 PostgreSQL 事务；未提交或已回滚（`ROLLBACK`）的事务绝不会出现在列存镜像表中：

```sql
BEGIN;
INSERT INTO user_activity VALUES
    (5, 'login', '2024-01-02 10:00:00', 200),
    (6, 'login', '2024-01-02 10:30:00', 90);
ROLLBACK;

-- 已回滚的行（user_id 5 和 6）不会出现在查询结果中
SELECT * FROM user_activity_columnstore ORDER BY user_id;
```

## 5. 列存表与行存表混合关联（JOIN） {#joins}

你可以在两张列存镜像表之间执行关联查询，也可以在单条 SQL 中将 `USING mooncake` 列存镜像表与常规 PostgreSQL 行存表直接 `JOIN`：

```sql
-- 两张列存表之间的关联查询
SELECT ua.user_id, ua.activity_type, ua.duration
FROM user_activity_columnstore ua
JOIN user_activity_columnstore ua2 ON ua.user_id = ua2.user_id;

-- 创建一张常规 PostgreSQL 行存表存储用户信息
CREATE TABLE users (
    user_id BIGINT PRIMARY KEY,
    username TEXT,
    tier TEXT
);

INSERT INTO users VALUES
    (1, 'alice', 'enterprise'),
    (3, 'bob', 'pro'),
    (4, 'charlie', 'free');

-- 直接关联 PostgreSQL 行存表与列存镜像表
SELECT u.username, u.tier, ua.activity_type, ua.duration
FROM users u
JOIN user_activity_columnstore ua ON u.user_id = ua.user_id
ORDER BY u.user_id;
```

## 6. 查看复制状态并生成 Iceberg 快照 {#inspect}

通过 `mooncake.list_tables()` 查看当前的提交 LSN、刷盘 LSN 及 Iceberg 仓库目录，或调用 `mooncake.create_snapshot` 将内存 Arrow 写缓冲区强制刷盘并生成新的 Apache Iceberg v2 快照：

```sql
-- 查看复制 LSN 进度与 Iceberg 仓库路径
SELECT * FROM mooncake.list_tables();

-- 将内存 Arrow 缓冲刷写为新的 Apache Iceberg v2 快照
CALL mooncake.create_snapshot('user_activity_columnstore');
```
