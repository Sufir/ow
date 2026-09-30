"""
palette.py — цвета областей игрового поля: подбор палитры, контраст соседей, тестовая страница.

Этап 3 компонента COMP-C-03, шаг 1. Цвет области один на все полотна, где она есть;
контраст проверяется по графу каждой из четырёх раскладок (board/derived/MC-*.json →
edge_list, включая рёбра через склейку краёв).

Правила (задача Alek 30.09.2026, SPEC-BOARD §9):
  - стартовые области — цвет своей фракции; остальная суша — от цвета фракции своего
    материка или соседа (семейство оттенков, FAMILY), океаны — голубые, синие, морской волны;
  - соседи контрастны: «светлые рядом с тёмными» — это в первую очередь ΔL*;
  - светлота рабочей зоны 25–55 % (SPEC §9) — по HSL (Alek 30.09.2026); Ледовитый и Антарктида
    закреплены Alek вне §9 (PINNED); Юг Тихого и Азия цвет фракции не берут (NOT_FACTION).

Подбор детерминированный: отжиг по сетке кандидатов в CIE LCh с фиксированным зерном.

Запуск из корня репозитория:
    python3 board/tools/palette.py solve OUT.json [варианты]   подбор вариантов в OUT.json
    python3 board/tools/palette.py test OUT.json    тестовая страница board/geo/palette-test.html
    python3 board/tools/palette.py table           контраст принятых цветов (board/redesign.yaml), markdown
Зависимости: numpy, shapely, scipy, pyyaml (+ boardcheck.py, slice5.py рядом).
"""
import json
import math
import random
import sys
from pathlib import Path

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[2]
BOARD = ROOT / 'board'
GEO = BOARD / 'geo'
LAYOUTS = ('MC-3P', 'MC-4P-A', 'MC-4P-B', 'MC-5P')
SIDES = {'MC-3P': ('L3', 'R3'), 'MC-4P-A': ('L3', 'R5'), 'MC-4P-B': ('L5', 'R3'), 'MC-5P': ('L5', 'R5')}

# ---------------------------------------------------------------------------
# цвет: sRGB ↔ CIE Lab (D65), ΔE2000
# ---------------------------------------------------------------------------

_M = np.array([[0.4124564, 0.3575761, 0.1804375], [0.2126729, 0.7151522, 0.0721750],
               [0.0193339, 0.1191920, 0.9503041]])
_MI = np.linalg.inv(_M)
_WP = np.array([0.95047, 1.0, 1.08883])


def _lin(c):
    c = np.asarray(c, float)
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def _gam(c):
    c = np.asarray(c, float)
    return np.where(c <= 0.0031308, 12.92 * c, 1.055 * np.clip(c, 0, None) ** (1 / 2.4) - 0.055)


def _f(t):
    return np.where(t > (6 / 29) ** 3, np.cbrt(t), t / (3 * (6 / 29) ** 2) + 4 / 29)


def _fi(t):
    return np.where(t > 6 / 29, t ** 3, 3 * (6 / 29) ** 2 * (t - 4 / 29))


def hex2rgb(h):
    h = h.lstrip('#')
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)]) / 255


def rgb2hex(r):
    r = np.clip(np.round(np.asarray(r) * 255), 0, 255).astype(int)
    return '#%02X%02X%02X' % tuple(r)


def rgb2lab(r):
    fx, fy, fz = _f(_M @ _lin(r) / _WP)
    return np.array([116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)])


def lab2rgb(lab):
    L, a, b = lab
    fy = (L + 16) / 116
    return _gam(_MI @ (np.array([_fi(fy + a / 500), _fi(fy), _fi(fy - b / 200)]) * _WP))


def hex2lab(h):
    return rgb2lab(hex2rgb(h))


def lch2lab(L, C, h):
    return np.array([L, C * math.cos(math.radians(h)), C * math.sin(math.radians(h))])


def lab2lch(lab):
    L, a, b = lab
    return float(L), float(math.hypot(a, b)), math.degrees(math.atan2(b, a)) % 360


def in_gamut(lab, eps=1e-6):
    r = lab2rgb(lab)
    return bool(np.all(r >= -eps) and np.all(r <= 1 + eps))


def hsl_l(h):
    r = hex2rgb(h)
    return (r.max() + r.min()) / 2


def de2000(l1, l2):
    """ΔE2000 (Sharma, Wu, Dalal 2005)"""
    L1, a1, b1 = l1
    L2, a2, b2 = l2
    C1, C2 = math.hypot(a1, b1), math.hypot(a2, b2)
    Cb7 = ((C1 + C2) / 2) ** 7
    G = 0.5 * (1 - math.sqrt(Cb7 / (Cb7 + 25 ** 7)))
    a1p, a2p = (1 + G) * a1, (1 + G) * a2
    C1p, C2p = math.hypot(a1p, b1), math.hypot(a2p, b2)
    h1p = math.degrees(math.atan2(b1, a1p)) % 360
    h2p = math.degrees(math.atan2(b2, a2p)) % 360
    dLp, dCp = L2 - L1, C2p - C1p
    if C1p * C2p == 0:
        dh = 0.0
    else:
        dh = h2p - h1p
        dh -= 360 if dh > 180 else (-360 if dh < -180 else 0)
    dHp = 2 * math.sqrt(C1p * C2p) * math.sin(math.radians(dh / 2))
    Lbp, Cbp = (L1 + L2) / 2, (C1p + C2p) / 2
    if C1p * C2p == 0:
        hbp = h1p + h2p
    elif abs(h1p - h2p) <= 180:
        hbp = (h1p + h2p) / 2
    else:
        hbp = (h1p + h2p + 360) / 2 if h1p + h2p < 360 else (h1p + h2p - 360) / 2
    T = (1 - 0.17 * math.cos(math.radians(hbp - 30)) + 0.24 * math.cos(math.radians(2 * hbp))
         + 0.32 * math.cos(math.radians(3 * hbp + 6)) - 0.20 * math.cos(math.radians(4 * hbp - 63)))
    dth = 30 * math.exp(-((hbp - 275) / 25) ** 2)
    Cbp7 = Cbp ** 7
    Rc = 2 * math.sqrt(Cbp7 / (Cbp7 + 25 ** 7))
    Sl = 1 + 0.015 * (Lbp - 50) ** 2 / math.sqrt(20 + (Lbp - 50) ** 2)
    Sc, Sh = 1 + 0.045 * Cbp, 1 + 0.015 * Cbp * T
    Rt = -math.sin(math.radians(2 * dth)) * Rc
    return math.sqrt((dLp / Sl) ** 2 + (dCp / Sc) ** 2 + (dHp / Sh) ** 2 + Rt * (dCp / Sc) * (dHp / Sh))


# ---------------------------------------------------------------------------
# реестр: фракции, стартовые области, семейства
# ---------------------------------------------------------------------------

# HEX — acrylic/ПРОМПТЫ — недостающий арт.md, «Цвета фракций»
FACTIONS = {
    'OW-F-01': ('Островная Империя', '#187830'),
    'OW-F-02': ('Эйркрафт Корпорейшн', '#00C0F0'),
    'OW-F-03': ('Глобал Петролеум', '#D8D800'),
    'OW-F-04': ('Братство Сингулярности', '#F0A800'),
    'OW-F-05': ('Клонэйд Ресёрч', '#C00030'),
    'OW-F-06': ('Moon Systems', '#D8DADE'),
    'OW-F-07': ('Сайнтифик Солюшн', '#BE31AE'),
    'OW-F-08': ('Североамериканский Альянс', '#904818'),
}

# семейство оттенков несоздающей суши: от чьего цвета, диапазон тона h и насыщенности C в LCh
FAMILY = {
    'MR-L5-NAME': ('brown', 'от Североамериканского Альянса: тот же материк'),
    'MR-L5-CAM': ('brown', 'от Североамериканского Альянса: тот же материк'),
    'MR-L3-SAM': ('terra', 'от Альянса к Клонэйд: терракота'),
    'MR-L5-SAMW': ('terra', 'от Альянса к Клонэйд: терракота'),
    'MR-L5-SAME': ('terra', 'от Альянса к Клонэйд: терракота'),
    'MR-L3-AUS': ('green', 'от Островной Империи: сосед через Юг Тихого'),
    'MR-L5-AUS': ('green', 'от Островной Империи: сосед через Юг Тихого'),
    'MR-L5-NZL': ('green', 'от Островной Империи: сосед через Юг Тихого'),
    'MR-R5-SCA': ('mustard', 'от Глобал Петролеум: тот же материк'),
    'MR-R5-ARB': ('ochre', 'от Глобал Петролеум к Клонэйд: охра'),
    'MR-R5-ASIN': ('jade', 'от Эйркрафт, уведён в зелень: суша не должна читаться водой'),
    'MR-R5-AFRE': ('rose', 'от Клонэйд: тот же материк'),
    'MR-SH-ANT': ('grey', 'нейтральный: своей фракции нет'),
}
FAMILIES = {   # (h от, h до), (C от, C до) — в LCh; насыщенность умеренная: яркие только цвета фракций
    'brown': ((45, 75), (20, 45)),
    'terra': ((25, 50), (20, 45)),
    'green': ((110, 155), (15, 40)),
    'mustard': ((85, 110), (20, 55)),
    'ochre': ((60, 90), (20, 45)),
    'jade': ((150, 195), (8, 26)),
    'rose': ((0, 35), (20, 45)),
    'plum': ((315, 350), (18, 40)),
    'asiagreen': ((125, 160), (18, 42)),
    'plumgrey': ((300, 345), (6, 20)),
    'grey': ((0, 360), (0, 7)),
    'ocean': ((215, 275), (15, 40)),   # голубые и синие (Alek 30.09.2026)
}
L_MAX = 76       # потолок L* для любой шкалы: светлее — уже не «тон арт-библии»
PULL = 1.5       # вес притяжения к середине семейства: без него подбор уходит в края тона и насыщенности
AC_GAP = 20      # вопрос 2, «голубой только у Эйркрафт»: океан не ближе ΔE2000 20 к цвету Эйркрафт
QCAP = 22        # качество ребра выше этого не засчитывается: запас контраста не стоит ухода в крайние тона
L_PREF = {'lab': 40, 'hsl': 52}   # L*, к которому тянется несоздающая суша, чтобы не уходить в чёрно-бурое


def load_reg():
    regions = {r['id']: r for r in yaml.safe_load((BOARD / 'regions.yaml').read_text(encoding='utf-8'))['regions']}
    names = {r['baseline_ref']: r['name_ru'] for r in
             yaml.safe_load((BOARD / 'redesign.yaml').read_text(encoding='utf-8'))['regions']}
    glyphs = yaml.safe_load((BOARD / 'glyphs.yaml').read_text(encoding='utf-8'))
    start = {}
    for s in glyphs['start_areas_redesign']:
        for key in ('regions_3p', 'regions_5p'):
            for rid in s.get(key) or []:
                start[rid] = s['faction']
    edges = {}
    for lay in LAYOUTS:
        d = json.loads((BOARD / 'derived' / f'{lay}.json').read_text(encoding='utf-8'))
        edges[lay] = [tuple(sorted(e)) for e in d['edge_list']]
    return regions, names, start, edges


# ---------------------------------------------------------------------------
# варианты: три вопроса Alek
# ---------------------------------------------------------------------------

SCALE = 'hsl'   # SPEC §9 по HSL: (max+min)/2 в 25–55 %, цвета фракций как есть (Alek 30.09.2026)

# закреплены Alek 30.09.2026 — вне §9 намеренно
PINNED = {
    'MR-OC-ARC': ('#D6E8F0', 'Alek: очень светло-голубой, белёсый'),
    'MR-SH-ANT': ('#F4F4F1', 'Alek: белая'),
}
NOT_FACTION = {   # стартовые области, которые цвет фракции не берут (Alek 30.09.2026)
    'MR-OC-SPAC': 'океан, как все: зелёная вода не читается',
    'MR-R3-ASI': 'Эйркрафт отступил: голубая суша у воды читается водой',
    'MR-R5-ASIS': 'Эйркрафт отступил: голубая суша у воды читается водой',
}
ASIA = {   # вопрос: во что перекрасить Азию; Северная Азия — в другое семейство
    'plum': ('Азия сливовая', {'MR-R3-ASI': 'plum', 'MR-R5-ASIS': 'plum', 'MR-R5-ASIN': 'jade'}),
    'green': ('Азия зелёная', {'MR-R3-ASI': 'asiagreen', 'MR-R5-ASIS': 'asiagreen', 'MR-R5-ASIN': 'plumgrey'}),
}
FAMILY_RU = {'plum': 'сливовый: тон, которого нет ни у материков, ни у воды',
             'asiagreen': 'зелёный: тон, которого нет у соседей Азии',
             'jade': 'серо-зелёный: тайга',
             'plumgrey': 'серо-лиловый: от Азии'}
L_RANGE = {'OCEAN': (30, 72), 'LAND': (35, 72)}   # L*: без чёрно-бурых пятен и без белёсого (кроме PINNED)


def variants():
    return [f'asia-{k}' for k in ASIA]


def fits_scale(lab, scale, typ='LAND'):
    lo, hi = L_RANGE[typ]
    if not lo <= lab[0] <= hi:
        return False
    if scale == 'lab':
        return 25 - 1e-6 <= lab[0] <= 55 + 1e-6
    l = hsl_l(rgb2hex(lab2rgb(lab)))
    return 0.25 <= l <= 0.55


def faction_lab(fid, scale):
    """цвет фракции в шкале: HSL — как есть; L* — тот же тон, L* в 25–55, C до края охвата"""
    lab = hex2lab(FACTIONS[fid][1])
    if scale == 'hsl':
        return lab
    L, C, h = lab2lch(lab)
    L2 = min(max(L, 25), 55)
    if L2 == L:
        return lab
    c = C
    while c > 0 and not in_gamut(lch2lab(L2, c, h)):
        c -= 0.25
    return lch2lab(L2, c, h)


def candidates(fam, scale, avoid=None, typ='LAND'):
    (h0, h1), (c0, c1) = FAMILIES[fam]
    out = []
    hs = [0] if fam == 'grey' else np.arange(h0, h1 + 0.1, 3)
    for L in np.arange(25, 83, 1.5):
        for h in hs:
            for C in np.arange(c0, c1 + 0.1, 3):
                lab = lch2lab(L, C, h)
                if in_gamut(lab) and fits_scale(lab, scale, typ):
                    h8 = rgb2hex(lab2rgb(lab))
                    if avoid is not None and de2000(hex2lab(h8), avoid) < AC_GAP:
                        continue
                    pen = 0.0 if fam == 'grey' else (abs(h - (h0 + h1) / 2) / (h1 - h0) + abs(C - (c0 + c1) / 2) / (c1 - c0))
                    if fam != 'ocean':
                        pen += abs(L - L_PREF[scale]) / 30
                    out.append((h8, hex2lab(h8), pen))
    return out


# ---------------------------------------------------------------------------
# контраст ребра и подбор
# ---------------------------------------------------------------------------

W = {'oo': 1.2, 'll': 0.9, 'ol': 0.6,   # вес требования: океан — океан строже всех (там нет линии)
     'dd': 0.35}                          # несмежные океаны: не один и тот же цвет — «голубые, синие, морской волны»


def kind(a, b, regions):
    ta, tb = regions[a]['type'], regions[b]['type']
    return 'oo' if ta == tb == 'OCEAN' else ('ll' if ta == tb == 'LAND' else 'ol')


def quality(la, lb, k):
    dL, dE = abs(la[0] - lb[0]), de2000(la, lb)
    q = {'oo': 1.4 * dL + 0.1 * dE, 'll': 1.0 * dL + 0.3 * dE, 'ol': dE, 'dd': dE}[k]
    return q / W[k], dL, dE


def solve(variant, seed=20260930, steps=40000, restarts=6):
    asia = ASIA[variant.split('-', 1)[1]][1]
    scale = SCALE
    regions, names, start, edges = load_reg()
    areas = sorted(regions)
    fixed = {rid: (h, hex2lab(h), 0.0) for rid, (h, _) in PINNED.items()}
    for rid, fid in start.items():
        if rid in NOT_FACTION:
            continue
        lab = faction_lab(fid, scale)
        fixed[rid] = (rgb2hex(lab2rgb(lab)), lab, 0.0)
    cands = {}
    for rid in areas:
        if rid in fixed:
            continue
        typ = regions[rid]['type']
        fam = 'ocean' if typ == 'OCEAN' else asia.get(rid, FAMILY.get(rid, (None,))[0])
        cands[rid] = candidates(fam, scale, None, typ)
    E = sorted({e for lay in LAYOUTS for e in edges[lay]})
    K = {e: kind(*e, regions) for e in E}
    oce = sorted(r for r in areas if regions[r]['type'] == 'OCEAN')
    for i, a in enumerate(oce):
        for b in oce[i + 1:]:
            if (a, b) not in K:
                E.append((a, b))
                K[(a, b)] = 'dd'
    inc = {rid: [e for e in E if rid in e] for rid in areas}
    free = sorted(cands)
    tau = 2.0

    memo = {}

    def edge_q(col, e):
        key = (col[e[0]][0], col[e[1]][0], K[e])
        if key not in memo:
            memo[key] = min(QCAP, quality(col[e[0]][1], col[e[1]][1], K[e])[0])
        return memo[key]

    def score(qs, col):
        m = min(qs.values())
        pen = sum(col[r][2] for r in free) / len(free)
        return m - tau * math.log(sum(math.exp(-(q - m) / tau) for q in qs.values())) - PULL * pen

    best = None
    rnd = random.Random(seed)
    for r in range(restarts):
        col = dict(fixed)
        for rid in free:
            col[rid] = rnd.choice(cands[rid])
        qs = {e: edge_q(col, e) for e in E}
        cur = score(qs, col)
        for i in range(steps):
            T = 3.0 * (0.02 / 3.0) ** (i / steps)
            rid = rnd.choice(free)
            old = col[rid]
            col[rid] = rnd.choice(cands[rid])
            new_q = {e: edge_q(col, e) for e in inc[rid]}
            saved = {e: qs[e] for e in inc[rid]}
            qs.update(new_q)
            s = score(qs, col)
            if s >= cur or rnd.random() < math.exp((s - cur) / T):
                cur = s
            else:
                col[rid] = old
                qs.update(saved)
        if best is None or cur > best[0]:
            best = (cur, {k: v[0] for k, v in col.items()})
    return best[1]


def contrast(pal, regions=None, edges=None):
    """по полотнам: [(ΔL*, ΔE2000, род, a, b)] по возрастанию качества"""
    if regions is None:
        regions, _, _, edges = load_reg()
    out = {}
    for lay in LAYOUTS:
        rows = []
        for a, b in edges[lay]:
            k = kind(a, b, regions)
            q, dL, dE = quality(hex2lab(pal[a]), hex2lab(pal[b]), k)
            rows.append((q, dL, dE, k, a, b))
        out[lay] = sorted(rows)
    return out


# ---------------------------------------------------------------------------
# геометрия страницы: области, территории океанов под размытие, фишки
# ---------------------------------------------------------------------------

CHIP_R = 12.5        # мм: фишка ⌀25 — миниатюра на подставке


def _shapes():
    from shapely.geometry import shape
    R = {}
    for lay in ('MC-5P', 'MC-3P'):
        fc = json.loads((GEO / f'board-{lay}.geojson').read_text(encoding='utf-8'))
        for f in fc['features']:
            R.setdefault(f['properties']['id'], shape(f['geometry']))
    return R


def ocean_territories(R, regions):
    """слой океанов под размытие — тот же, что рисует boardview.py"""
    import boardview as bv
    return bv.ocean_territories({r: g for r, g in R.items() if regions[r]['type'] == 'OCEAN'})


def chips(g):
    """центры фишек ⌀25 в области: жадно по карте расстояний, шаг 26 мм, при нехватке места — теснее"""
    import boardcheck as bc
    D, xs, ys, edge = bc.distance_map(g)
    for s in (26, 24, 22, 20, 18, 16):
        work = D.copy()
        pts = []
        while len(pts) < 8:
            i = int(np.argmax(work))
            iy, ix = divmod(i, work.shape[1])
            if work[iy, ix] < CHIP_R:
                break
            cx, cy = xs[ix], ys[iy]
            pts.append((round(float(cx), 1), round(float(cy), 1)))
            for sx in ((0.0, bc.WRAP, -bc.WRAP) if edge else (0.0,)):
                dx = xs[None, :] - (cx + sx)
                dy = ys[:, None] - cy
                work[dx * dx + dy * dy < s * s] = -1.0
        if len(pts) == 8:
            break
    return pts


# ---------------------------------------------------------------------------
# тестовая страница
# ---------------------------------------------------------------------------

THRESH = {'oo': ('dL', 12.0), 'll': ('dE', 15.0), 'ol': ('dE', 12.0)}   # предложение порога: ниже — слабая пара
WIDTHS = (0, 6, 8, 10)   # мм: ширина перехода 10–90 % между океанами; 0 — строгая линия
KIND_RU = {'oo': 'океан — океан', 'll': 'суша — суша', 'ol': 'океан — суша'}


def side_of(rid, regions):
    return 'S' if regions[rid]['side'] == 'BOTH' else rid[3:5]


def page_data(pals):
    import boardview as bv
    import slice5 as s5
    regions, names, start, edges = load_reg()
    R = _shapes()
    T, mask = ocean_territories(R, regions)
    areas = sorted(R)
    decor = []
    for cont, g in s5.load_decor():
        r5 = s5.decor_region(cont, g)
        d = bv.path_d(g)
        if regions[r5]['side'] == 'BOTH':
            decor.append(('S', r5, d))
        else:
            decor.append((r5[3:5], r5, d))
            decor.append((r5[3] + '3', regions[r5]['parent'], d))
    info = {}
    for rid in areas:
        x, y = bv.node_point(R[rid])
        fam = 'ocean' if regions[rid]['type'] == 'OCEAN' else (FAMILY.get(rid, (None, ''))[0])
        info[rid] = {'name': names[rid], 'side': side_of(rid, regions), 'type': regions[rid]['type'],
                     'd': bv.path_d(R[rid]), 'xy': [round(x, 1), round(y, 1)],
                     'start': rid in start, 'chips': chips(R[rid])}
    why = {}
    for v in pals:
        asia = ASIA[v.split('-', 1)[1]][1]
        w = {}
        for rid in areas:
            if rid in PINNED:
                w[rid] = PINNED[rid][1] + ' — вне §9'
            elif rid in start and rid not in NOT_FACTION:
                w[rid] = 'цвет фракции ' + FACTIONS[start[rid]][0]
            elif regions[rid]['type'] == 'OCEAN':
                w[rid] = 'океан' + (': ' + NOT_FACTION[rid] if rid in NOT_FACTION else '')
            elif rid in asia:
                w[rid] = (NOT_FACTION[rid] + '; ' if rid in NOT_FACTION else '') + FAMILY_RU[asia[rid]]
            else:
                w[rid] = FAMILY[rid][1]
        why[v] = w
    con = {}
    for v, pal in pals.items():
        c = contrast(pal, regions, edges)
        con[v] = {lay: [[a, b, k, round(dL, 1), round(dE, 1)] for q, dL, dE, k, a, b in rows] for lay, rows in c.items()}
    return {
        'areas': info, 'decor': decor,
        'terr': {rid: bv.path_d(g) for rid, g in T.items()}, 'mask': bv.path_d(mask),
        'pals': pals, 'con': con, 'sides': SIDES,
        'factions': [[n, h] for n, h in FACTIONS.values()],
        'lab': {h: [round(float(x), 1) for x in lab2lch(hex2lab(h))] + [round(hsl_l(h) * 100)]
                for pal in pals.values() for h in pal.values()},
        'thresh': THRESH, 'kind_ru': KIND_RU, 'why': why,
    }


def build_test(pals, out):
    import boardcheck as bc
    D = page_data(pals)
    W_, H_ = bc.CANVAS
    X0, Y0, X1, Y1 = bc.RECT
    A = D['areas']
    order = sorted(A, key=lambda r: (A[r]['type'] != 'OCEAN', r))
    oc_flat = ''.join(f'<path data-a="{r}" d="{A[r]["d"]}"><title>{A[r]["name"]}</title></path>'
                      for r in order if A[r]['type'] == 'OCEAN')
    grad = ''.join(f'<path data-a="{r}" d="{d}"/>' for r, d in D['terr'].items())
    land = {s: [] for s in ('S', 'L3', 'L5', 'R3', 'R5')}
    for r in order:
        if A[r]['type'] == 'LAND':
            land[A[r]['side']].append(f'<path data-a="{r}" d="{A[r]["d"]}"><title>{A[r]["name"]}</title></path>')
    dec = {s: [] for s in land}
    for s, r, d in D['decor']:
        dec[s].append(f'<path data-a="{r}" d="{d}"/>')
    sides = ''.join(f'<g class="side" data-side="{s}"><g class="land">{"".join(land[s])}</g>'
                    f'<g class="decor">{"".join(dec[s])}</g></g>' for s in land)
    chips_svg, labels = [], []
    for r in order:
        a = A[r]
        cs = ''.join(f'<circle cx="{x}" cy="{y}" r="{CHIP_R}" fill="{h}"><title>{n} на «{a["name"]}»</title></circle>'
                     for (x, y), (n, h) in zip(a['chips'], D['factions']))
        chips_svg.append(f'<g class="side" data-side="{a["side"]}">{cs}</g>')
        labels.append(f'<text class="side" data-side="{a["side"]}" x="{a["xy"][0]}" y="{a["xy"][1]}">'
                      f'{a["name"]}{" ★" if a["start"] else ""}</text>')
    data = json.dumps({k: D[k] for k in ('pals', 'con', 'sides', 'lab', 'thresh', 'kind_ru', 'why')}, ensure_ascii=False)
    meta = json.dumps({r: {'name': A[r]['name'], 'side': A[r]['side'], 'type': A[r]['type'],
                           'start': A[r]['start']} for r in order}, ensure_ascii=False)
    radios = lambda name, opts, sel: ''.join(
        f'<label><input type="radio" name="{name}" value="{v}"{" checked" if v == sel else ""}> {t}</label>' for v, t in opts)
    html = f'''<!doctype html>
<html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Цвета регионов</title>
<style>
:root{{--bg:#f4f1ea;--fg:#23211d;--mut:#6b665c;--line:#d6d0c4;--card:#fbf9f4;--bad:#b3261e;--ok:#2f7d4a}}
@media (prefers-color-scheme:dark){{:root:not([data-theme=light]){{--bg:#1d1c1a;--fg:#ece8df;--mut:#a39d91;--line:#3a3833;--card:#252421;--bad:#f2867e;--ok:#7fc79a}}}}
body{{margin:0;background:var(--bg);color:var(--fg);font:15px/1.45 system-ui,sans-serif}}
main{{max-width:1600px;margin:0 auto;padding:16px}}
h1{{font-size:20px;margin:0 0 4px}} h2{{font-size:16px;margin:18px 0 8px}} p.sub{{margin:0 0 12px;color:var(--mut)}}
.ctl{{display:grid;grid-template-columns:max-content 1fr;gap:6px 16px;align-items:baseline;margin:0 0 10px;padding:10px 12px;border:1px solid var(--line);border-radius:8px;background:var(--card)}}
.ctl .k{{color:var(--mut);font-weight:600}} .ctl .row{{display:flex;flex-wrap:wrap;gap:4px 18px}}
.ctl label{{display:inline-flex;gap:6px;align-items:center;cursor:pointer}}
svg#map{{width:100%;height:auto;display:block;border-radius:6px}}
#oc-flat path{{stroke:#2c2a26;stroke-width:.35;stroke-linejoin:round}}
.land path{{stroke:#2c2a26;stroke-width:.35;stroke-linejoin:round}}
.decor path{{stroke:#2c2a26;stroke-width:.25}}
#labels text{{font:600 6px system-ui,sans-serif;text-anchor:middle;fill:#111;paint-order:stroke;stroke:#fff;stroke-width:1.6px;stroke-linejoin:round}}
.cols{{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:24px;margin-top:8px}}
@media (max-width:900px){{.cols{{grid-template-columns:1fr}} .ctl{{grid-template-columns:1fr}}}}
table{{border-collapse:collapse;width:100%;font-size:13px}} td,th{{padding:3px 6px;border-bottom:1px solid var(--line);text-align:right;vertical-align:middle}}
td.l,th.l{{text-align:left}} th{{color:var(--mut);font-weight:500}}
.sw{{display:inline-block;width:14px;height:14px;border-radius:3px;vertical-align:-2px;border:1px solid #0003;margin-right:4px}}
tr.weak td{{color:var(--bad);font-weight:600}} .bad{{color:var(--bad)}} .ok{{color:var(--ok)}}
code{{font-size:12.5px}}
</style></head><body><main>
<h1>Цвета регионов — варианты</h1>
<p class="sub">Этап 3 COMP-C-03, шаг 1. Страница собрана <code>board/tools/palette.py test</code>. Геометрия — полотна этапа 2 (<code>D-098</code>), не менялась.
Круг 2: Юг Тихого — океан, Антарктида белая, Ледовитый белёсо-голубой, Азия перекрашена, шкала §9 — HSL, переход 8 мм.</p>
<div class="ctl">
<span class="k">Полотно</span><div class="row">{radios('lay', [(l, l) for l in LAYOUTS], 'MC-5P')}</div>
<span class="k">Азия</span><div class="row">{radios('asia', [(k, t) for k, (t, _) in ASIA.items()], 'plum')}</div>
<span class="k">Граница океанов</span><div class="row">{radios('w', [(str(w), 'строгая линия' if w == 0 else f'переход {w} мм') for w in WIDTHS], '8')}</div>
<span class="k">Показать</span><div class="row"><label><input type="checkbox" id="c-chips"> Фишки поверх: ⌀25 мм, восемь цветов фракций</label>
<label><input type="checkbox" id="c-lab" checked> Имена областей, ★ — стартовая</label>
<label><input type="checkbox" id="c-wrap"> Соседний край (склейка)</label></div>
</div>
<svg id="map" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W_:g} {H_:g}">
<defs>
<filter id="blur" filterUnits="userSpaceOnUse" x="{X0 - 200:g}" y="-60" width="{X1 - X0 + 400:g}" height="{H_ + 120:g}" color-interpolation-filters="sRGB"><feGaussianBlur id="fb" stdDeviation="2"/></filter>
<clipPath id="ocmask"><path d="{D['mask']}"/></clipPath>
<clipPath id="cl"><rect x="{X0 - 120:g}" y="0" width="120" height="{H_:g}"/></clipPath>
<clipPath id="cr"><rect x="{X1:g}" y="0" width="120" height="{H_:g}"/></clipPath>
</defs>
<rect x="-200" width="{W_ + 400:g}" height="{H_:g}" fill="#ece8df"/>
<g id="core">
<g id="oc-flat">{oc_flat}</g>
<g id="oc-grad" clip-path="url(#ocmask)"><g filter="url(#blur)">{grad}</g></g>
{sides}
</g>
<g id="wrap" style="display:none"><g clip-path="url(#cl)" opacity="0.6"><use href="#core" x="{-880:g}"/></g><g clip-path="url(#cr)" opacity="0.6"><use href="#core" x="{880:g}"/></g></g>
<g id="chips" style="display:none">{"".join(chips_svg)}</g>
<g id="labels">{"".join(labels)}</g>
<rect x="{X0:g}" y="{Y0:g}" width="{X1 - X0:g}" height="{Y1 - Y0:g}" fill="none" stroke="#2c2a26" stroke-width="0.4"/>
</svg>
<div class="cols">
<section><h2 id="t-con">Контраст соседей</h2>
<p class="sub">Сверху — самые слабые пары относительно порога. Предложение порога: океан — океан ΔL* ≥ {THRESH['oo'][1]:g} (между океанами нет линии, держит только светлота),
суша — суша ΔE2000 ≥ {THRESH['ll'][1]:g}, океан — суша ΔE2000 ≥ {THRESH['ol'][1]:g} (там строгая линия). Ниже порога — красным.</p>
<table id="con"></table></section>
<section><h2>Палитра варианта</h2>
<p class="sub">L*, C, h — CIE LCh; HSL — светлота (max+min)/2. «§9» — попадает ли область в 25–55 % по HSL.</p>
<table id="pal"></table></section>
</div>
</main>
<script>
const D={data};
const M={meta};
const $=id=>document.getElementById(id);
const val=n=>document.querySelector(`input[name=${{n}}]:checked`).value;
function variant(){{return 'asia-'+val('asia')}}
function apply(){{
  const v=variant(), lay=val('lay'), pal=D.pals[v], w=+val('w'), sd=D.sides[lay];
  document.querySelectorAll('[data-a]').forEach(e=>e.setAttribute('fill',pal[e.dataset.a]));
  document.querySelectorAll('.side').forEach(e=>{{const s=e.dataset.side;e.style.display=(s==='S'||sd.includes(s))?'':'none'}});
  $('oc-grad').style.display=w?'':'none';
  $('oc-flat').style.display=w?'none':'';
  if(w) $('fb').setAttribute('stdDeviation',(w/2.563).toFixed(3));
  const T=D.thresh, marg=r=>(T[r[2]][0]==='dL'?r[3]:r[4])/T[r[2]][1];
  const rows=[...D.con[v][lay]].sort((x,y)=>marg(x)-marg(y));
  let h='<tr><th class="l">Пара</th><th class="l">Род</th><th>ΔL*</th><th>ΔE2000</th></tr>';
  for(const [a,b,k,dL,dE] of rows){{
    const [m,t]=T[k], weak=(m==='dL'?dL:dE)<t;
    h+=`<tr class="${{weak?'weak':''}}"><td class="l"><span class="sw" style="background:${{pal[a]}}"></span>${{M[a].name}} — <span class="sw" style="background:${{pal[b]}}"></span>${{M[b].name}}</td><td class="l">${{D.kind_ru[k]}}</td><td>${{dL.toFixed(1)}}</td><td>${{dE.toFixed(1)}}</td></tr>`;
  }}
  $('con').innerHTML=h;
  $('t-con').textContent=`Контраст соседей — ${{lay}}, ${{rows.length}} рёбер`;
  const sc='hsl';
  let p='<tr><th class="l">Область</th><th class="l">Откуда цвет</th><th>HEX</th><th>L*</th><th>C</th><th>h</th><th>HSL, %</th><th>§9</th></tr>';
  for(const r of Object.keys(M)){{
    const s=M[r].side; if(!(s==='S'||sd.includes(s))) continue;
    const hx=pal[r], [L,C,hh,hl]=D.lab[hx], x=sc==='lab'?L:hl, ok=x>=24.5&&x<=55.5;
    p+=`<tr><td class="l"><span class="sw" style="background:${{hx}}"></span>${{M[r].name}}${{M[r].start?' ★':''}}</td><td class="l">${{D.why[v][r]}}</td><td><code>${{hx}}</code></td><td>${{L.toFixed(0)}}</td><td>${{C.toFixed(0)}}</td><td>${{hh.toFixed(0)}}</td><td>${{hl}}</td><td class="${{ok?'ok':'bad'}}">${{ok?'✓':'✗'}}</td></tr>`;
  }}
  $('pal').innerHTML=p;
}}
document.querySelectorAll('input[type=radio]').forEach(e=>e.onchange=apply);
$('c-chips').onchange=e=>$('chips').style.display=e.target.checked?'':'none';
$('c-lab').onchange=e=>$('labels').style.display=e.target.checked?'':'none';
$('c-wrap').onchange=e=>{{$('wrap').style.display=e.target.checked?'':'none';$('map').setAttribute('viewBox',e.target.checked?'-120 0 {W_ + 240:g} {H_:g}':'0 0 {W_:g} {H_:g}')}};
apply();
</script></body></html>
'''
    Path(out).write_text(html, encoding='utf-8')
    return out


def md_table(pal):
    """контраст по рёбрам всех четырёх раскладок, markdown: по полотну, слабые сверху (по запасу к порогу)"""
    regions, names, start, edges = load_reg()
    c = contrast(pal, regions, edges)
    out = []
    for lay in LAYOUTS:
        rows = []
        for q, dL, dE, k, a, b in c[lay]:
            m, t = THRESH[k]
            x = dL if m == 'dL' else dE
            rows.append((x / t, dL, dE, k, a, b, x < t))
        rows.sort()
        weak = sum(r[6] for r in rows)
        out.append(f'### {lay} — рёбер {len(rows)}, ниже порога {weak}\n')
        out.append('| Пара | Род | ΔL* | ΔE2000 | Порог |')
        out.append('|---|---|---:|---:|---|')
        for r, dL, dE, k, a, b, bad in rows:
            m, t = THRESH[k]
            out.append(f'| {names[a]} — {names[b]} | {KIND_RU[k]} | {dL:.1f} | {dE:.1f} | '
                       f'{"✗" if bad else "✓"} {"ΔL*" if m == "dL" else "ΔE"} ≥ {t:g} |')
        out.append('')
    return '\n'.join(out)


def main(argv):
    if len(argv) >= 3 and argv[1] == 'solve':
        out = Path(argv[2])
        pals = json.loads(out.read_text(encoding='utf-8')) if out.exists() else {}
        for v in argv[3:] or variants():
            pals[v] = solve(v)
            out.write_text(json.dumps(pals, indent=1, ensure_ascii=False), encoding='utf-8')
            print(v, flush=True)
        return 0
    if len(argv) >= 2 and argv[1] == 'table':
        import boardview as bv
        print(md_table(dict(bv.COLOUR)))
        return 0
    if len(argv) >= 3 and argv[1] == 'test':
        pals = json.loads(Path(argv[2]).read_text(encoding='utf-8'))
        print(build_test(pals, GEO / 'palette-test.html'))
        return 0
    print(__doc__)
    return 2


if __name__ == '__main__':
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    sys.exit(main(sys.argv))
