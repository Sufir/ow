# Elder God и боевой робот: нужен ли отдельный тип

**Дата:** 01.10.2026 · **Статус:** решение принято — `D-110`, вариант А (02.10.2026) ·
**Вопрос:** `FAC-013` · **Связано:** `D-011`, `D-052`, `D-057`, `D-077`, `D-106`, `MRC-I-011`,
`BL-UNIT-006`, `BL-UNIT-015`, `TERM-026`, `NUM-100` ·
**Приложения:** `rules/tasks/ИССЛЕДОВАНИЕ-Elder-God — таблицы.md` (три таблицы сверки),
`source/web/SRC-WEB-ELDERGODS__cw-elder-gods__2026-10-01.md` (веб-сбор)

---

## Вывод

Отдельный тип для Elder God вводить не нужно. «Зардоз» остаётся боевым роботом, а обе
особенности Elder God живут на его планшете — они там уже напечатаны.

1. **Оригинал устроен так же.** Elder God «treated as Great Old Ones for all purposes except»
   два пункта: нет собственного Elder Sign за ритуал и нет боевых кубиков. Издатель повторил
   это отдельно: «In virtually every other way, an Elder God is the same — for all rules purposes».
2. **Сейчас слияние ничего не ломает.** Проверено 138 правил ядра и 12 фракций оригинала,
   около 110 правил нейтралов и дополнений, 88 мест нашей книги и компонентов. Расхождений
   по механике на восьми наших фракциях и семи наёмных роботах нет.
3. **Отдельный тип сломал бы больше, чем починил.** Только в ядре и 12 фракциях 53 правила
   считают или выбирают GOO, и Elder God обязан в них участвовать. С отдельным типом каждое
   пришлось бы писать «БР или старший бог»; каждое пропущенное — ошибка.
4. **Риск появится только с новыми компонентами пяти видов** (раздел 4). Каждый ловится одной
   проверкой в момент, когда компонент вводится.

---

## 1. Elder God в оригинале

### Определение

Рулбук, раздел Bubastis, с. 70:

> Bastet is an Elder God; these beings are treated as Great Old Ones for all purposes except:
> they do not provide an inherent Elder Sign for a Ritual of Annihilation, though they often
> have other means of creating Elder Signs; and Elder Gods never roll Combat dice, but provide
> some fixed benefit. They do count as equal to Great Old Ones otherwise, so they can block Unit
> Captures. Nyarlathotep gets 2 Elder Signs or half-Power cost from his Harbinger ability compared
> with that of other Great Old Ones. You can use them to Capture Cultists even if an enemy Monster
> is present, and so forth.

Два исключения, всё остальное — как у GOO:

1. **Нет собственного Elder Sign за ритуал.** Знаки за ритуал дают только фракционные GOO:
   «ONLY Faction Great Old Ones provide Elder Signs when you perform a Ritual of Annihilation»
   (с. 109, правило независимых). Через спецспособность — можно: «Elder Gods do not provide
   Elder Signs for Rituals of Annihilation, except in conjunction with special abilities»
   (FAQ, с. 183).
2. **Никогда не бросает боевые кубики.** Вместо них — фиксированный результат, который
   действует и без броска: «Elder Gods just inflict results. They don't roll dice, and they don't
   require dice to be rolled for their results to take place» (FAQ, с. 183). Отсюда: «Can Elder
   Gods declare Battle since they have no Combat dice? — No.» (FAQ, с. 182).

### Подтверждения издателя

- **Апдейт 3 кампании CATaclysm, Сэнди Петерсен, про Bastet:** «She's an Elder God (like Nodens),
  not a Great Old One. This means she does not roll combat dice, and she does not inherently provide
  an Elder Sign when you Ritual… the enemy must lower their rolled Kill total by 1.»
- **Апдейт 50 той же кампании** (проверен повторным запросом 01.10.2026): «Some are labeled
  "Independent Elder God" on the backside, instead of Independent Great Old One, but there's no real
  difference… In virtually every other way, an Elder God is the same - for all rules purposes.»
- **Карта фракции Bubastis** печатает тип ELDER GOD — это метка на компоненте, а не отдельная
  категория правил: правила относят её к GOO «for all purposes».

### Все Elder God оригинала — шесть

| Elder God | Где | Цена | Бой (кубиков не бросает) | Знак при создании |
|---|---|---|---|---|
| Bastet | фракция Bubastis | 6 | +1 Kill; у противника −1 выброшенный Kill | нет |
| Nodens | независимый, CW-U28 | 6 | +1 Kill и +2 Pain | нет |
| Hagarg Ryonis | независимый, CW-U33 | 4 | +3 Pain | нет |
| Hellmother | независимый, кроссовер The Gods War | 4 | 1 Pain за каждого своего культиста; +1 Kill при 6 и больше | да |
| Sun God | то же | 4 | 1 Pain и 1 Kill | да |
| Thunder King | то же | 4 | 1 Pain за каждую фракционную технологию; +1 Kill при всех шести | да |

Наш аналог есть только у Bastet. Независимой карты Bastet в оригинале нет, поэтому нет
и наёмного «Зардоза» (`D-106`). В цифровой реализации HRF Elder God не реализованы вовсе;
независимые GOO там сделаны как тип GOO плюс флаг, а не отдельный тип.

---

## 2. Где Elder God равен GOO — и почему отдельный тип вреден

В этих правилах Elder God участвует как GOO. Слияние даёт этот результат само;
отдельный тип — только если переписать каждое правило.

1. **Захват.** Elder God блокирует захват своих культистов и захватывает сквозь вражеского
   монстра (с. 70).
2. **Эффекты против GOO.** Harbinger (за Bastet — 3 Power или 2 знака), Emissary of the Outer
   Gods (против Bastet не защищает), Unholy Ground, Vengeance. Иммунитеты GOO тоже её: Devour,
   Avatar, Berserkergang, Capture Monster на неё не действуют.
3. **Подсчёт GOO.** Сила Yog-Sothoth (2 за каждого вражеского фракционного GOO), блок
   The Beyond One, Hibernate, требование Opener «Your Great Old One shares an Area with an Enemy
   Great Old One». FAQ: Bastet рядом с Yog-Sothoth при Requires Attention даёт 3 знака.
4. **Создание независимого.** Условие «Your Controlled Gate is in an Area with your Great Old
   One» Elder God выполняет: «you may use one Independent to help Awaken another».
5. **Подсчёт типов отрядов.** Где эффект считает разные типы (Hortator, кроссовер Planet
   Apocalypse), Elder God — тип GOO, а не пятый тип.

У нас то же самое уже работает на «Зардоза»:

1. «Военные трофеи» Эйркрафт — «за каждого вражеского боевого робота (в том числе наёмного)»;
   `D-077` прямо включает «Зардоза».
2. Сила «Шрёдингера» — «удвоенному числу вражеских боевых роботов в игре».
3. Захват, §7.3.7 — «от боевого робота защищает только боевой робот».
4. Создание наёмного робота в регионе с вашим БР — «Зардоз» на Луне (`MRC-I-011`).
5. «Взлом систем» — «если там есть хотя бы один вражеский боевой робот».

---

## 3. Сверка: особенности Elder God на планшете «Зардоза»

| Оригинал | Наш текст | Итог |
|---|---|---|
| Нет собственного Elder Sign за ритуал | Сноска: «“Зардоз” не приносит карту скрытого влияния при оказании давления» | совпадает; §6.3 шаг 4 даёт карту «за каждого БР своей фракции», сноска побеждает по §3.9 |
| Знаки через спецспособность: +1 за вражескую фабрику, +2 за вражеского GOO | «Взлом систем» — то же; с «Шрёдингером» 1 + 2 = 3, как в FAQ | совпадает |
| Кубиков нет, битву не объявляет | Сила 0; §7.3.6: «сила не менее 1… даже если у ваших отрядов есть боевые эффекты» | совпадает |
| Результат без броска | «Киборг-убийца»: «добавьте 1 смерть к своему результату, даже если кубики не бросались» | совпадает; §8.5 и §13 знают смерть только как выпавшую 6 — побеждает планшет по §3.9 |
| У противника −1 выброшенный Kill | «из выброшенного противником вычтите 1 смерть (не подавление)» | совпадает с FAQ «enemy-rolled Kills» и апдейтом 3 «rolled Kill total» |
| Zagazig «does not affect Bastet's Combat» | «Системный сбой» меняет местами только «выброшенные» результаты | совпадает |
| Harbinger — как за любой GOO | «Военные трофеи»: половина цены создания (3 нефти) или 2 карты | совпадает |

**Сила 0 — не признак Elder God.** У «Шепарда» (King in Yellow) тоже сила 0, а карту за давление
он даёт. Особенность «Зардоза» держится на тексте планшета, а не на числе в таблице.

---

## 4. Где слияние может сломаться — пять триггеров

Сейчас в игре нет ни одного такого компонента. Проверять при вводе нового компонента,
наёмника или фракции.

1. **Эффект прибавляет, задаёт, удваивает или копирует силу** — у БР, у «всех отрядов»
   или у типа отряда. С силой 0 «Зардоз» получит кубики и право объявить битву, а Elder God
   кубиков не бросает никогда. Примеры оригинала:
   - Cthugha копирует силу вражеского GOO; FAQ: против Elder God «rolls no dice… gets no further
     benefit»;
   - Proteus у Nodens копирует технологию типа отряда (Frenzy, Absorb, Savagery); по букве
     Elder God кубиков не получает, официального ответа нет.

   **Что делать:** в тексте такого эффекта исключить «Зардоза» (и других Elder God) либо тогда
   же добавить на планшет строку «Не бросает кубики; эффекты, меняющие силу, на него
   не действуют».
2. **Эффект гасит способности вражеского БР.** Пример — Elder Thing, Mind Control: «the latter
   may not use its Special Ability». У нас боевой результат «Зардоза» — свойство, и такой эффект
   его погасит. В оригинале это строка Combat; гасится ли она — официального ответа нет.
   **Что делать:** при вводе решить явно и написать на карте эффекта.
3. **Карта скрытого влияния за БР вне давления.** Пример — карта Shaggai: «Each Faction Great Old
   One that is Eliminated also provides its owner with 1 Elder Sign». Elder God её получает:
   исключение касается только ритуала. Наша сноска ограничена словами «при оказании давления» —
   так и держать, не расширять.
4. **Новый Elder God в роли наёмника** — Nodens, Hagarg Ryonis, Hellmother, Sun God, Thunder King.
   Исключение по картам уже закрыто книгой: наёмные БР карт за давление не дают (§6.3, §11.4.3).
   Каждому нужны сила 0 и свойство с «даже если кубики не бросались», у Nodens ещё и Proteus —
   см. п. 1. **Порог пересмотра:** если таких роботов станет два и больше, завести в книге
   короткое общее свойство «Не бросает кубики» — одно правило в части 8 и метка на карте. Это
   свойство, а не тип: все «БР» в текстах остаются верными.
5. **Правило проверяет «силу 0» как признак Elder God.** Так делать нельзя: см. «Шепарда»
   в разделе 3.

---

## 5. Что в книге держится только на приоритете компонента

Книга даёт общее правило, планшет Moon Systems — исключение; по §3.9 действует планшет. Ни одно
из этих мест не входит в список безусловных правил §3.9, так что по нашим принципам это корректно.

1. **Карта скрытого влияния «за каждого боевого робота своей фракции»:** §6.3 шаг 4 и пример,
   §6.4, §6.7, §11.4.3, §13 «Оказание давления»; так же памятка игрока.
2. **Смерть «только от выпавшей шестёрки»:** §8.5, §13 «Смерть» («Результат броска 6 в битве,
   и только он»), памятка битвы («Смерть — только выпавшая на боевом кубике 6»).
3. **«Каждая сторона разбирает выпавшие противником результаты»** (§8.5): добавленная смерть
   «Зардоза» не выпавшая.

Риск один: «и только он» в §13 читается как безусловное правило, хотя в списке §3.9 его нет.
Править не обязательно. Если при игре возникнет спор — смягчить до «как правило».

---

## 6. Варианты решения

**А. Ничего не менять в компонентах (рекомендую).** Закрыть `FAC-013` этим исследованием.
Пять триггеров раздела 4 держать как проверку при вводе новых компонентов.

**Б. Заранее заменить у «Зардоза» силу «0» на прочерк** и добавить строку «Не бросает кубики;
эффекты, меняющие силу, на него не действуют».
- За: триггер 1 закрыт навсегда.
- Против: правка принятого планшета (`D-052`); прочерк придётся определять в книге (§7.3.6
  и §8.4 считают силу числом) — общее правило ради одной частности; от триггеров 2 и 3
  не защищает.

**В. Отдельный тип «старший бог».** Не рекомендую.
- Противоречит «for all purposes» оригинала.
- Правила, которые считают или выбирают GOO, пришлось бы переписать «БР или старший бог»:
  53 в ядре и 12 фракциях оригинала, плюс десятки мест нашей книги, планшетов, карт и памяток.
- Новый термин в книгу, глоссарий и памятки ради одного робота.

---

## 7. Попутные находки — не про тип

1. **`terms.yaml`, `TERM-026`:** «в рулбуке правило подаётся как свойство отдельных боевых
   роботов». В книге этого нет и по принципу «частности на компонентах» быть не должно.
   Противоречит `NUM-100` («в правилах оно не описано»).
2. **`baseline.yaml`, `BL-UNIT-006`:** Harbinger «даёт 2 Elder Signs либо половинную стоимость
   по сравнению с обычным Great Old One». Пересказ сбивает: в оригинале размер тот же, что у любого
   GOO. Планшет Эйркрафт верен (`D-077`).
3. **`factions.yaml`:** `FAC-013` всё ещё `DEFERRED`; у `CW-F-06` в `category_note` стоит
   «не сверено». Закрывается этим исследованием после решения.
4. **`print/FactoryEvents.html`:** «уничтожить свою боевую единицу» — термина «боевая единица»
   в книге нет.
5. **Порядок «−1 смерть» у «Киборга-убийцы»** против переброса («Временной сдвиг») и обмена
   результатов («Системный сбой») решён в книге правилом «первым применяет атакующий»; в оригинале
   FAQ на эти связки нет. На выбор типа не влияет: расклад тот же при любом типе.

---

## 8. Пробелы

1. Тексты faction cards в рулбуке — картинки. Требования технологий части фракций оригинала
   (Sleeper, Windwalker, Daemon Sultan, Ancients, Tcho-Tcho) сверены по пересказам и
   necronomicon.app, не по сканам. На вывод не влияет: требование, которое считает GOO,
   при слиянии работает одинаково.
2. Официальных ответов нет по трём связкам: Proteus с технологией, дающей силу; Mind Control
   против Elder God; «официальное альтернативное правило», по которому независимые дают знаки
   (упомянуто в апдейте 50, текст не найден).
3. Вики fandom закрыта (HTTP 402).

---

## 9. Источники

**Локальные:**
- `source/cthulhu-wars/SRC-RB-NEW__cw-rulebook-new-layout__2026-09-10.md` — с. 70–71 (Bubastis,
  Elder Gods, Zagazig), 109 (ритуал и независимые), 163 (Shaggai), FAQ с. 182–184, 195.
- `source/web/SRC-WEB-LOYALTY__cw-loyalty-cards__2026-10-01.md` — карты независимых, Elder Thing,
  Cthugha, Nodens, Hagarg Ryonis.
- `source/web/SRC-WEB-ELDERGODS__cw-elder-gods__2026-10-01.md` — веб-сбор этого исследования.
- Треды BGG в `source/*.mhtml` — сборники FAQ сообщества, вариант Bubastis от CW Discord.

**Веб:**
- [CATaclysm, апдейт 3 — Bubastis и Bastet](https://www.kickstarter.com/projects/petersengames/cthulhu-wars-cataclysm/posts/2466093)
- [CATaclysm, апдейт 50 — The Gods War Crossover](https://www.kickstarter.com/projects/petersengames/cthulhu-wars-cataclysm/posts/2746180)
- [necronomicon.app — Bubastis](https://necronomicon.app/factions/bubastis)
- [necronomicon.app — Independent Elder Gods](https://necronomicon.app/rulebook/expansion-products)
- [necronomicon.app — Kickstarter Specials (Nodens)](https://necronomicon.app/neutral-expansions/kickstarter-specials)
- [necronomicon.app — Something About Cats (Hagarg Ryonis)](https://necronomicon.app/neutral-expansions/something-about-cats)
- [necronomicon.app — The Gods War Crossover](https://necronomicon.app/neutral-expansions/the-gods-war-crossover)
- [Официальный FAQ Petersen Games](https://petersengames.freshdesk.com/support/solutions/articles/48000952254-cthulhu-wars-rules-faq)
- [HRF, цифровая реализация](https://github.com/haunt-roll-fail/cthulhu-wars)
