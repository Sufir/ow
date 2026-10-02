# -*- coding: utf-8 -*-
"""
Сборка карт лояльности наёмных боевых роботов «Нефтяные войны» (COMP-V-10).

    python3 Сборка.py              собрать все карты реестра в Наёмники.html
    python3 Сборка.py Шрёд         собрать только карты, чьё имя содержит «Шрёд»
    python3 Сборка.py --шаблон     обновить демо-данные Шаблон.html (“C.R.A.B.” и “Шрёдингер”)

Что делает. Берёт Шаблон.html и подставляет в слот <!--#данные--> … <!--/#данные-->
JSON с картами. Содержимое карт — из rules/registry/mercenaries.yaml (источник истины
по числам и текстам), силуэт робота — из той же картинки, что в таблице отрядов планшета
его фракции (print/Faction-Card-A/Данные/<фракция>.json → отряды → иконка).

Всё оформление и вся раскладка — в шаблоне: карты строит его скрипт, он же подбирает
размер чертежа под свободное место и проверяет переполнение. Скрипт сборки только
готовит данные и переводит силуэт в векторный контур.

Какие роботы попадают в комплект: записи robots со status: SOURCED и с текстами
(text_draft) создания, способности, задачи и технологии. Новая карта — новая такая
запись в реестре; если у робота нет фракции или его силуэта нет на планшете,
путь к картинке задаётся полем silhouette записи (от корня проекта).

Переносы. Текст способностей и технологий набран по ширине (D-111); мягкие переносы (U+00AD)
в него ставит этот скрипт по словарю ru_RU пакета pyphen — так переносы одинаковые в любом браузере
и в PDF, а не зависят от словаря браузера. Подробно — функция переносы().

Зависимости: pyyaml, numpy, Pillow, pyphen.
"""
import io, json, os, re, sys

import numpy as np
import yaml
from PIL import Image, ImageFilter
try:
    import pyphen
except ImportError:
    sys.exit('Нужен пакет pyphen — переносы в тексте способностей и технологий: pip install pyphen')

PRINT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.dirname(PRINT)
HERE = os.path.dirname(os.path.abspath(__file__))
REGISTRY = os.path.join(ROOT, 'rules', 'registry', 'mercenaries.yaml')
FACTIONS = os.path.join(PRINT, 'Faction-Card-A', 'Данные')
TPL = os.path.join(HERE, 'Шаблон.html')
OUT = os.path.join(HERE, 'Наёмники.html')
ДЕМО = ('MRC-R-01', 'MRC-R-06')          # примеры этапа 2: самая лёгкая и самая плотная карта

# Проверка кавычек (D-075): общая для всех печатных компонентов, лежит в print/.
sys.path.insert(0, PRINT)
from check_quotes import проверить as проверить_кавычки


# ══════════════════════════════════════════════════════════════ СИЛУЭТ → КОНТУР
# Силуэт отряда — PNG с альфой. Альфа слегка размывается (1,6 пикселя), контур
# снимается по уровню 110 из 255 — так рваный край рисованного силуэта становится
# ровной линией чертежа — и упрощается до точности 0,9 пикселя. Координаты —
# в пикселях обрезанного по силуэту прямоугольника; масштаб считает шаблон.
БЛЮР, УРОВЕНЬ, ТОЧНОСТЬ = 1.6, 110.0, 0.9


def _упростить(pts, eps):
    """Дуглас — Пекер для замкнутой ломаной, без рекурсии."""
    if len(pts) < 4:
        return pts
    P = np.array(pts + [pts[0]], dtype=float)
    far = int(np.argmax(np.hypot(P[:, 0] - P[0, 0], P[:, 1] - P[0, 1])))
    keep = np.zeros(len(P), dtype=bool)
    keep[[0, far, len(P) - 1]] = True
    стек = [(0, far), (far, len(P) - 1)]
    while стек:
        a, b = стек.pop()
        if b - a < 2:
            continue
        dx, dy = P[b] - P[a]
        n = np.hypot(dx, dy)
        seg = P[a + 1:b] - P[a]
        dist = np.abs(dx * seg[:, 1] - dy * seg[:, 0]) / n if n > 0 else np.hypot(seg[:, 0], seg[:, 1])
        i = int(np.argmax(dist))
        if dist[i] > eps:
            k = a + 1 + i
            keep[k] = True
            стек += [(a, k), (k, b)]
    return [tuple(p) for p in P[:-1][keep[:-1]]]


def контур(png):
    """PNG силуэта → {'W', 'H', 'd', 'ext'}: размеры, SVG-путь и крайние точки."""
    a = Image.open(png).convert('RGBA').getchannel('A').filter(ImageFilter.GaussianBlur(БЛЮР))
    A = np.asarray(a, dtype=float)
    m = A > УРОВЕНЬ
    ys, xs = np.nonzero(m)
    y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
    m = m[y0:y1 + 1, x0:x1 + 1]
    H, W = m.shape
    # поле с рамкой в одну клетку нулей, чтобы все контуры замкнулись
    F = np.zeros((H + 2, W + 2))
    F[1:-1, 1:-1] = A[y0:y1 + 1, x0:x1 + 1] - УРОВЕНЬ
    # марширующие квадраты: точка контура на каждом ребре сетки, где меняется знак
    def точка(e):
        i, j, вертик = e
        if вертик:            # ребро (i, j) — (i + 1, j)
            a, b = F[i, j], F[i + 1, j]; t = a / (a - b)
            return (j - 1.0, i + t - 1.0)
        a, b = F[i, j], F[i, j + 1]; t = a / (a - b)
        return (j + t - 1.0, i - 1.0)
    сосед = {}
    def связь(p, q):
        сосед.setdefault(p, []).append(q); сосед.setdefault(q, []).append(p)
    S = (F > 0).astype(int)
    K = S[:-1, :-1] * 8 + S[:-1, 1:] * 4 + S[1:, 1:] * 2 + S[1:, :-1]
    for i, j in zip(*np.nonzero((K > 0) & (K < 15))):
        i, j, k = int(i), int(j), int(K[i, j])
        top, right, bottom, left = (i, j, 0), (i, j + 1, 1), (i + 1, j, 0), (i, j, 1)
        пары = {1: [(left, bottom)], 2: [(bottom, right)], 3: [(left, right)], 4: [(top, right)],
                6: [(top, bottom)], 7: [(left, top)], 8: [(left, top)], 9: [(top, bottom)],
                11: [(top, right)], 12: [(left, right)], 13: [(bottom, right)], 14: [(left, bottom)]}
        if k in (5, 10):      # седло: решает среднее значение клетки
            центр = (F[i, j] + F[i, j + 1] + F[i + 1, j + 1] + F[i + 1, j]) / 4 > 0
            if (k == 5) == центр:
                пары[k] = [(left, top), (bottom, right)]
            else:
                пары[k] = [(left, bottom), (top, right)]
        for p, q in пары[k]:
            связь(p, q)
    # обход петель
    пути, был = [], set()
    for start in сосед:
        if start in был:
            continue
        петля, prev, cur = [], None, start
        while True:
            был.add(cur); петля.append(точка(cur))
            nxt = [n for n in сосед[cur] if n != prev]
            if not nxt:
                break
            prev, cur = cur, nxt[0]
            if cur == start:
                break
        if len(петля) < 8:
            continue
        pts = _упростить(петля, ТОЧНОСТЬ)
        if len(pts) >= 3:
            пути.append('M' + ' L'.join('%.1f,%.1f' % p for p in pts) + ' Z')
    yy, xx = np.nonzero(m)
    ext = {'left': float(np.mean(yy[xx == xx.min()])), 'right': float(np.mean(yy[xx == xx.max()])),
           'top': float(np.mean(xx[yy == yy.min()])), 'bottom': float(np.mean(xx[yy == yy.max()]))}
    row = np.nonzero(m[H // 2])[0]
    ext['midleft'] = float(row.min()) if len(row) else 0.0
    return {'W': int(W), 'H': int(H), 'd': ' '.join(пути), 'ext': {k: round(v, 1) for k, v in ext.items()}}


# ══════════════════════════════════════════════════════════════ ПЕРЕНОСЫ
# Текст способностей и технологий набран по ширине (D-111), мягкие переносы ставятся здесь.
# Правила — для читаемости, а не для плотности:
#   • слово от 5 букв, строчное; на строке остаётся не меньше 2 букв, переносится не меньше 3;
#   • без переносов: имена в кавычках “ ”, слова с прописной, слова с дефисом, цифрами
#     или значком {R}; склейка неразрывными пробелами, в которой есть слово с прописной
#     (название региона: “Юг Тихого океана”), — целиком;
#   • в остальных склейках (“скрытого влияния”, “не считается перемещением”) слова переносятся:
#     неразрывный пробел держит слова на одной строке, а по ширине без переноса длинная склейка
#     уходит на новую строку и растягивает пробелы предыдущей на всю ширину.
SHY, NBSP = '\u00ad', '\u00a0'
_ПЕРЕНОС = pyphen.Pyphen(lang='ru_RU', left=2, right=3)
_СЛОВО = re.compile(r'^([^А-Яа-яЁё]*)([а-яё]{5,})([^А-Яа-яЁё]*)$')
_ПРОПИСНАЯ = re.compile(r'[А-ЯЁ]')


def переносы(v):
    """Текст (строка или список абзацев) → тот же текст с мягкими переносами."""
    if isinstance(v, list):
        return [переносы(p) for p in v]
    части = re.split(r'(“[^”]*”)', str(v).replace(SHY, ''))      # нечётные — имена в кавычках
    for k in range(0, len(части), 2):
        группы = части[k].split(' ')
        for g, группа in enumerate(группы):
            слова = группа.split(NBSP)
            if len(слова) > 1 and _ПРОПИСНАЯ.search(группа):
                continue
            for i, с in enumerate(слова):
                m = _СЛОВО.match(с)
                if m and '-' not in с:
                    слова[i] = m.group(1) + _ПЕРЕНОС.inserted(m.group(2), hyphen=SHY) + m.group(3)
            группы[g] = NBSP.join(слова)
        части[k] = ' '.join(группы)
    return ''.join(части)


# ══════════════════════════════════════════════════════════════ РЕЕСТР → КАРТЫ
def силуэт_по_планшету(имя, фракция):
    """Иконка робота из таблицы отрядов планшета его фракции."""
    if not фракция:
        return None
    p = os.path.join(FACTIONS, фракция + '.json')
    if not os.path.exists(p):
        return None
    d = json.load(io.open(p, encoding='utf-8'))
    чисто = lambda s: (s or '').strip('“”" ')          # на планшете имя может стоять без кавычек (“C.R.A.B.”)
    for u in d.get('отряды', []):
        if чисто(u.get('имя')) == чисто(имя) and u.get('иконка'):
            return os.path.join(PRINT, u['иконка'])
    return None


def карта(r):
    """Запись robots реестра → данные одной карты для шаблона."""
    def td(блок):
        v = (r.get(блок) or {}).get('text_draft')
        if v is None:
            raise ValueError('%s: нет %s.text_draft' % (r['id'], блок))
        return v
    png = os.path.join(ROOT, r['silhouette']) if r.get('silhouette') else силуэт_по_планшету(r['name'], r.get('faction_name'))
    if not png or not os.path.exists(png):
        raise ValueError('%s: не найден силуэт (поле silhouette или иконка на планшете фракции)' % r['id'])
    ab = r['ability']
    способности = ab if isinstance(ab, list) else [ab]
    return {
        'id': r['id'],
        'имя': r['name'],
        'фракция': r.get('faction_name'),
        'стоимость': str(r['cost']),
        'сила': str(r['combat']) if r.get('combat') is not None else 'n',
        'сноска': r.get('combat_note'),
        'создание': td('creation'),
        'способности': [{'название': a['name'], 'фаза': a['phase'], 'текст': переносы(a['text_draft'])} for a in способности],
        'задача': td('task'),
        'технология': {'название': r['technology']['name'], 'фаза': r['technology']['phase'], 'текст': переносы(td('technology'))},
        'силуэт_файл': os.path.relpath(png, ROOT).replace(os.sep, '/'),
        'силуэт': контур(png),
    }


def роботы():
    d = yaml.safe_load(io.open(REGISTRY, encoding='utf-8'))
    return [r for r in d['robots'] if r.get('status') == 'SOURCED']


def подставить(шаблон, данные):
    блок = json.dumps(данные, ensure_ascii=False, indent=1)
    новое = '<!--#данные-->\n<script type="application/json" id="card-data">\n' + блок + '\n</script>\n<!--/#данные-->'
    s, n = re.subn(r'<!--#данные-->.*?<!--/#данные-->', lambda m: новое, шаблон, flags=re.S)
    if n != 1:
        raise ValueError('в шаблоне нет слота <!--#данные--> … <!--/#данные-->')
    return s


def main():
    арг = sys.argv[1:]
    в_шаблон = '--шаблон' in арг
    фильтр = [a for a in арг if not a.startswith('--')]
    rs = роботы()
    if в_шаблон:
        rs = [r for r in rs if r['id'] in ДЕМО]
    elif фильтр:
        rs = [r for r in rs if any(f.lower() in r['name'].lower() for f in фильтр)]
    if not rs:
        sys.exit('Нет карт для сборки.')
    карты = []
    for r in rs:
        c = карта(r)
        print('%-9s %-16s силуэт %s — %d × %d пикс.' % (c['id'], c['имя'], c['силуэт_файл'], c['силуэт']['W'], c['силуэт']['H']))
        карты.append(c)
    данные = {'компонент': 'COMP-V-10, карты лояльности наёмных боевых роботов',
              'формат': 'Tarot 70 × 120 мм, двусторонняя: сторона 1 — задача, сторона 2 — технология (переворот)',
              'источник': 'rules/registry/mercenaries.yaml',
              'карты': карты}
    ошибки = проверить_кавычки({'карты': [{k: v for k, v in c.items() if k != 'силуэт'} for c in карты]}, 'Наёмники')
    if ошибки:
        print('\n'.join(ошибки))
        sys.exit('Кавычки: %d ошибок, карты не собраны (D-075).' % len(ошибки))
    шаблон = io.open(TPL, encoding='utf-8').read()
    куда = TPL if в_шаблон else OUT
    s = подставить(шаблон, данные)
    if not в_шаблон:
        s = s.replace('<title>Наёмники — шаблон</title>', '<title>Наёмники</title>')
    io.open(куда, 'w', encoding='utf-8', newline='\n').write(s)
    print('Записано: %s — %d карт.' % (os.path.relpath(куда, ROOT), len(карты)))


if __name__ == '__main__':
    main()
