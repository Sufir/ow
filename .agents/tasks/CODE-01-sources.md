# CODE-01 — собрать исходники правил в `.agents/sources/`

**Исполнитель:** Claude Code. **Автор/редактор задачи:** Claude (Cowork).
**Зачем:** у редактора нет доступа к shell и к извлечению текста из PDF. Нужны
текстовые версии всех источников, дальше по ним идёт вычитка правил.

**Рабочая директория:** `C:\YandexDisk\Oil Wars`
**Ничего вне `.agents/` не создавать, не переименовывать и не удалять.**

---

## Соглашение об именах

```
.agents/sources/<original|redesign>/<SRC-ID>__<короткое-имя>__<ГГГГ-ММ-ДД>.<ext>
```

Дата — день скачивания. Оригинальные PDF кладём рядом с извлечённым текстом:
`...__2026-09-10.pdf` и `...__2026-09-10.md`.

Текст из PDF сохранять **как есть**, без пересказа, без правок, без перевода.
Разрешено только: убрать колонтитулы и номера страниц, склеить слова, разорванные
переносом, проставить `## Страница N` как разделители.

---

## Шаг 1. Черновик правил редизайна

Скачать экспорт гуглдока в текст:

```
https://docs.google.com/document/d/1Eb49tnE9XtmucsIQImUPP2uk2OEXHUC292uYP6iSz30/export?format=txt
```

→ `.agents/sources/redesign/SRC-DRAFT__rules-draft__2026-09-10.md`

Нормализовать переводы строк в `\n` (в экспорте `\r\n`). Содержимое не править.
Файл большой (~58 КБ), это нормально.

## Шаг 2. Приложения редизайна

Извлечь текст из трёх PDF в `Drafts/` (исходники не трогать, только читать):

| Файл | Куда |
|---|---|
| `Drafts/Нефтяные войны (приложения) - Особые фабрики.pdf` | `redesign/SRC-APP-FACTORY__special-factories__2026-09-10.md` |
| `Drafts/Нефтяные войны (наемники).pdf` | `redesign/SRC-APP-MERC__mercenaries__2026-09-10.md` |
| `Drafts/Нефтяные войны (приложения) - Уникальные полковники.pdf` | `redesign/SRC-APP-COLONEL__unique-colonels__2026-09-10.md` |

Инструмент на выбор: `pdftotext -layout`, `pypdf`, `pdfplumber`. Если текстового слоя
нет и нужен OCR — **не делать OCR молча**, написать об этом в отчёте.

## Шаг 3. Оригинальный рулбук Cthulhu Wars

Два официальных PDF с Google Drive (ссылки со страницы поддержки Petersen Games):

| Что | ID на Drive | Куда |
|---|---|---|
| Рулбук, старая вёрстка | `1wCEAJffAPaKYqctvlrKnjseLUr2s2psy` | `original/SRC-RB-OLD__cw-rulebook-old-layout__2026-09-10.pdf` |
| Рулбук, новая вёрстка | `1320UvIs5J2c8kUHPIuItAThc7f1NGwD6` | `original/SRC-RB-NEW__cw-rulebook-new-layout__2026-09-10.pdf` |

Прямая ссылка: `https://drive.google.com/uc?export=download&id=<ID>`.
Google может отдать HTML-страницу подтверждения вместо файла — тогда пройти
подтверждение (`confirm=` токен) или использовать `gdown`.

Для каждого PDF рядом положить `.md` с извлечённым текстом.

**Проверка после скачивания:** файл начинается с `%PDF`, размер больше 1 МБ,
в тексте встречается слово `Cthulhu`. Если нет — считать шаг проваленным и сказать
об этом, а не сохранять мусор.

## Шаг 4. Эррата

1. Excel с таблицей балансных правок:
   `https://drive.google.com/file/d/1-E381PGmHI2N6uM7_DMt5o4_gvMTgcuC/view?usp=sharing`
   → `original/SRC-ERRATA-XLSX__balance-changes__2026-09-10.xlsx` + `.md` с содержимым листа.
2. **Ultimate Errata Pack** — PDF лежит по ссылке из поста Kickstarter:
   `https://www.kickstarter.com/projects/petersengames/cthulhu-wars-the-daemon-sultan/posts/2736627`
   Открыть пост, найти ссылку на PDF, скачать →
   `original/SRC-ERRATA-PACK__ultimate-errata-pack__2026-09-10.pdf` + `.md`.
   Если Kickstarter требует логин — **не обходить**, зафиксировать как недоступное.

Таблица балансных правок уже сохранена вручную в
`original/SRC-ERRATA__balance-changes-table__2026-09-10.md` — её перезаписывать не надо,
Excel нужен для сверки, что там нет строк сверх таблицы.

## Шаг 5. Официальный FAQ

`https://petersengames.freshdesk.com/support/solutions/articles/48000952254-cthulhu-wars-rules-faq`

→ `original/SRC-FAQ__cw-rules-faq__2026-09-10.md`

Сохранить **только тело статьи** в формате `**Q.** … / **A.** …`, с сохранением
разбивки по разделам («Core Game Rules» и далее). Выкинуть шапку Freshdesk, меню,
cookie-баннер, футер. Ничего не переводить.

Из того же раздела поддержки забрать ещё две статьи:

- `48001060995-cthulhu-wars-product-list` → `original/SRC-PRODUCTS__cw-product-list__2026-09-10.md`
- `48001230803-my-copy-of-daemon-sultan-is-missing-the-azathoth-die` → пропустить, это про брак печати.

## Шаг 6. Necronomicon

`https://necronomicon.app/rulebook` — приложение клиентское, обычный GET может вернуть
пустую оболочку. Если так — снять содержимое через headless-браузер или найти, откуда
приложение тянет данные (JSON-эндпоинт), и сохранить JSON.

→ `original/SRC-NECRO__rulebook__2026-09-10.md` (или `.json`)

Не получилось за 15 минут — бросить и записать в отчёт. Это PRIORITY 3, не блокер.

## Шаг 7. Проверить реестры

```
pip install pyyaml
cd "C:\YandexDisk\Oil Wars\.agents"
python tools\registry.py all
```

Скрипт **ни разу не запускался**. Ожидаемо может упасть. Если падает:

- чинить сам скрипт, но **не менять схему данных** — словари значений, имена полей и
  формат ID заданы в `registry/SCHEMA.md` и являются контрактом;
- YAML-файлы реестров не редактировать вообще;
- отчёты появятся в `.agents/out/`, `registry.db` — в `.agents/registry/`.

## Шаг 8. Отчёт

Дописать в конец `.agents/sources/README.md` раздел:

```markdown
## Прогон CODE-01 — 2026-09-10

| SRC-ID | Статус | Файл | Комментарий |
|---|---|---|---|
```

Статусы: `OK` / `PARTIAL` / `FAILED`. Для каждого `PARTIAL` и `FAILED` — одна строка
о том, что именно помешало, и рабочая ссылка, по которой Alek скачает руками.

Отдельно в отчёте: результат `registry.py all` и что пришлось в нём править.

---

## Границы

- Не редактировать правила, не переводить, не пересказывать, не «улучшать» текст
  источников. Задача — доставка сырья.
- Не трогать ничего вне `.agents/`, кроме чтения `Drafts/*.pdf`.
- Не обходить логины, капчи и платные стены. Недоступное — в отчёт списком.
- Не коммитить ничего в `Templates/.git`.
