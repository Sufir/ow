"""
glue.py — полотна MC-3P, MC-4P-A, MC-4P-B склейкой областей MC-5P.

Этап 2 компонента COMP-C-03. Источник — board/geo/board-MC-5P.geojson (slice5.py, D-097).

Как собирается (SPEC-BOARD §3.1, §3.2):
  1. Область стороны «3» — объединение областей MC-5P, у которых parent = её id
     (board/regions.yaml): Северная Америка = Запад + Восток + Центральная Америка и т. д.
     Щели мельче 1 мм², оставшиеся от округления на бывших внутренних границах,
     засыпаются; координаты — до 0,001 мм, как в MC-5P.
  2. Океаны, Антарктида и области стороны «5» — те же полигоны MC-5P без изменений,
     до вершины. Это проверяется при каждой сборке.
  3. Состав полотна — board/derived/<раскладка>.json: MC-3P — обе половины «3»,
     MC-4P-A — слева «3», справа «5», MC-4P-B — наоборот.

Своей геометрии у сборки нет. Внешний контур материков правится в classic.py,
деление стороны «5» — в slice5.py; после этого пересобираются все четыре полотна:
    python3 board/tools/classic.py all
    python3 board/tools/slice5.py all
    python3 board/tools/glue.py all

Запуск из корня репозитория:
    python3 board/tools/glue.py all              три полотна, проверка boardcheck, запись
    python3 board/tools/glue.py all MC-3P        одно полотно
    python3 board/tools/glue.py fast             то же без укладки фигур (быстро), файлы пишутся

Пишет board/geo/board-<раскладка>.geojson (источник истины), .svg, .html.
Файлы пишутся и при красной проверке; код возврата 1, если есть отказы.
Зависимости: numpy, shapely, scipy, pyyaml (+ boardcheck.py, boardview.py, slice5.py рядом).
"""
import json
import sys
from datetime import date
from pathlib import Path

from shapely.geometry import Polygon, shape
from shapely.ops import unary_union

sys.path.insert(0, str(Path(__file__).resolve().parent))
import boardcheck as bc  # noqa: E402
import boardview as bv  # noqa: E402
import slice5 as s5  # noqa: E402

GEO = bv.GEO
SRC = GEO / 'board-MC-5P.geojson'

LAYOUTS = {   # раскладка: (кто на поле, заголовок страницы)
    'MC-3P': ('на троих', 'Поле на троих (MC-3P): обе половины — сторона «3»'),
    'MC-4P-A': ('на четверых, вариант A', 'Поле на четверых, вариант A (MC-4P-A): слева сторона «3», справа «5»'),
    'MC-4P-B': ('на четверых, вариант B', 'Поле на четверых, вариант B (MC-4P-B): слева сторона «5», справа «3»'),
}
NOTE = ('Сборка склейкой: область стороны «3» — объединение областей MC-5P с тем же родителем '
        '(<code>regions.yaml</code> → <code>parent</code>); океаны, Антарктида и области стороны «5» — '
        'те же полигоны, что в <code>board-MC-5P</code>. Своей геометрии у сборки нет: очертания правятся '
        'в <code>classic.py</code> и <code>slice5.py</code>.')


def load_source():
    fc = json.loads(SRC.read_text(encoding='utf-8'))
    feats = {f['properties']['id']: f for f in fc['features']}
    return fc, feats


def fill_small_holes(g):
    """щели мельче 1 мм² внутри склеенной области (следы округления на бывших границах) — засыпать"""
    out, filled = [], 0.0
    for p in bc.polys(g):
        keep = []
        for r in p.interiors:
            a = Polygon(r).area
            if a < bc.AREA_TOL:
                filled += a
            else:
                keep.append(r)
        out.append(Polygon(p.exterior, keep))
    return unary_union(out), filled


def glue(layout, feats, spec5):
    """области раскладки: сторона «3» — склейка детей, прочее — полигоны MC-5P как есть"""
    spec = bc.load_spec(layout)
    R, kids_of, log = {}, {}, []
    for rid in spec['areas']:
        if rid in feats:
            R[rid] = shape(feats[rid]['geometry'])
            continue
        kids = [k for k in spec5['areas'] if spec5['group'][k] == rid and k != rid]
        if not kids:
            raise SystemExit(f'{rid}: в MC-5P нет областей с parent = {rid} — проверить regions.yaml')
        u = unary_union([shape(feats[k]['geometry']) for k in kids])
        g, filled = fill_small_holes(u)
        g = bv.rounded(g)
        R[rid], kids_of[rid] = g, kids
        d = g.symmetric_difference(u).area
        log.append(f'{spec["names"][rid]} = {" + ".join(spec5["names"][k] for k in kids)}: '
                   f'A {g.area / 100:.1f} см², кусков {len(bc.polys(g))}; от объединения детей отличается на {d:.2f} мм²'
                   + (f' (засыпано щелей {filled:.2f} мм²)' if filled > 0.005 else ''))
    return spec, R, kids_of, log


def geojson(layout, R, spec, rows, kids_of, fc5):
    d = json.loads((bc.BOARD / 'derived' / f'{layout}.json').read_text(encoding='utf-8'))
    m5 = fc5['metadata']
    return {
        'type': 'FeatureCollection',
        'metadata': {
            'name': f'oil-wars-board-{layout}', 'layout': layout, 'generated': date.today().isoformat(),
            'generator': 'board/tools/glue.py', 'source': 'board/geo/board-MC-5P.geojson',
            'base': m5['base'], 'graph': f'board/derived/{layout}.json',
            'sides': {'left': d['left'], 'right': d['right']},
            'coordinateSystem': m5['coordinateSystem'], 'wrap': m5['wrap'], 'rings': m5['rings'],
            'glue': {rid: kids for rid, kids in kids_of.items()},
        },
        'features': [bv.feature(rid, R[rid], spec, rows.get(rid, {})) for rid in spec['areas']],
    }


def same_as_source(fc, feats):
    """SPEC §3.1: всё, что не склеено, совпадает с MC-5P до вершины"""
    bad, n = [], 0
    for f in fc['features']:
        rid = f['properties']['id']
        if rid in feats:
            n += 1
            if f['geometry'] != feats[rid]['geometry']:
                bad.append(rid)
    return n, bad


def build_one(layout, fc5, feats, spec5, with_pack):
    who, heading = LAYOUTS[layout]
    spec, R, kids_of, log = glue(layout, feats, spec5)
    fc = geojson(layout, R, spec, {}, kids_of, fc5)
    n, bad = same_as_source(fc, feats)
    if bad:
        log.append(f'ОШИБКА: не совпадают с MC-5P: {", ".join(bad)}')
    else:
        log.append(f'океаны, Антарктида и области стороны «5» ({n}) — те же полигоны, что в MC-5P, до вершины')
    chk = bc.run(fc, spec, str(s5.BASE), with_pack=with_pack)
    print(f'\n===== {layout} — поле {who}')
    for t in log:
        print('  лог  ' + t)
    nf = bc.print_results(chk) + len(bad)
    for rid in spec['areas']:
        r = chk['rows'][rid]
        print(f'   {rid:12} A {r["A"]:6.1f}  U {r["U"]:6.1f}  U/A {r["UA_main"]:.3f}  N {r.get("N25", "-")}/{r.get("N40", "-")}/{r.get("N60", "-")}'
              f'  связн {r["share"] * 100:3.0f}%{"  ★" if r["start"] else ""}')
    fc = geojson(layout, R, spec, chk['rows'], kids_of, fc5)
    nodes = {rid: bv.node_point(R[rid], s5.SEEDS[rid][0] if rid in s5.SEEDS else None) for rid in spec['areas']}
    decor = []
    for cont, g in s5.load_decor():
        r5 = s5.decor_region(cont, g)
        decor.append((r5 if r5 in spec['type'] else spec5['group'][r5], g))
    out = GEO / f'board-{layout}'
    out.with_suffix('.geojson').write_text(json.dumps(fc, ensure_ascii=False), encoding='utf-8')
    out.with_suffix('.svg').write_text(bv.svg(R, spec, f'Нефтяные войны — поле {who} ({layout}), склейка MC-5P', decor=decor), encoding='utf-8')
    out.with_suffix('.html').write_text(bv.html(
        R, s5.load_base()[0], spec, chk, log, nodes=nodes, decor=decor,
        page_title=f'Поле {layout} — склейка', heading=heading, generator='board/tools/glue.py',
        log_title='Лог склейки', note=NOTE), encoding='utf-8')
    print(f'Записано: {out.name}.geojson, .svg, .html')
    return nf


def main(argv):
    cmd = argv[1] if len(argv) > 1 else 'all'
    layouts = argv[2:] or list(LAYOUTS)
    if cmd not in ('all', 'fast') or any(lay not in LAYOUTS for lay in layouts):
        print(__doc__)
        return 2
    fc5, feats = load_source()
    spec5 = bc.load_spec('MC-5P')
    nf = 0
    for lay in layouts:
        nf += build_one(lay, fc5, feats, spec5, with_pack=(cmd == 'all'))
    print(f'\nВсего отказов по {len(layouts)} полотнам: {nf}')
    return 1 if nf else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
