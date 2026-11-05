---
title: "Things we learnt"
date: 2024-09-08
description: "As we start this new journey, we spent some time thinking about the axioms of data today. These are things we (or no one for that matter) can dispute."
author: "[Pranav Aurora](https://github.com/paurora17) · [Mooncake Labs](https://github.com/Mooncake-Labs)"
authors: ["pranav-aurora"]
tags:
  - "postgresql"
  - "iceberg"
  - "musings"
upstream_link: "https://www.mooncake.dev/blog/things-we-learnt"
upstream_copyright: "© 2024 Pranav Aurora (Mooncake Labs Inc.)"
aliases:
  - "/blog/things-we-learnt/"
  - "/blog/laws-of-data/"
  - "/blog/1/"
images: ["/blog/covers/things-we-learnt.svg"]
---

The title should really be "Things we learnt, the hard way".

As we start this new journey, we spent some time thinking about the axioms of data today. These are things we (or no one for that matter) can dispute.

## 1. If Postgres can do it, Postgres will do it

We've seen this one plenty of times now – it started with JSON, then moved to geo-spatial (`PostGIS`), and now we're seeing it with vector search (`pgvector`).

Performance used to be the battle. It was a battle we played a lot in our past lives. It was a battle we also won. But somehow, we never won the war.

In our past lives, we built the fastest general-purpose vector database (amongst others); we even wrote some papers on it ([SingleStore-V: PVLDB, 17: 3772 - 3785, 2024](https://dl.acm.org/doi/10.14778/3685800.3685805)). But somehow, that wasn't enough.

`pgvector` with its pretty average QPS and throughput –– won.

Why? It's good enough, and it's just there.

> Never fight gravity. Postgres is gravity.

## 2. We are in innings 0 of the open table format era. Play ball.

Open table formats ([Iceberg](https://iceberg.apache.org/)/[Delta](https://delta.io/)/[Hudi](https://hudi.apache.org/)) seem to be all the rage. Tabular didn't hurt. Apparently, the world's data is now suddenly all open. And seemingly, this happened in the last 6 months.

How? We were recently at the Iceberg meetup in San Francisco. We even gave a talk ([more on that later](/blog/post/iceberg-meetup/)). We were alongside Sridhar Ramaswamy, Ryan Blue, and some of the most skilled data engineers in the world. The meetup was 30 people –– largely representing two main customers. Tiny by SF standards. What's all the hype about?

Open table formats haven't eaten the world. Not even close, and definitely not yet. But they sure will. Open tables mean not much to not many just yet. But this will change. It really feels like the right architecture. Not just from an engineering standpoint. It is an architecture that can unite the community.

And when the community is united and builds deep conviction about a technology, you can bet some epic things are going to happen.

That's what these open tables will do. The Avengers are being formed around open table formats. Are you going to fight it?

### Entropy and change in the data landscape are constants

In our short tenure, we've witnessed:

- The Hadoop ecosystem rise and crumble
- MySQL dethroned
- The birth of terms like "big data" and, now somehow, "small data"

We sure could be in another one of these hype cycles. Maybe Postgres and open table formats don't eat the world. But they do put the developer at its center and provide them an A+ experience. That is very exciting.

**Developers always win. 🥮**
