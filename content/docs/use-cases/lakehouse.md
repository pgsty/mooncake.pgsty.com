---
title: "The Postgres Lakehouse"
linkTitle: "Postgres Lakehouse"
description: "Build a bidirectional Apache Iceberg v2 lakehouse in PostgreSQL: export operational Postgres tables to S3/R2 without Kafka or Debezium, and query external lakehouse tables in SQL."
weight: 30
icon: fa-solid fa-cloud
upstream_link: https://web.archive.org/web/20251207090603/https://docs.mooncake.dev/pg/use-cases/lakehouse
aliases:
  - "/pg/use-cases/lakehouse/"
---

The **Lakehouse** architecture stores data once in open table formats (**Apache Iceberg** or **Delta Lake**) on object storage so multiple compute engines—PostgreSQL, DuckDB, Apache Spark, Snowflake, Trino, and Python (Polars / PyIceberg)—can share the same dataset without copying it.

`pg_mooncake` makes PostgreSQL a first-class citizen of your lakehouse in **both directions**:

1. **Postgres $\rightarrow$ Iceberg Lakehouse (Zero-ETL Export)**: Replicate operational PostgreSQL tables directly into Apache Iceberg v2 tables on S3, Cloudflare R2, or local storage via [`moonlink`](/docs/intro/moonlink/).
2. **Lakehouse $\rightarrow$ Postgres (Direct In-DB Scan)**: Query external Parquet, Apache Iceberg, and Delta Lake tables directly from PostgreSQL and join them with live operational tables via [`pg_duckdb`](/docs/reference/query-data-lake/).

## 1. Export Operational Postgres Tables as Apache Iceberg v2 {#export}

Traditionally, landing PostgreSQL data in Apache Iceberg required deploying Debezium, Kafka, Schema Registry, and Spark/Flink consumers. With `pg_mooncake`, it takes three SQL commands:

```sql
-- 1. Configure your S3 or Cloudflare R2 bucket credentials
INSERT INTO duckdb.secrets (name, type, key_id, secret, region, scope)
VALUES ('lakehouse_s3', 'S3', '<ACCESS_KEY>', '<SECRET_KEY>', 'us-east-1', 's3://company-lakehouse');

SET mooncake.default_bucket = 's3://company-lakehouse/iceberg';

-- 2. Mirror your operational table into an Iceberg-backed columnstore table
CALL mooncake.create_table('customers_iceberg', 'customers');

-- 3. Flush an Iceberg v2 metadata snapshot for external engines
CALL mooncake.create_snapshot('customers_iceberg');
```

Inspect the generated warehouse path with `SELECT * FROM mooncake.list_tables();` and point Spark, Snowflake, Trino, or PyIceberg directly at `<iceberg_warehouse_location>/metadata/v*.metadata.json`.

## 2. Query External Lakehouse Tables Inside PostgreSQL {#import}

At the same time, your PostgreSQL applications can query tables written by Spark or Databricks in S3 and join them with live PostgreSQL heap tables:

```sql
SELECT duckdb.install_extension('iceberg');

SELECT
    c.customer_id,
    c.email,
    ml.churn_probability
FROM customers c
JOIN duckdb.iceberg_scan('s3://company-lakehouse/ml_features/churn_scores/metadata/v3.metadata.json') AS ml(
    customer_id BIGINT,
    churn_probability DOUBLE PRECISION
) ON c.customer_id = ml.customer_id
WHERE ml.churn_probability > 0.80;
```
