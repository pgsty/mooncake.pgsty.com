---
title: "PostgreSQL 湖仓一体 (The Postgres Lakehouse)"
linkTitle: "Postgres 湖仓一体"
description: "在 PostgreSQL 中构建双向 Apache Iceberg v2 湖仓一体架构：无需 Kafka 或 Debezium 即可将业务表实时导出至 S3/R2，并在 SQL 中直接关联外部湖仓表。"
weight: 30
icon: fa-solid fa-cloud
upstream_link: https://web.archive.org/web/20251207090603/https://docs.mooncake.dev/pg/use-cases/lakehouse
aliases:
  - "/zh/pg/use-cases/lakehouse/"
---

**湖仓一体（Lakehouse）**架构将数据以开放表格式（**Apache Iceberg** 或 **Delta Lake**）统一存储在对象存储上，使多个计算引擎——PostgreSQL、DuckDB、Apache Spark、Snowflake、Trino 以及 Python（Polars / PyIceberg）——能够共享同一份数据，而无需反复拷贝。

`pg_mooncake` 让 PostgreSQL 在**双向数据流**中都成为湖仓架构的一等公民：

1. **Postgres $\rightarrow$ Iceberg 数据湖（零 ETL 导出）**：通过 [`moonlink`](/zh/docs/intro/moonlink/) 将在线 PostgreSQL 业务表实时复制为 AWS S3、Cloudflare R2 或本地存储上的标准 Apache Iceberg v2 表。
2. **数据湖 $\rightarrow$ Postgres（库内直接联邦查询）**：通过 [`pg_duckdb`](/zh/docs/reference/query-data-lake/) 在 PostgreSQL 内直接扫描外部 Parquet、Apache Iceberg 与 Delta Lake 表，并与在线业务表实时 `JOIN`。

## 1. 将 Postgres 业务表零 ETL 导出为 Apache Iceberg v2 {#export}

在传统架构中，将 PostgreSQL 数据同步到 Apache Iceberg 需要部署 Debezium、Kafka、Schema Registry 以及 Spark/Flink 消费作业。使用 `pg_mooncake`，只需三条 SQL 命令：

```sql
-- 1. 配置 S3 或 Cloudflare R2 存储桶凭据
INSERT INTO duckdb.secrets (name, type, key_id, secret, region, scope)
VALUES ('lakehouse_s3', 'S3', '<ACCESS_KEY>', '<SECRET_KEY>', 'us-east-1', 's3://company-lakehouse');

SET mooncake.default_bucket = 's3://company-lakehouse/iceberg';

-- 2. 将在线业务表镜像为基于 Iceberg 的列存表
CALL mooncake.create_table('customers_iceberg', 'customers');

-- 3. 刷写生成供外部引擎读取的 Iceberg v2 元数据快照
CALL mooncake.create_snapshot('customers_iceberg');
```

通过 `SELECT * FROM mooncake.list_tables();` 查看生成的仓库路径后，Spark、Snowflake、Trino 或 PyIceberg 即可直接读取 `<iceberg_warehouse_location>/metadata/v*.metadata.json`。

## 2. 在 PostgreSQL 内直接关联查询外部湖仓表 {#import}

与此同时，你的 PostgreSQL 应用也可以直接查询由外部 Spark 或机器学习流水线写入 S3 的 Iceberg 表，并与本地实时行存表直接关联：

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
