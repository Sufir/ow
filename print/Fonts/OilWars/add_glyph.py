"""Добавляет или заменяет значок в шрифте проекта `print/Fonts/Oil Wars.ttf`.

    python add_glyph.py <шрифт.ttf> <значок.svg> <Буква> [--out путь] [--version 1.2]

Значок берётся из SVG как есть: высота viewBox ложится в 700 единиц
(высота всех значков шрифта, от базовой линии вверх), по бокам поля
по 25 единиц, как у остальных глифов. Буква и её строчная пара
получают ОДИН глиф, а не два одинаковых (icons.yaml, «один глиф = одно
значение»). Попутно сводит к одному глифу старые пары E/e, Q/q, W/w,
которые сборщик FontMaker развёл в копии.

Зависимости: fonttools.
"""
import argparse, re, sys
from fontTools.ttLib import TTFont
from fontTools.pens.t2CharStringPen import T2CharStringPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.svgLib.path import SVGPath
from fontTools import subset

HEIGHT, SIDE = 700, 25


def glyph_from_svg(svg_path, private):
    svg = SVGPath(svg_path)
    vb = [float(v) for v in re.search(r'viewBox="([^"]+)"', open(svg_path, encoding='utf-8').read()).group(1).split()]
    k = HEIGHT / vb[3]
    width = round(vb[2] * k) + 2 * SIDE
    pen = T2CharStringPen(width - private.nominalWidthX, None)
    # SVG: y вниз от верха viewBox → шрифт: y вверх от базовой линии
    svg.draw(TransformPen(pen, (k, 0, 0, -k, SIDE - vb[0] * k, HEIGHT + vb[1] * k)))
    return pen.getCharString(private=private), width


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('font'); ap.add_argument('svg'); ap.add_argument('char')
    ap.add_argument('--out')
    ap.add_argument('--version', help='новая версия шрифта, например 1.2')
    a = ap.parse_args()
    up, lo = a.char.upper(), a.char.lower()
    name = 'uni%04X' % ord(up)

    f = TTFont(a.font, recalcBBoxes=False)
    head0 = [getattr(f['head'], k) for k in ('xMin', 'yMin', 'xMax', 'yMax')]
    cff = f['CFF '].cff
    td = cff.topDictIndex[0]
    cs = td.CharStrings
    charstring, width = glyph_from_svg(a.svg, td.Private)

    order = list(f.getGlyphOrder())            # копия: у CFF это тот же список, что charset
    if name in cs.charStrings:                     # заменить
        cs.charStringsIndex[cs.charStrings[name]] = charstring
    else:                                          # добавить
        cs.charStrings[name] = len(cs.charStringsIndex)
        cs.charStringsIndex.append(charstring)
        order.append(name)
        td.charset = order
        f.setGlyphOrder(order)
        cff.charStringsAreIndexed = True
    f['hmtx'][name] = (width, 0)

    # cmap: прописная и строчная — на один глиф; старые пары тоже
    for t in f['cmap'].tables:
        if not t.isUnicode():
            continue
        t.cmap[ord(up)] = name
        if lo != up:
            t.cmap[ord(lo)] = name
        for u, l in (('E', 'e'), ('Q', 'q'), ('W', 'w')):
            if ord(u) in t.cmap:
                t.cmap[ord(l)] = t.cmap[ord(u)]

    # Пересохранить и перечитать: после правки CFF и порядка глифов таблицы
    # должны сойтись, прежде чем их тронет subsetter.
    import io
    buf = io.BytesIO(); f.save(buf); buf.seek(0); f = TTFont(buf, recalcBBoxes=False)

    # Выбросить глифы, на которые больше ничего не ссылается,
    # maxp пересчитается сам.
    opts = subset.Options()
    opts.name_IDs = ['*']; opts.name_languages = ['*']; opts.name_legacy = True
    opts.notdef_outline = True; opts.glyph_names = True
    opts.layout_features = ['*']; opts.hinting = True; opts.desubroutinize = False
    opts.drop_tables = []
    # Метрики и габариты шрифта не трогаем: от них зависит вёрстка принятых компонентов.
    opts.recalc_bounds = False; opts.recalc_average_width = False; opts.recalc_max_context = False
    opts.prune_unicode_ranges = False
    s = subset.Subsetter(opts)
    s.populate(unicodes=[u for t in f['cmap'].tables if t.isUnicode() for u in t.cmap])
    s.subset(f)
    # Габарит шрифта в head — прежний, расширяется только если новый значок за него вышел.
    from fontTools.pens.boundsPen import BoundsPen
    bp = BoundsPen(f.getGlyphSet()); f.getGlyphSet()[name].draw(bp)
    x0, y0, x1, y1 = bp.bounds
    h = f['head']
    h.xMin, h.yMin = min(head0[0], int(x0)), min(head0[1], int(y0))
    h.xMax, h.yMax = max(head0[2], int(round(x1))), max(head0[3], int(round(y1)))
    if a.version:
        h.fontRevision = float(a.version)
        for n in f['name'].names:
            if n.nameID == 5:
                n.string = a.version
    f.save(a.out or a.font)
    print(f'{up}/{lo} → {name}, ширина {width}')


if __name__ == '__main__':
    main()
