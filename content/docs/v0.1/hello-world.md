---
title: "v0.1 Hello World (USING columnstore)"
linkTitle: "v0.1 Hello World"
description: "Basic operations on v0.1 USING columnstore tables: CREATE TABLE, INSERT, UPDATE, DELETE, transactions, and joins."
weight: 25
icon: fa-solid fa-terminal
upstream_link: https://web.archive.org/web/20260124122532/https://docs.mooncake.dev/pg/0.1/get-started/Hello-world
aliases:
  - "/pg/0.1/get-started/Hello-world/"
  - "/0.1/get-started/Hello-world/"
  - "/pg/0.1/get-started/hello-world/"
  - "/0.1/get-started/hello-world/"
---

> [!WARNING] Legacy `pg_mooncake v0.1` Archive (Delta Lake Engine)
> This page documents **`pg_mooncake v0.1`**, which used direct `CREATE TABLE ... USING columnstore` DDL and Delta Lake storage. Starting in `v0.2` and PGSTY's **`v0.3.0`** release, `pg_mooncake` uses [`moonlink`](/docs/intro/moonlink/) real-time columnstore mirrors (`CALL mooncake.create_table` + `USING mooncake`) and Apache Iceberg v2. For current documentation, see [Introduction](/docs/intro/) and [v0.1 vs v0.2 & v0.3](/docs/intro/0.1-vs-0.2/).

## Create the Extension

```sql
CREATE EXTENSION pg_mooncake;
```

## Create a `USING columnstore` Table (`v0.1`)

```sql
CREATE TABLE user_activity (
    user_id BIGINT,
    activity_type TEXT,
    activity_timestamp TIMESTAMP,
    duration INT
) USING columnstore;
```

## Inserts, Updates, and Deletes

```sql
INSERT INTO user_activity VALUES
    (1, 'login', '2024-01-01 08:00:00', 120),
    (2, 'page_view', '2024-01-01 08:05:00', 30),
    (3, 'logout', '2024-01-01 08:30:00', 60),
    (4, 'error', '2024-01-01 08:13:00', 60);

UPDATE user_activity SET duration = 180 WHERE user_id = 1;
DELETE FROM user_activity WHERE user_id = 2;
```

## Transactions

```sql
BEGIN;
INSERT INTO user_activity VALUES
    (5, 'login', '2024-01-02 10:00:00', 200),
    (6, 'login', '2024-01-02 10:30:00', 90);
ROLLBACK;
SELECT * FROM user_activity;
```

## Joins

```sql
-- Between two columnstore tables
SELECT * FROM user_activity ua
JOIN user_activity ua2 ON ua.user_id = ua2.user_id;

-- Between a regular PostgreSQL table and a columnstore table
SELECT * FROM users JOIN user_activity ON users.user_id = user_activity.user_id;
```
