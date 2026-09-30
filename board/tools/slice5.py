"""
slice5.py — нарезка классической основы на 21 область раскладки на пятерых (MC-5P).

Этап 1 компонента COMP-C-03, проба. Основа — board/geo/classic-base.geojson (D-096),
граф — board/derived/MC-5P.json (решение Alek 18.09.2026: нарушать нельзя).

Как режется:
  1. Каждый материк основы делится РАЗРЕЗАМИ — ломаными в мм полотна, которые
     проходят материк насквозь от моря до моря. Куски, на которые разрезы делят
     материк, получают область по ЗЁРНАМ — точкам внутри куска. Кусок без зерна
     (остров) отходит области ближайшего зерна того же материка; это пишется в лог.
     Сумма детей равна материку основы по построению (SPEC-BOARD §3.2).
  2. Внутренние воды основы (Чёрное, Каспийское, север Красного моря) —
     не океан: каждое целиком отходит области суши из LAKES.
  3. Океан = прямоугольник карты минус суша и озёра. Режется так же: разрезы
     по воде от берега до берега или до края полотна, куски — по зёрнам.
     Склейка краёв (решение № 18): разрезы Северный Ледовитый / Север Тихого
     и Север Тихого / Индийский стоят на левом и правом краю на одной высоте —
     Y_ARC и Y_IND, общие для обоих краёв.
  4. Куски мельче 1 см², которые дали разрезы, отходят соседу того же рода
     с самой длинной общей границей (лог).

Каждый разрез — строка в CUTS с причиной: какое ребро или не-ребро графа он держит.
Правится только здесь; GeoJSON и SVG руками не правятся.

Запуск из корня репозитория:
    python3 board/tools/slice5.py all      собрать, проверить boardcheck, записать
    python3 board/tools/slice5.py fast     то же без укладки фигур (быстро), файлы пишутся
    python3 board/tools/slice5.py png      собрать и нарисовать PNG для глаз в scratch (не в репозиторий)

Пишет:
    board/geo/board-MC-5P.geojson    источник истины, мм полотна
    board/geo/board-MC-5P.svg        картинка из geojson
    board/geo/board-MC-5P.html       просмотр: области, id и метрики, граф, черновик, основа, склейка
Файлы пишутся и при красной проверке — это проба; код возврата 1, если есть отказы.
Зависимости: numpy, shapely, scipy, pyyaml (+ boardcheck.py и boardview.py рядом:
boardview.py — общая с glue.py запись и отрисовка).
"""
import json
import sys
from datetime import date
from pathlib import Path

import numpy as np
from shapely.geometry import LineString, Point, Polygon, box, shape
from shapely.ops import polygonize, unary_union

sys.path.insert(0, str(Path(__file__).resolve().parent))
import boardcheck as bc  # noqa: E402
import boardview as bv  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
GEO = ROOT / 'board' / 'geo'
BASE = GEO / 'classic-base.geojson'
OUT = GEO / 'board-MC-5P'
LAYOUT = 'MC-5P'

X0, Y0, X1, Y1 = bc.RECT                    # прямоугольник карты в мм полотна
RECT = box(X0, Y0, X1, Y1)
CRUMB = 100.0                               # мм²: кусок мельче — к соседу

# высота разрезов на склейке краёв: одна и та же слева и справа (решение № 18)
Y_ARC = 78.0      # Северный Ледовитый | Север Тихого: ниже Берингова пролива
Y_IND = 272.0     # Север Тихого | Индийский: выше Австралии на ≥ 12 мм (не-рёбра Тихий—Австралия, Тихий—НЗ)
T_PAC = (178.0, 270.0)    # тройная точка Север Тихого / Индийский / Юг Тихого — у мыса Йорк
T_ASIA = (750.0, 208.0)   # тройная точка Аравия / Северная Азия / Южная Азия

# ---------------------------------------------------------------------------
# дети материков и зёрна
# ---------------------------------------------------------------------------

CHILDREN = {
    'north_america': ['MR-L5-NAMW', 'MR-L5-NAME', 'MR-L5-CAM'],
    'south_america': ['MR-L5-SAMW', 'MR-L5-SAME'],
    'europe': ['MR-R5-SCA', 'MR-R5-EUR'],
    'asia': ['MR-R5-ASIN', 'MR-R5-ASIS', 'MR-R5-ARB'],
    'africa': ['MR-R5-AFRW', 'MR-R5-AFRE'],
    'australia': ['MR-L5-AUS', 'MR-L5-NZL'],
    'antarctica': ['MR-SH-ANT'],
}
OCEANS = ['MR-OC-ARC', 'MR-OC-NPAC', 'MR-OC-NATL', 'MR-OC-SATL', 'MR-OC-SPAC', 'MR-OC-IND']

# Кто владеет стыком, где материки основы налезают друг на друга: кто раньше, тот и владеет.
# Порядок тот же, что в classic.py (assemble). Нужен из-за упрощения основы: classic.py упрощает
# каждый материк и озеро порознь, и на стыках они налезают на доли мм² (Европа — Азия 1,2 мм²,
# Чёрное море — Европа 0,6). В MC-5P каждая пара ниже допуска 1 мм², но склейка стороны «3»
# их складывает: Азия — Европа 1,5 мм² — отказ формата на MC-3P и MC-4P-B (этап 2).
OWNER = ['europe', 'asia', 'africa', 'north_america', 'south_america', 'australia', 'antarctica']

# зёрна: точка внутри куска -> область. Острова, которые должны уйти не к ближайшему
# зерну, получают своё зерно явно.
SEEDS = {
    'MR-L5-NAMW': [(150, 110)],
    'MR-L5-NAME': [(300, 160), (355, 60), (345, 148)],            # материк, Гренландия, Ньюфаундленд
    'MR-L5-CAM': [(215, 250), (290, 314)],                          # Мексика, южный кусок за проливом
    'MR-L5-SAMW': [(262, 380), (285, 480)],
    'MR-L5-SAME': [(360, 380)],
    'MR-R5-SCA': [(540, 70), (428, 60)],                           # Скандинавия, Исландия
    'MR-R5-EUR': [(560, 150), (440, 128), (428, 124)],             # Европа, Британия, Ирландия
    'MR-R5-ASIN': [(760, 110)],
    'MR-R5-ASIS': [(800, 240)],
    'MR-R5-ARB': [(675, 300), (580, 212)],                         # Аравия, Анатолия
    'MR-R5-AFRW': [(520, 300)],
    'MR-R5-AFRE': [(600, 420)],
    'MR-L5-AUS': [(70, 400)],
    'MR-L5-NZL': [(180, 420)],
    'MR-SH-ANT': [(700, 525)],
    'MR-OC-ARC': [(450, 20), (260, 110)],                          # полоса, Гудзонов залив
    'MR-OC-NPAC': [(60, 180), (882, 200)],                         # у левого и у правого края
    'MR-OC-NATL': [(380, 250), (500, 205), (520, 105)],            # Атлантика, Средиземное, Балтика
    'MR-OC-SATL': [(480, 420)],
    'MR-OC-SPAC': [(240, 445), (300, 490)],
    'MR-OC-IND': [(750, 420), (60, 530)],                          # у правого и у левого края
}

# внутренние воды основы -> область суши, в которую входят целиком
LAKES = {
    'Чёрное море': ('MR-R5-EUR', 'южный берег — граница Европа — Аравия (ME-...: Европа — Аравия)'),
    'Каспийское море': ('MR-R5-ARB', 'Аравия граничит через него с Европой и Северной Азией'),
    'Красное море': ('MR-R5-ARB', 'север Красного моря — озеро, отходит Аравии'),
}

# ---------------------------------------------------------------------------
# разрезы: (что | что, ломаная в мм полотна, причина)
# ---------------------------------------------------------------------------

CUTS_LAND = [
    ('Центральная Америка | Запад Северной Америки',
     [(118, 120), (150, 124), (190, 130), (222, 138), (234, 165), (238, 205), (236, 225), (234, 240)],
     'Центральной Америке нужна площадь: Мексика одна не даёт U ≥ 55; берег Мексиканского залива восточнее остаётся Западу (ME: Запад — Север Атлантики)'),
    ('Запад Северной Америки | Восток Северной Америки',
     [(228, 72), (234, 105), (238, 140), (262, 165), (304, 188)],
     'от Ледовитого к Атлантике: Восток — Квебек, Онтарио, засыпанный Гудзонов залив и северо-восток США; Запад держит берег залива между Центральной Америкой и Флоридой — Центральная Америка — Восток не смежны, зазор ≥ 12'),
    ('Запад Южной Америки | Восток Южной Америки',
     [(294, 318), (304, 345), (312, 375), (318, 405), (327, 428), (338, 446), (348, 458)],
     'Запад — Анды и Патагония: выходит в Юг Атлантики южнее Ла-Платы (ME-034); Восток — в Юг Тихого не выходит (зазор ≥ 12)'),
    ('Скандинавия | Европа',
     [(548, 115), (580, 122), (615, 134), (648, 142), (672, 142), (714, 136)],
     'Скандинавия — весь север до Урала (ME: с Ледовитым, с Северной Азией); Европа от Ледовитого отодвинута ≥ 12 мм'),
    ('Аравия | Северная Азия',
     [(686, 208), (712, 214), (738, 210), T_ASIA],
     'Иран и Афганистан — Аравии; Туркмения и Узбекистан — Северной Азии (ME-013)'),
    ('Аравия | Южная Азия',
     [T_ASIA, (749, 228), (744, 252), (736, 280)],
     'по Инду: Пакистан до Инда — Аравии (D-096, проба основы)'),
    ('Северная Азия | Южная Азия',
     [T_ASIA, (747, 165), (767, 137), (788, 122), (803, 120)],
     'Монголия и Маньчжурия — Южной Азии: она отдала Аравии Пакистан, добирает у Северной (D-096)'),
    ('Западная Африка | Восточная Африка',
     [(520, 380), (548, 366), (578, 338), (600, 310), (624, 292)],
     'Восточная — Рог, восток, юг и Конго: выходит в Индийский и в Юг Атлантики; Западная — в Индийский не выходит (зазор ≥ 12); площади близки'),
    ('Австралия | Новая Зеландия',
     [(129, 330), (121, 380), (115, 430), (113, 470), (113, 530)],
     'Новая Зеландия — восточная половина Австралии основы, как в черновике; площади поровну (Alek)'),
]

# какой материк режет разрез суши (разрез режет только свой материк)
CUT_CONT = {
    'Центральная Америка | Запад Северной Америки': 'north_america',
    'Запад Северной Америки | Восток Северной Америки': 'north_america',
    'Запад Южной Америки | Восток Южной Америки': 'south_america',
    'Скандинавия | Европа': 'europe',
    'Аравия | Северная Азия': 'asia',
    'Аравия | Южная Азия': 'asia',
    'Северная Азия | Южная Азия': 'asia',
    'Западная Африка | Восточная Африка': 'africa',
    'Австралия | Новая Зеландия': 'australia',
}

CUTS_OCEAN = [
    ('Северный Ледовитый | Север Тихого, слева', [(X0 - 2, Y_ARC), (45, 80)],
     'Берингов пролив; высота Y_ARC — та же, что у правого края'),
    ('Северный Ледовитый | Север Тихого, справа', [(X1 + 2, Y_ARC), (866, 82)],
     'Берингов пролив со стороны Чукотки'),
    ('Северный Ледовитый | Север Атлантики: Гудзонов пролив', [(306, 86), (309, 101)],
     'Бассейн Фокса — Ледовитому, Гудзонов пролив — Атлантике (сам залив засыпан)'),
    ('Северный Ледовитый | Север Атлантики: Девисов пролив', {'strait': ((325, 80), (345, 85), (310, 65, 360, 100))},
     'Баффинова земля — Гренландия'),
    ('Северный Ледовитый | Север Атлантики: Датский пролив', {'strait': ((385, 70), (428, 60), (370, 45, 445, 80))},
     'Гренландия — Исландия'),
    ('Северный Ледовитый | Север Атлантики: Исландия — Норвегия', {'strait': ((432, 58), (505, 62), (420, 40, 530, 75))},
     'Норвежское море — Атлантике, Баренцево — Ледовитому: Скандинавия выходит в оба (ME: Скандинавия — Ледовитый, — Атлантика)'),
    ('Север Тихого | Индийский, слева', [(X0 - 2, Y_IND), T_PAC],
     'выше Австралии ≥ 12 мм: Север Тихого с Австралией и Новой Зеландией не смежен'),
    ('Север Тихого | Юг Тихого', [T_PAC, (212, 306), (240, 352)],
     'к берегу Эквадора: Запад Южной Америки выходит в оба Тихих (ME-048, ME-035)'),
    ('Индийский | Юг Тихого, север', [T_PAC, (164, 306)],
     'к мысу Йорк: залив Карпентария — Индийскому, восточный берег — Югу Тихого (ME: Новая Зеландия — оба)'),
    ('Индийский | Юг Тихого, юг', [(160, 470), (160, Y1 + 2)],
     'южный берег Австралии — Индийскому, восточнее — Югу Тихого: Австралия с Югом Тихого не смежна'),
    ('Север Тихого | Индийский, справа', [(X1 + 2, Y_IND), (827, 272)],
     'высота Y_IND — та же, что у левого края; к берегу Южного Китая'),
    ('Север Тихого | Север Атлантики: Панамский пролив', {'strait': ((262, 285), (262, 306), (250, 280, 280, 310))},
     'ME-074: два океана смежны напрямую, через пролив'),
    ('Север Атлантики | Юг Атлантики', [(424, 364), (466, 362), (506, 358)],
     'угол Бразилии — Гвинейский залив, не по самому узкому месту: так граница двух Атлантик ≥ 25 мм; Восток Южной Америки и Западная Африка выходят в оба'),
    ('Юг Атлантики | Юг Тихого', {'strait': ((280, 500), (460, 505), (250, 460, 520, 540))},   # Антарктида левее на 20 мм (classic.ANT_DX)
     'Магелланов узел (ME-077): пролив Дрейка, мыс Горн — Антарктический полуостров'),
    ('Юг Атлантики | Индийский', {'strait': ((565, 482), (575, 510), (540, 470, 620, 530))},
     'мыс Игольный — Антарктида'),
]

# ---------------------------------------------------------------------------
# сборка
# ---------------------------------------------------------------------------


def polys(g):
    return bc.polys(g)


def load_decor():
    """острова-декор основы: (материк, полигон) — не суша областей, рисуются поверх океана"""
    fc = json.loads(BASE.read_text(encoding='utf-8'))
    return [(f['properties']['continent'], shape(f['geometry'])) for f in fc['features']
            if f['properties']['type'] == 'DECOR_ISLAND']


def decor_region(cont, g):
    """чей декор: ближайшее зерно среди детей материка"""
    c = g.representative_point()
    return min(((rid, Point(xy).distance(c)) for rid in CHILDREN[cont] for xy in SEEDS[rid]), key=lambda t: t[1])[0]


def load_base():
    fc = json.loads(BASE.read_text(encoding='utf-8'))
    C, lakes = {}, {}
    for f in fc['features']:
        p, g = f['properties'], shape(f['geometry'])
        if p['type'] == 'LAND':
            C[p['id']] = g
        elif p['type'] == 'INLAND_WATER':
            lakes[p['name_ru']] = g
    return C, lakes


def strait(C, pa, pb, win):
    """разрез по самому узкому месту пролива: между куском суши у точки pa и куском
    у точки pb в окне win; концы заходят на сушу на 1,5 мм"""
    from shapely.ops import nearest_points
    land = [p for g in C.values() for p in polys(g)]
    W = box(*win)

    def piece(xy):
        P = Point(xy)
        return min(land, key=lambda p: p.distance(P)).intersection(W)
    a, b = nearest_points(piece(pa), piece(pb))
    v = np.subtract(b.coords[0], a.coords[0])
    v = v / np.hypot(*v)
    return [tuple(np.subtract(a.coords[0], v * 1.5)), tuple(np.add(b.coords[0], v * 1.5))]


def resolve(cuts, C):
    """разрезы вида {'strait': (pa, pb, окно)} -> ломаная"""
    out = []
    for nm, pts, why in cuts:
        if isinstance(pts, dict):
            pts = strait(C, *pts['strait'])
        out.append((nm, [tuple(map(float, p)) for p in pts], why))
    return out


def extend(pts, geom, nodes, log, name):
    """конец разреза, оставшийся внутри разрезаемого, дотягивается по направлению
    последнего отрезка до выхода наружу (+1 мм). Общие узлы разрезов не трогаются."""
    pts = [tuple(p) for p in pts]
    for end in (0, -1):
        p = pts[end]
        if p in nodes or not geom.contains(Point(p)):
            continue
        q = pts[1] if end == 0 else pts[-2]
        v = np.subtract(p, q)
        v = v / np.hypot(*v)
        for k in np.arange(0.5, 80.0, 0.5):
            r = tuple(np.add(p, v * k))
            if not geom.contains(Point(r)):
                r = tuple(np.add(p, v * (k + 1.0)))
                if k > 12:
                    log.append(f'разрез «{name}»: конец дотянут на {k:.0f} мм — проверить точку')
                break
        pts[end] = r
    return pts


def faces(geom, lines, log=None):
    """геометрия, разрезанная ломаными; куски — полигоны внутри geom"""
    log = [] if log is None else log
    ends = [tuple(p) for _, pts, _ in lines for p in (pts[0], pts[-1])]
    nodes = {p for p in ends if ends.count(p) > 1}
    ls = [LineString(extend(pts, geom, nodes, log, nm)).intersection(geom.buffer(0.5)) for nm, pts, _ in lines]
    ls = [l for l in ls if not l.is_empty]
    work = unary_union([geom.boundary] + ls)
    out = []
    for f in polygonize(work):
        if geom.contains(f.representative_point()):
            out.append(f.intersection(geom))
    return [p for f in out for p in polys(f)]


def label(fs, ids, log, what):
    """куски -> области по зёрнам; кусок без зерна — ближайшему зерну"""
    pts = [(rid, Point(xy)) for rid in ids for xy in SEEDS[rid]]
    lab = {rid: [] for rid in ids}
    for f in fs:
        hit = sorted({rid for rid, p in pts if f.covers(p)})
        if len(hit) > 1:
            log.append(f'ОШИБКА {what}: в одном куске зёрна {", ".join(hit)} — разрез не прошёл насквозь '
                       f'(кусок у {f.representative_point().x:.0f}, {f.representative_point().y:.0f})')
            lab[hit[0]].append(f)
        elif hit:
            lab[hit[0]].append(f)
        else:
            rid = min(pts, key=lambda t: t[1].distance(f))[0]
            c = f.representative_point()
            if f.area >= CRUMB:
                log.append(f'{what}: кусок {f.area / 100:.1f} см² у ({c.x:.0f}, {c.y:.0f}) без зерна — к ближайшему, {rid}')
            lab[rid].append(f)
    return lab


def merge_crumbs(R, ids, log, what):
    """куски мельче 1 см² — соседу того же рода с самой длинной общей границей"""
    for rid in ids:
        keep = []
        for p in polys(R[rid]):
            if p.area >= CRUMB:
                keep.append(p)
                continue
            best, bl = None, 0.0
            for other in ids:
                if other == rid:
                    continue
                L = p.boundary.intersection(R[other].buffer(0.05)).length
                if L > bl:
                    best, bl = other, L
            if best:
                R[best] = unary_union([R[best], p])
                c = p.representative_point()
                log.append(f'{what}: крошка {p.area:.0f} мм² у ({c.x:.0f}, {c.y:.0f}) — от {rid} к {best}')
            else:
                keep.append(p)       # остров-крошка: отдать некому, пусть ловит проверка
        R[rid] = unary_union(keep)


def build():
    C, lakes = load_base()
    log, R = [], {}
    for cont, kids in CHILDREN.items():
        mine = [c for c in CUTS_LAND if CUT_CONT[c[0]] == cont]
        fs = faces(C[cont], mine, log) if len(kids) > 1 else polys(C[cont])
        lab = label(fs, kids, log, cont)
        for rid in kids:
            R[rid] = unary_union(lab[rid])
        if len(kids) > 1:
            merge_crumbs(R, kids, log, cont)
    # наложения основы: каждый клочок стыка — одной области (OWNER); озеро — целиком своей
    taken = Polygon()
    for cont in OWNER:
        for rid in CHILDREN[cont]:
            R[rid] = R[rid].difference(taken)
        taken = unary_union([taken] + [R[rid] for rid in CHILDREN[cont]])
    lands = [r for kids in CHILDREN.values() for r in kids]
    for nm, g in lakes.items():
        rid = LAKES[nm][0]
        for other in lands:
            if other != rid:
                R[other] = R[other].difference(g)
        R[rid] = unary_union([R[rid], g])
    land = unary_union([C[k] for k in C] + list(lakes.values()))
    water = polys(RECT.difference(land))
    ocean = max(water, key=lambda p: p.area)          # мировой океан связен (проверка основы)
    for p in water:                                   # щели и лужи между материками основы — к суше
        if p is ocean:
            continue
        best = max(lands, key=lambda r: p.boundary.intersection(R[r].buffer(0.05)).length)
        R[best] = unary_union([R[best], p])
        if p.area > 1.0:
            c = p.representative_point()
            log.append(f'лужа {p.area:.1f} мм² у ({c.x:.0f}, {c.y:.0f}) между материками основы — к {best}')
    cuts = resolve(CUTS_OCEAN, C)
    lab = label(faces(ocean, cuts, log), OCEANS, log, 'океан')
    for rid in OCEANS:
        R[rid] = unary_union(lab[rid])
    merge_crumbs(R, OCEANS, log, 'океан')
    for rid in R:
        R[rid] = clean(R[rid])
    return R, C, lakes, log, cuts


clean, rounded = bv.clean, bv.rounded      # общие с glue.py — boardview.py

# ---------------------------------------------------------------------------
# запись: geojson
# ---------------------------------------------------------------------------


def geojson(R, spec, rows):
    feats = [bv.feature(rid, rounded(R[rid]), spec, rows.get(rid, {})) for rid in spec['areas']]
    return {
        'type': 'FeatureCollection',
        'metadata': {
            'name': f'oil-wars-board-{LAYOUT}', 'layout': LAYOUT, 'generated': date.today().isoformat(),
            'generator': 'board/tools/slice5.py', 'base': 'board/geo/classic-base.geojson',
            'graph': f'board/derived/{LAYOUT}.json',
            'coordinateSystem': {'units': 'mm', 'origin': 'левый верхний угол полотна', 'axis': 'x вправо, y вниз',
                                 'canvas': list(bc.CANVAS), 'map_rect': list(bc.RECT)},
            'wrap': 'левый и правый края склеены: Северный Ледовитый, Север Тихого и Индийский — по куску у каждого края, '
                    f'границы на высоте {Y_ARC:g} и {Y_IND:g} мм на обоих краях',
            'rings': 'RFC 7946 в координатах файла: внешнее кольцо — положительная площадь',
            'cuts_land': [{'between': a, 'points': p, 'reason': r} for a, p, r in CUTS_LAND],
            'cuts_ocean': [{'between': a, 'points': [[round(x, 2), round(y, 2)] for x, y in p], 'reason': r}
                           for a, p, r in resolve(CUTS_OCEAN, load_base()[0])],
            'lakes': {k: {'region': v[0], 'reason': v[1]} for k, v in LAKES.items()},
        },
        'features': feats,
    }

# ---------------------------------------------------------------------------
# картинка: svg и html — boardview.py
# ---------------------------------------------------------------------------


def graph_nodes(R, spec):
    """точки графа: первое зерно области"""
    return {rid: bv.node_point(R[rid], SEEDS[rid][0]) for rid in spec['areas']}


def svg(R, spec):
    return bv.svg(R, spec, 'Нефтяные войны — поле на пятерых (MC-5P), нарезка, проба')


def html(R, C, spec, chk, log):
    return bv.html(R, C, spec, chk, log, nodes=graph_nodes(R, spec),
                   decor=[(decor_region(k, g), g) for k, g in load_decor()],
                   page_title='Поле MC-5P — нарезка',
                   heading='Поле на пятерых (MC-5P) — нарезка классической основы, проба',
                   generator='board/tools/slice5.py', log_title='Лог нарезки')


# ---------------------------------------------------------------------------


def png(R, C, spec, path, chk=None):
    """картинка для глаз — только в scratch, не в репозиторий"""
    from PIL import Image, ImageDraw
    s = 2.0
    W, H = bc.CANVAS
    im = Image.new('RGB', (int(W * s), int(H * s)), '#ece8df')
    d = ImageDraw.Draw(im)
    for rid in spec['areas']:
        for p in polys(R[rid]):
            d.polygon([(x * s, y * s) for x, y in p.exterior.coords], fill=bv.COLOUR[rid], outline='#222')
            for r in p.interiors:
                d.line([(x * s, y * s) for x, y in r.coords], fill='#222')
    for x in range(0, int(W) + 1, 50):
        d.line([(x * s, 0), (x * s, H * s)], fill='#ffffff')
    for y in range(0, int(H) + 1, 50):
        d.line([(0, y * s), (W * s, y * s)], fill='#ffffff')
    if chk:
        nodes = graph_nodes(R, spec)
        st = {frozenset((a, b)): lvl for a, b, L, lvl in chk['edges']}
        for e in spec['edges']:
            a, b = sorted(e)
            col = {'ok': '#1d6b3a', 'WARN': '#c77800', 'FAIL': '#ff0000'}[st.get(e, 'FAIL')]
            for p, q in bv.edge_lines(nodes[a], nodes[b]):
                d.line([(p[0] * s, p[1] * s), (q[0] * s, q[1] * s)], fill=col, width=2)
        for a, b, dd, L in chk['close']:
            if L > bc.TOL or dd < bc.GAP_MIN:
                for p, q in bv.edge_lines(nodes[a], nodes[b]):
                    d.line([(p[0] * s, p[1] * s), (q[0] * s, q[1] * s)], fill='#ff00ff', width=3)
        for rid, (x, y) in nodes.items():
            d.ellipse([x * s - 4, y * s - 4, x * s + 4, y * s + 4], fill='black')
            d.text((x * s + 5, y * s - 5), rid.split('-')[-1], fill='black')
    im.save(path)


def main(argv):
    cmd = argv[1] if len(argv) > 1 else 'all'
    if cmd not in ('all', 'fast', 'png'):
        print(__doc__)
        return 2
    spec = bc.load_spec(LAYOUT)
    R, C, lakes, log, cuts = build()
    for t in log:
        print('  лог  ' + t)
    fc = geojson(R, spec, {})
    R = {f['properties']['id']: shape(f['geometry']) for f in fc['features']}
    chk = bc.run(fc, spec, str(BASE), with_pack=(cmd == 'all'))
    nf = bc.print_results(chk)
    for rid in spec['areas']:
        r = chk['rows'][rid]
        print(f'   {rid:12} A {r["A"]:6.1f}  U {r["U"]:6.1f}  U/A {r["UA"]:.2f}  N {r.get("N25", "-")}/{r.get("N40", "-")}/{r.get("N60", "-")}'
              f'  связн {r["share"] * 100:3.0f}%')
    if cmd == 'png':
        out = argv[2] if len(argv) > 2 else 'board-MC-5P.png'
        png(R, C, spec, out, chk)
        print(f'PNG: {out}')
        return 1 if nf else 0
    fc = geojson(R, spec, chk['rows'])
    OUT.with_suffix('.geojson').write_text(json.dumps(fc, ensure_ascii=False), encoding='utf-8')
    OUT.with_suffix('.svg').write_text(svg(R, spec), encoding='utf-8')
    OUT.with_suffix('.html').write_text(html(R, C, spec, chk, log), encoding='utf-8')
    print(f'\nЗаписано: {OUT.name}.geojson, .svg, .html')
    return 1 if nf else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
