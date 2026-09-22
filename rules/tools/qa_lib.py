#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
qa_lib.py — общая часть финальных QA-проверок P12.

Здесь лежит то, чем пользуются все проверки: разбор чистовика на разделы,
нормализация русского текста, карта терминов «оригинал → редизайн» и мера
покрытия «набор слов правила против текста раздела».

Мера покрытия. Правило эталона и текст книги написаны разными словами:
эталон — по-русски с английскими терминами оригинала, книга — нашей
терминологией. Поэтому слова правила сначала прогоняются через terms.yaml
(original_en и original_ru → redesign), потом режутся до основы (первые
5 букв — грубая замена стемминга, которой хватает для русских окончаний),
и только потом считается доля слов правила, найденных в тексте.
"""

import re
import unicodedata
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
REG = ROOT / "registry"
OUT = ROOT / "reports"
BOOK = OUT / "RULEBOOK.md"

STEM = 5

PROCESS = {w[:STEM] for w in """
внесено внесена внесены внесён находка находки находку находкой решение решения
решено автор автора авторское alek сверено сверка сверке оригинал оригинала
оригинале источник источника источники редакция редакции правка правки правку
абзац абзаца абзацем запись записи реестр реестра эталон эталона эталоне
черновик черновика цитата дословно подтверждено подтвердилось снято снята
заведено заведена переписан переписана переписано дописано дописан дописана
добавлен добавлено добавлена выведено прежний прежняя прежнее батч батча
формулировка формулировке формулировку поиск поиском отчёт отчёта отчёте
""".split()}

STOP = set("""
и в во не что он на я с со как а то все она так его но да ты к у же вы за бы
по только ее мне было вот от меня еще нет о из ему теперь когда даже ну вдруг
ли если уже или ни быть был него до вас нибудь опять уж вам ведь там потом
себя ничего ей может они тут где есть надо ней для мы тебя их чем была сам
чтоб без будто чего раз тоже себе под будет ж тогда кто этот того потому этого
какой совсем ним здесь этом один почти мой тем чтобы нее сейчас были куда зачем
всех никогда можно при наконец два об другой хоть после над больше тот через
эти нас про всего них какая много разве три эту моя впрочем хорошо свою этой
перед иногда лучше чуть том нельзя такой им более всегда конечно всю между
это её его них том том the and for with that this are not you your его
""".split())


def norm(text):
    """Строка → список основ значимых слов."""
    text = unicodedata.normalize("NFC", str(text or "")).lower().replace("ё", "е")
    words = re.findall(r"[а-я]{3,}|\{[A-Z_]+\}|\d+[.,]?\d*", text)
    return [w[:STEM] if w[0].isalpha() else w for w in words if w not in STOP]


def load_yaml(name, key):
    return yaml.safe_load((REG / name).read_text(encoding="utf-8"))[key]


def term_map():
    """original_en / original_ru → redesign, нижним регистром, по словам."""
    m = {}
    for t in load_yaml("terms.yaml", "terms"):
        red = t.get("redesign")
        if not red:
            continue
        for src in (t.get("original_en"), t.get("original_ru")):
            if not src:
                continue
            m[str(src).lower()] = str(red).lower()
    return m


def translate(text, tmap):
    """Меняет термины оригинала на наши до нормализации.

    Замена только по границам слов: без этого «рок» внутри «игрок»
    превращался во «влияние» и портил измерение.
    """
    s = unicodedata.normalize("NFC", str(text or "")).lower()
    for src in sorted(tmap, key=len, reverse=True):
        s = re.sub(r"(?<![\w])" + re.escape(src) + r"(?![\w])", tmap[src], s)
    return s


class Book:
    """Чистовик, разобранный на разделы по заголовкам."""

    HEAD = re.compile(r"^(#{2,4})\s+(?:(\d+(?:\.\d+)*)\.?\s+)?(.*)$")

    def __init__(self, path=BOOK):
        self.path = path
        self.text = path.read_text(encoding="utf-8")
        self.lines = self.text.split("\n")
        self.sections = {}      # "7.3.1" -> {"title", "start", "end", "text"}
        self.order = []
        cur = None
        for i, line in enumerate(self.lines):
            m = self.HEAD.match(line)
            if not m:
                continue
            num = m.group(2)
            if cur:
                self.sections[cur]["end"] = i
            key = num or m.group(3).strip()
            self.sections[key] = {"title": m.group(3).strip(), "start": i,
                                  "end": len(self.lines), "level": len(m.group(1))}
            self.order.append(key)
            cur = key
        for k, s in self.sections.items():
            s["text"] = "\n".join(self.lines[s["start"]:s["end"]])
            s["stems"] = set(norm(s["text"]))

    def numbered(self):
        return [k for k in self.order if re.fullmatch(r"\d+(\.\d+)*", k)]

    def section_and_children(self, num):
        """Текст раздела вместе со всеми его подразделами."""
        keys = [k for k in self.numbered() if k == num or k.startswith(num + ".")]
        return "\n".join(self.sections[k]["text"] for k in keys)

    def stems_of(self, nums):
        out = set()
        for n in nums:
            if n in self.sections:
                out |= set(norm(self.section_and_children(n)))
        return out

    @property
    def stems(self):
        if not hasattr(self, "_stems"):
            self._stems = set(norm(self.text))
        return self._stems


def coverage(words, stems):
    """Доля основ правила, найденных в тексте. Пустое правило — покрытие 1.0."""
    words = set(words)
    if not words:
        return 1.0, set()
    miss = words - stems
    return (len(words) - len(miss)) / len(words), miss
