# wiki-media

Изолированный Python CLI для публикации временных изображений TokenBel Wiki в Cloudflare R2.

## Установка и запуск

```bash
cd tools/wiki-media
uv sync
uv run python -m wiki_media publish --dry-run
```

Также можно установить package через `python -m pip install -e tools/wiki-media` и вызывать `wiki-media`. CLI ищет root репозитория по `.git/`, `hugo.yaml` и `content/`, поэтому запуск возможен из вложенной директории.

## Make commands

В `tools/wiki-media/` есть самостоятельный `Makefile` с uv-based commands:

```bash
make help
make test
make lint          # проверка Ruff без изменений
make refactor      # Ruff: исправления, включая unsafe fixes, и форматирование
make publish-dry-run MEDIA_PATH=content/guides
make validate MEDIA_PATH=content/guides
make cleanup DRY_RUN=--dry-run
```

`make refactor` обрабатывает только `src/` и `tests/`: применяет `ruff check --fix --unsafe-fixes`, затем `ruff format`. Перед изменением кода просмотрите `git diff`.

## Authoring

Изображение хранится **только** в `.wiki-media/inbox/`, например:

```text
.wiki-media/inbox/statistics/trading-volume.png
```

В Markdown используйте только image marker:

```markdown
![Объём торгов](upload:statistics/trading-volume.png)
![Объём торгов](upload:statistics/trading-volume.png "Источник")
![Объём торгов](<upload:statistics/Объём торгов.png>)
<img src="upload:statistics/trading-volume.png" alt="Объём торгов">
```

Обычная ссылка `[документ](upload:file.pdf)` запрещена. `upload:` всегда inbox-relative: абсолютные пути, `..`, `~`, URI и symlink запрещены.

## Commands

```bash
wiki-media publish [content-path] [--dry-run] [--remote] [--verbose] [--json-report report.json]
wiki-media validate [content-path] [--remote]
wiki-media cleanup [--dry-run]
```

Scope может быть всем `content/`, поддеревом или ровно `index.md`/`_index.md`. `cleanup` всегда сканирует весь `content/` и никогда не обращается к R2.

`publish --dry-run` без `--remote`, `validate` без `--remote` и `cleanup --dry-run` не требуют credentials.

### R2 credentials

Для remote publish CLI автоматически читает `tools/wiki-media/.env`; exported variables shell имеют приоритет над значениями из файла. `.env` не требует отдельной Python dependency и не должен попадать в Git:

```dotenv
AWS_S3_URL=https://<account-id>.r2.cloudflarestorage.com
AWS_ACCESS_KEY_ID=<r2-access-key-id>
AWS_SECRET_ACCESS_KEY=<r2-secret-access-key>
```

`AWS_S3_URL` — HTTPS S3 API endpoint Cloudflare R2, а не `https://cdn-wiki.tokenbel.info`.

## Immutable destination

Bucket is always `tokenbel-wiki`; prefix is always `wiki/media/images`; CDN is always `https://cdn-wiki.tokenbel.info`.

The object key is `wiki/media/images/<sha[:2]>/<sha><canonical-extension>`. The tool validates all local images before remote writes, checks existing objects without overwriting mismatches, uploads/verifies remote SHA-256, stages exact-span rewrites, and atomically promotes them with rollback backups. It never deletes R2 objects or commits Git changes.

Published Markdown images are emitted as clickable image-links `[![alt](url)](url)` (wrapping the whole `![alt](…)` construct, so alt text and title survive byte-for-byte). The Hugo `render-link` hook at `layouts/_default/_markup/render-link.html` adds `target="_blank" rel="noopener noreferrer"` to any link whose destination is an image file, so each published image opens full-size in a new browser tab; ordinary links keep rendering as standard same-tab anchors.
