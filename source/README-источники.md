# sources — исходные материалы

Машиночитаемый реестр — `../rules/registry/sources.yaml`. Здесь только раскладка файлов.

```
sources/
├── original/    материалы Cthulhu Wars: рулбук, эррата, FAQ, правила модулей,
│                выгрузки necronomicon.app и вики
└── redesign/    экспорт нашего черновика: гуглдок «Правила (черновик)»,
                 текст приложений из Drafts/
```

## Именование

```
<SRC-ID>__<короткое-имя>__<дата получения>.<ext>
```

Например: `SRC-DRAFT__rules-draft__2026-09-10.md`,
`SRC-ERRATA__cw-errata__2026-09-10.pdf`.

Снапшоты гуглдока не перезаписываются: каждый экспорт — новый файл с датой, чтобы
было видно, что менялось между сессиями.

## Статус на 2026-09-10

Пусто. Наполняется в фазе P1.

**Оригинала Cthulhu Wars в проекте нет** — единственный связанный файл —
`cthulhu-wars/Cthulhu_Wars_Faction_Selection_Cards.zip`. Рулбук, эррата и FAQ (PRIORITY 1–2)
подлежат сбору в P1; что не удастся достать — выносится списком Alek'у
(отчёт `../rules/reports/07-source-gaps.md`).

---

## Прогон CODE-01 — 2026-09-10

| SRC-ID | Статус | Файл | Комментарий |
|---|---|---|---|
| SRC-DRAFT | OK | `gdocs/SRC-DRAFT__rules-draft__2026-09-10.md` | Экспорт гуглдока в txt, без логина. 102 КБ, 829 строк. CRLF → LF, снят BOM; содержимое не правилось. |
| SRC-APP-FACTORY | OK | `gdocs/SRC-APP-FACTORY__special-factories__2026-09-10.md` | `pdftotext -layout`, 2 страницы. Исходник — широкая таблица 6 колонок (грани кубика), колонки в тексте расходятся построчно. Читать вместе с PDF. |
| SRC-APP-MERC | OK | `gdocs/SRC-APP-MERC__mercenaries__2026-09-10.md` | `pdftotext -layout`, 12 страниц. Текстовый слой чистый, OCR не понадобился. |
| SRC-APP-COLONEL | OK | `gdocs/SRC-APP-COLONEL__unique-colonels__2026-09-10.md` | `pdftotext -layout`, 2 страницы. Исходник — таблица из 5 колонок; колонка «Имя» физически отделена от строк способностей, поэтому в тексте имена идут отдельным блоком и **не выровнены** по способностям. Сопоставлять имя ↔ способность только по PDF. |
| SRC-RB-OLD | OK | `cthulhu-wars/SRC-RB-OLD__cw-rulebook-old-layout__2026-09-10.pdf` + `.md` | 77,5 МБ, `%PDF-1.5`, 254 страницы, «Cthulhu» встречается. Текст 786 КБ. |
| SRC-RB-NEW | OK | `cthulhu-wars/SRC-RB-NEW__cw-rulebook-new-layout__2026-09-10.pdf` + `.md` | 93,5 МБ, `%PDF-1.5`, 213 страниц, «Cthulhu» встречается. Текст 425 КБ. Подтверждение Google Drive не понадобилось, прямая ссылка отдала файл. |
| SRC-ERRATA-XLSX | OK | `cthulhu-wars/SRC-ERRATA-XLSX__balance-changes__2026-09-10.xlsx` + `.md` | 11 КБ, один лист `Feuil1`, диапазон B2:F30 = шапка + **28 строк данных**. Столько же строк в ручной `SRC-ERRATA__balance-changes-table__2026-09-10.md`, порядок совпадает. **Строк сверх таблицы нет.** Единственная разница: в Excel есть колонка `Item` с именем конкретного spellbook / карты (`The Red Sign`, `Ghroth`, `Passion`, …), которой в ручной таблице нет. Ручной файл не перезаписывался. |
| SRC-ERRATA-PACK | OK | `cthulhu-wars/SRC-ERRATA-PACK__ultimate-errata-pack__2026-09-10.pdf` + `.md` | 1,9 МБ, `%PDF-1.6`, 15 страниц. Логин Kickstarter **не потребовался**: пост #62 открыт публично, обход не применялся (см. ниже про 403). Ссылка из поста ведёт на Google Drive `1p5Mek8RGSaHgA4YQ3Ztdd3abpnoZXO6_`. Текстовый слой есть, но это листы карт — колонки местами накладываются, отдельные строки в тексте перемешаны. Как источник цитат — только вместе с PDF. |
| SRC-FAQ | OK | `cthulhu-wars/SRC-FAQ__cw-rules-faq__2026-09-10.md` | Тело статьи, 52 КБ. **159 пар Q/A**, разбивка по разделам сохранена. Шапка Freshdesk, меню, cookie-баннер, футер и Related Articles выброшены. Не переводилось. |
| SRC-PRODUCTS | OK | `cthulhu-wars/SRC-PRODUCTS__cw-product-list__2026-09-10.md` | 191 строка таблицы. В источнике это одна HTML-таблица, заголовки разделов (Onslaught 1/2/3/4, локализации) идут внутри неё обычными строками — так и сохранены. |
| SRC-NECRO | OK | `cthulhu-wars/SRC-NECRO__rulebook__2026-09-10.json` + `.md` | Страница `/rulebook` действительно отдаёт только оглавление. Найден JSON-эндпоинт `https://necronomicon.app/data-files/rulebook.json` (185 КБ, ключи `rules` / `variants` / `faq`) — сохранён как есть, headless-браузер не понадобился. `.md` рядом — только описание структуры, текст живёт в JSON. |
| — | пропущено | — | Статья `48001230803` (Azathoth die) не бралась: по условию задачи это брак печати, не правила. |

### Что мешало и как обошли

- **Kickstarter отдаёт 403 на `curl`** (антибот, не логин). Пост открыт через встроенный
  браузер, ссылка на PDF взята из тела поста. Ни логина, ни капчи не потребовалось,
  ничего не обходилось.
- **OCR не понадобился нигде** — у всех пяти PDF есть текстовый слой.
- **Два PDF-приложения редизайна — таблицы**, и `pdftotext -layout` их разваливает
  (см. строки SRC-APP-FACTORY и SRC-APP-COLONEL). Это ограничение носителя, а не потеря
  данных: PDF лежат рядом в `source/gdocs/pdf/`, сверять по ним.

### Шаг 7 — `registry.py all`

Прогон успешен, но не «из коробки»:

```
check:  ок (sources=17, baseline=0, redesign=0, issues=0, terms=0, numbers=0, icons=0)
build:  registry/registry.db
report: 00-executive-summary.md, 01-deviation-matrix.md, 02-author-decisions.md,
        03-issue-log.md, 04-numerical-audit.md, 05-terminology.md,
        06-icon-registry.md, 07-source-gaps.md
```

Что пришлось поправить:

1. **`build()` падал на датах.** `TypeError: Object of type date is not JSON serializable`
   — PyYAML разбирает `2026-09-10` в `datetime.date`, а `build()` всё, что не строка,
   гнал через `json.dumps`. Добавлена ветка: скаляры (`bool`, `int`, `float`,
   `datetime.date`, `datetime.time`) кладутся в SQLite через `str(v)`, контейнеры —
   по-прежнему через `json.dumps`. Добавлен `import datetime`.
   **Схема данных не менялась**: словари значений, имена полей и формат ID из
   `../rules/registry/SCHEMA.md` не тронуты. YAML-файлы реестров не редактировались.

Окружение: Python на машине нет (только заглушка Microsoft Store и Python 2.7 внутри
OpenOffice). Прогон сделан в Docker:

```
docker run --rm -v "C:/YandexDisk/Oil Wars/.agents:/w" -w /w python:3.12-slim \
  sh -c "pip install --quiet pyyaml && python tools/registry.py all"
```

### Требует внимания Alek

1. **`../rules/registry/sources.yaml` устарел по статусам.** Все 12 источников выше теперь
   `AVAILABLE`, но в YAML у них по-прежнему `REQUESTED` / `PARTIAL`, и `07-source-gaps.md`
   показывает их как недостающие. YAML по условию задачи не редактировался — нужна
   отдельная правка статусов.
2. **`SRC-FAQ`, один ответ без маркера.** В вопросе «Can I use *Energy Nexus* even if the
   Battle in the Area was not declared against me (or by me)?» в самом источнике перед
   ответом нет `A.` — абзац оставлен как есть, ничего не дописывалось.
3. **Оба рулбука вместе весят 171 МБ** и лежат в папке, синхронизируемой Яндекс.Диском.
   Если это нежелательно — PDF можно вынести, `.md` рядом самодостаточны для вычитки.

---

## Прогон CODE-02 — 2026-09-10

| Кусок | Статус | Файлы | Комментарий |
|---|---|---|---|
| 1. Colour Gates (SRC-RB-NEW) | OK | `cthulhu-wars/SRC-RB-NEW__colour-gates-table__2026-09-10.md`, `cthulhu-wars/pages/SRC-RB-NEW/стр-142.png`, `стр-143.png` | Таблица 6×10 восстановлена по координатам (PyMuPDF). **Страницы PDF — 142–143, а не 143–144**: нумерация книги (137–138) в ТЗ верна, PDF-нумерация сдвинута на единицу. Столбцы 1 `METEORITE` и 2 `FERTILITY` — на стр. 142, столбцы 3–6 — на стр. 143. Столбцы 1 и 6 — сплошной текст, как и сказано в ТЗ. Соответствие «заголовок ↔ колонка» подтверждено по `x` спанов. |
| 2. Особые фабрики (SRC-APP-FACTORY) | OK | `gdocs/SRC-APP-FACTORY__special-factories-table__2026-09-10.md`, `cthulhu-wars/pages/SRC-APP-FACTORY/стр-001.png` | **В PDF одна страница, не две.** Структура сделана 1:1 с куском 1. Границы ячеек однозначны: каждая ячейка колонок 2–5 начинается словом «Игрок», по 10 ячеек на колонку под 10 подписей цветов. Названия граней (`FERTILITY`, `FEASTING`, …) в русском PDF не напечатаны — восстановлены по строке «Белые (GLOW)», где источник сам их называет. |
| 3. Уникальные полковники (SRC-APP-COLONEL) | OK | `gdocs/SRC-APP-COLONEL__unique-colonels-table__2026-09-10.md`, `cthulhu-wars/pages/SRC-APP-COLONEL/стр-001.png` | **В PDF одна страница, не две.** Главное: соответствие «имя ↔ способность» восстановлено достоверно, без угадывания — верх строки с именем совпадает с верхом первой строки способности с точностью до 0,1 pt во всех 10 случаях. Проблема из CODE-01 была артефактом построчного `pdftotext`, а не потерей данных. PNG всё равно выложен. |
| 4. Ultimate Errata Pack | PARTIAL | `cthulhu-wars/pages/SRC-ERRATA-PACK/стр-001.png` … `стр-014.png`, `cthulhu-wars/SRC-ERRATA-PACK__cards-text__2026-09-10.md` | **В PDF 14 страниц, не 15** (в отчёте CODE-01 тоже указано 15 — цифру стоит поправить). PNG всех страниц выложены. Текст карт сгруппирован по рамкам: стр. 5–6 разобраны почти чисто (по 8 карт на лист), стр. 7–14 — по 1–2 карты на лист. `PARTIAL`, потому что: **стр. 1–4 вообще без текстового слоя** (чистый растр, только PNG), а в четырёх слотах карты наложены друг на друга и текстовые блоки физически перемешаны — они помечены ⚠ и годятся только вместе с PNG. Принадлежность карты к фракции в текстовом слое не закодирована (она в рисунке), поэтому не проставлена. |

### Ответ по `RULE-001` (кусок 1)

**Расхождение есть в самом PDF, извлечением оно не внесено.** Столбец `2 FERTILITY`,
стр. 142 PDF:

- GREEN (блок на `y=217`) — «earns an extra Elder Sign for a Ritual of Annihilation
  **this Doom Phase**.»
- PINK (блок на `y=415`) — «receives an extra Elder Sign for a Ritual of Annihilation
  **this turn**.»

Это два отдельных текстовых блока, «this turn» стоит отдельной строкой внутри блока PINK.
Попутно: в этих же двух ячейках расходятся и глаголы — `earns` у GREEN против `receives`
у PINK. Для сравнения, у PINK в столбце `4 MADNESS` формулировка — «receives an extra
Elder Sign for a Ritual of Annihilation **this Doom Phase**», то есть «this turn»
встречается во всей таблице ровно один раз.

В русской паре (кусок 2) этого расхождения нет: у «Розового» в столбце 2 стоит
«в этой фазе», как и во всех остальных ячейках.

Сам `issues.yaml` не редактировался.

### Поиск величины Power за `Unspeakable Oath` (кусок 4, `BL-UNIT-012`)

**Не найдено.** В `SRC-ERRATA-PACK__ultimate-errata-pack__2026-09-10.pdf` нет ни строки
`Unspeakable`, ни строки `Oath` — ни на одной из 14 страниц. Причём стр. 1–4 растровые,
без текстового слоя, поэтому по ним поиск по тексту в принципе невозможен: если карта
лояльности High Priest есть в паке, она может быть только там, и её надо смотреть глазами
по `cthulhu-wars/pages/SRC-ERRATA-PACK/стр-001.png` … `стр-004.png`.

Проверено заодно и в остальных источниках — величины Power там тоже нет, только ссылки
на карту лояльности:

- `SRC-RB-NEW`, стр. 3089: «Their key ability is Unspeakable Oath, (defined on their
  Loyalty Card), which allows a player to Sacrifice them for Power at any time.» — число
  не названо.
- `SRC-RB-NEW` стр. 3125–3128 и `SRC-RB-OLD` стр. 3536–3538 — только про то, что Unique
  High Priests этой способности не имеют.
- `SRC-FAQ` и `SRC-NECRO` — упоминания без числа.

Статус `GAP` у `BL-UNIT-012` остаётся обоснованным. `baseline.yaml` не редактировался.

### Шаг 5 — `registry.py all`

```
check:  ок (sources=17, baseline=95, redesign=0, issues=2, terms=27, numbers=0, icons=0)
build:  registry/registry.db
report: 00-executive-summary.md, 01-deviation-matrix.md, 02-author-decisions.md,
        03-issue-log.md, 04-numerical-audit.md, 05-terminology.md,
        06-icon-registry.md, 07-source-gaps.md
```

**Чинить ничего не пришлось.** Прогон прошёл с первого раза: ни синтаксических ошибок
YAML, ни значений вне словарей, ни битых ссылок валидатор не нашёл. Правка `build()` из
CODE-01 (даты в SQLite) на месте и работает. Ни один YAML-файл реестра в этом прогоне
не открывался на запись.

### Окружение

Python на машине по-прежнему нет, `pdftoppm` тоже нет. Всё сделано в Docker: собран
локальный образ `ow-pdf` (`python:3.12-slim` + `pymupdf`, `pdfplumber`, `pyyaml`),
рендер PNG — `PyMuPDF get_pixmap` при 200 dpi (эквивалент `pdftoppm -r 200 -png`),
разбор таблиц — `get_text("dict")` с координатами. `pdfplumber` в итоге не понадобился.
Реестры прогнаны отдельным контейнером `python:3.12-slim`, командой из ТЗ.

### Требует внимания Alek

1. **Три расхождения в паспортах файлов.** Errata Pack — 14 страниц, а не 15 (цифра 15
   стоит и в CODE-02, и в отчёте CODE-01). Оба PDF-приложения редизайна — по одной
   странице, а не по две. Ни один из этих файлов не менялся, речь только о цифрах в
   описаниях.
2. **Стр. 1–4 Errata Pack без текстового слоя.** В отчёте CODE-01 сказано «текстовый слой
   есть» — это верно для стр. 5–14, но не для первых четырёх. Если оттуда нужны цитаты,
   потребуется OCR или чтение глазами по PNG.
3. **Опечатки в обоих PDF редизайна** (оставлены как есть, перечислены в `.md`-файлах):
   `FRTILITY`, `ээфект`, `олжен`, «выших кругах», «присутсвует», «заплалите»,
   «не участвует не участвует», «вам вашему юниту».
4. **Колонка «Сила» у всех десяти уникальных полковников равна `0`.** Ничего не правил,
   но выглядит как незаполненное поле, а не как значение.
