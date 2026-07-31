# TokenBel Wiki

Статическая русскоязычная база знаний TokenBel: руководства, справочные материалы и статистика рынка белорусских токенов. Сайт собирается Hugo и публикуется на `https://wiki.tokenbel.info/`.

## Требования

- Docker;
- GNU Make;
- Git.

Hugo запускается в Docker-образе `hugomods/hugo:0.164.0`, поэтому локальная версия Hugo не требуется и совпадает с версией сборки.

## Локальный запуск

Запустите live-reload сервер:

```bash
make dev
```

Откройте <http://localhost:1313/>. Порт можно изменить: `make dev PORT=8080`.

Для production-подобного запуска соберите статический сайт:

```bash
make build
```

Собранный сайт появится в `public/`. Эта директория — build artifact и не коммитится. Деплой настраивается отдельно.

Доступные команды:

```text
make help      показать команды
make version   вывести версию Hugo
make dev       запустить live-reload сервер с draft/future страницами
make build     собрать production-сайт в public/
make check             собрать сайт и проверить основной HTML-вывод
make cloudflare-build  выполнить pinned production build для Cloudflare
make deploy-dry-run    проверить Cloudflare deploy без публикации
make deploy            опубликовать Worker и static assets
make clean             удалить артефакты сборки
```

`make serve` — алиас для `make dev`. Переменная `HUGO_IMAGE` позволяет переопределить Docker-образ, а `HUGO_VERSION` — версию Hugo.

## Deployment

Production deployment uses Cloudflare Workers Static Assets.

- Production branch: `main`
- Worker: `tokenbel-wiki`
- Production domain: `wiki.tokenbel.info`
- Build: `./build.sh`
- Deploy: `make deploy` (or `npm run deploy`)

Подробные настройки Workers Builds, staging, custom domain и rollback описаны в [docs/deployment.md](docs/deployment.md). Подключение production domain выполняется только после отдельно подтверждённой staging-проверки.

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
make version
make check
```

Никаких Node.js-зависимостей или внешней Hugo-темы для сборки не требуется.
