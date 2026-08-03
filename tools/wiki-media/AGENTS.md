# AGENTS.md — tools/wiki-media/

## Scope and inheritance

Applies to: `tools/wiki-media/`.
Inherits repository-wide guidance from `/AGENTS.md`.
This file defines only local differences для поддержки самого CLI `wiki-media` (а не для публикации изображений — контракты `upload:` и inbox описаны в `/AGENTS.md` и `content/AGENTS.md`).

## What lives here

```text
tools/wiki-media/
├── pyproject.toml        # Пакет wiki-media; Python ≥3.11; deps: boto3, Pillow; extras: test (pytest), style (ruff==0.16.*)
├── uv.lock               # Pinned Python deps — коммитится
├── Makefile              # uv-based: install/lint/refactor/test/publish*/validate/cleanup
├── .env                  # R2 credentials — НЕ коммитится (gitignored/untracked)
├── src/wiki_media/
│   ├── cli.py            # argparse entry (publish|validate|cleanup) → console_script `wiki-media`
│   ├── __main__.py       # `python -m wiki_media`
│   ├── config.py         # repo-root discovery; чтение .env / env (AWS_S3_URL, keys)
│   ├── discovery.py      # поиск `upload:` markers; scope: content/ | поддерево | один index.md
│   ├── images.py         # Pillow-валидация локальных изображений, размеры, SHA-256
│   ├── keys.py           # content-addressed ключ объекта R2
│   ├── markdown.py       # exact-span rewrite `upload:` → CDN URL
│   ├── transaction.py    # атомарный staging rewrite + rollback-бэкапы
│   ├── r2.py             # boto3 R2-клиент (upload, head, verify; без overwrite/delete)
│   ├── publisher.py      # оркестрация publish (dry-run vs --remote)
│   ├── reporting.py      # текстовый/JSON отчёт
│   └── models.py         # dataclass-типы
└── tests/
    └── test_core.py      # pytest-набор
```

## Local boundaries and invariants

- **Отдельный runtime:** Python 3.11+ под `uv`, не npm/Docker/Hugo. Сборка через `uv sync`, запуск — `uv run`. Не тяните сюда Node- или Hugo-инструменты.
- **Стиль:** Ruff 0.16 (`[tool.ruff]` line-length 120, target py312). `make lint` проверяет без изменений; `make refactor` применяет unsafe-fixes и форматирование только по `src/` и `tests/`.
- **Иммутабельный адрес назначения зафиксирован:** bucket `tokenbel-wiki`, prefix `wiki/media/images`, CDN `https://cdn-wiki.tokenbel.info`. Ключ объекта — `wiki/media/images/<sha[:2]>/<sha><canonical-extension>` (content-addressed, каноническое расширение). Не меняйте схему — это ломает дедупликацию и оставляет осиротевшие R2-объекты.
- **R2-immutable контракт:** никогда не перезаписывайте существующий объект с несовпадающим контентом, не удаляйте R2-объекты, всегда верифицируйте remote SHA-256. `publish` никогда не выполняет Git commit и не переписывает старые migrated URL `https://cdn-wiki.tokenbel.info/wiki/assets/...`.
- **`upload:` всегда inbox-relative** (`.wiki-media/inbox/...`): абсолютные пути, `..`, `~`, URI и symlink запрещены. Не-image `upload:` ссылки (например `[док](upload:file.pdf)`) запрещены — только image markers.
- **Credentials:** `tools/wiki-media/.env` никогда не коммитится. `AWS_S3_URL` — HTTPS S3 API endpoint Cloudflare R2, **не** CDN URL. Экспортированные переменные shell имеют приоритет над `.env`. Пути без сети (`publish --dry-run` без `--remote`, `validate` без `--remote`, `cleanup --dry-run`) не требуют credentials.

## Safe change rules

- Не меняйте bucket/prefix/CDN и схему object key — это нарушит иммутабельность и оставит orphan-объекты.
- Сохраняйте поведение «без overwrite/delete R2» и SHA-256 verification при любой правке `r2.py`/`publisher.py`/`transaction.py`.
- Не хардкодьте credentials и не выводите их в логи/отчёты (`reporting.py`).
- Перед правкой шаблонов rewrites проверяйте exact-span матчинг в `markdown.py` — rewrite должен затрагивать только destination `upload:`, не окружающий текст.

## Validation

```bash
cd tools/wiki-media
make lint                 # ruff format --check + ruff check (без изменений)
make test                 # uv sync --extra test && uv run pytest
make publish-dry-run MEDIA_PATH=content/guides   # план без записи; без credentials
make validate MEDIA_PATH=content/guides          # локальная проверка markers/изображений
```

Альтернативный путь запуска без uv — из корня репозитория: `make media-install` (pip install -e) затем `python3 -m wiki_media ...` (см. корневой `Makefile`).

## Nearby docs

- `tools/wiki-media/README.md` — каноническое описание commands, authoring (`upload:` syntax), R2 credentials и rollback.
- `/AGENTS.md`, `content/AGENTS.md` — контракты использования (`.wiki-media/inbox/`, image markers) на стороне сайта.
