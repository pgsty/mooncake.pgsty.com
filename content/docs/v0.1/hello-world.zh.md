---
title: "v0.1 Hello World (USING columnstore)"
linkTitle: "v0.1 Hello World"
description: "pg_mooncake v0.1 USING columnstore 表的基础操作：建表、增删改、事务回滚与关联查询。"
weight: 25
icon: fa-solid fa-terminal
upstream_link: https://web.archive.org/web/20260124122532/https://docs.mooncake.dev/pg/0.1/get-started/Hello-world
aliases:
  - "/zh/pg/0.1/get-started/Hello-world/"
  - "/zh/0.1/get-started/Hello-world/"
  - "/zh/pg/0.1/get-started/hello-world/"
  - "/zh/0.1/get-started/hello-world/"
---

> [!WARNING] `pg_mooncake v0.1` 历史归档文档（Delta Lake 引擎）
> 本页归档的是早期 **`pg_mooncake v0.1`** 版本文档（采用直接 `CREATE TABLE ... USING columnstore` DDL 与 Delta Lake 存储）。从 `v0.2` 及 PGSTY 维护的 **`v0.3.0`** 版本起，`pg_mooncake` 已全面转向基于 [`moonlink`](/zh/docs/intro/moonlink/) 的实时列存镜像架构（`CALL mooncake.create_table` + `USING mooncake`）与 Apache Iceberg v2。最新文档请参阅[简介](/zh/docs/intro/)与 [v0.1 与 v0.2 / v0.3 架构演进对比](/zh/docs/intro/0.1-vs-0.2/)。

## 启用扩展

```sql
CREATE EXTENSION pg_mooncake;
```

## 创建 `USING columnstore` 列存表（`v0.1`）

```sql
CREATE TABLE user_activity (
    user_id BIGINT,
    activity_type TEXT,
    activity_timestamp TIMESTAMP,
    duration INT
) USING columnstore;
```

## 插入、更新与删除

```sql
INSERT INTO user_activity VALUES
    (1, 'login', '2024-01-01 08:00:00', 120),
    (2, 'page_view', '2024-01-01 08:05:00', 30),
    (3, 'logout', '2024-01-01 08:30:00', 60),
    (4, 'error', '2024-01-01 08:13:00', 60);

UPDATE user_activity SET duration = 180 WHERE user_id = 1;
DELETE FROM user_activity WHERE user_id = 2;
```

## 事务与回滚

```sql
BEGIN;
INSERT INTO user_activity VALUES
    (5, 'login', '2024-01-02 10:00:00', 200),
    (6, 'login', '2024-01-02 10:30:00', 90);
ROLLBACK;
SELECT * FROM user_activity;
```

## 跨表关联（JOIN）

```sql
-- 两张列存表关联
SELECT * FROM user_activity ua
JOIN user_activity ua2 ON ua.user_id = ua2.user_id;

-- 普通 Postgres 行存表与列存表关联
SELECT * FROM users JOIN user_activity ON users.user_id = user_activity.user_id;
```
