#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
worldgeom.py — сборка эталонной географической основы «Нефтяных войн».

Master geometry проекта: чистая векторная география Земли (материки, острова,
океан) в WGS84, из которой детерминированно получаются нормализованное
представление, SVG и любая проекция под конкретное полотно.

Игровых регионов здесь нет и быть не должно — см. registry/map/geo/README.md.

Запуск:
    python tools/worldgeom.py all      # build + check + write + report
    python tools/worldgeom.py check    # build + check, ничего не пишет

Зависимости: shapely >= 2.0. Питона на машине нет — гонять в Docker:
    docker run --rm -v "C:/YandexDisk/Oil Wars/.agents:/w" -w /w python:3.12-slim \
      sh -c "pip install --quiet shapely && python tools/worldgeom.py all"
"""

from __future__ import annotations

import json
import math
import os
import sys
import hashlib
import datetime
from collections import OrderedDict

from shapely.geometry import (shape, mapping, box, Polygon, MultiPolygon, Point,
                              LineString)
from shapely.geometry.polygon import orient
from shapely.ops import unary_union, transform as shp_transform, nearest_points
from shapely import make_valid, set_precision

# ---------------------------------------------------------------------------
# 0. Пути и константы
# ---------------------------------------------------------------------------

HERE = os.path.dirname(os.path.abspath(__file__))
AGENTS = os.path.dirname(HERE)
GEO = os.path.join(AGENTS, "registry", "map", "geo")
SRC = os.path.join(GEO, "src")

VERSION = "1.0.0"

R_EARTH = 6371.0088                 # средний радиус Земли, км (IUGG)
WORLD = (-180.0, -90.0, 180.0, 90.0)

SIMPLIFY_TOL_DEG = 0.04             # Дуглас — Пекер, градусы (~4.4 км на экваторе)
MIN_ISLAND_KM2 = 5000.0             # порог значимого острова
SPLIT_MIN_KM2 = 1_000_000.0         # что режется доменами, а что относится целиком
GRID_PRECISION = 1e-9               # сетка округления координат
COORD_ND = 5                        # знаков в master GeoJSON: 1e-5° ≈ 1.1 м
COORD_ND_NORM = 8                   # знаков в нормализованном: 1e-8 × 360° ≈ 0.4 м

NAMES_RU = {
    "north_america": "Северная Америка",
    "south_america": "Южная Америка",
    "europe": "Европа",
    "africa": "Африка",
    "asia": "Азия",
    "australia": "Австралия и Океания",
    "antarctica": "Антарктида",
    "ocean": "Мировой океан",
    "arctic": "Северный Ледовитый океан",
    "north_atlantic": "Север Атлантического океана",
    "south_atlantic": "Юг Атлантического океана",
    "north_pacific": "Север Тихого океана",
    "south_pacific": "Юг Тихого океана",
    "indian": "Индийский океан",
    "caspian": "Каспийское море",
}

# Замкнутые водоёмы, которые слой Land оставляет дырой в суше и которые поэтому
# попадают в маску OCEAN. Опознаются по внутренней точке; выносятся отдельным
# справочным слоем, чтобы следующий этап мог их исключить.
INLAND_WATERS = [
    ("caspian", "Каспийское море", 51.0, 42.0),
]

CONTINENT_ORDER = ["north_america", "south_america", "europe", "africa",
                   "asia", "australia", "antarctica"]
BASIN_ORDER = ["arctic", "north_atlantic", "south_atlantic",
               "north_pacific", "south_pacific", "indian"]

# Именованные острова: точка внутри + имя. Справочный слой, геометрия берётся
# из того же LAND, отдельной геометрии не заводится.
NAMED_ISLANDS = [
    ("australia_mainland", "Австралия, материковая часть", 134.0, -25.0),
    ("greenland", "Гренландия", -42.0, 72.0),
    ("new_guinea", "Новая Гвинея", 141.0, -5.0),
    ("borneo", "Калимантан", 114.0, 0.5),
    ("madagascar", "Мадагаскар", 46.7, -19.0),
    ("baffin", "Баффинова Земля", -70.0, 68.0),
    ("sumatra", "Суматра", 101.5, -0.5),
    ("honshu", "Хонсю", 139.0, 36.5),
    ("great_britain", "Великобритания", -1.5, 53.0),
    ("victoria_island", "Виктория", -110.0, 71.0),
    ("ellesmere", "Элсмир", -78.0, 79.5),
    ("sulawesi", "Сулавеси", 120.5, -2.0),
    ("south_island_nz", "Южный остров, Новая Зеландия", 171.0, -43.5),
    ("north_island_nz", "Северный остров, Новая Зеландия", 175.5, -39.0),
    ("java", "Ява", 110.0, -7.3),
    ("luzon", "Лусон", 121.0, 16.0),
    ("iceland", "Исландия", -19.0, 65.0),
    ("mindanao", "Минданао", 125.0, 7.8),
    ("ireland", "Ирландия", -8.0, 53.3),
    ("hokkaido", "Хоккайдо", 142.8, 43.5),
    ("hispaniola", "Гаити", -71.5, 19.0),
    ("sakhalin", "Сахалин", 142.8, 50.5),
    ("tasmania", "Тасмания", 146.8, -42.0),
    ("sri_lanka", "Шри-Ланка", 80.7, 7.8),
    ("cuba", "Куба", -79.0, 21.8),
    ("novaya_zemlya", "Новая Земля", 56.0, 73.5),
    ("tierra_del_fuego", "Огненная Земля", -68.5, -54.0),
    ("svalbard", "Шпицберген", 16.0, 78.0),
    ("taiwan", "Тайвань", 121.0, 23.8),
    ("hainan", "Хайнань", 109.7, 19.2),
    ("sicily", "Сицилия", 14.0, 37.6),
    ("sardinia", "Сардиния", 9.1, 40.1),
    ("new_caledonia", "Новая Каледония", 165.8, -21.5),
    ("falklands", "Фолкленды", -59.0, -51.7),
    ("cyprus", "Кипр", 33.2, 35.0),
    ("crete", "Крит", 24.8, 35.2),
    ("corsica", "Корсика", 9.1, 42.2),
]

# ---------------------------------------------------------------------------
# 1. Площади и расстояния на сфере
# ---------------------------------------------------------------------------

def _cyl_equal_area(x, y, z=None):
    """Ламбертова цилиндрическая равновеликая: площадь в этой плоскости = площадь на сфере."""
    return (math.radians(x) * R_EARTH, R_EARTH * math.sin(math.radians(y)))


def area_km2(geom) -> float:
    if geom.is_empty:
        return 0.0
    return shp_transform(_cyl_equal_area, geom).area


def laea(lon0: float, lat0: float):
    """Ламбертова азимутальная равновеликая с центром (lon0, lat0) — для локальных замеров."""
    l0, p0 = math.radians(lon0), math.radians(lat0)
    sp0, cp0 = math.sin(p0), math.cos(p0)

    def fwd(x, y, z=None):
        l, p = math.radians(x), math.radians(y)
        dl = l - l0
        cosc = sp0 * math.sin(p) + cp0 * math.cos(p) * math.cos(dl)
        k = math.sqrt(max(0.0, 2.0 / (1.0 + cosc)))
        return (R_EARTH * k * math.cos(p) * math.sin(dl),
                R_EARTH * k * (cp0 * math.sin(p) - sp0 * math.cos(p) * math.cos(dl)))

    return fwd


def haversine_km(a, b) -> float:
    lon1, lat1 = math.radians(a[0]), math.radians(a[1])
    lon2, lat2 = math.radians(b[0]), math.radians(b[1])
    h = (math.sin((lat2 - lat1) / 2) ** 2
         + math.cos(lat1) * math.cos(lat2) * math.sin((lon2 - lon1) / 2) ** 2)
    return 2 * R_EARTH * math.asin(min(1.0, math.sqrt(h)))


def geo_min_distance_km(g1, g2):
    p1, p2 = nearest_points(g1, g2)
    return haversine_km((p1.x, p1.y), (p2.x, p2.y)), (p1.x, p1.y), (p2.x, p2.y)


# ---------------------------------------------------------------------------
# 2. Чистка геометрии
# ---------------------------------------------------------------------------

def _polygons_only(geom):
    if geom.is_empty:
        return geom
    gt = geom.geom_type
    if gt in ("Polygon", "MultiPolygon"):
        return geom
    parts = []
    for g in getattr(geom, "geoms", []):
        if g.geom_type == "Polygon":
            parts.append(g)
        elif g.geom_type == "MultiPolygon":
            parts.extend(g.geoms)
    if not parts:
        return Polygon()
    return MultiPolygon(parts) if len(parts) > 1 else parts[0]


def orient_geom(geom):
    """Ориентация колец по RFC 7946: внешнее против часовой, дыры по часовой."""
    if geom.is_empty or geom.geom_type not in ("Polygon", "MultiPolygon"):
        return geom
    ps = [orient(p, 1.0) for p in parts_of(geom)]
    if not ps:
        return geom
    return MultiPolygon(ps) if len(ps) > 1 else ps[0]


def clean(geom):
    """make_valid + округление на сетку + отбрасывание неполигональных остатков."""
    if geom.is_empty:
        return geom
    if not geom.is_valid:
        geom = make_valid(geom)
    geom = set_precision(geom, GRID_PRECISION)
    geom = _polygons_only(geom)
    if not geom.is_empty and not geom.is_valid:
        geom = _polygons_only(make_valid(geom))
    return orient_geom(geom)


def parts_of(geom):
    if geom.is_empty:
        return []
    return list(geom.geoms) if geom.geom_type == "MultiPolygon" else [geom]


def drop_slivers(geom, min_km2=1.0):
    keep = [p for p in parts_of(geom) if area_km2(p) >= min_km2]
    if not keep:
        return Polygon()
    return MultiPolygon(keep) if len(keep) > 1 else keep[0]


def nvertices(geom) -> int:
    n = 0
    for p in parts_of(geom):
        n += len(p.exterior.coords)
        for r in p.interiors:
            n += len(r.coords)
    return n


# ---------------------------------------------------------------------------
# 3. Домены материков — разбиение прямоугольника мира
# ---------------------------------------------------------------------------
# Домены применяются ПО ПОРЯДКУ, каждый обрезается по незанятому остатку.
# Перекрытия поэтому невозможны по построению, а последний домен забирает всё,
# что осталось. Обоснование каждой линии — в отчёте, раздел «Границы материков».

def _poly(coords):
    return clean(Polygon(coords))


# Линия Африка — Европа по Средиземному морю. Один список на оба домена, чтобы
# они не разошлись при правке. Идёт с запада на восток; каждая вершина подобрана
# по фактическим широтам берега после упрощения (проверяется контрольными точками).
MED_LINE = [
    (-6.40, 36.25),          # западный вход в Гибралтарский пролив
    (-5.60, 35.96),          # ось пролива: Марокко до 35.88, Испания от 36.03
    (-5.00, 36.00),
    (0.00, 37.30),           # севернее алжирского берега (36.42 на 1° в.д.)
    (5.00, 37.60),           # южнее Балеарских островов (от 38.6)
    (9.00, 37.85),           # южнее Сардинии (от 39.07)
    (11.00, 37.75),          # севернее мыса Бон (37.07)
    (12.60, 37.30),          # западнее Сицилии
    (15.00, 36.00),          # южнее мыса Пассеро (36.65)
    (23.00, 34.30),          # южнее Крита (юг Крита 34.80)
    (32.00, 33.00),          # южнее Кипра (юг Кипра 34.56)
]

# Линия Африка — Азия: Суэц, Красное море, Баб-эль-Мандеб, Аденский залив.
SUEZ_LINE = [
    (33.20, 31.40),          # Порт-Саид (32.32, 31.26)
    (32.55, 30.60),          # Суэцкий канал
    (32.80, 29.90),          # Суэцкий залив
    (34.30, 27.70),          # ось Красного моря
    (38.50, 20.00),
    (41.50, 15.00),
    (43.20, 12.70),          # Баб-эль-Мандеб: Африка до 12.57, Аравия от 13.90
    (44.00, 12.20),
    (48.00, 12.95),          # Аденский залив: Сомали до 11.14, Йемен от 14.05
    (52.00, 13.50),
    (60.00, 13.50),
]


def continent_domains():
    W, S, E, N = WORLD[0], WORLD[1], WORLD[2], WORLD[3]

    # 1. Антарктида: южнее 60° ю.ш. (граница Южного океана, IHO 2000)
    antarctica = _poly([(W, S), (E, S), (E, -60.0), (W, -60.0)])

    # 2. Австралия и Океания. Линия Азия|Океания по 141° в.д. (граница Индонезии
    #    и Папуа — Новой Гвинеи); южнее 11° ю.ш. уходит на запад к 110° в.д.,
    #    чтобы забрать Австралию и не забрать Яву и Малые Зондские острова.
    australia = _poly([
        (110.0, -60.0), (110.0, -11.0), (141.0, -11.0), (141.0, 0.0),
        (180.0, 0.0), (180.0, -60.0),
    ])
    oceania_east = _poly([(-180.0, -60.0), (-172.0, -60.0), (-172.0, 0.0), (-180.0, 0.0)])

    # 3. Африка. Восток: Суэцкий перешеек → Красное море → Баб-эль-Мандеб →
    #    Индийский океан до 60° в.д. Север: Средиземное море между мысом Бланко
    #    (Тунис, 37.35° с.ш.) и югом Сицилии (36.65° с.ш.), далее южнее Крита и Кипра.
    africa = _poly([(-30.0, -60.0), (-30.0, 36.25)] + MED_LINE + SUEZ_LINE + [(60.00, -60.0)])

    # 4. Европа. Запад: Атлантика до 35° з.д., затем Датский пролив (Гренландия
    #    по ту сторону, Исландия по эту), затем на север мимо Шпицбергена.
    #    Восток: Урал → река Урал → Каспий → Кума-Манычская впадина → Керченский
    #    пролив → Босфор → Эгейское море.
    europe = _poly(
        [(-35.0, 36.25), (-35.0, 55.0),
         (-30.0, 63.0), (-20.0, 68.0), (-10.0, 71.0), (-5.0, 74.0), (-5.0, 90.0),
         (69.0, 90.0), (69.0, 74.0),                 # восточнее Новой Земли
         (66.0, 69.5),                               # Байдарацкая губа, западнее Ямала
         (60.5, 65.0), (59.5, 55.0), (57.5, 51.0),   # Уральский хребет
         (51.90, 47.10),                             # устье реки Урал
         (47.50, 45.70), (39.00, 45.30), (37.50, 45.00),   # Кума-Манычская впадина, Керчь
         (29.10, 41.10),                             # Босфор
         (26.50, 40.50), (26.50, 34.00),             # Эгейское море: Крит — Европа, Родос и Кипр — Азия
         ] + list(reversed(MED_LINE))
    )

    # 5. Южная Америка. Север: Дарьенский перешеек (граница Колумбии и Панамы),
    #    далее на восток южнее Малых Антильских островов.
    south_america = _poly([
        (-180.0, -60.0), (-180.0, 0.0), (-100.0, 2.0),
        (-79.00, 6.00), (-77.90, 7.22), (-77.35, 8.67),   # граница Панамы и Колумбии
        (-77.30, 11.50), (-60.00, 11.60),   # Тринидад (10.8) — Южная, Барбадос (13.1) — Северная
        (-30.00, 11.60), (-30.00, -60.0),
    ])

    # 6. Азия: остаток восточного полушария плюс полоса Чукотки за антимеридианом
    #    до Берингова пролива (мыс Дежнёва, 169.66° з.д.).
    asia_main = _poly([(20.0, -60.0), (20.0, 90.0), (180.0, 90.0), (180.0, -60.0)])
    asia_chukotka = _poly([(-180.0, 58.0), (-168.95, 58.0), (-168.95, 90.0), (-180.0, 90.0)])

    # 7. Северная Америка — остаток мира.
    north_america = _poly([(W, S), (E, S), (E, N), (W, N)])

    return OrderedDict([
        ("antarctica", antarctica),
        ("australia", clean(unary_union([australia, oceania_east]))),
        ("africa", africa),
        ("europe", europe),
        ("south_america", south_america),
        ("asia", clean(unary_union([asia_main, asia_chukotka]))),
        ("north_america", north_america),
    ])


CONTINENT_SPOT_CHECKS = [
    ((-76.8, 7.6), "south_america", "Дарьен, колумбийская сторона"),
    ((-79.5, 9.0), "north_america", "Панамский канал"),
    ((10.2, 36.9), "africa", "мыс Бон, Тунис"),
    ((13.4, 37.5), "europe", "Сицилия"),
    ((24.9, 35.2), "europe", "Крит"),
    ((33.3, 35.0), "asia", "Кипр"),
    ((34.0, 29.5), "asia", "Синай"),
    ((31.2, 30.0), "africa", "Каир"),
    ((-18.0, 65.0), "europe", "Исландия"),
    ((-40.0, 72.0), "north_america", "Гренландия"),
    ((16.0, 78.0), "europe", "Шпицберген"),
    ((56.0, 73.5), "europe", "Новая Земля"),
    ((70.0, 68.5), "asia", "Ямал"),
    ((59.0, 58.0), "europe", "Западный Урал"),
    ((-173.0, 66.5), "asia", "Чукотка за антимеридианом"),
    ((-162.0, 65.0), "north_america", "полуостров Сьюард, Аляска"),
    ((142.0, -5.0), "australia", "Новая Гвинея, папуасская сторона"),
    # Новая Гвинея меньше порога разреза и относится целиком к Океании —
    # намеренное отступление от геосхемы ООН, см. отчёт, «Известные ограничения».
    ((138.0, -4.5), "australia", "Новая Гвинея, индонезийская сторона"),
    ((120.5, -8.6), "asia", "Флорес, Малые Зондские"),
    ((146.0, -20.0), "australia", "Квинсленд"),
    ((172.0, -43.0), "australia", "Южный остров Новой Зеландии"),
    ((46.7, -19.0), "africa", "Мадагаскар"),
    ((-68.5, -54.0), "south_america", "Огненная Земля"),
    ((-63.0, -66.0), "antarctica", "Антарктический полуостров"),
    ((14.0, 37.6), "europe", "Сицилия, центр"),
    ((-52.0, -10.0), "south_america", "центр Бразилии"),
    ((90.0, 60.0), "asia", "центральная Сибирь"),
]


# ---------------------------------------------------------------------------
# 4. Домены океанских бассейнов (справочный слой)
# ---------------------------------------------------------------------------

ARCTIC_CIRCLE = 66.5622


def basin_domains():
    W, S, E, N = WORLD[0], WORLD[1], WORLD[2], WORLD[3]

    arctic = _poly([(W, ARCTIC_CIRCLE), (E, ARCTIC_CIRCLE), (E, N), (W, N)])

    # Индийский: 20° в.д. (мыс Игольный) — 146°49' в.д. (Тасмания); северо-восток
    # по проливам Индонезии — упрощённая линия IHO.
    indian = _poly([
        (20.0, S), (20.0, 35.0), (60.0, 35.0), (80.0, 35.0), (97.0, 28.0),
        (99.0, 10.0), (100.60, 2.00),       # Малаккский пролив
        (105.90, -6.00),                     # Зондский пролив
        (110.0, -8.20), (120.0, -9.20), (125.5, -9.30),   # южнее Малых Зондских
        (127.0, -11.0), (126.95, -13.75),    # мыс Лондондерри, Австралия
        (140.0, -30.0),                      # по суше Австралии, воды не касается
        (146.82, -43.60),                    # мыс Саут-Ист, Тасмания
        (146.82, S),
    ])

    # Атлантический: восток — 20° в.д. и Средиземноморье; запад — водораздел
    # Америк и Дрейков пролив по 67° з.д.
    atlantic = _poly([
        (-67.0, S), (-67.0, -55.5), (-70.0, -40.0), (-73.0, -10.0),
        (-77.50, 7.50),                      # Дарьен
        (-84.0, 15.0), (-100.0, 30.0), (-115.0, 50.0), (-135.0, 60.0), (-141.0, 70.0),
        (-141.0, N), (42.0, N),
        (42.0, 42.0), (36.0, 42.0), (36.0, 34.0), (32.0, 31.0), (20.0, 32.0),
        (20.0, S),
    ])

    pacific = _poly([(W, S), (E, S), (E, N), (W, N)])   # остаток

    return OrderedDict([
        ("arctic", arctic),
        ("indian", indian),
        ("atlantic", atlantic),
        ("pacific", pacific),
    ])


BASIN_SPOT_CHECKS = [
    ((-30.0, 40.0), "north_atlantic", "середина Северной Атлантики"),
    ((-20.0, -30.0), "south_atlantic", "середина Южной Атлантики"),
    ((-150.0, 30.0), "north_pacific", "середина Северной Пацифики"),
    ((-120.0, -30.0), "south_pacific", "середина Южной Пацифики"),
    ((80.0, -20.0), "indian", "середина Индийского"),
    ((0.0, 85.0), "arctic", "Северный полюс"),
    ((-172.0, 60.0), "north_pacific", "Берингово море"),
    ((-170.0, 70.0), "arctic", "Чукотское море"),
    ((-40.0, -65.0), "south_atlantic", "море Уэдделла"),
    ((114.0, 14.0), "north_pacific", "Южно-Китайское море"),
    ((90.0, 15.0), "indian", "Бенгальский залив"),
    ((17.0, 35.0), "north_atlantic", "Средиземное море"),
    ((180.0, -72.0), "south_pacific", "море Росса"),
    ((90.0, -63.0), "indian", "море Дейвиса"),
]


# ---------------------------------------------------------------------------
# 5. Сборка
# ---------------------------------------------------------------------------

def load_land():
    path = os.path.join(SRC, "ne_50m_land.json")
    with open(path, "rb") as f:
        raw = f.read()
    sha = hashlib.sha256(raw).hexdigest()
    data = json.loads(raw.decode("utf-8"))
    geoms = []
    for feat in data["features"]:
        g = clean(shape(feat["geometry"]))
        if not g.is_empty:
            geoms.append(g)
    return geoms, sha, len(data["features"])


def build():
    log = []

    raw_geoms, src_sha, src_features = load_land()
    raw_union = clean(unary_union(raw_geoms))
    raw_parts = parts_of(raw_union)
    raw_area = area_km2(raw_union)
    log.append(("load", f"ne_50m_land.json: {src_features} записей → {len(raw_parts)} связных "
                        f"кусков, {nvertices(raw_union)} вершин, {raw_area:,.0f} км²"))

    kept, dropped = [], []
    for p in raw_parts:
        a = area_km2(p)
        (kept if a >= MIN_ISLAND_KM2 else dropped).append((a, p))
    dropped_area = sum(a for a, _ in dropped)
    log.append(("filter", f"порог значимого острова {MIN_ISLAND_KM2:,.0f} км²: оставлено "
                          f"{len(kept)} кусков, отброшено {len(dropped)} общей площадью "
                          f"{dropped_area:,.0f} км² ({dropped_area / raw_area * 100:.2f} % суши)"))

    land_raw = clean(unary_union([p for _, p in kept]))

    simp = []
    for p in parts_of(land_raw):
        s = clean(p.simplify(SIMPLIFY_TOL_DEG, preserve_topology=True))
        if not s.is_empty and area_km2(s) > 0:
            simp.append(s)
    land = drop_slivers(clean(unary_union(simp)), 1.0)
    log.append(("simplify", f"Дуглас — Пекер, допуск {SIMPLIFY_TOL_DEG}° "
                            f"(~{SIMPLIFY_TOL_DEG * 111.3:.1f} км на экваторе): "
                            f"{nvertices(land_raw)} → {nvertices(land)} вершин, площадь "
                            f"{area_km2(land_raw):,.0f} → {area_km2(land):,.0f} км² "
                            f"({(area_km2(land) / area_km2(land_raw) - 1) * 100:+.3f} %)"))

    # --- материки ---------------------------------------------------------
    domains = continent_domains()
    world_poly = box(*WORLD)
    dom_final, used = OrderedDict(), Polygon()
    for cid, d in domains.items():
        d2 = clean(d.intersection(world_poly).difference(used))
        dom_final[cid] = d2
        used = clean(unary_union([used, d2]))
    leftover_area = area_km2(clean(world_poly.difference(used)))
    if leftover_area > 1.0:
        raise RuntimeError(f"домены не покрывают мир, остаток {leftover_area:,.0f} км²")

    buckets = {cid: [] for cid in dom_final}
    n_split = 0
    for p in parts_of(land):
        if area_km2(p) >= SPLIT_MIN_KM2:
            n_split += 1
            for cid, d in dom_final.items():
                piece = drop_slivers(clean(p.intersection(d)), 1.0)
                if not piece.is_empty:
                    buckets[cid].append(piece)
        else:
            rp = p.representative_point()
            for cid, d in dom_final.items():
                if d.intersects(rp):
                    buckets[cid].append(p)
                    break
            else:
                raise RuntimeError(f"кусок суши не попал ни в один домен: {p.bounds}")

    continents = OrderedDict()
    for cid in CONTINENT_ORDER:
        g = clean(unary_union(buckets[cid])) if buckets[cid] else Polygon()
        continents[cid] = drop_slivers(g, 1.0)
    log.append(("continents", f"материки = суша ∩ домен; доменами разрезано {n_split} "
                              f"мегакуска, остальные отнесены целиком по внутренней точке"))

    land_all = clean(unary_union(list(continents.values())))
    ocean = drop_slivers(clean(world_poly.difference(land_all)), 1.0)
    log.append(("ocean", f"OCEAN = прямоугольник мира − LAND: {len(parts_of(ocean))} кусков, "
                         f"{area_km2(ocean):,.0f} км²"))

    # --- бассейны ---------------------------------------------------------
    bdoms = basin_domains()
    b_final, used = OrderedDict(), Polygon()
    for bid, d in bdoms.items():
        d2 = clean(d.intersection(world_poly).difference(used))
        b_final[bid] = d2
        used = clean(unary_union([used, d2]))

    eq_north = box(-180, 0, 180, 90)
    eq_south = box(-180, -90, 180, 0)
    basins = {}
    basins["arctic"] = drop_slivers(clean(ocean.intersection(b_final["arctic"])), 1.0)
    basins["indian"] = drop_slivers(clean(ocean.intersection(b_final["indian"])), 1.0)
    for base, nid, sid in [("atlantic", "north_atlantic", "south_atlantic"),
                           ("pacific", "north_pacific", "south_pacific")]:
        g = clean(ocean.intersection(b_final[base]))
        basins[nid] = drop_slivers(clean(g.intersection(eq_north)), 1.0)
        basins[sid] = drop_slivers(clean(g.intersection(eq_south)), 1.0)
    basins = OrderedDict((k, basins[k]) for k in BASIN_ORDER)
    log.append(("basins", "бассейны = OCEAN ∩ домен бассейна; линии конвенциональные, "
                          "слой справочный, игровыми регионами не является"))

    # --- именованные острова ---------------------------------------------
    islands = OrderedDict()
    for iid, name, lon, lat in NAMED_ISLANDS:
        pt = Point(lon, lat)
        found = None
        for p in parts_of(land_all):
            if p.intersects(pt):
                found = p
                break
        if found is not None:
            islands[iid] = (name, found)
    missing = [n for i, n, lo, la in NAMED_ISLANDS if i not in islands]
    log.append(("islands", f"справочный слой именованных островов: {len(islands)} из "
                           f"{len(NAMED_ISLANDS)} опознано по внутренней точке"
                           + (f"; не найдены (ниже порога): {', '.join(missing)}" if missing else "")))

    # --- замкнутые водоёмы внутри суши ------------------------------------
    inland = OrderedDict()
    ocean_parts = sorted(parts_of(ocean), key=area_km2, reverse=True)
    for wid, name, lon, lat in INLAND_WATERS:
        pt = Point(lon, lat)
        for p in ocean_parts[1:]:
            if p.intersects(pt):
                inland[wid] = (name, p)
                break
    log.append(("inland", f"маска OCEAN состоит из {len(ocean_parts)} кусков: "
                          f"мировой океан + {len(ocean_parts) - 1} замкнутых водоёмов, "
                          f"опознано {len(inland)}"))

    return {
        "inland": inland,
        "land": land_all,
        "continents": continents,
        "ocean": ocean,
        "basins": basins,
        "islands": islands,
        "log": log,
        "src_sha": src_sha,
        "src_features": src_features,
        "raw_area": raw_area,
        "raw_parts": len(raw_parts),
        "raw_vertices": nvertices(raw_union),
        "dropped": dropped,
        "dropped_area": dropped_area,
        "kept_parts": len(kept),
        "raw_union": raw_union,
    }


# ---------------------------------------------------------------------------
# 6. Преобразования координат
# ---------------------------------------------------------------------------
# Нормализованное пространство: равнопромежуточная цилиндрическая (plate carrée),
# 360° долготы = 1.0, начало в левом верхнем углу, Y вниз. Изотропно:
#   x = (lon + 180) / 360   ∈ [0, 1]
#   y = ( 90 - lat) / 360   ∈ [0, 0.5]

def norm_fwd(x, y, z=None):
    return ((x + 180.0) / 360.0, (90.0 - y) / 360.0)


def norm_inv(x, y):
    return (x * 360.0 - 180.0, 90.0 - y * 360.0)


def polar_fwd_factory(kind="equidistant", lon0=0.0, scale=1.0):
    """Южно-полярная азимутальная: r = 0 в Южном полюсе, r = scale в Северном.

    equidistant — r пропорционален (90 + lat), сохраняет расстояния по меридиану;
    equal_area  — r = 2·sin((90 + lat)/2), сохраняет площади.
    """
    if kind == "equidistant":
        def rad(lat):
            return (lat + 90.0) / 180.0
    elif kind == "equal_area":
        rmax = 2.0 * math.sin(math.pi / 2.0)

        def rad(lat):
            return 2.0 * math.sin(math.radians(lat + 90.0) / 2.0) / rmax
    else:
        raise ValueError(kind)

    def fwd(x, y, z=None):
        r = rad(y) * scale
        a = math.radians(x - lon0)
        return (r * math.sin(a), -r * math.cos(a))

    return fwd


def project(geom, fwd):
    return shp_transform(fwd, geom)


# ---------------------------------------------------------------------------
# 7. Масштабный разрыв: что требует игра против того, что даёт география
# ---------------------------------------------------------------------------
# Полотно карты 880 × 530 мм = 4664 см² (ТЗ §2). Целевые площади игровых
# областей — ТЗ §5.2 и §5.3. Здесь они сводятся к материкам, чтобы увидеть,
# во сколько раз игра растягивает каждый кусок географии.

BOARD_CM2 = 4664.0

GAME_TARGETS = OrderedDict([
    ("north_america", (490, "Центральная Америка 150 + Восток 165 + Запад 175")),
    ("south_america", (320, "Запад 160 + Восток 160")),
    ("europe", (330, "Европа 175 + Скандинавия 155")),
    ("africa", (335, "Западная 170 + Восточная 165")),
    ("asia", (510, "Северная 165 + Южная 180 + Аравийский полуостров 165")),
    ("australia", (300, "Австралия 150 + Новая Зеландия 150")),
    ("antarctica", (185, "одна область")),
    ("ocean", (2192, "шесть океанов, ТЗ §5.3")),
])

# Отдельные куски, по которым разрыв виден резче всего.
GAME_TARGETS_SPOT = [
    ("Новая Зеландия", 150, ["south_island_nz", "north_island_nz"]),
    ("Австралия, материк", 150, ["australia_mainland"]),
    ("Антарктида", 185, None),
]


def true_scale_cm2(area_km2_value):
    """Сколько см² заняла бы эта площадь на полотне при честном равновеликом масштабе."""
    return area_km2_value / 510_072_000.0 * BOARD_CM2


# ---------------------------------------------------------------------------
# 8. Диагностика под будущее разбиение
# ---------------------------------------------------------------------------

NARROW_PLACES = [
    ("Панамский перешеек", (-79.6, 9.0), 3.0),
    ("Суэцкий перешеек", (32.5, 30.2), 2.5),
    ("Перешеек Кра", (99.2, 10.3), 2.0),
    ("Коринфский перешеек", (23.0, 37.95), 1.0),
    ("Мексика, перешеек Теуантепек", (-94.8, 16.5), 2.5),
]

WATER_GAPS = [
    ("Берингов пролив", (-169.0, 65.8), "asia", "north_america"),
    ("Гибралтарский пролив", (-5.5, 35.95), "europe", "africa"),
    ("Баб-эль-Мандеб", (43.3, 12.6), "asia", "africa"),
    ("Дрейков пролив", (-63.0, -59.0), "south_america", "antarctica"),
    ("Датский пролив", (-27.0, 67.0), "europe", "north_america"),
    # «at:lon,lat» — кусок суши, содержащий эту точку; так меряются проливы
    # внутри одного материка, которые разделом материков не ловятся.
    ("Торресов пролив", (142.5, -9.7), "at:134,-25", "at:141.5,-5"),
    ("Ла-Манш", (1.5, 50.5), "at:-1.5,53", "at:5,48"),
    ("Мозамбикский пролив", (41.0, -17.0), "at:46.7,-19", "at:30,-18"),
    ("Пролив Кука", (174.5, -41.3), "at:175.5,-39", "at:171,-43.5"),
    ("Флоридский пролив (архипелаг Кис ниже порога)", (-81.0, 24.0),
     "at:-79,21.8", "at:-81.5,28"),
    ("Ла-Перуза, пролив", (141.9, 45.8), "at:142.8,50.5", "at:142.8,43.5"),
]


def measure_narrow(land):
    res = []
    for name, (lon, lat), rad_deg in NARROW_PLACES:
        fwd = laea(lon, lat)
        window = box(lon - rad_deg, lat - rad_deg, lon + rad_deg, lat + rad_deg)
        piece = clean(land.intersection(window))
        if piece.is_empty:
            res.append((name, None))
            continue
        g = shp_transform(fwd, piece)
        if not g.is_valid:
            g = make_valid(g)
        n0 = len(parts_of(g))
        lo, hi = 0.0, 400.0
        while hi - lo > 0.5:
            mid = (lo + hi) / 2
            e = g.buffer(-mid)
            if e.is_empty or len(parts_of(e)) > n0:
                hi = mid
            else:
                lo = mid
        res.append((name, round(lo * 2, 1)))
    return res


def _resolve_side(spec, continents, land):
    """Сторона пролива: id материка либо `at:lon,lat` — кусок суши в этой точке."""
    if spec.startswith("at:"):
        lon, lat = (float(v) for v in spec[3:].split(","))
        pt = Point(lon, lat)
        for p in parts_of(land):
            if p.intersects(pt):
                return p, f"кусок в ({lon}, {lat})"
        return None, spec
    return continents[spec], f"`{spec}`"


def measure_gaps(continents, land):
    res = []
    for name, near, a, b in WATER_GAPS:
        win = box(near[0] - 12, near[1] - 12, near[0] + 12, near[1] + 12)
        ga, la = _resolve_side(a, continents, land)
        gb, lb = _resolve_side(b, continents, land)
        if ga is None or gb is None:
            res.append((name, None, la, lb, None, None))
            continue
        pa, pb = ga.intersection(win), gb.intersection(win)
        if pa.is_empty or pb.is_empty:
            res.append((name, None, la, lb, None, None))
            continue
        d, p1, p2 = geo_min_distance_km(pa, pb)
        res.append((name, round(d, 1), la, lb,
                    (round(p1[0], 2), round(p1[1], 2)), (round(p2[0], 2), round(p2[1], 2))))
    return res


def max_inscribed_km(geom, eps=5.0):
    c = geom.representative_point()
    fwd = laea(c.x, c.y)
    g = shp_transform(fwd, geom)
    if not g.is_valid:
        g = make_valid(g)
    lo, hi = 0.0, 3000.0
    while hi - lo > eps:
        mid = (lo + hi) / 2
        if g.buffer(-mid).is_empty:
            hi = mid
        else:
            lo = mid
    return lo


def mainland_share(geom):
    ps = parts_of(geom)
    if not ps:
        return 0.0, 0
    areas = sorted((area_km2(p) for p in ps), reverse=True)
    return areas[0] / sum(areas), len(ps)


# ---------------------------------------------------------------------------
# 8b. Игровая база: коррекции поверх master
# ---------------------------------------------------------------------------
# Решение Alek 2026-09-17 (MF-016): игровая функция и узнаваемость важнее
# точных пропорций. Master остаётся честной географией и не трогается —
# коррекции живут отдельным слоем и применяются к нему детерминированно,
# каждая с причиной. Результат — world-game.geojson.

# Минимальный читаемый остров. Полотно 880 × 530 мм на весь мир даёт
# 1 мм² ≈ 1094 км², поэтому 15 000 км² — это примерно 3.7 × 3.7 мм:
# нижняя граница, на которой остров ещё виден и его силуэт читается.
MIN_VISIBLE_KM2 = 15000.0

# Острова ниже порога отбора, которые возвращаются: каждый чем-то полезен
# на поле — якорит океанскую область или подпирает узел.
RESTORE_ISLANDS = [
    ("trinidad", "Тринидад", -61.25, 10.43, "карибский якорь у панамского узла"),
    ("falklands", "Фолклендские острова", -59.98, -51.79,
     "единственная суша в Юге Атлантического океана"),
    ("galapagos", "Галапагосские острова", -91.09, -0.46, "якорь Севера Тихого океана"),
    ("socotra", "Сокотра", 53.90, 12.50, "якорь Индийского океана у Аравии"),
    ("azores", "Азорские острова", -28.20, 38.50, "якорь Севера Атлантики"),
    ("canaries", "Канарские острова", -15.60, 28.10, "якорь у западного берега Африки"),
    ("mauritius", "Маврикий и Реюньон", 56.00, -20.30, "якорь юга Индийского океана"),
    ("tahiti", "Таити", -149.45, -17.65, "якорь Юга Тихого океана"),
]

# Локальное расширение суши. Окно, целевая ширина перешейка, причина.
# Считается в локальной равновеликой азимутальной: суша в окне раздувается
# на (цель − факт) / 2 и приклеивается обратно.
WIDEN = [
    ("panama", (-82.6, 6.0, -76.6, 12.0), "Панамский перешеек", 150.0,
     "узел рисуется первым (ТЗ §6.3): шесть обязательных рёбер и одно "
     "обязательное не-ребро. 51 км — это 1.1 мм на полотне, рисовать не по чему, "
     "а выдумать сушу разбиение не может"),
    ("suez", (31.5, 28.8, 34.6, 31.4), "Суэцкий перешеек", 0.0,
     "рассмотрено и отклонено: узость Синая ничему не мешает — границу областей "
     "Западная Африка / Аравийский полуостров разбиение кладёт где хочет, "
     "суша там сплошная. Расширение съело бы Суэцкий залив и залив Акаба, "
     "то есть узнаваемый силуэт, ради нуля"),
    ("bering", (-176.0, 60.0, -160.0, 70.0), "Берингов пролив", 0.0,
     "не трогаем намеренно: пролив должен остаться проливом"),
]


def _scale_about_centroid(geom, k):
    from shapely.affinity import scale as aff_scale
    return aff_scale(geom, xfact=k, yfact=k, origin="centroid")


def build_game_base(data, raw_union):
    """Master + коррекции = игровая база. Возвращает (геометрия, журнал правок)."""
    journal = []
    land = data["land"]

    # --- 1. вернуть полезные острова ниже порога --------------------------
    raw_parts = parts_of(raw_union)
    restored = []
    for iid, name, lon, lat, why in RESTORE_ISLANDS:
        pt = Point(lon, lat)
        cand = None
        for p in raw_parts:
            if p.intersects(pt):
                cand = p
                break
        if cand is None:                      # точка в воде — берём ближайший кусок
            cand = min(raw_parts, key=lambda p: p.distance(pt))
            if cand.distance(pt) > 1.5:
                journal.append(("restore", name, None, "не найден в источнике"))
                continue
        g = clean(cand.simplify(SIMPLIFY_TOL_DEG, preserve_topology=True))
        if g.is_empty or land.intersects(g.representative_point()):
            journal.append(("restore", name, None, "уже есть в master"))
            continue
        restored.append((iid, name, g, why))
        journal.append(("restore", name, round(area_km2(g)), why))
    land = clean(unary_union([land] + [g for _, _, g, _ in restored]))

    # --- 2. раздуть всё, что меньше читаемого минимума ---------------------
    parts = parts_of(land)
    grown, out = [], []
    for p in parts:
        a = area_km2(p)
        if a >= MIN_VISIBLE_KM2:
            out.append(p)
            continue
        k_max = math.sqrt(MIN_VISIBLE_KM2 / a)
        others = [q for q in parts if q is not p]
        k = k_max
        while k > 1.001:
            cand = _scale_about_centroid(p, k)
            if not any(cand.intersects(q) for q in others):
                break
            k *= 0.9
        cand = clean(_scale_about_centroid(p, k)) if k > 1.001 else p
        if k > 1.001:
            grown.append((area_km2(p), area_km2(cand), k))
        out.append(cand)
    land = clean(unary_union(out))
    if grown:
        journal.append(("min_visible", f"{len(grown)} островов", round(sum(b - a for a, b, _ in grown)),
                        f"раздуты до {MIN_VISIBLE_KM2:,.0f} км²; максимальный коэффициент "
                        f"по линейному размеру {max(k for _, _, k in grown):.2f}"))

    # --- 3. расширить критические перешейки -------------------------------
    for wid, bbox, name, target_km, why in WIDEN:
        if target_km <= 0:
            journal.append(("widen", name, 0, why))
            continue
        cur = _neck_width_km(land, bbox)
        if cur is None or cur >= target_km:
            journal.append(("widen", name, 0,
                            f"уже {cur:.0f} км при цели {target_km:.0f} — не трогаем"))
            continue
        r = (target_km - cur) / 2.0
        win = box(*bbox)
        wide = box(bbox[0] - 3, bbox[1] - 3, bbox[2] + 3, bbox[3] + 3)
        lon0 = (bbox[0] + bbox[2]) / 2
        lat0 = (bbox[1] + bbox[3]) / 2
        fwd, inv = laea(lon0, lat0), laea_inverse(lon0, lat0)
        piece = clean(land.intersection(wide))
        dil = shp_transform(fwd, piece).buffer(r, quad_segs=8)
        dil = clean(shp_transform(inv, dil)).intersection(win)
        before = area_km2(land)
        land = clean(unary_union([land, clean(dil)]))
        now = _neck_width_km(land, bbox)
        journal.append(("widen", name, round(area_km2(land) - before),
                        f"{cur:.0f} → {now:.0f} км при цели {target_km:.0f}. {why}"))

    land = drop_slivers(land, 1.0)

    # --- 4. пересобрать материки и океан по тем же доменам ----------------
    domains = continent_domains()
    world_poly = box(*WORLD)
    dom_final, used = OrderedDict(), Polygon()
    for cid, d in domains.items():
        d2 = clean(d.intersection(world_poly).difference(used))
        dom_final[cid] = d2
        used = clean(unary_union([used, d2]))

    buckets = {cid: [] for cid in dom_final}
    for p in parts_of(land):
        if area_km2(p) >= SPLIT_MIN_KM2:
            for cid, d in dom_final.items():
                piece = drop_slivers(clean(p.intersection(d)), 1.0)
                if not piece.is_empty:
                    buckets[cid].append(piece)
        else:
            rp = p.representative_point()
            for cid, d in dom_final.items():
                if d.intersects(rp):
                    buckets[cid].append(p)
                    break
    continents = OrderedDict()
    for cid in CONTINENT_ORDER:
        g = clean(unary_union(buckets[cid])) if buckets[cid] else Polygon()
        continents[cid] = drop_slivers(g, 1.0)

    land_all = clean(unary_union(list(continents.values())))
    ocean = drop_slivers(clean(world_poly.difference(land_all)), 1.0)

    return {"land": land_all, "continents": continents, "ocean": ocean,
            "basins": {}, "islands": OrderedDict(), "inland": OrderedDict(),
            "src_sha": data["src_sha"]}, journal


def laea_inverse(lon0: float, lat0: float):
    l0, p0 = math.radians(lon0), math.radians(lat0)
    sp0, cp0 = math.sin(p0), math.cos(p0)

    def inv(x, y, z=None):
        x, y = x / R_EARTH, y / R_EARTH
        rho = math.hypot(x, y)
        if rho < 1e-15:
            return (lon0, lat0)
        c = 2.0 * math.asin(min(1.0, rho / 2.0))
        sc, cc = math.sin(c), math.cos(c)
        lat = math.asin(cc * sp0 + y * sc * cp0 / rho)
        lon = l0 + math.atan2(x * sc, rho * cp0 * cc - y * sp0 * sc)
        return (math.degrees(lon), math.degrees(lat))

    return inv


def _neck_width_km(land, bbox):
    """Ширина самого узкого места суши в окне: эрозия до распада."""
    lon0 = (bbox[0] + bbox[2]) / 2
    lat0 = (bbox[1] + bbox[3]) / 2
    piece = clean(land.intersection(box(*bbox)))
    if piece.is_empty:
        return None
    g = shp_transform(laea(lon0, lat0), piece)
    if not g.is_valid:
        g = make_valid(g)
    n0 = len(parts_of(g))
    lo, hi = 0.0, 600.0
    while hi - lo > 0.5:
        mid = (lo + hi) / 2
        e = g.buffer(-mid)
        if e.is_empty or len(parts_of(e)) > n0:
            hi = mid
        else:
            lo = mid
    return lo * 2


# ---------------------------------------------------------------------------
# 9. Запись GeoJSON
# ---------------------------------------------------------------------------

def _round_geom(geom, nd):
    def r(x, y, z=None):
        return (round(x, nd), round(y, nd))
    g = shp_transform(r, geom)
    if not g.is_valid:
        g = clean(g)
    return g


def feature(fid, ftype, role, geom, extra=None, nd=COORD_ND, fwd=None):
    g = project(geom, fwd) if fwd else geom
    g = _round_geom(g, nd)
    cen = geom.centroid
    pos = geom.representative_point()
    props = OrderedDict([
        ("id", fid),
        ("type", ftype),
        ("role", role),
        ("name_ru", NAMES_RU.get(fid, fid)),
        ("area_km2", round(area_km2(geom), 1)),
        ("parts", len(parts_of(geom))),
        ("vertices", nvertices(geom)),
        ("centroid_wgs84", [round(cen.x, 4), round(cen.y, 4)]),
        ("point_on_surface_wgs84", [round(pos.x, 4), round(pos.y, 4)]),
        ("bbox_wgs84", [round(v, 4) for v in geom.bounds]),
    ])
    if extra:
        props.update(extra)
    return OrderedDict([
        ("type", "Feature"),
        ("id", fid),
        ("bbox", [round(v, nd) for v in g.bounds]),
        ("properties", props),
        ("geometry", mapping(g)),
    ])


def metadata(data, seam=None):
    return OrderedDict([
        ("name", "oil-wars-world-base"),
        ("version", VERSION),
        ("generated", datetime.date.today().isoformat()),
        ("generator", "tools/worldgeom.py"),
        ("purpose", "master geometry: география мира под алгоритмическое разбиение "
                    "на игровые регионы; игровых регионов здесь нет"),
        ("source", OrderedDict([
            ("dataset", "Natural Earth 1:50m Physical — Land"),
            ("file", "src/ne_50m_land.json"),
            ("sha256", data["src_sha"]),
            ("license", "public domain"),
        ])),
        ("coordinateSystem", OrderedDict([
            ("type", "geographic"),
            ("crs", "urn:ogc:def:crs:OGC:1.3:CRS84"),
            ("epsg", 4326),
            ("units", "degrees"),
            ("origin", "пересечение нулевого меридиана и экватора"),
            ("axisOrder", "[lon, lat]"),
            ("axisDirection", "X на восток, Y на север"),
        ])),
        ("worldBounds", OrderedDict([
            ("lonMin", -180.0), ("lonMax", 180.0),
            ("latMin", -90.0), ("latMax", 90.0),
        ])),
        ("transforms", OrderedDict([
            ("normalized", OrderedDict([
                ("id", "equirect_norm"),
                ("formula", "x = (lon + 180) / 360 ; y = (90 - lat) / 360"),
                ("inverse", "lon = x * 360 - 180 ; lat = 90 - y * 360"),
                ("bounds", {"xMin": 0.0, "xMax": 1.0, "yMin": 0.0, "yMax": 0.5}),
                ("axisDirection", "X вправо, Y вниз"),
                ("isotropic", True),
                ("file", "world-base-normalized.geojson"),
            ])),
            ("svg", OrderedDict([
                ("id", "svg_units"),
                ("formula", "x_svg = x_norm * 2000 ; y_svg = y_norm * 2000"),
                ("viewBox", "0 0 2000 1000"),
                ("note", "равномерный масштаб, относительная геометрия не меняется"),
            ])),
            ("polar", OrderedDict([
                ("id", "south_polar_azimuthal"),
                ("variants", ["equidistant", "equal_area"]),
                ("equidistant", "r = (lat + 90) / 180 ; x = r·sin(lon - lon0) ; "
                                "y = -r·cos(lon - lon0)"),
                ("equal_area", "r = 2·sin((lat + 90)/2) / 2 ; x = r·sin(lon - lon0) ; "
                               "y = -r·cos(lon - lon0)"),
                ("center", "Южный полюс (r = 0); Северный полюс — окружность r = 1"),
                ("note", "перед проекцией рёбра догущаются: прямая в градусах — "
                         "не прямая в полярной плоскости"),
                ("file", "world-base-polar.svg"),
            ])),
        ])),
        ("seam", OrderedDict([
            ("applicable", False),
            ("note", "Шва нет и не планируется: поле «Нефтяных войн» — четыре "
                     "отдельных цельных полотна (SPEC-BOARD, решение № 1), край "
                     "листа в южно-полярной проекции материк не режет вовсе "
                     "(решение № 12). Вертикальный разрез из постановки этапа снят "
                     "решением Alek 2026-09-17. Не заводить заново."),
        ])),
        ("layers", OrderedDict([
            ("LAND", "7 материков, role=partition; их объединение точно равно суше"),
            ("OCEAN", "1 объект, role=partition; точное дополнение суши до границ мира"),
            ("OCEAN_BASIN", "6 бассейнов, role=reference; разбиение OCEAN по "
                            "конвенциональным линиям, не игровые регионы"),
            ("ISLAND", "именованные острова, role=reference; геометрия дублирует "
                       "часть материка, в проверках покрытия не участвует"),
            ("INLAND_WATER", "замкнутые водоёмы, role=reference; входят в маску "
                             "OCEAN, но океаном не являются — исключать явно"),
        ])),
        ("downstream", OrderedDict([
            ("graph", "registry/map/derived/all.json и MC-*.json — игровой граф"),
            ("contract", "WORLD GEOMETRY (этот файл) + GAME GRAPH → REGIONAL PARTITION"),
        ])),
    ])


def build_featurecollection(data, seam=None, fwd=None, nd=COORD_ND):
    feats = []
    for cid in CONTINENT_ORDER:
        feats.append(feature(cid, "LAND", "partition", data["continents"][cid], fwd=fwd, nd=nd))
    feats.append(feature("ocean", "OCEAN", "partition", data["ocean"], fwd=fwd, nd=nd))
    for bid in BASIN_ORDER:
        if bid not in data["basins"]:
            continue
        feats.append(feature(bid, "OCEAN_BASIN", "reference", data["basins"][bid],
                             fwd=fwd, nd=nd))
    for iid, (name, geom) in data["islands"].items():
        feats.append(feature(iid, "ISLAND", "reference", geom,
                             extra={"name_ru": name}, fwd=fwd, nd=nd))
    for wid, (name, geom) in data["inland"].items():
        feats.append(feature(wid, "INLAND_WATER", "reference", geom,
                             extra={"name_ru": name}, fwd=fwd, nd=nd))
    return OrderedDict([
        ("type", "FeatureCollection"),
        ("metadata", metadata(data, seam)),
        ("features", feats),
    ])


def write_json(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, separators=(",", ":"))
    return os.path.getsize(path)


# ---------------------------------------------------------------------------
# 10. SVG
# ---------------------------------------------------------------------------

SVG_SCALE = 2000.0

CSS = """
  .ocean { fill: #0e1f26; }
  .land  { fill: #cfd6d3; stroke: #5d6c67; stroke-width: 0.8; stroke-linejoin: round; }
  .grat  { fill: none; stroke: #ffffff; stroke-opacity: .14; stroke-width: 0.8; }
  .eq    { fill: none; stroke: #ffffff; stroke-opacity: .38; stroke-width: 1.4; }
  .bbox  { fill: none; stroke: #ffb020; stroke-width: 1.2; stroke-dasharray: 6 5; }
  .cen   { fill: #ff5a36; }
  .lbl   { font: 600 13px "DejaVu Sans", sans-serif; fill: #ffd6a0; }
  .tick  { font: 400 11px "DejaVu Sans", sans-serif; fill: #9fb0ad; }
"""


def path_d(geom, fwd, nd=2):
    out = []
    for p in parts_of(geom):
        for ring in [p.exterior] + list(p.interiors):
            cs = [fwd(x, y) for x, y in ring.coords]
            if len(cs) < 3:
                continue
            out.append("M" + " L".join(f"{x:.{nd}f},{y:.{nd}f}" for x, y in cs) + "Z")
    return "".join(out)


def svg_norm_fwd(x, y, z=None):
    nx, ny = norm_fwd(x, y)
    return (nx * SVG_SCALE, ny * SVG_SCALE)


def write_svg(path, data, seam=None, debug=False):
    W, H = SVG_SCALE, SVG_SCALE * 0.5
    L = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:.0f} {H:.0f}" '
         f'width="{W:.0f}" height="{H:.0f}">',
         f'<title>Oil Wars — эталонная география, {"debug" if debug else "preview"}</title>',
         f'<style>{CSS}</style>',
         f'<g id="ocean"><rect x="0" y="0" width="{W:.0f}" height="{H:.0f}" class="ocean"/></g>',
         '<g id="continents">']
    for cid, g in data["continents"].items():
        L.append(f'<path id="{cid}" class="land" d="{path_d(g, svg_norm_fwd)}"/>')
    L.append('</g>')

    L.append('<g id="reference">')
    for lon in range(-180, 181, 30):
        a, b = svg_norm_fwd(lon, -90), svg_norm_fwd(lon, 90)
        L.append(f'<line class="grat" x1="{a[0]:.1f}" y1="{a[1]:.1f}" '
                 f'x2="{b[0]:.1f}" y2="{b[1]:.1f}"/>')
    for lat in range(-60, 90, 30):
        a, b = svg_norm_fwd(-180, lat), svg_norm_fwd(180, lat)
        L.append(f'<line class="{"eq" if lat == 0 else "grat"}" x1="{a[0]:.1f}" '
                 f'y1="{a[1]:.1f}" x2="{b[0]:.1f}" y2="{b[1]:.1f}"/>')
    L.append('</g>')

    if debug:
        L.append('<g id="debug">')
        for cid, g in data["continents"].items():
            x0, y0, x1, y1 = g.bounds
            a, b = svg_norm_fwd(x0, y1), svg_norm_fwd(x1, y0)
            L.append(f'<rect class="bbox" x="{a[0]:.1f}" y="{a[1]:.1f}" '
                     f'width="{b[0] - a[0]:.1f}" height="{b[1] - a[1]:.1f}"/>')
            pos = g.representative_point()
            p = svg_norm_fwd(pos.x, pos.y)
            L.append(f'<circle class="cen" cx="{p[0]:.1f}" cy="{p[1]:.1f}" r="4"/>')
            cc = g.centroid
            p2 = svg_norm_fwd(cc.x, cc.y)
            L.append(f'<circle cx="{p2[0]:.1f}" cy="{p2[1]:.1f}" r="7" fill="none" '
                     f'stroke="#ff5a36" stroke-width="2"/>')
            L.append(f'<text class="lbl" x="{a[0] + 5:.1f}" y="{a[1] + 17:.1f}">{cid} · '
                     f'{area_km2(g) / 1e6:.2f} млн км² · {len(parts_of(g))} кусков</text>')
        L.append(f'<rect class="bbox" x="0" y="0" width="{W:.0f}" height="{H:.0f}" '
                 f'stroke="#ffffff" stroke-opacity=".55"/>')
        for lon in range(-180, 181, 30):
            p = svg_norm_fwd(lon, -87)
            L.append(f'<text class="tick" x="{p[0] + 4:.1f}" y="{p[1]:.1f}">{lon}°</text>')
        for lat in range(-60, 90, 30):
            p = svg_norm_fwd(-179, lat)
            L.append(f'<text class="tick" x="{p[0] + 4:.1f}" y="{p[1] - 4:.1f}">{lat}°</text>')
        L.append('</g>')

    L.append('</svg>')
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(L))
    return os.path.getsize(path)


def densify(geom, max_deg=1.0):
    """Догустить рёбра: прямая в градусах — не прямая в полярной плоскости."""
    def dens(coords):
        out = []
        for i in range(len(coords) - 1):
            x0, y0 = coords[i][0], coords[i][1]
            x1, y1 = coords[i + 1][0], coords[i + 1][1]
            out.append((x0, y0))
            n = int(max(abs(x1 - x0), abs(y1 - y0)) / max_deg)
            for k in range(1, n):
                t = k / n
                out.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * t))
        out.append((coords[-1][0], coords[-1][1]))
        return out

    ps = []
    for p in parts_of(geom):
        ps.append(Polygon(dens(list(p.exterior.coords)),
                          [dens(list(r.coords)) for r in p.interiors]))
    if not ps:
        return geom
    return MultiPolygon(ps) if len(ps) > 1 else ps[0]


def write_polar_svg(path, data, kind="equidistant"):
    S = 1000.0
    base = polar_fwd_factory(kind, lon0=0.0, scale=S)

    def fwd(x, y, z=None):
        px, py = base(x, y)
        return (px + S, py + S)

    L = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {2 * S:.0f} {2 * S:.0f}" '
         f'width="{2 * S:.0f}" height="{2 * S:.0f}">',
         f'<title>Oil Wars — эталонная география, южно-полярная азимутальная ({kind})</title>',
         f'<style>{CSS}</style>',
         f'<g id="ocean"><circle cx="{S:.0f}" cy="{S:.0f}" r="{S:.0f}" class="ocean"/></g>',
         '<g id="continents">']
    for cid, g in data["continents"].items():
        L.append(f'<path id="{cid}" class="land" d="{path_d(densify(g, 0.5), fwd)}"/>')
    L.append('</g>')
    L.append('<g id="reference">')
    for lon in range(-180, 180, 30):
        a, b = fwd(lon, -90), fwd(lon, 90)
        L.append(f'<line class="grat" x1="{a[0]:.1f}" y1="{a[1]:.1f}" '
                 f'x2="{b[0]:.1f}" y2="{b[1]:.1f}"/>')
    for lat in [-60, -30, 0, 30, 60]:
        pts = [fwd(-180 + i * 2.0, lat) for i in range(181)]
        L.append(f'<polyline class="{"eq" if lat == 0 else "grat"}" points="'
                 + " ".join(f"{x:.1f},{y:.1f}" for x, y in pts) + '"/>')
    L.append('</g>')
    L.append('</svg>')
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(L))
    return os.path.getsize(path)


# ---------------------------------------------------------------------------
# 11. Проверки
# ---------------------------------------------------------------------------

def run_checks(data):
    checks = []

    def ok(name, passed, detail=""):
        checks.append((name, bool(passed), detail))

    land, ocean = data["land"], data["ocean"]
    world_poly = box(*WORLD)
    partition = list(data["continents"].items()) + [("ocean", ocean)]
    all_feats = partition + list(data["basins"].items())

    bad = [k for k, g in all_feats if not g.is_valid]
    ok("все полигоны валидны (OGC)", not bad,
       f"невалидны: {bad}" if bad else f"проверено {len(all_feats)} объектов")

    selfint = [k for k, g in all_feats
               if any(not LineString(p.exterior.coords).is_simple for p in parts_of(g))]
    ok("нет самопересечений внешних колец", not selfint, str(selfint) if selfint else "—")

    zero = [k for k, g in all_feats if area_km2(g) <= 0]
    ok("нет нулевых площадей", not zero, str(zero) if zero else "—")

    unclosed = sorted({k for k, g in all_feats for p in parts_of(g)
                       for r in [p.exterior] + list(p.interiors)
                       if r.coords[0] != r.coords[-1]})
    ok("все контуры замкнуты", not unclosed, str(unclosed) if unclosed else "—")

    dups = sum(1 for k, g in all_feats for p in parts_of(g)
               for r in [p.exterior] + list(p.interiors)
               for i in range(len(r.coords) - 1) if r.coords[i] == r.coords[i + 1])
    ok("нет повторов вершин подряд", dups == 0, f"найдено {dups}")

    tiny = [(k, round(area_km2(p), 3)) for k, g in all_feats for p in parts_of(g)
            if area_km2(p) < 1.0]
    ok("нет кусков меньше 1 км²", not tiny, str(tiny[:5]) if tiny else "—")

    ccw = [k for k, g in all_feats for p in parts_of(g)
           if not p.exterior.is_ccw or any(r.is_ccw for r in p.interiors)]
    ok("ориентация колец приведена (внешние CCW, дыры CW)", not ccw,
       str(sorted(set(ccw))) if ccw else "—")

    cids = list(data["continents"])
    overl = []
    for i in range(len(cids)):
        for j in range(i + 1, len(cids)):
            a = area_km2(data["continents"][cids[i]].intersection(data["continents"][cids[j]]))
            if a > 1.0:
                overl.append((cids[i], cids[j], round(a, 2)))
    ok("материки попарно не перекрываются", not overl,
       str(overl) if overl else f"проверено {len(cids) * (len(cids) - 1) // 2} пар")

    ia = area_km2(land.intersection(ocean))
    ok("LAND ∩ OCEAN = ∅", ia < 1.0, f"пересечение {ia:.6f} км²")

    uni = unary_union([land, ocean])
    gap = area_km2(clean(world_poly.difference(uni)))
    ext = area_km2(clean(uni.difference(world_poly)))
    ok("WORLD = LAND ∪ OCEAN", gap < 1.0 and ext < 1.0,
       f"щели {gap:.6f} км², выход за границы {ext:.6f} км²")

    csum = sum(area_km2(g) for g in data["continents"].values())
    ok("Σ материков = площадь LAND", abs(csum - area_km2(land)) < 1.0,
       f"{csum:,.1f} против {area_km2(land):,.1f} км²")

    bsum = sum(area_km2(g) for g in data["basins"].values())
    ok("Σ бассейнов = площадь OCEAN", abs(bsum - area_km2(ocean)) < 10.0,
       f"{bsum:,.1f} против {area_km2(ocean):,.1f} км²")

    bids = list(data["basins"])
    bover = []
    for i in range(len(bids)):
        for j in range(i + 1, len(bids)):
            a = area_km2(data["basins"][bids[i]].intersection(data["basins"][bids[j]]))
            if a > 1.0:
                bover.append((bids[i], bids[j], round(a, 2)))
    ok("бассейны попарно не перекрываются", not bover,
       str(bover) if bover else f"проверено {len(bids) * (len(bids) - 1) // 2} пар")

    outside = [k for k, g in all_feats if not world_poly.buffer(1e-6).contains(g)]
    ok("все объекты внутри границ мира", not outside, str(outside) if outside else "—")

    fails = []
    for (lon, lat), expect, what in CONTINENT_SPOT_CHECKS:
        pt = Point(lon, lat)
        got = next((cid for cid, g in data["continents"].items() if g.intersects(pt)), None)
        if got != expect:
            fails.append(f"{what}: ждали {expect}, получили {got}")
    ok(f"контрольные точки материков ({len(CONTINENT_SPOT_CHECKS)})", not fails,
       "; ".join(fails) or "все совпали")

    bfails = []
    for (lon, lat), expect, what in BASIN_SPOT_CHECKS:
        pt = Point(lon, lat)
        got = next((bid for bid, g in data["basins"].items() if g.intersects(pt)), None)
        if got != expect:
            bfails.append(f"{what}: ждали {expect}, получили {got}")
    ok(f"контрольные точки бассейнов ({len(BASIN_SPOT_CHECKS)})", not bfails,
       "; ".join(bfails) or "все совпали")

    americas = clean(unary_union([data["continents"]["north_america"],
                                  data["continents"]["south_america"]]))
    big = max(parts_of(americas), key=area_km2)
    pan = big.intersects(Point(-60.0, -10.0)) and big.intersects(Point(-100.0, 40.0))
    ok("Панамский перешеек не порван упрощением", pan,
       "Северная и Южная Америка в одном связном куске")

    afeur = clean(unary_union([data["continents"]["africa"], data["continents"]["asia"],
                               data["continents"]["europe"]]))
    big2 = max(parts_of(afeur), key=area_km2)
    suez = big2.intersects(Point(20.0, 10.0)) and big2.intersects(Point(100.0, 50.0))
    ok("Суэцкий перешеек не порван упрощением", suez,
       "Африка и Евразия в одном связном куске")

    g1, g2 = data["continents"]["africa"], data["continents"]["south_america"]
    r_deg = g1.area / g2.area
    r_norm = project(g1, norm_fwd).area / project(g2, norm_fwd).area
    ok("нормализация не меняет относительные площади", abs(r_deg - r_norm) < 1e-9,
       f"Δ = {abs(r_deg - r_norm):.2e}")

    dx = abs(norm_fwd(1, 0)[0] - norm_fwd(0, 0)[0])
    dy = abs(norm_fwd(0, 1)[1] - norm_fwd(0, 0)[1])
    ok("нормализация изотропна: 1° по X = 1° по Y", abs(dx - dy) < 1e-12,
       f"{dx:.9f} против {dy:.9f}")

    xs, ys = [], []
    for _, g in all_feats:
        b = project(g, norm_fwd).bounds
        xs += [b[0], b[2]]
        ys += [b[1], b[3]]
    ok("нормализованные координаты в [0,1] × [0,0.5]",
       min(xs) >= -1e-9 and max(xs) <= 1 + 1e-9 and min(ys) >= -1e-9 and max(ys) <= 0.5 + 1e-9,
       f"x ∈ [{min(xs):.6f}, {max(xs):.6f}], y ∈ [{min(ys):.6f}, {max(ys):.6f}]")

    rt = max(abs(norm_inv(*norm_fwd(lon, lat))[0] - lon) + abs(norm_inv(*norm_fwd(lon, lat))[1] - lat)
             for lon in range(-180, 181, 15) for lat in range(-90, 91, 15))
    ok("нормализация обратима без потерь", rt < 1e-9, f"максимальная невязка {rt:.2e}°")

    # округление координат в файле не должно ломать валидность
    rounded_bad = [k for k, g in all_feats if not _round_geom(g, COORD_ND).is_valid]
    ok(f"геометрия валидна после округления до {COORD_ND} знаков", not rounded_bad,
       str(rounded_bad) if rounded_bad else "—")

    # мастер и нормализованный файл должны иметь одинаковый набор вершин
    mism = []
    for k, g in all_feats:
        a = _round_geom(g, COORD_ND)
        b = _round_geom(project(g, norm_fwd), COORD_ND_NORM)
        if nvertices(a) != nvertices(b) or len(parts_of(a)) != len(parts_of(b)):
            mism.append(k)
    ok("нормализованный слой вершина-в-вершину совпадает с master", not mism,
       str(mism) if mism else f"проверено {len(all_feats)} объектов")

    # именованные острова: каждый должен лежать внутри ровно одного материка
    ifails = []
    for iid, (name, geom) in data["islands"].items():
        hosts = [cid for cid, g in data["continents"].items()
                 if area_km2(g.intersection(geom)) > area_km2(geom) * 0.5]
        if len(hosts) != 1:
            ifails.append(f"{name}: материков {len(hosts)}")
    ok(f"именованные острова принадлежат ровно одному материку ({len(data['islands'])})",
       not ifails, "; ".join(ifails) or "все совпали")

    n_extra = len(parts_of(ocean)) - 1
    ok("все замкнутые водоёмы внутри маски OCEAN опознаны",
       n_extra == len(data["inland"]),
       f"кусков океана {n_extra + 1}, опознано водоёмов {len(data['inland'])}")

    return checks


# ---------------------------------------------------------------------------
# 12. Отчёт
# ---------------------------------------------------------------------------

def write_report(path, data, checks, narrow, gaps, game, game_journal):
    L = []
    A = L.append
    land, ocean = data["land"], data["ocean"]
    land_a, ocean_a = area_km2(land), area_km2(ocean)
    total = land_a + ocean_a

    A("# world-base-report — эталонная география мира")
    A("")
    A(f"Сгенерировано `tools/worldgeom.py`, руками не правится. "
      f"Версия {VERSION}, {datetime.date.today().isoformat()}.")
    A("")
    A("Это master geometry проекта: чистая география, поверх которой на следующем "
      "этапе строятся игровые регионы. Игровых регионов здесь нет.")
    A("")
    A("## Приоритеты")
    A("")
    A("Решение Alek 2026-09-17 (`MF-016`), оно важнее всего остального в этом файле:")
    A("")
    A("> Это в первую очередь **игровая** карта. Главное — решить функциональные "
      "игровые задачи и сохранить узнаваемость очертаний и взаимного расположения. "
      "Точность пропорций, полнота деталей и географическая достоверность идут "
      "следом и соблюдаются ровно настолько, насколько не мешают игре. "
      "Остров, перешеек или пролив можно сделать крупнее реального — или "
      "безжалостно убрать, если он мешает механике или плохо смотрится.")
    A("")
    A("Отсюда два слоя вместо одного:")
    A("")
    A("| Файл | Что это | Зачем |")
    A("|---|---|---|")
    A("| `world-base.geojson` | честная география, ничего не подправлено | "
      "опора и точка отсчёта: по ней видно, где и насколько мы отошли |")
    A("| `world-game.geojson` | та же география с игровыми коррекциями | "
      "рабочая основа для разбиения на регионы |")
    A("")
    A("Master не правится «под игру» — иначе через месяц не отличить, где была "
      "география, а где решение. Все правки лежат списком в генераторе, каждая "
      "с причиной, и применяются к master детерминированно.")
    A("")

    A("## Источник географии")
    A("")
    A("| Параметр | Значение |")
    A("|---|---|")
    A("| Набор | Natural Earth 1:50m Physical — Land |")
    A("| Лицензия | public domain |")
    A("| Файл | `registry/map/geo/src/ne_50m_land.json` (вендорная копия в репозитории) |")
    A(f"| SHA-256 | `{data['src_sha']}` |")
    A("| Доставка | git-клон `github.com/martynafford/natural-earth-geojson`, "
      "коммит `0b9a6ce` |")
    A(f"| Исходно | {data['src_features']} записей, {data['raw_parts']} связных кусков, "
      f"{data['raw_vertices']:,} вершин, {data['raw_area']:,.0f} км² |")
    A("")
    A("Растр не участвует нигде: ни как источник, ни как промежуточный шаг. "
      "Трассировки нет, вся геометрия векторная от начала до конца.")
    A("")
    A("Прямая загрузка с `naciscdn.org` и `raw.githubusercontent.com` в рабочей среде "
      "закрыта прокси, поэтому файл взят git-клоном с `github.com` и положен "
      "в репозиторий — сборка воспроизводится офлайн.")
    A("")

    A("## Преобразования")
    A("")
    for k, v in data["log"]:
        A(f"- **{k}** — {v}")
    A("")
    A("Порядок операций: загрузка → `make_valid` и округление на сетку "
      f"{GRID_PRECISION} → отбор кусков ≥ {MIN_ISLAND_KM2:,.0f} км² → упрощение "
      f"Дугласа — Пекера с допуском {SIMPLIFY_TOL_DEG}° → разрез доменами материков → "
      "OCEAN как дополнение → бассейны.")
    A("")
    A("Проекции на этом этапе нет: master хранится в WGS84. Нормализация "
      "и полярная проекция — производные, формулы в `metadata.transforms`.")
    A("")

    A("## Система координат")
    A("")
    A("| Слой | Система | Границы |")
    A("|---|---|---|")
    A("| master, `world-base.geojson` | WGS84 / CRS84, градусы, [lon, lat] | "
      "lon ∈ [−180, 180], lat ∈ [−90, 90] |")
    A("| производная, `world-base-normalized.geojson` | нормализованная декартова, "
      "X вправо, Y вниз | x ∈ [0, 1], y ∈ [0, 0.5] |")
    A("| SVG | те же нормализованные единицы × 2000 | viewBox `0 0 2000 1000` |")
    A("")
    A("```")
    A("x = (lon + 180) / 360        lon = x * 360 - 180")
    A("y = ( 90 - lat) / 360        lat = 90 - y * 360")
    A("```")
    A("")
    A("Диапазон Y равен 0…0.5, а не 0…1, сознательно: так один градус по долготе "
      "и по широте даёт один и тот же шаг, преобразование изотропно, а масштаб "
      "в SVG остаётся равномерным. Растягивание Y до единицы сплющило бы карту "
      "вдвое и сломало бы все дальнейшие измерения площадей и расстояний.")
    A("")

    A("## Границы материков")
    A("")
    A("Материк = LAND ∩ домен. Домены — разбиение прямоугольника мира; применяются "
      "по порядку, каждый обрезается по незанятому остатку, поэтому перекрытия "
      "невозможны по построению. Два мегакуска (Афроевразия и Америки) режутся "
      "доменами, все остальные куски относятся целиком по внутренней точке — "
      "остров не может быть разрезан пополам.")
    A("")
    A("| Раздел | Линия | Что решает |")
    A("|---|---|---|")
    A("| Антарктида | 60° ю.ш. | совпадает с границей Южного океана IHO 2000; "
      "Южные Шетландские острова уходят к Антарктиде |")
    A("| Африка — Азия | Суэцкий канал → Красное море → Баб-эль-Мандеб | "
      "Синай к Азии, дельта Нила к Африке |")
    A("| Африка — Европа | Гибралтар → между мысом Бланко (37.35°) и югом Сицилии "
      "(36.65°) → южнее Крита и Кипра | Сицилия, Сардиния, Корсика, Крит — Европа; "
      "весь Магриб — Африка |")
    A("| Европа — Азия | Урал → река Урал → Каспий → Кума-Манычская впадина → "
      "Керчь → Босфор → Эгейское море | Новая Земля и Шпицберген — Европа, Ямал — Азия; "
      "Кипр и Родос — Азия |")
    A("| Европа — Северная Америка | Датский пролив: ломаная (−35, 55) … (−5, 74) | "
      "Исландия — Европа, Гренландия — Северная Америка |")
    A("| Северная — Южная Америка | граница Панамы и Колумбии, Дарьенский перешеек | "
      "весь перешеек к Северной Америке; Тринидад — Южная, Барбадос — Северная |")
    A("| Азия — Океания | 141° в.д. (граница Индонезии и Папуа — Новой Гвинеи), "
      "южнее 11° ю.ш. — 110° в.д. | Новая Гвинея делится пополам как в реальности; "
      "Ява и Малые Зондские — Азия |")
    A("| Азия — Северная Америка | 168°57′ з.д., Берингов пролив между островами "
      "Диомида | Чукотка за антимеридианом остаётся Азией |")
    A("")
    A(f"Каждая линия закреплена контрольными точками в коде "
      f"(`CONTINENT_SPOT_CHECKS`, {len(CONTINENT_SPOT_CHECKS)} штук) — они гоняются "
      f"при каждой сборке, так что сдвиг линии не пройдёт молча.")
    A("")

    A("## Географические объекты")
    A("")
    A("| ID | Тип | Площадь, млн км² | Доля суши | Кусков | Вершин | Centroid | Bounding box |")
    A("|---|---|---:|---:|---:|---:|---|---|")
    for cid in CONTINENT_ORDER:
        g = data["continents"][cid]
        a = area_km2(g)
        c = g.centroid
        b = g.bounds
        A(f"| `{cid}` | LAND | {a / 1e6:.3f} | {a / land_a * 100:.1f} % | "
          f"{len(parts_of(g))} | {nvertices(g)} | "
          f"{c.x:.1f}, {c.y:.1f} | {b[0]:.1f}, {b[1]:.1f} … {b[2]:.1f}, {b[3]:.1f} |")
    g = ocean
    c, b = g.centroid, g.bounds
    A(f"| `ocean` | OCEAN | {ocean_a / 1e6:.3f} | — | {len(parts_of(g))} | "
      f"{nvertices(g)} | {c.x:.1f}, {c.y:.1f} | "
      f"{b[0]:.1f}, {b[1]:.1f} … {b[2]:.1f}, {b[3]:.1f} |")
    A("")
    A("Бассейны океана — справочный слой, не игровые регионы:")
    A("")
    A("| ID | Площадь, млн км² | Доля океана | Кусков |")
    A("|---|---:|---:|---:|")
    for bid in BASIN_ORDER:
        g = data["basins"][bid]
        a = area_km2(g)
        A(f"| `{bid}` | {a / 1e6:.3f} | {a / ocean_a * 100:.1f} % | {len(parts_of(g))} |")
    A("")

    A("## Land / Ocean")
    A("")
    A("| | Площадь, млн км² | Доля мира | Справочно, реальность |")
    A("|---|---:|---:|---|")
    A(f"| LAND | {land_a / 1e6:.2f} | {land_a / total * 100:.2f} % | 148.94 / 29.2 % |")
    A(f"| OCEAN | {ocean_a / 1e6:.2f} | {ocean_a / total * 100:.2f} % | 361.13 / 70.8 % |")
    A(f"| WORLD | {total / 1e6:.2f} | 100 % | 510.07 |")
    A("")
    A("Площади считаются точно: геометрия переносится в ламбертову цилиндрическую "
      "равновеликую проекцию, где площадь плоской фигуры равна площади сферической. "
      "Расхождение с реальностью — цена упрощения источника и порога на острова, "
      "разбор ниже.")
    A("")

    A("## Шва нет")
    A("")
    A("Постановка этапа требовала зафиксировать вертикальный разрез мира. "
      "Решением Alek от 2026-09-17 требование снято: на поле «Нефтяных войн» шва "
      "нет и не планировалось — четыре отдельных цельных полотна "
      "(`SPEC-BOARD`, решение № 1), а в южно-полярной проекции край листа материк "
      "не режет вовсе (решение № 12). Меридианы к нашим задачам отношения не имеют.")
    A("")
    A("В `metadata.seam` мастера стоит `applicable: false` с пояснением — "
      "чтобы шов не завели заново на следующем круге.")
    A("")

    # --- масштабный разрыв -----------------------------------------------
    A("## Масштабный разрыв: игра против географии")
    A("")
    A("Самое полезное число этого отчёта. Слева — сколько площади объект занял бы "
      "на полотне при честном равновеликом масштабе, справа — сколько ему "
      "положено по `ТЗ-ЭСКИЗ-КАРТЫ` §5.2 и §5.3.")
    A("")
    A("| Объект | Честный масштаб, см² | Цель ТЗ, см² | Во сколько раз | Из чего цель |")
    A("|---|---:|---:|---:|---|")
    for cid, (target, what) in GAME_TARGETS.items():
        g = data["ocean"] if cid == "ocean" else data["continents"][cid]
        t = true_scale_cm2(area_km2(g))
        A(f"| `{cid}` | {t:.0f} | {target} | ×{target / t:.2f} | {what} |")
    A("")
    for name, target, ids in GAME_TARGETS_SPOT:
        if ids is None:
            continue
        geoms = [data["islands"][i][1] for i in ids if i in data["islands"]]
        if not geoms:
            continue
        t = true_scale_cm2(sum(area_km2(g) for g in geoms))
        A(f"- **{name}**: честный масштаб {t:.1f} см², цель {target} см² — "
          f"**×{target / t:.0f}**")
    A("")
    A("Что из этого следует для следующего этапа:")
    A("")
    A("1. **Игровое поле — это картограмма, а не проекция.** Суша на нём занимает "
      "53 % площади вместо реальных 29 %, океаны ужаты с 71 % до 47 %. Пытаться "
      "получить раскладку обрезкой честной географии бессмысленно: она не сойдётся "
      "ни по одной области.")
    A("2. **Коэффициенты разные на порядок.** Африке нужно ×1.2, Европе ×3.7, "
      "Новой Зеландии — под ×60. Значит растягивать карту целиком нельзя, тянуть "
      "надо каждую область под свою цель.")
    A("3. **География задаёт форму и соседство, а не размер.** Из master берутся "
      "силуэт, взаимное расположение и то, что с чем рядом; площади берутся "
      "из ТЗ §5, топология — из `edges.yaml`.")
    A("")

    A("## Диагностика под будущее разбиение")
    A("")
    A("### Размеры материков")
    A("")
    A("| Материк | Площадь, млн км² | Наибольший вписанный круг, км | "
      "Доля главного куска | Кусков |")
    A("|---|---:|---:|---:|---:|")
    for cid in CONTINENT_ORDER:
        g = data["continents"][cid]
        share, n = mainland_share(g)
        A(f"| `{cid}` | {area_km2(g) / 1e6:.2f} | {max_inscribed_km(g):.0f} | "
          f"{share * 100:.1f} % | {n} |")
    A("")
    A("Вписанный круг — радиус, при котором эрозия материка обнуляет его целиком; "
      "это мера «есть ли куда поставить фигуру внутри материка».")
    A("")
    A("### Узкие места")
    A("")
    A("| Перешеек | Ширина суши, км |")
    A("|---|---:|")
    for name, w in narrow:
        A(f"| {name} | {w if w is not None else '—'} |")
    A("")
    A("| Пролив | Ширина воды, км | Между |")
    A("|---|---:|---|")
    for name, d, a, b, p1, p2 in gaps:
        A(f"| {name} | {d if d is not None else '—'} | {a} — {b} |")
    A("")
    A("### Что остаётся на следующий этап")
    A("")
    A("1. **Антарктида в цилиндрической проекции.** Растянута вдоль всей нижней "
      "кромки, форма нечитаема. В master она сохранена как есть, без подгонки "
      "под прямоугольник: это задача проекции, а не географии. В полярной "
      "раскладке проблема исчезает — Антарктида становится центром.")
    A("2. **Северный Ледовитый океан.** В нормализованных координатах — узкая "
      "полоса поверху, в полярной проекции — внешнее кольцо. Это одна и та же "
      "область в двух формах, обе получаются из master пересчётом.")
    A("3. **Разрозненность Океании.** Самый «дырявый» материк по доле главного "
      "куска: её регионы придётся собирать из архипелагов, а не резать сплошное "
      "тело. Игровая база это частично лечит — мелочь раздута до читаемого "
      "размера, — но собирать всё равно придётся.")
    A("4. **Площади.** Главное, см. «Масштабный разрыв» выше: геометрия даёт "
      "форму и соседство, площади задаются ТЗ §5 и достигаются растяжением "
      "каждой области под свою цель.")
    A("")

    # --- игровая база ------------------------------------------------------
    A("## Игровая база — `world-game.geojson`")
    A("")
    A("То же самое с коррекциями под игру. Master не тронут.")
    A("")
    A("| Правка | Объект | Добавлено, км² | Зачем |")
    A("|---|---|---:|---|")
    for op, what, delta, why in game_journal:
        d = f"{delta:,}" if isinstance(delta, (int, float)) and delta else "—"
        A(f"| `{op}` | {what} | {d} | {why} |")
    A("")
    gl, gb = area_km2(game["land"]), area_km2(data["land"])
    A(f"Итого суша {gb / 1e6:.2f} → {gl / 1e6:.2f} млн км² "
      f"({(gl / gb - 1) * 100:+.2f} %), доля суши {gb / 510.07e6 * 100:.2f} % → "
      f"{gl / 510.07e6 * 100:.2f} %.")
    A("")
    A("| Материк | master, млн км² | игровая база | Δ |")
    A("|---|---:|---:|---:|")
    for cid in CONTINENT_ORDER:
        a = area_km2(data["continents"][cid])
        b = area_km2(game["continents"][cid])
        A(f"| `{cid}` | {a / 1e6:.2f} | {b / 1e6:.2f} | {(b / a - 1) * 100:+.1f} % |")
    A("")
    A("Три правила, по которым это собрано:")
    A("")
    A(f"1. **Минимальный читаемый остров — {MIN_VISIBLE_KM2:,.0f} км².** На полотне "
      f"880 × 530 мм это примерно 3.7 × 3.7 мм. Всё, что меньше, раздувается "
      f"вокруг своего центра до этого размера с сохранением силуэта. Если при "
      f"раздувании остров начинает слипаться с соседом, коэффициент уменьшается, "
      f"пока слипание не пропадёт — остров остаётся островом.")
    A("2. **Возвращены якорные острова ниже порога отбора.** Не ради полноты, "
      "а потому что океанская область без единого клочка суши читается как пустое "
      "поле: Фолкленды держат Юг Атлантики, Азоры — Север Атлантики, Таити — "
      "Юг Тихого, Тринидад подпирает панамский узел.")
    A("3. **Критические перешейки расширены до читаемой ширины.** Панама и Суэц — "
      "те два места, где узел из `ТЗ` §6.3 и контакт из `SPEC-BOARD` §4.1 "
      "не нарисовать по реальной географии. Берингов пролив намеренно не трогаем: "
      "пролив должен остаться проливом.")
    A("")
    A("Любая из этих правок — строка в `tools/worldgeom.py` (`RESTORE_ISLANDS`, "
      "`MIN_VISIBLE_KM2`, `WIDEN`) и пересборка за минуту. Добавить остров, "
      "раздуть перешеек, выпилить мешающий архипелаг — так же.")
    A("")

    A("## Топология")
    A("")
    A("| Проверка | Итог | Детали |")
    A("|---|---|---|")
    for name, passed, detail in checks:
        A(f"| {name} | {'✅' if passed else '❌'} | {detail} |")
    A("")
    passed = sum(1 for _, p, _ in checks if p)
    A(f"**{passed} из {len(checks)} проверок пройдено.** Проверки гоняются командой "
      "`python tools/worldgeom.py check` и являются частью сборки: если хоть одна "
      "падает, файлы не пишутся.")
    A("")

    A("## Известные ограничения")
    A("")
    A("Читать с поправкой на «Приоритеты»: это перечень мест, где мы отошли "
      "от реальной географии, а не список дефектов. Отход допустим и ожидаем — "
      "важно только, чтобы он был записан.")
    A("")
    A(f"1. **Порог на острова: {MIN_ISLAND_KM2:,.0f} км².** Отброшено "
      f"{len(data['dropped'])} кусков общей площадью {data['dropped_area']:,.0f} км² "
      f"— {data['dropped_area'] / data['raw_area'] * 100:.2f} % суши. Крупнейшие "
      f"из отброшенных:")
    A("")
    A("| Площадь, км² | Центр |")
    A("|---:|---|")
    for a, p in sorted(data["dropped"], key=lambda t: -t[0])[:10]:
        c = p.representative_point()
        A(f"| {a:,.0f} | {c.x:.1f}, {c.y:.1f} |")
    A("")
    A(f"2. **Упрощение береговой линии: допуск {SIMPLIFY_TOL_DEG}°** "
      f"(~{SIMPLIFY_TOL_DEG * 111.3:.1f} км на экваторе). На полотне 900 мм это "
      f"около {SIMPLIFY_TOL_DEG / 360 * 900:.2f} мм — меньше толщины линии контура. "
      f"Мелкие изгибы побережья потеряны намеренно; форма материка, крупные "
      f"полуострова и заливы сохранены.")
    A("3. **Источник 1:50m.** Для полотна такого размера это верхняя разумная "
      "граница: 1:110m теряет средиземноморские острова и вырождает Панамский "
      "перешеек, 1:10m даёт на порядок больше вершин без выигрыша на печати.")
    A("4. **Антарктида взята с шельфовыми ледниками** — так устроен слой Land "
      "в Natural Earth. Площадь получается больше материковой; для игрового поля "
      "это скорее плюс (Антарктида — полноценная область), но число в таблице "
      "не равно «площади суши Антарктиды» в справочнике.")
    A("5. **Бассейны океана — конвенциональные и упрощённые.** Границы Индийского "
      "океана в индонезийских проливах и южная граница Северного Ледовитого "
      "(взята по Полярному кругу) огрублены. Слой справочный: игровые океанские "
      "области берутся из `regions.yaml`, а не отсюда.")
    A("6. **Южный океан как отдельный бассейн не заводится** — намеренно: в "
      "оригинале и у нас шесть океанских областей, воды вокруг Антарктиды "
      "распределены между Югом Атлантики, Югом Пацифики и Индийским.")
    A("7. **Рёбра — прямые в градусах, а не дуги большого круга.** Для проекций "
      "это важно: перед полярной проекцией геометрия догущается (`densify`), "
      "иначе длинные рёбра спрямляются и дают видимые изломы.")
    A("8. **Что стоит заменить перед финальной печатью**, если понадобится "
      "фотографическая точность берега: тот же Natural Earth 1:10m или GSHHG "
      "уровня `i`/`h`. Схема данных и весь конвейер при этом не меняются — "
      "меняется только файл в `src/` и допуск упрощения.")
    A("")

    A("## Что дальше")
    A("")
    A("Следующий этап получает на вход два файла и ничего больше:")
    A("")
    A("```")
    A("registry/map/geo/world-game.geojson      география с игровыми коррекциями")
    A("registry/map/derived/all.json            игровой граф (MF-001)")
    A("registry/map/ТЗ-ЭСКИЗ-КАРТЫ.md §5        целевые площади областей")
    A("        ↓")
    A("REGIONAL PARTITION")
    A("```")
    A("")
    A("Разбиение работает с `world-game.geojson`; `world-base.geojson` остаётся "
      "точкой отсчёта, по которой видно, где и насколько мы отошли от географии.")
    A("")
    A("Ручной правки геометрии не требуется: разбиение работает через стандартные "
      "операции (площадь, центроид, буфер, пересечение, разрезание, объединение, "
      "смежность, расстояние, связность) — все они на этой геометрии определены "
      "и проверены. Нужна другая коррекция — это строка в генераторе, а не "
      "правка файла руками.")
    A("")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    return os.path.getsize(path)


# ---------------------------------------------------------------------------
# 13. main
# ---------------------------------------------------------------------------

def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"

    data = build()
    for k, v in data["log"]:
        print(f"[{k}] {v}")

    checks = run_checks(data)
    bad = [c for c in checks if not c[1]]
    print()
    for n, p, d in checks:
        print(("  OK   " if p else " FAIL  ") + n + (f" — {d}" if d else ""))
    print(f"\n{len(checks) - len(bad)}/{len(checks)} проверок пройдено")

    if cmd == "check":
        return 0 if not bad else 1
    if bad:
        print("\nЕсть падающие проверки — файлы не пишутся.")
        return 1

    os.makedirs(GEO, exist_ok=True)

    print()
    fc = build_featurecollection(data)
    print("world-base.geojson            %8.1f КБ" %
          (write_json(os.path.join(GEO, "world-base.geojson"), fc) / 1024))

    fc_n = build_featurecollection(data, fwd=norm_fwd, nd=COORD_ND_NORM)
    fc_n["metadata"]["coordinateSystem"] = OrderedDict([
        ("type", "normalized_cartesian"),
        ("derivedFrom", "world-base.geojson"),
        ("transform", "equirect_norm"),
        ("formula", "x = (lon + 180) / 360 ; y = (90 - lat) / 360"),
        ("xMin", 0.0), ("xMax", 1.0), ("yMin", 0.0), ("yMax", 0.5),
        ("axisDirection", "X вправо, Y вниз"),
    ])
    fc_n["metadata"]["worldBounds"] = {"xMin": 0.0, "xMax": 1.0, "yMin": 0.0, "yMax": 0.5}
    print("world-base-normalized.geojson %8.1f КБ" %
          (write_json(os.path.join(GEO, "world-base-normalized.geojson"), fc_n) / 1024))

    print("world-base.svg                %8.1f КБ" %
          (write_svg(os.path.join(GEO, "world-base.svg"), data) / 1024))
    print("world-base-debug.svg          %8.1f КБ" %
          (write_svg(os.path.join(GEO, "world-base-debug.svg"), data, debug=True) / 1024))
    print("world-base-polar.svg          %8.1f КБ" %
          (write_polar_svg(os.path.join(GEO, "world-base-polar.svg"), data) / 1024))
    print("world-base-polar-equalarea.svg %7.1f КБ" %
          (write_polar_svg(os.path.join(GEO, "world-base-polar-equalarea.svg"), data,
                           kind="equal_area") / 1024))

    # --- игровая база -----------------------------------------------------
    game, journal = build_game_base(data, data["raw_union"])
    print()
    for op, what, delta, why in journal:
        d = f"{delta:+,} км²" if isinstance(delta, (int, float)) and delta else ""
        print(f"[{op}] {what} {d} — {why}")
    print()
    gfc = build_featurecollection(game)
    gfc["metadata"]["name"] = "oil-wars-world-game"
    gfc["metadata"]["purpose"] = (
        "география с игровыми коррекциями: рабочая основа для разбиения "
        "на регионы. Честная география — world-base.geojson"
    )
    gfc["metadata"]["adjustments"] = [
        OrderedDict([("op", op), ("subject", what), ("added_km2", delta), ("reason", why)])
        for op, what, delta, why in journal
    ]
    print("world-game.geojson            %8.1f КБ" %
          (write_json(os.path.join(GEO, "world-game.geojson"), gfc) / 1024))
    print("world-game.svg                %8.1f КБ" %
          (write_svg(os.path.join(GEO, "world-game.svg"), game) / 1024))
    print("world-game-polar.svg          %8.1f КБ" %
          (write_polar_svg(os.path.join(GEO, "world-game-polar.svg"), game) / 1024))

    narrow = measure_narrow(data["land"])
    gaps = measure_gaps(data["continents"], data["land"])
    print("world-base-report.md          %8.1f КБ" %
          (write_report(os.path.join(GEO, "world-base-report.md"),
                        data, checks, narrow, gaps, game, journal) / 1024))
    return 0


if __name__ == "__main__":
    sys.exit(main())
