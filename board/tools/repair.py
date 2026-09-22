# -*- coding: utf-8 -*-
"""
repair.py — разбиение поля, верное по графу MC-5P. Вариант B, шаг 1.

Взвешенная диаграмма не годится: её ячейки выпуклы, а Северу Атлантики с его
одиннадцатью соседями нужно извиваться. Поэтому разбиение строится по растру
и правится локально, клетка за клеткой:

  лишнее ребро  — вдоль общей границы пары клетки отдаются третьей области,
                  смежной с обеими: пара разъединяется, граф от этого не рвётся;
  нет ребра     — между областями прокладывается коридор шириной в пару клеток
                  за счёт того, кто стоит между ними;
  площади       — брать стараемся у того, у кого излишек, отдавать тому, кому мало.

Каждый перенос проверяется на связность: область, у которой забрали клетки,
обязана остаться одним куском. Это и есть «все регионы должны сообщаться».
"""
import json, os, sys, math, random
import numpy as np
from scipy import ndimage

HERE = os.path.dirname(os.path.abspath(__file__))
MAPD = os.path.dirname(HERE)                      # board/
sys.path.insert(0, HERE)
from partition import (REG, ARC, W, H, CX, CY, FR_END, FR_SIDE, GRID,
                       truth_edges, make_grid)

NAMES = [r for r in REG if r != ARC]
IDX   = {n:i for i,n in enumerate(NAMES)}
K     = len(NAMES)
RIM_OK = set(IDX[r] for r in ("MR-OC-NPAC","MR-L5-NAMW","MR-L5-NAME",
                              "MR-OC-NATL","MR-R5-SCA","MR-R5-ASIN"))
CONN = np.array([[0,1,0],[1,1,1],[0,1,0]])

# ME-074: Север Тихого и Север Атлантики смежны НАПРЯМУЮ, сквозь Панамский
# перешеек. Именно из-за него граф MC-5P непланарен (EXPERIMENT-POLAR §2.2),
# а смежности любого разбиения плоскости планарны всегда. Значит отжигом это
# ребро не собрать ни при каких усилиях — оригинал рисует там цепочку островков,
# между которыми проходит вода. Из целевой функции ребро выведено, вносится
# отдельным приёмом panama() после того, как сойдётся всё остальное.
PANAMA = ("MR-OC-NPAC", "MR-OC-NATL")
def req_pairs(with_panama=False):
    t = truth_edges()
    out = set((min(IDX[a],IDX[b]), max(IDX[a],IDX[b]))
              for a,b in t if a != ARC and b != ARC)
    if not with_panama:
        out.discard((min(IDX[PANAMA[0]],IDX[PANAMA[1]]), max(IDX[PANAMA[0]],IDX[PANAMA[1]])))
    return out

def adj_of(lab, inner):
    """смежности по 4-соседству; K означает рамку (Северный Ледовитый).
    Считается целиком в numpy: это делается на каждый ход отжига."""
    L = np.where(inner, lab, K)
    u = []; v = []
    for a,b in ((L[:,:-1],L[:,1:]), (L[:-1,:],L[1:,:])):
        m = a!=b
        u.append(a[m]); v.append(b[m])
    u = np.concatenate(u); v = np.concatenate(v)
    lo = np.minimum(u,v); hi = np.maximum(u,v)
    code = np.unique(lo.astype(np.int64)*(K+1) + hi)
    return set((int(c//(K+1)), int(c%(K+1))) for c in code)

def components_penalty(lab):
    """сколько лишних кусков у областей: связность — императив"""
    extra = 0
    for i in range(K):
        m = (lab==i)
        if not m.any(): extra += 3; continue
        _, n = ndimage.label(m, structure=CONN)
        extra += n-1
    return extra

def area_err(lab, inner, tg):
    ar = np.bincount(lab[inner].ravel(), minlength=K+1)[:K]*(GRID*GRID/100.0)
    return float(np.abs(ar-tg).sum()), ar

def targets(inner):
    tg = np.array([REG[n][1] for n in NAMES], float)
    return tg/tg.sum()*(inner.sum()*GRID*GRID/100.0)

# Композиция по эскизу Alek: в центре Антарктида, по краю рамкой Северный
# Ледовитый, слева две Америки, справа Африка с Евразией, Австралия снизу
# по центру. Океаны свободны — они и расчерчиваются между материками.
ZONE = None      # заполняется из sketch_seeds() при старте
# Антарктида в центре, но не строго (уточнение Alek): ей задана не точка,
# а средняя зона поля — внутри неё она гуляет свободно.
ANT_BOX = (330, 185, 570, 365)
ZW = 0.18        # вес композиции: направляет, но графу не мешает
def zone_penalty(lab):
    if ZONE is None: return 0.0
    tot = 0.0
    i = IDX["MR-SH-ANT"]; ys,xs = np.where(lab==i)
    if len(ys):
        cx, cy = xs.mean()*GRID, ys.mean()*GRID
        x0,y0,x1,y1 = ANT_BOX
        tot += max(0, x0-cx) + max(0, cx-x1) + max(0, y0-cy) + max(0, cy-y1)
    for r,(zx,zy) in ZONE.items():
        if r == "MR-SH-ANT": continue
        i = IDX[r]; ys,xs = np.where(lab==i)
        if len(ys)==0: tot += 400; continue
        tot += math.hypot(xs.mean()*GRID-zx, ys.mean()*GRID-zy)
    return tot

def cost_of(lab, inner, tg):
    miss, extra, rmiss, rextra = graph_state(lab, inner)
    nb = len(miss)+len(extra)+len(rmiss)+len(rextra)
    cp = components_penalty(lab)
    ae, _ = area_err(lab, inner, tg)
    return 120.0*nb + 45.0*cp + 0.8*ae + ZW*zone_penalty(lab), nb, cp, ae

def connected(lab, i):
    m = (lab==i)
    if not m.any(): return False
    _, n = ndimage.label(m, structure=CONN)
    return n == 1

def init_labels(seeds, inner):
    X, Y, _, nx, ny = make_grid()
    S = np.array([seeds[n] for n in NAMES], float)
    d = (X[...,None]-S[None,None,:,0])**2 + (Y[...,None]-S[None,None,:,1])**2
    lab = np.argmin(d, axis=2)
    return np.where(inner, lab, -1)

# ------------------------------------------------------------------- отжиг
def build_counts(lab, ny, nx):
    """cnt[i][j] — сколько пар соседних клеток разделяют области i и j.
    Смежность есть, пока cnt > 0. Перенос одной клетки правит cnt за O(1),
    поэтому отжиг может сделать сотни тысяч шагов."""
    cnt = np.zeros((K+1, K+1), int)
    for a,b in ((lab[:,:-1],lab[:,1:]), (lab[:-1,:],lab[1:,:])):
        m = a!=b
        np.add.at(cnt, (np.minimum(a[m],b[m]), np.maximum(a[m],b[m])), 1)
    return cnt

def simple_point(lab, y, x, a):
    """можно ли забрать клетку у области a, не порвав её локально:
    её соседи той же области должны оставаться связными в окне 3x3"""
    ring = [(-1,0),(-1,1),(0,1),(1,1),(1,0),(1,-1),(0,-1),(-1,-1)]
    v = []
    for dy,dx in ring:
        yy,xx = y+dy, x+dx
        v.append(1 if (0<=yy<lab.shape[0] and 0<=xx<lab.shape[1] and lab[yy,xx]==a) else 0)
    if sum(v) == 0: return False
    runs = sum(1 for i in range(8) if v[i] and not v[(i-1)%8])
    return runs == 1

def anneal(lab, inner, steps=420000, T0=2.2, T1=0.02, seed=7, verbose=True):
    rng = random.Random(seed)
    ny, nx = lab.shape
    req = req_pairs()
    tg = np.array([REG[n][1] for n in NAMES], float)
    cell = GRID*GRID/100.0
    tg = tg/tg.sum() * (inner.sum()*cell)
    area = np.bincount(lab[inner].ravel(), minlength=K+1)[:K]*cell
    cnt = build_counts(lab, ny, nx)
    def graph_cost():
        c = 0
        for i,j in req:
            if cnt[i,j] == 0: c += 1
        for i in range(K):
            for j in range(i+1,K):
                if cnt[i,j] > 0 and (i,j) not in req: c += 1
        for i in range(K):
            touch = cnt[i,K] > 0
            if touch != (i in RIM_OK): c += 1
        return c
    gc = graph_cost()
    ac = float(np.abs(area-tg).sum())
    cost = gc*140.0 + ac
    bord = [(y,x) for y in range(ny) for x in range(nx) if inner[y,x]]
    best = (cost, lab.copy(), gc, ac)
    for s in range(steps):
        T = T0*((T1/T0)**(s/steps))
        y,x = bord[rng.randrange(len(bord))]
        a = lab[y,x]
        nbs = []
        for dy,dx in ((-1,0),(1,0),(0,-1),(0,1)):
            yy,xx = y+dy,x+dx
            if 0<=yy<ny and 0<=xx<nx and inner[yy,xx] and lab[yy,xx]!=a: nbs.append(lab[yy,xx])
        if not nbs: continue
        b = nbs[rng.randrange(len(nbs))]
        if b == K: continue
        if not simple_point(lab, y, x, a): continue
        # пересчёт cnt вокруг клетки
        d = []
        for dy,dx in ((-1,0),(1,0),(0,-1),(0,1)):
            yy,xx = y+dy,x+dx
            o = lab[yy,xx] if (0<=yy<ny and 0<=xx<nx) else K
            d.append(o)
        for o in d:
            if o != a: cnt[min(a,o),max(a,o)] -= 1
            if o != b: cnt[min(b,o),max(b,o)] += 1
        area[a] -= cell; area[b] += cell
        lab[y,x] = b
        gc2 = graph_cost(); ac2 = float(np.abs(area-tg).sum())
        c2 = gc2*140.0 + ac2
        if c2 <= cost or rng.random() < math.exp((cost-c2)/max(T,1e-6)):
            cost, gc, ac = c2, gc2, ac2
            if c2 < best[0] and gc2 == 0 or (c2 < best[0]):
                best = (c2, lab.copy(), gc2, ac2)
        else:                                            # откат
            lab[y,x] = a
            for o in d:
                if o != b: cnt[min(b,o),max(b,o)] -= 1
                if o != a: cnt[min(a,o),max(a,o)] += 1
            area[a] += cell; area[b] -= cell
        if verbose and s % 60000 == 0:
            print("   шаг %6d  T=%.2f  нарушений графа %2d  площади ±%.0f" % (s, T, gc, ac))
    return best

def init_balanced(seeds, inner, rounds=140):
    """старт: взвешенная диаграмма, веса подобраны под целевые площади.
    Форма ячеек тут ещё выпуклая и графу не отвечает — это только затравка
    с правильными площадями, граф правит отжиг."""
    X, Y, _, nx, ny = make_grid()
    S = np.array([seeds[n] for n in NAMES], float)
    P = np.stack([X[inner], Y[inner]], axis=1)
    cell = GRID*GRID/100.0
    tg = np.array([REG[n][1] for n in NAMES], float)
    tg = tg/tg.sum()*(P.shape[0]*cell)
    Wt = np.zeros(K)
    for r in range(rounds):
        d = ((P[:,None,0]-S[None,:,0])**2 + (P[:,None,1]-S[None,:,1])**2) - Wt[None,:]
        l = np.argmin(d, axis=1)
        ar = np.bincount(l, minlength=K)*cell
        if np.abs(ar-tg).sum() < 25: break
        Wt += (tg-ar)*2.4
        for i in range(K):                      # Ллойд: зерно к центру своей ячейки
            m = l==i
            if m.any(): S[i] = 0.75*S[i] + 0.25*P[m].mean(axis=0)
    lab = np.full((ny,nx), K, int)
    lab[inner] = l
    return lab, ar, tg

# --------------------------------------------- адресные операции над разбиением
# Одиночная клетка почти никогда не меняет граф: чтобы появилось ребро, коридор
# между областями надо проложить целиком, и выигрыш виден только на последней
# клетке. Поэтому правим не случайно, а адресно.
from collections import deque
def dist_to(lab, inner, b):
    """расстояние по клеткам поля до области b"""
    ny,nx = lab.shape
    d = np.full(lab.shape, 10**9, int)
    q = deque()
    ys,xs = np.where(lab==b)
    for y,x in zip(ys.tolist(), xs.tolist()): d[y,x]=0; q.append((y,x))
    while q:
        y,x = q.popleft()
        for dy,dx in ((-1,0),(1,0),(0,-1),(0,1)):
            yy,xx = y+dy,x+dx
            if not (0<=yy<ny and 0<=xx<nx) or not inner[yy,xx]: continue
            if d[yy,xx] > d[y,x]+1:
                d[yy,xx] = d[y,x]+1; q.append((yy,xx))
    return d

import random as _rnd
rngf = _rnd.Random(11)
def carve(lab, inner, a, b, max_steps=260, strict=False):
    """Наступление фронтом: область a растёт в сторону b по одной клетке.
    Прямой коридор резал бы область, через которую идёт, — поэтому каждая
    клетка берётся только если донор от её потери не распадается."""
    ny,nx = lab.shape
    d = dist_to(lab, inner, b)
    for _ in range(max_steps):
        A = (lab==a)
        front = np.zeros_like(A)
        front[:-1,:] |= A[1:,:]; front[1:,:] |= A[:-1,:]
        front[:,:-1] |= A[:,1:]; front[:,1:] |= A[:,:-1]
        front &= inner & ~A & (lab!=K)
        ys,xs = np.where(front)
        if len(ys)==0: return False
        cands = sorted(zip(d[ys,xs].tolist(), ys.tolist(), xs.tolist()))
        if cands[0][0] == 0: return True                 # дошли, ребро есть
        done = False
        for dd,y,x in cands[:40]:
            donor = lab[y,x]
            if (lab==donor).sum() < 14: continue
            # связность донора здесь НЕ требуется: чтобы дойти до цели, области
            # надо пройти между двумя другими, и жёсткое требование это блокирует.
            # Разрывы чинит reconnect() после того, как все коридоры проложены.
            if not strict and not simple_point(lab, y, x, donor):
                if rngf.random() > 0.35: continue
            elif strict and not simple_point(lab, y, x, donor): continue
            lab[y,x] = a
            done = True; break
        if not done: return False
    return False

def separate(lab, inner, a, b, rng):
    """развести пару a,b: клетки их общей границы отдаются третьей области,
    которой с обеими граничить можно"""
    ny, nx = lab.shape
    req = req_pairs()
    A = (lab==a); B = (lab==b)                      # границу пары ищем сдвигами,
    touch = np.zeros_like(A)                        # а не перебором по растру
    touch[:-1,:] |= A[:-1,:] & B[1:,:]; touch[1:,:] |= A[1:,:] & B[:-1,:]
    touch[:,:-1] |= A[:,:-1] & B[:,1:]; touch[:,1:] |= A[:,1:] & B[:,:-1]
    ys,xs = np.where(touch)
    cellsab = list(zip(ys.tolist(), xs.tolist()))
    if not cellsab: return False
    rng.shuffle(cellsab)
    done = 0
    for (y,x) in cellsab[:max(6,len(cellsab)//2)]:
        cur = lab[y,x]
        cand = []
        for dy,dx in ((-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,1),(-1,1),(1,-1)):
            yy,xx = y+dy,x+dx
            if not (0<=yy<ny and 0<=xx<nx) or not inner[yy,xx]: continue
            c = lab[yy,xx]
            if c in (a,b,K): continue
            ok_a = (min(c,a),max(c,a)) in req; ok_b = (min(c,b),max(c,b)) in req
            if ok_a and ok_b: cand.append(c)
        if not cand: continue
        c = cand[0]
        if not simple_point(lab, y, x, cur): continue
        lab[y,x] = c
        if not connected(lab, cur): lab[y,x] = cur; continue
        done += 1
    return done > 0

def rebalance_fast(lab, inner, tg, rounds=260):
    """быстрый возврат площадей: клетки границы переходят пачками от области
    с излишком к смежной с нехваткой, связность стережёт только simple_point"""
    ny,nx = lab.shape
    cell = GRID*GRID/100.0
    for _ in range(rounds):
        ar = np.bincount(lab[inner].ravel(), minlength=K+1)[:K]*cell
        d = ar-tg
        if np.abs(d).sum() < 60: break
        order = np.argsort(-d)
        moved = False
        for src in order[:6]:
            if d[src] <= 2: break
            for dst in np.argsort(d)[:6]:
                if d[dst] >= -2: break
                A = (lab==src); B = (lab==dst)
                t = np.zeros_like(A)
                t[:-1,:] |= A[:-1,:] & B[1:,:]; t[1:,:] |= A[1:,:] & B[:-1,:]
                t[:,:-1] |= A[:,:-1] & B[:,1:]; t[:,1:] |= A[:,1:] & B[:,:-1]
                ys,xs = np.where(t)
                if len(ys)==0: continue
                k = 0
                for y,x in zip(ys.tolist(), xs.tolist()):
                    if simple_point(lab, y, x, src):
                        lab[y,x] = dst; k += 1; moved = True
                    if k >= 6: break
                if k: break
            if moved: break
        if not moved: break
    return lab

def rebalance(lab, inner, rounds=5000):
    """вернуть площади к целям, не трогая граф: клетка границы переходит
    от области с излишком к смежной с нехваткой"""
    ny,nx = lab.shape
    cell = GRID*GRID/100.0
    tg = np.array([REG[n][1] for n in NAMES], float)
    tg = tg/tg.sum()*(inner.sum()*cell)
    for _ in range(rounds):
        ar = np.bincount(lab[inner].ravel(), minlength=K+1)[:K]*cell
        d = ar - tg
        if np.abs(d).sum() < 40: break
        src = int(np.argmax(d)); dst = int(np.argmin(d))
        moved = False
        A = (lab==src); B = (lab==dst)
        t = np.zeros_like(A)
        t[:-1,:] |= A[:-1,:] & B[1:,:]; t[1:,:] |= A[1:,:] & B[:-1,:]
        t[:,:-1] |= A[:,:-1] & B[:,1:]; t[:,1:] |= A[:,1:] & B[:,:-1]
        ys,xs = np.where(t)
        for y,x in zip(ys.tolist(), xs.tolist()):
            if not simple_point(lab, y, x, src): continue
            lab[y,x] = dst
            if not connected(lab, src): lab[y,x] = src; continue
            moved = True; break
        if not moved:
            d[src] = -1e9                      # эта пара не касается — пробуем другую
    return lab

def graph_state(lab, inner):
    req = req_pairs()
    pr = adj_of(lab, inner)
    got = set((i,j) for i,j in pr if j < K); rim = set(i for i,j in pr if j == K)
    return req-got, got-req, RIM_OK-rim, rim-RIM_OK


def reconnect(lab, inner):
    """после прокладки коридоров области могли распасться: мелкие обрывки
    отдаются соседям, у кого нехватка площади. Связность — императив:
    все регионы должны сообщаться."""
    changed = True; rounds = 0
    while changed and rounds < 40:
        changed = False; rounds += 1
        for i in range(K):
            m = (lab==i)
            if not m.any(): continue
            cc, n = ndimage.label(m, structure=CONN)
            if n <= 1: continue
            sizes = ndimage.sum(m, cc, range(1, n+1))
            keep = int(np.argmax(sizes)) + 1
            for c in range(1, n+1):
                if c == keep: continue
                ys, xs = np.where(cc == c)
                for y, x in zip(ys.tolist(), xs.tolist()):
                    nb = [lab[y+dy,x+dx] for dy,dx in ((-1,0),(1,0),(0,-1),(0,1))
                          if 0<=y+dy<lab.shape[0] and 0<=x+dx<lab.shape[1]]
                    nb = [v for v in nb if v != i and v != K]
                    if nb: lab[y,x] = max(set(nb), key=nb.count); changed = True
    return lab

def push_from_rim(lab, inner, i, rng):
    """область не должна касаться рамки: её приграничные клетки отдаются соседу,
    которому рамку касаться можно"""
    ny,nx = lab.shape
    A = (lab==i); F = (lab==K)
    t = np.zeros_like(A)
    t[:-1,:] |= A[:-1,:] & F[1:,:]; t[1:,:] |= A[1:,:] & F[:-1,:]
    t[:,:-1] |= A[:,:-1] & F[:,1:]; t[:,1:] |= A[:,1:] & F[:,:-1]
    ys,xs = np.where(t)
    if len(ys)==0: return False
    done = 0
    for y,x in zip(ys.tolist(), xs.tolist()):
        cand = []
        for dy,dx in ((-1,0),(1,0),(0,-1),(0,1),(-1,-1),(1,1),(-1,1),(1,-1)):
            yy,xx = y+dy,x+dx
            if not (0<=yy<ny and 0<=xx<nx) or not inner[yy,xx]: continue
            c = lab[yy,xx]
            if c != i and c in RIM_OK: cand.append(c)
        if not cand: continue
        if not simple_point(lab, y, x, i): continue
        lab[y,x] = cand[0]; done += 1
    return done > 0

def pull_to_rim(lab, inner, i):
    return carve(lab, inner, i, K, max_steps=90)

# ------------------------------------------- отжиг по адресным операциям
SAVE_TO = "/sessions/modest-confident-hypatia/w2/lab_live.npy"
def anneal_ops(lab, inner, tg, seconds=600, T0=260.0, T1=6.0, seed=5, log=print):
    """Ход отжига — не клетка, а целая операция: проложить коридор, развести
    пару, вытолкнуть из рамки. Каждая оценивается общей стоимостью
    (нарушения графа + разрывы + площади) и откатывается, если стало хуже."""
    import time
    rng = random.Random(seed)
    cost, nb, cp, ae = cost_of(lab, inner, tg)
    best = (cost, lab.copy(), nb, cp, ae)
    t0 = time.time(); moves = 0; acc = 0
    while time.time()-t0 < seconds:
        T = T0*((T1/T0)**min(1.0, (time.time()-t0)/seconds))
        miss, extra, rmiss, rextra = graph_state(lab, inner)
        acts = ([("carve",i,j) for i,j in miss] + [("sep",i,j) for i,j in extra] +
                [("pull",i,None) for i in rmiss] + [("push",i,None) for i in rextra])
        hot = {}                                   # кто чаще всех в нарушениях —
        for i,j in list(miss)+list(extra):         # того и стоит переносить целиком
            hot[i] = hot.get(i,0)+1; hot[j] = hot.get(j,0)+1
        for r,c in sorted(hot.items(), key=lambda kv:-kv[1])[:3]:
            acts += [("move", r, None)]*max(1, c//2)
        if not acts: break
        kind, i, j = acts[rng.randrange(len(acts))]
        save = lab.copy()
        if   kind == "carve": carve(lab, inner, i, j, max_steps=110)
        elif kind == "sep":   separate(lab, inner, i, j, rng)
        elif kind == "pull":  pull_to_rim(lab, inner, i)
        elif kind == "push":  push_from_rim(lab, inner, i, rng)
        else:                 relocate(lab, inner, i, tg, rng)
        reconnect(lab, inner)
        rebalance_fast(lab, inner, tg, rounds=90)
        c2, nb2, cp2, ae2 = cost_of(lab, inner, tg)
        moves += 1
        if c2 <= cost or rng.random() < math.exp((cost-c2)/max(T,1e-6)):
            cost, nb, cp, ae = c2, nb2, cp2, ae2; acc += 1
            if c2 < best[0]:
                best = (c2, lab.copy(), nb2, cp2, ae2)
                np.save(SAVE_TO, best[1])        # лучшее пишем сразу: прогон могут прервать
        else:
            lab[:] = save
        if moves % 25 == 0:
            log("   ход %4d  T=%5.0f  нарушений %2d  разрывов %d  площади ±%4.0f  (лучшее %d/%d/±%.0f)"
                % (moves, T, nb, cp, ae, best[2], best[3], best[4]))
    log("   ходов %d, принято %d" % (moves, acc))
    return best

def relocate(lab, inner, i, tg, rng):
    """Крупный ход: область стирается и выращивается заново там, где сходятся
    её соседи по реестру. Коридорами такое не чинится — область, попавшая не
    в то соседство целиком, должна переехать."""
    ny,nx = lab.shape
    req = req_pairs()
    nbrs = [j for (a,b) in req for j in ((b,) if a==i else (a,) if b==i else ())]
    if not nbrs: return False
    pts = []
    for j in nbrs:
        ys,xs = np.where(lab==j)
        if len(ys): pts.append((xs.mean(), ys.mean()))
    if not pts: return False
    tx = sum(p[0] for p in pts)/len(pts); ty = sum(p[1] for p in pts)/len(pts)
    want = int(round(tg[i]/(GRID*GRID/100.0)))
    save = lab.copy()
    # стереть: клетки уходят ближайшему соседу
    for _ in range(60):
        m = (lab==i)
        if not m.any(): break
        d = ndimage.binary_dilation(~m & inner, structure=CONN) & m
        ys,xs = np.where(d)
        if len(ys)==0: break
        for y,x in zip(ys.tolist(), xs.tolist()):
            nb=[lab[y+dy,x+dx] for dy,dx in ((-1,0),(1,0),(0,-1),(0,1))
                if 0<=y+dy<ny and 0<=x+dx<nx and inner[y+dy,x+dx]]
            nb=[v for v in nb if v!=i]
            if nb: lab[y,x]=max(set(nb), key=nb.count)
    if (lab==i).any(): lab[:] = save; return False
    # вырастить заново у целевой точки
    sy, sx = int(np.clip(ty,0,ny-1)), int(np.clip(tx,0,nx-1))
    if not inner[sy,sx]:
        ys,xs = np.where(inner)
        k = np.argmin((xs-tx)**2 + (ys-ty)**2); sy,sx = int(ys[k]), int(xs[k])
    lab[sy,sx] = i
    got = 1
    while got < want:
        A = (lab==i)
        fr = np.zeros_like(A)
        fr[:-1,:] |= A[1:,:]; fr[1:,:] |= A[:-1,:]
        fr[:,:-1] |= A[:,1:]; fr[:,1:] |= A[:,:-1]
        fr &= inner & ~A & (lab!=K)
        ys,xs = np.where(fr)
        if len(ys)==0: break
        ar = np.bincount(lab[inner].ravel(), minlength=K+1)[:K]*(GRID*GRID/100.0)
        sur = ar - tg
        order = sorted(range(len(ys)), key=lambda t: -sur[lab[ys[t],xs[t]]])
        took = 0
        for t in order:
            y,x = int(ys[t]), int(xs[t]); dn = lab[y,x]
            if (lab==dn).sum() < 14: continue
            if not simple_point(lab, y, x, dn): continue
            lab[y,x] = i; got += 1; took += 1
            if got >= want or took >= 25: break
        if took == 0: break
    if got < want*0.55: lab[:] = save; return False
    reconnect(lab, inner)
    return True

def force_path(lab, inner, a, b, width=2):
    """Проложить коридор силой: кратчайший путь по полю отдаётся области a,
    без оглядки на связность донора. Разрывы чинит reconnect. Нужно там, где
    фронт упирается: длинные рукава вроде Средиземного так и рисуются."""
    ny,nx = lab.shape
    from collections import deque as dq
    d = np.full(lab.shape, -1, int); prev = {}
    q = dq()
    ys,xs = np.where(lab==a)
    for y,x in zip(ys.tolist(), xs.tolist()): d[y,x]=0; q.append((y,x))
    tgt=None
    while q:
        y,x = q.popleft()
        if lab[y,x]==b and d[y,x]>0: tgt=(y,x); break
        for dy,dx in ((-1,0),(1,0),(0,-1),(0,1)):
            yy,xx=y+dy,x+dx
            if not (0<=yy<ny and 0<=xx<nx) or not inner[yy,xx] or d[yy,xx]>=0: continue
            d[yy,xx]=d[y,x]+1; prev[(yy,xx)]=(y,x); q.append((yy,xx))
    if tgt is None: return False
    path=[]; cur=tgt
    while cur in prev:
        cur=prev[cur]
        if lab[cur]!=a: path.append(cur)
    if not path: return False
    mask = np.zeros(lab.shape, bool)
    for y,x in path: mask[y,x]=True
    for _ in range(width-1): mask = ndimage.binary_dilation(mask, structure=CONN)
    mask &= inner & (lab!=b)
    lab[mask] = a
    return True

# ------------------------------- расстановка по эскизу Alek (22.09.2026)
# «В центре Антарктида, по краю рамкой Северный Ледовитый. Слева две Америки,
# справа Африка, Евразия и Австралия. Между ними расчертить океаны.»
# Порядок областей по кругу берём из ТЗ §4.4 (он же подтверждён укладкой Тутта)
# и поворачиваем так, чтобы дуга Америк смотрела влево. Радиус — из слоя графа.
TZ_AZ = {"MR-OC-NPAC":0,"MR-L5-AUS":22,"MR-L5-NZL":49,"MR-L5-NAMW":68,"MR-L5-CAM":74,
         "MR-OC-SPAC":85,"MR-L5-NAME":111,"MR-L5-SAMW":118,"MR-L5-SAME":135,
         "MR-OC-NATL":180,"MR-OC-SATL":202,"MR-R5-AFRW":225,"MR-R5-EUR":232,
         "MR-R5-SCA":244,"MR-R5-AFRE":261,"MR-R5-ARB":289,"MR-R5-ASIN":309,
         "MR-R5-ASIS":327,"MR-OC-IND":336}
def sketch_seeds(rot=80.0):
    lay = None
    truth = [tuple(sorted(e)) for e in json.load(
        open(os.path.join(MAPD,"derived","MC-5P.json"), encoding="utf-8"))["edge_list"]]
    nb = {r:set() for r in REG}
    for a,b in truth: nb[a].add(b); nb[b].add(a)
    d = {ARC:0}; q=[ARC]
    while q:
        c=q.pop(0)
        for m in nb[c]:
            if m not in d: d[m]=d[c]+1; q.append(m)
    dmax = max(d.values())
    hw, hh = W/2-FR_END-6, H/2-FR_SIDE-6
    out = {}
    for r, az0 in TZ_AZ.items():
        az = math.radians(az0 + rot)
        cs, sn = math.cos(az), math.sin(az)
        R = min(hw/abs(cs) if abs(cs)>1e-6 else 1e9, hh/abs(sn) if abs(sn)>1e-6 else 1e9)
        frac = (dmax - d[r])/float(dmax)              # 1 у рамки, 0 в центре
        rr = R*(0.34 + 0.62*frac)
        out[r] = (CX + rr*cs, CY + rr*sn)
    out["MR-SH-ANT"] = (CX, CY)
    return out
