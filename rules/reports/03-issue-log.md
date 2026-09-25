# Полный issue log

| ID | Тип | Область | Батч | Суть | Severity | Статус | Решение |
|---|---|---|---|---|---|---|---|
| DEV-001 | DEVIATION | MODULE | B8 | Наёмный боевой робот: «уничтожен» вместо «погиб» расширяет условие | ERROR | DECIDED | D-020 |
| DEV-002 | DEVIATION | ROUND | B1 | Порядок фаз и стартовый запас сдвинуты — но результат эквивалентен | INFO | CLOSED | D-035 |
| DEV-003 | DEVIATION | DOOM | B7 | Особые события фазы влияния перенесены на конец фазы | ERROR | DECIDED | D-020 |
| DEV-004 | DEVIATION | ROUND | B1 | Первый игрок в начале партии: «всегда» заменено на «рекомендуется» | ERROR | DECIDED | D-020 |
| MISS-001 | MISSING | UNIT | B5 | Полностью отсутствует способность полковника «жертва ради нефти» | CRITICAL | CLOSED | D-021 |
| MISS-002 | MISSING | ACTION | B2 | У задач, требующих действия, потеряны стоимость по умолчанию и лимит | ERROR | DECIDED | D-022 |
| DEV-007 | DEVIATION | MODULE | B8 | Игра на двоих: реализован другой режим вместо оригинального | CRITICAL | CLOSED | D-021 |
| TISS-002 | TERMINOLOGY | MAP | B1 | «Запас» означает и резерв фигурок, и запас нефти | WARNING | DECIDED | D-024 |
| DEV-008 | DEVIATION | SETUP | B1 | Раскладка поля: остаток игры на двоих и несверенные раскладки 6–8 | WARNING | DECIDED | D-024 |
| DEV-009 | DEVIATION | ACTION | B2 | Вербовка: лишний тайминг в исключении и «за ход» вместо «за действие» | ERROR | DECIDED | D-025 |
| MISS-003 | MISSING | ACTION | B2 | Потеряно: выставление боевой машины способностью — не производство | ERROR | DECIDED | D-022 |
| MISS-004 | MISSING | ACTION | B2 | Создание боевого робота: потеряны лимит и правило доступности способности | ERROR | DECIDED | D-022 |
| MISS-005 | MISSING | ACTION | B3 | Битва: потеряны «противник с боевой силой 0» и обязательность участия | ERROR | DECIDED | D-022 |
| MISS-006 | MISSING | ACTION | B3 | Захват: потеряны лимит за действие и запрет защищать чужого пехотинца | ERROR | DECIDED | D-022 |
| MISS-007 | MISSING | ACTION | B2 | Уникальные действия: потеряно требование выполнимости целиком | WARNING | DECIDED | D-022 |
| MISS-008 | MISSING | ACTION | B2 | Свободное действие с фабрикой: потеряны два ограничения | ERROR | DECIDED | D-022 |
| RULE-003 | AMBIGUITY | ACTION | B2 | «Прерывающие» способности: не указано, что порядок начинается с активного игрока | WARNING | DECIDED | D-025 |
| DEV-011 | DEVIATION | TECH | B5 | Постоянные эффекты объявлены неотключаемыми — обратно оригиналу | CRITICAL | DECIDED | D-022 |
| DEV-012 | DEVIATION | VICTORY | B7 | Победа в фазу действий наступает немедленно вместо конца хода | ERROR | DECIDED | D-027 |
| DEV-010 | DEVIATION | COMBAT | B3 | Битва: три фазы вместо четырёх, назначение и применение слиты | ERROR | DECIDED | D-026 |
| MISS-009 | MISSING | COMBAT | B3 | Потеряно: удаление отряда в тактической фазе и досрочный конец битвы | ERROR | DECIDED | D-022 |
| MISS-010 | MISSING | COMBAT | B3 | Потеряно: лишние результаты игнорируются и третий тип результата | ERROR | DECIDED | D-022 |
| MISS-011 | MISSING | COMBAT | B3 | Потеряно: эффекты финальной фазы работают, даже если отряд удалён | ERROR | DECIDED | D-022 |
| MISS-012 | MISSING | TECH | B5 | Потеряно: несколько технологий разом и технология, заработанная в бою | ERROR | DECIDED | D-022 |
| EXTRA-001 | DEVIATION | COMBAT | B3 | Фракция вне битвы пущена в тактическую фазу и объявлена первой | ERROR | DECIDED | D-026 |
| DEV-013 | DEVIATION | UNIT | B5 | Полковник даёт «1 дополнительную нефть» — возможно, вдвое больше нужного | ERROR | DECIDED | D-022 |
| DEV-014 | DEVIATION | MODULE | B8 | Наёмники: стоимость карт лояльности разная вместо единой | ERROR | CLOSED | D-051 |
| DEV-015 | DEVIATION | UNIT | B8 | Контроль над Роем привязан к фазе влияния и противоречит сам себе | ERROR | DECIDED | D-022 |
| MISS-013 | MISSING | UNIT | B5 | Энграммы: не названо количество и потеряно правило назначения результатов | WARNING | DECIDED | D-022 |
| MISS-014 | MISSING | UNIT | B8 | У Роя не названа боевая сила | WARNING | CLOSED | D-051 |
| RULE-004 | AMBIGUITY | MODULE | B8 | «Бросьте тяните карту события» — недоредактированная фраза | INFO | DECIDED | D-021 |
| RULE-005 | AMBIGUITY | MODULE | B8 | Лаборатория: два пункта подряд «в партии на 4 игрока» | INFO | DECIDED | D-021 |
| DEV-016 | DEVIATION | COMBAT | B3 | FAQ черновика прямо противоречит оригиналу: битва без отрядов | CRITICAL | DECIDED | D-022 |
| MISS-015 | MISSING | UNIT | B5 | Определение отряда в глоссарии не включает мехов | ERROR | DECIDED | D-022 |
| RULE-006 | AMBIGUITY | MODULE | B8 | «Баланс сил» не сверен с оригиналом | WARNING | CLOSED | D-023 |
| MISS-016 | MISSING | GLOSSARY | B9 | Глоссарий: устаревшее определение пехотинца и половина терминов отсутствует | ERROR | DECIDED | D-022 |
| DEV-017 | DEVIATION | UNIT | B8 | Неконтролируемому Рою нельзя объявить бой — в оригинале можно | ERROR | DECIDED | D-022 |
| DEV-018 | NUMBER | MODULE | B8 | Уникальные полковники: три разных числа — 8, 10 и 11 | WARNING | CLOSED | D-028 |
| SRC-002 | SOURCE-CONFLICT | MODULE | B8 | Приложение «Уникальные полковники» описывает устаревший набор | WARNING | DECIDED | D-028 |
| MISS-017 | MISSING | UNIT | B5 | Потерян предел в 4 энграммы и правило захвата сверх предела | ERROR | DECIDED | D-022 |
| DEV-005 | NUMBER | POWER | B4 | Трек запаса размечен до 25 вместо 20 | INFO | CLOSED | D-020 |
| DEV-006 | NUMBER | ACTION | B2 | Стоимость производства боевой машины зафиксирована как 1–3 | WARNING | CLOSED | D-022 |
| DEV-020 | DEVIATION | ACTION | B2 | Контроль после постройки фабрики: черновик делает его обязательным | WARNING | DECIDED | D-022 |
| DEV-021 | DEVIATION | ACTION | B2 | Мех: в оригинале отдельное действие призыва, у нас имени действия нет | WARNING | APPLIED | D-032 |
| SRC-001 | SOURCE-CONFLICT | COMBAT | — | Невидимость: «for this purpose» против «for any purpose» | WARNING | APPLIED | D-015 |
| TISS-001 | TERMINOLOGY | COMBAT | — | Разведение трёх терминов: результат боя, удаление и подавление | CRITICAL | DECIDED | D-019 |
| RULE-001 | AMBIGUITY | MODULE | — | Colour Gates, столбец «Плодородие»: «this turn» против «this Doom Phase» | WARNING | CLOSED | D-014 |
| RULE-002 | AMBIGUITY | VICTORY | — | Rule Omega ссылается на FAQ издателя — в нашем рулбуке так нельзя | INFO | DECIDED | D-013 |
| TISS-003 | TERMINOLOGY | ACTION | — | Одно действие под двумя именами: «Неограниченная Битва» и свободные действия | INFO | DECIDED | D-029 |
| TISS-004 | TERMINOLOGY | RITUAL | — | Деление трека Судного дня названо двумя именами | INFO | DECIDED | D-029 |
| TISS-005 | TERMINOLOGY | MAP | — | «Запас» означает и место хранения фигурок, и ресурс | INFO | DECIDED | D-024 |
| TISS-006 | TERMINOLOGY | UNIT | — | У обращения энграммы нет названия, а глагол «заменить» занят ещё трижды | INFO | DECIDED | D-029 |
| TISS-007 | TERMINOLOGY | SETUP | — | «Стартовая зона» против «стартового региона», при том что «зона» занята | INFO | DECIDED | — |
| TISS-008 | TERMINOLOGY | SETUP | — | «Герб или логотип фракции» — два синонима в одном предложении | INFO | DECIDED | — |
| TISS-009 | TERMINOLOGY | POWER | — | «Стоимость: 0 Силы» — ресурс назван словом, занятым под боевую силу | INFO | DECIDED | — |
| TISS-010 | TERMINOLOGY | GLOSSARY | — | Сводный список сплошных замен по замороженной карте терминов | INFO | DECIDED | — |
| ICON-101 | ICON | GLOSSARY | — | Иконочного набора у проекта нет — весь текст правил пишется плейсхолдерами | WARNING | DECIDED | D-029 |
| DEV-022 | DEVIATION | COMBAT | B3 | Отряд, выбитый в тактической подготовке, сохранял финальные эффекты | CRITICAL | DECIDED | D-022 |
| MISS-019 | MISSING | COMBAT | B3 | Потеряно: эффект, написанный через смерть, от уничтожения не срабатывает | ERROR | DECIDED | D-022 |
| MISS-020 | MISSING | COMBAT | B3 | Потеряно: способность, ведущая чужое отступление, не связана порядком сторон | WARNING | APPLIED | D-022 |
| RULE-008 | AMBIGUITY | COMBAT | B3 | Судьба фабрики, чей пехотинец убит или отступил, нигде не названа | WARNING | DECIDED | D-026 |
| DEV-023 | DEVIATION | UNIT | B5 | Первая редакция 11.2 напечатала цену вербовки полковника, а вопрос открыт | CRITICAL | DECIDED | D-022 |
| MISS-021 | MISSING | UNIT | B5 | Энграммы: потеряна разрешающая половина правила и замена на фабрике | ERROR | DECIDED | D-022 |
| MISS-022 | MISSING | UNIT | B8 | Рой: потеряно условие развёртывания и отступление ничейного Роя | ERROR | DECIDED | D-022 |
| DEV-024 | DEVIATION | UNIT | B5 | Уникальный полковник: в оговорке названа не та причина отсутствия в игре | ERROR | DECIDED | D-022 |
| RULE-009 | AMBIGUITY | MODULE | B8 | Действия вариантов не отнесены ни к одной из четырёх категорий действий | WARNING | DECIDED | D-026 |
| RULE-010 | AMBIGUITY | MODULE | B8 | «Белая фабрика» на компоненте не опознаётся — правило неприменимо за столом | WARNING | CLOSED | D-039 |
| TISS-011 | TERMINOLOGY | GLOSSARY | — | Четыре статьи глоссария названы иначе, чем их запись в замороженной карте | INFO | CLOSED | D-034 |
| RULE-011 | AMBIGUITY | VICTORY | B7 | Момент окончания не задан для фазы ресурсов и фазы первого игрока | WARNING | DECIDED | D-026 |
| DEV-019 | DEVIATION | POWER | B1 | Нефть за пехотинцев начисляется «на поле» вместо «в игре» | WARNING | DECIDED | D-022 |
| RULE-007 | AMBIGUITY | ROUND | B1 | Первый игрок в первом раунде: перестановка фаз создала пробел | WARNING | CLOSED | D-035 |
| MISS-018 | MISSING | SETUP | B1 | Очерёдность фракций напечатана на планшетах, но в правилах не описана | ERROR | DECIDED | D-031 |
| SRC-003 | SOURCE-CONFLICT | SETUP | B1 | «Очередь» Сайнтифик Солюшн: 10 в напечатанном PDF, 8 в JSON — и 8 занят | WARNING | CLOSED | D-048 |
| SRC-004 | SOURCE-CONFLICT | SETUP | B1 | Планшеты печатают «Запас нефти: 8», правила начинают партию с нуля | CRITICAL | CLOSED | D-035 |
| EXTRA-002 | DEVIATION | UNIT | P9-F | Наёмный боевой робот ставился в любой регион со своей фабрикой | ERROR | APPLIED | D-038 |
| EXTRA-003 | DEVIATION | MODULE | P9-F | Рекомендация оригинала про число наёмных роботов стояла императивом | WARNING | APPLIED | D-038 |
| EXTRA-004 | MISSING | COMBAT | P9-F | За ничейный Рой атакующий выбирает регион не только при подавлении | WARNING | APPLIED | D-038 |
| EXTRA-005 | EXTRA | VICTORY | P9-F | Окончание игры в фазе ресурсов и в фазе первого игрока — наше достроение | INFO | APPLIED | D-038 |
| MISS-023 | OUT-OF-SCOPE | MAP | P9-E | Игровое поле: число частей и стороны подтвердить после реализации компонента | INFO | DECIDED | D-047 |
| MISS-024 | OUT-OF-SCOPE | COMBAT | P9-E | Лист наклеек на кубики не собран; арт символов есть, имя файла от старой терминологии | WARNING | DECIDED | D-040 |
| PLAY-001 | PLAYTHROUGH | MAP | P10 | Состав регионов на стороне «3» не сходится с собственными утверждениями книги | WARNING | CLOSED | D-041 |
| PLAY-002 | PLAYTHROUGH | MAP | P10 | Символы на игровом поле нигде не описаны, а три задачи фракции на них опираются | ERROR | WONTFIX | D-041 |
| PLAY-003 | PLAYTHROUGH | COMBAT | P10 | Можно ли назначить одному отряду несколько результатов и что с подавлением на убитом | ERROR | APPLIED | D-041 |
| PLAY-004 | PLAYTHROUGH | COMBAT | P10 | Состояния «отряд выведен из битвы, оставшись в регионе» в правилах нет | ERROR | APPLIED | D-041 |
| PLAY-005 | PLAYTHROUGH | COMBAT | P10 | Формула боевой силы разрешена только боевым роботам, а на планшете она у боевых машин | ERROR | APPLIED | D-042 |
| PLAY-006 | PLAYTHROUGH | ACTION | P10 | Бросок кубика вне битвы не описан, а символьные наклейки делают его невозможным | ERROR | APPLIED | D-041 |
| PLAY-007 | PLAYTHROUGH | POWER | P10 | Не сказано, что запас нефти — открытая информация, хотя два правила требуют его сравнивать | WARNING | APPLIED | D-042 |
| PLAY-008 | PLAYTHROUGH | POWER | P10 | Порядок собственных эффектов внутри фазы получения ресурсов не задан | WARNING | APPLIED | D-042 |
| PLAY-009 | PLAYTHROUGH | ACTION | P10 | «Такое действие выполняется только один раз за партию» читается двумя способами | WARNING | APPLIED | D-042 |
| PLAY-010 | PLAYTHROUGH | ACTION | P10 | Не сказано, когда проверяется окончание фазы действий и что если нефть вернулась | WARNING | APPLIED | D-042 |
| PLAY-011 | PLAYTHROUGH | VICTORY | P10 | Влияние выше 30 некуда отмечать и двух лидеров нечем сравнить | ERROR | APPLIED | D-041 |
| PLAY-012 | PLAYTHROUGH | MODULE | P10 | В вариантах игры не назван тот, кто выбирает регион, число жетонов и тянет карту события | WARNING | APPLIED | D-042 |
| PLAY-013 | PLAYTHROUGH | MODULE | P10 | Списки регионов Лаборатории по книге не проверяются | WARNING | DECIDED | D-041 |
| PLAY-014 | PLAYTHROUGH | GATE | P10 | Уход пехотинца с фабрики вне битвы разобран только через свободное действие | WARNING | APPLIED | D-042 |
| PLAY-015 | PLAYTHROUGH | SETUP | P10 | Совет на первую партию называет четыре фракции при целевом составе 3–5 | INFO | APPLIED | D-042 |
| PLAY-016 | PLAYTHROUGH | DOOM | P10 | Шаг 2 оказания давления повисает, когда маркер уже в Ядерной катастрофе | INFO | APPLIED | D-042 |
| PLAY-017 | PLAYTHROUGH | ACTION | P10 | Оговорка «выставление способностью — не это действие» есть только у производства | WARNING | APPLIED | D-042 |
| PLAY-018 | PLAYTHROUGH | MOVE | P10 | Способность, меняющая дальность перемещения, и цена «1 нефть за отряд» | WARNING | APPLIED | D-042 |
| PLAY-019 | PLAYTHROUGH | ACTION | P10 | Второе действие от способности и действия вариантов игры не сведены | WARNING | APPLIED | D-042 |
| PLAY-020 | PLAYTHROUGH | TECH | P10 | Понятия «бонус на карте задачи» в правилах нет | INFO | APPLIED | D-042 |
| PLAY-021 | PLAYTHROUGH | SETUP | P10 | «Шесть пехотинцев» в стартовой расстановке против шести рекрутов и седьмого полковника | INFO | APPLIED | D-042 |
| PLAY-022 | PLAYTHROUGH | ACTION | P10 | Не сказано, в какой момент хода объявляется пас | INFO | APPLIED | D-042 |
| PLAY-023 | OUT-OF-SCOPE | FACTION | P10 | Замеченное на компонентах трёх сыгранных фракций | WARNING | DECIDED | D-042 |
| MISS-025 | OUT-OF-SCOPE | UNIT | P10 | «Стелс»: карта и приложение по фракциям формулируют технологию по-разному | WARNING | DECIDED | D-051 |
| PLAY-024 | PLAYTHROUGH | SETUP | P10B | Стартовый регион определён через логотип на поле, которого на поле нет | ERROR | APPLIED | D-042 |
| PLAY-025 | PLAYTHROUGH | SETUP | P10B | Символы Q/W/E — решение по PLAY-002 принято на посылке, которая не выполняется | ERROR | APPLIED | D-043 |
| PLAY-026 | PLAYTHROUGH | SETUP | P10B | «Любой свободный» и «кроме стартовых регионов других фракций» книга не читает | ERROR | APPLIED | D-042 |
| PLAY-027 | PLAYTHROUGH | SETUP | P10B | Планшет называет стартовый регион, которого в собранной раскладке нет | WARNING | APPLIED | D-042 |
| PLAY-028 | PLAYTHROUGH | DOOM | P10B | Не сказано, что перечёркнутые деления трека Судного дня пропускаются | INFO | APPLIED | D-042 |
| PLAY-029 | PLAYTHROUGH | SETUP | P10B | §2.1 не говорит, какая половина поля кладётся какой стороной на четверых | ERROR | APPLIED | D-047 |
| PLAY-030 | PLAYTHROUGH | TECH | P10B | §3.9 объявляет пять категорий способностей, а на компонентах их больше | WARNING | DECIDED | D-042 |
| PLAY-031 | PLAYTHROUGH | COMBAT | P10B | Сторона с боевой силой 0 не бросает, а §8.4 ждёт броска обеих сторон | INFO | APPLIED | D-042 |
| PLAY-032 | PLAYTHROUGH | GATE | P10B | «Одна фабрика в регионе за всю партию» против подвижных фабрик | WARNING | APPLIED | D-042 |
| PLAY-033 | PLAYTHROUGH | GATE | P10B | Фабрика, которую нельзя взять под контроль, не попадает ни в одно состояние §3.6 | ERROR | APPLIED | D-042 |
| PLAY-034 | PLAYTHROUGH | COMBAT | P10B | Правило нулевой суммы §8.1 отключает битвы у целой фракции | ERROR | APPLIED | D-042 |
| PLAY-035 | OUT-OF-SCOPE | FACTION | P10B | Замеченное на компонентах четырёх сыгранных фракций | WARNING | DECIDED | D-042 |
| PLAY-036 | PLAYTHROUGH | TECH | P10B | Книга не говорит, что компонент может переопределять её правила | WARNING | APPLIED | D-042 |
| PLAY-037 | PLAYTHROUGH | COMBAT | P10B | Отряд, ушедший из региона битвы до бросков, не описан ни одним из двух способов §8.3 | ERROR | APPLIED | D-042 |
| RED-001 | PLAYTHROUGH | COMBAT | P11 | §8.4 умножает формульную боевую силу на число отрядов: 4 «Саранчи» дают 12 кубиков вместо трёх | CRITICAL | APPLIED | D-045 |
| RED-002 | PLAYTHROUGH | ACTION | P11 | §7.9 разрешает повторить то же действие — «Вторжение» даёт неограниченное число действий за ход | CRITICAL | APPLIED | D-045 |
| RED-003 | PLAYTHROUGH | ACTION | P11 | «Оперативная пауза» замораживает фазу действий навсегда: правило FAQ оригинала не перенесено | ERROR | APPLIED | D-045 |
| RED-004 | PLAYTHROUGH | COMBAT | P11 | «Специальная операция» даёт бесконечную цепочку битв: три ограничения FAQ оригинала не перенесены | ERROR | APPLIED | D-045 |
| RED-005 | PLAYTHROUGH | TECH | P11 | §3.9 защищает не те правила, которые D-042 считал безусловными: §3.4 и §8.7 маркеров не несут | ERROR | APPLIED | D-045 |
| RED-006 | PLAYTHROUGH | FACTION | P11 | Луны нет в правилах: Moon Systems не контролирует ни одной фабрики и не получает влияния за фабрики | ERROR | CLOSED | D-049 |
| RED-007 | PLAYTHROUGH | GATE | P11 | Фабрика на планшете: §3.4 определяет «на поле» и «в игре» только для отрядов | ERROR | APPLIED | D-045 |
| RED-008 | PLAYTHROUGH | MODULE | P11 | Фабрика Узла управления, убранная на планшет, делает контроль над Роем неотбираемым | ERROR | APPLIED | D-045 |
| RED-009 | PLAYTHROUGH | DOOM | P11 | «Взлом систем» читается как второе оказание давления за фазу и перебивает §6.3 через §3.9 | WARNING | CLOSED | D-045 |
| RED-010 | PLAYTHROUGH | TECH | P11 | «Шантаж»: противникам всегда выгодно не договариваться, и переговорная механика вырождается | WARNING | APPLIED | D-045 |
| RED-011 | PLAYTHROUGH | TECH | P11 | «Ручная сборка»: стоимость производства боевой машины не задана — 1 нефть или цена с планшета | WARNING | APPLIED | D-045 |
| RED-012 | PLAYTHROUGH | ACTION | P11 | §7.5 не говорит, что делать с невыполнимым требованием задачи (задачи 5 и 6 Братства против Moon Systems) | WARNING | APPLIED | D-049 |
| RED-013 | PLAYTHROUGH | GATE | P11 | Уникальный полковник «Роберт Клоуз» ставит вторую фабрику в регион и перебивает §3.6 через §3.9 | WARNING | APPLIED | D-045 |
| RED-014 | PLAYTHROUGH | DOOM | P11 | «Репрессии» без лимита частоты: шесть и более карт скрытого влияния за одну фазу влияния | WARNING | APPLIED | D-045 |
| RED-015 | PLAYTHROUGH | COMBAT | P11 | «Санкции» и «Системный сбой» преобразуют результаты по кругу; §8.5 порядка между ними не даёт | WARNING | APPLIED | D-045 |
| RED-016 | PLAYTHROUGH | MOVE | P11 | «Карательная операция» даёт бесплатный переброс любого числа отрядов через всю карту в чужой ход | WARNING | WONTFIX | D-045 |
| RED-017 | PLAYTHROUGH | TECH | P11 | «Жертва» не называет, какой вражеский боевой робот уничтожается и где; §3.9 отвечает наполовину | WARNING | APPLIED | D-045 |
| RED-018 | PLAYTHROUGH | COMBAT | P11 | Совет §8.7 про окружение противника неверен для пехотинца на фабрике | INFO | APPLIED | D-045 |
| RED-019 | PLAYTHROUGH | TECH | P11 | ORIGINAL PARITY: задача Островной Империи выполняется сама собой, без условий | INFO | WONTFIX | D-045 |
| RED-020 | PLAYTHROUGH | TECH | P11 | ORIGINAL PARITY: задача «накопить N нефти» выполняется чужим богатством через правило минимального запаса | INFO | WONTFIX | D-045 |
| RED-021 | PLAYTHROUGH | VICTORY | P11 | ORIGINAL PARITY: проигрывающий игрок может в любой момент обрушить партию в общее поражение | WARNING | APPLIED | D-045 |
| RED-022 | PLAYTHROUGH | COMBAT | P11 | ORIGINAL PARITY: «отступить некуда» стоит ровно одного отряда, сколько бы подавлений ни осталось | INFO | WONTFIX | D-045 |
| RED-023 | PLAYTHROUGH | GATE | P11 | ORIGINAL PARITY: фабрика, которую нельзя взять под контроль, кормит владельца нефтью и влиянием даром | INFO | WONTFIX | D-045 |
| RED-024 | PLAYTHROUGH | COMBAT | P11 | ORIGINAL PARITY: «Временной сдвиг» позволяет перебрасывать кубики неограниченно, пока есть нефть | INFO | WONTFIX | D-045 |
| RED-025 | PLAYTHROUGH | GATE | P11 | ORIGINAL PARITY: «Пространственный сдвиг» увозит ЧУЖУЮ контролируемую фабрику вместе с чужим пехотинцем | INFO | WONTFIX | D-045 |
| RED-026 | PLAYTHROUGH | DOOM | P11 | ORIGINAL PARITY: боевой робот на планшете остаётся «в игре» и даёт карту скрытого влияния, будучи неуязвимым | INFO | WONTFIX | D-045 |
| RED-027 | PLAYTHROUGH | UNIT | P11 | ORIGINAL PARITY: «Муштра» бесплатно меняет рекрутов на боевые машины в чужой ход, без фабрики и без лимита | INFO | WONTFIX | D-045 |
| TISS-012 | TERMINOLOGY | GLOSSARY | P12 | Глоссарий вырос с 47 статей до 49: «Карта лояльности» и «Основное действие» стоят вне замороженного состава | INFO | CLOSED | D-050 |
