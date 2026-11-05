---
title: "v0.1 云端对象存储配置 (mooncake.create_secret)"
linkTitle: "v0.1 对象存储配置"
description: "在 pg_mooncake v0.1 中使用 mooncake.create_secret 与 mooncake.default_bucket 配置 S3 与 Cloudflare R2 存储桶。"
weight: 30
icon: fa-solid fa-cloud
upstream_link: https://web.archive.org/web/20251207090357/https://docs.mooncake.dev/pg/0.1/get-started/Cloud-storage
aliases:
  - "/zh/pg/0.1/get-started/Cloud-storage/"
  - "/zh/0.1/get-started/Cloud-storage/"
  - "/zh/pg/0.1/get-started/cloud-storage/"
  - "/zh/0.1/get-started/cloud-storage/"
---

> [!WARNING] `pg_mooncake v0.1` 历史归档文档（Delta Lake 引擎）
> 本页归档的是早期 **`pg_mooncake v0.1`** 版本文档（采用直接 `CREATE TABLE ... USING columnstore` DDL 与 Delta Lake 存储）。从 `v0.2` 及 PGSTY 维护的 **`v0.3.0`** 版本起，`pg_mooncake` 已全面转向基于 [`moonlink`](/zh/docs/intro/moonlink/) 的实时列存镜像架构（`CALL mooncake.create_table` + `USING mooncake`）与 Apache Iceberg v2。最新文档请参阅[简介](/zh/docs/intro/)与 [v0.1 与 v0.2 / v0.3 架构演进对比](/zh/docs/intro/0.1-vs-0.2/)。

> [!NOTE] 当前 `v0.3.0` 对象存储配置方式
> 在 `v0.2` 与 `v0.3.0` 中，对象存储凭据通过 `duckdb.secrets` 表管理，不再使用 `mooncake.create_secret`。最新说明请参阅 [Iceberg 与对象存储配置](/zh/docs/reference/iceberg/)。

## 配置 Amazon S3 存储桶（`v0.1`）

```sql
SELECT mooncake.create_secret(
    '<name>', 'S3', '<key_id>', '<secret>',
    '{"REGION": "<s3-region>", "SCOPE": "s3://<bucket>"}'
);
```

针对 S3 Express 存储桶：

```sql
SELECT mooncake.create_secret(
    '<name>', 'S3', '<key_id>', '<secret>',
    '{"ENDPOINT": "s3express-use1-az6.us-east-1.amazonaws.com", "REGION": "us-east-1"}'
);
```

## 配置 Cloudflare R2 存储桶（`v0.1`）

```sql
SELECT mooncake.create_secret(
    '<name>', 'S3', '<key_id>', '<secret>',
    '{"ENDPOINT": "<ACCOUNT_ID>.r2.cloudflarestorage.com"}'
);
```

## 设置默认存储桶

```sql
ALTER DATABASE <database> SET mooncake.default_bucket = 's3://<bucket>';
SHOW mooncake.default_bucket;
```

## S3 与 R2 参数说明

| 参数名 | 说明 | 是否必填 |
|:---|:---|:---:|
| `name` | 凭据名称 | 是 |
| `key_id` | S3 / R2 Access Key ID | 是 |
| `secret` | S3 / R2 Secret Access Key | 是 |
| `REGION` | S3 存储桶所在区域 | 是 |
| `ENDPOINT` | R2 或 S3 Express 自定义端点 | 是（R2 / S3 Express） |
| `SCOPE` | 凭据生效的存储桶路径前缀（如 `s3://mybucket`） | 否 |
{.wide .expand}
