# AGENTS.md

Руководство для AI-агентов по репозиторию TokenBel Wiki.

## Обзор репозитория

Статическая русскоязычная база знаний TokenBel, собираемая Hugo и публикуемая на `https://wiki.tokenbel.info/` как Cloudflare Worker со Static Assets. Минимальный `worker.mjs` только переписывает валидный `?page=N` для списков в Hugo-ассеты `/page/N/`; runtime-данных, KV и серверного рендеринга нет. Внешних Hugo-тем нет — вся вёрстка локальная.

## Где работать

```text
content/               Markdown-контент и front matter (основная поверхность редактирования)
layouts/               Локальные Hugo-шаблоны и partials (без темы)
static/css/input.css  Tailwind CSS 4 source; output.css и tailwind.min.css — committed CLI output
static/                Статики, включая committed Tailwind output и favicon.svg
archetypes/            Шаблоны `hugo new`
assets/                Зарезервировано Hugo assets/ (пусто; CSS-pipeline использует static/, а не assets/)
scripts/               Зарезервировано (пусто; сборка — через Makefile/build.sh, а не скрипты здесь)
docs/                  Документация развёртывания (deployment.md)
tools/                 Изолированный Python CLI wiki-media (публикация изображений в Cloudflare R2)
hugo.yaml              Конфигурация сайта (язык ru, секции меню, taxonomies)
Makefile               Локальная Docker-обёртка над Hugo
build.sh               Pinned-сборка для Cloudflare (только Linux x86_64)
wrangler.toml         Конфиг Cloudflare Worker (static assets dir = ./public, ASSETS binding)
worker.mjs           Query-param pagination rewrite → Hugo static assets
```

**Не коммитьте и не правьте:** `public/`, `resources/`, `.cache/`, `.wrangler/`, `.hugo_build.lock`, `node_modules/` — это артефакты сборки.

## Архитектурные инварианты

- Hugo **standard** edition (не Extended): Tailwind CSS 4 предварительно собирается pinned `@tailwindcss/cli` из `static/css/input.css`; Hugo только копирует committed static CSS. Dart Sass / `.scss` запрещены. Обоснование — в `docs/deployment.md`.
- `enableGitInfo: false` → даты берутся только из front matter (`date`/`lastmod`); `lastmod` показывается в UI.
- Все тексты интерфейса и контента — на русском (locale `ru-BY`).
- Разделы (`news`, `statistics`, `guides`, `policies`, `about`) автособираются из `content/`; пункты меню — в `hugo.yaml`.

## Маршрутизация контекста

Читайте по необходимости:

- Архитектурные или кросс-модульные правки → `ARCHITECTURE.md` (каноническая карта слоёв, зависимостей и инвариантов)
- Правки контента, front matter, структуры разделов → `content/AGENTS.md`
- Правки шаблонов, SEO-мета, иконок, CSS-подключения → `layouts/AGENTS.md`
- Правки media-publisher CLI `wiki-media` (Python, R2) → `tools/wiki-media/AGENTS.md`
- Развёртывание, staging, rollback, pinned-инструменты → `docs/deployment.md`

## Правила изменений

- Новый раздел: `content/<section>/_index.md` с `title`, `description`, `weight`, `icon` ∈ {news, chart, guide, document, info}; при необходимости добавьте пункт в `menus.main` в `hugo.yaml`.
- Новая статья: leaf bundle `content/<section>/<slug>/index.md` с вложениями рядом.
- Одноразовая миграция BookStack создаёт чистый Hugo content без `url`, `aliases`, legacy-адресов и BookStack metadata в `content/`. Связи с исходными страницами хранятся только в gitignored migration artifacts; изображения используют абсолютные CDN URL `https://cdn-wiki.tokenbel.info/wiki/assets/...`.
- Не добавляйте внешние Hugo-темы и Sass-зависимости.
- Для новых изображений не используйте article bundles: положите файл в gitignored `.wiki-media/inbox/`, добавьте image-only marker `upload:<inbox-relative-path>` и опубликуйте через `wiki-media`. CLI находится в `tools/wiki-media/`, публикует immutable R2 objects и не выполняет Git commit; старые `https://cdn-wiki.tokenbel.info/wiki/assets/...` не переписываются.
- Визуальный reference — основной TokenBel: `../tbel/src/tbel/static/css/input.css`, `../tbel/src/tbel/templates/base.html`, `../tbel/src/tbel/templates/elements/header.html`. Не переносите dashboard-компоненты, AlpineJS или аналитику.
- Для уникального layout используйте Tailwind utilities; для повторяющихся wiki-компонентов — стабильные semantic classes через `@apply` в `static/css/input.css`. Не формируйте Tailwind class names динамически.
- После изменения `input.css` или Tailwind classes в шаблонах запустите `make css-build` и закоммитьте оба output-файла.
- Не правьте `public/` — это результат сборки.

## Валидация

```bash
npm ci        # установить pinned build dependencies, включая Tailwind CSS 4
make css-build # пересобрать committed static/css/output.css и tailwind.min.css
make dev       # live-reload сервер (Docker, Hugo 0.164.0 через hugomods)
make check     # проверить актуальность committed CSS и HTML-вывод
```

`make check` жёстко проверяет: наличие `База знаний TokenBel` в `index.html`, `Страница не найдена` и `noindex, follow` в `404.html`. Не ломайте эти строки при рефакторинге.

Перед завершением: `npm ci`, `make check` (или `hugo --gc --minify`), проверка 320 px, и наличие `public/index.html`, `public/404.html`. Изменения в `tools/wiki-media/` (Python) валидируются отдельно (`make lint`/`make test` и `make publish-dry-run`), см. `tools/wiki-media/AGENTS.md`.

## Потенциальные ловушки

- Канонический URL всегда `https://wiki.tokenbel.info/` (включая staging) — не вставляйте `localhost`/порт в canonical или ссылки.
- Пагинация списков: Hugo генерирует `/page/N/`, а `worker.mjs` принимает один валидный `?page=N` для маршрутов разделов и тегов и запрашивает соответствующий static asset. Не добавляйте клиентскую пагинацию или меняйте контракт rewrite без тестов.
- Страница 404 должна отдавать `noindex, follow` и текст `Страница не найдена`.
- Параметр `excludeFromRecent: true` исключает страницу из блока «Последние обновления».
- Локальный путь сборки (Docker `make`) и Cloudflare (`build.sh`, Linux x86_64) различаются — не запускайте `build.sh` вне Linux x86_64.
