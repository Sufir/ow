# -*- coding: utf-8 -*-
"""
Проверка кавычек в текстах печатных компонентов «Нефтяных войн».

    python3 print/check_quotes.py          проверить всё из списка ФАЙЛЫ
    python3 print/check_quotes.py <файл>   проверить один JSON

Правило (D-075, CLAUDE.md §4 «Кавычки»): на печатных компонентах —
только “ ”, для любой функции. Ёлочки « », лапки „ “ и прямые " — ошибка.
Пары “ ” должны закрываться в пределах одной строки данных, без вложения.

Сборка.py планшетов вызывает проверить() перед записью каждого планшета.
Код выхода 1, если нашлась хоть одна ошибка.
"""
import io, json, os, re, sys

ROOT = os.path.dirname(os.path.abspath(__file__))

# Источники истины текстов печатных компонентов. Новый источник — дописать сюда.
ФАЙЛЫ = [
    'Faction-Card-A/Данные/*.json',          # планшеты фракций, COMP-F-01
    'Saved/Cards - Технологии и задачи.json', # карты задач и технологий, COMP-F-07/08
]

ЗАПРЕЩЕНО = {'«': 'ёлочка «', '»': 'ёлочка »', '„': 'лапка „', '"': 'прямая "'}
ТЕГ = re.compile(r'<[^>]*>')


def _ошибки_строки(s):
    if s.startswith('data:'):                 # встроенные картинки
        return []
    s = ТЕГ.sub(' ', s)                        # атрибуты HTML-разметки не текст
    out = []
    for i, ch in enumerate(s):
        if ch in ЗАПРЕЩЕНО:
            out.append((ЗАПРЕЩЕНО[ch], s[max(0, i - 30):i + 30]))
    открыта = False
    for i, ch in enumerate(s):
        if ch == '“':
            if открыта:
                out.append(('вложенная или незакрытая “', s[max(0, i - 30):i + 30]))
            открыта = True
        elif ch == '”':
            if not открыта:
                out.append(('” без открывающей', s[max(0, i - 30):i + 30]))
            открыта = False
    if открыта:
        out.append(('незакрытая “', s[-60:]))
    return out


def проверить(данные, имя=''):
    """Вернуть список строк-ошибок для разобранного JSON. Пустой список — всё чисто."""
    ошибки = []

    def обход(x, путь):
        if isinstance(x, str):
            for что, где in _ошибки_строки(x):
                ошибки.append('%s %s: %s — …%s…' % (имя, путь, что, где.replace('\n', ' ')))
        elif isinstance(x, dict):
            for k, v in x.items():
                обход(v, путь + '.' + k)
        elif isinstance(x, list):
            for i, v in enumerate(x):
                обход(v, '%s[%d]' % (путь, i))

    обход(данные, '')
    return ошибки


def main():
    import glob
    пути = sys.argv[1:] or sorted(p for m in ФАЙЛЫ for p in glob.glob(os.path.join(ROOT, m)))
    всего = 0
    for p in пути:
        ош = проверить(json.load(io.open(p, encoding='utf-8')), os.path.relpath(p, ROOT))
        for строка in ош:
            print(строка)
        всего += len(ош)
    print('кавычки: %d файлов, %s' % (len(пути), 'ошибок нет' if not всего else 'ошибок %d' % всего))
    sys.exit(1 if всего else 0)


if __name__ == '__main__':
    main()
