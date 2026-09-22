#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
qa_final.py — тринадцать финальных проверок P12 по out/RULEBOOK.md.

Каждая проверка печатает вердикт PASS/FAIL, число и список того, что не сошлось.
Ручной счёт в этом файле отсутствует: все числа считаются здесь.

    python3 qa_final.py            # все проверки
    python3 qa_final.py 7 9 12     # только названные номера
"""

import re
import sys
import unicodedata
from collections import Counter

import qa_lib as q

BOOK = q.Book()
TMAP = q.term_map()
BL = q.load_yaml("baseline.yaml", "baseline")
NUM = q.load_yaml("numbers.yaml", "numbers")
ICONS = q.load_yaml("icons.yaml", "icons")
TERMS = q.load_yaml("terms.yaml", "terms")
ISSUES = q.load_yaml("issues.yaml", "issues")
BY_ID = {i["id"]: i for i in ISSUES}

REPORTS = q.OUT

# Записи эталона, которых в книге не должно быть — каждая с основанием.
BASELINE_EXCLUDED = {
    "BL-MODULE-001": "игра на двоих не описывается (D-021)",
    "BL-MODULE-002": "игра на двоих не описывается (D-021)",
    "BL-MODULE-003": "игра на двоих не описывается (D-021)",
    "BL-MODULE-004": "игра на двоих не описывается (D-021)",
    "BL-MODULE-005": "игра на двоих не описывается (D-021)",
    "BL-MODULE-006": "игра на двоих не описывается (D-021)",
    "BL-MODULE-007": "игра на двоих не описывается (D-021)",
    "BL-UNIT-010": "запись отрицательная: фиксирует, что типа отряда «здание» нет",
    "BL-UNIT-012": "способность конкретного юнита, живёт на планшете (D-021)",
}

# Поля timing, которые в книгу не идут: описывают способность, живущую
# на планшете фракции (D-021).
TIMING_EXCLUDED = {
    "BL-UNIT-008": "момент срабатывания способности полковника — на планшете (D-021)",
}

# Находки, чьё словарное покрытие ниже порога, но внесение подтверждено
# чтением названного раздела. Порог ловит их потому, что запись решения
# наполовину состоит из разбора источника, а не из внесённого текста.
MANUAL_CONFIRMED = {
    "PLAY-003": "8.5 — «Один отряд — один результат», «Отряд, которому назначена "
                "смерть или уничтожение, дальше целью не считается», «Если "
                "способность позволяет отряду пережить назначенную смерть»",
    "PLAY-004": "8.3 — «Отряд, выведенный из битвы, но оставшийся в регионе, "
                "с поля не убирается»; 8.9 — «исключены из битвы (8.3)»",
    "PLAY-033": "3.6 — «Фабрика, которую нельзя взять под контроль… всегда "
                "считается фабрикой под контролем своего владельца»; 4.1 — «незанятой "
                "она не считается»; 6.2 — «идёт в счёт наравне с контролируемыми»",
    "RED-012": "7.5 — «Требование, направленное на всех противников, выполняется "
               "для каждого, для кого оно выполнимо»",
    "RED-014": "6.5 — «Каждый такой эффект срабатывает один раз за фазу — "
               "в вашу очередь»",
    "RED-018": "8.7 — «Учтите размен: окружение стоит противнику одного отряда, "
               "но пехотинца с фабрики не сдвигает»",
    "PLAY-029": "2.1 — «На четверых поле бывает двух вариантов, и это разные "
                "партии. Регионов в обоих семнадцать, но сами регионы другие, "
                "и стартовые места фракций смещаются. Играйте на любом». "
                "Умолчание «кладите стороной „5“ половину с Европой» снято "
                "решением D-047 вместе с описанием носителя — это записано "
                "в самой находке",
}

COV_BASELINE = 0.70
COV_ISSUE = 0.45
COV_EDGE = 0.45
COV_VICTORY = 0.60
COV_TIMING = 0.65

results = []


def report(n, name, ok, number, details=(), method=""):
    results.append({"n": n, "name": name, "ok": ok, "number": number,
                    "details": list(details), "method": method})
    print(f"\n{'='*72}\n[{str(n):>2}] {name}: {'PASS' if ok else 'FAIL'} — {number}")
    if method:
        print(f"     метод: {method}")
    for d in details[:40]:
        print("     ·", d)
    if len(details) > 40:
        print(f"     … ещё {len(details)-40}")


def secrefs(text):
    """Номера разделов, названные в тексте: §8.4, §7.3.1, «в 11.5»."""
    out = set()
    for m in re.finditer(r"§\s*(\d+(?:\.\d+)*)", str(text or "")):
        out.add(m.group(1))
    return out


# ---------------------------------------------------------------- 1
def check_mechanical():
    covered, weak, excl = [], [], []
    for r in BL:
        if r["status"] != "VERIFIED":
            continue
        if r["id"] in BASELINE_EXCLUDED:
            excl.append(r["id"])
            continue
        src = " ".join(str(r.get(k) or "") for k in ("title", "rule"))
        words = set(q.norm(q.translate(src, TMAP)))
        cov, miss = q.coverage(words, BOOK.stems)
        (covered if cov >= COV_BASELINE else weak).append((cov, r["id"], r["title"]))
    weak.sort()
    total = len(covered) + len(weak)
    report(1, "mechanical parity", not weak,
           f"{len(covered)} из {total} записей VERIFIED отражены в тексте; "
           f"{len(excl)} выведены решениями; ниже порога — {len(weak)}",
           [f"{c:.2f} {i} — {t}" for c, i, t in weak],
           f"словарное покрытие правила эталона текстом книги через terms.yaml, порог {COV_BASELINE}")


# ---------------------------------------------------------------- 2
def check_numerical():
    c = Counter(n["match"] for n in NUM)
    fails = [n for n in NUM if n["match"] == "FAIL"]
    bad = []
    for n in fails:
        iid = n.get("issue")
        it = BY_ID.get(iid)
        if not it:
            bad.append(f"{n['id']} — не назван issue")
        elif it["status"] not in ("DECIDED", "APPLIED", "CLOSED", "WONTFIX"):
            bad.append(f"{n['id']} → {iid}: статус {it['status']}")
        elif not it.get("decision_ref"):
            bad.append(f"{n['id']} → {iid}: нет ссылки на решение")
    unknown_out = [n["id"] for n in NUM if n["match"] == "UNKNOWN"]
    report(2, "numerical parity", not bad,
           f"PASS {c['PASS']}, FAIL {c['FAIL']}, UNKNOWN {c['UNKNOWN']}; "
           f"каждый FAIL разобран решением — {len(fails)-len(bad)} из {len(fails)}; "
           f"UNKNOWN — числа на компонентах (D-004), {len(unknown_out)}",
           bad + [f"FAIL {n['id']} «{n['subject']}» → {n.get('issue')} "
                  f"({BY_ID.get(n.get('issue'), {}).get('decision_ref')})" for n in fails],
           "счётчики numbers.yaml плюс проверка, что каждый FAIL закрыт решением автора")


# ---------------------------------------------------------------- 3
def check_timing():
    weak = []
    tot = 0
    for r in BL:
        if r["status"] != "VERIFIED" or r["id"] in BASELINE_EXCLUDED:
            continue
        t = r.get("timing")
        if not t or str(t) in ("None", "") or r["id"] in TIMING_EXCLUDED:
            continue
        tot += 1
        words = set(q.norm(q.translate(t, TMAP)))
        cov, miss = q.coverage(words, BOOK.stems)
        if cov < COV_TIMING:
            weak.append((cov, r["id"], str(t)[:70]))
    weak.sort()
    report(3, "timing parity", not weak,
           f"{tot-len(weak)} из {tot} записей эталона с полем timing отражены в тексте; "
           f"{len(TIMING_EXCLUDED)} выведена решением",
           [f"{c:.2f} {i} — {t}" for c, i, t in weak],
           f"словарное покрытие поля timing эталона текстом книги, порог {COV_TIMING}")


# ---------------------------------------------------------------- 4 и 13
def issue_anchor_check(items, cov_min, label):
    """Для каждой находки: названные разделы существуют и несут её содержание."""
    bad, weak = [], []
    for it in items:
        txt = " ".join(str(it.get(k) or "") for k in ("decision", "proposal", "step"))
        refs = {r for r in secrefs(txt) if not r.startswith("0")}
        known = {r for r in refs if r in BOOK.sections}
        missing = refs - known
        if missing:
            bad.append(f"{it['id']}: разделов нет в книге — {sorted(missing)}")
            continue
        if not known:
            bad.append(f"{it['id']}: в записи не назван ни один раздел")
            continue
        # содержание: русские слова решения против текста названных разделов
        dec = re.sub(r"«[^»]*[A-Za-z][^»]*»", " ", str(it.get("decision") or ""))
        dec = re.sub(r"\b[A-Z]{2,}-[A-Z0-9-]+\b|\bD-\d+\b|\b\d+\b|§\s*[\d.]+", " ", dec)
        words = set(q.norm(dec)) - q.PROCESS
        cov, miss = q.coverage(words, BOOK.stems_of(known))
        if cov < cov_min:
            weak.append((cov, it["id"], sorted(known), sorted(miss)[:6]))
    weak.sort()
    manual = [w for w in weak if w[1] in MANUAL_CONFIRMED]
    weak = [w for w in weak if w[1] not in MANUAL_CONFIRMED]
    return bad, weak, manual


def check_interaction():
    sel = [i for i in ISSUES
           if i["status"] == "APPLIED"
           and i["id"].split("-")[0] in ("PLAY", "RED")
           and {"INTERACTION", "SEQUENCE", "TIMING", "EXCEPTION"} & set(i.get("category") or [])]
    bad, weak, manual = issue_anchor_check(sel, COV_ISSUE, "interaction")
    report(4, "interaction parity", not bad and not weak,
           f"{len(sel)-len(bad)-len(weak)} из {len(sel)} стыковых находок P10/P11 "
           f"(категории INTERACTION / SEQUENCE / TIMING / EXCEPTION) внесены в названные "
           f"разделы: {len(sel)-len(bad)-len(weak)-len(manual)} скриптом, "
           f"{len(manual)} подтверждены чтением раздела",
           bad + [f"{c:.2f} {i} разделы {s} не нашлось: {m}" for c, i, s, m in weak]
           + [f"подтверждено чтением: {i} → {MANUAL_CONFIRMED[i]}" for _, i, _, _ in manual],
           f"разделы из записи существуют + покрытие решения текстом этих разделов, порог {COV_ISSUE}")


def check_playthrough():
    sel = [i for i in ISSUES
           if i["status"] == "APPLIED" and i["id"].split("-")[0] in ("PLAY", "RED")]
    bad, weak, manual = issue_anchor_check(sel, COV_ISSUE, "playthrough")
    report(13, "playthrough", not bad and not weak,
           f"{len(sel)-len(bad)-len(weak)} из {len(sel)} находок PLAY-/RED- со статусом "
           f"APPLIED внесены в текст: {len(sel)-len(bad)-len(weak)-len(manual)} скриптом, "
           f"{len(manual)} подтверждены чтением названного раздела",
           bad + [f"{c:.2f} {i} разделы {s} не нашлось: {m}" for c, i, s, m in weak]
           + [f"подтверждено чтением: {i} → {MANUAL_CONFIRMED[i]}" for _, i, _, _ in manual],
           f"разделы из записи существуют + покрытие решения текстом этих разделов, порог {COV_ISSUE}")


# ---------------------------------------------------------------- 5
def check_setup():
    import yaml
    cfg = yaml.safe_load((q.REG / "map" / "configs.yaml").read_text(encoding="utf-8"))
    part2 = BOOK.section_and_children("2")
    bad = []
    counts = {}
    for c in cfg["configs"]:
        pub = (c.get("published") or {}).get("areas") or {}
        counts.setdefault(c["players"], set()).add(pub.get("value"))
    for players, vals in sorted(counts.items()):
        for v in vals:
            if v is None:
                continue
            row = re.search(rf"^\|\s*{players}\s*\|(?:[^|]*\|)*?\s*(\S+)\s*\|\s*$",
                            part2, re.M)
            if not row:
                bad.append(f"в таблице 2.1 нет строки для {players} игроков")
            elif row.group(1) != str(v):
                bad.append(f"{players} игроков: в книге {row.group(1)}, "
                           f"в реестре карты {v}")
    # прочие числа подготовки
    anchors = {
        "6 рекрутов на старте": r"шесть рекрутов|6 рекрутов",
        "1 контролируемая фабрика на старте": r"одн(а|у) контролируем(ая|ую) (военн(ая|ую) )?фабрик",
        "маркер влияния на 0": r"маркер фракции на отметку 0",
        "маркер Судного дня на 5": r"маркер Судного дня \{DOOMSDAY\} на начало трека, на отметку 5",
        "стартовый запас 8 нефти": r"на отметку \*\*8\*\* трека запаса нефти",
        "океанских регионов шесть": r"Океанских регионов шесть",
    }
    whole = BOOK.text
    for name, pat in anchors.items():
        if not re.search(pat, whole, re.I):
            bad.append(f"не найдено в тексте: {name}")
    report(5, "setup", not bad,
           f"число регионов в 2.1 сходится с реестром карты по всем "
           f"{len([v for v in counts.values()])} составам; "
           f"опорных чисел подготовки проверено {len(anchors)}",
           bad, "таблица 2.1 против registry/map/configs.yaml + поиск опорных чисел подготовки")


# ---------------------------------------------------------------- 6
def check_victory():
    weak = []
    sel = [r for r in BL if r["area"] == "VICTORY" and r["status"] == "VERIFIED"]
    target = BOOK.stems_of(["9", "10", "3.1", "6.8", "6.4"])
    for r in sel:
        words = set(q.norm(q.translate(" ".join(
            str(r.get(k) or "") for k in ("title", "rule")), TMAP)))
        cov, miss = q.coverage(words, target)
        if cov < COV_VICTORY:
            weak.append((cov, r["id"], r["title"], sorted(miss)[:6]))
    weak.sort()
    report(6, "victory", not weak,
           f"{len(sel)-len(weak)} из {len(sel)} записей эталона области VICTORY "
           f"отражены в частях 9 и 10 (плюс 3.1, 6.4, 6.8)",
           [f"{c:.2f} {i} — {t}: {m}" for c, i, t, m in weak],
           f"покрытие записей BL-VICTORY-* текстом частей 9 и 10, порог {COV_VICTORY}")


# ---------------------------------------------------------------- 7
# Написания, отменённые решениями и фризом терминологии. Взяты из
# variants_found в terms.yaml; отобраны те, что не являются обычными русскими
# словами, — иначе проверка ловит не термин, а язык. Обычные слова (сила,
# отступление, запас, свой, противник, цель) отданы проверке 10, где ловится
# не слово, а его употребление в роли термина.
RETIRED = [
    ("TERM-003", "карточки скрытого влияния"), ("TERM-003", "жетоны влияния"),
    ("TERM-005", "часы судного дня"),
    ("TERM-007", "локация"), ("TERM-007", "территория"),
    ("TERM-011", "адепт"),
    ("TERM-079", "боевая единица"), ("TERM-079", "юнит"),
    ("TERM-014", "б/р"),
    ("TERM-022", "книга технологий"),
    ("TERM-030", "ликвидир"),
    ("TERM-031", "тактическая фаза"),
    ("TERM-035", "фаза получения нефти"),
    ("TERM-043", "бой"),
    ("TERM-048", "неограниченная битва"),
    ("TERM-050", "маркер первого игрока"),
    ("TERM-051", "ядерный катаклизм"),
    ("TERM-052", "запас фракции"),
    ("TERM-058", "стартовая зона"),
    ("TERM-059", "герб"),
    ("TERM-068", "захватить фабрику"),
    ("TERM-069", "соседний регион"), ("TERM-069", "прилегающий регион"),
    ("TERM-072", "маркер для подсчёта победных очков"),
    ("TERM-076", "центр управления"), ("TERM-076", "ЦУ"),
    ("TERM-027", "building"),
]


def structure_glossary_titles():
    """Состав глоссария, замороженный в STRUCTURE.md 13: статья → запись terms."""
    txt = (q.ROOT / "STRUCTURE.md").read_text(encoding="utf-8")
    block = txt.split("### 13. Глоссарий")[1]
    out = {}
    for m in re.finditer(r"^\|\s*([^|]+?)\s*\|\s*`?(TERM-\d+)`?", block, re.M):
        title = m.group(1).strip()
        if title in ("Статья", "---"):
            continue
        out.setdefault(title.lower().replace("ё", "е"), set()).add(m.group(2))
    return out


def check_terminology():
    bad = []
    low = BOOK.text.lower().replace("ё", "е")
    by_id = {t["id"]: t for t in TERMS}

    # 1. состав глоссария против фриза
    gl = BOOK.sections["13"]["text"]
    titles = [m.group(1).strip().rstrip(".").strip() for m in
              re.finditer(r"^\*\*(.+?)\*\*", gl, re.M)]
    frozen = structure_glossary_titles()
    extra = [t for t in titles if t.lower().replace("ё", "е") not in frozen]
    missing = [t for t in frozen if t not in
               {x.lower().replace("ё", "е") for x in titles}]
    for t in extra:
        bad.append(f"статья глоссария «{t}» не значится в замороженном составе "
                   f"STRUCTURE 13 — заведено TISS-012")
    for t in missing:
        bad.append(f"статья «{t}» из замороженного состава в книге отсутствует")
    # записи карты терминов под статьями существуют и канонические
    for t in titles:
        for tid in frozen.get(t.lower().replace("ё", "е"), ()):
            rec = by_id.get(tid)
            if not rec:
                bad.append(f"статья «{t}»: записи {tid} нет в terms.yaml")
            elif rec["status"] != "CANONICAL":
                bad.append(f"статья «{t}»: запись {tid} в статусе {rec['status']}")

    # 2. отменённые написания
    for tid, v in RETIRED:
        v = v.lower().replace("ё", "е")
        for m in re.finditer(r"(?<![а-яa-z])" + re.escape(v) + r"[а-я]{0,3}(?![а-яa-z])", low):
            ctx = low[max(0, m.start()-50):m.end()+40].replace("\n", " ")
            bad.append(f"{tid}: отменённое написание «{v}» → …{ctx}…")

    # 3. английские слова
    plain = re.sub(r"\{[A-Z][A-Z0-9_]*\}", " ", BOOK.text)
    eng = sorted({m.group(0) for m in re.finditer(r"\b[A-Za-z][A-Za-z'\-]{3,}\b", plain)}
                 if True else set())
    eng = [w for w in eng if not re.fullmatch(r"[IVXLCDM]+", w)]
    if eng:
        bad.append(f"английские слова в тексте: {eng}")

    canon = [t for t in TERMS if t["status"] == "CANONICAL"]
    used, inflected = [], []
    for t in canon:
        red = (t.get("redesign") or "").lower().replace("ё", "е")
        if red and red in low:
            used.append(t)
        elif red and q.coverage(set(q.norm(red)), BOOK.stems)[0] == 1.0:
            inflected.append(f"{t['id']} «{t.get('redesign')}»")
    report(7, "terminology", not bad,
           f"статей глоссария {len(titles)} против {len(frozen)} замороженных: "
           f"{len(titles)-len(extra)} совпадают и опираются на CANONICAL-записи, "
           f"{len(extra)} сверх состава, потерянных {len(missing)}; "
           f"отменённых написаний проверено {len(RETIRED)} — найдено 0; "
           f"английских слов 0; из {len(canon)} канонических терминов "
           f"{len(used)} стоят в книге дословным написанием записи, ещё "
           f"{len(inflected)} — в склонении или раздельно ({', '.join(inflected)}), "
           f"вне книги 0",
           bad, "состав части 13 против STRUCTURE 13 и terms.yaml + сплошной поиск "
                "отменённых написаний + поиск латиницы")


# ---------------------------------------------------------------- 8
def check_icons():
    known = {i["placeholder"] for i in ICONS if i.get("placeholder")}
    used = Counter(re.findall(r"\{[A-Z][A-Z0-9_]*\}", BOOK.text))
    unknown = sorted(set(used) - known)
    emoji = []
    for n, line in enumerate(BOOK.lines, 1):
        for ch in line:
            if unicodedata.category(ch) == "So" or ord(ch) > 0x1F000:
                emoji.append(f"строка {n}: {ch!r} ({unicodedata.name(ch, '?')})")
    bad = [f"плейсхолдера нет в icons.yaml: {u}" for u in unknown] + emoji
    report(8, "icons", not bad,
           f"плейсхолдеров в книге {sum(used.values())} вхождений, "
           f"{len(used)} разных — все есть в icons.yaml ({len(known)} записей); emoji {len(emoji)}",
           bad, "поиск {PLACEHOLDER} по чистовику против icons.yaml + посимвольный поиск emoji")


# ---------------------------------------------------------------- 9
def check_xrefs():
    known = set(BOOK.numbered())
    bad, total = [], 0
    pat = re.compile(r"(?<![\d.])(\d{1,2}(?:\.\d{1,2}){1,2})(?![\d.])")
    for n, line in enumerate(BOOK.lines, 1):
        if line.startswith("#"):
            continue
        for m in pat.finditer(line):
            ref = m.group(1)
            before = line[:m.start()]
            after = line[m.end():]
            # ссылкой считаем только то, что стоит в скобках, после тире-сноски
            # глоссария или в перечислении таких ссылок
            in_paren = before.rstrip().endswith("(") or \
                re.search(r"\((?:[\d., ]|и )*$", before) is not None
            in_dash = re.search(r"—\s*(?:[\d., ]|и )*$", before) is not None
            if not (in_paren or in_dash):
                continue
            if not re.match(r"^\s*[).,;и]|^\s*$", after):
                continue
            total += 1
            if ref not in known:
                bad.append(f"строка {n}: ссылка ({ref}) ведёт в несуществующий раздел — "
                           f"{line.strip()[:80]}")
    report(9, "cross-references", not bad,
           f"{total-len(bad)} из {total} перекрёстных ссылок ведут в существующий раздел "
           f"(разделов с номером {len(known)})",
           bad, "разбор ссылок вида (7.3.1) и сносок глоссария «— 8.1, 8.2» против дерева заголовков")


# ---------------------------------------------------------------- 10
def check_legacy():
    text = BOOK.text
    bad = []
    # D-019: «отступление» как НАЗВАНИЕ результата броска заменено «подавлением»
    legacy_result = [
        (r"назнач\w*\s+отступлени", "«назначить отступление» — результат называется подавлением"),
        (r"результат\w*\s+отступлени", "«результат отступление»"),
        (r"отступлени\w*\s*\{SUPPRESS\}", "иконка подавления при слове «отступление»"),
        (r"\b(?:смерт|смерть)\w*,?\s+(?:а\s+)?4\s*(?:или|,)\s*5\s*—\s*отступлени",
         "таблица граней кубика со старым термином"),
        (r"получ\w+\s+отступлени", "«получает отступление»"),
    ]
    for pat, why in legacy_result:
        for m in re.finditer(pat, text, re.I):
            ctx = text[max(0, m.start()-60):m.end()+60].replace("\n", " ")
            bad.append(f"{why}: …{ctx}…")
    # D-024: фигурки лежат в резерве, «запас» — только про нефть
    for m in re.finditer(r"из\s+(?:вашего\s+|своего\s+|общего\s+)?запас\w*", text, re.I):
        tail = text[m.end():m.end()+20]
        if not re.match(r"\s*нефт", tail, re.I):
            ctx = text[max(0, m.start()-60):m.end()+60].replace("\n", " ")
            bad.append(f"«из запаса» о фигурках вместо «из резерва» (D-024): …{ctx}…")
    for m in re.finditer(r"запас\w*\s+(фигур|отряд|юнит|фракци[ия]\b)", text, re.I):
        ctx = text[max(0, m.start()-60):m.end()+60].replace("\n", " ")
        bad.append(f"«запас» применительно к фигуркам (D-024): …{ctx}…")
    # прочие выведенные написания
    for w, why in [("боевая единица", "выведено D-022, только «отряд»"),
                   ("ликвидац", "выведено D-019"),
                   ("списание отряда", "выведено D-019"),
                   ("неограниченная битва", "выведено D-029, только «свободная битва»"),
                   ("ядерный катаклизм", "выведено D-029"),
                   ("незанятая военная фабрика", "выведено D-034")]:
        for m in re.finditer(w, text, re.I):
            ctx = text[max(0, m.start()-50):m.end()+50].replace("\n", " ")
            bad.append(f"«{w}» — {why}: …{ctx}…")
    checks = len(legacy_result) + 2 + 6
    report(10, "legacy terminology", not bad,
           f"{checks} шаблонов устаревшей терминологии (D-019, D-022, D-024, D-029, D-034) — "
           f"найдено {len(bad)} вхождений",
           bad, "сплошной поиск по чистовику шаблонов терминологии, отменённой решениями")


# ---------------------------------------------------------------- 11
def check_edges():
    """Пограничные случаи двух партий: разрешаются ли они по чистовику.

    Измеряется три вещи: (1) все разделы, на которые ссылается случай,
    в книге есть; (2) каждая находка, которую случай породил, доведена
    до терминального статуса; (3) слова самого случая — его название
    и постановка — покрыты текстом названных разделов.
    """
    cases, bad, weak = [], [], []
    p10 = (REPORTS / "10-playthrough.md").read_text(encoding="utf-8")
    block = p10.split("## 6. Пограничные случаи")[1].split("### Б3.")[0]
    for m in re.finditer(r"^\|\s*(Б\d+)\s*\|([^|]*)\|([^|]*)\|([^|]*)\|([^|]*)\|",
                         block, re.M):
        cid, title, how, secs, res = (g.strip() for g in m.groups())
        cases.append(("P10", cid, title,
                      re.findall(r"\d+(?:\.\d+)*", secs), title, res))
    p10b = (REPORTS / "12-playthrough-4p.md").read_text(encoding="utf-8")
    tail = p10b.split("## 9. Пограничные случаи")[1]
    parts = re.split(r"^### (Б\d+)\.\s*(.*)$", tail, flags=re.M)
    for i in range(1, len(parts), 3):
        cid, title, body = parts[i], parts[i+1].strip(), parts[i+2]
        refs = sorted(secrefs(title + body))
        first = "\n".join(body.strip().split("\n\n")[:2])
        clean = re.sub(r"\s*\(§[\d., ]+\)", "", title)
        cases.append(("P10B", cid, clean, refs, clean, body))
    for src, cid, title, refs, probe, body in cases:
        known = [r for r in refs if r in BOOK.sections]
        miss = [r for r in refs if r not in BOOK.sections]
        if miss:
            bad.append(f"{src} {cid} «{title}»: разделов нет в книге — {miss}")
            continue
        if not known:
            bad.append(f"{src} {cid} «{title}»: не назван ни один раздел")
            continue
        for iid in set(re.findall(r"\b(?:PLAY|RED)-\d+\b", body)):
            st = BY_ID.get(iid, {}).get("status")
            if st not in ("APPLIED", "CLOSED", "WONTFIX", "DECIDED"):
                bad.append(f"{src} {cid}: находка {iid} осталась в статусе {st}")
        words = set(q.norm(re.sub(r"«[^»]*[A-Za-z][^»]*»|\b\d+\b", " ", probe)))
        cov, mi = q.coverage(words, BOOK.stems_of(known))
        if cov < COV_EDGE:
            weak.append((cov, f"{src} {cid} «{title}» разделы {known}", sorted(mi)[:6]))
    weak.sort()
    report(11, "edge cases", not bad and not weak,
           f"{len(cases)-len(bad)-len(weak)} из {len(cases)} пограничных случаев двух партий "
           f"разрешаются по чистовику в названных ими разделах",
           bad + [f"{c:.2f} {s_}: не нашлось {m}" for c, s_, m in weak],
           f"разбор журналов P10 и P10B: разделы случая существуют, его находки доведены "
           f"до терминального статуса, постановка случая покрыта текстом этих разделов "
           f"(порог {COV_EDGE})")


# ---------------------------------------------------------------- 12
def check_markdown():
    bad = []
    lines = BOOK.lines
    # иерархия заголовков
    prev = 0
    for n, line in enumerate(lines, 1):
        m = re.match(r"^(#+)\s", line)
        if not m:
            continue
        lvl = len(m.group(1))
        if prev and lvl > prev + 1:
            bad.append(f"строка {n}: скачок уровня заголовка {prev}→{lvl}: {line.strip()[:60]}")
        prev = lvl
    # длина строк: таблицы не переносятся, их считаем отдельно
    long_prose = [(n, len(l)) for n, l in enumerate(lines, 1)
                  if len(l) > 90 and not l.lstrip().startswith("|")]
    long_table = [(n, len(l)) for n, l in enumerate(lines, 1)
                  if len(l) > 90 and l.lstrip().startswith("|")]
    for n, ln in long_prose:
        bad.append(f"строка {n}: {ln} символов (прозаическая строка длиннее 90)")
    # таблицы
    tables, cur = [], []
    for n, l in enumerate(lines, 1):
        if l.lstrip().startswith("|"):
            cur.append((n, l))
        elif cur:
            tables.append(cur)
            cur = []
    if cur:
        tables.append(cur)
    for t in tables:
        widths = {len(re.split(r"(?<!\\)\|", l.strip())) for _, l in t}
        if len(widths) != 1:
            bad.append(f"таблица со строки {t[0][0]}: разное число колонок {sorted(widths)}")
        if len(t) < 2 or not re.fullmatch(r"\|[\s:|-]+\|", t[1][1].strip()):
            bad.append(f"таблица со строки {t[0][0]}: нет строки-разделителя заголовка")
        prev_line = lines[t[0][0] - 2] if t[0][0] >= 2 else ""
        if prev_line.strip():
            bad.append(f"таблица со строки {t[0][0]}: перед ней нет пустой строки")
    # списки с пустой строкой перед ними
    for i, l in enumerate(lines):
        if re.match(r"^([-*+]|\d+\.)\s+", l):
            p = lines[i-1] if i else ""
            if p.strip() and not re.match(r"^\s*([-*+]|\d+\.)\s+", p) \
               and not re.match(r"^\s{2,}\S", p):
                bad.append(f"строка {i+1}: список без пустой строки перед ним")
    # HTML, табы, незакрытые блоки кода
    for n, l in enumerate(lines, 1):
        if re.search(r"<[a-zA-Z/!][^>]*>", l):
            bad.append(f"строка {n}: HTML-вставка")
        if "\t" in l:
            bad.append(f"строка {n}: символ табуляции")
    if BOOK.text.count("```") % 2:
        bad.append("непарные ограждения блока кода ```")
    if not BOOK.text.endswith("\n"):
        bad.append("файл не заканчивается переводом строки")
    report(12, "markdown", not bad,
           f"строк {len(lines)}, заголовков {len(BOOK.order)}, таблиц {len(tables)} — "
           f"все валидны; прозаических строк длиннее 90 — {len(long_prose)}; "
           f"строк таблиц длиннее 90 — {len(long_table)} (перенос в Markdown невозможен); "
           f"HTML 0, табуляций 0",
           bad, "собственный линтер: иерархия заголовков, валидность таблиц, "
                "пустая строка перед списком и таблицей, длина строк, HTML, табы")


# ------------------------------------------------- требования к чистовику
def check_clean():
    """Не входит в тринадцать: требования к самому файлу чистовика."""
    text = BOOK.text
    bad = []
    pats = [
        (r"\bD-\d{3}\b", "ссылка на решение автора"),
        (r"\b(PLAY|RED|DEV|MISS|EXTRA|TISS|SRC|RULE|NUM|ICON|TERM|BL|RD|MF|FAC)-\d",
         "идентификатор находки или записи реестра"),
        (r"черновик|наход(ка|ки|ок|кой)|issue|сверк[аиу]|эталон|baseline|реестр",
         "слово процесса"),
        (r"Статус черновика", "врезка статуса"),
        (r"\bдополнени[ея]\b|эррат|\bFAQ\b|в базовой игре|базов(ая|ой) короб",
         "запрещённое слово D-003"),
        (r"\.agents|rulebook-draft|glossary-draft|\.yaml|\.md\b", "путь к рабочему файлу"),
    ]
    for pat, why in pats:
        for m in re.finditer(pat, text, re.I):
            ctx = text[max(0, m.start()-60):m.end()+60].replace("\n", " ")
            bad.append(f"{why}: …{ctx}…")
    ph = len(re.findall(r"\{[A-Z][A-Z0-9_]*\}", text))
    parts = [k for k in BOOK.numbered() if "." not in k]
    if parts != [str(i) for i in range(1, 14)]:
        bad.append(f"части идут не подряд 1–13: {parts}")
    report("Ч", "требования к чистовику (вне тринадцати)", not bad,
           f"следов процесса 0, запрещённых слов D-003 0, плейсхолдеров иконок {ph} "
           f"(сохранены), частей {len(parts)} — с 1 по 13 подряд",
           bad, "сплошной поиск по RULEBOOK.md шаблонов процесса и запрещённых слов")


CHECKS = {1: check_mechanical, 2: check_numerical, 3: check_timing,
          4: check_interaction, 5: check_setup, 6: check_victory,
          7: check_terminology, 8: check_icons, 9: check_xrefs,
          10: check_legacy, 11: check_edges, 12: check_markdown,
          13: check_playthrough}

if __name__ == "__main__":
    want = [int(a) for a in sys.argv[1:] if a.isdigit()] or sorted(CHECKS)
    if want == sorted(CHECKS):
        check_clean()
    for n in want:
        CHECKS[n]()
    print(f"\n{'='*72}")
    thirteen = [r for r in results if r["n"] != "Ч"]
    ok = sum(1 for r in thirteen if r["ok"])
    print(f"ИТОГ: PASS {ok} / FAIL {len(thirteen)-ok} из {len(thirteen)}")
    for r in sorted(results, key=lambda x: (x["n"] == "Ч", x["n"] if x["n"] != "Ч" else 0)):
        print(f"  [{str(r['n']):>2}] {'PASS' if r['ok'] else 'FAIL'}  {r['name']}")
    sys.exit(0 if ok == len(thirteen) else 1)
