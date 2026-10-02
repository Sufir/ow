# SRC-WEB-ELDERGODS — Elder Gods в Cthulhu Wars (веб-сбор)

> **SRC-ID:** `SRC-WEB-ELDERGODS` · **Получено:** 2026-10-01 · **Собрано для:** `FAC-013`,
> исследование `rules/tasks/ИССЛЕДОВАНИЕ-Elder-God.md`.
>
> **Что это.** Сводка, а не скачанная страница. Собрана Claude через WebFetch, API GitHub
> и API BGG (6 тредов, по одному запросу, пауза 30 с). Каждый факт — с URL.
> Тексты — по-английски, как на источнике.
>
> **Доверие.** necronomicon.app и Kickstarter читались через пересказчик WebFetch: короткие
> цитаты совпадали при повторных запросах, длинные перед переносом на компонент сверять
> на странице. HRF — низкий приоритет (решение Alek 28.09.2026). Вики fandom закрыта (402).
>
> **Поправки после сбора (сверка с локальными источниками, 01.10.2026).**
> 1. FAQ «Can Elder Gods declare Battle since they have no Combat dice? — No.» есть
>    во встроенном FAQ рулбука: `SRC-RB-NEW`, с. 182. Пункты 2.3 и 6 ниже, где сказано
>    «первоисточник не найден», этого не учитывают.
> 2. Апдейт 50 CATaclysm проверен повторным запросом: на странице автор поста — Sandy
>    Petersen; три цитаты про Elder Gods подтверждены дословно.
> 3. Апдейт 3 CATaclysm («rolled Kill total») совпадает с FAQ рулбука, с. 183:
>    «reduce the enemy-rolled Kills by 1». Расхождения с картой нет — necronomicon
>    просто сокращает.

---

Дата сбора: 2026-10-01. Цитаты — английские, как в источнике. Комментарии — по-русски.

Уровни доверия:
- **official** — текст Petersen Games (рулбук/карта/FAQ/Kickstarter-апдейт издателя)
- **designer** — Сэнди Петерсен лично
- **fan reference** — necronomicon.app (воспроизводит официальные тексты и FAQ, но это фан-ресурс)
- **community** — BGG, игроки
- **digital implementation** — HRF (haunt-roll-fail), низкий приоритет, не ruling

Оговорка о точности цитат: necronomicon.app и Kickstarter читались через WebFetch, который
пропускает страницу через модель-пересказчик. Короткие цитаты совпадали при повторных
запросах, но дословность длинных фрагментов перед использованием в нашем рулбуке стоит
сверить глазами на странице. Прямой curl к necronomicon.app, orderofgamers.com заблокирован
прокси (403).

---

## 1. Полный список Elder Gods в продуктах Cthulhu Wars

Проверены все 12 фракций и все 19 страниц «Neutral Expansions» на necronomicon.app
(Rulebook Extras, Azathoth, Beyond Time and Space, Cosmic Terrors, Dreamlands Surface/Underworld,
GOO Pack 1–4, High Priests, Masks of Nyarlathotep, Ramsey Campbell Horrors 1–2, Something About Cats,
The Dunwich Horror, Kickstarter Specials, The Gods War Crossover, Planet Apocalypse Crossover).
Метка «Elder God» встречается ровно у шести юнитов. Других Elder Gods (в т. ч. в Planet Apocalypse
Crossover — там 14 Independent GOO, ни одного Elder God) не найдено.

| # | Юнит | Тип | Продукт | Цена | Бой |
|---|------|-----|---------|------|-----|
| 1 | Bastet | фракционный Elder God (Bubastis) | Bubastis Faction CW-F8, Kickstarter CATaclysm | 6 | +1 Kill, у врага −1 Kill |
| 2 | Nodens | Independent Elder God | CW-U28; Onslaught 3, выдан всем уровням пледжа; на necronomicon — «Kickstarter Specials» | 6 | +1 Kill и +2 Pain |
| 3 | Hagarg Ryonis («Cat from Jupiter») | Independent Elder God | Something About Cats CW-U33 (CATaclysm) | 4 | +3 Pain |
| 4 | Hellmother | Independent Elder God | The Gods War Crossover (бесплатный PDF, CATaclysm Update 50) | 4 | 1 Pain за каждого своего культиста на карте; +1 Kill при ≥6 культистах |
| 5 | Sun God | Independent Elder God | там же | 4 | 1 Pain и 1 Kill |
| 6 | Thunder King | Independent Elder God | там же | 4 | 1 Pain за каждый фракционный спеллбук; +1 Kill при всех 6 |

Lady of Disease, Mad God и Magna Mater из того же кроссовера — **Independent Great Old Ones**, не Elder Gods.

### 1.1 Bastet — тексты
Источник: https://necronomicon.app/factions/bubastis (fan reference, воспроизводит официальный лист фракции)
- Определение: "Bastet is an Elder God; these beings are treated as Great Old Ones for all purposes except: they do not provide an inherent Elder Sign for a Ritual of Annihilation, though they often have other means of creating Elder Signs; and Elder Gods never roll Combat dice, but provide some fixed benefit."
- Продолжение того же блока: "They do count as equal to Great Old Ones otherwise, so they can block Unit Captures." / "Nyarlathotep gets 2 Elder Signs or half-Power cost from his Harbinger ability..." / "You can use them to Capture Cultists even if an enemy Monster is present, and so forth."
- Requires Attention (Doom Phase) по necronomicon: "During the Doom Phase, if Bastet is in an Area containing an enemy Cultist, you may perform a Ritual of Annihilation. For you, this adds exactly 4 Doom plus: If Bastet's Area has an Enemy-Controlled Gate, gain 1 Elder Sign; If Bastet's Area has an Enemy Great Old One, gain 2 Elder Sign."
- Бой (пересказ necronomicon): "Add 1 Kill to your combat total (Bastet rolls no dice); the enemy must lower their Kill total by 1."
- Бубастис не может брать High Priests (petersengames.com, блог 2026-07-31, official, к Elder Gods напрямую не относится): https://petersengames.com/blogs/news/cthulhu-wars-expansion-factions-complete-guide

Источник: Kickstarter CATaclysm, Update 3 «What's the Bubastis faction like? Not to mention the penguins?», автор Sandy Petersen (designer/official), дата на странице не видна.
https://www.kickstarter.com/projects/petersengames/cthulhu-wars-cataclysm/posts/2466093
- "She's an Elder God (like Nodens), not a Great Old One. This means she does not roll combat dice, and she does not inherently provide an Elder Sign when you Ritual."
- "Her Combat ability is still potent – she adds 1 Kill to your combat total, and additionally the enemy must lower their rolled Kill total by 1."
- "If Bastet is in an area with an enemy cultist (only), you can perform a Ritual of Annihilation. In this case, the Ritual adds exactly 4 Doom, plus if the area Bastet is in has an enemy Gate, gain 1 Elder Sign, and if the Area has an Enemy Great Old One, 2 more Elder Signs."
- **Расхождение формулировок:** в апдейте — «rolled Kill total», то есть снижаются выброшенные на кубах Kills; в пересказе necronomicon — просто «Kill total». Свериться с картой (на нашем планшете это вопрос того, режет ли Bastet фиксированные Kills вражеских Elder Gods и способностей).
- Апдейт описывает максимальный сценарий «9 Doom and 3 Elder Signs».

### 1.2 Nodens
Источник: https://necronomicon.app/neutral-expansions/kickstarter-specials (fan reference)
- Пробуждение: требование стандартное ("Your Controlled Gate is in an Area with your Great Old One"); "Pay 6 Power, place Nodens into the Area." — **без** «Gain 1 Elder Sign».
- Бой: "Add 1 Kill and 2 Pains to your Combat total (Nodens doesn't roll any Combat Dice)"
- Healing (Doom Phase): "At the end of the Doom Phase, unless the Ritual of Annihilation track has reached Sudden Death, move the Ritual marker backwards 1 step (but not past the start)."
- Proteus (Action: Cost 2): "Choose one of your earned Faction Spellbooks that names either a type of Unit (e.g., Acolytes or Flying Polyps). Place your Faction Glyph on that Spellbook. Nodens then benefits from that Spellbook's effects as if it were the named Unit or type of Unit."
- Требование спеллбука: "Perform a Ritual of Annihilation."
- FAQ: "If Nodens copies The Ancients' Extinction Spellbook, is He removed from the game upon being killed or eliminated?" — "No." (то же на https://necronomicon.app/factions/the-ancients и https://necronomicon.app/rulebook/independent-great-old-ones)
- Магазин Petersen Games (official): "Nodens has the ability to take on the same ability as one of your faction units from a Faction Spellbook – the most versatile of any Independent Great Old One!" — https://petersengames.com/the-games-shop/nodens/ (обратите внимание: магазин сам называет его «Independent Great Old One»).
- Происхождение: Kickstarter Onslaught 3, Update 44 «THE BIG ONE: NODENS + DIRE AZATHOTH!», Sandy Petersen (designer): "EVERY PLEDGE LEVEL IMMEDIATELY GETS NODENS! He is NOT a Stretch Goal..." О статусе Elder God — только лор: статус «certainly does NOT indicate friendship towards Earth life». Механики Elder God в апдейте нет. https://www.kickstarter.com/projects/1816687860/cthulhu-wars-onslaught-3/posts/1961682
- Контекст (designer, 2015-11-13/14, BGG «Ask Sandy 7», стр. 4, Sandy Petersen userid 14336): на вопрос «do you think the Elder Gods could find a place in Cthulhu Wars?» — "pshaw..."; "I don't want to do figures of humanoid Elder Gods like Nodens, when I could instead be building models of stuff like Ghroth, Vulthoom, or Brown Jenkin." Позже позиция изменилась (Nodens вышел в Onslaught 3). https://boardgamegeek.com/thread/1468640 (через api.geekdo.com, pageid=4)

### 1.3 Hagarg Ryonis
Источник: https://necronomicon.app/neutral-expansions/something-about-cats (fan reference)
- Заголовок: "Hagarg Ryonis" / "(Cat from Jupiter)", тип Independent Elder God.
- Пробуждение: стандартное требование; "Pay 4 Power, and place Hagarg Ryonis in the Area containing the Gate." — **без** «Gain 1 Elder Sign».
- Бой: "Hagarg Ryonis rolls no dice. Instead, she adds 3 Pains to your Combat total."
- Subversion (First Player Phase): "Choose a player, if that player performs a Ritual of Annihilation in this Doom Phase, you steal 1 of the Elder Signs he earns (if any)."
- Спеллбук Laziness (Action: Cost 0): "Any Faction with exactly 1 Power left loses that Power. Alternatively, pay 1 Power to force Windwalker to also lose 1 Power. You can only use this Action if Windwalker is Hibernating, or one or more enemy Factions have exactly 1 Power." Требование спеллбука на странице дано картинкой, текстом не получено.
- FAQ по ней на necronomicon нет.
- Магазин (official): "...one independent Elder God Hagarg Ryonis" — https://petersengames.com/products/something-about-cats

### 1.4 Hellmother, Sun God, Thunder King (кроссовер The Gods War)
Источник: https://necronomicon.app/neutral-expansions/the-gods-war-crossover (fan reference)
- У всех трёх: "Your Controlled Gate is in an Area with your Great Old One" и "Pay 4 Power, and place <X> in the Area containing the Gate. **Gain 1 Elder Sign.**" — единственные Elder Gods, дающие Знак при пробуждении.
- Hellmother: бой "Inflict 1 Pain per Cultist you have on the Map. Also inflict 1 Kill if you have at least 6 Cultists."; Hellborn (Ongoing): "your monsters can be Recruited instead of Summoned. I.e., you can place them in any Area in which you have a Unit."; требование спеллбука "One of your units is Killed"; Nocturnal Raids (Doom Phase): "Place a free cultist in Hellmother's Area."
- Sun God: бой "Inflict 1 Pain and 1 Kill."; Sunrise (Ongoing): "The Sun God cannot be killed or eliminated. When he is chosen to receive such a result, instead the enemy player gets to pick up and place Sun God in any Area, and Sun God's owner loses 1 Power or 1 Doom (your choice)."; Sunspear (Action: Cost 2): "Choose an enemy unit and roll 1d6. If you roll at least twice as high as that unit's Cost, eliminate it, and move the Sun God to that Area." Ещё строка "spend 1 Power. Choose an enemy faction to gain 1 Elder Sign" — пересказчик подал её как действие; вероятнее, это требование спеллбука. **Не проверено.**
- Thunder King: бой "Inflict 1 Pain per faction spellbook. Also inflict 1 Kill if you have all 6 faction spellbooks."; Inferiority Complex (Doom Phase): "You may choose to spend 2 Doom to gain 5 Power."; требование спеллбука "Kill or eliminate an enemy Cultist"; Kinship (Doom Phase): "Choose an enemy faction. You then choose to receive either 1 Doom or 2 Power. Your chosen enemy gains the other possible reward."
- Наблюдение: Sun God и Thunder King **сами бросают d6** (Sunspear) или работают от счётчика — запрет «never roll Combat dice» касается только боевых кубов.

---

## 2. Тексты и решения, уточняющие Elder God vs GOO (сверх известного абзаца)

### 2.1 Общее правило Independent Elder Gods — official через fan reference
https://necronomicon.app/rulebook/expansion-products, раздел «Independent Elder Gods»:
- "Elder Gods are similar to Great Old Ones, except they do not provide Elder Signs during a Ritual of Annihilation, and do not roll combat dice."
- "When you perform a Ritual of Annihilation, do NOT gain an Elder Sign for any Independent Elder Gods you Control." (параллельно для IGOO: "do NOT gain an Elder Sign for any Independent Great Old Ones you Control")
- "There are no limits to how many Independents you may Control, and you may use one Independent to help you Awaken another." Отсюда: Independent Elder God может служить «your Great Old One» для требования пробуждения другого Independent. Это прямое правило для Independents, Elder Gods не исключены.
- Та же формула "Elder Gods are similar to Great Old Ones..." напечатана на страницах Nodens, Hagarg Ryonis и кроссовера.

### 2.2 Издатель: Elder God = IGOO «во всём остальном», и альтернативное правило про Знаки — official
Kickstarter CATaclysm, Update 50 «The Gods War Crossover - New Cthulhu Wars Independent Great Old Ones (and Elder Gods) Download», подпись «Arthur» (Arthur Petersen, Petersen Games); дата на странице не видна.
https://www.kickstarter.com/projects/petersengames/cthulhu-wars-cataclysm/posts/2746180
- "Some are labeled 'Independent Elder God' on the backside, instead of Independent Great Old One, but there's no real difference. It is clarified that Elder Gods do not provide Elder Signs, but the basic rule is that Independent Great Old Ones do not do so anyway - but in a game in which you use the official alternate rule that Indie GOOs do provide Elder Signs, then the Elder Gods still don't. In virtually every other way, an Elder God is the same - for all rules purposes."
- Новое:
  - (а) существует **официальное альтернативное правило**, по которому IGOO дают Знак при Ритуале. Elder Gods не дают его даже тогда.
  - (б) по базовому правилу для Independent разница Elder God/IGOO в Ритуале **нулевая**: не дают оба.
  - (в) Отказ от боевых кубов здесь не назван как отдельное правило: каждый Elder God пишет фиксированный результат на своей карте.
- Текст самого альтернативного правила не найден (на странице expansion-products necronomicon его нет).

### 2.3 Объявление битвы — official
- Базовое правило (https://necronomicon.app/rulebook/battle): "The Faction initiating the Battle must have at least 1 Combat among its Units in the Area."
- Официальный FAQ Petersen Games (freshdesk, обновлён 2019-09-25), Miri Nigri: "If I have a Controlled Gate and only Units with 0 Combat, can I declare Battle due to Miri Nigri?" — "Yes! Although Miri Nigri does not technically add 3 Combat to a particular Unit (as with Absorb), the fact that you will roll Combat dice means that you can initiate Battle even if all you have is a single Cultist (on that Gate) in the Area." https://petersengames.freshdesk.com/support/solutions/articles/48000952254-cthulhu-wars-rules-faq
- Отсюда принцип: право объявить битву даёт наличие боевых кубов. Elder God в одиночку кубов не даёт. Известный FAQ «Elder Gods cannot declare Battle» в текстах necronomicon **не найден**: слова «declare» на странице Bubastis нет. Подтвердить первоисточник не удалось.

### 2.4 Bastet и Ритуал: Yog-Sothoth, лимит Знаков — official FAQ через fan reference
https://necronomicon.app/factions/bubastis и https://necronomicon.app/factions/opener-of-the-way
- "If Bastet is in an area with Yog-Sothoth, and you ritual, do you get 3 Elder Signs?" — "Yes. But the presence of another Enemy Controlled Gate does not increase this reward."
  → Yog-Sothoth считается одновременно «Enemy Great Old One» (+2) и «Enemy-Controlled Gate» (+1). Вторые врата в той же области бонус не увеличивают: максимум 1 + 2.
- "Do I get an Elder Sign for Ritualing with Bastet if I'm not using her Requires Attention ability?" — "No. Elder Gods do not provide Elder Signs for Rituals of Annihilation, except in conjunction with special abilities."
- "If Bastet is in a Battle by herself, does she still get to inflict her one Kill, even though no Combat dice are rolled for her side?" — "Yes, of course. Elder Gods just inflict results. They don't roll dice, and they don't require dice to be rolled for their results to take place."
- "Can Earth Cats be given up to Blood Offering in exchange for Elder Signs?" — "No. Although they aren't technically 'being Captured,' the Action still results in them being Captured." (к Elder God не относится, но к Знакам Bubastis — да.)

### 2.5 Cthugha — official FAQ через fan reference
https://necronomicon.app/neutral-expansions/great-old-one-pack-1
- "Does Cthugha copy the combat of Elder Gods?" — "Cthugha rolls no dice when facing an Elder God, and gets no further benefit vs. Elder Gods." (подтверждает известное)
- Тексты Cthugha, важные для Elder Gods, в FAQ не разобраны: пробуждение "Pay Power equal to 6 minus your Great Old One's Awakening Power Cost"; требование спеллбука "Kill an enemy Great Old One in Battle".

### 2.6 Mind Control (Elder Thing) — official FAQ, к Elder Gods применимо только выводом
https://necronomicon.app/rulebook/neutral-monsters
- "This ability also works on Independent Great Old Ones (but only their special abilities, and not their Spellbooks)."
- Elder Gods прямо не названы. По правилу «treated as GOO for all purposes except...» и по Update 50 («the same - for all rules purposes») — должно действовать и на них. **Это вывод, не ruling.**

### 2.7 Тексты «анти-GOO» и «enemy GOO», по которым ruling для Elder Gods НЕ найдено
Тексты взяты с necronomicon (fan reference), FAQ про Elder Gods к ним нет:
- Unholy Ground (Ancients): "If there is a Cathedral in the Battle Area, you may choose to remove a Cathedral from anywhere. If you do, an enemy Great Old One in the Battle must be Eliminated by its owner."
- Harbinger (Crawling Chaos): "If Nyarlathotep is in a Battle in which one or more enemy Great Old Ones are Pained or Killed, you receive Power equal to half the cost to Awaken those Great Old Ones." Для Elder Gods прямо разрешено в абзаце Bubastis.
- Yog-Sothoth Combat: "Equal to twice the number of enemy-Controlled Faction Great Old Ones in play." Открытый вопрос: Bastet — фракционный юнит, считается ли она «Faction Great Old One»? Independents (Nodens и др.) под «Faction» не подпадают в любом случае.
- The Beyond One: "...in an Area that contains a Gate and no enemy Great Old Ones." — Bastet/Elder God блокирует? ruling нет.
- Hibernate: "Add +1 Power to your total for each enemy Great Old One in play..." — ruling нет.
- Berserkergang: "For each Gnoph Keh assigned a Kill in Battle, the enemy must Eliminate 1 Monster or Cultist." К GOO не относится вообще, вопрос снимается.
- Avatar (Black Goat) — FAQ про Elder Gods нет.
- Ancients FAQ (official через fan reference): "How do the Ancients generally interact with requirements or rules necessitating all Factions to have a Great Old One?" — "The Ancients are ignored for this purpose. For example, the Ancients need not have a Great Old One..." Про Bubastis/Bastet в этом контексте ничего нет.

### 2.8 Пробуждение и Знак
- Nodens, Hagarg Ryonis: пробуждение без Знака (см. выше).
- Hellmother, Sun God, Thunder King: "Gain 1 Elder Sign" при пробуждении (на карте).
- Общего правила «Знак за пробуждение Independent» на странице expansion-products нет.

---

## 3. HRF (github.com/haunt-roll-fail/cthulhu-wars) — digital implementation

Склонирован main @ 56fb862 (2026-03-14, «unholy no goo / curse on gate / lone brainless dematerialization / beyond one threat»), плюс все открытые PR-рефы #2–#11 (последний #10 от 2026-04-03).
- `grep -i "bastet|bubastis|elder ?god|eldergod|nodens|hagarg|hellmother|sun god|thunder king"` по всем .scala в main и во всех PR — **0 совпадений**.
- Фракции в коде: GC, CC, BG, YS, SL, WW, OW, AN (8). Bubastis нет.
- Independent GOO: Byatis, Abhoth, Daoloth, Nyogtha (`solo/IGOOs.scala`). Нейтральные монстры: Ghast, Gug, Shantak, Star Vampire.
- Модель: `sealed trait UnitType` с `Cultist | Monster | Terror | GOO | Token | Building` (`solo/Game.scala:131–141`). Independent GOO — тот же `UnitType GOO` плюс маркерный `trait IGOO` (`Game.scala:143`; `case object Byatis extends UnitClass("Byatis", GOO, 4) with IGOO`). Помощники `factionGOO` / `independentGOO` (`solo/implicits.scala:46–47, 83–84`).
- Ритуал: `val es = f.goos.factionGOOs.num + ...Consecration...` (`Game.scala:1815`) — Знаки только за фракционных GOO; IGOO исключены флагом.
- Боевая сила Yog-Sothoth: `2 * factions.but(f)./(_.factionGOOs.num).sum` (`FactionOW.scala:58`).
- Вывод: **Elder Gods в HRF не реализованы**, отдельного класса или флага нет. Готовый шаблон кода — «GOO + маркерный trait», так сделаны IGOO.

---

## 4. Вариант/ребаланс Bubastis от сообщества

BGG thread 2951519 «A rigorously play-tested Bubastis variant brought to you by the CW Discord», автор Matthew (userid 2041305), 2022-10-13T18:48:35Z, 17 постов (community).
https://boardgamegeek.com/thread/2951519 (через api.geekdo.com)
- Изменения: Catabolism → **Carnivore**, Ailurophobia → **Syzygy**, эррата Луны: "we errata the Moon so that no tokens, buildings and other markers can be placed on it."
- Тексты Carnivore и Syzygy в посте **только картинками** (image 7123210, 7123211), текстом не получены.
- **Bastet в варианте не меняется**: в треде нет упоминаний Bastet, Elder God, Requires Attention, Elder Signs.
- Мотивация (цитаты): "the Bubastis player's optimal play is to pick on the player that is already losing, since vanilla Bubastis has the fastest Doom tempo in the game by quite a bit"; "Catabolism basically sidesteps how cool the Moon is as a concept"; "Catabolism is also incredibly accelerating Bubastis tempo to 30 Doom..."; без Catabolism "if the Moon ever got Ice-Aged then they would be in an auto-lose situation."
- Одобрения Petersen Games нет: "I hope somehow Sandy will see this post.." (user 1559785, 2022-10-15).
- Официальной эрраты к Bastet не найдено.

---

## 5. Прочее сообщество (BGG, community)
- Thread 3346971 «Awakening Cthuga…» (2024-08-08): OP спрашивает, можно ли пробудить Cthugha за Bubastis ("Bastet is an Elder God, not a GOO."). Ответ Michael_K13 (userid 3374971): "Don't forget, Cthugha replaces your GOO (and Bubastis's Elder God if you are playing them) when awakened." Это мнение игрока, не ruling.
- Thread 3097038 «Bubastis & Ritual of Annihalation» (2023-06-08 / 2023-08-26): интерпретация игрока: Requires Attention — "this IS their Ritual, not an extra one"; "They can't control gates...and they have no faction Great Old Ones". Не ruling.
- Thread 3142781 «Bubastis Rules Clarifications» (2023-08-26 / 2024-05-07): Earth Cats, Dark Demon, Moon vs Library. Elder God не обсуждается; официальных ответов нет.
- Thread 1802504 «The Gods War Crossover Rules...» (2017–2019): Elder God не обсуждается, Сэнди не пишет.
- Не прочитан (лимит BGG исчерпан): 3117761 «Summoning Hagarg Ryonis with the Ancients?».

Использовано 6 запросов к api.geekdo.com (2951519, 3142781, 3097038, 3346971, 1468640 p.4, 1802504), между запросами пауза ≥30 с.

---

## 6. Не удалось / пробелы
- cthulhuwars.fandom.com — HTTP 402, одна попытка, дальше не шли.
- Первоисточник FAQ «Elder Gods cannot declare Battle» не найден (есть только базовое правило и FAQ Miri Nigri, из которых это следует).
- Нет ruling по Unholy Ground, Beyond One, Hibernate, Avatar, Yog-Sothoth combat (Bastet как «Faction GOO»?), требованию спеллбука Cthugha «Kill an enemy Great Old One», бонусам «+кубы к GOO» и Proteus, если скопированный спеллбук даёт кубы.
- Текст «official alternate rule that Indie GOOs do provide Elder Signs» не найден.
- Даты Kickstarter-апдейтов (CATaclysm 3 и 50, Onslaught 3 №44) на страницах не видны.
- Тексты Carnivore/Syzygy (картинки на BGG) не получены.
- Проверить дословно: Bastet «rolled Kill total» (апдейт) против «Kill total» (necronomicon).
