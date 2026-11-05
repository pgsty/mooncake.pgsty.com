---
title: "v0.1 数据归档方案"
linkTitle: "v0.1 数据归档"
description: "pg_mooncake v0.1 中将历史数据从行存表迁移至 USING columnstore 归档表的历史方案。"
weight: 80
icon: fa-solid fa-box-archive
upstream_link: https://web.archive.org/web/20251207093226/https://docs.mooncake.dev/pg/0.1/Use-cases/Archiving
aliases:
  - "/zh/pg/0.1/Use-cases/Archiving/"
  - "/zh/0.1/Use-cases/Archiving/"
  - "/zh/pg/0.1/use-cases/archiving/"
  - "/zh/0.1/use-cases/archiving/"
---

> [!WARNING] `pg_mooncake v0.1` 历史归档文档（Delta Lake 引擎）
> 本页归档的是早期 **`pg_mooncake v0.1`** 版本文档（采用直接 `CREATE TABLE ... USING columnstore` DDL 与 Delta Lake 存储）。从 `v0.2` 及 PGSTY 维护的 **`v0.3.0`** 版本起，`pg_mooncake` 已全面转向基于 [`moonlink`](/zh/docs/intro/moonlink/) 的实时列存镜像架构（`CALL mooncake.create_table` + `USING mooncake`）与 Apache Iceberg v2。最新文档请参阅[简介](/zh/docs/intro/)与 [v0.1 与 v0.2 / v0.3 架构演进对比](/zh/docs/intro/0.1-vs-0.2/)。

> [!TIP] 当前 `v0.3.0` 分区冷热归档方案
> 在 `v0.2` 与 `v0.3.0` 中，无需再手动编写 `INSERT INTO ... DELETE FROM` 迁移脚本，只需对分区表调用 `CALL mooncake.create_table` 并直接 `DROP` 旧分区即可。详见[大表分区冷热归档](/zh/docs/use-cases/archiving/)。

## `v0.1` 数据归档方式

```sql
-- 创建列存归档表
CREATE TABLE orders_archive (
    order_id INT,
    customer_id INT,
    order_date TIMESTAMP,
    amount NUMERIC(10, 2)
) USING columnstore;

-- 将历史数据拷贝至列存归档表
INSERT INTO orders_archive
SELECT * FROM orders
WHERE order_date < CURRENT_DATE - INTERVAL '1 year';

-- 从源表删除历史数据并回收空间
DELETE FROM orders
WHERE order_date < CURRENT_DATE - INTERVAL '1 year';
VACUUM FULL orders;
```
