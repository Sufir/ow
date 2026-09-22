# -*- coding: utf-8 -*-
"""
layout.py — раскладка игрового поля «Нефтяных войн», проход 1.

Не проекция. Материк берётся как ЖЁСТКИЙ силуэт (масштаб + поворот + перенос,
без деформации) и кладётся на своё место вокруг Антарктиды южной оконечностью
к центру. Океан — то, что осталось между материками; он и решает граф.

Решения Alek 2026-09-18:
  - граф MC-5P (56 рёбер) соблюдается на 100 %, это не обсуждается;
  - силуэты и расстановка жёсткие и максимально узнаваемые, пока не ломают граф;
  - материки развёрнуты югом к центру;
  - рабочая часть — всё полотно 900 x 550, технологическое поле 5 мм сверх него.
"""
import json, math, os, sys
from shapely.geometry import shape, box, Polygon, MultiPolygon, Point, LineString
from shapely.ops import unary_union
from shapely.affinity import rotate, scale as shp_scale, translate

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)                      # board/
MAPD = ROOT
GEO  = os.path.join(MAPD, "geo")
OUT  = os.path.join(MAPD, "sketch")

# ------------------------------------------------------------------ полотно
W, H = 900.0, 550.0            # рабочая часть = всё полотно
TECH = 5.0                     # технологическое поле СВЕРХ рабочей части
CX, CY = W/2, H/2
SHEET_W, SHEET_H = W + 2*TECH, H + 2*TECH
BUDGET = W*H/100.0             # 4950 см²
R_CORE = 100.0   # ядро: Антарктида плюс кольцо южных океанов, суша не заходит                 # ядро под Антарктиду и кольцо южных океанов, мм
FR_END, FR_SIDE = 58.0, 10.0   # рамка Арктики: торцы / длинные края, мм
IN_W, IN_H = W-2*FR_END, H-2*FR_SIDE
# Прирост полотна (4664 -> 4950) целиком уходит океанам: суша остаётся ровно
# по ТЗ §5, её доля падает с 53 % до 50 % — тот самый запас, о котором шла речь.
FR_ARC = None                  # площадь рамки считается из FR_END/FR_SIDE

# ------------------------------------------------------------------ области
REG = {   # id: (имя, цель ТЗ §5 см², материк)
 "MR-OC-ARC" : ("Сев. Ледовитый ок.", 788, None),
 "MR-OC-NPAC": ("Сев. Тихий ок.",     300, None),
 "MR-OC-NATL": ("Сев. Атлантика",     300, None),
 "MR-OC-SPAC": ("Юг Тихого ок.",      250, None),
 "MR-OC-SATL": ("Юг Атлантики",       250, None),
 "MR-OC-IND" : ("Индийский ок.",      304, None),
 "MR-SH-ANT" : ("Антарктида",         185, "antarctica"),
 "MR-L5-NAMW": ("Запад Сев. Америки", 175, "north_america"),
 "MR-L5-CAM" : ("Центр. Америка",     150, "north_america"),
 "MR-L5-NAME": ("Восток Сев. Америки",165, "north_america"),
 "MR-L5-SAMW": ("Запад Южн. Америки", 160, "south_america"),
 "MR-L5-SAME": ("Восток Южн. Америки",160, "south_america"),
 "MR-L5-AUS" : ("Австралия",          150, "australia"),
 "MR-L5-NZL" : ("Новая Зеландия",     150, "australia"),
 "MR-R5-AFRW": ("Западная Африка",    170, "africa"),
 "MR-R5-AFRE": ("Восточная Африка",   165, "africa"),
 "MR-R5-EUR" : ("Европа",             175, "europe"),
 "MR-R5-SCA" : ("Скандинавия",        155, "europe"),
 "MR-R5-ARB" : ("Аравия",             165, "asia"),
 "MR-R5-ASIN": ("Северная Азия",      165, "asia"),
 "MR-R5-ASIS": ("Южная Азия",         180, "asia"),
}
OCEANS = [r for r,v in REG.items() if v[2] is None]
LAND   = [r for r,v in REG.items() if v[2] is not None]
LAND_K = 0.92      # доля суши: 53 % ТЗ -> 50 % при новом полотне -> 46 % здесь.
                   # Alek: 53 % — ориентир, а не жёсткое ограничение. Разница уходит
                   # океанам и даёт материкам зазор, без которого они трутся боками.
_ARC = (W*H - (W-2*FR_END)*(H-2*FR_SIDE))/100.0          # площадь рамки, см²
_LAND = sum(v[1] for k,v in REG.items() if v[2] is not None)
_OC   = sum(v[1] for k,v in REG.items() if v[2] is None and k != "MR-OC-ARC")
_KOC  = (BUDGET - _LAND*0.92 - _ARC)/_OC                       # океанам — весь прирост
def target(rid):
    if rid == "MR-OC-ARC": return _ARC
    return REG[rid][1]*(LAND_K if REG[rid][2] else _KOC)

COL = {
 "MR-L5-NAMW":"#c98f5a","MR-L5-NAME":"#e0b183","MR-L5-CAM":"#a96b34",
 "MR-L5-SAMW":"#7ea055","MR-L5-SAME":"#a9c67d",
 "MR-R5-EUR" :"#a95fa0","MR-R5-SCA" :"#cb96c5",
 "MR-R5-AFRW":"#d6b552","MR-R5-AFRE":"#e8d489",
 "MR-R5-ASIN":"#cf6a56","MR-R5-ASIS":"#e69384","MR-R5-ARB":"#b04b3c",
 "MR-L5-AUS" :"#4e9d8a","MR-L5-NZL" :"#8ac9b9","MR-SH-ANT":"#e3eaee",
 "MR-OC-ARC" :"#13293a","MR-OC-NPAC":"#2f7f9e","MR-OC-NATL":"#4a6fa5",
 "MR-OC-SPAC":"#1d6f6f","MR-OC-SATL":"#5b8bbd","MR-OC-IND":"#265f80",
}

# --------------------------------------------------- единицы суши и расстановка
# Единица — жёсткая фигура: масштабируется, поворачивается и переносится целиком.
# Внутренние границы областей единицей НЕ являются: их можно двигать, силуэт
# от этого не меняется. Поэтому площади областей набираются сдвигом реза.
#
#   src   — материк из world-game.geojson
#   keep  — рамка долгота/широта, если из материка берётся только часть
#   lon   — меридиан, по которому единица ставится на колесо
#   az    — экранный азимут места (градусы, 0 = вправо, рост по часовой)
#   r_in  — на каком радиусе стоит ближняя к центру точка силуэта
#   spin  — доворот силуэта, градусы (плюс = по часовой)
#   cuts  — последовательные резы: (область, азимут нормали в локальной рамке).
#           Локальная рамка: x на восток, y на юг. Область = {точка·n > d},
#           d подбирается под целевую площадь. Последняя область — остаток.
LON0 = 60.0
UNITS = {
 "australia":     dict(src="australia", keep=(100,-50,158,5), lon=134, az=100, mode="inner", r_in=126, spin=0,
                       regs=["MR-L5-AUS"], cuts=[]),
 "new_zealand":   dict(src="australia", keep=(158,-50,180,5), lon=170, az=134, mode="inner", r_in=130, spin=0, frac=0.30, glue=0.05, fat=0.22,
                       regs=["MR-L5-NZL"], cuts=[]),
 "north_america": dict(src="north_america", fat=0.115, lon=-98, az=184, mode="outer", back=4, spin=25,
                       regs=["MR-L5-CAM","MR-L5-NAMW","MR-L5-NAME"],
                       cuts=[("MR-L5-CAM",120),("MR-L5-NAMW",180)]),
 "south_america": dict(src="south_america", lon=-62, az=222, mode="inner", r_in=126, spin=0,
                       regs=["MR-L5-SAMW","MR-L5-SAME"], cuts=[("MR-L5-SAMW",160)]),
 "africa":        dict(src="africa", lon=20,  az=296, mode="inner", r_in=150, spin=0,
                       regs=["MR-R5-AFRW","MR-R5-AFRE"], cuts=[("MR-R5-AFRE",40)]),
 "europe":        dict(src="europe", lon=22,  az=330, mode="inner", r_in=240, spin=0,
                       regs=["MR-R5-EUR","MR-R5-SCA"], cuts=[("MR-R5-SCA",270)]),
 "asia":          dict(src="asia", fat=0.135, lon=95,  az= 52, mode="inner", r_in=152, spin=0,
                       regs=["MR-R5-ARB","MR-R5-ASIN","MR-R5-ASIS"],
                       cuts=[("MR-R5-ARB",140),("MR-R5-ASIN",270)]),
}
def theta(lon):   # экранный угол, y вниз, 0 = вправо, рост по часовой
    return lon - LON0 - 90.0
def Rdir(t, hw=W/2, hh=H/2):
    d = (math.cos(math.radians(t)), math.sin(math.radians(t)))
    r = float("inf")
    if abs(d[0]) > 1e-12: r = min(r, hw/abs(d[0]))
    if abs(d[1]) > 1e-12: r = min(r, hh/abs(d[1]))
    return r

def polys_of(g):
    if g is None or g.is_empty: return []
    if isinstance(g, Polygon): return [g] if g.area > 0 else []
    out = []
    for x in getattr(g,"geoms",[]): out += polys_of(x)
    return out
def clean(g, tol=0.55, minp=0.9):
    ps = [p for p in polys_of(unary_union(polys_of(g)).buffer(0)) if p.area >= minp]
    if not ps: ps = sorted(polys_of(g), key=lambda p:-p.area)[:1]
    ps = [p.simplify(tol, preserve_topology=True) for p in ps]
    ps = [p for p in ps if not p.is_empty and p.area > 0]
    return unary_union(ps).buffer(0)

def rrect(w, h, r):
    return box(CX-w/2, CY-h/2, CX+w/2, CY+h/2).buffer(-r).buffer(r, join_style=1)

def halfplane(a_deg, d, R=4000.0):
    """{ p·n > d }, n = (cos a, sin a); большой прямоугольник, сдвинутый на d по n"""
    a = math.radians(a_deg); n = (math.cos(a), math.sin(a)); t = (-n[1], n[0])
    base = [(n[0]*d + t[0]*R, n[1]*d + t[1]*R), (n[0]*d - t[0]*R, n[1]*d - t[1]*R),
            (n[0]*(d+R) - t[0]*R, n[1]*(d+R) - t[1]*R), (n[0]*(d+R) + t[0]*R, n[1]*(d+R) + t[1]*R)]
    return Polygon(base)

def cut_to_area(geom, a_deg, want):
    """сдвинуть рез по нормали так, чтобы отрезанная часть дала want см²"""
    xs = [c for p in polys_of(geom) for c in p.exterior.coords]
    a = math.radians(a_deg)
    proj = [x*math.cos(a) + y*math.sin(a) for x,y in xs]
    lo, hi = min(proj)-1, max(proj)+1
    for _ in range(46):
        d = (lo+hi)/2
        if cm2(geom.intersection(halfplane(a_deg, d))) > want: lo = d
        else: hi = d
    d = (lo+hi)/2
    hp = halfplane(a_deg, d)
    return geom.intersection(hp), geom.difference(hp)

# ---------------------------------------- локальная проекция «истинной формы»
def azeq(lon0, lat0):
    """азимутальная равнопромежуточная с центром в (lon0,lat0): силуэт без искажения.
       (lon,lat) -> (x на восток, y на юг), единицы — радианы дуги."""
    p0, l0 = math.radians(lat0), math.radians(lon0)
    s0, c0 = math.sin(p0), math.cos(p0)
    def f(lon, lat):
        ph, dl = math.radians(lat), math.radians(lon)-l0
        cc = max(-1.0, min(1.0, s0*math.sin(ph) + c0*math.cos(ph)*math.cos(dl)))
        c = math.acos(cc)
        k = 1.0 if abs(c) < 1e-9 else c/math.sin(c)
        return (k*math.cos(ph)*math.sin(dl),
                -k*(c0*math.sin(ph) - s0*math.cos(ph)*math.cos(dl)))
    return f
def project(geom, f):
    res = []
    for p in polys_of(geom):
        try:
            q = Polygon([f(x,y) for x,y in p.exterior.coords],
                        [[f(x,y) for x,y in i.coords] for i in p.interiors])
            if not q.is_valid: q = q.buffer(0)
            res += polys_of(q)
        except Exception: pass
    return unary_union(res).buffer(0) if res else Polygon()
def cm2(g): return sum(p.area for p in polys_of(g))/100.0

# ------------------------------------------------------------------ сборка
KEEP_FRAC = 0.07   # кусок меньше этой доли самого крупного в единице — в эскиз не идёт
def main_body(g, frac=KEEP_FRAC, glue=0.0):
    """главное тело единицы: архипелаги и мелочь отбрасываются.
    Игровая область — территория, а не строгий контур суши, и мелкий остров,
    раздутый в десять раз, только съедает полотно."""
    ps = sorted(polys_of(g), key=lambda q:-q.area)
    if not ps: return g
    keep = [q for q in ps if q.area >= ps[0].area*frac]
    u = unary_union(keep).buffer(0)
    if glue > 0:                      # склеить близкие куски в одно тело
        u = u.buffer(glue).buffer(-glue*0.85)
    return u

def fatten(g, k=0.10):
    """морфологическое замыкание: глубокие бухты и изрезанность подбираются,
    силуэт остаётся своим. k — доля от корня площади."""
    a = sum(q.area for q in polys_of(g))
    if a <= 0: return g
    r = k*math.sqrt(a)
    u = unary_union(polys_of(g)).buffer(r, join_style=1).buffer(-r*0.72, join_style=1)
    return unary_union(polys_of(u)).buffer(0)

def build(az_over=None, back_over=None, cut_over=None):
    src = json.load(open(os.path.join(GEO,"world-game.geojson"), encoding="utf-8"))
    src = {f["properties"]["id"]: shape(f["geometry"]) for f in src["features"]}
    out, units, base = {}, {}, {}
    for name, u in UNITS.items():
        g = clean(src[u["src"]])
        if u.get("keep"): g = g.intersection(box(*u["keep"])).buffer(0)
        ps = sorted(polys_of(g), key=lambda q:-q.area)
        lat0 = ps[0].centroid.y
        shp = project(g, azeq(u["lon"], lat0))
        shp = main_body(shp, u.get("frac", KEEP_FRAC), u.get("glue", 0.0))
        shp = fatten(shp, u.get("fat", 0.055))
        tgt = sum(target(r) for r in u["regs"])
        sc = math.sqrt(tgt/cm2(shp))
        c0 = shp.centroid
        shp = shp_scale(shp, sc, sc, origin=(c0.x,c0.y))           # в миллиметры полотна
        rest, parts = shp, {}
        cuts = (cut_over or {}).get(name) or [a for _, a in u["cuts"]]
        for (rid, _), ang in zip(u["cuts"], cuts):
            take, rest = cut_to_area(rest, ang, target(rid))
            parts[rid] = take
        left = [r for r in u["regs"] if r not in dict(u["cuts"])]
        parts[left[0]] = rest
        base[name] = {rid: translate(v, -shp.centroid.x, -shp.centroid.y)
                      for rid, v in parts.items()}       # центроид в нуле, без поворота
        t = (az_over or {}).get(name, u["az"]); a = t + 90.0 + u["spin"]
        c1 = shp.centroid
        rot = {rid: translate(rotate(v, a, origin=(c1.x,c1.y)), -c1.x, -c1.y)
               for rid, v in parts.items()}                       # центроид в нуле
        d = (math.cos(math.radians(t)), math.sin(math.radians(t)))
        pts = [(x,y) for v in rot.values() for q in polys_of(v) for x,y in q.exterior.coords]
        pr = [x*d[0]+y*d[1] for x,y in pts]
        if u.get("mode","outer") == "outer":
            L = Rdir(t, W/2-6, H/2-6) - (back_over or {}).get(name, u.get("back",0.0)) - max(pr)
        else:
            L = u.get("r_in", 140.0) - min(pr)
        pos = [CX + L*d[0] + u.get("nudge",(0,0))[0],
               CY + L*d[1] + u.get("nudge",(0,0))[1]]
        near = min(math.hypot(x+CX+L*d[0]-CX, y+CY+L*d[1]-CY) for x,y in pts) if pts else 999
        if near < R_CORE: L += (R_CORE - near)
        pos = [CX + L*d[0] + u.get("nudge",(0,0))[0],
               CY + L*d[1] + u.get("nudge",(0,0))[1]]
        xs = [x for x,y in pts]; ys = [y for x,y in pts]
        MRG = 6.0
        f0,g0 = MRG, MRG; f1,g1 = W-MRG, H-MRG
        pos[0] = min(max(pos[0], f0-min(xs)), f1-max(xs))
        pos[1] = min(max(pos[1], g0-min(ys)), g1-max(ys))
        units[name] = dict(parts=rot, pos=pos, az=t, alpha=a%360,
                           scale=sc, regs=u["regs"])
    for name, un in units.items():
        for rid, v in un["parts"].items():
            out[rid] = translate(v, un["pos"][0], un["pos"][1])
    def polar(lon, lat):
        rr = (lat+90.0)/180.0; u = math.radians(lon-LON0)
        return (rr*math.sin(u), -rr*math.cos(u))
    ant = project(clean(src["antarctica"], tol=0.8, minp=2.0), polar)
    ant = fatten(main_body(ant, 0.25), 0.085)      # убрать шельфовые шипы: центр карты
                                                   # должен быть компактным телом
    sc = math.sqrt(target("MR-SH-ANT")/cm2(ant)); c = ant.centroid
    out["MR-SH-ANT"] = translate(shp_scale(ant, sc, sc, origin=(c.x,c.y)), CX-c.x, CY-c.y)
    return out, units, base

GAP = 2.5        # зазор между единицами суши, мм
TANG = 0.30      # насколько свободно единица гуляет вбок от своего луча
def relax(units, iters=400):
    """развести единицы, не ломая ни азимут, ни очертания: двигаются только позиции"""
    names = list(units)
    home = {n: list(units[n]["pos"]) for n in names}
    field = box(CX-IN_W/2, CY-IN_H/2, CX+IN_W/2, CY+IN_H/2)
    core  = Point(CX,CY).buffer(R_CORE, resolution=64)
    for it in range(iters):
        moved = 0.0
        shp = {n: translate(unary_union([q for v in units[n]["parts"].values()
                                         for q in polys_of(v)]).buffer(0),
                            units[n]["pos"][0], units[n]["pos"][1]) for n in names}
        for i in range(len(names)):
            for j in range(i+1, len(names)):
                a, b = shp[names[i]], shp[names[j]]
                dist = a.distance(b)
                if dist >= GAP: continue
                ca, cb = a.centroid, b.centroid
                vx, vy = cb.x-ca.x, cb.y-ca.y
                L = math.hypot(vx,vy) or 1.0
                push = (GAP - dist)*0.55 if dist > 0 else (GAP + 6.0)
                dx, dy = vx/L*push/2, vy/L*push/2
                for nm, sx, sy in ((names[i],-dx,-dy), (names[j],dx,dy)):
                    ax = math.radians(units[nm]["az"]); rd = (math.cos(ax), math.sin(ax))
                    rad = sx*rd[0] + sy*rd[1]
                    tx, ty = sx - rad*rd[0], sy - rad*rd[1]
                    units[nm]["pos"][0] += rad*rd[0] + tx*TANG
                    units[nm]["pos"][1] += rad*rd[1] + ty*TANG
                moved += push
        for n in names:                     # не залезать в центр и не выходить за поле
            g = shp[n]; c = g.centroid
            if g.intersects(core):
                vx, vy = c.x-CX, c.y-CY; L = math.hypot(vx,vy) or 1.0
                units[n]["pos"][0] += vx/L*2.0; units[n]["pos"][1] += vy/L*2.0; moved += 2
            x0,y0,x1,y1 = g.bounds
            f0,g0,f1,g1 = field.bounds
            if x0 < f0: units[n]["pos"][0] += (f0-x0); moved += f0-x0
            if x1 > f1: units[n]["pos"][0] -= (x1-f1); moved += x1-f1
            if y0 < g0: units[n]["pos"][1] += (g0-y0); moved += g0-y0
            if y1 > g1: units[n]["pos"][1] -= (y1-g1); moved += y1-g1
            pass
        if moved < 0.4: break
    return units

# ------------------------------ автоподгонка азимутов: развести налегающие пары
# Коридоры под океанские клинья резервируются: в них суша не заходит.
LANES = {"MR-OC-NPAC": (62, 96), "MR-OC-NATL": (248, 286)}
def unit_shape(u):
    return unary_union([q for v in u["parts"].values() for q in polys_of(v)]).buffer(0)
def spread(iters=34, step=0.55, gap=4.0):
    az = {n: UNITS[n]["az"] for n in UNITS}
    names = list(UNITS)
    best, best_bad = dict(az), 1e18
    for it in range(iters):
        regs, units, _ = build(az)
        sh = {n: translate(unit_shape(u), u["pos"][0], u["pos"][1]) for n,u in units.items()}
        bad = 0.0; force = {n: 0.0 for n in names}
        core = Point(CX,CY).buffer(R_CORE, resolution=64)
        for n in names:                      # заход в ядро — брак: там Антарктида и кольцо
            ci = sh[n].intersection(core).area/100.0
            if ci > 0.2:
                bad += ci*6.0
                cor = min((34,146,214,326), key=lambda c: abs((c-az[n]+180)%360-180))
                force[n] += max(-6.0, min(6.0, ((cor-az[n]+180)%360-180)*0.25))
        for i in range(len(names)):
            for j in range(i+1, len(names)):
                a, b = sh[names[i]], sh[names[j]]
                ov = a.intersection(b).area/100.0
                d  = 0.0 if ov > 0 else a.distance(b)
                if ov <= 0 and d >= gap: continue
                bad += ov + max(0.0, gap-d)*0.2
                da = (az[names[j]] - az[names[i]] + 540) % 360 - 180
                push = step*(math.sqrt(max(ov,0.0)) + max(0.0, gap-d)*0.15)
                sgn = 1.0 if da >= 0 else -1.0
                force[names[i]] -= push*sgn; force[names[j]] += push*sgn
        if bad < best_bad: best_bad, best = bad, dict(az)
        if bad < 0.5: break
        for n in names:
            nz = (az[n] + force[n]) % 360
            for lo, hi in LANES.values():                 # не заходить в коридор океана
                if lo <= nz <= hi:
                    nz = lo-0.5 if (nz-lo) < (hi-nz) else hi+0.5
            az[n] = nz
    return best, best_bad

# ------------------------------------------------------------------ SVG
FONT = "DejaVu Sans, Arial, sans-serif"
def render(regs, fname, title, subs, extra=None):
    p = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="%g %g %g %g" width="%gmm" height="%gmm">'
         % (-TECH,-TECH,SHEET_W,SHEET_H,SHEET_W,SHEET_H),
         '<style>text{font-family:%s}.lb{font-size:7.4px;font-weight:600;text-anchor:middle}'
         '.lv{font-size:5px;text-anchor:middle}.hd{font-size:11px;font-weight:700;fill:#eef4f7}'
         '.hs{font-size:5.6px;fill:#8ea0aa}.ft{font-size:5px;fill:#8ea0aa}</style>' % FONT,
         '<rect x="%g" y="%g" width="%g" height="%g" fill="#0b1418"/>' % (-TECH,-TECH,SHEET_W,SHEET_H),
         '<rect x="0" y="0" width="%g" height="%g" fill="#16323f"/>' % (W,H)]
    for rid in OCEANS + LAND:
        g = regs.get(rid)
        if g is None or g.is_empty: continue
        p.append('<path d="%s" fill="%s" stroke="#0b1418" stroke-width="0.6" stroke-linejoin="round"/>'
                 % (path_of(g), COL[rid]))
    if extra: p += extra
    items = []
    for rid in OCEANS + LAND:
        g = regs.get(rid)
        if g is None or g.is_empty: continue
        a = cm2(g); pt = rep_point(g)
        if pt: items.append((pt[0],pt[1],REG[rid][0],
                             "%d см² · цель %d" % (round(a), round(target(rid))), rid in LAND))
    draw_labels(p, items)
    p.append('<rect x="0" y="0" width="%g" height="%g" fill="none" stroke="#44606e" '
             'stroke-width="0.6" stroke-dasharray="4 3"/>' % (W,H))
    p.append('<rect x="3" y="3" width="440" height="%g" rx="2.5" fill="#0b1418" fill-opacity="0.9" '
             'stroke="#2b4250" stroke-width="0.5"/>' % (14+6.8*len(subs)))
    p.append('<text class="hd" x="8" y="14">%s</text>' % title)
    for i,s in enumerate(subs):
        p.append('<text class="hs" x="8" y="%g">%s</text>' % (23+6.8*i, s))
    p.append('<text class="ft" x="%g" y="%g" text-anchor="end">рабочая часть %g×%g мм = %g см² · '
             'технологическое поле %g мм сверх неё · полотно %g×%g мм</text>'
             % (W-4, H-4, W, H, BUDGET, TECH, SHEET_W, SHEET_H))
    p.append('</svg>')
    open(os.path.join(OUT,fname),"w",encoding="utf-8").write("\n".join(p))

def path_of(g):
    d = []
    for q in polys_of(g):
        for ring in [q.exterior]+list(q.interiors):
            d.append("M " + " L ".join("%.2f %.2f"%c for c in ring.coords) + " Z")
    return " ".join(d)
def rep_point(g):
    ps = sorted(polys_of(g), key=lambda q:-q.area)
    if not ps: return None
    pt = ps[0].representative_point(); return (pt.x, pt.y)
def lab_w(it): return max(len(it[2])*4.35, len(it[3])*2.75) + 7
def draw_labels(p, items):
    P = [[x,y] for x,y,_,_,_ in items]; A = [(x,y) for x,y,_,_,_ in items]
    Wd = [lab_w(i) for i in items]; h = 14.5
    for _ in range(500):
        mv = False
        for i in range(len(P)):
            for j in range(i+1,len(P)):
                w = (Wd[i]+Wd[j])/2
                dx, dy = P[j][0]-P[i][0], P[j][1]-P[i][1]
                ox, oy = w-abs(dx), h-abs(dy)
                if ox > 0 and oy > 0:
                    mv = True
                    if oy/h < ox/w:
                        s=(oy/2+0.3)*(1 if dy>=0 else -1); P[i][1]-=s; P[j][1]+=s
                    else:
                        s=(ox/2+0.3)*(1 if dx>=0 else -1); P[i][0]-=s; P[j][0]+=s
        for i,q in enumerate(P):
            q[0]=min(max(q[0], Wd[i]/2+2), W-Wd[i]/2-2); q[1]=min(max(q[1],16), H-8)
            if q[0] < 445+Wd[i]/2 and q[1] < 40: q[1] = 40
        if not mv: break
    for i,(x,y) in enumerate([(q[0],q[1]) for q in P]):
        ax,ay = A[i]; nm, val, dark = items[i][2], items[i][3], items[i][4]
        if (x-ax)**2+(y-ay)**2 > 45:
            p.append('<path d="M %.1f %.1f L %.1f %.1f" stroke="#93a7b2" stroke-width="0.35" fill="none"/>'%(ax,ay,x,y-3.5))
            p.append('<circle cx="%.1f" cy="%.1f" r="0.9" fill="#93a7b2"/>'%(ax,ay))
        col = "#0d1a22" if dark else "#eef4f7"
        if not dark:
            p.append('<text class="lb" x="%.1f" y="%.1f" stroke="#0b1418" stroke-width="1.6" '
                     'stroke-opacity=".5" fill="none">%s</text>'%(x,y,nm))
        p.append('<text class="lb" x="%.1f" y="%.1f" fill="%s">%s</text>'%(x,y,col,nm))
        p.append('<text class="lv" x="%.1f" y="%.1f" fill="%s" fill-opacity=".9">%s</text>'%(x,y+5.6,col,val))

# ==================================== направления резов, выведенные из графа
# Линия внутреннего реза — не деталь рисунка, а то, какая область единицы смотрит
# на соседа. Её направление считается из мест, а не подбирается:
#
#   Сев. Америка  нормаль реза Центральной Америки -> на Южную Америку;
#                 второй рез в ту же сторону, тогда Запад ложится полосой
#                 между Центральной и Востоком и запрещённое касание пропадает
#   Южн. Америка  рез поперёк направления на Северную: обе половины смотрят на неё
#   Африка        рез поперёк направления на Азию: обе половины смотрят на Аравию
#   Азия          Аравия -> на Африку, Северная Азия -> на Европу, Южная — остаток
#   Европа        рез поперёк радиуса: Скандинавия наружу, к рамке; Европа внутрь
def _ang(a, b): return math.degrees(math.atan2(b[1]-a[1], b[0]-a[0]))
def world_cuts(pos):
    P = pos
    return {
      "north_america": [_ang(P["north_america"], P["south_america"]),
                        _ang(P["north_america"], P["south_america"])],
      "south_america": [_ang(P["south_america"], P["north_america"]) + 90.0],
      "africa":        [_ang(P["africa"], P["asia"]) + 90.0],
      "asia":          [_ang(P["asia"], P["africa"]), _ang(P["asia"], P["europe"])],
      "europe":        [_ang((CX,CY), P["europe"])],
    }
def local_cuts(pos, spin=None):
    """перевести мировые направления в локальную рамку единицы"""
    out = {}
    for n, angs in world_cuts(pos).items():
        az = math.degrees(math.atan2(pos[n][1]-CY, pos[n][0]-CX))
        rot = az + 90.0 + (spin or {}).get(n, UNITS[n]["spin"])
        out[n] = [(a - rot) % 360 for a in angs]
    return out

# ============================================================ решатель по графу
# Граф MC-5P на уровне единиц суши даёт три массива и двадцать разделённых пар:
#   Америки         nam — sam      (Центр. Америка с обеими половинами Южной)
#   Австралазия     aus — nzl
#   Старый Свет     afr — asi — eur
#   Антарктида      не касается ничего
# Это и есть целевая функция: обязательные пары притягиваются до касания,
# все остальные разводятся на ширину океанского канала.
PARENT = {"MR-L5-NAMW":"north_america","MR-L5-CAM":"north_america","MR-L5-NAME":"north_america",
          "MR-L5-SAMW":"south_america","MR-L5-SAME":"south_america",
          "MR-L5-AUS":"australia","MR-L5-NZL":"new_zealand",
          "MR-R5-AFRW":"africa","MR-R5-AFRE":"africa",
          "MR-R5-EUR":"europe","MR-R5-SCA":"europe",
          "MR-R5-ARB":"asia","MR-R5-ASIN":"asia","MR-R5-ASIS":"asia",
          "MR-SH-ANT":"antarctica"}
# Северного Ледовитого (рамки) касаются ровно шесть областей, из них суша — четыре.
# Остальной суше в рамку нельзя: иначе появляются рёбра, которых в реестре нет.
FRAME_OK = {"MR-L5-NAMW", "MR-L5-NAME", "MR-R5-SCA", "MR-R5-ASIN"}
CHAN = 10.0      # ширина океанского канала между разделёнными областями, мм
CHAN_ANT = 30.0  # кольцо южных океанов вокруг Антарктиды, мм
# Австралия граничит только с Новой Зеландией и Индийским океаном, Новая Зеландия —
# ещё и с Югом Тихого. Значит эта пара — острова ВНУТРИ южного океана, а не часть
# внешнего кольца, и наружу её толкать нельзя: место у рамки нужно Северу Тихого.
# Между областью, которой рамки касаться нельзя, и самой рамкой должен пройти
# ЦЕЛЫЙ океан, а не щель: Север Тихого обязан протянуться понизу от Америк до Азии,
# и если Австралия стоит у кромки, дороги ему нет.
CHAN_FRAME = 55.0
SPREAD = {"australia": -2.0, "new_zealand": -2.0}
SPREAD_DEF = 4.0 # распорка наружу: без неё материки сбиваются в три кучи

def graph_pairs():
    truth = set(tuple(sorted(e)) for e in
                json.load(open(os.path.join(MAPD,"derived","MC-5P.json"),
                               encoding="utf-8"))["edge_list"])
    req, forb = [], []
    ids = [r for r in REG if REG[r][2]]
    for i in range(len(ids)):
        for j in range(i+1, len(ids)):
            a, b = ids[i], ids[j]
            if PARENT[a] == PARENT[b]: continue
            (req if tuple(sorted((a,b))) in truth else forb).append((a,b))
    return req, forb

SPIN = {}          # заполняется tune_spins(); доворот силуэта внутри своего места

# Найдено решателем (solve), запомнено, чтобы прогон был быстрым и повторяемым.
# Пересчитать: python tools/layout.py solve
SOLVED = {
  "australia":     (415.1, 445.3),
  "new_zealand":   (292.1, 438.5),
  "north_america": (171.3, 164.5),
  "south_america": (159.8, 331.1),
  "africa":        (634.0, 132.8),
  "europe":        (775.9, 267.7),
  "asia":          (679.2, 305.5),
}

def tune_spins(grid=(-45,-25,0,25,45), rounds=1, short=55):
    """каким боком единица повёрнута — решает, та ли её область смотрит на соседа.
    Координатный спуск: по очереди для каждой единицы перебираются довороты."""
    global SPIN
    SPIN = {n: UNITS[n]["spin"] for n in UNITS}
    best_pos, best = solve(iters=short, verbose=False)
    for r in range(rounds):
        for n in list(UNITS):
            cur = SPIN[n]; loc = (cur, best, best_pos)
            for g in grid:
                SPIN[n] = g
                pos, c = solve(iters=short, seed=best_pos, verbose=False)
                if c < loc[1] - 0.5: loc = (g, c, pos)
            SPIN[n], best, best_pos = loc
        print("   круг %d: невязка %.1f, довороты %s" % (r+1, best,
              ", ".join("%s=%d" % (k, v) for k, v in SPIN.items())))
    return best_pos, best

def solve(iters=420, k_pull=1.6, k_push=0.42, seed=None, verbose=True, cuts=None):
    req, forb = graph_pairs()
    _, units0, base = build(cut_over=cuts)
    pos = {n: list(units0[n]["pos"]) for n in base}
    if seed: pos.update({k: list(v) for k,v in seed.items()})
    spin = {n: UNITS[n]["spin"] for n in base}
    ant = translate(unary_union(polys_of(build(cut_over=cuts)[0]["MR-SH-ANT"])), 0, 0)
    simp = {n: {rid: v.simplify(1.5) for rid,v in d.items()} for n,d in base.items()}
    best, best_cost = None, 1e18
    for it in range(iters):
        sh, F = {}, {n: [0.0,0.0] for n in pos}
        for n, d in simp.items():
            az = math.degrees(math.atan2(pos[n][1]-CY, pos[n][0]-CX))
            rot = az + 90.0 + spin[n]
            for rid, v in d.items():
                sh[rid] = translate(rotate(v, rot, origin=(0,0)), pos[n][0], pos[n][1])
        sh["MR-SH-ANT"] = ant
        cost = 0.0
        def act(a, b, fx, fy):
            """a двигается вдоль +f, b вдоль -f"""
            for rid, sgn in ((a,1.0),(b,-1.0)):
                u = PARENT[rid]
                if u == "antarctica": continue
                F[u][0] += sgn*fx; F[u][1] += sgn*fy
        def dirv(a, b):
            pa, pb = sh[a].centroid, sh[b].centroid
            vx, vy = pb.x-pa.x, pb.y-pa.y
            L = math.hypot(vx,vy) or 1.0
            return vx/L, vy/L
        for a, b in req:            # притянуть до касания — и не дальше:
            ov = sh[a].intersection(sh[b]).area/100.0   # раньше тормоза не было,
            if ov > 0.05:                               # и пары входили друг в друга
                pen = ov*3.0; cost += pen
                ux, uy = dirv(a,b)
                act(a, b, -ux*pen*k_push*2.0, -uy*pen*k_push*2.0)
                continue
            d = sh[a].distance(sh[b])
            if d > 1.2:
                cost += d
                ux, uy = dirv(a,b)
                act(a, b, ux*d*k_pull, uy*d*k_pull)
        for a, b in forb:                                 # развести на канал
            gap = CHAN_ANT if "MR-SH-ANT" in (a,b) else CHAN
            ov = sh[a].intersection(sh[b]).area/100.0
            d  = 0.0 if ov > 0 else sh[a].distance(sh[b])
            if ov > 0 or d < gap:
                pen = (gap-d) + ov*2.0
                if "MR-SH-ANT" in (a,b): pen *= 2.5
                cost += pen
                ux, uy = dirv(a,b)
                act(a, b, -ux*pen*k_push, -uy*pen*k_push)
        for rid, g in sh.items():                         # рамка Арктики
            if rid in FRAME_OK or rid == "MR-SH-ANT": continue
            x0,y0,x1,y1 = g.bounds
            cl = CHAN_FRAME                              # между такой областью и рамкой
            pen = max(0.0, FR_END+cl-x0, x1-(W-FR_END-cl), # обязан пройти океан
                           FR_SIDE+cl-y0, y1-(H-FR_SIDE-cl))
            if pen > 0:
                cost += pen
                u = PARENT[rid]
                c = g.centroid
                vx, vy = CX-c.x, CY-c.y; Lv = math.hypot(vx,vy) or 1.0
                F[u][0] += vx/Lv*pen*0.8; F[u][1] += vy/Lv*pen*0.8
        for i in range(len(LAND)):                        # налегание запрещено всем
            for j in range(i+1, len(LAND)):
                a, b = LAND[i], LAND[j]
                if PARENT[a] == PARENT[b]: continue
                ov = sh[a].intersection(sh[b]).area/100.0
                if ov > 0.05:
                    cost += ov*2.0
                    ux, uy = dirv(a,b)
                    act(a, b, -ux*ov*k_push, -uy*ov*k_push)
        for n in pos:                                     # слабая распорка наружу:
            vx, vy = pos[n][0]-CX, pos[n][1]-CY           # кольцо вокруг Антарктиды
            Lv = math.hypot(vx,vy) or 1.0                 # выравнивается, углы заполняются
            sp = SPREAD.get(n, SPREAD_DEF)
            F[n][0] += vx/Lv*sp; F[n][1] += vy/Lv*sp
        bnds = {}
        for n in pos:
            bnds[n] = unary_union([sh[r] for r in simp[n]]).bounds
        px = {n: pos[n][0] for n in pos}; py = {n: pos[n][1] for n in pos}
        if cost < best_cost: best_cost, best = cost, {n: list(v) for n,v in pos.items()}
        if verbose and it % 20 == 0: print("   итерация %3d  невязка %7.1f" % (it, cost))
        if cost < 1.0: break
        damp = 1.0 - 0.8*it/iters          # шаг ограничен по модулю и затухает:
        for n in pos:                        # иначе восемьдесят восемь разведённых
            fx, fy = F[n]                    # пар складываются и раскидывают поле
            m = math.hypot(fx, fy)
            if m < 1e-6: continue
            step = min(m*0.035, 6.0)*damp
            pos[n][0] += fx/m*step; pos[n][1] += fy/m*step
            x0,y0,x1,y1 = bnds[n]                       # жёсткий зажим в рабочую часть:
            dx0,dy0 = pos[n][0]-px[n], pos[n][1]-py[n]  # мягкая сила её не держит
            x0+=dx0; x1+=dx0; y0+=dy0; y1+=dy0
            if x0 < 6:   pos[n][0] += (6-x0)
            if x1 > W-6: pos[n][0] -= (x1-W+6)
            if y0 < 6:   pos[n][1] += (6-y0)
            if y1 > H-6: pos[n][1] -= (y1-H+6)
    return best, best_cost

def build_at(pos, cuts=None):
    """пересобрать области по найденным позициям, поворот — югом к центру"""
    _, units0, base = build(cut_over=cuts)
    out = {}
    for n, d in base.items():
        az = math.degrees(math.atan2(pos[n][1]-CY, pos[n][0]-CX))
        rot = az + 90.0 + UNITS[n]["spin"]
        for rid, v in d.items():
            out[rid] = translate(rotate(v, rot, origin=(0,0)), pos[n][0], pos[n][1])
    out["MR-SH-ANT"] = build(cut_over=cuts)[0]["MR-SH-ANT"]
    return out

def resolve_overlaps(regs, rounds=4):
    """Остаточные налегания разбираются геометрией: общий кусок делится серединным
    перпендикуляром между центрами, каждая область забирает свою половину.
    После этого суша — честное разбиение: пересечений нет, а пара, которая
    налегала, получает общую границу, то есть настоящее касание."""
    regs = dict(regs)
    for _ in range(rounds):
        moved = False
        for i in range(len(LAND)):
            for j in range(i+1, len(LAND)):
                a, b = LAND[i], LAND[j]
                if a not in regs or b not in regs: continue
                inter = regs[a].intersection(regs[b])
                if inter.is_empty or inter.area/100.0 < 0.05: continue
                moved = True
                ca, cb = regs[a].centroid, regs[b].centroid
                vx, vy = cb.x-ca.x, cb.y-ca.y
                Lv = math.hypot(vx,vy) or 1.0
                ang = math.degrees(math.atan2(vy, vx))
                mid = ((ca.x+cb.x)/2, (ca.y+cb.y)/2)
                d = mid[0]*vx/Lv + mid[1]*vy/Lv          # полуплоскость со стороны b
                hb = halfplane(ang, d)
                regs[a] = unary_union(polys_of(regs[a].difference(inter.intersection(hb)))).buffer(0)
                regs[b] = unary_union(polys_of(regs[b].difference(inter.difference(hb)))).buffer(0)
        if not moved: break
    return regs

# ----------------------------------------------- сверка с графом: суша с сушей
def land_check(regs, tol=2.0):
    """из 56 рёбер MC-5P шестнадцать — суша с сушей; остальные 40 решает океан,
    а он на этом проходе ещё не нарезан. Здесь проверяются только эти 16."""
    truth = set(tuple(sorted(e)) for e in
                json.load(open(os.path.join(MAPD,"derived","MC-5P.json"),
                               encoding="utf-8"))["edge_list"])
    lt = set(e for e in truth if e[0] in LAND and e[1] in LAND)
    got, over = set(), {}
    for i in range(len(LAND)):
        for j in range(i+1, len(LAND)):
            a, b = regs.get(LAND[i]), regs.get(LAND[j])
            if a is None or b is None: continue
            key = tuple(sorted((LAND[i], LAND[j])))
            ov = a.intersection(b).area/100.0
            if ov > 0.3: over[key] = ov          # налегание — НЕ смежность
            elif a.distance(b) < tol: got.add(key)
    return lt, got, over

def main(resolve=False):
    os.makedirs(OUT, exist_ok=True)
    pos = {n: list(v) for n,v in SOLVED.items()}
    cuts = local_cuts(pos)
    if resolve:                                   # резы <- места <- резы, по очереди
        for k in range(4):
            cuts = local_cuts(pos)
            pos, cost = solve(iters=170, seed=pos, verbose=False, cuts=cuts)
            print("   круг %d: невязка %.1f" % (k+1, cost))
        cuts = local_cuts(pos)
        for n,v in pos.items(): print('  "%s": (%.1f, %.1f),' % (n, v[0], v[1]))
        print("невязка графа %.1f; места:" % cost)
        for n,v in pos.items(): print('  "%s": (%.1f, %.1f),' % (n, v[0], v[1]))
    regs = build_at(pos, cuts)
    units = {n: dict(az=math.degrees(math.atan2(pos[n][1]-CY, pos[n][0]-CX))%360, pos=pos[n])
             for n in pos}
    for n,u in units.items():
        print("%-15s азимут=%4.0f место=(%.0f,%.0f)" % (n, u["az"], *u["pos"]))
    print("\n%-22s %7s %7s" % ("область","эскиз","цель"))
    for rid in OCEANS+LAND:
        if rid in regs: print("%-22s %7.0f %7.0f" % (REG[rid][0], cm2(regs[rid]), target(rid)))
    print("суша %.0f см² = %.0f%% полотна; рамка Арктики %.0f см²; остальным океанам %.0f см²"
          % (sum(cm2(regs[r]) for r in LAND),
             100*sum(cm2(regs[r]) for r in LAND)/BUDGET, _ARC, BUDGET-_ARC-_LAND*LAND_K))
    lt, got = land_check(regs)
    print("\nрёбра суша—суша: реестр %d, эскиз даёт %d, лишних %d" % (len(lt), len(lt&got), len(got-lt)))
    if lt-got: print("   нет:", ", ".join(sorted("%s—%s"%(REG[a][0],REG[b][0]) for a,b in (lt-got))))
    if got-lt: print("   лишние:", ", ".join(sorted("%s—%s"%(REG[a][0],REG[b][0]) for a,b in (got-lt))))
    render(regs, "layout-03.svg", "Раскладка — проход 4, места и резы по графу",
      ["Места и линии внутренних резов выведены из графа MC-5P: обязательные касания притянуты, разделённые разведены на канал 10 мм.",
       "Материк — жёсткий силуэт, развёрнут южной оконечностью к Антарктиде. Рамки Арктики касаются только те четыре области, кому положено.",
       "Суша 46 % полотна: ТЗ §5 как есть, минус 8 % на зазор. Океан ещё не нарезан — он решает остальные 40 рёбер из 56."])

if __name__ == "__main__":
    main(resolve=(len(sys.argv) > 1 and sys.argv[1] == "solve"))

def _old(units):
    for c,v in units.items():
        print("%-15s азимут=%5.0f  поворот=%5.0f  масштаб=%7.1f  место=(%.0f,%.0f)"
              % (c, v["az"], v["alpha"], v["scale"], *v["pos"]))
    print()
    for rid in LAND:
        print("%-22s %6.0f см²  цель %6.0f" % (REG[rid][0], cm2(regs[rid]), target(rid)))
    print("суша всего: %.0f см² из %.0f" % (sum(cm2(regs[r]) for r in LAND), BUDGET))
    render(regs, "layout-01.svg", "Раскладка — проход 1, расстановка материков",
           ["Материк — жёсткий силуэт: масштаб, поворот, перенос. Очертания не деформируются.",
            "Каждый развёрнут южной оконечностью к Антарктиде. Океан пока не нарезан."])

# ============================================================ нарезка океана
# Океан — это всё, что осталось от рабочей части после суши. Режется он не
# линиями, а ростом: пять областей растут от своих зёрен внутри океанской маски,
# каждая берёт ближайшие к себе клетки. Рост идёт ПО ВОДЕ (геодезически), поэтому
# область не может перепрыгнуть через материк и всегда остаётся связной.
# Площади выбираются весами: область меньше цели — её вес растёт, она забирает
# больше соседних клеток.
import heapq
GRID = 2.5          # шаг растра, мм
OSEED = {           # зёрна: где у области центр тяжести по смыслу графа
 "MR-OC-SPAC": (322, 372),   # между Антарктидой, Новой Зеландией и Южной Америкой
 "MR-OC-SATL": (372, 196),   # между Южной Америкой, Африкой и Антарктидой
 "MR-OC-NATL": (470,  52),   # между Северной Америкой и Африкой, выходит на рамку
 "MR-OC-IND" : (566, 322),   # между Антарктидой, Африкой, Аравией и Австралией
 "MR-OC-NPAC": (372, 506),   # между Америками и Азией понизу, выходит на рамку
}
def ocean_seed_targets(land):
    """Зерно океана — там, где сходятся его соседи по реестру: средняя точка
    центров всех областей суши, с которыми он обязан граничить."""
    truth = set(tuple(sorted(e)) for e in
                json.load(open(os.path.join(MAPD,"derived","MC-5P.json"),
                               encoding="utf-8"))["edge_list"])
    out = {}
    for n in OSEED:
        pts = [land[r].centroid for r in land
               if tuple(sorted((n, r))) in truth and r in land]
        if not pts: out[n] = OSEED[n]; continue
        out[n] = (sum(p.x for p in pts)/len(pts), sum(p.y for p in pts)/len(pts))
    return out

def cut_ocean(land, iters=60, verbose=False):
    nx, ny = int(W/GRID), int(H/GRID)
    land_u = unary_union([q for r in land for q in polys_of(land[r])]).buffer(0.01)
    frame  = box(0,0,W,H).difference(rrect(IN_W, IN_H, 28))
    cells, idx = [], {}
    kind = {}                                   # 0 — вода, 1 — рамка Арктики
    for iy in range(ny):
        for ix in range(nx):
            p = Point((ix+0.5)*GRID, (iy+0.5)*GRID)
            if land_u.contains(p): continue
            idx[(ix,iy)] = len(cells); cells.append((ix,iy))
            kind[(ix,iy)] = 1 if frame.contains(p) else 0
    inner = [c for c in cells if kind[c] == 0]
    names = list(OSEED)
    avail = len(inner)*GRID*GRID/100.0          # цели нормируются на то, что реально есть
    kt = avail/sum(target(n) for n in names)
    tgt = {n: target(n)*kt for n in names}
    want = ocean_seed_targets(land)
    seeds = {n: min(inner, key=lambda c: (c[0]*GRID-want[n][0])**2 + (c[1]*GRID-want[n][1])**2)
             for n in names}
    wt = {n: 0.0 for n in names}
    cell_a = GRID*GRID/100.0
    for it in range(iters):
        dist = {}; owner = {}
        pq = [(-wt[n], seeds[n], n) for n in names]
        heapq.heapify(pq)
        while pq:
            d, c, n = heapq.heappop(pq)
            if c in dist and dist[c] <= d: continue
            dist[c] = d; owner[c] = n
            for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
                nb = (c[0]+dx, c[1]+dy)
                if nb not in idx or kind[nb] != 0: continue
                nd = d + GRID
                if nb not in dist or nd < dist[nb]: heapq.heappush(pq, (nd, nb, n))
        area = {n: 0.0 for n in names}
        for c, n in owner.items(): area[n] += cell_a
        err = max(abs(area[n]-tgt[n]) for n in names)
        if verbose: print("   растр %2d: макс. отклонение %5.1f см²" % (it, err))
        if err < 4: break
        for n in names: wt[n] += (tgt[n]-area[n])*0.30
    return owner, kind, idx, cells, area

def cells_to_poly(cells_of, simp=2.0):
    """клетки -> полигон: сперва горизонтальные пробеги в прямоугольники"""
    rows = {}
    for ix, iy in cells_of: rows.setdefault(iy, []).append(ix)
    rects = []
    for iy, xs in rows.items():
        xs.sort(); a = b = xs[0]
        for x in xs[1:]+[None]:
            if x == b+1: b = x; continue
            rects.append(box(a*GRID, iy*GRID, (b+1)*GRID, (iy+1)*GRID))
            if x is None: break
            a = b = x
    g = unary_union(rects)
    return unary_union(polys_of(g)).simplify(simp)

def ocean_regions(land, verbose=False):
    owner, kind, idx, cells, area = cut_ocean(land, verbose=verbose)
    land_u = unary_union([q for r in land for q in polys_of(land[r])]).buffer(0)
    ocean  = box(0,0,W,H).difference(land_u).buffer(0)
    # Арктика — это ровно рамка минус суша, считается вектором, а не растром
    fr = box(0,0,W,H).difference(rrect(IN_W, IN_H, 28))
    out = {"MR-OC-ARC": ocean.intersection(fr).buffer(0)}
    ocean = ocean.difference(fr).buffer(0)
    for n in list(OSEED):
        out[n] = ocean.intersection(cells_to_poly([c for c,o in owner.items() if o == n])).buffer(0)
    # растр режет по клеткам, вдоль берега остаются полоски — раздать по соседям
    rest = ocean.difference(unary_union([q for n in OSEED for q in polys_of(out[n])])).buffer(0)
    for piece in polys_of(rest):
        if piece.area < 1e-6: continue
        who = max(OSEED, key=lambda n: out[n].buffer(GRID).intersection(piece).area)
        out[who] = unary_union(polys_of(out[who]) + [piece]).buffer(0)
    return out

# ------------------------------------------- нарезка океана по правилу (надёжная)
# Рост от зёрен неустойчив: веса разгоняются, и одна область заливает всё поле.
# Правило проще и предсказуемо — клетка воды относится к океану по радиусу
# и азимуту от центра, ровно как слои и секторы ТЗ §4:
#   рамка                      -> Северный Ледовитый
#   r < R  (кольцо у Антарктиды) -> Юг Атлантики / Юг Тихого / Индийский, по азимуту
#   r >= R (внешняя вода)        -> Север Атлантики / Север Тихого, по азимуту
# Порядок секторов задан графом: Север Атлантики смежен только с Югом Атлантики
# из южных трёх, Север Тихого — с Югом Тихого и Индийским.
SOUTH = ["MR-OC-SATL", "MR-OC-SPAC", "MR-OC-IND"]
NORTH = ["MR-OC-NATL", "MR-OC-NPAC"]
def _norm(a): return a % 360.0
def _in_arc(th, a, b): return _norm(th-a) < _norm(b-a)

def cut_ocean_rule(land, P=None, iters=90, verbose=False):
    nx, ny = int(W/GRID), int(H/GRID)
    land_u = unary_union([q for r in land for q in polys_of(land[r])]).buffer(0.01)
    fr = box(0,0,W,H).difference(rrect(IN_W, IN_H, 28))
    water = []
    for iy in range(ny):
        for ix in range(nx):
            x, y = (ix+0.5)*GRID, (iy+0.5)*GRID
            p = Point(x, y)
            if land_u.contains(p) or fr.contains(p): continue
            water.append((ix, iy, math.hypot(x-CX, y-CY),
                          _norm(math.degrees(math.atan2(y-CY, x-CX)))))
    cell_a = GRID*GRID/100.0
    avail = len(water)*cell_a
    tgt = {n: target(n) for n in SOUTH+NORTH}
    k = avail/sum(tgt.values()); tgt = {n: v*k for n, v in tgt.items()}
    if P is None:
        P = dict(R=190.0, s=[150.0, 250.0, 340.0], nb=[300.0, 110.0])
    def assign(P):
        lab = {}
        for ix, iy, r, th in water:
            if r < P["R"]:
                s = P["s"]
                n = SOUTH[0] if _in_arc(th, s[0], s[1]) else (
                    SOUTH[1] if _in_arc(th, s[1], s[2]) else SOUTH[2])
            else:
                nb = P["nb"]
                n = NORTH[0] if _in_arc(th, nb[0], nb[1]) else NORTH[1]
            lab[(ix, iy)] = n
        return lab
    for it in range(iters):
        lab = assign(P)
        ar = {n: 0.0 for n in SOUTH+NORTH}
        for n in lab.values(): ar[n] += cell_a
        err = max(abs(ar[n]-tgt[n]) for n in ar)
        if verbose and it % 15 == 0: print("   правило %2d: макс. отклонение %5.1f см²" % (it, err))
        if err < 5: break
        south_tot = sum(ar[n] for n in SOUTH); south_t = sum(tgt[n] for n in SOUTH)
        P["R"] += max(-6, min(6, (south_t-south_tot)*0.08))        # радиус кольца
        for i in range(3):                                          # границы южных
            d = (ar[SOUTH[i]] - tgt[SOUTH[i]])*0.06
            P["s"][i] = _norm(P["s"][i] + max(-4, min(4, d)))
        d = (ar[NORTH[0]] - tgt[NORTH[0]])*0.05
        P["nb"][0] = _norm(P["nb"][0] + max(-4, min(4, d)))
        P["nb"][1] = _norm(P["nb"][1] - max(-4, min(4, d)))
    lab = assign(P)
    ocean = box(0,0,W,H).difference(land_u).buffer(0)
    out = {"MR-OC-ARC": ocean.intersection(fr).buffer(0)}
    inner = ocean.difference(fr).buffer(0)
    for n in SOUTH+NORTH:
        out[n] = inner.intersection(cells_to_poly([c for c, v in lab.items() if v == n])).buffer(0)
    rest = inner.difference(unary_union([q for n in SOUTH+NORTH for q in polys_of(out[n])])).buffer(0)
    for piece in polys_of(rest):
        who = max(SOUTH+NORTH, key=lambda n: out[n].buffer(GRID).intersection(piece).area)
        out[who] = unary_union(polys_of(out[who]) + [piece]).buffer(0)
    return out, P

# ============================== планарная укладка графа: расстановка ВСЕХ областей
# Океаны не должны нарезаться после суши — они полноправные области, и места
# всем 21 надо брать из самого графа. Приём — укладка Тутта: шесть соседей
# Северного Ледовитого закрепляются по периметру в их порядке из реестра
# (ТЗ §4.5, проверено машинно), остальные вершины ставятся в среднее своих
# соседей. Для планарного графа это даёт укладку без самопересечений, то есть
# смежные по реестру области заведомо оказываются рядом.
RIM = [("MR-OC-NPAC",   0.0), ("MR-L5-NAMW",  68.0), ("MR-L5-NAME", 111.0),
       ("MR-OC-NATL", 180.0), ("MR-R5-SCA",  244.0), ("MR-R5-ASIN", 309.0)]
def tutte_layout(shrink=0.82):
    import numpy as np
    truth = [tuple(sorted(e)) for e in
             json.load(open(os.path.join(MAPD,"derived","MC-5P.json"),
                            encoding="utf-8"))["edge_list"]]
    nodes = [r for r in REG if r != "MR-OC-ARC"]
    nb = {n: set() for n in nodes}
    for a, b in truth:
        if a == "MR-OC-ARC" or b == "MR-OC-ARC": continue
        nb[a].add(b); nb[b].add(a)
    fixed = {}
    for rid, az in RIM:
        d = (math.cos(math.radians(az)), math.sin(math.radians(az)))
        R = Rdir(az, IN_W/2*shrink, IN_H/2*shrink)
        fixed[rid] = (CX + R*d[0], CY + R*d[1])
    free = [n for n in nodes if n not in fixed]
    ix = {n: i for i, n in enumerate(free)}
    A = np.zeros((len(free), len(free))); B = np.zeros((len(free), 2))
    for n in free:
        i = ix[n]; A[i, i] = len(nb[n])
        for m in nb[n]:
            if m in fixed: B[i] += fixed[m]
            else: A[i, ix[m]] -= 1.0
    X = np.linalg.solve(A, B)
    pos = dict(fixed)
    for n in free: pos[n] = (float(X[ix[n]][0]), float(X[ix[n]][1]))
    return pos

def graph_layers():
    """слой области = расстояние по графу до Северного Ледовитого (рамки).
    0 — рамка, 1 — те шесть, кто её касается, дальше вглубь; Антарктида самая дальняя."""
    truth = [tuple(sorted(e)) for e in
             json.load(open(os.path.join(MAPD,"derived","MC-5P.json"),
                            encoding="utf-8"))["edge_list"]]
    nb = {r: set() for r in REG}
    for a, b in truth: nb[a].add(b); nb[b].add(a)
    d = {"MR-OC-ARC": 0}; q = ["MR-OC-ARC"]
    while q:
        cur = q.pop(0)
        for m in nb[cur]:
            if m not in d: d[m] = d[cur]+1; q.append(m)
    return d

def polar_seeds(shrink=0.86):
    """место области = угол из укладки Тутта + радиус из слоя графа.
    Тутт даёт верный порядок по кругу, но схлопывает радиусы к центру;
    слой графа даёт честную глубину. Вместе — полярная раскладка, выведенная
    из реестра, а не назначенная руками."""
    t = tutte_layout(); lay = graph_layers()
    dmax = max(lay.values())
    seeds = {}
    for r, (x, y) in t.items():
        az = math.degrees(math.atan2(y-CY, x-CX))
        frac = (dmax - lay[r]) / float(dmax)          # 1 у рамки, 0 в центре
        R = Rdir(az, IN_W/2*shrink, IN_H/2*shrink) * (0.30 + 0.70*frac)
        if r == "MR-SH-ANT": R = 0.0
        seeds[r] = (CX + R*math.cos(math.radians(az)), CY + R*math.sin(math.radians(az)))
    return seeds, lay

def seeds_to_units(seeds):
    """место единицы — среднее мест её областей; направление реза — от центра
    единицы к месту той области, которую этот рез отрезает"""
    pos, cuts_w = {}, {}
    for name, u in UNITS.items():
        pts = [seeds[r] for r in u["regs"] if r in seeds]
        cx = sum(p[0] for p in pts)/len(pts); cy = sum(p[1] for p in pts)/len(pts)
        pos[name] = [cx, cy]
        cuts_w[name] = [math.degrees(math.atan2(seeds[rid][1]-cy, seeds[rid][0]-cx))
                        for rid, _ in u["cuts"]]
    return pos, cuts_w

def cuts_local(pos, cuts_w):
    out = {}
    for n, angs in cuts_w.items():
        az = math.degrees(math.atan2(pos[n][1]-CY, pos[n][0]-CX))
        rot = az + 90.0 + UNITS[n]["spin"]
        out[n] = [(a - rot) % 360 for a in angs]
    return out
