"""Мастера значков книги правил — глифы шрифта print/Fonts/Oil Wars.ttf.

    python book-icons.py [папка с print/dices]   # пишет kill.svg, suppress.svg, task.svg рядом

KILL (ICON-018, глиф K) и SUPPRESS (ICON-019, глиф S) не рисуются заново:
это трассировка арта наклеек кубиков, тех же файлов, что стоят в мастере
`print/Saved/Dices Print Sheet.pdf` и на памятке битвы (`print/dices/
kill-simple.png`, `suppress-simple.png`). Иначе одно значение получит
два изображения.
  KILL — чернила там, где на наклейке красный; белый череп выбит.
  SUPPRESS — чернила там, где на наклейке цвет (зелёный и пурпурный);
  белые шевроны, кружки и просветы выбиты.
TASK (ICON-027, глиф G — goal) — вектор знака «Внимание» с карт задач
(D-089, `print/mini-cards/cards-landscape-sixes.css`, `.goal-text::before`)
один в один; контур знака развёрнут против гекса, чтобы он выбивался
и по правилу ненулевого обхода, которым заливает шрифт.

В шрифт: `print/Fonts/OilWars/add_glyph.py <шрифт> kill.svg K`.
Зависимости: numpy, scipy, pillow, potracer.
"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
import potrace

HERE = Path(__file__).parent
DICES = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE.parent / 'dices'


def trace(ink, sigma=1.2, turd=12):
    """ink: bool-маска (True — чернила) → SVG path d; контуры дырок обратного обхода."""
    m = ndi.gaussian_filter(ink.astype(float), sigma) > 0.5 if sigma else ink
    bm = potrace.Bitmap(~m)          # potracer: чернила — False
    plist = bm.trace(turdsize=turd, alphamax=1.0, opticurve=True, opttolerance=0.2)
    d = []
    for c in plist:
        s = c.start_point
        d.append(f'M{s.x:.1f} {s.y:.1f}')
        for seg in c.segments:
            if seg.is_corner:
                d.append(f'L{seg.c.x:.1f} {seg.c.y:.1f}L{seg.end_point.x:.1f} {seg.end_point.y:.1f}')
            else:
                d.append(f'C{seg.c1.x:.1f} {seg.c1.y:.1f} {seg.c2.x:.1f} {seg.c2.y:.1f} '
                         f'{seg.end_point.x:.1f} {seg.end_point.y:.1f}')
        d.append('Z')
    return ''.join(d)


def bbox_crop(ink):
    ys, xs = np.where(ink)
    return ink[ys.min():ys.max() + 1, xs.min():xs.max() + 1]


def write(name, vb, d, note):
    w, h = vb[2], vb[3]
    (HERE / name).write_text(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{" ".join(f"{v:g}" for v in vb)}" '
        f'width="{w:g}" height="{h:g}">\n<!-- {note} -->\n'
        f'<path fill="#000000" fill-rule="evenodd" d="{d}"/>\n</svg>\n', encoding='utf-8')


def main():
    a = np.asarray(Image.open(DICES / 'kill-simple.png').convert('RGB')).astype(int)
    red = (a[..., 0] - (a[..., 1] + a[..., 2]) / 2) > 64
    k = bbox_crop(red)
    write('kill.svg', (0, 0, k.shape[1], k.shape[0]), trace(k),
          'ICON-018 {KILL}: трассировка print/dices/kill-simple.png, красное — чернила; book-icons.py')

    a = np.asarray(Image.open(DICES / 'suppress-simple.png').convert('RGB')).astype(int)
    col = a.min(-1) < 128
    s = bbox_crop(col)
    write('suppress.svg', (0, 0, s.shape[1], s.shape[0]), trace(s),
          'ICON-019 {SUPPRESS}: трассировка print/dices/suppress-simple.png, цветное — чернила; book-icons.py')

    hexagon = 'M15 1.6L27.4 8.8V23.2L15 30.4L2.6 23.2V8.8Z'
    bar = 'M13.6 9.4V18.4H16.4V9.4Z'          # обход обратный гексу
    dot = 'M13.6 20.6V23.4H16.4V20.6Z'
    write('task.svg', (2.6, 1.6, 24.8, 28.8), hexagon + bar + dot,
          'ICON-027 {TASK}: знак «Внимание» карт задач, D-089, вектор из cards-landscape-sixes.css; book-icons.py')


if __name__ == '__main__':
    main()
