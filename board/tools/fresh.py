import sys, numpy as np; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import os as _os
_W = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', 'sketch')
_W = _os.path.normpath(_W)
_os.makedirs(_W, exist_ok=True)
import repair
from partition import make_grid
import layout as L
L.MAPD=repair.MAPD; L.GEO=repair.MAPD+'/geo'
X,Y,inner,nx,ny = make_grid(); tg = repair.targets(inner)
rot = float(sys.argv[1]) if len(sys.argv)>1 else 80.0
seeds = repair.sketch_seeds(rot)
repair.ZONE = {r:v for r,v in seeds.items() if repair.REG[r][2]}
lab,_,_ = repair.init_balanced(seeds, inner)
m,e,rm,re = repair.graph_state(lab, inner)
print('поворот %3.0f: нарушений %d (нет %d, лишних %d, рамка -%d/+%d)'
      % (rot, len(m)+len(e)+len(rm)+len(re), len(m), len(e), len(rm), len(re)), flush=True)
np.save(_os.path.join(_W, 'lab_fresh_%d.npy')%int(rot), lab)
