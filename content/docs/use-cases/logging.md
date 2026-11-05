---
title: "Log Analytics with OpenTelemetry"
linkTitle: "Log Analytics"
description: "Store and analyze high-volume application logs and OpenTelemetry traces in PostgreSQL with pg_mooncake and object-storage-backed Parquet columnstore mirrors."
weight: 40
icon: fa-solid fa-file-waveform
upstream_link: https://web.archive.org/web/20260124121327/https://docs.mooncake.dev/pg/use-cases/logging
aliases:
  - "/pg/use-cases/logging/"
---

PostgreSQL is rarely used for large-scale log analytics because uncompressed heap tables and indexes grow expensive quickly, and full-table scans over millions of log entries are slow.

With `pg_mooncake`, you can combine **partitioned PostgreSQL log ingestion** with an **object-storage-backed columnstore mirror**:

- **Low storage cost**: Historical logs are compressed into columnar Parquet files on S3, Cloudflare R2, or local disk.
- **Simple self-hosting**: Just PostgreSQL + object storage—no Elasticsearch or ClickHouse cluster required.
- **Fast vectorized scans**: DuckDB 2.0 scans millions of log records per second with segment elimination on timestamps.

## Implementation Pattern {#implementation}

Combine a time-partitioned rowstore table for log ingestion with a `USING mooncake` columnstore mirror for analytical queries:

```sql
-- 1. Create your partitioned log ingestion table
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

-- 2. Create the columnstore mirror for fast log analytics
CALL mooncake.create_table('application_logs_analytics', 'application_logs');

-- 3. Ingest logs into the rowstore table
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

-- 4. Run analytical queries against the columnstore mirror
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

As daily log partitions age out (for example, after 24 or 48 hours), drop the old partitions from `application_logs` (`DROP TABLE application_logs_2026_11_01;`) as described in [Archiving Large Postgres Tables](/docs/use-cases/archiving/). The complete log history remains queryable in `application_logs_analytics`.
