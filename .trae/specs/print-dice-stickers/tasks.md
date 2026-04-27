# Tasks
- [x] Task 1: Подготовка базовой структуры и стилей
  - [x] SubTask 1.1: Создать (или обновить) `Dices.html` с базовой разметкой и подключением `dices/dices.css`.
  - [x] SubTask 1.2: Создать папку `dices` и файл `dices.css` (или обновить существующий).
  - [x] SubTask 1.3: Настроить правила печати (`@page { size: A4; margin: 10mm; }`, `print-color-adjust: exact`).
- [x] Task 2: Настройка сетки и контейнера
  - [x] SubTask 2.1: Создать сетку на 14 колонок по 13mm, строки 13mm, без gap (`grid-template-columns: repeat(14, 13mm); grid-auto-rows: 13mm;`).
  - [x] SubTask 2.2: Центрировать сетку на странице (например, через `justify-content: center` или `margin: 0 auto`).
- [x] Task 3: Стилизация ячеек и контента
  - [x] SubTask 3.1: Настроить flex-центрирование внутри ячеек (13x13mm), `margin: 0`, `padding: 0`.
  - [x] SubTask 3.2: Настроить изображения (`width: 100%; height: 100%; object-fit: contain;`).
  - [x] SubTask 3.3: Подключить шрифт `AlienEncounters.ttf` локально (`@font-face` из `../fonts/AlienEncounters.ttf` или аналогично).
  - [x] SubTask 3.4: Стилизовать цифры (цвет `#00ffff`, высота ~85% от ячейки, `text-rendering: geometricPrecision; -webkit-font-smoothing: none;`).
- [x] Task 4: Метки реза (крестики)
  - [x] SubTask 4.1: Реализовать черные крестики на углах/стыках ячеек с помощью CSS (например, псевдоэлементы или background/border хитрости), без сплошных рамок.
- [x] Task 5: Генерация HTML-разметки наклеек
  - [x] SubTask 5.1: Добавить блок `<!-- KILL START -->` и 20 ячеек с `<img src="./dices/kill.png">`.
  - [x] SubTask 5.2: Добавить блок `<!-- RETREAT START -->` и 40 ячеек с `<img src="./dices/retreat.png">`.
  - [x] SubTask 5.3: Добавить блок `<!-- NUMBERS START -->` и по 20 ячеек для "1", "2", "3".
  - [x] SubTask 5.4: Убедиться, что всего ровно 120 ячеек и они идут подряд.

# Task Dependencies
- [Task 2] depends on [Task 1]
- [Task 3] depends on [Task 2]
- [Task 4] depends on [Task 3]
- [Task 5] depends on [Task 4]
