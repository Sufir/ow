# SCHEMA — реконструкция игрового поля

Подреестр карты. Источник истины — YAML-файлы в этой папке. Всё в `derived/`
и отчёт `board/reports/11-map.md` собираются скриптом `board/tools/map.py` и руками
не правятся.

Общие соглашения те же, что в `rules/registry/SCHEMA.md`: UTF-8, отступ 2 пробела, даты
`YYYY-MM-DD`, пустое значение — `null`, ID не переиспользуются.

**Объём.** Только оригинальная Earth Map базовой коробки, стороны «3 игрока»
и «5 игроков», конфигурации на 3, 4 и 5 игроков. Карты 6–8, 9–11, Oversized,
Dreamlands, Library, Primeval и map packs — вне объёма (`MF-006`).

---

## Модель

Поле оригинала — **два планшета**, `LEFT` (Western Hemisphere) и `RIGHT`
(Eastern Hemisphere), каждый напечатан с двух сторон: `3P` и `5P`.
Конфигурация — пара «сторона левого × сторона правого»:

| Конфигурация | left | right | Областей |
|---|---|---|---|
| `MC-3P` | 3P | 3P | 13 |
| `MC-4P-A` (3-5) | 3P | 5P | 17 |
| `MC-4P-B` (5-3) | 5P | 3P | 17 |
| `MC-5P` | 5P | 5P | 21 |

Океанские области на обеих сторонах одинаковы; различается только дробление
суши. Отсюда арифметика: 7 общих областей (6 океанов + Антарктида) + 3 или 7
суши слева + 3 или 7 суши справа.

**Правило присутствия.** Область входит в конфигурацию, если `side == BOTH`
либо `side` совпадает со стороной её планшета (`board`). Ребро входит в
конфигурацию тогда и только тогда, когда в неё входят обе его области.
Это корректно, потому что связей «суша — суша» между разными планшетами на
карте нет: планшеты разделены океаном.

**Граф с ограничениями.** Вершина несёт тип (`LAND` / `OCEAN`) и
принадлежность: суша — к материку (`landmass`), океан — к бассейну (`basin`).
Дробные области 5P ссылаются на свою область 3P полем `parent`, поэтому
разбиение суши проверяемо: `parent` для всех `5P` заполнен, и объединение
детей покрывает родителя.

Геометрия (контуры, центроиды, координаты) в этот подреестр **не входит** —
решение Alek от 2026-09-16. `contact_px` в `edges.yaml` — не геометрия, а
доказательство смежности.

---

## regions.yaml — области

```yaml
regions:
  - id: MR-L5-NAMW            # MR-<SCOPE>-<SHORT>; SCOPE: OC | SH | L3 | R3 | L5 | R5
    name_en: North America West   # как напечатано на поле оригинала
    type: LAND                    # LAND | OCEAN
    landmass: NORTH_AMERICA       # для LAND; для OCEAN — null
                                  # NORTH_AMERICA | SOUTH_AMERICA | EUROPE | ASIA |
                                  # AFRICA | AUSTRALIA | ANTARCTICA
    basin: null                   # для OCEAN; для LAND — null
                                  # PACIFIC | ATLANTIC | INDIAN | ARCTIC
    board: LEFT                   # LEFT | RIGHT | BOTH (BOTH — область пересекает шов)
    side: 5P                      # 3P | 5P | BOTH
    parent: MR-L3-NAM             # какую область стороны 3P дробит; null у 3P и BOTH
    printed_in_two_pieces: false  # напечатана двумя кусками у левого и правого краёв листа
    sources: [SRC-RB-NEW, SRC-BGA-GRAPH, SRC-OW-MAP-PSD]
```

Стартовых глифов здесь нет намеренно: один глиф живёт сразу в двух областях
(своей на стороне «5» и родительской на стороне «3»), поэтому он описан
записью в `glyphs.yaml`, а не полем области. `board/tools/map.py` сшивает их сам.

Префиксы `SCOPE`: `OC` — океан (всегда `board: BOTH` или `LEFT`, `side: BOTH`),
`SH` — суша, общая для обеих сторон (Антарктида), `L3`/`R3` — суша стороны 3P
левого/правого планшета, `L5`/`R5` — то же для стороны 5P.

## edges.yaml — смежности

```yaml
edges:
  - id: ME-001                  # ME-###
    a: MR-L3-NAM                # ссылка на regions.yaml
    b: MR-OC-NATL
    kind: LAND-OCEAN            # LAND-LAND | LAND-OCEAN | OCEAN-OCEAN
    observed_on: [3P]           # на какой стороне поля смежность наблюдалась: 3P и/или 5P
    contact_px: {3P: 11699}     # длина общей границы в эталоне 2400×1203 — доказательство
    note: >                     # необязательное: почему это ребро легко нарисовать неверно
```

Рёбра ненаправленные, `a` < `b` по ID. Дубликатов и петель нет.
`observed_on` — свидетельство, а не правило: принадлежность ребра конфигурации
вычисляется из присутствия обеих областей.

`note` заполнено только там, где смежность неочевидна или где её легко
«починить» по интуиции и тем сломать: девять рёбер двух перекрёстков —
панамского и магелланова (см. `MF-010`).

## configs.yaml — конфигурации и опубликованные инварианты

Блок `meta` описывает планшеты, шов и склейку по меридиану.
Блок `configs[].published` — **опубликованные значения из источников**, каждое
со ссылкой `ref` и местом `loc`. Это не результат нашего разбора, а эталон,
против которого `board/tools/map.py verify` проверяет собранный граф:

```yaml
published:
  areas:        {value: 13, ref: SRC-RB-NEW, loc: "с. 7"}
  ocean_areas:  {value: 6,  ref: SRC-BGA-GRAPH, loc: "..."}
  diameter:     {value: 3,  ref: SRC-BGA-GRAPH, loc: "..."}
  degrees:      {ref: ..., loc: ..., values: {MR-L3-AUS: 2, ...}}
  longest_pairs:{ref: ..., loc: ..., values: [[MR-..., MR-...], ...]}
  degree_count_2 / degree_count_4: {value: N, ref: ..., loc: ...}
  edges_minus_other: {value: 1, other: MC-4P-B, ref: ..., loc: ...}
```

Любой ключ необязателен: проверяется то, что опубликовано.

## redesign.yaml — области нашей карты и соответствие

```yaml
regions:
  - id: OW-L5-NAMW              # OW-<тот же SHORT>
    name_ru: Запад Северной Америки   # подпись на нашей карте
    psd_layer: Сев. Америка - запад   # имя слоя в board/legacy/карта 5.psd
    baseline_ref: MR-L5-NAMW
    match: EXACT                # EXACT | RENAMED | DEVIATION | MISSING | UNVERIFIED
```

## glyphs.yaml — что напечатано на поле

Пять разделов. Стартовые области фракций оригинала первично живут в
`rules/registry/factions.yaml` (там текст и обоснование); здесь они привязаны к ID областей
и разложены по сторонам планшета.

В файле два разных знака, и путать их нельзя: `faction_glyphs` — стартовая
область фракции (семь штук, на нашем поле их нет, `MF-009`); `region_symbols` —
символ региона (три штуки, на нашем поле есть, `D-043`, `D-046`).

```yaml
faction_glyphs:
  - id: MG-001                    # MG-###
    faction_original: CW-F-01     # ссылка в ../factions.yaml → original
    faction_original_name: Great Cthulhu
    faction_redesign: OW-F-01     # ссылка в ../factions.yaml → redesign; null, если пары нет
    faction_redesign_name: Островная Империя
    regions_3p: [MR-OC-SPAC]      # где стоит глиф на стороне «3»; список — у Windwalker две области
    regions_5p: [MR-OC-SPAC]      # то же на стороне «5»
    landmark: ML-001              # подпись-ориентир рядом; null — нет или не прочитана
    glyph_colour_observed: синий  # что видно своими глазами; null — не смотрели
    glyph_shape_observed: >        # то же про форму
    confidence: HIGH              # HIGH | MEDIUM | LOW
    note: >
    sources: [SRC-WIKI-MAP]

no_glyph:                         # фракции без глифа на поле, с правилом расстановки
  - {faction_original: CW-F-05, faction_original_name: ..., faction_redesign: ...,
     faction_redesign_name: ..., rule: >}

region_symbols:                   # три символа региона, ровно три записи
  - id: MS-001                    # MS-###
    original_name: Dragon Glyph   # как называет его вики/рулбук оригинала
    original_shape: >             # что видно на растре своими глазами
    redesign_symbol: капля        # наш знак
    redesign_glyph: "Q"           # глиф в шрифте Oil Wars
    icon_ref: ICON-032            # ссылка в ../icons.yaml
    resource_reading: нефть       # тематическое чтение (D-046); игровой силы не несёт
    landmasses: [NORTH_AMERICA, SOUTH_AMERICA]   # материки, которые несут символ
    regions_3p: [MR-L3-NAM, ...]  # ВСЕ области стороны «3» с этим символом
    regions_5p: [MR-L5-NAMW, ...] # то же для стороны «5»
    confidence: HIGH
    note: >
    sources: [SRC-CW-MAP-SCAN, SRC-WIKI-YS]

start_areas_redesign:             # стартовые области наших восьми фракций
  - faction: OW-F-03
    name: Глобал Петролеум
    queue: 3.0                    # очередь расстановки; float, см. registry/SCHEMA.md
    start_region_text: Европа     # дословно с планшета фракции
    regions_3p: [MR-R3-EUR]       # null, если правило «любой свободный»
    regions_5p: [MR-R5-EUR]
    glyph: MG-002                 # null, если глифа на поле нет
    baseline_ref: CW-F-02
    mapping_ref: MAP-03           # пара из ../factions.yaml → mapping

landmarks:                        # топонимы мифоса в круглых скобках
  - id: ML-001                    # ML-###
    label: "R'LYEH"
    regions_3p: [MR-OC-SPAC]
    regions_5p: [MR-OC-SPAC]      # null, если не проверено
    observed_on: [3P, 5P]         # на каких сторонах подпись прочитана своими глазами
    glyph_nearby: MG-001          # null — рядом глифа нет
    confidence: HIGH
    note: >                       # необязательное
```

Глиф на стороне «3» стоит в родительской области того же места, где он стоит
на стороне «5». Проверяется это по `landmark`: подпись-ориентир на обеих
сторонах одна и та же, и глиф печатается вплотную к ней.

`region_symbols` проверяется жёстче остальных разделов, потому что от него
зависят семь задач двух фракций. `map.py check` требует: ровно три записи;
уникальные `id`, `redesign_glyph` и `icon_ref`; каждая область из
`regions_3p` / `regions_5p` существует и лежит на своей стороне; **ни одна
область не несёт двух символов**; **каждая область суши, кроме Антарктиды,
несёт ровно один**; **океаны и Антарктида — ни одного**; дети области стороны «5»
несут тот же символ, что их `parent`. Сборка кладёт символ в поле `symbol`
каждой вершины и сводку `region_symbols` по каждой конфигурации.

**`MG-###`, `ML-###`, `MS-###` — новые ID-пространства этого файла.** Префикс `MAP-##`
здесь **не используется**: он занят таблицей соответствий фракций в
`rules/registry/factions.yaml` (`mapping`). Находки карты поэтому носят префикс `MF-###`.

## findings.yaml — находки по карте

```yaml
findings:
  - id: MF-001                 # MF-###
    type: VERIFICATION          # VERIFICATION | DEVIATION | AMBIGUITY | SOURCE-GAP |
                                # TERMINOLOGY | OUT-OF-SCOPE | DECISION
    severity: INFO              # CRITICAL | ERROR | WARNING | INFO
    status: CLOSED              # OPEN | AUTHOR-DECISION-REQUIRED | DEFERRED | DECIDED | CLOSED
    title: ...
    subject: ...                # MR-* / MC-* / OW-* / список / null
    detail: >
    proposal: >
    decision: null
    decided: null
    refs: []                    # ссылки в другие реестры: PLAY-001, D-041, FAC-###
    opened: 2026-09-16
    closed: 2026-09-16
```

Поле `closed` заполняется тогда и только тогда, когда `status: CLOSED`
(то же правило, что в `rules/registry/SCHEMA.md`).

---

## Что собирает tools/map.py

- `check` — валидация YAML: уникальность ID, словари значений, целостность
  ссылок, согласованность `parent`/`side`/`board`, отсутствие петель и дублей,
  покрытие родителя детьми, а в `glyphs.yaml` — что `regions_3p` ссылается
  только на области стороны «3», а `regions_5p` — только на области стороны «5».
- `build` — `derived/<config>.json` (вершины, рёбра, степени, расстояния),
  `derived/<config>.dot` (Graphviz), `derived/all.json`, `derived/<config>.md`
  (матрица смежности).
- `verify` — сверка собранных графов с `published` из `configs.yaml`,
  таблица PASS/FAIL.
- `report` — `board/reports/11-map.md`.
- `all` — check + build + verify + report.

Зависимость только `PyYAML`, как и у `registry.py`.
