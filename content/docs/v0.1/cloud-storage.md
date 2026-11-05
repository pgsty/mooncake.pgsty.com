---
title: "v0.1 Cloud Storage (mooncake.create_secret)"
linkTitle: "v0.1 Cloud Storage"
description: "Configuring S3 and Cloudflare R2 buckets in pg_mooncake v0.1 using mooncake.create_secret and mooncake.default_bucket."
weight: 30
icon: fa-solid fa-cloud
upstream_link: https://web.archive.org/web/20251207090357/https://docs.mooncake.dev/pg/0.1/get-started/Cloud-storage
aliases:
  - "/pg/0.1/get-started/Cloud-storage/"
  - "/0.1/get-started/Cloud-storage/"
  - "/pg/0.1/get-started/cloud-storage/"
  - "/0.1/get-started/cloud-storage/"
---

> [!WARNING] Legacy `pg_mooncake v0.1` Archive (Delta Lake Engine)
> This page documents **`pg_mooncake v0.1`**, which used direct `CREATE TABLE ... USING columnstore` DDL and Delta Lake storage. Starting in `v0.2` and PGSTY's **`v0.3.0`** release, `pg_mooncake` uses [`moonlink`](/docs/intro/moonlink/) real-time columnstore mirrors (`CALL mooncake.create_table` + `USING mooncake`) and Apache Iceberg v2. For current documentation, see [Introduction](/docs/intro/) and [v0.1 vs v0.2 & v0.3](/docs/intro/0.1-vs-0.2/).

> [!NOTE] Current `v0.3.0` Cloud Storage Setup
> In `v0.2` and `v0.3.0`, credentials are inserted into `duckdb.secrets` rather than `mooncake.create_secret`. See [Iceberg & Object Storage](/docs/reference/iceberg/).

## S3 Buckets (`v0.1`)

```sql
SELECT mooncake.create_secret(
    '<name>', 'S3', '<key_id>', '<secret>',
    '{"REGION": "<s3-region>", "SCOPE": "s3://<bucket>"}'
);
```

For S3 Express buckets:

```sql
SELECT mooncake.create_secret(
    '<name>', 'S3', '<key_id>', '<secret>',
    '{"ENDPOINT": "s3express-use1-az6.us-east-1.amazonaws.com", "REGION": "us-east-1"}'
);
```

## Cloudflare R2 Buckets (`v0.1`)

```sql
SELECT mooncake.create_secret(
    '<name>', 'S3', '<key_id>', '<secret>',
    '{"ENDPOINT": "<ACCOUNT_ID>.r2.cloudflarestorage.com"}'
);
```

## Set Default Bucket

```sql
ALTER DATABASE <database> SET mooncake.default_bucket = 's3://<bucket>';
SHOW mooncake.default_bucket;
```

## S3 and R2 Parameters

| Parameter | Description | Required |
|:---|:---|:---:|
| `name` | Name for your credentials | Yes |
| `key_id` | S3 / R2 access key ID | Yes |
| `secret` | S3 / R2 secret access key | Yes |
| `REGION` | AWS region where your bucket is located | Yes |
| `ENDPOINT` | Custom endpoint for R2 or S3 Express | Yes (R2 / S3 Express) |
| `SCOPE` | Bucket prefix path to scope credentials (e.g. `s3://mybucket`) | No |
{.wide .expand}
