# Исследование Elder God — рабочие таблицы сверки

**Дата:** 01.10.2026 · **К чему:** `rules/tasks/ИССЛЕДОВАНИЕ-Elder-God.md` · **Статус:** рабочий материал

Три таблицы собраны агентами-исследователями по отдельности и не вычитаны построчно.
Выводы основного файла проверены по первоисточникам; таблицы — нет. Если строка таблицы
расходится с основным файлом, верен основной файл. При сомнении — сверять с первоисточником
по указанной странице.

## Поправки к таблицам

1. **Таблица 1, BU-08 / FAQ-12** («p.183 говорит о flat 4 Doom, p.184 — о 3 Elder Signs, какая
   награда верна — не установить»). Противоречия нет: Doom и Elder Signs — разные награды.
   Requires Attention даёт ровно 4 Doom плюс 1 знак за вражескую фабрику и 2 знака
   за вражеского GOO; Yog-Sothoth считается и тем и другим, итого 3 знака.
2. **Таблицы 1 и 2, «Elder Gods cannot declare Battle — первоисточник не найден».** Найден:
   встроенный FAQ рулбука, `SRC-RB-NEW` с. 182.
3. **Таблица 3, A10 / B6** («Альтернативные источники энергии»: даёт ли нефть сам Bastet).
   К вопросу типа не относится; планшет сверен с оригиналом в `D-052`.
4. **Таблица 3, F3** (`STATE.md` требует напечатать на планшете «не объявляет битву»).
   Печатать не нужно: запрет следует из общего правила §7.3.6 («сила не менее 1… даже если
   у ваших отрядов есть боевые эффекты») и силы 0 в таблице.

Страницы `SRC-RB-NEW` в таблицах — печатные номера; маркер «## Страница N» в .md больше на 5.

---

# Таблица 1. Оригинал: ядро правил, 12 фракций, FAQ


Дата: 2026-10-01. Аудит под вопрос «где слитная модель (Bastet = обычный GOO, Combat 0 + отдельная
способность “+1 Kill даже без кубиков; −1 Kill (не Pain) из выброшенного противником” + локальная
пометка “не даёт Elder Sign за ритуал”) ведёт себя иначе, чем Elder God оригинала».

### Условные обозначения

**Источники.**
- `RB-NEW p.N (Стр M)` — `SRC-RB-NEW__cw-rulebook-new-layout__2026-09-10.md`; p. — печатный номер, Стр — маркер в .md. Смещение постоянное: печатная = Стр − 5.
- `RB-OLD p.N (Стр M)` — `SRC-RB-OLD__cw-rulebook-old-layout__2026-09-10.md`.
- `ERR-PACK стр.N` — `SRC-ERRATA-PACK__cards-text…` / `…ultimate-errata-pack…`; `BAL` — таблицы балансных правок.
- `FAQ-ONLINE` — `SRC-FAQ__cw-rules-faq__2026-09-10.md` (freshdesk).
- `WIKI` — `SRC-WIKI__faction-units-and-components__2026-09-11.md`.
- `REG/factions.yaml`, `REG/mercenaries.yaml` — проектные реестры (`rules/registry/`): русский пересказ faction card с картинок вики и английские тексты карт лояльности. **Вторичный источник**, применён только там, где в корпусе нет английского текста карты.
- `BGG:<тред>` — выписки тредов BGG (community, низкое доверие).

**Важное ограничение корпуса.** Тексты faction card (способности фракций и GOO, spellbooks, требования spellbooks) в RB-NEW **текстом не извлечены** — это картинки (пустые Стр 50, 55–56, 60, 64, 71–72, 77–78, 83–84, 88, 92, 98, 102). В RB-OLD от них остались искажённые обрывки. Английские тексты взяты из: версий фракционных GOO как Independents (RB-OLD p.115–119), ERR-PACK, FAQ, страниц стратегии; остальное — пересказ реестра (помечено). Списки требований spellbooks у Sleeper, Windwalker, Daemon Sultan, Bubastis, Ancients, Tcho-Tcho **полностью не проверены** — в корпусе их нет.

**Категории:** RITUAL / COMBAT / EXPLICIT-EG / COUNT-TARGET / OTHER.

**Вердикт «слитная модель даёт тот же результат?»:** YES / NO / DEPENDS.

**Опорное правило (RB-NEW p.70, Стр 75):** «Bastet is an Elder God; these beings are treated as Great Old Ones for all purposes except: they do not provide an inherent Elder Sign for a Ritual of Annihilation, though they often have other means of creating Elder Signs; and Elder Gods never roll Combat dice, but provide some fixed benefit. They do count as equal to Great Old Ones otherwise, so they can block Unit Captures. Nyarlathotep gets 2 Elder Signs or half-Power cost from his Harbinger ability compared with that of other Great Old Ones. You can use them to Capture Cultists even if an enemy Monster is present, and so forth.» Далее — «p.70».

---

### A. Ядро правил

| ID | Источник | Цитата | Кат. | Elder God в оригинале (что решает) | Слитная модель |
|---|---|---|---|---|---|
| CORE-01 | RB-NEW p.9 (Стр 14) | «Each Faction has 3 categories of Units: Cultists, Monsters, and Great Old Ones… Great Old Ones are individual beings, and thus every single Great Old One has a unique name» | OTHER | Четвёртой категории не образует: «treated as Great Old Ones for all purposes» (p.70) | YES — Bastet просто GOO |
| CORE-02 | RB-NEW p.9 (Стр 14) | «Monsters and Great Old Ones cannot Control Gates, and they may never be placed on top of them» | COUNT-TARGET | Как GOO (p.70) | YES |
| CORE-03 | RB-NEW p.10 (Стр 15) | «Each Great Old One has its own unique ability, available while that Great Old One is in play and described on each Faction Card» | OTHER | Requires Attention действует, пока Bastet в игре | YES. Оговорка: в слитной модели боевой эффект Bastet тоже становится «способностью» — значимо только для внешних эффектов, гасящих способности GOO (см. PTR-01) |
| CORE-04 | RB-NEW p.11 (Стр 16); p.13 (Стр 18) | «Elder Sign Trophies symbolize the shattering of the bonds that once held the Great Old Ones in check»; «The Action Phase is where the Great Old Ones destroy the world» | OTHER | флейвор | YES |
| CORE-05 | RB-NEW p.12 (Стр 17) | «G. Great Old One Information: Shows your Great Old One’s silhouette, Cost, and Combat rating, plus notes… describe how to Awaken that Great Old One, provide its Combat formula (if any), and describe its special ability.» | COMBAT | У Bastet в графе Combat «*» и текст фикс. эффекта (WIKI; карта — картинка) | YES — «0 + способность» передаёт то же; «(if any)» допускает GOO без формулы |
| CORE-06 | RB-NEW p.14 (Стр 19) | «The Awaken Great Old One Action allows you to bring your Great Old One into play… You may only Awaken a single Great Old One per Awaken Action… If your Great Old One leaves play, its ability will not be available to you until the Great Old One has been Awakened once again.» | COUNT-TARGET | Bastet пробуждается этим действием (как GOO) | YES |
| CORE-07 | RB-NEW p.14 (Стр 19), Tips | «Since a Great Old One can be “Killed” (after which it must be re-Awakened), do not bring it out before you can protect it… Two exceptions are the King in Yellow and Cthulhu» | OTHER | — | YES |
| CORE-08 | RB-NEW p.14 (Стр 19) | Recruit Cultist: «One of your Units must be in the Area… This Unit can be of any type (another Cultist, a Monster, or even a Great Old One).» | COUNT-TARGET | Как GOO (у Bubastis Acolytes нет — практически не применяется) | YES |
| CORE-09 | RB-NEW p.15 (Стр 20) | «Battle Cost: 1 Power (Requires Unit with at least 1 Combat)… You must have at least 1 Combat on your side in order to declare a Battle. You may Battle an enemy who has 0 Combat.» | COMBAT | Сама объявить бой не может: FAQ p.182 «Can Elder Gods declare Battle since they have no Combat dice? A. No.» Атакована быть может | YES — Combat 0 даёт тот же запрет. Расхождение возможно только если какой-то эффект добавит Combat GOO/«всем отрядам»: в ядре и 12 фракциях такого эффекта нет (проверено, см. итог) |
| CORE-10 | RB-NEW p.16 (Стр 21) | «To Capture an enemy Cultist, you must have a Monster or Great Old One in the same Area… Great Old Ones outrank Monsters, which in turn outrank Cultists. A Great Old One can Capture an enemy Cultist, unless the target is protected by its own Great Old One in the Area. A Monster can capture… unless the target is protected by its own Monster (or Great Old One).» | COUNT-TARGET | Прямо p.70: «can block Unit Captures… Capture Cultists even if an enemy Monster is present» | YES |
| CORE-11 | RB-NEW p.16 (Стр 21) | «Your Monster or Great Old One will never protect another Faction’s Cultist… Only Monsters and Great Old Ones from a Cultist’s Faction can protect it.» | COUNT-TARGET | Как GOO | YES |
| CORE-12 | RB-NEW p.16 (Стр 21), Note | «Even if… a Capturing Monster has a Combat of 0, the Cultist can still be Captured. Capture is not Battle, and Battle abilities do not apply.» | COMBAT | Захват не зависит от Combat | YES |
| CORE-13 | RB-NEW p.17–18 (Стр 22–23), пример | «Rich must Move his Cultist out of the Area, Move his own Great Old One into the Area, or drive away or Kill Cthulhu in a Battle.» | COUNT-TARGET | Как GOO | YES |
| CORE-14 | RB-NEW p.21 (Стр 26) | «Non-Cultist Units such as Monsters and Great Old Ones do not produce Power (with rare exceptions).» | COUNT-TARGET | Bastet Power не даёт (1 Power дают только кошки — WIKI) | YES |
| CORE-15 | RB-NEW p.22 (Стр 27) | Ritual, шаг «4. Gain one Elder Sign for each of your Faction Great Old Ones in play.» | RITUAL | Исключение p.70: «do not provide an inherent Elder Sign»; FAQ p.183 | YES при локальной пометке. Формулировка пометки — см. BU-07 (DEPENDS) |
| CORE-16 | RB-NEW p.22 (Стр 27), пример | «…receives an Elder Sign for Nyarlathotep, his Great Old One.» | RITUAL | — | YES |
| CORE-17 | RB-NEW p.23 (Стр 28) | «The Faction initiating the Battle must have at least 1 Combat among its Units in the Area.» | COMBAT | см. CORE-09 | YES |
| CORE-18 | RB-NEW p.23 (Стр 28) | «Each Unit has a Combat rating… Some have 0 Combat, and some require a simple calculation (such as Yellow Sign’s Monsters, or many Great Old Ones). Your Faction’s Combat in the Battle is equal to the sum of the Combat rating of all of your Units» | COMBAT | Bastet в сумму кубиков не входит; «never roll Combat dice, but provide some fixed benefit» (p.70) | YES — 0 в сумму + способность. Эквивалентно, пока нет эффекта, который ссылается на «Combat» Bastet как на её фикс. эффект (единственный такой в объёме — Zagazig, BU-09) |
| CORE-19 | RB-NEW p.23 (Стр 28) | «Both sides then roll a number of dice equal to their individual Combat totals.» | COMBAT | кубиков не добавляет | YES |
| CORE-20 | RB-NEW p.24 (Стр 29) | «Opener of the Way’s Channel Power Spellbook allows him to re-roll dice that did not roll a Kill or Pain result.» | COMBAT (переброс) | перебрасывает только свои кубики | YES |
| CORE-21 | RB-NEW p.25 (Стр 30), пример | «…while her Cultists and the King have Combat ratings of zero, she rolls 3 dice.» | COMBAT | **Прецедент:** в оригинале уже есть GOO с напечатанным Combat 0 — King in Yellow; при этом он даёт ES за ритуал | YES |
| CORE-22 | RB-NEW p.26 (Стр 31), пример | «Angela chooses an Undead to be Devoured because her King In Yellow is a Great Old One and therefore cannot be chosen.» | COUNT-TARGET | Devour по GOO невозможен → Bastet иммунна | YES |
| CORE-23 | RB-NEW p.29 (Стр 34), пример | «Berserkergang… Eliminates an enemy Monster or Cultist… (…and Shub-Niggurath is a Great Old One).» | COUNT-TARGET | иммунна | YES |
| CORE-24 | RB-NEW p.30 (Стр 35), пример | «…(since Cthugha, a Great Old One, is immune).» | COUNT-TARGET | иммунна | YES |
| CORE-25 | RB-NEW p.32 (Стр 37), пример | «Bill has no Combat; Bruce rolls a single Pain. Bill assigns this Pain to his Undead, to prevent Bruce from gaining any benefit for Paining a Great Old One (via Harbinger).» … «Bruce decides to gain 2 Elder Signs» | COUNT-TARGET | Сторона с 0 Combat обороняется; Harbinger по EG — p.70 | YES |
| CORE-26 | RB-NEW p.37 (Стр 42) | «All Great Old Ones, Monsters, and evil Cultists are sucked back…»; Tips: «Be choosy about when you Awaken your Great Old One»; «…your Great Old One is in play» | OTHER | — | YES |
| CORE-27 | RB-NEW p.39 (Стр 44), 2 игрока | «When a Unit is Eliminated or Killed, the opposing player gains Doom equal to that Unit’s Power cost!… Units which are able to avoid death… still provide Doom… but only half as much» | COUNT-TARGET | Bastet стоит 6 → 6 Doom; от категории не зависит. (Bubastis vs Crawling Chaos в 2P запрещено, p.70) | YES |
| CORE-28 | RB-NEW p.40 (Стр 45), 2 игрока | «The Ritual of Annihilation still produces Doom equal to your Controlled Gates (plus an Elder Sign for each of your Faction Great Old Ones in play).» | RITUAL | как CORE-15 | YES (при пометке) |
| CORE-29 | RB-NEW p.40 (Стр 45), 2 игрока | «Yog-Sothoth’s Combat is always 4.» | COMBAT (задание значения) | Формула Yog заменена константой; Bastet не участвует | YES |
| CORE-30 | RB-NEW p.40 (Стр 45) | Tip «Keeping your Great Old One alive is even more important…»; Note «Windwalker may fulfill his “Another Faction has 6 Spellbooks” requirement by sacrificing Ithaqua» | OTHER | — | YES |
| CORE-31 | ERR-PACK стр.14 (памятка) | «-1 Power to Battle (requires Unit with at least 1 Combat)»; «-? Power to Awaken 1 Great Old One»; «+1 Elder Sign per Faction Great Old One» | COMBAT / RITUAL | как CORE-09, CORE-15 | YES |
| CORE-32 | RB-NEW p.109 (Стр 114), правила Independents (перекрёстно) | «ONLY Faction Great Old Ones provide Elder Signs when you perform a Ritual of Annihilation. (Great Cthulhu still gets an Elder Sign when Awakening any Great Old One, however).» | RITUAL | Bastet — фракционный, но частное правило p.70 снимает ES за ритуал | YES (при пометке) |

---

### B. Разделы фракций (12 разделов компендиума: 4 ядра + Ancients, Bubastis, Daemon Sultan, Opener, Sleeper, Tcho-Tcho, Tcho-Tcho Tribes, Windwalker)

#### B1. Great Cthulhu

| ID | Источник | Цитата | Кат. | Elder God в оригинале | Слитная модель |
|---|---|---|---|---|---|
| GC-01 | WIKI; RB-NEW p.44 (Стр 49) | Cthulhu: Cost 10 (затем 4), Combat 6; «Cthulhu only rolls six dice» | COMBAT | своё | YES |
| GC-02 | RB-NEW p.109 (Стр 114); p.44 (Стр 49); FAQ p.187 | Immortal: «Great Cthulhu still gets an Elder Sign when Awakening any Great Old One»; «you can re-Awaken him cheaply and gain an Elder Sign» (текст карты в корпусе отсутствует) | RITUAL | ES при пробуждении любого GOO — только для Great Cthulhu; Bastet не пробуждает | YES |
| GC-03 | RB-OLD p.116 (Стр 126); RB-NEW p.26 (Стр 31) | Devour: «Your enemy chooses and eliminates one of his own Monsters or Cultists from the Battle Area.» | COUNT-TARGET | GOO не цель → Bastet иммунна | YES |
| GC-04 | RB-NEW p.11 (Стр 16); p.44 (Стр 49); FAQ p.189–190 | «Great Cthulhu’s requirement that demands a Devour and/or Kill in Battle»; «your two “Kill/Devour” Spellbooks» | COUNT-TARGET | Kill по Bastet засчитывается (как любой Kill) | YES |
| GC-05 | RB-NEW p.44 (Стр 49) | «Cthulhu accompanied by two Starspawn is well-armored against even enemy Great Old Ones.» | OTHER | — | YES |
| GC-06 | RB-NEW p.44 (Стр 49) | «Killing Cthulhu himself isn’t particularly effective (unless you are Crawling Chaos, since Harbinger then gives you two Power or Elder Signs)» | COUNT-TARGET | — | YES |
| GC-07 | RB-NEW p.44 (Стр 49); p.26 (Стр 31) | Absorb: «Turns Shoggoths into major Combat dice»; пример «2 + 3 for the “Absorbent” Shoggoth» | COMBAT (прибавка) | Прибавка только Shoggoth, поглощает только Monster/Cultist | YES |

#### B2. Yellow Sign

| ID | Источник | Цитата | Кат. | Elder God в оригинале | Слитная модель |
|---|---|---|---|---|---|
| YS-01 | WIKI; RB-NEW p.48 (Стр 53) | King in Yellow Combat 0; Hastur Combat = текущая стоимость ритуала; «The King in Yellow, despite its lack of Combat, is a nightmare» | COMBAT | KiY — штатный GOO с Combat 0 | YES |
| YS-02 | RB-NEW p.48 (Стр 53) | «you must rely on Third Eye or your two Great Old Ones for Elder Signs» | RITUAL | Два фракционных GOO → 2 ES за ритуал; у Bastet 0 | YES |
| YS-03 | RB-NEW p.48 (Стр 53); RB-OLD p.115 (Стр 125) | «Thanks to Vengeance, you can ensure the death of an enemy Great Old One once Hastur rolls into action»; Vengeance: «If Hastur is involved in a Battle, you choose which Combat results are applied to which enemy Units. For instance, you could apply a Kill to a particular enemy Great Old One involved in that Battle.» | COUNT-TARGET | Kill назначается Bastet | YES |
| YS-04 | RB-NEW p.48 (Стр 53) | He Who is Not to be Named: «The basic function is to assassinate an opposing Great Old One»; «declare Battle… to assassinate any other Great Old One» | COUNT-TARGET | — | YES |
| YS-05 | RB-NEW p.48 (Стр 53); p.49 (Стр 54) | «…give some ‘oomph’ to your Great Old Ones»; «Third Eye is terrifying, but they need both of their Great Old Ones out» | OTHER | своё | YES |

#### B3. Crawling Chaos

| ID | Источник | Цитата | Кат. | Elder God в оригинале | Слитная модель |
|---|---|---|---|---|---|
| CC-01 | WIKI; RB-NEW p.54 (Стр 59) | Nyarlathotep: Combat = faction spellbooks своих и противника; «a huge combat ability (up to twelve dice)» | COMBAT | Против Bubastis считает её spellbooks; от Bastet не зависит | YES |
| CC-02 | RB-OLD p.117 (Стр 127); RB-NEW p.54 (Стр 59); p.70 | Harbinger: «If Nyarlathotep is in a Battle in which one or more enemy Great Old Ones are Killed or Pained, receive Power equal to half of the cost of Awakening those Great Old Ones. For each enemy Great Old One so affected, you may choose to receive 2 Elder Signs instead of Power.»; «Smite enemies’ Great Old Ones for the Harbinger bonus» | EXPLICIT-EG / COUNT-TARGET | p.70 прямо: Bastet = 2 ES или половина стоимости (6/2 = 3 Power) | YES |
| CC-03 | RB-NEW p.54 (Стр 59); FAQ p.181 | Emissary of the Outer Gods: «Less useful when Great Old Ones are out»; FAQ «…when he has Emissary of the Outer Gods and is not Battling an enemy Great Old One» (текст карты в корпусе нет) | COUNT-TARGET | Bastet в бою = «enemy GOO» → Emissary не защищает | YES |

#### B4. Black Goat

| ID | Источник | Цитата | Кат. | Elder God в оригинале | Слитная модель |
|---|---|---|---|---|---|
| BG-01 | ERR-PACK стр.5; BAL (O2) | The Red Sign: «Each Dark Young adds 1 to Shub-Niggurath’s Combat»; формула Shub = Gates + Cultists (WIKI) | COMBAT (прибавка конкретному GOO) | Только Shub | YES |
| BG-02 | RB-OLD p.116 (Стр 126); BGG:Compilation | Avatar: «Swap the location of Shub-Niggurath with that of a Monster or Cultist in the chosen Area, chosen by the Faction owner.»; BGG «Can Avatar be used on a Great Old One or an empty Area? A: No.» | COUNT-TARGET | Bastet не цель | YES |
| BG-03 | RB-OLD Стр 12 (обрывки карты) | Blood Sacrifice: «If Shub-Niggurath is in play during the Doom Phase, you can choose to Eliminate one of your Cultists (from anywhere on the map). If you do, gain 1 Elder Sign.» | RITUAL | своё | YES |
| BG-04 | RB-NEW p.25 (Стр 30) | Frenzy: «his Cultists each have a Combat of 1» | COMBAT (прибавка) | Только Cultists | YES |
| BG-05 | RB-NEW p.58 (Стр 63) | «all three of the other Factions can pull this off with proper use of their Great Old Ones» | OTHER | — | YES |

#### B5. The Ancients

| ID | Источник | Цитата | Кат. | Elder God в оригинале | Слитная модель |
|---|---|---|---|---|---|
| AN-01 | RB-NEW p.64 (Стр 69) | «Uniquely, they are not led by a Great Old One»; «Because you don’t have any Great Old Ones…»; «Your great weaknesses are that you have no Great Old Ones» | OTHER | — | YES |
| AN-02 | RB-NEW p.64 (Стр 69) | «with Yothans, you have more Combat dice than any Great Old One» | OTHER | — | YES |
| AN-03 | RB-NEW p.64 (Стр 69); BGG:Ancients Unholy Ground (текст карты) | «Unholy Ground can protect you if your foes go for early Great Old One strategies»; карта: «If there is a Cathedral in the Battle Area, you may choose to remove a Cathedral from anywhere. If you do, an enemy Great Old One in the Battle must be Eliminated by its owner.» | COUNT-TARGET | Bastet устраняема | YES |
| AN-04 | REG/factions.yaml; BGG:Ancients question | 4 Cathedrals заменяют «свой GOO» в условии пробуждения Independent | COUNT-TARGET | n/a | YES |

#### B6. Bubastis

| ID | Источник | Цитата | Кат. | Elder God в оригинале | Слитная модель |
|---|---|---|---|---|---|
| BU-01 | RB-NEW p.70 (Стр 75) | «Bastet is an Elder God; these beings are treated as Great Old Ones for all purposes except: …» | EXPLICIT-EG | базовое правило | YES — слитная модель и есть «GOO для всех целей» |
| BU-02 | RB-NEW p.70 | «…they do not provide an inherent Elder Sign for a Ritual of Annihilation, though they often have other means of creating Elder Signs» | EXPLICIT-EG / RITUAL | снят только «inherent» ES шага 4 | YES при пометке; DEPENDS по формулировке — см. BU-07 |
| BU-03 | RB-NEW p.70 | «…and Elder Gods never roll Combat dice, but provide some fixed benefit.» | EXPLICIT-EG / COMBAT | 0 кубиков при любых обстоятельствах + фикс. эффект | YES в объёме (нет эффектов, добавляющих Combat GOO). Структурный риск: «never» ≠ «0» при внешних прибавках — см. PTR-03 |
| BU-04 | RB-NEW p.70 | «They do count as equal to Great Old Ones otherwise, so they can block Unit Captures… You can use them to Capture Cultists even if an enemy Monster is present» | EXPLICIT-EG / COUNT-TARGET | — | YES |
| BU-05 | RB-NEW p.70 | «Nyarlathotep gets 2 Elder Signs or half-Power cost from his Harbinger ability compared with that of other Great Old Ones.» | EXPLICIT-EG | — | YES |
| BU-06 | RB-OLD p.71 (Стр 81) | Старая вёрстка: «…treated as Great Old Ones for all purposes except they do not provide an inherent Elder Sign… Elder Gods never roll Combat dice, but provide some fixed benefit.» | EXPLICIT-EG | В старой вёрстке исключением формально названо только ES, «never roll» — отдельной фразой; в новой оба под «except:» | YES, смысл не меняется |
| BU-07 | RB-NEW FAQ p.183 (Стр 188) | «Do I get an Elder Sign for Ritualing with Bastet if I’m not using her Requires Attention ability? A. No. Elder Gods do not provide Elder Signs for Rituals of Annihilation, except in conjunction with special abilities. Also, since Bubastis can only “Control” one Gate (the Moon), a non-Requires Attention ritual only ever adds 1 Doom. Finally, if you DO use the Requires Attention ritual, you do NOT add another 1 Doom for the Moon’s “Gate.” You only get the flat 4 Doom bonus. Really, it’s Bastet adding 3 Doom, plus the 1 extra for the Moon» | EXPLICIT-EG / RITUAL | Свой ES нет; ES/Doom через спецспособность — да | **DEPENDS** — пометка «не даёт Elder Sign за ритуал» совпадает, только если она снимает именно базовый ES шага 4, а не всякий ES при ритуале. Абсолютная формулировка погасит награду, которую оригинал даёт «in conjunction with special abilities» (Requires Attention, BU-08) |
| BU-08 | RB-NEW FAQ p.184 (Стр 189) | «If Bastet is in an area with Yog-Sothoth, and you ritual, do you get 3 Elder Signs? A. Yes. But the presence of another Enemy Controlled Gate does not increase this reward.» | EXPLICIT-EG / RITUAL | Requires Attention срабатывает и от Yog-Sothoth как вражеских врат; награда фиксирована | **DEPENDS** — как BU-07. Плюс неясность самого оригинала: BU-07 говорит о «flat 4 Doom», BU-08 — о «3 Elder Signs»; текста карты Requires Attention в корпусе нет |
| BU-09 | RB-NEW p.71 (Стр 76); FAQ p.183 (Стр 188); FAQ p.192 (Стр 197) | Zagazig: «Makes your Cats from Mars really mean. Also note that it does not affect Bastet’s Combat. It does affect the enemy’s die rolls too»; FAQ «If you choose to use Zagazig, both sides get the benefits»; «First, Zagazig swaps all rolled Kills and Pains. Then apply Bloodthirst» | EXPLICIT-EG / COMBAT | Фикс. эффект Bastet называется её «Combat» и обменом Kill↔Pain не затрагивается | **DEPENDS** — в слитной модели +1 Kill — способность, не Combat. Совпадёт, если аналог Zagazig меняет только выброшенные (rolled) результаты и прописан порядок «обмен → −1 Kill Bastet» (или обратный). Порядок «−1 к вражеским Kill» относительно обмена не определён и в оригинале |
| BU-10 | RB-NEW FAQ p.183 (Стр 188) | «If Bastet is in a Battle by herself, does she still get to inflict her one Kill…? A. Yes, of course. Elder Gods just inflict results. They don’t roll dice, and they don’t require dice to be rolled for their results to take place. Also, if Bastet is alone, she also still gets her ability to reduce the enemy-rolled Kills by 1.» | EXPLICIT-EG / COMBAT | — | YES — текст способности «even if no dice were rolled» |
| BU-11 | RB-NEW FAQ p.182 (Стр 187) | «Can Elder Gods declare Battle since they have no Combat dice? A. No.» | EXPLICIT-EG / COMBAT | — | YES (Combat 0 → CORE-09) |
| BU-12 | WIKI; REG/factions.yaml (карта — картинка) | Bastet: Cost 6, Combat «*»: кубиков не бросает, +1 Kill к результату, противник снимает 1 Kill. Пробуждение: все 4 вида кошек в игре, 6 Power, область без вражеских отрядов | EXPLICIT-EG / COMBAT | — | YES |
| BU-13 | RB-NEW p.70 (Стр 75) | «The Moon counts as a land Area with a Bubastis-Controlled Gate for all purposes, except that Control may not be seized» | COUNT-TARGET | Bastet на Луне = «Controlled Gate + свой GOO» (условие пробуждения Independent, ср. FAQ p.186) | YES |
| BU-14 | RB-OLD p.68 (Стр 78) | Savagery: «Pay 1 power in Pre-Battle to increase the combat of all Cats from Saturn by 4 for this battle.» | COMBAT (прибавка) | Только Cats from Saturn | YES |
| BU-15 | RB-OLD p.68 (Стр 78) | Predator: «If a Cat from Uranus was in the battle, you can select one unit lost by the enemy. He must eliminate a second unit of that type anywhere on the map, if possible.» | COUNT-TARGET | Если враг потерял GOO, «unit of that type» неоднозначно (категория или конкретный юнит); к Bastet не относится | YES (неоднозначность общая) |
| BU-16 | RB-OLD p.68 (Стр 78); RB-NEW p.71 (Стр 76) | Ailurophobia: «Score one Doom per different cat variety on the map outside of the Moon.» | OTHER | Считается ли Bastet «видом кошки» — не сказано; от категории EG/GOO не зависит | YES |

#### B7. Daemon Sultan

| ID | Источник | Цитата | Кат. | Elder God в оригинале | Слитная модель |
|---|---|---|---|---|---|
| DS-01 | WIKI | Три Аватара — GOO; стоимость/Combat от маркера Azathoth; Synthesis бросает кубик Azathoth; Larva Combat 2, если в игре её Аватар | COMBAT | своё | YES |
| DS-02 | RB-NEW p.76–77 (Стр 81–82) | «get your second Great Old One out early»; «later your three Great Old Ones help you surge ahead»; «if you can manage to perform Rituals, you can get up to 3 Elder Signs each time»; «takes him at least three turns and 19 Power to set up all his Great Old Ones»; «If he doesn’t have a relevant Larva, he can’t Awaken that Great Old One» | RITUAL / OTHER | своё | YES |
| DS-03 | RB-NEW p.77 (Стр 82); FAQ p.184 (Стр 189) | Cosmic Ruler: «you can Sacrifice it cheaply to keep another, better Avatar alive via Synthesis’ Cosmic Ruler ability»; FAQ «You can only use Cosmic Ruler to transfer a death to an Avatar which isn’t already being Killed in the Battle» | COUNT-TARGET | своё | YES |
| DS-04 | RB-NEW p.77 (Стр 82); FAQ p.198 (Стр 203) | Animate Matter: «Your signature move… “Other Great Old Ones hate him!”»; FAQ «Can the Daemon Sultan’s Chaos Gate move through a destroyed area with Animate Matter? A. Yes, but the Controlling Unit is Eliminated.» | OTHER | **Текста карты в корпусе нет**; задевает ли GOO — не проверено | YES* (если бьёт по GOO — Bastet попадает в обеих моделях; проверить по карте) |
| DS-05 | RB-OLD p.74 (Стр 84) | Undirected Energy: «Flip this Spellbook face down if Avatar Thesis is in play. Gain 1 Power per Faction with Units in Thesis’s Area, including you.» | OTHER | — | YES |

#### B8. Opener of the Way

| ID | Источник | Цитата | Кат. | Elder God в оригинале | Слитная модель |
|---|---|---|---|---|---|
| OW-01 | WIKI; FAQ p.186 (Стр 191); BGG:Compilation 2 | Yog-Sothoth Combat = удвоенное число вражеских faction GOO; FAQ «if there are 4 Enemy Faction Great Old Ones on the Map… Yog-Sothoth’s Combat would be 11 (8 + 3)»; BGG «Opener’s Combat and Hibernate have already been errata’d to only include enemy Faction GOOs» | COUNT-TARGET / COMBAT | Bastet — вражеский фракционный GOO → +2 | YES |
| OW-02 | RB-NEW p.82 (Стр 87) | «Everyone else has to pay for their Great Old Ones all at once»; «bring your Great Old One out at the right time (usually once two or three other Great Old Ones have taken the field)» | COUNT-TARGET | — | YES |
| OW-03 | RB-OLD p.117 (Стр 127); REG/factions.yaml; FAQ p.185 (Стр 190) | The Beyond One (версия IGOO): «Yog-Sothoth must be in an Area containing a Gate, but no enemy Great Old One.»; фракционная — отряд стоимостью 3+ в области с Gate и без вражеских GOO; FAQ «Do enemy Great Old Ones still cancel Beyond One if the Gate in question is not Controlled by their Faction? …Independent…? …Watcher? A. Yes, to all three.» | COUNT-TARGET | Bastet блокирует | YES |
| OW-04 | RB-OLD p.117 (Стр 127); BGG:Compilation 2 (цитата Dreamlands); BGG:Compilation | Требование spellbook: «Yog-Sothoth shares an Area with an enemy Great Old One» / «Your Great Old One shares an Area with an Enemy Great Old One»; BGG «Do Independent Great Old Ones count towards the Share Area with Enemy GOOs requirement? A: Yes they do, if they’re controlled by another Faction.» | COUNT-TARGET | Bastet засчитывается | YES |
| OW-05 | RB-OLD p.117; FAQ p.185 (Стр 190) | Key and the Gate: «Yog-Sothoth counts as a Gate for every purpose…»; FAQ «If he performs a Ritual of Annihilation, he gets 1 point for Yog-Sothoth as a Gate (plus an Elder Sign for Yog-Sothoth as a Great Old One).» | RITUAL | Для Bastet n/a; Yog как вражеские врата включает Requires Attention (BU-08) | YES |
| OW-06 | FAQ p.186 (Стр 191) | «To Awaken an Independent Great Old One, you need a Controlled Gate and your own Great Old One. Does Yog-Sothoth, by himself, fulfill both…? A. No, because Yog-Sothoth is not technically a Controlled Gate.» | COUNT-TARGET | Bastet + Луна выполняют оба условия | YES |
| OW-07 | FAQ p.186 (Стр 191) | Channel Power: «You can keep re-rolling misses… paying one Power per re-roll» | COMBAT (переброс) | только кубики Opener | YES |
| OW-08 | FAQ p.185 (Стр 190) | Dread Curse: «not considered a Battle, despite the fact that Combat dice are rolled»; «The victim selects the targets» | COMBAT / COUNT-TARGET | Bastet может быть выбрана владельцем; от категории не зависит | YES |

#### B9. Sleeper

| ID | Источник | Цитата | Кат. | Elder God в оригинале | Слитная модель |
|---|---|---|---|---|---|
| SL-01 | WIKI; RB-NEW p.86 (Стр 91) | Tsathoggua Combat = Power противника или 2; «Even though Tsathoggua’s Combat is reduced late in the Action Phase» | COMBAT | Против Bubastis зависит от её Power, не от Bastet | YES |
| SL-02 | WIKI | Formless Spawn: кубик за каждого Formless Spawn и Tsathoggua на карте | COMBAT | свой GOO | YES |
| SL-03 | RB-OLD p.118 (Стр 128) | Lethargy: «If Tsathoggua is in play and at least one enemy player has more Power than you, do nothing. This counts as an Action.» | OTHER | своё | YES |
| SL-04 | ERR-PACK стр.5; FAQ p.187 (Стр 192); FAQ p.183 (Стр 188) | Demand Sacrifice: «If Tsathoggua is in play, your enemy chooses ONE…: 1) You gain an Elder Sign. OR 2) All of their Kill results against your Units in this Battle count as Pains instead.»; «So long as Tsathoggua is in play, Demand Sacrifice applies to all Battles»; с Zagazig: «…all of Bubastis’ rolled Kill results count as Pains due to Demand Sacrifice» | COMBAT | Фикс. Kill Bastet по тексту карты — тоже «Kill result» → Pain; FAQ говорит только о «rolled» — **в оригинале неоднозначно** | YES (неоднозначность общая, в слитной модели +1 Kill тоже Kill result) |
| SL-05 | FAQ p.187 (Стр 192); FAQ p.184 (Стр 189) | Ancient Sorcery: «a unique ability that names a specific Great Old One allows Sleeper to apply that ability to Tsathoggua… re-Awaken Tsathoggua for 4 Power (and will also earn 1 Elder Sign)»; «What happens if Sleeper uses Ancient Sorcery to target Bubastis? A. Nothing, unless he has some way to add Earth Cats» | COUNT-TARGET | Lunacy не про GOO | YES |
| SL-06 | BGG:Compilation | Capture Monster: «he may only choose Monsters» | COUNT-TARGET | Bastet не цель | YES |

#### B10. Tcho-Tcho

| ID | Источник | Цитата | Кат. | Elder God в оригинале | Слитная модель |
|---|---|---|---|---|---|
| TT-01 | WIKI; RB-NEW p.90 (Стр 95) | Ubbo-Sathla Combat = Growth counter; «you normally spend 0 Power on your Great Old One» | COMBAT | своё | YES |
| TT-02 | RB-NEW p.90 (Стр 95) | «If your enemies don’t send in Great Old Ones, you can often use Proto-Shoggoths to handle the riffraff» | OTHER | — | YES |
| TT-03 | FAQ p.189 (Стр 194) | Terror: «roll 4 dice and subtract 4 from the enemy dice total… (and if the enemy’s reduction goes to below 0, he still just rolls 0. No negative Combat ratings!)» | COMBAT (снижение кубиков врага) | Кубиков Bastet нет; фикс. Kill от кубиков не зависит (FAQ p.183) | YES — при «even if no dice were rolled» |
| TT-04 | RB-NEW p.36 (Стр 41), пример | Martyrdom: «when his High Priest takes a Kill, all other Kills against Tcho-Tcho Units are transformed into Pains» | COMBAT | Kill Bastet тоже становится Pain | YES |

#### B11. Tcho-Tcho Tribes

| ID | Источник | Цитата | Кат. | Elder God в оригинале | Слитная модель |
|---|---|---|---|---|---|
| TR-01 | RB-NEW p.92 (Стр 97) | Fulmination: «It’s a one-off, because it Kills Ubbo Sathla… Only Kills count, not Eliminations.» | RITUAL / COMBAT | своё | YES |
| TR-02 | RB-NEW p.91–92 (Стр 96–97) | «Do not choose Sarkomand unless your game includes both Independent Great Old Ones and Neutral Monsters»; «your free Great Old One is an important decision»; Doomsday «A free Great Old One!»; «you can’t take the Cost 6 and Cost 0 Independents with Doomsday»; «Once you get those Great Old Ones in play, the other players may try to Kill them» | COUNT-TARGET | Independents; не про Bastet | YES |
| TR-03 | RB-NEW p.92 (Стр 97) | Inerrant: «Because you double-dip with Ubbo Sathla this way, you gain 1 Elder Sign for it anyway (as your Faction Great Old One). Then, if Ubbo is at an enemy Gate, you get another Elder Sign, plus a third if your free Great Old One is usefully placed.» | RITUAL | своё | YES |

#### B12. Windwalker

| ID | Источник | Цитата | Кат. | Elder God в оригинале | Слитная модель |
|---|---|---|---|---|---|
| WW-01 | RB-NEW p.96 (Стр 101); REG/factions.yaml; BAL (O2); BGG:Compilation 2 | Hibernate: +1 Power за каждого вражеского (faction) GOO в игре, не больше текущего Power; «When other players have their Great Old Ones out, you should be able to bank on 2 to 4 extra Power via Hibernate» | COUNT-TARGET | Bastet засчитывается | YES |
| WW-02 | REG/mercenaries.yaml (original_en; в RB-OLD p.119 текст искажён); RB-NEW p.96 | Ferox: «Your Cultists cannot be Captured by enemy Monsters or Terrors. They are still vulnerable to enemy Great Old Ones.»; «While Ferox lets you safely leave Cultists more-or-less alone» | COUNT-TARGET | Bastet захватывает (p.70) | YES |
| WW-03 | RB-NEW p.96 (Стр 101); FAQ p.190 (Стр 195) | Howl: «removing an Enemy Great Old One’s protective guard»; «Although Howl works on any Unit, rather than the typical specification of a Monster or Cultist…» | COUNT-TARGET | Bastet может быть отброшена | YES |
| WW-04 | RB-NEW p.96 (Стр 101) | «Your Great Old Ones are inexpensive and useful»; «one of the few forces that can take on even Great Cthulhu itself»; «you getting a Great Old One in your face» | OTHER | — | YES |
| WW-05 | WIKI; RB-OLD p.119 | Ithaqua Combat = половина Doom противника; Rhan Tegoth 3; Eternal | COMBAT | своё | YES |

#### B13. The Invasion (12-я фракция по реестру; в компендиуме отсутствует)

| ID | Источник | Цитата | Кат. | Elder God в оригинале | Слитная модель |
|---|---|---|---|---|---|
| INV-01 | REG/factions.yaml; WIKI (низкое доверие, текста правил нет) | Baphomet Combat = 4 + Doom с Elder Signs в эту Action Phase; «Число пробуждаемых Independent Great Old Ones ограничено числом Lord’s Shadow» | COMBAT / COUNT-TARGET | Не про Bastet | YES |

---

### C. FAQ (RB-NEW p.181–190 и FAQ-ONLINE; ядро и 12 фракций). Записи, уже разобранные выше, даны ссылкой

| ID | Источник | Цитата | Кат. | Elder God в оригинале | Слитная модель |
|---|---|---|---|---|---|
| FAQ-01 | RB-NEW p.181 (Стр 186); FAQ-ONLINE | «How much Power does Crawling Chaos get for Killing or Paining Cthulhu? A. He receives 2 Power, since that is now half the cost of Awakening Cthulhu… he could instead just take 2 Elder Signs.» | COUNT-TARGET | Для Bastet: 3 Power или 2 ES (p.70) | YES |
| FAQ-02 | RB-NEW p.181; FAQ-ONLINE | «Since Nyarlathotep cannot be Eliminated due to being surrounded (when he has Emissary of the Outer Gods and is not Battling an enemy Great Old One)…» | COUNT-TARGET | = CC-03 | YES |
| FAQ-03 | RB-NEW p.182 (Стр 187); RB-OLD p.211 | «Can Elder Gods declare Battle since they have no Combat dice? A. No.» | EXPLICIT-EG / COMBAT | = BU-11 | YES |
| FAQ-04 | RB-NEW p.182; FAQ-ONLINE | «If there is more than one enemy Great Old One in a Battle against me and I invoke Unholy Ground, can I remove two Cathedrals to Eliminate two Great Old Ones? A. Yes.» (в FAQ-ONLINE — «to kill two») | COUNT-TARGET | = AN-03 | YES |
| FAQ-05 | RB-NEW p.182 | «If an enemy Great Old One is assigned a Kill, and that Kill is later turned into a Pain (e.g. Nyarlathotep’s Emissary…), can Unholy Ground still be used to Eliminate the Great Old One? A. Yes» | COUNT-TARGET | — | YES |
| FAQ-06 | RB-NEW p.182; FAQ-ONLINE | «Can Rhan Tegoth avoid Unholy Ground’s Kill by spending 1 Power…? A. No, because Unholy Ground produces an Elimination, not a Kill.» | COUNT-TARGET | — | YES |
| FAQ-07 | RB-NEW p.183 (Стр 188) | «How do the Ancients generally interact with requirements or rules necessitating all Factions to have a Great Old One? A. The Ancients are ignored for this purpose…» | COUNT-TARGET | Bubastis не игнорируется: условие выполняется, когда Bastet в игре | YES |
| FAQ-08 | RB-NEW p.183 | ES за ритуал с Bastet | EXPLICIT-EG / RITUAL | = BU-07 | **DEPENDS** |
| FAQ-09 | RB-NEW p.183 | Zagazig для обеих сторон | COMBAT | = BU-09 | **DEPENDS** |
| FAQ-10 | RB-NEW p.183 | Zagazig + Demand Sacrifice | COMBAT | = SL-04 | YES (неоднозначность общая) |
| FAQ-11 | RB-NEW p.183 | Bastet одна в бою наносит Kill | EXPLICIT-EG / COMBAT | = BU-10 | YES |
| FAQ-12 | RB-NEW p.184 (Стр 189) | Bastet + Yog-Sothoth → 3 ES | EXPLICIT-EG / RITUAL | = BU-08 | **DEPENDS** |
| FAQ-13 | RB-NEW p.184 | Cosmic Ruler | COUNT-TARGET | = DS-03 | YES |
| FAQ-14 | RB-NEW p.185 (Стр 190); FAQ-ONLINE | Key and the Gate: «…plus an Elder Sign for Yog-Sothoth as a Great Old One» | RITUAL | = OW-05 | YES |
| FAQ-15 | RB-NEW p.185; FAQ-ONLINE | Beyond One отменяется вражескими GOO («Yes, to all three» в RB; «Yes, to both» без Watcher в FAQ-ONLINE) | COUNT-TARGET | = OW-03 | YES |
| FAQ-16 | RB-NEW p.186 (Стр 191) | Пробуждение Independent: Controlled Gate + свой GOO | COUNT-TARGET | = OW-06 | YES |
| FAQ-17 | RB-NEW p.186; FAQ-ONLINE | Miri Nigri + Yog: «4 Enemy Faction Great Old Ones… 11 (8 + 3)» | COUNT-TARGET / COMBAT | = OW-01 | YES |
| FAQ-18 | RB-NEW p.186 | Channel Power | COMBAT | = OW-07 | YES |
| FAQ-19 | RB-NEW p.187 (Стр 192) | Ancient Sorcery и способности, называющие GOO | COUNT-TARGET | = SL-05 | YES |
| FAQ-20 | RB-NEW p.187 | «Does Tsathoggua have to be personally involved in a Battle to use Demand Sacrifice? A. No.» | COMBAT | — | YES |
| FAQ-21 | RB-NEW p.189 (Стр 194) | Terror снижает кубики врага | COMBAT | = TT-03 | YES |
| FAQ-22 | RB-NEW p.189; FAQ-ONLINE | «With the Hierophants Spellbook, do the Tcho-Tcho get to place a free High Priest when they earn an Independent Great Old One’s Spellbook, too? A. No… “Faction Spellbooks.”» | OTHER | — | YES |
| FAQ-23 | RB-NEW p.189–190; FAQ-ONLINE | «Rhan Tegoth’s Eternal ability only cancels the effect of a Kill or Pain on Rhan Tegoth itself… Nyarlathotep can gain Power or Elder Signs» | COUNT-TARGET | — | YES |
| FAQ-24 | RB-NEW p.190 (Стр 195); FAQ-ONLINE | «Can Units retreated due to Howl still use Battle Abilities… (such as… Nyarlathotep’s Harbinger)? A. No» | COUNT-TARGET | — | YES |
| FAQ-25 | RB-NEW p.190; FAQ-ONLINE | Howl действует на любой Unit | COUNT-TARGET | = WW-03 | YES |
| FAQ-26 | BGG:Compilation (Petersens как источник) | «Submerge: If Great Cthulhu performs a Ritual of Annihilation with Cthulhu Submerged, does he receive an Elder Sign? A: Yes, Cthuhu is still in Play.» | RITUAL | «in play» ≠ «на карте» | YES |
| FAQ-27 | BGG:Compilation | Harbinger: «Can Harbinger affect more than one Great Old One at a time? A: Yes.»; «…Necrophagy is triggered and a Pain is inflicted, does Harbinger also trigger? A: Yes.»; Eternal не отменяет срабатывания | COUNT-TARGET | — | YES |
| FAQ-28 | BGG:Compilation | Beyond One: «any enemy GOO prevents The Beyond One from working»; Berserkergang: «Can Berserkergang eliminate a Great Old One? A: No.»; Avatar на GOO — нет | COUNT-TARGET | — | YES |

---

### D. Эррата и балансные правки, касающиеся GOO

| ID | Источник | Правка | Кат. | Связь с Elder God | Слитная модель |
|---|---|---|---|---|---|
| ERR-01 | BAL (O2), ERR-PACK стр.5 | The Red Sign: «Each Dark Young adds 1 to Shub-Niggurath’s Combat»; «Black Goat board: Shubby combat value calculation» | COMBAT | Прибавка только к Shub | YES |
| ERR-02 | BAL (O2) | «WindWalker board: Hibernation nerf (gain capped at current power level)» | COUNT-TARGET | Hibernate считает вражеских GOO; Bastet считается | YES |
| ERR-03 | BGG:Compilation 2 (community) | «Opener’s Combat and Hibernate have already been errata’d to only include enemy Faction GOOs» | COUNT-TARGET | Bastet — фракционная | YES |
| ERR-04 | BAL (O2) | «Great Cthulhu board: Elder Sign gain on 2 spellbooks unlock (first and last)»; «Opener board: Specific spellbook unlock for 2-3 players game» | RITUAL / OTHER | не про категорию GOO | YES |
| ERR-05 | BAL (O2), ERR-PACK стр.5 | Demand Sacrifice: «only 2 choices, not 3 anymore» | COMBAT | см. SL-04 | YES |
| ERR-06 | RB-NEW p.109 | Independents не дают ES за ритуал — «We did not specify this rule in the original release» | RITUAL | Определение «кто даёт ES» сужено до faction GOO; EG — отдельное исключение p.70 | YES |

Правок, меняющих определение Great Old One или Elder God, в эррате нет.

---

### E. Вне объёма (для агента по Independents / нейтралам / картам) — найдено попутно

| ID | Источник | Цитата | Почему важно |
|---|---|---|---|
| PTR-01 | FAQ-ONLINE (Neutral Monsters); REG/mercenaries.yaml | Elder Thing, Mind Control: «If an Elder Thing shares an Area with an enemy Great Old One, the latter may not use its Special Ability.» | **Потенциальное NO.** В слитной модели +1/−1 Kill Bastet — способность, Mind Control её гасит. В оригинале это её Combat (ср. «does not affect Bastet’s Combat», p.71) — по логике не гасится. FAQ прямо не разбирает |
| PTR-02 | RB-NEW FAQ p.195 (Стр 200) | «Does Cthugha copy the combat of Elder Gods? A. Cthugha rolls no dice when facing an Elder God, and gets no further benefit vs. Elder Gods.» | Слитная модель: копирует 0, способность не копирует — совпадает, если способность не объявлена частью Combat |
| PTR-03 | FAQ-ONLINE (Chaugnar Faugn, Star Vampires) | «…the fact that you will roll Combat dice means that you can initiate Battle even if all you have is a single Cultist»; «if your total dice are technically zero, you cannot Declare Battle» | Право объявить бой привязано к сумме кубиков стороны. Любой внешний эффект «+N Combat GOO/всем отрядам» даст Bastet в слитной модели кубики и право боя, в оригинале — нет («never roll Combat dice») |
| PTR-04 | RB-NEW p.163 (Стр 168), Shaggai | «…Faction Great Old One that is Eliminated also provides its owner with 1 Elder Sign» | Исключение EG касается только ES за ритуал → Bastet ES здесь даёт; пометка слитной модели должна быть ограничена ритуалом |
| PTR-05 | RB-NEW p.116 (Стр 121), p.130 (Стр 135) | «Nodens, Independent Elder God»; «Hagarg Ryonis, Independent Elder God» | Ещё два Elder God вне фракций |
| PTR-06 | ERR-PACK стр.12 | Terrors: «Great Old Ones can still Capture Cultists protected by Terrors» | Bastet пробивает Terror |
| PTR-07 | REG/mercenaries.yaml | Cacodemon: «…unless they are Great Old Ones or if they are accompanied by a Great Old One»; Elder Shoggoth Prime Cause: «You can gain a Faction Great Old One that was previously Awakened» | GOO-зависимые нейтралы |
| PTR-08 | FAQ-ONLINE; BGG | Watcher/Bhole как «enemy Great Old One» для Hibernate/Beyond One/Yog | Расширение понятия «вражеский GOO» |


---

# Таблица 2. Оригинал: нейтралы, независимые, карты, дополнения, все Elder God


Дата сбора: 2026-10-01. Цитаты — по-английски, как в источнике; комментарии — по-русски.

### 0. Источники и обозначения

| Код | Что | Доверие |
|-----|-----|---------|
| RB-NEW p.N (Стр.M) | `source/cthulhu-wars/SRC-RB-NEW__…md`. p.N — печатная страница, Стр.M — маркер PDF, M = N + 5 | официальный |
| RB-OLD p.N | `source/cthulhu-wars/SRC-RB-OLD__…md`, печатная страница. Тексты карт лояльности есть, но часть перемешана pdftotext | официальный |
| FAQ-ONL | `source/cthulhu-wars/SRC-FAQ__cw-rules-faq__…md` (freshdesk) | официальный |
| ERR | `SRC-ERRATA-PACK__cards-text…`, `…ultimate-errata-pack…` | официальный |
| DOS | `source/web/SRC-WEB-LOYALTY__cw-loyalty-cards__2026-10-01.md` (раздел указан) | сводка с URL |
| NEC-KS | https://necronomicon.app/neutral-expansions/kickstarter-specials (снято 01.10.2026) | транскрипция карт |
| NEC-CATS | https://necronomicon.app/neutral-expansions/something-about-cats | транскрипция |
| NEC-GW | https://necronomicon.app/neutral-expansions/the-gods-war-crossover | транскрипция |
| NEC-PA | https://necronomicon.app/neutral-expansions/planet-apocalypse-crossover | транскрипция |
| NEC-DUN | https://necronomicon.app/neutral-expansions/the-dunwich-horror | транскрипция |
| NEC-BUB | https://necronomicon.app/factions/bubastis | транскрипция |
| NEC-JSON | https://necronomicon.app/data-files/rulebook.json (раздел expansion-products → Independent Elder Gods) | транскрипция |
| WIKI-GW | https://cthulhuwars.fandom.com/wiki/Glorantha:_The_Gods_War/CW (открылась 1 раз; остальные страницы вики — HTTP 402) | вики |
| WIKI-LIB | https://cthulhuwars.fandom.com/wiki/Library_at_Celaeno_Map | вики |
| PG-NOD | https://petersengames.com/products/nodens | магазин, маркетинг |
| BGG | `scratchpad/bgg/Compilation of FAQs_*.txt` | сообщество, низкое |

Тексты карт лояльности в RB-NEW — картинки; текста там нет. Поэтому карты — по RB-OLD (где читается),
NEC и DOS.

---

### A. Досье Elder God

#### A.0. Общие правила Elder God — три официальные формулировки

1. **Лист Bubastis** (RB-NEW p.70 / Стр.75; RB-OLD, раздел Bubastis; NEC-BUB):
   > «Bastet is an Elder God; these beings are treated as Great Old Ones for all purposes except: they do not provide an inherent Elder Sign for a Ritual of Annihilation, though they often have other means of creating Elder Signs; and Elder Gods never roll Combat dice, but provide some fixed benefit. They do count as equal to Great Old Ones otherwise, so they can block Unit Captures. Nyarlathotep gets 2 Elder Signs or half-Power cost from his Harbinger ability compared with that of other Great Old Ones. You can use them to Capture Cultists even if an enemy Monster is present, and so forth.»
2. **Блок «Independent Elder Gods»** под Nodens (NEC-KS), Hagarg Ryonis (NEC-CATS) и в NEC-JSON:
   > «Elder Gods are similar to Great Old Ones, except they do not provide Elder Signs during a Ritual of Annihilation, and do not roll combat dice.»
   > «Doom Phase: When you perform a Ritual of Annihilation, do NOT gain an Elder Sign for any Independent Elder Gods you Control.»
   Остальное (Awakening, Death, Spellbook) — дословно как у IGOO.
3. **Gods War** (NEC-GW, под каждым из трёх EG) — та же фраза, что в п.2.

Разница формулировок: у Bubastis «treated as GOO for all purposes except», у независимых — «similar to GOO, except».
По смыслу одно и то же: исключений два — нет Elder Sign за Ritual и нет кубиков.

**FAQ, прямо называющие Elder God** (все официальные):

| # | Источник | Текст |
|---|----------|-------|
| F1 | RB-NEW p.182 (Стр.187); RB-OLD p.212 | «Q. Can Elder Gods declare Battle since they have no Combat dice? A. No.» |
| F2 | RB-NEW p.183 (Стр.188); NEC-BUB Q5 | «Q. If Bastet is in a Battle by herself, does she still get to inflict her one Kill, even though no Combat dice are rolled for her side? A. Yes, of course. Elder Gods just inflict results. They don't roll dice, and they don't require dice to be rolled for their results to take place. Also, if Bastet is alone, she also still gets her ability to reduce the enemy-rolled Kills by 1.» |
| F3 | RB-NEW p.183; NEC-BUB Q1 | «Q. Do I get an Elder Sign for Ritualing with Bastet if I'm not using her Requires Attention ability? A. No. Elder Gods do not provide Elder Signs for Rituals of Annihilation, except in conjunction with special abilities. …» |
| F4 | RB-NEW p.184 (Стр.189); NEC-BUB Q13 | «Q. If Bastet is in an area with Yog-Sothoth, and you ritual, do you get 3 Elder Signs? A. Yes. But the presence of another Enemy Controlled Gate does not increase this reward.» |
| F5 | RB-NEW p.195 (Стр.200); RB-OLD p.228 | «Q. Does Cthugha copy the combat of Elder Gods? A. Cthugha rolls no dice when facing an Elder God, and gets no further benefit vs. Elder Gods.» |
| F6 | RB-NEW p.195; RB-OLD p.229 | «Q. If Nodens copies The Ancients' Extinction Spellbook, is He removed from the game upon being killed or eliminated? A. Yes. But at least He was cheaper to Awaken.» |
| F7 | RB-NEW p.71 (Стр.76), советы Bubastis | «Zagazig … Also note that it does not affect Bastet's Combat. It does affect the enemy's die rolls too, though, so be careful!» |

Прочее:
- На компонентах тип печатается отдельно: Bastet — «ELDER GOD» (`SRC-WIKI…`, строка 352), Nodens и Hagarg —
  «INDEPENDENT ELDER GOD» (RB-OLD p.123, p.140; RB-NEW p.116, p.130).
- Маркетинг Petersen (PG-NOD): «A new type of unit - an Elder God!» — не правило, но называет EG «новым типом юнита».

#### A.1. Bastet (фракционный Elder God Bubastis)

- Продукт: Bubastis Faction, **CW-F8** (`SRC-PRODUCTS`). Отдельной карты Independent для Bastet нет ни в одном источнике (DOS C.12).
- Стоимость: **6**. Статблок NEC-BUB: «Bastet Elder God 6 1 Kill»; в `SRC-WIKI` бой — `*`.
- Пробуждение (NEC-BUB): «1) All your Cat varieties are in play. 2) Pay 6 Power. 3) Place Bastet in an Area containing no enemy Units.»
- Combat (NEC-BUB): «Add 1 Kill to your combat total (Bastet rolls no dice); the enemy must lower their Kill total by 1.»
  - FAQ F2 называет вторую часть «her ability to reduce the enemy-rolled Kills by 1» — «enemy-rolled», тогда как карта — «Kill total».
- Особая способность **Requires Attention** (NEC-BUB): «During the Doom Phase, if Bastet is in an Area containing an enemy Cultist, you may perform a Ritual of Annihilation. For you, this adds exactly 4 Doom plus: If Bastet's Area has an Enemy-Controlled Gate, gain 1 Elder Sign. If Bastet's Area has an Enemy Great Old One, gain 2 Elder Sign.»
- Своего Spellbook нет: 6 фракционных (Ailurophobia, Catabolism, Catnapping, Predator, Savagery, Zagazig).
- Правила, специфичные для EG: A.0 п.1; FAQ F2, F3, F4, F7. Shaggai: «Bubastis is allowed to use the "Pay 6 Power" rule but not the "Pay 2 Power" rule» (RB-NEW p.163, p.198).

#### A.2. Nodens (Independent Elder God)

- Продукт: **CW-U28** (Kickstarter special; RB-NEW p.116 «Nodens, Independent Elder God Loyalty & Spellbook Cards»). Текст — NEC-KS (снят повторно 01.10.2026, совпал с DOS F.8); RB-OLD p.123 — перемешан.
- Пробуждение (Cost 6): «1. Your Controlled Gate is in an Area with your Great Old One. 2. Pay 6 Power, place Nodens into the Area.»
- Combat: «Add 1 Kill and 2 Pains to your Combat total (Nodens doesn't roll any Combat Dice)»
- **Healing (Doom Phase):** «At the end of the Doom Phase, unless the Ritual of Annihilation track has reached Sudden Death, move the Ritual marker backwards 1 step (but not past the start).»
- Требование Spellbook: «Perform a Ritual of Annihilation.»
- **Proteus (Action: Cost 2):** «Choose one of your earned Faction Spellbooks that names either a type of Unit (e.g., Acolytes or Flying Polyps). Place your Faction Glyph on that Spellbook. Nodens then benefits from that Spellbook's effects as if it were the named Unit or type of Unit.»
- FAQ: F6. Других официальных ответов по Proteus нет.

#### A.3. Hagarg Ryonis («Cat from Jupiter», Independent Elder God)

- Продукт: Something About Cats Box, **CW-U33** (RB-NEW p.130; RB-OLD p.140). Текст — NEC-CATS (снят 01.10.2026).
- Пробуждение (Cost 4): «1. Your Controlled Gate is in an Area with your Great Old One 2. Pay 4 Power, and place Hagarg Ryonis in the Area containing the Gate.»
- Combat: «Hagarg Ryonis rolls no dice. Instead, she adds 3 Pains to your Combat total.»
- **Subversion (First Player Phase):** «Choose a player, if that player performs a Ritual of Annihilation in this Doom Phase, you steal 1 of the Elder Signs he earns (if any).»
- Требование Spellbook: «You have 0 Power.» — из DOS F.9 (второй запрос); сегодня повторно не извлечено.
- **Laziness (Action: Cost 0):** «Any Faction with exactly 1 Power left loses that Power. Alternatively, pay 1 Power to force Windwalker to also lose 1 Power. You can only use this Action if Windwalker is Hibernating, or one or more enemy Factions have exactly 1 Power.»
- FAQ: нет.

#### A.4–A.6. Elder Gods кроссовера Glorantha: The Gods War

Источник — NEC-GW (снято 01.10.2026), подтверждено WIKI-GW. Код продукта не найден.

**Hellmother**
- «How to Awaken Hellmother (Cost 4): 1. Your Controlled Gate is in an Area with your Great Old One 2. Pay 4 Power, and place Hellmother in the Area containing the Gate. Gain 1 Elder Sign.»
- Combat: «Inflict 1 Pain per Cultist you have on the Map. Also inflict 1 Kill if you have at least 6 Cultists.»
- **Hellborn (Ongoing):** «If Hellmother is in play, your monsters can be Recruited instead of Summoned. I.e., you can place them in any Area in which you have a Unit.»
- Требование: «One of your units is Killed». SB **Nocturnal Raids (Doom Phase):** «Place a free cultist in Hellmother's Area.»

**Sun God**
- Пробуждение: Cost 4, тот же текст, «… Gain 1 Elder Sign.»
- Combat: «Inflict 1 Pain and 1 Kill.»
- **Sunrise (Ongoing):** «The Sun God cannot be killed or eliminated. When he is chosen to receive such a result, instead the enemy player gets to pick up and place Sun God in any Area, and Sun God's owner loses 1 Power or 1 Doom (your choice).»
- Требование: «As an Action, spend 1 Power. Choose an enemy faction to gain 1 Elder Sign.» SB **Sunspear (Action: Cost 2):** «Choose an enemy unit and roll 1d6. If you roll at least twice as high as that unit's Cost, eliminate it, and move the Sun God to that Area.»

**Thunder King**
- Пробуждение: Cost 4, «… Gain 1 Elder Sign.»
- Combat: «Inflict 1 Pain per faction spellbook. Also inflict 1 Kill if you have all 6 faction spellbooks.»
- **Inferiority Complex (Doom Phase):** «You may choose to spend 2 Doom to gain 5 Power.»
- Требование: «Kill or eliminate an enemy Cultist». SB **Kinship (Doom Phase):** «Choose an enemy faction. You then choose to receive either 1 Doom or 2 Power. Your chosen enemy gains the other possible reward.»

Остальные карты того же кроссовера — Lady of Disease, Mad God, Magna Mater — обычные **Independent Great Old One** (NEC-GW).

#### A.7. Что ещё проверено

- 19 страниц NEC «neutral-expansions» и 12 страниц фракций: других Elder God нет. Baphomet у The Invasion — обычный GOO.
- Elder Thing (нейтральный монстр), Elder Shoggoth (Terror), Elder Sign — к Elder God отношения не имеют.
- Не открыты (HTTP 402): Category:Independent_Elder_Gods, Strategy:Independent_Elder_Gods, Nodens, «Elder Races/CW» (вероятно, фракция Gods War для CW — не проверено).

**Итог по EG:** 6 штук. Bastet (фракционный), Nodens, Hagarg Ryonis, Hellmother, Sun God, Thunder King (независимые).

---

### B. Таблица: всё вне ядра и 12 фракций, что ссылается на GOO или Elder God

Категории: RITUAL / COMBAT / EXPLICIT-EG / COUNT-TARGET / OTHER.
«Слитая модель» — EG = GOO с напечатанной силой 0, фиксированный эффект отдельным текстом свойства, локальная пометка «не даёт Elder Sign при Ritual».

#### B.1. Общие правила Independent GOO

| ID | Источник | Цитата | Кат. | Как EG в оригинале | Слитая модель |
|----|----------|--------|------|--------------------|---------------|
| IG-01 | RB-NEW p.107 (Стр.112) | «Each Independent Great Old One has an inherent ability, must be Awakened to bring it into play, and has a Spellbook that goes only on its own Loyalty Card.» | OTHER | IEG устроены так же (блок IEG в NEC-KS) | YES |
| IG-02 | RB-NEW p.109 (Стр.114), Awakening | «There is no limit to how many Independents you may Control. You may use one Independent to help Awaken another.» | COUNT-TARGET | IEG годится как «your GOO» для пробуждения следующего; BGG-компиляция: «Yes, for Example Bokrug and a controlled Gate can be used to Awaken Father Dagon» | YES |
| IG-03 | RB-NEW p.109, Death | «If your Independent Great Old One is Killed, place its Loyalty Card, figure, unused tokens, and Spellbook back into the general Pool…» | OTHER | то же; Sun God убить нельзя (Sunrise) | YES |
| IG-04 | RB-NEW p.109, Spellbook | «These Spellbooks never count as one of the Spellbooks on your Faction Card…» | OTHER | Proteus, Laziness и SB Gods War — то же | YES |
| IG-05 | RB-NEW p.109, Doom Phase | «When you perform a Ritual of Annihilation, do NOT gain an Elder Sign for any of the Independent Great Old Ones you Control. … ONLY Faction Great Old Ones provide Elder Signs when you perform a Ritual of Annihilation.» | RITUAL | IEG — нет (двойное основание); Bastet — нет (правило EG) | YES: IEG закрыт правилом IGOO, Bastet — пометкой |
| IG-06 | RB-NEW p.109 | «(Great Cthulhu still gets an Elder Sign when Awakening any Great Old One, however).» | RITUAL / COUNT | пробуждение любого EG даёт Cthulhu Elder Sign: EG = GOO во всём, кроме Ritual и кубиков | YES |
| IG-07 | NEC-KS / NEC-CATS / NEC-JSON | «Doom Phase: When you perform a Ritual of Annihilation, do NOT gain an Elder Sign for any Independent Elder Gods you Control.» | EXPLICIT-EG | — | YES |
| IG-08 | RB-NEW p.113 (Стр.118) | «We do NOT recommend using a Great Old One as an Independent if a player is playing as that Great Old One's Faction.» | OTHER | карты «Bastet as Independent» нет | n/a |
| IG-09 | RB-NEW p.140 | «Place these rings on the bases of grey Neutral Monsters, Terrors, and Independent Great Old Ones…» | OTHER | IEG — тоже | YES |

#### B.2. Фракционные GOO как Independent (RB-OLD p.115–119; NEC-RX; DOS C)

| ID | Источник | Цитата | Кат. | Как EG в оригинале | Слитая модель |
|----|----------|--------|------|--------------------|---------------|
| FI-01 | все 10 карт, шаг 1 | «Your Controlled Gate is in an Area with your Great Old One.» | COUNT-TARGET | EG выполняет: прямое чтение A.0 п.1, DOS E.2. Bastet — только на Луне (единственный Gate Bubastis) | YES |
| FI-02 | Hastur, Vengeance | «…you could apply a Kill to a particular enemy Great Old One involved in that Battle.» | COUNT-TARGET | вражеский EG — законная цель | YES |
| FI-03 | Nyarlathotep, Harbinger | «If Nyarlathotep is in a Battle in which one or more enemy Great Old Ones are Killed or Pained, receive Power equal to half of the cost of Awakening those Great Old Ones. For each enemy Great Old One so affected, you may choose to receive 2 Elder Signs instead of Power.» | COUNT-TARGET | прямо в A.0 п.1: EG даёт Harbinger как GOO (Bastet/Nodens — 3 Power, Hagarg/GW — 2). Sun God: «chosen to receive» Kill, но не Killed — неясно в обеих моделях | YES |
| FI-04 | Nyarlathotep, Combat | «Equal to the total number of Spellbooks held by your enemy (Faction Spellbooks, as well as any others).» | COUNT | SB у IEG считаются | YES |
| FI-05 | Tsathoggua и Yog-Sothoth, Combat | «Equal to the number of enemy Faction Great Old Ones (not counting any Independent Great Old Ones).» | COUNT | вражеская Bastet считается, IEG — нет | YES |
| FI-06 | Yog-Sothoth, The Beyond-One | «Yog-Sothoth must be in an Area containing a Gate, but no enemy Great Old One.» | COUNT | вражеский EG блокирует | YES |
| FI-07 | Yog-Sothoth, требование | «Yog-Sothoth shares an Area with an enemy Great Old One.» | COUNT | EG засчитывается | YES |
| FI-08 | Ithaqua, Ferox | «Your Cultists cannot be Captured by enemy Monsters or Terrors. They are still vulnerable to enemy Great Old Ones.» | COUNT-TARGET | EG может захватить (A.0 п.1) | YES |
| FI-09 | Cthulhu, Hastur — шаг 3 | «Gain 1 Elder Sign» | OTHER | прецедент: Elder Sign при пробуждении — обычный шаг (ср. Gods War EG) | n/a |

Rhan-Tegoth, Shub-Niggurath, The King in Yellow, Ubbo-Sathla: кроме шага 1 пробуждения, ссылок на GOO нет.

#### B.3. Пакеты IGOO, Masks, RC, Kickstarter, Dunwich, Gods War, Planet Apocalypse

| ID | Источник | Цитата | Кат. | Как EG в оригинале | Слитая модель |
|----|----------|--------|------|--------------------|---------------|
| IP-01 | все IGOO, шаг 1: Abhoth, Chaugnar, Cthugha, Hydra, Yig, Atlach, Bokrug, Dagon, Ghatanothoa, Gobogeg, Byatis, Nyogtha, Tulzscha, Eihort, Gla'aki, Y'Golonac, Daoloth, Bloated Woman, Haunter, Nodens, Hagarg, Dire Cthulhu, GW, PA | «Your Controlled Gate is in an Area with your Great Old One» | COUNT | EG годится как «your GOO» | YES |
| IP-02 | Chaugnar Faugn, Miri Nigri (DOS F.1) + FAQ RB-NEW p.194 / FAQ-ONL | «In a Battle taking place in an Area with your Controlled Gate, add +3 Combat Dice.» / «…Although Miri Nigri does not technically add 3 Combat to a particular Unit (as with Absorb), the fact that you will roll Combat dice means that you can initiate Battle even if all you have is a single Cultist…» | COMBAT | кубики добавляются стороне, не EG → сторона с одним EG бросает 3 и, видимо, может объявить Battle. F1 сформулирован без оговорок — небольшая неясность | YES: 0 + 3 = 3 |
| IP-03 | Cthugha, пробуждение | «Pay Power equal to 6 minus your Great Old One's Awakening Power Cost. If the result is negative gain the result in Power. 3. Replace your Great Old One with Cthugha.» | COUNT-TARGET | можно заменить EG: Bastet и Nodens 6 → 0; Hagarg и GW 4 → 2 | YES |
| IP-04 | Cthugha, Combat + FAQ F5 | «Equals the Combat of an enemy Great old One in the Battle (your choice). If none are present, Cthugha's Combat is 0.» | COMBAT / EXPLICIT-EG | против EG — 0 кубиков, фиксированный эффект не копируется | **YES в базовом случае**: копируется напечатанный 0, свойство не копируется. **DEPENDS**, если сила EG изменена (Nodens + Proteus/Frenzy, см. EG-01): слитая модель даёт Cthugha 1+, оригинал — «no further benefit» |
| IP-05 | Cthugha, требование | «Kill an enemy Great Old One in Battle.» | COUNT | убийство EG засчитывается (Sun God неубиваем) | YES |
| IP-06 | Mother Hydra, требование (DOS F.1) | «Choose EITHER Control no Great Old Ones in Ocean Areas OR enemy Factions control no Great Old Ones in Ocean Areas.» | COUNT | EG считается | YES |
| IP-07 | Gobogeg, Book of Law (DOS F.3) | «While Gobogeg is in play, whenever a Great Old One is Awakened, the owner receives 6 Power after the Awakening.» | COUNT | пробуждение EG срабатывает | YES |
| IP-08 | Nyogtha, требование (DOS F.4) | «Nyogtha survives a Battle against an enemy Great Old One.» | COUNT | EG засчитывается: его можно атаковать, сам он Battle не объявляет | YES |
| IP-09 | Daoloth, Cosmic Unity (DOS F.6; RB-OLD p.138) | «In a Battle involving Daoloth, choose one enemy Great Old One. It rolls no Combat dice (it still gets its Battle Ability, if any).» | COMBAT | выбор EG пустой: кубиков нет и так, фиксированные результаты остаются | YES: свойство EG сохраняется по скобке «still gets its Battle Ability» |
| IP-10 | Daoloth, требование | «A Great Old One is Killed (anywhere on the Map).» | COUNT | убийство EG засчитывается | YES |
| IP-11 | Haunter of the Dark, Combat (DOS F.7; RB-OLD p.133) | «Equal to the total number of Spellbooks earned by your enemy (including those for any Independent Great Old Ones).» | COUNT | SB у IEG считаются | YES |
| IP-12 | Haunter, Fly to the Light | «If the enemy scored exactly one Kill, it must be applied to the haunter.» | COMBAT | фиксированный Kill EG — «scored» (одна Bastet → Kill идёт в Haunter) | YES, если свойство в слитой модели «добавляет Kill к итогу» |
| IP-13 | Bloated Woman, Haunter — Crawling Chaos | «Crawling Chaos does not need a Great Old One in the Area into which he Awakens…» | COUNT | n/a | YES |
| IP-14 | Dire Cthulhu, Lord and Master (NEC-KS) | «When you Awaken an Independent Great Old One (except Dire Cthulhu), gain 1 Elder Sign.» | COUNT / RITUAL-adj. | IEG срабатывает; у GW EG сверху их собственный +1 Elder Sign | YES |
| IP-15 | Dire Cthulhu, Non-Euclidean + FAQ RB-NEW p.195 | «If any results are assigned to a non-participating Faction, that Faction may not use Battle abilities or Spellbooks in response.» | COMBAT | Bastet третьей стороны в бою не участвует; её срез Kill FAQ называет «ability» | YES |
| IP-16 | Azathoth (IGOO), пробуждение и требование (DOS C.12) | «You must have 8+ Power and your Great Old One at your Controlled Gate.» / «All players have at least one Great Old One in play.» + FAQ RB-NEW p.188: Ancients игнорируются | COUNT | Bastet закрывает и то, и другое; Bubastis не игнорируется | YES |
| IP-17 | Cthulhu, the Harbinger (NEC-KS) | «All other Factions: 1. You have a Great Old One in play.» / «It takes at least 3 Kills and/or Eliminates in the same Combat to Kill Harbinger Cthulhu.» | COUNT / COMBAT | EG годится; фиксированные Kill EG идут в зачёт | YES |
| IP-18 | The Risen One (NEC-KS) | «Your Controlled Gate is in an Area with your Great Old One.» / «…if the Risen One's side scores more Kills than its opposition, the Risen One is Eliminated.» | COUNT | EG годится | YES |
| IP-19 | Dire Yog-Sothoth, Combat (NEC-DUN) | «Equal to the number of enemy-Controlled Faction Great Old Ones in play.» | COUNT | вражеская Bastet считается | YES |
| IP-20 | Dire Yog-Sothoth, To Rule Them All | «Dire Yog-Sothoth can Capture other Great Old Ones following the same rules as Capture Cultist.» | COUNT-TARGET | EG можно захватить (Sun God тоже: захват — не Kill) | YES |
| IP-21 | Dire Yog-Sothoth, пробуждение и требование | «You have a Great Old One in play, as well as your most expensive Monster or Terror.» / «Your Great Old One is in the same Area as two enemy Great Old Ones.» | COUNT | EG считается с обеих сторон | YES |
| IP-22 | Chthon, Anteus (NEC-PA) | «Chthon is not normally affected by a Kill or Elimination. Instead you must choose another Great Old One under your Control and Kill it instead.» | COUNT-TARGET | свой EG годится; Sun God → Sunrise | YES |
| IP-23 | Argus, Combat (NEC-PA) | «Equal to the Combat of all your other Units present (excluding any Great Old Ones)» | COMBAT | EG исключён как GOO | YES (вклад 0 в любом случае) |
| IP-24 | Tarasque, Extinguish (NEC-PA) | «In an enemy Great Old One is in the Battle, Tarasque's Combat is 0, and he cannot apply his Spined ability.» | COUNT | вражеский EG включает | YES |
| IP-25 | Humbaba, Swarm (NEC-PA) | «Instead of rolling Humbaba's Combat dice, you can choose to automatically score two Pains.» | OTHER (прецедент) | у обычного IGOO фиксированные результаты вместо кубиков | n/a — показывает, что «фикс вместо кубиков» в CW бывает и у не-EG |
| IP-26 | Jabootu (NEC-PA) | «the enemy rolls 1 less Combat die in any Battle against you» / Criticism: «the enemy receives 1 less Kill result (minimum of 0)» | COMBAT | против EG: кубиков 0, Deadly Tedium пуст; Criticism режет и фиксированный Kill | YES |
| IP-27 | Magna Mater, The Unholy Trio (NEC-GW) | «At the end of any Battle (even if you did not participate), turn all Pain results into Kills.» | COMBAT | фиксированные Pain EG (Hagarg 3, Nodens 2) тоже превращаются | YES |
| IP-28 | Tulzscha, Ceremony of Annihilation (DOS F.4) | «You earn no extra Doom points nor Elder Signs.» | RITUAL | неважно | YES |
| IP-29 | Gla'aki, пробуждение (DOS F.5) | «3. Gain 1 Elder Sign.» | OTHER (прецедент) | Elder Sign при пробуждении у не-EG | n/a |

#### B.4. Нейтральные монстры

| ID | Источник | Цитата | Кат. | Как EG в оригинале | Слитая модель |
|----|----------|--------|------|--------------------|---------------|
| NM-01 | Elder Thing, Mind Control (DOS A.2 №8) + FAQ RB-NEW p.192 / FAQ-ONL | «If an Elder Thing shares an Area with an enemy Great Old One, the latter may not use its Special Ability.» / FAQ: «…This ability also works on Independent Great Old Ones (but only their special abilities, and not their Spellbooks). Nyarlathotep can't use Harbinger, Azathoth can be Killed with a single Kill result, and so on.» | COMBAT / COUNT | EG — GOO: гасится его Special Ability (Requires Attention, Healing, Subversion, Hellborn, Sunrise, Inferiority Complex). Фиксированный боевой эффект стоит в строке **Combat:**, а не в Special Ability; разъяснения нет — по раскладке карты, видимо, не гасится | **DEPENDS**: если «Киборг-убийца» и аналоги оформлены свойством того же класса, что Special Ability, Mind Control его гасит, и EG в бою становится нулём |
| NM-02 | Servitor of the Outer Gods (DOS A.2 №9) + FAQ RB-NEW p.193 | Combat −1; «If the presence of Servitors reduces my combat total to less than zero… Just leave it at zero.» | COMBAT | у стороны с EG и так 0; фиксированные результаты не зависят от кубиков | YES |
| NM-03 | Star Vampire, FAQ RB-NEW p.193 | «However, if your total dice are technically zero, you cannot Declare Battle.» | COMBAT | согласуется с F1 | YES |
| NM-04 | Giant Blind Albino Penguins (NEC-KS) | Combat −2; Laughingstock | COMBAT | как Servitor | YES |
| NM-05 | Leng Spider, Bloodthirst (DOS A.2 №6) | «you may exchange two Pain results for a Kill before results are assigned… applied to your results OR you opponent's» | COMBAT | фиксированные Pain EG конвертируются | YES |
| NM-06 | Voonith, Vicious (RB-OLD p.135) | «For each Kill you score fewer than the number of Vooniths involved in the Battle, add 1 Kill.» | COMBAT | фиксированный Kill EG — «score» | YES |
| NM-07 | Moonbeast, Blasphemous Obeisance | «place it on a Spellbook on an enemy's Faction Card. While the Moonbeast is on that Spellbook, that Spellbook cannot be used» | OTHER | заблокированный фракционный SB не даёт эффекта и через Proteus (вывод, не FAQ) | YES |

#### B.5. Terror

| ID | Источник | Цитата | Кат. | Как EG в оригинале | Слитая модель |
|----|----------|--------|------|--------------------|---------------|
| TR-01 | Общий блок, RB-NEW p.103 (Стр.108); ERR p.12 | «Monsters can protect Cultists against Terrors (and vice-versa), and Great Old Ones can still Capture a Cultist protected by a Terror.» | COUNT | EG захватывает и защищает как GOO (A.0 п.1) | YES |
| TR-02 | Great Race of Yith, Possession | «…you may Capture that Cultist regardless of the presence of any enemy Units or Great Old Ones…» | COUNT | защита EG игнорируется | YES |
| TR-03 | Cacodemon, Cosmic Terror (RB-OLD p.109) + FAQ RB-NEW p.193 | «Enemy Units may not Move or be Pained into the Area with the Cacodemon unless they are Great Old Ones or if they are accompanied by a Great Old One.» | COUNT | EG проходит и сопровождает | YES |
| TR-04 | Elder Shoggoth, Prime Cause (NEC-KS) | «You can gain a Faction Great Old One that was previously Awakened… 1. Pay half the new Unit's Power cost… 3. If the new Unit is a Great Old One, the enemy gains 1 Elder Sign.» | COUNT | Bastet доступна (6/2 = 3), враг +1 Elder Sign | YES |
| TR-05 | Junior Whateley, Transmogrification (NEC-DUN) | «replace Junior with any Great Old One (Neutral or Faction), ignoring all Awakening requirements, including cost.» | COUNT | EG годится. Даёт ли GW EG свой «+1 Elder Sign» без пробуждения по шагам — неясно в обеих моделях | YES |
| TR-06 | Gadarene, Mastermind (NEC-PA) | «you may Move all enemy Great Old Ones into an Area adjacent to their current Area» | COUNT | вражеские EG двигаются | YES |
| TR-07 | Hellhound, Hellbreath (NEC-PA) | «it still adds its attack to your total. However, it cannot more than double the number of dice you roll.» | COMBAT | у стороны с одним EG 0 кубиков → Hellhound добавляет 0 | YES |
| TR-08 | Hortator, Xhort (NEC-PA) | «add +1 Combat die for each other different type of Unit you have present.» | COMBAT | EG «treated as GOO» → тип GOO. Карта печатает тип «ELDER GOD», Petersen — «new type of unit» | **DEPENDS (слабо)**: если в оригинале читать EG отдельным типом, при EG и GOO в бою +2 кубика вместо +1. Слитая модель тип стирает |
| TR-09 | Philter, Catholicon (NEC-PA) | «the enemy loses 1 of his rolled Kill and 1 of his rolled Pain results before tallying results.» | COMBAT | фиксированные результаты EG не «rolled» → не трогаются | YES, если свойство EG в слитой модели «добавляет», а не «выбрасывает» |
| TR-10 | Mandrake, Doppleganger (NEC-PA) | «at least one enemy Kill and one enemy Pain are used to target his own Units» | COMBAT | включая фиксированные результаты EG | YES |

#### B.6. High Priests, Unique HP, клан Whateley, Prophetess, Investigators

| ID | Источник | Цитата | Кат. | Как EG в оригинале | Слитая модель |
|----|----------|--------|------|--------------------|---------------|
| HP-01 | Unique HP Lavinia Whateley, The Bride (RB-OLD p.147) + FAQ RB-NEW p.196 | «When you Awaken a Great Old One, you can choose to Eliminate Lavinia Whateley. If you do so, your Great Old One costs 3 fewer Power to Awaken.» | COUNT | скидка на EG действует (Nodens 3, Hagarg/GW 1; при Cthugha вычитается номинал заменяемого EG) | YES |
| HP-02 | The Prophetess, True Vision (RB-OLD p.153) | «Unit rank in order from lowest to highest is Cultist, Monster, Terror, Independent Great Old One, Faction Great Old One.» | COUNT | Bastet — ранг Faction GOO, IEG — ранг IGOO | YES |
| HP-03 | Investigator Tarang, Cowardice (RB-OLD p.162) | «If a Great Old One Moves into Tarang's Area, Tarang and all of your other Cultists in the area immediately retreat…» | COUNT | EG срабатывает | YES |
| HP-04 | Investigator Hannah, Loner (RB-OLD p.160) | «She adds 1 Pain to your combat totals and is unaffected by any results rolled by your enemy.» | OTHER (прецедент) | фиксированный результат у культиста | n/a |
| HP-05 | Lavinia (клан Dunwich), Bride of the Old Ones (NEC-DUN) | «If Lavinia shares an Area with any Great Old One (any Faction) at the start of an Action, she is immune…» | COUNT | EG засчитывается | YES |
| HP-06 | Lavinia (клан), Mother of Monsters | «pay half as much Power and/or Doom for any Independent Great Old One…» | COUNT | IEG за полцены | YES |
| HP-07 | Wizard Whateley, Magician | «you can immediately muster an Independent Great Old One; Neutral Monster, Terror, or Cultist…» | COUNT | IEG | YES |
| HP-08 | High Priests, советы (RB-NEW p.131–132) | «Recruit your High Priest in the first Action Phase, then Sacrifice him to enable you to Awaken your Great Old One…» | OTHER | — | YES |
| HP-09 | Asenath Waite (RB-OLD p.144) | «replace it with one of your own Units costing 3 or less» | OTHER | EG стоят 4+ → не применимо | n/a |

#### B.7. Карты поля

| ID | Источник | Цитата | Кат. | Как EG в оригинале | Слитая модель |
|----|----------|--------|------|--------------------|---------------|
| MP-01 | Dreamlands, Bhole (RB-NEW p.145, Стр.150) | «The Bhole is a Terror Unit. Additionally, while Spellbooks and abilities can be used in Battle against the Bhole, they can only affect your own Units… nor does Demand Sacrifice have any effect on the Bhole's dice results.» / «A single Kill result destroys the Bhole» | COMBAT | срез Kill у Bastet («her ability», F2) на кубики Bhole не действует; её +1 Kill — собственный результат, Bhole убивает | YES. Слабый риск: в слитой модели и +1 Kill — «свойство»; читается всё равно как собственный результат |
| MP-02 | BGG (цитата Dreamlands rulebook p.10, старое) | «Q. Does the Bhole increase Yog-Sothoth's Combat by 2? Does he count as an Enemy Great Old One…? A. Yes to all…» | OTHER | устарело: в RB-NEW Bhole — Terror | n/a |
| MP-03 | Dreamlands, Zoogs (RB-NEW p.146) | «Zoogs have 0 Combat, and so they never roll any Combat dice.» | COMBAT (прецедент) | — | в пользу слитой модели: в CW «Combat 0» и есть «не бросает кубиков» |
| MP-04 | Dreamlands, Zoogs | «Each Pain result likewise Eliminates a Zoog, but also Pains one of your Units in the Battle.» | COMBAT | фиксированные Pain EG отражаются | YES |
| MP-05 | Shaggai, Eradication (RB-NEW p.163, Стр.168) | «Each Faction Great Old One that is Eliminated also provides its owner with 1 Elder Sign. (Since Yog-Sothoth counts as a Gate, he provides 1 Power and 2 Elder Signs if Eliminated).» | RITUAL-adj. | Bastet даёт 1 Elder Sign: это не Ritual, исключение EG не действует | YES, **если пометка ограничена Ritual**. Если она звучит как «не даёт Elder Sign» вообще — NO |
| MP-06 | Shaggai, Cosmic Power (RB-NEW p.163) | «you can place any Spellbook (including those of the Independent Great Old Ones) simply by spending 6 Power…» / «you may bypass Area restrictions on Awakening or Summoning your Units by paying 2 additional Power» + особое правило Bubastis | COUNT | SB у IEG — тоже; Bastet не может «Pay 2» (прямо в правиле) | YES |
| MP-07 | Yuggoth, Watcher (RB-NEW p.173–174) | «The Watcher is a Great Old One. While Spellbooks and abilities can be used in Battle against it, they may only affect your own Units…» / «The defending Faction rolls Combat dice against the Watcher as normal; each Kill rolled drops the Watcher Token down 1 point.» / «As a Great Old One, however, the Watcher can provide Nyarlathotep with 2 Elder Signs…» | COMBAT / COUNT | срез Kill у Bastet не действует. Снижает ли фиксированный Kill EG Watcher'а («each Kill **rolled**») — не разъяснено | YES: неясность одна и та же в обеих моделях |
| MP-08 | Yuggoth, FAQ RB-NEW p.199 | «Does the Watcher count as an enemy Great Old One for Windwalker's Hibernate ability? … He is always considered an enemy Great Old One.» / «The Elder Things' Mind Control ability has no effect on the Watcher.» | COUNT | для Requires Attention у Bastet Watcher — «Enemy GOO» (+2 Elder Sign) | YES |
| MP-09 | Library at Celaeno, тома (WIKI-LIB) и Custodian/Librarian (RB-NEW p.152–153) | Barrier of Naach-Tith: «No other player may declare Battle against you unless…»; Larvae: «Gain 1 Elder Sign if any active Faction has more Power than you.» | OTHER | ссылок на GOO нет | n/a |
| MP-10 | Colour Out of Space (RB-NEW p.137–138) | «GREEN: The Gate's Controller earns an extra Elder Sign for a Ritual of Annihilation…» | RITUAL | к GOO не привязано → Bubastis получает | YES |

Primeval, Eradicators, Shining Trapezohedron, Unnameable, 6–11 player maps: ссылок на GOO нет.

#### B.8. Эррата и памятка

| ID | Источник | Цитата | Кат. | Как EG в оригинале | Слитая модель |
|----|----------|--------|------|--------------------|---------------|
| ER-01 | Player Hint Card, Ultimate Errata Pack p.14 (ERR) | «-1 Power to Battle (requires Unit with at least 1 Combat)» | COMBAT | EG сам Battle не объявляет (F1) | YES (сила 0) |
| ER-02 | там же | «Rituals of Annihilation in player order, earning +1 Doom per Controlled Gate and +1 Elder Sign per Faction Great Old One» | RITUAL | Bastet исключена правилом EG | YES (пометка) |
| ER-03 | `SRC-ERRATA__balance-changes-table` | Cthugha: эррата O2 к Spellbook (Firestorm) и к карте лояльности | OTHER | текст правки не найден | не проверено |

#### B.9. Официальные FAQ (вне фракций) с GOO

| ID | Источник | Цитата | Кат. | Как EG в оригинале | Слитая модель |
|----|----------|--------|------|--------------------|---------------|
| FQ-01 | F1 | «Can Elder Gods declare Battle since they have no Combat dice? A. No.» | EXPLICIT-EG | — | YES при силе 0. **NO**, если сила Nodens поднята через Proteus (EG-01): в слитой модели он объявит Battle один |
| FQ-02 | F2 | «Elder Gods just inflict results…» | EXPLICIT-EG | — | YES, если текст свойства не завязан на бросок |
| FQ-03 | F3 | Elder Sign за Ritual с Bastet | EXPLICIT-EG / RITUAL | — | YES |
| FQ-04 | F4 | Bastet + Yog-Sothoth = 3 Elder Sign | EXPLICIT-EG | — | YES |
| FQ-05 | F5 | Cthugha против EG | EXPLICIT-EG / COMBAT | — | см. IP-04 |
| FQ-06 | F6 | Nodens + Extinction | EXPLICIT-EG | — | YES (Proteus сохранён) |
| FQ-07 | F7 | Zagazig «does not affect Bastet's Combat»; карта Zagazig: «all rolled Pains become Kills, and all rolled Kills become Pains» (NEC-BUB) | EXPLICIT-EG | фиксированный Kill не «rolled» | YES |
| FQ-08 | RB-NEW p.186 (Стр.191); FAQ-ONL | «Q. To Awaken an Independent Great Old One, you need a Controlled Gate and your own Great Old One. Does Yog-Sothoth, by himself, fulfill both these requirements? A. No, because Yog-Sothoth is not technically a Controlled Gate.» | COUNT | Bastet на Луне выполняет оба условия: Луна «counts as … a Bubastis-Controlled Gate for all purposes» | YES |
| FQ-09 | RB-NEW p.188 | «How do the Ancients generally interact with requirements… necessitating all Factions to have a Great Old One? A. The Ancients are ignored for this purpose…» | COUNT | Bubastis не игнорируется; Bastet засчитывается | YES |
| FQ-10 | RB-NEW p.194; FAQ-ONL | «Nyarlathotep can get at most 2 Elder Signs when fighting Azathoth.» | COUNT (аналог) | — | n/a |
| FQ-11 | RB-NEW p.195 (Nyogtha) | «If only one of the two Nyogtha Units is Killed or Eliminated in Battle, does this trigger any effects related to the Elimination of a Great Old One? A. Yes.» | COUNT | n/a | n/a |
| FQ-12 | RB-NEW p.191; FAQ-ONL | «You may NOT use Recriminations in conjunction with any Independent Great Old One Spellbooks» | OTHER | SB у IEG — тоже | YES |
| FQ-13 | RB-NEW p.189 (Tcho-Tcho, фракционный) | «Hierophants … It reads "Faction Spellbooks."» — SB у IGOO не считаются | OTHER | SB у IEG — тоже | YES |
| FQ-14 | RB-NEW p.185 (Opener, фракционный) | «Do enemy Great Old Ones still cancel Beyond One… And do enemy Independent Great Old Ones still cancel it, too? What about the Watcher…? A. Yes, to all three.» | COUNT | вражеский EG отменяет | YES |
| FQ-15 | RB-NEW p.193 (Cacodemon) | «If my Great Old One shares an enemy Cacodemon's Area, can I pain other non-Great Old One Units into that Area? A. No.» | COUNT | — | YES |

#### B.10. Сообщество (BGG, низкое доверие)

| ID | Цитата | Слитая модель |
|----|--------|---------------|
| CM-01 | «Q: Does an Independent Great Old One count as the GOO with the controlled Gate to Awaken a new IGOO? A: Yes…» | YES (то же для IEG) |
| CM-02 | «Q: Do Independent Great Old Ones count towards the Share Area with Enemy GOOs requirement? A: Yes they do, if they're controlled by another Faction.» | YES |
| CM-03 | Тред «They Break Through…»: «The Hellmother's ability to place monsters instead of summoning them.» — взаимодействие с требованиями Ancients, без ответа | n/a |

#### B.11. Механики самих EG против шаблона «GOO, сила 0, свойство, нет Elder Sign за Ritual»

| ID | Механика | Оригинал | Слитая модель |
|----|----------|----------|---------------|
| EG-01 | **Proteus (Nodens) копирует фракционный SB, поднимающий силу названного юнита.** Проверенные примеры: Frenzy (Black Goat) «Your Cultists now have 1 Combat.»; Absorb (Great Cthulhu) «…add 3 dice to the Shoggoth's Combat for that Battle.»; Savagery (Bubastis) «Pay 1 Power to increase the Combat of all Cats from Saturn by 4 for this Battle.» (тексты — NEC-страницы фракций) | По букве: «(Nodens doesn't roll any Combat Dice)» и «Elder Gods never roll Combat dice» → кубиков он не получает. Официального ответа нет | **NO**: 0 → 1 / 3·n / 4 кубика. Следом расходятся FQ-01 (Battle в одиночку) и IP-04 (что копирует Cthugha). Копии уровня стороны совпадают: Red Sign — +1 к Shub; Terror (Tcho-Tcho) — +1 к сумме за Proto-Shoggoth. Не-боевые копии тоже совпадают (Extinction, F6) |
| EG-02 | GW EG: «Gain 1 Elder Sign» при пробуждении | обычный шаг пробуждения, как у Cthulhu/Hastur IGOO, Dire Cthulhu, Gla'aki | YES, если пометка — только про Ritual |
| EG-03 | Переменный фиксированный эффект: Hellmother — от числа культистов и порога 6; Thunder King — от числа SB и порога 6 | формула в строке Combat | YES: формула переезжает в текст свойства; ничего, кроме Cthugha, «Combat» EG не читает, а F5 закрывает Cthugha |
| EG-04 | Защитная часть Bastet: на карте «the enemy must lower their Kill total by 1», в FAQ F2 — «enemy-rolled Kills» | против фиксированного Kill другого EG (Nodens, Sun God…) неоднозначно уже в оригинале | **DEPENDS** от формулировки свойства в Oil Wars: «итог» или «выброшенные» |
| EG-05 | Sun God, Sunrise — «cannot be killed or eliminated» | обычная особая способность | YES. Mind Control (NM-01) её гасит в обеих моделях |
| EG-06 | «Elder God» как отдельный печатный тип (карта; маркетинг «new type of unit») против «treated as GOO for all purposes» | по правилам — тип GOO | DEPENDS (слабо), см. TR-08 |
| EG-07 | Где стоит фиксированный эффект: строка Combat против Special Ability | в оригинале — Combat | **DEPENDS**, см. NM-01 |
| EG-08 | Объявление Battle | F1: нет | YES при силе 0; ломается только через EG-01 |

---

### C. Сводка расхождений

**NO**
1. EG-01 Proteus + SB, поднимающий силу юнита → в слитой модели Nodens бросает кубики; следом FQ-01 и IP-04.

**DEPENDS**
2. NM-01 Elder Thing / Mind Control — зависит от того, считается ли боевое свойство EG «Special Ability».
3. MP-05 Shaggai Eradication — зависит от того, ограничена ли пометка «нет Elder Sign» Ritual'ом. То же для FI-03 Harbinger и IG-06 Cthulhu.
4. EG-04 срез Kill у Bastet — «итог» или «выброшенные».
5. IP-04 Cthugha — только при изменённой силе EG.
6. TR-08 Hortator / EG-06 — «Elder God» как отдельный тип юнита; риск низкий.
7. TR-09 Philter, IP-12 Haunter, FQ-02 — совпадают, пока свойство EG «добавляет результат к итогу», а не «выбрасывается».

Всё остальное — YES.

### D. Пробелы

- Требование SB у Hagarg «You have 0 Power» — из DOS; сегодня повторно не извлечено.
- Код продукта Gods War crossover не найден.
- Вики (Strategy/Category Independent Elder Gods, Nodens, Elder Races/CW) — HTTP 402. Другие EG, кроме шести, не исключены на 100 %, но на NEC их нет.
- Официальных FAQ по Proteus (кроме F6), Hagarg, GW EG и Mind Control против EG нет.
- Тексты эрраты Cthugha (O2) не найдены.
- Карты сверены по транскрипциям NEC и RB-OLD, не по сканам.


---

# Таблица 3. «Нефтяные войны»: книга, планшеты, карты, наёмники, прочие компоненты


Дата: 2026-10-01. Только чтение, ничего не правилось.

**Что прочитано.** `rules/RULEBOOK.md` целиком (2443 строки). Все 8 файлов `print/Faction-Card-A/Данные/*.json`. Тексты карт задач и технологий из `cards-text.tsv`, сверены с `print/Saved/Cards - Технологии и задачи.json`. `rules/registry/mercenaries.yaml` (роботы и пул), а также `print/Mercenaries/Наёмники.html`. Компоненты: `print/Памятка.html`, `print/Памятка — битва.html`, `print/FactoryEvents.html`, `print/Контроль сети.html`, `print/Энграммы.html`, `print/UniqueColonel/uc.md`. Реестры (поиск по «робот», «Elder», «Зардоз», «Bastet»): `factions.yaml`, `terms.yaml`, `numbers.yaml`, `baseline.yaml`, `issues.yaml`, `redesign.yaml`. Решения D-011, D-045, D-052, D-057, D-073, D-077, D-079, D-083, D-085, D-106. Плюс `STATE.md`. Источники оригинала: `source/cthulhu-wars/SRC-RB-NEW` (с. 70–71, FAQ с. 182–183), `SRC-RB-OLD`, `SRC-WIKI`, `source/web/SRC-WEB-LOYALTY`.

**Эталон оригинала.** Bastet — Elder God. Elder God считается GOO во всём, кроме двух пунктов: он не даёт собственного Elder Sign за ритуал и никогда не бросает боевых кубиков, вместо этого давая фиксированный эффект. Он блокирует захват, захватывает сквозь Monster, а Harbinger против него работает как против обычного GOO. FAQ уточняет: Elder God не может объявить битву; Bastet в одиночку всё равно наносит свой Kill и снимает 1 Kill с броска противника; Zagazig не влияет на бой Bastet; Bastet рядом с Yog-Sothoth при Requires Attention даёт 3 Elder Sign; ритуал без Requires Attention даёт только 1 Doom. Текст боя Bastet в формулировке D-057: «Add 1 Kill to your combat total (Bastet rolls no dice); the enemy must lower their Kill total by 1».

**Легенда.** Значения столбца «Совпадает?»:
- **ДА** — поведение совпадает;
- **ДА\*** — совпадает только благодаря приоритету компонента над книгой (§3.9);
- **НЕТ** — расходится;
- **ЗАВИСИТ** — исход зависит от прочтения, порядка эффектов или непроверенного факта;
- **н/п** — к «Зардозу» на практике не применяется, совпадение формальное.

---

### A. `rules/RULEBOOK.md`

| № | Файл и место | Цитата | Что проверяет | «Зардоз» по нашему тексту | Bastet по оригиналу | Совпадает? |
|---|---|---|---|---|---|---|
| A1 | §1.2, стр. 62–74 | «фигурки отрядов: … и 1 боевой робот… у одной фракции два боевых робота, у другой его нет вовсе» | подсчёт (состав) | единственный БР Moon, 1 шт. | 1 Bastet | ДА |
| A2 | §1.3 Ж, стр. 102–105 | «Боевой робот. Силуэт, стоимость, боевая сила и описание особенностей… здесь же напечатаны условия» | прочее | блок БР на планшете: стоимость 6, сила 0, блок создания | на карте фракции категория «ELDER GOD», бой «*» | ДА. Категория Elder God на планшете не названа: по D-011 это свойство БР, а не тип |
| A3 | §3.5, стр. 347–348 и 382–385; §13 «Отряд» (2297) и «Боевой робот» (2195–2198) | «Отряд — это пехотинец, боевая машина, мех или боевой робот»; «Способности и технологии, адресованные пехотинцам и боевым машинам, на боевого робота не распространяются» | тип отряда / цель | обычный БР, подтипа в книге нет | Elder God = GOO «for all purposes except» двух пунктов | ДА по D-011. Оба исключения в книге не названы вовсе, они живут только на планшете |
| A4 | §3.5, стр. 377–380; §7.3.7, стр. 1068–1104; §13 «Мех» (2259–2263); Памятка, «Захват» | «боевой робот пробивает и то, и другое прикрытие»; «От боевого робота защищает только боевой робот»; «Захват — не битва… Боевая сила не учитывается» | захват | захватывает пехотинца (в том числе энграмму) сквозь прикрытие БМ или меха; сам прикрывает своих от вражеских БР; сила 0 не мешает | «can block Unit Captures… Capture Cultists even if an enemy Monster is present» | ДА |
| A5 | §3.5, стр. 387–388; §7.3.3, стр. 983–985 | «Боевая сила у любого отряда может быть задана как числом, так и формулой»; «Боевая сила у роботов своя… идёт в общую сумму (8.4)» | сила | число 0, в сумму идёт 0 | числа нет, «never roll Combat dice» | ДА сейчас. По смыслу «0» и «не бросает» различаются, см. раздел G |
| A6 | §3.6, стр. 402–405; §13 «Контроль фабрики» (2244) | «Боевые машины, мехи и боевые роботы контролировать фабрику не могут» | прочее | не контролирует | GOO не контролирует Gate | ДА |
| A7 | §3.6, стр. 418–424 | «она не закрывает собой два требования разом… при создании наёмного боевого робота» | условие | касается «Шрёдингера». «Зардоз» вместе с Луной (тайл, не отряд) закрывает условие «фабрика + ваш БР» | прямое чтение «treated as GOO for all purposes» (SRC-WEB-LOYALTY E.2), официального ответа нет | ДА (вывод, а не источник) |
| A8 | §3.9, стр. 494–499; §7.3.3, стр. 979–981 | «собственная способность вашего боевого робота, действующая, пока он в игре» | прочее | «Взлом систем» и «Киборг-убийца» работают, пока он в игре | Requires Attention и боевой эффект — свойства Bastet | ДА |
| A9 | §3.9, стр. 549–552 | «Если текст карты или планшета расходится с общим правилом этой книги, действует текст карты или планшета» | механизм | только он даёт силу сноске и «Киборгу-убийце» против §6.3 и §8.5 | Elder God описан в разделе фракции, то есть тоже частное правило | ДА (опора всех строк ДА\*) |
| A10 | §4.1, стр. 611–612 и планшет Moon, «Альтернативные источники энергии» (стр. 45–48) | «Боевые машины, мехи и боевые роботы, за редкими исключениями, нефти не дают»; «Получите 1{R} за каждую вашу боевую машину в игре» | подсчёт (нефть) | нефти не даёт | SRC-WIKI: «Все кошки дают по 1 Power». Даёт ли Power сама Bastet, дословно не найдено. Условие «All your Cat varieties» отделяет её от кошек | ЗАВИСИТ: не проверено дословно, D-052 принял 1:1 |
| A11 | §6.3 шаг 4, стр. 735–737 | «Получите карту скрытого влияния… за каждого боевого робота своей фракции {ROBOT} в игре. Наёмные боевые роботы скрытого влияния не дают» | давление | по книге дал бы карту; сноска планшета отменяет | «do not provide an inherent Elder Sign» | ДА\* |
| A12 | §6.3, пример, стр. 739–743 | «За своего боевого робота он берёт карту скрытого влияния» | давление | для Moon пример без сноски неверен | — | ДА\* |
| A13 | §6.4, стр. 750–751 | «оказание давления: карта за каждого своего боевого робота в игре» | давление | как A11 | как A11 | ДА\* |
| A14 | §6.7, стр. 817–819 | «оказывают давление по обычным правилам… и получают скрытое влияние как обычно» | давление | сноска действует и при Ядерной катастрофе | — | ДА\* |
| A15 | §6.3, стр. 719–722 и 732–733; §3.9, безусловное «одна возможность оказать давление за фазу»; «Взлом систем» | «способность может изменить то, что давление приносит, но оказать его дважды за фазу нельзя»; шаг 3 «1 пункт за каждую военную фабрику» | давление | давление через «Зардоза» остаётся единственным давлением фазы; вместо шага 3 ровно 4 влияния | FAQ: «flat 4 Doom bonus»; «a non-Requires Attention ritual only ever adds 1 Doom» | ДА (D-045, D-052). Замену шага 3 книга сама разрешает |
| A16 | §7.3.1, стр. 932–934 | «в регион, где у вас есть любой свой отряд — пехотинец, боевая машина, мех или боевой робот» | условие | даёт право вербовки, но вербовать Moon некого: андроиды — БМ, энграммы не вербуются | GOO даёт то же право, Cultists у Bubastis нет | ДА (н/п) |
| A17 | §7.3, таблица (стр. 920); §7.3.3, стр. 966–977; Памятка, «Создание боевого робота» | «Стоимость и условия указаны на планшете… Шагов всегда не меньше двух… ровно один боевой робот» | создание | три шага: все виды БМ в игре → 6{R} → регион без вражеских отрядов | «All your Cat varieties are in play. Pay 6 Power. Place Bastet in an Area containing no enemy Units» | ДА |
| A18 | §7.3.3, стр. 983–984 | «одной назначенной ему смерти достаточно, чтобы убрать его с поля» | битва | уходит с одной смерти | как GOO | ДА |
| A19 | §7.3.6, стр. 1036–1040; таблица §7.3 (стр. 923); §8.1, стр. 1287–1295; Памятка, «Битва» | «боевая сила не менее 1 — то есть вы должны быть в состоянии бросить хотя бы один боевой кубик. Иначе битву объявить нельзя, даже если у ваших отрядов есть боевые эффекты» | объявление битвы | один, или вместе с андроидами с силой 0, битву не объявляет; «Киборг-убийца» не помогает | FAQ: «Can Elder Gods declare Battle…? No.» | ДА сейчас. Держится на «силе 0», а не на «не бросает кубиков», см. G |
| A20 | §7.3.6, стр. 1042–1043 | «атаковать врага с боевой силой 0 можно» | объявление битвы | «Зардоза» атаковать можно | можно | ДА |
| A21 | §7.4, стр. 1112–1114 | «уникальное действие боевого робота недоступно, пока сам робот не создан» | условие | своего уникального действия нет; «Орбитальной катапульте» по тексту нужен «Зардоз» на поле | Catnapping так же | ДА |
| A22 | §8.3, стр. 1334–1342 | «ни один его боевой эффект больше не применяется: ни тактический, ни финальный» | битва | выведенный до бросков «Зардоз» «Киборга-убийцы» не даёт. Сейчас ни один компонент его тактически не выводит: «Стелс», «Диверсия», «Камикадзе» бьют только по пехотинцам и БМ | Invisibility, Devour, Abduct бьют по Monster и Cultist | ДА |
| A23 | §8.4, стр. 1367–1368 и 1393–1394; §13 «Боевая сила» (2180–2186); Памятка — битва, «Сражение» | «У части отрядов она равна 0»; «Каждая сторона бросает столько кубиков, сколько у неё боевой силы. Сторона с боевой силой 0 не бросает ничего»; «Боевая сила. Число боевых кубиков» | сила / кубики | 0 кубиков; смерть добавляет «Киборг-убийца» «даже если кубики не бросались» | «Elder Gods just inflict results. They don't roll dice» | ДА сейчас, см. G |
| A24 | §8.4, стр. 1378–1380 | «например, боевая сила равна … числу вражеских боевых роботов» | подсчёт | в счёте как вражеский БР (сила «Шрёдингера») | «treated as GOO for all purposes» — в счёте (D-073) | ДА |
| A25 | §8.4, стр. 1417–1420 | «“Битва. Сражение”. Обычно они действуют одновременно; если порядок важен, первым применяет атакующий» | порядок эффектов | Moon атакует Сайнтифик Солюшн: −1 смерть снимается с выброшенного раньше «Временного сдвига», и новые шестёрки от переброса уже не уменьшаются. Moon защищается — порядок обратный | «lower their Kill total by 1» (итог); FAQ о связке Channel Power и Bastet не найден | ЗАВИСИТ |
| A26 | §8.5, стр. 1424–1427; Памятка — битва, такт 1 | «Каждая сторона разбирает выпавшие противником результаты и распределяет их по своим собственным отрядам» | назначение | смерть «Зардоза» не «выпавшая»; назначается только потому, что планшет велит «добавьте 1 смерть к своему результату» | «Add 1 Kill to your combat total» | ДА\* |
| A27 | §8.5, стр. 1444–1447 | «Эффекты, говорящие о выброшенных результатах, — они читают кубики так, как те выпали» | смена типа результата | смерть «Зардоза» не выброшена, «Системный сбой» её не трогает | «Zagazig… does not affect Bastet's Combat» | ДА |
| A28 | §8.5, стр. 1466–1477; §13 «Смерть» (2380–2383); Памятка — битва, «Смерть и уничтожение» | «Через смерть — только от выпавшей шестёрки»; «Смерть. Результат броска 6 в битве, и только он»; «Смерть — только выпавшая на боевом кубике 6» | определение | добавляет смерть без шестёрки. По определению книги это не смерть, по планшету — смерть | Kill Bastet — полноценный Kill | ЗАВИСИТ: книга и памятка противоречат планшету. Держится на §3.9, а для памятки — только на неписаном «частное над общим» |
| A29 | §8.5, стр. 1479–1494 | «Один отряд — один результат… Лишние результаты игнорируются» | назначение | его смерть — обычный результат, лишняя пропадает | так же | ДА |
| A30 | §11.4.3, стр. 1883–1886 и 1893–1895 | «контролируемая вами фабрика стояла в одном регионе с вашим боевым роботом… можно использовать как робота своей фракции» | создание наёмного | годится. Единственная фабрика Moon — Луна; «Зардоз» туда заходит, наёмник ставится на Луну (MRC-I-011) | прямое чтение (E.2), «это вывод, а не источник» | ДА (вывод) |
| A31 | §11.4.3, стр. 1897–1902 | «Если… наёмный боевой робот убит… Условие здесь — именно смерть, то есть назначенный в битве результат» | смерть | его смерть, назначенная вражескому наёмнику, отбирает карту лояльности: здесь смерть — «назначенный результат» | Kill Bastet убивает IGOO | ДА |
| A32 | §11.4.3, стр. 1917–1918 | «вы не получаете карт скрытого влияния за наёмных боевых роботов. Только за роботов своей фракции» | давление | по книге как робот своей фракции дал бы карту; сноска отменяет | не даёт | ДА\* |
| A33 | §11.4.3, стр. 1924–1927 и MRC-R-10 | «Фракционный робот в роли наёмного» | прочее | карты нет | карты Independent Bastet нет | ДА |
| A34 | §13 «Оказание давления», стр. 2281–2285 | «берёте карту скрытого влияния за каждого боевого робота своей фракции» | давление | как A11 | как A11 | ДА\* |
| A35 | Вступление (33); §3.6 (395); §12 (2135, 2140); §13 «Военная фабрика» (2216) | «строят боевых роботов», «а иногда и боевых роботов», советы | прочее | правил не задаёт | — | ДА (н/п) |

### B. Планшеты (`print/Faction-Card-A/Данные/*.json`)

| № | Файл и место | Цитата | Что проверяет | «Зардоз» по нашему тексту | Bastet по оригиналу | Совпадает? |
|---|---|---|---|---|---|---|
| B1 | Moon Systems.json, блок «Создание БР “Зардоз”», стр. 25–29 | «В игре присутствуют все виды ваших боевых машин. / Заплатите 6{R}. / “Зардоз” появляется в любом регионе, где нет вражеских отрядов.» | создание | см. A17 | см. A17 | ДА |
| B2 | Moon Systems.json, таблица, стр. 109–115 | «“Зардоз”… стоимость 6, сила 0» | сила | 0 | «*» | ДА сейчас, см. G |
| B3 | Moon Systems.json, сноска, стр. 118 | «“Зардоз” не приносит карту скрытого влияния при оказании давления.» | давление | карты нет | «do not provide an inherent Elder Sign» | ДА |
| B4 | Moon Systems.json, «Киборг-убийца» (Битва. Сражение), стр. 63–66 | «добавьте 1 смерть к своему результату, даже если кубики не бросались, а из выброшенного противником вычтите 1 смерть (не подавление)» | сила / результат | +1 смерть без кубиков, −1 с выброшенных смертей противника; работает и в одиночку | «Add 1 Kill… the enemy must lower their Kill total by 1»; FAQ «reduce the enemy-rolled Kills by 1», «if Bastet is alone… still» | ДА, с оговорками A25, A28, C2 |
| B5 | Moon Systems.json, «Взлом систем», стр. 53–58 | «вы можете оказать давление через него… ровно 4 влияния… фабрика под контролем противника — карту… хотя бы один вражеский боевой робот — ещё две карты» | давление | 4 влияния; +1 карта; +2 карты | FAQ: 4 Doom flat; Bastet рядом с Yog-Sothoth даёт 3 ES; ещё одни вражеские врата награду не увеличивают | ДА по FAQ. Полного английского текста Requires Attention в `source/` нет; входят ли наёмные во «вражеский БР», не проверено |
| B6 | Moon Systems.json, «Альтернативные источники энергии», стр. 45–48 | «Получите 1{R} за каждую вашу боевую машину в игре.» | подсчёт (нефть) | «Зардоз» не БМ, нефти не даёт | см. A10 | ЗАВИСИТ |
| B7 | Островная Империя.json, «Эффективное производство», стр. 30–35 | «Всякий раз, когда вы создаёте любого боевого робота, получите карту скрытого влияния.» | создание | ОИ «Зардоза» создать не может: карты наёмника нет | Cthulhu получает ES за пробуждение любого GOO; Independent Bastet нет | ДА (н/п) |
| B8 | Островная Империя.json, «Диверсия», стр. 47 | «уничтожает одну из своих боевых машин или одного из своих пехотинцев» | цель | не цель | Devour бьёт по Monster и Cultist | ДА |
| B9 | Эйркрафт Корпорейшн.json, «Военные трофеи», стр. 51 (и MRC-R-02) | «за каждого вражеского боевого робота (в том числе наёмного), которому назначена смерть или подавление… половину стоимости… или 2 карты» | цель / награда | в счёте: 3{R} или 2 карты | «Nyarlathotep gets 2 Elder Signs or half-Power cost from his Harbinger ability compared with that of other Great Old Ones» | ДА |
| B10 | Глобал Петролеум.json, «Эффективность», стр. 58 (и MRC-R-04) | «вы, а не владелец, назначаете результаты боя вражеским отрядам» | назначение | смерть можно назначить «Зардозу» | Vengeance — любым врагам, Bastet тоже | ДА |
| B11 | Глобал Петролеум.json, таблица, стр. 112 | «“Шепард”… сила 0» | сила | — | King in Yellow: combat 0, обычный GOO, ES даёт | ДА. Наблюдение для G: «сила 0» есть и у обычного БР, «Зардоза» выделяет только сноска |
| B12 | Клонэйд Ресёрч.json, «Аватар», стр. 42 (и MRC-R-05) | «хотя бы один пехотинец или боевая машина» | цель | обменять нельзя | Avatar бьёт по Monster и Cultist | ДА |
| B13 | Сайнтифик Солюшн.json, «Пространственный сдвиг», стр. 24 (и MRC-R-06 «Квантовый скачок») | «нет вражеских боевых роботов (в том числе наёмных)» | условие | блокирует | Beyond One: «no enemy Great Old One» — блокирует | ДА |
| B14 | Сайнтифик Солюшн.json, сноска, стр. 111 | «n — сила отряда равна удвоенному числу вражеских боевых роботов в игре. Наёмные… не считаются.» | сила (подсчёт) | +2 к силе «Шрёдингера» | «twice the number of enemy-controlled Faction GOO» — Bastet в счёте (D-073) | ДА |
| B15 | Сайнтифик Солюшн.json, «Мобильная военная фабрика», стр. 44, вместе с «Взломом систем» | «“Шрёдингер” считается фабрикой для любых целей» | давление | фабрика противника + вражеский БР = 3 карты | FAQ: «Bastet… with Yog-Sothoth… 3 Elder Signs? Yes» | ДА |
| B16 | карта САА «Внедрение агентуры» (packs[11]) | «Если в ней назван боевой робот этой фракции, для вас она говорит о “Биг Тексе”» | прочее | уникальная способность Moon БР не называет | FAQ Ancient Sorcery против Bubastis: «Nothing» | ДА (н/п) |
| B17 | Братство Сингулярности.json, сноска, стр. 104 | «у Братства нет боевых роботов… не требуется собственный боевой робот» | прочее | — | — | ДА (н/п) |

### C. Карты задач и технологий (`cards-text.tsv` / `Cards - Технологии и задачи.json`)

| № | Файл и место | Цитата | Что проверяет | «Зардоз» по нашему тексту | Bastet по оригиналу | Совпадает? |
|---|---|---|---|---|---|---|
| C1 | Moon, «Системный сбой» (packs[7]/1, Битва. Тактическая подготовка) | «у обеих сторон все выброшенные смерти считаются подавлениями, а все выброшенные подавления — смертями» | смена типа | его смерть не меняется (D-057) | Zagazig «does not affect Bastet's Combat» | ДА |
| C2 | то же вместе с «Киборгом-убийцей» | «из выброшенного противником вычтите 1 смерть» | порядок | −1 снимается в «Сражении» с выброшенных шестёрок, до переворота по §8.5 (группа 1). В итоге у противника на одно подавление меньше, а смертей — сколько выпало подавлений | «lower their Kill total by 1»: до или после Zagazig — FAQ не отвечает | ЗАВИСИТ |
| C3 | Moon, «Орбитальная катапульта» (packs[7]/3) | «Перенесите на Луну все отряды любых фракций, кроме “Зардоза”, из региона, где находится “Зардоз”» | цель / условие | остаётся на месте, вражеские БР уезжают на Луну | Catnapping («except for Yog-Sothoth via Catnapping») | ДА по D-079 (текст Catnapping взят с вики, в `source/` его нет) |
| C4 | Moon, «Технофобия» (packs[7]/5) | «За каждый тип ваших боевых машин» | подсчёт | не в счёте | Ailurophobia: «Monster Cat Variety» | ДА |
| C5 | Moon, задача 3 (packs[6]/2) | «В стартовом регионе каждого из противников есть ваша боевая машина» | условие | не подходит | Cat ≠ Bastet (D-079) | ДА |
| C6 | Moon, задача 6 (packs[6]/5) | «Создать боевого робота “Зардоз”.» | создание | — | «Awaken Bastet» | ДА |
| C7 | Задачи «Создать боевого робота …» прочих фракций (packs 0/4, 2/5, 4/0, 4/4, 8/5, 10/5, 12/5) | — | создание | — | — | ДА (н/п) |
| C8 | Эйркрафт, «Манёвренность» (packs[3]/3) | «Если в битве не участвует ни один вражеский боевой робот, в том числе наёмный» | условие | его участие отключает карту | Emissary: Bastet = enemy GOO | ДА |
| C9 | Эйркрафт, «Камикадзе» и «Стелс» (packs[3]/0–1) | «одного своего пехотинца или одну боевую машину»; «одного пехотинца или одну боевую машину любой из сторон» | цель | не цель | Abduct и Invisibility бьют по Monster и Cultist | ДА |
| C10 | Сайнтифик Солюшн, задача 5 (packs[12]/4), и задача наёмного MRC-R-06 | «Ваш боевой робот находится в одном регионе с вражеским боевым роботом. Наёмные боевые роботы тоже подходят» | условие | подходит как вражеский БР | «Your GOO… same Area as an enemy GOO» — Bastet в счёте | ДА |
| C11 | Сайнтифик Солюшн, «Пушка Гаусса» (packs[13]/3) | «Распределите выпавшие результаты… Это не битва: боевые эффекты не применяются» | цель | смерть можно назначить ему; «Киборг-убийца» не работает | Dread Curse — так же | ДА |
| C12 | Сайнтифик Солюшн, «Временной сдвиг» (packs[13]/0, Битва. Сражение) | «После своего броска вы можете заплатить 1{R} и перебросить все свои кубики с промахами» | порядок | см. A25 | см. A25 | ЗАВИСИТ |
| C13 | САА, «Санкции» (packs[11]/4) | «все его смерти в этой битве становятся подавлениями» | смена типа | если Moon выберет этот вариант, смерть «Зардоза» тоже станет подавлением, но лишь при условии, что это «смерть» (A28) | Demand Sacrifice: «All of their Kill results»; FAQ — превращённые тоже | ДА при чтении планшета, зависит от A28 |
| C14 | САА, «Эффективный захват» (packs[11]/2) | «может захватывать вражеские боевые машины так же, как пехотинцев» | захват | прикрывает БМ Moon от «Биг Текса» (§7.3.7) | «they can block Unit Captures» | ДА |
| C15 | Братство, «Жертва» (packs[15]/5) | «противник уничтожает одного своего боевого робота, участвующего в этой битве» | цель | годится | Unholy Ground: enemy GOO, Bastet тоже | ДА |
| C16 | Островная Империя, задачи 1–2 (packs[0]/1–2) | «Убить или уничтожить “Диверсией” вражеский отряд» | цель | обычный вражеский отряд | — | ДА (н/п) |

### D. Наёмники (`rules/registry/mercenaries.yaml`, `print/Mercenaries/Наёмники.html`)

| № | Файл и место | Цитата | Что проверяет | «Зардоз» по нашему тексту | Bastet по оригиналу | Совпадает? |
|---|---|---|---|---|---|---|
| D1 | MRC-R-01…07, `creation.text_draft[0]`; Наёмники.html, стр. 200, 240, 287, 330, 370, 415, 458 | «Ваш боевой робот находится в регионе с контролируемой вами фабрикой.» | создание наёмного | см. A30 | см. A30 | ДА (вывод) |
| D2 | MRC-R-06 «Шрёдингер», `combat_note`; Наёмники.html, стр. 413 | «n — число вражеских боевых роботов в игре. Наёмные боевые роботы не считаются.» | сила | +1 | «enemy Faction GOOs (not counting Independent)» — Bastet в счёте | ДА |
| D3 | MRC-R-07 «Биг Текс», `combat_note`; Наёмники.html, стр. 456 | то же | сила | +1 | то же | ДА |
| D4 | MRC-R-02 «Спрут», технология «Военные трофеи» | см. B9 | цель | см. B9 | см. B9 | ДА |
| D5 | MRC-R-04 «Чёрный вихрь», технология «Эффективность» | см. B10 | назначение | см. B10 | см. B10 | ДА |
| D6 | MRC-R-01 и MRC-R-04, шаг «Получите карту скрытого влияния» | — | создание | к «Зардозу» не относится | — | ДА (н/п) |
| D7 | MRC-R-10 «Зардоз», `status: NO-SOURCE` | «Карты независимого для Bastet (Elder God) нет ни в одном источнике» | прочее | карты нет | карты нет | ДА |

### E. Прочие компоненты

| № | Файл и место | Цитата | Что проверяет | «Зардоз» по нашему тексту | Bastet по оригиналу | Совпадает? |
|---|---|---|---|---|---|---|
| E1 | `print/Памятка.html`, стр. 163 (фаза влияния) | «по карте скрытого влияния за каждого боевого робота своей фракции в игре» | давление | по памятке дал бы карту | не даёт | ЗАВИСИТ: компонент против компонента. §3.9 решает только спор «книга против карты или планшета»; правило «частное над общим» есть лишь в CLAUDE.md |
| E2 | `print/Памятка.html`, стр. 169 (общие действия) | «Ваша боевая сила там должна быть не менее 1»; «боевой робот — если не прикрывает боевой робот»; «Выполните шаги, указанные на вашем планшете» | битва / захват / создание | как A19, A4, A17 | как там | ДА |
| E3 | `print/Памятка — битва.html`, стр. 182 | «Каждая сторона бросает столько кубиков, какова суммарная боевая сила её отрядов в битве. В этот момент срабатывают эффекты “Битва. Сражение”» | кубики | 0 кубиков, эффект срабатывает | — | ДА |
| E4 | `print/Памятка — битва.html`, стр. 204 | «Смерть — только выпавшая на боевом кубике 6.» | определение | см. A28 | — | ЗАВИСИТ |
| E5 | `print/FactoryEvents.html`, ✚05 и ⬢07 на картах «Волатильность рынков» и «Сбой поставок» (стр. 41, 43, 77, 79) | «должен уничтожить свою боевую единицу в регионе с фабрикой» | цель | «Боевая единица» в книге не определена. Если это «отряд», «Зардоз» выбрать можно. Moon контролирует особую фабрику только энграммой | «уничтожает свой отряд на вратах» (Unit, GOO и Elder God тоже) | ЗАВИСИТ (термин) |
| E6 | `print/FactoryEvents.html`, ✚05 и ⬢07 на «Профиците» и «Дестабилизации биржи» (стр. 23, 25, 59, 61) | «боевую машину или пехотинца противника с самой низкой стоимостью» | цель | не цель | «Monster or Cultist» | ДА |
| E7 | `print/Контроль сети.html` | БР не упоминаются (только «Шрёдингер» как фабрика) | — | Рой считается БМ и от захвата «Зардозом» не прикрывает | — | ДА (н/п) |
| E8 | `print/Энграммы.html`, вариант Moon, стр. 182–183 | «Андроиды не контролируют фабрики: первую энграмму вы получите только перепрошивкой.» «В отличие от андроидов, её можно захватить.» | захват | перепрошивка = захват; «Зардоз» захватывает энграмму сквозь прикрытие БМ | «Capture Cultists even if an enemy Monster is present» | ДА |
| E9 | `print/UniqueColonel/uc.md`, № 6 «Жертвенный протокол» | «когда ты создаёшь боевого робота, ты можешь уничтожить Эвелин… стоимость создания уменьшается на 3 нефти» | создание | у Moon полковника нет (FAC-020) | Bubastis High Priest не использует | ДА (н/п) |

### F. Реестры и решения: прямые ссылки на Elder God

| № | Файл и место | Цитата | Что проверяет | «Зардоз» по нашему тексту | Bastet по оригиналу | Совпадает? |
|---|---|---|---|---|---|---|
| F1 | `terms.yaml` TERM-026, `notes` | «в рулбуке правило подаётся как свойство отдельных боевых роботов» | соответствие реестра книге | в RULEBOOK.md нет ни «Elder God», ни «старш…», ни какого-либо «свойства» БР | — | НЕТ: реестр утверждает то, чего в книге нет, и противоречит NUM-100 («в правилах оно не описано») |
| F2 | `factions.yaml` FAC-013 | «status: DEFERRED… При финальной сверке разобрать» | статус | этот аудит и есть та сверка; пункты из `proposal` закрыты D-052, D-057, D-073 и D-077 («Военные трофеи») | — | открыт |
| F3 | `STATE.md`, стр. 1168–1177 | «все три пункта обязаны быть напечатаны на планшете Moon Systems» (нет карты, нет кубиков, нет объявления битвы) | полнота планшета | (1) сноска есть; (2) косвенно: «сила 0» и «даже если кубики не бросались»; (3) не напечатан, выводится из §7.3.6 через «силу 0» | BL-UNIT-006, BL-UNIT-015 | ЗАВИСИТ (см. G) |
| F4 | `baseline.yaml` BL-UNIT-006, BL-UNIT-015, BL-ACTION-016, BL-RITUAL-001; `numbers.yaml` NUM-092, NUM-100; `factions.yaml` OW-F-06 `robot_notes` | — | реестр | согласованы между собой и с планшетом | — | ДА |

### G. «Сила 0» и «никогда не бросает кубики»

**Сейчас исход не расходится нигде.** Проверены все модификаторы силы в наших компонентах:
- «Усиление» — бьёт только по «Цунами»;
- «Наращивание мощи» — только по Т-800;
- «Генетический эксперимент» — только по пехотинцам;
- «Универсализация» — только по «Жнецу»;
- сноска к «Абрамсам» — только по «Абрамсам»;
- «Боевая перегрузка» — только по полковнику Ковачу.

Ни один из них не прибавляет силу «Зардозу». Формул, копирующих чужую силу, в принятых компонентах нет.

**Где эквивалентность держится только на числе 0:**
1. §7.3.6 и §8.1: «сила не менее 1 — то есть… хотя бы один боевой кубик». Запрета «Elder God не объявляет битву» нет ни в книге, ни на планшете: он выводится из «0» (строки A19 и F3).
2. §8.4 и §13 «Боевая сила»: сила = число кубиков (A23).
3. Таблица «Шепарда» показывает 0 у обычного БР (B11). Значит, «0» не отличает Elder God от обычного робота; его отличают только сноска и текст «Киборга-убийцы».

**Где расхождение появится, если добавить компоненты:**
1. Любой эффект «+N к силе ваших отрядов / боевых роботов / всех отрядов в битве» или «сила равна X». «Зардоз» начнёт бросать кубики и сможет объявлять битву; Bastet не может никогда.
2. Копирование силы, как у Cthugha (MRC-G-04 в справочном пуле, «бой выбранного вражеского GOO»). Скопированный 0 совпадёт с FAQ «Cthugha rolls no dice», но правило «gets no further benefit vs. Elder Gods» нигде не записано.
3. Наёмные Elder God из пула: Nodens (MRC-G-21), Hagarg Ryonis (MRC-G-22). Общего правила Elder God в книге нет, поэтому каждому понадобятся свои сноски: нет карты при давлении, нет кубиков, нет объявления битвы.
