---
title: "我们学到的几条铁律"
date: 2024-09-08
description: "在开启这段全新创业旅程之际，我们花了一些时间思考当今数据领域的公理——那些无论我们还是任何人都无法回避的事实。"
author: "[Pranav Aurora](https://github.com/paurora17) · [Mooncake Labs](https://github.com/Mooncake-Labs)"
authors: ["pranav-aurora"]
tags:
  - "postgresql"
  - "iceberg"
  - "musings"
upstream_link: "https://www.mooncake.dev/blog/things-we-learnt"
upstream_copyright: "© 2024 Pranav Aurora (Mooncake Labs Inc.)"
aliases:
  - "/zh/blog/things-we-learnt/"
images: ["/blog/covers/things-we-learnt.svg"]
---

这篇文章的标题其实应该叫《我们用惨痛代价学到的几条铁律》。

在开启这段全新旅程之际，我们花了一些时间思考当今数据领域的底层公理——这些规律无论我们还是任何人都无法回避。

## 1. 只要 Postgres 能做的事，最终都会由 Postgres 来做 {#1-if-postgres-can-do-it-postgres-will-do-it}

这一幕我们已经见过太多次了——最早是 JSON，接着是地理空间数据（`PostGIS`），而现在则是向量检索（`pgvector`）。

过去，性能曾经是决胜的主战场。在之前的职业生涯里，我们打过无数场性能战役，而且赢下了绝大部分。但不知为何，我们赢了战役，却没能赢下整场战争。

在上一家公司（SingleStore），我们打造了业界最快的通用向量数据库，甚至还在顶会上发表了论文（[SingleStore-V: PVLDB, 17: 3772 - 3785, 2024](https://dl.acm.org/doi/10.14778/3685800.3685805)）。但即便如此，依然不够。

QPS 和吞吐量看起来平平无奇的 `pgvector`——最终赢下了市场。

为什么？因为它“足够好用”，而且它就在 Postgres 里面，触手可及。

> 永远不要对抗万有引力。Postgres 就是数据世界的万有引力。

## 2. 开放表格式时代才刚刚进入第 0 局，入场打球吧 {#2-we-are-in-innings-0-of-the-open-table-format-era-play-ball}

开放表格式（[Iceberg](https://iceberg.apache.org/)、[Delta](https://delta.io/)、[Hudi](https://hudi.apache.org/)）如今风头无两。Tabular 的天价收购更是火上浇油。仿佛一夜之间，全世界的数据都变成了开放格式，而且这一切似乎都是在过去 6 个月内发生的。

真相究竟如何？我们最近参加了在旧金山举办的 Iceberg Meetup，还在会上做了一场分享（[详见后续文章](/zh/blog/post/iceberg-meetup/)）。与我们同台的有 Snowflake CEO Sridhar Ramaswamy、Tabular 创始人 Ryan Blue，以及世界上最顶尖的一批数据工程师。然而整场聚会只有大约 30 个人——而且主要来自两家大客户。按照旧金山的标准，这个规模小得惊人。那铺天盖地的热潮到底是怎么回事？

开放表格式还没有吞噬世界——甚至连边都还没摸到。但它们终将做到。此时此刻，开放表格式对绝大多数普通开发者而言还很遥远，但这一切很快就会改变。无论从工程视角还是生态视角来看，它都是真正正确的架构——一种能够团结整个开源与数据社区的架构。

而当整个社区团结一致、对某项技术建立起深厚信仰时，你可以笃定，真正波澜壮阔的变革即将发生。

这就是开放表格式正在酝酿的力量。围绕开放表格式的“复仇者联盟”正在集结，难道你要逆势而行吗？

### 数据版图的熵增与演进是永恒的常量 {#entropy-and-change-in-the-data-landscape-are-constants}

在我们并不算漫长的职业生涯中，就已经亲眼见证了：

- Hadoop 生态系统的崛起与崩塌
- MySQL 从王座上跌落
- “大数据（Big Data）”以及如今“小数据（Small Data）”等概念的诞生与更替

我们或许正身处新一轮技术浪潮之中。也许 Postgres 和开放表格式未必能吞噬一切，但它们确实把开发者放在了舞台中央，并为开发者提供了 A+ 级的体验。这本身就足以令人热血沸腾。

**开发者永远是最终的赢家。🥮**
