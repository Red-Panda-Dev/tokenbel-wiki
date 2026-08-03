---
title: "Разработка"
description: "Как устроен TokenBel: PostgreSQL, pgvector, Redis, высокая доступность и технологические решения для хранения и обработки финансовых данных."
date: "2025-11-15"
lastmod: "2026-08-03"
draft: false
weight: 4
---

### Схема сервиса

v3
[![Схема проекта](https://cdn-wiki.tokenbel.info/wiki/media/images/5e/5e4597243f8416904dc122e77cd2e44f620ab120dd3a25fc57c7072188a03bc9.webp)](https://cdn-wiki.tokenbel.info/wiki/media/images/5e/5e4597243f8416904dc122e77cd2e44f620ab120dd3a25fc57c7072188a03bc9.webp)

### Хранение данных

В качестве основной базы данных используется [PostgreSQL 18.4](https://www.postgresql.org/). Подключено расширение [pgvector](https://github.com/pgvector/pgvector), которое лежит в основе новой дедупликации событий с помощью эмбеддингов. Для хранения временных данных используется [Redis 8](https://redis.io/).

Вместо собственной сборки PostgreSQL с архитектурой master–slave и PgBouncer теперь используется кластер высокой доступности от провайдера на базе Patroni, etcd, HAProxy и PgBouncer. Переход ускорил обработку запросов и повысил надёжность системы благодаря автоматическому управлению отказоустойчивостью.

Схема таблиц базы данных:

v3
[![Схема базы данных](https://cdn-wiki.tokenbel.info/wiki/media/images/4d/4d8aeb2a01f9fe942c31946e4e41d410032bcfa99c4bddd7342fa21aed760240.webp)](https://cdn-wiki.tokenbel.info/wiki/media/images/4d/4d8aeb2a01f9fe942c31946e4e41d410032bcfa99c4bddd7342fa21aed760240.webp)

### Планы и задачи

Для планирования и отслеживания задач используется [Planka](https://github.com/plankanban/planka).
