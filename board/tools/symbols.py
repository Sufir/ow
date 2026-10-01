"""
symbols.py — символы регионов на полотне: капля Q, пламя W, вагонетка E (SPEC-BOARD §8.2).

Этап 3 компонента COMP-C-03, шаг 3. Какой символ у какой области — board/derived/<раскладка>.json
→ region_symbols (из glyphs.yaml, D-046): символ идёт по материку. Глифы — print/Fonts/Oil Wars.ttf.
Символ печатается в рабочей зоне и из U не вычитается: фигура может стоять поверх.

Запуск из корня репозитория:
    python3 board/tools/symbols.py test     тестовая страница board/geo/symbols-test.html
Зависимости: numpy, shapely, fontTools (+ boardcheck.py, labels.py, slice5.py рядом).
"""
import json
import re
import sys
from pathlib import Path

from shapely.geometry import box, shape
from shapely.ops import unary_union

sys.path.insert(0, str(Path(__file__).resolve().parent))
import boardcheck as bc  # noqa: E402
import labels as lb  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
GEO = ROOT / 'board' / 'geo'
LAYOUTS = ('MC-3P', 'MC-4P-A', 'MC-4P-B', 'MC-5P')
SYM_FONT = 'OilWarsSym'
SYM_URL = '../../print/Fonts/Oil%20Wars.ttf'
CAP = 0.70                     # высота глифа Q/W/E в кеглях (700 из 1000)
PLATE_K = 1.45                 # диаметр круглой плашки к высоте знака
GAP = 2.0                      # мм: от подписи до знака
SIZES = (12, 16, 20)           # мм: высота знака — варианты тестовой страницы
POSITIONS = ('left', 'above', 'free')
SIZE, POS = 12.0, 'free'       # выбор Alek 01.10.2026 (D-102): 12 мм, в глубине области
FILL, FILL_OPACITY = '#141210', 0.45   # тёмный полупрозрачный — «водяной знак»


def load(layout):
    fc = json.loads((GEO / f'board-{layout}.geojson').read_text(encoding='utf-8'))
    R = {f['properties']['id']: shape(f['geometry']) for f in fc['features']}
    d = json.loads((ROOT / 'board' / 'derived' / f'{layout}.json').read_text(encoding='utf-8'))
    return R, {k: v['glyph'] for k, v in d['region_symbols'].items()}


def label_box(p):
    x0, y0, x1, y1 = lb.bbox(p['lines'], p['fs'], p['anchor'])
    b = (p['x'] + x0, p['y'] + y0, p['x'] + x1, p['y'] + y1)
    if p['plate'] and p['plate'][0] == 'rect':
        b = p['plate'][1]
    return b


def place_one(rid, g, lab, size, pos, dec):
    """центр знака: рядом с подписью (слева/справа/сверху/снизу) или отдельно, в глубине области"""
    d = size * PLATE_K
    lbx = label_box(lab) if lab else None
    keep = box(lbx[0] - 1.5, lbx[1] - 1.5, lbx[2] + 1.5, lbx[3] + 1.5) if lbx else None

    def ok(cx, cy):
        b = (cx - d / 2, cy - d / 2, cx + d / 2, cy + d / 2)
        if not lb._fits(g, dec, b, 1.0):
            return False
        return keep is None or box(*b).disjoint(keep)

    near = []
    if lbx:
        cy = (lbx[1] + lbx[3]) / 2
        cx = (lbx[0] + lbx[2]) / 2
        sides = {'left': (lbx[0] - GAP - d / 2, cy), 'right': (lbx[2] + GAP + d / 2, cy),
                 'above': (cx, lbx[1] - GAP - d / 2), 'below': (cx, lbx[3] + GAP + d / 2)}
        order = {'left': ['left', 'right', 'above', 'below'], 'above': ['above', 'below', 'left', 'right']}.get(pos, [])
        near = [sides[k] for k in order]
    if pos != 'free':
        for c in near:
            if ok(*c):
                return c
    for cx, cy in lb.candidates(g):
        if keep is not None and pos == 'free' and box(cx - d, cy - d, cx + d, cy + d).intersects(keep.buffer(6)):
            continue
        if ok(cx, cy):
            return (cx, cy)
    return None


def place(R, spec, sym, decor, size, pos):
    labels, _ = lb.place(R, spec, decor)
    by = {p['id']: p for p in labels}
    dec = unary_union([g.buffer(1.0) for _, g in decor]) if decor else None
    out, miss = {}, []
    for rid, ch in sym.items():
        c = place_one(rid, R[rid], by.get(rid), size, pos, dec)
        if c:
            out[rid] = (round(c[0], 2), round(c[1], 2), ch)
        else:
            miss.append(spec['names'][rid])
    return out, miss


def font_css():
    return f"@font-face{{font-family:'{SYM_FONT}';src:url('{SYM_URL}') format('truetype')}}"


def region_symbols(layout):
    d = json.loads((ROOT / 'board' / 'derived' / f'{layout}.json').read_text(encoding='utf-8'))
    return {k: v['glyph'] for k, v in d['region_symbols'].items()}


def svg_layer(R, spec, decor=()):
    """символы полотна: [(область, центр)], слой SVG; не поместившиеся — в списке"""
    pts, miss = place(R, spec, region_symbols(spec['layout']), list(decor), SIZE, POS)
    fs = SIZE / CAP
    out = ''.join(f'<text x="{x:.2f}" y="{y + SIZE / 2:.2f}" font-family="{SYM_FONT}" font-size="{fs:.2f}" '
                  f'text-anchor="middle" fill="{FILL}" fill-opacity="{FILL_OPACITY:g}">'
                  f'<title>{spec["names"][rid]}</title>{ch}</text>' for rid, (x, y, ch) in sorted(pts.items()))
    return out, miss


def shade(hexc, dL):
    import palette as P
    L, C, h = P.lab2lch(P.hex2lab(hexc))
    lab = P.lch2lab(max(5, min(95, L + dL)), C * 0.9, h)
    while not P.in_gamut(lab):
        lab = P.lch2lab(lab[0], P.lab2lch(lab)[1] * 0.95, h)
    return P.rgb2hex(P.lab2rgb(lab))


def build_test(out):
    import boardview as bv
    import slice5 as s5
    data, boards = {}, []
    for lay in LAYOUTS:
        R, sym = load(lay)
        spec = bc.load_spec(lay)
        decor = [(None, g) for _, g in s5.load_decor()]
        data[lay] = {}
        for size in SIZES:
            for pos in POSITIONS:
                pts, miss = place(R, spec, sym, decor, size, pos)
                data[lay][f'{size}-{pos}'] = {'pts': pts, 'miss': miss}
        svg = (GEO / f'board-{lay}.svg').read_text(encoding='utf-8')
        inner = re.sub(r'^.*?<svg[^>]*>', '', svg, flags=re.S).rsplit('</svg>', 1)[0]
        inner = re.sub(r'<title>.*?</title>', '', inner, count=1, flags=re.S)
        inner = inner.replace('id="blend"', f'id="blend-{lay}"').replace('url(#blend)', f'url(#blend-{lay})') \
                     .replace('id="ocmask"', f'id="ocmask-{lay}"').replace('url(#ocmask)', f'url(#ocmask-{lay})')
        boards.append(f'<g class="board" data-lay="{lay}">{inner}</g>')
    tone = {rid: (shade(c, -24) if P_L(c) > 45 else shade(c, 24)) for rid, c in bv.COLOUR.items()}
    W, H = bc.CANVAS
    radios = lambda name, opts, sel: ''.join(
        f'<label><input type="radio" name="{name}" value="{v}"{" checked" if v == sel else ""}> {t}</label>' for v, t in opts)
    js = json.dumps({'pos': data, 'tone': tone}, ensure_ascii=False)
    html = f'''<!doctype html>
<html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Символы регионов</title>
<style>
@font-face{{font-family:'{SYM_FONT}';src:url('{SYM_URL}') format('truetype')}}
:root{{--bg:#f4f1ea;--fg:#23211d;--mut:#6b665c;--line:#d6d0c4;--card:#fbf9f4}}
@media (prefers-color-scheme:dark){{:root:not([data-theme=light]){{--bg:#1d1c1a;--fg:#ece8df;--mut:#a39d91;--line:#3a3833;--card:#252421}}}}
body{{margin:0;background:var(--bg);color:var(--fg);font:15px/1.45 system-ui,sans-serif}}
main{{max-width:1700px;margin:0 auto;padding:16px}}
h1{{font-size:20px;margin:0 0 4px}} p.sub{{margin:0 0 12px;color:var(--mut)}}
.ctl{{display:grid;grid-template-columns:max-content 1fr;gap:6px 16px;align-items:baseline;margin:0 0 10px;padding:10px 12px;border:1px solid var(--line);border-radius:8px;background:var(--card)}}
.ctl .k{{color:var(--mut);font-weight:600}} .ctl .row{{display:flex;flex-wrap:wrap;gap:4px 18px}}
.ctl label{{display:inline-flex;gap:6px;align-items:center;cursor:pointer}}
@media (max-width:900px){{.ctl{{grid-template-columns:1fr}}}}
svg#map{{width:100%;height:auto;display:block;border-radius:6px}}
#miss{{color:#b3261e}}
</style></head><body><main>
<h1>Символы регионов — варианты</h1>
<p class="sub">Этап 3 COMP-C-03, шаг 3. Страница собрана <code>board/tools/symbols.py test</code> поверх принятых полотен (цвета, подписи — <code>D-099</code>–<code>D-101</code>).
Символ идёт по материку (SPEC §8.2): капля — Америки, пламя — Европа и Азия, вагонетка — Африка и Австралия; у океанов и Антарктиды символа нет.
Знак не заходит на границу области, на острова и на подпись.</p>
<div class="ctl">
<span class="k">Полотно</span><div class="row">{radios('lay', [(l, l) for l in LAYOUTS], 'MC-5P')}</div>
<span class="k">Высота знака</span><div class="row">{radios('size', [(str(s), f'{s} мм') for s in SIZES], '16')}</div>
<span class="k">Где</span><div class="row">{radios('pos', [('left', 'рядом с подписью, слева'), ('above', 'над подписью'), ('free', 'отдельно, в глубине области')], 'left')}</div>
<span class="k">Оформление</span><div class="row">{radios('style', [('outline', 'белый с тёмной обводкой, как подписи'), ('plate', 'на круглой серо-зелёной плашке'), ('tone', 'тоном области, темнее или светлее заливки'), ('dark', 'тёмный полупрозрачный, «водяной знак»')], 'outline')}</div>
</div>
<p class="sub" id="miss"></p>
<svg id="map" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:g} {H:g}">
{''.join(boards)}
<g id="sym"></g>
</svg>
</main>
<script>
const D={js};
const NS='http://www.w3.org/2000/svg', $=id=>document.getElementById(id);
const val=n=>document.querySelector(`input[name=${{n}}]:checked`).value;
function el(t,a,p){{const e=document.createElementNS(NS,t);for(const k in a)e.setAttribute(k,a[k]);if(p)p.appendChild(e);return e}}
function draw(){{
  const lay=val('lay'), size=+val('size'), pos=val('pos'), st=val('style');
  document.querySelectorAll('.board').forEach(b=>b.style.display=b.dataset.lay===lay?'':'none');
  const V=D.pos[lay][size+'-'+pos], G=$('sym');G.innerHTML='';
  const fs=size/{CAP}, d=size*{PLATE_K};
  for(const rid in V.pts){{
    const [cx,cy,ch]=V.pts[rid], g=el('g',{{}},G);
    if(st==='plate')el('circle',{{cx,cy,r:d/2,fill:'{lb.PLATE}',stroke:'{lb.PLATE_LINE}','stroke-width':0.4}},g);
    const a={{x:cx,y:cy+size/2,'font-family':'{SYM_FONT}','font-size':fs,'text-anchor':'middle'}};
    if(st==='outline')Object.assign(a,{{fill:'#ffffff',stroke:'#1c1a17','stroke-width':fs*0.09,'paint-order':'stroke','stroke-linejoin':'round'}});
    else if(st==='plate')a.fill='#ffffff';
    else if(st==='tone')a.fill=D.tone[rid];
    else a.fill='rgba(20,18,16,.45)';
    el('text',a,g).textContent=ch;
  }}
  $('miss').textContent=V.miss.length?('Не поместились: '+V.miss.join(', ')):'';
}}
document.querySelectorAll('input[type=radio]').forEach(e=>e.onchange=draw);
document.fonts.load('10px {SYM_FONT}').then(draw);
</script></body></html>
'''
    Path(out).write_text(html, encoding='utf-8')
    return out


def P_L(c):
    import palette as P
    return P.hex2lab(c)[0]


def main(argv):
    if len(argv) >= 2 and argv[1] == 'test':
        print(build_test(GEO / 'symbols-test.html'))
        return 0
    print(__doc__)
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv))
