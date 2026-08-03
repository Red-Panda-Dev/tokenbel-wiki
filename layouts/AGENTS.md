# AGENTS.md — layouts/

## Scope and inheritance

Applies to: `layouts/` и `static/css/input.css` (собирается standalone Tailwind CLI).
Inherits repository-wide guidance from `/AGENTS.md`.
This file defines only local differences для шаблонов и презентации.

## What lives here

```text
layouts/
├── home.html                # Главная: hero + site.Sections.ByWeight + recent
├── 404.html                 # 404: фиксированный текст и кнопки
├── _default/
│   ├── baseof.html          # Каркас <html>, partials head/header/footer, блок main
│   ├── list.html            # Список статей раздела (сортировка по Lastmod)
│   └── single.html          # Одна статья
├── _markup/
│   └── render-table.html    # Render hook таблиц Markdown
└── partials/
    ├── head.html            # <head>: title, canonical, robots, OG, JSON-LD
    ├── css.html             # Всегда линкует tailwind.min.css (захардкожено, без переключения окружения)
    ├── header.html / footer.html
    ├── page-dates.html      # «Опубликовано/Обновлено» из front matter — рендер-поверхность инварианта enableGitInfo: false
    ├── section-card.html    # Карточка раздела: рендер icon-enum
    └── recent-pages.html    # «Последние обновления»: фильтр excludeFromRecent
```

## Local boundaries and invariants

- CSS source — `static/css/input.css`; pinned standalone `@tailwindcss/cli` собирает committed `static/css/output.css` (unminified) и `static/css/tailwind.min.css` (minified). `partials/css.html` **всегда** линкует только `tailwind.min.css` (захардкожено, без переключения по окружению); `output.css` служит ссылкой для `make css-watch` и freshness-проверки `make css-check` и ни одним шаблоном не подключается. Не добавляйте `.scss` / Sass `@import`.
- Для уникального layout используйте Tailwind utilities, а для повторяющихся wiki-компонентов — semantic classes через `@apply` в `static/css/input.css`. Все условные class strings должны быть полными literal mappings, а не динамическими фрагментами. После изменения templates/input.css выполните `make css-build` и закоммитьте оба CSS output-файла.
- `head.html` управляет SEO: `canonical` = `.Permalink` (всегда production-домен), `noindex, follow` только для 404, OG-теги, JSON-LD на главной. Не ломайте логику canonical/robots.
- `make check` жёстко ищет строки: `База знаний TokenBel` (home), `Страница не найдена` (404). Сохраняйте их дословно при рефакторинге.
- Icon-enum в `section-card.html` ({news, chart, guide, document, info}) должно совпадать со значениями `icon` в `content/<section>/_index.md` (см. `content/AGENTS.md`).
- `home.html` читает hero-параметры из front matter главной (`heroPrimaryLabel/URL`, `heroSecondaryLabel/URL`) — это контракт с `content/_index.md`.

## Safe change rules

- Не вставляйте `localhost`/порт в canonical или ссылки — канонический домен `https://wiki.tokenbel.info/`.
- Новая иконка раздела → добавьте ветку в `section-card.html` и используйте то же значение в `content/_index.md`.
- Не полагайтесь на Git-даты: `.Lastmod` в шаблонах берётся из front matter (`enableGitInfo: false`).

## Validation

`npm ci`, `make css-build` и `make check` после правок шаблонов; проверьте, что подключается именно `tailwind.min.css` (его линкует `partials/css.html` во всех окружениях), canonical на домашней и 404, а также layout на ширине 320 px.
