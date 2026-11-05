---
title: "日志分析与 OpenTelemetry"
linkTitle: "日志与可观测性分析"
description: "结合 pg_mooncake 列存镜像与对象存储 Parquet 压缩，在 PostgreSQL 中以极低成本存储并分析海量应用日志与 OpenTelemetry 链路数据。"
weight: 40
icon: fa-solid fa-file-waveform
upstream_link: https://web.archive.org/web/20260124121327/https://docs.mooncake.dev/pg/use-cases/logging
aliases:
  - "/zh/pg/use-cases/logging/"
---

在传统架构中，人们很少使用 PostgreSQL 承载大规模日志分析，因为行存堆表与索引的磁盘占用增长极快，且对数千万条日志执行全表聚合扫描非常缓慢。

借助 `pg_mooncake`，你可以将**按时间分区的 PostgreSQL 行存写入**与**基于对象存储的列存镜像**结合起来：

- **极低存储成本**：历史日志以高压缩比的列式 Parquet 格式保存在 S3、Cloudflare R2 或本地磁盘上。
- **架构极简**：只需 PostgreSQL + 对象存储，无需额外部署运维 Elasticsearch 或 ClickHouse 集群。
- **高速向量化检索**：利用 DuckDB 2.0 的时间戳分段跳过（Segment Elimination）与向量化扫描，每秒可扫描数百万条日志记录。

## 推荐实现方案 {#implementation}

使用按天/按小时分区的行存表承接实时日志写入，并创建 `USING mooncake` 列存镜像表执行聚合检索：

```sql
-- 1. 创建按时间分区的日志写入表
CREATE TABLE application_logs (
    log_id BIGSERIAL,
    timestamp TIMESTAMPTZ NOT NULL,
    level TEXT NOT NULL,
    service TEXT NOT NULL,
    message TEXT,
    trace_id TEXT,
    span_id TEXT,
    attributes JSONB,
    PRIMARY KEY (log_id, timestamp)
) PARTITION BY RANGE (timestamp);

CREATE TABLE application_logs_today PARTITION OF application_logs
    FOR VALUES FROM ('2026-11-05') TO ('2026-11-06');

-- 2. 创建用于快速聚合检索的列存镜像表
CALL mooncake.create_table('application_logs_analytics', 'application_logs');

-- 3. 将日志写入行存表
INSERT INTO application_logs (timestamp, level, service, message, trace_id, span_id, attributes)
VALUES (
    NOW(),
    'ERROR',
    'api-service',
    'Database connection timeout',
    'trace-123',
    'span-456',
    '{"user_id": 1001, "region": "us-east-1"}'
);

-- 4. 在列存镜像表上执行高速聚合分析
SELECT
    service,
    level,
    COUNT(*) AS error_count
FROM application_logs_analytics
WHERE timestamp >= NOW() - INTERVAL '1 hour'
  AND level = 'ERROR'
GROUP BY service, level
ORDER BY error_count DESC;
```

当每日日志分区超过热保留窗口（例如 24 或 48 小时后），可按照[大表分区冷热归档](/zh/docs/use-cases/archiving/)模式直接从行存中删除旧分区（`DROP TABLE application_logs_2026_11_01;`），而完整的历史日志依然保留在 `application_logs_analytics` 中供长期回溯分析。
