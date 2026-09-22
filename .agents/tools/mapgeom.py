#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
mapgeom.py — геометрическая приёмка игрового поля по SPEC-BOARD.md.

map.py проверяет ТОПОЛОГИЮ (кто с кем граничит) по YAML-реестру.
mapgeom.py проверяет ГЕОМЕТРИЮ (влезают ли фигуры, не слиплись ли области)
по слоям PSD и сверяет полученные смежности с тем же реестром.

Источник геометрии — маски областей в слоях PSD. Источник истины
по смежностям — registry/map/edges.yaml: картинка подгоняется под реестр,
а не наоборот.

Использование:
    python mapgeom.py measure            # замер: A, U, N_пех/маш/роб, U/A -> derived/geometry.json
    python mapgeom.py adjacency          # смежности из масок против edges.yaml
    python mapgeom.py check              # PASS/FAIL по SPEC-BOARD §4 и §6
    python mapgeom.py report             # ../out/12-mapgeom.md
    python mapgeom.py all                # measure + adjacency + check + report

Ключи:
    --psd ПУТЬ        файл карты (по умолчанию ../../Карта/карта 5.psd)
    --scale N         уменьшение при замере, по умолчанию 4
    --sheet ШхВ       габарит полотна в мм, по умолчанию берётся из --dpi
    --dpi N           плотность исходника, по умолчанию 300
    --inside 85       доля подставки внутри региона, % (SPEC-BOARD §5.2)
    --target ШхВ      пересчитать замер на целевой габарит полотна, мм

Зависимости: PyYAML, psd-tools, numpy, scipy, Pillow
    pip install pyyaml psd-tools numpy scipy pillow

Python на машине нет — гонять в Docker, как registry.py и map.py:

    docker run --rm -v "C:/YandexDisk/Oil Wars:/w" -w /w/.agents python:3.12-slim \\
      sh -c "pip install --quiet pyyaml psd-tools numpy scipy pillow && \\
             python tools/mapgeom.py all"
"""

import argparse
import gc
import json
import math
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("Нужен PyYAML: pip install pyyaml")
try:
    import numpy as np
    from scipy import ndimage as ndi
    from PIL import Image
    import psd_tools
except ImportError as e:
    sys.exit(f"Нужны psd-tools, numpy, scipy, Pillow: pip install psd-tools numpy scipy pillow ({e})")

Image.MAX_IMAGE_PIXELS = None

ROOT = Path(__file__).resolve().parent.parent
MAP = ROOT / "registry" / "map"
DERIVED = MAP / "derived"
OUT = ROOT / "out"
PSD_DEFAULT = ROOT.parent / "Карта" / "карта 5.psd"

# --- SPEC-BOARD §5.2, §6 -----------------------------------------------------

D_INF, D_MAC, D_ROB = 25.0, 40.0, 60.0   # ⌀ подставок, мм
GAP = 1.0                                 # зазор между фигурами, мм
EDGE_MIN_MM = 8.0                         # §4.1 отказ: граница не читается
EDGE_WARN_MM = 25.0                       # §4.1 предупреждение: узкое место
NONADJ_MIN_MM = 12.0                      # §4.2 минимальный зазор несмежных
DILATE = 3                                # px расширения маски при поиске касаний
MIN_PART_CM2 = 1.0                        # кусок мельче — мусор слоя, не остров
TECH_MARGIN_MM = 10.0                     # §2 технологическое поле полотна

# §6: (минимум, норма, крупные). Площадь A в вердикт НЕ входит — §5.1 прямо
# говорит, что требования на ней не строятся: она справочная.
THRESHOLDS = {
    "U":    (55, 85, 150),
    "Ninf": (10, 14, 20),
    "Nmac": (3, 5, 8),
    "Nrob": (1, 2, 3),
    "UA":   (0.55, 0.65, 0.70),
}
A_REFERENCE = (90, 140, 250)              # ориентир по площади, не критерий
START_NINF = 14                           # §6, §8.2 стартовые области

# Слои PSD -> ID областей реестра. Правится, если в PSD переименуют слои.
LAYER_MAP = {
    ("Материки База", "Сев. Америка"):        "MR-L3-NAM",
    ("Материки База", "Южная Америка"):       "MR-L3-SAM",
    ("Материки База", "Австралия"):           "MR-L3-AUS",
    ("Материки База", "Европа"):              "MR-R3-EUR",
    ("Материки База", "Азия"):                "MR-R3-ASI",
    ("Материки База", "Африка"):              "MR-R3-AFR",
    ("Материки База", "Антарктида"):          "MR-SH-ANT",
    ("Океаны База", "Северный ледовитый"):    "MR-OC-ARC",
    ("Океаны База", "Север Тихого океана"):   "MR-OC-NPAC",
    ("Океаны База", "Юг Тихого океана"):      "MR-OC-SPAC",
    ("Океаны База", "Северная Атлантика"):    "MR-OC-NATL",
    ("Океаны База", "Южная Атлантика"):       "MR-OC-SATL",
    ("Океаны База", "Индийский океан"):       "MR-OC-IND",
    ("3 игрока", "Сев. Америка - запад"):     "MR-L5-NAMW",
    ("3 игрока", "Сев. Америка - восток"):    "MR-L5-NAME",
    ("3 игрока", "Центральная америка"):      "MR-L5-CAM",
    ("3 игрока", "Южная Америка - запад"):    "MR-L5-SAMW",
    ("3 игрока", "Южная Америка - восток"):   "MR-L5-SAME",
    ("3 игрока", "Австралия"):                "MR-L5-AUS",
    ("3 игрока", "Новая зеландия"):           "MR-L5-NZL",
    ("3 игрока", "Антарктида"):               "MR-SH-ANT",
    ("3 игрока", "Африка западная"):          "MR-R5-AFRW",
    ("3 игрока", "Африка восточная"):         "MR-R5-AFRE",
    ("3 игрока", "Азия"):                     "MR-R5-ASIS",
    ("3 игрока", "Слой 3"):                   "MR-R5-ARB",   # MF-002: слой не назван
    ("3 игрока", "Северная Азия"):            "MR-R5-ASIN",
    ("3 игрока", "Европа"):                   "MR-R5-EUR",
    ("3 игрока", "Скандинавия"):              "MR-R5-SCA",
}
GROUPS = ("Материки База", "Океаны База", "3 игрока")


def k_inside(pct):
    """Во сколько радиусов от границы должен стоять центр фигуры,
    чтобы внутри региона оказалось не менее pct % площади подставки."""
    want = pct / 100.0
    lo, hi = 0.0, 1.0
    for _ in range(80):
        m = (lo + hi) / 2
        th = 2 * math.acos(m)
        inside = 1 - (th - math.sin(th)) / 2 / math.pi
        if inside < want:
            lo = m
        else:
            hi = m
    return (lo + hi) / 2


def load_registry():
    def y(name):
        return yaml.safe_load((MAP / name).read_text(encoding="utf-8"))
    regions = y("regions.yaml")["regions"]
    edges = y("edges.yaml")["edges"]
    cfg = y("configs.yaml")
    redesign = {r["baseline_ref"]: r for r in y("redesign.yaml")["regions"]}
    glyphs = y("glyphs.yaml")
    return regions, edges, cfg, redesign, glyphs


def start_regions(glyphs):
    ids = set()
    for g in glyphs.get("start_areas_redesign") or glyphs.get("faction_glyphs") or []:
        for key in ("regions_3p", "regions_5p"):
            for rid in (g.get(key) or []):
                ids.add(rid)
    return ids


# --- замер -------------------------------------------------------------------

def extract_masks(psd_path, scale):
    psd = psd_tools.PSDImage.open(str(psd_path))
    W, H = psd.width // scale, psd.height // scale
    raw, order = {}, {}
    for group in psd:
        if not group.is_group() or group.name not in GROUPS:
            continue
        layers = [l for l in group if l.kind == "pixel"]
        order[group.name] = []
        for i, layer in enumerate(layers):
            rid = LAYER_MAP.get((group.name, layer.name))
            if rid is None:
                continue
            pil = layer.topil()
            if pil is None:
                continue
            a = pil.getchannel("A") if pil.mode in ("RGBA", "LA") else pil.convert("L")
            nw, nh = max(1, a.size[0] // scale), max(1, a.size[1] // scale)
            arr = np.asarray(a.resize((nw, nh), Image.BILINEAR)) > 127
            del pil, a
            canvas = np.zeros((H, W), dtype=bool)
            x0, y0 = layer.offset[0] // scale, layer.offset[1] // scale
            x1, y1 = min(W, x0 + nw), min(H, y0 + nh)
            sx0, sy0 = max(0, x0), max(0, y0)
            if x1 > sx0 and y1 > sy0:
                canvas[sy0:y1, sx0:x1] = arr[sy0 - y0:y1 - y0, sx0 - x0:x1 - x0]
            del arr
            gc.collect()
            raw[(group.name, i, rid)] = canvas
            order[group.name].append((i, rid))
    # вычитание вышележащих слоёв внутри группы
    clean = {}
    for gname in order:
        keys = sorted([k for k in raw if k[0] == gname], key=lambda k: k[1])
        for idx, k in enumerate(keys):
            m = raw[k].copy()
            for k2 in keys[idx + 1:]:
                m &= ~raw[k2]
            clean[k[2]] = clean.get(k[2], np.zeros_like(m)) | m
    return clean, (W, H), (psd.width, psd.height)


def drop_specks(masks, mm_per_px, min_cm2=MIN_PART_CM2):
    """Отбрасывает связные куски мельче min_cm2: это мусор в слоях PSD,
    а не острова. Без этого одиночный обрывок у края листа даёт ложную
    смежность — так Африка «касалась» Северного Ледовитого океана."""
    px_limit = min_cm2 * 100.0 / (mm_per_px ** 2)
    dropped = []
    for rid, m in masks.items():
        lab, n = ndi.label(m)
        if n <= 1:
            continue
        sizes = ndi.sum(m, lab, range(1, n + 1))
        keep = np.zeros_like(m)
        for i, sz in enumerate(sizes, start=1):
            if sz >= px_limit:
                keep |= (lab == i)
            else:
                ys, xs = np.nonzero(lab == i)
                dropped.append((rid, round(sz * mm_per_px ** 2 / 100, 2),
                                round(float(xs.mean()) * mm_per_px),
                                round(float(ys.mean()) * mm_per_px)))
        masks[rid] = keep
    return dropped


def pack(edt, d, k, mm_per_px, maxn=200):
    r_edge = (k * d / 2.0) / mm_per_px
    r_excl = ((d + GAP) / 2.0) / mm_per_px
    work = edt.copy()
    yy, xx = np.ogrid[:work.shape[0], :work.shape[1]]
    n = 0
    while n < maxn:
        i = int(np.argmax(work))
        y, x = divmod(i, work.shape[1])
        if work[y, x] < r_edge:
            break
        n += 1
        work[(xx - x) ** 2 + (yy - y) ** 2 < (2 * r_excl) ** 2] = 0
    return n


def edt_of(m):
    h, w = m.shape
    pad = np.zeros((h + 2, w + 2), bool)
    pad[1:-1, 1:-1] = m
    return ndi.distance_transform_edt(pad)[1:-1, 1:-1]


def measure(masks, mm_per_px, k):
    rows = {}
    for rid, m in masks.items():
        area_px = int(m.sum())
        if area_px == 0:
            continue
        e = edt_of(m)
        A = area_px * mm_per_px ** 2 / 100.0
        U = float((e >= (k * D_INF / 2.0) / mm_per_px).sum()) * mm_per_px ** 2 / 100.0
        lab, ncc = ndi.label(e >= (k * D_INF / 2.0) / mm_per_px)
        if ncc > 1:
            sizes = ndi.sum(np.ones_like(lab), lab, range(1, ncc + 1))
            main_share = float(max(sizes)) / float(sum(sizes))
        else:
            main_share = 1.0
        rows[rid] = {
            "A": round(A, 1),
            "U": round(U, 1),
            "UA": round(U / A, 3) if A else 0.0,
            "Ninf": pack(e, D_INF, k, mm_per_px),
            "Nmac": pack(e, D_MAC, k, mm_per_px),
            "Nrob": pack(e, D_ROB, k, mm_per_px),
            "incircle": round(float(e.max()) * 2 * mm_per_px, 1),
            "U_main_share": round(main_share, 3),
            "parts": int(ndi.label(m)[1]),
        }
        del e
        gc.collect()
    return rows


# --- смежности ---------------------------------------------------------------

def present(region, conf):
    """Правило присутствия из configs.yaml: область входит в раскладку, если
    side == BOTH либо side совпадает со стороной её планшета."""
    if region["side"] == "BOTH":
        return True
    if region["board"] == "LEFT":
        return region["side"] == conf["left"]
    if region["board"] == "RIGHT":
        return region["side"] == conf["right"]
    return True


def adjacency(masks, mm_per_px, edges, regions, cfg):
    """Смежности сверяются ПО РАСКЛАДКАМ: пара сравнивается только если обе
    области попадают на одно полотно. Иначе родитель стороны «3» и его дети
    стороны «5» дают ложные пересечения — они никогда не лежат вместе."""
    declared = {frozenset((e["a"], e["b"])) for e in edges}
    byid = {r["id"]: r for r in regions}
    ids = sorted(masks)

    # Маски в PSD разделены нарисованной линией границы, поэтому расширяем
    # каждую на DILATE px — иначе соседние области «не касаются». Пересечение
    # двух расширенных масок — полоса вдоль границы толщиной ~2*DILATE+1 px;
    # длина границы = площадь полосы / её толщина.
    band = 2 * DILATE + 1
    grown = {rid: ndi.binary_dilation(masks[rid], iterations=DILATE) for rid in ids}
    dist = {rid: ndi.distance_transform_edt(~masks[rid]) for rid in ids}

    touch_mm, gap_mm = {}, {}
    for i, a in enumerate(ids):
        for b in ids[i + 1:]:
            px = int((grown[a] & grown[b]).sum())
            pair = frozenset((a, b))
            if px:
                touch_mm[pair] = round(px * mm_per_px / band, 1)
            else:
                gap_mm[pair] = round(float(dist[a][masks[b]].min()) * mm_per_px, 1)

    problems = []
    seen = set()
    for conf in cfg["configs"]:
        inside = {rid for rid in ids
                  if rid in byid and present(byid[rid], conf)}
        cid = conf["id"]
        for pair in declared:
            a, b = sorted(pair)
            if a not in inside or b not in inside:
                continue
            key = ("MISSING", a, b)
            if pair not in touch_mm:
                if key not in seen:
                    seen.add(key)
                    problems.append(("MISSING", a, b, None, cid,
                                     "реестр требует смежность, на карте её нет"))
            elif touch_mm[pair] < EDGE_MIN_MM:
                key = ("SHORT", a, b)
                if key not in seen:
                    seen.add(key)
                    problems.append(("SHORT", a, b, touch_mm[pair], cid,
                                     f"касание короче {EDGE_MIN_MM:.0f} мм — "
                                     f"граница не читается"))
            elif touch_mm[pair] < EDGE_WARN_MM:
                key = ("NARROW", a, b)
                if key not in seen:
                    seen.add(key)
                    problems.append(("NARROW", a, b, touch_mm[pair], cid,
                                     f"узкое место: касание короче "
                                     f"{EDGE_WARN_MM:.0f} мм, проверить глазами"))
        for pair, mm in touch_mm.items():
            a, b = sorted(pair)
            if a not in inside or b not in inside or pair in declared:
                continue
            key = ("EXTRA", a, b)
            if key not in seen:
                seen.add(key)
                problems.append(("EXTRA", a, b, mm, cid,
                                 "области соприкасаются, в реестре ребра нет"))
        for pair, gap in gap_mm.items():
            a, b = sorted(pair)
            if a not in inside or b not in inside or pair in declared:
                continue
            if gap >= NONADJ_MIN_MM:
                continue
            key = ("NEAR", a, b)
            if key not in seen:
                seen.add(key)
                problems.append(("NEAR", a, b, gap, cid,
                                 f"несмежные ближе {NONADJ_MIN_MM:.0f} мм"))
    return problems, touch_mm, gap_mm


# --- проверка ----------------------------------------------------------------

def grade(row):
    lvl = "не проходит"
    for name, idx in (("минимум", 0), ("норма", 1), ("крупная", 2)):
        ok = all(row[key] >= THRESHOLDS[key][idx] for key in THRESHOLDS)
        if ok:
            lvl = name
    return lvl


def check(rows, starts, verbose=True):
    fails = []
    for rid, row in sorted(rows.items()):
        lvl = row["grade"] = grade(row)
        if lvl == "не проходит":
            bad = [k for k in THRESHOLDS if row[k] < THRESHOLDS[k][0]]
            fails.append((rid, "минимум не взят: " + ", ".join(bad)))
        if row["U_main_share"] < 0.60:
            fails.append((rid, f"рабочая зона разорвана: крупнейший кусок "
                               f"{row['U_main_share']*100:.0f} % при норме 60 %"))
        if rid in starts and row["Ninf"] < START_NINF:
            fails.append((rid, f"стартовая область: N_пех {row['Ninf']} "
                               f"при требуемых {START_NINF}"))
    if verbose:
        for rid, msg in fails:
            print(f"  FAIL  {rid}: {msg}")
    return fails


# --- вывод -------------------------------------------------------------------

def name_of(rid, redesign):
    r = redesign.get(rid)
    return r["name_ru"] if r else rid


def print_table(rows, redesign, starts):
    hdr = (f"{'ID':13}{'область':26}{'A':>6}{'U':>6}{'U/A':>6}"
           f"{'пех':>5}{'маш':>5}{'роб':>5}{'вписан':>8}  вердикт")
    print(hdr)
    print("-" * len(hdr))
    for rid, r in sorted(rows.items(), key=lambda kv: kv[1]["U"]):
        star = " ★" if rid in starts else ""
        print(f"{rid:13}{(name_of(rid, redesign) + star)[:25]:26}{r['A']:6.0f}{r['U']:6.0f}"
              f"{r['UA']:6.2f}{r['Ninf']:5d}{r['Nmac']:5d}{r['Nrob']:5d}"
              f"{r['incircle']:8.0f}  {r['grade']}")


def report(rows, problems, redesign, starts, meta):
    OUT.mkdir(parents=True, exist_ok=True)
    L = ["# 12 — геометрическая приёмка поля", "",
         "Сгенерировано `tools/mapgeom.py`, руками не правится.",
         f"Критерии — `registry/map/SPEC-BOARD.md`. Источник геометрии — `{meta['psd']}`.",
         "", "## Параметры замера", "",
         f"- полотно: {meta['sheet_w']:.0f} × {meta['sheet_h']:.0f} мм",
         f"- исходник: {meta['px_w']} × {meta['px_h']} px, {meta['dpi']:.0f} dpi",
         f"- правило вписывания: {meta['inside']:.0f} % подставки внутри региона "
         f"(отступ центра {meta['k']:.3f} · r)",
         f"- отступы до центра: пехота {meta['k']*D_INF/2:.1f} мм, "
         f"машина {meta['k']*D_MAC/2:.1f} мм, робот {meta['k']*D_ROB/2:.1f} мм",
         "", "## Области", "",
         "| Область | A, см² | U, см² | U/A | N_пех | N_маш | N_роб | Вписан, мм | Вердикт |",
         "|---|---|---|---|---|---|---|---|---|"]
    for rid, r in sorted(rows.items(), key=lambda kv: kv[1]["U"]):
        star = " ★" if rid in starts else ""
        L.append(f"| {name_of(rid, redesign)}{star} | {r['A']:.0f} | {r['U']:.0f} | "
                 f"{r['UA']:.2f} | {r['Ninf']} | {r['Nmac']} | {r['Nrob']} | "
                 f"{r['incircle']:.0f} | {r['grade']} |")
    L += ["", "★ — стартовая область, требование N_пех ≥ "
          f"{START_NINF} (SPEC-BOARD §6, §8.3).", ""]
    L += ["## Смежности против реестра", "",
          "Сверка идёт по раскладкам: пара областей сравнивается только там, "
          "где обе лежат на одном полотне.", ""]
    if not problems:
        L.append("Расхождений нет: геометрия совпадает с `edges.yaml`.")
    else:
        L += ["| Тип | Область A | Область B | Замер, мм | Раскладка | Что не так |",
              "|---|---|---|---|---|---|"]
        for kind, a, b, val, cid, msg in sorted(problems):
            v = f"{val:.1f}" if val is not None else "—"
            L.append(f"| `{kind}` | {name_of(a, redesign)} | {name_of(b, redesign)} "
                     f"| {v} | `{cid}` | {msg} |")
    L += ["", "Типы: `MISSING` — реестр требует смежность, её нет; `EXTRA` — "
          "области соприкасаются, ребра в реестре нет; `SHORT` — касание короче "
          f"{EDGE_MIN_MM:.0f} мм; `NEAR` — несмежные ближе {NONADJ_MIN_MM:.0f} мм.", ""]
    (OUT / "12-mapgeom.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"Записано {OUT / '12-mapgeom.md'}")


# --- CLI ---------------------------------------------------------------------

def parse_size(s):
    w, h = s.lower().replace("×", "x").split("x")
    return float(w), float(h)


def main():
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("cmd", choices=["measure", "adjacency", "check", "report", "all"])
    ap.add_argument("--psd", default=str(PSD_DEFAULT))
    ap.add_argument("--scale", type=int, default=4)
    ap.add_argument("--dpi", type=float, default=300.0)
    ap.add_argument("--sheet", default=None, help="габарит полотна ШхВ в мм")
    ap.add_argument("--target", default=None, help="пересчитать на целевой габарит ШхВ")
    ap.add_argument("--inside", type=float, default=85.0)
    a = ap.parse_args()

    psd_path = Path(a.psd)
    if not psd_path.exists():
        sys.exit(f"Нет файла карты: {psd_path}")

    regions, edges, cfg, redesign, glyphs = load_registry()
    starts = start_regions(glyphs)
    k = k_inside(a.inside)

    print(f"Файл: {psd_path.name}")
    masks, (W, H), (PW, PH) = extract_masks(psd_path, a.scale)
    print(f"Областей снято: {len(masks)} из {len(set(LAYER_MAP.values()))}")

    if a.sheet:
        sw, sh = parse_size(a.sheet)
    else:
        sw, sh = PW / a.dpi * 25.4, PH / a.dpi * 25.4
    if a.target:
        tw, th = parse_size(a.target)
        print(f"Пересчёт на целевой габарит {tw:.0f} × {th:.0f} мм "
              f"(было {sw:.0f} × {sh:.0f})")
        sw, sh = tw, th
    mm_per_px = sw / W
    print(f"Полотно {sw:.0f} × {sh:.0f} мм, {mm_per_px:.4f} мм/px, "
          f"правило вписывания {a.inside:.0f} % (k = {k:.3f})")

    dropped = drop_specks(masks, mm_per_px)
    if dropped:
        print(f"Отброшено крошек мельче {MIN_PART_CM2} см² — {len(dropped)}:")
        for rid, cm2, x, y_ in sorted(dropped, key=lambda d: -d[1])[:10]:
            print(f"   {rid:13}{cm2:6.2f} см²  в точке x {x} мм, y {y_} мм")
        print("   Это мусор в слоях PSD; на замер не влияет, но ломал смежности.")

    rows = measure(masks, mm_per_px, k)
    for r in rows.values():
        r["grade"] = grade(r)
    DERIVED.mkdir(parents=True, exist_ok=True)
    meta = {"psd": psd_path.name, "sheet_w": sw, "sheet_h": sh,
            "px_w": PW, "px_h": PH, "dpi": a.dpi, "inside": a.inside, "k": k,
            "scale": a.scale}
    (DERIVED / "geometry.json").write_text(
        json.dumps({"meta": meta, "regions": rows}, ensure_ascii=False, indent=1),
        encoding="utf-8")

    problems = []
    if a.cmd in ("adjacency", "check", "report", "all"):
        problems, _, _ = adjacency(masks, mm_per_px, edges, regions, cfg)

    if a.cmd in ("measure", "all"):
        print()
        print_table(rows, redesign, starts)
    if a.cmd in ("adjacency", "all"):
        print()
        if not problems:
            print("Смежности: расхождений с реестром нет.")
        else:
            for kind, x, y_, val, cid, msg in sorted(problems):
                v = f"{val:7.1f} мм" if val is not None else "      —   "
                print(f"  {kind:8}{v}  [{cid:8}]  {x} — {y_}: "
                      f"{name_of(x, redesign)} — {name_of(y_, redesign)}")
    fails = []
    if a.cmd in ("check", "all"):
        print()
        fails = check(rows, starts)
        hard = [p for p in problems if p[0] in ("MISSING", "EXTRA", "SHORT")]
        warn = [p for p in problems if p[0] == "NARROW"]
        soft = [p for p in problems if p[0] == "NEAR"]
        print(f"\nИтог: областей {len(rows)}, не проходят минимум "
              f"{len({f[0] for f in fails})}; "
              f"нарушений топологии {len(hard)}, сближений {len(soft)}, "
              f"узких мест {len(warn)}")
        if not fails and not hard and not soft and not warn:
            print("PASS — поле удовлетворяет SPEC-BOARD.")
    if a.cmd in ("report", "all"):
        report(rows, problems, redesign, starts, meta)

    bad = bool(fails) or any(p[0] in ("MISSING", "EXTRA", "SHORT") for p in problems)
    sys.exit(1 if bad and a.cmd in ("check", "all") else 0)


if __name__ == "__main__":
    main()
