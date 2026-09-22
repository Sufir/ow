# out — производные артефакты

Здесь лежат сборки и отчёты. **Всё содержимое генерируется** и руками не правится:
правится YAML в `../registry/`, дальше `python ../tools/registry.py all`.

Генерируемые отчёты:

| Файл | Что |
|------|-----|
| `00-executive-summary.md` | Сводка: объём baseline, счётчики issue по критичности, типу и статусу |
| `01-deviation-matrix.md` | Mechanical deviation report |
| `02-author-decisions.md` | Вопросы, требующие решения Alek |
| `03-issue-log.md` | Полный issue log |
| `04-numerical-audit.md` | Сплошная сверка чисел |
| `05-terminology.md` | Карта терминов оригинал → редизайн |
| `06-icon-registry.md` | Реестр иконок |
| `07-source-gaps.md` | Чего не хватает из источников |

Исключение — `rulebook-draft.md`: это рабочий текст рулбука, он пишется руками
в P8 и живёт здесь до переноса чистовика в корень проекта.
