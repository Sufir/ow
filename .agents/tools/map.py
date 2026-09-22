#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
map.py — валидация подреестра карты, сборка графов конфигураций и отчёт.

YAML в ../registry/map/ — источник истины. Всё в registry/map/derived/ и
../out/11-map.md — производные: руками не правятся, пересобираются этим скриптом.

Использование:
    python map.py check      # валидация YAML: ID, словари, ссылки, целостность модели
    python map.py build      # собрать графы всех конфигураций в registry/map/derived/
    python map.py verify     # сверить собранные графы с опубликованными инвариантами
    python map.py report     # сгенерировать ../out/11-map.md
    python map.py all        # check + build + verify + report

Зависимость: PyYAML  ->  pip install pyyaml
"""

import json
import re
import sys
from collections import deque
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("Нужен PyYAML: pip install pyyaml")

ROOT = Path(__file__).resolve().parent.parent
MAP = ROOT / "registry" / "map"
DERIVED = MAP / "derived"
OUT = ROOT / "out"

TYPES = {"LAND", "OCEAN"}
LANDMASSES = {"NORTH_AMERICA", "SOUTH_AMERICA", "EUROPE", "ASIA",
              "AFRICA", "AUSTRALIA", "ANTARCTICA"}
BASINS = {"PACIFIC", "ATLANTIC", "INDIAN", "ARCTIC"}
BOARDS = {"LEFT", "RIGHT", "BOTH"}
SIDES = {"3P", "5P", "BOTH"}
KINDS = {"LAND-LAND", "LAND-OCEAN", "OCEAN-OCEAN"}
RE_REGION = re.compile(r"^MR-(OC|SH|L3|R3|L5|R5)-[A-Z]+$")
RE_EDGE = re.compile(r"^ME-\d{3}$")
RE_CONFIG = re.compile(r"^MC-[0-9A-Z-]+$")
RE_FINDING = re.compile(r"^MF-\d{3}$")
RE_GLYPH = re.compile(r"^MG-\d{3}$")
RE_LANDMARK = re.compile(r"^ML-\d{3}$")
RE_SYMBOL = re.compile(r"^MS-\d{3}$")


def load():
    def y(name):
        return yaml.safe_load((MAP / name).read_text(encoding="utf-8"))
    return {
        "regions": y("regions.yaml")["regions"],
        "edges": y("edges.yaml")["edges"],
        "cfg": y("configs.yaml"),
        "redesign": y("redesign.yaml")["regions"],
        "findings": y("findings.yaml")["findings"],
        "glyphs": y("glyphs.yaml"),
    }


def glyph_index(d, cfg):
    """region_id -> список глифов, присутствующих в этой конфигурации."""
    side = {"LEFT": cfg["left"], "RIGHT": cfg["right"]}
    R = {r["id"]: r for r in d["regions"]}
    idx = {}
    for g in d["glyphs"]["faction_glyphs"]:
        for rid in (g["regions_3p"] or []) + (g["regions_5p"] or []):
            r = R.get(rid)
            if r is None:
                continue
            if r["side"] == "BOTH" or r["board"] == "BOTH" or \
                    r["side"] == side[r["board"]]:
                idx.setdefault(rid, [])
                if g["id"] not in [x["id"] for x in idx[rid]]:
                    idx[rid].append({"id": g["id"],
                                     "faction_original": g["faction_original_name"],
                                     "faction_redesign": g["faction_redesign_name"],
                                     "confidence": g["confidence"]})
    return idx


def symbol_index(d, cfg=None):
    """region_id -> запись символа региона. cfg=None — по обеим сторонам сразу."""
    R = {r["id"]: r for r in d["regions"]}
    idx = {}
    for s in d["glyphs"].get("region_symbols", []):
        for rid in (s["regions_3p"] or []) + (s["regions_5p"] or []):
            r = R.get(rid)
            if r is None:
                continue
            if cfg is not None and not present(r, cfg):
                continue
            idx[rid] = {"id": s["id"], "original_name": s["original_name"],
                        "glyph": s["redesign_glyph"], "symbol": s["redesign_symbol"],
                        "icon_ref": s["icon_ref"]}
    return idx


# ---------------------------------------------------------------- check

def check_region_symbols(d, R, errs):
    S = d["glyphs"].get("region_symbols")
    if not S:
        errs.append("region_symbols: раздел отсутствует или пуст")
        return
    if len(S) != 3:
        errs.append(f"region_symbols: записей {len(S)}, должно быть ровно 3")
    seen_id, seen_glyph, seen_icon = set(), set(), set()
    owner = {}                       # region_id -> symbol_id
    for s in S:
        i = s["id"]
        if not RE_SYMBOL.match(i):
            errs.append(f"region_symbol {i}: ID не по формату MS-###")
        for key, bag in (("id", seen_id), ("redesign_glyph", seen_glyph),
                         ("icon_ref", seen_icon)):
            if s[key] in bag:
                errs.append(f"{i}: дубликат {key}={s[key]}")
            bag.add(s[key])
        if s["confidence"] not in ("HIGH", "MEDIUM", "LOW"):
            errs.append(f"{i}: confidence={s['confidence']} вне словаря")
        for lm in s["landmasses"]:
            if lm not in LANDMASSES:
                errs.append(f"{i}: landmass={lm} вне словаря")
        for key, want_side in (("regions_3p", "3P"), ("regions_5p", "5P")):
            for rid in s[key] or []:
                r = R.get(rid)
                if r is None:
                    errs.append(f"{i}: {key} ссылается на несуществующую {rid}")
                    continue
                if r["side"] not in ("BOTH", want_side):
                    errs.append(f"{i}: {key}={rid}, но эта область не со стороны {want_side}")
                if r["type"] != "LAND":
                    errs.append(f"{i}: {key}={rid} — это не суша, символы стоят только на суше")
                if r["landmass"] not in s["landmasses"]:
                    errs.append(f"{i}: {key}={rid} на материке {r['landmass']}, "
                                f"а символ объявлен для {s['landmasses']}")
                if rid in owner:
                    errs.append(f"{rid}: два символа сразу — {owner[rid]} и {i}")
                owner[rid] = i
    for i, r in R.items():
        # Антарктида — единственная область суши без символа, см. glyphs.yaml
        if r["type"] == "LAND" and r["landmass"] != "ANTARCTICA" and i not in owner:
            errs.append(f"{i}: область суши без символа региона")
        if (r["type"] == "OCEAN" or r["landmass"] == "ANTARCTICA") and i in owner:
            errs.append(f"{i}: у этой области символа быть не должно ({owner[i]})")
    for i, r in R.items():
        if r["parent"] and i in owner and r["parent"] in owner \
                and owner[i] != owner[r["parent"]]:
            errs.append(f"{i}: символ {owner[i]} не совпадает с символом "
                        f"родителя {r['parent']} ({owner[r['parent']]})")


def check(d):
    errs = []
    R = {}
    for r in d["regions"]:
        i = r["id"]
        if not RE_REGION.match(i):
            errs.append(f"region {i}: ID не по формату MR-<SCOPE>-<SHORT>")
        if i in R:
            errs.append(f"region {i}: дубликат ID")
        R[i] = r
    for i, r in R.items():
        if r["type"] not in TYPES:
            errs.append(f"{i}: type={r['type']} вне словаря")
        if r["board"] not in BOARDS:
            errs.append(f"{i}: board={r['board']} вне словаря")
        if r["side"] not in SIDES:
            errs.append(f"{i}: side={r['side']} вне словаря")
        if r["type"] == "LAND":
            if r["landmass"] not in LANDMASSES:
                errs.append(f"{i}: landmass={r['landmass']} вне словаря")
            if r["basin"] is not None:
                errs.append(f"{i}: у суши не должно быть basin")
        else:
            if r["basin"] not in BASINS:
                errs.append(f"{i}: basin={r['basin']} вне словаря")
            if r["landmass"] is not None:
                errs.append(f"{i}: у океана не должно быть landmass")
        p = r["parent"]
        if r["side"] == "5P":
            if p is None:
                errs.append(f"{i}: область стороны 5P обязана ссылаться на parent")
            elif p not in R:
                errs.append(f"{i}: parent={p} не найден")
            else:
                q = R[p]
                if q["side"] != "3P":
                    errs.append(f"{i}: parent {p} не со стороны 3P")
                if q["board"] != r["board"]:
                    errs.append(f"{i}: parent {p} на другом планшете")
                if q["landmass"] != r["landmass"]:
                    errs.append(f"{i}: parent {p} на другом материке")
        elif p is not None:
            errs.append(f"{i}: parent разрешён только у стороны 5P")
    for i, r in R.items():
        if r["side"] == "3P":
            kids = [k for k, q in R.items() if q["parent"] == i]
            if not kids:
                errs.append(f"{i}: у области стороны 3P нет ни одной области стороны 5P")

    E, seen = {}, set()
    for e in d["edges"]:
        i = e["id"]
        if not RE_EDGE.match(i):
            errs.append(f"edge {i}: ID не по формату ME-###")
        if i in E:
            errs.append(f"edge {i}: дубликат ID")
        E[i] = e
        a, b = e["a"], e["b"]
        if a not in R or b not in R:
            errs.append(f"{i}: ссылка на несуществующую область {a}/{b}")
            continue
        if a == b:
            errs.append(f"{i}: петля")
        key = frozenset((a, b))
        if key in seen:
            errs.append(f"{i}: дубликат ребра {a}–{b}")
        seen.add(key)
        ta, tb = R[a]["type"], R[b]["type"]
        want = "OCEAN-OCEAN" if ta == tb == "OCEAN" else ("LAND-LAND" if ta == tb == "LAND" else "LAND-OCEAN")
        if e["kind"] != want:
            errs.append(f"{i}: kind={e['kind']}, а по типам областей должно быть {want}")
        obs = set(e.get("observed_on") or [])
        if not obs or not obs <= {"3P", "5P"}:
            errs.append(f"{i}: observed_on={sorted(obs)} пуст или вне словаря")
        if set((e.get("contact_px") or {})) - obs:
            errs.append(f"{i}: contact_px содержит сторону, которой нет в observed_on")
        for s in obs:
            for x in (a, b):
                if R[x]["side"] not in ("BOTH", s):
                    errs.append(f"{i}: наблюдалось на {s}, но {x} на этой стороне не существует")

    cfgs = {}
    for c in d["cfg"]["configs"]:
        if not RE_CONFIG.match(c["id"]):
            errs.append(f"config {c['id']}: ID не по формату MC-*")
        if c["id"] in cfgs:
            errs.append(f"config {c['id']}: дубликат ID")
        if c["left"] not in ("3P", "5P") or c["right"] not in ("3P", "5P"):
            errs.append(f"config {c['id']}: стороны планшетов вне словаря")
        cfgs[c["id"]] = c

    ow = set()
    for r in d["redesign"]:
        if r["baseline_ref"] not in R:
            errs.append(f"redesign {r['id']}: baseline_ref={r['baseline_ref']} не найден")
        if r["baseline_ref"] in ow:
            errs.append(f"redesign {r['id']}: на область оригинала уже есть ссылка")
        ow.add(r["baseline_ref"])
    for i in R:
        if i not in ow:
            errs.append(f"{i}: нет пары в redesign.yaml")

    G = d["glyphs"]
    gids, lids = set(), {l["id"] for l in G["landmarks"]}
    for g in G["faction_glyphs"]:
        if not RE_GLYPH.match(g["id"]):
            errs.append(f"glyph {g['id']}: ID не по формату MG-###")
        if g["id"] in gids:
            errs.append(f"glyph {g['id']}: дубликат ID")
        gids.add(g["id"])
        if g["confidence"] not in ("HIGH", "MEDIUM", "LOW"):
            errs.append(f"{g['id']}: confidence={g['confidence']} вне словаря")
        if g["landmark"] is not None and g["landmark"] not in lids:
            errs.append(f"{g['id']}: landmark={g['landmark']} не найден")
        for key, want_side in (("regions_3p", "3P"), ("regions_5p", "5P")):
            for rid in g[key] or []:
                if rid not in R:
                    errs.append(f"{g['id']}: {key} ссылается на несуществующую {rid}")
                elif R[rid]["side"] not in ("BOTH", want_side):
                    errs.append(f"{g['id']}: {key}={rid}, но эта область не со стороны {want_side}")
    for l in G["landmarks"]:
        if not RE_LANDMARK.match(l["id"]):
            errs.append(f"landmark {l['id']}: ID не по формату ML-###")
        if l["glyph_nearby"] is not None and l["glyph_nearby"] not in gids:
            errs.append(f"{l['id']}: glyph_nearby={l['glyph_nearby']} не найден")
        for key, want_side in (("regions_3p", "3P"), ("regions_5p", "5P")):
            for rid in l[key] or []:
                if rid not in R:
                    errs.append(f"{l['id']}: {key} ссылается на несуществующую {rid}")
                elif R[rid]["side"] not in ("BOTH", want_side):
                    errs.append(f"{l['id']}: {key}={rid}, но эта область не со стороны {want_side}")
    for s in G["start_areas_redesign"]:
        if s["glyph"] is not None and s["glyph"] not in gids:
            errs.append(f"start_area {s['faction']}: glyph={s['glyph']} не найден")
        for key, want_side in (("regions_3p", "3P"), ("regions_5p", "5P")):
            for rid in s[key] or []:
                if rid not in R:
                    errs.append(f"start_area {s['faction']}: {key} ссылается на несуществующую {rid}")
                elif R[rid]["side"] not in ("BOTH", want_side):
                    errs.append(f"start_area {s['faction']}: {key}={rid} не со стороны {want_side}")

    check_region_symbols(d, R, errs)

    for f in d["findings"]:
        if not RE_FINDING.match(f["id"]):
            errs.append(f"finding {f['id']}: ID не по формату MF-###")
        closed = f.get("closed") is not None
        if (f["status"] == "CLOSED") != closed:
            errs.append(f"{f['id']}: поле closed заполняется тогда и только тогда, когда status: CLOSED")

    if errs:
        print("check: ОШИБКИ")
        for e in errs:
            print("  -", e)
        return False
    print(f"check: ок (regions={len(R)}, edges={len(E)}, configs={len(cfgs)}, "
          f"redesign={len(d['redesign'])}, glyphs={len(gids)}, landmarks={len(lids)}, "
          f"start_areas={len(G['start_areas_redesign'])}, "
          f"region_symbols={len(G.get('region_symbols', []))}, "
          f"findings={len(d['findings'])})")
    return True


# ---------------------------------------------------------------- build

def present(r, cfg):
    if r["side"] == "BOTH":
        return True
    if r["board"] == "BOTH":
        return True
    return r["side"] == (cfg["left"] if r["board"] == "LEFT" else cfg["right"])


def bfs(adj, s):
    dist = {s: 0}
    q = deque([s])
    while q:
        v = q.popleft()
        for w in adj[v]:
            if w not in dist:
                dist[w] = dist[v] + 1
                q.append(w)
    return dist


def build_graph(d, cfg):
    R = {r["id"]: r for r in d["regions"]}
    gi = glyph_index(d, cfg)
    si = symbol_index(d, cfg)
    V = sorted(i for i, r in R.items() if present(r, cfg))
    S = set(V)
    E = [(e["a"], e["b"]) for e in d["edges"] if e["a"] in S and e["b"] in S]
    adj = {v: set() for v in V}
    for a, b in E:
        adj[a].add(b)
        adj[b].add(a)
    deg = {v: len(adj[v]) for v in V}
    dists = {v: bfs(adj, v) for v in V}
    reach = all(len(dists[v]) == len(V) for v in V)
    diam = max(max(x.values()) for x in dists.values()) if reach else None
    longest = sorted(tuple(sorted((a, b))) for a in V for b in V
                     if a < b and dists[a].get(b) == diam) if reach else []
    hist = {}
    for v in deg.values():
        hist[v] = hist.get(v, 0) + 1
    return {
        "config": cfg["id"], "players": cfg["players"],
        "left": cfg["left"], "right": cfg["right"],
        "areas": len(V),
        "ocean_areas": sum(1 for v in V if R[v]["type"] == "OCEAN"),
        "land_areas": sum(1 for v in V if R[v]["type"] == "LAND"),
        "edges": len(E),
        "connected": reach,
        "diameter": diam,
        "degree_histogram": dict(sorted(hist.items())),
        "degrees": {v: deg[v] for v in V},
        "longest_pairs": [list(p) for p in longest],
        "vertices": [{"id": v, "name_en": R[v]["name_en"], "type": R[v]["type"],
                      "landmass": R[v]["landmass"], "basin": R[v]["basin"],
                      "board": R[v]["board"], "side": R[v]["side"],
                      "glyphs": gi.get(v, []), "symbol": si.get(v), "degree": deg[v],
                      "neighbours": sorted(adj[v])} for v in V],
        "start_glyphs": {v: gi[v] for v in V if v in gi},
        "region_symbols": {v: si[v] for v in V if v in si},
        "region_symbol_counts": {
            s["id"]: sum(1 for v in V if v in si and si[v]["id"] == s["id"])
            for s in d["glyphs"].get("region_symbols", [])},
        "areas_without_symbol": sorted(v for v in V if v not in si),
        "edge_list": [list(p) for p in sorted(E)],
        "distance_matrix": {a: {b: dists[a][b] for b in V} for a in V} if reach else None,
    }


def dot(g, R):
    lines = [f'graph "{g["config"]}" {{', '  layout=neato; overlap=false; splines=true;',
             '  node [shape=ellipse, fontname="Helvetica"];']
    for v in g["vertices"]:
        color = "#9ecae1" if v["type"] == "OCEAN" else "#fdd0a2"
        grp = v["basin"] or v["landmass"]
        lines.append(f'  "{v["id"]}" [label="{v["name_en"]}\\n{grp} · deg {v["degree"]}", '
                     f'style=filled, fillcolor="{color}"];')
    for a, b in g["edge_list"]:
        lines.append(f'  "{a}" -- "{b}";')
    lines.append("}")
    return "\n".join(lines) + "\n"


def matrix_md(g):
    V = [v["id"] for v in g["vertices"]]
    short = {v: v.split("-")[-1] for v in V}
    out = ["| |" + "|".join(short[v] for v in V) + "|",
           "|---|" + "---|" * len(V)]
    S = {tuple(sorted(e)) for e in map(tuple, g["edge_list"])}
    for a in V:
        row = ["1" if tuple(sorted((a, b))) in S else "·" for b in V]
        out.append(f"|**{short[a]}**|" + "|".join(row) + "|")
    return "\n".join(out)


def build(d):
    DERIVED.mkdir(parents=True, exist_ok=True)
    R = {r["id"]: r for r in d["regions"]}
    all_g = {}
    for cfg in d["cfg"]["configs"]:
        g = build_graph(d, cfg)
        all_g[cfg["id"]] = g
        (DERIVED / f"{cfg['id']}.json").write_text(
            json.dumps(g, ensure_ascii=False, indent=1), encoding="utf-8")
        (DERIVED / f"{cfg['id']}.dot").write_text(dot(g, R), encoding="utf-8")
        (DERIVED / f"{cfg['id']}.md").write_text(
            f"# {cfg['id']} — матрица смежности\n\n"
            f"Сгенерировано tools/map.py. Не править руками.\n\n" + matrix_md(g) + "\n",
            encoding="utf-8")
        print(f"build: {cfg['id']}: V={g['areas']} E={g['edges']} "
              f"oceans={g['ocean_areas']} diam={g['diameter']}")
    (DERIVED / "all.json").write_text(
        json.dumps(all_g, ensure_ascii=False, indent=1), encoding="utf-8")
    return all_g


# ---------------------------------------------------------------- verify

def verify(d, all_g):
    rows = []
    ok = True
    for cfg in d["cfg"]["configs"]:
        g = all_g[cfg["id"]]
        p = cfg.get("published") or {}

        def row(name, want, got, ref):
            nonlocal ok
            good = want == got
            ok = ok and good
            rows.append((cfg["id"], name, want, got, "PASS" if good else "FAIL", ref))

        for key, field in (("areas", "areas"), ("ocean_areas", "ocean_areas"),
                           ("diameter", "diameter")):
            if key in p:
                row(key, p[key]["value"], g[field], p[key]["ref"])
        if "degrees" in p:
            want = p["degrees"]["values"]
            got = {k: g["degrees"].get(k) for k in want}
            row("degrees (пофамильно)", want, got, p["degrees"]["ref"])
        if "longest_pairs" in p:
            want = sorted(tuple(sorted(x)) for x in p["longest_pairs"]["values"])
            got = sorted(tuple(sorted(x)) for x in g["longest_pairs"])
            row("longest_pairs", want, got, p["longest_pairs"]["ref"])
        for k, deg in (("degree_count_2", 2), ("degree_count_4", 4)):
            if k in p:
                row(k, p[k]["value"], g["degree_histogram"].get(deg, 0), p[k]["ref"])
        if "edges_minus_other" in p:
            o = p["edges_minus_other"]
            row("edges − edges(%s)" % o["other"], o["value"],
                g["edges"] - all_g[o["other"]]["edges"], o["ref"])
    print(f"verify: {sum(1 for r in rows if r[4]=='PASS')}/{len(rows)} проверок пройдено")
    for r in rows:
        if r[4] == "FAIL":
            print(f"  FAIL {r[0]} {r[1]}: ожидалось {r[2]}, собрано {r[3]} ({r[5]})")
    return rows, ok


# ---------------------------------------------------------------- report

def report(d, all_g, rows, ok):
    OUT.mkdir(parents=True, exist_ok=True)
    R = {r["id"]: r for r in d["regions"]}
    ow = {r["baseline_ref"]: r for r in d["redesign"]}
    L = ["# 11 — Карта: реконструкция оригинального поля",
         "",
         "Сгенерировано `tools/map.py`. Не править руками — источник в `registry/map/`.",
         "",
         "## Сводка по конфигурациям", "",
         "| Конфигурация | Игроков | Левый | Правый | Областей | Суша | Океан | Рёбер | Диаметр | Связный |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for cfg in d["cfg"]["configs"]:
        g = all_g[cfg["id"]]
        L.append(f"| `{g['config']}` | {g['players']} | {g['left']} | {g['right']} | {g['areas']} | "
                 f"{g['land_areas']} | {g['ocean_areas']} | {g['edges']} | {g['diameter']} | "
                 f"{'да' if g['connected'] else 'НЕТ'} |")
    L += ["", "## Сверка с опубликованными величинами оригинала", "",
          "| Конфигурация | Проверка | Опубликовано | Собрано | Итог | Источник |",
          "|---|---|---|---|---|---|"]
    for c, name, want, got, verdict, ref in rows:
        def fmt(x):
            s = json.dumps(x, ensure_ascii=False) if isinstance(x, (dict, list)) else str(x)
            return s if len(s) <= 70 else s[:67] + "…"
        L.append(f"| `{c}` | {name} | {fmt(want)} | {fmt(got)} | **{verdict}** | `{ref}` |")
    L += ["", f"**Итог сверки: {'все проверки пройдены' if ok else 'ЕСТЬ РАСХОЖДЕНИЯ'}.**", ""]
    L += ["## Области", "",
          "| ID | Оригинал | Наше название | Тип | Материк / бассейн | Планшет | Сторона | Дробит |",
          "|---|---|---|---|---|---|---|---|"]
    for i, r in R.items():
        L.append(f"| `{i}` | {r['name_en']} | {ow[i]['name_ru']} | {r['type']} | "
                 f"{r['landmass'] or r['basin']} | {r['board']} | {r['side']} | "
                 f"{'`'+r['parent']+'`' if r['parent'] else '—'} |")

    noted = [e for e in d["edges"] if e.get("note")]
    if noted:
        L += ["", "## Неочевидные смежности", "",
              "Рёбра, у которых в `edges.yaml` заполнено поле `note`: места, где",
              "смежность легко нарисовать неверно.", ""]
        for e in noted:
            L.append(f"**`{e['id']}` {R[e['a']]['name_en']} — {R[e['b']]['name_en']}** "
                     f"({', '.join(e['observed_on'])}): {' '.join(e['note'].split())}")
            L.append("")

    G = d["glyphs"]

    def nm(lst):
        return ", ".join(R[x]["name_en"] for x in (lst or [])) or "—"

    L += ["", "## Стартовые глифы, напечатанные на поле", "",
          "| Глиф | Фракция оригинала | Наша фракция | Сторона «3» | Сторона «5» | Ориентир рядом | Доверие |",
          "|---|---|---|---|---|---|---|"]
    for g in G["faction_glyphs"]:
        lm = next((l["label"] for l in G["landmarks"] if l["id"] == g["landmark"]), "—")
        L.append(f"| `{g['id']}` | {g['faction_original_name']} | {g['faction_redesign_name']} | "
                 f"{nm(g['regions_3p'])} | {nm(g['regions_5p'])} | {lm} | {g['confidence']} |")
    L += ["", "Фракции оригинала без глифа на поле:", ""]
    for n in G["no_glyph"]:
        who = n["faction_redesign_name"] or "пары нет"
        L.append(f"- **{n['faction_original_name']}** ({who}) — {' '.join(n['rule'].split())}")

    SY = G.get("region_symbols", [])
    if SY:
        L += ["", "## Символы регионов", "",
              "Три знака, напечатанные на поле помимо стартовых глифов. В оригинале —",
              "три Spellbook Glyph фракции Yellow Sign; у нас — капля, пламя, вагонетка.",
              "Размещение повторяет оригинал один в один (`D-046`), источник — растр",
              "обеих сторон оригинального поля (`SRC-CW-MAP-SCAN`).", "",
              "| ID | Оригинал | Наш знак | Глиф | Иконка | Чтение | Материки | Доверие |",
              "|---|---|---|---|---|---|---|---|"]
        for s in SY:
            L.append(f"| `{s['id']}` | {s['original_name']} | {s['redesign_symbol']} | "
                     f"`{s['redesign_glyph']}` | `{s['icon_ref']}` | {s['resource_reading']} | "
                     f"{', '.join(s['landmasses'])} | {s['confidence']} |")
        L += ["", "| ID | Сторона «3» | Сторона «5» |", "|---|---|---|"]
        for s in SY:
            L.append(f"| `{s['id']}` | {nm(s['regions_3p'])} | {nm(s['regions_5p'])} |")
        L += ["", "Закон размещения: **символ идёт по материку**. Каждая область суши,",
              "кроме Антарктиды, несёт ровно один символ; шесть океанов и Антарктида —",
              "ни одного. Дети области стороны «5» наследуют символ родителя.", ""]
        L += ["| Конфигурация | " + " | ".join(f"{s['redesign_symbol']} `{s['redesign_glyph']}`"
                                               for s in SY) + " | Без символа |",
              "|---|" + "---|" * (len(SY) + 1)]
        for cfg in d["cfg"]["configs"]:
            g = all_g[cfg["id"]]
            c = g["region_symbol_counts"]
            L.append(f"| `{g['config']}` | " +
                     " | ".join(str(c.get(s["id"], 0)) for s in SY) +
                     f" | {len(g['areas_without_symbol'])} |")
        for cfg in d["cfg"]["configs"]:
            g = all_g[cfg["id"]]
            L += ["", f"### {g['config']} — символ в каждой области", "",
                  "| Область | Символ |", "|---|---|"]
            for v in g["vertices"]:
                sym = v["symbol"]
                L.append(f"| {v['name_en']} | " +
                         (f"{sym['symbol']} `{sym['glyph']}` ({sym['original_name']})"
                          if sym else "— *(без символа)*") + " |")

    L += ["", "## Стартовые области наших восьми фракций", "",
          "| Очередь | Фракция | По планшету | Сторона «3» | Сторона «5» | Глиф | Оригинал |",
          "|---|---|---|---|---|---|---|"]
    for s in sorted(G["start_areas_redesign"], key=lambda x: (x["queue"], x["name"])):
        L.append(f"| {s['queue']:g} | {s['name']} | {s['start_region_text']} | "
                 f"{nm(s['regions_3p'])} | {nm(s['regions_5p'])} | "
                 f"{'`'+s['glyph']+'`' if s['glyph'] else '—'} | `{s['baseline_ref']}` |")

    L += ["", "## Подписи-ориентиры на поле", "",
          "| ID | Подпись | Сторона «3» | Сторона «5» | Прочитано на | Глиф рядом | Доверие |",
          "|---|---|---|---|---|---|---|"]
    for l in G["landmarks"]:
        L.append(f"| `{l['id']}` | {l['label']} | {nm(l['regions_3p'])} | {nm(l['regions_5p'])} | "
                 f"{', '.join(l['observed_on']) or '—'} | "
                 f"{'`'+l['glyph_nearby']+'`' if l['glyph_nearby'] else '—'} | {l['confidence']} |")

    for cfg in d["cfg"]["configs"]:
        g = all_g[cfg["id"]]
        L += ["", f"### {g['config']} — где стоят глифы в этой раскладке", ""]
        for v, gs in sorted(g["start_glyphs"].items()):
            who = "; ".join(f"{x['faction_original']} / {x['faction_redesign']}" for x in gs)
            L.append(f"- **{R[v]['name_en']}** — {who}")

    for cfg in d["cfg"]["configs"]:
        g = all_g[cfg["id"]]
        L += ["", f"## {g['config']} — степени вершин", "",
              "| Область | Тип | Степень | Соседи |", "|---|---|---|---|"]
        for v in sorted(g["vertices"], key=lambda x: (-x["degree"], x["id"])):
            nb = ", ".join(R[n]["name_en"] for n in v["neighbours"])
            L.append(f"| {v['name_en']} | {v['type']} | {v['degree']} | {nb} |")
    L += ["", "## Открытые находки", "",
          "| ID | Тип | Уровень | Статус | Суть |", "|---|---|---|---|---|"]
    for f in d["findings"]:
        if f["status"] != "CLOSED":
            L.append(f"| `{f['id']}` | {f['type']} | {f['severity']} | {f['status']} | {f['title']} |")
    (OUT / "11-map.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("report: out/11-map.md")


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    d = load()
    if cmd == "check":
        sys.exit(0 if check(d) else 1)
    if cmd == "build":
        build(d)
        return
    if cmd == "verify":
        rows, ok = verify(d, build(d))
        sys.exit(0 if ok else 1)
    if cmd == "report":
        g = build(d)
        rows, ok = verify(d, g)
        report(d, g, rows, ok)
        return
    if cmd == "all":
        if not check(d):
            sys.exit(1)
        g = build(d)
        rows, ok = verify(d, g)
        report(d, g, rows, ok)
        sys.exit(0 if ok else 1)
    sys.exit("Команды: check | build | verify | report | all")


if __name__ == "__main__":
    main()
