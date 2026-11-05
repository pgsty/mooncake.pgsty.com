---
title: "Reflections from the Iceberg Meetup"
date: 2024-10-08
description: "Last month, I spoke at the Iceberg meetup at Snowflake HQ. Here are my key takeaways on community-driven development, the early stages of open table formats, and the future of data performance."
author: "[Zhou Sun](https://github.com/zhousun) · [Mooncake Labs](https://github.com/Mooncake-Labs)"
authors: ["zhou-sun"]
tags:
  - "iceberg"
  - "community"
  - "lakehouse"
upstream_link: "https://www.mooncake.dev/blog/iceberg-meetup"
upstream_copyright: "© 2024 Zhou Sun (Mooncake Labs Inc.)"
aliases:
  - "/blog/iceberg-meetup/"
  - "/blog/2/"
images: ["/blog/covers/iceberg-meetup.svg"]
---

Last month, I spoke at the Iceberg meetup at Snowflake HQ. Public speaking has never been my favorite, and knowing Snowflake CEO Sridhar and Tabular CEO Ryan were in the audience did not help.

It was day 18 of starting Mooncake Labs, and I spoke about a general indexing framework for Iceberg. You can find the details [here](https://docs.google.com/presentation/d/1dkCA-y-T5Iuwa8A-7cif6pIUe80kN4V_tLGA05Ks3Mo/edit?usp=sharing). Here were some of my learnings:

## 1. Great products are a reflection of its community.

I spent the last decade building a proprietary database. Every time a feature request came in, engineering and product leaders would spend hours prioritizing its impact. Almost every time, it boiled down to one question: How much ARR? I watched my best engineers spend months building awkward hooks and extensions that did not fit the bigger picture. I often thought, *Just ask the customer to make a PR :)* The end product of this type of prioritization process tends to look like:

![Product Burger](/images/blog/blog2_burger.svg)

The Iceberg community feels very different. There's a clear end goal, with contributors and users working together. Developer experience is at the center, which feels refreshing—like the right way to build things people love.

I'm excited to build in the open and bring a community around Mooncake. Successful products reflect the people behind them—both builders and users.

## 2. Holy sh*t it's early days.

While much of the conversation focused on pushing the frontier of Iceberg—metadata caching, v3 format, optimized deletion files—there was also a lot of focus on the basics. I was often asked: *"What is a catalog, and why do I need it?"*

And, in talking with some AI developers and product engineers, these conversations feel even more foreign.

> "wtf is Iceberg && what is the lake?"

These are developers with a bunch of files on S3 who would benefit from table semantics – they feel the pain of managing files, processing with Python, and serving processed datasets to apps. They should care about the lakehouse, but many don't even know what it means.

It's clear I live in a narrow bubble within the Twitter data stratosphere. The most sophisticated companies are consolidating around open table technologies, but there's still a long way to go before they become standard tools for every product engineer.

First, the interfaces, syntax, and terminology need to be tailored to how modern applications are built. Setting up the infrastructure shouldn't require a dozen data engineers.

Hopefully, Mooncake can play a role in accelerating that journey 🙂

## 3. Freakish performance is on the horizon. And then there will only be one.

Some of my friends at Databricks SQL, DuckDB, Snowflake, and StarRocks are optimizing their systems for open tables. I've seen how this typically unfolds—it starts with a 2x improvement and quickly compounds, leading to significant gains.

Stateful systems will always have a place, particularly in OLTP or HTAP. However, it's hard not to envision a future where ML/AI processing, analytics (both backend and user-facing), and ad-hoc queries are fully stateless on these open tables.

I'm most excited about the work being done in adaptive query execution [(PVLDB, 17(12): 3947 - 3959, 2024)](https://www.vldb.org/pvldb/vol17/p3947-bu.pdf). This has been a long-standing interest of mine, but I was never able to convince people to build it effectively in my past experience. It's great to see it being implemented on the lakehouse better than in most data warehouses!

–– In many ways, the era of open tables is similar to this AI era. There's a lot of promise—some have already capitalized on it and won big. But it's still very early days 🥮
