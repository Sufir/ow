"""
boardcheck.py — приёмка игрового поля по вектору (SPEC-BOARD §4–§7, §10; ТЗ-ЭСКИЗ-КАРТЫ §10.1, §10.3).

Читает GeoJSON раскладки в мм полотна и сверяет его с реестром: состав областей,
смежности из edges.yaml, пороги касания и зазора, рабочую площадь U, укладку
фигур, край полотна со склейкой, целостность материков против основы.

Запуск из корня репозитория:
    python3 board/tools/boardcheck.py all --board board/geo/board-MC-5P.geojson
    python3 board/tools/boardcheck.py all --board ... --md out.md --json out.json
    python3 board/tools/boardcheck.py fast --board ...    без укладки фигур (N_*), для быстрых итераций
    python3 board/tools/boardcheck.py selftest            прогон на заведомо плохих входах

Раскладка берётся из --layout, иначе из metadata.layout, иначе из имени файла
board-<раскладка>.geojson. Основа для целостности материков — --base
(по умолчанию board/geo/classic-base.geojson; --base none — не сверять).

Код возврата 1 при любом отказе (FAIL). Предупреждения (WARN) код не меняют.
Зависимости: numpy, shapely, scipy, pyyaml.

Склейка краёв (SPEC-BOARD решение № 18, §7): левый и правый края карты — одна
линия. Смежность через край считается сдвигом геометрии на ±880 мм; U, укладка
фигур и связность рабочей зоны областей у края считаются на развёрнутой
геометрии, чтобы край не работал как граница области.

Ориентация колец по RFC 7946 проверяется в координатах файла как они есть:
внешнее кольцо — положительная площадь по формуле Гаусса (против часовой в осях
x, y), дыры — наоборот. На экране с осью y вниз это выглядит по часовой.
"""
import argparse
import json
import sys
from pathlib import Path

import numpy as np
import shapely
import yaml
from scipy import ndimage
from shapely import affinity
from shapely.geometry import LineString, MultiPolygon, Polygon, box, shape
from shapely.ops import linemerge, unary_union
from shapely.validation import explain_validity, make_valid

ROOT = Path(__file__).resolve().parents[2]
BOARD = ROOT / 'board'

# ---------------------------------------------------------------------------
# пороги — одним блоком, со ссылками
# ---------------------------------------------------------------------------

CANVAS = (900.0, 550.0)
MARGIN = 10.0                                   # SPEC-BOARD §2: технологическое поле
RECT = (MARGIN, MARGIN, CANVAS[0] - MARGIN, CANVAS[1] - MARGIN)
WRAP = RECT[2] - RECT[0]                        # 880 мм: сдвиг склейки краёв

CONTACT_FAIL = 8.0      # мм, SPEC §4.1: касание объявленного ребра короче — отказ
CONTACT_WARN = 25.0     # мм, SPEC §4.1: 8–25 — NARROW
GAP_MIN = 12.0          # мм, SPEC §4.2: зазор несмежных
PART_MIN = 100.0        # мм² = 1 см², ТЗ §10.1: кусков мельче нет
TOP_LAND_MIN = 15.0     # мм, SPEC §7: суша к верхнему краю не ближе
TOL = 0.05              # мм: допуск общей границы
AREA_TOL = 1.0          # мм²: наложение пары / щель — допуск округления координат

# фигуры: ⌀ → (отступ центра от границы при 85 % внутри, шаг укладки ⌀ + 1 мм), SPEC §5.2–§5.3
INF, MAC, ROB = 25, 40, 60
EDGE = {INF: 7.3, MAC: 11.7, ROB: 17.6}
STEP = {d: d + 1.0 for d in EDGE}

# SPEC §6: минимум / норма
U_MIN, U_NORM = 55.0, 85.0
N_MIN = {INF: 10, MAC: 3, ROB: 1}
N_NORM = {INF: 14, MAC: 5, ROB: 2}
N_START = 14            # SPEC §6, §8.3: стартовые области
UA_MIN, UA_NORM = 0.55, 0.65  # U/A — по главному куску области (с наибольшей U); острова в КПД формы не входят
U_MAIN_SHARE = 0.60     # SPEC §6: крупнейший связный кусок U
CONT_TOL = 0.02         # SPEC §3.2: целостность материка, допуск по площади

RES = 0.35              # мм: шаг карты расстояний для укладки (легаси-замер — 0,34)
PAD = 120.0             # мм: запас развёртки через край для карты расстояний

# Кого режет край полотна. SPEC §7, решение № 18: только океаны — Северный
# Ледовитый полосой по верху, Север Тихого и Индийский по два куска.
SEAM_REGIONS = {'MR-OC-ARC', 'MR-OC-NPAC', 'MR-OC-IND'}
TOP_REGIONS = {'MR-OC-ARC'}

# родитель стороны «3» (или сама область, если она на всех полях) -> материк основы
BASE_CONTINENT = {'MR-L3-NAM': 'north_america', 'MR-L3-SAM': 'south_america', 'MR-R3-EUR': 'europe',
                  'MR-R3-ASI': 'asia', 'MR-R3-AFR': 'africa', 'MR-L3-AUS': 'australia',
                  'MR-SH-ANT': 'antarctica'}

# ---------------------------------------------------------------------------
# реестр
# ---------------------------------------------------------------------------


def load_spec(layout):
    """Состав раскладки, рёбра, стартовые области, имена — из реестра board/."""
    d = json.loads((BOARD / 'derived' / f'{layout}.json').read_text(encoding='utf-8'))
    regions = {r['id']: r for r in yaml.safe_load((BOARD / 'regions.yaml').read_text(encoding='utf-8'))['regions']}
    names = {r['baseline_ref']: r['name_ru'] for r in
             yaml.safe_load((BOARD / 'redesign.yaml').read_text(encoding='utf-8'))['regions']}
    glyphs = yaml.safe_load((BOARD / 'glyphs.yaml').read_text(encoding='utf-8'))
    areas = [v['id'] for v in d['vertices']]
    starts = set()
    for s in glyphs['start_areas_redesign']:
        for key in ('regions_3p', 'regions_5p'):
            starts.update(s.get(key) or [])
    return {
        'layout': layout,
        'areas': areas,
        'edges': {frozenset(e) for e in d['edge_list']},
        'starts': starts & set(areas),
        'names': {a: names.get(a, a) for a in areas},
        'type': {a: regions[a]['type'] for a in areas},
        'group': {a: regions[a]['parent'] or a for a in areas},
        'seam': SEAM_REGIONS & set(areas),
        'top': TOP_REGIONS & set(areas),
    }


def load_board(path):
    g = json.loads(Path(path).read_text(encoding='utf-8'))
    return g


# ---------------------------------------------------------------------------
# геометрия-помощники
# ---------------------------------------------------------------------------

def polys(g):
    if g is None or g.is_empty:
        return []
    if g.geom_type == 'Polygon':
        return [g]
    if hasattr(g, 'geoms'):
        return [p for q in g.geoms for p in polys(q)]
    return []


def at_side_edge(g, eps=0.01):
    x0, _, x1, _ = g.bounds
    return x0 <= RECT[0] + eps or x1 >= RECT[2] - eps


def shifts(a, b):
    """сдвиги b, при которых пара может встретиться через край"""
    return (0.0, WRAP, -WRAP) if at_side_edge(a) and at_side_edge(b) else (0.0,)


def unwrap(g, pad=None):
    """область у края вместе с её продолжением за краем; pad — сколько оставить за краем"""
    if not at_side_edge(g):
        return g
    u = unary_union([g, affinity.translate(g, WRAP, 0), affinity.translate(g, -WRAP, 0)])
    if pad is not None:
        u = u.intersection(box(RECT[0] - pad, RECT[1] - 1, RECT[2] + pad, RECT[3] + 1))
    return u


def contact(a, b, ba=None):
    """длина общей границы с учётом склейки краёв"""
    L = 0.0
    for dx in shifts(a, b):
        bb = affinity.translate(b, dx, 0) if dx else b
        if a.distance(bb) > TOL:
            continue
        seg = a.boundary.intersection(bb.buffer(TOL))
        parts = [s for s in getattr(seg, 'geoms', [seg]) if s.geom_type == 'LineString'] + \
                [s for q in getattr(seg, 'geoms', []) if q.geom_type == 'MultiLineString' for s in q.geoms]
        parts = [s for s in parts if not s.is_empty]
        if not parts:
            continue
        seg = linemerge(parts)
        # буфер захватывает по TOL за каждым концом общей границы — вычитается
        L += sum(max(0.0, s.length - 2 * TOL) if not s.is_ring else s.length for s in getattr(seg, 'geoms', [seg]))
    return L


def gap(a, b):
    return min(a.distance(affinity.translate(b, dx, 0) if dx else b) for dx in shifts(a, b))


def edge_intervals(g, x):
    """какие отрезки края x = const занимает область"""
    line = LineString([(x, RECT[1]), (x, RECT[3])])
    return line.intersection(g.buffer(TOL / 2))

# ---------------------------------------------------------------------------
# проверки. Каждая возвращает список (уровень, раздел, текст), уровень: ok / WARN / FAIL
# ---------------------------------------------------------------------------


def check_format(fc, spec):
    out, G = [], {}
    sec = 'формат'
    if fc.get('type') != 'FeatureCollection' or not isinstance(fc.get('features'), list):
        return [('FAIL', sec, 'не FeatureCollection')], G
    seen = {}
    for i, f in enumerate(fc['features']):
        rid = (f.get('properties') or {}).get('id')
        if not rid:
            out.append(('FAIL', sec, f'Feature №{i}: нет properties.id'))
            continue
        if rid in seen:
            out.append(('FAIL', sec, f'{rid}: второй Feature с тем же id — одна область, один Feature'))
            continue
        seen[rid] = f
    ids = set(seen)
    for rid in sorted(ids - set(spec['areas'])):
        out.append(('FAIL', sec, f'{rid}: нет в раскладке {spec["layout"]}'))
    for rid in sorted(set(spec['areas']) - ids):
        out.append(('FAIL', sec, f'{rid} ({spec["names"][rid]}): области нет в файле'))
    for rid, f in seen.items():
        if rid not in spec['names']:
            continue
        try:
            g = shape(f['geometry'])
        except Exception as e:           # noqa: BLE001 — любой мусор в geometry
            out.append(('FAIL', sec, f'{rid}: geometry не читается ({e})'))
            continue
        if g.geom_type not in ('Polygon', 'MultiPolygon'):
            out.append(('FAIL', sec, f'{rid}: {g.geom_type} вместо Polygon/MultiPolygon'))
            continue
        if not g.is_valid:
            out.append(('FAIL', sec, f'{rid}: невалидна по OGC — {explain_validity(g)}'))
            g = make_valid(g)
            g = MultiPolygon(polys(g))
        bad_or = 0
        for p in polys(g):
            if not shapely.is_ccw(p.exterior):
                bad_or += 1
            bad_or += sum(1 for r in p.interiors if shapely.is_ccw(r))
        if bad_or:
            out.append(('FAIL', sec, f'{rid}: {bad_or} колец ориентировано не по RFC 7946'))
        small = [p.area for p in polys(g) if p.area < PART_MIN]
        if small:
            out.append(('FAIL', sec, f'{rid}: {len(small)} кусков мельче 1 см² '
                                     f'({", ".join(f"{a:.0f}" for a in small)} мм²)'))
        x0, y0, x1, y1 = g.bounds
        if x0 < RECT[0] - 0.01 or y0 < RECT[1] - 0.01 or x1 > RECT[2] + 0.01 or y1 > RECT[3] + 0.01:
            out.append(('FAIL', sec, f'{rid}: выходит за прямоугольник карты '
                                     f'({x0:.1f}, {y0:.1f}, {x1:.1f}, {y1:.1f})'))
        G[rid] = g
    # наложения и щели
    keys = sorted(G)
    tree = shapely.STRtree([G[k] for k in keys])
    hits = tree.query(np.array([G[k] for k in keys], dtype=object), predicate='intersects') if keys else [[], []]
    for i, j in zip(*hits):
        if i >= j:
            continue
        a = G[keys[i]].intersection(G[keys[j]]).area
        if a > AREA_TOL:
            out.append(('FAIL', sec, f'{keys[i]} и {keys[j]} налезают друг на друга: {a:.1f} мм²'))
    if G:
        holes = box(*RECT).difference(unary_union(list(G.values())))
        bad = [p for p in polys(holes) if p.area > AREA_TOL]
        if bad:
            c = bad[0].representative_point()
            out.append(('FAIL', sec, f'карта покрыта не полностью: {len(bad)} щелей, {sum(p.area for p in bad):.1f} мм², '
                                     f'первая у ({c.x:.0f}, {c.y:.0f})'))
    if not any(l == 'FAIL' for l, _, _ in out):
        out.append(('ok', sec, f'{len(G)} областей, по Feature на область, OGC-валидно, кольца по RFC 7946, '
                               f'без кусков < 1 см², карта покрыта без щелей и наложений'))
    return out, G


def check_topology(G, spec):
    out, edges_tab, close = [], [], []
    sec = 'смежности'
    keys = sorted(G)
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            req = frozenset((a, b)) in spec['edges']
            L = contact(G[a], G[b])
            if req:
                lvl = 'FAIL' if L < CONTACT_FAIL else 'WARN' if L < CONTACT_WARN else 'ok'
                edges_tab.append((a, b, L, lvl))
                if lvl != 'ok':
                    what = 'нет общей границы' if L < TOL else f'касание {L:.1f} мм'
                    out.append((lvl, sec, f'{spec["names"][a]} — {spec["names"][b]}: {what} '
                                          f'({"< 8, отказ" if lvl == "FAIL" else "8–25, NARROW"})'))
            else:
                d = gap(G[a], G[b])
                if d < GAP_MIN + 8:
                    close.append((a, b, d, L))
                if L > TOL:
                    out.append(('FAIL', sec, f'{spec["names"][a]} — {spec["names"][b]}: лишняя смежность, '
                                             f'касание {L:.1f} мм'))
                elif d < GAP_MIN:
                    out.append(('FAIL', sec, f'{spec["names"][a]} — {spec["names"][b]}: несмежные, зазор {d:.1f} мм (< 12)'))
    n_req = len(spec['edges'])
    n_ok = sum(1 for *_, lvl in edges_tab if lvl != 'FAIL')
    n_all = len(spec['areas'])
    n_pairs = n_all * (n_all - 1) // 2 - n_req
    n_far = (len(keys) * (len(keys) - 1) // 2 - len(edges_tab)
             - sum(1 for a, b, d, L in close if d < GAP_MIN or L > TOL))
    out.append(('ok' if n_ok == n_req else 'FAIL', sec, f'объявленных рёбер с касанием ≥ 8 мм: {n_ok} из {n_req}'))
    out.append(('ok' if n_far == n_pairs else 'FAIL', sec, f'несмежных пар с зазором ≥ 12 мм: {n_far} из {n_pairs}'))
    return out, edges_tab, sorted(close, key=lambda t: t[2])


def check_edges(G, spec):
    """край полотна: кого режет, склейка на одной высоте, полоса Ледовитого"""
    out, sec = [], 'край полотна'
    xl, xr = RECT[0], RECT[2]
    on = {'left': {}, 'right': {}}
    for rid, g in G.items():
        for side, x in (('left', xl), ('right', xr)):
            seg = edge_intervals(g, x)
            if seg.length > 0.5:
                on[side][rid] = seg
    cut = set(on['left']) | set(on['right'])
    for rid in sorted(cut - spec['seam']):
        out.append(('FAIL', sec, f'{spec["names"][rid]}: доходит до бокового края, а режутся краем только '
                                 f'{", ".join(spec["names"][s] for s in sorted(spec["seam"]))}'))
    for rid in sorted(spec['seam'] & set(G)):
        if not (rid in on['left'] and rid in on['right']):
            out.append(('FAIL', sec, f'{spec["names"][rid]}: должна выходить на оба боковых края (решение № 18)'))
    mism = 0.0
    for rid in sorted(set(on['left']) | set(on['right'])):
        l = on['left'].get(rid, LineString())
        r = on['right'].get(rid, LineString())
        l2 = affinity.translate(l, WRAP, 0) if not l.is_empty else l
        d = l2.symmetric_difference(r).length if not (l.is_empty and r.is_empty) else 0.0
        if d > 1.0:
            mism += d
            out.append(('FAIL', sec, f'{spec["names"][rid]}: слева и справа на краю разная высота, расхождение {d:.1f} мм'))
    if spec['top']:
        tl = LineString([(xl, RECT[1]), (xr, RECT[1])])
        for rid, g in G.items():
            if rid not in spec['top'] and tl.intersection(g.buffer(TOL / 2)).length > 0.5:
                out.append(('FAIL', sec, f'{spec["names"][rid]}: доходит до верхнего края — там полоса Ледовитого'))
        land = [g for rid, g in G.items() if spec['type'][rid] != 'OCEAN']
        if land:
            top = min(g.bounds[1] for g in land) - RECT[1]
            out.append(('ok' if top >= TOP_LAND_MIN else 'FAIL', sec,
                        f'суша от верхнего края: {top:.1f} мм (≥ {TOP_LAND_MIN:.0f})'))
    if not any(l == 'FAIL' for l, _, _ in out):
        out.append(('ok', sec, f'боковыми краями режутся только {", ".join(spec["names"][s] for s in sorted(cut))}; '
                               f'границы на левом и правом краю на одной высоте'))
    return out


def check_continents(G, spec, base_path):
    out, sec = [], 'материки'
    if base_path is None:
        return out
    fc = json.loads(Path(base_path).read_text(encoding='utf-8'))
    B = {f['properties']['id']: shape(f['geometry']) for f in fc['features']}
    lakes = unary_union([shape(f['geometry']) for f in fc['features'] if f['properties'].get('type') == 'INLAND_WATER'])
    groups = {}
    for rid in G:
        if spec['type'][rid] != 'OCEAN':
            groups.setdefault(spec['group'][rid], []).append(rid)
    for grp, kids in sorted(groups.items()):
        bid = BASE_CONTINENT.get(grp)
        if bid not in B:
            out.append(('WARN', sec, f'{grp}: нет материка основы для сверки'))
            continue
        u = unary_union([G[k] for k in kids]).difference(lakes)
        d = u.symmetric_difference(B[bid]).area
        rel = d / B[bid].area
        out.append(('ok' if rel <= CONT_TOL else 'FAIL', sec,
                    f'{B[bid].area / 100:.0f} см² {fc_name(fc, bid)}: дети {" + ".join(spec["names"][k] for k in kids)}, '
                    f'расхождение с основой {d / 100:.2f} см² ({rel * 100:.2f} %, допуск 2 %)'))
    oc = [G[r] for r in G if spec['type'][r] == 'OCEAN']
    if oc and 'ocean' in B:
        o = unary_union(oc)
        d = o.symmetric_difference(B['ocean']).area
        out.append(('ok' if d / B['ocean'].area <= CONT_TOL else 'FAIL', sec,
                    f'океаны в сумме = океан основы: расхождение {d / 100:.2f} см²'))
        wet = o.intersection(lakes).area
        out.append(('ok' if wet <= AREA_TOL else 'FAIL', sec,
                    f'озёра не входят в океанские области: {wet:.1f} мм²'))
    return out


def fc_name(fc, bid):
    for f in fc['features']:
        if f['properties']['id'] == bid:
            return f['properties'].get('name_ru', bid)
    return bid

# ---------------------------------------------------------------------------
# метрики области: A, U, U/A, связность U, укладка фигур
# ---------------------------------------------------------------------------


def u_pieces(g):
    """рабочая зона пехотинца: эрозия на 7,3 мм, у края — по развёрнутой геометрии"""
    e = unwrap(g, pad=PAD).buffer(-EDGE[INF])
    return e.intersection(box(*RECT))


def main_share(ug):
    ps = polys(ug)
    if not ps:
        return 0.0
    parent = list(range(len(ps)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i
    right = [i for i, p in enumerate(ps) if p.bounds[2] >= RECT[2] - 0.01]
    left = [i for i, p in enumerate(ps) if p.bounds[0] <= RECT[0] + 0.01]
    for i in right:
        for j in left:
            if ps[i].distance(affinity.translate(ps[j], WRAP, 0)) < 0.02:
                parent[find(i)] = find(j)
    area = {}
    for i, p in enumerate(ps):
        area[find(i)] = area.get(find(i), 0.0) + p.area
    return max(area.values()) / sum(area.values())


def ua_main(g):
    """U/A главного куска (с наибольшей U): острова — декор, в КПД формы не входят (SPEC §6, Alek 30.09.2026)"""
    ps = polys(unwrap(g, pad=PAD)) if at_side_edge(g) else polys(g)
    best = max(ps, key=lambda p: (p.buffer(-EDGE[INF]).area, p.area))
    return best.buffer(-EDGE[INF]).area / best.area if best.area else 0.0


def distance_map(g):
    """карта расстояний до границы области, мм; у края — с развёрнутой геометрией"""
    edge = at_side_edge(g)
    if edge:
        x0, x1 = RECT[0] - PAD, RECT[2] + PAD
        src = unwrap(g, pad=PAD)
    else:
        x0, x1 = g.bounds[0] - 2 * RES, g.bounds[2] + 2 * RES
        src = g
    y0, y1 = g.bounds[1] - 2 * RES, g.bounds[3] + 2 * RES
    xs = np.arange(x0 + RES / 2, x1, RES)
    ys = np.arange(y0 + RES / 2, y1, RES)
    X, Y = np.meshgrid(xs, ys)
    shapely.prepare(src)
    m = shapely.contains_xy(src, X, Y)
    D = ndimage.distance_transform_edt(np.pad(m, 1))[1:-1, 1:-1] * RES - RES / 2
    D[~m] = 0
    if edge:
        keep = (xs >= RECT[0]) & (xs < RECT[2])
        D, xs = D[:, keep], xs[keep]
    return D, xs, ys, edge


def pack(D, xs, ys, edge, d):
    """жадная укладка SPEC §5.3: точка максимума карты расстояний, фигура, гашение ⌀ + 1 мм"""
    work = D.copy()
    r_edge, r_ex = EDGE[d], STEP[d]
    k = int(np.ceil(r_ex / RES)) + 1
    pts = []
    while True:
        i = int(np.argmax(work))
        iy, ix = divmod(i, work.shape[1])
        if work[iy, ix] < r_edge:
            break
        cx, cy = xs[ix], ys[iy]
        pts.append((float(cx), float(cy)))
        for sx in ((0.0, WRAP, -WRAP) if edge else (0.0,)):
            jx = np.searchsorted(xs, cx + sx)
            a, b = max(0, jx - k), min(len(xs), jx + k + 1)
            if a >= b:
                continue
            c, e = max(0, iy - k), min(len(ys), iy + k + 1)
            sub = work[c:e, a:b]
            dx = xs[a:b][None, :] - (cx + sx)
            dy = ys[c:e][:, None] - cy
            sub[dx * dx + dy * dy < r_ex * r_ex] = -1.0
    return pts


def metrics(G, spec, with_pack=True):
    rows = {}
    for rid in spec['areas']:
        if rid not in G:
            continue
        g = G[rid]
        ug = u_pieces(g)
        A, Uv = g.area / 100, ug.area / 100
        row = {'id': rid, 'name': spec['names'][rid], 'type': spec['type'][rid], 'A': A, 'U': Uv,
               'UA': Uv / A if A else 0.0, 'share': main_share(ug), 'parts': len(polys(g)),
               'start': rid in spec['starts'], 'seam': at_side_edge(g), 'UA_main': ua_main(g)}
        if with_pack:
            D, xs, ys, edge = distance_map(g)
            row['incircle'] = 2 * float(D.max())
            for dd in (INF, MAC, ROB):
                pts = pack(D, xs, ys, edge, dd)
                row[f'N{dd}'] = len(pts)
                row[f'P{dd}'] = pts
        rows[rid] = row
    return rows


def grade(row, with_pack=True):
    """уровень по SPEC §6 и список отказов"""
    fails, warns = [], []
    if row['U'] < U_MIN:
        fails.append(f'U {row["U"]:.0f} < {U_MIN:.0f}')
    elif row['U'] < U_NORM:
        warns.append(f'U {row["U"]:.0f} ниже нормы {U_NORM:.0f}')
    if row['UA_main'] < UA_MIN:        # КПД формы — по главному куску: острова — декор (Alek 30.09.2026)
        fails.append(f'U/A {row["UA_main"]:.3f} < {UA_MIN}')
    if row['share'] < U_MAIN_SHARE:
        fails.append(f'рабочая зона разорвана: крупнейший кусок {row["share"] * 100:.0f} % < 60 %')
    if with_pack:
        for dd, nm in ((INF, 'N_пех'), (MAC, 'N_маш'), (ROB, 'N_роб')):
            if row[f'N{dd}'] < N_MIN[dd]:
                fails.append(f'{nm} {row[f"N{dd}"]} < {N_MIN[dd]}' + (' — отказной без исключений' if dd == ROB else ''))
        if row['start'] and row[f'N{INF}'] < N_START:
            fails.append(f'стартовая: N_пех {row[f"N{INF}"]} < {N_START}')
    return fails, warns


def check_metrics(rows, with_pack=True):
    out, sec = [], 'области'
    nf = 0
    for rid, row in rows.items():
        fails, warns = grade(row, with_pack)
        row['fails'], row['warns'] = fails, warns
        if fails:
            nf += 1
            out.append(('FAIL', sec, f'{row["name"]}: ' + '; '.join(fails)))
        elif warns:
            out.append(('WARN', sec, f'{row["name"]}: ' + '; '.join(warns)))
    out.append(('ok' if nf == 0 else 'FAIL', sec, f'областей без отказов по SPEC §6: {len(rows) - nf} из {len(rows)}'))
    return out

# ---------------------------------------------------------------------------
# прогон и вывод
# ---------------------------------------------------------------------------


def run(fc, spec, base=None, with_pack=True):
    res, G = check_format(fc, spec)
    topo, edges_tab, close = check_topology(G, spec)
    res += topo
    res += check_edges(G, spec)
    if base is not None:
        res += check_continents(G, spec, base)
    rows = metrics(G, spec, with_pack)
    res += check_metrics(rows, with_pack)
    return {'results': res, 'rows': rows, 'edges': edges_tab, 'close': close, 'G': G}


def print_results(r):
    for lvl, sec, t in r['results']:
        print(f'{"  ok" if lvl == "ok" else lvl:>4}  [{sec}] {t}')
    nf = sum(1 for l, _, _ in r['results'] if l == 'FAIL')
    nw = sum(1 for l, _, _ in r['results'] if l == 'WARN')
    print(f'\nИтог: отказов {nf}, предупреждений {nw} — {"ЗЕЛЁНОЕ" if nf == 0 else "НЕ ПРИНЯТО"}')
    return nf


def md_table(r, spec, with_pack=True):
    L = ['| Область | A, см² | U, см² | U/A всей | U/A (главный кусок) | N_пех | N_маш | N_роб | ⌀ впис., мм | U одним куском | Вердикт |',
         '|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|']
    for rid in spec['areas']:
        row = r['rows'].get(rid)
        if not row:
            continue
        v = '✗ ' + '; '.join(row['fails']) if row['fails'] else ('△ ' + '; '.join(row['warns']) if row['warns'] else '✓')
        star = ' ★' if row['start'] else ''
        n = (f'{row[f"N{INF}"]} | {row[f"N{MAC}"]} | {row[f"N{ROB}"]} | {row["incircle"]:.0f}' if with_pack
             else '— | — | — | —')
        L.append(f'| {row["name"]}{star} | {row["A"]:.0f} | {row["U"]:.0f} | {row["UA"]:.3f} | {row["UA_main"]:.3f} | {n} | '
                 f'{row["share"] * 100:.0f} % | {v} |')
    L += ['', '★ — стартовая область, N_пех ≥ 14.', '', '| Ребро | Касание, мм | |', '|---|---:|---|']
    for a, b, Lc, lvl in sorted(r['edges'], key=lambda t: t[2]):
        L.append(f'| {spec["names"][a]} — {spec["names"][b]} | {Lc:.1f} | '
                 f'{"✗" if lvl == "FAIL" else "△ NARROW" if lvl == "WARN" else "✓"} |')
    L += ['', 'Самые тесные несмежные пары (порог 12 мм):', '', '| Пара | Зазор, мм |', '|---|---:|']
    for a, b, d, Lc in r['close'][:12]:
        L.append(f'| {spec["names"][a]} — {spec["names"][b]} | {d:.1f}{" ✗" if d < GAP_MIN else ""} |')
    return '\n'.join(L) + '\n'


def json_out(r):
    rows = {k: {kk: vv for kk, vv in v.items() if not kk.startswith('P')} for k, v in r['rows'].items()}
    pos = {k: {f'P{d}': v.get(f'P{d}', []) for d in (INF, MAC, ROB)} for k, v in r['rows'].items()}
    return {'results': [{'level': l, 'section': s, 'text': t} for l, s, t in r['results']],
            'regions': rows, 'placements': pos,
            'edges': [{'a': a, 'b': b, 'contact_mm': round(L, 2), 'level': lvl} for a, b, L, lvl in r['edges']],
            'closest_nonadjacent': [{'a': a, 'b': b, 'gap_mm': round(d, 2)} for a, b, d, _ in r['close']]}


def detect_layout(fc, path):
    lay = (fc.get('metadata') or {}).get('layout')
    if lay:
        return lay
    stem = Path(path).stem
    return stem[len('board-'):] if stem.startswith('board-') else None

# ---------------------------------------------------------------------------
# selftest: заведомо плохие входы должны давать отказ, хороший — проходить
# ---------------------------------------------------------------------------


def _fc(geoms):
    feats = []
    for rid, g in geoms.items():
        feats.append({'type': 'Feature', 'properties': {'id': rid},
                      'geometry': shapely.geometry.mapping(shapely.geometry.polygon.orient(g, 1.0)
                                                           if g.geom_type == 'Polygon' else
                                                           MultiPolygon([shapely.geometry.polygon.orient(p, 1.0)
                                                                         for p in g.geoms]))})
    return json.loads(json.dumps({'type': 'FeatureCollection', 'features': feats}))


def _mini():
    """Мини-раскладка на полном прямоугольнике карты, которая обязана пройти всё:
    T — полоса по верху (режется краем), O — полоса по низу (режется краем),
    S — средний пояс двумя кусками у краёв, P — середина. Смежности: все пары,
    кроме T—O."""
    x0, y0, x1, y1 = RECT
    T = box(x0, y0, x1, 110)
    O = box(x0, 440, x1, y1)
    S = MultiPolygon([box(x0, 110, 100, 440), box(800, 110, x1, 440)])
    P = box(100, 110, 800, 440)
    geoms = {'T': T, 'O': O, 'S': S, 'P': P}
    ids = list(geoms)
    spec = {'layout': 'TEST', 'areas': ids,
            'edges': {frozenset(p) for p in [('T', 'S'), ('T', 'P'), ('O', 'S'), ('O', 'P'), ('S', 'P')]},
            'starts': {'P'}, 'names': {k: k for k in ids}, 'type': {k: 'OCEAN' for k in ids},
            'group': {k: k for k in ids}, 'seam': {'T', 'O', 'S'}, 'top': {'T'}}
    return geoms, spec


def _add(s, rid, typ='LAND', edges=(), start=False):
    """добавить в мини-спецификацию область rid со смежностями edges"""
    s['areas'] = s['areas'] + [rid]
    s['names'] = {**s['names'], rid: rid}
    s['type'] = {**s['type'], rid: typ}
    s['group'] = {**s['group'], rid: rid}
    s['edges'] = s['edges'] | {frozenset((rid, e)) for e in edges}
    if start:
        s['starts'] = {rid}


def selftest():
    base, spec = _mini()
    x0, y0, x1, y1 = RECT
    P0 = base['P']
    cases = []

    def case(name, expect, geoms=None, spec_fn=None, cw=False):
        g = dict(base)
        g.update(geoms or {})
        g = {k: v for k, v in g.items() if v is not None}
        s = {k: (set(v) if isinstance(v, set) else v) for k, v in spec.items()}
        if spec_fn:
            spec_fn(s)
        fc = _fc(g)
        if cw:
            f = next(f for f in fc['features'] if f['properties']['id'] == 'P')
            f['geometry']['coordinates'][0].reverse()
        cases.append((name, fc, s, expect))

    case('исходная мини-раскладка проходит', None)
    case('области нет в файле', 'области нет в файле', {'P': None})
    case('чужой id', 'нет в раскладке', {'P': None, 'Q': P0})
    case('наложение', 'налезают', {'P': box(90, 110, 800, 440)})
    case('щель', 'щелей', {'P': box(100, 110, 795, 440)})
    hole = box(400, 200, 408, 208)
    case('кусок мельче 1 см²', 'мельче 1 см²', {'P': P0.difference(hole), 'Q': hole},
         lambda s: _add(s, 'Q', edges=['P']))
    case('невалидный полигон', 'невалидна',
         {'P': Polygon([(100, 110), (800, 440), (800, 110), (100, 440)])})
    case('кольцо по часовой', 'не по RFC 7946', cw=True)
    case('объявленное ребро без касания', 'нет общей границы',
         spec_fn=lambda s: s.update(edges=s['edges'] | {frozenset(('T', 'O'))}))
    case('лишняя смежность', 'лишняя смежность',
         spec_fn=lambda s: s.update(edges=s['edges'] - {frozenset(('S', 'P'))}))
    bite = box(100, 110, 795, 150)          # T и P касаются только на 5 мм у правого конца
    case('касание 5 мм', 'касание 5.0 мм', {'P': P0.difference(bite), 'S': unary_union([base['S'], bite])})
    bite = box(100, 110, 785, 150)
    case('касание 15 мм — предупреждение, не отказ', None,
         {'P': P0.difference(bite), 'S': unary_union([base['S'], bite])})
    # несмежные P и O разведены полосой Z толщиной 6 мм
    case('зазор несмежных 6 мм', 'зазор 6.0 мм',
         {'P': box(100, 110, 800, 300), 'Z': box(100, 300, 800, 306),
          'O': unary_union([box(100, 306, 800, 440), box(x0, 440, x1, y1)])},
         lambda s: (_add(s, 'Z', 'OCEAN', ['P', 'O', 'S']), s.update(edges=s['edges'] - {frozenset(('O', 'P'))})))
    case('суша на боковом краю', 'доходит до бокового края', spec_fn=lambda s: s.update(seam=s['seam'] - {'S'}))
    case('склейка на разной высоте', 'разная высота',
         {'S': MultiPolygon([box(x0, 110, 100, 440), box(800, 120, x1, 440)]),
          'T': unary_union([base['T'], box(800, 110, x1, 120)])})
    small = box(300, 200, 330, 230)
    case('робот не встаёт', 'N_роб 0 < 1', {'P': P0.difference(small), 'R': small},
         lambda s: _add(s, 'R', edges=['P']))
    dumb = unary_union([box(300, 150, 420, 400), box(420, 270, 600, 280), box(600, 150, 720, 400)])
    case('гантель: рабочая зона распадается', 'рабочая зона разорвана', {'P': P0.difference(dumb), 'R': dumb},
         lambda s: _add(s, 'R', edges=['P']))
    st = box(300, 200, 400, 260)
    case('стартовая: мало пехоты', 'стартовая: N_пех', {'P': P0.difference(st), 'R': st},
         lambda s: _add(s, 'R', edges=['P'], start=True))
    top = box(300, 20, 400, 110)
    case('суша у верхнего края', 'от верхнего края', {'P': P0, 'T': base['T'].difference(top), 'R': top},
         lambda s: _add(s, 'R', edges=['P', 'T']))
    ok_all = True
    for name, fc, s, expect in cases:
        r = run(fc, s, base=None, with_pack=True)
        fails = [t for l, _, t in r['results'] if l == 'FAIL']
        if expect is None:
            good = not fails
            why = '; '.join(fails[:3]) if fails else 'отказов нет'
        else:
            hit = [t for t in fails if expect in t]
            good = bool(hit)
            why = hit[0] if hit else f'ожидался отказ «{expect}», получено: ' + ('; '.join(fails[:3]) or 'ничего')
        ok_all &= good
        print(f'{"  ok" if good else "FAIL"}  {name}: {why}')
    # склейка: касание через край и связность рабочей зоны через край
    left, right = box(x0, 110, 100, 440), box(800, 110, x1, 440)
    L = contact(left, right)
    good = abs(L - 330) < 1
    ok_all &= good
    print(f'{"  ok" if good else "FAIL"}  склейка: касание через край {L:.1f} мм (ждали 330)')
    sh = main_share(u_pieces(base['S']))
    good = sh > 0.999
    ok_all &= good
    print(f'{"  ok" if good else "FAIL"}  склейка: рабочая зона S из двух кусков у краёв — один кусок ({sh * 100:.0f} %)')
    print('\nselftest: ' + ('все случаи пойманы' if ok_all else 'ЕСТЬ ПРОПУСКИ'))
    return 0 if ok_all else 1


def main(argv):
    ap = argparse.ArgumentParser(description='приёмка поля по вектору')
    ap.add_argument('cmd', choices=['all', 'fast', 'selftest'])
    ap.add_argument('--board')
    ap.add_argument('--layout')
    ap.add_argument('--base', default=str(BOARD / 'geo' / 'classic-base.geojson'))
    ap.add_argument('--md')
    ap.add_argument('--json')
    a = ap.parse_args(argv[1:])
    if a.cmd == 'selftest':
        return selftest()
    if not a.board:
        ap.error('нужен --board')
    fc = load_board(a.board)
    lay = a.layout or detect_layout(fc, a.board)
    if not lay:
        ap.error('раскладка не определилась: --layout MC-5P')
    spec = load_spec(lay)
    base = None if a.base in ('none', '') else a.base
    with_pack = a.cmd == 'all'
    print(f'boardcheck: {a.board}, раскладка {lay}, основа {base or "—"}\n')
    r = run(fc, spec, base, with_pack)
    nf = print_results(r)
    if a.md:
        Path(a.md).write_text(md_table(r, spec, with_pack), encoding='utf-8')
    if a.json:
        Path(a.json).write_text(json.dumps(json_out(r), ensure_ascii=False, indent=1), encoding='utf-8')
    return 1 if nf else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
