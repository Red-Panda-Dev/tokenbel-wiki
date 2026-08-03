# TokenBel Wiki

Статическая русскоязычная база знаний TokenBel: руководства, справочные материалы и статистика рынка белорусских токенов. Сайт собирается Hugo и публикуется на `https://wiki.tokenbel.info/`.

## Требования

- Docker;
- GNU Make;
- Git;
- Node.js и npm (для Tailwind CSS 4 build dependencies).
- Python 3.11+ (только для optional CLI `wiki-media`).

Hugo запускается в Docker-образе `hugomods/hugo:0.164.0`, поэтому локальная версия Hugo не требуется и совпадает с версией сборки.

## Локальный запуск

Установите pinned Node.js-зависимости, включая Tailwind CSS 4:

```bash
npm ci
```

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
make help              показать команды
make version           вывести версию Hugo
make css-build         пересобрать committed CSS output и minified CSS
make css-watch         следить за input.css и обновлять output.css
make dev               запустить live-reload сервер с draft/future страницами
make build             собрать production-сайт в public/
make check             проверить актуальность CSS и основной HTML-вывод
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
- `static/css/input.css` — Tailwind CSS 4 source;
- `static/css/output.css` и `static/css/tailwind.min.css` — committed CLI output для development и production;
- `static/` — статические файлы, копируемые Hugo без обработки.

### Новый раздел

Создайте `content/<section>/_index.md` с `title`, `description`, `weight` и одним из значений `icon`: `news`, `chart`, `guide`, `document`, `info`. Главная страница автоматически показывает разделы из `site.Sections`, сортируя их по `weight`.

### Новая статья

Используйте leaf bundle для статьи:

```text
content/guides/ytm/
└── index.md
```

Одноразовая миграция BookStack создаёт чистый Hugo content без `url`, `aliases`, legacy-адресов и BookStack metadata. Исходные связи остаются только в gitignored migration artifacts; изображения мигрированных статей используют абсолютные CDN URL `https://cdn-wiki.tokenbel.info/wiki/assets/...`.

### Новые изображения

Не коммитьте новые изображения в article bundles. Поместите их в gitignored `.wiki-media/inbox/` и добавьте в статью image marker, например `![Объём торгов](upload:statistics/trading-volume.png)`. Для пробелов используйте `<upload:statistics/Объём торгов.png>`. Затем CLI загружает проверенное изображение в immutable R2 и заменяет только `upload:` destination на CDN URL:

```bash
make media-install
make media-publish-dry-run MEDIA_PATH=content/statistics
make media-publish MEDIA_PATH=content/guides
make media-validate
```

`wiki-media publish` поддерживает весь `content/`, directory scope и один `index.md`/`_index.md`; обычные `upload:` links запрещены. Старые migrated URLs под `https://cdn-wiki.tokenbel.info/wiki/assets/...` остаются валидными и не переписываются. Детали syntax, R2 и transaction/rollback есть в [tools/wiki-media/README.md](tools/wiki-media/README.md).

## Валидация

```bash
make version
make check
```

Для CSS-сборки требуются pinned Node.js-зависимости из `package-lock.json`; внешняя Hugo-тема не используется. Standalone `@tailwindcss/cli` собирает `static/css/input.css` в committed `output.css` и minified `tailwind.min.css` — Hugo только копирует их в `public/`.

После изменения Tailwind classes в шаблонах или `input.css` выполните:

```bash
make css-build
make check
```

Для production-подобной сборки используйте:

```bash
./build.sh
```
