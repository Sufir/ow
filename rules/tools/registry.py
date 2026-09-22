#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
registry.py — валидация реестров правил, сборка SQLite и генерация отчётов.

YAML в ../registry/ — источник истины. registry.db и отчёты в ../out/ — производные:
руками не правятся, пересобираются этим скриптом.

Использование:
    python registry.py check     # валидация YAML: ID, словари значений, ссылки
    python registry.py build     # пересобрать registry/registry.db из YAML
    python registry.py report    # сгенерировать отчёты в out/
    python registry.py all       # check + build + report

Зависимость: PyYAML  ->  pip install pyyaml
"""

import datetime
import json
import re
import shutil
import sqlite3
import sys
import tempfile
from collections import Counter
from pathlib import Path

try:
    import yaml
except ImportError:
    sys.exit("Нужен PyYAML: pip install pyyaml")

ROOT = Path(__file__).resolve().parent.parent
REG = ROOT / "registry"
OUT = ROOT / "reports"
DB = REG / "registry.db"

AREAS = {
    "SETUP", "ROUND", "ACTION", "MOVE", "COMBAT", "GATE", "POWER", "DOOM",
    "RITUAL", "TECH", "UNIT", "FACTION", "MAP", "VICTORY", "MODULE", "GLOSSARY",
}

ENUMS = {
    "confidence": {"HIGH", "MEDIUM", "LOW"},
    "baseline_status": {"VERIFIED", "PROVISIONAL", "GAP"},
    "match": {"EXACT", "RENAMED", "DEVIATION", "MISSING", "AMBIGUOUS",
              "CONTRADICTORY", "UNVERIFIED"},
    "issue_type": {"DEVIATION", "MISSING", "EXTRA", "AMBIGUITY", "TERMINOLOGY",
                   "ICON", "REFERENCE", "PLAYTHROUGH", "SOURCE-CONFLICT",
                   "NUMBER", "OUT-OF-SCOPE"},
    "category": {"NUMBER", "TIMING", "COST", "LIMIT", "TARGET", "CONDITION",
                 "EFFECT", "SEQUENCE", "EXCEPTION", "INTERACTION", "VICTORY",
                 "SETUP", "OTHER"},
    "severity": {"CRITICAL", "ERROR", "WARNING", "INFO"},
    "issue_status": {"OPEN", "AUTHOR-DECISION-REQUIRED", "DECIDED", "APPLIED",
                     "CLOSED", "WONTFIX"},
    "term_status": {"PROVISIONAL", "CANONICAL", "CONFLICT", "UNMAPPED"},
    "num_match": {"PASS", "FAIL", "UNKNOWN"},
    "icon_status": {"OK", "MISSING", "DUPLICATE", "UNMAPPED", "EMOJI-SUBSTITUTE"},
    "source_status": {"AVAILABLE", "REQUESTED", "UNREACHABLE", "PARTIAL"},
}

FILES = {
    "sources":  ("sources.yaml",  "sources"),
    "baseline": ("baseline.yaml", "baseline"),
    "redesign": ("redesign.yaml", "redesign"),
    "issues":   ("issues.yaml",   "issues"),
    "terms":    ("terms.yaml",    "terms"),
    "numbers":  ("numbers.yaml",  "numbers"),
    "icons":    ("icons.yaml",    "icons"),
}

SEVERITY_ORDER = ["CRITICAL", "ERROR", "WARNING", "INFO"]


def load():
    """Читает все реестры. Возвращает dict[str, list[dict]]."""
    data = {}
    for key, (fname, root_key) in FILES.items():
        path = REG / fname
        if not path.exists():
            data[key] = []
            continue
        raw = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        items = raw.get(root_key) or []
        if not isinstance(items, list):
            raise SystemExit(f"{fname}: ключ '{root_key}' должен быть списком")
        data[key] = items
    return data


def check(data):
    """Валидация. Возвращает (errors, warnings) — списки сообщений."""
    errors = []
    warnings = []
    seen = {}      # (реестр, id) -> True, уникальность внутри своего реестра
    owners = {}    # id -> [реестры], в которых он встретился

    def uid(reg, item, pattern):
        i = item.get("id")
        if not i:
            errors.append(f"{reg}: запись без id: {json.dumps(item, ensure_ascii=False)[:80]}")
            return
        if not re.fullmatch(pattern, i):
            errors.append(f"{reg}: id '{i}' не соответствует шаблону {pattern}")
        # Уникальность требуется внутри реестра. Между реестрами префиксы
        # TERM/ICON/SRC/NUM пересекаются по самой конвенции RULES-CHARTER §9:
        # один и тот же префикс обозначает и запись профильного реестра,
        # и issue соответствующего типа. Это не ошибка данных, но и молчать
        # об этом нельзя — идёт в предупреждения.
        if (reg, i) in seen:
            errors.append(f"{reg}: дубль id '{i}' внутри реестра")
        else:
            seen[(reg, i)] = True
        owners.setdefault(i, []).append(reg)

    def enum(reg, item, field, name, required=True):
        v = item.get(field)
        if v is None:
            if required:
                errors.append(f"{reg} {item.get('id')}: пустое поле '{field}'")
            return
        if v not in ENUMS[name]:
            errors.append(f"{reg} {item.get('id')}: {field}='{v}' вне словаря {sorted(ENUMS[name])}")

    def area(reg, item, required=True):
        v = item.get("area")
        if v is None and not required:
            return
        if v not in AREAS:
            errors.append(f"{reg} {item.get('id')}: area='{v}' вне словаря AREA")

    for it in data["sources"]:
        uid("sources", it, r"SRC-[A-Z0-9\-]+")
        enum("sources", it, "status", "source_status")

    for it in data["baseline"]:
        uid("baseline", it, r"BL-[A-Z]+-\d{3}")
        area("baseline", it)
        enum("baseline", it, "confidence", "confidence")
        enum("baseline", it, "status", "baseline_status")
        if not it.get("sources"):
            errors.append(f"baseline {it.get('id')}: нет ни одного источника")

    for it in data["redesign"]:
        uid("redesign", it, r"RD-[A-Z]+-\d{3}")
        area("redesign", it)
        enum("redesign", it, "match", "match")

    for it in data["issues"]:
        # TISS-### — issue типа TERMINOLOGY (D-028). Префикс TERM-### по уставу
        # §9 закреплён только за terms.yaml и в issues.yaml больше не встречается.
        # RED-### — находка red team (фаза P11). Тип PLAYTHROUGH, как у PLAY-###,
        # но заведена не проигрыванием партии, а поиском эксплойтов.
        uid("issues", it, r"(DEV|MISS|EXTRA|RULE|TISS|ICON|REF|PLAY|RED|SRC|NUM)-\d{3}")
        area("issues", it, required=False)
        enum("issues", it, "type", "issue_type")
        enum("issues", it, "severity", "severity")
        enum("issues", it, "status", "issue_status")
        for c in it.get("category") or []:
            if c not in ENUMS["category"]:
                errors.append(f"issues {it.get('id')}: category '{c}' вне словаря")
        if it.get("status") in ("DECIDED", "APPLIED", "CLOSED") and not it.get("decision_ref"):
            if it.get("severity") != "INFO":
                errors.append(f"issues {it.get('id')}: статус {it['status']} без decision_ref (D-###)")
        # Поле closed заполнено тогда и только тогда, когда issue завершён:
        # status CLOSED или WONTFIX (SCHEMA.md, раздел issues.yaml).
        # Дыра найдена приёмкой CODE-03 на DEV-005: дата закрытия стояла при
        # статусе DECIDED, проверка прошла молча, и счёт по статусам разошёлся
        # со сводкой в STATE.md. WONTFIX тогда попал в SCHEMA.md, но не в скрипт:
        # скрипт требовал дату только у CLOSED. Сведено к схеме в CODE-05.
        closed = it.get("closed")
        has_closed = closed not in (None, "")
        done = it.get("status") in ("CLOSED", "WONTFIX")
        if done and not has_closed:
            errors.append(f"issues {it.get('id')}: статус {it['status']} без даты в поле closed")
        if not done and has_closed:
            errors.append(
                f"issues {it.get('id')}: closed='{closed}' при статусе {it.get('status')} — "
                f"дата закрытия ставится только вместе со статусом CLOSED или WONTFIX"
            )

    for it in data["terms"]:
        uid("terms", it, r"TERM-\d{3}")
        enum("terms", it, "status", "term_status")

    for it in data["numbers"]:
        uid("numbers", it, r"NUM-\d{3}")
        enum("numbers", it, "match", "num_match")
        # UNKNOWN и FAIL обязаны быть объяснены: либо ссылкой на существующий
        # issue, либо строкой note. Новые идентификаторы issue при сплошной
        # сверке не выдумываются (ТЗ CODE-03), поэтому note равноправен.
        if it.get("match") in ("UNKNOWN", "FAIL") and not (it.get("issue") or it.get("note")):
            errors.append(
                f"numbers {it.get('id')}: match={it['match']} без issue и без note"
            )

    for it in data["icons"]:
        uid("icons", it, r"ICON-\d{3}")
        enum("icons", it, "status", "icon_status")

    # Один и тот же id в разных реестрах — не ошибка, но повод посмотреть
    for i, regs in sorted(owners.items()):
        if len(regs) > 1:
            warnings.append(
                f"id '{i}' встречается в нескольких реестрах: {', '.join(regs)}"
            )

    # Ссылочная целостность
    ids = {i for _, i in seen}
    def ref(reg, item, field, prefix):
        v = item.get(field)
        if v and v not in ids:
            errors.append(f"{reg} {item.get('id')}: {field}='{v}' — нет такой записи")
        if v and not v.startswith(prefix):
            errors.append(f"{reg} {item.get('id')}: {field}='{v}' — ожидался префикс {prefix}")

    for it in data["redesign"]:
        ref("redesign", it, "baseline_ref", "BL-")
    for it in data["issues"]:
        ref("issues", it, "baseline_ref", "BL-")
        ref("issues", it, "redesign_ref", "RD-")
    for it in data["numbers"]:
        ref("numbers", it, "baseline_ref", "BL-")
        ref("numbers", it, "redesign_ref", "RD-")
    for it in data["baseline"]:
        for s in it.get("sources") or []:
            r = s.get("ref") if isinstance(s, dict) else None
            if r and r not in ids:
                errors.append(f"baseline {it.get('id')}: источник '{r}' не найден в sources.yaml")

    # Дубли значений в icon registry
    for field in ("placeholder", "glyph"):
        vals = [i.get(field) for i in data["icons"] if i.get(field)]
        for v, n in Counter(vals).items():
            if n > 1:
                errors.append(f"icons: {field} '{v}' встречается {n} раз — нарушен принцип 1:1")

    return errors, warnings


def build(data):
    """Пересобирает SQLite из YAML."""
    # База всегда собирается во временном файле, а на место копируется байтами.
    # Причина: в песочнице Cowork каталог реестров — сетевое монтирование, где
    # sqlite не работает вовсе (unlink даёт "Operation not permitted", запись
    # в базу — "disk I/O error"), хотя обычная запись файла проходит.
    # Сборка во временном каталоге снимает оба ограничения и ничего не меняет
    # там, где монтирования нет.
    tmp_dir = tempfile.mkdtemp(prefix="registry-build-")
    tmp_db = Path(tmp_dir) / "registry.db"
    con = sqlite3.connect(tmp_db)
    cur = con.cursor()
    for table, items in data.items():
        cols = sorted({k for it in items for k in it}) or ["id"]
        cur.execute(
            "CREATE TABLE %s (%s)" % (table, ", ".join('"%s" TEXT' % c for c in cols))
        )
        for it in items:
            vals = []
            for c in cols:
                v = it.get(c)
                if v is None or isinstance(v, str):
                    vals.append(v)
                elif isinstance(v, (bool, int, float, datetime.date, datetime.time)):
                    # YAML разбирает даты и числа в объекты Python; в SQLite кладём
                    # их строковым представлением, а не JSON
                    vals.append(str(v))
                else:
                    vals.append(json.dumps(v, ensure_ascii=False))
            cur.execute(
                "INSERT INTO %s (%s) VALUES (%s)"
                % (table, ", ".join('"%s"' % c for c in cols), ", ".join("?" * len(cols))),
                vals,
            )
    con.commit()
    con.close()
    # Копируем байтами: перезапись существующего файла разрешена и там, где
    # запрещено его удаление.
    DB.write_bytes(tmp_db.read_bytes())
    shutil.rmtree(tmp_dir, ignore_errors=True)
    return DB


def md_table(headers, rows):
    out = ["| " + " | ".join(headers) + " |",
           "|" + "|".join(["---"] * len(headers)) + "|"]
    for r in rows:
        cells = [str(c).replace("\n", " ").replace("|", "\\|").strip() if c is not None else "—"
                 for c in r]
        out.append("| " + " | ".join(cells) + " |")
    return "\n".join(out)


def report(data):
    """Генерирует отчёты в out/."""
    OUT.mkdir(exist_ok=True)
    issues = data["issues"]
    written = []

    # 1. Executive summary
    by_sev = Counter(i.get("severity") for i in issues)
    by_type = Counter(i.get("type") for i in issues)
    by_status = Counter(i.get("status") for i in issues)
    lines = [
        "# Executive summary", "",
        f"- Записей в ORIGINAL BASELINE: **{len(data['baseline'])}**",
        f"- Записей в REDESIGN BASELINE: **{len(data['redesign'])}**",
        f"- Всего issue: **{len(issues)}**",
        f"- Проверено чисел: **{len(data['numbers'])}** "
        f"(FAIL: {sum(1 for n in data['numbers'] if n.get('match') == 'FAIL')}, "
        f"UNKNOWN: {sum(1 for n in data['numbers'] if n.get('match') == 'UNKNOWN')})",
        f"- Терминов в карте: **{len(data['terms'])}**",
        f"- Иконок в реестре: **{len(data['icons'])}**",
        "", "## По критичности", "",
        md_table(["Severity", "Кол-во"],
                 [[s, by_sev.get(s, 0)] for s in SEVERITY_ORDER]),
        "", "## По типу", "",
        md_table(["Тип", "Кол-во"], sorted(by_type.items())),
        "", "## По статусу", "",
        md_table(["Статус", "Кол-во"], sorted(by_status.items())),
    ]
    (OUT / "00-executive-summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    written.append("00-executive-summary.md")

    # 2. Deviation matrix
    dev = [i for i in issues if i.get("type") == "DEVIATION"]
    rows = [[i.get("id"), i.get("area"), i.get("original"), i.get("redesign"),
             i.get("difference"), i.get("severity"), i.get("status")] for i in dev]
    (OUT / "01-deviation-matrix.md").write_text(
        "# Mechanical deviation report\n\n" +
        (md_table(["ID", "Механика", "Оригинал", "Редизайн", "Разница", "Severity", "Статус"], rows)
         if rows else "_Расхождений не зафиксировано._") + "\n",
        encoding="utf-8")
    written.append("01-deviation-matrix.md")

    # 3. Требуют решения автора
    need = [i for i in issues if i.get("status") == "AUTHOR-DECISION-REQUIRED"]
    body = ["# Требуют решения автора", ""]
    if not need:
        body.append("_Открытых вопросов нет._")
    for i in sorted(need, key=lambda x: SEVERITY_ORDER.index(x.get("severity", "INFO"))):
        body += [
            f"## {i['id']} — {i.get('title')}  `{i.get('severity')}`  `{i.get('area')}`", "",
            f"- **Оригинал:** {i.get('original')}",
            f"- **Черновик:** {i.get('redesign')}",
            f"- **Разница:** {i.get('difference')}",
            f"- **Предложение:** {i.get('proposal')}",
            f"- **Confidence:** {i.get('confidence')}", "",
        ]
    (OUT / "02-author-decisions.md").write_text("\n".join(body) + "\n", encoding="utf-8")
    written.append("02-author-decisions.md")

    # 4. Полный issue log
    rows = [[i.get("id"), i.get("type"), i.get("area"), i.get("batch"),
             i.get("title"), i.get("severity"), i.get("status"), i.get("decision_ref")]
            for i in issues]
    (OUT / "03-issue-log.md").write_text(
        "# Полный issue log\n\n" +
        (md_table(["ID", "Тип", "Область", "Батч", "Суть", "Severity", "Статус", "Решение"], rows)
         if rows else "_Пусто._") + "\n", encoding="utf-8")
    written.append("03-issue-log.md")

    # 5. Numerical audit
    nums = data["numbers"]
    by_match = Counter(n.get("match") for n in nums)
    rows = [[n.get("id"), n.get("subject"), n.get("area"),
             n.get("original"), n.get("redesign"), n.get("unit"),
             n.get("match"), n.get("issue"), n.get("loc")] for n in nums]
    body = ["# Numerical audit", "",
            f"Проверено чисел: **{len(nums)}** — "
            f"PASS {by_match.get('PASS', 0)}, "
            f"FAIL {by_match.get('FAIL', 0)}, "
            f"UNKNOWN {by_match.get('UNKNOWN', 0)}.", "",
            md_table(["ID", "Показатель", "Область", "Оригинал", "Редизайн",
                      "Ед.", "Итог", "Issue", "Где в редизайне"], rows)
            if rows else "_Пусто._"]
    # Пояснения к несовпадениям выводим отдельно: в таблице они нечитаемы
    explained = [n for n in nums if n.get("note")]
    if explained:
        body += ["", "## Пояснения", ""]
        for n in explained:
            body.append(
                "- **%s** (%s) — %s"
                % (n.get("id"), n.get("match"),
                   " ".join(str(n["note"]).split()))
            )
    (OUT / "04-numerical-audit.md").write_text("\n".join(body) + "\n", encoding="utf-8")
    written.append("04-numerical-audit.md")

    # 6. Терминология
    rows = [[t.get("id"), t.get("original_en"), t.get("original_ru"), t.get("redesign"),
             "да" if t.get("semantic_equivalent") else "нет", t.get("status")]
            for t in data["terms"]]
    (OUT / "05-terminology.md").write_text(
        "# Original → Redesign terminology\n\n" +
        (md_table(["ID", "Оригинал (EN)", "Оригинал (RU)", "Редизайн", "Эквивалент", "Статус"], rows)
         if rows else "_Пусто._") + "\n", encoding="utf-8")
    written.append("05-terminology.md")

    # 7. Icon registry
    rows = [[i.get("id"), i.get("placeholder"), i.get("meaning"),
             i.get("original_concept"), i.get("status")] for i in data["icons"]]
    (OUT / "06-icon-registry.md").write_text(
        "# Icon registry\n\n" +
        (md_table(["ID", "Плейсхолдер", "Значение", "Оригинал", "Статус"], rows)
         if rows else "_Пусто._") + "\n", encoding="utf-8")
    written.append("06-icon-registry.md")

    # 8. Чего не хватает из источников
    miss = [s for s in data["sources"] if s.get("status") in ("REQUESTED", "UNREACHABLE", "PARTIAL")]
    rows = [[s.get("id"), s.get("kind"), s.get("title"), s.get("status"), s.get("need")]
            for s in miss]
    (OUT / "07-source-gaps.md").write_text(
        "# Недостающие источники\n\n" +
        (md_table(["ID", "Тип", "Название", "Статус", "Что нужно"], rows)
         if rows else "_Все источники на месте._") + "\n", encoding="utf-8")
    written.append("07-source-gaps.md")

    return written


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    data = load()

    failed = False

    if cmd in ("check", "all"):
        errs, warns = check(data)
        for w in warns:
            print("предупреждение:", w)
        if errs:
            print("ВАЛИДАЦИЯ НЕ ПРОШЛА (%d):" % len(errs))
            for e in errs:
                print("  -", e)
            if cmd == "check":
                sys.exit(1)
            # Для all валидация не обрывает работу: база и отчёты нужны и тогда,
            # когда в реестрах есть незакрытая ошибка, иначе один неверный
            # признак блокирует всю пересборку. Ненулевой код возврата
            # выставляется в конце.
            failed = True
        else:
            print("check: ок (%s)" % ", ".join("%s=%d" % (k, len(v)) for k, v in data.items()))

    if cmd in ("build", "all"):
        print("build:", build(data))

    if cmd in ("report", "all"):
        print("report:", ", ".join(report(data)))

    if cmd not in ("check", "build", "report", "all"):
        sys.exit(__doc__)

    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
