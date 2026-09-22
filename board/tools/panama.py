import sys, numpy as np; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import os as _os
_W = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', 'sketch')
_W = _os.path.normpath(_W)
_os.makedirs(_W, exist_ok=True)
import repair
from partition import make_grid
from collections import deque
import layout as L
L.MAPD=repair.MAPD; L.GEO=repair.MAPD+'/geo'
X,Y,inner,nx,ny=make_grid(); tg=repair.targets(inner)
seeds=repair.sketch_seeds(90.0); repair.ZONE={r:v for r,v in seeds.items() if repair.REG[r][2]}
F=_os.path.join(_W, 'lab_live.npy')
lab=np.load(F); I=repair.IDX
NP, NA, CAM = I["MR-OC-NPAC"], I["MR-OC-NATL"], I["MR-L5-CAM"]
# кратчайший проток от Севера Тихого до Севера Атлантики, дешевле всего через
# Центральную Америку: ровно там оригинал рисует цепочку островков
COST = {CAM: 1}
d = np.full(lab.shape, 1e9); prev={}
import heapq
pq=[]
for y,x in zip(*np.where(lab==NP)): d[y,x]=0; heapq.heappush(pq,(0,(int(y),int(x))))
tgt=None
while pq:
    dd,(y,x)=heapq.heappop(pq)
    if dd>d[y,x]: continue
    if lab[y,x]==NA and dd>0: tgt=(y,x); break
    for dy,dx in ((-1,0),(1,0),(0,-1),(0,1)):
        yy,xx=y+dy,x+dx
        if not (0<=yy<ny and 0<=xx<nx) or not inner[yy,xx]: continue
        w = COST.get(int(lab[yy,xx]), 6)
        if lab[yy,xx] in (NP,NA): w = 0.1
        if dd+w < d[yy,xx]:
            d[yy,xx]=dd+w; prev[(yy,xx)]=(y,x); heapq.heappush(pq,(dd+w,(yy,xx)))
path=[]; cur=tgt
while cur in prev: cur=prev[cur]; path.append(cur)
mid=len(path)//2
for k,(y,x) in enumerate(path):
    if lab[y,x] in (NP,NA): continue
    lab[y,x] = NA if k < mid else NP
pr0 = repair.adj_of(lab, inner)
print('после протока смежность есть:', (min(NP,NA),max(NP,NA)) in set((i,j) for i,j in pr0 if j<repair.K))
print('длина пути %d клеток, середина %d' % (len(path), mid))
m,e,rm,re = repair.graph_state(lab, inner)
req_all = repair.req_pairs(with_panama=True)
pr = repair.adj_of(lab, inner); got=set((i,j) for i,j in pr if j<repair.K)
have_panama = (min(NP,NA),max(NP,NA)) in got
pieces = {}
for i in range(repair.K):
    from scipy import ndimage
    _,n = ndimage.label(lab==i, structure=repair.CONN); pieces[i]=n
print('проток проложен: ME-074 есть — %s' % have_panama)
print('куски: ' + ', '.join('%s×%d'%(repair.REG[repair.NAMES[i]][0],n) for i,n in pieces.items() if n>1))
print('весь граф: %d из %d, лишних %d' % (len(req_all&got)+ (6-len(rm)), len(req_all)+6, len(got-req_all)))
N=repair.NAMES
print('нет:', '; '.join('%s—%s'%(repair.REG[N[i]][0],repair.REG[N[j]][0]) for i,j in sorted(req_all-got)) or '—')
print('лишние:', '; '.join('%s—%s'%(repair.REG[N[i]][0],repair.REG[N[j]][0]) for i,j in sorted(got-req_all)) or '—')
np.save(_os.path.join(_W, 'lab_panama.npy'), lab)
