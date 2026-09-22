# Cthulhu Wars — юниты и компоненты по фракциям (выписка)

- **SRC-ID:** `SRC-WIKI` (основной), сверено с `SRC-NECRO-FAC` и `SRC-RB-NEW`
- **Источник A:** Cthulhu Wars Strategy Wiki (Fandom), викитекст страниц фракций,
  шаблоны `{{unit|имя|фракция|количество|стоимость|бой|spellbook}}` и
  `{{comp|имя|фракция|количество}}`. Получено 2026-09-11 через `api.php`.
- **Источник B:** `https://necronomicon.app/data-files/factions.json` (v2.0,
  Filippo Salvarani), поля `tot / cost / combat / notes`. Получено 2026-09-11.
- **Источник C:** `SRC-RB-NEW`, страницы COMPONENTS каждой фракции (только количества фигурок).

**Результат сверки:** по всем 11 фракциям компендиума количества, стоимости и боевые
значения источников A и B совпадают **полностью**. Источник C (рулбук) подтверждает
количества фигурок везде, кроме двух мест, отмеченных ниже как расхождение вёрстки.

Обозначения: `*` — значение задаётся формулой, формула приведена отдельной строкой.
`n/a` — параметра у компонента нет.

---

## Универсальное (одинаково у всех фракций, если не сказано иное)

| Компонент | Кол-во | Ст-ть | Бой |
|---|---|---|---|
| Acolyte Cultist | 6 | 1 | 0 |
| Faction Card, Faction Token, Power Marker, Doom Marker | по 1 | — | — |
| Battle Dice | 20 | — | — |
| Gate (общий компонент ядра, не фракционный) | 24 на игру | 3 | n/a |

Компоненты из дополнений, доложенные в коробку фракции (не входят в базовый состав):
`High Priest` ×1 (ст. 3, бой 0), `Brain Cylinder` ×4 (ст. 0, бой 0),
`The Dark Demon` ×1 (ст. 1, бой 0), 7-й `Acolyte` ×1.
Bubastis и Daemon Sultan их не используют (см. ниже).

---

## Great Cthulhu (ядро, рулбук с. 43)

| Юнит | Тип | Кол-во | Ст-ть | Бой | Spellbook |
|---|---|---|---|---|---|
| Acolyte | Cultist | 6 | 1 | 0 | Dreams |
| Deep One | Monster | 4 | 1 | 1 | Devolve |
| Shoggoth | Monster | 2 | 2 | 2 | Absorb |
| Starspawn | Monster | 2 | 3 | 3 | Regenerate |
| Cthulhu | Great Old One | 1 | 10 / затем 4 | 6 | — |

- Уникальная способность: **Immortal** (Ongoing).
- Spellbooks: Absorb, Devolve, Dreams, Regenerate, Submerge, Y'ha Nthlei.
- Отдельных жетонов фракции нет.

## Yellow Sign (ядро, с. 47)

| Юнит | Тип | Кол-во | Ст-ть | Бой | Spellbook |
|---|---|---|---|---|---|
| Acolyte | Cultist | 6 | 1 | 0 | Passion |
| Undead | Monster | 6 | 1 | `*` | Zingaya |
| Byakhee | Monster | 4 | 2 | `*` | Shriek of the Byakhee |
| King in Yellow | Great Old One | 1 | 4 | 0 | — |
| Hastur | Great Old One | 1 | 10 | `*` | — |

- Undead: кубиков на 1 меньше, чем всего Undead в битве.
- Byakhee: кубиков на 1 больше, чем всего Byakhee в битве.
- Hastur: бой равен текущей стоимости Ritual of Annihilation.
- Жетоны: **Desecration Marker ×12**, кастомный кубик ×1.
- Уникальная способность: **Feast** (Ongoing).
- Spellbooks: He Who is Not to be Named, Passion, Shriek of the Byakhee,
  The Screaming Dead, The Third Eye, Zingaya.

## Crawling Chaos (ядро, с. 53)

| Юнит | Тип | Кол-во | Ст-ть | Бой | Spellbook |
|---|---|---|---|---|---|
| Acolyte | Cultist | 6 | 1 | 0 | — |
| Nightgaunt | Monster | 3 | 1 | 0 | Abduct |
| Flying Polyp | Monster | 3 | 2 | 1 | Invisibility |
| Hunting Horror | Monster | 2 | 3 | 2 | Seek and Destroy |
| Nyarlathotep | Great Old One | 1 | 10 | `*` | — |

- Nyarlathotep: бой равен сумме faction spellbooks своих и противника в битве.
- Уникальная способность: **Flight** (Ongoing).
- Spellbooks: Abduct, Emissary of the Outer Gods, Invisibility, Madness,
  Seek and Destroy, The Thousand Forms.

## Black Goat (ядро, с. 57)

| Юнит | Тип | Кол-во | Ст-ть | Бой | Spellbook |
|---|---|---|---|---|---|
| Acolyte | Cultist | 6 | 1 | 0 (1 с Frenzy) | — |
| Ghoul | Monster | 2 | 1 (0 с The Thousand Young) | 0 | Necrophagy |
| Fungi From Yuggoth | Monster | 4 | 2 (1 с TTY) | 1 | Ghroth |
| Dark Young | Monster | 3 | 3 (2 с TTY) | 2 | The Red Sign |
| Shub-Niggurath | Great Old One | 1 | 8 | `*` | — |

- Shub-Niggurath: бой = контролируемые Gates + Cultists в игре; с The Red Sign
  ещё +1 за каждого Dark Young.
- Уникальная способность: **Fertility Cult** (Ongoing).
- Spellbooks: Blood Sacrifice, Frenzy, Ghroth, Necrophagy, The Red Sign,
  The Thousand Young. **Avatar — способность Great Old One, а не spellbook.**

## The Ancients (дополнение CW-F6, с. 63)

| Юнит | Тип | Кол-во | Ст-ть | Бой | Spellbook |
|---|---|---|---|---|---|
| Acolyte | Cultist | 6 | 1 | 0 | — |
| Un-Men | Monster | 3 | 3 (0 с Festival) | 0 | Festival |
| Reanimated | Monster | 3 | 4 (1 с Brainless) | 2 | Brainless |
| Yothan | Terror | 3 | 6 (3 с Extinction) | 7 | Extinction |
| Cathedral | Building | 4 | 3 (1, если не рядом с другим Cathedral) | n/a | Worship Services |

- **Great Old One отсутствует** — единственная такая фракция.
- Уникальная способность: **Dematerialization** (Doom Phase).
- Spellbooks: Brainless, Consecration, Extinction, Festival, Unholy Ground,
  Worship Services.

## Bubastis (дополнение CW-F8, с. 69)

| Юнит | Тип | Кол-во | Ст-ть | Бой | Spellbook |
|---|---|---|---|---|---|
| Earth Cat | Monster | 6 | 1 | 0 | Catabolism |
| Cat from Mars | Monster | 2 | 2 | 1 | Zagazig |
| Cat from Saturn | Monster | 2 | 3 | 2 | Savagery |
| Cat from Uranus | Monster | 2 | 4 | 3 | Predator |
| Bastet | **Elder God** | 1 | 6 | `*` | — |

- Все кошки дают по 1 Power в Gather Power Phase.
- Bastet: кубиков не бросает, добавляет 1 Kill к результату, противник снимает 1 Kill.
- Acolytes у фракции нет вовсе — их роль играют 6 Earth Cats.
- Жетоны: **Moon Tile ×1**. Доложены, но фракцией не используются:
  4 Brain Cylinders + 4 Brain Cylinder Tokens, 1 Dark Demon, High Priest.
- Уникальная способность: **Lunacy** (Ongoing).
- Spellbooks: Ailurophobia, Catabolism, Catnapping, Predator, Savagery, Zagazig.

## Daemon Sultan (дополнение CW-F7, с. 75)

| Юнит | Тип | Кол-во | Ст-ть | Бой | Spellbook |
|---|---|---|---|---|---|
| Acolyte | Cultist | 6 | 1 | 0 | — |
| Larva Thesis | Monster | 2 | 1 | 0 (2, если в игре Avatar Thesis) | — |
| Larva Antithesis | Monster | 2 | 1 | 0 (2, если в игре Avatar Antithesis) | — |
| Larva Synthesis | Monster | 2 | 1 | 0 (2, если в игре Avatar Synthesis) | — |
| Avatar Thesis | Great Old One | 1 | = позиция маркера Azathoth (0–8) | = позиция маркера | Undirected Energy |
| Avatar Antithesis | Great Old One | 1 | = 8 − позиция маркера | = 8 − позиция маркера | Fiendish Growth |
| Avatar Synthesis | Great Old One | 1 | 8 | бросок кубика Azathoth → столько боевых кубиков | — |
| Chaos Gate | Building | 3 | n/a | n/a | Chaos Gate |

- Старт: **4 Power и ничего на карте**.
- Жетоны: Azathoth Die ×1, Azathoth Glyph Token ×1, Great Old One Card ×1.
  Доложены, но не используются: High Priest ×1, Dark Demon ×1, Brain Cylinders ×4.
- Уникальная способность: **Psychosis** (Action: Cost 0).
- Spellbooks: Animate Matter, Chaos Gate, Consummation, Fiendish Growth, Traitors!,
  Undirected Energy.
- **Расхождение вёрстки:** на странице COMPONENTS рулбука (с. 75) подписаны только
  «2 Larvae Thesis» и «2 Larvae Synthesis», Antithesis и три Аватара не подписаны.
  Источники A и B дают полный состав, он и принят.

## Opener of the Way (дополнение CW-F1, с. 81)

| Юнит | Тип | Кол-во | Ст-ть | Бой | Spellbook |
|---|---|---|---|---|---|
| Acolyte | Cultist | 6 | 1 | 0 | The Million Favored Ones |
| Mutant | Monster | 4 | 2 | 1 | The Million Favored Ones |
| Abomination | Monster | 3 | 3 | 2 | The Million Favored Ones |
| Spawn of Yog-Sothoth | Monster | 2 | 4 | 3 | The Million Favored Ones |
| Yog-Sothoth | Great Old One | 1 | 6 (поверх Spawn) | `*` | — |

- Yog-Sothoth: бой = удвоенное число вражеских faction Great Old Ones в игре.
  В игре на двоих — всегда 4 (правка рулбука, с. 40).
- Жетоны: кастомные кубики ×5.
- Уникальная способность: **The Beyond One** (Action: Cost 1).
- Spellbooks: Channel Power, Dragon Ascending, Dragon Descending,
  Dread Curse of Azathoth, The Million Favored Ones, They Break Through.

## Sleeper (дополнение CW-F2, с. 85)

| Юнит | Тип | Кол-во | Ст-ть | Бой | Spellbook |
|---|---|---|---|---|---|
| Acolyte | Cultist | 6 | 1 | 0 | — |
| Wizard | Monster | 2 | 1 | 0 | Energy Nexus |
| Serpent Man | Monster | 3 | 2 | 1 | Ancient Sorcery |
| Formless Spawn | Monster | 4 | 3 | `*` | — |
| Tsathoggua | Great Old One | 1 | 8 | `*` | — |

- Formless Spawn: каждый бросает по кубику за каждого Formless Spawn и Tsathoggua
  на карте.
- Tsathoggua: бой = текущий Power противника или 2, что больше.
- Уникальная способность: **Death From Below** (Doom Phase).
- Spellbooks: Ancient Sorcery, Burrow, Capture Monster, Cursed Slumber,
  Demand Sacrifice, Energy Nexus.

## Tcho-Tcho (дополнение CW-F5, с. 89)

| Юнит | Тип | Кол-во | Ст-ть | Бой | Spellbook |
|---|---|---|---|---|---|
| Acolyte | Cultist | 6 | 1 | 0 | Soulless |
| High Priest | Cultist | 3 | 3 | 0 | Martyrdom |
| Proto-Shoggoth | Monster | 6 | 2 | 1 | Terror |
| Ubbo-Sathla | Great Old One | 1 | 0 в Doom Phase / 6 в Action Phase | `*` | — |

- Ubbo-Sathla: бой = значение Growth counter на треке Doom.
- Жетоны: Growth Counter ×1, кастомный кубик ×1.
- Уникальная способность: **Sycophancy** (Doom Phase).
- **Spellbooks — 12 карт, в партии играют 6** (рулбук с. 91, «Tcho-Tcho Tribes»):
  - универсальные (всегда): Hierophants, Soulless, Terror;
  - Tsang: Idolatry, Martyrdom, Tablets of the Gods — это исходная версия фракции;
  - Leng: Dark Rituals, Fulmination, Surprise!;
  - Sarkomand: Doomsday, Inerrant, Otherworld Alliances.
  Игрок тайно выбирает племя, берёт его тройку, остальные 6 карт убираются в коробку.

## Windwalker (дополнение CW-F3, с. 95)

| Юнит | Тип | Кол-во | Ст-ть | Бой | Spellbook |
|---|---|---|---|---|---|
| Acolyte | Cultist | 6 | 1 | 0 | Cannibalism |
| Wendigo | Monster | 4 | 1 | 1 | Cannibalism, Howl |
| Gnoph-Keh | Monster | 4 | `*` | 3 | Berserkergang |
| Rhan Tegoth | Great Old One | 1 | 6 | 3 | — |
| Ithaqua | Great Old One | 1 | 6 (заменяет Gate) | `*` | — |

- Gnoph-Keh: стоимость = число Gnoph-Keh, оставшихся в пуле (один в пуле → цена 1).
- Ithaqua: бой = половина Doom противника, округление вверх.
- Жетоны: Ice Age Token ×1.
- Уникальная способность: **Hibernate** (Action: Cost 0).
- Spellbooks: Arctic Wind, Berserkergang, Cannibalism, Herald of the Outer Gods,
  Howl, Ice Age.
- Два стартовых региона; фракция никогда не ходит первой в начале партии.

## The Invasion (дополнение CW-F9) — в компендиуме SRC-RB-NEW отсутствует

| Юнит | Тип | Кол-во | Ст-ть | Бой | Spellbook |
|---|---|---|---|---|---|
| Demon Larva | Cultist | 6 | 1 | 0 | — |
| Gryllus | Monster | 6 | 2 | 1 | Scavenge |
| Fiend | Monster | 4 | 4 | 3 | Entropy Siphon |
| Baphomet | Great Old One | 1 | 0 (насовсем убрать свой отряд из игры) | `*` | — |
| Lord's Shadow Marker | Building | 6 | X | n/a | — |

- Baphomet: бой = 4 + весь Doom, полученный с Elder Signs в эту Action Phase.
- Demon Larvae не строят и не контролируют Gates, во всём остальном считаются Acolytes.
- Жетоны: **Portents Marker ×15**, Portents/Lord's Shadow Card ×1,
  Baphomet's Fury Card ×1.
- Уникальная способность: **Eternal Servitude** (Ongoing).
- Spellbooks: Blood Offering, Eclipse, Entropy Siphon, Hellgate, Infernolatreia,
  Scavenge.
- Расстановка: после Windwalker, 8 Power, Lord's Shadow + Fiend + 6 Demon Larvae
  в любой незанятый регион.
- Происхождение: кроссовер с *Planet Apocalypse*, автор Matthew Folger, вышла
  с кампанией Return to Planet Apocalypse. В официальном списке фракций
  Petersen Games (блог, 17.07.2026) не числится — там названы 11 фракций, — но
  продаётся как отдельный продукт `CW-F9` / `CW-F9-NM`.

---

## Расхождения в написании названий

| Рулбук SRC-RB-NEW | Вики | necronomicon | Принято |
|---|---|---|---|
| Regeneration | Regenerate | Regenerate | Regenerate (название карты), «Regeneration» — в тексте правил |
| He Who is Not to be Named | He Who is Not to be Named | He Who Must Not Be Named | He Who is Not to be Named |
| Rhan Tegoth | Rhan-Tegoth | Rhan Tegoth | Rhan Tegoth |
| Ubbo Sathla | Ubbo-Sathla | Ubbo-Sathla | Ubbo-Sathla |

---

## The Invasion — дополнительные правила компонентов

Добавлено 2026-09-11 по решению Alek: фракция в работу не берётся, но данные
вносятся полностью.

**Lord's Shadow.** Во всём равен Gate, кроме трёх пунктов: его нельзя перемещать;
в регионе с ним можно построить обычный Gate; по умолчанию он контролируется
игроком The Invasion без контролирующего отряда — но если в регионе есть чужой
контролируемый Gate, Shadow достаётся тому игроку как дополнительный Gate
(Yog-Sothoth считается Gate для этой цели, если он единственный не-Shadow Gate
в регионе). Уничтожение контролируемого The Invasion Lord's Shadow (Ithaqua,
Bhole и подобное) даёт The Invasion 2 Elder Sign вместо любого другого эффекта;
уничтожение региона с жетонами Portent — 1 Elder Sign.

> В печатных правилах на месте Bhole стоит Dhole; Matthew Folger подтвердил, что
> это опечатка. Источник пометки — примечание на вики.

**Жетоны Portent при расстановке.** В конце расстановки The Invasion (после
выбора стартового региона и до расстановки Opener) каждый не-игрок The Invasion,
включая Opener, по очереди кладёт один Portent в любой регион без Gate и без
Portent, не соседний со стартовым регионом The Invasion. Так выкладывается
не больше 5 жетонов.

**Baphomet's Fury Card.** Не действует, пока маркер трека Ritual не дойдёт
до первой «7»; тогда карта переворачивается.

- *Torment* (Ongoing): убивая или уничтожая вражеские отряды (кроме захвата),
  вместо этого противник теряет Power, равный половине исходной стоимости
  каждого отряда с округлением вверх. Не может заплатить — эффект не работает
  вовсе, отряды гибнут как обычно. Обязательно.
- *Transference* (Ongoing): когда вражеская фракция убивает или уничтожает ваш
  отряд (не захватом), карта переходит к ней в конце текущего действия,
  а The Invasion получает 1 Doom. Обязательно.

**Условия получения spellbooks:** пробудить Baphomet; в конце второй Doom Phase
взять карту (все прочие теряют 1 Doom); действием заплатить 4 Power и 1 Doom;
иметь на планшете захваченных Cultists двух и более фракций; создать
Lord's Shadow; создать ещё один Lord's Shadow.

---

## Стартовые регионы: как восстановлены

В оригинале стартовый регион подписан только на faction card, на карте стоит
глиф. У нас регионы названы, поэтому имя берётся с нашего планшета через
подтверждённую пару маппинга.

| Фракция оригинала | Регион | Откуда | Доверие |
|---|---|---|---|
| Great Cthulhu | South Pacific / юг Тихого океана | рулбук с. 44 (R’lyeh) **и** планшет Островной Империи | HIGH |
| Black Goat | Africa → Западная Африка | рулбук с. 8 **и** планшет Клонэйд Ресёрч | HIGH |
| Yellow Sign | Европа | планшет Глобал Петролеум (MAP-03) | MEDIUM |
| Crawling Chaos | Южная Азия | планшет Эйркрафт Корпорейшн (MAP-02) | MEDIUM |
| Sleeper | запад Северной Америки | планшет Североамериканского Альянса (MAP-08) | MEDIUM |
| Windwalker | — | пара только гипотеза, брать неоткуда | — |

У The Ancients, Bubastis, Opener, Tcho-Tcho, Daemon Sultan и The Invasion
стартовый регион задан правилом расстановки, а не глифом.

---

## Сверка по самим компонентам (2026-09-11, второй заход)

Нашлись планшеты фракций — то, чего не хватало в первый заход.

**Источник D — `SRC-PLANCARD`:** `Plan_Card.pdf` в корне проекта. Русское издание,
8 страниц: планшеты четырёх фракций ядра (стр. 2 Ползучий Хаос, 4 Чёрные Козлы,
6 Великий Ктулху, 8 Жёлтый Знак) и по шесть карт заклинаний к каждой.
PDF создан 14.10.2015, изменён 22.08.2017 — издание O1/O2.

**Источник E — `SRC-WIKI-FC`:** изображения `File:Faction Card - <Фракция>.png`
на вики, 609×342, читаются при увеличении втрое. Прочитаны все десять.

**Источник F — `SRC-WIKI-MAP`:** карта Земли на 5 игроков, половины 5P-L и 5P-R,
660×660. Глифы опознаны сличением с `File:Sigil - <Фракция>.png`.

### Что подтвердилось

| Фракция | Чем подтверждено | Итог |
|---|---|---|
| Great Cthulhu | русский планшет | совпало полностью |
| Yellow Sign | русский планшет | совпало полностью |
| Black Goat | русский планшет | совпало полностью |
| Crawling Chaos | русский планшет **и** англ. карта | **расхождение**, см. ниже |
| The Ancients, Bubastis, Daemon Sultan, Opener, Sleeper, Tcho-Tcho, Windwalker | англ. faction card | совпало полностью |
| The Invasion | нечем — карты нет нигде | остаётся MEDIUM |

Дополнительно с компонентов:

- **Bastet напечатана как ELDER GOD**, а не Great Old One — это не ошибка
  фанатских источников, а текст на карте.
- **Yothan напечатан как TERROR**, Cathedral и Chaos Gate — как BUILDING.
- **На faction card Daemon Sultan есть все три Larva**, включая Antithesis;
  трёх Аватаров на ней нет вовсе — они на отдельной Great Old One Card.
- **Faction card не называет стартовый регион.** На всех картах написано
  «6 Acolytes and a Controlled Gate in the Area marked with this Glyph» /
  «6 Адептов и врата под контролем в зоне, помеченной глифом».

### Расхождение изданий: Ползучий Хаос

| Юнит | Русское издание (2015/2017) | Актуальная англ. карта |
|---|---|---|
| Летающий полип / Flying Polyp | 2 / **2** | 2 / **1** |
| Охотящийся Ужас / Hunting Horror | 3 / **3** | 3 / **2** |

Всё остальное у фракции совпадает. В эррате и FAQ Petersen изменений по Crawling
Chaos нет ни строчки. В реестре оставлены актуальные значения. См. `FAC-017`.

### Стартовые регионы — сняты с глифов карты

| Фракция | Зона (ориг.) | Зона (наша карта) |
|---|---|---|
| Great Cthulhu | South Pacific (подпись «R'lyeh») | юг Тихого океана |
| Yellow Sign | Europe | Европа |
| Crawling Chaos | South Asia | Южная Азия |
| Black Goat | West Africa | Западная Африка |
| Sleeper | North America West | запад Северной Америки |
| Windwalker | Arctic Ocean (подпись «Lomar») **и** Antarctica | Северный Ледовитый океан и Антарктида |

У Ancients, Bubastis, Opener, Tcho-Tcho, Daemon Sultan и The Invasion глифа нет:
регион задан правилом расстановки.

Наша карта повторяет деление оригинала один в один — те же 17 зон: Запад/Восток
Северной Америки, Центральная Америка, Запад/Восток Южной Америки, Европа,
Скандинавия, Северная/Южная Азия, Аравийский полуостров, Западная/Восточная
Африка, Австралия, Новая Зеландия, Антарктида и шесть океанских зон.

### Русские названия юнитов ядра (официальная локализация)

| Оригинал | Русское издание |
|---|---|
| Acolyte | Адепт |
| Deep One | Глубоководный |
| Shoggoth | Шоггот |
| Starspawn | Звёздное отродье |
| Nightgaunt | Ночной Мверзь |
| Flying Polyp | Летающий полип |
| Hunting Horror | Охотящийся Ужас |
| Ghoul | Упырь |
| Fungi From Yuggoth | Ми-го |
| Dark Young | Тёмная Молодь |
| Undead | Зомби |
| Byakhee | Бьякхи |
| Cthulhu / Nyarlathotep / Shub-Niggurath / Hastur / King in Yellow | Ктулху / Ньярлатотеп / Шаб-Ниггурат / Хастур / Король в Жёлтом |

Термины планшета: Power → **сила**, Combat → **мощь**, Gate → **врата**,
Elder Sign → **Знак Древних**, Doom → **Судьба**, Spellbook → **книга**,
Ritual of Annihilation → **Ритуал Уничтожения**, Area → **зона**.

---

## Решение по конфликту изданий (Alek, 2026-09-11)

Редизайн равняется на **актуальное издание**. В реестре по Ползучему Хаосу
оставлены значения актуальной карты: Летающий полип 2 / 1, Охотящийся Ужас 3 / 2.

Русское издание (`SRC-PLANCARD`) переведено в источники исторической справки:
из него берутся русские названия юнитов и терминология, но не числа.
Его приоритет понижен с 1 до 3.

Порядок разрешения конфликтов записан в `factions.yaml` → `meta.source_policy`:

1. компонент актуального издания — изображения faction cards и карты Земли;
2. рулбук-компендиум, эррата, FAQ;
3. фанатские базы — вики и necronomicon (допустимый крайний источник,
   такие записи помечаются `stats_confidence: MEDIUM`);
4. русское издание 2015/2017 — только названия и термины.

Назначение реестра: фундамент для последующей выверки наших планшетов, карт
и жетонов. Сами планшеты в этой задаче не правятся — выверка идёт отдельными
задачами и опирается на эти числа как на эталон.
