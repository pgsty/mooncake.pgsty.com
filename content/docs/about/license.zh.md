---
title: "开源许可"
linkTitle: "开源许可"
description: "pg_mooncake、duckdb_mooncake、moonlink 与 mooncake.pgsty.com 的开源与源码可用许可证详情。"
weight: 20
icon: "fa-solid fa-scale-balanced"
---

PGSTY Mooncake 生态完整保留了 Mooncake Labs, Inc. 为各个代码仓库设定的上游许可证条款。

---

## 各仓库许可证总览

| 组件 | 代码仓库 | 许可证 | 说明 |
|:---|:---|:---|:---|
| **`pg_mooncake`** | [`pgsty/pg_mooncake`](https://github.com/pgsty/pg_mooncake) | **`MIT`** | 宽松开源许可证（`Copyright (c) 2024 Mooncake Labs`）。 |
| **`duckdb_mooncake`** | [`pgsty/duckdb_mooncake`](https://github.com/pgsty/duckdb_mooncake) | **`MIT`** | 宽松开源许可证（`Copyright (c) 2025 Mooncake Labs`）。 |
| **`moonlink`（核心引擎）** | [`pgsty/moonlink`](https://github.com/pgsty/moonlink) | **`BSL-1.1` + 链接豁免** | Business Source License 1.1，附带 **`PG_MOONCAKE LINKING & DISTRIBUTION EXCEPTION`**，将于 **`2029-05-05`** 自动转换为 **`Apache-2.0`**。 |
| **`moonlink`（客户端 Crate）** | `moonlink_rpc`、`moonlink_proto`、`moonlink_error`、`moonlink_table_metadata` | **`MIT`** | 显式采用 MIT 许可，确保 `pg_mooncake` 与 `duckdb_mooncake` 链接客户端接口时保持纯 MIT 属性。 |
| **伴生文档站** | [`pgsty/mooncake.pgsty.com`](https://github.com/pgsty/mooncake.pgsty.com) | **`CC-BY-4.0` / `Apache-2.0`** | 文档正文采用知识共享署名 4.0 国际许可协议（`CC-BY-4.0`）；站点构建脚本采用 `Apache-2.0`。 |
{.wide .expand}

---

## `pg_mooncake` 与 `duckdb_mooncake` — MIT 许可证

[`pg_mooncake`](https://github.com/pgsty/pg_mooncake/blob/main/LICENSE) 与 [`duckdb_mooncake`](https://github.com/pgsty/duckdb_mooncake/blob/main/LICENSE) 均采用 **MIT License** 发布：

```text
MIT License

Copyright (c) 2024-2025 Mooncake Labs

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## `moonlink` — Business Source License 1.1 与 `pg_mooncake` 链接豁免

[`moonlink`](https://github.com/pgsty/moonlink/blob/main/LICENSE) 采用 **Business Source License 1.1 (`BSL-1.1`)** 并附带 **`PG_MOONCAKE LINKING & DISTRIBUTION EXCEPTION`**：

- **许可方（Licensor）**：Mooncake Labs, Inc.
- **受许可作品（Licensed Work）**：`moonlink` (`v0.0.1`)
- **转换日期（Change Date）**：`2029-05-05`
- **转换后许可证（Change License）**：`Apache-2.0`（Apache License, Version 2.0）

### 附加使用授权（Additional Use Grant）

- 您可以在组织内部（包括生产环境）自由使用 `moonlink`，也可以将其集成到向第三方提供的软件应用或服务中，前提是该服务不将 `moonlink` 本身作为竞争性托管云服务（Managed Service / DBaaS / SaaS）向第三方直接售卖。

### `PG_MOONCAKE LINKING & DISTRIBUTION EXCEPTION`（链接与分发豁免）

由于 `pg_mooncake` 通过 FFI（`pg_mooncake_moonlink_ffi`）内嵌了 `moonlink`，且 `duckdb_mooncake` 链接了 `moonlink_ffi`，上游许可证专门提供了以下豁免条款：

1. **MIT 客户端 Crate**：仓库中的客户端接口 crate（`moonlink_rpc`、`moonlink_proto`、`moonlink_error` 与 `moonlink_table_metadata`）单独采用 **MIT** 许可，不属于 BSL-1.1 受限范围。
2. **链接许可（Linking Permission）**：允许将 `moonlink`（含 `pg_mooncake_moonlink_ffi`）与 `pg_mooncake`（及其任何 MIT 许可的分支或衍生作品）进行静态或动态链接，生成组合二进制文件或 PostgreSQL 扩展安装包，且不会导致 `pg_mooncake` 本身的源代码受制于 BSL-1.1。
3. **二进制再分发许可（Binary Redistribution Permission）**：允许通过 Linux 发行版软件源、容器镜像、PGXN、Pigsty、Homebrew 等包管理器向第三方免费构建、打包并分发组合扩展包，只需随附 `LICENSE` 文件并遵守托管服务限制即可。

---

## 第三方子模块许可证

`pg_mooncake` 在构建时还使用了 `versions.json` 中锁定的两个开源子模块：

- **[`pg_duckdb`](https://github.com/pgsty/pg_duckdb)** (`v1.2.0`)：`MIT` 许可证（`Copyright (c) 2024 Hydra, MotherDuck, and pg_duckdb contributors`）。
- **[`rust-postgres`](https://github.com/sfackler/rust-postgres)** (`14c8e599`)：`Apache-2.0 OR MIT` 双重许可。
