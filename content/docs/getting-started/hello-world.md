---
title: "Hello World Tutorial"
linkTitle: "Hello World"
description: "Step-by-step walkthrough: create a PostgreSQL rowstore table, mirror it into a real-time columnstore table with mooncake.create_table, and run analytical queries."
weight: 10
icon: fa-solid fa-terminal
upstream_link: https://web.archive.org/web/20251207105427/https://docs.mooncake.dev/pg/get-started/Hello-world
aliases:
  - "/pg/get-started/Hello-world/"
  - "/get-started/Hello-world/"
  - "/pg/get-started/hello-world/"
  - "/get-started/hello-world/"
---

This tutorial walks through the core operations of `pg_mooncake`: creating a regular PostgreSQL rowstore table, creating a real-time columnstore mirror (`USING mooncake`), running transactional `INSERT`, `UPDATE`, and `DELETE` statements, testing rollback semantics, and joining columnstore and rowstore tables.

## 1. Enable the Extension {#enable}

Connect to your PostgreSQL database and ensure `pg_mooncake` (along with `pg_duckdb`) is enabled:

```sql
CREATE EXTENSION IF NOT EXISTS pg_mooncake CASCADE;
```

## 2. Create a Rowstore Table & Columnstore Mirror {#create-mirror}

First, create a standard PostgreSQL heap table (`user_activity`) for your transactional writes, then call `mooncake.create_table` to create its real-time columnstore mirror (`user_activity_columnstore`):

```sql
-- 1. Create a standard PostgreSQL rowstore (heap) table
CREATE TABLE user_activity (
    user_id BIGINT PRIMARY KEY,
    activity_type TEXT,
    activity_timestamp TIMESTAMP,
    duration INT
);

-- 2. Create a real-time columnstore mirror of user_activity
CALL mooncake.create_table('user_activity_columnstore', 'user_activity');
```

Behind the scenes, `mooncake.create_table` creates `user_activity_columnstore USING mooncake`, sets up a logical replication slot on `user_activity`, and registers the table with [`moonlink`](/docs/intro/moonlink/).

## 3. Insert, Update, and Delete Rows {#dml}

Perform all writes (`INSERT`, `UPDATE`, `DELETE`) on the primary rowstore table (`user_activity`), and run your analytical `SELECT` queries on the columnstore mirror (`user_activity_columnstore`):

```sql
-- Insert rows into the rowstore table
INSERT INTO user_activity VALUES
    (1, 'login', '2024-01-01 08:00:00', 120),
    (2, 'page_view', '2024-01-01 08:05:00', 30),
    (3, 'logout', '2024-01-01 08:30:00', 60),
    (4, 'error', '2024-01-01 08:13:00', 60);

-- Update a row in the rowstore table
UPDATE user_activity SET duration = 180 WHERE user_id = 1;

-- Delete a row from the rowstore table
DELETE FROM user_activity WHERE user_id = 2;

-- Query the columnstore mirror (automatically waits for the latest WAL LSN)
SELECT * FROM user_activity_columnstore ORDER BY user_id;
```

Output:

```text
 user_id | activity_type | activity_timestamp  | duration
---------+---------------+---------------------+----------
       1 | login         | 2024-01-01 08:00:00 |      180
       3 | logout        | 2024-01-01 08:30:00 |       60
       4 | error         | 2024-01-01 08:13:00 |       60
(3 rows)
```

## 4. Transactional Consistency & Rollback {#transactions}

Moonlink only ingests committed PostgreSQL transactions from the logical replication stream. Uncommitted or rolled-back transactions never appear in the columnstore mirror:

```sql
BEGIN;
INSERT INTO user_activity VALUES
    (5, 'login', '2024-01-02 10:00:00', 200),
    (6, 'login', '2024-01-02 10:30:00', 90);
ROLLBACK;

-- Rolled-back rows (user_id 5 and 6) are not present
SELECT * FROM user_activity_columnstore ORDER BY user_id;
```

## 5. Joins Across Columnstore & Rowstore Tables {#joins}

You can join two columnstore tables together, or join a `USING mooncake` columnstore table directly with a regular PostgreSQL heap table in the same SQL query:

```sql
-- Join between two columnstore tables
SELECT ua.user_id, ua.activity_type, ua.duration
FROM user_activity_columnstore ua
JOIN user_activity_columnstore ua2 ON ua.user_id = ua2.user_id;

-- Create a regular PostgreSQL heap table for user profiles
CREATE TABLE users (
    user_id BIGINT PRIMARY KEY,
    username TEXT,
    tier TEXT
);

INSERT INTO users VALUES
    (1, 'alice', 'enterprise'),
    (3, 'bob', 'pro'),
    (4, 'charlie', 'free');

-- Join the regular Postgres heap table with the columnstore mirror
SELECT u.username, u.tier, ua.activity_type, ua.duration
FROM users u
JOIN user_activity_columnstore ua ON u.user_id = ua.user_id
ORDER BY u.user_id;
```

## 6. Inspect Replication Status & Create an Iceberg Snapshot {#inspect}

Check the current commit LSN, flushed LSN, and Iceberg warehouse directory using `mooncake.list_tables()`, or force-flush buffered Arrow data into Parquet + Apache Iceberg v2 metadata with `mooncake.create_snapshot`:

```sql
-- View replication LSN progress and warehouse path
SELECT * FROM mooncake.list_tables();

-- Flush in-memory Arrow buffer into a new Apache Iceberg v2 snapshot
CALL mooncake.create_snapshot('user_activity_columnstore');
```
