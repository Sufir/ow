#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_rulebook.py — сборка чистового RULEBOOK.md из двух черновиков.

Сборка идёт ПЕРЕНОСОМ: текст правил не переписывается. Скрипт делает ровно
четыре вещи:

  1. снимает служебные врезки «Статус черновика» из обоих файлов;
  2. снимает служебные шапки глоссария (свой заголовок H1, строка «Часть 13
     рулбука…») и ставит вместо них заголовок части «## 13. Глоссарий»;
  3. склеивает тело правил и глоссарий в один файл;
  4. переносит по словам две прозаические строки, вышедшие за 90 символов
     (чистая переверстка, ни одного слова не меняется).

Всё остальное копируется байт в байт. Проверка этого — `--verify`.

    python3 build_rulebook.py          # собрать ../out/RULEBOOK.md
    python3 build_rulebook.py --verify # собрать и доказать, что текст не изменён
"""

import re
import sys
import textwrap
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "reports"
SRC_BOOK = OUT / "rulebook-draft.md"
SRC_GLOS = OUT / "glossary-draft.md"
DST = ROOT / "RULEBOOK.md"

MAXLEN = 90
WRAP_TO = 80

GLOSSARY_HEAD = """## 13. Глоссарий

Алфавитный порядок, сорок девять статей.
"""


def strip_status_block(lines):
    """Убирает врезку «> **Статус черновика.** …» вместе с пустой строкой после."""
    out, i, removed = [], 0, 0
    while i < len(lines):
        if lines[i].startswith("> ") and "Статус черновика" in lines[i]:
            while i < len(lines) and (lines[i].startswith(">") or lines[i] == ">"):
                i += 1
                removed += 1
            while i < len(lines) and lines[i] == "":
                i += 1
            continue
        out.append(lines[i])
        i += 1
    return out, removed


def rewrap_long(lines):
    """Переносит по словам прозаические строки длиннее MAXLEN.

    Не трогает таблицы, заголовки, списки, цитаты и код: там перенос
    либо ломает разметку, либо невозможен.
    """
    out, touched = [], []
    for n, line in enumerate(lines, 1):
        if len(line) <= MAXLEN:
            out.append(line)
            continue
        s = line.lstrip()
        if s.startswith(("|", "#", ">", "`")) or re.match(r"^([-*+]|\d+\.)\s", s):
            out.append(line)
            continue
        wrapped = textwrap.wrap(
            line, width=WRAP_TO, break_long_words=False, break_on_hyphens=False
        )
        touched.append((n, len(line)))
        out.extend(wrapped)
    return out, touched


def norm_words(text):
    """Текст как последовательность слов — для доказательства, что он не изменён."""
    text = unicodedata.normalize("NFC", text)
    return re.split(r"\s+", text.strip())


def build():
    book = SRC_BOOK.read_text(encoding="utf-8").split("\n")
    glos = SRC_GLOS.read_text(encoding="utf-8").split("\n")

    book, b_removed = strip_status_block(book)
    glos, g_removed = strip_status_block(glos)

    # Служебные шапки глоссария: H1 файла и строка «Часть 13 рулбука…».
    assert glos[0].startswith("# "), glos[0]
    assert glos[2].startswith("Часть 13 рулбука"), glos[2]
    glos_body = glos[3:]
    while glos_body and glos_body[0] == "":
        glos_body.pop(0)

    while book and book[-1] == "":
        book.pop()
    while glos_body and glos_body[-1] == "":
        glos_body.pop()

    merged = book + ["", "---", ""] + GLOSSARY_HEAD.split("\n") + glos_body
    merged, touched = rewrap_long(merged)

    text = "\n".join(merged).rstrip("\n") + "\n"
    DST.write_text(text, encoding="utf-8")

    print(f"RULEBOOK.md собран: {len(merged)} строк, {len(text)} символов")
    print(f"  врезки «Статус черновика» сняты: {b_removed} строк в правилах, "
          f"{g_removed} в глоссарии")
    print(f"  переверстано длинных строк: {len(touched)} "
          f"{[f'исх.{n} ({ln} симв.)' for n, ln in touched]}")
    return text


def verify(text):
    """Слово в слово: чистовик = черновики минус снятое служебное."""
    book = strip_status_block(SRC_BOOK.read_text(encoding="utf-8").split("\n"))[0]
    glos = strip_status_block(SRC_GLOS.read_text(encoding="utf-8").split("\n"))[0]
    # заголовок части 13, поставленный вместо служебной шапки глоссария
    head = norm_words("---\n" + GLOSSARY_HEAD)
    expected = (norm_words("\n".join(book)) + head
                + norm_words("\n".join(glos[3:])))
    got = norm_words(text)
    ok = got == expected
    print(f"  слов в чистовике:                                  {len(got)}")
    print(f"  слов в черновиках + шапка части 13 ({len(head)} слова):    {len(expected)}")
    if not ok:
        n = min(len(got), len(expected))
        for i in range(n):
            if got[i] != expected[i]:
                print(f"  ПЕРВОЕ РАСХОЖДЕНИЕ на слове {i}: "
                      f"чистовик={got[i]!r} черновик={expected[i]!r}")
                print(f"  контекст чистовика:  {' '.join(got[i-8:i+8])}")
                print(f"  контекст черновика:  {' '.join(expected[i-8:i+8])}")
                break
        else:
            print(f"  хвост: чистовик {got[n:n+12]} / черновик {expected[n:n+12]}")
    print("VERIFY:", "OK — ни одного слова не потеряно и не изменено" if ok else "FAIL")
    return ok


if __name__ == "__main__":
    t = build()
    if "--verify" in sys.argv:
        sys.exit(0 if verify(t) else 1)
