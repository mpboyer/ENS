from heapq import *

def dijkstra(s, t, g):
    M = set()
    d = {s: 0}
    p = {}  
    suivants = [(0, s)]
    while suivants : 
        du, u = heappop(suivants)
        if u in M : 
            continue

        M.add(u)
        for v in range(len(g)):
            w = g[u][v]
            if w == 0:
                continue

            if v in M:
                continue
            dv = du + w
            if v not in d or d[v] > dv : 
                heappush(suivants, (dv, v))
                p[v] = [u]
                d[v] = dv
            elif d[v] == dv : 
                p[v].append(u)
                heappush(suivants, (dv, v))

    paths = [set([t])]
    while True:
        rpo = set()
        for x in paths[0]:
            rpo = rpo.union(set(p[x]))
        paths.insert(0, rpo)
        if s in paths[0]:
            break
    return paths

def short_edge(g, s, t, u, v):
    p = dijkstra(s, t, g)
    if not p :
        return True
    for i in range(len(p)):
        if u in p[i] :
            if v in p[i+1]:
                return True 
    return False
