# 11 — Карта: реконструкция оригинального поля

Сгенерировано `board/tools/map.py`. Не править руками — источник в `board/`.

## Сводка по конфигурациям

| Конфигурация | Игроков | Левый | Правый | Областей | Суша | Океан | Рёбер | Диаметр | Связный |
|---|---|---|---|---|---|---|---|---|---|
| `MC-3P` | 3 | 3P | 3P | 13 | 7 | 6 | 33 | 3 | да |
| `MC-4P-A` | 4 | 3P | 5P | 17 | 11 | 6 | 45 | 4 | да |
| `MC-4P-B` | 4 | 5P | 3P | 17 | 11 | 6 | 44 | 4 | да |
| `MC-5P` | 5 | 5P | 5P | 21 | 15 | 6 | 56 | 4 | да |

## Сверка с опубликованными величинами оригинала

| Конфигурация | Проверка | Опубликовано | Собрано | Итог | Источник |
|---|---|---|---|---|---|
| `MC-3P` | areas | 13 | 13 | **PASS** | `SRC-RB-NEW` |
| `MC-3P` | ocean_areas | 6 | 6 | **PASS** | `SRC-BGA-GRAPH` |
| `MC-3P` | diameter | 3 | 3 | **PASS** | `SRC-BGA-GRAPH` |
| `MC-3P` | degrees (пофамильно) | {"MR-L3-AUS": 2, "MR-R3-EUR": 3, "MR-SH-ANT": 3, "MR-L3-NAM": 4, "M… | {"MR-L3-AUS": 2, "MR-R3-EUR": 3, "MR-SH-ANT": 3, "MR-L3-NAM": 4, "M… | **PASS** | `SRC-BGA-GRAPH` |
| `MC-3P` | longest_pairs | [["MR-L3-AUS", "MR-L3-NAM"], ["MR-L3-AUS", "MR-OC-ARC"], ["MR-L3-AU… | [["MR-L3-AUS", "MR-L3-NAM"], ["MR-L3-AUS", "MR-OC-ARC"], ["MR-L3-AU… | **PASS** | `SRC-BGA-GRAPH` |
| `MC-4P-A` | areas | 17 | 17 | **PASS** | `SRC-RB-NEW` |
| `MC-4P-A` | ocean_areas | 6 | 6 | **PASS** | `SRC-BGA-GRAPH` |
| `MC-4P-A` | diameter | 4 | 4 | **PASS** | `SRC-BGA-GRAPH` |
| `MC-4P-A` | longest_pairs | [["MR-L3-AUS", "MR-R5-SCA"]] | [["MR-L3-AUS", "MR-R5-SCA"]] | **PASS** | `SRC-BGA-GRAPH` |
| `MC-4P-A` | degree_count_4 | 6 | 6 | **PASS** | `SRC-BGA-GRAPH` |
| `MC-4P-A` | edges − edges(MC-4P-B) | 1 | 1 | **PASS** | `SRC-BGA-GRAPH` |
| `MC-4P-B` | areas | 17 | 17 | **PASS** | `SRC-RB-NEW` |
| `MC-4P-B` | ocean_areas | 6 | 6 | **PASS** | `SRC-BGA-GRAPH` |
| `MC-4P-B` | diameter | 4 | 4 | **PASS** | `SRC-BGA-GRAPH` |
| `MC-4P-B` | longest_pairs | [["MR-L5-AUS", "MR-L5-NAME"], ["MR-L5-NAME", "MR-L5-NZL"]] | [["MR-L5-AUS", "MR-L5-NAME"], ["MR-L5-NAME", "MR-L5-NZL"]] | **PASS** | `SRC-BGA-GRAPH` |
| `MC-5P` | areas | 21 | 21 | **PASS** | `SRC-RB-NEW` |
| `MC-5P` | ocean_areas | 6 | 6 | **PASS** | `SRC-BGA-GRAPH` |
| `MC-5P` | diameter | 4 | 4 | **PASS** | `SRC-BGA-GRAPH` |
| `MC-5P` | longest_pairs | [["MR-L5-AUS", "MR-L5-NAME"], ["MR-L5-AUS", "MR-R5-SCA"], ["MR-L5-N… | [["MR-L5-AUS", "MR-L5-NAME"], ["MR-L5-AUS", "MR-R5-SCA"], ["MR-L5-N… | **PASS** | `SRC-BGA-GRAPH` |
| `MC-5P` | degree_count_2 | 1 | 1 | **PASS** | `SRC-BGA-GRAPH` |
| `MC-5P` | degree_count_4 | 6 | 6 | **PASS** | `SRC-BGA-GRAPH` |

**Итог сверки: все проверки пройдены.**

## Области

| ID | Оригинал | Наше название | Тип | Материк / бассейн | Планшет | Сторона | Дробит |
|---|---|---|---|---|---|---|---|
| `MR-OC-ARC` | Arctic Ocean | Северный Ледовитый океан | OCEAN | ARCTIC | BOTH | BOTH | — |
| `MR-OC-NPAC` | North Pacific | Север Тихого океана | OCEAN | PACIFIC | BOTH | BOTH | — |
| `MR-OC-SPAC` | South Pacific | Юг Тихого океана | OCEAN | PACIFIC | LEFT | BOTH | — |
| `MR-OC-NATL` | North Atlantic | Север Атлантического океана | OCEAN | ATLANTIC | BOTH | BOTH | — |
| `MR-OC-SATL` | South Atlantic | Юг Атлантического океана | OCEAN | ATLANTIC | BOTH | BOTH | — |
| `MR-OC-IND` | Indian Ocean | Индийский океан | OCEAN | INDIAN | BOTH | BOTH | — |
| `MR-SH-ANT` | Antarctica | Антарктида | LAND | ANTARCTICA | BOTH | BOTH | — |
| `MR-L3-NAM` | North America | Северная Америка | LAND | NORTH_AMERICA | LEFT | 3P | — |
| `MR-L3-SAM` | South America | Южная Америка | LAND | SOUTH_AMERICA | LEFT | 3P | — |
| `MR-L3-AUS` | Australia | Австралия | LAND | AUSTRALIA | LEFT | 3P | — |
| `MR-R3-EUR` | Europe | Европа | LAND | EUROPE | RIGHT | 3P | — |
| `MR-R3-ASI` | Asia | Азия | LAND | ASIA | RIGHT | 3P | — |
| `MR-R3-AFR` | Africa | Африка | LAND | AFRICA | RIGHT | 3P | — |
| `MR-L5-NAMW` | North America West | Запад Северной Америки | LAND | NORTH_AMERICA | LEFT | 5P | `MR-L3-NAM` |
| `MR-L5-NAME` | North America East | Восток Северной Америки | LAND | NORTH_AMERICA | LEFT | 5P | `MR-L3-NAM` |
| `MR-L5-CAM` | Central America | Центральная Америка | LAND | NORTH_AMERICA | LEFT | 5P | `MR-L3-NAM` |
| `MR-L5-SAMW` | South America West | Запад Южной Америки | LAND | SOUTH_AMERICA | LEFT | 5P | `MR-L3-SAM` |
| `MR-L5-SAME` | South America East | Восток Южной Америки | LAND | SOUTH_AMERICA | LEFT | 5P | `MR-L3-SAM` |
| `MR-L5-AUS` | Australia | Австралия | LAND | AUSTRALIA | LEFT | 5P | `MR-L3-AUS` |
| `MR-L5-NZL` | New Zealand | Новая Зеландия | LAND | AUSTRALIA | LEFT | 5P | `MR-L3-AUS` |
| `MR-R5-SCA` | Scandinavia | Скандинавия | LAND | EUROPE | RIGHT | 5P | `MR-R3-EUR` |
| `MR-R5-EUR` | Europe | Европа | LAND | EUROPE | RIGHT | 5P | `MR-R3-EUR` |
| `MR-R5-ASIN` | North Asia | Северная Азия | LAND | ASIA | RIGHT | 5P | `MR-R3-ASI` |
| `MR-R5-ASIS` | South Asia | Южная Азия | LAND | ASIA | RIGHT | 5P | `MR-R3-ASI` |
| `MR-R5-ARB` | Arabia | Аравийский полуостров | LAND | ASIA | RIGHT | 5P | `MR-R3-ASI` |
| `MR-R5-AFRW` | West Africa | Западная Африка | LAND | AFRICA | RIGHT | 5P | `MR-R3-AFR` |
| `MR-R5-AFRE` | East Africa | Восточная Африка | LAND | AFRICA | RIGHT | 5P | `MR-R3-AFR` |

## Неочевидные смежности

Рёбра, у которых в `edges.yaml` заполнено поле `note`: места, где
смежность легко нарисовать неверно.

**`ME-004` Central America — South America East** (5P): Центральная Америка своей карибской полосой достаёт и до Востока Южной Америки — короткий контакт 507 px.

**`ME-005` Central America — South America West** (5P): Граница поперёк перешейка у панамского перекрёстка. Именно она решает, кому достаётся карибский берег: он уходит Центральной Америке (ME-027).

**`ME-027` Central America — North Atlantic** (5P): Центральная Америка на стороне «5» — не только перешеек: полосой она тянется на восток по карибскому берегу и полностью отделяет Запад Южной Америки от Северной Атлантики. Поэтому ребра Запад Южной Америки — Северная Атлантика НЕТ ни на нашей карте, ни на оригинале.

**`ME-044` North Atlantic — South America** (3P): На стороне «3» Южная Америка выходит в Северную Атлантику напрямую: карибского берега ни с кем делить не надо. На стороне «5» это ребро исчезает — берег забирает Центральная Америка (ME-027), а Северную Атлантику из Южной Америки видит только её восточная половина (ME-045).

**`ME-047` North Pacific — South America** (3P): Короткий контакт (458 px) на тихоокеанском берегу Колумбии, там же, где к берегу выходит граница Севера и Юга Тихого океана. Это ребро обязательно: без него у Южной Америки было бы 4 соседа, а опубликованная степень — 5 (SRC-BGA-GRAPH).

**`ME-048` North Pacific — South America West** (5P): То же место, что ME-047, но на стороне «5»: контакт наследует Запад Южной Америки. 458 px — самый короткий контакт суши с океаном на всей карте.

**`ME-074` North Atlantic — North Pacific** (3P, 5P): Два океана сходятся напрямую в разрыве Панамского перешейка: суша там нарисована цепочкой островков, вода проходит между ними. Рулбук это специально отмечает — «Note that the North Atlantic is directly adjacent to the North Pacific!» (SRC-RB-NEW, с. 9). Смежность есть на обеих сторонах поля. Контакт замерен на x 0.207–0.253, y 0.539–0.627 листа.

**`ME-077` South Atlantic — South Pacific** (3P, 5P): Два океана сходятся южнее Огненной Земли — перекрёсток у Магелланова пролива. Смежность есть на обеих сторонах поля.


## Стартовые глифы, напечатанные на поле

| Глиф | Фракция оригинала | Наша фракция | Сторона «3» | Сторона «5» | Ориентир рядом | Доверие |
|---|---|---|---|---|---|---|
| `MG-001` | Great Cthulhu | Островная Империя | South Pacific | South Pacific | R'LYEH | HIGH |
| `MG-002` | Yellow Sign | Глобал Петролеум | Europe | Europe | DREIEICH | HIGH |
| `MG-003` | Crawling Chaos | Эйркрафт Корпорейшн | Asia | South Asia | LENG | HIGH |
| `MG-004` | Black Goat | Клонэйд Ресёрч | Africa | West Africa | G'HARNE | HIGH |
| `MG-005` | Sleeper | Североамериканский Альянс | North America | North America West | — | MEDIUM |
| `MG-006` | Windwalker | Криогеник Технолоджис (пара только предполагается, MAP-09) | Arctic Ocean | Arctic Ocean | LOMAR | MEDIUM |
| `MG-007` | Windwalker | Криогеник Технолоджис (пара только предполагается, MAP-09) | Antarctica | Antarctica | — | MEDIUM |

Фракции оригинала без глифа на поле:

- **The Ancients** (Братство Сингулярности) — Любой регион без чужого глифа и без игрового символа; расставляются раньше Tcho-Tcho, Windwalker и Opener.
- **Bubastis** (Moon Systems) — Не на Земле: 6 Earth Cats кладутся на тайл Луны.
- **Daemon Sultan** (пары нет) — На карте ничего; стартовой считается область, куда способностью Psychosis поставлен первый Acolyte. Фракция вне объёма (scope: IGNORED).
- **Opener of the Way** (Сайнтифик Солюшн) — Область выбирается игроком; расставляется последним.
- **Tcho-Tcho** (пары нет) — Любая незанятая область С ГЛИФОМ фракции — то есть Tcho-Tcho занимает чужую стартовую область, если её хозяин не в игре. Отсюда следует, что набор глифов на поле имеет игровой смысл и в отсутствие их владельцев. Фракция вне объёма (scope: IGNORED).
- **The Invasion** (пары нет) — Любая незанятая область, дальше по инструкции на карте Lord's Shadow. Фракция вне объёма (scope: IGNORED).

## Символы регионов

Три знака, напечатанные на поле помимо стартовых глифов. В оригинале —
три Spellbook Glyph фракции Yellow Sign; у нас — капля, пламя, вагонетка.
Размещение повторяет оригинал один в один (`D-046`), источник — растр
обеих сторон оригинального поля (`SRC-CW-MAP-SCAN`).

| ID | Оригинал | Наш знак | Глиф | Иконка | Чтение | Материки | Доверие |
|---|---|---|---|---|---|---|---|
| `MS-001` | Dragon Glyph | капля | `Q` | `ICON-032` | нефть | NORTH_AMERICA, SOUTH_AMERICA | HIGH |
| `MS-002` | Thorns Glyph | пламя | `W` | `ICON-033` | природный газ | EUROPE, ASIA | HIGH |
| `MS-003` | Chevron Glyph | рудничная вагонетка | `E` | `ICON-034` | уголь и руды | AFRICA, AUSTRALIA | HIGH |

| ID | Сторона «3» | Сторона «5» |
|---|---|---|
| `MS-001` | North America, South America | North America West, North America East, Central America, South America West, South America East |
| `MS-002` | Europe, Asia | Scandinavia, Europe, North Asia, South Asia, Arabia |
| `MS-003` | Africa, Australia | West Africa, East Africa, Australia, New Zealand |

Закон размещения: **символ идёт по материку**. Каждая область суши,
кроме Антарктиды, несёт ровно один символ; шесть океанов и Антарктида —
ни одного. Дети области стороны «5» наследуют символ родителя.

| Конфигурация | капля `Q` | пламя `W` | рудничная вагонетка `E` | Без символа |
|---|---|---|---|---|
| `MC-3P` | 2 | 2 | 2 | 7 |
| `MC-4P-A` | 2 | 5 | 3 | 7 |
| `MC-4P-B` | 5 | 2 | 3 | 7 |
| `MC-5P` | 5 | 5 | 4 | 7 |

### MC-3P — символ в каждой области

| Область | Символ |
|---|---|
| Australia | рудничная вагонетка `E` (Chevron Glyph) |
| North America | капля `Q` (Dragon Glyph) |
| South America | капля `Q` (Dragon Glyph) |
| Arctic Ocean | — *(без символа)* |
| Indian Ocean | — *(без символа)* |
| North Atlantic | — *(без символа)* |
| North Pacific | — *(без символа)* |
| South Atlantic | — *(без символа)* |
| South Pacific | — *(без символа)* |
| Africa | рудничная вагонетка `E` (Chevron Glyph) |
| Asia | пламя `W` (Thorns Glyph) |
| Europe | пламя `W` (Thorns Glyph) |
| Antarctica | — *(без символа)* |

### MC-4P-A — символ в каждой области

| Область | Символ |
|---|---|
| Australia | рудничная вагонетка `E` (Chevron Glyph) |
| North America | капля `Q` (Dragon Glyph) |
| South America | капля `Q` (Dragon Glyph) |
| Arctic Ocean | — *(без символа)* |
| Indian Ocean | — *(без символа)* |
| North Atlantic | — *(без символа)* |
| North Pacific | — *(без символа)* |
| South Atlantic | — *(без символа)* |
| South Pacific | — *(без символа)* |
| East Africa | рудничная вагонетка `E` (Chevron Glyph) |
| West Africa | рудничная вагонетка `E` (Chevron Glyph) |
| Arabia | пламя `W` (Thorns Glyph) |
| North Asia | пламя `W` (Thorns Glyph) |
| South Asia | пламя `W` (Thorns Glyph) |
| Europe | пламя `W` (Thorns Glyph) |
| Scandinavia | пламя `W` (Thorns Glyph) |
| Antarctica | — *(без символа)* |

### MC-4P-B — символ в каждой области

| Область | Символ |
|---|---|
| Australia | рудничная вагонетка `E` (Chevron Glyph) |
| Central America | капля `Q` (Dragon Glyph) |
| North America East | капля `Q` (Dragon Glyph) |
| North America West | капля `Q` (Dragon Glyph) |
| New Zealand | рудничная вагонетка `E` (Chevron Glyph) |
| South America East | капля `Q` (Dragon Glyph) |
| South America West | капля `Q` (Dragon Glyph) |
| Arctic Ocean | — *(без символа)* |
| Indian Ocean | — *(без символа)* |
| North Atlantic | — *(без символа)* |
| North Pacific | — *(без символа)* |
| South Atlantic | — *(без символа)* |
| South Pacific | — *(без символа)* |
| Africa | рудничная вагонетка `E` (Chevron Glyph) |
| Asia | пламя `W` (Thorns Glyph) |
| Europe | пламя `W` (Thorns Glyph) |
| Antarctica | — *(без символа)* |

### MC-5P — символ в каждой области

| Область | Символ |
|---|---|
| Australia | рудничная вагонетка `E` (Chevron Glyph) |
| Central America | капля `Q` (Dragon Glyph) |
| North America East | капля `Q` (Dragon Glyph) |
| North America West | капля `Q` (Dragon Glyph) |
| New Zealand | рудничная вагонетка `E` (Chevron Glyph) |
| South America East | капля `Q` (Dragon Glyph) |
| South America West | капля `Q` (Dragon Glyph) |
| Arctic Ocean | — *(без символа)* |
| Indian Ocean | — *(без символа)* |
| North Atlantic | — *(без символа)* |
| North Pacific | — *(без символа)* |
| South Atlantic | — *(без символа)* |
| South Pacific | — *(без символа)* |
| East Africa | рудничная вагонетка `E` (Chevron Glyph) |
| West Africa | рудничная вагонетка `E` (Chevron Glyph) |
| Arabia | пламя `W` (Thorns Glyph) |
| North Asia | пламя `W` (Thorns Glyph) |
| South Asia | пламя `W` (Thorns Glyph) |
| Europe | пламя `W` (Thorns Glyph) |
| Scandinavia | пламя `W` (Thorns Glyph) |
| Antarctica | — *(без символа)* |

## Стартовые области наших восьми фракций

| Очередь | Фракция | По планшету | Сторона «3» | Сторона «5» | Глиф | Оригинал |
|---|---|---|---|---|---|---|
| 1 | Островная Империя | Юг Тихого океана | South Pacific | South Pacific | `MG-001` | `CW-F-01` |
| 2 | Эйркрафт Корпорейшн | Южная Азия | Asia | South Asia | `MG-003` | `CW-F-03` |
| 3 | Глобал Петролеум | Европа | Europe | Europe | `MG-002` | `CW-F-02` |
| 6 | Moon Systems | любой, кроме стартовых регионов других фракций | — | — | — | `CW-F-06` |
| 7 | Клонэйд Ресёрч | Западная Африка | Africa | West Africa | `MG-004` | `CW-F-04` |
| 8 | Североамериканский Альянс | запад Северной Америки | North America | North America West | `MG-005` | `CW-F-09` |
| 9 | Братство Сингулярности | любой, кроме стартовых регионов других фракций | — | — | — | `CW-F-05` |
| 12 | Сайнтифик Солюшн | любой свободный | — | — | — | `CW-F-08` |

## Подписи-ориентиры на поле

| ID | Подпись | Сторона «3» | Сторона «5» | Прочитано на | Глиф рядом | Доверие |
|---|---|---|---|---|---|---|
| `ML-001` | R'LYEH | South Pacific | South Pacific | 3P, 5P | `MG-001` | HIGH |
| `ML-002` | LENG | Asia | — | 3P | — | MEDIUM |
| `ML-003` | G'HARNE | Africa | West Africa | 3P, 5P | `MG-004` | HIGH |
| `ML-004` | DREIEICH | Europe | Europe | 3P, 5P | `MG-002` | MEDIUM |
| `ML-005` | LOMAR | Arctic Ocean | Arctic Ocean | — | `MG-006` | MEDIUM |

### MC-3P — где стоят глифы в этой раскладке

- **North America** — Sleeper / Североамериканский Альянс
- **Arctic Ocean** — Windwalker / Криогеник Технолоджис (пара только предполагается, MAP-09)
- **South Pacific** — Great Cthulhu / Островная Империя
- **Africa** — Black Goat / Клонэйд Ресёрч
- **Asia** — Crawling Chaos / Эйркрафт Корпорейшн
- **Europe** — Yellow Sign / Глобал Петролеум
- **Antarctica** — Windwalker / Криогеник Технолоджис (пара только предполагается, MAP-09)

### MC-4P-A — где стоят глифы в этой раскладке

- **North America** — Sleeper / Североамериканский Альянс
- **Arctic Ocean** — Windwalker / Криогеник Технолоджис (пара только предполагается, MAP-09)
- **South Pacific** — Great Cthulhu / Островная Империя
- **West Africa** — Black Goat / Клонэйд Ресёрч
- **South Asia** — Crawling Chaos / Эйркрафт Корпорейшн
- **Europe** — Yellow Sign / Глобал Петролеум
- **Antarctica** — Windwalker / Криогеник Технолоджис (пара только предполагается, MAP-09)

### MC-4P-B — где стоят глифы в этой раскладке

- **North America West** — Sleeper / Североамериканский Альянс
- **Arctic Ocean** — Windwalker / Криогеник Технолоджис (пара только предполагается, MAP-09)
- **South Pacific** — Great Cthulhu / Островная Империя
- **Africa** — Black Goat / Клонэйд Ресёрч
- **Asia** — Crawling Chaos / Эйркрафт Корпорейшн
- **Europe** — Yellow Sign / Глобал Петролеум
- **Antarctica** — Windwalker / Криогеник Технолоджис (пара только предполагается, MAP-09)

### MC-5P — где стоят глифы в этой раскладке

- **North America West** — Sleeper / Североамериканский Альянс
- **Arctic Ocean** — Windwalker / Криогеник Технолоджис (пара только предполагается, MAP-09)
- **South Pacific** — Great Cthulhu / Островная Империя
- **West Africa** — Black Goat / Клонэйд Ресёрч
- **South Asia** — Crawling Chaos / Эйркрафт Корпорейшн
- **Europe** — Yellow Sign / Глобал Петролеум
- **Antarctica** — Windwalker / Криогеник Технолоджис (пара только предполагается, MAP-09)

## MC-3P — степени вершин

| Область | Тип | Степень | Соседи |
|---|---|---|---|
| North Atlantic | OCEAN | 8 | North America, South America, Arctic Ocean, North Pacific, South Atlantic, Africa, Asia, Europe |
| Indian Ocean | OCEAN | 7 | Australia, North Pacific, South Atlantic, South Pacific, Africa, Asia, Antarctica |
| North Pacific | OCEAN | 7 | North America, South America, Arctic Ocean, Indian Ocean, North Atlantic, South Pacific, Asia |
| South Atlantic | OCEAN | 6 | South America, Indian Ocean, North Atlantic, South Pacific, Africa, Antarctica |
| South Pacific | OCEAN | 6 | Australia, South America, Indian Ocean, North Pacific, South Atlantic, Antarctica |
| Asia | LAND | 6 | Arctic Ocean, Indian Ocean, North Atlantic, North Pacific, Africa, Europe |
| South America | LAND | 5 | North America, North Atlantic, North Pacific, South Atlantic, South Pacific |
| Arctic Ocean | OCEAN | 5 | North America, North Atlantic, North Pacific, Asia, Europe |
| North America | LAND | 4 | South America, Arctic Ocean, North Atlantic, North Pacific |
| Africa | LAND | 4 | Indian Ocean, North Atlantic, South Atlantic, Asia |
| Europe | LAND | 3 | Arctic Ocean, North Atlantic, Asia |
| Antarctica | LAND | 3 | Indian Ocean, South Atlantic, South Pacific |
| Australia | LAND | 2 | Indian Ocean, South Pacific |

## MC-4P-A — степени вершин

| Область | Тип | Степень | Соседи |
|---|---|---|---|
| North Atlantic | OCEAN | 9 | North America, South America, Arctic Ocean, North Pacific, South Atlantic, West Africa, Arabia, Europe, Scandinavia |
| Indian Ocean | OCEAN | 8 | Australia, North Pacific, South Atlantic, South Pacific, East Africa, Arabia, South Asia, Antarctica |
| North Pacific | OCEAN | 8 | North America, South America, Arctic Ocean, Indian Ocean, North Atlantic, South Pacific, North Asia, South Asia |
| South Atlantic | OCEAN | 7 | South America, Indian Ocean, North Atlantic, South Pacific, East Africa, West Africa, Antarctica |
| Arabia | LAND | 7 | Indian Ocean, North Atlantic, East Africa, West Africa, North Asia, South Asia, Europe |
| South Pacific | OCEAN | 6 | Australia, South America, Indian Ocean, North Pacific, South Atlantic, Antarctica |
| North Asia | LAND | 6 | Arctic Ocean, North Pacific, Arabia, South Asia, Europe, Scandinavia |
| South America | LAND | 5 | North America, North Atlantic, North Pacific, South Atlantic, South Pacific |
| Arctic Ocean | OCEAN | 5 | North America, North Atlantic, North Pacific, North Asia, Scandinavia |
| North America | LAND | 4 | South America, Arctic Ocean, North Atlantic, North Pacific |
| East Africa | LAND | 4 | Indian Ocean, South Atlantic, West Africa, Arabia |
| West Africa | LAND | 4 | North Atlantic, South Atlantic, East Africa, Arabia |
| South Asia | LAND | 4 | Indian Ocean, North Pacific, Arabia, North Asia |
| Europe | LAND | 4 | North Atlantic, Arabia, North Asia, Scandinavia |
| Scandinavia | LAND | 4 | Arctic Ocean, North Atlantic, North Asia, Europe |
| Antarctica | LAND | 3 | Indian Ocean, South Atlantic, South Pacific |
| Australia | LAND | 2 | Indian Ocean, South Pacific |

## MC-4P-B — степени вершин

| Область | Тип | Степень | Соседи |
|---|---|---|---|
| North Atlantic | OCEAN | 10 | Central America, North America East, North America West, South America East, Arctic Ocean, North Pacific, South Atlantic, Africa, Asia, Europe |
| Indian Ocean | OCEAN | 8 | Australia, New Zealand, North Pacific, South Atlantic, South Pacific, Africa, Asia, Antarctica |
| North Pacific | OCEAN | 8 | Central America, North America West, South America West, Arctic Ocean, Indian Ocean, North Atlantic, South Pacific, Asia |
| South Atlantic | OCEAN | 7 | South America East, South America West, Indian Ocean, North Atlantic, South Pacific, Africa, Antarctica |
| Arctic Ocean | OCEAN | 6 | North America East, North America West, North Atlantic, North Pacific, Asia, Europe |
| South Pacific | OCEAN | 6 | New Zealand, South America West, Indian Ocean, North Pacific, South Atlantic, Antarctica |
| Asia | LAND | 6 | Arctic Ocean, Indian Ocean, North Atlantic, North Pacific, Africa, Europe |
| Central America | LAND | 5 | North America West, South America East, South America West, North Atlantic, North Pacific |
| North America West | LAND | 5 | Central America, North America East, Arctic Ocean, North Atlantic, North Pacific |
| South America West | LAND | 5 | Central America, South America East, North Pacific, South Atlantic, South Pacific |
| South America East | LAND | 4 | Central America, South America West, North Atlantic, South Atlantic |
| Africa | LAND | 4 | Indian Ocean, North Atlantic, South Atlantic, Asia |
| North America East | LAND | 3 | North America West, Arctic Ocean, North Atlantic |
| New Zealand | LAND | 3 | Australia, Indian Ocean, South Pacific |
| Europe | LAND | 3 | Arctic Ocean, North Atlantic, Asia |
| Antarctica | LAND | 3 | Indian Ocean, South Atlantic, South Pacific |
| Australia | LAND | 2 | New Zealand, Indian Ocean |

## MC-5P — степени вершин

| Область | Тип | Степень | Соседи |
|---|---|---|---|
| North Atlantic | OCEAN | 11 | Central America, North America East, North America West, South America East, Arctic Ocean, North Pacific, South Atlantic, West Africa, Arabia, Europe, Scandinavia |
| Indian Ocean | OCEAN | 9 | Australia, New Zealand, North Pacific, South Atlantic, South Pacific, East Africa, Arabia, South Asia, Antarctica |
| North Pacific | OCEAN | 9 | Central America, North America West, South America West, Arctic Ocean, Indian Ocean, North Atlantic, South Pacific, North Asia, South Asia |
| South Atlantic | OCEAN | 8 | South America East, South America West, Indian Ocean, North Atlantic, South Pacific, East Africa, West Africa, Antarctica |
| Arabia | LAND | 7 | Indian Ocean, North Atlantic, East Africa, West Africa, North Asia, South Asia, Europe |
| Arctic Ocean | OCEAN | 6 | North America East, North America West, North Atlantic, North Pacific, North Asia, Scandinavia |
| South Pacific | OCEAN | 6 | New Zealand, South America West, Indian Ocean, North Pacific, South Atlantic, Antarctica |
| North Asia | LAND | 6 | Arctic Ocean, North Pacific, Arabia, South Asia, Europe, Scandinavia |
| Central America | LAND | 5 | North America West, South America East, South America West, North Atlantic, North Pacific |
| North America West | LAND | 5 | Central America, North America East, Arctic Ocean, North Atlantic, North Pacific |
| South America West | LAND | 5 | Central America, South America East, North Pacific, South Atlantic, South Pacific |
| South America East | LAND | 4 | Central America, South America West, North Atlantic, South Atlantic |
| East Africa | LAND | 4 | Indian Ocean, South Atlantic, West Africa, Arabia |
| West Africa | LAND | 4 | North Atlantic, South Atlantic, East Africa, Arabia |
| South Asia | LAND | 4 | Indian Ocean, North Pacific, Arabia, North Asia |
| Europe | LAND | 4 | North Atlantic, Arabia, North Asia, Scandinavia |
| Scandinavia | LAND | 4 | Arctic Ocean, North Atlantic, North Asia, Europe |
| North America East | LAND | 3 | North America West, Arctic Ocean, North Atlantic |
| New Zealand | LAND | 3 | Australia, Indian Ocean, South Pacific |
| Antarctica | LAND | 3 | Indian Ocean, South Atlantic, South Pacific |
| Australia | LAND | 2 | New Zealand, Indian Ocean |

## Открытые находки

| ID | Тип | Уровень | Статус | Суть |
|---|---|---|---|---|
| `MF-003` | TERMINOLOGY | INFO | DECIDED | Три названия областей у нас длиннее оригинальных |
| `MF-009` | DECISION | INFO | DECIDED | Глифов на нашей карте не будет — стартовый регион пишется текстом на планшете |
| `MF-005` | VERIFICATION | INFO | OPEN | Канонический состав 13 областей стороны «3» закрывает вопрос PLAY-001 |
| `MF-007` | DECISION | INFO | DECIDED | Геометрия в подреестр не заводится |
| `MF-012` | DECISION | INFO | DECIDED | Форматы офисной бумаги в контексте карты не считаются и не упоминаются |
| `MF-016` | DECISION | INFO | DECIDED | Игровая функция важнее географической точности; заведена игровая база world-game |
| `MF-017` | DECISION | INFO | DECIDED | Формат и инструментарий поля — вектор GeoJSON плюс SVG, проверка по вектору |
