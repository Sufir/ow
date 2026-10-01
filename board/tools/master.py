"""Печатные мастера полей 900 × 550 (этап 3, шаг 6).

Берёт готовые board/geo/board-<id>.svg и делает из каждого растровый PDF
300 dpi в двух раскладках:

  trim    910 × 560 мм — поле + 5 мм на обрез со всех сторон (SPEC §2:
          «запас на обрез 5 мм сверх технологического поля»). Для заказа
          «в размер» через менеджера.
  canvas  1000 × 700 мм — онлайн-холст баннера «100×70 см» в «Фотокопи»:
          поле с вылетом по центру, вокруг белое, уголки реза снаружи вылета.

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
import os
import re
import sys

import img2pdf
from PIL import Image, ImageCms
from playwright.sync_api import sync_playwright

Image.MAX_IMAGE_PIXELS = None

DPI = 300
TRIM = (900.0, 550.0)
BLEED = 5.0
BOARDS = ('MC-3P', 'MC-4P-A', 'MC-4P-B', 'MC-5P')
PAPER = '#ece8df'                 # фон листа в board-*.svg
CANVAS = (1000.0, 700.0)          # онлайн-холст баннера 100×70
MARK = dict(gap=2.0, len=10.0, w=0.25, colour='#000000')
CAPTION_MM = 4.0
TILE = 1024                       # CSS px на плитку рендера
PX_PER_MM = 96 / 25.4             # CSS px в мм


def layouts():
    tw, th = TRIM
    bw, bh = tw + 2 * BLEED, th + 2 * BLEED
    cw, ch = CANVAS
    return {
        'trim': dict(page=(bw, bh), origin=(BLEED, BLEED), marks=False),
        'canvas': dict(page=(cw, ch), origin=((cw - tw) / 2, (ch - th) / 2),
                       marks=True),
    }


def board_inner(svg_text):
    """Содержимое board-*.svg без корневого тега, фон растянут на вылет."""
    body = re.sub(r'^.*?<svg[^>]*>', '', svg_text, count=1, flags=re.S)
    body = re.sub(r'</svg>\s*$', '', body, flags=re.S)
    old = f'<rect width="900" height="550" fill="{PAPER}"/>'
    if old not in body:
        raise SystemExit('нет фонового прямоугольника 900×550 — формат svg изменился')
    new = (f'<rect x="{-BLEED}" y="{-BLEED}" width="{TRIM[0] + 2 * BLEED}" '
           f'height="{TRIM[1] + 2 * BLEED}" fill="{PAPER}"/>')
    return body.replace(old, new, 1)


def marks_svg(ox, oy):
    """Уголки реза снаружи вылета: по два штриха на угол, продолжают линии реза."""
    tw, th = TRIM
    g, L = BLEED + MARK['gap'], MARK['len']
    out = []
    for x in (ox, ox + tw):
        for y, d in ((oy, -1), (oy + th, 1)):
            out.append(f'M{x:.2f},{y + d * g:.2f}V{y + d * (g + L):.2f}')
    for y in (oy, oy + th):
        for x, d in ((ox, -1), (ox + tw, 1)):
            out.append(f'M{x + d * g:.2f},{y:.2f}H{x + d * (g + L):.2f}')
    return (f'<path d="{" ".join(out)}" fill="none" stroke="{MARK["colour"]}" '
            f'stroke-width="{MARK["w"]}"/>')


def page_html(bid, inner, lay):
    pw, ph = lay['page']
    ox, oy = lay['origin']
    bw, bh = TRIM[0] + 2 * BLEED, TRIM[1] + 2 * BLEED
    parts = [f'<rect width="{pw}" height="{ph}" fill="#ffffff"/>',
             f'<svg x="{ox - BLEED}" y="{oy - BLEED}" width="{bw}" height="{bh}" '
             f'viewBox="{-BLEED} {-BLEED} {bw} {bh}" overflow="hidden">{inner}</svg>']
    if lay['marks']:
        parts.append(marks_svg(ox, oy))
        cap = (f'Нефтяные войны · поле {bid} · {TRIM[0]:.0f} × {TRIM[1]:.0f} мм · '
               f'резать по уголкам · {DPI} dpi')
        parts.append(f'<text x="{ox}" y="{oy + TRIM[1] + BLEED + MARK["gap"] + MARK["len"] + 6}" '
                     f'font-family="OpenGostTypeB" font-size="{CAPTION_MM}" fill="#555">{cap}</text>')
    W, H = pw * PX_PER_MM, ph * PX_PER_MM
    return (f'<!doctype html><meta charset="utf-8"><style>html,body{{margin:0;padding:0;'
            f'background:#fff}}svg{{display:block}}</style>'
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.3f}" height="{H:.3f}" '
            f'viewBox="0 0 {pw} {ph}">{"".join(parts)}</svg>')


def render(page, html_path, lay):
    pw, ph = lay['page']
    W, H = pw * PX_PER_MM, ph * PX_PER_MM
    dsf = DPI / 96
    PW, PH = round(pw / 25.4 * DPI), round(ph / 25.4 * DPI)
    page.set_viewport_size({'width': int(W) + 1, 'height': int(H) + 1})
    page.goto('file://' + html_path)
    page.evaluate('document.fonts.ready')
    page.wait_for_timeout(800)
    img = Image.new('RGB', (PW, PH), 'white')
    for ty in range(0, int(H) + 1, TILE):
        for tx in range(0, int(W) + 1, TILE):
            cw, ch = min(TILE, W - tx), min(TILE, H - ty)
            if cw <= 0 or ch <= 0:
                continue
            png = page.screenshot(clip={'x': tx, 'y': ty, 'width': cw, 'height': ch})
            tile = Image.open(io.BytesIO(png)).convert('RGB')
            img.paste(tile, (round(tx * dsf), round(ty * dsf)))
    return img.crop((0, 0, PW, PH)), dsf


def save_pdf(img, lay, path):
    pw, ph = lay['page']
    icc = ImageCms.ImageCmsProfile(ImageCms.createProfile('sRGB')).tobytes()
    buf = io.BytesIO()
    img.save(buf, 'JPEG', quality=94, subsampling=0, dpi=(DPI, DPI), icc_profile=icc)
    mm = img2pdf.mm_to_pt
    fun = img2pdf.get_layout_fun((mm(pw), mm(ph)), fit=img2pdf.FitMode.exact)
    with open(path, 'wb') as f:
        f.write(img2pdf.convert(buf.getvalue(), layout_fun=fun))


def main():
    root, out = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2])
    ids = sys.argv[3:] or BOARDS
    os.makedirs(out, exist_ok=True)
    geo = os.path.join(root, 'board', 'geo')
    with sync_playwright() as p:
        b = p.chromium.launch(args=['--force-color-profile=srgb'])
        pg = b.new_page(device_scale_factor=DPI / 96)
        for bid in ids:
            inner = board_inner(open(os.path.join(geo, f'board-{bid}.svg'), encoding='utf-8').read())
            for name, lay in layouts().items():
                html = os.path.join(geo, f'_master-{bid}-{name}.html')
                with open(html, 'w', encoding='utf-8') as f:
                    f.write(page_html(bid, inner, lay))
                img, _ = render(pg, html, lay)
                os.remove(html)
                pdf = os.path.join(out, f'поле-{bid}-{name}.pdf')
                save_pdf(img, lay, pdf)
                img.resize((img.width // 10, img.height // 10), Image.LANCZOS).save(
                    os.path.join(out, f'_preview-{bid}-{name}.png'))
                print(bid, name, img.size, f'{os.path.getsize(pdf) / 1e6:.1f} МБ')
        b.close()


if __name__ == '__main__':
    main()
