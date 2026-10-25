---
title: "TokenBelInfoBot"
description: "TokenBelInfoBot — наш бот-сборщик публичных рыночных данных для TokenBel.info: User-Agent, источники, регламент запросов и цели использования."
date: 2026-10-24
lastmod: 2026-10-24
draft: false
weight: 5
---

[Русский](#о-боте) · [English](#about-the-bot)

## О боте

**TokenBelInfoBot** — сервисный робот (бот) аналитической платформы **TokenBel.info**, посвящённой белорусскому рынку ценных бумаг. Бот периодически опрашивает публичные рыночные API и скачивает открытые документы эмитентов, чтобы платформа показывала пользователям актуальные данные: выпуски, вторичный рынок, рейтинги, курсы валют и новости.

Эта страница — публичный «профиль» бота для команд безопасности и администраторов сайтов-источников (например, Cloudflare): по каким признакам его идентифицировать, что и как он собирает и для чего используются полученные данные.

### Идентификация

Бот представляется заголовком User-Agent следующего формата:

```text
TokenBelInfoBot/x.y.z (+https://tokenbel.info/contacts)
```

Пример реального значения:

```text
TokenBelInfoBot/1.0.0 (+https://tokenbel.info/contacts)
```

- `x.y.z` — версия сборщика данных;
- ссылка в скобках ведёт на страницу контактов TokenBel;
- при прямой загрузке файлов используется короткая форма `TokenBelInfoBot/1.0`.

Запросы выполняются из инфраструктуры Cloudflare (Workers) и с серверов TokenBel. Все потоки данных, описанные на этой странице, отправляются с указанным User-Agent.

### Подпись запросов (Web Bot Auth)

Опрос рыночных API и загрузка новостных страниц дополнительно подписываются по стандарту [Web Bot Auth](https://developers.cloudflare.com/bots/reference/bot-verification/web-bot-auth/) — профиль HTTP Message Signatures ([RFC 9421](https://www.rfc-editor.org/rfc/rfc9421)), алгоритм Ed25519. Каждый подписанный запрос содержит три заголовка:

- `Signature-Agent` — идентификатор бота: `https://tokenbel.info/.well-known/http-message-signatures-directory`;
- `Signature-Input` — параметры подписи (`keyid`, `alg="ed25519"`, `created`, `expires`, `nonce`, `tag="web-bot-auth"`);
- `Signature` — сама подпись; подписываются поля `@authority` и `signature-agent`.

**Проверка подписи администратором сайта-источника:**

1. Получите открытый ключ: `GET https://tokenbel.info/.well-known/http-message-signatures-directory` — JWKS с одним ключом Ed25519 (`kid` = `RM4PjQzgjHDY5FCphG5LdcvNiZSIWcVnXF8hZBsEbjY`).
2. Сверьте `keyid` из `Signature-Input` с `kid` в JWKS.
3. Проверьте подпись Ed25519 по базовой строке из `@authority`, `signature-agent` и `@signature-params`; подпись действует 300 секунд с момента `created`.

Cloudflare проверяет такие подписи автоматически в рамках Verified Bot / WAF. Разовые загрузки документов выпуска выполняются сервером TokenBel с коротким User-Agent `TokenBelInfoBot/1.0` без подписи.

### Какие данные собирает бот

| Источник                                                                                                                                        | Данные                                                                       | Режим опроса                     |
| ----------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------- | -------------------------------- |
| `api.nbrb.by` — Национальный банк Республики Беларусь                                                                                           | официальные курсы иностранных валют                                          | 2 раза в сутки                   |
| Fainex                                                                                                                                          | выпуски токенов и статусы продаж на первичном рынке (включая завершённые и распроданные выпуски) | периодически                     |
| ByNex                                                                                                                                           | выпуски токенов, графики дивидендов и погашений                              | периодически                     |
| WhiteBird                                                                                                                                       | выпуски первичного рынка                                                     | периодически                     |
| `bikratings.by` — бизнес-рейтинговое агентство                                                                                                  | кредитные, репутационные, ESG и сервисные рейтинги компаний                  | периодически                     |
| Новостные разделы белорусских финансовых СМИ и платформ (myfin.by, neg.by, minfin.gov.by, officelife.media, probusiness.io, fainex.by, bcse.by) | статьи о финансовом рынке                                                    | регулярно в течение дня          |
| Сайты платформ и эмитентов                                                                                                                      | документы выпуска (whitepaper), логотипы компаний                            | по мере появления новых выпусков |

### Как работает бот

- собираются только публично доступные рыночные данные и открытые документы — без обращения к платному контенту;
- каждый запрос к внешнему источнику идентифицируется User-Agent бота;
- на каждый запрос установлен таймаут — от 5 до 45 секунд;
- повторные попытки ограничены (не более 2–3) и выполняются с нарастающей задержкой; повторяются только сетевые ошибки и ответы 429/5xx;
- число одновременных запросов к одному источнику ограничено (один–три запроса); во внутренний API TokenBel данные передаются небольшими пакетами;
- опрос идёт по расписанию, без агрессивного обхода сайтов: от нескольких минут в торговые часы до нескольких раз в сутки;
- каждая статья и документ загружаются один раз — повторные ссылки отсекаются по хешу URL;
- полученные данные нормализуются во внутреннюю схему и сохраняются в базу TokenBel; при выдаче данных пользователям трафик на источники не генерируется.

### Хранение и использование данных

Собранные данные **сохраняются в базе данных TokenBel и используются повторно** для работы платформы (полное использование контента, а не только ссылка на источник):

- рыночные данные и курсы валют хранятся в базе и пересчитываются в каталог выпусков, аналитику и статистику;
- тексты новостных публикаций сохраняются в нормализованном виде и служат основой новостной ленты, автоматического анализа и уведомлений;
- документы выпуска (whitepaper) сохраняются в хранилище TokenBel и используются в карточках эмиссий;
- рейтинги хранятся и отображаются в карточках компаний.

### Для чего используются данные

- каталог и аналитика выпусков (токены, акции, облигации) и вторичного рынка на TokenBel.info;
- пересчёт стоимостей и рыночной статистики в валюту по официальным курсам НБРБ;
- рейтинговые карточки компаний (кредитные, репутационные, ESG, сервисные рейтинги);
- новостная лента, автоматический анализ публикаций и уведомления пользователям;
- карточки эмиссий с документами выпуска и извлечёнными из них параметрами.

### Чего бот не делает

- не собирает персональные данные;
- не создаёт учётные записи и не отправляет формы на сайтах-источниках;
- не пытается обходить ограничения доступа, капчи и платный контент;
- не занимается массовой рассылкой и не взаимодействует с посетителями сайтов.

### Для администраторов и служб безопасности

Надёжный способ подтвердить запрос бота — проверить подпись Web Bot Auth (см. раздел выше); User-Agent `TokenBelInfoBot/... (+https://tokenbel.info/contacts)` — дополнительный признак. Если активность бота мешает вашему сервису, напишите нам — снизим частоту опроса или исключим источник:

- страница контактов — <https://tokenbel.info/contacts>
- email — <admin@tokenbel.info>
- Telegram — [@tokenbel](https://t.me/tokenbel)

---

## About the bot

**TokenBelInfoBot** is a service bot operated by **TokenBel.info**, an analytics platform focused on the Belarusian securities market. The bot periodically polls public market APIs and downloads openly published issuer documents so that the platform can show users up-to-date data: issuances, secondary-market offers, ratings, exchange rates and market news.

This page is the bot's public profile for security teams and source-site administrators (for example, Cloudflare): how to identify it, what and how it collects, and what the collected data is used for.

### Identification

The bot identifies itself with a User-Agent header in the following format:

```text
TokenBelInfoBot/x.y.z (+https://tokenbel.info/contacts)
```

A real-world example:

```text
TokenBelInfoBot/1.0.0 (+https://tokenbel.info/contacts)
```

- `x.y.z` is the data collector version;
- the URL in parentheses leads to the TokenBel contacts page;
- direct file downloads use the short form `TokenBelInfoBot/1.0`.

Requests originate from Cloudflare infrastructure (Workers) and TokenBel's own servers. Every data flow described on this page is sent with the User-Agent shown above.

### Request signatures (Web Bot Auth)

Market-API polling and news-page fetches are additionally signed according to [Web Bot Auth](https://developers.cloudflare.com/bots/reference/bot-verification/web-bot-auth/) — an HTTP Message Signatures profile ([RFC 9421](https://www.rfc-editor.org/rfc/rfc9421)) using Ed25519. Every signed request carries three headers:

- `Signature-Agent` — the bot identity: `https://tokenbel.info/.well-known/http-message-signatures-directory`;
- `Signature-Input` — signature parameters (`keyid`, `alg="ed25519"`, `created`, `expires`, `nonce`, `tag="web-bot-auth"`);
- `Signature` — the signature itself, covering the `@authority` and `signature-agent` fields.

**How a source-site administrator verifies a signature:**

1. Fetch the public key: `GET https://tokenbel.info/.well-known/http-message-signatures-directory` — a JWKS with a single Ed25519 key (`kid` = `RM4PjQzgjHDY5FCphG5LdcvNiZSIWcVnXF8hZBsEbjY`).
2. Match the `keyid` from `Signature-Input` against the `kid` in the JWKS.
3. Verify the Ed25519 signature over the base string built from `@authority`, `signature-agent`, and `@signature-params`; a signature is valid for 300 seconds after `created`.

Cloudflare verifies these signatures automatically as part of Verified Bot / WAF. One-off issuance-document downloads are performed by the TokenBel server with the short User-Agent `TokenBelInfoBot/1.0` and no signature.

### What the bot collects

| Source                                                                                                                                            | Data                                                                          | Polling schedule             |
| ------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------- | ---------------------------- |
| `api.nbrb.by` — National Bank of the Republic of Belarus                                                                                          | official foreign exchange rates                                               | twice a day                  |
| Fainex                                                                                                                                            | token issuances and sale statuses on the primary market (including finished and sold-out issuances) | periodically                 |
| ByNex                                                                                                                                             | token issuances, dividend and redemption schedules                            | periodically                 |
| WhiteBird                                                                                                                                         | primary-market issuances                                                      | periodically                 |
| `bikratings.by` — business rating agency                                                                                                          | credit, reputation, ESG and service ratings of companies                      | periodically                 |
| News sections of Belarusian financial media and platforms (myfin.by, neg.by, minfin.gov.by, officelife.media, probusiness.io, fainex.by, bcse.by) | financial market articles                                                     | regularly throughout the day |
| Platform and issuer websites                                                                                                                      | issuance documents (whitepapers), company logos                               | as new issuances appear      |

### How the bot works

- only publicly available market data and open documents are collected — paywalled content is never requested;
- every request to an external source is identified by the bot's User-Agent;
- every request has a timeout of 5 to 45 seconds;
- retries are limited (no more than 2–3) and performed with increasing delays; only network errors and 429/5xx responses are retried;
- concurrency towards a single source is limited to one–three simultaneous requests; data is written to the TokenBel internal API in small batches;
- polling follows a schedule, without aggressive crawling: from a few minutes during trading hours to a few times per day;
- each article and document is downloaded once — duplicate links are dropped by URL hash;
- collected data is normalized into an internal schema and stored in the TokenBel database; serving data to users generates no traffic towards the sources.

### Data storage and use

Collected data is **stored in the TokenBel database and reused** to power the platform (full content use, not merely a link back to the source):

- market data and exchange rates are stored in the database and drive the issuance catalogue, analytics and statistics;
- news article texts are stored in a normalized form and power the news feed, automated analysis and notifications;
- issuance documents (whitepapers) are kept in TokenBel storage and used on issuance cards;
- ratings are stored and shown on company cards.

### What the data is used for

- the issuance catalogue and market analytics (tokens, shares, bonds) and the secondary market on TokenBel.info;
- converting values and market statistics into currency using official NBRB rates;
- company rating cards (credit, reputation, ESG, service ratings);
- the news feed, automated article analysis and user notifications;
- issuance cards with whitepapers and parameters extracted from them.

### What the bot does not do

- does not collect personal data;
- does not create accounts or submit forms on source websites;
- does not attempt to bypass access restrictions, CAPTCHAs or paywalled content;
- does not send mass mailings and does not interact with website visitors.

### For administrators and security teams

The most reliable way to confirm a bot request is to verify its Web Bot Auth signature (see the section above); the `TokenBelInfoBot/... (+https://tokenbel.info/contacts)` User-Agent is an additional signal. If the bot's activity interferes with your service, contact us — we will reduce the polling rate or exclude the source:

- contacts page — <https://tokenbel.info/contacts>
- email — <admin@tokenbel.info>
- Telegram — [@tokenbel](https://t.me/tokenbel)
