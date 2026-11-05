---
title: "Moonlink 实时摄取引擎"
linkTitle: "Moonlink 引擎"
description: "深入剖析 Moonlink (v0.0.1)：实时 CDC 数据摄取、Arrow 内存写缓冲、Roaring 删除向量、LSN 快照屏障与独立 HTTP/RPC 服务部署。"
weight: 20
icon: fa-solid fa-arrows-rotate
upstream_source: moonlink
upstream_link: https://github.com/Mooncake-Labs/moonlink
aliases:
  - "/zh/moonlink/intro/"
  - "/zh/intro/moonlink/"
  - "/zh/moonlink/"
---

**Moonlink**（[`pgsty/moonlink`](https://github.com/pgsty/moonlink)，当前正式版本 **`v0.0.1`**）是一个使用 Rust 编写的高性能实时列存摄取库与独立服务，旨在无需引入 Apache Spark 或 Kafka 的前提下，面向在线业务系统与事件流实时构建并维护 **Apache Iceberg v2** 与 **Delta Lake** 表。

在 [`pg_mooncake`](/zh/docs/intro/) 内部，Moonlink 作为内嵌的 PostgreSQL 后台工作进程（`mooncake_bgworker`）运行，并通过本地 Unix 域套接字（`$PGDATA/pg_mooncake/moonlink.sock`）提供低延迟 RPC 通信；同时，它也可以独立编译并部署为对外提供 HTTP REST 与 gRPC 接口的摄取服务（`moonlink_service`）。

> [!NOTE] 开源许可证说明（`BSL-1.1` 附带 `pg_mooncake` 链接与分发豁免）
> 核心 `moonlink` 服务端引擎采用 **BSL-1.1** 许可证（将于 `2029-05-05` 自动转换为 **Apache-2.0**），并附带明确的 **`PG_MOONCAKE LINKING & DISTRIBUTION EXCEPTION`（链接与分发豁免条款）**，允许在作为 `pg_mooncake` 的一部分嵌入或分发时不受限制地链接、修改与再分发。其协议与客户端库（`moonlink_rpc`、`moonlink_proto`、`moonlink_error`、`moonlink_table_metadata`）均采用 **MIT** 许可证。完整条款请参阅[许可证说明](/zh/docs/about/license/)。

## 核心设计原理 {#design}

传统数据湖写入器在**数据新鲜度（Freshness）**与**查询性能（Query Performance）**之间面临天然矛盾：如果每次单行写入都立即刷盘，会产生数以万计的微小 Parquet 文件；如果攒批 5–15 分钟再写入，又无法满足实时分析的延迟要求。

Moonlink 通过多级存储架构彻底消除了这一矛盾：

1. **内存 Apache Arrow 写缓冲区**：实时流入的 `INSERT` 与 `UPDATE` 新行首先追加至内存中的 Arrow `RecordBatch` 写缓冲区（`write_buffer_size`，默认 `32 MB`）。读取端（`duckdb_mooncake`）无需等待刷盘即可通过零拷贝 Arrow 接口直接扫描最新数据。
2. **基于 Roaring Bitmap 的删除向量（Deletion Vectors）**：面对高频 `UPDATE` 与 `DELETE`，Moonlink 无需重写已有 Parquet 文件，而是通过 B-Tree 主键索引（`moonlink_btree`）定位旧行偏移量，并将其记录在压缩的 **Roaring Bitmap 删除向量**中。
3. **LSN 位点追踪与非阻塞快照屏障**：从 PostgreSQL WAL 摄取的每一笔事务均带有提交 `lsn` 标记。查询在调用 `scan_table_begin` 时传入目标 LSN，仅当逻辑复制尚未追平该 LSN 时才短暂等待，确保强一致性读取。
4. **后台异步合并与 Iceberg v2 元数据输出**：后台合并任务自动将刷盘后的 Parquet 文件段合并为大文件、清理已标记删除的行，并在本地磁盘或 S3/R2 对象存储上生成标准 **Apache Iceberg v2** `metadata.json` 与 Avro 清单文件。

## `moonlink v0.0.1` 的核心工程修复 {#v001-fixes}

在 PGSTY 发布的 **`moonlink v0.0.1`**（`b298ef7444890e3c8af5544e350232518bcfd8e5`）版本中，包含了以下关键工程修复：

- **修复其他表推进数据库 WAL 时 `create_snapshot(lsn)` 挂起的问题**：此前，当数据库内其他无关表发生写入导致全局 WAL LSN 推进，而目标列存镜像表没有新事务提交时，调用 `CALL mooncake.create_snapshot('table')` 会无限期等待目标表达到最新数据库 LSN。在 `v0.0.1` 中，复制流进度通知会自动推进表级安全 LSN 水位线并立即刷写已提交的旧数据，即使该表后续没有新事务提交也能正常完成快照。
- **58/58 表处理器单元测试全部通过**：在 Rocky Linux 10（`aarch64`）与 Ubuntu 24.04（`aarch64`）环境下全面验证了追加、更新、删除、回滚、文件合并与快照屏障场景。
- **RustSec 依赖安全升级**：升级修复了 `bytes`、`crossbeam-epoch`、`h2`、`lz4_flex`、`quinn-proto`、`rustls`、`rustls-webpki`、`webpki-roots`、`time`、`zstd`、`anyhow`、`event-listener`、`lru`（`0.18.5`）、`memmap2`、`rand`、`tokio`（`1.51.6`）、`aws-lc-rs` 与 `serial_test` 等 20 余项安全公告。

## 独立服务部署（`moonlink_service`） {#standalone}

除了内嵌在 `pg_mooncake` 中运行外，你也可以将 `moonlink_service` 作为独立摄取服务器运行，通过 HTTP REST 或 gRPC 流式写入 Iceberg 表。

### 从源码编译 `moonlink_service` {#build}

```bash
git clone https://github.com/pgsty/moonlink.git
cd moonlink
cargo build --release -p moonlink_service
./target/release/moonlink_service
```

### 独立 REST API 使用示例 {#rest-api}

独立服务默认监听 `3030` 端口，提供表创建、实时行写入与 Iceberg 快照生成的 JSON 接口：

```python
import json
import requests

BASE_URL = "http://localhost:3030"

# 1. 创建 Moonlink Iceberg 表
create_payload = {
    "database": "default",
    "table": "events",
    "schema": {
        "fields": [
            {"name": "id", "data_type": "Int64", "nullable": False},
            {"name": "service", "data_type": "Utf8", "nullable": False},
            {"name": "latency_ms", "data_type": "Float64", "nullable": True},
        ],
        "primary_key": ["id"],
    },
    "table_config": {
        "write_buffer_size": 33554432,
        "iceberg_warehouse_location": "/tmp/moonlink_warehouse",
    },
}
resp = requests.post(f"{BASE_URL}/tables", json=create_payload)
resp.raise_for_status()

# 2. 实时写入或更新行数据
insert_payload = {
    "database": "default",
    "table": "events",
    "row": {"id": 1, "service": "checkout", "latency_ms": 12.4},
}
resp = requests.post(f"{BASE_URL}/insert", json=insert_payload)
resp.raise_for_status()

# 3. 触发生成 Iceberg v2 快照
snapshot_payload = {
    "database": "default",
    "table": "events",
    "lsn": resp.json().get("lsn", 1),
}
requests.post(f"{BASE_URL}/snapshot", json=snapshot_payload).raise_for_status()
```

### 使用 DuckDB 直接查询生成的 Iceberg 快照 {#query-iceberg}

快照生成后，任何兼容 Apache Iceberg 的计算引擎（DuckDB、Spark、Trino、Snowflake、PyIceberg）均可直接读取该表：

```sql
INSTALL iceberg;
LOAD iceberg;

SELECT service, COUNT(*), AVG(latency_ms)
FROM iceberg_scan('/tmp/moonlink_warehouse/default/events/metadata/v2.metadata.json')
GROUP BY service;
```
