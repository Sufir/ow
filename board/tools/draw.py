import sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import os as _os
_W = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', 'sketch')
_W = _os.path.normpath(_W)
_os.makedirs(_W, exist_ok=True)
import numpy as np, repair, layout as L
from partition import make_grid, REG, GRID, ARC
from shapely.geometry import box as SB
L.MAPD=repair.MAPD; L.GEO=repair.MAPD+'/geo'; L.OUT=_W
lab = np.load(_os.path.join(_W, 'lab_final.npy'))
X,Y,inner,nx,ny = make_grid()
m,e,rm,re = repair.graph_state(lab, inner)
ar = np.bincount(lab[inner].ravel(), minlength=repair.K+1)[:repair.K]*GRID**2/100
tg = np.array([REG[n][1] for n in repair.NAMES], float); tg = tg/tg.sum()*(inner.sum()*GRID**2/100)
ok = all(repair.connected(lab,i) for i in range(repair.K))
print('нет %d, лишних %d, рамка -%d/+%d; площади ±%.0f; связны все: %s'%(len(m),len(e),len(rm),len(re),np.abs(ar-tg).sum(),ok))
L.GRID = GRID
regs = {}
for i,n in enumerate(repair.NAMES):
    ys,xs = np.where(lab==i)
    regs[n] = L.cells_to_poly(list(zip(xs.tolist(), ys.tolist())), simp=2.5)
ys,xs = np.where(lab==repair.K)
regs[ARC] = L.cells_to_poly(list(zip(xs.tolist(), ys.tolist())), simp=2.5)
L.render(regs, "board-B5.svg", "Поле — вариант B, разбиение по графу, граф сведён",
  ["Сначала разбиение, верное по графу, потом география. Граф — императив (решение Alek).",
   "55 рёбер реестра из 56. Композиция по эскизу Alek: Антарктида в центре, рамка по краю, Америки слева, Старый Свет справа.",
   "Центральная Америка — цепочка из трёх кусков: так оригинал проводит воду между Севером Тихого и Севером Атлантики (ME-074).",
   "Очертания материков на этот скелет ещё не натянуты: это следующий шаг."])
import cairosvg; cairosvg.svg2png(url=L.OUT+'/board-B5.svg', write_to=L.OUT+'/board-B5.png', output_width=1600)
print('нарисовано')
