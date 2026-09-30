"""
classic.py — векторная основа классического поля: материки и океаны, без областей.

Источник — board/geo/world-game.geojson (Natural Earth 1:50m с игровыми коррекциями).
Реальные берега переносятся на полотно 900 × 550 мм плавной деформацией
(MLS, affine, Schaefer 2006): каждый материк получает свою рамку — куда встать
и во сколько раз вырасти, — а деформация сшивает рамки без разрывов на суше.
Раскладка — как у черновика «карта 5» и оригинала Cthulhu Wars: Америки слева,
Австралия внизу слева, Евразия и Африка справа, Антарктида внизу по центру.

Запуск из корня репозитория:
    python3 board/tools/classic.py all     собрать, проверить, записать
    python3 board/tools/classic.py check   только собрать и проверить

Пишет (всё генерируется, руками не править):
    board/geo/classic-base.geojson      мм полотна, 0…900 × 0…550, y вниз
    board/geo/classic-base.svg          картинка из geojson
    board/geo/classic-base.html         просмотр: наложение черновика, сетка, склейка краёв
    board/geo/classic-base-report.md    площади, зазоры, контакты, игровые правки

Если хоть одна проверка падает, файлы не пишутся, код возврата 1.
Зависимости: numpy, shapely.
"""
import json
import sys
import urllib.parse
from datetime import date
from pathlib import Path

import numpy as np
import shapely
from shapely import affinity
from shapely.geometry import MultiPolygon, Point, Polygon, box, mapping, shape
from shapely.ops import unary_union
from shapely.validation import make_valid

ROOT = Path(__file__).resolve().parents[2]
GEO = ROOT / 'board' / 'geo'
SRC = GEO / 'world-game.geojson'
OUT = GEO / 'classic-base'
DRAFT = ROOT / 'board' / 'legacy' / 'карта 5.jpg'

CANVAS_W, CANVAS_H, MARGIN = 900.0, 550.0, 10.0      # SPEC-BOARD §2: полотно и технологическое поле
W, H = CANVAS_W - 2*MARGIN, CANVAS_H - 2*MARGIN      # прямоугольник карты 880 × 530
MAP = box(0, 0, W, H)                                # внутренние координаты карты, сдвиг на MARGIN при записи

MIN_PART = 100.0     # мм²: острова мельче выбрасываются — ТЗ-ЭСКИЗ §10.1: у области нет кусков мельче 1 см²
MIN_HOLE = 25.0      # мм²: водоёмы внутри суши мельче — засыпаются
DECOR_MIN = 20.0     # мм²: острова от этого размера до MIN_PART — не суша, а декор с пометкой материка
DECOR = []           # (материк, полигон в мм карты) — заполняет assemble()
GAP_MIN = 12.0       # мм: несмежные материки (SPEC-BOARD §4.2)
CONTACT_MIN = 8.0    # мм: смежные материки (SPEC-BOARD §4.1)
TOP_MIN = 15.0       # мм: полоса Северного Ледовитого над сушей не рвётся

# ---------------------------------------------------------------------------
# геометрия-помощники
# ---------------------------------------------------------------------------

def polys(g):
    g = make_valid(g)
    if g.geom_type == 'Polygon':
        return [g] if not g.is_empty else []
    if g.geom_type in ('MultiPolygon', 'GeometryCollection'):
        return [p for q in g.geoms for p in polys(q)]
    return []


def U(gs):
    return make_valid(unary_union(list(gs)))


def UC(gs):
    """объединение с зашивкой волосяных щелей по линиям стыка частей"""
    return make_valid(unary_union(list(gs)).buffer(0.15, join_style='mitre').buffer(-0.15, join_style='mitre'))


def mp(g):
    ps = polys(g)
    return MultiPolygon(ps) if ps else MultiPolygon()


def rough(pts, amp=1.2, seed=7):
    """линия с мелкой неровностью, чтобы срез выглядел берегом, а не лекалом"""
    rng = np.random.default_rng(seed)
    pts = np.asarray(pts, float)
    out = [pts[0]]
    for a, b in zip(pts[:-1], pts[1:]):
        n = max(1, int(np.hypot(*(b - a))/2.5))
        for t in np.linspace(0, 1, n + 1)[1:]:
            q = a + (b - a)*t
            out.append(q + rng.normal(0, amp, 2) if t < 1 else q)
    return out

# ---------------------------------------------------------------------------
# 1. источник: материки в градусах (lon, lat), разрезанные на части с разными рамками
# ---------------------------------------------------------------------------

# Красное море южнее 18,8° с. ш. засыпано: Восточная Африка граничит с Аравией
# по суше (ME-011, длинный контакт). Северная часть моря остаётся озером.
RED_SEA_FILL = Polygon([(37.8, 18.8), (41.3, 18.8), (43.2, 15.5), (43.55, 13.0), (43.45, 12.5), (43.2, 12.2),
                        (42.9, 12.6), (42.5, 13.2), (40.5, 14.8), (39.2, 15.8), (38.3, 17.5)])
# Шельфовый ледник Ронне—Фильхнера: у Natural Earth суша кончается на линии опоры,
# и море Уэдделла режет материк на два куска. Карты мира рисуют кромку ледника — и мы.
RONNE = Polygon([(-80, -76.2), (-74, -76.0), (-66, -75.4), (-61.5, -74.3), (-56, -76.3), (-50, -77.6),
                 (-43, -78.2), (-36, -77.9), (-31, -76.8), (-27, -75.8), (-22, -75.2), (-20, -90), (-80, -90)])
# Босфор закрыт: Чёрное море — озеро, как Каспий. Иначе вода Северной Атлантики
# через волосяной пролив достаёт до берегов, где на стороне «5» будет Северная Азия
BOSPORUS = Polygon([(28.85, 40.95), (29.3, 40.95), (29.3, 41.4), (28.85, 41.4)])
# Гудзонов залив засыпан (поле-1, Alek 30.09.2026: «эта дыра необходима?» — нет):
# Северная Америка сплошная, её областям нужна рабочая площадь
HUDSON_FILL = Polygon([(-96, 64.3), (-87.5, 64.4), (-81, 63.3), (-78.3, 62.4), (-76.8, 60.5), (-76.8, 56),
                       (-78.5, 51), (-83, 50.8), (-96, 56.5)])
GREENLAND_ZONE = Polygon([(-74, 59.5), (-10, 59.5), (-10, 84), (-60, 84), (-74, 78)])
NAARC_ZONE = Polygon([(-130, 70.6), (-60, 70.6), (-60, 84), (-130, 84)])
MIDEAST_ZONE = Polygon([(25, 10), (25, 43.2), (37, 42), (48, 43.5), (54, 41), (63, 37.5), (63, 10)])
# Юго-Восточная Азия южнее 10° с. ш. — декор (Alek 30.09.2026: «огрызки внизу убрать»):
# рамка Южной Азии тянет их по вертикали втрое; хвост Малакки, Суматра, Калимантан, Сулавеси, Ява
SEASIA_DECOR = Polygon([(94, 10), (160, 10), (160, -12), (94, -12)])
# Тенассерим и Малакка южнее 14,5° с. ш. срезаны: рамка тянет их в нитку (Alek: «хвосты»)
MALAY_CUT = Polygon([(94, 14.5), (100.4, 14.5), (100.4, 0), (94, 0)])
SCHINA_ZONE = Polygon([(108, 18), (125, 18), (125, 33.5), (116, 35), (108, 35)])
JAPAN_ZONE = Polygon([(129.4, 30), (147, 30), (147, 46.5), (139.5, 46.5), (131.5, 35.2), (129.4, 34.2)])
NASIA_ZONE = Polygon([(25, 43.2), (37, 42), (48, 43.5), (54, 41), (63, 37.5), (75, 40), (90, 48), (120, 53),
                      (135, 47.5), (141, 48), (150, 47), (200, 47), (200, 85), (25, 85)])


def load_sources():
    g = json.loads(SRC.read_text(encoding='utf-8'))
    raw = {f['properties']['id']: shape(f['geometry']) for f in g['features']}
    # Чукотка за антимеридианом переносится к остальной Азии
    asia = U(affinity.translate(p, 360, 0) if p.bounds[2] < -100 else p for p in polys(raw['asia']))
    na, sa, eu, af, au, an = (raw[k] for k in ['north_america', 'south_america', 'europe',
                                               'africa', 'australia', 'antarctica'])

    def keep(geom, pred, minarea=0.15):
        return U(p for p in polys(geom) if p.area >= minarea and pred(p))

    # далёкие острова и полярная мелочь, которых нет ни в черновике, ни в оригинале
    na = keep(na, lambda p: not (p.bounds[2] < -150 and p.bounds[3] < 30)          # Гавайи
              and not (p.bounds[3] < 20 and p.area < 2))                            # Ревилья-Хихедо
    sa = keep(sa, lambda p: p.bounds[0] > -85                                       # Таити, Галапагосы
              and not (p.bounds[1] > -53 and p.bounds[3] < -50.5 and p.bounds[0] > -62))  # Фолкленды
    eu = keep(eu, lambda p: p.bounds[1] < 69.5                                      # Шпицберген, ЗФИ, Н. Земля
              and not (p.bounds[0] > -32 and p.bounds[2] < -24))                    # Азоры
    af = keep(af, lambda p: (p.bounds[0] > -16.5 or p.area > 5)                     # Канары
              and not (p.bounds[0] > 54 and p.area < 3))                            # Маскарены, Сокотра
    asia = keep(asia, lambda p: (p.bounds[1] < 74.5 or p.area > 40)                 # Сев. Земля, Н.-Сиб. о-ва
                and p.bounds[3] > -30                                               # Кергелен
                and not (p.bounds[0] > 141 and p.bounds[2] < 145.5 and p.bounds[1] > 45.5))  # Сахалин: на стыке
                # рамок Сибири и Южной Азии его растягивает в нитку вдоль берега
    # Новой Зеландии и Тасмании отдельной сушей нет — как в черновике и оригинале:
    # Австралия крупнее, область «Новая Зеландия» нарезается из её восточной половины
    au = keep(au, lambda p: p.bounds[3] < -10.5 and p.bounds[0] < 160              # Н. Гвинея, Океания, НЗ
              and not (p.bounds[0] > 143 and p.bounds[3] < -39.4))                  # Тасмания
    af = U([af, RED_SEA_FILL.difference(asia)])
    na = U([na, HUDSON_FILL])
    asia = U([asia, BOSPORUS.difference(eu)])

    S = {}
    gl = [p for p in polys(na) if p.representative_point().within(GREENLAND_ZONE) and p.bounds[0] > -74
          and not (p.bounds[0] < -61 and p.bounds[2] < -60)]
    S['greenland'] = U(gl)
    na = na.difference(S['greenland'])
    S['naarc'] = na.intersection(NAARC_ZONE)
    S['na'] = na.difference(NAARC_ZONE)
    S['sa'] = sa
    S['iceland'] = U(p for p in polys(eu) if p.bounds[2] < -12 and p.bounds[1] > 62)
    S['europe'] = eu.difference(S['iceland'])
    S['africa'] = af
    S['mideast'] = asia.intersection(MIDEAST_ZONE)
    asia = asia.difference(MIDEAST_ZONE)
    S['nasia'] = asia.intersection(NASIA_ZONE)
    sas = asia.difference(NASIA_ZONE)
    S['seasia'] = U(p for p in polys(sas.intersection(SEASIA_DECOR)) if p.bounds[3] < 9.95)   # только острова
    S['japan'] = sas.difference(SEASIA_DECOR).intersection(JAPAN_ZONE)
    rest = sas.difference(SEASIA_DECOR).difference(JAPAN_ZONE).difference(MALAY_CUT)
    S['schina'] = rest.intersection(SCHINA_ZONE)
    S['sasia'] = rest.difference(SCHINA_ZONE)
    S['australia'] = au
    S['antarctica'] = U([an, RONNE]).intersection(box(-95, -85, 112, -60))
    return S

# ---------------------------------------------------------------------------
# 2. рамки: куда встаёт каждая часть. (lon0, lat_сев, lon1, lat_юж) -> (x0, y0, x1, y1), мм карты
# ---------------------------------------------------------------------------

def rect_frame(src, tgt):
    (lon0, lat_n, lon1, lat_s), (x0, y0, x1, y1) = src, tgt
    sx = (x1 - x0)/(lon1 - lon0)
    sy = (y1 - y0)/(lat_n - lat_s)
    return lambda X, Y: (x0 + (np.asarray(X) - lon0)*sx, y0 + (lat_n - np.asarray(Y))*sy)


def pt(f, lon, lat):
    x, y = f(lon, lat)
    return float(x), float(y)


FRAMES = {
    #               источник                          цель на карте
    'na':         ((-168, 72, -52.6, 25),        (14, 34, 348, 243)),      # поле-1: ниже на 5 мм, выше на 8 — растёт в Ледовитый
    'naarc':      ((-125, 83, -60, 70.6),        (126, 16, 290, 44)),      # арктические острова поджаты к полосе
    'greenland':  ((-73, 83.6, -12, 60),         (305, 24, 391, 90)),      # уменьшена вдвое против Канады
    'iceland':    ((-24.5, 66.6, -13.5, 63.4),   (408, 46, 436, 60)),
    'sa':         ((-81.3, 12.4, -34.8, -55.9),  (214, 292, 424, 500)),
    'europe':     ((-10, 71.2, 60, 36),          (410, 28, 684, 212)),     # Европа ×3.3 по площади против Азии
    'africa':     ((-17.5, 37.3, 51.4, -34.8),   (426, 238, 655, 478)),    # уже и западнее: место Аравии
    'nasia':      ((60, 77.7, 190, 43.5),        (670, 26, 868, 164)),     # Сибирь сжата по долготе
    'sasia':      ((63, 53, 141, 1.3),           (726, 134, 872, 328)),
    'schina':     ((108, 35, 125, 18),           (809, 202, 868, 266)),    # поле-1: юго-восток Китая шире вправо (Alek)    # Индия уже: место Аравии; поле-1: восток шире (Alek)
    'japan':      ((129.3, 45.6, 146, 30.8),     (851, 164, 873, 214)),    # Япония своей рамкой: Азия расширена вправо
    'mideast':    ((34, 40, 62, 12.5),           (592, 186, 720, 330)),    # крупнее Африки: Аравия круглая, как в оригинале
    'australia':  ((113.2, -10.7, 153.6, -39.1), (4, 277, 202, 515)),     # вмещает две области: и НЗ; поле-1: уже и выше — место Югу Тихого за счёт Индийского (Alek)
    'antarctica': ((-75, -63, 110, -78),         (450, 448, 943, 516)),   # верх поднят на 8 мм (поле-1): U/A Антарктиды ≥ 0,55
}
F = {k: rect_frame(*v) for k, v in FRAMES.items()}
eu, af = F['europe'], F['africa']
# Ближний Восток крупнее соседей, поэтому на сухопутных стыках его прибивают
# к их рамкам опорными точками: Босфор и Кавказ — к Европе, Суэц, Газа и
# Баб-эль-Мандеб — к Африке. Иначе стык рвётся или складывается
ANCHORS = {'oldworld': [
    ((29.1, 41.0), pt(eu, 29.1, 41.0)), ((45.0, 42.2), pt(eu, 45.0, 42.2)),
    ((32.6, 30.0), pt(af, 32.4, 30.0)), ((34.3, 31.4), pt(af, 34.0, 31.4)), ((43.4, 12.6), pt(af, 43.2, 12.2))]}
ANCHOR_W = 25.0
GROUPS = {'americas': ['na', 'naarc', 'greenland', 'sa'],
          'oldworld': ['europe', 'mideast', 'nasia', 'sasia', 'schina', 'africa', 'seasia'],
          'japan': ['japan'],
          'iceland': ['iceland'],
          'oceania': ['australia'],
          'antarctica': ['antarctica']}
# через море рамки друг друга не тянут: иначе Гибралтар, Сардиния и пролив Нэрса
# смешивают две рамки и остров вытягивается в нитку
EXCLUDE = {'europe': ['africa'], 'africa': ['europe'],
           'greenland': ['na', 'naarc'], 'na': ['greenland'], 'naarc': ['greenland']}

# ---------------------------------------------------------------------------
# 3. деформация
# ---------------------------------------------------------------------------

def controls(name, geom, step=1.5):
    minx, miny, maxx, maxy = geom.bounds
    area = geom.buffer(0.8)
    xs = np.arange(minx - 1, maxx + 1, step)
    ys = np.arange(miny - 1, maxy + 1, step)
    gx, gy = np.meshgrid(xs, ys)
    P = np.c_[gx.ravel(), gy.ravel()]
    P = P[shapely.contains_xy(area, P[:, 0], P[:, 1])]
    qx, qy = F[name](P[:, 0], P[:, 1])
    return P, np.c_[qx, qy]


def mls_affine(P, Q, V, wts, alpha=2.0, sigma=1.2):
    out = np.empty_like(V)
    for s in range(0, len(V), 3000):
        v = V[s:s + 3000]
        d2 = ((P[None] - v[:, None])**2).sum(-1)
        w = wts[None, :]/(d2 + sigma**2)**alpha
        ws = w.sum(1, keepdims=True)
        ps = (w[:, :, None]*P[None]).sum(1)/ws
        qs = (w[:, :, None]*Q[None]).sum(1)/ws
        ph = P[None] - ps[:, None]
        qh = Q[None] - qs[:, None]
        A = np.einsum('bn,bni,bnj->bij', w, ph, ph) + 1e-9*np.eye(2)
        B = np.einsum('bn,bni,bnj->bij', w, ph, qh)
        out[s:s + 3000] = np.einsum('bi,bij->bj', v - ps, np.linalg.solve(A, B)) + qs
    return out


def warp_all(S):
    out, warpers = {}, {}
    for gname, members in GROUPS.items():
        P, Q, Wt, tag = [], [], [], []
        for m in members:
            if m not in F:          # Ближний Восток — только опорные точки
                continue
            p, q = controls(m, S[m])
            P.append(p); Q.append(q); Wt.append(np.ones(len(p))); tag += [m]*len(p)
        for (lon, lat), (x, y) in ANCHORS.get(gname, []):
            P.append(np.array([[lon, lat]])); Q.append(np.array([[x, y]]))
            Wt.append(np.array([ANCHOR_W])); tag.append('anchor')
        P, Q, Wt, tag = np.vstack(P), np.vstack(Q), np.concatenate(Wt), np.array(tag)
        for m in members:
            sel = ~np.isin(tag, EXCLUDE.get(m, []))
            Ps, Qs, Ws = P[sel], Q[sel], Wt[sel]
            warpers[m] = (lambda V, Ps=Ps, Qs=Qs, Ws=Ws: mls_affine(Ps, Qs, np.asarray(V, float), Ws))
            geom = shapely.segmentize(S[m], 0.3)
            out[m] = make_valid(shapely.set_coordinates(geom, warpers[m](shapely.get_coordinates(geom))))
    return out, warpers

# ---------------------------------------------------------------------------
# 4. сборка материков и игровые правки на полотне
# ---------------------------------------------------------------------------

# Панама (поле-1). Координаты — мм карты (полотно минус 10). Рамка Северной Америки
# опущена, перешеек сам доходит до Колумбии; стык сглаживается в окне PANAMA_WIN
# и целиком отходит Северной Америке.
PANAMA_WIN = box(-2, -2, -1, -1)          # сглаживание стыка не нужно: перешеек сам входит в Колумбию
PANAMA_NW = box(-100, -100, 1000, 1000)
# Пролив поперёк перешейка между Коста-Рикой и Панамой: ME-074 — Север Атлантики
# и Север Тихого смежны напрямую, их общая граница — ширина пролива, ≥ 8 мм
# (MF-010, как в оригинале). Alek 30.09.2026: уже, чем 9,6 мм, Америки ближе.
STRAIT_Y, STRAIT_W = 288.0, 9.2            # мм карты: северный берег пролива и его ширина
STRAIT_X = (238, 262)                      # от Тихого океана до Карибского моря поперёк Панамы
STRAIT = Polygon(rough([(STRAIT_X[0], STRAIT_Y), (250, STRAIT_Y - 0.3), (STRAIT_X[1], STRAIT_Y)], amp=0.35, seed=21)
                 + rough([(STRAIT_X[1], STRAIT_Y + STRAIT_W), (250, STRAIT_Y + STRAIT_W + 0.3),
                          (STRAIT_X[0], STRAIT_Y + STRAIT_W)], amp=0.35, seed=22))
# Панама и карибский берег Колумбии и Венесуэлы — Северной Америке: на стороне «5»
# это южный кусок Центральной Америки. Он граничит с Западом и Востоком Южной Америки
# (ME-005, ME-004) и отгораживает Запад Южной Америки от Северной Атлантики (MF-010:
# «полоса Центральной Америки идёт по берегу до самого Востока Южной Америки»).
PANAMA_TO_SA = box(236, 316.9, 278, 334)
CARIB = Polygon([(230, 294), (246, 294), (256, 290), (275, 290), (304, 294), (318, 301), (320, 316),
                 (280, 317), (252, 317), (235, 317)])
PANAMA_STRAIT_MIN = 8.0
# Сглаживание берега Европы, мм (поле-1): без него у Европы и Скандинавии U/A 0,545 и 0,52
# при минимуме 0,55 (SPEC §6) — площадь уходит в фьорды и узкие мысы, где фигура не встаёт
SMOOTH_EU = 1.5
MAD_ZONE = box(620, 380, 670, 460)       # мм карты: где искать Мадагаскар
MAD_GAP = 2.5                            # мм: пролив между Мадагаскаром и Африкой
MAD_DY = 10.0                            # мм: сдвиг вниз — остров ложится в изгиб берега, пролив ровный
PUDDLE = 200.0       # мм²: запертая вода мельче — засыпается
SMOOTH = [('europe', SMOOTH_EU, box(-10, -10, 900, 600)),
          ('north_america', 2.0, box(-10, -10, 400, 92)),       # север Америки: архипелаг не пестрит (Alek)
          ('asia', 1.2, box(700, -10, 900, 600))]               # Азия восточнее Ирана: берег ровнее, как у остальных
SMOOTH_KEEP = U([box(540, 170, 575, 200),      # Босфор и Дарданеллы: Чёрное море остаётся озером
                 box(575, 38, 625, 80)])      # горло Белого моря: море остаётся Ледовитому
# Карибский берег Колумбии и Венесуэлы с Панамой — к Северной Америке: на стороне «5»
# это южный кусок Центральной Америки. Он граничит с Западом и Востоком Южной Америки
# (ME-005, ME-004) и отгораживает Запад Южной Америки от Северной Атлантики (MF-010:
# «полоса Центральной Америки идёт по берегу до самого Востока Южной Америки»).
CARIB = Polygon([(222, 286), (252, 286), (266, 282), (292, 286), (314, 293), (318, 300), (316, 315),
                 (282, 316.5), (252, 314.5), (236, 314), (222, 310)])

CORRECTIONS = [
    ('Красное море', 'засыпано южнее 18,8° с. ш., север — озеро', 'ME-011: Восточная Африка — Аравия граничат по суше'),
    ('Ближний Восток', 'своя рамка крупнее соседних: Африка ужата и сдвинута к западу, Индия ужата по долготе', 'Аравия должна резаться в круглую область, как в оригинале; без этого её U < 55 см²'),
    ('Босфор', 'закрыт, Чёрное море — озеро', 'через волосяной пролив Северная Атлантика доставала бы до берегов будущей Северной Азии'),
    ('Ледник Ронне—Фильхнера', 'дорисован по кромке', 'без него море Уэдделла режет Антарктиду надвое'),
    ('Панамский перешеек', 'рамка Северной Америки опущена — перешеек сам входит в Колумбию', 'Америки ближе друг к другу, как в оригинале (Alek)'),
    ('Панамский пролив', f'перешеек между Коста-Рикой и Панамой прорезан проливом ≈{STRAIT_W:g} мм, самое узкое место ≈8,6', 'ME-074: Север Атлантики и Север Тихого смежны напрямую, их общая граница ≥ 8 мм — это ширина пролива (MF-010, как в оригинале); Alek: уже 9,6 мм, Америки ближе'),
    ('Гудзонов залив', 'засыпан', 'Alek 30.09.2026: дыра в Северной Америке не нужна; её областям нужна рабочая площадь'),
    ('Северная Америка', 'рамка ниже на 5 мм и выше на 8 — растёт в полосу Ледовитого, шире на 8 мм', 'трём областям не хватало площади: U материка 209 при нужных ≈ 230; Америки ближе друг к другу (Alek)'),
    ('Южная Азия', 'рамка до 141° в. д. шире на 4 мм — восточный берег Китая и Кореи на 8–10 мм ближе к краю; Япония — своей рамкой', 'Alek: Азию можно смело расширить вправо'),
    ('Юго-Восточная Азия', 'острова южнее 10° с. ш. (Суматра, Калимантан, Сулавеси, Ява) — декор, хвост Малакки срезан по 10°', 'рамка Южной Азии тянет их по вертикали вдвое с лишним: «огрызки» (Alek)'),
    ('Австралия', 'рамка уже на 12 мм и выше на 21', 'Юг Тихого шире между Австралией и Южной Америкой; место взято у Индийского вокруг Австралии (Alek)'),
    ('Мадагаскар', f'придвинут к Африке, пролив {MAD_GAP:g} мм', 'оторванный, не прибавлял Африке места и съедал Индийский узким местом (Alek)'),
    ('Берег Европы', f'сглажен на {SMOOTH_EU:g} мм: фьорды, шхеры и узкие заливы засыпаны, узкие мысы срезаны', 'U/A Европы и Скандинавии ≥ 0,55 (SPEC §6): моря и заливы как сущности не важны (Alek 30.09.2026)'),
    ('Граница Северной и Южной Америки', 'Панама и карибский берег Колумбии и Венесуэлы — Северной Америке', 'на стороне «5» это южный кусок Центральной Америки: граничит с Западом и Востоком Южной Америки и отгораживает Запад Южной Америки от Северной Атлантики (MF-010)'),
    ('Новая Зеландия', 'отдельной сушей не рисуется; Австралия увеличена, область «Новая Зеландия» нарезается из её восточной половины', 'как в черновике «карта 5» и в оригинале; ME-002 — граница по суше'),
    ('Гренландия', 'часть Северной Америки, подвинута к Канадскому архипелагу', 'как в черновике и оригинале: арктические острова — в Северной Америке'),
    ('Антарктида', 'концы уходят под нижний край кривой, а не срезаны по вертикали', 'как в оригинале: материк — выступ из нижнего края'),
    ('Антарктида: толщина', 'верх рамки поднят на 8 мм (+14 см²)', 'полоса у нижнего края давала U/A 0,53 при минимуме 0,55 (SPEC §6): край полотна тоже граница рабочей зоны'),
    ('Арктические острова', 'Шпицберген, ЗФИ, Новая Земля, Северная Земля, Новосибирские убраны; Канадский архипелаг поджат', 'полоса Северного Ледовитого не рвётся'),
    ('Мелкие острова', f'от {DECOR_MIN:.0f} мм² до {MIN_PART/100:.0f} см² — не суша, а декор с пометкой материка (Гаити, Тринидад, Шри-Ланка, Хайнань, Кипр, Корсика, Сардиния, Ванкувер, мелочь архипелагов); мельче — убраны; Гавайи, Галапагосы, Фолкленды, Азоры, Канары, Новая Гвинея, Океания, Тасмания и Сахалин — тоже', 'нет в черновике и оригинале, мусор на поле'),
]


def antarctic_keep():
    t = np.linspace(0, 1, 30)
    left = [(430 + 22*s, 534 - 46*np.sin(s*np.pi/2)) for s in t]        # подъём вдоль запада полуострова
    right = [(846 + 26*s, 466 + 68*(1 - np.cos(s*np.pi/2))) for s in t]   # спуск под нижний край
    return Polygon(rough(left) + [(left[-1][0], 400), (right[0][0], 400)] + rough(right, seed=11)
                   + [(884, 536), (398, 536)]).buffer(0)


def assemble(w):
    C = {}
    C['north_america'] = UC([w['na'], w['naarc'], w['greenland']])
    C['south_america'] = w['sa']
    C['europe'] = UC([w['europe'], w['iceland']])
    C['asia'] = UC([w['mideast'], w['nasia'], w['sasia'], w['schina'], w['japan']])
    DECOR.extend(('asia', p) for p in polys(w['seasia'].intersection(MAP)) if p.area >= DECOR_MIN)
    C['africa'] = w['africa']
    C['australia'] = w['australia']
    C['antarctica'] = w['antarctica']
    C = {k: v.intersection(MAP) for k, v in C.items()}
    C['antarctica'] = C['antarctica'].intersection(antarctic_keep())
    # Панама: одна гладкая шейка, делится прямой линией
    both = U([C['north_america'], C['south_america']]).intersection(PANAMA_WIN)
    neck = both.buffer(2.5).buffer(-2.5).buffer(-1.2).buffer(1.2).buffer(1.6).intersection(PANAMA_WIN)
    C['north_america'] = UC([C['north_america'].difference(PANAMA_WIN), neck.intersection(PANAMA_NW)])
    C['south_america'] = UC([C['south_america'].difference(PANAMA_WIN), neck.difference(PANAMA_NW)])
    back = C['north_america'].intersection(PANAMA_TO_SA)      # хвост перешейка южнее полосы — Колумбии
    C['south_america'] = UC([C['south_america'], back])
    C['north_america'] = C['north_america'].difference(PANAMA_TO_SA)
    moved = C['south_america'].intersection(CARIB)
    C['north_america'] = UC([C['north_america'], moved])
    C['south_america'] = C['south_america'].difference(CARIB)
    for k in ('north_america', 'south_america'):
        C[k] = C[k].difference(STRAIT)
    # южный кусок Центральной Америки сглажен: стык перешейка с Колумбией даёт зубцы
    south = C['north_america'].intersection(CARIB.buffer(1))
    smooth = south.buffer(1.5).buffer(-1.5).buffer(-1.0).buffer(1.0).intersection(CARIB.buffer(1)).difference(STRAIT)
    C['north_america'] = UC([C['north_america'].difference(CARIB.buffer(1)), smooth])
    C['south_america'] = C['south_america'].difference(smooth)

    def dehole(p):
        return Polygon(p.exterior, [r for r in p.interiors if Polygon(r).area >= MIN_HOLE])
    for k in C:
        DECOR.extend((k, p) for p in polys(C[k]) if DECOR_MIN <= p.area < MIN_PART)
        C[k] = mp(U(dehole(p) for p in polys(C[k]) if p.area >= MIN_PART))
    # берег сглажен: заливы и проливы уже 2·r мм засыпаны, мысы тоньше срезаны — в окнах SMOOTH,
    # кроме окон SMOOTH_KEEP: там узкие проливы, которые сглаживание открыло бы или закрыло
    for k, r, win in SMOOTH:
        e0 = C[k]
        sm = e0.buffer(-r).buffer(r).buffer(r).buffer(-r)
        e1 = U([sm.intersection(win).difference(SMOOTH_KEEP), e0.difference(win), e0.intersection(win).intersection(SMOOTH_KEEP)])
        DECOR.extend((k, p) for p in polys(e1) if DECOR_MIN <= p.area < MIN_PART)
        C[k] = mp(U(p for p in polys(e1) if p.area >= MIN_PART))
    # Мадагаскар придвинут к Африке с узким проливом MAD_GAP: оторванный, он не прибавлял
    # Африке места и съедал Индийский узким местом (Alek 30.09.2026)
    parts = polys(C['africa'])
    mad = [p for p in parts if p.representative_point().within(MAD_ZONE) and p.area > MIN_PART]
    if mad:
        m = affinity.translate(mad[0], 0, MAD_DY)          # ниже, в изгиб берега Мозамбика
        rest = U(p for p in parts if not p.equals(mad[0]))
        lo, hi = -60.0, 20.0                                # и к западу — до пролива MAD_GAP
        for _ in range(40):
            mid = (lo + hi)/2
            mm = affinity.translate(m, mid, 0)
            lo, hi = (mid, hi) if mm.intersects(rest) or mm.distance(rest) < MAD_GAP else (lo, mid)
        C['africa'] = mp(U([rest, affinity.translate(m, hi, 0)]))
    # лужи, которые сглаживание заперло между островами, мельче PUDDLE — суше вокруг
    water = polys(MAP.difference(U(C.values())))
    for p in water:
        if p.intersects(MAP.exterior) or p.area >= PUDDLE:
            continue
        k = max(C, key=lambda k: p.boundary.intersection(C[k].buffer(0.05)).length)
        C[k] = mp(U([C[k], p.buffer(0.02)]))
    # наложения: кто раньше в списке, тот и владеет
    taken = Polygon()
    for k in ['europe', 'asia', 'africa', 'north_america', 'south_america', 'australia', 'antarctica']:
        C[k] = mp(C[k].difference(taken))
        taken = U([taken, C[k]])
    return C


LAKE_POINTS = {'Каспийское море': ('mideast', 50.5, 41.5), 'Чёрное море': ('mideast', 34.0, 43.2),
               'Красное море': ('mideast', 37.0, 23.0)}


def waters(C, warpers):
    land = U(C.values())
    water = polys(MAP.difference(land))
    ocean = [p for p in water if p.intersects(MAP.exterior)]
    lakes = []
    for p in water:
        if p.intersects(MAP.exterior) or p.area < MIN_HOLE:
            continue
        name = None
        for nm, (member, lon, lat) in LAKE_POINTS.items():
            x, y = warpers[member]([[lon, lat]])[0]
            if p.buffer(1.0).contains(Point(x, y)):
                name = nm
        lakes.append((name or 'Озеро', p))
    return mp(U(ocean)), lakes

# ---------------------------------------------------------------------------
# 5. проверки
# ---------------------------------------------------------------------------

NAMES = {'north_america': 'Северная Америка', 'south_america': 'Южная Америка', 'europe': 'Европа',
         'asia': 'Азия', 'africa': 'Африка', 'australia': 'Австралия', 'antarctica': 'Антарктида'}
ADJ = [('north_america', 'south_america'), ('europe', 'asia'), ('africa', 'asia')]   # сторона «3», суша—суша
DRAFT_AREA = {'north_america': 396.6, 'south_america': 174.0, 'europe': 298.2, 'asia': 454.9,
              'africa': 302.8, 'australia': 158.5, 'antarctica': 183.9}          # SPEC-BOARD §3.2
TARGET_AREA = {'north_america': 490, 'south_america': 320, 'europe': 330, 'asia': 510,
               'africa': 335, 'australia': 300, 'antarctica': 185}                # ТЗ-ЭСКИЗ §5.4


def wrap_distance(a, b):
    """расстояние с учётом склейки левого и правого краёв"""
    return min(a.distance(b), affinity.translate(a, W, 0).distance(b), affinity.translate(a, -W, 0).distance(b))


# Проба: Аравия на этапе областей — полуостров, Левант, Ирак, Иран, Афганистан,
# Пакистан до Инда и юго-восток Турции. Основа обязана давать ей хотя бы минимум SPEC §6
ARABIA_PROBE = [(33, 29.6), (35.8, 36.6), (37, 38.5), (41, 39.5), (44.5, 39.5), (47, 38.4), (49, 37.3), (54, 37.3),
                (61, 36.6), (66, 37.3), (71, 36.8), (71.5, 31), (68.5, 24.5), (66, 10), (30, 10)]
U_MIN = 55.0      # см², SPEC-BOARD §6


def arabia_probe(C, warpers):
    cut = Polygon(warpers['mideast'](np.array(ARABIA_PROBE, float)))
    g = max(polys(C['asia'].intersection(cut)), key=lambda p: p.area)
    return g, g.buffer(-7.3)


def check(C, ocean, lakes, warpers=None):
    res = []   # (ok, текст)
    keys = list(C)
    for k, g in C.items():
        res.append((g.is_valid and not g.is_empty, f'{NAMES[k]}: геометрия валидна'))
    top = min(p.bounds[1] for g in C.values() for p in g.geoms)
    res.append((top >= TOP_MIN, f'полоса Северного Ледовитого: суша не ближе {TOP_MIN:.0f} мм к верхнему краю — {top:.1f} мм'))
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            if (a, b) in ADJ or (b, a) in ADJ:
                continue
            d = wrap_distance(C[a], C[b])
            res.append((d >= GAP_MIN, f'{NAMES[a]} — {NAMES[b]}: зазор {d:.1f} мм (≥ {GAP_MIN:.0f})'))
    for a, b in ADJ:
        c = C[a].buffer(0.05).intersection(C[b].buffer(0.05)).length/2
        res.append((c >= CONTACT_MIN, f'{NAMES[a]} — {NAMES[b]}: граница по суше {c:.1f} мм (≥ {CONTACT_MIN:.0f})'))
    big = [p for p in C['antarctica'].geoms if p.area > 1000]
    res.append((len(big) == 1, f'Антарктида одним куском: {len(big)}'))
    gl = [p for p in C['north_america'].geoms if p.area > 1500 and p.bounds[0] > 280 and p.bounds[3] < 110]
    rest = MultiPolygon([p for p in C['north_america'].geoms if not any(p.equals(q) for q in gl)])
    gg = min((q.distance(rest) for q in gl), default=0)
    res.append((len(gl) == 1 and gg >= 3, f'Гренландия читается островом: до Канады {gg:.1f} мм (≥ 3)'))
    nag = sorted(C['north_america'].geoms, key=lambda p: -p.area)
    main = nag[0]
    south = [p for p in nag[1:] if p.intersects(CARIB) and p.area > 500]
    sw = min((p.distance(main) for p in south), default=0)
    res.append((len(south) == 1 and sw >= PANAMA_STRAIT_MIN,
                f'Панамский пролив: ширина {sw:.1f} мм (≥ {PANAMA_STRAIT_MIN:.0f}), южный кусок Центральной Америки '
                f'{sum(p.area for p in south)/100:.1f} см²'))
    res.append((len(polys(ocean)) == 1, f'Мировой океан связен: {len(polys(ocean))} кусок'))
    if warpers is not None:
        g, u = arabia_probe(C, warpers)
        res.append((u.area/100 >= U_MIN, f'Аравия режется в область: A {g.area/100:.0f} см², U {u.area/100:.0f} см² '
                    f'(минимум {U_MIN:.0f}, норма 85), вписанный круг ⌀{2*shapely.maximum_inscribed_circle(g).length:.0f} мм'))
    return res

# ---------------------------------------------------------------------------
# 6. запись
# ---------------------------------------------------------------------------

def to_canvas(g, tol=0.12):
    g = affinity.translate(g.simplify(tol, preserve_topology=True), MARGIN, MARGIN)
    return mp(U(p for p in polys(g) if p.area >= MIN_PART)) if g.geom_type != 'Polygon' else g   # крошки после упрощения


def rnd(geom):
    g = shapely.set_precision(geom, 0.01)
    if g.geom_type == 'MultiPolygon':            # сетка 0,01 мм оставляет вырожденные крошки — вон
        g = MultiPolygon([p for p in g.geoms if p.area >= 1.0])
    return json.loads(json.dumps(mapping(g)))


def geojson(C, ocean, lakes, res):
    feats = []
    for k, g in C.items():
        props = {'id': k, 'type': 'LAND', 'name_ru': NAMES[k], 'area_cm2': round(g.area/100, 1),
                 'parts': len(g.geoms)}
        if k == 'australia':
            props['note'] = 'область «Новая Зеландия» нарезается из восточной половины, как в черновике и оригинале'
        feats.append({'type': 'Feature', 'properties': props, 'geometry': rnd(to_canvas(g))})
    feats.append({'type': 'Feature', 'properties': {'id': 'ocean', 'type': 'OCEAN', 'name_ru': 'Мировой океан',
                  'area_cm2': round(ocean.area/100, 1), 'note': 'одним объектом: деление на шесть океанов — этап областей'},
                  'geometry': rnd(to_canvas(ocean))})
    for i, (nm, p) in enumerate(lakes, 1):
        feats.append({'type': 'Feature', 'properties': {'id': f'lake-{i}', 'type': 'INLAND_WATER', 'name_ru': nm,
                      'area_cm2': round(p.area/100, 1)}, 'geometry': rnd(to_canvas(p))})
    for i, (k, p) in enumerate(sorted(DECOR, key=lambda t: (t[0], -t[1].area)), 1):
        feats.append({'type': 'Feature', 'properties': {'id': f'decor-{i}', 'type': 'DECOR_ISLAND', 'continent': k,
                      'area_mm2': round(p.area), 'note': 'остров-декор: не суша области, рисуется поверх океана, '
                      'относится к своему материку (Alek 30.09.2026)'}, 'geometry': rnd(to_canvas(p))})
    return {
        'type': 'FeatureCollection',
        'metadata': {
            'name': 'oil-wars-classic-base', 'generated': date.today().isoformat(),
            'generator': 'board/tools/classic.py', 'source': 'board/geo/world-game.geojson',
            'purpose': 'векторная основа классического поля: материки и океаны, без областей',
            'coordinateSystem': {'units': 'mm', 'origin': 'левый верхний угол полотна', 'axis': 'x вправо, y вниз',
                                 'canvas': [CANVAS_W, CANVAS_H], 'map_rect': [MARGIN, MARGIN, MARGIN + W, MARGIN + H],
                                 'technical_margin_mm': MARGIN},
            'wrap': 'левый и правый края карты склеены, как в оригинале: Север Тихого и Индийский океаны — по два куска',
            'method': 'MLS affine (Schaefer 2006) по опорной сетке материковых рамок, alpha 2, sigma 1.2°',
            'frames': {k: {'src_lon_lat': v[0], 'tgt_mm': v[1]} for k, v in FRAMES.items()},
            'corrections': [{'subject': a, 'op': b, 'reason': c} for a, b, c in CORRECTIONS],
            'checks': [{'ok': ok, 'text': t} for ok, t in res],
        },
        'features': feats,
    }


LAND_TINT = {'north_america': '#d9b98c', 'south_america': '#b9c98f', 'europe': '#c7aecb', 'asia': '#e2b0a0',
             'africa': '#dcc38f', 'australia': '#9fc9b5', 'antarctica': '#e6ecef'}


def path_d(g):
    d = []
    for p in polys(g):
        for ring in [p.exterior, *p.interiors]:
            c = np.asarray(ring.coords)
            d.append('M' + ' '.join(f'{x:.2f},{y:.2f}' for x, y in c[:-1]) + 'Z')
    return ''.join(d)


def svg_body(C, ocean, lakes, extras=''):
    Cc = {k: to_canvas(g) for k, g in C.items()}
    borders = []
    for a, b in ADJ:
        seg = Cc[a].buffer(0.05).intersection(Cc[b].buffer(0.05))
        if not seg.is_empty:
            borders.append(f'<path d="{path_d(seg.buffer(0.01))}"/>')
    land = ''.join(f'<path id="{k}" data-tint="{LAND_TINT[k]}" d="{path_d(g)}"/>' for k, g in Cc.items())
    lk = ''.join(f'<path d="{path_d(to_canvas(p))}"><title>{nm}</title></path>' for nm, p in lakes)
    return (f'<rect width="{CANVAS_W:g}" height="{CANVAS_H:g}" fill="#ece8df"/>'
            f'<g id="ocean"><rect x="{MARGIN:g}" y="{MARGIN:g}" width="{W:g}" height="{H:g}" fill="#46647d"/></g>'
            f'<g id="land" fill="#d8ccb0" stroke="#2c2a26" stroke-width="0.3" stroke-linejoin="round">{land}</g>'
            f'<g id="lakes" fill="#46647d" stroke="#2c2a26" stroke-width="0.3">{lk}</g>'
            f'<g id="borders" fill="none" stroke="#2c2a26" stroke-width="0.35" stroke-dasharray="1.6 1.2">{"".join(borders)}</g>'
            f'{extras}'
            f'<rect x="{MARGIN:g}" y="{MARGIN:g}" width="{W:g}" height="{H:g}" fill="none" stroke="#2c2a26" stroke-width="0.4"/>')


def svg(C, ocean, lakes):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{CANVAS_W:g}mm" height="{CANVAS_H:g}mm" '
            f'viewBox="0 0 {CANVAS_W:g} {CANVAS_H:g}">\n<title>Нефтяные войны — основа поля, классическая</title>\n'
            + svg_body(C, ocean, lakes) + '\n</svg>\n')


def area_rows(C):
    rows = []
    for k in ['north_america', 'south_america', 'europe', 'asia', 'africa', 'australia', 'antarctica']:
        a = C[k].area/100
        rows.append((NAMES[k], a, DRAFT_AREA[k], TARGET_AREA[k]))
    return rows


def html(C, ocean, lakes, res):
    draft = urllib.parse.quote(DRAFT.relative_to(GEO.parent).as_posix())
    grid = ''.join(f'<line x1="{x:g}" y1="{MARGIN:g}" x2="{x:g}" y2="{MARGIN + H:g}"/>' for x in np.arange(MARGIN, MARGIN + W + 1, 50)) + \
        ''.join(f'<line x1="{MARGIN:g}" y1="{y:g}" x2="{MARGIN + W:g}" y2="{y:g}"/>' for y in np.arange(MARGIN, MARGIN + H + 1, 50))
    labels = ''.join(f'<text x="{x + 1:g}" y="{MARGIN - 2:g}">{int(x - MARGIN)}</text>' for x in np.arange(MARGIN, MARGIN + W + 1, 100)) + \
        ''.join(f'<text x="1" y="{y + 3:g}">{int(y - MARGIN)}</text>' for y in np.arange(MARGIN + 100, MARGIN + H + 1, 100))
    extras = (f'<g id="draft" style="display:none"><image href="../{draft}" x="{MARGIN:g}" y="{MARGIN:g}" width="{W:g}" '
              f'height="{H:g}" preserveAspectRatio="none" opacity="0.5"/></g>'
              f'<g id="grid" style="display:none" stroke="#fff" stroke-opacity="0.35" stroke-width="0.25">{grid}'
              f'<g fill="#2c2a26" stroke="none" font-size="5" font-family="sans-serif">{labels}</g></g>'
              f'<g id="wrap" style="display:none" opacity="0.45">'
              f'<clipPath id="cl"><rect x="{MARGIN - 110:g}" y="{MARGIN:g}" width="110" height="{H:g}"/></clipPath>'
              f'<clipPath id="cr"><rect x="{MARGIN + W:g}" y="{MARGIN:g}" width="110" height="{H:g}"/></clipPath>'
              f'<g clip-path="url(#cl)"><use href="#ocean" x="{-W:g}"/><use href="#land" x="{-W:g}"/></g>'
              f'<g clip-path="url(#cr)"><use href="#ocean" x="{W:g}"/><use href="#land" x="{W:g}"/></g></g>')
    rows = ''.join(f'<tr><td>{n}</td><td>{a:.0f}</td><td>{d:.0f}</td><td>{t}</td><td>{(a/d - 1)*100:+.0f} %</td></tr>'
                   for n, a, d, t in area_rows(C))
    land = sum(g.area for g in C.values())/100
    checks = ''.join(f'<li class="{"ok" if ok else "bad"}">{"✓" if ok else "✗"} {t}</li>' for ok, t in res)
    draft_note = '' if DRAFT.exists() else '<p class="bad">Файл черновика не найден — наложение не покажется.</p>'
    return f'''<!doctype html>
<html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Основа поля — классическая</title>
<style>
:root{{--bg:#f4f1ea;--fg:#23211d;--mut:#6b665c;--line:#d6d0c4;--ok:#2f7d4a;--bad:#b3261e}}
@media (prefers-color-scheme:dark){{:root{{--bg:#1d1c1a;--fg:#ece8df;--mut:#a39d91;--line:#3a3833;--ok:#7fc79a;--bad:#f2867e}}}}
body{{margin:0;background:var(--bg);color:var(--fg);font:15px/1.45 system-ui,sans-serif}}
main{{max-width:1500px;margin:0 auto;padding:16px}}
h1{{font-size:20px;margin:0 0 4px}} p.sub{{margin:0 0 12px;color:var(--mut)}}
.ctl{{display:flex;flex-wrap:wrap;gap:8px 20px;align-items:center;margin:0 0 10px;padding:10px 12px;border:1px solid var(--line);border-radius:8px}}
.ctl label{{display:flex;gap:6px;align-items:center;cursor:pointer}}
.ctl input[type=range]:disabled{{opacity:.4}}
svg{{width:100%;height:auto;display:block;border-radius:6px}}
.cols{{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:24px;margin-top:16px}}
@media (max-width:900px){{.cols{{grid-template-columns:1fr}}}}
table{{border-collapse:collapse;width:100%}} td,th{{padding:4px 8px;border-bottom:1px solid var(--line);text-align:right}}
td:first-child,th:first-child{{text-align:left}} th{{color:var(--mut);font-weight:500}}
ul{{padding-left:0;list-style:none;margin:0}} li{{padding:2px 0}} .ok{{color:var(--ok)}} .bad{{color:var(--bad)}}
h2{{font-size:16px;margin:0 0 8px}}
</style></head><body><main>
<h1>Основа поля — классическая проекция</h1>
<p class="sub">Материки и океан без деления на области · полотно {CANVAS_W:g} × {CANVAS_H:g} мм, карта {W:g} × {H:g} мм внутри технологического поля {MARGIN:g} мм · сборка {date.today().isoformat()}, <code>board/tools/classic.py</code></p>
{draft_note}
<div class="ctl">
<label><input type="checkbox" id="c-draft"> Наложить черновик «карта 5»</label>
<label>прозрачность <input type="range" id="r-op" min="10" max="90" value="50" disabled></label>
<label><input type="checkbox" id="c-grid"> Сетка 50 мм</label>
<label><input type="checkbox" id="c-tint"> Материки разным цветом</label>
<label><input type="checkbox" id="c-wrap"> Склейка краёв: показать соседний край</label>
</div>
<svg id="map" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {CANVAS_W:g} {CANVAS_H:g}">{svg_body(C, ocean, lakes, extras)}</svg>
<div class="cols">
<section><h2>Площади материков, см²</h2>
<table><tr><th>Материк</th><th>Основа</th><th>Черновик</th><th>ТЗ §5.4</th><th>к черновику</th></tr>{rows}
<tr><td><b>Суша всего</b></td><td><b>{land:.0f}</b></td><td>1970</td><td>2470</td><td>{(land/1970 - 1)*100:+.0f} %</td></tr></table>
<p class="sub">Суша — {land/(W*H/100)*100:.0f} % карты. Черновик мерился на полотне 934 × 468 мм; у него Австралия — вместе с Новой Зеландией.</p></section>
<section><h2>Проверки</h2><ul>{checks}</ul></section>
</div>
</main>
<script>
const $=id=>document.getElementById(id);
const show=(id,on)=>{{$(id).style.display=on?'':'none'}};
$('c-draft').onchange=e=>{{show('draft',e.target.checked);$('r-op').disabled=!e.target.checked}};
$('r-op').oninput=e=>{{document.querySelector('#draft image').setAttribute('opacity',e.target.value/100)}};
$('c-grid').onchange=e=>show('grid',e.target.checked);
$('c-tint').onchange=e=>{{document.querySelectorAll('#land path').forEach(p=>p.style.fill=e.target.checked?p.dataset.tint:'')}};
$('c-wrap').onchange=e=>{{show('wrap',e.target.checked);$('map').setAttribute('viewBox',e.target.checked?'-110 0 {CANVAS_W + 220:g} {CANVAS_H:g}':'0 0 {CANVAS_W:g} {CANVAS_H:g}')}};
</script></body></html>
'''


def report(C, ocean, lakes, res):
    L = [f'# Основа поля, классическая — отчёт сборки', '',
         f'Сгенерировано `board/tools/classic.py`, {date.today().isoformat()}. Руками не править.', '',
         f'Полотно {CANVAS_W:g} × {CANVAS_H:g} мм, карта {W:g} × {H:g} мм. Координаты файлов — мм полотна, y вниз.', '',
         '## Площади материков, см²', '',
         '| Материк | Основа | Черновик «карта 5» | ТЗ §5.4 | К черновику |', '|---|---:|---:|---:|---:|']
    for n, a, d, t in area_rows(C):
        L.append(f'| {n} | {a:.0f} | {d:.0f} | {t} | {(a/d - 1)*100:+.0f} % |')
    land = sum(g.area for g in C.values())/100
    L += [f'| **Суша всего** | **{land:.0f}** | 1970 | 2470 | {(land/1970 - 1)*100:+.0f} % |', '',
          f'Суша — {land/(W*H/100)*100:.0f} % карты, океан — {ocean.area/(W*H)*100:.0f} %, '
          f'внутренние воды — {sum(p.area for _, p in lakes)/(W*H)*100:.1f} %.', '',
          '## Проверки', '']
    L += [f'- {"✓" if ok else "✗ **ОТКАЗ**"} {t}' for ok, t in res]
    L += ['', '## Игровые правки поверх географии', '', '| Что | Как | Зачем |', '|---|---|---|']
    L += [f'| {a} | {b} | {c} |' for a, b, c in CORRECTIONS]
    L += ['', '## Внутренние воды', '']
    L += [f'- {nm}: {p.area/100:.1f} см²' for nm, p in lakes]
    return '\n'.join(L) + '\n'


def main(argv):
    cmd = argv[1] if len(argv) > 1 else 'all'
    if cmd not in ('all', 'check'):
        print(__doc__)
        return 2
    S = load_sources()
    w, warpers = warp_all(S)
    C = assemble(w)
    ocean, lakes = waters(C, warpers)
    res = check(C, ocean, lakes, warpers)
    for ok, t in res:
        print(('  ok  ' if ok else 'FAIL  ') + t)
    if not all(ok for ok, _ in res):
        print('\nЕсть отказы — файлы не записаны.')
        return 1
    if cmd == 'check':
        return 0
    OUT.with_suffix('.geojson').write_text(json.dumps(geojson(C, ocean, lakes, res), ensure_ascii=False), encoding='utf-8')
    OUT.with_suffix('.svg').write_text(svg(C, ocean, lakes), encoding='utf-8')
    OUT.with_suffix('.html').write_text(html(C, ocean, lakes, res), encoding='utf-8')
    (GEO / 'classic-base-report.md').write_text(report(C, ocean, lakes, res), encoding='utf-8')
    print(f'\nЗаписано: {OUT.name}.geojson, .svg, .html, classic-base-report.md')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
