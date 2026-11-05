---
title: "PostgreSQL 大表分区冷热归档"
linkTitle: "大表分区归档"
description: "利用 pg_mooncake 将按时间分区的 PostgreSQL 大表归档为 Parquet 与 Apache Iceberg 格式，直接删除旧行存分区释放磁盘，同时在列存镜像中完整保留全部历史数据。"
weight: 20
icon: fa-solid fa-box-archive
upstream_link: https://web.archive.org/web/20251207100724/https://docs.mooncake.dev/pg/use-cases/archiving
aliases:
  - "/zh/pg/use-cases/archiving/"
  - "/zh/reference/archive-into-columnstore/"
---

`pg_mooncake` 的列存镜像表将数据写为高压缩比的 Parquet 文件（保存在本地磁盘或 AWS S3 / Cloudflare R2 对象存储上），使你能够在 PostgreSQL 行存中仅保留近期热分区，同时在列存镜像中以极低成本持久化保留完整的历史数据。

## 架构设计模式 {#pattern}

分区冷热归档模式遵循以下三条核心原则：

1. **为按时间或范围分区的 PostgreSQL 表创建列存镜像**（`CALL mooncake.create_table`）。
2. **定期从行存中 `DROP` 或 `TRUNCATE` 过期旧分区**，立即释放昂贵的本地 NVMe / SSD 空间，避免 `VACUUM FULL` 锁表开销。
3. **在列存镜像中完整保留全部历史数据**——`pg_mooncake` 会**有意忽略**针对分区源表子分区的 `DROP TABLE` 与 `TRUNCATE` 事件，因此被删除分区的历史行依然完整保留在列存镜像中并可随时查询！

## 完整实操示例 {#walkthrough}

下面以一张按范围分区的 `transactions` 交易流水表为例演示完整归档流程。

### 第 1 步：创建分区行存表 {#step-1}

```sql
CREATE TABLE transactions (
    id INT,
    amount DECIMAL(10, 2),
    user_id INT,
    created_at TIMESTAMP,
    PRIMARY KEY (id)
) PARTITION BY RANGE (id);
```

### 第 2 步：创建实时列存镜像表 {#step-2}

```sql
CALL mooncake.create_table('transactions_archive', 'transactions');
```

### 第 3 步：创建第一个子分区并写入数据 {#step-3}

```sql
-- 创建承载 ID 0..50 的第一个子分区
CREATE TABLE transactions_p1 PARTITION OF transactions
    FOR VALUES FROM (0) TO (50);

-- 插入示例交易数据
INSERT INTO transactions_p1 VALUES
    (1, 99.99, 101, '2024-01-01 10:00:00'),
    (2, 150.50, 102, '2024-01-01 11:00:00'),
    (3, 75.25, 103, '2024-01-01 12:00:00');
```

### 第 4 步：从行存中直接删除历史旧分区 {#step-4}

当 `transactions_p1` 变为历史冷数据、需要回收 PostgreSQL 本地磁盘空间时：

```sql
-- 直接从行存中删除旧子分区
DROP TABLE transactions_p1;
```

### 第 5 步：在列存镜像中查询历史数据 {#step-5}

尽管 `transactions_p1` 已从行存中删除，但它的全部历史记录依然完好地保存在 `transactions_archive` 中：

```sql
SELECT * FROM transactions_archive ORDER BY id;
```

### 第 6 步：继续挂载新分区并写入增量数据 {#step-6}

```sql
-- 为近期新数据创建第二个子分区
CREATE TABLE transactions_p2 PARTITION OF transactions
    FOR VALUES FROM (50) TO (100);

-- 注意：如果分区表没有主键，在向新建子分区执行 UPDATE/DELETE 前请先设置：
-- ALTER TABLE transactions_p2 REPLICA IDENTITY FULL;

INSERT INTO transactions_p2 VALUES
    (51, 200.00, 104, '2024-01-02 10:00:00'),
    (52, 89.99, 105, '2024-01-02 11:00:00'),
    (53, 125.75, 106, '2024-01-02 12:00:00');

-- 查询列存镜像表，将同时返回全部 6 条历史与最新数据
SELECT * FROM transactions_archive ORDER BY id;
```

## 最佳实践 {#best-practices}

- **切勿向已删除分区的键范围重复写入冲突数据**：在删除或清空某个旧行存分区后，请勿重新创建相同范围的分区并写入重复主键，因为已删除分区的历史行仍保留在列存镜像中。
- **使用声明式分区表管理归档生命周期**：`pg_mooncake` 专门针对分区子表的 `DROP` / `TRUNCATE` 做了归档保留处理。
- **配合 S3 / R2 对象存储实现无限容量归档**：在创建镜像前设置 `mooncake.default_bucket = 's3://...'`，即可将所有历史 Parquet 文件与 Iceberg 元数据直接存储在廉价的云端对象存储上。详见 [Iceberg 与对象存储配置](/zh/docs/reference/iceberg/)。
