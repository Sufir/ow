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


TINT = {  # оттенки по материкам, океаны — синие; сторона «3» — свой оттенок материка
    'MR-L5-NAMW': '#d9a066', 'MR-L5-NAME': '#c98a5a', 'MR-L5-CAM': '#b8764e',
    'MR-L5-SAMW': '#c96a5e', 'MR-L5-SAME': '#a9ad6a',
    'MR-R5-SCA': '#a27a4f', 'MR-R5-EUR': '#8e9a6a',
    'MR-R5-ASIN': '#b85a50', 'MR-R5-ASIS': '#d97a5a', 'MR-R5-ARB': '#d7b050',
    'MR-R5-AFRW': '#b09090', 'MR-R5-AFRE': '#958d78',
    'MR-L5-AUS': '#9a7a58', 'MR-L5-NZL': '#d2a843',
    'MR-L3-NAM': '#cf955f', 'MR-L3-SAM': '#b98c62', 'MR-L3-AUS': '#b8914d',
    'MR-R3-EUR': '#98896b', 'MR-R3-ASI': '#c9744f', 'MR-R3-AFR': '#a58f84',
    'MR-SH-ANT': '#dcd6c4',
    'MR-OC-ARC': '#9fb6c6', 'MR-OC-NPAC': '#4d6a8c', 'MR-OC-NATL': '#5a6592',
    'MR-OC-SATL': '#4f8a92', 'MR-OC-SPAC': '#58708a', 'MR-OC-IND': '#4a7f86',
}


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
    out = []
    for rid in spec['areas']:
        cls = 'oc' if spec['type'][rid] == 'OCEAN' else 'ld'
        out.append(f'<path id="r-{rid}" class="{cls}" fill="{TINT[rid]}" d="{path_d(R[rid])}">'
                   f'<title>{spec["names"][rid]} ({rid})</title></path>')
    return ''.join(out)


def svg(R, spec, title):
    W, H = bc.CANVAS
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:g}mm" height="{H:g}mm" viewBox="0 0 {W:g} {H:g}">\n'
            f'<title>{title}</title>\n'
            f'<rect width="{W:g}" height="{H:g}" fill="#ece8df"/>'
            f'<g stroke="#2c2a26" stroke-width="0.35" stroke-linejoin="round">{svg_regions(R, spec)}</g>'
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
    draft = urllib.parse.quote(DRAFT.relative_to(GEO.parent).as_posix())
    base = ''.join(f'<path d="{path_d(g)}"/>' for g in C.values())
    decor = ''.join(f'<path fill="{TINT[rid]}" d="{path_d(g)}"><title>остров-декор: '
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
:root{{--bg:#f4f1ea;--fg:#23211d;--mut:#6b665c;--line:#d6d0c4;--ok:#2f7d4a;--warn:#a86a00;--bad:#b3261e}}
@media (prefers-color-scheme:dark){{:root:not([data-theme=light]){{--bg:#1d1c1a;--fg:#ece8df;--mut:#a39d91;--line:#3a3833;--ok:#7fc79a;--warn:#e6b35c;--bad:#f2867e}}}}
body{{margin:0;background:var(--bg);color:var(--fg);font:15px/1.45 system-ui,sans-serif}}
main{{max-width:1600px;margin:0 auto;padding:16px}}
h1{{font-size:20px;margin:0 0 4px}} p.sub{{margin:0 0 12px;color:var(--mut)}}
.ctl{{display:flex;flex-wrap:wrap;gap:8px 20px;align-items:center;margin:0 0 10px;padding:10px 12px;border:1px solid var(--line);border-radius:8px}}
.ctl label{{display:flex;gap:6px;align-items:center;cursor:pointer}}
.ctl input[type=range]:disabled{{opacity:.4}}
svg#map{{width:100%;height:auto;display:block;border-radius:6px}}
#regions path{{stroke:#2c2a26;stroke-width:.35;stroke-linejoin:round}}
#base path{{fill:none;stroke:#fff;stroke-width:.7;stroke-dasharray:2 1.4}}
#decor path{{stroke:#2c2a26;stroke-width:.3;stroke-dasharray:1 .8;opacity:.85}}
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
<label><input type="checkbox" id="c-lab" checked> Подписи: id и метрики</label>
<label><input type="checkbox" id="c-graph" checked> Граф: центры и рёбра</label>
<label><input type="checkbox" id="c-base"> Контур основы</label>
<label><input type="checkbox" id="c-decor" checked> Острова-декор</label>
<label><input type="checkbox" id="c-draft"> Черновик «карта 5»</label>
<label>прозрачность <input type="range" id="r-op" min="10" max="90" value="50" disabled></label>
<label><input type="checkbox" id="c-wrap"> Склейка краёв: показать соседний край</label>
</div>
<p class="sub">Граф: зелёная линия — ребро с касанием ≥ 25 мм, оранжевый пунктир — 8–25 мм, красный пунктир — ребро не держится (&lt; 8 мм или нет), сплошной красный — лишнее касание или зазор несмежных &lt; 12 мм. Ребро через склейку рисуется двумя кусками у краёв. Острова-декор (пунктир) — не суша областей: рисуются поверх океана, цвет — регион, к которому относятся. Подписи: A и U в см², N — пехота/машины/роботы, ★ — стартовая.</p>{notep}
<svg id="map" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:g} {H:g}">
<rect x="-200" width="{W + 400:g}" height="{H:g}" fill="#ece8df"/>
<g id="regions">{svg_regions(R, spec)}</g>
<g id="wrap" style="display:none">{wrap}</g>
<g id="draft" style="display:none"><image href="../{draft}" x="{X0:g}" y="{Y0:g}" width="{X1 - X0:g}" height="{Y1 - Y0:g}" preserveAspectRatio="none" opacity="0.5"/></g>
<g id="base" style="display:none">{base}</g>
<g id="decor">{decor}</g>
<clipPath id="cmap"><rect id="cmaprect" x="{X0:g}" y="{Y0:g}" width="{X1 - X0:g}" height="{Y1 - Y0:g}"/></clipPath>
<g id="graph" clip-path="url(#cmap)">{glayer}</g>
<g id="labels">{labels_layer(spec, rows, nodes)}</g>
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
$('c-graph').onchange=e=>show('graph',e.target.checked);
$('c-base').onchange=e=>show('base',e.target.checked);
$('c-decor').onchange=e=>show('decor',e.target.checked);
$('c-draft').onchange=e=>{{show('draft',e.target.checked);$('r-op').disabled=!e.target.checked}};
$('r-op').oninput=e=>{{document.querySelector('#draft image').setAttribute('opacity',e.target.value/100)}};
$('c-wrap').onchange=e=>{{show('wrap',e.target.checked);$('map').setAttribute('viewBox',e.target.checked?'-120 0 {W + 240:g} {H:g}':'0 0 {W:g} {H:g}')}};
</script></body></html>
'''
