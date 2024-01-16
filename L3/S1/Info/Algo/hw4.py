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

            if v in M:
                continue
            dv = du + w
            if y not in d or d[y] > dy : 
                heappush(suivants, (dy, y))
                p[y] = u
            elif d[y] == dy : 
                p[y].append(u)
                heappush(suivants, (dy, y))
    paths = [t]
    x = t
    while x != s: 
        x = tuple(p[x])
        paths.insert(0, x)
    return paths

