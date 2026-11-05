---
title: "Welcome to pg_mooncake"
linkTitle: "Introduction"
description: "Overview of pg_mooncake (v0.3.0), real-time columnstore mirror tables, Moonlink CDC ingestion, and DuckDB 2.0 vectorized execution in PostgreSQL."
weight: 10
icon: fa-solid fa-compass
upstream_link: https://web.archive.org/web/20251207085834/https://docs.mooncake.dev/pg/intro/
aliases:
  - "/pg/intro/"
  - "/intro/"
  - "/pg/"
---

**`pg_mooncake`** is a PostgreSQL extension that adds **real-time columnstore mirror tables** (`USING mooncake`), **DuckDB 2.0** vectorized analytical execution (via [`pg_duckdb`](https://pgext.cloud/e/pg_duckdb) and [`duckdb_mooncake`](/docs/intro/duckdb-mooncake/)), and open **Apache Iceberg v2** storage (powered by [`moonlink`](/docs/intro/moonlink/)) directly inside PostgreSQL.

PostgreSQL with `pg_mooncake` ranks among the fastest analytical databases on ClickBench while keeping your existing PostgreSQL transactional write path untouched. Originally created by [Mooncake Labs](https://github.com/Mooncake-Labs), the extension suite (`pg_mooncake v0.3.0`, `duckdb_mooncake v0.0.2`, and `moonlink v0.0.1`) is now maintained by the [PGSTY](https://pigsty.io/) community for **PostgreSQL 14–18**.

> [!NOTE] PGSTY Maintained Suite (`v0.3.0`)
> - **[`pgsty/pg_mooncake`](https://github.com/pgsty/pg_mooncake)** (`v0.3.0`, `MIT`): PostgreSQL extension providing the `USING mooncake` table access method, `mooncake.*` SQL procedures, and the embedded Moonlink background worker (`pgrx 0.19.3`).
> - **[`pgsty/moonlink`](https://github.com/pgsty/moonlink)** (`v0.0.1`, `BSL-1.1` with [`pg_mooncake` Linking Exception](/docs/about/license/)): Real-time Rust storage engine that ingests PostgreSQL logical replication streams into in-memory Arrow buffers, Roaring Bitmap deletion vectors, and Apache Iceberg v2 / Parquet files.
> - **[`pgsty/duckdb_mooncake`](https://github.com/pgsty/duckdb_mooncake)** (`v0.0.2`, `MIT`): DuckDB 2.0 storage extension bundled with `pg_mooncake` that scans Moonlink tables with multi-file Parquet statistics pruning.

## The Problem {#problem}

PostgreSQL is an exceptional transactional (OLTP) database, but its row-oriented heap storage and tuple-at-a-time executor are not designed for large-scale analytical scans (OLAP). Historically, PostgreSQL teams faced two flawed choices:

1. **Adopt a separate analytical system (ClickHouse, Snowflake, BigQuery)**
   Requires maintaining fragile CDC pipelines (Debezium + Kafka), duplicating data models, dealing with eventual consistency lag, and losing the ability to join live operational tables with analytical history in a single query.
2. **Use in-database columnstores without vectorized execution or real-time CDC**
   Traditional columnar extensions either lack a modern vectorized execution engine or cannot handle high-frequency transactional `INSERT`, `UPDATE`, and `DELETE` operations without generating thousands of tiny Parquet files.

![pg_mooncake Venn Diagram](/img/mooncake/pg_mooncake_intro.jpg)

## How `pg_mooncake` Solves It {#solution}

Starting in `v0.2` and refined in PGSTY's **`v0.3.0`** release, `pg_mooncake` introduces a **columnstore mirror** architecture:

```sql
-- 1. Enable pg_mooncake (automatically loads pg_duckdb 1.2.0)
CREATE EXTENSION IF NOT EXISTS pg_mooncake CASCADE;

-- 2. Your regular OLTP rowstore table remains unchanged
CREATE TABLE trades (
    id BIGINT PRIMARY KEY,
    symbol TEXT,
    price DOUBLE PRECISION,
    volume INT,
    traded_at TIMESTAMPTZ
);

-- 3. Create a real-time columnstore mirror in one command
CALL mooncake.create_table('trades_analytics', 'trades');
```

1. **Write to Rowstore, Read from Columnstore**: Your application continues writing (`INSERT`, `UPDATE`, `DELETE`) to the standard PostgreSQL `trades` heap table with full ACID guarantees and indexes.
2. **Sub-Second Logical Replication via Moonlink**: Behind the scenes, `pg_mooncake`'s background worker streams WAL changes into `moonlink`, buffering recent mutations in memory as **Apache Arrow** batches and tracking updates/deletes via **Roaring Bitmap deletion vectors** before compacting into **Parquet** files.
3. **Vectorized DuckDB 2.0 Queries**: Analytical queries against `trades_analytics` are routed through `pg_duckdb 1.2.0` and `duckdb_mooncake v0.0.2`, merging in-memory Arrow buffers and on-disk Parquet segments with segment elimination and LSN consistency barriers.
4. **Open Apache Iceberg v2 Lakehouse**: With `CALL mooncake.create_snapshot('trades_analytics')`, Moonlink emits standard Apache Iceberg v2 metadata on local disk, AWS S3, or Cloudflare R2—ready for Spark, Snowflake, DuckDB, or PyIceberg without any ETL pipeline.

## Explore This Section {#explore}

{{< cards >}}
{{< card title="System Architecture" icon="fa-solid fa-sitemap" link="/docs/intro/architecture/" >}}
Understand how `pg_mooncake`, `pg_duckdb`, `duckdb_mooncake`, and `moonlink` coordinate writes, reads, and Iceberg snapshots.
{{< /card >}}
{{< card title="Moonlink Ingestion Engine" icon="fa-solid fa-arrows-rotate" link="/docs/intro/moonlink/" >}}
Deep dive into Moonlink (`v0.0.1`), in-memory Arrow write buffers, deletion vectors, and standalone HTTP/RPC server deployment.
{{< /card >}}
{{< card title="duckdb_mooncake & DuckDB 2.0" icon="fa-solid fa-database" link="/docs/intro/duckdb-mooncake/" >}}
Learn how `duckdb_mooncake v0.0.2` integrates with DuckDB 2.0 and `pg_duckdb 1.2.0` for vectorized scans and Parquet statistics pruning.
{{< /card >}}
{{< card title="v0.1 vs v0.2 & v0.3 Evolution" icon="fa-solid fa-code-compare" link="/docs/intro/0.1-vs-0.2/" >}}
Compare the legacy `v0.1` Delta Lake (`USING columnstore`) architecture with `v0.2` Moonlink mirrors and PGSTY's `v0.3.0` enhancements.
{{< /card >}}
{{< /cards >}}
