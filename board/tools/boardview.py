"""
boardview.py — общая запись и отрисовка полотна: свойства областей в GeoJSON,
картинка SVG и страница просмотра HTML.

Вынесено из slice5.py на этапе 2 COMP-C-03: одной отрисовкой пользуются нарезка
MC-5P (slice5.py) и склейка MC-3P, MC-4P-A, MC-4P-B (glue.py). Своей геометрии
здесь нет: области, основа и декор приходят готовыми.

Сам не запускается. Зависимости: numpy, shapely (+ boardcheck.py рядом).
"""
import json
import urllib.parse
from datetime import date
from pathlib import Path

import numpy as np
import shapely
from shapely.geometry import MultiPolygon, Point, mapping
from shapely.geometry.polygon import orient

import boardcheck as bc

ROOT = Path(__file__).resolve().parents[2]
GEO = ROOT / 'board' / 'geo'
DRAFT = ROOT / 'board' / 'legacy' / 'карта 5.jpg'

X0, Y0, X1, Y1 = bc.RECT                    # прямоугольник карты в мм полотна

# ---------------------------------------------------------------------------
# запись: геометрия и свойства области
# ---------------------------------------------------------------------------


def clean(g):
    """валидно, кольца по RFC 7946, без пыли мельче 1 мм² (следы округления на стыках)"""
    ps = [orient(p, 1.0) for p in bc.polys(shapely.make_valid(g)) if p.area >= bc.AREA_TOL]
    return ps[0] if len(ps) == 1 else MultiPolygon(ps)


def rounded(g, nd=3):
    """координаты до 0,001 мм: соседние области получают одинаковые вершины"""
    r = shapely.set_precision(g, 10 ** -nd, mode='pointwise')
    return clean(r)


def feature(rid, g, spec, row):
    """Feature области: id, имя, род, родитель, площадь, число кусков, U и U/A из проверки"""
    props = {'id': rid, 'name_ru': spec['names'][rid], 'type': spec['type'][rid],
             'parent': spec['group'][rid] if spec['group'][rid] != rid else None,
             'area_cm2': round(g.area / 100, 1), 'parts': len(bc.polys(g))}
    for k, kk, nd in (('U', 'U_cm2', 1), ('UA', 'U_over_A', 3)):
        if k in row:
            props[kk] = round(row[k], nd)
    return {'type': 'Feature', 'properties': props, 'geometry': json.loads(json.dumps(mapping(g)))}

# ---------------------------------------------------------------------------
# картинка: svg и html
# ---------------------------------------------------------------------------


BLEND_MM = 8.0       # мм: ширина перехода 10–90 % между океанами (Alek 30.09.2026, D-099)
BLEND_PAD = 60.0     # мм: на сколько слой океанов выходит за край карты — под размытие


def load_colours():
    """заливки областей из board/redesign.yaml → colour, по id оригинала (MR-…)"""
    import yaml
    regs = yaml.safe_load((ROOT / 'board' / 'redesign.yaml').read_text(encoding='utf-8'))['regions']
    return {r['baseline_ref']: r['colour'] for r in regs}


COLOUR = load_colours()


def ocean_territories(oceans, step=1.0):
    """слой океанов под размытие: каждый океан + суша, которая к нему ближе всех, с копиями через
    склейку (±WRAP). Суша под слоем нужна, чтобы у берега размытие не тянуло прозрачность;
    ближайший океан — по диаграмме Вороного точек берега (граница океан — океан в точки не идёт).
    oceans — {id: полигон}. Возвращает ({id: слой}, маска океанов в прямоугольнике карты)."""
    from shapely import affinity
    from shapely.geometry import MultiPoint, box
    from shapely.ops import unary_union
    oc = [(rid, affinity.translate(g, k * bc.WRAP, 0)) for rid, g in sorted(oceans.items()) for k in (-1, 0, 1)]
    dom = box(X0 - BLEND_PAD - 30, Y0 - BLEND_PAD, X1 + BLEND_PAD + 30, Y1 + BLEND_PAD)
    pts, lab = [], []
    for rid, g in oc:
        others = unary_union([h for r2, h in oc if r2 != rid])
        for p in bc.polys(g):
            for ring in [p.exterior, *p.interiors]:
                n = max(4, int(ring.length / step))
                P = shapely.line_interpolate_point(ring, np.linspace(0, ring.length, n, endpoint=False))
                far = shapely.distance(P, others) > 0.05
                pts.extend(P[far])
                lab.extend([rid] * int(far.sum()))
    cells = shapely.voronoi_polygons(MultiPoint(pts), extend_to=dom, ordered=True)
    by = {}
    for c, rid in zip(shapely.get_parts(cells), lab):
        by.setdefault(rid, []).append(c)
    water = unary_union([g for _, g in oc])
    out = {}
    for rid, cs in by.items():
        own = unary_union([g for r2, g in oc if r2 == rid])
        out[rid] = shapely.set_precision(unary_union(cs).difference(water).union(own).intersection(dom), 0.01)
    mask = unary_union(list(oceans.values())).intersection(box(X0, Y0, X1, Y1))
    return out, mask


_BLEND = {}


def blend_layer(R, spec):
    """слой океанов один на все полотна (SPEC §3.1) — считается раз на процесс"""
    oceans = {rid: R[rid] for rid in spec['areas'] if spec['type'][rid] == 'OCEAN'}
    key = tuple(sorted((rid, round(g.area, 1)) for rid, g in oceans.items()))
    if key not in _BLEND:
        _BLEND[key] = ocean_territories(oceans)
    return _BLEND[key]


def blend_defs(R, spec):
    """фильтр размытия и маска океанов: σ = ширина 10–90 % / 2,563"""
    _, mask = blend_layer(R, spec)
    return (f'<filter id="blend" filterUnits="userSpaceOnUse" x="{X0 - 200:g}" y="{-BLEND_PAD:g}" '
            f'width="{X1 - X0 + 400:g}" height="{bc.CANVAS[1] + 2 * BLEND_PAD:g}" color-interpolation-filters="sRGB">'
            f'<feGaussianBlur stdDeviation="{BLEND_MM / 2.563:.3f}"/></filter>'
            f'<clipPath id="ocmask"><path d="{path_d(mask)}"/></clipPath>')


def path_d(g):
    d = []
    for p in bc.polys(g):
        for ring in [p.exterior, *p.interiors]:
            c = np.asarray(ring.coords)
            d.append('M' + ' '.join(f'{x:.2f},{y:.2f}' for x, y in c[:-1]) + 'Z')
    return ''.join(d)


def node_point(g, seed=None):
    """точка графа: первое зерно области, если на нём встаёт пехотинец, иначе ближайшая
    к зерну точка рабочей зоны; без зерна — центр вписанного круга"""
    from shapely.ops import nearest_points
    if g.is_empty:
        return (X0 + 5, Y0 + 5)
    u = bc.u_pieces(g)
    if seed is not None and not u.is_empty:
        P = Point(seed)
        q = P if u.covers(P) else nearest_points(u, P)[0]
        return q.x, q.y
    src = max(bc.polys(u), key=lambda p: p.area) if not u.is_empty else max(bc.polys(g), key=lambda p: p.area)
    c = shapely.maximum_inscribed_circle(src).coords[0]
    return c[0], c[1]


def svg_regions(R, spec):
    """океаны — заливкой без линии и поверх неё слой с переходом BLEND_MM между океанами (обрезан по
    маске океанов); суша — поверх, со строгой линией: и по берегу, и между областями суши"""
    terr, _ = blend_layer(R, spec)
    oc, ld = [], []
    for rid in spec['areas']:
        is_oc = spec['type'][rid] == 'OCEAN'
        (oc if is_oc else ld).append(
            f'<path id="r-{rid}" class="{"oc" if is_oc else "ld"}" fill="{COLOUR[rid]}" d="{path_d(R[rid])}">'
            f'<title>{spec["names"][rid]} ({rid})</title></path>')
    bl = ''.join(f'<path class="bl" fill="{COLOUR[rid]}" d="{path_d(g)}"/>' for rid, g in sorted(terr.items()))
    return (''.join(oc) + f'<g clip-path="url(#ocmask)"><g filter="url(#blend)">{bl}</g></g>' + ''.join(ld))


def svg(R, spec, title, decor=()):
    """decor — [(область, полигон)] островов-декора: поверх океана, цвет области, та же линия берега"""
    W, H = bc.CANVAS
    dec = ''.join(f'<path class="ld" fill="{COLOUR[rid]}" d="{path_d(g)}"/>' for rid, g in decor)
    import labels as lb
    import symbols as sy
    import decor as dc
    names = lb.svg_layer(lb.place(R, spec, decor)[0])
    syms = sy.svg_layer(R, spec, decor)[0]
    deco = dc.svg_layer(R, spec, decor)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:g}mm" height="{H:g}mm" viewBox="0 0 {W:g} {H:g}">\n'
            f'<title>{title}</title>\n<defs>{blend_defs(R, spec)}</defs>'
            f'<rect width="{W:g}" height="{H:g}" fill="#ece8df"/>'
            f'<style>{lb.font_css()}{sy.font_css()}</style>'
            f'<g stroke-linejoin="round"><style>.ld{{stroke:#2c2a26;stroke-width:.35}}</style>{svg_regions(R, spec)}{dec}</g>'
            f'<g id="deco">{deco}</g><g id="symbols">{syms}</g><g id="names">{names}</g>'
            f'<rect x="{X0:g}" y="{Y0:g}" width="{X1 - X0:g}" height="{Y1 - Y0:g}" fill="none" stroke="#2c2a26" stroke-width="0.4"/>'
            f'\n</svg>\n')


def edge_lines(p, q):
    """отрезки ребра p—q с учётом склейки: если короче через край — два куска"""
    (x1, y1), (x2, y2) = p, q
    dx = x2 - x1
    if abs(dx) <= bc.WRAP / 2:
        return [((x1, y1), (x2, y2))]
    s = -bc.WRAP if dx > 0 else bc.WRAP
    return [((x1, y1), (x2 + s, y2)), ((x1 - s, y1), (x2, y2))]


def graph_layer(spec, chk, nodes):
    status = {frozenset((a, b)): (L, lvl) for a, b, L, lvl in chk['edges']}
    lines = []
    for e in sorted(spec['edges'], key=lambda e: sorted(e)):
        a, b = sorted(e)
        L, lvl = status.get(e, (0.0, 'FAIL'))
        cls = {'ok': 'eok', 'WARN': 'ewarn', 'FAIL': 'efail'}[lvl]
        for (p, q) in edge_lines(nodes[a], nodes[b]):
            lines.append(f'<line class="{cls}" x1="{p[0]:.1f}" y1="{p[1]:.1f}" x2="{q[0]:.1f}" y2="{q[1]:.1f}">'
                         f'<title>{spec["names"][a]} — {spec["names"][b]}: касание {L:.1f} мм</title></line>')
    bad = []   # лишние касания и тесные несмежные
    for a, b, d, L in chk['close']:
        if L > bc.TOL or d < bc.GAP_MIN:
            what = f'лишняя смежность, касание {L:.1f} мм' if L > bc.TOL else f'несмежные, зазор {d:.1f} мм'
            for (p, q) in edge_lines(nodes[a], nodes[b]):
                bad.append(f'<line class="ebad" x1="{p[0]:.1f}" y1="{p[1]:.1f}" x2="{q[0]:.1f}" y2="{q[1]:.1f}">'
                           f'<title>{spec["names"][a]} — {spec["names"][b]}: {what}</title></line>')
    dots = ''.join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.6"><title>{spec["names"][rid]}</title></circle>'
                   for rid, (x, y) in nodes.items())
    return ''.join(lines) + ''.join(bad) + f'<g class="nodes">{dots}</g>'


def labels_layer(spec, rows, nodes):
    out = []
    for rid, (x, y) in nodes.items():
        r = rows[rid]
        short = rid.split('-')[-1]
        bad = 'lbad' if r.get('fails') else ('lwarn' if r.get('warns') else 'lok')
        n = f'{r.get("N25", "–")}/{r.get("N40", "–")}/{r.get("N60", "–")}'
        out.append(f'<g class="lab {bad}" transform="translate({x:.1f},{y:.1f})">'
                   f'<text y="-6">{short}{" ★" if r["start"] else ""}</text>'
                   f'<text y="12" class="sm">A {r["A"]:.0f} · U {r["U"]:.0f}</text>'
                   f'<text y="18.5" class="sm">N {n}</text></g>')
    return ''.join(out)


def html(R, C, spec, chk, log, *, nodes, decor, page_title, heading, generator, log_title, note=''):
    """страница просмотра. R — области, C — материки основы (контур), nodes — точки графа,
    decor — [(область, полигон)] островов-декора; note — лишний абзац под легендой"""
    W, H = bc.CANVAS
    rows = chk['rows']
    glayer = graph_layer(spec, chk, nodes)
    import labels as lb
    import symbols as sy
    names, names_miss = lb.place(R, spec, decor)
    syms, syms_miss = sy.svg_layer(R, spec, decor)
    import decor as dc
    deco = dc.svg_layer(R, spec, decor)
    if names_miss:
        log = list(log) + ['подписи не поместились: ' + ', '.join(names_miss)]
    if syms_miss:
        log = list(log) + ['символы не поместились: ' + ', '.join(syms_miss)]
    draft = urllib.parse.quote(DRAFT.relative_to(GEO.parent).as_posix())
    base = ''.join(f'<path d="{path_d(g)}"/>' for g in C.values())
    decor = ''.join(f'<path fill="{COLOUR[rid]}" d="{path_d(g)}"><title>остров-декор: '
                    f'{spec["names"][rid]}</title></path>' for rid, g in decor)
    wrap = (f'<clipPath id="cl"><rect x="{X0 - 120:g}" y="0" width="120" height="{H:g}"/></clipPath>'
            f'<clipPath id="cr"><rect x="{X1:g}" y="0" width="120" height="{H:g}"/></clipPath>'
            f'<g clip-path="url(#cl)" opacity="0.55"><use href="#regions" x="{-bc.WRAP:g}"/></g>'
            f'<g clip-path="url(#cr)" opacity="0.55"><use href="#regions" x="{bc.WRAP:g}"/></g>')
    res = chk['results']
    nf = sum(1 for l, _, _ in res if l == 'FAIL')
    nw = sum(1 for l, _, _ in res if l == 'WARN')
    items = ''.join(f'<li class="{ {"ok": "ok", "WARN": "warn", "FAIL": "bad"}[l] }">'
                    f'{ {"ok": "✓", "WARN": "△", "FAIL": "✗"}[l] } <span class="sec">{s}</span> {t}</li>' for l, s, t in res)
    trs = []
    for rid in spec['areas']:
        r = rows[rid]
        v = ('✗ ' + '; '.join(r['fails'])) if r['fails'] else ('△ ' + '; '.join(r['warns']) if r['warns'] else '✓')
        cls = 'bad' if r['fails'] else ('warn' if r['warns'] else 'ok')
        trs.append(f'<tr><td>{r["name"]}{" ★" if r["start"] else ""}</td><td>{r["A"]:.0f}</td><td>{r["U"]:.0f}</td>'
                   f'<td>{r["UA"]:.3f}</td><td>{r["UA_main"]:.3f}</td><td>{r.get("N25", "–")}</td><td>{r.get("N40", "–")}</td><td>{r.get("N60", "–")}</td>'
                   f'<td>{r["share"] * 100:.0f} %</td><td class="{cls} v">{v}</td></tr>')
    ers = ''.join(f'<tr><td>{spec["names"][a]} — {spec["names"][b]}</td><td>{L:.1f}</td>'
                  f'<td class="{ {"ok": "ok", "WARN": "warn", "FAIL": "bad"}[lvl] }">'
                  f'{ {"ok": "✓", "WARN": "△ 8–25", "FAIL": "✗ < 8"}[lvl] }</td></tr>'
                  for a, b, L, lvl in sorted(chk['edges'], key=lambda t: t[2]))
    logh = ''.join(f'<li>{t}</li>' for t in log) or '<li>без происшествий</li>'
    notep = f'\n<p class="sub">{note}</p>' if note else ''
    return f'''<!doctype html>
<html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{page_title}</title>
<style>
{lb.font_css()}{sy.font_css()}
:root{{--bg:#f4f1ea;--fg:#23211d;--mut:#6b665c;--line:#d6d0c4;--ok:#2f7d4a;--warn:#a86a00;--bad:#b3261e}}
@media (prefers-color-scheme:dark){{:root:not([data-theme=light]){{--bg:#1d1c1a;--fg:#ece8df;--mut:#a39d91;--line:#3a3833;--ok:#7fc79a;--warn:#e6b35c;--bad:#f2867e}}}}
body{{margin:0;background:var(--bg);color:var(--fg);font:15px/1.45 system-ui,sans-serif}}
main{{max-width:1600px;margin:0 auto;padding:16px}}
h1{{font-size:20px;margin:0 0 4px}} p.sub{{margin:0 0 12px;color:var(--mut)}}
.ctl{{display:flex;flex-wrap:wrap;gap:8px 20px;align-items:center;margin:0 0 10px;padding:10px 12px;border:1px solid var(--line);border-radius:8px}}
.ctl label{{display:flex;gap:6px;align-items:center;cursor:pointer}}
.ctl input[type=range]:disabled{{opacity:.4}}
svg#map{{width:100%;height:auto;display:block;border-radius:6px}}
#regions path.ld{{stroke:#2c2a26;stroke-width:.35;stroke-linejoin:round}}
#base path{{fill:none;stroke:#fff;stroke-width:.7;stroke-dasharray:2 1.4}}
#decor path{{stroke:#2c2a26;stroke-width:.35;stroke-linejoin:round}}
#graph line{{stroke-width:1.1;stroke-linecap:round}}
#graph .eok{{stroke:#1d6b3a}} #graph .ewarn{{stroke:#c77800;stroke-dasharray:3 1.5}}
#graph .efail{{stroke:#d0161b;stroke-width:1.6;stroke-dasharray:1.2 1.6}}
#graph .ebad{{stroke:#d0161b;stroke-width:1.8}}
#graph .nodes circle{{fill:#111;stroke:#fff;stroke-width:.7}}
.lab text{{font:700 7px system-ui,sans-serif;text-anchor:middle;fill:#111;paint-order:stroke;stroke:#fff;stroke-width:1.8px;stroke-linejoin:round}}
.lab text.sm{{font-weight:500;font-size:5.4px}}
.lab.lbad text:first-child{{fill:#b3261e}} .lab.lwarn text:first-child{{fill:#8a5200}}
.cols{{display:grid;grid-template-columns:minmax(0,3fr) minmax(0,2fr);gap:24px;margin-top:16px}}
@media (max-width:900px){{.cols{{grid-template-columns:1fr}}}}
table{{border-collapse:collapse;width:100%;font-size:13px}} td,th{{padding:3px 6px;border-bottom:1px solid var(--line);text-align:right;vertical-align:top}}
td:first-child,th:first-child,td.v{{text-align:left}} th{{color:var(--mut);font-weight:500}}
ul{{padding-left:0;list-style:none;margin:0;font-size:13px}} li{{padding:2px 0}}
.ok{{color:var(--ok)}} .warn{{color:var(--warn)}} .bad{{color:var(--bad)}} .sec{{color:var(--mut)}}
h2{{font-size:16px;margin:18px 0 8px}} .big{{font-size:17px;font-weight:600}}
</style></head><body><main>
<h1>{heading}</h1>
<p class="sub">Полотно {W:g} × {H:g} мм · сборка {date.today().isoformat()}, <code>{generator}</code> · проверка <code>board/tools/boardcheck.py</code></p>
<p class="big {"bad" if nf else "ok"}">{"Отказов: " + str(nf) if nf else "Зелёное: отказов нет"} · предупреждений: {nw}</p>
<div class="ctl">
<label><input type="checkbox" id="c-names" checked> Подписи областей</label>
<label><input type="checkbox" id="c-sym" checked> Символы регионов</label>
<label><input type="checkbox" id="c-deco" checked> Декор: береговые линии, шкала</label>
<label><input type="checkbox" id="c-lab"> Метрики: id, A, U, N</label>
<label><input type="checkbox" id="c-graph" checked> Граф: центры и рёбра</label>
<label><input type="checkbox" id="c-base"> Контур основы</label>
<label><input type="checkbox" id="c-decor" checked> Острова-декор</label>
<label><input type="checkbox" id="c-draft"> Черновик «карта 5»</label>
<label>прозрачность <input type="range" id="r-op" min="10" max="90" value="50" disabled></label>
<label><input type="checkbox" id="c-wrap"> Склейка краёв: показать соседний край</label>
</div>
<p class="sub">Граф: зелёная линия — ребро с касанием ≥ 25 мм, оранжевый пунктир — 8–25 мм, красный пунктир — ребро не держится (&lt; 8 мм или нет), сплошной красный — лишнее касание или зазор несмежных &lt; 12 мм. Ребро через склейку рисуется двумя кусками у краёв. Острова-декор — не суша областей: рисуются поверх океана, цвет — регион, к которому относятся. Подписи: A и U в см², N — пехота/машины/роботы, ★ — стартовая.</p>{notep}
<svg id="map" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:g} {H:g}">
<defs>{blend_defs(R, spec)}</defs>
<rect x="-200" width="{W + 400:g}" height="{H:g}" fill="#ece8df"/>
<g id="regions">{svg_regions(R, spec)}</g>
<g id="wrap" style="display:none">{wrap}</g>
<g id="draft" style="display:none"><image href="../{draft}" x="{X0:g}" y="{Y0:g}" width="{X1 - X0:g}" height="{Y1 - Y0:g}" preserveAspectRatio="none" opacity="0.5"/></g>
<g id="base" style="display:none">{base}</g>
<g id="decor">{decor}</g>
<clipPath id="cmap"><rect id="cmaprect" x="{X0:g}" y="{Y0:g}" width="{X1 - X0:g}" height="{Y1 - Y0:g}"/></clipPath>
<g id="graph" clip-path="url(#cmap)">{glayer}</g>
<g id="deco">{deco}</g>
<g id="symbols">{syms}</g>
<g id="names">{lb.svg_layer(names)}</g>
<g id="labels" style="display:none">{labels_layer(spec, rows, nodes)}</g>
<rect x="{X0:g}" y="{Y0:g}" width="{X1 - X0:g}" height="{Y1 - Y0:g}" fill="none" stroke="#2c2a26" stroke-width="0.4"/>
</svg>
<div class="cols">
<section><h2>Области</h2>
<table><tr><th>Область</th><th>A</th><th>U</th><th>U/A всей</th><th>U/A главного куска</th><th>N пех</th><th>N маш</th><th>N роб</th><th>U одним куском</th><th>Вердикт</th></tr>{"".join(trs)}</table>
<h2>Рёбра графа, касание в мм</h2><table><tr><th>Ребро</th><th>мм</th><th></th></tr>{ers}</table></section>
<section><h2>Проверка</h2><ul>{items}</ul>
<h2>{log_title}</h2><ul>{logh}</ul></section>
</div>
</main>
<script>
const $=id=>document.getElementById(id);
const show=(id,on)=>{{$(id).style.display=on?'':'none'}};
$('c-lab').onchange=e=>show('labels',e.target.checked);
$('c-names').onchange=e=>show('names',e.target.checked);
$('c-sym').onchange=e=>show('symbols',e.target.checked);
$('c-deco').onchange=e=>show('deco',e.target.checked);
$('c-graph').onchange=e=>show('graph',e.target.checked);
$('c-base').onchange=e=>show('base',e.target.checked);
$('c-decor').onchange=e=>show('decor',e.target.checked);
$('c-draft').onchange=e=>{{show('draft',e.target.checked);$('r-op').disabled=!e.target.checked}};
$('r-op').oninput=e=>{{document.querySelector('#draft image').setAttribute('opacity',e.target.value/100)}};
$('c-wrap').onchange=e=>{{show('wrap',e.target.checked);$('map').setAttribute('viewBox',e.target.checked?'-120 0 {W + 240:g} {H:g}':'0 0 {W:g} {H:g}')}};
</script></body></html>
'''
