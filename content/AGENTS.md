# AGENTS.md — content/

## Scope and inheritance

Applies to: `content/`.
Inherits repository-wide guidance from `/AGENTS.md`.
This file defines only local differences for редактирования контента.

## What lives here

```text
content/
├── _index.md                # Главная: требует hero-параметры (см. ниже)
├── <section>/_index.md      # Landing раздела (news, statistics, guides, policies, about)
└── <section>/<slug>/        # Leaf bundle статьи
    ├── index.md             # Единственный контент-файл статьи
    └── <вложения>           # изображения/файлы рядом; для мигрированных — CDN URL, не локальные
```

## Local boundaries and invariants

- Весь контент — на русском. Текст интерфейса тоже на русском.
- Section landing = `_index.md`; статья = leaf bundle с `index.md` + вложениями рядом (не `_index.md` внутри статьи).
- Front matter раздела (`_index.md`): обязательны `title`, `description`, `weight`, `icon`.
- `icon` ∈ {`news`, `chart`, `guide`, `document`, `info`}. Значение рендерится в `layouts/partials/section-card.html`; неизвестное значение молча даёт иконку `info`.
- Разделы автособираются и сортируются по `weight` (главная страница + меню `hugo.yaml`).
- Главная (`content/_index.md`) требует hero-параметры: `heroPrimaryLabel`/`heroPrimaryURL`, `heroSecondaryLabel`/`heroSecondaryURL` — используются в `layouts/home.html`.

## Safe change rules

- Новый раздел: создайте `content/<section>/_index.md` и добавьте пункт в `menus.main` в `hugo.yaml`, если он нужен в навигации.
- Не задавайте `icon` вне enum — иконка будет неверной без ошибки сборки.
- Даты: `lastmod` показывается пользователям (`Обновлено ...`). Git-даты не используются (`enableGitInfo: false`), обновляйте `date`/`lastmod` осознанно.
- Одноразовая миграция BookStack создаёт чистые leaf bundles без `url`, `aliases`, legacy-адресов и BookStack metadata. Связи с исходниками остаются только в gitignored migration artifacts; изображения используют абсолютные CDN URL `https://cdn-wiki.tokenbel.info/wiki/assets/...`, а не локальные вложения.
- Новые изображения не коммитьте в leaf bundles. Храните их только в gitignored `.wiki-media/inbox/` и используйте image marker `![alt](upload:section/file.png)` (для пробелов: `<upload:section/file name.png>`). `wiki-media publish` заменяет marker на content-addressed CDN URL после R2 verification; обычные ссылки с `upload:` запрещены.

## Validation

`make check` собирает сайт и проверяет `index.html`/`404.html`. Перед добавлением вложений убедитесь, что статья — leaf bundle (папка с `index.md`), а не branch (`_index.md`).
