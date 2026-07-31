# AGENTS.md — layouts/

## Scope and inheritance

Applies to: `layouts/` и `assets/css/main.css` (обрабатывается здесь через Hugo Pipes).
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
└── partials/
    ├── head.html            # <head>: title, canonical, robots, OG, CSS-Pipes, JSON-LD
    ├── header.html / footer.html
    ├── section-card.html    # Карточка раздела: рендер icon-enum
    └── recent-pages.html    # «Последние обновления»: фильтр excludeFromRecent
```

## Local boundaries and invariants

- CSS — только plain CSS. Hugo **standard** edition не поддерживает Dart Sass: `assets/css/main.css` подключается через `resources.Get | minify | fingerprint` в `head.html`. Не добавляйте `.scss` / Sass `@import`.
- `head.html` управляет SEO: `canonical` = `.Permalink` (всегда production-домен), `noindex, follow` только для 404, OG-теги, JSON-LD на главной. Не ломайте логику canonical/robots.
- `make check` жёстко ищет строки: `База знаний TokenBel` (home), `Страница не найдена` (404). Сохраняйте их дословно при рефакторинге.
- Icon-enum в `section-card.html` ({news, chart, guide, document, info}) должно совпадать со значениями `icon` в `content/<section>/_index.md` (см. `content/AGENTS.md`).
- `home.html` читает hero-параметры из front matter главной (`heroPrimaryLabel/URL`, `heroSecondaryLabel/URL`) — это контракт с `content/_index.md`.

## Safe change rules

- Не вставляйте `localhost`/порт в canonical или ссылки — канонический домен `https://wiki.tokenbel.info/`.
- Новая иконка раздела → добавьте ветку в `section-card.html` И используйте то же значение в `content/_index.md`.
- Не полагайтесь на Git-даты: `.Lastmod` в шаблонах берётся из front matter (`enableGitInfo: false`).

## Validation

`make check` после правок шаблонов; проверьте fingerprinted CSS (атрибут `integrity=`) и canonical на домашней и 404.
