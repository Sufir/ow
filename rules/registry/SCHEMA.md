# SCHEMA — описание реестров

Источник истины — YAML-файлы в этой папке. `registry.db` (SQLite) и отчёты в `../reports/`
собираются из них скриптом `../tools/registry.py` и руками не правятся.

**Подреестр карты — `board/`, своя схема `board/SCHEMA.md`.** Реконструкция
оригинального игрового поля (области, типы, материки, связи, четыре раскладки
на 3–5 игроков) живёт отдельно: там граф, а не правила, и своё ID-пространство
(`MR-*`, `ME-*`, `MC-*`, `MAP-*`). Собирается своим скриптом `board/tools/map.py`,
в `registry.db` не попадает, `registry.py` его не валидирует. Общие с этим
реестром — только `sources.yaml` и дисциплина ссылок на источники.

Общие соглашения:

- Кодировка UTF-8, отступ 2 пробела, длинный текст — блочный скаляр `>` или `|`.
- Даты — `YYYY-MM-DD`.
- Пустое значение — `null`, а не пустая строка.
- ID уникальны в пределах своего префикса и не переиспользуются после удаления записи.

Словарь `AREA` (общий для всех реестров):
`SETUP`, `ROUND`, `ACTION`, `MOVE`, `COMBAT`, `GATE`, `POWER`, `DOOM`, `RITUAL`,
`TECH`, `UNIT`, `FACTION`, `MAP`, `VICTORY`, `MODULE`, `GLOSSARY`.

---

## sources.yaml — реестр источников

```yaml
- id: SRC-RB2                     # SRC-###
  side: ORIGINAL                  # ORIGINAL | REDESIGN
  priority: 1                     # 1..5 по иерархии из RULES-CHARTER §5; для REDESIGN — null
  kind: RULEBOOK                  # RULEBOOK | ERRATA | FAQ | MODULE | WIKI | DB | FORUM | DRAFT | APPENDIX
  title: Cthulhu Wars Rulebook
  edition: null                   # издание/версия, если известно
  url: null
  local_path: source/cthulhu-wars/... # относительно rules/, либо null
  retrieved: null                 # дата получения
  status: REQUESTED               # AVAILABLE | REQUESTED | UNREACHABLE | PARTIAL
  need: >                         # что именно нужно, если REQUESTED
  notes: null
```

## baseline.yaml — ORIGINAL RULE BASELINE

```yaml
- id: BL-COMBAT-001               # BL-<AREA>-###
  area: COMBAT
  title: Краткое имя правила
  rule: >                         # каноническая формулировка правила оригинала
  numbers: {}                     # словарь именованных чисел: {dice_per_unit: 1}
  timing: null                    # когда происходит
  prerequisites: []               # предпосылки
  targets: null                   # кто/что может быть целью
  cost: null
  limits: []                      # ограничения, частота
  exceptions: []
  interactions: []                # ссылки на другие BL-* и словесное описание
  sources:                        # минимум один
    - {ref: SRC-RB2, loc: "p.12", note: null}
  errata_applied: []              # [SRC-ERR1#3] — что наложено поверх рулбука
  faq_applied: []
  confidence: HIGH                # HIGH | MEDIUM | LOW
  status: VERIFIED                # VERIFIED | PROVISIONAL | GAP
```

`status: GAP` — правило известно, что существует, но текст источника недоступен.

## redesign.yaml — REDESIGN RULE BASELINE

```yaml
- id: RD-COMBAT-001               # RD-<AREA>-###
  baseline_ref: BL-COMBAT-001     # null, если пары в оригинале нет (кандидат в EXTRA)
  area: COMBAT
  title: null
  text_ru: >                      # формулировка из черновика, дословно
  loc: "Правила (черновик) → Бой → Розыгрыш"
  extracted: 2026-09-10
  match: UNVERIFIED               # EXACT | RENAMED | DEVIATION | MISSING |
                                  # AMBIGUOUS | CONTRADICTORY | UNVERIFIED
  issues: []                      # [DEV-001]
```

Отсутствующее в редизайне правило оригинала записи `RD-*` не получает — оно
фиксируется issue `MISS-###` со ссылкой на `BL-*`.

## issues.yaml — единый issue log

```yaml
- id: DEV-001                     # DEV | MISS | EXTRA | RULE | TISS | ICON | REF | PLAY | RED | SRC | NUM
                                  # TERM здесь НЕ используется — он занят terms.yaml (D-028).
                                  # Issue типа TERMINOLOGY носят префикс TISS-###.
                                  # RED-### — находка red team (P11): тип PLAYTHROUGH, но заведена
                                  # поиском эксплойтов, а не проигрыванием партии
  type: DEVIATION                 # DEVIATION | MISSING | EXTRA | AMBIGUITY | TERMINOLOGY |
                                  # ICON | REFERENCE | PLAYTHROUGH | SOURCE-CONFLICT |
                                  # NUMBER | OUT-OF-SCOPE
  category: [NUMBER]              # NUMBER | TIMING | COST | LIMIT | TARGET | CONDITION |
                                  # EFFECT | SEQUENCE | EXCEPTION | INTERACTION |
                                  # VICTORY | SETUP | OTHER
  area: COMBAT
  batch: B3                       # батч аудита из PLAN.md
  title: Краткая суть
  baseline_ref: BL-COMBAT-001     # или null
  redesign_ref: RD-COMBAT-001     # или null
  original: >                     # что в оригинале
  redesign: >                     # что в черновике
  difference: >                   # в чём именно разница
  severity: ERROR                 # CRITICAL | ERROR | WARNING | INFO
  status: OPEN                    # OPEN | AUTHOR-DECISION-REQUIRED | DECIDED |
                                  # APPLIED | CLOSED | WONTFIX
  proposal: >                     # предлагаемое разрешение
  confidence: HIGH
  decision: null                  # что решил Alek
  decision_ref: null              # D-###
  opened: 2026-09-10
  closed: null
```

**Правило поля `closed`:** дата проставлена тогда и только тогда, когда issue
завершён, то есть при `status: CLOSED` **или** `status: WONTFIX`. При любом
другом статусе `closed: null`. Проверяется валидатором.

`WONTFIX` включён в это правило намеренно: он означает «разобрались и решили
не чинить», то есть работа по issue закончена. Без даты такая запись
неотличима от живой в любом хронологическом срезе.

Для `type: SOURCE-CONFLICT` дополнительно:

```yaml
  source_a: {ref: SRC-RB2, says: "..."}
  source_b: {ref: SRC-ERR1, says: "..."}
  newer: SRC-ERR1
  official: both
```

Для `type: PLAYTHROUGH` дополнительно:

```yaml
  step: "Ход 1, фаза сбора нефти"
  assumption: >                   # что пришлось додумать
```

## terms.yaml — карта терминов

```yaml
- id: TERM-001
  original_en: Power
  original_ru: Сила               # если есть устоявшийся русский перевод
  redesign: Нефть
  area: POWER
  semantic_equivalent: true       # true = замена чисто терминологическая
  status: PROVISIONAL             # PROVISIONAL | CANONICAL | CONFLICT | UNMAPPED
  variants_found: []              # разнобой, найденный в черновике
  refs: []                        # [BL-POWER-001]
  notes: null
```

`status: UNMAPPED` — термин одной стороны без пары на другой.
`status: CONFLICT` — один термин редизайна покрывает два разных понятия оригинала
или наоборот; требует `TERM-###` issue.

## numbers.yaml — numerical audit

```yaml
- id: NUM-001
  subject: Максимум нефти на планшете
  area: POWER
  original: 25
  redesign: 25
  unit: null                      # "шт", "кубика", "очка" — если нужно
  match: PASS                     # PASS | FAIL | UNKNOWN
  baseline_ref: BL-POWER-003
  redesign_ref: RD-POWER-003
  issue: null                     # NUM-### или DEV-###, если FAIL
```

Проверяются все числа без исключения: стоимости, количества, лимиты, дальности,
боевые значения, пороги победы, кубики, число игроков, число юнитов, числа в тайминге.

## icons.yaml — icon registry

```yaml
- id: ICON-001
  placeholder: "{OIL}"            # единый синтаксис для Markdown
  glyph: null                     # кодовая точка в кастомном шрифте, например ""
  font: null
  meaning: Нефть
  original_concept: Power
  redesign_term: Нефть
  term_ref: TERM-001
  status: UNMAPPED                # OK | MISSING | DUPLICATE | UNMAPPED | EMOJI-SUBSTITUTE
  used_in: []                     # где встречается
  notes: null
```

## factions.yaml — реестр фракций

**Вне объёма аудита правил.** По `RULES-CHARTER.md` фракции в задачу P0–P12
не входят; файл лежит здесь только потому, что здесь живут все машиночитаемые
реестры проекта. `rules/tools/registry.py` его не валидирует и в `registry.db`
не собирает. Заведён 2026-09-11.

Пять разделов верхнего уровня:

- `meta` — счётчики и блок `universal`: соответствия, общие для всех фракций
  (6 рекрутов = 6 Acolytes, старт 8 нефти, Полковник = High Priest,
  Энграммы = Brain Cylinders), чтобы не повторять их в каждой записи.
- `original` — 12 фракций Cthulhu Wars, `CW-F-##`: 11 из компендиума SRC-RB-NEW
  плюс The Invasion (CW-F9), которой там нет.
- `redesign` — 8 канонических фракций `OW-F-##` плюс 3 вне состава `OW-X-##`.
- `mapping` — пары с доказательствами, `MAP-##`.
- `findings` — находки, `FAC-###`. Отдельно от `issues.yaml` намеренно:
  смешивать фракционные находки с `DEV`/`MISS`/`TISS` нельзя.

```yaml
original:
  - id: CW-F-01                   # CW-F-##
    name_en: Great Cthulhu
    scope: null                   # IGNORED — фракция в работу не берётся (решение автора);
                                  # null — берётся
    set: CORE                     # CORE | EXPANSION
    product_code: CW              # код продукта Petersen Games (CW, CW-F1…CW-F9)
    rulebook_page: 43             # страница книги в SRC-RB-NEW; null, если фракции там нет
    start_power: 8                # стартовый запас Power; у Daemon Sultan — 4
    goo:                          # null = у фракции нет Great Old One
      name_en: Cthulhu
      count: 1
      cost: 10                    # число ИЛИ null, если стоимость задаётся формулой
      cost_note: null             # формула/условие стоимости; обязателен, если cost: null
      combat: 6                   # число ИЛИ null, если бой задаётся формулой
      combat_note: null           # формула боя; обязателен, если combat: null
      awaken: null                # условия пробуждения, кратко
      ability: null               # способность GOO с faction card
    secondary_goo: null           # второй Great Old One, если есть; та же структура
    unique_ability:               # уникальная способность фракции с faction card
      {name_en: Immortal, timing: Ongoing, text: "…"}
    units:
      - {name_en: Deep One, category: MONSTER, count: 4, cost: 1, combat: 1,
         spellbook: Devolve}      # category: CULTIST | MONSTER | TERROR | GOO
                                  # cost/combat — те же правила с null и *_note
                                  # spellbook — какая карта относится к отряду
    buildings: []                 # постройки-не-отряды: Cathedral, Chaos Gate,
                                  # Lord's Shadow. Поля как у units, без category
    extras: []                    # жетоны, тайлы, кубики фракции
    unused_components: []         # доложено в коробку, но фракцией не используется
    start_area: South Pacific     # null, если неизвестен (FAC-016) или задан правилом
    start_area_source: null       # откуда взят регион, если он восстановлен
    signature: []                 # уникальные механики — основа сопоставления
    spellbooks: []                # ровно 6, кроме Tcho-Tcho (12 карт, играют 6)
    spellbooks_status: COMPLETE   # COMPLETE | PARTIAL
    spellbooks_note: null
    stats_confidence: HIGH        # HIGH — количества по рулбуку, статы сошлись
                                  #        у SRC-WIKI и SRC-NECRO-FAC
                                  # MEDIUM — сошлись только фанатские источники
                                  # LOW — один источник
    stats_confidence_note: null   # обязателен при MEDIUM и LOW
    sources: [{ref: SRC-RB-NEW, loc: "с. 43"}]
    redesign_ref: OW-F-01         # null, если пары нет
    redesign_hypothesis: null     # OW-X-##, если пара только предполагается

redesign:
  - id: OW-F-01                   # OW-F-## в составе, OW-X-## вне состава
    name: Островная Империя       # эталонное написание из CLAUDE.md §2
    colour: тёмно-зелёный
    status: CANON                 # CANON | OUT-OF-SCOPE
    scope: null                   # IGNORED | null — как в `original`
    queue: 1.0                    # очередь расстановки с планшета.
                                  # ТИП — float, не int (D-048, уточнение 2026-09-22).
                                  # Целые значения пишутся с хвостом `.0`. Дробные
                                  # нужны, чтобы втиснуть новую фракцию между двумя
                                  # уже напечатанными: 1.5 встанет между Островной
                                  # Империей и Эйркрафт Корпорейшн, ничего не сдвигая.
                                  # На планшете печатается как 01.0 (D-053, D-060).
                                  # null — если определить нельзя (см. queue_note)
    start_oil: 8
    start_region: Юг Тихого океана
    units:
      - {name: Моторизированный морпех, group: Боевые машины, stats: [4, 1, 1]}
      # stats = [количество, стоимость в нефти, боевые кубики] — порядок столбцов планшета
    robot_creation: null          # шаги создания б/р, дословно с планшета
    robot_combat_formula: null    # если сила задана формулой, а не числом
    abilities: [{name: Диверсия, note: "Битва. Тактическая подготовка"}]
    technologies: []              # 6 названий из Cards - Технологии и задачи.json
    extras: []
    sources: [{ref: "FC-Островная Империя"}]
    baseline_ref: CW-F-01         # null, если пары нет
    baseline_hypothesis: null     # CW-F-##, если пара только предполагается

mapping:
  - id: MAP-01
    redesign_ref: OW-F-01
    baseline_ref: CW-F-01
    pair: Островная Империя ↔ Great Cthulhu
    author_claim: true            # соответствие названо Alek, а не выведено здесь
    verdict: CONFIRMED            # CONFIRMED | REJECTED | HYPOTHESIS | UNVERIFIED
    confidence: HIGH              # HIGH — 3+ независимых числовых/механических совпадения
                                  # MEDIUM — совпадения есть, числовой сверки нет
                                  # LOW — только тематика
    status: null                  # DEFERRED, если пару решено не разбирать; иначе null
    decision: null                # что решил Alek
    decided: null                 # дата решения
    evidence: []                  # каждый пункт — проверяемое совпадение со ссылкой
    deviations: []                # расхождения внутри подтверждённой пары
    unverified: []                # что сверить не удалось из-за пробела в источниках
    issue: null                   # FAC-###

findings:
  - id: FAC-001                   # FAC-###
    type: DATA-STALE              # DATA-STALE | DEVIATION | AMBIGUITY |
                                  # SOURCE-GAP | HYPOTHESIS | TERMINOLOGY
    area: FACTION
    title: Краткая суть
    severity: ERROR               # CRITICAL | ERROR | WARNING | INFO
    status: OPEN                  # OPEN | AUTHOR-DECISION-REQUIRED | DEFERRED |
                                  # DECIDED | CLOSED
    decision: null                # что решил Alek; обязательно при DEFERRED и DECIDED
    decided: null                 # дата решения; обязательна там же
    subject: OW-F-07              # OW-F-## / CW-F-## / список / null
    detail: >
    need: null                    # что нужно добрать, если type: SOURCE-GAP
    proposal: >
```

`DEFERRED` — решение принято, и оно состоит в том, чтобы зафиксировать находку
и пока по ней не работать. Отличается и от `OPEN` (никто не смотрел), и от
`CLOSED` (сделано). У записи в `DEFERRED` поля `decision` и `decided` заполнены,
а `proposal` остаётся — он понадобится, когда задачу возьмут в работу.

**Правило сопоставления.** Пары выводятся по свойствам: количества фигурок
по категориям, стоимости, боевые значения, формула силы боевого робота,
уникальные механики и не-отрядные компоненты. Названия — только
дополнительный признак, сами по себе они основанием не являются.

---

## components.yaml — реестр физических компонентов

**Отвечает на один вопрос: что физически есть в коробке, из чего сделано
и в каком состоянии.** Игровые данные компонента здесь не живут и не
дублируются — на них стоят ссылки. Заведён 2026-09-22, сменил черновую
ревизию `Инвентаризация компонентов.xlsx` (27.08.2026).

Собирается `rules/tools/components.py`:

```
python rules/tools/components.py check    # валидация
python rules/tools/components.py all      # check + reports/16-components.md
```

Валидатор проверяет словари, уникальность ID, правило даты решения,
**существование каждого пути** в `files` и `master` (реестр обязан указывать
на файлы, а не на намерения), и ссылки на находки **в обе стороны**: если
находка названа предметом записи, запись обязана перечислить её в `findings`.

Дедупликация проверяется двумя способами. Первый — поля: `count` и
`count_per_faction` при `count_source: FACTIONS` запрещены. Второй — свободный
текст записей секции `faction` и находок про них: там не должно встречаться
ни числа рядом со словом «Очередь», ни количества вида `×N`. Цифры внутри
идентификаторов (`D-048`, `§2.4`, годы) числами не считаются. Если число
понадобилось в прозе — значит, фраза пересказывает `factions.yaml` вместо
того, чтобы на него сослаться.

`registry.py` его не валидирует и в `registry.db` не собирает — по той же
причине, что и `factions.yaml`: это не реестр правил.

### Дедупликация — главное правило файла

Количества отрядов фракции в `components.yaml` не пишутся **ни разу**.
Запись фракционного компонента несёт `count_source: FACTIONS` и `count_ref`
на путь внутри `factions.yaml`; число подставляет отчёт при сборке.
Валидатор падает, если рядом с `count_source: FACTIONS` оказалось
собственное число.

`meta.truth_map` перечисляет, где живёт истина по каждому вопросу:
состав фракции — `factions.yaml`, числа правил — `numbers.yaml`,
термины — `terms.yaml`, поле — `board/`, решения — `DECISIONS.md`.
Если понадобилось записать сюда что-то из этого списка — значит, запись
заводится не в том файле.

### Четыре секции и находки

| Секция | ID | Что внутри |
|---|---|---|
| `common` | `COMP-C-##` | по одному на коробку, от фракции не зависят |
| `faction` | `COMP-F-##` | одна запись на ТИП компонента, состояние по фракциям в `by_faction` |
| `variant` | `COMP-V-##` | компоненты вариантов игры |
| `not_taken` | `COMP-N-##` | взятое из оригинала обратно: запись заведена, чтобы вопрос не открывался заново |
| `findings` | `COMP-I-###` | находки по компоненту как по физической вещи |

Находки по правилам остаются в `issues.yaml`, по фракциям — в
`factions.yaml → findings`. Здесь на них ставится ссылка в `refs`,
дубликат не заводится.

### Три оси состояния

Компонент завершён тогда и только тогда, когда закрыты все три. Одна ось
не заменяет другую: свёрстанный, но не напечатанный компонент не готов,
и напечатанный с невычитанным текстом — тоже.

| Ось | Словарь | Про что |
|---|---|---|
| `content` | `N/A` `TODO` `IN-REVIEW` `ISSUES` `VERIFIED` | текст и числа вычитаны, сверены с оригиналом |
| `design` | `N/A` `NONE` `DRAFT` `IN-REVIEW` `APPROVED` | арт и вёрстка приняты Alek |
| `production` | `N/A` `NONE` `READY` `PARTIAL` `DONE` `UNKNOWN` | физически изготовлено, нарезано, напечатано, куплено |

Итог считает отчёт: `ГОТОВО`, если все три оси в `{VERIFIED, APPROVED, DONE, N/A}`;
`не начато`, если все в `{TODO, NONE, N/A}`; `не подтверждено`, если
`production: UNKNOWN`; иначе `в работе`. У записи с `by_faction` итог —
**худший** из состояния по умолчанию и отличий по фракциям.

**`production: UNKNOWN` — не «скорее всего готово».** Это «файл есть,
факт изготовления не подтверждён». Отчёт выносит такие записи отдельным
списком. Достраивать состояние догадкой запрещено: поле `evidence`
обязательно и говорит, чем именно состояние подтверждено.

### Запись

```yaml
common:
  - id: COMP-C-05                 # COMP-C-## | COMP-F-## | COMP-V-##
    name: Маркер Судного дня      # наш нейминг, эталонный
    original: Ritual of Annihilation Marker
    original_set: BASE            # BASE | ONSLAUGHT-1..4 | PACK-<код> | NONE
    count: 1                      # наше количество; null, если не зафиксировано
    count_original: 1
    count_source: RULES           # RULES | FACTIONS | FILE | DERIVED |
                                  # DECISION | PURCHASE | NONE
    count_ref: null               # путь в factions.yaml, NUM-###, D-###, файл
    count_status: FIXED           # FIXED | OPEN | CONFLICT
                                  # OPEN требует записи в findings
    carrier: ACRYLIC              # BOOK | SHEET | CARD | TOKEN-CARDBOARD |
                                  # ACRYLIC | MINIATURE | PURCHASED |
                                  # BANNER | NONE
    spec: {shape: круглый жетон, size: ⌀15 мм}   # физика: размер, формат, материал
    files: []                     # реальные пути в репозитории
    generator: null               # чем пересобирается, если пересобирается
    master: null                  # мастер для типографии или резки
    truth: rules/RULEBOOK.md      # где живёт содержимое компонента
    state: {content: VERIFIED, design: APPROVED, production: NONE}
    evidence: >                   # ОБЯЗАТЕЛЕН: чем подтверждено состояние
    refs: []                      # D-### / DEV- / MISS- / PLAY- / FAC- / NUM-
    blocks_print: false           # мешает ли компонент отправить НАБОР в типографию.
                                  # Не про книгу: её текст ни от одного компонента
                                  # не зависит (D-021 — фракционная конкретика живёт
                                  # на планшетах, книга её не дублирует). true ставится,
                                  # когда в компоненте есть дефект, который
                                  # молча уедет в типографию: файл выглядит
                                  # готовым, а игру ломает. Не «компонент ещё
                                  # не сделан» — это видно по осям состояния
    findings: [COMP-I-004]        # COMP-I-###
    notes: >
```

Дополнительно в секции `faction`:

```yaml
    per_faction: true
    count_per_faction: 6          # либо count_source: FACTIONS без числа
    by_faction:                   # ТОЛЬКО отличия от состояния по умолчанию
      OW-F-06:
        state: {content: ISSUES, design: DRAFT, production: NONE}
        reason: >                 # обязателен
        refs: []
        blocks_print: true
```

В секции `not_taken` полей три: `original`, `original_set`, `replaced_by`
(ID нашей записи или `null`) и обязательный `reason`.

### Находка

```yaml
findings:
  - id: COMP-I-004                # COMP-I-###
    type: NAMING                  # COUNT | SPEC | NAMING | STATE | SOURCE-GAP
    subject: COMP-C-05            # ID записи или список ID
    title: Краткая суть
    severity: WARNING             # CRITICAL | ERROR | WARNING | INFO
    status: OPEN                  # OPEN | AUTHOR-DECISION-REQUIRED |
                                  # DEFERRED | DECIDED | CLOSED | WONTFIX
    detail: >
    proposal: >
    decision: null                # обязателен при DECIDED, DEFERRED, CLOSED
    decided: null                 # дата; правило то же, что у issues.yaml
```
