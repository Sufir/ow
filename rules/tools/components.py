#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
components.py — валидация реестра компонентов и сборка отчёта.

registry/components.yaml — источник истины по физическим компонентам.
reports/16-components.md — производное: руками не правится, пересобирается отсюда.

Использование:
    python components.py check    # валидация: ID, словари, ссылки, дубли чисел
    python components.py report   # собрать reports/16-components.md
    python components.py all      # check + report

Главная проверка — дедупликация. Количества отрядов фракций живут только
в factions.yaml; если запись компонента несёт count_source: FACTIONS и при этом
собственное число, это дефект реестра, и скрипт падает.

Зависимость: PyYAML  ->  pip install pyyaml
"""

import datetime
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("Нужен PyYAML: pip install pyyaml")

ROOT = Path(__file__).resolve().parent.parent
REG = ROOT / "registry"
OUT = ROOT / "reports"
COMPONENTS = REG / "components.yaml"
FACTIONS = REG / "factions.yaml"
REPORT = OUT / "16-components.md"

SECTIONS = ("common", "faction", "variant", "not_taken")

ID_PATTERNS = {
    "common": re.compile(r"^COMP-C-\d{2}$"),
    "faction": re.compile(r"^COMP-F-\d{2}$"),
    "variant": re.compile(r"^COMP-V-\d{2}$"),
    "not_taken": re.compile(r"^COMP-N-\d{2}$"),
    "findings": re.compile(r"^COMP-I-\d{3}$"),
}

ENUMS = {
    "content": {"N/A", "TODO", "IN-REVIEW", "ISSUES", "VERIFIED"},
    "design": {"N/A", "NONE", "DRAFT", "IN-REVIEW", "APPROVED"},
    "production": {"N/A", "NONE", "READY", "PARTIAL", "DONE", "UNKNOWN"},
    "carrier": {"BOOK", "SHEET", "CARD", "TOKEN-CARDBOARD", "ACRYLIC",
                "MINIATURE", "PURCHASED", "BANNER", "NONE",
                "CARD + MINIATURE", "разный, см. by_faction"},
    "count_source": {"RULES", "FACTIONS", "FILE", "DERIVED", "DECISION",
                     "PURCHASE", "NONE"},
    "count_status": {"FIXED", "OPEN", "CONFLICT"},
    "finding_type": {"COUNT", "SPEC", "NAMING", "STATE", "SOURCE-GAP"},
    "severity": {"CRITICAL", "ERROR", "WARNING", "INFO"},
    "finding_status": {"OPEN", "AUTHOR-DECISION-REQUIRED", "DEFERRED",
                       "DECIDED", "CLOSED", "WONTFIX"},
}

# Состояние считается закрытым, если все три оси в этих множествах.
DONE = {
    "content": {"VERIFIED", "N/A"},
    "design": {"APPROVED", "N/A"},
    "production": {"DONE", "N/A"},
}
NOT_STARTED = {
    "content": {"TODO", "N/A"},
    "design": {"NONE", "N/A"},
    "production": {"NONE", "N/A"},
}


def load():
    comp = yaml.safe_load(COMPONENTS.read_text(encoding="utf-8"))
    fac = yaml.safe_load(FACTIONS.read_text(encoding="utf-8"))
    return comp, fac


def records(comp):
    """Все записи компонентов с указанием секции."""
    for section in SECTIONS:
        for item in comp.get(section) or []:
            yield section, item


def canon_factions(fac):
    return {f["id"]: f for f in fac.get("redesign") or []
            if f.get("status") == "CANON"}


# ─────────────────────────────── check ──────────────────────────────────────

def check(comp, fac):
    errors = []
    seen = {}
    factions = canon_factions(fac)

    def err(where, msg):
        errors.append(f"{where}: {msg}")

    for section, item in records(comp):
        cid = item.get("id")
        if not cid:
            err(section, "запись без id")
            continue
        if not ID_PATTERNS[section].match(cid):
            err(cid, f"id не соответствует шаблону секции {section}")
        if cid in seen:
            err(cid, f"id повторяется (секции {seen[cid]} и {section})")
        seen[cid] = section

        if section == "not_taken":
            if not item.get("reason"):
                err(cid, "в not_taken обязателен reason")
            continue

        # словари
        if item.get("carrier") not in ENUMS["carrier"]:
            err(cid, f"carrier вне словаря: {item.get('carrier')!r}")
        if item.get("count_source") not in ENUMS["count_source"]:
            err(cid, f"count_source вне словаря: {item.get('count_source')!r}")
        if item.get("count_status") not in ENUMS["count_status"]:
            err(cid, f"count_status вне словаря: {item.get('count_status')!r}")

        state = item.get("state") or {}
        for axis in ("content", "design", "production"):
            if state.get(axis) not in ENUMS[axis]:
                err(cid, f"state.{axis} вне словаря: {state.get(axis)!r}")

        # ГЛАВНОЕ ПРАВИЛО: числа фракций не дублируются
        if item.get("count_source") == "FACTIONS":
            if item.get("count") is not None:
                err(cid, "count_source: FACTIONS, но число записано здесь — "
                         "дубль источника истины")
            if item.get("count_per_faction") is not None:
                err(cid, "count_source: FACTIONS, но count_per_faction "
                         "записан здесь — дубль источника истины")
            if not item.get("count_ref"):
                err(cid, "count_source: FACTIONS требует count_ref")

        # OPEN-количество обязано иметь находку
        if item.get("count_status") == "OPEN" and not item.get("findings"):
            err(cid, "count_status: OPEN без записи в findings")

        # состояние обязано быть обосновано
        if not item.get("evidence"):
            err(cid, "пустой evidence — состояние ничем не подтверждено")

        # ссылки на фракции
        for fid, override in (item.get("by_faction") or {}).items():
            if fid not in factions:
                err(cid, f"by_faction ссылается на неизвестную фракцию {fid}")
            ostate = override.get("state") or {}
            for axis, value in ostate.items():
                if axis not in ENUMS or value not in ENUMS[axis]:
                    err(cid, f"by_faction[{fid}].state.{axis}: {value!r} вне словаря")
            if not override.get("reason"):
                err(cid, f"by_faction[{fid}] без reason")

        if item.get("per_faction") and section != "faction":
            err(cid, "per_faction вне секции faction")

    # пути обязаны существовать: реестр указывает на файлы, а не на намерения
    import glob
    project = ROOT.parent
    for section, item in records(comp):
        if section == "not_taken":
            continue
        refs = list(item.get("files") or [])
        if item.get("master"):
            refs.append(item["master"])
        for ov in (item.get("by_faction") or {}).values():
            refs += list(ov.get("files") or [])
        for rel in refs:
            full = str(project / rel)
            ok = bool(glob.glob(full)) if "*" in rel else (project / rel).exists()
            if not ok:
                err(item["id"], f"путь не найден: {rel}")

    # дедупликация в свободном тексте: числа фракций не пишутся словами
    FREE = ("notes", "evidence", "reason", "detail", "proposal", "decision",
            "title", "composition", "cost", "note")
    # цифры внутри идентификаторов (D-048, §2.4, 2026) числом не считаются
    QUEUE = re.compile(r"«Очередь»?[^.\n]{0,24}?(?<![-D§\d])\d")
    TIMES = re.compile(r"[×x]\s?\d")

    def scan_free(cid, obj):
        if isinstance(obj, dict):
            for k, v in obj.items():
                if k in FREE and isinstance(v, str):
                    if QUEUE.search(v):
                        err(cid, f"{k}: число «Очередь» записано текстом — "
                                 f"оно живёт в factions.yaml → meta.queue_scale")
                    if TIMES.search(v):
                        err(cid, f"{k}: количество вида ×N записано текстом — "
                                 f"состав фракции живёт в factions.yaml")
                else:
                    scan_free(cid, v)
        elif isinstance(obj, list):
            for x in obj:
                scan_free(cid, x)

    for section, item in records(comp):
        if section in ("faction", "not_taken"):
            scan_free(item.get("id", "?"), item)
    for f in comp.get("findings") or []:
        subj = f.get("subject")
        subj = subj if isinstance(subj, list) else [subj]
        if any(str(x).startswith("COMP-F-") for x in subj):
            scan_free(f.get("id", "?"), f)

    # находки
    finding_ids = set()
    for f in comp.get("findings") or []:
        fid = f.get("id", "")
        if not ID_PATTERNS["findings"].match(fid):
            err(fid or "?", "id находки не соответствует шаблону COMP-I-###")
        if fid in finding_ids:
            err(fid, "id находки повторяется")
        finding_ids.add(fid)
        if f.get("type") not in ENUMS["finding_type"]:
            err(fid, f"type вне словаря: {f.get('type')!r}")
        if f.get("severity") not in ENUMS["severity"]:
            err(fid, f"severity вне словаря: {f.get('severity')!r}")
        if f.get("status") not in ENUMS["finding_status"]:
            err(fid, f"status вне словаря: {f.get('status')!r}")
        # правило даты решения — как в issues.yaml
        if f.get("status") in ("DECIDED", "DEFERRED", "CLOSED"):
            if not f.get("decision"):
                err(fid, f"status {f['status']} требует decision")
            if not f.get("decided"):
                err(fid, f"status {f['status']} требует decided")
        elif f.get("decided"):
            err(fid, "decided проставлен при незавершённом статусе")
        subj = f.get("subject")
        for s in (subj if isinstance(subj, list) else [subj]):
            if s and s not in seen:
                err(fid, f"subject ссылается на неизвестную запись {s}")

    # обратные ссылки — в обе стороны
    back = {}
    for f in comp.get("findings") or []:
        subj = f.get("subject")
        for sid in (subj if isinstance(subj, list) else [subj]):
            if sid:
                back.setdefault(sid, set()).add(f["id"])
    for section, item in records(comp):
        cid = item.get("id", "?")
        listed = set(item.get("findings") or [])
        for ref in listed:
            if ref not in finding_ids:
                err(cid, f"findings: неизвестная находка {ref}")
        for ref in back.get(cid, set()) - listed:
            err(cid, f"находка {ref} указывает на эту запись, "
                     f"а в её findings не перечислена")

    return errors


# ────────────────────────────── report ──────────────────────────────────────

def resolve_faction_counts(item, factions):
    """Подставить количества из factions.yaml. Числа не хранятся в реестре."""
    ref = (item.get("count_ref") or "")
    out = {}
    for fid, f in factions.items():
        units = f.get("units") or []
        if "group = Пехотинцы и name = Рекрут" in ref:
            n = sum(u["stats"][0] for u in units if u.get("name") == "Рекрут")
        elif "name = Полковник" in ref:
            n = sum(u["stats"][0] for u in units if u.get("name") == "Полковник")
        elif "Боевые машины или Боевой мех" in ref:
            n = sum(u["stats"][0] for u in units
                    if u.get("group") in ("Боевые машины", "Боевой мех"))
        elif "group = Боевой робот" in ref:
            n = sum(u["stats"][0] for u in units
                    if u.get("group") == "Боевой робот")
        elif "extras" in ref:
            n = sum(e.get("count", 0) for e in (f.get("extras") or []))
        else:
            n = None
        out[fid] = n
    return out


def status_of(state):
    if all(state.get(a) in DONE[a] for a in DONE):
        return "ГОТОВО"
    if all(state.get(a) in NOT_STARTED[a] for a in NOT_STARTED):
        return "не начато"
    if state.get("production") == "UNKNOWN":
        return "не подтверждено"
    return "в работе"


RANK = {"не начато": 0, "в работе": 1, "не подтверждено": 2, "ГОТОВО": 3}


def effective_status(item):
    """Итог записи — худшее из состояния по умолчанию и отличий по фракциям."""
    states = [item.get("state") or {}]
    for o in (item.get("by_faction") or {}).values():
        if o.get("state"):
            states.append(o["state"])
    return min((status_of(s) for s in states), key=lambda s: RANK[s])


def total_count(item, factions):
    if item.get("count_source") == "FACTIONS":
        vals = resolve_faction_counts(item, factions)
        known = [v for v in vals.values() if v is not None]
        return str(sum(known)) if known else "—"
    if item.get("per_faction"):
        per = item.get("count_per_faction")
        if not per:
            return "—"
        k = len(factions)
        return f"{per}×{k} = {per * k}"
    c = item.get("count")
    return "—" if c is None else str(c)


def md_table(headers, rows):
    out = ["| " + " | ".join(headers) + " |",
           "|" + "|".join("---" for _ in headers) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(c).replace("\n", " ") for c in r) + " |")
    return "\n".join(out)


def report(comp, fac):
    factions = canon_factions(fac)
    lines = []
    A = lines.append

    A("# 16 — Реестр компонентов")
    A("")
    A(f"Собрано `rules/tools/components.py` "
      f"{datetime.date.today().isoformat()}. Руками не правится — "
      f"источник `rules/registry/components.yaml`.")
    A("")

    # счётчики
    all_items = [i for s, i in records(comp) if s != "not_taken"]
    by_status = {}
    for item in all_items:
        by_status.setdefault(effective_status(item), []).append(item)
    findings = comp.get("findings") or []
    open_findings = [f for f in findings if f.get("status") == "OPEN"]

    A("## Готовность")
    A("")
    A(md_table(
        ["Состояние", "Записей"],
        [[k, len(v)] for k, v in sorted(by_status.items())]
        + [["**Всего рабочих записей**", len(all_items)],
           ["Из оригинала не берём", len(comp.get("not_taken") or [])]]))
    A("")
    A(f"Находок по компонентам: {len(findings)}, из них открытых "
      f"{len(open_findings)}.")
    A("")

    # что ждёт подтверждения
    def has_unknown(i):
        states = [i.get("state") or {}]
        states += [o["state"] for o in (i.get("by_faction") or {}).values()
                   if o.get("state")]
        return any(s.get("production") == "UNKNOWN" for s in states)

    unknown = [i for i in all_items if has_unknown(i)]
    if unknown:
        A("## Требует подтверждения Alek")
        A("")
        A("Файл готов, факт изготовления не подтверждён. Состояние "
          "не достраивается догадкой. Записи с отличиями по фракциям "
          "могут числиться «в работе» по другой причине и всё равно "
          "стоять здесь.")
        A("")
        made = {"PURCHASED": "куплено / не куплено",
                "ACRYLIC": "нарезано / не нарезано",
                "MINIATURE": "есть / нет"}
        A(md_table(["ID", "Компонент", "Носитель", "Чем подтверждать"],
                   [[i["id"], i["name"], i.get("carrier"),
                     made.get(i.get("carrier"), "напечатано / не напечатано")]
                    for i in unknown]))
        A("")

    # блокирующее печать
    blockers = []
    for item in all_items:
        if item.get("blocks_print"):
            blockers.append((item["id"], item["name"], "вся запись"))
        for fid, ov in (item.get("by_faction") or {}).items():
            if ov.get("blocks_print"):
                blockers.append((item["id"],
                                 f"{item['name']} — {factions[fid]['name']}",
                                 (ov.get("reason") or "").strip().split("\n")[0]))
    if blockers:
        A("## Блокирует отправку комплекта в типографию")
        A("")
        A("Не книгу: её текст ни от одного компонента не зависит. Здесь "
          "тихие дефекты — те, что уедут в типографию незамеченными, потому "
          "что компонент выглядит готовым. «Ещё не сделано» сюда не попадает: "
          "это и так видно по осям состояния.")
        A("")
        A(md_table(["ID", "Компонент", "Почему"], blockers))
        A("")

    # разделы
    titles = {"common": "Общие компоненты",
              "faction": "Фракционные компоненты",
              "variant": "Компоненты вариантов игры"}
    for section in ("common", "faction", "variant"):
        items = comp.get(section) or []
        if not items:
            continue
        A(f"## {titles[section]}")
        A("")
        rows = []
        for item in items:
            st = item.get("state") or {}
            rows.append([
                item["id"], item["name"], total_count(item, factions),
                item.get("carrier"), st.get("content"), st.get("design"),
                st.get("production"), effective_status(item),
            ])
        A(md_table(["ID", "Компонент", "Кол-во", "Носитель",
                    "Текст", "Вёрстка", "Производство", "Итог"], rows))
        A("")

        # отличия по фракциям
        for item in items:
            ov = item.get("by_faction") or {}
            if not ov:
                continue
            A(f"### {item['id']} — отличия по фракциям")
            A("")
            rows = []
            for fid, o in ov.items():
                st = o.get("state") or item.get("state") or {}
                rows.append([factions[fid]["name"], status_of(st),
                             (o.get("reason") or "").strip().replace("\n", " ")])
            A(md_table(["Фракция", "Итог", "Почему отличается"], rows))
            A("")
            if item.get("count_source") == "FACTIONS":
                counts = resolve_faction_counts(item, factions)
                A("Количества подставлены из `factions.yaml`: "
                  + ", ".join(f"{factions[k]['name']} — {v}"
                              for k, v in counts.items() if v) + ".")
                A("")

    # количества фракционных компонентов целиком
    A("## Количества фракционных компонентов")
    A("")
    A("Числа не хранятся в этом реестре — подставлены из "
      "`rules/registry/factions.yaml` при сборке отчёта.")
    A("")
    fac_items = [i for i in (comp.get("faction") or [])
                 if i.get("count_source") == "FACTIONS"]
    headers = ["Фракция"] + [i["name"] for i in fac_items]
    rows = []
    for fid, f in factions.items():
        row = [f["name"]]
        for item in fac_items:
            v = resolve_faction_counts(item, factions)[fid]
            row.append("—" if not v else v)
        rows.append(row)
    A(md_table(headers, rows))
    A("")

    # не берём
    A("## Из оригинала не берём")
    A("")
    A(md_table(["ID", "Компонент оригинала", "Чем заменено", "Почему"],
               [[n["id"], n["original"], n.get("replaced_by") or "—",
                 (n.get("reason") or "").strip().replace("\n", " ")]
                for n in comp.get("not_taken") or []]))
    A("")

    # находки
    A("## Находки")
    A("")
    A(md_table(["ID", "Тип", "Важность", "Статус", "Предмет", "Суть"],
               [[f["id"], f["type"], f["severity"], f["status"],
                 ", ".join(f["subject"]) if isinstance(f.get("subject"), list)
                 else f.get("subject"),
                 f["title"]] for f in findings]))
    A("")
    if open_findings:
        A("### Открытые — ждут решения")
        A("")
        for f in open_findings:
            A(f"**{f['id']} — {f['title']}** ({f['severity']})")
            A("")
            A((f.get("detail") or "").strip())
            A("")
            A(f"*Предложение:* {(f.get('proposal') or '').strip()}")
            A("")

    A("---")
    A("")
    A("Источники истины, на которые ссылается этот реестр, перечислены "
      "в `components.yaml` → `meta.truth_map`. Ни одно число из них здесь "
      "не продублировано.")
    A("")

    REPORT.write_text("\n".join(lines), encoding="utf-8")
    return REPORT


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    if cmd not in ("check", "report", "all"):
        sys.exit(__doc__)

    comp, fac = load()

    if cmd in ("check", "all"):
        errors = check(comp, fac)
        if errors:
            print(f"ОШИБОК: {len(errors)}")
            for e in errors:
                print("  " + e)
            sys.exit(1)
        n = len(list(records(comp)))
        print(f"check: OK — {n} записей, "
              f"{len(comp.get('findings') or [])} находок")

    if cmd in ("report", "all"):
        path = report(comp, fac)
        print(f"report: {path.relative_to(ROOT.parent)}")


if __name__ == "__main__":
    main()
