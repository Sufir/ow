# -*- coding: utf-8 -*-
"""Сборка планшетов фракции, вариант A. Читает _faction-data.json и back-text.json."""
import io, json, math, os, re, html

ROOT = os.path.dirname(os.path.abspath(__file__))
DATA = json.load(io.open(os.path.join(ROOT, '_faction-data.json'), encoding='utf-8'))
BACK = json.load(io.open(os.path.join(ROOT, '_back-text.json'), encoding='utf-8'))

# ---------------------------------------------------------------- геометрия
CARD_W, CARD_H, PAD, GAP = 240.0, 170.0, 6.0, 4.0
ROW_TRACK, ROW_RAIL, ROW_BODY = 18.0, 0.0, 136.0
COL_LEFT, COL_ABIL, COL_TABLE = 66.0, 85.0, 69.0
C_ICON, C_GROUP, C_STAT = 24.0, 6.0, 13.0
BODY_TOP = PAD + ROW_TRACK + GAP                   # 28 мм
X_ABIL_R = PAD + COL_LEFT + GAP + COL_ABIL       # 161 мм
X_TABLE = X_ABIL_R + GAP                         # 165 мм

# ---------------------------------------------------- единый вид переменной силы
# В ячейке «Сила» переменное значение обозначается одной буквой n, расшифровка —
# строкой под отрядом, тем же розовым, что и само значение.
# Исходные состояния в print/Saved не трогаем: подмена только здесь.
#
# Moon Systems «Зардоз» сознательно НЕ переведён: у него сила действительно 0,
# а звёздочка помечает боевой эффект (лишняя смерть в броске), а не формулу силы.
# Перевод в n изменил бы смысл.
#
# Североамериканский «Абрамс 2220»: в исходниках у «?» нет никакой расшифровки.
# Правило не выдумываем — значение оставлено как есть, вопрос вынесен в отчёт.
POWER = {
 ('Глобал Петролеум',          '"Вихрь"'):        'n',
 ('Клонэйд Ресёрч',            '"Жнец"'):         'n',
 ('Сайнтифик Солюшн',          '“Шредингер”'):    'n',
 ('Эйркрафт Корпорейшн',       'Спрут'):          'n',
 ('Североамериканский Альянс', '“Техасец”'):      'n',
}
# Комментарий под отрядом: ключ — начало исходного текста, значение — новый текст.
CMT = {
 'Глобал Петролеум': {
   'Сила равна текущей стоимости': 'n — сила равна текущей стоимости оказания давления на треке влияния.',
   'n - кол-во юнитов':            'n — количество юнитов этого типа в регионе.',
 },
 'Клонэйд Ресёрч': {
   'Сила равна сумме ваших пехотинцев':
     'n — сила равна сумме ваших пехотинцев на поле и фабрик под вашим контролем.'},
 'Сайнтифик Солюшн': {
   '* Сила равна удвоенному':
     'n — сила равна удвоенному количеству вражеских боевых роботов, находящихся в игре.'},
 'Эйркрафт Корпорейшн': {
   'Сила равна сумме ваших технологий':
     'n — сила равна сумме ваших технологий и технологий противника в этой битве.'},
 'Североамериканский Альянс': {
   '* Сила равна текущему запасу нефти':
     'n — сила равна текущему запасу нефти вашего противника, но не меньше 2.'},
}
def power_of(key, cap, val):
    return POWER.get((key, cap.replace('\xa0', ' ')), val)
def cmt_of(key, text):
    for pref, new in CMT.get(key, {}).items():
        if text.lstrip().startswith(pref): return new
    return text

PT = 25.4 / 72.0
def line_h(pt, lh=1.22): return pt * PT * lh
def cpl(width_mm, pt):   return max(8, int((width_mm - 2.0) / (pt * PT * 0.50)))

# высота силуэта по роли: рекрут меньше всех, боевые роботы крупнее всех
ICON_H = {'infantry1': 9.0, 'infantry2': 10.5, 'machine': 12.0, 'mech': 12.5, 'robot': 14.5}

def role_of(group, idx_in_group):
    g = (group or '').lower()
    if 'пехот' in g:  return 'infantry1' if idx_in_group == 0 else 'infantry2'
    if 'мех' in g:    return 'mech'
    if g.startswith('бр') or 'робот' in g: return 'robot'
    return 'machine'

# ---------------------------------------------------------------- ассеты
LOGO = {
 'Островная Империя': 'Островная Империя.png', 'Эйркрафт Корпорейшн': 'Эйркрафт Корпорейшн.png',
 'Глобал Петролеум': 'Глобал Петролеум.png',   'Братство Сингулярности': 'Братство Сингулярности.png',
 'Клонэйд Ресёрч': 'Клонэйд Ресёрч.png',       'Moon Systems': 'Moon Systems.png',
 'Сайнтифик Солюшн': 'Сайнтифик Солюшн.png',   'Североамериканский Альянс': 'Североамериканский Альянс.png',
}
UNITS = {
 'Островная Империя': {'Рекрут':'Units/adept.png','Полковник':'Units/colonel.png',
   'Моторизированный морпех':'Units/ОстровнаяИмперия/Морпех.png','Робот "Цунами"':'Units/ОстровнаяИмперия/Цунами.png',
   'Танк "МЕГ-01"':'Units/ОстровнаяИмперия/Мегалодон.png','C.R.A.B.':'Units/ОстровнаяИмперия/Краб.png'},
 'Эйркрафт Корпорейшн': {'Рекрут':'Units/adept.png','Полковник':'Units/colonel.png',
   'Дрон “Ночной призрак”':'Units/Эйркрафт Корпорейшн/Ночной призрак.png',
   'Самолёт “Фантом”':'Units/Эйркрафт Корпорейшн/Фантом.png',
   'Робот “Небесный охотник”':'Units/Эйркрафт Корпорейшн/Небесный охотник.png',
   '“Спрут”':'Units/Эйркрафт Корпорейшн/Спрут.png'},
 'Глобал Петролеум': {'Рекрут':'Units/adept.png','Полковник':'Units/colonel.png',
   'ББМП "Саранча"':'Units/ГлобалПетролеум/ББМ Саранча.png',
   'Моторизированный десантник':'Units/ГлобалПетролеум/Моторизированный десантник.png',
   '"Шепард"':'Units/ГлобалПетролеум/Пастух.png','"Вихрь"':'Units/ГлобалПетролеум/БР Вихрь.png'},
 'Братство Сингулярности': {'Рекрут':'Units/adept.png','Полковник':'Units/Братство Сингулярности/Полковник.png',
   'Фанатик':'Units/Братство Сингулярности/Боец.png','Киборг':'Units/Братство Сингулярности/Киборг.png',
   '“Паладин”':'Units/Братство Сингулярности/Паладин.png'},
 'Клонэйд Ресёрч': {'Рекрут':'Units/adept.png','Полковник':'Units/colonel.png',
   'Робот “Стервятник”':'Units/Клонэйд Ресёрч/Стервятник.png','Танк “Чёрная смерть”':'Units/Клонэйд Ресёрч/Танк.png',
   '“Рипо” М-3':'Units/Клонэйд Ресёрч/Рипер.png','"Жнец"':'Units/Клонэйд Ресёрч/БР.png'},
 'Moon Systems': {'Андроид':'Units/MoonNet/Андроид.png','Модель 2':'Units/MoonNet/Бишоп341b.png',
   'Т-800':'Units/MoonNet/Т800.png','Т-1000':'Units/MoonNet/Т1000.png','“Зардоз”':'Units/MoonNet/БР Зардоз.png'},
 'Сайнтифик Солюшн': {'Рекрут':'Units/adept.png','Полковник':'Units/colonel.png',
   'ББМ “Квант”':'Units/Сайнтифик Солюшн/Квант.png','РСЗО “Вектор”':'Units/Сайнтифик Солюшн/Катюша.png',
   '“Тесла-Танк”':'Units/Сайнтифик Солюшн/Тесла.png','“Шредингер”':'Units/Сайнтифик Солюшн/Шрёдингер.png'},
 'Североамериканский Альянс': {'Рекрут':'Units/adept.png','Полковник':'Units/colonel.png',
   'БРМ “Визард”':'Units/СевероамериканскийАльянс/БРМ “Визард”.png','БРМ “Снейк”':'Units/СевероамериканскийАльянс/БРМ “Снейк”.png',
   '“Абрамс 2220”':'Units/СевероамериканскийАльянс/Абрамс.png','“Техасец”':'Units/СевероамериканскийАльянс/БР.png'},
}
# правки заведомо испорченных полей (см. отчёт: JSON перезаписаны 22.09, поля перекрёстно загрязнены)
FIXES = {'Сайнтифик Солюшн': {'region': 'любой свободный'}}

def esc(s): return html.escape(s, quote=False)

SYM = re.compile(r'<span[^>]*class="sym"[^>]*>(.*?)</span>', re.S)
TAG = re.compile(r'<[^>]+>')

def rich(s):
    """Оставляем только символы регионов (шрифт Oil Wars), всё прочее — текст."""
    s = SYM.sub(lambda m: '\x01' + m.group(1) + '\x02', s)
    s = TAG.sub('', s)
    s = esc(s)
    return s.replace('\x01', '<span class="sym">').replace('\x02', '</span>')

# ---------------------------------------------------------------- сборка
HEAD = os.environ.get('HEAD', 'wm')      # wm = логотип подложкой, track = логотип в полосе трека
HEXW = 13.8 if HEAD == 'wm' else 12.6


def build(key, d):
    name = d['name'] or key
    fixes = FIXES.get(key, {})
    region = fixes.get('region', d['region'])

    # ---- отряды: роли, высоты, вертикальная раскладка таблицы
    rows, gi, cur_group = [], 0, None
    for r in d['rows']:
        if r['k'] == 'u':
            if r['group']: cur_group, gi = r['group'], 0
            role = role_of(cur_group, gi); gi += 1
            rows.append(dict(r, role=role, ih=ICON_H[role]))
        else:
            rows.append(dict(r)); cur_group = cur_group
    y, geo = 4.6, {}                                   # 4.6 — шапка таблицы
    for r in rows:
        if r['k'] == 'u':
            h = r['ih'] + 5.8
            geo[r['id']] = y + r['ih'] + 2.0           # середина подписи юнита
            y += h
        elif r['k'] == 's': y += 2.7
        else:
            n = max(1, math.ceil(len(r['text']) / cpl(COL_TABLE, 9)))
            y += n * line_h(9) + 1.6
    table_h = y

    # ---- способности: порядок как на исходном планшете (поле y состояния)
    props = sorted(d['props'], key=lambda p: p.get('y', 0))
    link_row = {}
    order_of = {r['id']: i for i, r in enumerate(rows) if r['k'] == 'u'}
    for l in d['links']: link_row[l['p']] = order_of.get(l['u'], 99)

    # ---- оценка высоты блока способности
    W = cpl(COL_ABIL, 9)
    for p in props:
        lines = sum(max(1, math.ceil(len(x) / W)) for x in p['desc'])
        p['h'] = 0.8 + line_h(12.5, 0.98) + line_h(9, 1.15) + 0.6 + lines * line_h(9)

    # ---- умное распределение: тянем к своему юниту, но не в ущерб порядку
    tops, cur = [], 0.0
    for i, p in enumerate(props):
        t = None
        if p['id'] in link_row and link_row[p['id']] < 99:
            t = geo.get(next(l['u'] for l in d['links'] if l['p'] == p['id']), None)
            if t is not None: t -= p['h'] / 2.0
        top = cur if (i == 0 or t is None) else max(cur, t)
        tops.append(top); cur = top + p['h'] + 3.0
    over = cur - 3.0 - ROW_BODY
    if over > 0:                                       # не влезло — ужимаем добавленные отступы
        extra = [tops[i] - (tops[i-1] + props[i-1]['h'] + 3.0) if i else 0 for i in range(len(props))]
        tot = sum(extra)
        if tot > 0:
            k = max(0.0, 1 - over / tot); run = 0.0
            for i, p in enumerate(props):
                run = run + extra[i] * k if i else 0.0
                tops[i] = run
                run += p['h'] + 3.0
    left = ROW_BODY - (cur - 3.0)
    if left > 12.0 and len(props) > 1:                 # остаток делим пополам между зазорами
        add = (left * 0.55) / (len(props) - 1)
        for i in range(1, len(props)): tops[i] += add * i
    margins = [tops[0]] + [tops[i] - (tops[i-1] + props[i-1]['h'] + 3.0) for i in range(1, len(props))]

    # ---- связи
    links_svg = []
    for i, p in enumerate(props):
        for l in d['links']:
            if l['p'] != p['id'] or l['u'] not in geo: continue
            ya = BODY_TOP + tops[i] + 0.8 + line_h(12.5, 0.98) / 2.0   # строка заголовка свойства
            yu = BODY_TOP + geo[l['u']]
            links_svg.append('<polyline points="%.1f,%.1f %.1f,%.1f %.1f,%.1f %.1f,%.1f"/>\n'
                             '      <circle cx="%.1f" cy="%.1f" r="0.9"/>'
                             % (X_ABIL_R, ya, X_ABIL_R+2.5, ya, X_ABIL_R+2.5, yu, X_TABLE+4, yu, X_ABIL_R, ya))

    # ---- разметка
    ab = []
    for p, m in zip(props, margins):
        body = ''.join('<div>%s</div>' % rich(x) for x in p['desc'])
        lnk = next((l['u'] for l in d['links'] if l['p'] == p['id']), '')
        ab.append('        <div class="ability" data-link="%s" style="margin-top: %.1fmm;">\n'
                  '          <div class="ability-name">%s</div>\n'
                  '          <div class="ability-note">%s</div>\n'
                  '          <div class="ability-text">%s</div>\n'
                  '        </div>' % (esc(lnk), max(0.0, m), esc(p['title']), esc(p['note']), body))

    tb, pend = [], None
    for r in rows:
        if r['k'] == 's':
            tb.append('            <tr class="sep"><td colspan="5"><div class="unit-sep"></div></td></tr>')
        elif r['k'] == 'c':
            txt = cmt_of(key, r['text'])
            # Розовым — только расшифровки значения в колонке «Сила»: они начинаются
            # с «n —» или со звёздочки, парной звёздочке в ячейке. Прочие заметки
            # (например «Особенность…» у Братства) остаются белыми.
            cls = 'cmt pw' if txt.lstrip()[:1] in ('*',) or txt.lstrip().startswith('n —') else 'cmt'
            tb.append('            <tr class="%s"><td colspan="5">%s</td></tr>' % (cls, rich(txt)))
        else:
            src = UNITS.get(key, {}).get(r['cap'].replace('\xa0', ' '))
            img = ('<img src="../%s" style="height: %.1fmm;" alt="">' % (esc(src), r['ih'])) if src else \
                  ('<div class="noimg" style="height: %.1fmm;">нет файла</div>' % r['ih'])
            gl = ''
            if r['group']:
                span = 0
                for q in rows[rows.index(r):]:
                    if q['k'] != 'u': break
                    if q is not r and q['group']: break
                    span += 1
                gl = '<td class="group-label" rowspan="%d">%s</td>' % (span, esc(r['group']))
            c = (r['cells'] + ['', '', ''])[:3]
            tb.append('            <tr>\n              <td class="u-icon">%s<div class="unit-cap" data-uid="%s">%s</div></td>%s\n'
                      '              <td class="stat count">%s</td><td class="stat">%s</td>'
                      '<td class="stat power">%s</td>\n'
                      '            </tr>' % (img, esc(r['id']), esc(r['cap']), gl,
                                             esc(c[0]), esc(c[1]), esc(power_of(key, r['cap'], c[2]))))

    panels = []
    for p in d['panels']:
        steps = ''.join('\n            <li>%s</li>' % rich(s) for s in p['steps'])
        panels.append('        <div>\n          <div class="block-title">%s</div>\n'
                      '          <ol class="steps">%s\n          </ol>\n        </div>' % (esc(p['title']), steps))

    bt = BACK.get(key, {'lore': '', 'guide': []})
    guide = ''.join('\n      <p>%s</p>' % esc(x) for x in bt['guide'])

    HEXH = HEXW * 0.866
    # Цепочка гексов одним SVG: штрих в SVG центрируется на контуре, поэтому на общих
    # рёбрах две обводки ложатся друг на друга и дают ту же толщину, что на свободных.
    def hexpts(i):
        L = i * 0.75 * HEXW; T = (HEXH / 2 if i % 2 else 0)
        return ' '.join('%.3f,%.3f' % q for q in
                        [(L + .25 * HEXW, T), (L + .75 * HEXW, T), (L + HEXW, T + HEXH / 2),
                         (L + .75 * HEXW, T + HEXH), (L + .25 * HEXW, T + HEXH), (L, T + HEXH / 2)])
    CH_W = 19 * 0.75 * HEXW + HEXW
    CH_H = HEXH * 1.5
    HEX = ('\n          <svg class="hexgrid" viewBox="0 0 %.3f %.3f" width="%.3fmm" height="%.3fmm"'
           ' xmlns="http://www.w3.org/2000/svg" aria-hidden="true">' % (CH_W, CH_H, CH_W, CH_H)
           + ''.join('\n            <polygon points="%s"/>' % hexpts(i) for i in range(20))
           + '\n          </svg>')
    HEX += ''.join('\n          <div class="hex" style="left: %.2fmm; top: %.2fmm;"><span>%d</span></div>'
                   % (i * 0.75 * HEXW, (HEXH / 2 if i % 2 else 0), i + 1) for i in range(20))

    logo_src = '../../art/logos/' + esc(LOGO.get(key, ''))
    if HEAD == 'wm':
        head = ('        <div class="head-wm">\n'
                '          <img class="logo-wm" src="%s" alt="">\n'
                '          <div class="faction-name">%s</div>\n'
                '        </div>' % (logo_src, esc(name)))
        headtrack = ''
    else:
        head = ('        <div>\n'
                '          <div class="faction-name">%s</div>\n'
                '        </div>' % esc(name))
        headtrack = '\n        <img class="logo-track" src="%s" alt="">' % logo_src

    vals = {'name': esc(name), 'head': head, 'headtrack': headtrack,
            'hexw': '%.2f' % HEXW, 'hexh': '%.2f' % HEXH, 'logo': esc(LOGO.get(key, '')), 'region': esc(region),
            'queue': esc(d['queue']), 'oil': esc(d['oil']), 'notes': rich(d['notes']),
            'hexes': HEX, 'panels': '\n'.join(panels), 'abilities': '\n'.join(ab),
            'tbody': '\n'.join(tb), 'links': '\n      '.join(links_svg),
            'lore': esc(bt['lore']), 'guide': guide,
            'cardh': '%g' % CARD_H,
            'table_h': '%.1f' % table_h, 'over': '%.1f' % max(0.0, cur - 3.0 - ROW_BODY)}
    out = TPL
    for k, v in vals.items():
        out = out.replace('@@%s@@' % k, v)
    return out


TPL = io.open(os.path.join(ROOT, 'template.html'), encoding='utf-8').read()

if __name__ == '__main__':
    for key, d in DATA.items():
        s = build(key, d)
        io.open(os.path.join(ROOT, 'Планшет — %s.html' % key), 'w', encoding='utf-8').write(s)
        print('%-26s таблица %5s мм | перелив способностей %s мм' %
              (key, re.search(r'data-table-h="([\d.]+)"', s).group(1),
               re.search(r'data-over="([\d.]+)"', s).group(1)))
