"""Мастер значка «бочка нефти» — глиф T шрифта print/Fonts/Oil Wars.ttf (ICON-045).

    python oil-barrel.py      # пишет oil-barrel.svg и oil-barrel-cyan.svg рядом

НЕ обозначение нефти как ресурса: ресурс — капля в кольце, глиф R (ICON-001).
Бочка сохранена про запас (решение Alek 26.09.2026): в тексте размером
2,7 мм она читается хуже капли, поэтому на компоненты не ставится.

Упрощённая пиктограмма по мотивам бочки у трека (`print/Faction-Card-A/barrel.png`):
крышка с белым эллипсом и два сквозных обруча, обода выступают за боковину.
Деталь не тоньше ~48 единиц из 700 — чтобы пережить печать в размере текста.
Из SVG в шрифт: `print/Fonts/OilWars/add_glyph.py <шрифт> oil-barrel.svg T`.

Координаты в единицах глифа: высота 700, y вниз. Зависимости: shapely.
"""
import math
from pathlib import Path
from shapely.geometry import Polygon, box
from shapely.ops import unary_union
from shapely.geometry.polygon import orient

HERE = Path(__file__).parent
H = 700


def ell(cx, cy, rx, ry, n=360):
    return Polygon([(cx + rx * math.cos(2 * math.pi * i / n),
                     cy + ry * math.sin(2 * math.pi * i / n)) for i in range(n)])


def arc_band(W, cy, ry, t):
    """Полоса толщиной t вдоль нижней дуги эллипса (cx=W/2, rx=W/2) — обруч."""
    xs = [W * i / 200 for i in range(201)]
    def y(x):
        u = (x - W / 2) / (W / 2)
        return cy + ry * math.sqrt(max(0.0, 1 - u * u))
    up = [(x, y(x) - t / 2) for x in xs]
    dn = [(x, y(x) + t / 2) for x in xs]
    return Polygon([(-10, up[0][1])] + up + [(W + 10, up[-1][1]), (W + 10, dn[-1][1])]
                   + dn[::-1] + [(-10, dn[0][1])])


def barrel(W, lid_ry, rim, hoops, gap, round_r, hoop_ry, flare=0, rib=0):
    """W — ширина по ободам; lid_ry — полувысота крышки; rim — толщина обода
    крышки; hoops — y обручей у боковины; gap — толщина просвета; hoop_ry —
    прогиб обруча; flare — насколько обод-обруч выступает за боковину;
    rib — высота выступающего обода над и под просветом."""
    cx = W / 2
    bw = W - 2 * flare                                   # ширина корпуса
    lid = ell(cx, lid_ry, W / 2, lid_ry)
    body = box(flare, lid_ry, W - flare, H - lid_ry).union(
        ell(cx, H - lid_ry, bw / 2, lid_ry))
    if flare:                                            # выступающие обода
        for yc in hoops:
            body = body.union(arc_band(W, yc, hoop_ry, gap + 2 * rib)
                              .intersection(box(0, 0, W, H)))
    solid = body
    for yc in hoops:
        solid = solid.difference(arc_band(W, yc, hoop_ry, gap))
    # скруглить углы сегментов у боковин
    solid = solid.buffer(-round_r, join_style=1).buffer(round_r, join_style=1)
    solid = unary_union([solid, lid])
    inner = ell(cx, lid_ry, W / 2 - rim * 1.35, lid_ry - rim)
    return solid.difference(inner).simplify(0.2)


def to_path(geom):
    polys = [geom] if geom.geom_type == 'Polygon' else list(geom.geoms)
    out = []
    for p in polys:
        p = orient(p, sign=-1.0)
        for r in [p.exterior] + list(p.interiors):
            c = list(r.coords)[:-1]
            out.append('M' + 'L'.join(f'{x:.1f} {y:.1f}' for x, y in c) + 'Z')
    return ''.join(out)


PARAMS = dict(W=476, lid_ry=70, rim=40, hoops=[268, 468], gap=48, round_r=18,
              hoop_ry=50, flare=24, rib=40)

g = barrel(**PARAMS)
x0, y0, x1, y1 = g.bounds
assert abs(y0) < 1 and abs(y1 - H) < 1, g.bounds
W = PARAMS['W']
for name, color, title in (('oil-barrel.svg', '#000000', 'чёрный'),
                           ('oil-barrel-cyan.svg', '#11C5FF', 'голубой')):
    (HERE / name).write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}">\n'
        f'  <!-- Бочка нефти — {title}. Глиф T шрифта Oil Wars (ICON-045),\n'
        f'       НЕ значок ресурса: нефть как ресурс — глиф R (ICON-001).\n'
        f'       Собирается oil-barrel.py. Цвет меняется одним атрибутом fill. -->\n'
        f'  <path fill="{color}" d="{to_path(g)}"/>\n</svg>\n', encoding='utf-8')
print(f'oil-barrel.svg: {W} × {H}')
