# -*- coding: utf-8 -*-
"""
Иллюстрации книги правил «Нефтяные войны» — схемы, ряды компонентов, значки.

ВСЕ ФАЙЛЫ В img/ ПРОИЗВОДНЫЕ (D-108). Руками их не править: поправить
исходник или этот скрипт и пересобрать. Генерируемый арт (обложка, Рой
для §11.6) сюда не входит — он лежит в art/ и делается по
«ПРОМПТЫ — арт книги.md».

Запуск — там, где есть Playwright + Chromium и poppler (pdftoppm). На ПК их
нет, сборка идёт в облачном контейнере Claude, как board/tools/master.py:

    python3 Иллюстрации.py SRC_ROOT OUT_DIR [имя ...]

SRC_ROOT — корень проекта. OUT_DIR — обычно print/Rulebook/img.
Без имён собирается всё; имена — из списка СБОРКА внизу файла.

Что из чего берётся (меняется исходник — пересобрать):

    planshet.svg       §1.3  планшет Островной Империи, выноски А–Ж
                             ← print/Faction-Card-A/Планшет — Островная Империя.html
    trek-nefti.svg     §4.2  трек запаса нефти, два состояния   ← тот же планшет
    polya.svg          §2.1  все поля, подпись — состав ← board/configs.yaml, board/geo/*.svg
    stol.svg           §2.2  схема стола             ← поле 5P, PDF треков, карт, жетонов, фигурки
    kuklovod.png       §6.3  кукловод — центр трека Судного дня ← art/doomsday/4 игрока v1.1.png
    primer-stol.svg    §2    стол на четверых после подготовки ← поле 4P-B, планшеты, фигурки
    istochniki-nefti.svg §4.1 пример: Александр получает нефть ← поле 5P, фигурки, жетоны
    zheton.svg         §5.2  две стороны жетона первого игрока ← acrylic/08
    bitva.svg          §8.11 примеры 1 и 2           ← board/geo/board-MC-5P.geojson
    roy.svg            §11.6 размещение Роя          ← то же поле
    komponenty-1.svg   §1.1  общие компоненты        ← print/Saved/*.pdf, acrylic/
    komponenty-2.svg   §1.2  компоненты фракции      ← планшет, карты, print/Units/
    frakcii.svg        §2.3  восемь фракций          ← acrylic/07. Жетоны-логотипы…/
    znak-*.png         §11   значки компонентов вариантов на поля
    konc-*.png         концовки частей: вырезки без нарисованной шахматки (D-139)
                             ← art/quartermaster-g1, -g2; нужен numpy
    valve.png          лист 18 — «Две стороны вентиля», просвет без обводки (D-146) ← art/valve-g1
    ref-duel.png       схема расстановки для генерации «Краб и Спрут» (D-156) ← print/Units, не в книге
    office.png         §9.2 — «Кабинет», светлее исходника: гамма 0,6 (D-160) ← art/office-g1
    truce.png          часть 10 — «Перемирие», светлее исходника: гамма 0,75 (D-164) ← art/truce-g1
    komiks-bitva.png   лист 32 — комикс «битва и после неё», две панели, просвет с наклоном 8° (D-161, D-162)
                             ← art/duel-g1, art/aftermath-g1

Размеры в мм. Ширина полосы набора — 170 мм; все схемы рассчитаны на неё.
Шрифты подключаются из print/Fonts по пути ../../Fonts/ — так SVG открывается
сам по себе и через <object>. В <img> шрифты не подгрузятся: это свойство
браузера, не файла.
"""
import base64
import io
import json
import math
import os
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

from PIL import Image, ImageChops, ImageFilter

# ══════════════════════════════════════════════════════════════ ПУТИ
SRC = None   # корень проекта, задаётся в main()
OUT = None


def p(*parts):
    return os.path.join(SRC, *parts)


ACR = 'acrylic'
ACR_LOGO = 'acrylic/07. Жетоны-логотипы, шестигранные - по 1шт - ⌀18мм'
CARD_HTML = 'print/Faction-Card-A/Планшет — Островная Империя.html'
SAVED = 'print/Saved'

# ══════════════════════════════════════════════════════════════ ОФОРМЛЕНИЕ
W = 170.0                      # ширина полосы набора, мм
INK = '#1E2A33'                # основной текст
MUTED = '#5B6873'              # подписи второго плана
ACCENT = '#EE688C'             # акцент книги
LAND = '#E9E5DD'
OCEAN = '#DCEBF2'
BORDER = '#A7B3BC'
KILL = '#E8205A'               # смерть — цвет наклейки kill.png, чуть темнее
SUPPRESS = '#B3A800'           # подавление — жёлтый наклейки, затемнён для белой бумаги
FONT_DIR = '../../Fonts/'      # от print/Rulebook/img/

FACTION_COLOR = {              # acrylic/ПРОМПТЫ — недостающий арт.md, «Цвета фракций»
    'Островная Империя': '#187830',
    'Эйркрафт Корпорейшн': '#00C0F0',
    'Глобал Петролеум': '#D8D800',
    'Братство Сингулярности': '#F0A800',
    'Клонэйд Ресёрч': '#C00030',
    'Moon Systems': '#D8DADE',
    'Сайнтифик Солюшн': '#BE31AE',
    'Североамериканский Альянс': '#904818',
}

STYLE = f"""
@font-face {{ font-family: 'Liberation Sans'; src: url('{FONT_DIR}LiberationSans-Regular.ttf'); }}
@font-face {{ font-family: 'Liberation Sans'; font-weight: bold; src: url('{FONT_DIR}LiberationSans-Bold.ttf'); }}
@font-face {{ font-family: 'OpenGostTypeB'; src: url('{FONT_DIR}OpenGostTypeB.ttf'); }}
@font-face {{ font-family: 'Rationale'; src: url('{FONT_DIR}Rationale-Regular.ttf'); }}
@font-face {{ font-family: 'Oil Wars'; src: url('{FONT_DIR}Oil Wars.ttf'); }}
text {{ font-family: 'Liberation Sans', sans-serif; fill: {INK}; }}
.h {{ font-family: 'OpenGostTypeB', sans-serif; letter-spacing: 0.04em; }}
.n {{ font-family: 'Rationale', sans-serif; }}
.g {{ font-family: 'Oil Wars'; }}
"""


def esc(s):
    return (str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            .replace('"', '&quot;'))


def f(v):
    return f'{v:.2f}'.rstrip('0').rstrip('.')


def svg_doc(w, h, body, title):
    return (f'<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<!-- ПРОИЗВОДНЫЙ ФАЙЛ: собирается print/Rulebook/Иллюстрации.py. Руками не править. -->\n'
            f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'width="{f(w)}mm" height="{f(h)}mm" viewBox="0 0 {f(w)} {f(h)}">\n'
            f'<title>{esc(title)}</title>\n<style>{STYLE}</style>\n'
            f'<defs><marker id="arrow" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="4" '
            f'markerHeight="4" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{INK}"/></marker>'
            f'<marker id="arrowA" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="4" '
            f'markerHeight="4" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="{ACCENT}"/></marker>'
            f'</defs>\n{body}\n</svg>\n')


def text(x, y, s, size=3.0, anchor='start', fill=INK, weight=None, cls=None, extra=''):
    a = f' text-anchor="{anchor}"' if anchor != 'start' else ''
    w = f' font-weight="{weight}"' if weight else ''
    c = f' class="{cls}"' if cls else ''
    fl = f' style="fill:{fill}"' if fill != INK else ''
    return f'<text x="{f(x)}" y="{f(y)}" font-size="{f(size)}"{a}{w}{c}{fl}{extra}>{esc(s)}</text>'


def lines(x, y, rows, size=3.0, lead=1.25, **kw):
    out = []
    for i, r in enumerate(rows):
        out.append(text(x, y + i * size * lead, r, size, **kw))
    return '\n'.join(out)


def img_uri(im, fmt='PNG', quality=90):
    buf = io.BytesIO()
    if fmt == 'JPEG':
        im.convert('RGB').save(buf, 'JPEG', quality=quality, optimize=True)
        mime = 'image/jpeg'
    else:
        im.save(buf, 'PNG', optimize=True)
        mime = 'image/png'
    return f'data:{mime};base64,' + base64.b64encode(buf.getvalue()).decode('ascii')


def image(im, x, y, w, h=None, dpi=300, fmt=None, extra=''):
    """Растр в SVG: ужимается до dpi на заданном размере, встраивается data URI."""
    if h is None:
        h = w * im.height / im.width
    px = max(1, int(round(w / 25.4 * dpi)))
    if im.width > px:
        im = im.resize((px, max(1, int(round(im.height * px / im.width)))), Image.LANCZOS)
    if fmt is None:
        fmt = 'PNG' if im.mode in ('RGBA', 'LA', 'P') else 'JPEG'
    return (f'<image x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" '
            f'preserveAspectRatio="xMidYMid meet" href="{img_uri(im, fmt)}"{extra}/>')


def badge(cx, cy, label, r=2.9, fill='#FFFFFF', ring=ACCENT, color=INK, size=None):
    size = size or r * 1.25
    return (f'<circle cx="{f(cx)}" cy="{f(cy)}" r="{f(r)}" fill="{fill}" stroke="{ring}" stroke-width="0.6"/>'
            + text(cx, cy + size * 0.36, label, size, anchor='middle', cls='h', fill=color, weight='bold'))


def write(name, data, binary=False):
    path = os.path.join(OUT, name)
    with open(path, 'wb' if binary else 'w', **({} if binary else {'encoding': 'utf-8'})) as fh:
        fh.write(data)
    print('  ', name, f'{os.path.getsize(path) / 1024:.0f} КБ')


# ══════════════════════════════════════════════════════════════ ИСТОЧНИКИ-РАСТРЫ
def load(rel):
    return Image.open(p(rel))


def trim(im, pad=0):
    """Обрезать прозрачные (или белые для RGB) поля."""
    if im.mode == 'RGBA':
        box = im.getchannel('A').point(lambda a: 255 if a > 8 else 0).getbbox()
    else:
        g = ImageChops.difference(im.convert('RGB'), Image.new('RGB', im.size, 'white')).convert('L')
        box = g.point(lambda v: 255 if v > 20 else 0).getbbox()
    if not box:
        return im
    l, t, r, b = box
    return im.crop((max(0, l - pad), max(0, t - pad), min(im.width, r + pad), min(im.height, b + pad)))


# Реальные размеры компонентов, мм (по мастерам print/Saved и акрилу) — для скругления
# углов и для поправки масштаба в рядах компонентов (D-126).
R_CARD = 3.5          # скругление карт, мм в натуральную величину
R_TOKEN = 5.5         # скругление жетонов фабрик


def rounded(im, real_w_mm, r_mm, inset_mm=0.0):
    """Скруглить углы картинки компонента. real_w_mm — ширина картинки в натуре
    (вместе с выпуском, если он есть), inset_mm — сколько выпуска срезать с каждой стороны."""
    im = im.convert('RGBA')
    k = im.width / real_w_mm                      # px на мм
    if inset_mm:
        d = int(round(inset_mm * k))
        im = im.crop((d, d, im.width - d, im.height - d))
    ss = 4
    mask = Image.new('L', (im.width * ss, im.height * ss), 0)
    from PIL import ImageDraw
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, im.width * ss - 1, im.height * ss - 1),
                                           radius=int(r_mm * k * ss), fill=255)
    mask = mask.resize(im.size, Image.LANCZOS)
    a = ImageChops.multiply(im.getchannel('A'), mask)
    im.putalpha(a)
    return im


def scale_mm(real_long_mm):
    """Длинная сторона компонента в ряду: не натуральные пропорции, а сжатые —
    крупное остаётся крупнее, мелкое не теряется (D-126). Трек Судного дня 142,5 мм → 27 мм."""
    return 27.0 * (real_long_mm / 142.5) ** 0.45


_pdf_cache = {}


def pdf_page(rel, page, dpi=200):
    key = (rel, page, dpi)
    if key not in _pdf_cache:
        with tempfile.TemporaryDirectory() as d:
            subprocess.run(['pdftoppm', '-r', str(dpi), '-f', str(page), '-l', str(page), '-png',
                            p(rel), os.path.join(d, 'x')], check=True)
            fn = [x for x in os.listdir(d) if x.endswith('.png')][0]
            _pdf_cache[key] = Image.open(os.path.join(d, fn)).convert('RGB')
    return _pdf_cache[key]


def content_box(im, thr=200, frac=0.5):
    """Габарит плотного содержимого листа: строки и столбцы, где тёмного больше
    половины. Тонкие метки реза в него не попадают."""
    g = im.convert('L').point(lambda v: 255 if v < thr else 0)
    w, h = g.size
    px = g.load()
    cols = [sum(1 for y in range(0, h, 3) if px[x, y]) / (h / 3) for x in range(w)]
    rows = [sum(1 for x in range(0, w, 3) if px[x, y]) / (w / 3) for y in range(h)]
    xs = [i for i, v in enumerate(cols) if v > frac * max(cols)]
    ys = [i for i, v in enumerate(rows) if v > frac * max(rows)]
    return xs[0], ys[0], xs[-1] + 1, ys[-1] + 1


def grid_cell(im, cols, rows, col, row, inset=0.0):
    """Ячейка сетки карт или жетонов на листе мастера (листы без зазоров)."""
    x0, y0, x1, y1 = content_box(im)
    cw, ch = (x1 - x0) / cols, (y1 - y0) / rows
    l = x0 + col * cw + inset * cw
    t = y0 + row * ch + inset * ch
    return im.crop((int(l), int(t), int(l + cw * (1 - 2 * inset)), int(t + ch * (1 - 2 * inset))))


def tint(rel, color, outline='#1E2A33', ow=3, h_px=200):
    """Силуэт отряда в цвет фракции с тёмной обводкой — читается на светлой карте."""
    src = Image.open(p(rel)).convert('RGBA')
    src = trim(src)
    k = h_px / src.height
    src = src.resize((max(1, int(src.width * k)), h_px), Image.LANCZOS)
    pad = ow * 2
    a = Image.new('L', (src.width + 2 * pad, src.height + 2 * pad), 0)
    a.paste(src.getchannel('A'), (pad, pad))
    a = a.point(lambda v: 255 if v > 90 else 0)
    ring = a.filter(ImageFilter.MaxFilter(ow * 2 + 1))
    out = Image.new('RGBA', a.size, (0, 0, 0, 0))
    out.paste(Image.new('RGBA', a.size, outline), (0, 0), ring)
    out.paste(Image.new('RGBA', a.size, color), (0, 0), a)
    return out


# ══════════════════════════════════════════════════════════════ ПЛАНШЕТ
_card = {}


def card_render():
    """Лицо планшета Островной Империи в 3× и координаты зон в мм планшета."""
    if _card:
        return _card
    from playwright.sync_api import sync_playwright
    url = 'file://' + p(CARD_HTML)
    with sync_playwright() as pw:
        b = pw.chromium.launch(args=['--force-color-profile=srgb'])
        pg = b.new_page(viewport={'width': 1400, 'height': 1000}, device_scale_factor=3)
        pg.goto(url)
        pg.evaluate('document.fonts.ready')
        pg.wait_for_timeout(500)
        card = pg.locator('.card').first
        png = card.screenshot()
        info = pg.evaluate("""() => {
          const c = document.querySelector('.card').getBoundingClientRect();
          const r = s => [...document.querySelectorAll(s)].map(e => {
              const b = e.getBoundingClientRect();
              return {x:b.x-c.x, y:b.y-c.y, w:b.width, h:b.height, t:(e.innerText||'').trim()}; });
          return {cw:c.width, ch:c.height,
            name:r('.card:not(.back) .faction-name'), track:r('.card:not(.back) .track'),
            hex:r('.card:not(.back) .hex'), logo:r('.card:not(.back) .logo-wm'),
            titles:r('.card:not(.back) .block-title'), prep:r('.card:not(.back) .prep-note'),
            steps:r('.card:not(.back) .steps'), abil:r('.card:not(.back) .col-abil'),
            table:r('.card:not(.back) .units-table'), glabel:r('.card:not(.back) .group-label'),
            caps:r('.card:not(.back) .unit-cap'), decor:r('.card:not(.back) .decor-abs'),
            blocks:r('.card:not(.back) .block-text'), abilities:r('.card:not(.back) .ability') };
        }""")
        b.close()
    im = Image.open(io.BytesIO(png)).convert('RGB')
    k = 240.0 / info['cw']                     # css px → мм планшета (240 × 170)

    def mm(o):
        return {'x': o['x'] * k, 'y': o['y'] * k, 'w': o['w'] * k, 'h': o['h'] * k, 't': o['t']}
    zones = {key: [mm(o) for o in val] for key, val in info.items() if isinstance(val, list)}
    _card.update(im=im, z=zones, w=240.0, h=info['ch'] * k)
    return _card


def build_planshet():
    """§1.3 — зоны А–Ж обведены на планшете, буквы — на полях слева и справа,
    чтобы не закрывать текст планшета (в оригинале буквы стоят прямо на нём, с. 12)."""
    c = card_render()
    z = c['z']
    M = 8.0                                     # поле под буквы с каждой стороны
    cw = W - 2 * M
    s = cw / c['w']
    H = c['h'] * s
    out = [image(c['im'], M, 0, cw, H, dpi=330, fmt='JPEG')]

    def R(x, y, w, h):
        return M + x * s, y * s, w * s, h * s

    def frame(x, y, w, h, pad=1.0):
        X, Y, Ww, Hh = R(x - pad, y - pad, w + 2 * pad, h + 2 * pad)
        out.append(f'<rect x="{f(X)}" y="{f(Y)}" width="{f(Ww)}" height="{f(Hh)}" rx="1.2" '
                   f'fill="none" stroke="{ACCENT}" stroke-width="0.45" stroke-dasharray="1.6 0.9"/>')
        return X, Y, Ww, Hh

    def left(letter, X, y):
        bx = M / 2 - 0.4
        out.append(f'<line x1="{f(bx + 2.8)}" y1="{f(y)}" x2="{f(X)}" y2="{f(y)}" stroke="{ACCENT}" stroke-width="0.45"/>')
        out.append(badge(bx, y, letter, r=2.8))

    def right(letter, X, y):
        bx = W - M / 2 + 0.4
        out.append(f'<line x1="{f(X)}" y1="{f(y)}" x2="{f(bx - 2.8)}" y2="{f(y)}" stroke="{ACCENT}" stroke-width="0.45"/>')
        out.append(badge(bx, y, letter, r=2.8))

    # Буквы — сверху вниз, сначала левая сторона, затем правая (D-126).
    # А — трек запаса нефти
    t = z['track'][0]
    X, Y, Ww, Hh = frame(t['x'], t['y'], t['w'], t['h'], pad=0.6)
    left('А', X, Y + Hh / 2)
    # Б — название и логотип фракции (логотип не обводится — каша)
    n = z['name'][0]
    X, Y, Ww, Hh = frame(n['x'], n['y'], n['w'] * 0.62, n['h'], pad=0.8)
    left('Б', X, Y + Hh / 2)
    # В — начальные силы и стартовый регион: от «Подготовки» до примечания
    t0 = z['titles'][0]
    pn = z['prep'][0]
    X, Y, Ww, Hh = frame(t0['x'], t0['y'], t0['w'], pn['y'] + pn['h'] - t0['y'])
    left('В', X, Y + Hh / 2)
    # Г — создание боевого робота
    t1 = z['titles'][1]
    st = z['steps'][0]
    X, Y, Ww, Hh = frame(t1['x'], t1['y'], t1['w'], st['y'] + st['h'] - t1['y'])
    left('Г', X, Y + Hh / 2)
    # Д — средняя колонка свойств: от первого свойства до конца последнего
    ab = z['abilities']
    a0, a1 = ab[0], ab[-1]
    X, Y, Ww, Hh = frame(a0['x'], a0['y'], a0['w'], a1['y'] + a1['h'] - a0['y'], pad=0.8)
    out.append(f'<line x1="{f(X + Ww / 2)}" y1="{f(Y + Hh)}" x2="{f(X + Ww / 2)}" y2="{f(Y + Hh + 2.2)}" '
               f'stroke="{ACCENT}" stroke-width="0.45"/>')
    out.append(badge(X + Ww / 2, Y + Hh + 4.6, 'Д', r=2.6))
    # Е — пехотинцы и боевые машины
    gl = z['glabel']
    tb = z['table'][0]
    top = z['caps'][0]['y'] - 6
    X, Y, Ww, Hh = frame(tb['x'], top, tb['w'], gl[1]['y'] + gl[1]['h'] - top + 0.5, pad=0.6)
    right('Е', X + Ww, Y + Hh / 2)
    # Ж — боевой робот: строка таблицы
    br = gl[2]
    X2, Y2, W2, H2 = frame(tb['x'], br['y'] - 1.5, tb['w'], br['h'] + 3.5, pad=0.6)
    right('Ж', X2 + W2, Y2 + H2 / 2)

    write('planshet.svg', svg_doc(W, H, '\n'.join(out), 'Планшет фракции: выноски А–Ж (§1.3)'))


def build_trek():
    """§4.2 — оборачивание трека: 23 → маркер на 3; 21 − 1 → маркер на 20."""
    c = card_render()
    z = c['z']
    k = c['im'].width / c['w']                 # px растра на мм планшета
    t = z['track'][0]
    crop = c['im'].crop((int(t['x'] * k) - 4, int(t['y'] * k) - 4,
                         int((t['x'] + t['w']) * k) + 4, int((t['y'] + t['h']) * k) + 4))
    tw = W - 2.0
    s = tw / (t['w'] + 8 / k)
    th = crop.height / crop.width * tw
    hexes = {h['t']: h for h in z['hex']}

    def hex_xy(num, ox, oy):
        h = hexes[str(num)]
        return ox + (h['x'] - t['x'] + 4 / k + h['w'] / 2) * s, oy + (h['y'] - t['y'] + 4 / k + h['h'] / 2) * s

    barrel = open(p('print/icons/oil-barrel.svg'), encoding='utf-8').read()
    barrel_uri = 'data:image/svg+xml;base64,' + base64.b64encode(barrel.encode('utf-8')).decode('ascii')

    def marker(num, ox, oy, ghost=False):
        """Бочонок стоит на делении, но смещён вверх-вправо, чтобы число было видно."""
        h = hexes[str(num)]
        cx, cy = hex_xy(num, ox, oy)
        cx += h['w'] * s * (0.30 if num < 19 else -0.34)
        cy -= h['h'] * s * 0.30
        r = 3.1
        op = ' opacity="0.5"' if ghost else ''
        dash = ' stroke-dasharray="1.0 0.7"' if ghost else ''
        return (f'<g{op}><circle cx="{f(cx)}" cy="{f(cy)}" r="{f(r)}" fill="#FFFFFF" stroke="{ACCENT}" '
                f'stroke-width="0.7"{dash}/>'
                f'<image x="{f(cx - r * 0.62)}" y="{f(cy - r * 0.7)}" width="{f(r * 1.24)}" height="{f(r * 1.4)}" '
                f'href="{barrel_uri}"/></g>'), (cx, cy)

    def head(y, bold, rest):
        return (f'<text x="0" y="{f(y)}" font-size="3.0"><tspan class="h" font-size="3.4" font-weight="bold">'
                f'{esc(bold)}</tspan><tspan style="fill:{MUTED}"> — {esc(rest)}</tspan></text>')

    out = []
    y = 4.5
    out.append(head(y, 'Запас 23', 'маркер стоит на делении 3 — второй круг трека.'))
    y0 = y + 4.0
    out.append(image(crop, 1, y0, tw, th, dpi=330, fmt='JPEG'))
    out.append(marker(3, 1, y0)[0])
    y = y0 + th + 9
    out.append(head(y, 'Запас 21, трата 1', 'запас 20 — маркер ставят на деление 20, а не на 0.'))
    y1 = y + 4.0
    out.append(image(crop, 1, y1, tw, th, dpi=330, fmt='JPEG'))
    g1, (ax, ay) = marker(1, 1, y1, ghost=True)
    g2, (bx, by) = marker(20, 1, y1)
    out += [g1, g2]
    # дуга под треком: от 1 к 20
    ax0, ay0 = hex_xy(1, 1, y1)
    bx0, by0 = hex_xy(20, 1, y1)
    base = y1 + th + 1.2
    out.append(f'<path d="M{f(ax0)},{f(base)} C{f(ax0 + 20)},{f(base + 7)} {f(bx0 - 20)},{f(base + 7)} '
               f'{f(bx0)},{f(base + 0.4)}" fill="none" stroke="{ACCENT}" stroke-width="0.6" marker-end="url(#arrowA)"/>')
    H = base + 7
    write('trek-nefti.svg', svg_doc(W, H, '\n'.join(out), 'Трек запаса нефти: как оборачивать (§4.2)'))


# ══════════════════════════════════════════════════════════════ ПОЛЕ
SVGNS = '{http://www.w3.org/2000/svg}'


def board_regions_svg(rel):
    """Из SVG поля — только заливки регионов и острова, без размытий, подписей и знаков."""
    root = ET.parse(p(rel)).getroot()
    vb = root.get('viewBox').split()
    vw, vh = float(vb[2]), float(vb[3])
    parts = []
    for g in root.findall(SVGNS + 'g'):
        if g.get('id') in ('deco', 'symbols', 'names'):
            continue
        for e in g:
            if e.tag == SVGNS + 'path' and e.get('class') in ('oc', 'ld'):
                parts.append(f'<path d="{e.get("d")}" fill="{e.get("fill")}" fill-rule="evenodd"/>')
    return vw, vh, parts


def board_thumb(rel, x, y, w):
    vw, vh, parts = board_regions_svg(rel)
    s = w / vw
    body = ''.join(parts)
    return (f'<g transform="translate({f(x)},{f(y)}) scale({s:.5f})">'
            f'<g stroke="#FFFFFF" stroke-width="{f(0.35 / s)}" stroke-linejoin="round">{body}</g></g>'
            f'<rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(vh * s)}" fill="none" '
            f'stroke="{BORDER}" stroke-width="0.3"/>'), vh * s


def players_word(n):
    return f'{n} игрок' + ('а' if n % 10 in (2, 3, 4) and n % 100 not in (12, 13, 14) else 'ов')


def build_polya():
    """§2.1 — все версии поля сеткой по два, под каждым — состав (D-129).
    Список полей — из board/configs.yaml: появится новое поле — оно встанет само."""
    import yaml
    cfg = yaml.safe_load(open(p('board/configs.yaml'), encoding='utf-8'))['configs']
    tw, gx, gy = 74.0, 8.0, 5.0
    x0 = (W - 2 * tw - gx) / 2
    out = []
    y = 1.0
    for i in range(0, len(cfg), 2):
        row_h = 0
        for j, c in enumerate(cfg[i:i + 2]):
            x = x0 + j * (tw + gx)
            svg, h = board_thumb(f'board/geo/board-{c["id"]}.svg', x, y, tw)
            out.append(f'<g data-config="{c["id"]}">{svg}'
                       f'{text(x + tw / 2, y + h + 4.2, players_word(c["players"]), 3.0, anchor="middle", weight="bold")}</g>')
            row_h = max(row_h, h)
        y += row_h + 4.2 + gy
    write('polya.svg', svg_doc(W, y - gy + 1.5, '\n'.join(out), 'Версии игрового поля (§2.1)'))


# ── геометрия регионов (мм полотна 900 × 550) ─────────────────────────────
_geo = {}


def geo(cfg='5P'):
    if cfg not in _geo:
        gj = json.load(open(p(f'board/geo/board-MC-{cfg}.geojson'), encoding='utf-8'))
        graph = json.load(open(p(f'board/derived/MC-{cfg}.json'), encoding='utf-8'))
        reg = {}
        for ft in gj['features']:
            gm = ft['geometry']
            polys = gm['coordinates'] if gm['type'] == 'MultiPolygon' else [gm['coordinates']]
            reg[ft['properties']['id']] = {'name': ft['properties']['name_ru'],
                                           'type': ft['properties']['type'], 'polys': polys}
        nb = {v['id']: v['neighbours'] for v in graph['vertices']}
        _geo[cfg] = (reg, nb)
    return _geo[cfg]


def rid_by_name(cfg, name):
    reg, _ = geo(cfg)
    return [k for k, v in reg.items() if v['name'] == name][0]


def inside(pt, polys):
    x, y = pt
    for poly in polys:
        hit = False
        for ring in poly:
            n = len(ring)
            c = False
            for i in range(n):
                x1, y1 = ring[i]
                x2, y2 = ring[(i + 1) % n]
                if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1 + 1e-12) + x1:
                    c = not c
            if ring is poly[0]:
                hit = c
            elif c:
                hit = False
        if hit:
            return True
    return False


def seg_dist(px, py, x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    L = dx * dx + dy * dy
    t = 0 if L == 0 else max(0, min(1, ((px - x1) * dx + (py - y1) * dy) / L))
    return math.hypot(px - x1 - t * dx, py - y1 - t * dy)


def edge_dist(pt, polys):
    best = 1e9
    for poly in polys:
        for ring in poly:
            for i in range(len(ring) - 1):
                d = seg_dist(pt[0], pt[1], *ring[i], *ring[i + 1])
                if d < best:
                    best = d
    return best


def label_point(polys, win, step=3.0):
    """Самая «глубокая» точка региона в окне — туда ставятся подпись и фигурки."""
    x0, y0, x1, y1 = win
    best, bp = -1, None
    for poly in polys:
        xs = [q[0] for q in poly[0]]
        ys = [q[1] for q in poly[0]]
        ax0, ay0 = max(x0, min(xs)), max(y0, min(ys))
        ax1, ay1 = min(x1, max(xs)), min(y1, max(ys))
        if ax0 >= ax1 or ay0 >= ay1:
            continue
        yy = ay0 + step / 2
        while yy < ay1:
            xx = ax0 + step / 2
            while xx < ax1:
                if inside((xx, yy), [poly]):
                    d = min(edge_dist((xx, yy), [poly]), xx - x0, x1 - xx, yy - y0, y1 - yy)
                    if d > best:
                        best, bp = d, (xx, yy)
                xx += step
            yy += step
    return bp, best


def shared_mid(cfg, a, b):
    """Середина общей границы двух регионов (общие вершины совпадают точно)."""
    reg, _ = geo(cfg)
    va = {(round(x, 2), round(y, 2)) for poly in reg[a]['polys'] for ring in poly for x, y in ring}
    vb = {(round(x, 2), round(y, 2)) for poly in reg[b]['polys'] for ring in poly for x, y in ring}
    common = list(va & vb)
    if not common:
        return None
    common.sort()
    mx = sum(q[0] for q in common) / len(common)
    my = sum(q[1] for q in common) / len(common)
    # точка общей границы, ближайшая к среднему, — чтобы не попасть в пустоту
    return min(common, key=lambda q: (q[0] - mx) ** 2 + (q[1] - my) ** 2)


class MapPanel:
    """Врезка карты: окно полотна (мм поля) → прямоугольник в полосе."""

    def __init__(self, cfg, win, x, y, w, h):
        self.cfg, self.win = cfg, win
        self.x, self.y, self.w, self.h = x, y, w, h
        wx0, wy0, wx1, wy1 = win
        self.s = min(w / (wx1 - wx0), h / (wy1 - wy0))
        self.ox = x + (w - (wx1 - wx0) * self.s) / 2
        self.oy = y + (h - (wy1 - wy0) * self.s) / 2

    def P(self, pt):
        return self.ox + (pt[0] - self.win[0]) * self.s, self.oy + (pt[1] - self.win[1]) * self.s

    def draw(self, style=None, names=None, uid='m'):
        reg, _ = geo(self.cfg)
        style = style or {}
        clip = f'clip{uid}'
        out = [f'<clipPath id="{clip}"><rect x="{f(self.x)}" y="{f(self.y)}" width="{f(self.w)}" '
               f'height="{f(self.h)}" rx="1.5"/></clipPath><g clip-path="url(#{clip})">',
               f'<rect x="{f(self.x)}" y="{f(self.y)}" width="{f(self.w)}" height="{f(self.h)}" fill="{OCEAN}"/>']
        order = sorted(reg, key=lambda r: 0 if reg[r]['type'] == 'OCEAN' else 1)
        for rid in order:
            r = reg[rid]
            fill = style.get(rid, {}).get('fill', OCEAN if r['type'] == 'OCEAN' else LAND)
            stroke = style.get(rid, {}).get('stroke', BORDER)
            sw = style.get(rid, {}).get('sw', 0.3)
            d = ''
            for poly in r['polys']:
                for ring in poly:
                    pts = [self.P(q) for q in ring]
                    d += 'M' + ' L'.join(f'{f(a)},{f(b)}' for a, b in pts) + 'Z'
            out.append(f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" '
                       f'fill-rule="evenodd" stroke-linejoin="round"/>')
        # край поля, если окно до него доходит: за ним — пусто
        CW, CH = 900.0, 550.0
        x0, y0 = self.P((0, 0))
        x1, y1 = self.P((CW, CH))
        # левый и правый края склеены (это не край мира), поэтому только верх и низ
        for side, cond in (('t', self.win[1] <= 0), ('b', self.win[3] >= CH)):
            if not cond:
                continue
            if side == 'l':
                out.append(f'<rect x="{f(self.x)}" y="{f(self.y)}" width="{f(max(0, x0 - self.x))}" height="{f(self.h)}" fill="#FFFFFF"/>')
                out.append(f'<line x1="{f(x0)}" y1="{f(self.y)}" x2="{f(x0)}" y2="{f(self.y + self.h)}" stroke="{INK}" stroke-width="0.7"/>')
            if side == 'r':
                out.append(f'<rect x="{f(x1)}" y="{f(self.y)}" width="{f(max(0, self.x + self.w - x1))}" height="{f(self.h)}" fill="#FFFFFF"/>')
                out.append(f'<line x1="{f(x1)}" y1="{f(self.y)}" x2="{f(x1)}" y2="{f(self.y + self.h)}" stroke="{INK}" stroke-width="0.7"/>')
            if side == 't':
                out.append(f'<rect x="{f(self.x)}" y="{f(self.y)}" width="{f(self.w)}" height="{f(max(0, y0 - self.y))}" fill="#FFFFFF"/>')
                out.append(f'<line x1="{f(self.x)}" y1="{f(y0)}" x2="{f(self.x + self.w)}" y2="{f(y0)}" stroke="{INK}" stroke-width="0.7"/>')
            if side == 'b':
                out.append(f'<rect x="{f(self.x)}" y="{f(y1)}" width="{f(self.w)}" height="{f(max(0, self.y + self.h - y1))}" fill="#FFFFFF"/>')
                out.append(f'<line x1="{f(self.x)}" y1="{f(y1)}" x2="{f(self.x + self.w)}" y2="{f(y1)}" stroke="{INK}" stroke-width="0.7"/>')
        out.append('</g>')
        out.append(f'<rect x="{f(self.x)}" y="{f(self.y)}" width="{f(self.w)}" height="{f(self.h)}" rx="1.5" '
                   f'fill="none" stroke="{BORDER}" stroke-width="0.35"/>')
        return '\n'.join(out)

    def anchor(self, rid, near=None, depth=4.5, margin=5.0):
        """Точка внутри региона, в окне, не ближе depth мм полосы к границе региона
        и margin мм к краю врезки; near — тянуть к точке (мм поля)."""
        reg, _ = geo(self.cfg)
        win = self.win
        dmin = depth / self.s
        m = margin / self.s
        polys = reg[rid]['polys']
        if near:
            nx, ny = near
            for rad in range(4, 160, 4):
                best = None
                for ang in range(0, 360, 10):
                    q = (nx + rad * math.cos(math.radians(ang)), ny + rad * math.sin(math.radians(ang)))
                    if not (win[0] + m < q[0] < win[2] - m and win[1] + m < q[1] < win[3] - m):
                        continue
                    if inside(q, polys):
                        dd = edge_dist(q, polys)
                        if dd >= dmin and (best is None or dd > best[1]):
                            best = (q, dd)
                if best:
                    return best[0]
        return label_point(polys, (win[0] + m, win[1] + m, win[2] - m, win[3] - m))[0]


def spot(mp, rid, toward, avoid=(), depth=4.0, margin=4.0, clear=8.0, step=4.0):
    for d, c in ((depth, clear), (depth * 0.7, clear * 0.75), (depth * 0.5, clear * 0.55)):
        r = _spot(mp, rid, toward, avoid, d, margin, c, step)
        if r:
            return r
    return mp.P(mp.anchor(rid))


def _spot(mp, rid, toward, avoid, depth, margin, clear, step):
    """Место для фигурки в регионе rid: не ближе depth мм к его границе, clear мм
    от точек avoid (подписи, другие фигурки) и как можно ближе к toward. Всё в мм полосы."""
    reg, _ = geo(mp.cfg)
    polys = reg[rid]['polys']
    dmin = depth / mp.s
    best = None
    x0, y0, x1, y1 = mp.win
    yy = y0 + step / 2
    while yy < y1:
        xx = x0 + step / 2
        while xx < x1:
            X, Y = mp.P((xx, yy))
            if (mp.x + margin < X < mp.x + mp.w - margin and mp.y + margin < Y < mp.y + mp.h - margin
                    and all(math.hypot(X - a, Y - b) > clear for a, b in avoid)
                    and inside((xx, yy), polys)):
                ed = edge_dist((xx, yy), polys)
                if ed < dmin:
                    xx += step
                    continue
                dd = math.hypot(X - toward[0], Y - toward[1]) - 1.5 * min(ed * mp.s, 8.0)
                if best is None or dd < best[0]:
                    best = (dd, (X, Y))
            xx += step
        yy += step
    return best[1] if best else None


def region_label(mp, rid, pt=None, size=2.5, fill=MUTED, dy=0):
    reg, _ = geo(mp.cfg)
    pt = pt or mp.anchor(rid)
    x, y = mp.P(pt)
    words = reg[rid]['name'].split(' ')
    # перенос в две строки по середине
    if len(reg[rid]['name']) > 14 and len(words) > 1:
        cut = max(range(1, len(words)), key=lambda i: -abs(len(' '.join(words[:i])) - len(' '.join(words[i:]))))
        rows = [' '.join(words[:cut]), ' '.join(words[cut:])]
    else:
        rows = [reg[rid]['name']]
    out = []
    for i, r in enumerate(rows):
        out.append(text(x, y + dy + i * size * 1.15, r, size, anchor='middle', fill=fill,
                        extra=' paint-order="stroke" stroke="#FFFFFF" stroke-width="0.6" stroke-opacity="0.8"'))
    return '\n'.join(out)


# ══════════════════════════════════════════════════════════════ БИТВА
UNIT_H = {'Танк МЕГ-01': 4.8, 'Морпех': 6.4, 'Цунами': 6.4, 'Фантом': 4.4, 'Дрон': 4.0, 'Рекрут ЭК': 5.6}
UNIT = {
    'Танк МЕГ-01': ('print/Units/ОстровнаяИмперия/Мегалодон.png', 'Островная Империя'),
    'Морпех': ('print/Units/ОстровнаяИмперия/Морпех.png', 'Островная Империя'),
    'Цунами': ('print/Units/ОстровнаяИмперия/Цунами.png', 'Островная Империя'),
    'Фантом': ('print/Units/Эйркрафт Корпорейшн/Фантом.png', 'Эйркрафт Корпорейшн'),
    'Дрон': ('print/Units/Эйркрафт Корпорейшн/Ночной призрак.png', 'Эйркрафт Корпорейшн'),
    'Рекрут ЭК': ('print/Units/adept.png', 'Эйркрафт Корпорейшн'),
}
_tinted = {}


def unit_img(key):
    if key not in _tinted:
        rel, fac = UNIT[key]
        _tinted[key] = tint(rel, FACTION_COLOR[fac])
    return _tinted[key]


def factory_token():
    if 'factory' not in _tinted:
        im = pdf_page(f'{SAVED}/Factory Tokens.pdf', 1, 150)
        _tinted['factory'] = rounded(grid_cell(im, 4, 6, 0, 0), 43.5, R_TOKEN)
    return _tinted['factory']


def put_unit(key, cx, cy, h=7.0):
    im = unit_img(key)
    w = h * im.width / im.height
    return image(im, cx - w / 2, cy - h / 2, w, h, dpi=360, fmt='PNG'), w


def result_badge(cx, cy, kind):
    col = KILL if kind == 'K' else SUPPRESS
    return (f'<circle cx="{f(cx)}" cy="{f(cy)}" r="2.1" fill="#FFFFFF" stroke="{col}" stroke-width="0.5"/>'
            + text(cx, cy + 1.05, kind, 2.9, anchor='middle', cls='g', fill=col))


def cross(cx, cy, r=3.2):
    return (f'<path d="M{f(cx - r)},{f(cy - r)} L{f(cx + r)},{f(cy + r)} M{f(cx + r)},{f(cy - r)} '
            f'L{f(cx - r)},{f(cy + r)}" stroke="{KILL}" stroke-width="0.8" stroke-linecap="round"/>')


def arrow(x1, y1, x2, y2, bend=0.25, col=INK):
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    nx, ny = -(y2 - y1) * bend, (x2 - x1) * bend
    mk = 'arrowA' if col == ACCENT else 'arrow'
    return (f'<path d="M{f(x1)},{f(y1)} Q{f(mx + nx)},{f(my + ny)} {f(x2)},{f(y2)}" fill="none" '
            f'stroke="{col}" stroke-width="0.55" marker-end="url(#{mk})"/>')


def dice_row(x, y, faces, size=4.2):
    out = []
    for i, v in enumerate(faces):
        X = x + i * (size + 1.2)
        out.append(f'<rect x="{f(X)}" y="{f(y)}" width="{f(size)}" height="{f(size)}" rx="0.8" '
                   f'fill="#FFFFFF" stroke="{INK}" stroke-width="0.35"/>')
        out.append(text(X + size / 2, y + size * 0.78, str(v), size * 0.82, anchor='middle', cls='n'))
        res = 'K' if v == 6 else ('S' if v in (4, 5) else '')
        if res:
            out.append(text(X + size / 2, y + size + 3.6, res, 3.2, anchor='middle', cls='g',
                            fill=KILL if res == 'K' else SUPPRESS))
        else:
            out.append(text(X + size / 2, y + size + 3.0, '–', 2.6, anchor='middle', fill=MUTED))
    return '\n'.join(out), len(faces) * (size + 1.2)


def build_bitva():
    """§8.11, примеры 1 и 2: Южная Азия, Александр (ОИ) против Ильи (ЭК)."""
    cfg = '5P'
    reg, nb = geo(cfg)
    asis = rid_by_name(cfg, 'Южная Азия')
    nbs = nb[asis]
    pw, ph = (W - 6) / 2, 62.0
    win = (620, 118, 900, 118 + 280 * ph / pw)
    out = []
    head = 5.0
    panels = [(0, head), (pw + 6, head), (0, head + ph + 24), (pw + 6, head + ph + 24)]
    titles = ['1. Битва объявлена', '2. Броски и назначение', '3. Применение и отступление',
              'Пример 2. Отступать некуда']
    S = {asis: {'fill': '#F6DCE3', 'stroke': ACCENT, 'sw': 0.6}}
    mps = []
    for i, (px, py) in enumerate(panels):
        mp = MapPanel(cfg, win, px, py, pw, ph)
        mps.append(mp)
        out.append(text(px, py - 1.6, titles[i], 3.1, cls='h', weight='bold'))
        style = dict(S)
        out.append(mp.draw(style, uid=f'b{i}'))
        for r in nbs:
            out.append(region_label(mp, r))
    lab_pts = []
    for r in nbs:                               # подпись занимает ширину: три точки на строку
        lx, ly_ = mps[0].P(mps[0].anchor(r))
        lab_pts += [(lx - 6, ly_), (lx, ly_), (lx + 6, ly_), (lx, ly_ + 3)]
    ind = rid_by_name(cfg, 'Индийский океан')
    # куда тянуть фигурку в соседнем регионе: в сторону открытой части этого региона
    pull = {ind: (-24, 18), rid_by_name(cfg, 'Север Тихого океана'): (30, 2),
            rid_by_name(cfg, 'Северная Азия'): (-24, -2), rid_by_name(cfg, 'Аравийский полуостров'): (-28, 6)}
    toward = lambda r, X, Y: (X + pull.get(r, (0, 0))[0], Y + pull.get(r, (0, 0))[1])
    # точки внутри Южной Азии: центр и раскладка двух групп
    c0, _ = label_point(reg[asis]['polys'], win, step=2.0)
    # раскладка фигурок — в мм полосы от центра Южной Азии на панели
    g_alex = [(-7.0, -13.0), (3.5, -13.0), (12.0, -13.0)]
    g_ilya = [(-6.5, -1.5), (6.0, -1.5), (-6.5, 9.0), (6.5, 8.5)]
    alex = ['Танк МЕГ-01', 'Морпех', 'Морпех']
    ilya = ['Фантом', 'Дрон', 'Дрон', 'Рекрут ЭК']

    def units(mp, which, marks=None, gone=(), moved=None):
        """which: 'alex'/'ilya'; marks: {idx: 'K'|'S'}; gone: убранные; moved: {idx: rid}"""
        res = []
        pts, keys = (g_alex, alex) if which == 'alex' else (g_ilya, ilya)
        CX, CY = mp.P(c0)
        for i, (q, key) in enumerate(zip(pts, keys)):
            if i in gone:
                continue
            X, Y = CX + q[0], CY + q[1]
            if key == 'Рекрут ЭК':
                fac = factory_token()
                res.append(image(fac, X - 3.6, Y - 1.2, 7.2, 7.2, dpi=300, fmt='PNG'))
                im, _ = put_unit(key, X, Y - 1.6, h=UNIT_H[key])
                res.append(im)
                continue
            im, w = put_unit(key, X, Y, h=UNIT_H[key])
            res.append(im)
            if marks and i in marks:
                res.append(result_badge(X, Y - UNIT_H[key] / 2 - 2.4, marks[i]))
        return '\n'.join(res)

    # панель 1 — расстановка
    out.append(units(mps[0], 'alex'))
    out.append(units(mps[0], 'ilya'))
    # панель 2 — результаты назначены
    out.append(units(mps[1], 'alex', marks={1: 'K'}))
    out.append(units(mps[1], 'ilya', marks={0: 'S', 1: 'K', 2: 'S'}))
    # панель 3 — убитые убраны, подавленные отступают
    out.append(units(mps[2], 'alex', gone=(1,)))
    out.append(units(mps[2], 'ilya', gone=(0, 1, 2)))
    tgt = {0: rid_by_name(cfg, 'Северная Азия'), 2: rid_by_name(cfg, 'Индийский океан')}
    CX, CY = mps[2].P(c0)
    dy = mps[2].y - mps[0].y
    avoid = [(a, b + dy) for a, b in lab_pts]
    for i, r in tgt.items():
        X0, Y0 = CX + g_ilya[i][0], CY + g_ilya[i][1]
        X1, Y1 = spot(mps[2], r, toward(r, X0, Y0), avoid=avoid, depth=6.0 if r == ind else 3.5)
        avoid.append((X1, Y1))
        im, _ = put_unit(ilya[i], X1, Y1, h=UNIT_H[ilya[i]])
        out.append(f'<g opacity="0.35">{put_unit(ilya[i], X0, Y0, h=UNIT_H[ilya[i]])[0]}</g>')
        out.append(im)
        dx, dy = X1 - X0, Y1 - Y0
        L = math.hypot(dx, dy)
        out.append(arrow(X0 + dx / L * 4.5, Y0 + dy / L * 3.5, X1 - dx / L * 5.5, Y1 - dy / L * 3.5, bend=0.15))
    # панель 4 — все соседи заняты Александром
    mp = mps[3]
    out.append(units(mp, 'alex', gone=(1,)))
    occupy = ['Морпех', 'Морпех', 'Цунами', 'Танк МЕГ-01']
    CX, CY = mp.P(c0)
    dy = mp.y - mps[0].y
    avoid = [(a, b + dy) for a, b in lab_pts]
    for r, key in zip(nbs, occupy):
        X, Y = spot(mp, r, toward(r, CX, CY), avoid=avoid, depth=6.0 if r == ind else 3.5)
        avoid.append((X, Y))
        out.append(put_unit(key, X, Y, h=UNIT_H[key])[0])
    CX, CY = mp.P(c0)
    for i in (0, 2, 3):
        X, Y = CX + g_ilya[i][0], CY + g_ilya[i][1]
        if ilya[i] == 'Рекрут ЭК':
            out.append(image(factory_token(), X - 3.6, Y - 1.2, 7.2, 7.2, dpi=300, fmt='PNG'))
            out.append(put_unit(ilya[i], X, Y - 1.6, h=6.0)[0])
            continue
        out.append(put_unit(ilya[i], X, Y, h=UNIT_H[ilya[i]])[0])
        out.append(result_badge(X, Y - UNIT_H[ilya[i]] / 2 - 2.4, 'S'))
        if i == 2:
            out.append(cross(X, Y))
    # подписи под панелями
    cap = [
        ['Александр — Островная Империя: Танк МЕГ-01 (3)', 'и два Моторизированных морпеха (по 1). Илья —',
         'Эйркрафт Корпорейшн: Самолёт «Фантом» (1), два', 'Дрона «Ночной призрак» (0), рекрут на фабрике.'],
        ['Сила 5 против 1.'],
        ['Дрон Ильи и Морпех Александра убраны в резерв.', 'Самолёт и Дрон отступают в смежные регионы.',
         'Рекрут на фабрике остаётся — фабрика его.'],
        ['Все смежные регионы заняты Александром.', 'Илья уничтожает один отряд — Дрон.',
         'Самолёт остаётся, как будто подавления не было.'],
    ]
    for i, (px, py) in enumerate(panels):
        if i == 1:
            continue
        out.append(lines(px, py + ph + 4.2, cap[i], 2.7, fill=MUTED))
    # панель 2 — кубики под картой
    px, py = panels[1]
    out.append(text(px, py + ph + 4.4, 'Александр:', 2.7, fill=MUTED))
    d, wd = dice_row(px + 15.5, py + ph + 1.4, [6, 5, 4, 2, 1], size=3.8)
    out.append(d)
    out.append(text(px + 15.5 + wd + 2, py + ph + 4.4, 'Илья:', 2.7, fill=MUTED))
    d, _ = dice_row(px + 15.5 + wd + 10, py + ph + 1.4, [6], size=3.8)
    out.append(d)
    out.append(text(px, py + ph + 13.4, 'Сначала смерти обеих сторон, потом подавления.', 2.7, fill=MUTED))
    # легенда
    ly = head + 2 * ph + 24 + 18
    lx = 0
    for fac, who in (('Островная Империя', 'Александр'), ('Эйркрафт Корпорейшн', 'Илья')):
        out.append(f'<rect x="{f(lx)}" y="{f(ly - 2.6)}" width="3.2" height="3.2" rx="0.6" '
                   f'fill="{FACTION_COLOR[fac]}" stroke="{INK}" stroke-width="0.25"/>')
        out.append(text(lx + 4.6, ly, f'{who} — {fac}', 2.7))
        lx += 58
    out.append(result_badge(lx + 2, ly - 1, 'K'))
    out.append(text(lx + 5.4, ly, 'смерть', 2.7))
    out.append(result_badge(lx + 20, ly - 1, 'S'))
    out.append(text(lx + 23.4, ly, 'подавление', 2.7))
    H = ly + 2
    write('bitva.svg', svg_doc(W, H, '\n'.join(out), 'Примеры битвы 1 и 2 (§8.11)'))


# ══════════════════════════════════════════════════════════════ РОЙ
def build_roy():
    """§11.6 — два варианта из примера: Узел у края карты и Узел ближе к середине."""
    cfg = '5P'
    reg, nb = geo(cfg)
    uzel = trim(load(f'{ACR}/05. ЦУ - стенд - 1шт - ↔️45мм.png').convert('RGBA'))
    zona = trim(load(f'{ACR}/06. Контроль - круглый жетон - ⌀20мм.png').convert('RGBA'))
    pw = (W - 6) / 2
    ph = 66.0
    out = []
    variants = [
        ('Новая Зеландия', (0, 563 - 300 * ph / pw, 300, 563),
         'Узел у края карты',
         ['Смежных регионов три — зон тоже три.', 'Сеть компактная, Рой выходит', 'из неё в одну сторону.']),
        ('Юг Атлантического океана', (280, 285, 680, 285 + 400 * ph / pw),
         'Узел ближе к середине',
         ['Смежных регионов восемь — четыре зоны', 'через один. Рой появляется сразу на', 'нескольких направлениях.']),
    ]
    for i, (node_name, win, title, cap) in enumerate(variants):
        px, py = i * (pw + 6), 5.0
        node = rid_by_name(cfg, node_name)
        nbs = nb[node]
        mp = MapPanel(cfg, win, px, py, pw, ph)
        out.append(text(px, py - 1.6, title, 3.1, cls='h', weight='bold'))
        out.append(mp.draw({node: {'fill': '#F6DCE3', 'stroke': ACCENT, 'sw': 0.6}}, uid=f'r{i}'))
        # соседи по кругу — по направлению на общую границу
        c, _ = label_point(reg[node]['polys'], win, step=2.0)
        mids = {r: shared_mid(cfg, node, r) for r in nbs}
        order = sorted(nbs, key=lambda r: math.atan2(mids[r][1] - c[1], mids[r][0] - c[0]))
        if len(order) <= 4:
            zones = order
        else:
            zones = order[0::2][:4]
        NX, NY = mp.P(c)
        labs = {r: mp.anchor(r) for r in nbs}
        avoid = [mp.P(q) for q in labs.values()] + [(NX, NY), (NX, NY + 8.5)]
        for r in nbs:
            out.append(region_label(mp, r, pt=labs[r], size=2.3))
        print('    вокруг', node_name, '→', [reg[r]['name'] + ('*' if r in zones else '') for r in order])
        for r in zones:
            X, Y = spot(mp, r, mp.P(labs[r]), avoid=avoid, depth=4.5, clear=9.0)
            avoid.append((X, Y))
            out.append(image(zona, X - 4.0, Y - 4.0, 8.0, 8.0, dpi=300, fmt='PNG'))
        out.append(image(uzel, NX - 6.5, NY - 6.5, 13, None, dpi=300, fmt='PNG'))
        out.append(region_label(mp, node, pt=c, dy=8.5, size=2.4, fill=INK))
        out.append(lines(px, py + ph + 4.2, cap, 2.7, fill=MUTED))
    ly = 5.0 + ph + 4.2 + 3 * 2.7 * 1.25 + 3.5
    out.append(image(uzel, 0, ly - 4, 8, None, dpi=300, fmt='PNG'))
    out.append(text(9.5, ly, 'Узел управления', 2.7))
    out.append(image(zona, 40, ly - 3.6, 5.2, 5.2, dpi=300, fmt='PNG'))
    out.append(text(46.5, ly, 'Зона сети', 2.7))
    H = ly + 2.5
    write('roy.svg', svg_doc(W, H, '\n'.join(out), 'Размещение Роя боевых дронов (§11.6)'))


# ══════════════════════════════════════════════════════════════ СТОЛ
def build_stol():
    """§2.2, §2.4 — схема раскладки. Номера в кружках — шаги 1–6 §2.2."""
    out = []
    H = 120.0
    out.append(f'<rect x="0.5" y="0.5" width="{f(W - 1)}" height="{f(H - 1)}" rx="6" fill="#F4F2EE" '
               f'stroke="{BORDER}" stroke-width="0.35"/>')
    lab = dict(size=2.6, fill=MUTED)
    # поле в центре
    bw, bx, by = 88.0, 38.0, 11.0
    thumb, bh = board_thumb('board/geo/board-MC-5P.svg', bx, by, bw)
    out.append(thumb)
    out.append(text(bx + bw / 2, by + bh + 4.0, 'Игровое поле для числа игроков', anchor='middle', **lab))
    # треки и колода — справа от поля
    tx, tw = bx + bw + 6, W - (bx + bw + 6) - 5
    out.append(text(tx, by - 2, 'Треки и колода', **lab))
    dt = pdf_page(f'{SAVED}/Трек Судного дня.pdf', 2, 150)
    dsq = grid_cell(dt, 1, 2, 0, 0)
    dw = 24.0
    out.append(image(dsq, tx, by + 1, dw, dw, dpi=300, fmt='JPEG'))
    out.append(badge(tx, by + 1, '1', r=2.4))
    mk = trim(load(f'{ACR}/04. Жетон влияния - 1шт. - ⌀15мм.png').convert('RGBA'))
    # деление «5» на треке на троих — справа вверху кольца
    out.append(image(mk, tx + dw * 0.71 - 2.2, by + 1 + dw * 0.205 - 2.2, 4.4, 4.4, dpi=300, fmt='PNG'))
    out.append(badge(tx + dw + 1.5, by + 1 + dw * 0.205, '3', r=2.4))
    vp = vp_render()
    vh = tw * vp.height / vp.width
    vy = by + dw + 4
    out.append(image(vp, tx, vy, tw, vh, dpi=300, fmt='JPEG'))
    out.append(badge(tx, vy, '2', r=2.4))
    hi = rounded(grid_cell(pdf_page(f'{SAVED}/Карты скрытого влияния - (формат Mini USA).pdf', 2, 150),
                           5, 4, 0, 0), 40.8, R_CARD)
    cw = 9.0
    ch = cw * hi.height / hi.width
    cy = vy + vh + 4
    for k in range(3):
        out.append(image(hi, tx + k * 0.6, cy - k * 0.6, cw, ch, dpi=300, fmt='PNG'))
    out.append(badge(tx, cy, '4', r=2.4))
    out.append(lines(tx + cw + 3, cy + 4, ['Колода скрытого', 'влияния'], **lab))
    # общий резерв — слева от поля
    rx = 6.0
    ft = factory_token()
    for k in range(3):
        out.append(image(ft, rx + k * 0.8, by + 3 - k * 0.8, 10, 10, dpi=300, fmt='PNG'))
    out.append(badge(rx, by + 1.5, '5', r=2.4))
    die = dice_face(6)
    for k in range(3):
        out.append(die(rx + k * 5.4, by + 17, 4.6))
    out.append(lines(rx, by + 27, ['Общий резерв:', 'фабрики', 'и кубики'], **lab))
    # перед игроком — снизу: планшет в центре, вокруг него компоненты фракции (§2.4)
    card = card_render()['im']
    pw_ = 42.0
    ph_ = pw_ * card.height / card.width
    # Всё стоит низом на одной линии с планшетом, подписи — одной строкой под ними.
    px, py = 50.0, H - ph_ - 9.5
    base = py + ph_
    cap_y = base + 3.4

    def cap(cx, rows):
        out.append(lines(cx, cap_y, rows, anchor='middle', **lab))

    out.append(text(6.0, py - 3.0, 'Перед игроком', size=2.8, weight='bold'))
    out.append(image(card, px, py, pw_, ph_, dpi=300, fmt='JPEG'))
    cap(px + pw_ / 2, ['планшет'])
    # слева — фигурки (резерв)
    fx, fw = 6.0, px - 4.0 - 6.0
    out.append(figs_pic(fx, base - 13.0, fw, 13.0, gap=1.6))
    cap(fx + fw / 2, ['фигурки', 'резерв'])
    # справа — задачи, технологии, памятка
    tt = pdf_page(f'{SAVED}/Технологии и задачи.pdf', 1, 150)
    tk = rounded(grid_cell(tt, 3, 6, 0, 0), 64.3, R_CARD)
    th = rounded(grid_cell(tt, 3, 6, 0, 2), 64.3, R_CARD)
    kw, kg = 9.0, 0.8
    kh = kw * tk.height / tk.width
    kx = px + pw_ + 5
    ky = base - 2 * kh - kg
    for k in range(6):
        out.append(image(tk, kx + (k % 3) * (kw + kg), ky + (k // 3) * (kh + kg), kw, kh, dpi=300, fmt='PNG'))
    cap(kx + (3 * kw + 2 * kg) / 2, ['задачи', 'лицом вверх'])
    hx = kx + 3 * (kw + kg) + 4.5
    for k in range(3):
        out.append(image(th, hx + k * 0.7, base - kh - k * 0.7, kw, kh, dpi=300, fmt='PNG'))
    cap(hx + kw / 2 + 0.7, ['технологии', 'резерв'])
    pm = rounded(pdf_page(f'{SAVED}/Памятка.pdf', 1, 150), 105.2, R_CARD)
    mx, mw = hx + kw + 7.5, 9.0
    mh = mw * pm.height / pm.width
    out.append(image(pm, mx, base - mh, mw, mh, dpi=300, fmt='PNG'))
    out.append(badge(mx, base - mh, '6', r=2.4))
    cap(mx + mw / 2, ['памятка'])
    write('stol.svg', svg_doc(W, H, '\n'.join(out), 'Подготовка: раскладка стола (§2.2, §2.4)'))


def build_kuklovod():
    """§6.3 — кукловод из центра трека Судного дня, круглой вырезкой."""
    im = load('art/doomsday/4 игрока v1.1.png').convert('RGB')
    k = im.width / 2048          # координаты — по кадру 2048 × 2048
    cx, cy, r = 1032 * k, 930 * k, 395 * k
    c = im.crop((round(cx - r), round(cy - r), round(cx + r), round(cy + r)))
    m = Image.new('L', (c.width * 4, c.height * 4), 0)
    from PIL import ImageDraw
    ImageDraw.Draw(m).ellipse((0, 0, m.width - 1, m.height - 1), fill=255)
    c.putalpha(m.resize(c.size, Image.LANCZOS))
    buf = io.BytesIO()
    c.save(buf, 'PNG', optimize=True)
    write('kuklovod.png', buf.getvalue(), binary=True)


# ══════════════════════════════════════════════════════════════ КОНЦОВКИ ЧАСТЕЙ (D-139)
# Генератор нарисовал «прозрачный фон» серо-белой шахматкой прямо в картинке. Снимаем её:
#   фон      — светлые нейтральные пиксели, связанные с краем кадра (и крупные островки внутри);
#   кромка   — два пикселя у фона размешиваются с цветом соседней клетки;
#   тень     — мягкая: альфа — среднее за период шахматки, клетки в ней не видны;
#   голограмма — полупрозрачная: подложка-шахматка восстанавливается по клеткам (под голограммой —
#              по контрасту клетки с соседями), альфа и цвет — размешиванием с ней.
# Картинка рассчитана на белый лист книги; на тёмном фоне в дымке голограммы видна зернистость.
KONCOVKI = {   # арт в art/ → (файл в img/, тень, голограмма); ящик и эмблема сняты (D-141)
    'quartermaster-g1': ('konc-quartermaster-1.png', False, True),
    'quartermaster-g2': ('konc-quartermaster-2.png', False, True),
}
_NB8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]


def _box(x, r):
    """Среднее по окну (2r+1)²."""
    import numpy as np
    q = np.pad(x, r + 1, mode='edge').cumsum(0).cumsum(1)
    k = 2 * r + 1
    s = q[k:, k:] - q[:-k, k:] - q[k:, :-k] + q[:-k, :-k]
    return s[:x.shape[0], :x.shape[1]] / (k * k)


def _shift(x, dy, dx, fill):
    import numpy as np
    out = np.full_like(x, fill)
    h, w = x.shape[:2]
    ys, yd = (slice(0, h - dy), slice(dy, h)) if dy >= 0 else (slice(-dy, h), slice(0, h + dy))
    xs, xd = (slice(0, w - dx), slice(dx, w)) if dx >= 0 else (slice(-dx, w), slice(0, w + dx))
    out[yd, xd] = x[ys, xs]
    return out


def _flood(seed, allowed):
    """Пиксели allowed, связанные с seed (4-связность)."""
    import numpy as np
    from collections import deque
    h, w = allowed.shape
    out = seed & allowed
    q = deque(zip(*np.nonzero(out)))
    while q:
        y, x = q.popleft()
        for yy, xx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
            if 0 <= yy < h and 0 <= xx < w and allowed[yy, xx] and not out[yy, xx]:
                out[yy, xx] = True
                q.append((yy, xx))
    return out


def _islands(mask):
    """Связные области mask: номер области у каждого пикселя и размеры областей."""
    import numpy as np
    from collections import deque
    h, w = mask.shape
    lab = np.zeros((h, w), np.int32)
    sizes = [0]
    for y0, x0 in zip(*np.nonzero(mask)):
        if lab[y0, x0]:
            continue
        n = len(sizes)
        lab[y0, x0] = n
        q, c = deque([(y0, x0)]), 0
        while q:
            y, x = q.popleft()
            c += 1
            for yy, xx in ((y - 1, x), (y + 1, x), (y, x - 1), (y, x + 1)):
                if 0 <= yy < h and 0 <= xx < w and mask[yy, xx] and not lab[yy, xx]:
                    lab[yy, xx] = n
                    q.append((yy, xx))
        sizes.append(c)
    return lab, np.array(sizes)


def _checker_step(L, N):
    """Клетка шахматки, пикс.: по пику спектра светлых нейтральных пикселей."""
    import numpy as np
    h, w = L.shape
    M = np.abs(np.fft.fft2(np.where(N, L - L[N].mean(), 0)))
    fy, fx = np.fft.fftfreq(h)[:, None], np.fft.fftfreq(w)[None, :]
    band = (np.abs(fx) > 1 / 60) & (np.abs(fy) > 1 / 60) & (np.abs(fx) < 1 / 10) & (np.abs(fy) < 1 / 10)
    j = int(np.argmax(np.where(band, M, 0)))
    return 1 / (abs(fx.ravel()[j % w]) + abs(fy.ravel()[j // w]))


def _grid_lines(L, N, axis, s):
    """Границы клеток вдоль оси (граница между пикселями x-1 и x — позиция x), дробные."""
    import numpy as np
    if axis == 0:
        L, N = L.T, N.T
    d = L[:, 1:] - L[:, :-1]
    wgt = np.where(N[:, 1:] & N[:, :-1] & (np.abs(d) > 4), np.abs(d), 0).sum(0)
    n = len(wgt)
    sm = np.convolve(wgt, [1, 1, 1], 'same')
    thr = 0.12 * np.percentile(sm[sm > 0], 95)
    keep = []
    for i in range(1, n - 1):
        if sm[i] >= thr and sm[i] >= sm[i - 1] and sm[i] > sm[i + 1]:
            j0, j1 = i - 1, min(n, i + 2)
            ww = wgt[j0:j1]
            if ww.sum() <= 0:
                continue
            pos = float((np.arange(j0, j1) * ww).sum() / ww.sum()) + 1.0
            if keep and pos - keep[-1][0] < 0.6 * s:
                if sm[i] > keep[-1][1]:
                    keep[-1] = (pos, sm[i])
                continue
            keep.append((pos, sm[i]))
    full = [keep[0][0]]
    for pos, _ in keep[1:]:
        g = pos - full[-1]
        m = max(1, int(round(g / s)))
        full += [full[-1] + g * t / m for t in range(1, m + 1)]
    while full[0] > 0:
        full.insert(0, full[0] - s)
    while full[-1] < n + 1:
        full.append(full[-1] + s)
    return np.array(full)


def _cells(lines, n):
    """Для пикселя: клетка его центра, соседняя клетка и доля пикселя в соседней."""
    import numpy as np
    x0 = np.arange(n, dtype=float)
    k = np.searchsorted(lines, x0 + 0.5, side='right') - 1
    fl, fh = np.clip(lines[k] - x0, 0, 1), np.clip(x0 + 1 - lines[k + 1], 0, 1)
    return k, np.where(fl > fh, k - 1, k + 1), np.maximum(fl, fh)


def _plate(a, L, N, s, zone):
    """Подложка-шахматка под картинкой: цвет видимой клетки — из картинки; клетки под голограммой
    (zone) — по контрасту с соседями; остальные скрытые — по ближайшей видимой и правилу шахматки."""
    import numpy as np
    h, w = L.shape
    gx, gy = _grid_lines(L, N, 1, s), _grid_lines(L, N, 0, s)
    kx, nx, fx = _cells(gx, w)
    ky, ny, fy = _cells(gy, h)
    nX, nY = len(gx) + 1, len(gy) + 1
    inner = (fx[None, :] < 0.01) & (fy[:, None] < 0.01)
    cid = ky[:, None] * nX + kx[None, :]

    def per_cell(mask, vals):
        idx = cid[mask]
        cnt = np.bincount(idx, minlength=nX * nY)
        return cnt, [np.bincount(idx, weights=v[mask], minlength=nX * nY) / np.maximum(cnt, 1) for v in vals]

    cnt, cols = per_cell(N & inner, [a[..., 0], a[..., 1], a[..., 2]])
    col = np.stack(cols, 1).reshape(nY, nX, 3)
    vis = (cnt >= 6).reshape(nY, nX)
    lv = col.mean(2)
    med = np.median(lv[vis])
    dark = vis & (lv < (np.median(lv[vis & (lv > med)]) + np.median(lv[vis & (lv <= med)])) / 2)
    lite_c, dark_c = np.median(col[vis & ~dark], 0), np.median(col[dark], 0)
    # под голограммой: клетка темнее соседей — тёмная
    cnt2, (m2, zc) = per_cell(inner, [L, zone.astype(float)])
    m2, zc = m2.reshape(nY, nX), zc.reshape(nY, nX)
    pd = np.pad(m2, 1, mode='edge')
    c = m2 - (pd[:-2, 1:-1] + pd[2:, 1:-1] + pd[1:-1, :-2] + pd[1:-1, 2:]) / 4
    sure = ~vis & (zc > 0.5) & (np.abs(c) > 3) & (cnt2.reshape(nY, nX) >= 6)
    dark[sure] = c[sure] < 0
    col[sure] = np.where(dark[sure][:, None], dark_c, lite_c)
    known = vis | sure
    vy, vx = np.nonzero(known)
    hy, hx = np.nonzero(~known)
    for i in range(0, len(hy), 2000):
        yy, xx = hy[i:i + 2000], hx[i:i + 2000]
        j = np.argmin((yy[:, None] - vy[None, :]) ** 2 + (xx[:, None] - vx[None, :]) ** 2, 1)
        dk = dark[vy[j], vx[j]] ^ ((yy - vy[j] + xx - vx[j]) % 2 == 1)
        col[yy, xx] = np.where(dk[:, None], dark_c, lite_c)
    nxc, nyc = np.clip(nx, 0, nX - 1), np.clip(ny, 0, nY - 1)
    FX, FY = fx[None, :, None], fy[:, None, None]
    return ((1 - FX) * (1 - FY) * col[ky[:, None], kx[None, :]] + FX * (1 - FY) * col[ky[:, None], nxc[None, :]]
            + (1 - FX) * FY * col[nyc[:, None], kx[None, :]] + FX * FY * col[nyc[:, None], nxc[None, :]])


def _unmix(a, B, cut=0.0):
    """Наименьшая альфа, при которой a = α·F + (1-α)·B с F в [0, 255]; и сам F."""
    import numpy as np
    al = np.maximum((B - a) / np.maximum(B, 1), (a - B) / np.maximum(255 - B, 1)).max(2)
    al = np.clip((al - cut) / (1 - cut), 0, 1)
    k = np.clip(al, 1e-3, 1)[..., None]
    return al, np.clip((a - (1 - k) * B) / k, 0, 255)


def vyrezka(im, shadow=False, holo=False):
    """Снять нарисованную шахматку с картинки: RGBA, обрезанная по предмету."""
    import numpy as np
    a = np.asarray(im.convert('RGB')).astype(float)
    h, w, _ = a.shape
    L, sat = a.mean(2), a.max(2) - a.min(2)
    N = (sat < 12) & (L > 200)
    lite = np.median(L[N & (L > 245)])
    dark = np.median(L[N & (L < lite - 10)])
    s = _checker_step(L, N)
    edge = np.zeros((h, w), bool)
    edge[0, :] = edge[-1, :] = edge[:, 0] = edge[:, -1] = True
    Z = np.zeros((h, w), bool)
    if holo:   # зона голограммы: яркий циан и всё вокруг на три периода шахматки
        cy = (a[..., 2] - a[..., 0] > 60) & (a[..., 1] - a[..., 0] > 30) & (L > 120)
        Z = _box(cy.astype(float), int(round(6 * s))) > 0.01
    cand = (sat < 14) & (L > dark - 14) & ~Z
    bg = _flood(edge, cand)
    lab, sz = _islands(cand & ~bg)
    big = sz >= 1.5 * s * s
    big[0] = False
    bg |= big[lab]
    alpha, F = np.ones((h, w)), a.copy()
    sh = np.zeros((h, w), bool)
    if shadow:   # мягкая тень: нейтральная, темнее фона, связана с фоном
        zone = _flood(bg, (sat < 16) & (L > 150))
        r, Bm = max(2, int(round(s))), (lite + dark) / 2
        als = _box(np.where(zone, (Bm - L) / Bm, 0), r) / np.maximum(_box(zone.astype(float), r), 1e-3)
        als = np.clip((als - 0.015) / 0.985, 0, 1) * zone
        sh = zone & (als > 0.004)
        alpha[sh], F[sh] = als[sh], 35
    lab, sz = _islands(~(bg | sh))   # крошки среди фона — фон
    small = sz < 80
    small[0] = False
    bg |= small[lab]
    tr = np.zeros((h, w), bool)
    if holo:
        B = _plate(a, L, N & bg, s, Z)
        tr = Z & ~bg & ~sh & ((L > 140) | (a[..., 2] - a[..., 0] > 25)) & (a[..., 0] <= a[..., 2] + 5)
        at, Ft = _unmix(a, B, 0.03)
        # нейтральное светлое в зоне — остаток шахматки, а не голограмма: только «темнее подложки»
        neu = tr & (sat < 14)
        an = np.clip((((B - a) / np.maximum(B, 1)).max(2) - 0.08) / 0.92, 0, 1)
        kk = np.clip(an, 1e-3, 1)[..., None]
        at[neu] = an[neu]
        Ft[neu] = np.clip((a - (1 - kk) * B) / kk, 0, 255)[neu]
        alpha[tr], F[tr] = at[tr], Ft[tr]
    # кромка: два кольца у фона — размешать с цветом соседней клетки
    Bl, kn = a.copy(), bg.copy()
    for _ in range(3):
        acc, cnt = np.zeros_like(Bl), np.zeros((h, w))
        for dy, dx in _NB8:
            k = _shift(kn, dy, dx, False)
            acc += np.where(k[..., None], _shift(Bl, dy, dx, 0), 0)
            cnt += k
        new = ~kn & (cnt > 0)
        Bl[new] = acc[new] / cnt[new][:, None]
        kn |= new
    ring, cur = np.zeros((h, w), np.int8), bg.copy()
    for i in (1, 2):
        nxt = cur.copy()
        for dy, dx in _NB8:
            nxt |= _shift(cur, dy, dx, False)
        ring[nxt & ~cur] = i
        cur = nxt
    band = (ring > 0) & ~sh & ~tr & kn
    ab, Fb = _unmix(a, Bl)
    ab = np.where(ring == 1, ab, np.maximum(ab, 0.5))
    alpha[band], F[band] = ab[band], Fb[band]
    alpha[bg & ~sh] = 0
    out = Image.fromarray(np.dstack([F, alpha * 255]).round().astype(np.uint8), 'RGBA')
    return trim(out, pad=round(0.02 * max(h, w)))


def build_valve():
    """Лист 18 — «Две стороны вентиля» (D-146). Генератор обвёл просвет между панелями чёрным,
    а наружные края полосы без обводки. Обводку закрашиваем белым — просвет становится шире
    (около 2,5 мм в книге), панели без рамок, как все полосы книги. Диагональ находится по
    белому просвету в самой картинке."""
    import numpy as np
    a = np.asarray(load('print/Rulebook/art/valve-g1.png').convert('RGB')).astype(float)
    h, w, _ = a.shape
    mn = a.min(2)
    ys, xs = [], []
    for y in range(0, h, 4):              # центр белого просвета в строке: белый отрезок 8–16 пикс.
        white = np.concatenate([[False], mn[y] > 215, [False]])
        d = np.diff(white.astype(int))
        for x0, x1 in zip(np.nonzero(d == 1)[0], np.nonzero(d == -1)[0]):
            if 8 <= x1 - x0 <= 16 and w * 0.2 < x0 < w * 0.8:
                ys.append(y)
                xs.append((x0 + x1 - 1) / 2)
    ys, xs = np.array(ys, float), np.array(xs, float)
    keep = np.ones(len(ys), bool)
    for _ in range(3):                    # прямая по точкам, выбросы (белое в небе) — прочь
        k, b = np.polyfit(ys[keep], xs[keep], 1)
        keep = np.abs(xs - (k * ys + b)) < 2.5
    assert keep.sum() > h / 8, 'просвет между панелями не найден'
    hw = 10.5                             # полпросвета 5,5 + обводка 3 + сглаживание 2, пикс.
    yy, xx = np.mgrid[0:h, 0:w]
    cover = np.clip(hw + 1 - np.abs(xx - (k * yy + b)), 0, 1)[..., None]
    out = a * (1 - cover) + 255 * cover
    buf = io.BytesIO()
    Image.fromarray(out.round().astype(np.uint8)).save(buf, 'PNG', optimize=True)
    write('valve.png', buf.getvalue(), binary=True)


def svetlee(src, gamma, out):
    """Тёмный арт светлее (D-160): гамма поднимает тени, светлые места почти не трогает.
    Исходник в art/ не меняется, результат — в img/."""
    import numpy as np
    a = np.asarray(load('print/Rulebook/art/' + src).convert('RGB')).astype(float) / 255
    buf = io.BytesIO()
    Image.fromarray((a ** gamma * 255).round().astype(np.uint8)).save(buf, 'PNG', optimize=True)
    write(out, buf.getvalue(), binary=True)


def build_office():
    """§9.2 — «Кабинет» колонкой рядом с текстом (D-160). Исходник очень тёмный: медианная
    светлота 13 %, у остальных картинок книги 21–62 %, а печать ещё темнит. Гамма 0,6 —
    медиана около 30 %."""
    svetlee('office-g1.png', 0.6, 'office.png')


def build_truce():
    """Часть 10 — «Перемирие» (D-163, D-164). Медианная светлота исходника 19 %, гамма 0,75 —
    около 29 %, как у «Кабинета»."""
    svetlee('truce-g1.png', 0.75, 'truce.png')


def build_komiks():
    """Лист 32 — комикс из двух панелей (D-161, D-162): слева «Краб и Спрут» целиком, справа тот же
    «Краб» после битвы. Полоса 170 × 51 мм; панели разделяет белый просвет 2,5 мм с лёгким
    наклоном: 7 мм на высоту полосы, около 8°. Каждая картинка не уже своей панели в самом
    широком месте — иначе у просвета остаётся белый клин (D-162); проверка — assert."""
    import numpy as np
    W = 2000                              # 170 мм
    px = W / 170
    H = round(51 * px)
    hg = 2.5 * px / 2                     # полпросвета
    xt, xb = 0.52, 0.48                   # середина просвета: доля ширины вверху и внизу
    def panel(name, width, c, left):
        im = load('print/Rulebook/art/' + name).convert('RGB')
        w = round(width)
        h = round(w * im.height / im.width)
        im = im.resize((w, h), Image.LANCZOS)
        top = max(0, min(h - H, int(round(c * h - H / 2))))      # c — центр кадра по высоте
        canvas = Image.new('RGB', (W, H), 'white')
        x0 = 0 if left else W - w
        canvas.paste(im.crop((0, top, w, top + H)), (x0, 0))
        cov = np.zeros((H, W), bool)
        cov[:, x0:x0 + w] = True
        return np.asarray(canvas).astype(float), cov
    lft, cl = panel('duel-g1.png', max(xt, xb) * W - hg + 20, 0.48, True)
    rgt, cr = panel('aftermath-g1.png', (1 - min(xt, xb)) * W - hg + 20, 0.55, False)
    yy, xx = np.mgrid[0:H, 0:W]
    line = (xt + (xb - xt) * yy / (H - 1)) * W
    ml = np.clip(line - hg - xx + 0.5, 0, 1)
    mr = np.clip(xx - (line + hg) + 0.5, 0, 1)
    assert not ((ml > 0) & ~cl).any() and not ((mr > 0) & ~cr).any(), 'панель не закрыта картинкой'
    out = lft * ml[..., None] + rgt * mr[..., None] + 255 * (1 - ml - mr)[..., None]
    buf = io.BytesIO()
    Image.fromarray(out.round().astype(np.uint8)).save(buf, 'PNG', optimize=True)
    write('komiks-bitva.png', buf.getvalue(), binary=True)


def build_ref_duel():
    """Схема расстановки для генерации сцены «Краб и Спрут» (лист 32, D-156): не арт книги,
    а приложение к промпту. Силуэты — с компонентов (print/Units), цвета — фракций.
    Кадр 3 : 2; в книге останется средняя полоса (от 28 до 72 % высоты), поэтому всё
    значимое — в ней, сверху только небо, снизу только вода и берег."""
    from PIL import ImageDraw
    W_, H_ = 1536, 1024
    im = Image.new('RGB', (W_, H_), '#C9D3DA')
    d = ImageDraw.Draw(im)
    for y in range(H_ // 2):                                    # небо светлее к горизонту
        c = int(201 + 30 * y / (H_ / 2))
        d.line([(0, y), (W_, y)], fill=(c - 8, c - 2, c + 4))
    horizon = 470
    d.polygon([(0, horizon), (W_, horizon), (W_, H_), (0, H_)], fill='#7E95A3')       # море
    d.polygon([(640, H_), (930, horizon), (W_, horizon), (W_, H_)], fill='#A79C88')   # берег справа
    for x0, x1, top in ((1250, 1290, 380), (1300, 1360, 420), (1370, 1395, 350), (1410, 1490, 425),
                        (1500, 1525, 370)):                                           # завод на горизонте
        d.rectangle([x0, top, x1, horizon], fill='#8A939B')
    for x in (1382, 1512):                                                            # дым труб
        for k in range(6):
            r = 14 + k * 7
            d.ellipse([x - r + k * 10, 340 - k * 30 - r, x + r + k * 10, 340 - k * 30 + r], fill='#B5BEC6')

    def unit(rel, fac, h, x, y, flip=False, rot=0, cut=None):
        sil = load(f'print/Units/{rel}').convert('RGBA')
        sil = sil.crop(sil.getbbox())
        if flip:
            sil = sil.transpose(Image.FLIP_LEFT_RIGHT)
        if rot:
            sil = sil.rotate(rot, expand=True, resample=Image.BICUBIC)
        sil = sil.resize((round(sil.width * h / sil.height), h), Image.LANCZOS)
        col = Image.new('RGBA', sil.size, FACTION_COLOR[fac])
        col.putalpha(sil.getchannel('A'))
        if cut is not None:                                                           # под водой — не видно
            a = col.getchannel('A')
            ImageDraw.Draw(a).rectangle([0, cut - y, col.width, col.height], fill=0)
            col.putalpha(a)
        im.paste(col, (x, y), col)
        return x, y, col.width, col.height

    isl, air = 'Островная Империя', 'Эйркрафт Корпорейшн'
    unit('ОстровнаяИмперия/Мегалодон.png', isl, 70, 120, 560, cut=610)               # танк на мелководье
    cx, cy, cw, ch = unit('ОстровнаяИмперия/Краб.png', isl, 340, 300, 380, flip=True, cut=625)
    for k in range(10):                                                               # пена у ватерлинии
        d.ellipse([cx + 10 + k * 36, 615, cx + 62 + k * 36, 640], fill='#E8EEF2')
    sx, sy, sw, sh = unit('Эйркрафт Корпорейшн/Спрут.png', air, 260, 820, 285, rot=-14)
    for k, (dx, dy) in enumerate(((0.32, 0.78), (0.62, 0.8))):                       # очереди Спрута в Краба
        x0, y0 = sx + sw * dx, sy + sh * dy
        x1, y1 = cx + cw * (0.45 + 0.1 * k), cy + ch * 0.35
        d.line([(x0, y0), (x1, y1)], fill='#F28C28', width=5)
        d.ellipse([x0 - 12, y0 - 12, x0 + 12, y0 + 12], fill='#FFB347')
    unit('Эйркрафт Корпорейшн/Ночной призрак.png', air, 46, 1230, 320)              # авиация в небе
    unit('Эйркрафт Корпорейшн/Фантом.png', air, 40, 640, 315, flip=True)
    unit('Эйркрафт Корпорейшн/Небесный охотник.png', air, 150, 1300, 520, flip=True)  # мех на берегу
    for i, x in enumerate((990, 1050, 1115)):                                          # морпехи на берегу
        unit('ОстровнаяИмперия/Морпех.png', isl, 74, x, 600 + i * 8)
    buf = io.BytesIO()
    im.save(buf, 'PNG', optimize=True)
    write('ref-duel.png', buf.getvalue(), binary=True)


def build_koncovki():
    """Концовки частей: вырезки из art/ на прозрачном фоне."""
    for src, (dst, shadow, holo) in KONCOVKI.items():
        path = p(f'print/Rulebook/art/{src}.png')
        if not os.path.exists(path):
            print('  нет', src)
            continue
        buf = io.BytesIO()
        vyrezka(Image.open(path), shadow, holo).save(buf, 'PNG', optimize=True)
        write(dst, buf.getvalue(), binary=True)

_vp = {}


def vp_render():
    """Трек влияния — рендер print/VP.svg (мастер компонента)."""
    if 'im' not in _vp:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            b = pw.chromium.launch(args=['--force-color-profile=srgb'])
            pg = b.new_page(viewport={'width': 1116, 'height': 454}, device_scale_factor=2)
            pg.goto('file://' + p('print/VP.svg'))
            pg.wait_for_timeout(500)
            png = pg.screenshot(clip={'x': 0, 'y': 0, 'width': 1115, 'height': 453})
            b.close()
        _vp['im'] = Image.open(io.BytesIO(png)).convert('RGB')
    return _vp['im']


def dice_face(v):
    pips = {1: [(0, 0)], 2: [(-1, -1), (1, 1)], 3: [(-1, -1), (0, 0), (1, 1)],
            4: [(-1, -1), (1, -1), (-1, 1), (1, 1)], 5: [(-1, -1), (1, -1), (0, 0), (-1, 1), (1, 1)],
            6: [(-1, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (1, 1)]}[v]

    def draw(x, y, s):
        o = [f'<rect x="{f(x)}" y="{f(y)}" width="{f(s)}" height="{f(s)}" rx="{f(s * 0.18)}" '
             f'fill="#FFFFFF" stroke="{INK}" stroke-width="0.3"/>']
        for a, b in pips:
            o.append(f'<circle cx="{f(x + s / 2 + a * s * 0.27)}" cy="{f(y + s / 2 + b * s * 0.27)}" '
                     f'r="{f(s * 0.08)}" fill="{INK}"/>')
        return ''.join(o)
    return draw


# ══════════════════════════════════════════════════════════════ РЯДЫ КОМПОНЕНТОВ
def row_cells(items, y, row_h, widths, x0=0.0):
    """Ряд «картинка + подпись». items: (картинка | функция(x, y, w, h) -> svg,
    реальная длинная сторона в мм или None, подпись, количество). Картинка — по scale_mm(),
    но не больше клетки."""
    out = []
    x = x0
    for (pic, real, cap, cnt), cw in zip(items, widths):
        box_w, box_h = cw - 4, row_h
        if callable(pic):
            out.append(pic(x + 2, y, box_w, box_h))
        else:
            L = scale_mm(real) if real else max(box_w, box_h)
            k = L / max(pic.width, pic.height)
            k = min(k, box_w / pic.width, box_h / pic.height)
            w, h = pic.width * k, pic.height * k
            fmt = 'PNG' if pic.mode == 'RGBA' else 'JPEG'
            out.append(image(pic, x + 2 + (box_w - w) / 2, y + (box_h - h), w, h, dpi=300, fmt=fmt))
        ty = y + box_h + 4.0
        out.append(text(x + cw / 2, ty, cap, 2.7, anchor='middle', weight='bold'))
        for k_, r in enumerate((cnt or '').split('\n')):
            if r:
                out.append(text(x + cw / 2, ty + 3.4 + k_ * 3.1, r, 2.6, anchor='middle', fill=MUTED))
        x += cw
    return out


def svg_vector(rel):
    raw = open(p(rel), encoding='utf-8').read()
    return 'data:image/svg+xml;base64,' + base64.b64encode(raw.encode('utf-8')).decode('ascii')


FIGS = [('print/Units/adept.png', 22), ('print/Units/colonel.png', 24),
        ('print/Units/ОстровнаяИмперия/Морпех.png', 26), ('print/Units/ОстровнаяИмперия/Краб.png', 34)]


def figs_pic(x, y, w, h, gap=1.0):
    """Фигурки Островной Империи в ряд, низом по y + h (§1.2, §2.2)."""
    o = []
    ims = [(tint(r, FACTION_COLOR['Островная Империя']), hh) for r, hh in FIGS]
    hs = [scale_mm(hh) * 0.75 for _, hh in ims]
    tot = sum(hh * im.width / im.height for (im, _), hh in zip(ims, hs)) + gap * (len(ims) - 1)
    k = min(1.0, w / tot)
    X = x + (w - tot * k) / 2
    for (im, _), hh in zip(ims, hs):
        hh *= k
        ww = hh * im.width / im.height
        o.append(image(im, X, y + h - hh, ww, hh, dpi=300, fmt='PNG'))
        X += ww + gap * k
    return ''.join(o)


def build_komponenty():
    """§1.1 и §1.2. Карты и фабрики со скруглёнными углами, размеры — с поправкой
    на реальный (D-126): не в натуральную пропорцию, но планшет крупнее карты,
    жетон мельче."""
    hi = pdf_page(f'{SAVED}/Карты скрытого влияния - (формат Mini USA).pdf', 2, 150)
    hi_front = pdf_page(f'{SAVED}/Карты скрытого влияния - (формат Mini USA).pdf', 3, 150)
    dt = pdf_page(f'{SAVED}/Трек Судного дня.pdf', 2, 150)
    barrel = svg_vector('print/icons/oil-barrel.svg')
    kill = trim(load('print/dices/kill.png').convert('RGBA'))
    supp = trim(load('print/dices/suppress.png').convert('RGBA'))
    card_back = rounded(grid_cell(hi, 5, 4, 0, 0), 40.8, R_CARD)
    card_front = rounded(grid_cell(hi_front, 5, 4, 0, 0), 40.8, R_CARD)
    pamyatka = rounded(pdf_page(f'{SAVED}/Памятка.pdf', 1, 150), 105.2, R_CARD)

    def board_pic(x, y, w, h):
        vw, vh, _ = board_regions_svg('board/geo/board-MC-5P.svg')
        bw = min(w, h * vw / vh, scale_mm(900))
        svg, _ = board_thumb('board/geo/board-MC-5P.svg', x + (w - bw) / 2, y + h - bw * vh / vw, bw)
        return svg

    def barrel_pic(x, y, w, h):
        s_ = scale_mm(20) * 0.95
        return (f'<image x="{f(x + (w - s_) / 2)}" y="{f(y + h - s_)}" width="{f(s_)}" height="{f(s_)}" '
                f'href="{barrel}"/>')

    def dice_pic(x, y, w, h):
        s_ = scale_mm(16)
        o = []
        for k, im in enumerate((kill, supp)):
            X = x + w / 2 - s_ - 1 + k * (s_ + 2)
            o.append(f'<rect x="{f(X)}" y="{f(y + h - s_)}" width="{f(s_)}" height="{f(s_)}" rx="{f(s_ * 0.18)}" '
                     f'fill="#FFFFFF" stroke="{INK}" stroke-width="0.3"/>')
            o.append(image(im, X + s_ * 0.12, y + h - s_ + s_ * 0.12, s_ * 0.76, s_ * 0.76, dpi=300, fmt='PNG'))
        return ''.join(o)

    def numdie_pic(x, y, w, h):
        s_ = scale_mm(16)
        return dice_face(5)(x + (w - s_) / 2, y + h - s_, s_)

    def cards_pic(x, y, w, h):
        ch_ = scale_mm(63)
        cw_ = ch_ * card_back.width / card_back.height
        return (image(card_back, x + w / 2 - cw_ - 0.8, y + h - ch_, cw_, ch_, dpi=300, fmt='PNG')
                + image(card_front, x + w / 2 + 0.8, y + h - ch_, cw_, ch_, dpi=300, fmt='PNG'))

    out = []
    y = 0.0
    row = [(board_pic, None, 'Игровое поле', 'карта Земли'),
           (vp_render(), 295, 'Трек влияния', '1 шт.'),
           (grid_cell(dt, 1, 2, 0, 0), 142.5, 'Трек Судного дня', '2 шт.')]
    out += row_cells(row, y, 32.0, [66, 62, 42])
    y += 32.0 + 12
    row = [(cards_pic, None, 'Скрытое влияние', '36 карт'),
           (factory_token(), 43.5, 'Военные фабрики', '24 шт.'),
           (trim(load(f'{ACR}/08. Жетон первого игрока - ⌀30 мм.png').convert('RGBA')), 30, 'Жетон первого игрока', '1 шт.'),
           (trim(load(f'{ACR}/04. Жетон влияния - 1шт. - ⌀15мм.png').convert('RGBA')), 15, 'Маркер Судного дня', '1 шт.'),
           (barrel_pic, None, 'Маркеры нефти', '10 шт., бочонки')]
    out += row_cells(row, y, 20.0, [36, 31, 37, 35, 31])
    y += 20.0 + 12
    row = [(pamyatka, 148.2, 'Памятки', '5 шт.'),
           (dice_pic, None, 'Боевые кубики', '20 шт. и наклейки'),
           (numdie_pic, None, 'Числовой кубик', '1 шт.')]
    out += row_cells(row, y, 28.0, [40, 40, 40], x0=25)
    y += 28.0 + 11
    write('komponenty-1.svg', svg_doc(W, y, '\n'.join(out), 'Общие компоненты (§1.1)'))

    tt = pdf_page(f'{SAVED}/Технологии и задачи.pdf', 1, 150)      # лица
    tb = pdf_page(f'{SAVED}/Технологии и задачи.pdf', 2, 150)      # рубашки (строки те же)

    def card_pair(row_):
        """Рубашка над лицом — карта задач (строка 0) или технологий (строка 2)."""
        face = rounded(grid_cell(tt, 3, 6, 0, row_), 64.3, R_CARD)
        back = rounded(grid_cell(tb, 3, 6, 0, row_), 64.3, R_CARD)

        def pic(x, y, w, h, gap=1.0):
            cw_ = scale_mm(64.3)
            ch_ = cw_ * face.height / face.width
            k = min(1.0, (h - gap) / (2 * ch_), w / cw_)
            cw_, ch_ = cw_ * k, ch_ * k
            X = x + (w - cw_) / 2
            return (image(back, X, y + h - 2 * ch_ - gap, cw_, ch_, dpi=300, fmt='PNG')
                    + image(face, X, y + h - ch_, cw_, ch_, dpi=300, fmt='PNG'))
        return pic

    row = [(card_render()['im'], 240, 'Планшет фракции', '1 шт.'),
           (trim(load(f'{ACR_LOGO}/Островная Империя.png').convert('RGBA')), 18, 'Маркер влияния', '1 шт.'),
           (card_pair(0), None, 'Карты задач', '6 шт.'),
           (card_pair(2), None, 'Карты технологий', '6 шт.'),
           (figs_pic, None, 'Фигурки отрядов', 'рекруты, специалист,\nбоевые машины, робот')]
    out = row_cells(row, 0, 26.0, [44, 26, 31, 31, 38])
    write('komponenty-2.svg', svg_doc(W, 26.0 + 14, '\n'.join(out), 'Компоненты фракции (§1.2)'))


def build_frakcii():
    """§2.3 — восемь фракций; четыре для первой партии отмечены."""
    first = ['Островная Империя', 'Глобал Петролеум', 'Эйркрафт Корпорейшн', 'Клонэйд Ресёрч']
    rest = ['Братство Сингулярности', 'Сайнтифик Солюшн', 'Североамериканский Альянс', 'Moon Systems']
    out = []
    cw, rh, logo = W / 4, 17.0, 13.0
    out.append(f'<rect x="0" y="0" width="{f(W)}" height="{f(rh + 6.5)}" rx="2" fill="#FBE8ED"/>')
    out.append(text(2.5, 4.6, 'Для первой партии', 2.8, cls='h', weight='bold', fill=ACCENT))
    for row, names in enumerate((first, rest)):
        y = 6.0 + row * (rh + 3.5)
        for i, name in enumerate(names):
            im = trim(load(f'{ACR_LOGO}/{name}.png').convert('RGBA'))
            x = i * cw + 2
            out.append(image(im, x, y + (rh - logo) / 2, logo, logo, dpi=300, fmt='PNG'))
            rows = name.split(' ', 1)
            ty = y + rh / 2 + (0.3 if len(rows) == 1 else -1.2)
            out.append(lines(x + logo + 2.2, ty + 1.0, rows, 2.7))
    H = 6.0 + 2 * rh + 3.5 + 1
    write('frakcii.svg', svg_doc(W, H, '\n'.join(out), 'Фракции (§2.3)'))


# ══════════════════════════════════════════════════════════════ ЗНАЧКИ НА ПОЛЯ
def build_znaki():
    """§11 — значки «Что нужно» у вариантов: как значки Лаборатории в оригинале (с. 171)."""
    def save(name, im, max_px=700):
        im = trim(im) if im.mode == 'RGBA' else im
        if max(im.size) > max_px:
            k = max_px / max(im.size)
            im = im.resize((int(im.width * k), int(im.height * k)), Image.LANCZOS)
        buf = io.BytesIO()
        im.save(buf, 'PNG', optimize=True)
        write(name, buf.getvalue(), binary=True)

    ft2 = pdf_page(f'{SAVED}/Factory Tokens.pdf', 2, 150)
    save('znak-fabrika-osobaya.png', rounded(grid_cell(ft2, 4, 6, 0, 1), 43.5, R_TOKEN))
    # события — Tarot 70 × 120 в ячейке 76 × 126: выпуск по 3 мм срезается
    save('znak-sobytiya.png', rounded(grid_cell(pdf_page(f'{SAVED}/Factory Events.pdf', 3, 150), 2, 2, 0, 0),
                                      76.1, R_CARD, inset_mm=3.0))
    save('znak-polkovniki.png', rounded(grid_cell(pdf_page(f'{SAVED}/Уникальные полковники.pdf', 1, 150), 3, 3, 0, 0),
                                        64.9, R_CARD))
    save('znak-naemniki.png', rounded(pdf_page(f'{SAVED}/Наёмники.pdf', 1, 200), 70.2, R_CARD))
    save('znak-laboratoriya.png', load(f'{ACR}/02. Лаборатория - стенд - 1шт - ↔️45мм.png').convert('RGBA'))
    en = load(f'{ACR}/03. Энграммы - 8x4шт - ↕️20мм.png').convert('RGBA')
    save('znak-engramma.png', en.crop((0, 0, en.width // 4, int(en.height * 0.47))))
    save('znak-uzel.png', load(f'{ACR}/05. ЦУ - стенд - 1шт - ↔️45мм.png').convert('RGBA'))
    save('znak-zona.png', load(f'{ACR}/06. Контроль - круглый жетон - ⌀20мм.png').convert('RGBA'))
    save('znak-kontrol-seti.png', rounded(pdf_page(f'{SAVED}/Контроль сети.pdf', 1, 200), 70.2, R_CARD))
    save('znak-roy.png', load(f'{ACR}/09. Рой дронов - стенд - 6шт - ↔️35мм.png').convert('RGBA'))


# ══════════════════════════════════════════════════════════════ ПРИМЕР ПОДГОТОВКИ И НЕФТЬ
_faces = {}


def planshet_face(fac):
    """Лицо планшета фракции — снимок .card из «Планшет — <фракция>.html»."""
    if fac not in _faces:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            b = pw.chromium.launch(args=['--force-color-profile=srgb'])
            pg = b.new_page(viewport={'width': 1400, 'height': 1000}, device_scale_factor=2)
            pg.goto('file://' + p(f'print/Faction-Card-A/Планшет — {fac}.html'))
            pg.evaluate('document.fonts.ready')
            pg.wait_for_timeout(400)
            png = pg.locator('.card').first.screenshot()
            b.close()
        _faces[fac] = Image.open(io.BytesIO(png)).convert('RGB')
    return _faces[fac]


def recruit(fac):
    k = 'rec-' + fac
    if k not in _tinted:
        _tinted[k] = tint('print/Units/adept.png', FACTION_COLOR[fac])
    return _tinted[k]


def tint_hex(col, a):
    """Цвет фракции, разбавленный белым: a — доля цвета."""
    c = col.lstrip('#')
    r, g, b = (int(c[i:i + 2], 16) for i in (0, 2, 4))
    return '#%02X%02X%02X' % tuple(round(255 - (255 - v) * a) for v in (r, g, b))


def halo_text(x, y, s, size=2.6, anchor='middle', fill=MUTED, weight=None):
    return text(x, y, s, size, anchor=anchor, fill=fill, weight=weight,
                extra=' paint-order="stroke" stroke="#FFFFFF" stroke-width="0.7" stroke-opacity="0.85"')


def box_spot(mp, rid, bw, bh, pad=1.2):
    """Центр прямоугольника bw × bh (мм полосы), целиком лежащего в регионе и во врезке;
    из подходящих — самый удалённый от границы региона."""
    reg, _ = geo(mp.cfg)
    polys = reg[rid]['polys']
    others = [r['polys'] for k, r in reg.items() if k != rid and r['type'] != 'OCEAN'] \
        if reg[rid]['type'] == 'OCEAN' else []
    inv = lambda X, Y: (mp.win[0] + (X - mp.ox) / mp.s, mp.win[1] + (Y - mp.oy) / mp.s)
    best = None
    Y = mp.y + bh / 2 + pad
    while Y < mp.y + mp.h - bh / 2 - pad:
        X = mp.x + bw / 2 + pad
        while X < mp.x + mp.w - bw / 2 - pad:
            pts = [(X + dx * bw / 2, Y + dy * bh / 2) for dx in (-1, 0, 1) for dy in (-1, 0, 1)]
            if all(inside(inv(a, b), polys) and not any(inside(inv(a, b), o) for o in others)
                   for a, b in pts):
                d = edge_dist(inv(X, Y), polys) * mp.s
                if best is None or d > best[0]:
                    best = (d, (X, Y))
            X += 1.0
        Y += 1.0
    return best[1] if best else None


def start_cluster(fac, cx, cy, h=4.6, row=False):
    """Стартовые силы: фабрика с рекрутом сверху (контроль) и пять рекрутов рядом —
    двумя рядами (3 + 2) или, в узком регионе, одной строкой (row)."""
    out = []
    im = recruit(fac)
    rw = h * im.width / im.height
    fs = 6.6
    step = rw + 0.8
    fx = cx - (5 * step + fs) / 2 + fs / 2 if row else cx - 6.5
    out.append(image(factory_token(), fx - fs / 2, cy - fs / 2 + 1.2, fs, fs, dpi=300, fmt='PNG'))
    out.append(image(im, fx - rw / 2, cy - h / 2 - 1.0, rw, h, dpi=360, fmt='PNG'))
    for i in range(5):
        if row:
            X, Y = fx + fs / 2 + 0.8 + i * step, cy - h / 2 + 0.6
        else:
            r_, c_ = i // 3, i % 3
            X = cx - 1.2 + c_ * step + r_ * step / 2
            Y = cy - h - 0.2 + r_ * (h + 0.5)
        out.append(image(im, X, Y, rw, h, dpi=360, fmt='PNG'))
    return '\n'.join(out)


def oil_pill(cx, cy, label, zero=False):
    """Плашка «+2 нефть» у источника; zero — «0» серым."""
    col = BORDER if zero else ACCENT
    w = 4.2 if zero else 7.0
    body = (f'<rect x="{f(cx - w / 2)}" y="{f(cy - 2.0)}" width="{f(w)}" height="4.0" rx="2.0" '
            f'fill="#FFFFFF" stroke="{col}" stroke-width="0.45"/>')
    if zero:
        return body + text(cx, cy + 1.05, '0', 2.9, anchor='middle', cls='n', fill=MUTED)
    return (body + f'<text x="{f(cx - 0.6)}" y="{f(cy + 1.05)}" font-size="2.9" text-anchor="middle">'
            f'<tspan class="n">{esc(label)}</tspan><tspan class="g" font-size="2.6" dx="0.3">R</tspan></text>')


ORDINAL = {1: 'первой', 2: 'второй', 3: 'третьей', 4: 'четвёртой'}


def build_primer():
    """После §2.6 — стол на четверых после подготовки: поле на четверых (вариант Б),
    четыре фракции первой партии в стартовых регионах, очередь расстановки, первый игрок.
    Сидящие сверху смотрят на поле с другой стороны — их планшеты повёрнуты (текст — нет)."""
    cfg = '4P-B'
    reg, _ = geo(cfg)
    # фракция, очередь на планшете, регион на планшете, регион этого поля
    seats = [  # сверху: слева, справа; снизу: слева, справа
        ('Глобал Петролеум', 3, 'Европа', 'Европа'),
        ('Эйркрафт Корпорейшн', 2, 'Южная Азия', 'Азия'),
        ('Островная Империя', 1, 'Юг Тихого океана', 'Юг Тихого океана'),
        ('Клонэйд Ресёрч', 7, 'Западная Африка', 'Африка'),
    ]
    order = {fac: i + 1 for i, (fac, *_ ) in enumerate(sorted(seats, key=lambda s: s[1]))}
    out = []
    out.append(text(0, 3.4, 'Пример. Стол на четверых после подготовки', 3.1, cls='h', weight='bold'))
    pw_ = 42.0
    face0 = planshet_face(seats[0][0])
    ph_ = pw_ * face0.height / face0.width
    top_y, bh = 7.0, 170.0 * 550 / 900
    board_y = top_y + ph_ + 8.0
    bot_y = board_y + bh + 8.0

    def seat(i, fac, queue, plan_reg, board_reg):
        top = i < 2
        x = (i % 2) * 86.0
        y = top_y if top else bot_y
        o = []
        face = planshet_face(fac)
        o.append(image(face.rotate(180) if top else face, x, y, pw_, ph_, dpi=300, fmt='JPEG'))
        n = order[fac]
        o.append(badge(x + (pw_ - 0.5 if top else 2.8), y + (ph_ if top else 0), str(n), r=2.6))
        lx = x + pw_ + 3.5
        logo = trim(load(f'{ACR_LOGO}/{fac}.png').convert('RGBA'))
        o.append(image(logo, lx, y + 0.3, 6.2, 6.2, dpi=300, fmt='PNG'))
        nm = fac.split(' ', 1)
        o.append(lines(lx + 7.6, y + 2.9, nm, 2.8, lead=1.15, weight='bold'))
        o.append(text(lx, y + 11.2, f'Очередь: {queue:02d}', 2.5, fill=MUTED))
        o.append(text(lx, y + 14.8, f'Регион: {plan_reg}', 2.5, fill=MUTED))
        if board_reg != plan_reg:
            o.append(text(lx, y + 18.4, f'→ на этом поле: {board_reg}', 2.5, fill=ACCENT, weight='bold'))
        if fac == 'Островная Империя':
            tok = trim(load(f'{ACR}/08. Жетон первого игрока - ⌀30 мм.png').convert('RGBA'))
            o.append(image(tok, lx, y + ph_ - 6.4, 6.4, 6.4, dpi=300, fmt='PNG'))
            o.append(text(lx + 7.8, y + ph_ - 2.4, 'первый игрок (п. 2.5)', 2.5, fill=INK))
        return '\n'.join(o)

    style = {}
    for fac, _, _, rname in seats:
        style[rid_by_name(cfg, rname)] = {'fill': tint_hex(FACTION_COLOR[fac], 0.22),
                                         'stroke': FACTION_COLOR[fac], 'sw': 0.6}
    mp = MapPanel(cfg, (0, 0, 900, 550), 0, board_y, W, bh)
    out.append(mp.draw(style, uid='pr'))
    for i, (fac, queue, plan_reg, board_reg) in enumerate(seats):
        rid = rid_by_name(cfg, board_reg)
        c = box_spot(mp, rid, 23.0, 15.0)
        if c:                              # два ряда, подпись снизу
            cx, cy = c
            out.append(start_cluster(fac, cx, cy - 1.0))
            out.append(badge(cx + 11.5, cy - 6.0, str(order[fac]), r=2.2))
            out.append(halo_text(cx, cy + 8.6, board_reg, 2.5, fill=INK))
        else:                              # узкий регион: одной строкой, подпись справа
            cx, cy = box_spot(mp, rid, 48.0, 9.0, pad=0.6)
            gx = cx - 11.5
            out.append(start_cluster(fac, gx, cy, row=True))
            out.append(badge(gx - 18.5, cy - 0.5, str(order[fac]), r=2.2))
            out.append(halo_text(gx + 15.5, cy + 1.6, board_reg, 2.5, anchor='start', fill=INK))
        out.append(seat(i, fac, queue, plan_reg, board_reg))
    write('primer-stol.svg', svg_doc(W, bot_y + ph_ + 1.0, '\n'.join(out), 'Пример: стол на четверых после подготовки (§2)'))


def build_neft():
    """§4.1 — пример из книги: Александр (Островная Империя) получает 9 нефти."""
    cfg = '5P'
    reg, _ = geo(cfg)
    fac, other = 'Островная Империя', 'Эйркрафт Корпорейшн'
    win = (468, 38, 822, 278)
    mw = 100.0
    mh = mw * (win[3] - win[1]) / (win[2] - win[0])
    my = 7.0
    out = [text(0, 3.4, 'Пример. Александр получает нефть', 3.1, cls='h', weight='bold')]
    mp = MapPanel(cfg, win, 0, my, mw, mh)
    eur, sca = rid_by_name(cfg, 'Европа'), rid_by_name(cfg, 'Скандинавия')
    arb, afw = rid_by_name(cfg, 'Аравийский полуостров'), rid_by_name(cfg, 'Северная Азия')
    out.append(mp.draw({}, uid='nf'))
    rec = recruit(fac)
    RH = 6.0
    rw = RH * rec.width / rec.height
    fs = 8.4

    def factory_with(cx, cy, who):
        o = [image(factory_token(), cx - fs / 2, cy - fs / 2 + 1.6, fs, fs, dpi=300, fmt='PNG')]
        if who:
            o.append(image(who, cx - rw / 2, cy - RH / 2 - 1.2, rw, RH, dpi=360, fmt='PNG'))
        return '\n'.join(o)

    for rid in (eur, sca, arb, afw):
        b = box_spot(mp, rid, 22, 18) or mp.P(mp.anchor(rid))
        cx, cy = b
        nm = reg[rid]['name']
        out.append(halo_text(cx, cy + 8.0, nm, 2.4))
        if rid in (eur, arb):              # фабрика под контролем: рекрут на ней
            out.append(factory_with(cx - 2.5, cy - 1.5, rec))
            out.append(oil_pill(cx + 6.2, cy - 4.2, '+1'))
            out.append(oil_pill(cx + 6.2, cy + 0.6, '+2'))
        elif rid == afw:                   # незанятая фабрика
            out.append(factory_with(cx - 2.5, cy - 1.5, None))
            out.append(oil_pill(cx + 6.2, cy - 1.0, '+1'))
        else:                              # рекрут и боевая машина
            out.append(image(rec, cx - 6.5 - rw / 2, cy - RH / 2 - 1.5, rw, RH, dpi=360, fmt='PNG'))
            out.append(oil_pill(cx - 6.5, cy - 7.4, '+1'))
            tank, _ = put_unit('Танк МЕГ-01', cx + 3.0, cy - 1.2, h=UNIT_H['Танк МЕГ-01'] * 1.15)
            out.append(tank)
            out.append(oil_pill(cx + 3.0, cy - 6.6, '0', zero=True))
    # расчёт справа
    x0 = mw + 6.0
    cw = W - x0
    y = my + 2.0
    panel_at = len(out)
    out.append(f'<rect x="{f(x0 + 3)}" y="{f(y + 1.2)}" width="3.2" height="3.2" rx="0.6" '
               f'fill="{FACTION_COLOR[fac]}" stroke="{INK}" stroke-width="0.25"/>')
    out.append(text(x0 + 7.6, y + 4.0, 'Александр — Островная Империя', 2.7, weight='bold'))
    y += 9.0
    cap = recruit(other)
    tank_im = unit_img('Танк МЕГ-01')
    rows = [
        ('rec', 'Пехотинцы в игре: 3 × 1', 'двое из них стоят на фабриках', '3'),
        ('fac+', 'Фабрики под контролем: 2 × 2', None, '4'),
        ('fac', 'Незанятая фабрика на поле', 'её получает каждый игрок', '1'),
        ('cap', 'Захваченный пехотинец', 'на планшете; сразу вернуть Илье', '1'),
        ('tank', 'Боевая машина', 'нефти не приносит', '0'),
    ]
    for kind, t1, t2, v in rows:
        ix = x0 + 5.5
        if kind == 'rec':
            o = image(rec, ix - rw / 2 * 0.8, y - 0.5, rw * 0.8, RH * 0.8, dpi=360, fmt='PNG')
        elif kind == 'cap':
            o = image(cap, ix - rw / 2 * 0.8, y - 0.5, rw * 0.8, RH * 0.8, dpi=360, fmt='PNG')
        elif kind == 'tank':
            th_ = 3.6
            tw_ = th_ * tank_im.width / tank_im.height
            o = image(tank_im, ix - tw_ / 2, y + 1.2, tw_, th_, dpi=360, fmt='PNG')
        else:
            o = image(factory_token(), ix - 3.2, y - 0.3, 6.4, 6.4, dpi=300, fmt='PNG')
            if kind == 'fac+':
                o += image(rec, ix - rw / 2 * 0.7, y - 1.6, rw * 0.7, RH * 0.7, dpi=360, fmt='PNG')
        out.append(o)
        out.append(text(x0 + 11.5, y + 2.8, t1, 2.6))
        if t2:
            out.append(text(x0 + 11.5, y + 6.0, t2, 2.3, fill=MUTED))
        out.append(text(x0 + cw - 3.5, y + 4.4, v, 4.6, anchor='end', cls='n',
                        fill=MUTED if v == '0' else INK))
        y += 9.4
    out.append(f'<line x1="{f(x0 + 3)}" y1="{f(y - 1.0)}" x2="{f(x0 + cw - 3)}" y2="{f(y - 1.0)}" '
               f'stroke="{INK}" stroke-width="0.35"/>')
    out.append(text(x0 + 11.5, y + 4.6, 'Итого', 3.0, weight='bold'))
    out.append(f'<text x="{f(x0 + cw - 3.5)}" y="{f(y + 5.6)}" font-size="6.4" text-anchor="end">'
               f'<tspan class="n" style="fill:{ACCENT}">9</tspan><tspan class="g" font-size="5.2" dx="0.6">R</tspan></text>')
    ph = max(mh, y + 9.0 - my)
    out.insert(panel_at, f'<rect x="{f(x0)}" y="{f(my)}" width="{f(cw)}" height="{f(ph)}" rx="1.5" '
                         f'fill="#F4F2EE" stroke="{BORDER}" stroke-width="0.35"/>')
    write('istochniki-nefti.svg', svg_doc(W, my + max(mh, ph) + 1.0, '\n'.join(out), 'Источники нефти: пример (§4.1)'))


def build_zheton():
    """§5.2 — две стороны жетона первого игрока. Жетон акриловый: с обратной стороны
    рисунок зеркальный, стрелка смотрит в другую сторону — это и есть направление хода."""
    tok = trim(load(f'{ACR}/08. Жетон первого игрока - ⌀30 мм.png').convert('RGBA'))
    sides = [(tok.transpose(Image.FLIP_LEFT_RIGHT), 'по часовой стрелке'), (tok, 'против часовой стрелки')]
    th = 28.0                    # вдвое меньше прежнего (D-142): рисунок, а не главный герой листа
    tw = th * tok.width / tok.height
    out = []
    for i, (im, cap) in enumerate(sides):
        cx = W / 2 + (i * 2 - 1) * 30.0
        out.append(image(im, cx - tw / 2, 1.0, tw, th, dpi=300, fmt='PNG'))
        out.append(text(cx, th + 6.0, cap, 3.0, anchor='middle', weight='bold'))
    out.append(text(W / 2, th + 11.0, 'Две стороны одного жетона первого игрока', 2.6, anchor='middle', fill=MUTED))
    write('zheton.svg', svg_doc(W, th + 13.0, '\n'.join(out), 'Жетон первого игрока: направление хода (§5.2)'))

# ══════════════════════════════════════════════════════════════ ЗАПУСК
СБОРКА = {
    'planshet': build_planshet,
    'trek': build_trek,
    'polya': build_polya,
    'stol': build_stol,
    'kuklovod': build_kuklovod,
    'primer': build_primer,
    'neft': build_neft,
    'zheton': build_zheton,
    'bitva': build_bitva,
    'roy': build_roy,
    'komponenty': build_komponenty,
    'frakcii': build_frakcii,
    'znaki': build_znaki,
    'koncovki': build_koncovki,
    'valve': build_valve,
    'ref_duel': build_ref_duel,
    'office': build_office,
    'truce': build_truce,
    'komiks': build_komiks,
}


def main():
    global SRC, OUT
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    SRC, OUT = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
    os.makedirs(OUT, exist_ok=True)
    names = sys.argv[3:] or list(СБОРКА)
    for n in names:
        print(n)
        СБОРКА[n]()


if __name__ == '__main__':
    main()
