---
title: "License"
linkTitle: "License"
description: "Open-source and source-available licenses across pg_mooncake, duckdb_mooncake, moonlink, and mooncake.pgsty.com."
weight: 20
icon: "fa-solid fa-scale-balanced"
---

The PGSTY Mooncake ecosystem preserves the exact upstream license terms of each repository created by Mooncake Labs, Inc.

---

## Summary by Repository

| Component | Repository | License | Notes |
|:---|:---|:---|:---|
| **`pg_mooncake`** | [`pgsty/pg_mooncake`](https://github.com/pgsty/pg_mooncake) | **`MIT`** | Permissive open-source license (`Copyright (c) 2024 Mooncake Labs`). |
| **`duckdb_mooncake`** | [`pgsty/duckdb_mooncake`](https://github.com/pgsty/duckdb_mooncake) | **`MIT`** | Permissive open-source license (`Copyright (c) 2025 Mooncake Labs`). |
| **`moonlink` (Engine)** | [`pgsty/moonlink`](https://github.com/pgsty/moonlink) | **`BSL-1.1` + Exception** | Business Source License 1.1 with the **`PG_MOONCAKE LINKING & DISTRIBUTION EXCEPTION`**, converting to **`Apache-2.0`** on **`2029-05-05`**. |
| **`moonlink` (Client Crates)** | `moonlink_rpc`, `moonlink_proto`, `moonlink_error`, `moonlink_table_metadata` | **`MIT`** | Explicitly licensed under MIT so `pg_mooncake` and `duckdb_mooncake` remain pure MIT works when linking against them. |
| **Documentation Site** | [`pgsty/mooncake.pgsty.com`](https://github.com/pgsty/mooncake.pgsty.com) | **`CC-BY-4.0` / `Apache-2.0`** | Documentation prose under Creative Commons Attribution 4.0 International (`CC-BY-4.0`); site build scripts under `Apache-2.0`. |
{.wide .expand}

---

## `pg_mooncake` & `duckdb_mooncake` — MIT License

Both [`pg_mooncake`](https://github.com/pgsty/pg_mooncake/blob/main/LICENSE) and [`duckdb_mooncake`](https://github.com/pgsty/duckdb_mooncake/blob/main/LICENSE) are distributed under the **MIT License**:

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

## `moonlink` — Business Source License 1.1 + `pg_mooncake` Exception

[`moonlink`](https://github.com/pgsty/moonlink/blob/main/LICENSE) is licensed under the **Business Source License 1.1 (`BSL-1.1`)** together with the **`PG_MOONCAKE LINKING & DISTRIBUTION EXCEPTION`**:

- **Licensor**: Mooncake Labs, Inc.
- **Licensed Work**: `moonlink` (`v0.0.1`)
- **Change Date**: `2029-05-05`
- **Change License**: `Apache-2.0` (Apache License, Version 2.0)

### Additional Use Grant

> You may make use of the Licensed Work provided that such use does not constitute Offering the Licensed Work as a Managed Service. "Offering the Licensed Work as a Managed Service" means providing third parties with access to functionality of the Licensed Work as part of a cloud service, software-as-a-service (SaaS), platform-as-a-service (PaaS), database-as-a-service (DBaaS), or similar hosted service where the primary value of the service derives substantially from the functionality of the Licensed Work itself, and competes with a commercial product or service offered by the Licensor.
>
> Notwithstanding the foregoing, you may use the Licensed Work internally within your organization, including in production environments, and you may incorporate the Licensed Work into software applications or services provided to third parties so long as such services do not expose the Licensed Work itself (or a substantially similar data ingestion/columnstore management interface) as a managed service.

### `PG_MOONCAKE LINKING & DISTRIBUTION EXCEPTION`

Because `pg_mooncake` embeds `moonlink` via FFI (`pg_mooncake_moonlink_ffi`) and `duckdb_mooncake` links `moonlink_ffi`, the upstream license includes an explicit linking and distribution exception:

> **1. MIT Client Crates.** The client interface crates contained in this repository — specifically `moonlink_rpc`, `moonlink_proto`, `moonlink_error`, and `moonlink_table_metadata` — are separately licensed under the MIT License (see the `LICENSE-MIT` file in each crate directory) and are not part of the BSL-covered Licensed Work.
>
> **2. Linking Permission.** You may compile, link (statically or dynamically), and combine the Licensed Work (`moonlink`, including `pg_mooncake_moonlink_ffi`) with `pg_mooncake` (and any MIT-licensed fork or derivative of `pg_mooncake`) to produce a combined binary or PostgreSQL extension package (a "Combined Extension"), without such linking causing the `pg_mooncake` source code itself to become subject to the Business Source License 1.1. The `pg_mooncake` source code remains governed by its own MIT License.
>
> **3. Binary Redistribution Permission.** You may build, package, and redistribute a Combined Extension in source or binary form (including via Linux distribution repositories, container images, PGXN, Pigsty, Homebrew, or similar package managers) to third parties free of charge, provided that:
>   (a) the Combined Extension includes or is accompanied by a copy of this `LICENSE` file; and
>   (b) any recipient's use of the `moonlink` portion of the Combined Extension remains subject to the terms and conditions of the Business Source License 1.1 above (in particular, the restriction against Offering the Licensed Work as a Managed Service).
>
> **4. Scope.** This exception applies solely to linking and redistribution with `pg_mooncake` (and its MIT-licensed forks/derivatives) and `duckdb_mooncake`. It does not grant permission to offer the Combined Extension, or `moonlink` standalone, as a Managed Service in violation of the Additional Use Grant above.

---

## Third-Party Bundled Submodules

The `pg_mooncake` repository also builds against two MIT/Apache-licensed submodules pinned in `versions.json`:

- **[`pg_duckdb`](https://github.com/pgsty/pg_duckdb)** (`v1.2.0`): `MIT` License (`Copyright (c) 2024 Hydra, MotherDuck, and pg_duckdb contributors`).
- **[`rust-postgres`](https://github.com/sfackler/rust-postgres)** (`14c8e599`): Dual-licensed under `Apache-2.0 OR MIT`.
