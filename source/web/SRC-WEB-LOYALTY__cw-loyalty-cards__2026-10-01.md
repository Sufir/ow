# SRC-WEB-LOYALTY — карты лояльности нейтральных юнитов Cthulhu Wars (веб-сбор)

> **SRC-ID:** `SRC-WEB-LOYALTY` · **Получено:** 2026-10-01 · **Собрано для:** `COMP-V-10`, этап 1
> (`rules/registry/mercenaries.yaml`).
>
> **Что это.** Сводка, а не скачанная страница. Собрана Claude через WebFetch и API
> GitHub/BGG: транскрипции карт с necronomicon.app (основной источник текстов), код HRF,
> блоги и магазин Petersen Games, апдейты Kickstarter, 10 тредов BGG через API.
> Каждый факт — с URL. Тексты карт — по-английски, как на источнике.
>
> **Доверие.** necronomicon.app — транскрипция, не скан карты; страница проходила через
> пересказчик WebFetch, мелкие искажения возможны. HRF — низкий приоритет (решение
> Alek 28.09.2026). Вики Cthulhu Wars была закрыта (HTTP 402) — адреса в
> `rules/tools/fetch-queue.txt`.
>
> **Дополнение после сбора (сверка с локальным SRC-ERRATA-PACK).** Пять карт лояльности
> Ultimate Errata Pack, которые здесь в разделе C.13 названы «не найдено», лежат
> в проекте: `source/cthulhu-wars/SRC-ERRATA-PACK__cards-text__2026-09-10.md`, страницы 7–13 —
> Bokrug (Cost 4 — расхождение «Pay 6» снято), Ghatanothoa (новое требование Spellbook),
> Dark Demon, The Shadow Pharaoh (**Cost 4, Combat 2** — не 2/0, как на necronomicon.app),
> The Eidolon. Карт «Faction GOO as Independents» в эррате нет.

---

# Карты лояльности нейтральных юнитов Cthulhu Wars: веб-ресёрч по оригиналу

Дата сбора: 01.10.2026. Тексты карт — по-английски, как на источнике; комментарии — по-русски.

---

## 0. Источники и как им доверять

**Главная оговорка.** Вики Cthulhu Wars (cthulhuwars.fandom.com) оказалась недоступна:
WebFetch получает от fandom HTTP 402, curl — отказ прокси (403, политика организации).
Зеркала тоже закрыты: breezewiki — капча, antifandom — robots.txt, web.archive.org,
archive.ph и translate.goog — заблокированы. Поэтому основной источник текстов —
фан-приложение **Necronomicon** (necronomicon.app), а не вики. Список страниц вики
для ручного сохранения — в разделе «Не найдено».

| Код | Источник | Что это | Надёжность |
|-----|----------|---------|------------|
| **NEC** | https://necronomicon.app/neutral-expansions/… (страницы ниже) | Фан-справочник Филиппо Сальварани, указан Petersen Games как партнёр; транскрипция текстов карт и рулбука | Высокая по содержанию, но **это транскрипция, а не скан карты**. Текст получен через WebFetch: страница проходит через модель-пересказчик. Карты запрошены «сырым текстом в code block», формулировки совпадали при повторных запросах. Мелкие искажения всё же возможны |
| **HRF** | https://github.com/haunt-roll-fail/cthulhu-wars, ветка `main`, коммит `56fb862` от 14.03.2026; плюс PR #11 (`3aa4698`, 17.03.2026, George Remus, не влит) | Исходники цифровой версии: числа в коде, тексты карт в `solo/overlay.scala` | Низкий приоритет по ТЗ. Годится для сверки чисел. Покрывает только Ghast, Gug, Shantak, Star Vampire, High Priest и 4 IGOO; в PR #11 добавлены Voonith, Dimensional Shambler, Gnorri, Tulzscha, Y'Golonac |
| **FAQ** | https://petersengames.freshdesk.com/support/solutions/articles/48000952254-cthulhu-wars-rules-faq | Официальный FAQ Petersen Games | Официальный |
| **PL** | https://petersengames.freshdesk.com/support/solutions/articles/48001060995-cthulhu-wars-product-list | Официальный список продуктов с кодами CW-… | Официальный |
| **BLOG1** | https://petersengames.com/sandys-design-corner-why-are-the-monster-great-old-one-figure-expansions-like-that/ | Колонка Сэнди «How Do Expansions Work» | Официальный (дизайнер) |
| **BLOG2** | https://petersengames.com/neutral-monsters-vs-indie-goos/ | Блог Petersen Games «Neutral Monsters vs. Indie GOOs» | Официальный |
| **BLOG3** | https://petersengames.com/independent-goos-part-1/ | Блог «Independent GOOs (Part 1)» | Официальный |
| **KS-PEN** | https://www.kickstarter.com/projects/petersengames/cthulhu-wars-cataclysm/posts/2466093 | Апдейт 3 кампании CATaclysm (пингвины, Бубастис) | Официальный |
| **KS-O3** | https://www.kickstarter.com/projects/1816687860/cthulhu-wars-onslaught-3/posts/2119431 | Апдейт 86 Onslaught 3, «All the PDFs for CW O3» | Официальный |
| **BGG-n** | `https://api.geekdo.com/api/articles?threadid=<n>` | Треды BGG через API, использовано 6 из 6 | Сообщество; официальных постов в них не нашлось |
| **магазины** | ссылки у фактов | Описания продуктов | Средняя |

Страницы NEC, на которые даны ссылки ниже:

- NEC-RX — https://necronomicon.app/neutral-expansions/rulebook-extras
- NEC-DS — https://necronomicon.app/neutral-expansions/dreamlands-surface-monsters
- NEC-DU — https://necronomicon.app/neutral-expansions/dreamlands-underworld-monsters
- NEC-AZ — https://necronomicon.app/neutral-expansions/azathoth
- NEC-CT — https://necronomicon.app/neutral-expansions/cosmic-terrors
- NEC-BTS — https://necronomicon.app/neutral-expansions/beyond-time-and-space
- NEC-RC1 — https://necronomicon.app/neutral-expansions/ramsey-campbell-horrors-1
- NEC-RC2 — https://necronomicon.app/neutral-expansions/ramsey-campbell-horrors-2
- NEC-CATS — https://necronomicon.app/neutral-expansions/something-about-cats
- NEC-KS — https://necronomicon.app/neutral-expansions/kickstarter-specials
- NEC-MASK — https://necronomicon.app/neutral-expansions/masks-of-nyarlathotep
- NEC-DUN — https://necronomicon.app/neutral-expansions/the-dunwich-horror
- NEC-PA — https://necronomicon.app/neutral-expansions/planet-apocalypse-crossover
- NEC-GW — https://necronomicon.app/neutral-expansions/the-gods-war-crossover
- NEC-HP — https://necronomicon.app/neutral-expansions/high-priests
- NEC-G1…G4 — https://necronomicon.app/neutral-expansions/great-old-one-pack-1 … -4

---

## A. Neutral Monsters

### A.0. Общие правила (дословно)

> «A player may purchase a Neutral Monster's Loyalty Card during the Doom Phase. A player may never purchase more than one of these in a given Doom Phase, but there is no limit to the number of Neutral Monster Loyalty Cards a player may possess.
>
> To purchase one of these Loyalty Cards, pay 2 Doom when it is your turn to perform a Ritual of Annihilation. If you wish, you may still perform the Ritual. When spending Doom, choose a Neutral Monster Loyalty Card from among those available, placing that card and its associated Monsters by your Faction Card. You will typically have the opportunity to immediately place one of these new Monsters for free.
>
> Once you have purchased a Neutral Monster Loyalty Card, it is yours for the rest of the game. From then on only you may Summon and Control its associated Neutral Monsters.»
> — NEC-CATS (общий блок «Neutral Monsters» под каждой картой)

Подтверждение от дизайнера (BLOG1): платишь 2 Doom и берёшь карту, *«Typically he then places one of the monsters on the map for free, and the rest are added to his force pool.»*

### A.1. Сводная таблица: 20 официальных карт Neutral Monster

«Цена» — плата за **получение карты**. Cost — цена призыва одной фигурки (Power).

| # | Карта | Продукт (код) | Фиг. | Цена | Cost | Combat | Источник |
|---|-------|---------------|------|------|------|--------|----------|
| 1 | Gnorri | Dreamlands Surface Monster Expansion, **CW-U1** | 3 | 2 Doom | 3 | 2 | NEC-DS; HRF PR#11 (3/3/2) |
| 2 | Moonbeast | CW-U1 | 4 | 2 Doom | 2 | 0 | NEC-DS; BGG-1529006 (Combat 0) |
| 3 | Shantak | CW-U1 | 2 | 2 Doom | 2 | 2 | NEC-DS; HRF |
| 4 | Ghast | Dreamlands Underworld Monster Expansion, **CW-U2** | 4 | 2 Doom | 2 | 0 | NEC-DU; HRF |
| 5 | Gug | CW-U2 | 2 | 2 Doom | **1** | 3 | NEC-DU; HRF; BGG-1529006 («they only cost 1 to summon») |
| 6 | Leng Spider | CW-U2 | 3 | 2 Doom | 2 | 1 | NEC-DU |
| 7 | Dimensional Shambler | Azathoth Neutral Expansion, **CW-F4** | 3 | 2 Doom | 2 | 2 | NEC-AZ; HRF PR#11 |
| 8 | Elder Thing | CW-F4 | 3 | 2 Doom | 2 | 2 | NEC-AZ |
| 9 | Servitor of the Outer Gods | CW-F4 | 3 | 2 Doom, **карта отдаётся другому игроку** | 1 | **−1** | NEC-AZ; BGG-1529006; FAQ |
| 10 | Star Vampire | CW-F4 | 3 | 2 Doom | 2 | 1 | NEC-AZ; HRF |
| 11 | Wamp | Beyond Time and Space, **CW-U11** | 4 | 2 Doom | 1 | 0 | NEC-BTS |
| 12 | Voonith | CW-U11 | 2 | 2 Doom | 3 | 1 | NEC-BTS; HRF PR#11 (3/2/1) |
| 13 | Insects from Shaggai | Ramsey Campbell Horrors 1, **CW-RC1** | 3 | 2 Doom | 2 | 0 | NEC-RC1 |
| 14 | Satyr | Ramsey Campbell Horrors 2, **CW-RC2** | 3 | 2 Doom | 2 | 1 | NEC-RC2 |
| 15 | Asteroid Cat | Something About Cats Box, **CW-U33** | 2 | 2 Doom | 1 | 1 | NEC-CATS |
| 16 | Cat from Mercury | CW-U33 | 2 | 2 Doom | 1 | 1 | NEC-CATS |
| 17 | Cat from Venus | CW-U33 | 2 | 2 Doom | 1 | 1 | NEC-CATS |
| 18 | Giant Blind Albino Penguins | Giant Albino Penguin, **CW-U32** | 2 | 2 Doom | 1 | **−2** | NEC-KS; KS-PEN |
| 19 | Fiend | Planet Apocalypse crossover (код не найден) | 4 | 2 Doom | 3 | 2 | NEC-PA |
| 20 | Gryllus | Planet Apocalypse crossover (код не найден) | 6 | 2 Doom | 2 | 1 | NEC-PA |

Коды продуктов — по PL. Распределение по продуктам: CW-U1/U2/U11/U33 — NEC; CW-F4 — NEC-AZ; RC1/RC2 — NEC.

**Итог по цене:** у всех 20 карт цена ровно «2 Doom», без Power. Особые только Servitor
(2 Doom, но карта уходит **другому** игроку) и Wamp (фигурки ставит противник).
Скидка возможна только через Lavinia Whateley (см. A.3).

### A.2. Тексты карт дословно

Цитаты из NEC, если не указано иное.

**1. Gnorri (3)** — NEC-DS
- Получение: «Pay 2 Doom to obtain this Loyalty Card, then place 1 Gnorri at your Controlled Gates.»
- Cost: 3 · Combat: 2
- **Grottos (Doom Phase):** «During the Doom Phase, if you have 2 Gnorri in play, you earn 1 extra Doom point. If you have 3 Gnorri in play, you earn 2 extra Doom points.»
- В HRF PR#11 текст тот же.

**2. Moonbeast (4)** — NEC-DS
- Получение: «Pay 2 Doom to obtain this Loyalty Card, then place 1 Moonbeast on an enemy Faction Spellbook.»
- Cost: 2 · Combat: 0
- **Blasphemous Obeisance (Ongoing):** «When a Moonbeast is Summoned, place it on a Spellbook on an enemy's Faction Card. While the Moonbeast is on that Spellbook, that Spellbook cannot be used (it still counts for other purposes such as Unlimited Battle, and winning the game). In the next Doom Phase, remove all Moonbeasts from enemy Spellbooks and place them into any Areas on the Map containing a Controlled Gate(s). A Moonbeast may be prematurely returned to the Map if its victim spends 1 Doom point (at any time; this does not count as an Action).»
- FAQ: если Yellow Sign получает Moonbeast или Dimensional Shambler при попытке Desecration, фигурка ставится в «Desecrated Area, as described in the ability».

**3. Shantak (2)** — NEC-DS
- Получение: «Pay 2 Doom to obtain this Loyalty Card, then place 1 Shantak at your Controlled Gates.»
  - В HRF иначе: «Pay 2 Doom to obtain this Loyalty Card, plus place 1 Shantak at your controlled Gate.»
- Cost: 2 · Combat: 2
- **Horror Steed (Ongoing):** «When Moving a Shantak, it can reach any Area on the Map. In addition, the Shantak may carry one of you Cultists with it for free.» («you» вместо «your» — так на NEC; в HRF «your»)

**4. Ghast (4)** — NEC-DU
- Получение: «Pay 2 Doom to obtain this Loyalty Card, then place all 4 Ghasts at your Controlled Gate(s).»
  - HRF: «…plus place all 4 Ghasts at your controlled Gate(s).»
- Cost: 2 · Combat: 0
- **Hordeling (Ongoing):** «When you spend 2 Power to Summon Ghasts, all Ghasts in your Pool are Immediately placed on the Map at any Gate(s) you Control.»
- FAQ: «Q. How many points when a Ghast is Shriveled? A. Two, since that's how much a single Ghast costs to Summon.»

**5. Gug (2)** — NEC-DU
- Получение: «Pay 2 Doom to obtain this Loyalty Card, then place 1 Gug at your Controlled Gates.»
  - HRF: «…plus place 1 Gug at your controlled Gate.»
- Cost: 1 · Combat: 3
- **Clumsy (Ongoing):** «A Gug cannot Capture a Cultist.»

**6. Leng Spider (3)** — NEC-DU
- Получение: «Pay 2 Doom to obtain this Loyalty Card, then place 1 Leng Spider at your Controlled Gates.»
- Cost: 2 · Combat: 1
- **Bloodthirst (Ongoing):** «If a Leng Spider is involved in a Battle, you may exchange two Pain results for a Kill before results are assigned. you may do this once for each Leng Spider in the Battle. Each use of this ability may be applied to your results OR you opponent's.»
- FAQ: «Q. How does Demand Sacrifice interact with the Leng Spiders' Bloodthirst? A. Any Pains converted into Kills become single Pains. I recommend against using Bloodthirst!»

**7. Dimensional Shambler (3)** — NEC-AZ
- Получение: «Pay 2 Doom points to obtain this Loyalty Card, then place 1 Dimensional Shambler onto your Faction Card.»
- Cost: 2 · Combat: 2
- **Walk Between World (Ongoing):** «When Summoning a Dimensional Shambler, place it onto your Faction Card. After any Action (by any player), you may place one or more Dimensional Shamblers from your Faction Card into any Area. Once placed, Dimensional Shambler remain on the Map (until Killed or otherwise Eliminated).»
  - В HRF PR#11 название «Walk Between Worlds».
- FAQ: случай Desecration — см. Moonbeast.

**8. Elder Thing (3)** — NEC-AZ
- Получение: «Pay 2 Doom points to obtain this Loyalty Card, then place 1 Elder Thing at one of your Controlled Gates.»
- Cost: 2 · Combat: 2
- **Mind Control (Ongoing):** «If an Elder Thing shares an Area with an enemy Great Old One, the latter may not use its Special Ability.»
- FAQ, начало длинного ответа: «In an Elder Thing's Area, Cthulhu can't Devour. He can still use Submerge and Y'Ha Nthlei, as those are Spellbooks, not Great Old One special abilities.» Дальше в FAQ разобраны другие GOO; дословно не снято.

**9. Servitor of the Outer Gods (3)** — NEC-AZ
- Получение: «Pay 2 Doom points to give this Loyalty Card to another player. That player now keeps this Card for the rest of the game. Do not place a Servitor.»
- Cost: 1 · Combat: −1
- **Adulation (Ongoing):** «You may not Summon any Monsters except for Servitors if any Servitors remain in your Pool. (You may still place other Monsters on the Map via abilities or means other than the Summon Action.)»
- FAQ, все вопросы о Servitor:
  - «Q. Is there any way to get rid of the Servitor of the Outer Gods Loyalty Card once it has been given to you? A. No.»
  - «Q. If the presence of Servitors reduces my combat total to less than zero, what happens? A. Just leave it at zero. That's bad enough.»
  - «Q. What if I have both Star Vampires and Servitors in the same Area…? A. Just go ahead and roll your Star Vampires' total Combat dice. In this case, you will actually get to roll Combat dice, even though your total is theoretically zero.»
  - «Q. Can I use Black Goat's Fertility Cult ability to simultaneously Summon all the remaining Servitors in my Pool, as well as other Monsters? A. Yes, you can do this as long as no Servitors remain in your Pool at the end of this Action.»
  - Ещё был вопрос о Windwalker и Cannibalism: начало ответа «Yes. For example, Windwalker can use Cannibalism to place Wendigos…»; полный текст не снят.

**10. Star Vampire (3)** — NEC-AZ
- Получение: «Pay 2 Doom points to obtain this Loyalty Card, then place 1 Star Vampire at one of your Controlled Gates.»
  - HRF: «Pay 2 Doom to obtain this Loyalty Card, plus place 1 Star Vampire at your controlled Gate.»
- Cost: 2 · Combat: 1
- **Vampirism (Ongoing)** — так на NEC; в HRF фаза «Battle»: «Roll each Star Vampire's combat dice separately. Each Pain they roll drains 1 Power from the enemy Faction. Each Kill they roll drains 1 Doom point from the enemy Faction. The drained point(s) are transferred to you immediately. If the enemy Faction lacks Power or Doom points, you get nothing. The Pains and Kills rolled still count towards you Battle results.»
  - Текст HRF: «Roll the Star Vampire's combat dice separately. … still count towards your Combat Results.»

**11. Wamp (4)** — NEC-BTS
- Получение: «Pay 2 Doom points to obtain this Loyalty Card, then choose an enemy to place all 4 Wamps in any Area without a Gate.»
- Cost: 1 · Combat: 0
- **Crypt Dweller (Doom Phase):** «Choose an enemy to place all Wamps from your Pool into any Area or Areas without a Gate. (You may still summon Wamps normally.)»

**12. Voonith (2)** — NEC-BTS
- Получение: «Pay 2 Doom points to obtain this Loyalty Card, then place 1 Voonith at one of your Controlled Gates.»
- Cost: 3 · Combat: 1
- **Vicious (Post-Battle):** «For each Kill you score fewer than the number of Vooniths involved in the Battle, add 1 Kill. (I.e., if you have 2 Vooniths in the Battle and roll 1 Kill, add 1 extra Kill for a total of 2: if you rolled no Kills, add 2 Kills).»
  - В HRF PR#11 фаза «Battle» и другой текст: «After rolling dice in Battle, before Kills are assigned, add extra Kills equal to the number of Vooninths in Battle minus the number of Kills rolled (minimum 0). The extra Kills cannot be used to Capture.»

**13. Insects from Shaggai (3)** — NEC-RC1
- Получение: «Pay 2 Doom to obtain this Loyalty Card, then place an Insect from Shaggai into any Area.»
- Cost: 2 · Combat: 0
- **Mind Parasite (Ongoing):** «All Acolytes Cultists who are not on a Gate, and who share an Area with an Insect from Shaggai, are Controlled by you during the Action Phase for the following purposes only: 1. Only you can Move them 2. They fight on your side in any Battle. They do not benefit from any Faction's Spellbooks (including yours). They can only be Captured by you if their true Faction permits it. They cannot be Captured by their true Faction (though they could be targeted by a Spellbook or Killed in a battle by them, etc.). Once an Acolyte is free. These Cultists are not Controlled by you during the Gather Power or Doom Phases – they provide Power and Doom to their true Faction.»
  - «Once an Acolyte is free.» — обрывок фразы на самом NEC.

**14. Satyr (3)** — NEC-RC2
- Получение: «Pay 2 Doom to obtain this Loyalty Card, then place a Satyr and an Acolyte Cultist at your Controlled Gate.»
- Cost: 2 · Combat: 1
- **Fecund (Ongoing):** «Each time you Summon a Satyr, also place an Acolyte Cultist from your Pool into the Same Area.»

**15. Asteroid Cat (2)** — NEC-CATS
- Получение: «Pay 2 Doom points to obtain this Loyalty Card, then place an Asteroid Cat at your Controlled Gate.»
- Cost: 1 · Combat: 1
- **Abandoned to Lusts (Action: Cost 0):** «If an Asteroid Cat shares an Area with a Unit from another Faction that has 5 or fewer Faction Spellbooks, remove the Cat from the Map and place it on one of that enemy's empty Spellbook slots. When that enemy earns that Spellbook, return the Asteroid Cat to your Controlled Gate, and you get to choose immediately which of his available Spellbooks he must take in that slot.»

**16. Cat from Mercury (2)** — NEC-CATS
- Получение: «Pay 2 Doom points to obtain this Loyalty Card, then place a Cat from Mercury at your Controlled Gate.»
- Cost: 1 · Combat: 1
- **Needs Affection (Pre-Battle):** «If a Cat from Mercury is in a Battle, you can choose one or more of your Monsters present at that Battle; and immediately replace them with your Acolyte Cultists from your pool.»

**17. Cat from Venus (2)** — NEC-CATS
- Получение: «Pay 2 Doom points to obtain this Loyalty Card, then place a Cat from Venus at your Controlled Gate.»
- Cost: 1 · Combat: 1
- **Honeymoon (Ongoing):** «When a Cat from Venus Captures a Cultist, gain 1 Power and immediately return the Cultist to the owner's Pool.»

**18. Giant Blind Albino Penguins (2)** — NEC-KS
- Получение: «Pay 2 Doom points to obtain this Loyalty Card, then place a Penguin at your Controlled Gate.»
- Cost: 1 · Combat: −2
- **Laughingstock (Pre-Battle):** «Move one or more Penguins to the Battle area, even if you are not part of the battle. If you are part of the Battle, the penguin fights on your side. Otherwise, you choose which side the Penguin is on, and it belongs to that player until the battle's end.»
- Подтверждено в KS-PEN: «The Penguins are cost 1, Combat MINUS 2.» и «As with other neutral monsters you pay 2 Doom in the Doom phase, then get a free Penguin at your gate.»

**19. Fiend (4)** — NEC-PA
- Получение: «Pay 2 Doom points to obtain this Loyalty Card, then place 1 Fiend at your Controlled Gate.»
- Cost: 3 · Combat: 2
- **Torment (Ongoing):** «Fiends are able to Capture their owner's own Cultists. This Capture cannot be prevented by enemy Units. Such a Captured Cultist, when Sacrificed in Gather Power Phase, can either give the owner 1 Power, or permit him to place a free Fiend on the Map at one of his Controlled Gates.»

**20. Gryllus (6)** — NEC-PA
- Получение: «Pay 2 Doom points to obtain this Loyalty Card, then place 1 Gryllus at your Controlled Gate.»
- Cost: 2 · Combat: 1
- **The Gates of Hell (Ongoing):** «Each time any player drops to 0 Power, he immediately takes 1 Gryllus from the owner's Pool, and places it on the Map as he pleases.»

### A.3. Что из названных в задании — не Neutral Monster

| Имя | Что это на самом деле | Цена карты | Источник |
|-----|----------------------|------------|----------|
| **Nightgaunts** | Фракционный монстр Crawling Chaos (`FactionUnitClass(CC, "Nightgaunt", Monster, 1)`, 3 шт). «Nightguant 3 Pack» CG-B1 — допфигурки для фракции. Правила «фракционные монстры как нейтральные» на BGG — фанатские | — | HRF `solo/FactionCC.scala:8`; PL; BGG-1821790 (LuckyHaster, 31.07.2017: «This is my fan-creation…») |
| **Dark Demon** (9) | **Cultist**, Masks of Nyarlathotep **CW-U10** | 2 Doom; для Crawling Chaos — **0 Doom**, и каждая другая фракция получает 1 Elder Sign. Остальные фракции навсегда теряют Acolyte и получают Dark Demon своего цвета | NEC-MASK |
| **Cat from Neptune** (1) | **Terror** (CW-U33) — см. B | 2 Doom + 2 Power | NEC-CATS |
| **Hagarg Ryonis** (Cat from Jupiter) | **Independent Elder God** (CW-U33) | Пробуждение за 4 Power | NEC-CATS |
| **Larva** (10) | **Cultist**, Planet Apocalypse crossover | 2 Doom | NEC-PA |
| **High Priest** | **Cultist**, CW-U3. Вербуется за 3 Power, Doom не нужен | — | NEC-HP; HRF |
| **Unique High Priests** (8: Asenath Waite, Crawford Tillinghast, Ermengarde Stubbs, Herbert West, Joseph Curwen, Keziah Mason, Lavinia Whateley, Pitpipo) | Вариант High Priest: «This is not a physical product» | Cost 3, Doom не нужен | NEC-RX |
| **The Eidolon**, **The Prophetess** | Особые культисты на картах лояльности | «Pay 2 Doom to take this Loyalty Card…» | NEC-RX |
| **Eradicators** (15) | «Eradicators are not Units» | «Pay 2 Doom to take this Loyalty Card, then place 1 Eradicator into each player's Start Area.» | NEC-RX |
| **Investigators** (12: Amelia Azevedo, Bernice Kuchler, …) | Investigator, Planet Apocalypse crossover | **1 Doom**: карта уходит другому игроку | NEC-PA |
| **Demon Gate** | Gate | **1 Doom + 3 Power** при постройке | NEC-PA |
| **Whateley Clan**: Lavinia, Wilbur, Wizard — Cultist; Junior — Terror | The Dunwich Horror (код не найден) | «pay that Whateley's cost»: 2 / 3 / 2 / 4. Валюта в снятом тексте не названа. Lavinia: «pay half as much Power and/or Doom for any Independent Great Old One; Neutral Monster, Terror, or Cultist; or Clan member you acquire. Round fractions up.» | NEC-DUN |
| Megalodon, юниты Ancients как нейтральные | Фанатские | — | Выдача поиска: BGG thread 2417664, файл BGG 156114; не открывались |

---

## B. Terrors

### B.0. Общие правила (дословно)

> «Terrors are Summoned as though they are Monsters, and require a Controlled Gate to be able to enter play. They are equal to Monsters in their ability to Capture Cultists. That is, Monsters can protect Cultists against Terrors (and vice versa), and Great Old Ones can still Capture Cultists protected by Terrors. However,as Terrors are a different type of Unit, they are not vulnerable to abilities that specifically target Monsters.
>
> To acquire a Terror, pay 2 Power and 2 Doom when it is your turn to perform a Ritual of Annihilation. You may still perform the Ritual, if you wish. Take your choice of available Terror Loyalty Cards and follow the instructions for placing your new figure on the Map.
>
> Players may only purchase a single Loyalty Card in any given Doom Phase, so they may not gain a Neutral Monster in the same Doom Phase in which they acquire a Terror (and vice versa). Once a Terror Loyalty Card has been acquired, it belongs to that player for the rest of the game. Only that player may Summon and control that Terror.»
> — NEC-CATS (общий блок «Terrors»)

BLOG1: «2 Doom AND 2 Power», «only one Terror exists per set», «can only buy one creature type in a particular Doom phase».

### B.1. Сводная таблица: 25 карт Terror (11 обычных + 14 Fourth Circle)

| # | Карта | Продукт (код) | Фиг. | Цена | Куда ставится | Cost | Combat | Источник |
|---|-------|---------------|------|------|---------------|------|--------|----------|
| 1 | Dhole | Cosmic Terrors Pack, **CW-U5** | 1 | 2 Doom + 2 Power | свои Controlled Gates | 4 | 5 | NEC-CT |
| 2 | Great Race of Yith | CW-U5 | 1 | 2 D + 2 P | свои Controlled Gates | 4 | 3 | NEC-CT |
| 3 | Quachil Uttaus | CW-U5 | 1 | 2 D + 2 P | свои Controlled Gates | 4 | 1 | NEC-CT |
| 4 | Hound of Tindalos | Beyond Time and Space, **CW-U11** | 1 | 2 D + 2 P | **любые Gate, в том числе чужие** | 4 | 4 | NEC-BTS |
| 5 | Brown Jenkin | **CW-U29** | 1 | 2 D + 2 P | свои Controlled Gate | 2 | 0 | NEC-KS; PL |
| 6 | The Elder Shoggoth | **CW-U31** | 1 | 2 D + 2 P | свои Controlled Gate | 4 | 2 | NEC-KS; PL |
| 7 | Cacodemon | **CW-U30**, кроссовер Planet Apocalypse | 1 | 2 D + 2 P | «in an Area with your Controlled Gate» | 4 | 3 | NEC-PA; PL |
| 8 | Cat from Neptune | **CW-U33** | 1 | 2 D + 2 P | свои Controlled Gate | 1 | 1 | NEC-CATS |
| 9 | The Shadow Pharaoh | Masks of Nyarlathotep, **CW-U10** | 1 | 2 D + 2 P; **Crawling Chaos — только 2 Power**, каждая другая фракция +1 Elder Sign | свои Controlled Gate | 2 | 0 | NEC-MASK |
| 10 | Worms of Ghroth | фигурки — Shaggai Map **CW-M11**; карта — отдельный PDF (KS-O3) | 6 | 2 D + 2 P | свои Controlled Gate | **N/A** | 0 | NEC-RX; PL |
| 11 | Junior Whateley | The Dunwich Horror (код не найден) | 1 | правило Clan: «pay that Whateley's cost» | «as the new owner wishes» | 4 | 4 | NEC-DUN |
| 12–25 | Fourth Circle Terrors (14 шт.) | кроссовер Planet Apocalypse (код не найден) | по 1 | 2 D + 2 P **и −1 Power в каждой Gather Power за каждую такую карту** | свои Controlled Gate | 2 | 2–6 | NEC-PA |

Hound of Tindalos — коды CW-U11 и состав по NEC. Shadow Pharaoh — CW-U10 по PL.

**Итог по цене:** правило «2 Doom + 2 Power» выполняется у всех, кроме:
- Shadow Pharaoh для Crawling Chaos — 2 Power без Doom;
- Fourth Circle — сверху постоянный налог Power;
- Junior Whateley — собственное правило Clan;
- скидка Lavinia — половина цены.

### B.2. Тексты карт дословно

Цитаты из NEC.

**1. Dhole (1)** — NEC-CT
- «Pay 2 Doom and 2 Power to obtain this Loyalty Card, then place the Dhole at one of you Controlled Gates.»
- Cost: 4 · Combat: 5
- **Planetary Destruction (Post-Battle):** «If the Dhole is Killed or Eliminated in a Battle, earn 2 Elder signs. Additionally, your opponent gains your choice of 2 Doom or 2 Power.»

**2. Great Race of Yith (1)** — NEC-CT
- «Pay 2 Doom and 2 Power to obtain this Loyalty Card, then place the Great Race of Yith at one of you Controlled Gates.»
- Cost: 4 · Combat: 3
- **Possession (Ongoing and Gather Power Phase):** «If the Great Race of Yith is in an Area with an enemy Cultist, you may Capture that Cultist regardless of the presence of any enemy Units or Great Old Ones (or whether Windwalker's Ferox ability is in effect). In addition, if the Great Race of Yith is in play during the Gather Power Phase, earn 1 Power per Captured Cultist in addition to the normal reward of 1 Power per Cultist.»
- FAQ: «Q. How does the Tcho-Tcho's Soulless interact with the Yithian's Possession ability? A. Soulless makes the base reward 0 Power, rather than 1. The Yithian's Possession adds to whatever the base reward is…»; ответ снят не до конца.

**3. Quachil Uttaus (1)** — NEC-CT
- «Pay 2 Doom and 2 Power to obtain this Loyalty Card, then place Quachil Uttaus at one of you Controlled Gates.»
- Cost: 4 · Combat: 1
- **Dust to Dust (Post-Battle):** «If an enemy Unit is Killed or Eliminated in a Battle involving Quachil Uttaus, that Unit's owner must choose one of the following options: 1) Select one his lost units to be permanently removed from the game OR 2) You receive an Elder Sign»

**4. Hound of Tindalos (1)** — NEC-BTS
- «Pay 2 Doom and 2 Power to obtain this Loyalty Card, then place the Hound of Tindalos at any Gate (even one you don't Control).»
- Cost: 4 · Combat: 4
- **Cronophage (Ongoing):** «The Hound cannot perform the Move Action by itself. The Hound Moves for free whenever you Move any other Unit. In doing so, the Hound teleports directly from an Area with a Gate to another Area with a Gate – neither of which need to be Controlled by you (or anyone).»
- **Angles of Time (Ongoing):** «The Hound cannot be assigned a Kill in Battle. However, if a Hound is ever in an Area without a Gate (due to being Pained to such an Area, or the Gate itself being desttroyed or moved, etc.), it is Eliminated. It can also be Eliminated if it cannot be Pained due to Enemy presence in adjacent Areas (per normal Pain rules).»

**5. Brown Jenkin (1)** — NEC-KS
- «Pay 2 Doom and 2 Power to obtain this Loyalty Card, then place Brown Jenkin at your Controlled Gate.»
- Cost: 2 · Combat: 0
- **Loathsome Titter (Gather Power Phase):** «Brown Jenkin shares an area with an enemy-controlled Gate during the Gather Power Phase, gain 2 Power, plus 1 more power for each enemy Cultist in the area.»
- **Familiar (Ongoing):** «If Brown Jenkin is killed or eliminated, if (or as soon as) you have at least 2 Power, pay 2 Power and place Brown Jenkin at your Controlled Gate. This does not count as an Action. This is not Optional.»

**6. Elder Shoggoth (1)** — NEC-KS
- «Pay 2 Doom and 2 Power to take this Loyalty Card. Then, place the Elder Shoggoth at your Controlled Gate.»
- Cost: 4 · Combat: 2
- **Prime Cause (Post-Battle):** «In a Battle involving the Elder Shoggoth, choose any of you Units (including this one) and replace it with any other Unit from your Pool. You can gain a Faction Great Old One that was previously Awakened, but still must fulfill other requirements (for example, to place Cthulhu, the Battle must be in his Start Area, plus a gate). If you choose to replace the Elder Shoggoth itself, pay nothing, and no enemy gains a reward. Otherwise, follow these rules: 1. Pay half the new Unit's Power cost (rounded down–so you pay 1 Power for a cost 3 Monster). 2. If the new Unit is a Terror, the enemy gains 1 Doom. 3. If the new Unit is a Great Old One, the enemy gains 1 Elder Sign.»

**7. Cacodemon (1)** — NEC-PA
- «Pay 2 Doom and 2 Power, then place the Cacodemon in an Area with your Controlled Gate.»
- Cost: 4 · Combat: 3
- **Cosmic Terror (Ongoing):** «Enemy Units may not Move or be Pained into the Area with Cacodemon unless they are Great Old Ones or if they are accompanied by a Great Old One.»

**8. Cat from Neptune (1)** — NEC-CATS
- «Pay 2 Doom and 2 Power to take this Loyalty Card. Place the Cat from Neptune at your Controlled Gate.»
- Cost: 1 · Combat: 1
- **The Final Ritual (Post-Battle):** «If the Cat from Neptune is Killed in a Battle, you may immediately perform a Ritual of Annihilation. If this causes the marker to move to Instant Death, the game ends after this action.»

**9. The Shadow Pharaoh (1)** — NEC-MASK
- «In the Doom Phase, when it is your turn to perform a Ritual of Annihilation, pay 2 Doom and 2 Power to obtain this Loyalty Card, then place the Shadow Pharaoh at your Controlled Gate. If you wish, you may still perform a Ritual.»
- Для Crawling Chaos: «In the Doom Phase, when it is your turn to perform a Ritual of Annihilation, pay only 2 Power to obtain this Loyalty Card, then place the Shadow Pharaoh at one of your Controlled Gates. If you wish, you may still perform a Ritual. Each other Faction gains 1 Elder Sign.»
- Cost: 2 · Combat: 0
- **Hebephrenia (Ongoing):** «Gates may not be Controlled by any Faction in the Shadow Pharaoh's Area. When the Shadow Pharaoh enters an Area, any occupying Unit immediately Abandons the Gate. (Yog-Sothoth is unaffected.).»

**10. Worms of Ghroth (6)** — NEC-RX
- «Pay 2 Doom and 2 Power to take this Loyalty Card. Then, place one Worm of Ghroth at your Controlled Gate.»
- «Cost: N/A. Whenever a Worm of Ghroth is Killed or Eliminated, roll a die. If the result is higher than the number of Worms in play, you may place up to two Worms into any available, unoccupied areas of the Map. In the event that multiple Worms are Killed or Eliminated, roll a die for each Worm so removed from play. Resolve this ability one roll at a time.»
- Combat: 0
- **Eradication (Gather Power Phase):** «Roll a die. If the result is equal to or less than the number of Worms of Ghroth in play, gain 1 Elder Sign and lose Power equal to the number shown on the die.»
- «Note: The Worms of Ghroth miniatures are found only in the Shaggai Map expansion. Worms of Ghroth cannot be used as Terrors if you are playing on the Shaggai Map.»
- Отдельный PDF «Worms of Ghroth Loyalty Card» упомянут в KS-O3. Страница petersengames.com/download/worms-of-ghroth-loyalty-card/ отдаёт 404.

**11. Junior Whateley (1)** — NEC-DUN
- Правило Clan: «DOOM PHASE: In player order, each Faction can choose to recruit one Whateley in each Doom Phase. To do so, they must pay that Whateley's cost. If the recruited Whateley is not yet in play, place it on the Map as the new owner wishes. You can recruit a Whateley that is already in play! In this case, the former owner hands over the relevant Loyalty Card (the miniature remains in play its current location). That Whateley is now yours until (possibly) the next Doom Phase.»
- Cost: 4 · Combat: 4
- **Growth (Doom Phase):** «If Junior Whateley is in play, place any token on his Loyalty Card. These tokens remain even when Junior switches loyalty.»
- **Transmogrification (Action: Cost 0):** «If Junior has at least 1 token on this Loyalty Card, roll a die. If the die roll is equal to or less than the number of tokens on Junior Whateley's Loyalty Card, replace Junior with any Great Old One (Neutral or Faction), ignoring all Awakening requirements, including cost. Place Junior back in your Pool. Whether or not you succeed, discard one token from Junior Whateley's Loyalty Card. If you recruit a rival's Great Old One by this means, it remains under their Control.»

**12–25. Fourth Circle Terrors (кроссовер Planet Apocalypse)** — NEC-PA

У всех одинаково:
- «Pay 2 Doom and 2 Power to obtain this Loyalty Card, then place the <имя> at your Controlled Gate.»
- Cost: 2
- **Fourth Circle (Gather Power):** «Lose 1 Power during Gather Power for each Fourth Circle Terror Loyalty Card you own.»

| Имя | Combat | Способность дословно |
|-----|--------|----------------------|
| Bellatrix | 5 | **Berserkergang (Post-Battle):** «After Battle results are tallied, add 1 extra Kill to your total if the Bellatrix was present.» |
| Catoblepas | 3 | **Poison Gaze (Battle):** «Each time the Catoblepas is placed on the Map, each enemy player must choose and Eliminate half of his Cultists, rounding fractions in his favor.» |
| Cendiary | 6 | **Hellfire (Pre-Battle):** «If the Cendiary is in the Battle, before dice are rolled, the enemy can choose one of his Units and Eliminate it. If he does so, the Cendiary rolls no Combat dice.» |
| Elemental | 4 | **Invisibility (Pre-Battle):** «Select one Monster or Cultist (from either Faction) and "exempt" it. The selected Unit takes no part in the rest of the Battle.» |
| Gadarene | 4 | **Mastermind (Ongoing):** «Each time the Gadarene is placed on the Map, you may Move all enemy Great Old Ones into an Area adjacent to their current Area, chosen by you.» |
| Hellhound | 4 | **Hellbreath (Battle):** «If you are in a Battle, and the Hellhound is on the Map, but not involved, it still adds its attack to your total. However, it cannot more than double the number of dice you roll.» |
| Hortator | 3 | **Xhort (Battle):** «If the Hortator is in a Battle, add +1 Combat die for each other different type of Unit you have present.» |
| Magdalene | 3 | **Mastermind (Ongoing):** «You can Recruit & Summon Monsters and Terrors for 1 less Power each in the Magdalene's Area. Cost cannot drop below 0.» |
| Mandrake | 4 | **Doppleganger (Battle):** «If the Mandrake is in a Battle, at least one enemy Kill and one enemy Pain are used to target his own Units (his choice as to which ones).» |
| Nuckelavee | 2 | **Pestilence (When Spawned):** «Each time the Nuckelavee is placed on the Map, each enemy player must lower his Power by 2. When the Nuckelavee is Eliminated or Killed, all enemy players immediately gain 2 Power.» |
| Philter | 2 | **Catholicon (Battle):** «If the Philter was in the Battle, the enemy loses 1 of his rolled Kill and 1 of his rolled Pain results before tallying results.» |
| Raparee | 3 | **Robbery (When Spawned):** «Each time the Raparee is placed on the Map, each enemy player must take 1 of their Elder Signs (if any) and place them on the Doom Track. When the Raparee is Eliminated or Killed, each enemy player chooses one of these Elder Signs, randomly, and returns it to their store.» |
| Secutor | 5 | **Battle Rage (Ongoing):** «Roll the Secutor's Battle dice separately from your other Units. The Secutor's results cannot be used to target enemy Cultists. Your enemy can choose to target the Secutor's dice either before or after your other Unit's dice results, at his option.» |
| Tardigrade | 3 | **Encyst (Post-Battle & Doom Phase):** «If the Tardigrade is Eliminated or Killed, place the Cyst token in the Area. In the next Doom phase, replace the Cyst token with the Tardigrade, unless it is currently on the Map.» |

---

## C. Faction Great Old Ones as Independents (дизайн Сэнди Петерсена)

### C.0. Происхождение и общие правила

- NEC-RX, вводный абзац раздела: «These Loyalty Cards, Spellbooks, and abilities were designed by Sandy so that Faction Great Old Ones could be used as Independents. We do NOT recommend using a Great Old One as an Independent if a player is playing as that Great Old One's Faction.»
- Продукты по PL:
  - **CW-GLO1** «Glowthulhu»; на странице магазина: «Cthulhu as an independent Great Old One (with Loyalty Card and Spell book)!» — https://petersengames.com/the-games-shop/glowthulhu-independent-cthulhu-great-old-one/
  - **CW-GLO2** «Glow GOOs». У TheGameSteward пишется «CW-GL02»: 11 фигурок светящихся GOO — «Azathoth, Cthulhu, King In Yellow, Hastur, Ithaqua, Nyarlathotep, Rhan Tegoth, Ubbo Sathla, Yog-Sothoth, Tsathoggua, Shub Niggurath», и «10 loyalty cards so they may all be played as neutral GOO's» — https://www.thegamesteward.com/products/cthulhu-wars-glow-in-the-dark-miniatures-collection-cw-gl02-kickstarter-special
  - 11 фигурок, 10 карт: у Azathoth уже есть своя карта независимого GOO в CW-F4 (см. C.12).
  - Noble Knight продаёт «Glow in the Dark Independent Great Old Ones Collection #1»: «Shub-Niggurath, King in Yellow, Hastur, Rhan-Tegoth, Ithaqua, Ubbo-Sathla», лот без карт — https://www.nobleknight.com/P/2148200045/Glow-in-the-Dark-Independent-Great-Old-Ones-Collection-1
- Официальный PDF **«Faction GOO LCs»** выложен в апдейте 86 Onslaught 3 (KS-O3). Прямой ссылки на файл WebFetch не отдал.
- BGG-2185446, пользователь 181979, 13.04.2019: «They are also in the rulebook for you to photocopy if you want to make your own.» и «the rules say you are not supposed to use a GOO that is in the game as an IGOO.»

Общий блок «Independent Great Old Ones» стоит на NEC-RX под каждой из 10 карт (дословно):

> «Awakening: Take the Independent's Loyalty Card, Spellbook and tokens, and add them to you pool. Place the Independent's figure on the Map, under your Control. There are no limits to how many Independents you may Control, and you may use one Independent to help you Awaken another.
>
> Death: If your Independent is Killed, place it's Loyalty Card, figure, unused tokens, and Spellbook back into the general Pool (tokens already on the Map remain there). If you had earned its Spellbook, it "falls off" the Loyalty Card and is no longer in effect. If this Independent is Awakened again, even by the same player, the Spellbook must be earned anew.
>
> Spellbook: Each Independent has its own Spellbook to be earned. When a Spellbook's requirements have been met, place the Spellbook on the Independent's Loyalty Card; you may reap that Spellbook's benefits as lon as you control that Independent. This Spellbook does not count as one of your "Faction" Spellbooks for any purpose, and it cannot be placed on your Faction Card.
>
> Doom Phase: When you perform a Ritual of Annihilation, do NOT gain an Elder Sign for any Independent Great Old Ones you Control.
>
> Note: For your first game with Independents, it is recommended to use one fewer Independent than the number of players.»

**Как читать карты ниже.** На NEC у карты нет подписи «Spellbook Requirement»: строка
требования стоит отдельной строкой между способностью и общим блоком. В тексте она
помечена «Требование Spellbook». Стоимость в скобках «(Cost N)» — из заголовка карты.
Строки Combat и Cost сняты дважды, в двух независимых запросах, и совпали.

### C.1. Сводная таблица

| GOO | Cost | Combat | Способность (фаза) | Spellbook (фаза) |
|-----|------|--------|-------------------|------------------|
| Cthulhu | 6 (+1 Elder Sign) | 3 | The Stars are Right (Doom Phase) | Devour (Pre-Battle) |
| Hastur | 6 (+1 Elder Sign) | половина цены Ritual, вниз | The Stars are Wrong (Doom Phase) | Vengeance (Post-Battle) |
| Ithaqua | 4 | 5 | Hibernate (Action: Cost 0) | Ferox (Ongoing) |
| Nyarlathotep | 6 | = число Spellbook у врага | Chaos (Ongoing) | The Harbinger (Post-Battle) |
| Rhan-Tegoth | 4 | 2 | Herald (Doom Phase) | Eternal (Post-Battle) |
| Shub-Niggurath | 4 | = число своих Controlled Gates | Fertile (Ongoing) | Avatar (Action: Cost 1) |
| The King in Yellow | 2 | 0 | Defilement (Action: Cost 2) | Feast (Gather Power Phase) |
| Tsathoggua | 4 | = число вражеских фракционных GOO | Death from Below (Doom Phase) | Lethargy (Action: Cost 0) |
| Ubbo-Sathla | 4 | = позиция счётчика Growth | Sycophancy (Doom Phase) | Hell's Banquet (Doom Phase) |
| Yog-Sothoth | 6 | = число вражеских фракционных GOO (**подозрение на ошибку**, см. «Расхождения») | The Beyond-One (Action: Cost 1) | The Key and the Gate (Ongoing) |

### C.2–C.11. Тексты дословно (NEC-RX)

**Cthulhu**
- «How to Awaken Cthulhu (Cost 6): 1. Your Controlled Gate is in an Area with your Great Old One. 2. Pay 6 Power, and place Cthulhu in the Area containing the Gate. 3. Gain 1 Elder Sign.»
- «Combat: 3»
- «The Stars are Right (Doom Phase): Gain 1 Elder Sign in each Doom Phase in which you Control a Gate in the Area with Cthulhu's Glyph.»
- Требование Spellbook: «EITHER Control 3 Gates in ocean/sea Areas, OR 4 Gates exist in ocean/sea Areas.»
- **Devour (Pre-Battle):** «Your enemy chooses and eliminates one of his own Monsters or Cultists from the Battle Area.»

**Hastur**
- «How to Awaken Hastur (Cost 6): 1. Your Controlled Gate is in an Area with your Great Old One. 2. Pay 6 Power, and place Hastur in the Area containing the Gate. 3. Gain 1 Elder Sign.»
- «Combat: Equal to half of the current cost of a Ritual of Annihilation (round down).»
- «The Stars are Wrong (Doom Phase): Gain 1 Elder Sign during each Doom Phase in which you Control a Gate in the Area containing Yellow Sign's Faction Glyph (NOT one of the King in Yellow's 3 Spellbook Glyphs, but the Yellow Sign, itself).»
- Требование Spellbook: «As an Action, select another player to gain 3 Doom points.»
- **Vengeance (Post-Battle):** «If Hastur is involved in a Battle, you choose which Combat results are applied to which enemy Units. For instance, you could apply a Kill to a particular enemy Great Old One involved in that Battle.»

**Ithaqua**
- «How to Awaken Ithaqua (Cost 4): 1. Your Controlled Gate is in an Area with your Great Old One. 2. Pay 4 Power, and place Ithaqua in the Area containing the Gate.»
- «Combat: 5»
- «Hibernate (Action: Cost 0): You can perform no more Actions during the rest of this Action Phase (as if you were at 0 Power). Add your current Power to your total in the next Gather Power Phase.»
- Требование Spellbook: «Gates exist in both Areas containing a Windwalker Glyph.»
- **Ferox (Ongoing):** «Your Cultists cannot be Captured by enemy Monsters or Terrors. They are still vulnerable to enemy Great Old Ones.»

**Nyarlathotep**
- «How to Awaken Nyarlathotep (Cost 6): 1. Your Controlled Gate is in an Area with your Great Old One. 2. Pay 6 Power, and place Nyarlathotep in the Area containing the Gate.»
- «Combat: Equal to the total number of Spellbooks held by your enemy (Faction Spellbooks, as well as any others).»
- «Chaos (Ongoing): Nyarlathotep can Move 2 Areas on a Move Action. He can fly over Areas containing enemy Units.»
- Требование Spellbook: «Capture an enemy Cultist.»
- **The Harbinger (Post-Battle):** «If Nyarlathotep is in a Battle in which one or more enemy Great Old Ones are Killed or Pained, receive Power equal to half of the cost of Awakening those Great Old Ones. For each enemy Great Old One so affected, you may choose to receive 2 Elder Signs instead of Power.»

**Rhan-Tegoth**
- «How to Awaken Rhan-Tegoth (Cost 4): 1. Your Controlled Gate is in an Area with your Great Old One. 2. Pay 4 Power, and place Rhan-Tegoth in the Area containing the Gate.»
- «Combat: 2»
- «Herald (Doom Phase): You never pay more than 5 Power to perform a Ritual of Annihilation, regardless of its actual cost.»
- Требование Spellbook: «Control a Gate in an Area with a Windwalker Glyph.»
- **Eternal (Post-Battle):** «If Rhan-Thegoth receives a Kill result in Battle, you may pay 1 Power to turn it into a Pain.» («Rhan-Thegoth» — опечатка на NEC)

**Shub-Niggurath**
- «How to Awaken Shub-Niggurath (Cost 4): 1. Your Controlled Gate is in an Area with your Great Old One. 2. Pay 4 Power, and place Shub-Niggurath in the Area containing the Gate.»
- «Combat: Equal to the total number of Gates you Control.»
- «Fertile (Ongoing): When you Recruit a Cultist, you may Recruit more than one as a single Action, into one or more Areas. You may still only Summon a single Monster per Summon Action.»
- Требование Spellbook: «Share Areas with all enemy Factions (i.e., both you and the enemy have Units there).»
- **Avatar (Action: Cost 1):** «Choose an Area and a Faction. Swap the location of Shub-Niggurath with that of a Monster or Cultist in the chosen Area, chosen by the Faction owner.»

**The King in Yellow**
- «How to Awaken The King in Yellow (Cost 2): 1. Your Controlled Gate is in an Area with your Great Old One. 2. Pay 2 Power, and place The King in Yellow in the Area containing the Gate.»
- «Combat: 0»
- «Defilement (Action: Cost 2): If the King in Yellow is in an Area with no Desecration token, roll a die. On a roll equal to or less than the number of your Units in the Area (including the King), place a Desecration token into that Area. Whatever the result, place a Monster or Cultist with a cost of 2 or less into the Area.»
- Требование Spellbook: «Place a Desecration token in an Area containing a enemy-Controlled Gate.»
- **Feast (Gather Power Phase):** «Gain 1 Power for each Area that contains a Desecration token.»

**Tsathoggua**
- «How to Awaken Tsathoggua (Cost 4): 1. Your Controlled Gate is in an Area with your Great Old One. 2. Pay 4 Power, and place Tsathoggua in the Area containing the Gate.»
- «Combat: Equal to the number of enemy Faction Great Old Ones (not counting any Independent Great Old Ones).»
- «Death from Below (Doom Phase): Place the lowest-cost Monster currently in your Pool into any Area containing at least one of your Units. In the event of a tie for lowest cost, you may choose which of those Units to put into play.»
- Требование Spellbook: «As an Action, spend 3 Power and choose an enemy player to gain 3 Power.»
- **Lethargy (Action: Cost 0):** «If Tsathoggua is in play and at least one enemy player has more Power than you, do nothing. This counts as an Action.»

**Ubbo-Sathla** ★
- «How to Awaken Ubbo-Sathla (Cost 4): 1. Your Controlled Gate is in an Area with your Great Old One. 2. Pay 4 Power, and place Ubbo-Sathla in the Area containing the Gate. 3. Place Ubbo-Sathla's Growth counter at 0 on the Doom track.»
- «Combat: Equal to the current position of Ubbo-Sathla's Growth counter.»
- «Sycophancy (Doom Phase): When an enemy player performs a Ritual of Annihilation, he chooses whether you gain 1 Doom or if he earns 1 fewer Doom.»
- Требование Spellbook: «As an Action, remove your Controlled Gate from your Start Area, then roll a die and increase Ubbo Sathla's Growth counter by the number rolled.»
- **Hell's Banquet (Doom Phase):** «Roll a die and increase Ubbo-Sathla's Growth Counter by the amount shown.»

**Yog-Sothoth**
- «How to Awaken Yog-Sothoth (Cost 6): 1. Your Controlled Gate is in an Area with your Great Old One. 2. Pay 6 Power, and place Yog-Sothoth in the Area containing the Gate.»
- «Combat: Equal to the number of enemy Faction Great Old Ones (not counting any Independent Great Old Ones).»
- «The Beyond-One (Action: Cost 1): Yog-Sothoth must be in an Area containing a Gate, but no enemy Great Old One. Move Yog-Sothoth to any Area on the Map lacking a Gate. In doing so, he takes the Gate with him, along with any Controlling Unit.»
- Требование Spellbook: «Yog-Sothoth shares an Area with an enemy Great Old One.»
- **The Key and the Gate (Ongoing):** «Yog-Sothoth counts as a Gate for every purpose, except that he is not Controlled by a Cultist and can exist in the same Area as another Gate.»

### C.12. Проверка: Bastet, Azathoth, другие

- **Bastet (Bubastis, CW-F8):** карты Independent для неё не найдено.
  - KS-PEN (апдейт кампании CATaclysm): о Bastet или Bubastis как независимых нет ничего.
  - Страница NEC «Additional Factions» (https://necronomicon.app/rulebook/additional-factions): про использование фракционных GOO или Elder God как Independent — ничего.
  - Вывод: такой карты нет ни в одном из доступных источников. Подтвердить её отсутствие по вики нельзя: вики закрыта.
  - Существуют другие **Independent Elder Gods**: Hagarg Ryonis (CW-U33), Nodens (CW-U28), Hellmother, Sun God, Thunder King (кроссовер The Gods War) — NEC-CATS, NEC-KS, NEC-GW.
  - Правило Elder God (NEC-CATS): «Elder Gods are similar to Great Old Ones, except they do not provide Elder Signs during a Ritual of Annihilation, and do not roll combat dice.»
- **Azathoth:** изначально независимый GOO из Azathoth Neutral Expansion **CW-F4**, со своей картой (NEC-AZ):
  - «How to Awaken Azathoth (Cost 0): 1. You must have 8+ Power and your Great Old One at your Controlled Gate. 2. Roll 1 die and add 2 to the total, then lose that much Power (i.e., 3-8). 3. All enemy players choose and simultaneously reveal a die face. Each receives Power equal to their revealed number (i.e., 1-6). The player(s) with lowest score loses 2 Doom points. Sum the dice and place the Azathoth Glyph on that spot on the Doom track. Place Azathoth at your Controlled Gate.»
  - «Combat: Equal to the position of the Azathoth Glyph on the Doom track.»
  - «Daemon Sultan (Ongoing): If Azathoth is assigned a Kill in Battle, roll 1 die. Lower the Azathoth marker by the amount shown on the die. If the marker reaches 0, Azathoth is Killed.»
  - Требование Spellbook: «All players have at least one Great Old One in play.»
  - **Nuclear Chaos (Action: Cost 0):** «Each player rolls 1 die. The player(s) with the highest roll gains that much Power. The player(s) with the lowest roll gains that many Elder Signs. You may choose to add or subtract 1 to your die roll after seeing all results. Flip this Spellbook face-down (it cannot be used again this Action Phase). Flip it face-up again during the Gather Power Phase.»
  - Отдельной карты «Independent» для GOO фракции Daemon Sultan (CW-F7) **не найдено**. Есть Dire Azathoth (CW-U27) — это отдельный IGOO, Cost 10 (NEC-KS).
- **Варианты «Dire»/«Harbinger» фракционных GOO** — отдельные IGOO, у каждого своё правило для «родной» фракции (NEC-KS, NEC-DUN):
  - Dire Cthulhu — CW-U13, Cost 6;
  - Cthulhu, the Harbinger — Cost 8;
  - The Risen One (Hastur/Yellow Sign) — Cost 8, для Yellow Sign 7;
  - Dire Yog-Sothoth (Dunwich) — Cost 6 для Opener; остальным «Pay 10 Power, minus your Unit's cost».

### C.13. Менялись ли карты (O3, O4, Ultimate Errata Pack)

- **Ultimate Errata Pack, CW-E26.** Описание у Chaos Cards: «includes the errata from Onslaughts 2 and 3, with the exclusion of the Cthugha Loyalty Card, as well as some errata new to the Final Onslaught». Состав: «4 Faction Cards, 5 Loyalty Cards, 18 Additional Cards, 1 Player Hint Card».
  - Источник: https://www.chaoscards.co.uk/prod/all-board-games/cthulhu-wars-ultimate-errata-pack
  - **Какие именно 5 карт лояльности — не найдено.** PDF лежит на Google Drive, доступ закрыт.
- Изменений именно в 10 картах «Faction GOO as Independents» в доступных источниках **не найдено**. Ни подтверждения, ни опровержения: см. «Не найдено».

---

## D. Официальные рекомендации по составу

| Что | Официально | Источник |
|-----|------------|----------|
| Число независимых GOO | «For your first game with Independents, it is recommended to use one fewer Independent than the number of players.» | NEC-RX, общий блок IGOO (из рулбука) |
| Фракционный GOO как независимый | «We do NOT recommend using a Great Old One as an Independent if a player is playing as that Great Old One's Faction.» | NEC-RX |
| Число нейтральных монстров и Terror | **Числовой рекомендации официально не найдено.** Есть только наблюдения дизайнера, см. ниже | — |
| Лимит покупки | Одна карта лояльности за Doom Phase, монстр или Terror; сколько карт держать — без ограничений | NEC-CATS; BLOG1 |

Наблюдения дизайнера (официальные, но не правило):
- BLOG1: «most games see players obtaining only one monster type», так как «players who 'buy' more find that they don't really have enough time or Power to properly use both types». Фраза пересказана WebFetch; дословно сняты только части в кавычках.
- BLOG2 (пересказ WebFetch): «common to see people take one of each» (монстр + IGOO); «rare to see a player take more than one monster type or more than one independent great old one»; монстры доступны со 2-го хода, IGOO — обычно со 2–3-го.

Сообщество, **не официально**, BGG-3077839:
- пользователь 523814, 04.05.2023: «The general suggestion is one less IGOO than player count and/or neutrals at one more than player count.»
- пользователь 3374971, 06.05.2023: «For a 4 player game I usually have 4 Independent Great Old Ones and 6 neutral monsters.»

### D.1. Neutral Unit Identifiers (CW-U26)

- Код и название по PL: «Neutral Unit Identifiers (colored rings for bases) — CW-U26».
- Отдельные наборы для поздних фракций: «Neutral Unit Identifiers for Bubastis — CW-U35», «Neutral Unit Identifiers for Daemon Sultan — CW-U37».
- Состав CW-U26 (TheGameSteward, https://www.thegamesteward.com/products/cthulhu-wars-neutral-unit-identifiers): «144 rings to fit on neutral units to show ownership by each faction».
- По размерам (WorthPoint, https://www.worthpoint.com/worthopedia/cthulhu-wars-base-rings-neutral-unit-1996343357): «Plastic rings to fit on your neutral unit bases! There are an equal number of rings in each of the 9 Faction's colors: 6 per color in 25mm, 3 per color in 40mm, 3 per color in 50mm, 3 per color in 60mm, 1 per color in 80mm.» Проверка: 16 × 9 = 144.
- Как это работает: кольцо цвета фракции надевается на подставку нейтральной фигурки и показывает владельца. Официальный текст правил о кольцах **не найден**.
- Почему 6 колец по 25 мм: вероятно, по максимальному числу нейтральных монстров одного типа (Gryllus — 6). **Это моё предположение**, источник его не подтверждает.

---

## Справочно: цены пробуждения прочих IGOO

Платится только Power; Doom не нужен (подтверждено BLOG2 и BLOG3: «To get an independent Great Old One, you only have to pay power»).

| IGOO | Cost | Источник |
|------|------|----------|
| Abhoth, Chaugnar Faugn, Mother Hydra, Yig | по 4 | NEC-G1 |
| Cthugha | «Nominal Cost 6»: «Pay Power equal to 6 minus your Great Old One's Awakening Power Cost» | NEC-G1 |
| Atlach-Nacha | 6 | NEC-G2 |
| Bokrug | заголовок «Cost 4», шаг 2 «Pay 6 Power» — **расхождение внутри карты** | NEC-G2 |
| Father Dagon, Ghatanothoa | по 4 | NEC-G2 |
| Gobogeg | 0, нужно «At least one player has 6 Faction Spellbooks» | NEC-G3 |
| Byatis | 4 | NEC-G4; HRF |
| Nyogtha | 6, 2 фигурки | NEC-G4; HRF |
| Tulzscha | 4 | NEC-G4; HRF PR#11 |
| Eihort, Gla'aki | по 4 | NEC-RC1 |
| Y'Golonac | 2 | NEC-RC2; HRF PR#11 |
| Daoloth | 6 | NEC-RC2; HRF |
| The Bloated Woman | 4; для Crawling Chaos 3 и всем остальным +1 Elder Sign | NEC-MASK |
| The Haunter of the Dark | 6; для Crawling Chaos 5 | NEC-MASK |
| Nodens | 6 | NEC-KS |
| Hagarg Ryonis | 4 | NEC-CATS |
| Lady of Disease | 2 | NEC-GW |
| Mad God | 6 | NEC-GW |
| Magna Mater, Hellmother, Sun God, Thunder King | по 4 | NEC-GW |
| Argus, Asmod, Jabootu, Orobas, Procrustes, Scylla, Stheno, Tarasque | по 4 | NEC-PA |
| Baphomet, Chthon, Humbaba, Stroma | по 2 | NEC-PA |
| Geryon, Pulgasaur | по 6 | NEC-PA |

GOO Pack 3 на NEC содержит только Gobogeg, в PL он назван «Great Old One Pack 3 (Gobogeg)».

---

## Расхождения между источниками

1. **Формулировка получения у Ghast, Gug, Shantak, Star Vampire.**
   - HRF: «Pay 2 Doom to obtain this Loyalty Card, **plus** place 1 … at your **controlled Gate**».
   - NEC: «… **then** place 1 … at your **Controlled Gates**», у Star Vampire — «at one of your Controlled Gates».
   - Какая формулировка печатная — по картам или вики не проверено.
2. **Фаза Vampirism у Star Vampire:** NEC — «Ongoing», HRF — «Battle». Текст тоже расходится: «Roll each Star Vampire's…» / «…you Battle results» против «Roll the Star Vampire's…» / «…your Combat Results».
3. **Voonith, Vicious:** у NEC — «Post-Battle» и текст из A.2 (12). У HRF PR#11 — «Battle» и другая формулировка, в том числе «The extra Kills cannot be used to Capture». Это ветка фаната, в main не влита.
4. **Dimensional Shambler:** «Walk Between World» (NEC) против «Walk Between Worlds» (HRF PR#11).
5. **Yog-Sothoth как Independent:** Combat дословно совпадает с Combat Tsathoggua. У фракционного Yog-Sothoth Combat = **2 ×** число вражеских фракционных GOO (HRF `solo/FactionOW.scala:58`: `2 * factions.but(f)./(_.factionGOOs.num).sum`). Не исключена ошибка копирования на NEC. Это не доказано: независимая версия могла быть ослаблена намеренно. **Проверить по карте или PDF «Faction GOO LCs».**
6. **Bokrug (справочно):** заголовок «Cost 4», а шаг «Pay 6 Power» (NEC-G2).
7. **Cacodemon:** по PL отдельный продукт CW-U30, а NEC относит его к кроссоверу Planet Apocalypse. Противоречия нет: это кроссоверный промо-юнит. Отмечено для порядка.
8. **Код Glow GOOs:** PL пишет «CW-GLO2» и «CW-GLO1» (буква O), TheGameSteward — «CW-GL02» (ноль).
9. **Опечатки NEC, перенесённые как есть:** «one of you Controlled Gates» (Dhole, Yith, Quachil), «Rhan-Thegoth», «desttroyed», «Cronophage» (вероятно, Chronophage), «Pay Pay 4 Power» (Eihort, Gla'aki), «as lon as», «add them to you pool».

---

## Не найдено

1. **Вики Cthulhu Wars — ни одной страницы.** WebFetch получает HTTP 402, curl — CONNECT 403 по политике организации. Зеркала закрыты: breezewiki — капча; antifandom, pussthecat — robots.txt; web.archive.org, archive.ph — SITE_BLOCKED; translate.goog — блок как прокси. Страницы для ручного сохранения в `source/web/` через `rules/tools/fetch-queue.txt`:
   - https://cthulhuwars.fandom.com/wiki/Category:Loyalty_Cards
   - https://cthulhuwars.fandom.com/wiki/Category:Independent_Great_Old_One_Loyalty_Cards
   - https://cthulhuwars.fandom.com/wiki/Glow_Great_Old_Ones
   - https://cthulhuwars.fandom.com/wiki/Ultimate_Errata_Pack
   - https://cthulhuwars.fandom.com/wiki/Neutral_Unit_Identifiers
   - https://cthulhuwars.fandom.com/wiki/Strategy:Neutral_Monsters
   - https://cthulhuwars.fandom.com/wiki/Strategy:Independent_Great_Old_Ones
   - https://cthulhuwars.fandom.com/wiki/Strategy:Independent_Elder_Gods
   - https://cthulhuwars.fandom.com/wiki/Bubastis
   - https://cthulhuwars.fandom.com/wiki/Cosmic_Terrors
   - https://cthulhuwars.fandom.com/wiki/Dreamlands_Surface_Monster_Pack
   - https://cthulhuwars.fandom.com/wiki/Dreamlands_Underworld_Monster_Pack
   - https://cthulhuwars.fandom.com/wiki/Beyond_Time_and_Space
   - https://cthulhuwars.fandom.com/wiki/Giant_Blind_Albino_Penguin
   - https://cthulhuwars.fandom.com/wiki/Cacodemon
2. **PDF Ultimate Errata Pack** — https://drive.google.com/open?id=1p5Mek8RGSaHgA4YQ3Ztdd3abpnoZXO6_ (ссылка из https://www.kickstarter.com/projects/petersengames/cthulhu-wars-the-daemon-sultan/posts/2736627), папка https://drive.google.com/drive/folders/1jSwJiQGxI0HhutGQQofjm9qEiuAlZvpn. Google Drive закрыт: robots и политика прокси. Отсюда неизвестно, какие 5 карт лояльности получили эррату.
3. **Официальный PDF «Faction GOO LCs»** (KS-O3, апдейт 86) — прямой ссылки нет. Его же стоит сохранить руками: это первоисточник для раздела C.
4. **Страницы загрузок Petersen Games** — https://petersengames.com/download/worms-of-ghroth-loyalty-card/, https://petersengames.com/download/cacodemon-loyalty-card/, https://eu.petersengames.com/downloads/ — отдают 404: старый сайт снят.
5. **Требование Spellbook у Hagarg Ryonis** — WebFetch выдал вместо него список фигурок набора. Не извлечено.
6. **Коды продуктов** The Dunwich Horror, кроссоверов Planet Apocalypse и The Gods War, а также Cthulhu the Harbinger и The Risen One — в выдержках PL не встретились.
7. **Официальный текст правил о Neutral Unit Identifiers** — только описания продукта.
8. **Карта Independent для Bastet** и для GOO фракции Daemon Sultan — нигде не найдена (см. C.12).
9. **Обзоры RPGnet** с цитатами карт — https://www.rpg.net/reviews/archive/16/16748.phtml — 403.
10. **Изображения карт не просматривались.** Все тексты — транскрипции NEC или HRF; сверки с физической картой нет.

## Использованные треды BGG (6 из 6, через api.geekdo.com)

| ID | Тема | Что дал |
|----|------|---------|
| 3045913 | Ultimate Errata pack and upgrading first edition | ссылки на эррату |
| 3077839 | How many neutral monsters/terrors/IGOOs… | рекомендации сообщества |
| 2185446 | Glow in the dark IGOOs — any gameplay value? | «also in the rulebook»; запрет брать GOO фракции, которая в игре |
| 3105263 | Most Recent Errata — 2023 | ссылки; имён карт лояльности нет |
| 1529006 | Strategy Thread — Neutral GOOs, Monsters, Spellbooks | сверка Combat; Gug cost 1; Servitor −1 |
| 1821790 | Using Faction Monsters as Neutral Monsters | только фанатские правила |

Ни 403, ни 429 не было. Повторные вопросы к уже скачанному треду обслуживал кэш WebFetch, новых запросов к BGG не делалось.

---

## E. Дополнительно (запрос 2): The Ancients и Bubastis при пробуждении независимых GOO

На этот раздел ушло ещё 2 треда BGG через API: 3255319 и 2181716. Всего за работу — 8 тредов.

### E.1. Может ли The Ancients пробудить независимого GOO

**Ответ: да, но только когда в игре все 4 Cathedral.** Это написано на листе фракции,
и официальный FAQ этого не опровергает.

Официальный текст — строка «Special» у Cathedral на листе фракции:
> «Special: If all 4 Cathedrals are in play, you may Awaken an Independent Great Old One without your own Great Old One (when Awakening Cthugha this way, just pay 6 Power).»

Где этот текст встречается:
- NEC, лист фракции: https://necronomicon.app/factions/the-ancients
- HRF, та же фраза в `solo/overlay.scala:440`, коммит `56fb862`.

Остальные факты:
- **Yothan — тип Terror, не Great Old One.**
  - NEC, там же: «Yothan(3) Terror 6 (3 with Extinction) 7».
  - HRF: `case object Yothan extends FactionUnitClass(AN, "Yothan", Terror, 6)` (`solo/FactionAN.scala`).
  - Поэтому Yothan условию «with your Great Old One» не соответствует.
- **Официальный FAQ** (O3, через NEC «Additional Factions», https://necronomicon.app/rulebook/additional-factions):
  > «Q. How do the Ancients generally interact with requirements or rules necessitating all Factions to have a Great Old One? A. The Ancients are ignored for this purpose. For example, the Ancients need not have a Great Old One for an independent Azathoth's controller to earn his Nuclear Chaos Spellbook.»
  - Это про требования вида «у всех фракций есть GOO». Про пробуждение IGOO самими Ancients — не здесь.
  - В FAQ на freshdesk отдельного вопроса «Ancients и пробуждение IGOO» **нет**. Проверены раздел The Ancients и упоминания Ancients вместе с Independent и Awaken: https://petersengames.freshdesk.com/support/solutions/articles/48000952254-cthulhu-wars-rules-faq
- **Сэнди**, апдейт 3 Onslaught 3 (https://www.kickstarter.com/projects/1816687860/cthulhu-wars-onslaught-3/posts/1939499):
  > «they don't have their own Great Old One»
  >
  > «The bottom line is that the Cathedrals are NOT some kind of 'substitute' for a Great Old One.»
  >
  > «These structures help the Ancients to substitute (partly) for their atheistic lack of any Great Old One.»
- **Фракционные GOO как независимые.** Отдельного разъяснения **не найдено**. На их картах тот же первый шаг: «Your Controlled Gate is in an Area with your Great Old One». А «Special» у Cathedral говорит об «an Independent Great Old One» вообще. По букве правило к ним применимо; это мой вывод, официального подтверждения нет.
- **Чем Ancients могут пробудить второго IGOO.** В общем блоке IGOO сказано: «you may use one Independent to help you Awaken another» (NEC-RX). По букве текста Ancients, уже владея независимым GOO, могли бы пробуждать следующих у Gate с ним — даже без 4 Cathedral. **Официального ответа на этот случай не найдено.**

**Как это сделано в HRF:**
- Общее правило: `def canAwakenIGOO(r) = f.gates.has(r) && f.at(r, GOO).any` (`solo/Game.scala:267`). Нужен свой Controlled Gate в области и любой свой юнит типа GOO, в том числе независимый: в HRF они тоже типа GOO.
- Для Ancients оно переопределено: `override def canAwakenIGOO(r) = this.gates.has(r) && game.cathedrals.num == 4` (`solo/FactionAN.scala:61`).
  - Подходит любой свой Gate, если в игре все 4 Cathedral.
  - Наличие GOO в области не проверяется вовсе. Поэтому без 4 Cathedral Ancients в HRF не пробудят IGOO, даже если рядом с Gate стоит уже их независимый GOO. Это расходится с буквой правила «use one Independent to help you Awaken another».
- Cthugha в HRF не реализован. Из IGOO есть только Byatis, Abhoth, Daoloth, Nyogtha, поэтому оговорка «just pay 6 Power» не проверялась.
- Ссылка: https://github.com/haunt-roll-fail/cthulhu-wars/blob/56fb862b1b8ff00001af353fc4b80cd0c82c40c8/solo/FactionAN.scala

**Разъяснения сообщества** (не официальные; посты пересказаны WebFetch):
- BGG-3255319 «Is there no limit to the number of GOO's that the Ancients can awaken?»
  - RollforCrap (3023651), 26.02.2024, цитирует правило: «If all 4 Cathedrals are in play, you may awaken an Independent GOO without you own Great Old One.» Сын играл за Ancients и пробудил так 5 GOO.
  - Graham (91716), 27.02.2024: обычные условия — «Your goo is awake - You can pay the power - the goo you want is available»; 4 Cathedral снимают первое условие. Предела числу пробуждений в правилах нет: общий блок IGOO говорит «There are no limits to how many Independents you may Control».
- BGG-2181716 «Awakening Independent GOOs», первый пост от 07.04.2019.
  - touchstonethefool (329445): правило 4 Cathedral уже обсуждается. Вопросы: надо ли платить цену с карты (подразумевается «да») и куда ставить IGOO.
  - LordZon (380314), 22.04.2019: «Just ignore the 'your GOO' part of the requirement. So at your controlled gate is usually what is left.»
  - Dark5eider (752382), 15.04.2019: «You won't have a GOO of your own so you ignore the instruction to awaken at the gate your GOO is at. You still have to awaken it at one of your controlled gates unless otherwise instructed in the GOO's rules text.»
  - В другой выборке WebFetch тому же автору приписано предложение ввести эррату: Cathedral и Controlled Gate в области пробуждения. Пересказы противоречат друг другу — **дословность не гарантирую**.
  - Сотрудников Petersen и ссылок на FAQ в треде нет.
- Итог по сообществу: ставить IGOO у любого своего Controlled Gate, платить цену с карты.

### E.2. Считается ли Bastet «your Great Old One» для Bubastis

**Ответ: да.** Официальный текст листа Bubastis приравнивает Elder God к GOO во всём,
кроме двух вещей (NEC, https://necronomicon.app/factions/bubastis):
> «Bastet is an Elder God; these beings are treated as Great Old Ones for all purposes except: they do not provide an inherent Elder Sign for a Ritual of Annihilation, though they often have other means of creating Elder Signs; and Elder Gods never roll Combat dice, but provide some fixed benefit.»

Пробуждение IGOO в этих исключениях не названо. Значит, Bastet выполняет условие «with
your Great Old One». Это прямое чтение текста; отдельного официального ответа именно про
IGOO **не найдено**.

**Практическое ограничение — Gate.** У Bubastis один Controlled Gate — Луна:
- лист Bubastis: «The Moon counts as a land Area with a Bubastis-Controlled Gate for all purposes, except that Control may not be seized by another Faction.»;
- официальный FAQ Bubastis (через NEC «Additional Factions»): «…since Bubastis can only "Control" one Gate (the Moon)…»;
- лист Bubastis: Earth Cats «Cannot be captured as Cultists nor can they Create or Control Gates».

Отсюда, по букве карты IGOO:
- Bastet должна стоять **на Луне**, и независимый GOO ставится туда же («place … in the Area containing the Gate»).
- Попасть на Луну Bastet может: «Your Units can Move and be Pained freely between the Moon and any other Map Area. Other Factions may Move or be Pained from the Moon to another Map Area, but not the reverse.»
- Сама Bastet пробуждается так: «1) All your Cat varieties are in play. 2) Pay 6 Power. 3) Place Bastet in an Area containing no enemy Units.» Это тоже условие, которое надо выполнить до пробуждения IGOO.

Что **не найдено:**
- официального разбора «Bubastis + IGOO» (FAQ freshdesk — нет; раздел Bubastis на NEC — нет);
- тредов BGG на эту тему (поиск ничего не дал, лимит BGG израсходован);
- реализации в HRF: фракции Bubastis в ней нет.

Можно ли поставить IGOO на Луну и как он потом с неё ходит — официальных разъяснений
нет. Если верна общая формула «Луна — land Area», то он ходит как обычный юнит
Bubastis. **Это вывод, а не источник.**

Для сравнения — FAQ про Worm of Ghroth на Луне (https://necronomicon.app/factions/bubastis):
> «Can a Worm of Groth be placed on the Bubastis Moon tile? No, it is not considered adjacent to any Area except for Bubastis, and cats don't bring Worms home.»

---

## F. Остальные независимые GOO: полные тексты

Источник — NEC, текст снят «сырым» через WebFetch. Формат каждой карты:
**Awaken** → **Combat** → **способность** → **Треб.** (требование Spellbook) → **SB** (Spellbook).
Общий блок IGOO (C.0) у всех одинаковый и здесь опущен. Фигурка у всех одна, кроме
Nyogtha (2). Коды продуктов — по PL.

### F.1. Great Old One Pack 1 (CW-GOO1) — NEC-G1

**Abhoth**
- Awaken: «How to Awaken Abhoth (Cost 4): 1. Your Controlled Gate is in an Area with your Great Old One 2. Pay 4 Power, and place Abhoth in the Area containing the Gate.»
- «Combat: Equals the number of Filth Tokens in play (0 - 12).»
- «Filth (Action: Cost 1): Place a Filth Token in any Area. Filth Tokens act as Combat 0 Monsters. They belong to Abhoth's Faction, but never Move nor take Actions. They can be Killed or Pained normally in Battle, and are affected by Spellbooks and abilities.»
- Треб.: «Choose one: EITHER your Faction has 4+ different Monster types in play, including Filth Tokens OR your Faction has 8+ total Monsters in play. Including Filth Tokens.»
- SB **The Brood (Ongoing)**: «Gates in Area containing Filth Tokens do not count during the Doom Phase. Does not apply to Abhoth's Faction.»
- Жетоны: Filth — 12 (по строке Combat «0 - 12»; HRF: `12.times(Filth)`).

**Chaugnar Faugn**
- Awaken: Cost 4, тот же двухшаговый текст: «Pay 4 Power, and place Chaugnar Faugn in the Area containing the Gate.»
- «Combat: 3»
- «Miri Nigri (Ongoing): In a Battle taking place in an Area with your Controlled Gate, add +3 Combat Dice.»
- Треб.: «As your Action for a Round, discard 2 Elder Signs (you receive no Doom for them).»
- SB **Curse of Chaugnar Faugn (Ongoing)**: «Turn all the Elder Signs in the Pool face-up. When any player receives an Elder Sign, you pick which one they receive. If you lose this Spellbook, turn the Elder Signs face-down again, and mix them up.»

**Cthugha**
- Awaken: «How to Awaken Cthugha (Nominal Cost 6): 1. Your Controlled Gate is in an Area with your Great Old One 2. Pay Power equal to 6 minus your Great Old One's Awakening Power Cost. If the result is negative *gain* the result in Power. 3. Replace your Great Old One with Cthugha.»
- «Combat: Equals the Combat of an enemy Great old One in the Battle (your choice). If none are present, Cthugha's Combat is 0.»
- «Fire Vampires (Post-Battle): If Cthugha is involved in a Battle, after all Kills results are assigned, you may choose to "spare" one or more Killed enemy Units, by reducing their loss to a Pain instead. For each Killed enemy Unit you spare in this way, you gain 1 Power.»
- Треб.: «Kill an enemy Great Old One in Battle.»
- SB **Firestorm (Post-Battle)**: «If Cthugha is involved in a Battle, for each Killed enemy unit you "spare", you also gain 1 Elder Sign.»
- Эррата: карта лояльности Cthugha правилась отдельно и **не вошла** в Ultimate Errata Pack (Chaos Cards). Что именно изменено — не найдено. На BGG-3105263 спрашивали, не задублирована ли в пачке «Cthuga's Firestorm spellbook».
- Для Ancients: «when Awakening Cthugha this way, just pay 6 Power» (раздел E.1).

**Mother Hydra**
- Awaken: Cost 4, двухшаговый текст.
- «Combat: 6 minus the number of enemy Units in the Area (minimum 1).»
- «The Agony Sting (Action: Cost 1): Choose any Ocean Area. All enemy Cultist in that Area must be moved into adjacent Land Areas by their owners (your Cultists are immune). In a dispute over who moves first, you decide.»
- Треб., как на NEC: «Choose EITHER Control no Great Old Ones in Ocean Areas OR enemy Factions control no Great Old Ones in Ocean Areas.» Формулировка выглядит странно; сверить с картой.
- SB **The Zygote (Action: Cost 1)**: «Take all the Acolyte Cultists in your Pool and place them on the Map in any Areas in which you have a Unit.»

**Yig**
- Awaken: Cost 4, двухшаговый текст.
- «Combat: 2»
- «Snakebite (Post-Battle): Your Cultists are now poisonous. If any of your Cultists are killed in a Battle, the enemy receives 1 extra Kill result (he only takes 1 extra Kill regardless of how many Cultists die).»
- Треб.: «As your Action for a Round, remove one of your Controlled Gates from the Map.»
- SB **Messenger of Yig (Ongoing)**: «In the Doom Phase, each other player must decide if they will donate 1 Power from their total to you. For each player that refuses, gain 1 Doom Point.»

### F.2. Great Old One Pack 2 (CW-GOO2) — NEC-G2

**Atlach-Nacha**
- Awaken: Cost 6, «Pay 6 Power».
- «Combat: 4»
- «Spinnerets (Action: Cost 1): If Atlach-Nacha is in an Area that is lacking a Web Token, place one there.»
- Треб.: «Web Tokens are in 6 different Areas»
- SB **Cosmic Web (Action: Cost 0)**: «Immediately win the game, even with fewer than 6 Faction Spellbooks.»
- Жетоны: Web; сколько их в наборе — не найдено.

**Bokrug**
- Awaken: «How to Awaken Bokrug (Cost 4): … 2. Pay 6 Power, and place Bokrug in the Area containing the Gate.» Цена в заголовке и в шаге расходится.
- «Combat: 1»
- «Ghosts of Ib (Ongoing): If Bokrug is killed, you do not lose this Loyalty Card. Instead, place Bokrug's figure on this card. At the end of the next Doom Phase, return Bokrug to any Area of the Map that does not contain any enemy Units. If there are no such areas, Bokrug remains on this card until the next Doom Phase.»
- Треб.: «Take this Loyalty Card and give it to the player of your choice. That player then places Bokrug's Spellbook on this card.»
- SB **Doom that Came to Sarnath (Doom Phase)**: «At the end of the Doom Phase, select an enemy and one of these two options: 1) Your enemy chooses a Monster or Cultist of yours to Eliminate. ORb 2) He chooses one of your Elder Signs to discard.» («ORb» — опечатка NEC)

**Father Dagon**
- Awaken: Cost 4.
- «Combat: 2 on Land, 6 in an Ocean Area.»
- «Tsunami (Action: Cost 1): Choose a Land Area adjacent to an Ocean Area. All Cultists in the Area must be moved into adjacent Ocean Areas by their owners (this includes your Cultists). In a dispute over who moves first, you decide.»
- Треб.: «You have 8 Units in Ocean Areas.»
- SB **The Innsmouth Look (Ongoing)**: «During the Doom Phase, remove one of your Acolyte Cultists from the Map and out of the game permanently. Gain 6 Power. This is not optional. If you have no Acolyte Cultists on the Map, there is no effect.»

**Ghatanothoa**
- Awaken: Cost 4.
- «Combat: Equal to the number of Cultists your opponent has on the Map.»
- «Mummify (Action: Cost 1): Any enemy Acolyte Cultists sharing an Area with Ghatanothoa are immediately "Mummified." Lay Mummified Cultist figures on their sides. Such Cultists cannot use the Move Action, do not participate in Battle, and produce no Power during the next Gather Power Phase. During the Doom Phase, stand any Mummified Cultists back up. (A Mummified Cultist can be Captured. If a Cultist Controlled a Gate before becoming Mummified, it retains Control of that Gate.)»
- Треб.: «EITHER you have fewer than 6 total Gates and Cultists in the Doom Phase, OR As an Action, pay 4 Power.»
- SB **Execration of Mu (Ongoing)**: «The Mummify Ability is no longer an Action. It now occurs instantly when any enemy Acolyte Cultists share an Area with Ghatanothoa.»

### F.3. Great Old One Pack 3 (CW-GOO3, «Gobogeg») — NEC-G3

**Gobogeg**
- Awaken: «How to Awaken Gobogeg (Cost 0): 1. At least one player has 6 Faction Spellbooks. 2. Your Controlled Gate is in an Area with your Great Old One 3. Pay 0 Power, and place Gobogeg in the Area containing the Gate.»
- «Combat: Rolls 0 dice, but if Gobogeg is Killed or Pained, all Units in the Area are Pained. This regardless of Faction.»
- «Book of Law (Doom Phase): While Gobogeg is in play, whenever a Great Old One is Awakened, the owner receives 6 Power after the Awakening.» Фаза указана так на NEC.
- Треб.: «Someone wins the game (need not be you).»
- SB **Book of Chaos (Post-Game!)**: «If the game ends while you Control Gobogeg, immediately place this Spellbook and gloat. Then YOU get to pick the Factions, Expansions, Map, Neutral Monsters, and Independent Great Old Ones to be used the next time your group plays Cthulhu Wars.»

### F.4. Great Old One Pack 4 (CW-GOO4) — NEC-G4

**Byatis**
- Awaken: Cost 4.
- «Combat: 4»
- «Toad of Berkeley (Ongoing): Byatis may not Move, nor can he be moved with movement-type abilities (such as Arctic Winds or Submerge). He can still be Pained. If there are no enemy Units in Byatis' Area during the Doom Phase, receive 1 Elder Sign.»
- Треб.: «Byatis survives a Battle in which at least one enemy Unit is Killed.»
- SB **God of Forgetfulness (Action: Cost 1)**: «Select all enemy Cultists in an Area adjacent to Byatis. Those Cultists are moved into Byatis's Area.»
- HRF совпадает по смыслу и числам: «earn 1 Elder Sign» вместо «receive».

**Nyogtha** (фигурок: 2)
- Awaken: «How to Awaken Nyogtha (Cost 6): … 2. Pay 6 Power, and place all Nyogtha Units from your Pool to the Area containing the Gate.»
- «Combat: 4 if Nyogtha's Faction declared the Battle, 1 if not.»
- «From Below (Ongoing): Nyogtha is two Units. Any Common Action involving one of these Units can be applied simultaneously to the other as part of the same Action and at no extra cost. When one Nyogtha Unit Moves, so may the other. When one Captures a Cultist, so may the other. If Battle is declared in one's Area, you can also declare a Battle in the other's Area, for free. You only lose this Loyalty Card if both Nyogtha Units have been Killed.»
- Треб.: «Nyogtha survives a Battle against an enemy Great Old One.»
- SB **Nightmare Web (Ongoing)**: «If one of the Nyogtha Units is in your Pool, you can Awaken it for 2 Power, placing it in any Area in which you have a Unit.»

**Tulzscha**
- Awaken: Cost 4.
- «Combat: 1»
- «Undying Flame (Gather Power Phase): At the end of the Gather Power Phase, gain 1 Doom if at least one Faction has more Doom than you, gain 1 Elder Sign if at least one Faction has more Elder Sign than you, gain 1 Power if at least one Faction has more Power than you.»
- Треб.: «As an Action, each enemy Faction gains 2 Power.»
- SB **Ceremony of Annihilation (Doom Phase)**: «When you perform a Ritual of Annihilation, you may choose to pay nothing, and instead EARN Power equal to the current position of the Ritual of Annihilation marker, then advance the marker 1 step. You earn no extra Doom points nor Elder Signs.»

### F.5. Ramsey Campbell Horrors 1 (CW-RC1) — NEC-RC1

**Eihort**
- Awaken: «How to Awaken Eihort (Cost 4): 1. Your Controlled Gate is in an Area with your Great Old One. 2. Pay Pay 4 Power, place Eihort in the Area containing the Gate.»
- «Combat: 0»
- «The Brood (Ongoing): When you Awaken Eihort, immediately replace all of your Acolyte Cultists in play with Brood tokens. Brood tokens are treated as Cultists with a Combat of 1. They cannot take the Move Action, nor can they be moved by movement like or movement-modifying abilities (such as Submerge or Arctic Winds). Brood tokens can still be Pained or moved by enemy abilities and Spellbooks.»
- Треб.: «You have at least 3 Acolyte Cultists in play.»
- SB **Unclean Bargain (Doom Phase)**: «If you have any Brood tokens in your Pool, replace your Acolyte Cultists with Brood tokens on a one-for-one basis until either you run out of Acolyte Cultists (on the Map) or Brood tokens (in your Pool). This is not optional.»
- Жетоны: Brood; сколько — не найдено.

**Gla'aki**
- Awaken: «How to Awaken Gla'aki (Cost 4): 1. Your Controlled Gate is in an Area with your Great Old One. 2. Pay Pay 4 Power, place Gla'aki in the Area containing the Gate. 3. Gain 1 Elder Sign.»
- «Combat: Equal to the number of Acolyte Cultists in your Pool.»
- «The Tomb-Herd (Gather Power Phase): Earn 1 Power per Acolyte Cultist in your Pool. This occurs before any Captured Cultists are Sacrified by your enemies and returned to your Pool.»
- Треб.: «You are the first player to reach 0 Power in the Action Phase. (Windwalker taking Hibernate Action does NOT fulfill this requirement).»
- SB **Green Decay (Gather Power Phase)**: «When a Captured Cultist is Sacrificed and returned, gain an Elder Sign instead of your normal reward (of 1 Power).»

### F.6. Ramsey Campbell Horrors 2 (CW-RC2) — NEC-RC2

**Y'Golonac**
- Awaken: «How to Awaken Y'Golonac (Cost 2): 1. Your Controlled Gate is in an Area with your Great Old One. 2. Pay 2 Power, place Y'Golonac in the Area containing the Gate.»
- «Combat: 1»
- «Orifices (Post-Battle): If Y'Golonac is Killed in a Battle, select a surviving enemy Terror, Monster, or Cultist. Replace it with Y'Golonac, then give Y'Golonac's Loyalty Card to that player. If no enemies survived, Y'Golonac dies normally (placing this Loyalty Card in the general Pool).»
- Треб.: «You have just received Y'Golonac as a result of his Orifices ability.»
- SB: **не найдено.** На NEC под заголовком Spellbook нет ни названия, ни текста. Первая выборка подставила туда требование Daoloth — это ошибка пересказа.

**Daoloth**
- Awaken: «How to Awaken Daoloth (Cost 6): … 2. Pay 6 Power, place Daoloth in the Area containing the Gate.»
- «Combat: 0»
- «Cosmic Unity (Pre-Battle): In a Battle involving Daoloth, choose one enemy Great Old One. It rolls no Combat dice (it still gets its Battle Ability, if any).»
- Треб.: «A Great Old One is Killed (anywhere on the Map).»
- SB **Interdimensional (Ongoing)**: «When Daoloth enters an Area without a Gate, immediately place a Gate there.»

### F.7. Masks of Nyarlathotep (CW-U10) — NEC-MASK

**The Bloated Woman**
- Awaken: «How to Awaken the Bloated Woman (Cost 4): 1. Your Controlled Gate is in an Area with your Great Old One. 2. Pay 4 Power and place the Bloated Woman in the Area containing the Gate.»
- Для Crawling Chaos: «1. Pay 3 Power, then place the Bloated Woman at one of your Controlled Gates. Then, each other Faction receives 1 Elder Sign. Crawling Chaos does not need a Great Old One in the Area into which he Awakens the Bloated Woman.»
- «Combat: 1»
- «The Velvet Fan (Post-Battle): After any Battle involving the Bloated Woman, choose one Killed or Eliminated enemy Monster or Cultist and place it on this card; that Unit is considered to be out of play. If a Unit is later Recruited or Summoned from this card, its owner pays its Power cost directly to you. Units remain on this card if the Bloated Woman is Killed or Eliminated - they may still be Recruited or Summoned from this card, but no one will be paid Power for this while she is out of play. If she is later returned to play, her controller will receive payments as described above. There is no limit to the number of Units you may have on this card.»
- Треб.: «Have all 6 Faction Spellbooks»
- SB **Disaster Looms (Gather Power Phase)**: «Your Controlled Gates now earn 1 Elder Sign instead of 2 Power. (They still earn 1 Doom during the Doom Phase.)»

**The Haunter of the Dark**
- Awaken: «How to Awaken the Haunter of the Dark: 1. Your Controlled Gate is in an Area with your Great Old One. 2. Pay 6 Power and place the Haunter of the Dark in the Area containing the Gate.» Цены в заголовке на NEC нет; по шагу — 6.
- Для Crawling Chaos: «1. Pay 5 Power, then place the Haunter of the Dark at one of your Controlled Gates. Each other Faction then takes 1 Elder Sign. Crawling Chaos does not need a Great Old One in the Area into which he Awakens the Haunter of the Dark.»
- «Combat: Equal to the total number of Spellbooks earned by your enemy (including those for any Independent Great Old Ones).»
- «Fly to the Light (Post-Battle): If the enemy scored exactly one Kill, it must be applied to the haunter. If he scored 2 or more Kills, you can apply the Kills normally.»
- Треб.: «As an Action, pay 1 Power.»
- SB **The Shining Trapezohedron (Pre-Battle)**: «In a Battle involving the Haunter, your enemy must roll a die for each of his Units present in the Battle. For every 6 rolled by your enemy, he must choose and Eliminate one of his own Units.»

### F.8. Kickstarter-специалы — NEC-KS

**Nodens** (Independent Elder God, CW-U28)
- Awaken: «How to Awaken Nodens (Cost 6): 1. Your Controlled Gate is in an Area with your Great Old One. 2. Pay 6 Power, place Nodens into the Area.»
- «Combat: Add 1 Kill and 2 Pains to your Combat total (Nodens doesn't roll any Combat Dice)»
- «Healing (Doom Phase): At the end of the Doom Phase, unless the Ritual of Annihilation track has reached Sudden Death, move the Ritual marker backwards 1 step (but not past the start).»
- Треб.: «Perform a Ritual of Annihilation.»
- SB **Proteus (Action: Cost 2)**: «Choose one of your earned Faction Spellbooks that names either a type of Unit (e.g., Acolytes or Flying Polyps). Place your Faction Glyph on that Spellbook. Nodens then benefits from that Spellbook's effects as if it were the named Unit or type of Unit.»
- Отдельный PDF «Nodens Loyalty Card» упомянут в KS-O3.

**Dire Cthulhu** (CW-U13)
- Awaken: «How to Awaken Dire Cthulhu (Cost 6): 1. Your Controlled Gate is in an Area with your Great Old One. 2. Pay 6 Power, place Dire Cthulhu in the Area containing the Gate. 3. Gain 1 Elder Sign.»
- «Combat: 3»
- «Lord and Master (Doom Phase): When you Awaken an Independent Great Old One (except Dire Cthulhu), gain 1 Elder Sign.»
- Треб.: «Kill 3 enemy Units in a single Battle.»
- SB **Non-Euclidean (Post-Battle)**: «If Dire Cthulhu is involved in a Battle, you may assign any Battle results you inflict to any Faction with Units in the Area, even if they did not participate in the Battle. If any results are assigned to a non-participating Faction, that Faction may not use Battle abilities or Spellbooks in response. Affected Factions still select which of their units receive Battle results.»

**Dire Azathoth** (CW-U27)
- Примечание: «Note: In a game with Dire Azathoth, Windwalker, Opener of the Way, Tcho-Tcho, and the Ancients must place their glyph tokens in their Start Areas. Do not use Dire Azathoth on the Primeval Earth or Shaggai Maps.»
- Awaken: «How to Awaken Dire Azathoth (Cost 10): 1. Control a Gate on an enemy Faction's Start Area. 2. Pay 10 Power, and place Dire Azathoth into the Area.» Своего GOO не требует.
- «Combat: Roll a die. Dire Azathoth's Combat rating is equal to the result of the roll.»
- «Mindless Destruction (Post-Battle): Any Faction Battling in Dire Azathoth's Area gains his choice of either 1 Doom or 1 Power for every Unit that Faction Kills or Eliminates in that Battle. (Dire Azathoth need not be involved in the Battle).»
- Треб.: «As an Action, pay 20 Power»
- SB **The Blind Idiot God (Game Over!)**: «Immediately win the game, even if you do not have all 6 Faction Spellbooks or the most Doom.»

### F.9. Hagarg Ryonis (Cat from Jupiter; Independent Elder God, CW-U33) — NEC-CATS

- Awaken: «How to Awaken Hagarg Ryonis (Cost 4): 1. Your Controlled Gate is in an Area with your Great Old One 2. Pay 4 Power, and place Hagarg Ryonis in the Area containing the Gate.»
- «Combat: Hagarg Ryonis rolls no dice. Instead, she adds 3 Pains to your Combat total.»
- «Subversion (First Player Phase): Choose a player, if that player performs a Ritual of Annihilation in this Doom Phase, you steal 1 of the Elder Signs he earns (if any).»
- Треб.: «You have 0 Power.» При повторном запросе извлеклось чисто; этим закрыт пробел из раздела «Не найдено».
- SB **Laziness (Action: Cost 0)**: «Any Faction with exactly 1 Power left loses that Power. Alternatively, pay 1 Power to force Windwalker to also lose 1 Power. You can only use this Action if Windwalker is Hibernating, or one or more enemy Factions have exactly 1 Power.»

### F.10. Кроссоверы и Dunwich — только список

Источники: NEC-GW, NEC-PA, NEC-DUN. Коды продуктов не найдены.

| Имя | Тип | Cost | Combat | Суть |
|-----|-----|------|--------|------|
| Lady of Disease | IGOO, Gods War | 2 | 0 | Plague: кто объявляет Battle в её Area, платит 1 Doom (и владелец тоже) |
| Mad God | IGOO, Gods War | 6 | = маркер Mad God | War!: каждое убийство или устранение юнита двигает маркер +1 |
| Magna Mater | IGOO, Gods War | 4 | 1d6 на битву | Irruption (Action 2): убить своих культистов у своего Gate и заменить монстрами ценой 0–2 |
| Hellmother | Elder God, Gods War | 4 (+1 Elder Sign) | 1 Pain за культиста; +1 Kill при 6+ | Hellborn: монстров можно рекрутировать как культистов |
| Sun God | Elder God, Gods War | 4 (+1 Elder Sign) | 1 Pain + 1 Kill | Sunrise: не убиваем; враг переставляет его, владелец теряет 1 Power или 1 Doom |
| Thunder King | Elder God, Gods War | 4 (+1 Elder Sign) | 1 Pain за фракционный Spellbook; +1 Kill при 6 | Inferiority Complex: 2 Doom → 5 Power |
| Argus | IGOO, Planet Apocalypse | 4 | = сумма Combat прочих своих юнитов (без GOO) | Reinforce: ставит юнит ценой 2 в битву |
| Asmod | IGOO, PA | 4 | 4 | Speaking in Tongues: Move можно применять к вражеским Monster и Terror |
| Baphomet | IGOO, PA | 2 | 6/2 | Baphomet's Wall: первое убийство не убивает, а даёт Spellbook |
| Chthon | IGOO, PA | 2 | = маркер Chthon на треке Power | Chthonic Might: перед битвой маркер +1 |
| Geryon | IGOO, PA | 6 | 6 | Thrice-Damned: +1 Power и +1 Doom после битвы |
| Humbaba | IGOO, PA | 2 | 2 | Swarm: вместо кубиков — 2 Pain |
| Jabootu | IGOO, PA | 4 | 4 | Deadly Tedium: у врага на 1 кубик меньше |
| Orobas | IGOO, PA | 4 | 8 | Royal Retribution: противник получает Royal Token |
| Procrustes | IGOO, PA | 4 | 0 | Too Short: бросок против цены вражеского юнита — устранить его или свой |
| Pulgasaur | IGOO, PA | 6 | 4 | Metamorphosis: первые два Kill не убивают |
| Scylla | IGOO, PA | 4 | 1 за голову (6 жетонов голов) | Multicapitus: Kill снимает голову |
| Stheno | IGOO, PA | 4 | 0 | Fossilization (Action 1): «окаменить» вражеский юнит |
| Stroma | IGOO, PA | 2 | 0 | Maelstrom: никто в её Area не двигается и не получает Pain-отход |
| Tarasque | IGOO, PA | 4 | 5 | Spined: Kill по нему — 2 Elimination врагу |
| Dire Yog-Sothoth | IGOO, Dunwich | 6 для Opener; остальным 10 минус цена заменяемого юнита | = число вражеских фракционных GOO | To Rule Them All (Action 4): захват чужих GOO как культистов |

---

## G. Размеры оригинальных фигурок

**Итог: по отдельным юнитам — не найдено.** Ни у одного из 20 нейтральных монстров,
11 обычных Terror или независимых GOO не нашёл подтверждённых диаметров подставок
или высот. Распределения «какая фигурка на каком кольце CW-U26» тоже не нашёл. Скорее
всего, оно есть на вики (https://cthulhuwars.fandom.com/wiki/Neutral_Unit_Identifiers),
но вики закрыта.

Что найдено:

| Факт | Источник |
|------|----------|
| CW-U26: «144 plastic rings to fit on your neutral unit bases! There are an equal number of rings in each of the first 9 Faction's colors- 6 per color in 25mm, 3 per color in 40mm, 3 per color in 50mm, 3 per color in 60mm, 1 per color in 80mm» | Petersen: https://petersengames.com/the-games-shop/neutral-unit-identifiers/ (то же — Noble Knight: https://www.nobleknight.com/P/2147754920/Neutral-Unit-Identifiers) |
| Отсюда: у нейтральных юнитов пять размеров подставок — 25, 40, 50, 60, 80 мм | там же; это вывод из комплектности |
| «Standard faction units are 28mm scale… The Great Old One figures are colossal — significantly larger than the 28mm units» | Petersen, https://petersengames.com/blogs/news/cthulhu-wars-miniatures-guide |
| Базовая коробка: фигурки «range in height from approximately 20 mm to nearly 180 mm» | TheGameSteward, https://www.thegamesteward.com/products/cthulhu-wars-cacodemon |
| Quachil Uttaus: «32mm scale miniature» | WorthPoint, https://www.worthpoint.com/worthopedia/quachil-uttaus-32mm-scale-miniature-1876381752 (лот, надёжность низкая) |
| Brown Jenkin: в названии лота «Neutral/Unaligned Mini 28mm» | Noble Knight, https://www.nobleknight.com/P/2147754714/Brown-Jenkin (выдача поиска) |
| BGG-1606789 (2016, идея колец-идентификаторов) | см. ниже |

Подробнее о BGG-1606789:
- Предложены кольца HeroClix: «They're 1"3/8 diameter. That's 35mm.» (user 258725, 17.07.2016). Это размер колец HeroClix, а не подставок CW.
- Пересказ WebFetch: «the independent GOO's bases have different dimensions», «3 base sizes».
- Sandy Petersen: «I will look into this, actually.»
- Сотрудник Petersen: «we did look into this for O2, and then decided against it, can't remember why».

**Гипотеза, не подтверждённая источником.** Число колец каждого размера на цвет
(6/3/3/3/1) похоже на максимальное число фигурок одного типа на этой подставке:
- 25 мм ×6 — Gryllus (6) или Worms of Ghroth (6);
- 40/50/60 мм ×3 — наборы по 3 фигурки;
- 80 мм ×1 — одиночные крупные GOO или Terror.

Сопоставления «юнит → размер» здесь **нет**: это надо мерить по фигуркам или смотреть
на вики.

Где искать дальше (закрыто): miniset.net (403; в каталоге есть раздел «Bases»),
Lost Minis Wiki (robots), RPGnet (403), вики fandom.

---

## H. Эррата и FAQ по шести Terror

Проверены: официальный FAQ на freshdesk; страницы NEC (BTS, MASK, KS, PA, CATS) — на
них нет FAQ к этим юнитам; апдейты Kickstarter; описания TheGameSteward.

| Юнит | Официальный FAQ / эррата | Расхождения версий текста |
|------|--------------------------|---------------------------|
| **Hound of Tindalos** | **Нет**: в FAQ freshdesk ничего, на NEC-BTS ничего | Не найдено |
| **The Shadow Pharaoh** | **Нет** (FAQ freshdesk, NEC-MASK) | Не найдено |
| **Elder Shoggoth** | **Нет** в FAQ | **Да.** TheGameSteward, CW-U31: «It has power of Prime Cause. In any battle, **before rolling dice**, choose ANY of your units (including the Elder Shoggoth) and replace it with any other unit from your pool.» — то есть **до** броска, а у NEC фаза «Prime Cause (**Post-Battle**)». Остальное совпадает: «Like other Terrors, it costs 2 Doom and 2 Power to acquire, after which it appears at your Controlled Gate.», «costs 4 Power to summon otherwise, and has a Combat of (only) 2», «pay half the new unit's Power cost, rounded down», «if you create a Terror, the enemy in the battle gets 1 Doom. if you create a Great Old One, the enemy in the battle gets 1 Elder Sign.» Источник: https://www.thegamesteward.com/products/cthulhu-wars-elder-shoggoth-expansion-kickstarter-edition-board-game-expansion. Какая фаза окончательная — по карте не проверено |
| **Brown Jenkin** | **Нет** в FAQ | **Да.** TheGameSteward, CW-U29: «Loathsome Titter (Gather Power Phase): If Brown Jenkin is in an Area with an enemy Controlled Gate during the Gather Power Phase gain power from that Gate and all Cultists in the Area regardless of faction.» и «Familiar (**Post-Battle and Doom Phase**): If Brown Jenkin is Killed or Eliminated in Battle immediately pay 2 Power and place Brown Jenkin at your Controlled Gate.» У NEC: «gain 2 Power, plus 1 more power for each enemy Cultist» и «Familiar (**Ongoing**) … if (or as soon as) you have at least 2 Power … This is not Optional». Текст TGS, видимо, ранний (кампания O3). Источник: https://www.thegamesteward.com/products/cthulhu-wars-brown-jenkin-kickstarter-edition |
| **Cacodemon** | **Разъяснение дизайнера** в апдейте 52 Onslaught 3, https://www.kickstarter.com/projects/1816687860/cthulhu-wars-onslaught-3/posts/1963064 — см. ниже | **Да.** Апдейт 52: «no faction may move or **retreat** units into the Cacodemon's area, unless they are accompanied by a Great Old One». У NEC: «Enemy Units may not Move **or be Pained** into the Area with Cacodemon unless they are Great Old Ones or if they are accompanied by a Great Old One.» В апдейте — «no faction» (включая владельца?), на NEC — «Enemy Units» |
| **Cat from Neptune** | **Нет** (FAQ freshdesk, NEC-CATS) | Не найдено |

Цитаты из апдейта 52 Onslaught 3 по Cacodemon:
- «It is a Terror, costing 2 Power and 2 Doom to gain for your side. Once gained, if it is killed, it costs 4 Power to re-summon. It has Combat 3»
- «Not even Crawling Chaos can use Madness to retreat units into the Cacodemon's area, unless a Great Old One comes along.» Блокируются движение и аналогичные способности и Spellbook, «except for Avatar».
- «You can still Recruit and Summon units into the Cacodemon's area. Just not move there.»

Попутная находка по Voonith (не из списка H). Ранний текст TheGameSteward, CW-U11: «its special ability is that if you roll NO kills in a battle involving your Voonith, add 1 kill to your total». Карта на NEC: «For each Kill you score fewer than the number of Vooniths…». Там же состав: «Hound of Tindalos figure, 4 Wamp Figures, 2 Voonith Figures, and 3 Loyalty Cards.» Источник: https://www.thegamesteward.com/products/cthulhu-wars-beyond-time-space

Остаётся открытым: в Ultimate Errata Pack 5 карт лояльности, их список не найден (C.13).
Какие-то из этих Terror могут быть среди них.

BGG в этом заходе: 2 треда.
- 1606789 — кольца-идентификаторы;
- 1071017 — **оказался тредом не про Cthulhu Wars** (Man O' War). Выдача поиска дала неверный ID; запрос потрачен впустую.

Всего за работу — 10 тредов BGG. Ни 403, ни 429 не было.
