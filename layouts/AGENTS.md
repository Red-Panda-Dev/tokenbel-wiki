# AGENTS.md — layouts/

## Scope and inheritance

Applies to: `layouts/` и `static/css/input.css` (собирается standalone Tailwind CLI).
Inherits repository-wide guidance from `/AGENTS.md`.
This file defines only local differences для шаблонов и презентации.

## What lives here

```text
layouts/
├── home.html                # Главная: hero + site.Sections.ByWeight + recent
├── home.markdown.md         # Markdown-версия главной (output format Markdown для Accept-негоциации)
├── 404.html                 # 404: фиксированный текст и кнопки
├── _default/
│   ├── baseof.html          # Каркас <html>, partials head/header/footer, блок main
│   ├── list.html            # Список статей раздела (сортировка по Lastmod)
│   ├── single.html          # Одна статья
│   ├── single.markdown.md   # Markdown-версия статьи: H1 + description + .RawContent
│   └── list.markdown.md     # Markdown-версия раздела/таксономии: H1 + подразделы + список статей
├── _markup/
│   ├── render-codeblock-mermaid.html  # Render hook ```mermaid блоков (включает mermaid.js loader)
│   ├── render-link.html    # Render hook ссылок: image-links `[![alt](url)](url)` → `target="_blank"` (new tab)
│   └── render-table.html   # Render hook таблиц Markdown
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
- `head.html` управляет SEO: `canonical` = `.Permalink` (всегда production-домен), `noindex, follow` только для 404, OG-теги, JSON-LD на главной, а также `<link rel="alternate" type="text/markdown">` на страницах с Markdown-версией и `<link rel="describedby">` на главную (llms.txt, sitemap.xml — зеркалит Link-заголовки worker.js). Не ломайте логику canonical/robots.
- `*.markdown.md` — шаблоны output format `Markdown` (см. `hugo.yaml` `outputs`) для `worker.js`-негоциации `Accept: text/markdown`. Они используют `.RawContent` (render hooks НЕ применяются — намеренно: агентам нужен исходный Markdown) и обязаны начинаться с `# {{ .Title }}` (это проверяет `tests/check_markdown.py`). HTML-шаблоны остаются каноническими; не дублируйте в Markdown-шаблонах разметку/стили.
- `make check` жёстко ищет строки: `База знаний TokenBel` (home), `Страница не найдена` (404). Сохраняйте их дословно при рефакторинге.
- Icon-enum в `section-card.html` ({news, chart, guide, document, info}) должно совпадать со значениями `icon` в `content/<section>/_index.md` (см. `content/AGENTS.md`).
- `home.html` читает hero-параметры из front matter главной (`heroPrimaryLabel/URL`, `heroSecondaryLabel/URL`) — это контракт с `content/_index.md`.
- `render-link.html` добавляет `target="_blank" rel="noopener noreferrer"` только для image-links (destination с image-extension: content-addressed `wiki/media/images/...` и migrated `wiki/assets/...`); обычные Markdown-ссылки рендерятся как standard same-tab якоря. Это контракт с `wiki-media`: markdown `upload:` markers публикуются как `[![alt](url)](url)` (см. `tools/wiki-media/AGENTS.md`), чтобы изображение было кликабельным и открывалось в новой вкладке.

## Safe change rules

- Не вставляйте `localhost`/порт в canonical или ссылки — канонический домен `https://wiki.tokenbel.info/`.
- Новая иконка раздела → добавьте ветку в `section-card.html` и используйте то же значение в `content/_index.md`.
- Не полагайтесь на Git-даты: `.Lastmod` в шаблонах берётся из front matter (`enableGitInfo: false`).

## Validation

`npm ci`, `make css-build` и `make check` после правок шаблонов; проверьте, что подключается именно `tailwind.min.css` (его линкует `partials/css.html` во всех окружениях), canonical на домашней и 404, а также layout на ширине 320 px.
