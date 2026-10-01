"""
decor.py — декор игрового поля (этап 3 COMP-C-03, шаг 4, D-104).

Фон под фигурами (шаг 5, D-105) — bg_layer(): тень к краю суши и светлая вода у берега.

Выбор Alek 01.10.2026: береговые линии на воде (три тонкие белые линии вдоль берега,
1,6 / 3,6 / 6,4 мм, бледнее к морю) и рамка со шкалой (риски каждые 10 мм, каждые 50 — длиннее).
Отвергнуты: рельеф у берега, техническая сетка, гексы. Рисует boardview.py — svg_layer().

SPEC-BOARD §9: центр области спокойный, детали — к границам и в рукава; мелкого рисунка
под фигурами нет. Поэтому весь декор здесь — у берегов, у краёв и на воде, тонкими линиями.

    python3 board/tools/decor.py test     тестовая страница board/geo/decor-test.html
Зависимости: numpy, shapely (+ boardcheck.py, slice5.py рядом).
"""
import json
import math
import re
import sys
from pathlib import Path

import numpy as np
from shapely.geometry import LineString, MultiLineString, box, shape
from shapely.ops import unary_union

sys.path.insert(0, str(Path(__file__).resolve().parent))
import boardcheck as bc  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
GEO = ROOT / 'board' / 'geo'
LAYOUTS = ('MC-3P', 'MC-4P-A', 'MC-4P-B', 'MC-5P')


def lines_d(g, nd=2):
    out = []
    for ln in getattr(g, 'geoms', [g]):
        if ln.is_empty:
            continue
        if ln.geom_type in ('Polygon', 'MultiPolygon'):
            continue
        if ln.geom_type == 'LinearRing':
            ln = LineString(ln.coords)
        if ln.geom_type != 'LineString':
            continue
        c = np.asarray(ln.coords)
        out.append('M' + ' '.join(f'{x:.{nd}f},{y:.{nd}f}' for x, y in c))
    return ''.join(out)


def bound_lines(g):
    b = g.boundary
    return unary_union([b])


def geometry():
    import slice5 as s5
    fc = json.loads((GEO / 'board-MC-5P.geojson').read_text(encoding='utf-8'))
    R = {f['properties']['id']: shape(f['geometry']) for f in fc['features']}
    land = unary_union([g for r, g in R.items() if '-OC-' not in r])
    decor = unary_union([g for _, g in s5.load_decor()])
    X0, Y0, X1, Y1 = bc.RECT
    rect = box(X0, Y0, X1, Y1)
    allland = unary_union([land, decor])
    ocean = rect.difference(allland)
    out = {}
    # 1. береговые линии на воде: 1,5 / 3,5 / 6 мм от берега (и у островов)
    out['water'] = [lines_d(allland.buffer(d, quad_segs=6).boundary.intersection(ocean).simplify(0.15)) for d in (1.6, 3.6, 6.4)]
    # 2. рельеф у берега: кольца внутри суши 2 и 4,5 мм
    out['relief'] = [lines_d(land.buffer(-d, quad_segs=6).boundary.intersection(rect.buffer(-0.5)).simplify(0.15)) for d in (2.2, 4.8)]
    # 3. техническая сетка 50 мм по воде
    grid = [LineString([(x, Y0), (x, Y1)]) for x in np.arange(X0 + 50, X1, 50)] + \
           [LineString([(X0, y), (X1, y)]) for y in np.arange(Y0 + 50, Y1, 50)]
    out['grid'] = lines_d(unary_union(grid).intersection(ocean.buffer(-1.5)))
    # 4. гексы 14 мм по воде, только в полосе 25 мм от берега и от края полотна — центр океана чистый
    a = 7.0
    hexes = []
    w, h = math.sqrt(3) * a, 1.5 * a
    for j, y in enumerate(np.arange(Y0 - a, Y1 + a, h)):
        for x in np.arange(X0 - w + (w / 2 if j % 2 else 0), X1 + w, w):
            pts = [(x + a * math.cos(math.radians(60 * k + 30)), y + a * math.sin(math.radians(60 * k + 30))) for k in range(7)]
            hexes.append(LineString(pts))
    band = allland.buffer(25).union(rect.difference(rect.buffer(-25))).intersection(ocean.buffer(-1.0))
    out['hex'] = lines_d(unary_union(hexes).intersection(band).simplify(0.05))
    # 5. рамка со шкалой: риски внутрь карты, каждые 10 мм, каждые 50 — длиннее
    ticks = []
    for x in np.arange(X0 + 10, X1, 10):
        L = 4.0 if round(x - X0) % 50 == 0 else 2.0
        ticks += [LineString([(x, Y0), (x, Y0 + L)]), LineString([(x, Y1), (x, Y1 - L)])]
    for y in np.arange(Y0 + 10, Y1, 10):
        L = 4.0 if round(y - Y0) % 50 == 0 else 2.0
        ticks += [LineString([(X0, y), (X0 + L, y)]), LineString([(X1, y), (X1 - L, y)])]
    out['ticks'] = lines_d(MultiLineString(ticks))
    return out


WATER = ((1.6, 0.45, 0.55), (3.6, 0.35, 0.35), (6.4, 0.3, 0.2))   # мм от берега, толщина, непрозрачность


def svg_layer(R, spec, decor=()):
    """слой декора полотна: береговые линии на воде и рамка со шкалой"""
    X0, Y0, X1, Y1 = bc.RECT
    rect = box(X0, Y0, X1, Y1)
    land = unary_union([R[r] for r in spec['areas'] if spec['type'][r] != 'OCEAN'] + [g for _, g in decor])
    ocean = rect.difference(land)
    water = ''.join(f'<path d="{lines_d(land.buffer(d, quad_segs=6).boundary.intersection(ocean).simplify(0.15))}" '
                    f'stroke-width="{w}" stroke-opacity="{o}"/>' for d, w, o in WATER)
    ticks = []
    for x in np.arange(X0 + 10, X1, 10):
        L = 4.0 if round(x - X0) % 50 == 0 else 2.0
        ticks += [LineString([(x, Y0), (x, Y0 + L)]), LineString([(x, Y1), (x, Y1 - L)])]
    for y in np.arange(Y0 + 10, Y1, 10):
        L = 4.0 if round(y - Y0) % 50 == 0 else 2.0
        ticks += [LineString([(X0, y), (X0 + L, y)]), LineString([(X1, y), (X1 - L, y)])]
    return (f'<g fill="none" stroke="#ffffff" stroke-linecap="round">{water}</g>'
            f'<path d="{lines_d(MultiLineString(ticks))}" fill="none" stroke="#2c2a26" stroke-width="0.35"/>')


SHADE_W, SHADE_BLUR, SHADE_OP = 7.0, 3.0, 0.32   # тень к краю суши: ширина штриха, размытие, сила (D-105)
GLOW_BLUR, GLOW_OP = 7.0, 0.22                     # светлая вода у берега: размытие, сила


def bg_layer(R, spec):
    """фон (SPEC §9, D-105): тень к краю суши — у берега и у границ областей, центр ровный;
    вода у берега светлее. Возвращает (defs, слой)"""
    import boardview as bv
    W, H = bc.CANVAS
    X0, Y0, X1, Y1 = bc.RECT
    land = [R[r] for r in spec['areas'] if spec['type'][r] != 'OCEAN']
    mask = bv.path_d(unary_union(land))
    borders = ''.join(bv.path_d(g) for g in land)
    defs = (f'<filter id="bgshade" filterUnits="userSpaceOnUse" x="-50" y="-50" width="{W + 100:g}" height="{H + 100:g}">'
            f'<feGaussianBlur stdDeviation="{SHADE_BLUR:g}"/></filter>'
            f'<filter id="bgglow" filterUnits="userSpaceOnUse" x="-50" y="-50" width="{W + 100:g}" height="{H + 100:g}">'
            f'<feGaussianBlur stdDeviation="{GLOW_BLUR:g}"/></filter>'
            f'<clipPath id="bglm"><path d="{mask}"/></clipPath>'
            f'<clipPath id="bgom"><path d="M{X0:g},{Y0:g}H{X1:g}V{Y1:g}H{X0:g}Z{mask}" clip-rule="evenodd"/></clipPath>')
    layer = (f'<g clip-path="url(#bgom)"><g filter="url(#bgglow)"><path d="{mask}" fill="#ffffff" fill-opacity="{GLOW_OP:g}"/></g></g>'
             f'<g clip-path="url(#bglm)"><g filter="url(#bgshade)"><path d="{borders}" fill="none" stroke="#000000" '
             f'stroke-width="{SHADE_W:g}" stroke-opacity="{SHADE_OP:g}"/></g></g>')
    return defs, layer


def build_test(out):
    D = geometry()
    W, H = bc.CANVAS
    X0, Y0, X1, Y1 = bc.RECT
    layer = (
        '<g id="d-water" style="display:none" fill="none" stroke="#ffffff" stroke-linecap="round">'
        + ''.join(f'<path d="{d}" stroke-width="{w}" stroke-opacity="{o}"/>' for d, w, o in zip(D['water'], (0.45, 0.35, 0.3), (0.55, 0.35, 0.2)))
        + '</g>'
        + '<g id="d-relief" style="display:none" fill="none" stroke="#1c1a17" stroke-linecap="round">'
        + ''.join(f'<path d="{d}" stroke-width="0.3" stroke-opacity="{o}"/>' for d, o in zip(D['relief'], (0.28, 0.16)))
        + '</g>'
        + f'<path id="d-grid" style="display:none" d="{D["grid"]}" fill="none" stroke="#ffffff" stroke-width="0.3" stroke-opacity="0.22" stroke-dasharray="1.5 1.5"/>'
        + f'<path id="d-hex" style="display:none" d="{D["hex"]}" fill="none" stroke="#ffffff" stroke-width="0.25" stroke-opacity="0.18"/>'
        + f'<path id="d-ticks" style="display:none" d="{D["ticks"]}" fill="none" stroke="#2c2a26" stroke-width="0.35"/>'
    )
    boards = []
    for lay in LAYOUTS:
        svg = (GEO / f'board-{lay}.svg').read_text(encoding='utf-8')
        inner = re.sub(r'^.*?<svg[^>]*>', '', svg, flags=re.S).rsplit('</svg>', 1)[0]
        inner = re.sub(r'<title>.*?</title>', '', inner, count=1, flags=re.S)
        inner = inner.replace('id="blend"', f'id="blend-{lay}"').replace('url(#blend)', f'url(#blend-{lay})') \
                     .replace('id="ocmask"', f'id="ocmask-{lay}"').replace('url(#ocmask)', f'url(#ocmask-{lay})')
        lay_layer = layer.replace('id="d-', f'class="d-').replace('class="d-', 'class="dec d-')
        inner = inner.replace('<g id="symbols">', f'{lay_layer}<g id="symbols">', 1)
        boards.append(f'<g class="board" data-lay="{lay}">{inner}</g>')
    radios = ''.join(f'<label><input type="radio" name="lay" value="{l}"{" checked" if l == "MC-5P" else ""}> {l}</label>' for l in LAYOUTS)
    opts = [('water', 'береговые линии на воде — три тонкие линии вдоль берега, как на старых картах', True),
            ('relief', 'рельеф у берега — два тонких контура по краю суши внутрь', False),
            ('grid', 'техническая сетка 50 мм по воде, пунктир', False),
            ('hex', 'гексы по воде у берегов и у краёв полотна, центр океана чистый', False),
            ('ticks', 'рамка со шкалой: риски каждые 10 мм, каждые 50 — длиннее', False)]
    checks = ''.join(f'<label><input type="checkbox" id="c-{k}"{" checked" if on else ""}> {t}</label>' for k, t, on in opts)
    html = f'''<!doctype html>
<html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Декор поля</title>
<style>
:root{{--bg:#f4f1ea;--fg:#23211d;--mut:#6b665c;--line:#d6d0c4;--card:#fbf9f4}}
@media (prefers-color-scheme:dark){{:root:not([data-theme=light]){{--bg:#1d1c1a;--fg:#ece8df;--mut:#a39d91;--line:#3a3833;--card:#252421}}}}
body{{margin:0;background:var(--bg);color:var(--fg);font:15px/1.45 system-ui,sans-serif}}
main{{max-width:1700px;margin:0 auto;padding:16px}}
h1{{font-size:20px;margin:0 0 4px}} p.sub{{margin:0 0 12px;color:var(--mut)}}
.ctl{{display:grid;grid-template-columns:max-content 1fr;gap:6px 16px;align-items:baseline;margin:0 0 10px;padding:10px 12px;border:1px solid var(--line);border-radius:8px;background:var(--card)}}
.ctl .k{{color:var(--mut);font-weight:600}} .ctl .row{{display:flex;flex-wrap:wrap;gap:4px 18px}} .ctl .col{{display:flex;flex-direction:column;gap:4px}}
.ctl label{{display:inline-flex;gap:6px;align-items:center;cursor:pointer}}
@media (max-width:900px){{.ctl{{grid-template-columns:1fr}}}}
svg#map{{width:100%;height:auto;display:block;border-radius:6px}}
</style></head><body><main>
<h1>Декор поля — варианты</h1>
<p class="sub">Этап 3 COMP-C-03, шаг 4. Страница собрана <code>board/tools/decor.py test</code> поверх принятых полотен. По SPEC §9 центр области спокойный, детали — к берегам и краям, поэтому весь декор здесь у берега и на воде, тонкими линиями. Галочки можно включать вместе.</p>
<div class="ctl">
<span class="k">Полотно</span><div class="row">{radios}</div>
<span class="k">Декор</span><div class="col">{checks}</div>
<span class="k">Крупно</span><div class="row"><label><input type="checkbox" id="c-zoom"> показать фрагмент: Европа и Северная Атлантика</label></div>
</div>
<svg id="map" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:g} {H:g}">{''.join(boards)}</svg>
</main>
<script>
const $=id=>document.getElementById(id);
const val=n=>document.querySelector(`input[name=${{n}}]:checked`).value;
const K={json.dumps([k for k, _, _ in opts])};
function draw(){{
  const lay=val('lay');
  document.querySelectorAll('.board').forEach(b=>b.style.display=b.dataset.lay===lay?'':'none');
  for(const k of K)document.querySelectorAll('.d-'+k).forEach(e=>e.style.display=$('c-'+k).checked?'':'none');
  $('map').setAttribute('viewBox',$('c-zoom').checked?'330 30 330 210':'0 0 {W:g} {H:g}');
}}
document.querySelectorAll('input').forEach(e=>e.onchange=draw);
draw();
</script></body></html>
'''
    Path(out).write_text(html, encoding='utf-8')
    return out


def build_bg_test(out):
    """фон под фигурами (SPEC §9): варианты обработки заливки — центр спокойный, всё к краям"""
    import boardview as bv
    W, H = bc.CANVAS
    X0, Y0, X1, Y1 = bc.RECT
    boards = []
    for lay in LAYOUTS:
        fc = json.loads((GEO / f'board-{lay}.geojson').read_text(encoding='utf-8'))
        R = {f['properties']['id']: shape(f['geometry']) for f in fc['features']}
        land = {r: g for r, g in R.items() if '-OC-' not in r}
        lu = unary_union(list(land.values()))
        borders = ''.join(bv.path_d(g) for g in land.values())
        mask = bv.path_d(lu)
        svg = (GEO / f'board-{lay}.svg').read_text(encoding='utf-8')
        inner = re.sub(r'^.*?<svg[^>]*>', '', svg, flags=re.S).rsplit('</svg>', 1)[0]
        inner = re.sub(r'<title>.*?</title>', '', inner, count=1, flags=re.S)
        inner = inner.replace('id="blend"', f'id="blend-{lay}"').replace('url(#blend)', f'url(#blend-{lay})') \
                     .replace('id="ocmask"', f'id="ocmask-{lay}"').replace('url(#ocmask)', f'url(#ocmask-{lay})')
        L = lay
        fx = (f'<clipPath id="lm-{L}"><path d="{mask}"/></clipPath>'
              f'<clipPath id="om-{L}"><path d="M{X0},{Y0}H{X1}V{Y1}H{X0}Z{mask}" clip-rule="evenodd"/></clipPath>'
              f'<g class="bg bg-shade" style="display:none" clip-path="url(#lm-{L})"><g filter="url(#b3)">'
              f'<path d="{borders}" fill="none" stroke="#000" stroke-width="7" stroke-opacity="0.32"/></g></g>'
              f'<g class="bg bg-rim" style="display:none" clip-path="url(#lm-{L})"><g filter="url(#b3)">'
              f'<path d="{borders}" fill="none" stroke="#fff" stroke-width="6" stroke-opacity="0.35"/></g></g>'
              f'<g class="bg bg-grain" style="display:none" clip-path="url(#lm-{L})">'
              f'<rect x="{X0}" y="{Y0}" width="{X1 - X0}" height="{Y1 - Y0}" filter="url(#grain)"/></g>'
              f'<g class="bg bg-glow" style="display:none" clip-path="url(#om-{L})"><g filter="url(#b8)">'
              f'<path d="{mask}" fill="#fff" fill-opacity="0.22"/></g></g>')
        inner = inner.replace('<g id="deco">', fx + '<g id="deco">', 1)
        boards.append(f'<g class="board" data-lay="{lay}">{inner}</g>')
    defs = (f'<defs><filter id="b3" filterUnits="userSpaceOnUse" x="-50" y="-50" width="{W + 100}" height="{H + 100}"><feGaussianBlur stdDeviation="3"/></filter>'
            f'<filter id="b8" filterUnits="userSpaceOnUse" x="-50" y="-50" width="{W + 100}" height="{H + 100}"><feGaussianBlur stdDeviation="7"/></filter>'
            f'<filter id="grain" filterUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}">'
            f'<feTurbulence type="fractalNoise" baseFrequency="0.035" numOctaves="3" seed="7"/>'
            f'<feColorMatrix type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 0.45 -0.19"/></filter></defs>')
    radios = ''.join(f'<label><input type="radio" name="lay" value="{l}"{" checked" if l == "MC-5P" else ""}> {l}</label>' for l in LAYOUTS)
    opts = [('shade', 'тень к краю: суша темнеет у границ и берега на 6–8 мм, центр области ровный'),
            ('rim', 'светлая кромка: суша светлеет у границ и берега, центр ровный'),
            ('grain', 'зерно: крупное мягкое зерно по суше, как бетон или бумага — контраст очень низкий'),
            ('glow', 'вода у берега светлее: мягкое свечение до 15 мм от суши')]
    checks = ''.join(f'<label><input type="checkbox" id="c-{k}"> {t}</label>' for k, t in opts)
    html = f'''<!doctype html>
<html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Фон под фигурами</title>
<style>
:root{{--bg:#f4f1ea;--fg:#23211d;--mut:#6b665c;--line:#d6d0c4;--card:#fbf9f4}}
@media (prefers-color-scheme:dark){{:root:not([data-theme=light]){{--bg:#1d1c1a;--fg:#ece8df;--mut:#a39d91;--line:#3a3833;--card:#252421}}}}
body{{margin:0;background:var(--bg);color:var(--fg);font:15px/1.45 system-ui,sans-serif}}
main{{max-width:1700px;margin:0 auto;padding:16px}}
h1{{font-size:20px;margin:0 0 4px}} p.sub{{margin:0 0 12px;color:var(--mut)}}
.ctl{{display:grid;grid-template-columns:max-content 1fr;gap:6px 16px;align-items:baseline;margin:0 0 10px;padding:10px 12px;border:1px solid var(--line);border-radius:8px;background:var(--card)}}
.ctl .k{{color:var(--mut);font-weight:600}} .ctl .row{{display:flex;flex-wrap:wrap;gap:4px 18px}} .ctl .col{{display:flex;flex-direction:column;gap:4px}}
.ctl label{{display:inline-flex;gap:6px;align-items:center;cursor:pointer}}
@media (max-width:900px){{.ctl{{grid-template-columns:1fr}}}}
svg#map{{width:100%;height:auto;display:block;border-radius:6px}}
</style></head><body><main>
<h1>Фон под фигурами — варианты</h1>
<p class="sub">Этап 3 COMP-C-03, шаг 5. Страница собрана <code>board/tools/decor.py test-bg</code> поверх принятых полотен. SPEC §9: под фигурами — ровная подложка без мелкого рисунка, светлота 25–55 %, детали уходят к краям. Сейчас заливка плоская — это уже соответствует §9; варианты ниже добавляют глубину только у краёв. Без галочек — как сейчас.</p>
<div class="ctl">
<span class="k">Полотно</span><div class="row">{radios}</div>
<span class="k">Фон</span><div class="col">{checks}</div>
<span class="k">Крупно</span><div class="row"><label><input type="checkbox" id="c-zoom"> фрагмент: Африка и Аравия</label></div>
</div>
<svg id="map" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:g} {H:g}">{defs}{''.join(boards)}</svg>
</main>
<script>
const $=id=>document.getElementById(id);
const val=n=>document.querySelector(`input[name=${{n}}]:checked`).value;
const K={json.dumps([k for k, _ in opts])};
function draw(){{
  const lay=val('lay');
  document.querySelectorAll('.board').forEach(b=>b.style.display=b.dataset.lay===lay?'':'none');
  for(const k of K)document.querySelectorAll('.bg-'+k).forEach(e=>e.style.display=$('c-'+k).checked?'':'none');
  $('map').setAttribute('viewBox',$('c-zoom').checked?'500 180 300 220':'0 0 {W:g} {H:g}');
}}
document.querySelectorAll('input').forEach(e=>e.onchange=draw);
draw();
</script></body></html>
'''
    Path(out).write_text(html, encoding='utf-8')
    return out


def main(argv):
    if len(argv) >= 2 and argv[1] == 'test-bg':
        print(build_bg_test(GEO / 'background-test.html'))
        return 0
    if len(argv) >= 2 and argv[1] == 'test':
        print(build_test(GEO / 'decor-test.html'))
        return 0
    print(__doc__)
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv))
