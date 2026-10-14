# -*- coding: utf-8 -*-
"""
Превью книги правил «Нефтяные войны»: rules/RULEBOOK.md → HTML и PDF A4.

ВСЁ, ЧТО ПИШЕТ СКРИПТ, — ПРОИЗВОДНОЕ (D-108). Текст правится только
в rules/RULEBOOK.md, иллюстрации — в Иллюстрации.py, арт — в art/.

Запуск — в облачном контейнере Claude (Playwright + Chromium + poppler):

    python3 Книга.py SRC_ROOT OUT_DIR N

SRC_ROOT — корень проекта. Пишет в OUT_DIR:
    книга-preview-N.html                 просмотр в браузере
    книга-preview-N.pdf                  A4, настоящие страницы, одна колонка (D-126)
    книга-preview-N-переносы.txt         перенесённые слова и разреженные строки — для вычитки (D-144)
HTML кладётся в print/ (пути к шрифтам и картинкам — от print/).

Переносы ставятся при сборке (D-144): шаблоны Rulebook/hyph/hyph-ru.tex, свои — Rulebook/hyph/исключения.txt.

Содержание собирается в два прохода: PDF рендерится с невидимыми метками у
заголовков частей, pdftotext находит страницы меток, числа вписываются,
PDF рендерится снова. Chromium не умеет target-counter() — отсюда два прохода.
"""
import glob
import html
import json
import io
import os
import re
import subprocess
import sys
import tempfile

SRC = OUT = None
N = '2'

GLYPH = {'OIL': 'R', 'KILL': 'K', 'SUPPRESS': 'S', 'TASK': 'G',
         'MAP_MARK_DROP': 'Q', 'MAP_MARK_FLAME': 'W', 'MAP_MARK_CART': 'E'}

# ══════════════════════════════════════════════════════════════ РАЗБОР MARKDOWN
LIST_UL = re.compile(r'^- ')
LIST_OL = re.compile(r'^(\d+)\. ')
LIST_SUB = re.compile(r'^\s{2,}(\d+)\. ')
SUB = '\x00'


def parse(md):
    lines = md.split('\n')
    out, i = [], 0
    while i < len(lines):
        l = lines[i]
        if not l.strip():
            i += 1
            continue
        if l.startswith('#'):
            lvl = len(l) - len(l.lstrip('#'))
            out.append(('h', lvl, l[lvl:].strip()))
            i += 1
        elif l.strip() == '---':
            out.append(('hr',))
            i += 1
        elif l.startswith('|'):
            rows = []
            while i < len(lines) and lines[i].startswith('|'):
                cells = [c.strip() for c in lines[i].strip().strip('|').split('|')]
                if not all(re.fullmatch(r':?-{3,}:?', c) for c in cells):
                    rows.append(cells)
                i += 1
            out.append(('table', rows))
        elif l.startswith('>'):
            body = []
            while i < len(lines) and lines[i].startswith('>'):
                body.append(lines[i][1:].strip())
                i += 1
            paras, cur = [], []
            for b in body:
                if b:
                    cur.append(b)
                elif cur:
                    paras.append(' '.join(cur))
                    cur = []
            if cur:
                paras.append(' '.join(cur))
            out.append(('quote', paras))
        elif LIST_UL.match(l) or LIST_OL.match(l):
            ordered = bool(LIST_OL.match(l))
            items = []
            while i < len(lines) and lines[i].strip():
                m = LIST_OL.match(lines[i]) if ordered else LIST_UL.match(lines[i])
                ms = LIST_SUB.match(lines[i]) if items else None
                if m:
                    items.append(lines[i][m.end():].strip())
                elif ms:
                    # вложенный нумерованный список: подпункты хранятся в пункте через SUB (D-143)
                    items[-1] += SUB + lines[i][ms.end():].strip()
                else:
                    items[-1] += ' ' + lines[i].strip()
                i += 1
            out.append(('ol' if ordered else 'ul', items))
        else:
            cur = []
            while i < len(lines) and lines[i].strip():
                cur.append(lines[i].strip())
                i += 1
            out.append(('p', ' '.join(cur)))
    return out


def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', s)
    s = re.sub(r'\{([A-Z_]+)\}', lambda m: f'<span class="g">{GLYPH[m.group(1)]}</span>', s)
    return s


# Таблица результатов кубика (§8.4): смерть и подавление — картинками наклеек, как на памятке
# битвы (print/dices/*-simple-cut.png), а не глифом шрифта (D-155).
DIE_PIC = {'KILL': ('dices/kill-simple-cut.png', 'смерть'), 'SUPPRESS': ('dices/suppress-simple-cut.png', 'подавление')}


def die_pics(s):
    for k, (src, alt) in DIE_PIC.items():
        s = s.replace(f'<span class="g">{GLYPH[k]}</span>', f'<img class="die" src="{src}" alt="{alt}">')
    return s


def plain(s):
    return re.sub(r'\*\*|\{[A-Z_]+\}', '', s)


# ══════════════════════════════════════════════════════════════ ИЛЛЮСТРАЦИИ
def svg_inline(name):
    raw = open(os.path.join(SRC, 'print/Rulebook/img', name), encoding='utf-8').read()
    raw = raw[raw.index('<svg'):]
    raw = raw.replace('../../Fonts/', 'Fonts/')
    raw = re.sub(r'(<svg[^>]*?) width="[^"]+" height="[^"]+"', r'\1', raw, count=1)
    return raw


def fig(name, cls=''):
    return f'<figure class="fig {cls}">{svg_inline(name)}</figure>'


def side(name, w=62, fit=False, y=0):
    """Арт в колонку рядом с текстом, справа (D-147); 'img/файл' — из img/ (D-156).
    fit — низ картинки встаёт на базовую линию последней строки рядом с ней: картинку
    подрезает снизу раскладчик, до 20 % высоты (D-159); y — кадр по вертикали, %."""
    if name.startswith('img/'):
        src = 'Rulebook/' + name if os.path.exists(os.path.join(SRC, 'print/Rulebook', name)) else None
    else:
        src = art(name)
    if not src:
        return ''
    fit_attr = f' data-fit="1" data-y="{y}"' if fit else ''
    return f'<img class="side" src="{src}" alt=""{fit_attr} style="width:{w}mm">'


def artband(name, h, y=50):
    """Горизонтальный арт полосой во всю ширину посреди текста (D-147); 'img/файл' — из img/ (D-164)."""
    if name.startswith('img/'):
        src = 'Rulebook/' + name if os.path.exists(os.path.join(SRC, 'print/Rulebook', name)) else None
    else:
        src = art(name)
    return (f'<figure class="artband"><img src="{src}" alt="" style="height:{h}mm; '
            f'object-position:50% {y}%"></figure>') if src else ''


def znak(*names):
    imgs = ''.join(f'<img src="Rulebook/img/znak-{n}.png" alt="">' for n in names)
    return f'<span class="znaki n{len(names)}">{imgs}</span>'


def art(name):
    """Принятый арт (name.png) или последняя попытка (name-gN.png)."""
    base = os.path.join(SRC, 'print/Rulebook/art')
    if os.path.exists(os.path.join(base, name + '.png')):
        return f'Rulebook/art/{name}.png'
    tries = sorted(glob.glob(os.path.join(base, f'{name}-g*.png')),
                   key=lambda p: int(re.search(r'-g(\d+)\.png$', p).group(1)))
    return 'Rulebook/art/' + os.path.basename(tries[-1]) if tries else None


# куда что встаёт: (раздел, начало текста блока или шаблон re, что вставить, до/после).
# Начало берите короткое: текст правят, а якорь должен пережить правку стиля.
AFTER = [
    ('1.1', 'Карты скрытого влияния — 36 шт.', lambda: fig('komponenty-1.svg')),
    ('1.2', 'Точный состав напечатан на планшете', lambda: fig('komponenty-2.svg')),
    ('1.3', 'Планшет — главный справочник', lambda: fig('planshet.svg')),
    ('2.1', 'Возьмите игровое поле', lambda: fig('polya.svg')),
    ('2.2', 'Положите трек Судного дня рядом', lambda: fig('stol.svg', 'tall')),
    ('2.3', 'Игра за разные фракции различается', lambda: fig('frakcii.svg')),
    ('2.6', re.compile(r'\W*Каждый игрок ставит маркер нефти'), lambda: fig('primer-stol.svg', 'spaced')),
    ('4.1', re.compile(r'\W*Пример\.\W*У Александра три пехотинца'), lambda: fig('istochniki-nefti.svg')),
    ('4.2', re.compile(r'\W*На треке запаса нефти 20 делений'), lambda: fig('trek-nefti.svg')),
    ('5.2', re.compile(r'\W*Первый игрок выбирает направление хода'), lambda: fig('zheton.svg')),
    ('11.6', 'Пример: Узел управления', lambda: fig('roy.svg')),
]
BEFORE = [
    ('8.11', '**Пример 1. Битва без эффектов.**', lambda: fig('bitva.svg', 'tall')),
]
# арт перед заголовком пункта: пункт → что вставить (D-147)
BEFORE_HEAD = {
    '6.4': lambda: artband('states', 107, 50),  # здание с флагами — между §6.3 и §6.4 (D-147); 110 мм и больше — лишний лист
    # интендант с голограммой — рядом с §7.2 от заголовка, низ — по последней строке пункта (D-156, D-159)
    '7.2': lambda: side('img/konc-quartermaster-2.png', 54, fit=True),
    # комикс «Краб и Спрут» + «После битвы» — посреди листа 32, перед §8.9 (D-161, D-162, D-164)
    '8.9': lambda: artband('img/komiks-bitva.png', 51, 50),
}
# арт сразу после заголовка пункта, рядом с основным текстом: верх — по прописным первой строки (D-161)
AFTER_HEAD = {
    # «Кабинет»: чиновник и посланник корпорации — колонкой рядом с §9.2, светлее исходника (D-160)
    '9.2': lambda: side('img/office.png', 56, fit=True),
}
# картинка на листе «Содержание» — в свободное место под списком, как концовка части (D-161)
TOC_ART = ('band', 'reserves-g1', 90, 50, 40)      # резервуарный парк
# полосы арта под шапкой части: номер части ('' — Вступление) → (арт, высота мм, кадр по вертикали %)
PART_ART = {
    '': ('intro', 102, 30),       # сумерки над мегаполисом — первая строка Вступления; лист заполнен
}
# Ждут своих разделов (D-129): factories-g1, moon-g1 в art/ — вернёмся, когда дойдём до нужных
# разделов. Кадр по вертикали, если ставить полосой 52 мм: factories 50 %, moon 28 %.
# states-g1 — между §6.3 и §6.4 (D-147), кукловод из §6.3 снят.
# концовки частей (D-139, D-141): картинка на свободном месте последнего листа части, если влезает.
# номер части → что ставить:
#   ('img', файл в Rulebook/img/, наибольшая ширина мм, наибольшая высота мм) — вырезка на белом листе
#     (вырезки делает Иллюстрации.py, сборка koncovki);
#   ('band', арт в art/ или 'img/файл', наибольшая высота мм, кадр по вертикали %) — полоса во всю ширину,
#     как шапка части.
# Пятым числом можно задать наименьшую высоту, мм; ниже — картинку не ставим.
# Части без записи — без концовки: общей эмблемы нет (D-141).
KONC = {
    '1': ('band', 'warroom', 110, 55),                     # штаб над картой — после «Компонентов» (D-142: g2, 3 : 2)
    '5': ('band', 'img/valve.png', 100, 50),               # две стороны вентиля — после §5.2 (D-144, D-146)
    '8': ('band', 'retreat', 80, 30, 30),                  # «Отступление»: снизу режется больше, сверху меньше (D-163, D-164)
    '10': ('band', 'img/truce.png', 200, 50),              # «Перемирие», светлее исходника (D-163, D-164); запасной — warroom-g1
    '12': ('band', 'moon-g1', 113.3, 50),                  # лунная база — целиком, 3 : 2 (D-165, D-166)
}
# Картинки в пустоту посреди части (D-156): если лист кончается раньше — следующий блок
# не влез (таблица, рисунок, перенесённый заголовок), — в пустое место встаёт картинка.
# Ключ — последний пункт на этом листе; описание — как у KONC. Нет пустоты — нет картинки.
FILL = {
    '8.4': ('band', 'panorama', 60, 59, 18),               # панорама битвы вдали — перед таблицей результатов
}
KONC_MIN = 30                                     # мм: вырезка ниже — не ставим
KONC_MIN_BAND = 60                                # мм: полоса ниже — не ставим
SLOTS = False                                     # --slots: места под ещё не сгенерированный арт — пунктиром
ZNAKI = {
    '11.1': ('fabrika-osobaya', 'sobytiya'),
    '11.3': ('polkovniki',),
    '11.4': ('naemniki',),
    '11.5': ('laboratoriya', 'engramma'),
    '11.6': ('uzel', 'zona'),
}


def starts(txt, anchor):
    """Якорь — начало блока (строка) или шаблон re с начала блока."""
    return bool(anchor.match(txt)) if hasattr(anchor, 'match') else txt.startswith(anchor)


def span_lead(html_list):
    """Перед иллюстрацией во всю ширину: если между заголовком раздела и ней только
    короткий абзац, заголовок и абзац тоже идут во всю ширину — иначе в две колонки
    абзац рвётся на обрывки по обе стороны."""
    for k in range(len(html_list) - 1, -1, -1):
        if html_list[k].startswith('<h3'):
            tail = html_list[k + 1:]
            if len(tail) == 0 or (len(tail) == 1 and tail[0].startswith('<p>')
                                  and len(re.sub('<[^>]+>', '', tail[0])) < 400):
                html_list[k] = html_list[k].replace('<h3 ', '<h3 class="span" ', 1)
                if tail:
                    html_list[k + 1] = html_list[k + 1].replace('<p>', '<p class="span">', 1)
            return


def block_text(b):
    if b[0] == 'p':
        return b[1]
    if b[0] in ('ul', 'ol', 'quote'):
        return ' '.join(b[1]).replace(SUB, ' ')
    return ''


# ══════════════════════════════════════════════════════════════ ПЕРЕНОСЫ (D-144)
# Переносы ставятся при сборке мягкими переносами (U+00AD): браузер переносит слово только
# в этих местах, поэтому просмотр и печать раскладываются одинаково (D-138). Правила — открытые
# шаблоны hyph-ru (hyph-utf8; А. И. Лебедев; LPPL 1.2+) в Rulebook/hyph/, алгоритм Лянга, как в TeX.
# Не переносятся: заголовки, таблицы, подписи рисунков, слова целиком прописными (сокращения),
# слова короче 5 букв; на строке остаётся не меньше 2 букв. Последнее слово абзаца переносится:
# запрет давал строки с пробелами втрое шире нормы. Свои переносы и запреты —
# Rulebook/hyph/исключения.txt.
HYPH_DIR = 'print/Rulebook/hyph'
SHY = '\u00ad'
WORD = re.compile(r'[а-яёА-ЯЁ]+(?:-[а-яёА-ЯЁ]+)*')
_hy = {}


class Hyphenator:
    """Алгоритм Лянга: шаблоны из файла TeX (\\patterns{…}, \\hyphenation{…})."""
    def __init__(self, tex_path, left=2, right=2):
        txt = open(tex_path, encoding='utf-8').read()
        body = txt[txt.index('\\patterns{') + 10:]
        self.pats = {}
        for line in body[:body.index('}')].splitlines():
            p = line.split('%')[0].strip()
            if not p:
                continue
            pts, d = [], 0
            for ch in p:
                if ch.isdigit():
                    d = int(ch)
                else:
                    pts.append(d)
                    d = 0
            pts.append(d)
            self.pats[re.sub(r'\d', '', p)] = pts
        self.maxlen = max(len(k) for k in self.pats)
        self.exc = {}
        exc = txt[txt.index('\\hyphenation{') + 13:]
        for w in exc[:exc.index('}')].split():
            self.add_exception(w)
        self.left, self.right = left, right

    def add_exception(self, w):
        """«сло-во» — переносы только в этих местах; «слово» — без переносов."""
        pos, k = set(), 0
        for ch in w:
            if ch == '-':
                pos.add(k)
            else:
                k += 1
        self.exc[w.replace('-', '').lower()] = pos

    def points(self, word):
        """Позиции k: перенос перед буквой word[k]."""
        w = word.lower()
        if w in self.exc:
            return sorted(self.exc[w])
        work = '.' + w + '.'
        pts = [0] * (len(work) + 1)
        for i in range(len(work)):
            for j in range(i + 1, min(len(work), i + self.maxlen) + 1):
                p = self.pats.get(work[i:j])
                if p:
                    for k, v in enumerate(p):
                        if v > pts[i + k]:
                            pts[i + k] = v
        return [k for k in range(self.left, len(w) - self.right + 1)
                if pts[k + 1] % 2 and w[k - 1] != '-' and w[k] != '-']


def hyphenator():
    if 'h' not in _hy:
        h = Hyphenator(os.path.join(SRC, HYPH_DIR, 'hyph-ru.tex'))
        own = os.path.join(SRC, HYPH_DIR, 'исключения.txt')
        if os.path.exists(own):
            for line in open(own, encoding='utf-8'):
                w = line.split('#')[0].strip()
                if w:
                    h.add_exception(w)
        _hy['h'] = h
    return _hy['h']


# Висячие слова (D-145): короткий предлог или союз не остаётся в конце строки, частица «же», «ли»,
# «бы» — в начале, тире — в начале строки. Связка — неразрывный пробел (U+00A0).
NBSP = '\u00a0'
TIE_NEXT = ('а', 'в', 'и', 'к', 'о', 'с', 'у', 'я',
            'во', 'ко', 'со', 'об', 'от', 'до', 'за', 'из', 'на', 'по', 'не', 'ни', 'но')
TIE = re.compile(r'<[^>]+>'                                                       # теги — как есть
                 r'|(?<![\w-])(?:' + '|'.join(TIE_NEXT) + r') (?=\S)'           # «в регионе»
                 r'| (?=(?:же|ли|бы)(?![\w-]))'                                  # «если же»
                 r'| (?=— )', re.I)                                               # «фабрика — это»


def tie(s):
    """Неразрывные пробелы вокруг висячих слов — только в тексте, не в тегах."""
    def one(m):
        t = m.group(0)
        if t.startswith('<'):
            return t
        return t.replace(' ', NBSP)
    return TIE.sub(one, s)


def hyph(s):
    """Мягкие переносы и неразрывные пробелы в HTML абзаца — только в тексте, не в тегах."""
    h = hyphenator()
    parts = re.split(r'(<[^>]+>)', tie(s))

    def one(m):
        w = m.group(0)
        if len(w.replace('-', '')) < 5 or w.replace('-', '').isupper():
            return w
        cut, out = 0, []
        for k in h.points(w):
            out.append(w[cut:k])
            cut = k
        return SHY.join(out + [w[cut:]])

    for i, part in enumerate(parts):
        if part and not part.startswith('<'):
            parts[i] = WORD.sub(one, part)
    return ''.join(parts)


# ══════════════════════════════════════════════════════════════ СБОРКА HTML
def build_body(blocks):
    parts = []          # (id, номер, заголовок, html)
    cur = None
    sec = None
    after = {k: (t, f) for k, t, f in AFTER}
    after_used, before_used = set(), set()
    html_parts = []

    def flush():
        if cur:
            parts.append(cur)

    for b in blocks:
        if b[0] == 'h' and b[1] == 1:
            continue
        if b[0] == 'h' and b[1] == 2:
            flush()
            title = b[2]
            m = re.match(r'(\d+)\.\s+(.*)', title)
            num, name = (m.group(1), m.group(2)) if m else ('', title)
            cur = {'id': f'part-{num or "intro"}', 'num': num, 'name': name, 'html': []}
            sec = None
            continue
        if cur is None:
            continue          # титул «# Нефтяные войны / Правила.» — его заменяет обложка
        if b[0] == 'hr':
            if cur['num'] == '13':
                cur['html'].append('<hr class="soft">')
            continue
        if b[0] == 'h':
            m = re.match(r'(\d+(?:\.\d+)+)\.\s+(.*)', b[2])
            if m:
                sec = m.group(1)
                if sec in BEFORE_HEAD:
                    cur['html'].append(BEFORE_HEAD[sec]())
                tag = 'h3' if b[1] == 3 else 'h4'
                cur['html'].append(f'<{tag} id="s{sec.replace(".", "-")}"><span class="no">{sec}</span> '
                                   f'{tie(inline(m.group(2)))}</{tag}>')
                if sec == '11.6' and art('swarm'):
                    cur['html'].append(f'<img class="swarm" src="{art("swarm")}" alt="">')
                if sec in AFTER_HEAD:
                    cur['html'].append(AFTER_HEAD[sec]())
            else:
                cur['html'].append(f'<h3>{inline(b[2])}</h3>')
            continue
        txt = block_text(b)
        for k, t, f in BEFORE:
            if k == sec and starts(txt, t) and k not in before_used:
                span_lead(cur['html'])
                cur['html'].append(f())
                before_used.add(k)
        if b[0] == 'p':
            pre = ''
            if txt.startswith('**Что нужно:**') and sec in ZNAKI:
                pre = znak(*ZNAKI[sec])
            cls = ''
            if cur['num'] == '13' and re.match(r'\*\*[^*]+\*\*', txt):
                cls = ' class="term"'
            elif plain(txt).rstrip().endswith(':'):
                cls = ' class="lead"'          # вводная строка перед списком: держится со следующим (D-148)
            cur['html'].append(f'<p{cls}>{pre}{hyph(inline(txt))}</p>')
        elif b[0] in ('ul', 'ol'):
            def li(x):
                head, *subs = x.split(SUB)
                sub = ''.join(f'<li>{hyph(inline(s))}</li>' for s in subs)
                return f'<li>{hyph(inline(head))}' + (f'<ol class="sub">{sub}</ol>' if sub else '') + '</li>'
            lis = ''.join(li(x) for x in b[1])
            cur['html'].append(f'<{b[0]}>{lis}</{b[0]}>')
        elif b[0] == 'table':
            rows = b[1]
            th = ''.join(f'<th>{tie(inline(c))}</th>' for c in rows[0])
            trs = ''.join('<tr>' + ''.join(f'<td>{die_pics(tie(inline(c)))}</td>' for c in r) + '</tr>' for r in rows[1:])
            cur['html'].append(f'<table><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table>')
        elif b[0] == 'quote':
            first = b[1][0] if b[1] else ''
            kind = 'important' if first.startswith('**!') else 'example'
            if kind == 'example' and len(b[1]) > 3:
                kind += ' long'        # длинный пример (§8.11) может переходить на следующий лист (D-155)
            inner = ''.join(f'<p>{hyph(inline(x.replace("**! Важно.**", "**Важно.**")))}</p>' for x in b[1])
            cur['html'].append(f'<aside class="{kind}">{inner}</aside>')
        if sec in after and sec not in after_used:
            t, f = after[sec]
            if starts(txt, t) or (b[0] in ('ul', 'ol') and isinstance(t, str) and t in txt):
                span_lead(cur['html'])
                cur['html'].append(f())
                after_used.add(sec)
    flush()
    missing = [k for k, *_ in AFTER if k not in after_used] + [k for k, *_ in BEFORE if k not in before_used]
    if missing:
        raise SystemExit(f'не нашлось место для иллюстраций: {missing}')
    return parts


CSS = r"""
@font-face { font-family: 'Liberation Sans'; src: url('Fonts/LiberationSans-Regular.ttf'); }
@font-face { font-family: 'Liberation Sans'; font-weight: bold; src: url('Fonts/LiberationSans-Bold.ttf'); }
@font-face { font-family: 'Liberation Sans'; font-style: italic; src: url('Fonts/LiberationSans-Italic.ttf'); }
@font-face { font-family: 'OpenGostTypeB'; src: url('Fonts/OpenGostTypeB.ttf'); }
@font-face { font-family: 'Rationale'; src: url('Fonts/Rationale-Regular.ttf'); }
@font-face { font-family: 'Oil Wars'; src: url('Fonts/Oil Wars.ttf'); }
@font-face { font-family: 'AlienEncounters'; src: url('Fonts/AlienEncounters.ttf'); }
:root {
  --ink: #1E2A33; --muted: #5B6873; --accent: #EE688C; --cyan: #11C5FF; --line: #CFD8DE;
  --tint: #F1F6F9; --pinktint: #FCEEF2;
}
* { box-sizing: border-box; }
html { background: #DADFE3; }
body { margin: 0; color: var(--ink); font: 9.6pt/1.42 'Liberation Sans', Arial, sans-serif;
       -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body.c1 { font-size: 10.2pt; line-height: 1.45; }
span.g { font-family: 'Oil Wars'; font-weight: normal; font-style: normal; font-synthesis: none;
     font-size: 1.2em; line-height: 0; vertical-align: -0.06em; }  /* значки на 1,2 текста, строку не раздвигают (D-131);
        span — чтобы правило не задело class="g" внутри SVG-иллюстраций */
b { font-weight: bold; }

/* ── экран: листы шириной A4 ───────────────────────── */
.sheet { position: relative; width: 210mm; margin: 8mm auto; padding: 22mm 20mm 20mm; background: #fff;
         box-shadow: 0 1px 5px rgba(0,0,0,.18); overflow: hidden; }
.sheet .deco { position: absolute; width: 20mm; height: 20mm; pointer-events: none; }
.sheet .deco.tl { top: 0; left: 0; } .sheet .deco.br { bottom: 0; right: 0; }
.toolbar { position: sticky; top: 0; z-index: 10; display: flex; gap: 3mm; align-items: center; justify-content: center;
           padding: 2.5mm; background: rgba(30,42,51,.92); color: #fff; font: 10pt 'Liberation Sans'; }
.toolbar button { font: 10pt 'Liberation Sans'; padding: 1.2mm 4mm; border: 0.3mm solid #8FA0AC; background: transparent;
                  color: #fff; border-radius: 1mm; cursor: pointer; }
.toolbar button[aria-pressed="true"] { background: var(--accent); border-color: var(--accent); color: #1E2A33; }

/* ── обложка ───────────────────────────────────────── */
.cover { position: relative; width: 210mm; height: 297mm; margin: 8mm auto; overflow: hidden; background: #2b3138;
         box-shadow: 0 1px 5px rgba(0,0,0,.18); }
.cover img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; object-position: 50% 50%; }
.cover .scrim-t { position: absolute; left: 0; right: 0; top: 0; height: 70mm;
                  background: linear-gradient(rgba(16,22,28,.62), rgba(16,22,28,0)); }
.cover .scrim-b { position: absolute; left: 0; right: 0; bottom: 0; height: 55mm;
                  background: linear-gradient(rgba(16,22,28,0), rgba(16,22,28,.78)); }
.cover h1 { position: absolute; left: 0; right: 0; top: 16mm; margin: 0; text-align: center; color: #fff;
            font: 44pt/1 'AlienEncounters', sans-serif; letter-spacing: .04em; text-transform: uppercase;
            text-shadow: 0 0.6mm 2.5mm rgba(0,0,0,.55); }
.cover .rule { position: absolute; left: 50%; top: 37mm; width: 60mm; margin-left: -30mm; height: 0.8mm; background: var(--accent); }
.cover .sub { position: absolute; left: 0; right: 0; bottom: 16mm; text-align: center; color: #fff;
              font: 20pt 'OpenGostTypeB', sans-serif; letter-spacing: .3em; text-transform: uppercase; }
.cover .ver { position: absolute; left: 0; right: 0; bottom: 9.5mm; text-align: center; color: rgba(255,255,255,.78);
              font: 11pt 'Rationale', sans-serif; letter-spacing: .25em; }

/* ── содержание ────────────────────────────────────── */
.toc h2 { font: 22pt 'OpenGostTypeB', sans-serif; text-transform: uppercase; letter-spacing: .05em; margin: 0 0 8mm; }
.toc ol { list-style: none; margin: 0; padding: 0; columns: 1; }
.toc li { display: flex; align-items: baseline; gap: 2mm; padding: 2.2mm 0; border-bottom: 0.25mm solid var(--line);
          font: 12pt 'OpenGostTypeB', sans-serif; text-transform: uppercase; letter-spacing: .03em; }
.toc li .num { font-family: 'Rationale'; color: var(--accent); width: 10mm; font-size: 13pt; }
.toc li .name { flex: 1; }
.toc li .pg { font-family: 'Rationale'; font-size: 13pt; }
.toc .pg2 { display: none; }
body.c2 .toc .pg1 { display: none; } body.c2 .toc .pg2 { display: inline; }

/* ── шапка части ───────────────────────────────────── */
.parthead { position: relative; margin: 0 0 7mm; padding: 0 0 4mm; display: flex; align-items: baseline; gap: 4mm; }
.parthead .num { font: 30pt/1 'Rationale', sans-serif; color: var(--accent); }
.parthead .num:empty { display: none; }
.parthead h2 { margin: 0; font: 22pt/1.1 'OpenGostTypeB', sans-serif; text-transform: uppercase; letter-spacing: .04em; }
.parthead svg { position: absolute; left: 0; right: 0; bottom: 0; width: 100%; height: 3mm; }
.band { margin: 0 0 7mm; border-radius: 1.5mm; overflow: hidden; }
.band img { width: 100%; height: 100%; object-fit: cover; display: block; }

/* ── текст ─────────────────────────────────────────── */
/* автопереносы браузера выключены — листы расходились (D-138); переносы ставит сборка
   мягкими переносами, текст — по ширине (D-144) */
.body { orphans: 2; widows: 2; hyphens: manual; }
.body p, .body li { text-align: justify; }
body.c2 .body { column-count: 2; column-gap: 7mm; }
body.c2 .body.one { column-count: 1; }
p { margin: 0 0 2.2mm; }
h3 { font: 12.5pt/1.2 'OpenGostTypeB', sans-serif; text-transform: uppercase; letter-spacing: .03em;
     margin: 5.5mm 0 2.2mm; break-after: avoid; }
h3 .no { color: var(--accent); font-family: 'Rationale'; font-size: 13.5pt; letter-spacing: 0; margin-right: 1mm; }
h4 { font: bold 10.5pt/1.25 'Liberation Sans'; margin: 4mm 0 1.6mm; break-after: avoid; }
p.lead { break-after: avoid; }
h4 .no { color: var(--accent); font-family: 'Rationale'; font-weight: normal; font-size: 11.5pt; margin-right: 1mm; }
ul, ol { margin: 0 0 2.4mm; padding-left: 5mm; }
li { margin: 0 0 1mm; }
ol.sub { margin: 1mm 0 0; padding-left: 5mm; }
ul li::marker { color: var(--accent); }
ol li::marker { color: var(--accent); font-family: 'Rationale'; }
table { width: 100%; border-collapse: collapse; margin: 1.5mm 0 3.5mm; font-size: 0.95em; break-inside: avoid; }
body.c2 table { column-span: all; }
th { text-align: left; font: 9pt 'OpenGostTypeB', sans-serif; text-transform: uppercase; letter-spacing: .03em;
     border-bottom: 0.5mm solid var(--accent); padding: 1.3mm 2mm 1.3mm 0; }
td { border-bottom: 0.25mm solid var(--line); padding: 1.3mm 2mm 1.3mm 0; vertical-align: top; }
aside { break-inside: avoid; margin: 2mm 0 3.2mm; padding: 2.4mm 3mm 0.6mm 3.4mm; border-radius: 1mm; }
aside.example { background: var(--tint); border-left: 1.6mm solid var(--cyan); }   /* полоса 1,6 мм (D-150) */
aside.example.long { break-inside: auto; }
td img.die { height: 6.5mm; width: auto; vertical-align: middle; margin: -1.6mm 1.4mm -1.6mm 0; }
aside.important { background: var(--pinktint); border-left: 1.6mm solid var(--accent); }
aside p { margin-bottom: 1.8mm; }
.fig { margin: 3mm 0 5mm; break-inside: avoid; }
body.c2 .fig { column-span: all; }
.fig svg { display: block; width: 100%; height: auto; }
.fig.spaced { margin-top: 12mm; }
.znaki { float: left; display: flex; gap: 1mm; align-items: flex-end; margin: 0.6mm 3mm 1mm 0; }
.znaki img { height: 17mm; width: auto; max-width: 15mm; object-fit: contain; }
.znaki.n3 img { height: 13mm; max-width: 12mm; }
p:has(> .znaki) { min-height: 18mm; }
img.swarm { display: block; width: 100%; max-width: 78mm; margin: 0 auto 3mm; }
img.side { float: right; height: auto; margin: 1mm 0 3mm 6mm; border-radius: 1.5mm; }
figure.artband { margin: 4mm 0 5mm; break-inside: avoid; }
figure.artband img { display: block; width: 100%; object-fit: cover; border-radius: 1.5mm; }
body.c2 .span { column-span: all; }
.term { break-inside: avoid; }
hr.soft { border: 0; border-top: 0.25mm solid var(--line); margin: 3mm 0 4mm; }
.mk { font-size: 1px; color: #fff; line-height: 0; text-transform: none; letter-spacing: 0; }

/* ── печать ────────────────────────────────────────── */
@page { size: A4; margin: 20mm 20mm 20mm 20mm;
  @top-left-corner { content: ''; background: url("%%TL%%") no-repeat 0 0 / 20mm 20mm; }
  @bottom-right-corner { content: ''; background: url("%%BR%%") no-repeat 0 0 / 20mm 20mm; }
  @top-left { content: 'НЕФТЯНЫЕ ВОЙНЫ'; font: 7pt 'OpenGostTypeB'; letter-spacing: .2em; color: #8796A1; vertical-align: bottom; padding-bottom: 4mm; }
  @top-right { content: 'ПРАВИЛА'; font: 7pt 'OpenGostTypeB'; letter-spacing: .2em; color: #8796A1; vertical-align: bottom; padding-bottom: 4mm; }
  @bottom-center { content: counter(page); font: 10pt/9mm 'Rationale'; color: #5B6873; vertical-align: top;
                   padding-top: 6.5mm; width: 50mm; background: url("%%PN%%") no-repeat center 6.5mm / 50mm 9mm; }
}
@page cover { margin: 0; @top-left { content: none } @top-right { content: none } @bottom-center { content: none }
  @top-left-corner { content: none } @bottom-right-corner { content: none } }
@page toc { @top-left { content: none } @top-right { content: none } @bottom-center { content: none } }
@media print {
  html { background: #fff; }
  .toolbar { display: none; }
  .cover { page: cover; margin: 0; box-shadow: none; break-after: page; }
  .sheet { width: auto; margin: 0; padding: 0; box-shadow: none; overflow: visible; break-before: page; }
  .sheet.toc { page: toc; }
  .sheet .deco { display: none; }
}
"""

CORNER_TL = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20"><g fill="none" stroke="#11C5FF" '
             'stroke-width="0.35" stroke-linecap="round" opacity="0.8"><path d="M9,21 V12 Q9,9 12,9 H18"/>'
             '<circle cx="18.6" cy="9" r="0.7" fill="#11C5FF" stroke="none"/></g></svg>')
# декор номера страницы: шестигранник, как ячейки треков, и тонкие линии с точками, как у уголков
PAGE_NO = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 50 9"><g fill="none" stroke-linecap="round">'
           '<path d="M29.6,4.5 L27.3,0.52 H22.7 L20.4,4.5 L22.7,8.48 H27.3 Z" stroke="#11C5FF" stroke-width="0.35" '
           'stroke-linejoin="round" opacity="0.9"/>'
           '<path d="M18.6,4.5 H7.2 M31.4,4.5 H42.8" stroke="#11C5FF" stroke-width="0.3" opacity="0.8"/>'
           '<path d="M18.6,4.5 H16 M31.4,4.5 H34" stroke="#EE688C" stroke-width="0.7"/>'
           '<circle cx="6.4" cy="4.5" r="0.7" fill="#11C5FF" stroke="none"/>'
           '<circle cx="43.6" cy="4.5" r="0.7" fill="#11C5FF" stroke="none"/></g></svg>')
CORNER_BR = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20"><g fill="none" stroke="#11C5FF" '
             'stroke-width="0.35" stroke-linecap="round" opacity="0.8"><path d="M11,-1 V8 Q11,11 8,11 H2"/>'
             '<circle cx="1.4" cy="11" r="0.7" fill="#11C5FF" stroke="none"/></g></svg>')


def css():
    import urllib.parse
    q = lambda svg: 'data:image/svg+xml,' + urllib.parse.quote(svg)
    return (CSS + CSS_PAGED).replace('%%TL%%', q(CORNER_TL)).replace('%%BR%%', q(CORNER_BR)) \
        .replace('%%PN%%', q(PAGE_NO)).replace('%%RAIL_L%%', q(RAIL_L)).replace('%%RAIL_R%%', q(RAIL_R))


DECO = None   # собирается в build_html из тех же уголков, что и поля страниц в печати

VERSION = 'v1.0'   # версия правил на обложке (D-135)

# Рейка на внешнем поле листа — как side-rail.png планшета (print/Faction-Card-A/decor),
# перерисована вектором в цветах страницы: линия, шесть узлов-шестигранников с рисками,
# двойная риска посередине. Продолжает вертикаль уголка (D-135): на чётном листе выходит
# из верхнего левого уголка (x = 9 мм, от 20 мм вниз), на нечётном входит в нижний правый
# (x = 201 мм, до 277 мм). На стыке точки нет, на свободном конце — точка.
RAIL_LEN = 256.0


def _rail(join_top):
    H, cx = RAIL_LEN, 2.2
    c = '#41D1FF'   # #11C5FF при прозрачности 0,8 на белом — как уголок, но непрозрачный: перехлёст не темнеет
    nodes = [H * k for k in (0.075, 0.24, 0.405, 0.595, 0.76, 0.925)]
    y0, y1 = (0.0, H - 2.2) if join_top else (2.2, H)
    o = [f'<line x1="{cx}" y1="{y0}" x2="{cx}" y2="{H / 2 - 3.2}" stroke-linecap="butt"/>',
         f'<line x1="{cx}" y1="{H / 2 + 3.2}" x2="{cx}" y2="{y1}" stroke-linecap="butt"/>',
         f'<line x1="1.75" y1="{H / 2 - 2.2}" x2="1.75" y2="{H / 2 + 2.2}"/>',
         f'<line x1="2.65" y1="{H / 2 - 2.2}" x2="2.65" y2="{H / 2 + 2.2}"/>']
    for y in nodes:
        o.append(f'<path d="M{cx},{y - 2.0} L3.2,{y - 1.2} V{y + 1.2} L{cx},{y + 2.0} L1.2,{y + 1.2} V{y - 1.2} Z" '
                 f'fill="#FFFFFF"/>')
        for dy in (-0.5, 0.5):
            o.append(f'<line x1="0.15" y1="{y + dy}" x2="0.85" y2="{y + dy}"/>'
                     f'<line x1="3.55" y1="{y + dy}" x2="4.25" y2="{y + dy}"/>')
    dot = H - 1.2 if join_top else 1.2
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 4.4 {H}" width="4.4mm" height="{H}mm">'
            f'<g fill="none" stroke="{c}" stroke-width="0.35" stroke-linecap="round">'
            + ''.join(o) + f'<circle cx="{cx}" cy="{dot}" r="0.7" fill="{c}" stroke="none"/></g></svg>')


RAIL_L, RAIL_R = _rail(True), _rail(False)

# ══════════════════════════════════════════════════════════════ ПОСТРАНИЧНЫЙ ПРОСМОТР
# В браузере книга раскладывается на листы A4, как в печати (D-132). Своим кодом, без
# внешних библиотек: каждая часть ставится в многоколоночный блок с колонкой 170 × 257 мм —
# браузер режет его на колонки тем же механизмом, что и на страницы при печати (висячие
# строки, «не разрывать», «не отрывать заголовок»). Колонка = страница. Затем каждая
# страница — окно 170 × 257 мм в ту же часть, свёрстанную одним столбцом, со сдвигом
# к первой строке колонки. Раскладка идёт в браузере читателя, поэтому совпадает
# с его шрифтами. PDF (--pdf) — печать этих же листов (D-133); адрес с #flow — сплошной
# поток без раскладки, для отладки.
CSS_PAGED = r"""
.stage { position: absolute; left: 0; top: 0; visibility: hidden; pointer-events: none; }
.stage > div { position: absolute; left: 0; top: 0; }
.flow { width: 170mm; display: flow-root; }
.flow.cols { height: 257mm; column-width: 170mm; column-gap: 20mm; column-fill: auto; }
.flow thead { display: table-row-group; }
.page { position: relative; width: 210mm; height: 297mm; margin: 8mm auto; background: #fff;
        box-shadow: 0 1px 5px rgba(0,0,0,.18); overflow: hidden; }
.page .win { position: absolute; left: 20mm; top: 20mm; width: 170mm; overflow: hidden; }
.page .hd { position: absolute; left: 20mm; right: 20mm; top: 0; height: 16mm; display: flex;
            justify-content: space-between; align-items: flex-end;
            font: 7pt/1 'OpenGostTypeB'; letter-spacing: .2em; color: #8796A1; }
.page .hd .where { display: flex; align-items: baseline; gap: 2.6mm; }
.page .hd .part { font: 7.5pt/1 'OpenGostTypeB'; letter-spacing: .14em; color: var(--ink); text-transform: uppercase; }
.page .hd .sec { font: 14pt/1 'Rationale'; letter-spacing: .02em; color: var(--accent); }
/* брошюра: часть и пункты — всегда у внешнего края, номера пунктов — крайними (D-135) */
.page.even .hd, .page.even .hd .where { flex-direction: row-reverse; }
/* ось номера — на высоте горизонтали нижнего уголка, 288 мм (D-135) */
.page .pn { position: absolute; left: 80mm; width: 50mm; top: 283.5mm; height: 9mm; text-align: center;
            font: 10pt/9mm 'Rationale'; color: #5B6873; background: url("%%PN%%") no-repeat center / 50mm 9mm; }
.page > .deco { position: absolute; width: 20mm; height: 20mm; pointer-events: none; }
/* рейка — на внешнем поле: нечётный лист справа, чётный слева (брошюра) */
.page > .rail { position: absolute; width: 4.4mm; height: 256mm; pointer-events: none;
                background: no-repeat 0 0 / 100% 100%; }
/* ось рейки — на вертикали уголка: слева x = 9 мм от 20 мм, справа x = 201 мм до 277 мм */
.page > .rail.l { left: 6.8mm; top: 19.4mm; background-image: url("%%RAIL_L%%"); }   /* заходит под уголок на 0,6 мм */
.page > .rail.r { right: 6.8mm; top: 21.6mm; background-image: url("%%RAIL_R%%"); }
.page > .deco.tl { top: 0; left: 0; } .page > .deco.br { right: 0; bottom: 0; }
.page.cover-page > .cover { margin: 0; box-shadow: none; }
.page > .konc { position: absolute; object-fit: contain; pointer-events: none; }
.page > .konc.band { object-fit: cover; border-radius: 1.5mm; }
.page > .konc.slot { display: flex; align-items: center; justify-content: center; border: 0.4mm dashed #8796A1;
                     border-radius: 1.5mm; background: #F1F4F6; color: #5B6873; font: 9pt 'Liberation Sans'; }   /* как полоса под шапкой части */
.pager-note { position: fixed; top: 4mm; left: 50%; transform: translateX(-50%); z-index: 10;
              background: rgba(30,42,51,.92); color: #fff; padding: 2mm 5mm; border-radius: 1mm;
              font: 10pt 'Liberation Sans', sans-serif; }
"""

PAGER_JS = r"""
(function () {
  if (location.hash === '#flow') return;
  const MM = 96 / 25.4, CW = 170 * MM, CH = 257 * MM, GAP = 20 * MM;
  const note = document.createElement('div');
  note.className = 'pager-note'; note.textContent = 'Раскладываю страницы…';
  document.body.appendChild(note);

  const imgsReady = root => Promise.all([...root.querySelectorAll('img')].map(i =>
    i.complete ? (i.decode ? i.decode().catch(() => 0) : 0)
               : new Promise(r => { i.onload = i.onerror = r; })));
  const inSvg = n => !!(n.parentElement && n.parentElement.closest('svg'));
  function texts(root) {
    const out = [], w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    let n; while ((n = w.nextNode())) if (n.data.trim() && !inSvg(n)) out.push(n);
    return out;
  }
  const atoms = root => [...root.querySelectorAll('img, hr, svg')].filter(e => !inSvg(e));
  function charRect(n, o) {
    const r = document.createRange(); r.setStart(n, o); r.setEnd(n, Math.min(o + 1, n.length));
    const rs = r.getClientRects(); return rs.length ? rs[0] : r.getBoundingClientRect();
  }
  function flowOf(sec) {
    const f = document.createElement('div'); f.className = 'flow body';
    for (const el of sec.children) {
      if (el.classList.contains('deco')) continue;
      if (el.classList.contains('body')) for (const c of el.children) f.appendChild(c.cloneNode(true));
      else f.appendChild(el.cloneNode(true));
    }
    f.querySelectorAll('.mk').forEach(e => e.remove());
    // id заголовков снимаются (копии на нескольких листах), id внутри SVG — нет: на них
    // держатся обрезка врезок карт (clipPath) и стрелки (marker)
    f.querySelectorAll('[id]').forEach(e => { if (!e.closest('svg')) e.removeAttribute('id'); });
    return f;
  }
  function deco(sample) {
    return [...sample.querySelectorAll(':scope > .deco')].map(d => d.cloneNode(true));
  }
  function page(cls, decos) {
    const p = document.createElement('div'); p.className = 'page' + (cls ? ' ' + cls : '');
    (decos || []).forEach(d => p.appendChild(d.cloneNode(true)));
    return p;
  }

  // Картинка на свободное место листа под текстом, по центру полосы. Полоса — как можно выше,
  // отступ 6 мм от низа последней строки или рисунка, а не от конца окна листа: в окно входят
  // ещё поля абзаца и следующего блока (D-144, D-159); вырезка — по пропорции. Место под ещё не сгенерированный
  // арт (--slots) — пунктирная рамка с именем и размером (D-156).
  function placeArt(p, used, s) {
    const free = 257 - used, band = !!s.band;
    let H = Math.min(s.kh, free - (band ? 6 : 16)), W = 170;
    if (!band) { W = H * s.ar; if (W > s.kw) { W = s.kw; H = W / s.ar; } }
    if (H < s.min) return;
    const gap = band ? 6 : Math.min(15, (free - H) / 2);
    let el;
    if (s.slot) {
      el = document.createElement('div'); el.className = 'konc slot';
      el.textContent = `${s.label} — ${Math.round(W)} × ${Math.round(H)} мм`;
    } else {
      el = document.createElement('img'); el.className = band ? 'konc band' : 'konc';
      el.src = s.src; el.alt = '';
    }
    el.style.cssText = `left:${20 + (170 - W) / 2}mm; top:${20 + used + gap}mm; width:${W}mm; height:${H}mm`
                       + (band && !s.slot ? `; object-position: 50% ${s.y}%` : '');
    p.appendChild(el);
  }

  // Картинка рядом с текстом с data-fit (D-159): низ — на базовую линию последней строки рядом
  // с ней, картинка подрезается снизу, не больше чем на 20 % высоты. Меряется в самой части,
  // до раскладки по листам: там та же колонка 170 мм, что и в раскладке.
  function fitSide(sec) {
    for (const img of sec.querySelectorAll('img.side[data-fit]')) {
      // верх картинки: перед заголовком — по верху заголовка (D-160); после заголовка — по прописным
      // первой строки текста рядом (D-161). Liberation Sans: вынос вниз 0,19 высоты строки шрифта,
      // прописные — 0,688 кегля, кегль — высота строки шрифта / 1,117
      const nx = img.nextElementSibling;
      let top = null;
      if (nx && nx.matches('h3, h4')) top = nx.getBoundingClientRect().top;
      else for (const n of texts(sec)) {
        if (!(img.compareDocumentPosition(n) & Node.DOCUMENT_POSITION_FOLLOWING)) continue;
        const rg = document.createRange(); rg.selectNodeContents(n);
        const x = [...rg.getClientRects()].find(q => q.height);
        if (x) { top = x.bottom - 0.19 * x.height - 0.688 * x.height / 1.117; break; }
      }
      if (top !== null) {
        const d = top - img.getBoundingClientRect().top;
        if (Math.abs(d) > 0.3) img.style.marginTop = (parseFloat(getComputedStyle(img).marginTop) + d) + 'px';
      }
      const r = img.getBoundingClientRect(), mb = parseFloat(getComputedStyle(img).marginBottom) || 0;
      const after = n => img.compareDocumentPosition(n) & Node.DOCUMENT_POSITION_FOLLOWING;
      const lo = r.top + r.height * 0.8, hi = r.bottom + 0.5;
      // базовая линия строки рядом с картинкой, если попадает в допустимую подрезку
      const base = x => {
        if (!x.height || x.top >= r.bottom + mb || x.right > r.left + 0.5) return null;
        const b = x.bottom - 0.19 * x.height;               // Liberation Sans: нижний вынос — 0,19 высоты
        return b >= lo && b <= hi ? b : null;
      };
      // сначала — последняя строка абзаца или пункта списка: текст кончается вровень с картинкой
      let best = null;
      for (const el of sec.querySelectorAll('p, li')) {
        if (!after(el)) continue;
        const rg = document.createRange(); rg.selectNodeContents(el);
        const rs = [...rg.getClientRects()].filter(x => x.height);
        const b = rs.length ? base(rs[rs.length - 1]) : null;
        if (b !== null && (best === null || b > best)) best = b;
      }
      img.dataset.fitTo = best === null ? 'line' : 'para';
      if (best === null) for (const n of texts(sec)) {          // иначе — любая строка
        if (!after(n)) continue;
        const rg = document.createRange(); rg.selectNodeContents(n);
        for (const x of rg.getClientRects()) { const b = base(x); if (b !== null && (best === null || b > best)) best = b; }
      }
      if (best === null) continue;
      const h = best - r.top;
      if (h >= r.height - 0.5) continue;
      img.style.height = h + 'px';
      img.style.marginBottom = '0';      // строка под картинкой — уже во всю ширину
      img.style.objectFit = 'cover';
      img.style.objectPosition = `50% ${img.dataset.y || 0}%`;
      img.dataset.fitted = (h / MM).toFixed(1);
    }
  }

  // Заголовок пункта и вводная строка с двоеточием не остаются внизу листа одни (D-148): если
  // после них в той же колонке меньше KEEP мм текста, а продолжение уходит на следующий лист,
  // они начинают следующий лист. Цепочка «заголовок — вводная строка» переносится целиком.
  const KEEP = 15 * MM, KEEPERS = 'h3, h4, p.lead';
  function keepWithNext(A, B) {
    const kids = [...A.children], bk = [...B.children];
    for (let it = 0; it < 60; it++) {
      const ar = A.getBoundingClientRect();
      const colOf = r => Math.floor((r.left - ar.left + 1) / (CW + GAP));
      let moved = false;
      for (const k of kids) {
        if (!k.matches(KEEPERS) || k.style.breakBefore === 'column') continue;
        const r = k.getBoundingClientRect();
        if (!r.height || r.top - ar.top < 1) continue;            // уже вверху колонки
        const c = colOf(r);
        let bottom = r.bottom, spills = false;
        for (let s = k.nextElementSibling; s && !spills; s = s.nextElementSibling)
          for (const fr of s.getClientRects()) {
            if (!fr.height) continue;
            const cc = colOf(fr);
            if (cc === c) bottom = Math.max(bottom, fr.bottom); else if (cc > c) spills = true;
          }
        if (!spills || bottom - r.bottom >= KEEP) continue;
        let t = k;
        while (t.previousElementSibling && t.previousElementSibling.matches(KEEPERS)
               && t.previousElementSibling.getBoundingClientRect().top - ar.top >= 1) t = t.previousElementSibling;
        t.style.breakBefore = 'column';
        bk[kids.indexOf(t)].dataset.kept = '1';
        moved = true;
        break;
      }
      if (!moved) break;
    }
  }

  async function layoutPart(sec, stage) {
    const A = flowOf(sec), B = A.cloneNode(true);
    A.classList.add('cols');
    const wa = document.createElement('div'), wb = document.createElement('div');
    wa.appendChild(A); wb.appendChild(B); stage.append(wa, wb);
    await imgsReady(wa); await imgsReady(wb);
    keepWithNext(A, B);
    const ar = A.getBoundingClientRect(), br = B.getBoundingClientRect();
    const col = r => Math.floor((r.left - ar.left + 1) / (CW + GAP));
    const tA = texts(A), tB = texts(B), eA = atoms(A), eB = atoms(B);
    const first = [];
    const put = (c, top, it) => { if (c >= 0 && (!first[c] || top < first[c].top)) first[c] = Object.assign({ top }, it); };
    tA.forEach((n, i) => {
      const rg = document.createRange(); rg.selectNodeContents(n);
      for (const r of rg.getClientRects()) if (r.width || r.height) put(col(r), r.top, { t: 1, i });
    });
    eA.forEach((e, i) => { const r = e.getBoundingClientRect(); if (r.height) put(col(r), r.top, { t: 0, i }); });
    const n = Math.max(1, first.length), off = [0];
    for (let k = 1; k < n; k++) {
      const it = first[k];
      if (!it) { off.push(off[k - 1] + CH); continue; }
      let topA, topB;
      if (!it.t) { topA = eA[it.i].getBoundingClientRect().top; topB = eB[it.i].getBoundingClientRect().top; }
      else {
        const na = tA[it.i], nb = tB[it.i];
        let lo = 0, hi = na.length - 1;
        while (lo < hi) { const m = (lo + hi) >> 1; if (col(charRect(na, m)) < k) lo = m + 1; else hi = m; }
        topA = charRect(na, lo).top; topB = charRect(nb, lo).top;
      }
      off.push((topB - br.top) - (topA - ar.top));
    }
    const kids = [...B.children].map(e => {
      const r = e.getBoundingClientRect();
      return { e, top: r.top - br.top, bottom: r.bottom - br.top, mt: parseFloat(getComputedStyle(e).marginTop) || 0 };
    });
    const total = br.height;
    const secs = [...B.querySelectorAll('h3, h4')].map(h => {
      const no = h.querySelector('.no');
      return no ? { no: no.textContent.trim(), top: h.getBoundingClientRect().top - br.top } : null;
    }).filter(Boolean);
    wa.remove(); wb.remove();
    const wins = [];
    for (let k = 0; k < n; k++) {
      const a = off[k], h = Math.min(CH, (k + 1 < n ? off[k + 1] : total) - a);
      let f = 0, mx = -1e9;
      while (f < kids.length) { mx = Math.max(mx, kids[f].bottom); if (mx <= a + 0.5) f++; else break; }
      let l = kids.length - 1;
      while (l > f && kids[l].top >= a + h - 0.5) l--;
      const c = B.cloneNode(false);
      if (f > 0) { const s = document.createElement('div'); s.style.height = (kids[f].top - kids[f].mt) + 'px'; c.appendChild(s); }
      for (let i = f; i <= l; i++) c.appendChild(kids[i].e.cloneNode(true));
      c.style.marginTop = (-a) + 'px';
      const w = document.createElement('div'); w.className = 'win'; w.style.height = h + 'px';
      w.appendChild(c);
      // низ последней строки или рисунка на листе, мм: от него — отступ картинки в пустоту (D-159)
      let ink = 0;
      for (let i = f; i <= l; i++) ink = Math.max(ink, Math.min(kids[i].bottom, a + h) - a);
      w.dataset.ink = (ink / MM).toFixed(2);
      // пункты на листе: начатые на нём и тот, что продолжается сверху
      const on = secs.filter(x => x.top >= a - 1 && x.top < a + h - 1);
      const prev = secs.filter(x => x.top < a - 1).pop();
      if (prev && (!on.length || on[0].top > a + 2)) on.unshift(prev);
      w.dataset.secs = on.length ? (on.length > 1 ? on[0].no + '–' + on[on.length - 1].no : on[0].no) : '';
      wins.push(w);
    }
    return wins;
  }

  async function run() {
    await document.fonts.ready;
    const cover = document.querySelector('section.cover');
    const toc = document.querySelector('section.sheet.toc');
    const parts = [...document.querySelectorAll('section.sheet:not(.toc)')];
    const decos = deco(toc);
    const stage = document.createElement('div'); stage.className = 'stage'; document.body.appendChild(stage);
    const pages = [], starts = {};
    const pc = page('cover-page'); pc.appendChild(cover); pages.push(pc);
    const pt = page('toc-page', decos), tw = document.createElement('div');
    tw.className = 'win toc';
    [...toc.children].forEach(c => { if (!c.classList.contains('deco')) tw.appendChild(c); });
    pt.appendChild(tw); pages.push(pt);
    for (const sec of parts) {
      await imgsReady(sec); fitSide(sec);
      const wins = await layoutPart(sec, stage);
      starts[sec.id] = pages.length + 1;
      for (const w of wins) {
        const p = page((pages.length + 1) % 2 ? '' : 'even', decos);   // чётный лист — зеркальный колонтитул
        const hd = document.createElement('div'); hd.className = 'hd';
        hd.innerHTML = '<span>НЕФТЯНЫЕ ВОЙНЫ</span><span class="where"><span class="part"></span><span class="sec"></span></span>';
        hd.querySelector('.part').textContent = sec.dataset.name;
        hd.querySelector('.sec').textContent = w.dataset.secs || sec.dataset.num;
        p.appendChild(hd);
        p.appendChild(w);
        const pn = document.createElement('div'); pn.className = 'pn'; pn.textContent = pages.length + 1;
        p.appendChild(pn); pages.push(p);
      }
      // концовка (D-139, D-141) — на последнем листе части; картинка в пустоту (D-156) — на листе,
      // который кончается раньше, по последнему пункту листа
      const spec = sec.dataset.art ? JSON.parse(sec.dataset.art) : {};
      const own = pages.slice(-wins.length);
      wins.forEach((w, i) => {
        const used = parseFloat(w.dataset.ink) || parseFloat(w.style.height) / MM;
        if (i === wins.length - 1) { if (spec.end) placeArt(own[i], used, spec.end); return; }
        const last = (w.dataset.secs || '').split('–').pop();
        if (spec.fill && spec.fill[last]) placeArt(own[i], used, spec.fill[last]);
      });
    }
    pages.forEach((p, i) => {          // кроме обложки: рейка на внешнем поле
      if (!i) return;
      const r = document.createElement('div'); r.className = 'rail ' + ((i + 1) % 2 ? 'r' : 'l');
      p.appendChild(r);
    });
    stage.remove();
    const lis = tw.querySelectorAll('li');
    parts.forEach((sec, i) => { const s = lis[i] && lis[i].querySelector('.pg1'); if (s) s.textContent = starts[sec.id]; });
    parts.forEach(s => s.remove()); toc.remove();
    const book = document.createElement('div'); book.className = 'book';
    pages.forEach(p => book.appendChild(p));
    document.body.insertBefore(book, note);
    if (toc.dataset.art) {            // картинка на листе «Содержание» — под списком (D-161)
      const last = tw.querySelector('ol > li:last-child') || tw;
      const used = (last.getBoundingClientRect().bottom - tw.getBoundingClientRect().top) / MM;
      placeArt(pt, used, JSON.parse(toc.dataset.art).end);
    }
    const ps = document.createElement('style');
    ps.textContent = '@page { size: A4; margin: 0; @top-left { content: none } @top-right { content: none } ' +
      '@bottom-center { content: none } @top-left-corner { content: none } @bottom-right-corner { content: none } } ' +
      '@media print { html { background: #fff } .page { margin: 0; box-shadow: none; break-after: page; } .pager-note { display: none } }';
    document.head.appendChild(ps);
    note.remove();
    await Promise.all([...document.querySelectorAll('img.konc')].map(i => i.decode().catch(() => {})));
    window.__book = { pages: pages.length, starts };
    document.body.dataset.paged = '1';
  }
  if (document.readyState === 'complete') run(); else window.addEventListener('load', run);
})();
"""

PARTLINE = """<svg viewBox="0 0 170 3" preserveAspectRatio="none" aria-hidden="true"><g fill="none" stroke-linecap="round">
<path d="M0,1.5 H40" stroke="#EE688C" stroke-width="0.8"/><path d="M43,1.5 H170" stroke="#11C5FF" stroke-width="0.3" opacity="0.8"/>
<circle cx="41.5" cy="1.5" r="0.8" fill="#11C5FF"/></g></svg>"""


def art_spec(kind, name, a, b, mn=None):
    """Картинка для раскладчика: файл, предельные размеры, пропорция или кадр. Нет файла —
    пусто, а со --slots — место пунктиром с именем (D-156)."""
    if kind == 'band':
        if name.startswith('img/'):      # обработанный арт (Иллюстрации.py)
            src = 'Rulebook/' + name if os.path.exists(os.path.join(SRC, 'print/Rulebook', name)) else None
        else:
            src = art(name)
        spec = {'band': 1, 'kh': a, 'y': b, 'min': mn or KONC_MIN_BAND}
    else:
        path = os.path.join(SRC, 'print/Rulebook/img', name)
        src = f'Rulebook/img/{name}' if os.path.exists(path) else None
        spec = {'kw': a, 'kh': b, 'min': mn or KONC_MIN, 'ar': 0.66}
        if src:
            from PIL import Image
            w, h = Image.open(path).size
            spec['ar'] = round(w / h, 4)
    if src:
        spec['src'] = src
    elif SLOTS:
        spec.update(slot=1, label=name)
    else:
        return None
    return spec


def art_attrs(num):
    """data-art части: концовка (KONC) и картинки в пустоту (FILL)."""
    import json
    end = art_spec(*KONC[num]) if num in KONC else None
    fill = {}
    for sec, v in FILL.items():
        if sec.split('.')[0] == num:
            sp = art_spec(*v)
            if sp:
                fill[sec] = sp
    if not end and not fill:
        return ''
    return f' data-art="{html.escape(json.dumps({"end": end, "fill": fill}, ensure_ascii=False))}"'


def build_html(parts, pages1=None, pages2=None):
    import urllib.parse
    q = lambda svg: 'data:image/svg+xml,' + urllib.parse.quote(svg)
    DECO = (f'<img class="deco tl" src="{q(CORNER_TL)}" alt=""><img class="deco br" src="{q(CORNER_BR)}" alt="">')
    cover = art('cover')
    out = ['<!doctype html><html lang="ru"><head><meta charset="utf-8">',
           '<meta name="viewport" content="width=device-width, initial-scale=1">',
           f'<title>Нефтяные войны — правила, просмотр {N}</title>',
           '<!-- ПРОИЗВОДНЫЙ ФАЙЛ: собирается print/Rulebook/Книга.py из rules/RULEBOOK.md. Руками не править. -->',
           f'<style>{css()}</style></head><body class="c1">',
           ]
    # обложка
    out.append('<section class="cover">')
    if cover:
        out.append(f'<img src="{cover}" alt="">')
    out.append('<div class="scrim-t"></div><div class="scrim-b"></div>'
               '<h1>Нефтяные войны</h1><div class="rule"></div><div class="sub">Правила игры</div>'
               f'<div class="ver">{VERSION}</div></section>')
    # содержание
    toc_art = ''
    if TOC_ART:
        sp = art_spec(*TOC_ART)
        if sp:
            toc_art = f' data-art="{html.escape(json.dumps({"end": sp}, ensure_ascii=False))}"'
    out.append(f'<section class="sheet toc"{toc_art}>{DECO}<h2>Содержание</h2><ol>')
    for prt in parts:
        p1 = (pages1 or {}).get(prt['id'], '')
        p2 = (pages2 or {}).get(prt['id'], '')
        out.append(f'<li><span class="num">{prt["num"]}</span><span class="name">{html.escape(prt["name"])}</span>'
                   f'<span class="pg pg1">{p1}</span><span class="pg pg2">{p2}</span></li>')
    out.append('</ol></section>')
    # части
    for prt in parts:
        mark = f'<span class="mk">QQ{prt["id"]}QQ</span>'
        body_cls = 'body one' if prt['num'] in ('13', '10', '') else 'body'
        out.append(f'<section class="sheet" id="{prt["id"]}" data-num="{prt["num"]}" '
                   f'data-name="{html.escape(prt["name"])}"{art_attrs(prt["num"])}>{DECO}')
        out.append(f'<div class="parthead"><div class="num">{prt["num"]}</div>'
                   f'<h2>{mark}{html.escape(prt["name"])}</h2>{PARTLINE}</div>')
        if prt['num'] in PART_ART and art(PART_ART[prt['num']][0]):
            name, h, y = PART_ART[prt['num']]
            out.append(f'<div class="band" style="height:{h}mm"><img src="{art(name)}" alt="" '
                       f'style="object-position:50% {y}%"></div>')
        out.append(f'<div class="{body_cls}">' + '\n'.join(prt['html']) + '</div></section>')
    out.append(f'<script>{PAGER_JS}</script></body></html>')
    return '\n'.join(out)


# ══════════════════════════════════════════════════════════════ PDF И СОДЕРЖАНИЕ
# Проверка переносов и разрядки на готовых листах (D-144): какие слова перенеслись (мягкий
# перенос, у которого буквы до и после — на разных строках) и в каких строках по ширине
# пробел шире нормы шрифта больше чем в LOOSE раз. Последняя строка абзаца не выключается.
LOOSE = 1.8
TYPO_JS = r"""
() => {
  const SHY = '\u00ad', res = { broken: [], lines: 0, loose: [], kept: [] };
  // норма пробела — ширина пробела того же шрифта в строке без выключки
  const norm = new Map(), probe = document.createElement('span');
  probe.style.cssText = 'position:absolute; visibility:hidden; white-space:pre; left:0; top:0';
  document.body.appendChild(probe);
  const spaceW = el => {
    const cs = getComputedStyle(el), f = `${cs.fontStyle} ${cs.fontWeight} ${cs.fontSize} ${cs.fontFamily}`;
    if (!norm.has(f)) {
      probe.style.font = f;
      probe.textContent = 'н н'; const w1 = probe.getBoundingClientRect().width;
      probe.textContent = 'нн'; norm.set(f, w1 - probe.getBoundingClientRect().width);
    }
    return norm.get(f);
  };
  const rg = document.createRange();
  // у буквы сразу после перенесённого мягкого переноса Chromium отдаёт два прямоугольника:
  // первый — на прежней строке; настоящий — последний
  const rect = (n, i, last) => { rg.setStart(n, i); rg.setEnd(n, i + 1); const r = rg.getClientRects();
                                 return r.length ? r[last ? r.length - 1 : 0] : null; };
  const letter = /[а-яё\u00ad-]/i;
  document.querySelectorAll('.page').forEach((pg, pi) => {
    const win = pg.querySelector('.win'); if (!win) return;
    const wr = win.getBoundingClientRect();
    win.querySelectorAll('[data-kept]').forEach(e => {
      const r = e.getBoundingClientRect();
      if (r.top >= wr.top - 0.5 && r.top < wr.top + 8 * 96 / 25.4) res.kept.push([pi + 1, e.textContent.replace(/\u00ad/g, '').slice(0, 60)]);
    });
    const inWin = r => r.top >= wr.top - 0.5 && r.bottom <= wr.bottom + 0.5;
    const lines = new Map();
    const tw = document.createTreeWalker(win, NodeFilter.SHOW_TEXT);
    let n;
    while ((n = tw.nextNode())) {
      const t = n.data, blk = n.parentElement.closest('p, li');
      const just = blk && getComputedStyle(blk).textAlign === 'justify';
      for (let i = 0; i < t.length; i++) {
        if (t[i] === SHY && i > 0 && i + 1 < t.length) {
          const a = rect(n, i - 1), b = rect(n, i + 1, true);
          if (a && b && b.top - a.top > 2 && inWin(a)) {
            let s = i, e = i + 1;
            while (s > 0 && letter.test(t[s - 1])) s--;
            while (e < t.length && letter.test(t[e])) e++;
            res.broken.push([pi + 1, t.slice(s, i).replace(/\u00ad/g, '') + '-' + t.slice(i + 1, e).replace(/\u00ad/g, '')]);
          }
        } else if (t[i] === ' ' && just) {
          const r = rect(n, i);
          if (!r || !r.width || !inWin(r)) continue;
          const key = Math.round(r.top);
          let L = lines.get(blk); if (!L) { L = new Map(); lines.set(blk, L); }
          const o = L.get(key) || { w: 0, k: 0, sp: spaceW(n.parentElement), node: n, i };
          o.w += r.width; o.k++; L.set(key, o);
        }
      }
    }
    for (const [blk, L] of lines) {
      const tops = [...L.keys()].sort((x, y) => x - y);
      const br = blk.getBoundingClientRect();
      tops.forEach(top => {
        const o = L.get(top);
        if (top > br.bottom - 20 && top === tops[tops.length - 1]) return;   // последняя строка абзаца
        res.lines++;
        const ratio = o.w / o.k / o.sp;
        if (ratio > %%LOOSE%%) {
          const txt = o.node.data, a = Math.max(0, o.i - 40);
          res.loose.push([pi + 1, Math.round(ratio * 100) / 100,
                          txt.slice(a, o.i + 40).replace(/\u00ad/g, '').replace(/\s+/g, ' ').trim()]);
        }
      });
    }
  });
  probe.remove();
  return res;
}
"""


def typo_report(t):
    """Текст отчёта о переносах и разрядке для вычитки."""
    out = [f'Переносы и разрядка — книга-preview-{N}.html (D-144)',
           f'Перенесено слов: {len(t["broken"])}. Строк по ширине: {t["lines"]}, '
           f'из них разреженных (пробел шире нормы в {LOOSE:g} раза и больше): {len(t["loose"])}.',
           '', 'ПЕРЕНЕСЁННЫЕ СЛОВА — лист, слово']
    out += [f'{p:4d}  {w}' for p, w in t['broken']]
    out += ['', 'ПЕРЕНЕСЕНЫ НА НОВЫЙ ЛИСТ, ЧТОБЫ НЕ ОСТАТЬСЯ ВНИЗУ ОДНИМИ — лист, начало (D-148)']
    out += [f'{p:4d}  {txt}' for p, txt in t['kept']]
    out += ['', 'РАЗРЕЖЕННЫЕ СТРОКИ — лист, пробел к норме, текст рядом']
    out += [f'{p:4d}  ×{r:.2f}  …{txt}…' for p, r, txt in t['loose']]
    return '\n'.join(out) + '\n'


def paged_check(html_path, shots=None, which=(), pdf_path=None):
    """Открыть HTML как читатель: дождаться раскладки, вернуть число листов, начала частей
    и колонтитулы. shots — папка для снимков листов с номерами из which (проверка глазами).
    pdf_path — напечатать готовые листы в PDF: он совпадает с просмотром лист в лист (D-133)."""
    from playwright.sync_api import sync_playwright
    with sync_playwright() as pw:
        b = pw.chromium.launch(args=['--force-color-profile=srgb'])
        pg = b.new_page(viewport={'width': 900, 'height': 1200})
        pg.goto('file://' + html_path)
        pg.wait_for_function("document.body.dataset.paged === '1'", timeout=180000)
        info = pg.evaluate('window.__book')
        info['heads'] = pg.evaluate("[...document.querySelectorAll('.page')].map(p => "
                                    "{ const s = p.querySelector('.hd .where'); return s ? s.textContent : ''; })")
        info['typo'] = pg.evaluate(TYPO_JS.replace('%%LOOSE%%', str(LOOSE)))
        for k in which:
            pg.locator('.page').nth(k - 1).screenshot(path=os.path.join(shots, f'p{k:02d}.png'))
        if pdf_path:
            pg.pdf(path=pdf_path, prefer_css_page_size=True, print_background=True)
        b.close()
    return info


def main():
    """python3 Книга.py SRC_ROOT OUT_DIR N [--pdf] [--slots] [--shots DIR p1,p2,...]
    --slots — места под ещё не сгенерированный арт показываются пунктиром с размером (D-156).
    Выходит книга-preview-N.html: в браузере она сама раскладывается на листы A4 (D-132).
    PDF — только с --pdf, когда правила готовы (D-129): печать тех же листов (D-133)."""
    global SRC, OUT, N
    argv = sys.argv[1:]
    want_pdf = '--pdf' in argv
    global SLOTS
    SLOTS = '--slots' in argv
    shots, which = None, ()
    if '--shots' in argv:
        i = argv.index('--shots')
        shots, which = argv[i + 1], tuple(int(x) for x in argv[i + 2].split(','))
        del argv[i:i + 3]
    args = [a for a in argv if a not in ('--pdf', '--slots')]
    SRC, OUT, N = os.path.abspath(args[0]), os.path.abspath(args[1]), args[2]
    md = open(os.path.join(SRC, 'rules/RULEBOOK.md'), encoding='utf-8').read()
    parts = build_body(parse(md))
    # HTML живёт в print/: пути к Fonts/ и Rulebook/ — от него. Проверяем из копии в SRC/print.
    tmp_html = os.path.join(SRC, 'print', f'книга-preview-{N}.html')
    final = build_html(parts)
    open(tmp_html, 'w', encoding='utf-8').write(final)
    open(os.path.join(OUT, f'книга-preview-{N}.html'), 'w', encoding='utf-8').write(final)
    pdf = os.path.join(OUT, f'книга-preview-{N}.pdf') if want_pdf else None
    info = paged_check(tmp_html, shots, which, pdf)
    print(f'просмотр: {info["pages"]} листов A4; начала частей: '
          + ', '.join(f'{k.replace("part-", "")}→{v}' for k, v in info['starts'].items()))
    t = info['typo']
    open(os.path.join(OUT, f'книга-preview-{N}-переносы.txt'), 'w', encoding='utf-8').write(typo_report(t))
    print(f'переносы: {len(t["broken"])} слов; разреженных строк: {len(t["loose"])} из {t["lines"]}; '
          f'заголовков на новый лист: {len(t["kept"])}')
    if pdf:
        n = int(re.search(r'Pages:\s+(\d+)', subprocess.run(['pdfinfo', pdf], capture_output=True,
                                                              text=True).stdout).group(1))
        print(f'PDF: {n} стр.', 'лист в лист с просмотром' if n == info['pages'] else 'РАСХОЖДЕНИЕ с просмотром')
    return info


if __name__ == '__main__':
    main()
