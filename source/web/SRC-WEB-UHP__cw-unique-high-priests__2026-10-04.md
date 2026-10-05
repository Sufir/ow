# SRC-WEB-UHP — Unique High Priests Cthulhu Wars и три фанатских (веб-сбор)

> **SRC-ID:** `SRC-WEB-UHP` · **Получено:** 2026-10-04 · **Собрано для:** `COMP-V-03`,
> карты уникальных полковников (сверка `rules/tasks/СВЕРКА-уникальные-полковники.md`).
>
> **Что это.** Сводка, а не скачанная страница. Собрана Claude через WebFetch: вики Cthulhu Wars,
> API BoardGameGeek (`api.geekdo.com`), апдейт Kickstarter, necronomicon.app. `rules/tools/fetch.py`
> не сработал: прокси на компьютере Alek отдаёт 403 на `api.geekdo.com`. Тексты карт — по-английски,
> как на источнике.
>
> **Доверие.** Официальные тексты восьми карт взяты из локального рулбука (`SRC-RB-OLD`), вики
> с ними совпадает. Ответы дизайнера — пост BGG, пересказ писем Петерсенов, дословная копия поля
> `body` через API (art. 27245737). Три фанатские карты — пост автора на BGG через пересказчик
> WebFetch, один запрос (повторно на BGG не ходили): мелкие искажения возможны. Косвенная проверка —
> Surgery у Akeley совпадает с официальной Surgery карты Yuggoth (RB-NEW с. 171) почти слово в слово.
> Картинки карт в треде — 8 вложений, текст на них не сверялся.

---

## 0. Источники

| Код | Источник | Что это | Надёжность |
|---|---|---|---|
| **RB-OLD** | `source/cthulhu-wars/SRC-RB-OLD__cw-rulebook-old-layout__2026-09-10.md`, стр. PDF 153–158 (книжн. 143–147) | Правила Unique High Priests и тексты всех восьми карт | Официальный |
| **RB-NEW** | `source/cthulhu-wars/SRC-RB-NEW__cw-rulebook-new-layout__2026-09-10.md`, с. 132, 35–36, 196 | Правила UHP (тексты карт в новой вёрстке не напечатаны), пример битвы 9 с Keziah Mason, FAQ | Официальный |
| **FAQ** | `source/cthulhu-wars/SRC-FAQ__cw-rules-faq__2026-09-10.md`, раздел «Unique High Priests» | Три ответа: два по Lavinia, один по Asenath | Официальный |
| **WIKI** | https://cthulhuwars.fandom.com/wiki/High_Priests | Тексты восьми карт | Совпадает с RB-OLD; у Crawford Tillinghast сокращён |
| **BGG-1671563** | https://boardgamegeek.com/thread/1671563 — «Unique High Priest Q&A», пост 27245737 (2017-10-24) | Ответы Петерсенов по Asenath, Crawford, Curwen, Pitpipo — пересланные игроком | Дизайнер (пересказ из писем) |
| **BGG-3316625** | https://boardgamegeek.com/thread/3316625 — «More Unique High Priests (Albert Shiny, Nahum Gardner, & Henry Akeley)», Papa_Tom, 2024-06-12 | Три фанатских UHP — оригиналы наших Ковача, Гарднера и Брута | Фанатский, неофициальный |
| **KS-O2-30** | https://www.kickstarter.com/projects/1816687860/cthulhu-wars-onslaught-two/posts/1409570 — Update 30, Sandy’s Design Corner | Замысел UHP, ранний состав восьмёрки | Дизайнер |
| **BGG-1719427**, **BGG-1523661**, **BGG-1475574** | треды BGG об Asenath и списке UHP | Мнения игроков, официальных ответов нет | Сообщество |
| **NEC-RX** | https://necronomicon.app/neutral-expansions/rulebook-extras | Только вводные правила UHP, карт нет | Транскрипция |
| **HRF** | https://github.com/haunt-roll-fail/cthulhu-wars | Цифровая версия: есть обычный High Priest, уникальных нет | Низкий приоритет; по UHP пусто |

Балансные правки (`SRC-ERRATA__balance-changes-table`, `SRC-ERRATA-XLSX`, `2017-10-17_balance_changes.pdf`)
и Ultimate Errata Pack — про UHP ничего.

---

## 1. Правила Unique High Priests (RB-OLD с. 143, RB-NEW с. 132)

> «The Unique High Priests represent an additional set of rules for your High Priests, and offer 8 unique
> abilities. To play with the Unique High Priests rules, you will need the regular High Priest miniatures.
> When Recruiting a High Priest, you may choose for him or her to be a regular High Priest (with the
> Unspeakable Oath ability), or to be one of the named, Unique High Priests. (The Unique High Priests do NOT
> have the Unspeakable Oath ability).
> Whenever you Recruit your High Priest, you may choose for him to be normal or unique. However, once you have
> selected a Unique High Priest, that is the ONLY Unique High Priest that you may Recruit during that game.
> Once a player has Recruited a Unique High Priest, no other player may Recruit that particular Priest (even
> if it is not currently in play, either because the High Priest is dead or that player has Recruited him
> anew as a normal High Priest).
> This is not a physical product. They are presented below, or you may download the eight Unique High
> Priests from www.PetersenGames.com.»

FAQ (Tcho-Tcho): «the Unique High Priest acts as your other two “regular” High Priests in every way, EXCEPT
that it cannot use the normal Unspeakable Oath ability. High Priests can only use the abilities on their own
Loyalty Cards.»

KS-O2-30 (замысел): «The special characters are each more powerful, but less flexible, than the usual High
Priest.» Ранний состав восьмёрки в апдейте: Asenath Waite, Crawford Tillinghast, Ermengarde Stubbs, Herbert
West, Lady de la Poer, Lavinia Whateley, Pitpipo, Wizard Eibon. В рулбук вошли Joseph Curwen и Keziah Mason
вместо Lady de la Poer и Wizard Eibon.

---

## 2. Восемь официальных карт (RB-OLD с. 144–147, дословно)

У всех: **Cost: 3, Combat: 0.**

**Asenath Waite** — *The Thing from Beyond (Ongoing):* «After any player’s Action, choose any enemy Monster
or Cultist on the Map and replace it with one of your own Units costing 3 or less (except Asenath Waite),
then Eliminate Asenath Waite.»

**Crawford Tillinghast** — *The Ultra-Violet (Pre-Battle):* «Before any Battle (even if Crawford
Tillinghast is not involved), you may Eliminate Crawford Tillinghast and place Monsters and/or Cultists with
a total Power cost of up to 3 from your Pool into the Battle Area, off to one side. These Units participate
in the Battle, and can use any Pre-Battle or Post-Battle abilities they may have. After the entire Battle is
resolved, Eliminate any surviving “extra” Units.»
Вики — сокращённо, без двух последних предложений.

**Ermengarde Stubbs** — *A Simple Rustic Maid (Ongoing):* «Any player (including you) who declares a Battle
in Ermengarde Stubbs’ Area immediately loses 1 Doom.»

**Herbert West** — *The Reanimator Serum (Ongoing):* «After any player’s Action, you may Eliminate Herbert
West and place up to 3 Acolyte Cultists from your Pool into the Area from which Herbert West was removed.»

**Joseph Curwen** — *Beyond the Spheres (Ongoing):* «After any player’s Action, you may Eliminate Joseph
Curwen and either remove your Controlled Gate (but not its Controller) from anywhere on the Map, or place a
new Gate in any Area in which you have a Unit.»

**Keziah Mason** — *Daemon Heroine (Post-Battle):* «If Keziah Mason is assigned a Kill or Pain result, add
2 Kills or 2 Pains, respectively, to the total scored against the opponent.»

**Lavinia Whateley** — *The Bride (Ongoing):* «When you Awaken a Great Old One, you can choose to Eliminate
Lavinia Whateley. If you do so, your Great Old One costs 3 fewer Power to Awaken.»

**Pitpipo** — *The Pit of Despair (Post-Battle):* «When you take a Kill in Battle, you can assign it to
Pitpipo even if he was not involved in the Battle.»

---

## 3. Официальные уточнения

### 3.1. FAQ (раздел Unique High Priests; RB-NEW с. 196)

> **Q.** If I Awaken The King in Yellow (as an Independent Great Old One) via Lavinia Whateley, do I get a
> refund of 1 Power? **A.** Yes

> **Q.** When I have Lavinia Whateley, how do I calculate Awakening Cthugha?
> **A.** Lavinia Whateley reduces the cost to Awaken Cthugha himself, not whichever Great Old One Cthugha will
> replace as part of Awakening him. […] The result would be negative 7. Then, per Cthugha’s Awakening
> requirements, you would gain Power equal to the result if it is negative, so you would GAIN 7 Power […]

> **Q.** When I use Asenath Waite’s The Thing From Beyond, where does my replacement Unit come from?
> **A.** Your Pool.

### 3.2. Пример битвы 9 (RB-NEW с. 35–36) — Keziah Mason

> «Joey assigns this result to Keziah Mason. With a Kill assigned to Keziah Mason, her Daemon Heroine ability
> triggers. This will add 2 Kill results against Alex. […] the Snakebite ability that triggered an extra Kill
> on Joey has already taken place, so it is not removed from Keziah Mason; otherwise a paradox would occur!
> Post-Battle abilities that are triggered can modify how results are assigned, but do not retroactively
> prevent other Post Battle abilities […] from having taken place.»

### 3.3. Ответы Петерсенов (BGG-1671563, пост 27245737, 2017-10-24, дословно)

> «I got answers to my questions from the Petersens and I will share them with you»

- *Asenath:* «The Unit you replace an enemy Unit with is supposed to come from Another Area on the Map, not
  from your your Unit Pool right?» — «No. It comes from your unit pool. It is totally a new free unit. So you
  kill his unit and get your own free one.»
- *Asenath:* «does the replaced monster/cultist end up in its owner’s Pool, or to the other Unit’s starting
  Area?» — «It is eliminated and returns to its pool.»
- *Crawford:* «These Mosters can use their Pre-Battle abilities normally if you are the attacking Faction,
  correct?» — «Of course, or even if you are the defender, because the unit replacement happens BEFORE the
  battle, so Pre-Battle follows it.»
- *Curwen:* «Could you use “Beyond the Spheres” to remove the Gate Curwen is controlling?» — «Certainly»
- *Pitpipo:* «Is he supposed to be considered as “potentially present” in terms of assigning Kills, or is he
  to be a Unit to which you can “redirect” an already-assigned Kill?» — «He is a unit to which you can
  redirect an already assigned kill.»
- *Pitpipo, пример:* три ваших отряда в регионе, Pitpipo в другом, противник выбросил четыре смерти. «Can you
  have two of your Units and Pitpipo Killed, by first assigning the three Kills (the fourth being ignored as
  targetless) and then redirecting one of these three to Pitpipo?» — «The former.»

### 3.4. Мнения игроков без официального ответа

- BGG-1671563 (2016): Asenath сочли слишком сильной — «The major problem is the ability to get a gate
  everytime, so excluding Cultists would solve this». То есть заменой пехотинца на фабрике игроки забирают
  фабрику. Официально не подтверждено и не опровергнуто.
- BGG-1719427 (2017): Asenath нельзя «перепризвать» её же способностью, обычной вербовкой — можно.

---

## 4. Три фанатские карты (BGG-3316625, Papa_Tom, 2024-06-12)

Автор: «I've been using some extra Unique High Priests for a little while to incorporate yet even more
Lovecraftian themes into the game.» Карты печатает в формате Tarot.

**Albert Shiny** — Cost 3, Combat 0. *Shoggoth Form (Pre-Battle):* «You may pay up to 4 Power to increase
Ablert Shiny’s Combat by that amount for the duration of the Battle. When Battle results are assigned,
Albert Shiny receives the first Kill or Pain, in that order.»
Замысел: «revert to his violent and unstable Shoggoth form when faced with a threat, which recklessly (and
hungrily) throws itself into battle... and absorbs the first blow of the fight.»

**Nahum Gardner** — Cost 3, Combat 0. *Corrosion (Action: Cost 1):* «Sacrifice Nahum Gardner (return him to
your Pool) and up to 3 Power Cost worth of your Cultists, Monsters, or Terrors from the Map to gain their
total Power cost (for example, if you sacrifice Nahum Gardner and 2 Acolyte Cultists, you gain 5 Power). If a
Unit has a variable Cost (like Windwalker’s Gnoph-Keh), then you gain the amount of Power it would currently
cost to Summon/Recruit.»

**Henry Akeley** — Cost 3, Combat 0.
*Surgery (Action: Cost 1):* «Eliminate up to 4 of your Cultists in play and replace them with an equal number
of Brain Cylinder tokens in your Faction’s Color. You must place these Brain Cylinders in the same Area(s) as
the Cultists they replace—they can replace your Cultists on Gates, immediately retaking Control of those
Gates.»
*Duplicitous (Ongoing):* «Henry Akeley (unlike other Unique High Priests) may be Recruited by any player after
he is Killed or Eliminated.»
Замысел: «essentially a mobile Surgery Laboratory with the same abilities, but with a second special ability
to put a reasonable limiter on any one player hogging him for the whole game.»

---

## 5. Соответствие «наш полковник ↔ оригинал»

| № | Наш полковник | Оригинал | Способность |
|---|---|---|---|
| 1 | Герберт Морроу | Asenath Waite | The Thing from Beyond |
| 2 | Сигэру Исии | Crawford Tillinghast | The Ultra-Violet |
| 3 | Амелия Кейн | Ermengarde Stubbs | A Simple Rustic Maid |
| 4 | Кассия Рэйвен | Herbert West | The Reanimator Serum |
| 5 | Бато Распутин | Keziah Mason | Daemon Heroine |
| 6 | Эвелин Тайрелл | Lavinia Whateley | The Bride |
| 7 | Джон Крамер | Pitpipo | The Pit of Despair |
| 8 | Роберт Клоуз | Joseph Curwen | Beyond the Spheres |
| 9 | Виктор “Шайн” Ковач | Albert Shiny (фанатский) | Shoggoth Form |
| 10 | Ной Гарднер | Nahum Gardner (фанатский) | Corrosion |
| 11 | Генри Брут | Henry Akeley (фанатский) | Surgery, Duplicitous |

Набор «Investigators» (Onslaught 3, восемь карт) и карты The Eidolon / The Prophetess к нашим полковникам
отношения не имеют: их тексты — другие (RB-OLD с. 153–162).

## 6. Не найдено

- PDF восьми карт UHP с PetersenGames.com, на который ссылается рулбук. Тексты есть в RB-OLD — PDF
  не нужен для сверки, только если захочется сравнить вёрстку карт.
- Картинки фанатских карт из BGG-3316625 (вложения 8257787, 8257770, 8229325, 8257789, 8241481, 8257788,
  8257772, 8257771) — текст поста их дублирует.
