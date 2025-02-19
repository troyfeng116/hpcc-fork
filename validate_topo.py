from typing import Dict, Set

TOPO = "ky_dl"
TOPO_FILE_NAME = "simulation/mix/{topo}.txt".format(topo=TOPO)


def floyd_warshall(g):
    # type: (Dict[int, Set[int]]) -> Dict[int, Dict[int, int]]
    dist = {}
    nodes = g.keys()
    for u in nodes:
        if u not in dist:
            dist[u] = {}
        for v in nodes:
            dist[u][v] = 0 if u == v else 1 if v in g[u] else float('inf')
    for k in nodes:
        for u in nodes:
            for v in nodes:
                dist[u][v] = min(dist[u][v], dist[u][k] + dist[k][v])
    return dist

def analyze_diameter(g):
    # type: (Dict[int, Set[int]]) -> None
    dist = floyd_warshall(g)
    nodes = g.keys()
    max_u, max_v, max_dist = -1, -1, float('-inf')
    for u in nodes:
        for v in nodes:
            if dist[u][v] > max_dist:
                max_u, max_v, max_dist = u, v, dist[u][v]
    print("max distance {dist} for {u}->{v}".format(dist=max_dist, u=max_u, v=max_v))

def check_connected_dfs(u, g, visited):
    # type: (int, Dict[int, Set[int]], Set[int]) -> bool
    visited.add(u)
    for v in g[u]:
        if v not in visited:
            check_connected_dfs(v, g, visited)
    return True

def check_connected(g):
    # type: (Dict[int, Set[int]]) -> bool
    nodes = set(g.keys())
    n = len(nodes)
    visited = set()
    start_node = g.keys()[0]
    check_connected_dfs(start_node, g, visited)
    if visited != nodes:
        print("g is not connected!")
        print("dfs visited {v}; n={n}".format(v=len(visited), n=n))
    else:
        print("g is connected!")
        print("dfs visited all {n} nodes".format(n=n))
    return visited == nodes

def analyze_degrees(g):
    max_deg_node, max_deg = -1, -1
    deg = {}
    for u in g:
        for v in g[u]:
            for node in [u,v]:
                if node not in deg:
                    deg[node] = 0
                deg[node] += 1

            node = u if deg[u] > deg[v] else v
            if deg[node] > max_deg:
                max_deg_node, max_deg = node, deg[node]

    print("max deg = {max_deg} (node {node})".format(
        max_deg=max_deg, node=max_deg_node))

if __name__ == "__main__":
    g = {}
    with open(TOPO_FILE_NAME, 'r') as f:
        lines = f.readlines()
        for line in lines[2:]:
            # 0 320 100Gbps 1000ns 0.000000
            toks = line.split(' ')
            src, dest = int(toks[0]), int(toks[1])
            if src not in g:
                g[src] = set()
            g[src].add(dest)
            if dest not in g:
                g[dest] = set()
            g[dest].add(src)

    check_connected(g)
    analyze_degrees(g) 
    analyze_diameter(g)   
    