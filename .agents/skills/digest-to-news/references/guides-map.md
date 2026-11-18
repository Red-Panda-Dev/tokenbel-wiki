# Карта руководств

Ссылки в новости — относительные, от корня сайта:
`[«Аналитика портфеля»](/guides/rukovodstvo-polzovatelia/analitika-portfelia/)`.
Ставьте ссылку, когда изменение касается страницы, у которой есть руководство. Одна
ссылка на тему, обычно в конце абзаца или пункта. Название руководства берите из его
`title`.

Список мог устареть — сверяйтесь с актуальным:

```bash
grep -H '^title:' content/guides/*/*/index.md
```

`check_news.py` ругается на ссылку, если страницы нет в `content/`.

| Область изменений                                             | Руководство                                                             |
| ------------------------------------------------------------- | ----------------------------------------------------------------------- |
| Портфель: вкладка «Позиции», фильтры, группировка, экспорт    | `/guides/rukovodstvo-polzovatelia/pozitsii-portfelia/`                  |
| Портфель: вкладка «История», графики стоимости и структуры    | `/guides/rukovodstvo-polzovatelia/istoriia-stoimosti-portfelia/`        |
| Портфель: вкладка «Аналитика», диверсификация, матрица сроков | `/guides/rukovodstvo-polzovatelia/analitika-portfelia/`                 |
| Портфель: вкладка «Выплаты», расписание поступлений           | `/guides/rukovodstvo-polzovatelia/vyplaty-portfelia/`                   |
| Личный кабинет, настройки, уведомления, лимиты, избранное     | `/guides/rukovodstvo-polzovatelia/licnyi-kabinet/`                      |
| Регистрация, вход, Google/Telegram                            | `/guides/rukovodstvo-polzovatelia/registraciia-i-vxod/`                 |
| Тарифы и лимиты                                               | `/guides/rukovodstvo-polzovatelia/tarify/`                              |
| Курсы валют и драгметаллов, ставка НБРБ, индекс металлов      | `/guides/rukovodstvo-polzovatelia/kursy-valyut-i-dragmetallov/`         |
| Доходность к погашению токенов (YTM), вторичный рынок         | `/guides/rukovodstvo-polzovatelia/doxodnost-k-pogaseniiu-ytm/`          |
| Динамика торгов акциями                                       | `/guides/rukovodstvo-polzovatelia/dinamika-torgov-akciiami/`            |
| Динамика торгов облигациями                                   | `/guides/rukovodstvo-polzovatelia/dinamika-torgov-obligaciiami/`        |
| Статистика акций за 30 дней                                   | `/guides/rukovodstvo-polzovatelia/statistika-akcii-za-30-dnei/`         |
| Статистика облигаций за 30 дней                               | `/guides/rukovodstvo-polzovatelia/statistika-obligacii-za-30-dnei/`     |
| Страница акции: дивиденды, торги, история изменений данных    | `/guides/kak-eto-rabotaet/stranica-akcii/`                              |
| Страница облигации: условия, плавающий купон, погашение       | `/guides/kak-eto-rabotaet/stranica-obligacii/`                          |
| Страница эмитента бумаг                                       | `/guides/kak-eto-rabotaet/stranica-emitenta-bumag/`                     |
| Загрузка финансовых отчётов компаний                          | `/guides/kak-eto-rabotaet/dobavlenie-finansovogo-otcheta/`              |
| Лента событий, AI-анализ новостей                             | `/guides/kak-eto-rabotaet/ai-analizator-finansovyx-novostei/`           |
| Открытый API, MCP, AI-доступ к данным                         | `/guides/kak-eto-rabotaet/ai-dostup-k-dannym-tokenbel/`                 |
| Драгметаллы: обзорная статья                                  | `/guides/rukovodstvo-polzovatelia/investicii-v-dragmetally-v-belarusi/` |
| Пассивный доход: обзорная статья                              | `/guides/rukovodstvo-polzovatelia/passivnyj-dohod-v-belarusi/`          |

Другие внутренние страницы: статистика проекта `/about/statistics/` (для «Вех»),
статистика рынка `/statistics/…`, прошлые новости `/news/<slug>/`.

Страницы дашборда (не вики) — абсолютным URL `https://dashboard.tokenbel.info/<путь>/`:
`/secondhand/`, `/events/`, `/statistics/market/`, `/statistics/rates/`, `/company/<id>`.
