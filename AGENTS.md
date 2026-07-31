# AGENTS.md

Руководство для AI-агентов по репозиторию TokenBel Wiki.

## Что это

Статическая русскоязычная база знаний TokenBel, собираемая Hugo и публикуемая на `https://wiki.tokenbel.info/` как Cloudflare Worker со Static Assets (без runtime-скрипта, bindings, KV). Внешних Hugo-тем нет — вся вёрстка локальная.

## Где работать

```text
content/               Markdown-контент и front matter (основная поверхность редактирования)
layouts/               Локальные Hugo-шаблоны и partials (без темы)
assets/css/main.css    Единственный исходный CSS (Hugo Pipes: minify + fingerprint)
static/                Неизменяемые статики (favicon.svg)
archetypes/            Шаблоны `hugo new`
docs/                  Документация развёртывания (deployment.md)
hugo.yaml              Конфигурация сайта (язык ru, секции меню, taxonomies)
Makefile               Локальная Docker-обёртка над Hugo
build.sh               Pinned-сборка для Cloudflare (только Linux x86_64)
wrangler.toml         Конфиг Cloudflare Worker (static assets dir = ./public)
```

Не коммитьте и не правьте: `public/`, `resources/`, `.cache/`, `.wrangler/`, `.hugo_build.lock`, `node_modules/` — это артефакты сборки.

## Архитектурные инварианты

- Hugo **standard** edition (не Extended): только plain CSS, без Dart Sass / `.scss`. Обоснование — в `docs/deployment.md`.
- `enableGitInfo: false` → даты берутся только из front matter (`date`/`lastmod`); `lastmod` показывается в UI.
- Все тексты интерфейса и контента — на русском (locale `ru-BY`).
- Разделы (`news`, `statistics`, `guides`, `policies`, `about`) автособираются из `content/`; пункты меню — в `hugo.yaml`.

## Маршрутизация контекста

Читайте по необходимости:

- Правки контента, front matter, структуры разделов → `content/AGENTS.md`
- Правки шаблонов, SEO-мета, иконок, CSS-Pipes → `layouts/AGENTS.md`
- Развёртывание, staging, rollback, pinned-инструменты → `docs/deployment.md`

## Правила изменений

- Новый раздел: `content/<section>/_index.md` с `title`, `description`, `weight`, `icon` ∈ {news, chart, guide, document, info}; при необходимости добавьте пункт в `menus.main` в `hugo.yaml`.
- Новая статья: leaf bundle `content/<section>/<slug>/index.md` с вложениями рядом.
- Миграция BookStack: сохраняйте прежние адреса через front matter `url` и `aliases`.
- Не добавляйте внешние Hugo-темы и Sass-зависимости.
- Не правьте `public/` — это результат сборки.

## Валидация

```bash
make dev      # live-reload сервер (Docker, Hugo 0.164.0 через hugomods)
make check    # build + проверки public/index.html, public/404.html и строк
```

`make check` жёстко проверяет: наличие `База знаний TokenBel` в `index.html`, `Страница не найдена` и `noindex, follow` в `404.html`. Не ломайте эти строки при рефакторинге.

Перед завершением: `make check` (или `hugo --gc --minify`) и наличие `public/index.html`, `public/404.html`.

## Гоччи

- Канонический URL всегда `https://wiki.tokenbel.info/` (включая staging) — не вставляйте `localhost`/порт в canonical или ссылки.
- Страница 404 должна отдавать `noindex, follow` и текст `Страница не найдена`.
- Параметр `excludeFromRecent: true` исключает страницу из блока «Последние обновления».
- Локальный путь сборки (Docker `make`) и Cloudflare (`build.sh`, Linux x86_64) различаются — не запускайте `build.sh` вне Linux x86_64.
