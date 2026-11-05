---
title: "Known Limitations"
linkTitle: "Known Limitations"
description: "Operational requirements and current limitations of pg_mooncake (v0.3.0), including primary keys, partitioned tables, TRUNCATE, schema DDL, and unsupported procedures."
weight: 20
icon: fa-solid fa-triangle-exclamation
upstream_link: https://web.archive.org/web/20251207100516/https://docs.mooncake.dev/pg/get-started/known-limitations
aliases:
  - "/pg/get-started/known-limitations/"
  - "/get-started/known-limitations/"
---

Before deploying `pg_mooncake` (`v0.3.0`) in production, review the following architectural constraints and known limitations.

## 1. Read-Only Columnstore Mirror Tables {#read-only-mirror}

Tables created with `CALL mooncake.create_table(dst, src)` use the `USING mooncake` table access method and are **read-only replicas**.

- Direct `INSERT`, `UPDATE`, `DELETE`, or `COPY` statements targeting the `USING mooncake` table are rejected by PostgreSQL (`ERROR:cannot modify table "..." because it uses the mooncake access method`).
- Always execute DML operations against the source rowstore table (`src`); changes replicate automatically via [`moonlink`](/docs/intro/moonlink/).

## 2. Primary Keys & `REPLICA IDENTITY FULL` {#replica-identity}

To replicate `UPDATE` and `DELETE` operations accurately over PostgreSQL logical replication, the source table must provide complete old-row identification in the WAL stream:

- **Tables with a Primary Key**: Work out of the box using the primary key.
- **Tables without a Primary Key**: `CALL mooncake.create_table(dst, src)` automatically executes `ALTER TABLE src REPLICA IDENTITY FULL` before starting replication.
- **Partitioned Tables (`v0.3.0` behavior)**:
  - In `pg_mooncake 0.3.0`, calling `mooncake.create_table` on a partitioned table without a primary key automatically sets `REPLICA IDENTITY FULL` on both the **partitioned root table** and **all existing leaf partitions** (fixing an earlier bug where partition `UPDATE` events lacked complete old tuples and caused a replication worker panic).
  - **Important**: If you attach or create **new partitions** *after* `mooncake.create_table` has already run, you **must** explicitly run `ALTER TABLE <new_partition> REPLICA IDENTITY FULL;` on that new partition before executing `UPDATE` or `DELETE` statements on it.

## 3. `TRUNCATE` Behavior {#truncate}

- **Regular Heap Tables**: `TRUNCATE` on a mirrored regular heap table is **not** replicated to the columnstore mirror.
- **Partitioned Tables (Archiving Pattern)**: `TRUNCATE` or `DROP TABLE` on individual old partitions of a partitioned source table is **intentionally ignored** by the columnstore mirror so you can drop cold partitions from PostgreSQL heap storage while retaining the complete historical dataset in the columnstore. See [Archiving Large Postgres Tables](/docs/use-cases/archiving/).

## 4. Schema Evolution (`ALTER TABLE`) {#schema-evolution}

Only the following `ALTER TABLE` operations on the source rowstore table are automatically replicated to the columnstore mirror:

- `ALTER TABLE <src> ADD COLUMN <col> <type>`
- `ALTER TABLE <src> DROP COLUMN <col>`

Other DDL modifications (such as `ALTER COLUMN ... TYPE` or `RENAME COLUMN`) are not automatically propagated; drop and recreate the columnstore mirror (`DROP TABLE <dst>; CALL mooncake.create_table('<dst>', '<src>');`) when performing complex schema migrations.

## 5. Unsupported Data Types {#data-types}

While `pg_mooncake` supports all common PostgreSQL numeric, text, boolean, date/time, UUID, JSON/JSONB, and array types, the following types are currently unsupported or have caveats:

- PostgreSQL custom `ENUM` types and composite/domain types
- Geometric and network address types not mapped by `pg_duckdb`
- Very high-precision `NUMERIC` values exceeding DuckDB's `DECIMAL(38, s)` width

## 6. `mooncake.load_files` (`SQLSTATE 0A000`) {#load-files}

In `pg_mooncake 0.3.0`, calling `CALL mooncake.load_files(dst, files)` explicitly raises `SQLSTATE 0A000` (`ERRCODE_FEATURE_NOT_SUPPORTED`: `"mooncake.load_files is not implemented by the bundled Moonlink version"`).

- Previously, the bundled Moonlink server's `import_data` handler was a no-op stub that returned success without ingesting any rows.
- To load external Parquet or CSV files, either load them into the source PostgreSQL table with `COPY` / `INSERT INTO ... SELECT * FROM duckdb.read_parquet(...)`, or query them directly in place as described in [Query Your Data Lake in Postgres](/docs/reference/query-data-lake/).
