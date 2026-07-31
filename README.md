# TokenBel Wiki

Статическая русскоязычная база знаний TokenBel: руководства, справочные материалы и статистика рынка белорусских токенов. Сайт собирается Hugo и публикуется на `https://wiki.tokenbel.info/`.

## Требования

- Hugo (актуальная stable-версия, рекомендуется extended);
- Git.

## Локальный запуск

```bash
hugo server --buildDrafts
```

Откройте адрес, выведенный Hugo (обычно `http://localhost:1313/`).

## Production build

```bash
hugo --gc --minify
```

Собранный сайт появится в `public/`. Эта директория — build artifact и не коммитится. Деплой настраивается отдельно.

## Структура

- `content/` — Markdown-контент и front matter;
- `content/<section>/_index.md` — landing page раздела;
- `layouts/` — локальные Hugo-шаблоны и partials, без внешней темы;
- `assets/css/main.css` — исходный CSS, собираемый Hugo Pipes;
- `static/` — неизменяемые статические файлы.

### Новый раздел

Создайте `content/<section>/_index.md` с `title`, `description`, `weight` и одним из значений `icon`: `news`, `chart`, `guide`, `document`, `info`. Главная страница автоматически показывает разделы из `site.Sections`, сортируя их по `weight`.

### Новая статья

Используйте leaf bundle, чтобы Markdown и вложения находились рядом:

```text
content/guides/ytm/
├── index.md
├── chart.webp
└── example.xlsx
```

В front matter статьи можно задать стабильный URL и прежние адреса при миграции BookStack:

```yaml
url: "/books/rukovodstvo-polzovatelia/page/doxodnost-k-pogaseniiu-ytm/"
aliases:
  - "/link/42/"
```

## Валидация

```bash
hugo version
hugo server --buildDrafts
hugo --gc --minify
test -f public/index.html
test -f public/404.html
grep -q 'База знаний TokenBel' public/index.html
grep -q 'Страница не найдена' public/404.html
```

Никаких Node.js-зависимостей или внешней Hugo-темы для сборки не требуется.
