---
title: "Use Cases & Architecture Patterns"
linkTitle: "Use Cases"
description: "Production architecture patterns for pg_mooncake (v0.3.0): real-time operational analytics (HTAP), large table partition archiving, zero-ETL Postgres lakehouse, and OpenTelemetry log analytics."
weight: 40
icon: fa-solid fa-diagram-project
upstream_link: https://web.archive.org/web/20260124111154/https://docs.mooncake.dev/pg/use-cases/
aliases:
  - "/pg/use-cases/"
---

`pg_mooncake` enables four high-value analytical patterns directly inside PostgreSQL without introducing Kafka, Debezium, or an external data warehouse.

{{< cards >}}
{{< card title="Real-Time Operational Analytics" icon="fa-solid fa-bolt" link="/docs/use-cases/real-time-analytics/" >}}
Write to your primary OLTP rowstore table and route slow analytical aggregations to a sub-second `USING mooncake` columnstore mirror.
{{< /card >}}
{{< card title="Archiving Large Postgres Tables" icon="fa-solid fa-box-archive" link="/docs/use-cases/archiving/" >}}
Mirror a time-partitioned PostgreSQL table into object storage, drop old partitions from the rowstore to save disk space, and retain full queryable history in the columnstore.
{{< /card >}}
{{< card title="The Postgres Lakehouse" icon="fa-solid fa-cloud" link="/docs/use-cases/lakehouse/" >}}
Automatically export PostgreSQL tables as Apache Iceberg v2 tables on S3 or Cloudflare R2, and query external Iceberg/Delta Lake datasets inside Postgres.
{{< /card >}}
{{< card title="Log Analytics & OpenTelemetry" icon="fa-solid fa-file-waveform" link="/docs/use-cases/logging/" >}}
Ingest high-volume application logs and traces into PostgreSQL and run fast vectorized analytical queries over object-storage-backed Parquet files.
{{< /card >}}
{{< /cards >}}
