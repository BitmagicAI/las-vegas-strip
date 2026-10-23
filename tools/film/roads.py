#!/usr/bin/env python3
"""Routes for film drives over the game's road network (build/geographic-strip/road-network.json, OSM ways; X east, north -Z).

route(waypoints) finds the shortest drivable path through the given world points (one-way streets respected, small roads a
little dearer), smooths it (corner cutting that keeps to the carriageway's centre line), resamples it every `step` m and gives
each point a speed: the road's limit (main 22 m/s, links and unclassified 13, service 9) and a curve limit
v = sqrt(a_lat * R) with a gentle lateral acceleration, eased so the jeep brakes before a bend and accelerates out of it.
Used by make-takes.py; `python3 tools/film/roads.py` prints a test route.
"""
import heapq, json, math, os

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DRIVABLE = {'primary': 22, 'primary_link': 13, 'secondary': 16, 'secondary_link': 12, 'tertiary': 14, 'tertiary_link': 11,
            'unclassified': 13, 'residential': 10, 'service': 9}
COST = {'primary': 1.0, 'primary_link': 1.1, 'secondary': 1.05, 'secondary_link': 1.15, 'tertiary': 1.1, 'tertiary_link': 1.2,
        'unclassified': 1.15, 'residential': 1.4, 'service': 1.6}

_net = None
def network():
    global _net
    if _net: return _net
    roads = json.load(open(os.path.join(ROOT, 'build/geographic-strip/road-network.json')))['roads']
    pos, edges = {}, {}
    for r in roads:
        hw = r.get('highway')
        if hw not in DRIVABLE or r.get('access') in ('private', 'no'): continue
        nodes, pts = r['nodes'], r['points']
        if len(nodes) != len(pts): continue
        oneway = r.get('oneway') in ('yes', 'true', '1')
        for i, (n, p) in enumerate(zip(nodes, pts)): pos[n] = (p[0], p[2])
        for a, b in zip(nodes, nodes[1:]):
            L = math.dist(pos[a], pos[b])
            edges.setdefault(a, []).append((b, L * COST[hw], hw, r.get('name') or ''))
            if not oneway: edges.setdefault(b, []).append((a, L * COST[hw], hw, r.get('name') or ''))
    _net = (pos, edges)
    return _net

def nearest(p, hw_ok=None, heading=None):
    """The network node nearest p; with `heading` (degrees, 0 = north/-Z, 90 = east/+X) only nodes with an outgoing edge
    within 50 degrees of that direction (so a waypoint lands on the right carriageway)."""
    pos, edges = network()
    best = None
    hx, hz = (math.sin(math.radians(heading)), -math.cos(math.radians(heading))) if heading is not None else (0, 0)
    for n, q in pos.items():
        if n not in edges: continue
        if hw_ok and not any(e[2] in hw_ok for e in edges[n]): continue
        if heading is not None:
            ok = False
            for m, *_ in edges[n]:
                dx, dz = pos[m][0] - q[0], pos[m][1] - q[1]; l = math.hypot(dx, dz) or 1
                if (dx * hx + dz * hz) / l > math.cos(math.radians(50)): ok = True; break
            if not ok: continue
        d = math.dist(q, p)
        if best is None or d < best[0]: best = (d, n)
    return best[1]

def shortest(a, b):
    pos, edges = network()
    dist, prev, heap = {a: 0}, {}, [(0, a)]
    while heap:
        d, n = heapq.heappop(heap)
        if n == b: break
        if d > dist.get(n, 1e18): continue
        for m, c, hw, name in edges.get(n, []):
            nd = d + c
            if nd < dist.get(m, 1e18): dist[m] = nd; prev[m] = (n, hw, name); heapq.heappush(heap, (nd, m))
    if b not in prev and a != b: raise SystemExit(f'no route {a} -> {b}')
    path, n = [(b, None, None)], b
    while n != a: n, hw, name = prev[n]; path.append((n, hw, name))
    path.reverse()
    # each node carries the road type of the edge that leaves it
    out = []
    for i, (n, _, _) in enumerate(path):
        hw = path[i + 1][1] if i + 1 < len(path) else path[i][1]
        name = path[i + 1][2] if i + 1 < len(path) else path[i][2]
        out.append((pos[n], hw or 'primary', name or ''))
    return out

def route(waypoints, step=3.0, lat=2.6, start_speed=0.0, end_speed=0.0, max_speed=None, trim=0.0):
    """waypoints: world (x, z[, heading deg]) points the route must pass near (snapped to the network, on a road heading
    that way when given). Returns ([[x, z, speed], ...], road names per point)."""
    nodes = [nearest((p[0], p[1]), heading=p[2] if len(p) > 2 else None) for p in waypoints]
    seq = []
    for a, b in zip(nodes, nodes[1:]):
        part = shortest(a, b)
        seq += part if not seq else part[1:]
    pts = [p for p, _, _ in seq]; lim = [DRIVABLE[hw] for _, hw, _ in seq]
    names = [name for _, _, name in seq]
    # drop near-duplicates, then Chaikin corner cutting (3 passes) with the limits carried along
    P, Lm = [pts[0]], [lim[0]]
    for p, l in zip(pts[1:], lim[1:]):
        if math.dist(p, P[-1]) > 0.5: P.append(p); Lm.append(l)
    for _ in range(3):
        Q, Lq = [P[0]], [Lm[0]]
        for (a, la), (b, lb) in zip(zip(P, Lm), zip(P[1:], Lm[1:])):
            Q.append((a[0] * .75 + b[0] * .25, a[1] * .75 + b[1] * .25)); Lq.append(la)
            Q.append((a[0] * .25 + b[0] * .75, a[1] * .25 + b[1] * .75)); Lq.append(min(la, lb))
        Q.append(P[-1]); Lq.append(Lm[-1]); P, Lm = Q, Lq
    # resample every `step` m
    R, RL, acc = [P[0]], [Lm[0]], 0.0
    for (a, la), b in zip(zip(P, Lm), P[1:]):
        seg = math.dist(a, b)
        while acc + seg >= step:
            t = (step - acc) / seg; a = (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t); seg = math.dist(a, b); acc = 0
            R.append(a); RL.append(la)
        acc += seg
    if trim:
        k = int(trim / step); R, RL = R[k:len(R) - k], RL[k:len(RL) - k]
    # curve speed from the turning radius over +-3 samples
    n = len(R); v = []
    for i in range(n):
        a, b, c = R[max(0, i - 3)], R[i], R[min(n - 1, i + 3)]
        A, B, C = math.dist(b, c), math.dist(a, c), math.dist(a, b)
        area = abs((b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])) / 2
        radius = (A * B * C) / (4 * area) if area > 1e-6 else 1e9
        s = min(RL[i], math.sqrt(lat * radius))
        if max_speed: s = min(s, max_speed)
        v.append(s)
    # comfortable braking (1.6 m/s^2) and acceleration (2.2 m/s^2) envelopes
    v[0] = min(v[0], max(start_speed, 2.0)); v[-1] = min(v[-1], end_speed if end_speed else v[-1])
    for i in range(n - 2, -1, -1): v[i] = min(v[i], math.sqrt(v[i + 1] ** 2 + 2 * 1.6 * step))
    for i in range(1, n): v[i] = min(v[i], math.sqrt(v[i - 1] ** 2 + 2 * 2.2 * step))
    return [[round(p[0], 2), round(p[1], 2), round(max(2.0, s), 2)] for p, s in zip(R, v)], names

if __name__ == '__main__':
    pts, names = route([(-200, 330), (15, 300), (17, -150)])
    seen = []
    for n in names:
        if n and (not seen or seen[-1] != n): seen.append(n)
    print(len(pts), 'points', round(sum(math.dist(a[:2], b[:2]) for a, b in zip(pts, pts[1:]))), 'm via', seen)
    print('speeds', [p[2] for p in pts[::15]])
