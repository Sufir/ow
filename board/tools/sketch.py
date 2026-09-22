# -*- coding: utf-8 -*-
"""
sketch.py — грубый эскиз игрового поля «Нефтяных войн», проход 0.

Расположение и пропорции, без арта и без точной нарезки. Четыре SVG на полотне
900 x 550 мм:

  sketch-classic-geo.svg     классическая (цилиндрическая), честная география
  sketch-classic-target.svg  она же + площади по ТЗ-ЭСКИЗ-КАРТЫ §5
  sketch-polar-geo.svg       южно-полярная азимутальная, честная география
  sketch-polar-target.svg    раскладка по слоям и азимутам ТЗ §4, площади по §5

Вход : registry/map/geo/world-game.geojson, world-base.geojson (бассейны),
       registry/map/derived/MC-5P.json (граф 21 области)
Выход: registry/map/sketch/

Геометрия руками не правится — правятся константы в этом файле.
Запуск: python tools/sketch.py [all|check]
"""
import json, math, os, sys
from shapely.geometry import shape, box, Polygon, MultiPolygon, Point
from shapely.ops import unary_union

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                      # board/
MAPD = ROOT
GEO  = os.path.join(MAPD, "geo")
OUT  = os.path.join(MAPD, "sketch")

# ------------------------------------------------------------------ полотно
SHEET_W, SHEET_H = 900.0, 550.0
TECH = 10.0
MAP_W, MAP_H = SHEET_W - 2*TECH, SHEET_H - 2*TECH        # 880 x 530 = 4664 см²
CX, CY = SHEET_W/2, SHEET_H/2
FRAME_END, FRAME_SIDE = 60.0, 10.0                        # рамка Арктики, ТЗ §3
IN_W, IN_H = MAP_W - 2*FRAME_END, MAP_H - 2*FRAME_SIDE    # 760 x 510
R_ANT   = 77.0            # ТЗ §4.2, слой 0
SIMPLIFY = 0.7            # градусы; «эскиз без детализации»
MIN_PIECE = 0.6           # градус² — мелочь в эскиз не идёт

# ------------------------------------------------------------------ области
# id: (рус. имя, цель см² ТЗ §5, слой ТЗ §4.2, азимут φ ТЗ §4.4, положение в паре)
REG = {
 "MR-OC-ARC" : ("Сев. Ледовитый ок.", 788, "рамка", None, None),
 "MR-OC-NPAC": ("Сев. Тихий ок.",      300, "сектор",   0, None),
 "MR-OC-NATL": ("Сев. Атлантика", 300, "сектор", 180, None),
 "MR-OC-SPAC": ("Юг Тихого ок.",         250, 1,  85, None),
 "MR-OC-SATL": ("Юг Атлантики", 250, 1, 202, None),
 "MR-OC-IND" : ("Индийский ок.",          304, 1, 336, None),
 "MR-SH-ANT" : ("Антарктида",               185, 0, None, None),
 "MR-L5-NAMW": ("Запад Сев. Америки",       175, 3,  68, "out"),
 "MR-L5-CAM" : ("Центр. Америка",      150, 3,  68, "in"),
 "MR-L5-NAME": ("Восток Сев. Америки",      165, 3, 111, "out"),
 "MR-L5-SAMW": ("Запад Южн. Америки",       160, 2, 112, "in"),
 "MR-L5-SAME": ("Восток Южн. Америки",      160, 2, 135, None),
 "MR-L5-AUS" : ("Австралия",                150, 2,  22, None),
 "MR-L5-NZL" : ("Новая Зеландия",           150, 2,  49, None),
 "MR-R5-AFRW": ("Западная Африка",          170, 2, 225, None),
 "MR-R5-EUR" : ("Европа",                   175, 3, 228, "in"),
 "MR-R5-SCA" : ("Скандинавия",              155, 3, 244, "out"),
 "MR-R5-AFRE": ("Восточная Африка",         165, 2, 261, None),
 "MR-R5-ARB" : ("Аравия",    165, 2, 289, None),
 "MR-R5-ASIN": ("Северная Азия",            165, 3, 309, "out"),
 "MR-R5-ASIS": ("Южная Азия",               180, 2, 327, "in"),
}
OCEANS = {"MR-OC-ARC","MR-OC-NPAC","MR-OC-NATL","MR-OC-SPAC","MR-OC-SATL","MR-OC-IND"}
BASIN  = {"MR-OC-ARC":"arctic","MR-OC-NPAC":"north_pacific","MR-OC-NATL":"north_atlantic",
          "MR-OC-SPAC":"south_pacific","MR-OC-SATL":"south_atlantic","MR-OC-IND":"indian"}
FRAME_TOUCH = ["MR-OC-NPAC","MR-L5-NAMW","MR-L5-NAME","MR-OC-NATL","MR-R5-SCA","MR-R5-ASIN"]

COL = {
 "MR-L5-NAMW":"#c98f5a","MR-L5-NAME":"#e0b183","MR-L5-CAM":"#a96b34",
 "MR-L5-SAMW":"#7ea055","MR-L5-SAME":"#a9c67d",
 "MR-R5-EUR" :"#a95fa0","MR-R5-SCA" :"#cb96c5",
 "MR-R5-AFRW":"#d6b552","MR-R5-AFRE":"#e8d489",
 "MR-R5-ASIN":"#cf6a56","MR-R5-ASIS":"#e69384","MR-R5-ARB":"#b04b3c",
 "MR-L5-AUS" :"#4e9d8a","MR-L5-NZL" :"#8ac9b9",
 "MR-SH-ANT" :"#e3eaee",
 "MR-OC-ARC" :"#102b3a","MR-OC-NPAC":"#2b6a86","MR-OC-NATL":"#3a7d94",
 "MR-OC-SPAC":"#1f5a78","MR-OC-SATL":"#46889c","MR-OC-IND" :"#317architecture",
}
COL["MR-OC-IND"] = "#265f80"

# ---------------------------------------------------- нарезка (грубая, §домены)
def _nam(g):
    cam = Polygon([(-125,32),(-100,32),(-100,24),(-50,24),(-50,-8),(-125,-8)])
    c, rest = g.intersection(cam), g.difference(cam)
    w = box(-180,-90,-100,90)
    return {"MR-L5-CAM":c, "MR-L5-NAMW":rest.intersection(w), "MR-L5-NAME":rest.difference(w)}
def _sam(g):
    west = Polygon([(-100,13),(-79,9),(-60,-55),(-100,-60)])
    return {"MR-L5-SAMW":g.intersection(west), "MR-L5-SAME":g.difference(west)}
def _eur(g):
    n = box(-40,55,90,90)
    return {"MR-R5-SCA":g.intersection(n), "MR-R5-EUR":g.difference(n)}
def _afr(g):
    east = Polygon([(25+0.9*l, l) for l in range(-40,41,2)] + [(120,40),(120,-40)])
    return {"MR-R5-AFRE":g.intersection(east), "MR-R5-AFRW":g.difference(east)}
def _asi(g):
    arb = box(25,12,63,45); n = box(-180,40,180,90)
    a, rest = g.intersection(arb), g.difference(arb)
    return {"MR-R5-ARB":a, "MR-R5-ASIN":rest.intersection(n), "MR-R5-ASIS":rest.difference(n)}
def _aus(g):
    nz = box(158,-60,180,10)
    return {"MR-L5-NZL":g.intersection(nz), "MR-L5-AUS":g.difference(nz)}
SPLIT = {"north_america":_nam,"south_america":_sam,"europe":_eur,
         "africa":_afr,"asia":_asi,"australia":_aus}

def polys_of(g):
    if g is None or g.is_empty: return []
    if isinstance(g, Polygon): return [g] if g.area > 0 else []
    out = []
    for x in getattr(g, "geoms", []): out += polys_of(x)
    return out

def schematize(g, tol=SIMPLIFY, minp=MIN_PIECE):
    ps = [p for p in polys_of(g) if p.area >= minp]
    if not ps: ps = sorted(polys_of(g), key=lambda p:-p.area)[:1]
    ps = [p.simplify(tol, preserve_topology=True) for p in ps]
    ps = [p for p in ps if not p.is_empty and p.area > 0]
    return MultiPolygon(ps) if len(ps) != 1 else ps[0]

def build_regions(schematic=True):
    game = json.load(open(os.path.join(GEO,"world-game.geojson"), encoding="utf-8"))
    base = json.load(open(os.path.join(GEO,"world-base.geojson"), encoding="utf-8"))
    gf = {f["properties"]["id"]: shape(f["geometry"]) for f in game["features"]}
    bf = {f["properties"]["id"]: shape(f["geometry"]) for f in base["features"]}
    out = {}
    for cont, fn in SPLIT.items(): out.update(fn(gf[cont]))
    out["MR-SH-ANT"] = gf["antarctica"]
    for rid, bid in BASIN.items(): out[rid] = gf["ocean"].intersection(bf[bid])
    if schematic:
        for k in list(out):
            out[k] = schematize(out[k], minp=(MIN_PIECE if k not in OCEANS else 0.05))
    return out

# ------------------------------------------------------------------ проекции
def prj_classic(lon, lat):
    return (TECH + (lon+180.0)/360.0*MAP_W, TECH + (90.0-lat)/180.0*MAP_H)

LON0 = 60.0     # меридиан, смотрящий вверх; подобран так, чтобы география легла
                # на азимуты ТЗ §4.4 с наименьшим разбросом
def rect_radius(dx, dy, hw=MAP_W/2, hh=MAP_H/2):
    t = float("inf")
    if abs(dx) > 1e-12: t = min(t, hw/abs(dx))
    if abs(dy) > 1e-12: t = min(t, hh/abs(dy))
    return t
LAT_TOP = 72.0    # севернее — рамка Северного Ледовитого, в эскиз не идёт
def prj_polar(lon, lat):
    """южно-полярная азимутальная равнопромежуточная (формула world-base),
       радиально растянутая во внутреннее поле 760x510; рамка рисуется отдельно"""
    r = min(max((lat+90.0)/(LAT_TOP+90.0), 0.0), 1.0)
    a = math.radians(lon - LON0)
    dx, dy = math.sin(a), -math.cos(a)
    R = rect_radius(dx, dy, IN_W/2, IN_H/2)
    return (CX + r*R*dx, CY + r*R*dy)

def densify(ring, step=1.0):
    out = []
    for i in range(len(ring)-1):
        x0,y0 = ring[i]; x1,y1 = ring[i+1]
        n = max(1, int(max(abs(x1-x0), abs(y1-y0))/step))
        for k in range(n): out.append((x0+(x1-x0)*k/n, y0+(y1-y0)*k/n))
    out.append(ring[-1]); return out

def project(geom, prj, dens=None):
    """геометрия из градусов в миллиметры полотна"""
    res = []
    for p in polys_of(geom):
        def pr(r):
            pts = list(r.coords)
            if dens: pts = densify(pts, dens)
            return [prj(x,y) for x,y in pts]
        try:
            q = Polygon(pr(p.exterior), [pr(i) for i in p.interiors])
            if not q.is_valid: q = q.buffer(0)
            res += polys_of(q)
        except Exception: pass
    return unary_union(res) if res else Polygon()

def path_of(geom):
    d = []
    for p in polys_of(geom):
        for ring in [p.exterior] + list(p.interiors):
            d.append("M " + " L ".join("%.2f %.2f"%c for c in ring.coords) + " Z")
    return " ".join(d)
def cm2(geom): return sum(p.area for p in polys_of(geom))/100.0

# ------------------------------------------------------------------ SVG
FONT = "DejaVu Sans, Arial, sans-serif"
BG, INK, DIM = "#0b1418", "#eef4f7", "#8ea0aa"

def head(title, sub):
    return ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %g %g" width="%gmm" height="%gmm">'
            % (SHEET_W,SHEET_H,SHEET_W,SHEET_H),
            '<title>%s</title>' % title,
            '<style>text{font-family:%s}.lb{font-size:7.2px;font-weight:600;text-anchor:middle}'
            '.lv{font-size:5px;text-anchor:middle}.hd{font-size:11px;font-weight:700;fill:%s}'
            '.hs{font-size:5.6px;fill:%s}.ft{font-size:5px;fill:%s}'
            '.ld{stroke:#93a7b2;stroke-width:0.35;fill:none}</style>' % (FONT,INK,DIM,DIM),
            '<rect width="%g" height="%g" fill="%s"/>' % (SHEET_W,SHEET_H,BG)]

HEAD_W, HEAD_H = 470.0, 40.0
def foot(parts, title, subs, note=""):
    n = len(subs)
    h = 13 + 6.8*n
    parts.append('<rect x="%g" y="%g" width="%g" height="%g" rx="2.5" fill="#0b1418" fill-opacity="0.9" '
                 'stroke="#2b4250" stroke-width="0.5"/>' % (TECH+3, TECH+3, HEAD_W, h+5))
    parts.append('<text class="hd" x="%g" y="%g">%s</text>' % (TECH+8, TECH+14, title))
    for i,s in enumerate(subs):
        parts.append('<text class="hs" x="%g" y="%g">%s</text>' % (TECH+8, TECH+24+6.8*i, s))
    parts.append('<rect x="%g" y="%g" width="%g" height="%g" fill="none" stroke="#44606e" '
                 'stroke-width="0.6" stroke-dasharray="4 3"/>' % (TECH,TECH,MAP_W,MAP_H))
    parts.append('<text class="ft" x="%g" y="%g" text-anchor="end">полотно %g×%g мм · прямоугольник карты '
                 '%g×%g мм = %g см² · штриховая линия — технологическое поле %g мм%s</text>'
                 % (SHEET_W-TECH-3, SHEET_H-TECH-4, SHEET_W,SHEET_H,MAP_W,MAP_H,MAP_W*MAP_H/100,TECH,note))
    parts.append('</svg>')
    return "\n".join(parts)

def lab_w(it):  return max(len(it[2])*4.35, len(it[3])*2.75) + 7
def place_labels(items, h=14.5):
    """items: [(x,y,name,val,dark)] -> раздвинуть подписи, вернуть с якорями"""
    P = [[x,y] for x,y,_,_,_ in items]
    A = [(x,y) for x,y,_,_,_ in items]
    W = [lab_w(it) for it in items]
    for _ in range(500):
        moved = False
        for i in range(len(P)):
            for j in range(i+1,len(P)):
                w = (W[i]+W[j])/2
                dx, dy = P[j][0]-P[i][0], P[j][1]-P[i][1]
                ox, oy = w-abs(dx), h-abs(dy)
                if ox > 0 and oy > 0:
                    moved = True
                    if oy/h < ox/w:
                        s = (oy/2+0.3)*(1 if dy>=0 else -1); P[i][1]-=s; P[j][1]+=s
                    else:
                        s = (ox/2+0.3)*(1 if dx>=0 else -1); P[i][0]-=s; P[j][0]+=s
        for i,p in enumerate(P):
            p[0] = min(max(p[0], TECH+W[i]/2+2), SHEET_W-TECH-W[i]/2-2)
            p[1] = min(max(p[1], TECH+16), SHEET_H-TECH-13)
            if p[0] < TECH+HEAD_W+W[i]/2 and p[1] < TECH+HEAD_H+h/2:
                p[1] = TECH+HEAD_H+h/2
        if not moved: break
    return [(P[i][0],P[i][1],A[i][0],A[i][1])+items[i][2:] for i in range(len(items))]

def draw_labels(parts, items):
    for x,y,ax,ay,name,val,dark in place_labels(items):
        if (x-ax)**2+(y-ay)**2 > 40:
            parts.append('<path class="ld" d="M %.1f %.1f L %.1f %.1f"/>' % (ax,ay,x,y-3.5))
            parts.append('<circle cx="%.1f" cy="%.1f" r="0.9" fill="#93a7b2"/>' % (ax,ay))
        col = "#0d1a22" if dark else INK
        if not dark:
            parts.append('<text class="lb" x="%.1f" y="%.1f" stroke="%s" stroke-width="1.6" '
                         'stroke-opacity=".45" fill="none">%s</text>' % (x,y,BG,name))
        parts.append('<text class="lb" x="%.1f" y="%.1f" fill="%s">%s</text>' % (x,y,col,name))
        parts.append('<text class="lv" x="%.1f" y="%.1f" fill="%s" fill-opacity=".9">%s</text>'
                     % (x,y+5.6,col,val))

def rep_point(geom):
    ps = sorted(polys_of(geom), key=lambda p:-p.area)
    if not ps: return None
    p = ps[0].representative_point(); return (p.x, p.y)

# --------------------------------------------------------------- листы 1 и 3
def sheet_geo(regs, prj, dens, fname, title, subs, guide=None, frame=False):
    p = head(title, subs); proj = {}
    fr = None
    if frame:
        fr = box(TECH,TECH,TECH+MAP_W,TECH+MAP_H).difference(rrect(IN_W, IN_H, 28))
        p.append('<path d="%s" fill="%s" stroke="%s" stroke-width="0.7"/>'
                 % (path_of(fr), COL["MR-OC-ARC"], BG))
    for rid in list(OCEANS)+[r for r in REG if r not in OCEANS]:
        if frame and rid == "MR-OC-ARC":
            proj[rid] = fr; continue
        g = project(regs[rid], prj, dens)
        if frame: g = g.difference(fr)
        proj[rid] = g
        p.append('<path d="%s" fill="%s" stroke="%s" stroke-width="0.6" stroke-linejoin="round"/>'
                 % (path_of(g), COL[rid], BG))
    if guide: p += guide
    items, stats = [], {}
    for rid,(ru,tgt,lay,phi,mode) in REG.items():
        a = cm2(proj[rid]); stats[rid] = a
        pt = rep_point(proj[rid])
        if frame and rid == "MR-OC-ARC": pt = (TECH+FRAME_END/2, CY)
        if pt: items.append((pt[0],pt[1],ru,"%d см² → %d · ×%.1f" % (round(a),tgt,tgt/max(a,.1)),
                             rid not in OCEANS or rid=="MR-SH-ANT"))
    draw_labels(p, items)
    open(os.path.join(OUT,fname),"w",encoding="utf-8").write(foot(p,title,subs))
    return stats, proj

# ------------------------------------------------------- лист 2: цель, классика
def sheet_classic_target(regs, fname):
    title = "Эскиз поля — классическая проекция, целевые площади ТЗ §5"
    subs = ["Тонкий контур — честная география. Заливка — та же область, раздутая вокруг своего центра до целевой площади.",
            "Наложения показывают, где площадь брать неоткуда. Это не раскладка, а замер разрыва между географией и ТЗ."]
    p = head(title, subs)
    p.append('<rect x="%g" y="%g" width="%g" height="%g" fill="#132833"/>' % (TECH,TECH,MAP_W,MAP_H))
    items = []
    for rid,(ru,tgt,lay,phi,mode) in REG.items():
        g = project(regs[rid], prj_classic)
        a = cm2(g)
        if rid in OCEANS:            # океаны ужимаются, их рисуем контуром
            p.append('<path d="%s" fill="none" stroke="%s" stroke-width="0.5" stroke-opacity=".55"/>'
                     % (path_of(g), COL[rid]))
            continue
        p.append('<path d="%s" fill="none" stroke="#7f95a1" stroke-width="0.45" stroke-opacity=".8"/>'
                 % path_of(g))
        k = math.sqrt(tgt/max(a,1e-6))
        parts_ = []
        for q in polys_of(g):
            if q.area < 3.0: continue
            c = q.centroid
            parts_.append(Polygon([(c.x+(x-c.x)*k, c.y+(y-c.y)*k) for x,y in q.exterior.coords]))
        blown = unary_union(parts_) if parts_ else g
        p.append('<path d="%s" fill="%s" fill-opacity=".55" stroke="%s" stroke-width="0.7"/>'
                 % (path_of(blown), COL[rid], COL[rid]))
        pt = rep_point(blown) or rep_point(g)
        items.append((pt[0],pt[1],ru,"%d → %d см² · ×%.1f" % (round(a),tgt,tgt/max(a,.1)), False))
    for rid in OCEANS:
        g = project(regs[rid], prj_classic); a = cm2(g); ru,tgt = REG[rid][0], REG[rid][1]
        pt = rep_point(g)
        if pt: items.append((pt[0],pt[1],ru,"%d → %d см² · ×%.2f" % (round(a),tgt,tgt/max(a,.1)), False))
    draw_labels(p, items)
    open(os.path.join(OUT,fname),"w",encoding="utf-8").write(foot(p,title,subs))

# --------------------------------------------- лист 4: раскладка ТЗ §4 (полярная)
# Строение по ТЗ §4.2–4.6:
#   слой 0  — диск r 77, Антарктида
#   слой 1  — кольцо южных океанов; каждый на TONGUE своей площади уходит языком в слой 2
#   секторы — Север Тихого (φ 0) и Север Атлантического (φ 180), от кольца 1 до рамки
#   слой 2  — внутреннее кольцо между секторами: 8 областей суши + три языка
#   слой 3  — внешнее кольцо до рамки: 6 областей суши, две парами «внутрь/наружу»
#   слой 4  — рамка Северного Ледовитого
# Отсюда рамки касаются ровно шесть областей: два сектора, NAMW, NAME, SCA, ASIN (§4.5),
# а Центральная Америка и Европа до края не доходят (§4.6).
TONGUE = 0.25
ARC1_IN  = [("one","MR-L5-AUS"),("one","MR-L5-NZL"),("tongue","MR-OC-SPAC"),
            ("one","MR-L5-SAMW"),("one","MR-L5-SAME")]
ARC1_OUT = [("pair","MR-L5-CAM","MR-L5-NAMW"),("one","MR-L5-NAME")]
ARC2_IN  = [("tongue","MR-OC-SATL"),("one","MR-R5-AFRW"),("one","MR-R5-AFRE"),
            ("one","MR-R5-ARB"),("one","MR-R5-ASIS"),("tongue","MR-OC-IND")]
ARC2_OUT = [("pair","MR-R5-EUR","MR-R5-SCA"),("one","MR-R5-ASIN")]
def sl_area(s):
    if s[0]=="tongue": return REG[s[1]][1]*TONGUE
    if s[0]=="pair":   return REG[s[1]][1] + REG[s[2]][1]
    return REG[s[1]][1]

def rrect(w, h, r):
    return box(CX-w/2, CY-h/2, CX+w/2, CY+h/2).buffer(-r).buffer(r, join_style=1)

def Rdir(t):
    d = (math.cos(math.radians(t)), math.sin(math.radians(t)))
    return rect_radius(d[0], d[1], IN_W/2, IN_H/2)

def fan(t0, t1, R=800.0, step=0.4):
    pts, n = [(CX,CY)], max(2, int(abs(t1-t0)/step))
    for i in range(n+1):
        t = math.radians(t0 + (t1-t0)*i/n)
        pts.append((CX+R*math.cos(t), CY+R*math.sin(t)))
    return Polygon(pts)

def band(rin, rout, t0, t1, step=0.4):
    """кольцевой кусок; rin/rout — функции угла, мм"""
    pts, n = [], max(2, int(abs(t1-t0)/step))
    for i in range(n+1):
        t = t0+(t1-t0)*i/n; a = math.radians(t); d = (math.cos(a), math.sin(a))
        r = rout(t); pts.append((CX+r*d[0], CY+r*d[1]))
    for i in range(n, -1, -1):
        t = t0+(t1-t0)*i/n; a = math.radians(t); d = (math.cos(a), math.sin(a))
        r = rin(t);  pts.append((CX+r*d[0], CY+r*d[1]))
    return Polygon(pts).buffer(0)

STEP = 0.15
def sweep(t0, need, rin, rout):
    """докуда крутить угол, чтобы кусок кольца набрал need см²"""
    acc, t = 0.0, t0
    while acc < need and t-t0 < 361:
        a = 0.5*(rout(t)**2 - rin(t)**2)*math.radians(STEP)/100.0
        acc += a; t += STEP
    return t
def band_cm2(t0, t1, rin, rout):
    acc, t = 0.0, t0
    while t < t1:
        acc += 0.5*(rout(t)**2 - rin(t)**2)*math.radians(STEP)/100.0; t += STEP
    return acc
def split_f(t0, t1, rin, rout, need_in):
    """граница двух колец: полоса снаружи постоянной ширины d, внутри — остаток.
    Постоянная ширина, а не постоянная доля: иначе внешнее кольцо у углов полотна
    раздувается, а у длинных краёв вырождается в нитку."""
    lo = 0.0
    hi = min(rout(t0+i*(t1-t0)/48) - rin(t0+i*(t1-t0)/48) for i in range(49))
    for _ in range(46):
        d = (lo+hi)/2
        mid = lambda t: max(rout(t)-d, rin(t))
        if band_cm2(t0, t1, rin, mid) < need_in: hi = d
        else: lo = d
    d = (lo+hi)/2
    return lambda t: max(rout(t)-d, rin(t))

def sheet_polar_target(fname):
    title = "Эскиз поля — южно-полярная раскладка ТЗ §4, целевые площади ТЗ §5"
    subs = ["Слой 0 — Антарктида в центре; слой 1 — кольцо южных океанов; слой 2 и слой 3 — суша; слой 4 — рамка Северного Ледовитого.",
            "Север Тихого и Север Атлантического — секторы от кольца 1 до рамки на торцах. Рамки касаются ровно шесть областей (§4.5).",
            "Порядок по азимуту — ТЗ §4.4, площади — ТЗ §5. Границы условные: это чертёж раскладки, а не нарезка."]
    p = head(title, subs)
    inner = rrect(IN_W, IN_H, 28)
    frame = box(TECH,TECH,TECH+MAP_W,TECH+MAP_H).difference(inner)
    ring_t = sum(REG[r][1] for r in ("MR-OC-SPAC","MR-OC-SATL","MR-OC-IND"))*(1-TONGUE)
    R1 = math.sqrt(R_ANT**2 + ring_t*100/math.pi)
    rin_f, rout_f = (lambda t: R1), Rdir
    zone_total = band_cm2(0, 360, rin_f, rout_f)

    a1i = sum(sl_area(x) for x in ARC1_IN);  a1o = sum(sl_area(x) for x in ARC1_OUT)
    a2i = sum(sl_area(x) for x in ARC2_IN);  a2o = sum(sl_area(x) for x in ARC2_OUT)
    sec = REG["MR-OC-NPAC"][1]
    k = zone_total/(2*sec + a1i + a1o + a2i + a2o)      # нормировка под реальную площадь зоны

    drawn = {}
    t = -STEP; acc = 0.0                                # центрируем сектор Севера Тихого на 0°
    while acc < sec*k/2:
        acc += 0.5*(Rdir(t)**2 - R1**2)*math.radians(STEP)/100.0; t -= STEP
    t_np0 = t
    t_np1 = sweep(t_np0, sec*k, rin_f, rout_f)
    drawn["MR-OC-NPAC"] = band(rin_f, rout_f, t_np0, t_np1)
    t_a1 = sweep(t_np1, (a1i+a1o)*k, rin_f, rout_f)
    t_na1 = sweep(t_a1, sec*k, rin_f, rout_f)
    drawn["MR-OC-NATL"] = band(rin_f, rout_f, t_a1, t_na1)

    for (t0, t1, SIN, SOUT, ai) in ((t_np1, t_a1, ARC1_IN, ARC1_OUT, a1i),
                                  (t_na1, t_np0+360, ARC2_IN, ARC2_OUT, a2i)):
        mid = split_f(t0, t1, rin_f, rout_f, ai*k)      # граница слоёв 2 и 3
        for (lo, hi, slots) in ((rin_f, mid, SIN), (mid, rout_f, SOUT)):
            c = t0
            for sl in slots:
                c2 = sweep(c, sl_area(sl)*k, lo, hi)
                w = band(lo, hi, c, min(c2, t1))
                if sl[0] == "pair":
                    m2 = split_f(c, min(c2,t1), lo, hi, REG[sl[1]][1]*k)
                    drawn[sl[1]] = band(lo, m2, c, min(c2,t1))
                    drawn[sl[2]] = band(m2, hi, c, min(c2,t1))
                else:
                    drawn[sl[1]] = w
                c = c2
    # кольцо слоя 1: каждый кусок содержит свой язык
    tongues = []
    for rid in ("MR-OC-SPAC","MR-OC-SATL","MR-OC-IND"):
        g = drawn[rid]; c = g.centroid
        tongues.append((rid, math.degrees(math.atan2(c.y-CY, c.x-CX)) % 360))
    tongues.sort(key=lambda x: x[1])
    ring = Point(CX,CY).buffer(R1, resolution=256).difference(Point(CX,CY).buffer(R_ANT, resolution=256))
    bnd = []
    for i,(rid,c0) in enumerate(tongues):
        rid2, c1 = tongues[(i+1) % 3]
        if i == 2: c1 += 360
        w0, w1 = REG[rid][1], REG[rid2][1]
        bnd.append(c0 + (c1-c0)*w0/(w0+w1))
    for i,(rid,_) in enumerate(tongues):
        b0 = bnd[i-1] - (360 if i == 0 else 0)
        drawn[rid] = unary_union([drawn[rid], ring.intersection(fan(b0, bnd[i]))])
    drawn["MR-SH-ANT"] = Point(CX,CY).buffer(R_ANT, resolution=256)
    drawn["MR-OC-ARC"] = frame

    for rid in list(OCEANS)+[r for r in REG if r not in OCEANS]:
        g = drawn.get(rid)
        if g is None or g.is_empty: continue
        p.append('<path d="%s" fill="%s" stroke="%s" stroke-width="0.8" stroke-linejoin="round"/>'
                 % (path_of(g), COL[rid], BG))
    for r,lb in ((R_ANT,"0"), (R1,"1")):
        p.append('<circle cx="%g" cy="%g" r="%.1f" fill="none" stroke="#ffffff" stroke-opacity=".2" '
                 'stroke-width="0.5" stroke-dasharray="3 3"/>' % (CX,CY,r))
    p.append('<path d="%s" fill="none" stroke="#ffffff" stroke-opacity=".25" stroke-width="0.6" '
             'stroke-dasharray="4 3"/>' % path_of(inner))
    stats, items = {}, []
    for rid,(ru,tgt,lay,phi,mode) in REG.items():
        g = drawn.get(rid)
        if g is None or g.is_empty: continue
        a = cm2(g); stats[rid] = a
        pt = (TECH+MAP_W-FRAME_END/2, CY) if rid=="MR-OC-ARC" else rep_point(g)
        items.append((pt[0],pt[1],ru,"%d см² · цель %d" % (round(a),tgt), rid not in OCEANS))
    draw_labels(p, items)
    open(os.path.join(OUT,fname),"w",encoding="utf-8").write(foot(p,title,subs))
    return stats, drawn, R1

# ------------------------------------------------------------------ смежности
def adjacency(proj, tol=0.8):
    """пары областей, касающихся на полотне (зазор меньше tol мм)"""
    ids = list(proj); got = set()
    for i in range(len(ids)):
        for j in range(i+1, len(ids)):
            a, b = proj[ids[i]], proj[ids[j]]
            if a.is_empty or b.is_empty: continue
            if a.distance(b) < tol: got.add(tuple(sorted((ids[i], ids[j]))))
    return got

def truth_edges():
    d = json.load(open(os.path.join(MAPD,"derived","MC-5P.json"), encoding="utf-8"))
    return set(tuple(sorted(e)) for e in d["edge_list"])

def inradius(geom):
    """наибольший вписанный круг, мм — мера SPEC-BOARD §5.2"""
    ps = sorted(polys_of(geom), key=lambda q:-q.area)
    if not ps: return 0.0
    lo, hi = 0.0, 260.0
    for _ in range(34):
        m = (lo+hi)/2
        if ps[0].buffer(-m).is_empty: hi = m
        else: lo = m
    return lo

# ------------------------------------------------------------------ main
def main():
    os.makedirs(OUT, exist_ok=True)
    regs = build_regions()
    clip = box(-180,-90,180,LAT_TOP)
    polar = {k: schematize(unary_union(polys_of(v)).buffer(0).intersection(clip), tol=1.3, minp=1.2)
             for k,v in regs.items()}
    guide = ['<circle cx="%g" cy="%g" r="%g" fill="none" stroke="#ffffff" stroke-opacity=".13" '
             'stroke-width="0.5" stroke-dasharray="4 4"/>' % (CX,CY,IN_H/2)]
    a1, p1 = sheet_geo(regs, prj_classic, None, "sketch-classic-geo.svg",
        "Эскиз поля — классическая проекция, честная география",
        ["world-game.geojson, плоская прямоугольная проекция. Контуры упрощены до эскизного вида (допуск %.1f°)." % SIMPLIFY,
         "По вертикали растянута ×1.20, чтобы занять 880×530: честная цилиндрическая даёт 2:1, а полотно 1.66:1.",
         "Нарезка на 21 область — грубая, по доменам долгота/широта. Это не раскладка, а проверка расположения."])
    a3, p3 = sheet_geo(polar, prj_polar, 1.0, "sketch-polar-geo.svg",
        "Эскиз поля — южно-полярная проекция, честная география",
        ["Азимутальная равнопромежуточная от Южного полюса (формула world-base), радиально растянутая во внутреннее поле 760×510.",
         "Северный Ледовитый — рамка по ТЗ §3: 60 мм на торцах, 10 мм сверху и снизу. Севернее 72° с.ш. в эскиз не идёт.",
         "Штриховая окружность — честный круг Ø510: всё за ней растянуто к торцам. Край листа и есть край карты, швов и разрезов нет."],
        guide, frame=True)
    sheet_classic_target(regs, "sketch-classic-target.svg")
    a4, d4, R1 = sheet_polar_target("sketch-polar-target.svg")

    truth = truth_edges()
    rep = []
    rep.append("%-28s %6s %8s %8s %8s" % ("область","цель","классика","полярная","раскладка"))
    tot = [0,0,0,0]
    for rid,(ru,tgt,lay,phi,mode) in REG.items():
        rep.append("%-28s %6d %8.0f %8.0f %8.0f" % (ru,tgt,a1.get(rid,0),a3.get(rid,0),a4.get(rid,0)))
        tot[0]+=tgt; tot[1]+=a1.get(rid,0); tot[2]+=a3.get(rid,0); tot[3]+=a4.get(rid,0)
    rep.append("%-28s %6.0f %8.0f %8.0f %8.0f" % ("ИТОГО",*tot))
    rep.append("прямоугольник карты %.0f см²; R1 кольца %.1f мм" % (MAP_W*MAP_H/100, R1))
    rep.append("")
    rep.append("Форма областей в раскладке ТЗ §4 — вписанный круг, мм (SPEC-BOARD §6: норма 85+, минимум 55)")
    rr = sorted(((inradius(d4[r]), REG[r][0], REG[r][2]) for r in d4 if r in REG), key=lambda x:x[0])
    for v,nm,lay in rr:
        rep.append("   %-22s слой %-6s %5.0f мм%s" % (nm, lay, v, "   ← ниже минимума" if v < 55 else ""))
    for nm, pr in (("классика", p1), ("полярная", p3), ("раскладка ТЗ §4", d4)):
        got = adjacency(pr)
        rep.append("смежности %s: реестр 56, эскиз даёт %d из них, лишних %d"
                   % (nm, len(got & truth), len(got - truth)))
        rep.append("   нет в эскизе: " + ", ".join(sorted("%s—%s"%e for e in (truth-got))))
    print("\n".join(rep))
    open(os.path.join(OUT,"sketch-report.txt"),"w",encoding="utf-8").write("\n".join(rep)+"\n")

if __name__ == "__main__":
    main()
