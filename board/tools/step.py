import sys, os, numpy as np; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import os as _os
_W = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', 'sketch')
_W = _os.path.normpath(_W)
_os.makedirs(_W, exist_ok=True)
import repair
from partition import make_grid
import layout as L
L.MAPD=repair.MAPD; L.GEO=repair.MAPD+'/geo'
X,Y,inner,nx,ny = make_grid(); tg = repair.targets(inner)
seeds = repair.sketch_seeds(90.0)
repair.ZONE = {r:v for r,v in seeds.items() if repair.REG[r][2]}
F = _os.path.join(_W, 'lab_live.npy')
if os.path.exists(F): lab = np.load(F)
else:
    seeds,_ = L.polar_seeds(); lab,_,_ = repair.init_balanced(seeds, inner)
T0 = float(sys.argv[1]); T1 = float(sys.argv[2]); sec = float(sys.argv[3])
c = repair.cost_of(lab, inner, tg)
print("вход: нарушений %d, разрывов %d, площади ±%.0f" % (c[1],c[2],c[3]), flush=True)
best = repair.anneal_ops(lab, inner, tg, seconds=sec, T0=T0, T1=T1,
                         seed=int(sys.argv[4]), log=lambda s: None)
np.save(F, best[1])
m,e,rm,re = repair.graph_state(best[1], inner)
print("выход: нет %d, лишних %d, рамка -%d/+%d, разрывов %d, площади ±%.0f"
      % (len(m),len(e),len(rm),len(re), best[3], best[4]), flush=True)
