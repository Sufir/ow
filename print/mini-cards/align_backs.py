"""Выравнивание логотипов фракций на рубашках карт задач и технологий.

Каждый логотип перекладывается на квадратное прозрачное полотно 1080×1080 так,
чтобы его центр совпал с центром полотна, а крайняя точка лежала на окружности
радиуса FILL·1080 (доля от стороны полотна). Тогда в круге рубашки все логотипы стоят концентрично
и одного размера; положение круга на рубашке задаёт CSS (.back-center-icon).

Центр логотипа — середина между центром описанной окружности (логотип вписан
в круг) и центроидом выпуклой оболочки (зрительный центр массы): чистая
описанная окружность опускает «орла» крыльями на диаметр.
Вытянутые и «дырявые» силуэты (орёл, трилистник) зрительно легче круглых —
им небольшая компенсация размера, не больше MAX_BOOST.

Запуск: python3 align_backs.py "<путь к Cards - Технологии и задачи.json>"
Повторный запуск безопасен: уже выровненные логотипы не пересэмплируются.
"""
import sys, io, json, base64
import numpy as np, cv2
from PIL import Image

SIZE = 1080
FILL = 0.44        # радиус логотипа / сторона полотна
CENTER_W = 0.5     # 0 — центр описанной окружности, 1 — центроид оболочки
REF_DENSITY = 0.85 # заполнение круга оболочкой у «круглых» логотипов
BOOST_POW = 0.15
MAX_BOOST = 1.12   # FILL·MAX_BOOST < 0.5 — логотип не вылезает за полотно

def normalize(im):
    im = im.convert('RGBA')
    a = np.asarray(im)[:, :, 3]
    ys, xs = np.nonzero(a > 128)
    hull = cv2.convexHull(np.stack([xs, ys], 1).astype(np.float32))
    (ex, ey), _ = cv2.minEnclosingCircle(hull)
    m = cv2.moments(hull)
    hx, hy = m['m10'] / m['m00'], m['m01'] / m['m00']
    cx, cy = ex + (hx - ex) * CENTER_W, ey + (hy - ey) * CENTER_W
    h = hull.reshape(-1, 2)
    r = np.sqrt(((h - [cx, cy]) ** 2).sum(1)).max()
    density = cv2.contourArea(hull) / (np.pi * r * r)
    boost = min(MAX_BOOST, max(1.0, (REF_DENSITY / density) ** BOOST_POW))
    s = FILL * SIZE * boost / r
    info = dict(center=(round(cx), round(cy)), r=round(r), density=round(density, 2), boost=round(boost, 3), scale=round(s, 3))
    if abs(s - 1) < 0.005 and abs(cx - SIZE / 2) < 1 and abs(cy - SIZE / 2) < 1 and im.size == (SIZE, SIZE):
        return None, info  # уже выровнен
    # аффинное преобразование: точка (cx,cy) -> центр полотна, масштаб s
    M = (1 / s, 0, cx - SIZE / 2 / s, 0, 1 / s, cy - SIZE / 2 / s)
    # премультипликация, чтобы на краях не было тёмной каймы
    arr = np.asarray(im).astype(np.float32) / 255
    arr[:, :, :3] *= arr[:, :, 3:4]
    chans = [Image.fromarray(arr[:, :, i]).transform((SIZE, SIZE), Image.AFFINE, M, Image.BICUBIC) for i in range(4)]
    out = np.stack([np.asarray(c) for c in chans], 2).clip(0, 1)
    al = out[:, :, 3:4]
    out[:, :, :3] = np.where(al > 1e-4, out[:, :, :3] / np.maximum(al, 1e-4), 0)
    res = Image.fromarray((out * 255 + 0.5).astype(np.uint8), 'RGBA')
    return res, info

def main(path):
    d = json.load(open(path, encoding='utf8'))
    for k, v in d['imagePool'].items():
        im = Image.open(io.BytesIO(base64.b64decode(v.split(',', 1)[1])))
        res, info = normalize(im)
        print(k, info)
        if res is None:
            continue
        buf = io.BytesIO(); res.save(buf, 'PNG', optimize=True)
        d['imagePool'][k] = 'data:image/png;base64,' + base64.b64encode(buf.getvalue()).decode()
    with open(path, 'w', encoding='utf8') as f:
        json.dump(d, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    main(sys.argv[1])
