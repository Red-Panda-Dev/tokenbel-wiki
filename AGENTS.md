# Руководство для агентов

- Это Hugo-сайт TokenBel Wiki; основной код находится в `content/`, `layouts/`, `assets/` и `static/`.
- Контент храните в Markdown: section landing pages — в `_index.md`, статьи — в leaf bundles с `index.md` и вложениями рядом.
- Не используйте внешние Hugo-темы: presentation остаётся в локальных `layouts/` и `assets/css/main.css`.
- Пользовательские тексты интерфейса и нового контента должны быть на русском языке.
- При будущей миграции сохраняйте BookStack URLs через front matter `url` и `aliases`.
- Не редактируйте и не коммитьте `public/`: это результат сборки.
- Перед завершением запускайте `hugo --gc --minify` и проверки наличия `public/index.html` и `public/404.html`.
