"""Печатные мастера полей 900 × 550 (этап 3, шаг 6; карта в край — D-124).

Берёт готовые board/geo/board-<id>.svg и делает из каждого растровый PDF
300 dpi в двух раскладках:

  trim    910 × 560 мм — поле + 5 мм вылета со всех сторон. Для заказа
          «в размер» с технической обрезкой. Файл поле-<id>-печать-900x550.pdf.
  canvas  1000 × 700 мм — онлайн-холст баннера «100×70 см» (или атлас 105×70):
          поле с вылетом по центру, вокруг белое, уголки реза снаружи вылета.
          Файл поле-<id>-холст-100x70.pdf.

В обоих PDF задан TrimBox (рез 900 × 550) и BleedBox (рез + 5 мм).

Карта идёт в край полотна, технологического поля нет. Вылет — отражение
кромки карты на 5 мм: у края только океаны и льды (подписи и знаки не ближе
5 мм к резу, boardcheck.SAFE), поэтому отражённая полоса неотличима
от продолжения и после обрезки не видна.

Почему растр: размытия (переход между океанами, тень и свечение фона)
в PDF всё равно растрируются, а конструктор типографии принимает
JPG/PNG/TIFF/PDF и проверяет 150 dpi. Растр 300 dpi снимает вопросы
про шрифты, фильтры и прозрачности. Цвет — sRGB с профилем в файле.

Запуск — там, где есть Playwright + Chromium (на ПК его нет, рендер
идёт в облачном контейнере Claude):

    python master.py SRC_ROOT OUT_DIR [ID ...]

SRC_ROOT — корень проекта (нужны board/geo/*.svg и print/Fonts/).
"""
import io
import math
import os
import re
import sys

import img2pdf
import numpy as np
from PIL import Image, ImageCms, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

Image.MAX_IMAGE_PIXELS = None

DPI = 300
TRIM = (900.0, 550.0)
BLEED = 5.0
BOARDS = ('MC-3P', 'MC-4P-A', 'MC-4P-B', 'MC-5P')
CANVAS = (1000.0, 700.0)          # онлайн-холст баннера 100×70
MARK = dict(gap=2.0, len=10.0, w=0.25)
CAPTION_MM = 4.0
NAMES = {'trim': 'печать-900x550', 'canvas': 'холст-100x70'}    # имя файла = что заказывать
TILE = 1024                       # CSS px на плитку рендера
PX_PER_MM = 96 / 25.4             # CSS px в мм


def px(mm):
    return round(mm / 25.4 * DPI)


def layouts():
    tw, th = TRIM
    cw, ch = CANVAS
    return {
        'trim': dict(page=(tw + 2 * BLEED, th + 2 * BLEED), origin=(BLEED, BLEED), marks=False),
        'canvas': dict(page=(cw, ch), origin=((cw - tw) / 2, (ch - th) / 2), marks=True),
    }


def board_html(svg_text):
    """board-*.svg как есть, корень — на весь лист 900 × 550 в CSS px"""
    body = re.sub(r'^.*?<svg[^>]*>', '', svg_text, count=1, flags=re.S)
    body = re.sub(r'</svg>\s*$', '', body, flags=re.S)
    W, H = page_css()
    return (f'<!doctype html><meta charset="utf-8"><style>html,body{{margin:0;padding:0;'
            f'background:#fff}}svg{{display:block}}</style>'
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
            f'viewBox="0 0 {W / PX_PER_MM:.4f} {H / PX_PER_MM:.4f}" overflow="hidden">{body}</svg>')


def page_css():
    """лист в целых CSS px с запасом за край карты: при дробном размере Chromium оставляет у правого
    и нижнего края белую нитку. За краем карты — продолжение областей (boardview.past_edge)"""
    return math.ceil(TRIM[0] * PX_PER_MM) + 2, math.ceil(TRIM[1] * PX_PER_MM) + 2


def render(page, html_path):
    """поле 900 × 550 в 300 dpi, плитками — так Chromium не упирается в предел текстуры"""
    W, H = page_css()
    dsf = DPI / 96
    page.set_viewport_size({'width': W, 'height': H})
    page.goto('file://' + html_path)
    page.evaluate('document.fonts.ready')
    page.wait_for_timeout(800)
    img = Image.new('RGB', (round(W * dsf), round(H * dsf)), 'white')
    for ty in range(0, H, TILE):
        for tx in range(0, W, TILE):
            cw, ch = min(TILE, W - tx), min(TILE, H - ty)
            png = page.screenshot(clip={'x': tx, 'y': ty, 'width': cw, 'height': ch})
            img.paste(Image.open(io.BytesIO(png)).convert('RGB'), (round(tx * dsf), round(ty * dsf)))
    return img.crop((0, 0, px(TRIM[0]), px(TRIM[1])))


def with_bleed(img):
    """вылет: кромка карты отражена на BLEED мм с каждой стороны"""
    b = px(TRIM[0] + 2 * BLEED) - img.width
    l, r = b // 2, b - b // 2
    b = px(TRIM[1] + 2 * BLEED) - img.height
    t, d = b // 2, b - b // 2
    a = np.pad(np.asarray(img), ((t, d), (l, r), (0, 0)), mode='symmetric')
    return Image.fromarray(a)


def on_canvas(bled, bid, lay, font_path):
    """холст 1000 × 700: поле с вылетом по центру, уголки реза и подпись снаружи"""
    pw, ph = lay['page']
    ox, oy = lay['origin']
    tw, th = TRIM
    img = Image.new('RGB', (px(pw), px(ph)), 'white')
    img.paste(bled, (px(ox - BLEED), px(oy - BLEED)))
    d = ImageDraw.Draw(img)
    w = max(1, px(MARK['w']))
    g, L = BLEED + MARK['gap'], MARK['len']
    for x in (ox, ox + tw):
        for y, s in ((oy, -1), (oy + th, 1)):
            d.line([(px(x), px(y + s * g)), (px(x), px(y + s * (g + L)))], fill='black', width=w)
    for y in (oy, oy + th):
        for x, s in ((ox, -1), (ox + tw, 1)):
            d.line([(px(x + s * g), px(y)), (px(x + s * (g + L)), px(y))], fill='black', width=w)
    cap = (f'Нефтяные войны, поле {bid}, {tw:.0f} x {th:.0f} мм, резать по уголкам, {DPI} dpi')   # в шрифте нет · и ×
    font = ImageFont.truetype(font_path, px(CAPTION_MM))
    d.text((px(ox), px(oy + th + g + L + 2)), cap, fill='#555555', font=font)
    return img


def save_pdf(img, lay, path):
    pw, ph = lay['page']
    icc = ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB')).tobytes()
    buf = io.BytesIO()
    img.save(buf, 'JPEG', quality=94, subsampling=0, dpi=(DPI, DPI), icc_profile=icc)
    mm = img2pdf.mm_to_pt
    fun = img2pdf.get_layout_fun((mm(pw), mm(ph)), fit=img2pdf.FitMode.exact)
    with open(path, 'wb') as f:
        f.write(img2pdf.convert(buf.getvalue(), layout_fun=fun))
    set_boxes(path, lay)


def set_boxes(path, lay):
    """TrimBox — линия реза 900 × 550, BleedBox — она же + вылет. По ним RIP
    типографии сам видит формат обреза, не только по имени файла."""
    import pikepdf
    pw, ph = lay['page']
    ox, oy = lay['origin']
    tw, th = TRIM
    pt = img2pdf.mm_to_pt
    x0, y0 = ox, ph - oy - th                      # PDF считает y снизу
    trim = [pt(x0), pt(y0), pt(x0 + tw), pt(y0 + th)]
    bleed = [pt(x0 - BLEED), pt(y0 - BLEED), pt(x0 + tw + BLEED), pt(y0 + th + BLEED)]
    with pikepdf.open(path, allow_overwriting_input=True) as pdf:
        page = pdf.pages[0]
        page.TrimBox = pikepdf.Array(trim)
        page.BleedBox = pikepdf.Array(bleed)
        pdf.save(path)


def main():
    root, out = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
    ids = sys.argv[3:] or BOARDS
    os.makedirs(out, exist_ok=True)
    geo = os.path.join(root, 'board', 'geo')
    font = os.path.join(root, 'print', 'Fonts', 'OpenGostTypeB.ttf')
    L = layouts()
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--force-color-profile=srgb'])
        pg = b.new_page(device_scale_factor=DPI / 96)
        for bid in ids:
            html = os.path.join(geo, f'_master-{bid}.html')
            with open(html, 'w', encoding='utf-8') as f:
                f.write(board_html(open(os.path.join(geo, f'board-{bid}.svg'), encoding='utf-8').read()))
            bled = with_bleed(render(pg, html))
            os.remove(html)
            for name, img in (('trim', bled), ('canvas', on_canvas(bled, bid, L['canvas'], font))):
                pdf = os.path.join(out, f'поле-{bid}-{NAMES[name]}.pdf')
                save_pdf(img, L[name], pdf)
                print(bid, name, img.size, f'{os.path.getsize(pdf) / 1e6:.1f} МБ')
        b.close()


if __name__ == '__main__':
    main()
