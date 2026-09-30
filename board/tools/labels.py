"""
labels.py — подписи областей на полотне: где стоит имя, каким кеглем, на какой плашке.

Этап 3 компонента COMP-C-03 (D-101). Выбор Alek 30.09.2026:
  - OpenGostTypeB, строчные, белые с тёмной обводкой; суша 8 мм, океаны 10 мм;
  - океаны — на прямой плашке серо-зелёного цвета, суша — без плашки;
  - разрезанные краем океаны (Ледовитый, Север Тихого, Индийский) подписаны у каждого края,
    на плашке-стрелке, остриё — к краю: океан продолжается с другой стороны. Где тесно —
    кегль меньше, до 6 мм, потом переносы.

Подпись не пересекает границу области и не ложится на острова-декор (SPEC-BOARD §8.4): перебор
точек области от самой далёкой от границы и переносов строк, берётся первое место, где рамка
подписи с полем целиком внутри области. Ширина строки — по метрикам шрифта (fontTools).

Модуль вызывает boardview.py при сборке полотен (slice5.py, glue.py); сам по себе:
    python3 board/tools/labels.py check     расстановка на всех четырёх полотнах, что не поместилось
Зависимости: numpy, shapely, fontTools (+ boardcheck.py рядом).
"""
import json
import sys
from functools import lru_cache
from pathlib import Path

import numpy as np
import shapely
from shapely.geometry import LineString, Polygon, box
from shapely.ops import unary_union

sys.path.insert(0, str(Path(__file__).resolve().parent))
import boardcheck as bc  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
FONT_FILE = ROOT / 'print' / 'Fonts' / 'OpenGostTypeB.ttf'
FONT = 'OpenGostTypeB'
FONT_URL = '../../print/Fonts/OpenGostTypeB.ttf'     # от board/geo/
LAND_MM, OCEAN_MM, MIN_MM = 8.0, 10.0, 6.0          # кегль, мм полотна; у разреза — не мельче MIN_MM
LINE = 1.08                                          # межстрочный, в кеглях
TEXT_FILL, TEXT_LINE = '#ffffff', '#1c1a17'          # белый с тёмной обводкой 0,16 кегля
PLATE, PLATE_LINE = '#6E7F7A', '#4B5854'             # плашка океанов: серо-зелёная, матовая (Alek)
PAD_LAND, PAD_PLATE = 1.5, 1.0                       # мм: поле от рамки подписи / плашки до границы
CUT = tuple(sorted(bc.SEAM_REGIONS))                 # океаны, разрезанные краем
GAP_EDGE = 2.5                                       # мм: остриё плашки не доходит до края


@lru_cache(None)
def _metrics():
    from fontTools.ttLib import TTFont
    t = TTFont(str(FONT_FILE))
    upm = t['head'].unitsPerEm
    cmap, hmtx = t.getBestCmap(), t['hmtx']
    adv = {c: hmtx[g][0] / upm for c, g in cmap.items()}
    return adv, t['hhea'].ascent / upm, -t['hhea'].descent / upm


def width(s, fs):
    adv, _, _ = _metrics()
    return sum(adv.get(ord(c), 0.5) for c in s) * fs


def bbox(lines, fs, anchor):
    """рамка текста в своих координатах: первая базовая линия — y = 0, якорь — x = 0"""
    _, asc, desc = _metrics()
    w = max(width(s, fs) for s in lines)
    x0 = {'middle': -w / 2, 'start': 0.0, 'end': -w}[anchor]
    return x0, -asc * fs, x0 + w, (len(lines) - 1) * fs * LINE + desc * fs


def splits(name):
    """имя в одну строку, в две и в три — переносы по словам, самые ровные"""
    w = name.split(' ')
    out = [[name]]
    if len(w) >= 2:
        out.append(min(([' '.join(w[:i]), ' '.join(w[i:])] for i in range(1, len(w))), key=lambda l: max(map(len, l))))
    if len(w) >= 3:
        out.append(min(([' '.join(w[:i]), ' '.join(w[i:j]), ' '.join(w[j:])]
                        for i in range(1, len(w) - 1) for j in range(i + 1, len(w))), key=lambda l: max(map(len, l))))
    return out


def candidates(g, step=4.0, keep=250):
    """точки внутри области по убыванию расстояния до границы"""
    x0, y0, x1, y1 = g.bounds
    xs, ys = np.meshgrid(np.arange(x0 + step / 2, x1, step), np.arange(y0 + step / 2, y1, step))
    X, Y = xs.ravel(), ys.ravel()
    shapely.prepare(g)
    m = shapely.contains_xy(g, X, Y)
    X, Y = X[m], Y[m]
    d = shapely.distance(shapely.points(X, Y), g.boundary)
    o = np.argsort(-d)[:keep]
    return [(float(X[i]), float(Y[i])) for i in o]


def arrow_spots(R):
    """у каждого края в полосе каждого разрезанного океана — высота, где от края дальше всего
    чистая вода, ближе к середине полосы"""
    X0, Y0, X1, Y1 = bc.RECT
    out = []
    for rid in CUT:
        g = R[rid]
        for side, x, sgn in (('L', X0 + 0.01, 1), ('R', X1 - 0.01, -1)):
            iv = bc.edge_intervals(g, x)
            for seg in ([iv] if iv.geom_type == 'LineString' else list(getattr(iv, 'geoms', []))):
                if seg.length < 20:
                    continue
                ya, yb = sorted([seg.coords[0][1], seg.coords[-1][1]])
                mid, best = (ya + yb) / 2, None
                for y in np.arange(ya + 8, yb - 8, 1.0):
                    ray = LineString([(x, y), (x + sgn * 70, y)]).intersection(g)
                    run = 0.0
                    for piece in ([ray] if ray.geom_type == 'LineString' else list(getattr(ray, 'geoms', []))):
                        if not piece.is_empty and min(abs(c[0] - x) for c in piece.coords) < 0.5:
                            run = max(run, piece.length)
                    sc = min(run, 45) - 0.15 * abs(y - mid)
                    if best is None or sc > best[0]:
                        best = (sc, y)
                if best:
                    out.append({'id': rid, 'side': side, 'y': float(best[1]), 'band': (ya, yb)})
    return out


def _fits(g, dec, b, pad):
    r = box(b[0] - pad, b[1] - pad, b[2] + pad, b[3] + pad)
    return g.contains(r) and (dec is None or r.disjoint(dec))


def place_central(rid, g, name, ocean, dec):
    fs = OCEAN_MM if ocean else LAND_MM
    px, py = (fs * 0.35, fs * 0.31) if ocean else (0.0, 0.0)
    pad = PAD_PLATE if ocean else PAD_LAND
    cand = candidates(g)
    best = None
    for li, lines in enumerate(splits(name)):
        x0, y0, x1, y1 = bbox(lines, fs, 'middle')
        for k, (cx, cy) in enumerate(cand):
            if best and k + 4 * li >= best[0]:
                break
            dy = cy - (y0 + y1) / 2
            pb = (cx + x0 - px, y0 + dy - py, cx + x1 + px, y1 + dy + py)
            if _fits(g, dec, pb, pad):
                best = (k + 4 * li, dict(id=rid, lines=lines, fs=fs, x=cx, y=dy, anchor='middle',
                                         plate=('rect', pb) if ocean else None))
                break
    return best[1] if best else None


def place_edge(a, g, name, dec):
    X0, Y0, X1, Y1 = bc.RECT
    L = a['side'] == 'L'
    s, xe = (-1, X0) if L else (1, X1)
    tries = sorted(((OCEAN_MM - fs) + 2 * li, li, -fs, lines)
                   for li, lines in enumerate(splits(name)) for fs in np.arange(OCEAN_MM, MIN_MM - 0.01, -1.0))
    ys = [a['y'] + d for dd in range(0, 61, 2) for d in ((dd, -dd) if dd else (0,))]
    for _, _, nfs, lines in tries:
        fs = -nfs
        anchor = 'start' if L else 'end'
        x0, y0, x1, y1 = bbox(lines, fs, anchor)
        hb = fs * 0.62
        tip = (y1 - y0 + hb) * 0.45
        xt = xe - s * (GAP_EDGE + tip + fs * 0.35)
        for yc in ys:
            dy = yc - (y0 + y1) / 2
            bt = (xt + x0, y0 + dy, xt + x1, y1 + dy)
            bx = ((xe + GAP_EDGE, bt[1] - hb / 2, bt[2] + fs * 0.35, bt[3] + hb / 2) if L else
                  (bt[0] - fs * 0.35, bt[1] - hb / 2, xe - GAP_EDGE, bt[3] + hb / 2))
            if bx[1] < a['band'][0] + 1 or bx[3] > a['band'][1] - 1:
                continue
            if not _fits(g, dec, bx, 1.2):
                continue
            far = bt[2] if L else bt[0]
            near = xe - s * GAP_EDGE
            xf, xb = far - s * fs * 0.35, near - s * tip
            ya, yb = bt[1] - hb / 2, bt[3] + hb / 2
            poly = [(xf, ya), (xb, ya), (near, (ya + yb) / 2), (xb, yb), (xf, yb)]
            return dict(id=a['id'], lines=lines, fs=float(fs), x=xt, y=dy, anchor=anchor, plate=('poly', poly))
    return None


def place(R, spec, decor=()):
    """подписи полотна: [dict(id, lines, fs, x, y — первая базовая линия, anchor, plate)], [не поместились]"""
    dec = unary_union([g.buffer(1.0) for _, g in decor]) if decor else None
    out, miss = [], []
    for a in arrow_spots({r: R[r] for r in CUT if r in R}):
        p = place_edge(a, R[a['id']], spec['names'][a['id']], dec)
        (out.append(p) if p else miss.append(f"{spec['names'][a['id']]} ({'левый' if a['side'] == 'L' else 'правый'} край)"))
    for rid in spec['areas']:
        if rid in CUT:
            continue
        p = place_central(rid, R[rid], spec['names'][rid], spec['type'][rid] == 'OCEAN', dec)
        (out.append(p) if p else miss.append(spec['names'][rid]))
    return out, miss


def font_css():
    return f"@font-face{{font-family:'{FONT}';src:url('{FONT_URL}') format('truetype')}}"


def svg_layer(labels):
    """слой подписей: плашка, потом текст с обводкой"""
    out = []
    for p in labels:
        fs = p['fs']
        plate = ''
        if p['plate']:
            kind, geo = p['plate']
            if kind == 'rect':
                x0, y0, x1, y1 = geo
                plate = (f'<rect x="{x0:.2f}" y="{y0:.2f}" width="{x1 - x0:.2f}" height="{y1 - y0:.2f}" '
                         f'fill="{PLATE}" stroke="{PLATE_LINE}" stroke-width="0.4"/>')
            else:
                plate = (f'<path d="M' + ' L'.join(f'{x:.2f},{y:.2f}' for x, y in geo) + f'Z" fill="{PLATE}" '
                         f'stroke="{PLATE_LINE}" stroke-width="0.4" stroke-linejoin="round"/>')
        spans = ''.join(f'<tspan x="{p["x"]:.2f}" dy="{0 if i == 0 else fs * LINE:.2f}">{s}</tspan>'
                        for i, s in enumerate(p['lines']))
        out.append(f'<g>{plate}<text x="{p["x"]:.2f}" y="{p["y"]:.2f}" font-family="{FONT}" font-size="{fs:g}" '
                   f'text-anchor="{p["anchor"]}" fill="{TEXT_FILL}" stroke="{TEXT_LINE}" stroke-width="{fs * 0.16:.2f}" '
                   f'paint-order="stroke" stroke-linejoin="round">{spans}</text></g>')
    return ''.join(out)


def main(argv):
    if len(argv) >= 2 and argv[1] == 'check':
        from shapely.geometry import shape
        import slice5 as s5
        bad = 0
        for lay in ('MC-3P', 'MC-4P-A', 'MC-4P-B', 'MC-5P'):
            fc = json.loads((ROOT / 'board' / 'geo' / f'board-{lay}.geojson').read_text(encoding='utf-8'))
            R = {f['properties']['id']: shape(f['geometry']) for f in fc['features']}
            spec = bc.load_spec(lay)
            decor = [(None, g) for _, g in s5.load_decor()]
            labels, miss = place(R, spec, decor)
            small = [f"{spec['names'][p['id']]} {p['fs']:g} мм" for p in labels if p['fs'] < (OCEAN_MM if spec['type'][p['id']] == 'OCEAN' else LAND_MM)]
            print(f'{lay}: подписей {len(labels)}, не поместились: {", ".join(miss) or "нет"}; мельче кегля: {", ".join(small) or "нет"}')
            bad += len(miss)
        return 1 if bad else 0
    print(__doc__)
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv))
