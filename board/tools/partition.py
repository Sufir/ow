# -*- coding: utf-8 -*-
"""
partition.py — разбиение поля на 21 область, верное по графу MC-5P.

Вариант B, решение Alek 2026-09-18: **граф нарушать нельзя категорически**.
Поэтому порядок обратный прежнему: сначала строится разбиение прямоугольника,
у которого смежности ровно те, что в реестре, и площади в цель, и только потом
ячейки тянутся к очертаниям материков — настолько, насколько граф позволит.

Механика: взвешенная диаграмма (power diagram) по растру.
  - ячейка клетки = argmin_i (|p - s_i|^2 - w_i);
  - область внутри выпуклого поля от этого связна по построению — то самое,
    на чём провалились три попытки нарезать океан из остатка;
  - Северный Ледовитый — рамка по периметру, он в диаграмме не участвует;
  - Антарктида закреплена в центре.
Зёрна двигаются по невязке графа: нет ребра — сводим пару, лишнее — разводим.
Веса правятся по площадям.
"""
import json, math, os, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
MAPD = os.path.dirname(HERE)                      # board/

W, H = 900.0, 550.0
CX, CY = W/2, H/2
FR_END, FR_SIDE = 58.0, 10.0
GRID = 3.0
ARC = "MR-OC-ARC"

REG = {
 "MR-OC-ARC":("Сев. Ледовитый ок.",788,0),"MR-OC-NPAC":("Сев. Тихий ок.",300,0),
 "MR-OC-NATL":("Сев. Атлантика",300,0),"MR-OC-SPAC":("Юг Тихого ок.",250,0),
 "MR-OC-SATL":("Юг Атлантики",250,0),"MR-OC-IND":("Индийский ок.",304,0),
 "MR-SH-ANT":("Антарктида",185,1),"MR-L5-NAMW":("Запад Сев. Америки",175,1),
 "MR-L5-CAM":("Центр. Америка",150,1),"MR-L5-NAME":("Восток Сев. Америки",165,1),
 "MR-L5-SAMW":("Запад Южн. Америки",160,1),"MR-L5-SAME":("Восток Южн. Америки",160,1),
 "MR-L5-AUS":("Австралия",150,1),"MR-L5-NZL":("Новая Зеландия",150,1),
 "MR-R5-AFRW":("Западная Африка",170,1),"MR-R5-AFRE":("Восточная Африка",165,1),
 "MR-R5-EUR":("Европа",175,1),"MR-R5-SCA":("Скандинавия",155,1),
 "MR-R5-ARB":("Аравия",165,1),"MR-R5-ASIN":("Северная Азия",165,1),
 "MR-R5-ASIS":("Южная Азия",180,1),
}
def truth_edges():
    return set(tuple(sorted(e)) for e in json.load(
        open(os.path.join(MAPD,"derived","MC-5P.json"), encoding="utf-8"))["edge_list"])

# --------------------------------------------------------------- растр поля
def make_grid():
    nx, ny = int(W/GRID), int(H/GRID)
    xs = (np.arange(nx)+0.5)*GRID; ys = (np.arange(ny)+0.5)*GRID
    X, Y = np.meshgrid(xs, ys)
    inner = (X > FR_END) & (X < W-FR_END) & (Y > FR_SIDE) & (Y < H-FR_SIDE)
    return X, Y, inner, nx, ny

def areas_of(lab, names, nin):
    a = np.bincount(lab.ravel(), minlength=len(names)).astype(float)
    return a*GRID*GRID/100.0

def adjacency(lab, inner, names):
    """смежности по растру: 4-соседство; рамка — всё, что за inner"""
    K = len(names); pairs = set()
    L = np.where(inner, lab, -1)
    for a, b in ((L[:,:-1], L[:,1:]), (L[:-1,:], L[1:,:])):
        m = (a != b)
        for u, v in zip(a[m].ravel(), b[m].ravel()):
            if u < 0 and v < 0: continue
            i = K if u < 0 else u; j = K if v < 0 else v
            if i != j: pairs.add((min(i,j), max(i,j)))
    return pairs

# ------------------------------------------------------------------ решатель
def solve_partition(seeds0, iters=400, verbose=True):
    truth = truth_edges()
    names = [r for r in REG if r != ARC]
    K = len(names); idx = {n:i for i,n in enumerate(names)}
    X, Y, inner, nx, ny = make_grid()
    P = np.stack([X[inner], Y[inner]], axis=1)          # координаты клеток поля
    cell = GRID*GRID/100.0
    tot = P.shape[0]*cell
    tg = np.array([REG[n][1] for n in names], float)
    tg = tg/tg.sum()*tot                                 # цели нормируются на поле
    S = np.array([seeds0[n] for n in names], float)
    Wt = np.zeros(K)
    fixed = idx["MR-SH-ANT"]
    req = set(); 
    for a,b in truth:
        if a==ARC or b==ARC: continue
        req.add((min(idx[a],idx[b]), max(idx[a],idx[b])))
    rim_ok = set(idx[r] for r in ("MR-OC-NPAC","MR-L5-NAMW","MR-L5-NAME",
                                  "MR-OC-NATL","MR-R5-SCA","MR-R5-ASIN"))
    best, bestsc = None, (-1, 10**9)
    lab_full = np.full((ny,nx), -1, int)
    for it in range(iters):
        d = ((P[:,None,0]-S[None,:,0])**2 + (P[:,None,1]-S[None,:,1])**2) - Wt[None,:]
        lab = np.argmin(d, axis=1)
        lab_full[:] = -1; lab_full[inner] = lab
        ar = np.bincount(lab, minlength=K)*cell
        pr = adjacency(lab_full, inner, names)
        got = set((i,j) for i,j in pr if j < K)
        rim = set(i for i,j in pr if j == K)
        miss = req - got; extra = got - req
        rim_miss = rim_ok - rim; rim_extra = rim - rim_ok
        nbad = len(miss)+len(extra)+len(rim_miss)+len(rim_extra)
        aerr = float(np.abs(ar-tg).sum())
        sc = (-(nbad), -aerr)
        if sc > bestsc: bestsc, best = sc, (S.copy(), Wt.copy(), lab_full.copy(), ar.copy())
        if verbose and it % 40 == 0:
            print("   %3d: рёбер нет %2d, лишних %2d, рамка %d/%d, площади ±%.0f см²"
                  % (it, len(miss), len(extra), len(rim_miss), len(rim_extra), aerr))
        if nbad == 0 and aerr < 60: break
        Wt += (tg-ar)*2.2                                 # площади — весами
        F = np.zeros((K,2))
        cen = np.array([P[lab==i].mean(axis=0) if (lab==i).any() else S[i] for i in range(K)])
        for (i,j) in miss:                                # нет ребра — свести
            v = cen[j]-cen[i]; n = np.hypot(*v) or 1.0
            F[i] += v/n*3.0; F[j] -= v/n*3.0
        for (i,j) in extra:                               # лишнее — развести
            v = cen[j]-cen[i]; n = np.hypot(*v) or 1.0
            F[i] -= v/n*2.2; F[j] += v/n*2.2
        for i in rim_miss:                                # должен выйти на рамку
            v = cen[i]-np.array([CX,CY]); n = np.hypot(*v) or 1.0
            F[i] += v/n*3.5
        for i in rim_extra:                               # рамки касаться нельзя
            v = cen[i]-np.array([CX,CY]); n = np.hypot(*v) or 1.0
            F[i] -= v/n*3.5
        F += (cen-S)*0.35                                 # Ллойд: к своему центру
        F[fixed] = (np.array([CX,CY])-S[fixed])*0.5       # Антарктида — в центре
        S += np.clip(F, -9, 9)
        S[:,0] = np.clip(S[:,0], FR_END+4, W-FR_END-4)
        S[:,1] = np.clip(S[:,1], FR_SIDE+4, H-FR_SIDE-4)
    return best, names, (X,Y,inner,nx,ny), tg

if __name__ == "__main__":
    sys.path.insert(0, HERE)
    import layout as L
    L.MAPD = MAPD; L.GEO = MAPD+"/geo"
    seeds, lay = L.polar_seeds()
    (S,Wt,lab,ar), names, grid, tg = solve_partition(seeds)
    truth = truth_edges(); idx={n:i for i,n in enumerate(names)}
    pr = adjacency(lab, grid[2], names); K=len(names)
    got=set((i,j) for i,j in pr if j<K); rim=set(i for i,j in pr if j==K)
    req=set((min(idx[a],idx[b]),max(idx[a],idx[b])) for a,b in truth if a!=ARC and b!=ARC)
    rim_ok=set(idx[r] for r in ("MR-OC-NPAC","MR-L5-NAMW","MR-L5-NAME","MR-OC-NATL","MR-R5-SCA","MR-R5-ASIN"))
    print("\nИТОГ: рёбер %d/%d, лишних %d; рамка: нужно 6, есть %d, лишних %d"
          % (len(req&got), len(req), len(got-req), len(rim&rim_ok), len(rim-rim_ok)))
    if req-got: print("нет:", ", ".join(sorted("%s—%s"%(REG[names[i]][0],REG[names[j]][0]) for i,j in (req-got))))
    if got-req: print("лишние:", ", ".join(sorted("%s—%s"%(REG[names[i]][0],REG[names[j]][0]) for i,j in (got-req))))
    print("площади: " + ", ".join("%s %.0f/%.0f"%(REG[names[i]][0], ar[i], tg[i]) for i in range(K)))
    np.save(os.path.join(HERE,"part_lab.npy"), lab); np.save(os.path.join(HERE,"part_S.npy"), S)
