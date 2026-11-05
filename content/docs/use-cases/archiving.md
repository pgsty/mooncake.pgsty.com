---
title: "Archiving Large Postgres Tables"
linkTitle: "Archiving Large Tables"
description: "Archive time-partitioned PostgreSQL tables into Parquet and Apache Iceberg storage with pg_mooncake, dropping cold partitions from the rowstore while retaining full history in the columnstore."
weight: 20
icon: fa-solid fa-box-archive
upstream_link: https://web.archive.org/web/20251207100724/https://docs.mooncake.dev/pg/use-cases/archiving
aliases:
  - "/pg/use-cases/archiving/"
  - "/reference/archive-into-columnstore/"
---

`pg_mooncake`'s columnstore mirror writes data as compressed Parquet files (on local disk or S3 / Cloudflare R2 object storage), providing cost-effective, durable history while PostgreSQL heap storage only maintains hot recent partitions.

## Architecture Pattern {#pattern}

The partition archiving pattern follows three rules:

1. **Create a columnstore mirror** (`CALL mooncake.create_table`) of a time- or range-partitioned PostgreSQL table.
2. **Periodically `DROP` or `TRUNCATE` old partitions** from the PostgreSQL rowstore once they age out of your hot operational window.
3. **Retain complete history in the columnstore mirror**—`pg_mooncake` intentionally ignores `DROP TABLE` and `TRUNCATE` events on child partitions of a partitioned source table, so all historical rows remain queryable in the columnstore!

## Step-by-Step Walkthrough {#walkthrough}

Below is a complete example using a range-partitioned `transactions` table.

### Step 1: Create a Partitioned Rowstore Table {#step-1}

```sql
CREATE TABLE transactions (
    id INT,
    amount DECIMAL(10, 2),
    user_id INT,
    created_at TIMESTAMP,
    PRIMARY KEY (id)
) PARTITION BY RANGE (id);
```

### Step 2: Create a Columnstore Mirror {#step-2}

```sql
CALL mooncake.create_table('transactions_archive', 'transactions');
```

### Step 3: Add First Partition & Insert Data {#step-3}

```sql
-- Create first partition for IDs 0..50
CREATE TABLE transactions_p1 PARTITION OF transactions
    FOR VALUES FROM (0) TO (50);

-- Insert sample data
INSERT INTO transactions_p1 VALUES
    (1, 99.99, 101, '2024-01-01 10:00:00'),
    (2, 150.50, 102, '2024-01-01 11:00:00'),
    (3, 75.25, 103, '2024-01-01 12:00:00');
```

### Step 4: Drop the Old Partition from Rowstore {#step-4}

When `transactions_p1` is cold and you want to reclaim PostgreSQL disk space immediately:

```sql
-- Drop the old partition from the PostgreSQL rowstore
DROP TABLE transactions_p1;
```

### Step 5: Query Historical Data in the Columnstore {#step-5}

Even though `transactions_p1` was dropped from the rowstore, all three rows remain intact in `transactions_archive`:

```sql
SELECT * FROM transactions_archive ORDER BY id;
```

### Step 6: Continue with New Partitions {#step-6}

```sql
-- Add new partition for recent data
CREATE TABLE transactions_p2 PARTITION OF transactions
    FOR VALUES FROM (50) TO (100);

-- Note: if your partitioned table does NOT have a primary key, set REPLICA IDENTITY FULL
-- on newly added partitions before running UPDATE/DELETE:
-- ALTER TABLE transactions_p2 REPLICA IDENTITY FULL;

INSERT INTO transactions_p2 VALUES
    (51, 200.00, 104, '2024-01-02 10:00:00'),
    (52, 89.99, 105, '2024-01-02 11:00:00'),
    (53, 125.75, 106, '2024-01-02 12:00:00');

-- Querying the columnstore returns all 6 historical + recent rows
SELECT * FROM transactions_archive ORDER BY id;
```

## Best Practices {#best-practices}

- **Never re-insert overlapping keys into dropped partition ranges**: After dropping or truncating a rowstore partition, do not recreate a partition covering the same key range and insert conflicting rows, as the historical rows from the dropped partition are still retained in the columnstore.
- **Always use declarative partitioned tables for archiving**: `pg_mooncake` safely ignores partition drops and truncates on partitioned tables.
- **Pair with S3 / R2 object storage**: Set `mooncake.default_bucket = 's3://...'` before creating the mirror so archived partitions are stored directly in low-cost cloud object storage. See [Iceberg & Object Storage](/docs/reference/iceberg/).
