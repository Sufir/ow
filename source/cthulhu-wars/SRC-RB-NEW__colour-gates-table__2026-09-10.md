# SRC-RB-NEW — Colour Gates, таблица эффектов (The Colour Out of Space)

**Источник:** `SRC-RB-NEW__cw-rulebook-new-layout__2026-09-10.pdf`
**Страницы PDF:** 142–143 (нумерация книги — 137–138).
В ТЗ CODE-02 указаны PDF-страницы 143–144; фактически таблица лежит на 142–143,
номера книги (137–138) совпадают. См. PNG в `../cthulhu-wars/pages/SRC-RB-NEW/`.

**Раскладка:** столбцы 1 `METEORITE` и 2 `FERTILITY` — на стр. 142,
столбцы 3 `FEASTING`, 4 `MADNESS`, 5 `BLIGHT`, 6 `DEPARTURE` — на стр. 143.
Столбцы 1 и 6 — сплошной текст без разбивки по цветам, он повторён в каждой строке
таблицы ниже одним значением (в PDF это одна ячейка на всю высоту).

Текст дословно из PDF, английский, не переведён. Мягкие переносы строк сняты.

Вводный абзац перед таблицей (стр. 142→143, шапка чарта):

> When you Create a Gate, you may chose and place either an available Colour Gate or a normal Gate. You can ONLY Create the Glow Gate if you already Control another Colour Gate. You do not have to Create the Gate of your Faction color. So Crawling Chaos can Create a red Gate. A Colour Gate acts as a normal Gate during the Gather Power Phase. At the START of each Doom Phase, roll 1d6 and consult the appropriate column of the chart below:

## Столбцы 1 и 6 (сплошной текст, без разбивки по цветам)

| Столбец | Текст |
|---|---|
| 1 METEORITE | Beginning with the Starting Player, and continuing in turn order, the first player who does not Control a Colour Gate must select a Colour Gate from the Pool (if available) and replace one of his normal Gates with it. At most one player does this. |
| 6 DEPARTURE | The player with the lowest Doom total may select 1 Colour Gate anywhere on the map and replace it with a normal Gate. On a tie for lowest Doom, all tied players do this in player order. When finished, reroll the Colour die. On a second roll of 6, nothing further happens. On any other roll, consult the appropriate column of the chart. |

## Полная таблица

| Цвет | 1 METEORITE | 2 FERTILITY | 3 FEASTING | 4 MADNESS | 5 BLIGHT | 6 DEPARTURE |
|---|---|---|---|---|---|---|
| BLUE | *(см. выше, одна ячейка на весь столбец)* | BLUE: The Gate’s Controller gains 1 Power. | BLUE: The Gate’s Controller loses 1 Power. | BLUE: The Gate’s Controller gains 1 Power. | BLUE: The Gate’s Controller loses 1 Power. | *(см. выше, одна ячейка на весь столбец)* |
| GREEN | — | GREEN: The Gate’s Controller earns an extra Elder Sign for a Ritual of Annihilation this Doom Phase. | GREEN: The Gate’s Controller earns an extra Elder Sign for a Ritual of Annihilation this Doom Phase. | GREEN: The Gate’s Controller may not perform a Ritual of Annihilation this Doom Phase. | GREEN: The Gate’s Controller may not perform a Ritual of Annihilation this Doom Phase. | — |
| ORANGE | — | ORANGE: The Gate’s Controller gains 1 Power. | ORANGE: The Gate’s Controller gains 1 Power. | ORANGE: The Gate’s Controller loses 1 Power. | ORANGE: The Gate’s Controller loses 1 Power. | — |
| PURPLE | — | PURPLE: The Gate’s Controller gains 1 Doom. | PURPLE: The Gate’s Controller loses 1 Doom. | PURPLE: The Gate’s Controller gains 1 Doom. | PURPLE: The Gate’s Controller loses 1 Doom. | — |
| RED | — | RED: The Gate’s Controller Eliminates the lowest cost enemy Monster or Cultist at the Gate, if available. | RED: The Gate’s Controller Eliminates an owned Unit at the Gate. | RED: The Gate’s Controller Eliminates the lowest cost enemy Monster or Cultist at the Gate, if available. | RED: The Gate’s Controller Eliminates an owned Unit at the Gate. | — |
| PINK | — | PINK: The Gate’s Controller receives an extra Elder Sign for a Ritual of Annihilation this turn. | PINK: The Gate’s Controller may not perform a Ritual of Annihilation this Doom phase. | PINK: The Gate’s Controller receives an extra Elder Sign for a Ritual of Annihilation this Doom Phase. | PINK: The Gate’s Controller may not perform a Ritual of Annihilation this Doom Phase. | — |
| LIGHT BLUE | — | LIGHT BLUE: The Gate’s Controller Eliminates the lowest cost enemy Monster or Cultist at the Gate, if available. | LIGHT BLUE: The Gate’s Controller Eliminates an owned Unit at the Gate. | LIGHT BLUE: The Gate’s Controller Eliminates the lowest cost enemy Monster or Cultist at the Gate, if available. | LIGHT BLUE: The Gate’s Controller Eliminates an owned Unit at the Gate. | — |
| YELLOW | — | YELLOW: The Gate’s Controller gains 1 Doom. | YELLOW: The Gate’s Controller gains 1 Doom. | YELLOW: The Gate’s Controller loses 1 Doom. | YELLOW: The Gate’s Controller loses 1 Doom. | — |
| TURQUOISE | — | TURQUOISE: The Gate’s Controller chooses 2 Colour Gates and swaps them just before Gate effects happen. | TURQUOISE: The Gate’s Controller chooses 2 Colour Gates and swaps them just before Gate effects happen. | TURQUOISE: The Gate’s Controller replaces one of his or her Colour Gates for a normal Gate. | TURQUOISE: The Gate’s Controller replaces one of his or her Colour Gates for a normal Gate. | — |
| GLOW | — | GLOW: The Gate’s Controller chooses any other Colour’s effect from Fertility. | GLOW: The Gate’s Controller chooses any other Colour’s effect from Feasting. | GLOW: The Gate’s Controller chooses any other Colour’s effect from Madness. | GLOW: The Gate’s Controller chooses any other Colour’s effect from Blight. | — |

## Как восстановлено

PyMuPDF, `get_text("dict")` с координатами. Ячейки таблицы — отдельные текстовые
блоки PDF, колонки различаются по `x0`: стр. 142 — 315 (METEORITE) и 468 (FERTILITY);
стр. 143 — 49 (FEASTING), 189 (MADNESS), 329 (BLIGHT), 455 (DEPARTURE).
Заголовки и цифры граней кубика подтверждены по координатам спанов
(`1 METEORITE` x=338, `2 FERTILITY` x=482; `3 FEASTING` x=65, `4 MADNESS` x=205,
`5 BLIGHT` x=352, `6 DEPARTURE` x=477). Порядок строк цветов внутри столбца — по `y0`,
он одинаков во всех четырёх «цветных» столбцах.

## Замечание по RULE-001

Расхождение **есть в самом PDF**, извлечением оно не внесено. В столбце `2 FERTILITY`:

- GREEN — «earns an extra Elder Sign for a Ritual of Annihilation **this Doom Phase**.»
- PINK — «receives an extra Elder Sign for a Ritual of Annihilation **this turn**.»

В PDF это два отдельных блока (стр. 142, y=217 и y=415), «this turn» стоит отдельной
строкой блока PINK. Дополнительно в тех же двух ячейках расходятся глаголы:
`earns` у GREEN против `receives` у PINK. Для сравнения, в столбце `4 MADNESS` у PINK
формулировка — «receives an extra Elder Sign for a Ritual of Annihilation **this Doom
Phase**», то есть «this turn» встречается в таблице ровно один раз.
