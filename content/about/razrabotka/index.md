---
title: "Разработка"
description: "Как устроен TokenBel: PostgreSQL, pgvector, Redis, высокая доступность и технологические решения для хранения и обработки финансовых данных."
date: "2025-11-15"
lastmod: "2026-11-26"
draft: false
weight: 4
---

### Схема сервиса

```mermaid
C4Container
title "Схема сервиса TokenBel (C4 Container)"

Person(client, "Client", "Пользователь сервиса")

System(dns, "DNS", "Cloudflare DNS")
System(storage, "Object Storage", "R2 / S3: статика и файлы")
System_Ext(ext, "External Services", "Внешние источники данных и уведомления")

System_Boundary(tbel, "TokenBel") {
  Container(api, "API", "aiohttp backend", "JSON API и внутренний API")
  Container(wiki, "Wiki", "Hugo", "Статические страницы")
  Container(cron, "Cron", "Планировщик", "Расписание задач")
  ContainerQueue(queue, "Queue", "Очередь", "Очередь задач")
  Container(workers, "Workers", "Воркеры", "Коллекторы и конвейеры данных")
  ContainerDb(cache, "Cache", "Redis", "Кэш и сессии")
  ContainerDb(db, "Database", "PostgreSQL", "Основное хранилище")
}

BiRel(client, dns, "Запросы")
Rel(dns, storage, "Статика через CDN")
BiRel(dns, api, "Динамические запросы")
BiRel(dns, wiki, "Страницы")
BiRel(api, cache, "Кэш и сессии")
Rel(api, db, "Чтение и запись")
Rel(cron, queue, "Постановка задач")
Rel(queue, workers, "Сообщения")
Rel(api, workers, "Задания")
Rel(workers, queue, "Задачи для других воркеров")
BiRel(workers, ext, "Обмен данными")
Rel(workers, api, "Отправка данных")
BiRel(workers, cache, "Чтение и запись")
Rel(workers, db, "Чтение, read-only")

UpdateElementStyle(client, $borderColor="#D6B656", $fontColor="#8A6A1F")
UpdateElementStyle(dns, $borderColor="#9773A6", $fontColor="#6E4E7E")
UpdateElementStyle(storage, $borderColor="#9773A6", $fontColor="#6E4E7E")
UpdateElementStyle(ext, $borderColor="#9773A6", $fontColor="#6E4E7E")
UpdateElementStyle(tbel, $borderColor="#1e40af", $fontColor="#1e40af")
UpdateElementStyle(api, $borderColor="#2563eb", $fontColor="#1d4ed8")
UpdateElementStyle(wiki, $borderColor="#2563eb", $fontColor="#1d4ed8")
UpdateElementStyle(cron, $borderColor="#2563eb", $fontColor="#1d4ed8")
UpdateElementStyle(queue, $borderColor="#C2410C", $fontColor="#9A3412")
UpdateElementStyle(workers, $borderColor="#C2410C", $fontColor="#9A3412")
UpdateElementStyle(cache, $borderColor="#5E9484", $fontColor="#3D6B5A")
UpdateElementStyle(db, $borderColor="#5E9484", $fontColor="#3D6B5A")
```

### Хранение данных

В качестве основной базы данных используется [PostgreSQL 18.4](https://www.postgresql.org/). Подключено расширение [pgvector](https://github.com/pgvector/pgvector), которое лежит в основе новой дедупликации событий с помощью эмбеддингов. Для хранения временных данных используется [Redis 8](https://redis.io/).

Вместо собственной сборки PostgreSQL с архитектурой master–slave и PgBouncer теперь используется кластер высокой доступности от провайдера на базе Patroni, etcd, HAProxy и PgBouncer. Переход ускорил обработку запросов и повысил надёжность системы благодаря автоматическому управлению отказоустойчивостью.

Схема таблиц базы данных:

v3
[![Схема базы данных](https://cdn-wiki.tokenbel.info/wiki/media/images/4d/4d8aeb2a01f9fe942c31946e4e41d410032bcfa99c4bddd7342fa21aed760240.webp)](https://cdn-wiki.tokenbel.info/wiki/media/images/4d/4d8aeb2a01f9fe942c31946e4e41d410032bcfa99c4bddd7342fa21aed760240.webp)
