"""
badge.py — плашка состава на игровом поле: значок «игроки за столом» и число игроков.

Решение Alek 12.10.2026 (D-130): на каждом поле явно указан состав, на который оно
рассчитано. Плашка повторяет плашку состава на треке Судного дня
(print/Saved/Трек Судного дня.pdf, правый нижний угол): тёмное поле, неоновая рамка
пурпурный → голубой со скошенными углами и внешними уголками, белый значок
четырёх человек за круглым столом, белое число полужирным.

Где и какая:
  - правый нижний угол полотна, как на треке; там на всех четырёх полях открытая вода
    Индийского океана правее Антарктиды, подписей и символов нет;
  - внешний край плашки — на границе безопасного поля 5 мм (boardcheck.SAFE, D-124);
  - высота 9 мм, ширина по тексту (около 19–22 мм): читается при подготовке,
    в игре не спорит с подписями регионов (их кегль 4–6 мм, плашка океанов светлая);
  - шрифт — Liberation Sans Bold (D-091), кегль 5,4 мм, цифры высотой 3,9 мм.

Текст: MC-3P — «3», MC-4P-A — «4a», MC-4P-B — «4b», MC-5P — «5». Буквы — те же,
что в id полей и в реестре компонентов.

Рисует boardview.py: svg() и html() добавляют слой <g id="badge"> поверх подписей.
Сам не запускается. Зависимости: Pillow (ширина текста по TTF).
"""
from pathlib import Path

from PIL import ImageFont

import boardcheck as bc

ROOT = Path(__file__).resolve().parents[2]
FONT = 'Liberation Sans'
FONT_FILE = ROOT / 'print' / 'Fonts' / 'LiberationSans-Bold.ttf'
FONT_URL = '../../print/Fonts/LiberationSans-Bold.ttf'     # от board/geo/

TEXT = {'MC-3P': '3', 'MC-4P-A': '4a', 'MC-4P-B': '4b', 'MC-5P': '5'}

H = 9.0            # мм, высота плашки
OUT = 0.9          # мм, отступ внешних уголков от плашки
CHAMFER = 1.3      # мм, скос углов плашки
PAD = 1.5          # мм, поля слева и справа
GAP = 1.3          # мм, между значком и числом
FS = 5.4           # мм, кегль числа
ICON = 0.44        # мм на единицу значка (значок 16 × 14 единиц → 7,0 × 6,2 мм)
FILL = '#0e1216'   # тёмное поле плашки
WHITE = '#ffffff'
ALIGN = 'center'   # где число в поле шириной tmax: left — у значка, center, right
NEON = ('#e35cf7', '#1ba8ec')   # пурпурный → голубой, сняты с плашки трека


def text_width(s):
    f = ImageFont.truetype(str(FONT_FILE), 1000)
    return f.getlength(s) / 1000 * FS


def font_css():
    return f"@font-face{{font-family:'{FONT}';font-weight:700;src:url('{FONT_URL}') format('truetype')}}"


def chamfer_d(x0, y0, x1, y1, c):
    return (f'M{x0 + c:.2f},{y0:.2f}H{x1 - c:.2f}L{x1:.2f},{y0 + c:.2f}V{y1 - c:.2f}'
            f'L{x1 - c:.2f},{y1:.2f}H{x0 + c:.2f}L{x0:.2f},{y1 - c:.2f}V{y0 + c:.2f}Z')


def brackets_d(x0, y0, x1, y1, c, lx, ly):
    """внешние уголки: по куску у каждого угла, со скосом"""
    return (f'M{x0 + lx:.2f},{y0:.2f}H{x0 + c:.2f}L{x0:.2f},{y0 + c:.2f}V{y0 + ly:.2f}'
            f'M{x1 - lx:.2f},{y0:.2f}H{x1 - c:.2f}L{x1:.2f},{y0 + c:.2f}V{y0 + ly:.2f}'
            f'M{x0 + lx:.2f},{y1:.2f}H{x0 + c:.2f}L{x0:.2f},{y1 - c:.2f}V{y1 - ly:.2f}'
            f'M{x1 - lx:.2f},{y1:.2f}H{x1 - c:.2f}L{x1:.2f},{y1 - c:.2f}V{y1 - ly:.2f}')


def icon(x, y):
    """четыре человека за круглым столом: трое за дальним краем, один спиной к нам.
    Координаты в единицах 16 × 14, (x, y) — левый верхний угол в мм"""
    cut = f'stroke="{FILL}" stroke-width="0.9"'
    back = ''.join(f'<rect x="{bx}" y="{by}" width="4" height="5.2" rx="1.7" fill="{WHITE}"/>'
                   f'<circle cx="{bx + 2}" cy="{by - 1.9}" r="1.6" fill="{WHITE}"/>'
                   for bx, by in ((0.6, 4.4), (6, 3.7), (11.4, 4.4)))
    table = (f'<ellipse cx="8" cy="8.3" rx="6.4" ry="1.9" fill="none" stroke="{FILL}" stroke-width="2.2"/>'
             f'<ellipse cx="8" cy="8.3" rx="6.4" ry="1.9" fill="none" stroke="{WHITE}" stroke-width="0.8"/>')
    front = (f'<rect x="6" y="10.4" width="4" height="3.6" rx="1.5" fill="{WHITE}" {cut}/>'
             f'<circle cx="8" cy="9.2" r="1.6" fill="{WHITE}" {cut}/>')
    return f'<g transform="translate({x:.2f},{y:.2f}) scale({ICON})">{back}{table}{front}</g>'


def svg_layer(layout):
    """плашка состава; пусто, если раскладка неизвестна"""
    s = TEXT.get(layout)
    if not s:
        return '', ''
    W, Hc = bc.CANVAS
    tw = text_width(s)
    tmax = max(text_width(t) for t in TEXT.values())    # ширина одна на все поля — по самому длинному
    w = PAD + 16 * ICON + GAP + tmax + PAD
    x1 = W - bc.SAFE - OUT
    y1 = Hc - bc.SAFE - OUT
    x0, y0 = x1 - w, y1 - H
    defs = (f'<linearGradient id="badge-neon" gradientUnits="userSpaceOnUse" x1="{x0 - OUT:.2f}" y1="0" '
            f'x2="{x1 + OUT:.2f}" y2="0"><stop offset="0" stop-color="{NEON[0]}"/>'
            f'<stop offset="1" stop-color="{NEON[1]}"/></linearGradient>'
            f'<filter id="badge-glow" x="-20%" y="-50%" width="140%" height="200%">'
            f'<feGaussianBlur stdDeviation="0.45"/></filter>')
    frame = chamfer_d(x0, y0, x1, y1, CHAMFER)
    out = brackets_d(x0 - OUT, y0 - OUT, x1 + OUT, y1 + OUT, CHAMFER + 0.4, 6.0, 3.2)
    iy = y0 + (H - 14 * ICON) / 2
    zone = x0 + PAD + 16 * ICON + GAP        # поле числа: от значка до правого поля плашки
    tx = zone + {'left': 0, 'center': (tmax - tw) / 2, 'right': tmax - tw}[ALIGN]
    ty = y0 + H / 2 + 0.358 * FS          # середина высоты прописной
    layer = (f'<title>Состав: {s}</title>'
             f'<path d="{frame}" fill="none" stroke="url(#badge-neon)" stroke-width="1.3" '
             f'opacity="0.75" filter="url(#badge-glow)"/>'
             f'<path d="{frame}" fill="{FILL}" stroke="url(#badge-neon)" stroke-width="0.45"/>'
             f'<path d="{out}" fill="none" stroke="url(#badge-neon)" stroke-width="0.28" opacity="0.9"/>'
             f'{icon(x0 + PAD, iy)}'
             f'<text x="{tx:.2f}" y="{ty:.2f}" font-family="{FONT}" font-weight="700" font-size="{FS}" '
             f'fill="{WHITE}">{s}</text>')
    return defs, layer
