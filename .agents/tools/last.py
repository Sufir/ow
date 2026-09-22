import sys, numpy as np, random; sys.path.insert(0,'/sessions/modest-confident-hypatia/w2')
import repair
from partition import make_grid
from scipy import ndimage
import layout as L
L.MAPD=repair.MAPD; L.GEO=repair.MAPD+'/geo'
X,Y,inner,nx,ny=make_grid(); tg=repair.targets(inner)
seeds=repair.sketch_seeds(90.0); repair.ZONE={r:v for r,v in seeds.items() if repair.REG[r][2]}
I=repair.IDX; K=repair.K
base=np.load('/sessions/modest-confident-hypatia/w2/lab_panama.npy')
REQ = repair.req_pairs(with_panama=True)
def score(l):
    pr=repair.adj_of(l,inner); got=set((i,j) for i,j in pr if j<K); rim=set(i for i,j in pr if j==K)
    return len(REQ-got)+len(got-REQ)+len(repair.RIM_OK-rim)+len(rim-repair.RIM_OK), got
bn,_=score(base); best=base.copy(); print('вход %d'%bn, flush=True)
rng=random.Random(9)
CAM,SAME,NA,SAMW = I["MR-L5-CAM"],I["MR-L5-SAME"],I["MR-OC-NATL"],I["MR-L5-SAMW"]
for trial in range(60):
    lab=best.copy()
    k = trial % 3
    if k==0: repair.force_path(lab, inner, CAM, SAME, width=rng.choice([1,2]))
    elif k==1: repair.force_path(lab, inner, SAME, CAM, width=rng.choice([1,2]))
    else: repair.separate(lab, inner, NA, SAMW, rng)
    repair.reconnect(lab, inner)
    n,_=score(lab)
    if n<bn:
        bn=n; best=lab.copy(); print('   лучше: %d'%bn, flush=True)
        if bn==0: break
np.save('/sessions/modest-confident-hypatia/w2/lab_final.npy', best)
n,got=score(best)
print('итог: %d нарушений; рёбер %d из %d'%(n, len(REQ&got)+len(repair.RIM_OK), len(REQ)+6), flush=True)
N=repair.NAMES
print('нет:', '; '.join('%s—%s'%(repair.REG[N[i]][0],repair.REG[N[j]][0]) for i,j in sorted(REQ-got)) or '—')
print('лишние:', '; '.join('%s—%s'%(repair.REG[N[i]][0],repair.REG[N[j]][0]) for i,j in sorted(got-REQ)) or '—')
ar=np.bincount(best[inner].ravel(),minlength=K+1)[:K]*repair.GRID**2/100
print('площади ±%.0f см²'%np.abs(ar-tg).sum())
pieces={i:ndimage.label(best==i,structure=repair.CONN)[1] for i in range(K)}
print('в нескольких кусках:', ', '.join('%s×%d'%(repair.REG[N[i]][0],n) for i,n in pieces.items() if n>1) or '—')
