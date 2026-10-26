#!/usr/bin/env python3
"""Writes tools/film/takes/*.json (film takes for tools/film/record.mjs) from the level data.
Drives follow the Strip route (build/geographic-strip/road-network.json `stripRoute`, X east, north -Z), offset into the
right-hand lane. Run: python3 tools/film/make-takes.py"""
import json, math, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, 'tools/film/takes')
route = json.load(open(os.path.join(ROOT, 'build/geographic-strip/road-network.json')))['stripRoute']

def strip_path(z_from, z_to, lane=4.5, step=8.0):
    """Points along the Strip from z_from to z_to (either direction), `lane` metres right of the centreline, resampled every `step` m."""
    pts = [(p[0], p[2]) for p in route]
    north = z_to < z_from
    seq = sorted([p for p in pts if min(z_from, z_to) - 40 <= p[1] <= max(z_from, z_to) + 40], key=lambda p: -p[1] if north else p[1])
    # resample
    out = [seq[0]]
    for a, b in zip(seq, seq[1:]):
        d = math.dist(a, b); n = max(1, int(d // step))
        for k in range(1, n + 1): out.append((a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n))
    # clip to the z range and offset right of travel
    res = []
    for i, p in enumerate(out):
        q = out[min(i + 1, len(out) - 1)] if i < len(out) - 1 else p; o = out[max(i - 1, 0)]
        dx, dz = q[0] - o[0], q[1] - o[1]; l = math.hypot(dx, dz) or 1
        rx, rz = -dz / l, dx / l  # right of travel (X east, north -Z)
        x, z = p[0] + rx * lane, p[1] + rz * lane
        if (z_to < z_from and z_to <= z <= z_from) or (z_to > z_from and z_from <= z <= z_to): res.append([round(x, 2), round(z, 2)])
    return res

def heading(path):
    (x0, z0), (x1, z1) = path[0], path[1]
    return round(math.atan2(x1 - x0, z1 - z0), 4)  # 0 = +Z

SUBFRAMES = 4   # motion blur: every take records 4 frames per 1/60 s (tools/film/blend-subframes.py blends 3 of them)
def write(name, take):
    take['name'] = name
    take.setdefault('subframes', SUBFRAMES)
    with open(os.path.join(OUT, name + '.json'), 'w') as f: json.dump(take, f, indent=1)
    print('wrote', name, len(take['steps']), 'steps')

def ahead(p, d, k):
    return [round(p[0] + d[0] * k, 2), round(p[1] + d[1] * k, 2)]

def walk_take(name, pos, dirxz, back=4, forward=18, sway=(0.32, 9), pitch=0.0, run=False, warm=4, start=None, extra=None, seconds=None):
    """A first-person walk from `back` m behind the scouted point to `forward` m past it, along its view direction."""
    l = math.hypot(*dirxz); d = (dirxz[0] / l, dirxz[1] / l)
    s0 = ahead((pos[0], pos[2]), d, -back)
    path = [ahead((pos[0], pos[2]), d, k) for k in [x * 2 for x in range(-back // 2 + 1, forward // 2 + 1)]]
    take = {'start': start or {'at': [s0[0], pos[1] + 0.1, s0[1]], 'dir': list(d), 'pitch': pitch, 'view': 'first', 'warm': warm},
            'steps': [{'walk': {'path': path, 'run': run, 'sway': list(sway), 'pitch': pitch}}] + (extra or [])}
    if seconds: take['seconds'] = seconds
    take['maxSeconds'] = 50
    write(name, take)

# ── drives (jeep-relative camera keys: x right, y up, z forward)
north = strip_path(560, -760)
write('drive-north', {'start': {'seat': {'at': [north[0][0], 0.6, north[0][1]], 'heading': heading(north)}, 'warm': 5},
    'steps': [{'drive': {'path': north, 'speed': 17}}],
    'camera': [
        {'from': 7, 'to': 15, 'anchor': 'jeep', 'keys': [{'t': 0, 'pos': [3.8, 1.0, 9.0], 'look': [0, 1.1, 0]}, {'t': 8, 'pos': [2.6, 1.3, 6.2], 'look': [0, 1.2, -1]}]},
        {'from': 31, 'to': 39, 'anchor': 'jeep', 'keys': [{'t': 0, 'pos': [-5.5, 1.4, 2.0], 'look': [0, 1.0, 1.0]}, {'t': 8, 'pos': [-5.0, 1.6, -1.0], 'look': [0, 1.0, 2.0]}]},
        {'from': 56, 'to': 64, 'anchor': 'jeep', 'keys': [{'t': 0, 'pos': [0, 9, -12], 'look': [0, 1.5, 12]}, {'t': 8, 'pos': [0, 22, -18], 'look': [0, 2, 40]}]},
    ]})
south = strip_path(600, 1480)
write('drive-south', {'start': {'seat': {'at': [south[0][0], 0.6, south[0][1]], 'heading': heading(south)}, 'warm': 5},
    'steps': [{'drive': {'path': south, 'speed': 17}}],
    'camera': [
        {'from': 6, 'to': 14, 'anchor': 'jeep', 'keys': [{'t': 0, 'pos': [5.0, 0.8, 11.0], 'look': [0, 1.0, 0]}, {'t': 8, 'pos': [-1.5, 1.2, 7.5], 'look': [0, 1.2, -1]}]},
        {'from': 28, 'to': 36, 'anchor': 'jeep', 'keys': [{'t': 0, 'pos': [6.0, 2.2, -3.0], 'look': [0, 1.0, 3.0]}, {'t': 8, 'pos': [6.0, 2.6, 2.0], 'look': [0, 1.0, 5.0]}]},
    ]})

# ── casinos and lobbies (scouted with build/film/scout/scout.js)
walk_take('casino-caesars', [-192.44, 0.16, -80.57], (-1, 0), back=8, forward=20, pitch=0.12)
walk_take('casino-flamingo', [47.28, 0.16, -47.0], (1, 0), back=6, forward=20, pitch=0.16)
walk_take('casino-planet-hollywood', [92.56, 0.09, 655.15], (1, 0), back=4, forward=18, pitch=0.04)
walk_take('casino-horseshoe', [210.61, 0.09, 287.35], (-1, 0), back=4, forward=18, pitch=0.08)
walk_take('lobby-venetian', [202.06, 0.0, -688.59], (0.987, 0.122), back=6, forward=34, pitch=0.18, sway=(0.25, 12))
walk_take('lobby-palazzo', [311.85, 0.29, -933.5], (0.823, 0.521), back=2, forward=10, pitch=0.05, sway=(0.2, 10))
walk_take('lobby-bellagio', [-230.0, 0.18, 445.0], (-1, 0), back=4, forward=20, pitch=0.28, sway=(0.25, 12))
walk_take('bellagio-conservatory', [-317.5, 0.18, 475.0], (0, -1), back=4, forward=16, pitch=0.02)
walk_take('crystals-atrium', [-86.4, 0.09, 906.19], (-0.721, 0.693), back=4, forward=16, pitch=0.1)
walk_take('caesars-approach', [-90.95, 0.0, -80.57], (-1, 0), back=14, forward=10, pitch=0.12, sway=(0.2, 12))

# ── hotel rooms: corridor → kick → room → window
def kick_take(name, hotel, near=None, run=False, window=5.6, look=None):
    look = look or [{'look': {'pitch': -0.06, 'seconds': 1.4}}, {'wait': 0.8}]
    steps = [{'approachDoor': {}}, {'wait': 0.35}, {'kick': True}, {'wait': 1.0}, {'enterRoom': {'distance': window}}] + look
    write(name, {'start': {'hotel': hotel, 'door': ({'near': near} if near else {}), 'view': 'first', 'warm': 3}, 'steps': steps, 'maxSeconds': 45})
kick_take('kick-bellagio', ['bellagio-north', 20, None, 'corridor'],
          look=[{'look': {'pitch': -0.08, 'seconds': 1.2}}, {'wait': 1.5}, {'mark': 'window'}, {'wait': 3.5}])
kick_take('kick-caesars', ['caesars-palace', 20, None, 'corridor'])
kick_take('kick-cosmo', ['cosmo-boulevard', 40, None, 'corridor'],
          look=[{'look': {'pitch': -0.12, 'seconds': 1.4}}, {'wait': 1.0}, {'mark': 'window'}, {'wait': 3.0}])

# ── Eiffel deck (140 m), the coaster, the High Roller
walk_take('eiffel-deck', [71.1, 140.03, 403.9], (-0.981, 0.177), back=0, forward=10, pitch=-0.12, sway=(0.45, 14),
          start={'landmark': ['parisBlock', 'observation'], 'view': 'first', 'warm': 5})
station = route_exit = [-98.68, 12.65, 1482.07]
write('coaster-ride', {'start': {'at': station, 'dir': [-0.603, -0.798], 'pitch': -0.05, 'view': 'first', 'warm': 4},
    'maxSeconds': 260, 'steps': [{'wait': 1.0}, {'key': 'KeyR'}, {'until': {'what': 'coaster-start', 'max': 5}}, {'mark': 'board'}, {'until': {'what': 'coaster-done', 'max': 260}}, {'mark': 'end'}]})

# ── aerials (camera track; the player stands under the shot so the area streams)
write('aerial-open', {'start': {'at': [21.0, 0.6, 640.0], 'dir': [0, -1], 'view': 'first', 'warm': 6}, 'seconds': 16,
    'steps': [{'wait': 16}],
    'camera': [{'from': 0, 'to': 16, 'keys': [{'t': 0, 'pos': [60, 150, 900], 'look': [30, 40, 520]}, {'t': 16, 'pos': [40, 95, 700], 'look': [40, 30, 360]}]}]})
write('aerial-close', {'start': {'at': [21.0, 0.6, 470.0], 'dir': [0, -1], 'view': 'first', 'warm': 6}, 'seconds': 16,
    'steps': [{'wait': 16}],
    'camera': [{'from': 0, 'to': 16, 'keys': [{'t': 0, 'pos': [-20, 25, 520], 'look': [60, 60, 404]}, {'t': 16, 'pos': [-34, 150, 548], 'look': [60, 30, 380]}]}]})

# ── drone drives: one continuous flight per drive; keys in the jeep's frame (x right, y up, z forward), smoothed and
#    sprung by the film director (anchor 'drone'), pulled in front of buildings
def K(t, pos, look): return {'t': t, 'pos': pos, 'look': look}
north_d = strip_path(560, -520)
write('drone-north', {'start': {'seat': {'at': [north_d[0][0], 0.6, north_d[0][1]], 'heading': heading(north_d)}, 'warm': 6}, 'maxSeconds': 120,
    'steps': [{'drive': {'path': north_d, 'speed': 15}}],
    'camera': [{'from': 0, 'to': 115, 'anchor': 'drone', 'lag': 0.6, 'keys': [
        K(0,  [-3.0, 1.3, 9.0],   [0, 1.0, 0]),     # low, front-left: the jeep pulls away from the sanctuary toward us
        K(6,  [-1.0, 9.0, 2.0],   [0, 0.5, 14]),    # rise straight over it
        K(13, [0, 24, -18],       [0, 2, 34]),      # high trailing reveal down the Strip, Paris and the Eiffel ahead right
        K(21, [15, 11, -3],       [0, 1, 7]),       # swing out to the Paris side
        K(29, [7.5, 2.4, 3],      [0, 1, 5]),       # down to a low side track
        K(37, [5, 2.6, 15],       [0, 1.1, 0]),     # overtake: the jeep drives at us past Caesars
        K(45, [0, 19, 27],        [0, 0, 0]),       # climb ahead and look back down at it
        K(54, [-17, 13, 5],       [0, 1, 9]),       # arc over to the left, high
        K(62, [-6, 3, -8],        [0, 1.4, 10]),    # drop into a low chase, the Flamingo ahead
        K(70, [8, 6, -5],         [0, 1.5, 14]),    # drift right, the LINQ and the High Roller
        K(80, [0, 30, -6],        [0, 0, 12]),      # straight up, looking down the Strip
        K(92, [0, 14, 18],        [0, 1, 0]),       # come round in front
        K(104,[-4, 2.2, 10],      [0, 1, 0]),       # settle low in front for the stop
        K(115,[-4, 2.2, 10],      [0, 1, 0])]}]})
south_d = strip_path(610, 1470)
write('drone-south', {'start': {'seat': {'at': [south_d[0][0], 0.6, south_d[0][1]], 'heading': heading(south_d)}, 'warm': 6}, 'maxSeconds': 100,
    'steps': [{'drive': {'path': south_d, 'speed': 15}}],
    'camera': [{'from': 0, 'to': 95, 'anchor': 'drone', 'lag': 0.6, 'keys': [
        K(0,  [0, 34, -20],       [0, 2, 30]),      # start high behind: CityCenter ahead
        K(9,  [12, 12, 6],        [0, 1, 8]),       # dive to the right side
        K(17, [6, 2.4, 12],       [0, 1.1, 0]),     # in front, low, the jeep coming at us
        K(26, [-10, 5, 2],        [0, 1, 6]),       # cross to the left
        K(35, [-4, 2.2, -7],      [0, 1.4, 12]),    # low chase
        K(44, [0, 22, -10],       [0, 0, 26]),      # rise: New York-New York and the coaster ahead
        K(54, [14, 16, 10],       [0, 2, 20]),      # wide right, the coaster's loops
        K(64, [5, 3, 16],         [0, 1, 0]),       # front again
        K(76, [-6, 9, -4],        [0, 1, 12]),
        K(95, [-6, 9, -4],        [0, 1, 12])]}]})

# ── the Bellagio lake: a low glide toward the hotel and its reflection (realistic water)
write('lake-glide', {'start': {'at': [-14, 0.5, 360], 'dir': [-1, 0], 'view': 'first', 'warm': 6}, 'seconds': 14, 'maxSeconds': 16,
    'steps': [{'wait': 14}],
    'camera': [{'from': 0, 'to': 14, 'keys': [
        {'t': 0, 'pos': [-22, 3.2, 300], 'look': [-200, 24, 330]},
        {'t': 7, 'pos': [-70, 2.4, 318], 'look': [-230, 30, 340]},
        {'t': 14, 'pos': [-112, 2.0, 336], 'look': [-250, 40, 350]}]}]})


# ══ version 3 (2026-10-08, the owner's feedback on v2): faster camera work, spline flights around the landmarks, drives that
#    curve out of the side roads onto the Boulevard, quicker walks. Flights are checked with tools/film/clearance.py.

def _cr(p0, p1, p2, p3, u):
    """Centripetal Catmull-Rom between p1 and p2 (no overshoot or cusps on uneven control spacing)."""
    def tj(ti, a, b): return ti + max(1e-6, math.dist(a, b)) ** 0.5
    t0 = 0; t1 = tj(t0, p0, p1); t2 = tj(t1, p1, p2); t3 = tj(t2, p2, p3); t = t1 + (t2 - t1) * u
    def L(a, b, ta, tb): return [(tb - t) / (tb - ta) * x + (t - ta) / (tb - ta) * y for x, y in zip(a, b)]
    A1, A2, A3 = L(p0, p1, t0, t1), L(p1, p2, t1, t2), L(p2, p3, t2, t3)
    B1, B2 = L(A1, A2, t0, t2), L(A2, A3, t1, t3)
    return L(B1, B2, t1, t2)

def add_bank(keys, gain=0.35, max_deg=15.0, ease=0.3):
    """Bank into turns (the owner asked for a slight tilt in turns): roll from the path's own curvature and speed,
    like a drone or a plane (a = v * turn rate; bank = atan(gain * a / g)), capped, eased over `ease` s. Right turns roll
    right (negative, see Film's CameraKey.roll)."""
    n = len(keys)
    if n < 3: return keys
    hd, sp = [], []
    for i in range(n):
        a, b = keys[max(0, i - 1)], keys[min(n - 1, i + 1)]
        dx, dz = b['pos'][0] - a['pos'][0], b['pos'][2] - a['pos'][2]; dtt = max(1e-6, b['t'] - a['t'])
        hd.append(math.atan2(dx, -dz)); sp.append(math.hypot(dx, dz) / dtt)
    for i in range(1, n):   # unwrap
        while hd[i] - hd[i - 1] > math.pi: hd[i] -= 2 * math.pi
        while hd[i] - hd[i - 1] < -math.pi: hd[i] += 2 * math.pi
    raw = []
    for i in range(n):
        a, b = max(0, i - 1), min(n - 1, i + 1); rate = (hd[b] - hd[a]) / max(1e-6, keys[b]['t'] - keys[a]['t'])
        bank = -math.atan(gain * sp[i] * rate / 9.81) if sp[i] > 1 else 0.0
        raw.append(max(-math.radians(max_deg), min(math.radians(max_deg), bank)))
    dtk = (keys[-1]['t'] - keys[0]['t']) / (n - 1); k = max(1, int(ease / dtk))
    for i in range(n):
        acc = wsum = 0.0
        for j in range(max(0, i - 3 * k), min(n, i + 3 * k + 1)):
            w = math.exp(-0.5 * ((j - i) / k) ** 2); acc += w * raw[j]; wsum += w
        keys[i]['roll'] = round(acc / wsum, 4)
    return keys

def flight(name, points, speed, at, ramp=1.2, lookahead=30.0, dt=0.2, fov=None, warm=6, extra=None):
    """A world-anchored camera flight at a constant `speed` (m/s) through `points` [((x, y, z), look)], where look is
    None (look along the path, `lookahead` m ahead) or a world target; easing in and out over `ramp` s. The player stands
    at `at` (the area streams around the player). Writes keys every `dt` s."""
    P = [list(map(float, p)) for p, _ in points]; looks = [l for _, l in points]
    ext = [[2 * a - b for a, b in zip(P[0], P[1])]] + P + [[2 * a - b for a, b in zip(P[-1], P[-2])]]
    dense, owner = [], []
    for i in range(len(P) - 1):
        for k in range(40):
            dense.append(_cr(ext[i], ext[i + 1], ext[i + 2], ext[i + 3], k / 40)); owner.append(i + k / 40)
    dense.append(P[-1]); owner.append(len(P) - 1)
    S = [0.0]
    for a, b in zip(dense, dense[1:]): S.append(S[-1] + math.dist(a, b))
    total = S[-1]
    def at_s(s):
        s = min(max(s, 0), total); j = max(0, min(len(S) - 2, next((k for k in range(1, len(S)) if S[k] >= s), len(S) - 1) - 1))
        f = (s - S[j]) / max(1e-9, S[j + 1] - S[j])
        return [a + (b - a) * f for a, b in zip(dense[j], dense[j + 1])], owner[j] + (owner[j + 1] - owner[j]) * f
    # trapezoid speed profile with smooth ramps: duration so the cruise runs at `speed`
    T = total / speed + ramp
    n = int(T / dt) + 1; vel = []
    for i in range(n + 1):
        t = i * dt; e = min(1, t / ramp, (T - t) / ramp) if ramp > 0 else 1; e = max(0, e); vel.append(e * e * (3 - 2 * e))
    acc = [0.0]
    for v0, v1 in zip(vel, vel[1:]): acc.append(acc[-1] + (v0 + v1) / 2 * dt)
    keys = []
    for i in range(n + 1):
        s = acc[i] / acc[-1] * total; pos, u = at_s(s)
        ahead, _ = at_s(s + lookahead)
        if s + lookahead > total:   # past the end: continue straight along the last direction
            a, _ = at_s(total - 1); ahead = [p + (p - q) * (s + lookahead - total) for p, q in zip(P[-1], a)]
        i0 = min(int(u), len(P) - 2); f = u - i0; f = f * f * (3 - 2 * f)
        l0 = looks[i0] or ahead; l1 = looks[i0 + 1] or ahead
        look = [a + (b - a) * f for a, b in zip(l0, l1)]
        k = {'t': round(i * dt, 3), 'pos': [round(c, 2) for c in pos], 'look': [round(c, 2) for c in look]}
        if fov: k['fov'] = fov
        keys.append(k)
    seconds = round(n * dt, 2)
    add_bank(keys)
    write(name, {'start': {'at': list(at), 'dir': [0, -1], 'view': 'first', 'warm': warm}, 'seconds': seconds, 'maxSeconds': seconds + 4,
                 'steps': [{'wait': seconds}], 'camera': [{'from': 0, 'to': seconds, 'keys': keys}]})
    return total, seconds

# ── Paris: in from the casino side over the porte-cochere, through the Arc de Triomphe's vault at 9 m, past the balloon sign,
#    then up and around the Eiffel Tower (centre 74.5, 400.5; 158 m). Geometry: tools/film/glb-bounds.py on parisBlock.
EIFFEL = (74.5, 400.5)
print('fly-paris', flight('fly-paris', [
    ((240, 20, 492), None), ((196, 18, 492), None), ((162, 12.5, 491), None), ((127, 9, 490.7), None), ((95, 9.5, 490.7), None),
    ((55, 13, 487), None), ((20, 24, 470), None), ((5, 48, 438), (EIFFEL[0], 105, EIFFEL[1])), ((10, 72, 398), (EIFFEL[0], 112, EIFFEL[1])),
    ((36, 94, 352), (EIFFEL[0], 120, EIFFEL[1])), ((88, 112, 333), (EIFFEL[0], 126, EIFFEL[1])), ((128, 124, 356), (EIFFEL[0], 128, EIFFEL[1]))],
    speed=24, at=(60, 0.5, 470)))

# ── the High Roller (hub 437.1, 85.1, -182; radius 79.25): up from the LINQ side, across the wheel's face at hub height,
#    over its east rim, then a look back west over the Strip.
HUB = (437.1, 85.1, -182.0)
print('fly-highroller', flight('fly-highroller', [
    ((457, 46, 40), HUB), ((452, 64, -55), HUB), ((430, 82, -134), HUB), ((474, 96, -146), HUB), ((516, 122, -150), HUB),
    ((540, 166, -186), (437, 70, -182)), ((522, 186, -232), (300, 40, -300))],
    speed=22, at=(440, 0.5, -120)))

# ── the Sphere (centre 983.04, -583.71; radius 78.6, top ~112 m): a rising half-orbit round its south and east sides
SPH = (983.04, 40, -583.71)
orbit = []
for k in range(8):
    a = math.radians(130 - k * 20); r = 235 - 30 * math.sin(math.pi * k / 7)
    cx, cz = SPH[0] + r * math.cos(a), SPH[2] + r * math.sin(a)
    # look a little past the Sphere's centre toward the side we fly to, so it sits off-centre with the city around it
    orbit.append(((cx, 28 + k * 10, cz), (SPH[0] + 45 * math.cos(a - 1.2), 52, SPH[2] + 45 * math.sin(a - 1.2))))
print('fly-sphere', flight('fly-sphere', orbit, speed=32, at=(900, 0.5, -470)))

# ── down the Strip canyon: low and fast up the Boulevard from CityCenter to the Bellagio fountains, over the bridges
canyon = strip_path(1010, 560, lane=0, step=40)
pts = []
for i, (x, z) in enumerate(canyon):
    y = 26 if i < len(canyon) - 2 else 26 + 14 * (i - len(canyon) + 3)
    pts.append(((x + 5 * math.sin(i * 0.9), y, z), None if i < len(canyon) - 3 else (40, 40 + 10 * (i - len(canyon) + 3), 360)))
print('fly-strip', flight('fly-strip', pts, speed=28, at=(-5, 0.5, 800), lookahead=45))

# ── the Bellagio lake, higher and faster than v2 (the reflections read better from 8-12 m): toward the hotel
print('lake-glide', flight('lake-glide', [((-10, 14, 300), None), ((-55, 10.5, 314), (-260, 40, 350)), ((-95, 9, 328), (-260, 55, 352)),
    ((-122, 11, 338), (-270, 80, 355))], speed=12, at=(-14, 0.5, 360), lookahead=60))

# ── drives on cleared routes (tools/film/roads.py + route-check.js): build/film/route-*-clear.json, [x, z, speed] every 3 m.
#    Drone keys are in the jeep's frame (x right, y up, z forward); times follow the route's speed profile (scale 0.9).
north2 = json.load(open(os.path.join(ROOT, 'build/film/route-north2-clear.json')))
write('drone-north2', {'start': {'seat': {'at': [north2[0][0], 0.6, north2[0][1]], 'heading': heading([p[:2] for p in north2[:2]])}, 'warm': 6},
    'maxSeconds': 150, 'steps': [{'drive': {'path': north2, 'scale': 0.9, 'speed': 20, 'stop': False}}],
    'camera': [{'from': 0, 'to': 135, 'anchor': 'drone', 'lag': 0.42, 'keys': [
        K(0,   [-2.6, 1.1, 7.5],  [0, 1.0, 0]),      # low in front: the jeep pulls out of the Bellagio drive under the trees
        K(4,   [3.2, 1.4, 4.0],   [0, 1.0, 1.0]),    # whip round to its right
        K(8,   [4.5, 1.6, -3.0],  [0, 1.1, 6.0]),    # low right-rear through the curve
        K(12,  [-4.0, 2.6, -5.5], [0, 1.2, 8.0]),    # across behind it to the left
        K(16,  [-1.5, 6.0, 9.0],  [0, 0.8, 0]),      # up and in front, looking back down
        K(21,  [0, 16, -14],      [0, 2, 24]),       # rise behind as it turns onto the Boulevard: the Eiffel and the fountains
        K(26,  [9, 5, -4],        [0, 1, 10]),       # drop to the right
        K(30,  [6, 2.0, 6],       [0, 1.1, -2]),     # low beside it, the Arc and the balloon behind
        K(34,  [1.5, 1.4, 11],    [0, 1.0, 0]),      # in front, low: it comes at us at speed
        K(38,  [-7, 3.0, 2],      [0, 1.1, 8]),      # swing left, Caesars
        K(42,  [-3, 1.6, -6],     [0, 1.3, 10]),     # low chase
        K(46,  [0, 22, 4],        [0, 0, 6]),        # straight up over it
        K(51,  [12, 14, -6],      [0, 1, 12]),       # high right as it turns onto Flamingo Road
        K(56,  [4.5, 1.8, -4],    [0, 1.1, 8]),      # down to a low right chase
        K(58.5,[5.0, 2.0, 4],     [0, 1.1, 2]),      # up its right side (never through it)
        K(61,  [-3, 1.5, 9],      [0, 1, 0]),        # front-left, low
        K(66,  [-8, 5, -1],       [0, 1, 9]),
        K(71,  [0, 2.2, -7],      [0, 1.4, 12]),     # dead astern, low
        K(77,  [6, 9, 3],         [0, 1, 8]),
        K(84,  [0, 24, -16],      [0, 6, 40]),       # rise behind through the turn north: the High Roller ahead
        K(92,  [-10, 10, 6],      [0, 8, 30]),       # left, looking up the road at the wheel
        K(100, [-4, 2.0, 10],     [0, 2.5, 0]),      # low in front
        K(104, [5.5, 2.4, 3],     [0, 2.5, 4]),      # round its right side
        K(108, [5, 2.5, -6],      [0, 3, 14]),       # low right chase toward the wheel's base
        K(114, [3, 6, 4],         [-40, 60, 12]),    # passing the wheel: look up at it
        K(120, [0, 26, -10],      [0, 10, 40]),      # climb behind, the LINQ ahead
        K(135, [0, 30, -14],      [0, 8, 50])]}]})
south2 = json.load(open(os.path.join(ROOT, 'build/film/route-south2-clear.json')))
write('drone-south2', {'start': {'seat': {'at': [south2[0][0], 0.6, south2[0][1]], 'heading': heading([p[:2] for p in south2[:2]])}, 'warm': 6},
    'maxSeconds': 75, 'steps': [{'drive': {'path': south2, 'scale': 0.9, 'speed': 20, 'stop': False}}],
    'camera': [{'from': 0, 'to': 62, 'anchor': 'drone', 'lag': 0.42, 'keys': [
        K(0,  [0, 20, -14],      [0, 2, 26]),        # high behind on Harmon: the Cosmopolitan and CityCenter towers
        K(5,  [-6, 3, 4],        [0, 1, 8]),         # dive to its left
        K(9,  [-2.5, 1.3, 9],    [0, 1, 0]),         # low in front
        K(14, [6, 6, 2],         [0, 1, 10]),        # up to the right through the turn onto the Boulevard
        K(19, [3, 1.6, -6],      [0, 1.2, 10]),      # low right chase
        K(21, [4.6, 2.0, 3],     [0, 1.1, 3]),       # up its right side (never through it)
        K(23, [-1, 1.3, 11],     [0, 1, 0]),         # in front: Crystals behind it
        K(27, [-12, 12, 4],      [-20, 12, 16]),     # wide left, CityCenter above
        K(32, [-5, 2.0, -5],     [0, 1.3, 10]),      # low left chase past the Waldorf
        K(37, [0, 24, 2],        [0, 0, 10]),        # straight up
        K(42, [9, 8, 10],        [0, 1, 0]),         # come round in front, right
        K(47, [3, 1.5, 8],       [0, 1, 0]),         # low in front: New York-New York ahead of it
        K(52, [0, 18, -12],      [0, 10, 40]),       # rise behind: the coaster
        K(62, [0, 26, -16],      [0, 14, 50])]}]})

# ── walks at a run: casinos and lobbies (the owner: the camera should move about twice as fast)
walk_take('casino-caesars', [-192.44, 0.16, -80.57], (-1, 0), back=8, forward=26, pitch=0.12, run=True)
walk_take('casino-flamingo', [47.28, 0.16, -47.0], (1, 0), back=6, forward=26, pitch=0.16, run=True)
walk_take('casino-planet-hollywood', [92.56, 0.09, 655.15], (1, 0), back=4, forward=24, pitch=0.04, run=True)
walk_take('lobby-venetian', [202.06, 0.0, -688.59], (0.987, 0.122), back=6, forward=40, pitch=0.18, sway=(0.25, 12), run=True)
walk_take('lobby-bellagio', [-230.0, 0.18, 445.0], (-1, 0), back=4, forward=26, pitch=0.28, sway=(0.25, 12), run=True)
walk_take('crystals-atrium', [-86.4, 0.09, 906.19], (-0.721, 0.693), back=4, forward=22, pitch=0.1, run=True)


# ══ the 45-second clip (2026-10-08: on v3 the owner asked to check the flight paths before hours of rendering; the camera
#    hunted left and right and turned suddenly, the jeep bumped twice a second, the 4-frame blend looked blurry). One drive,
#    filmed as five simple moves (one drone segment each = a cut; two keys per segment, so nothing wanders), previewed in
#    real time and checked with camera-check.py before the final render. No sub-frames.
def seg(t0, t1, a, b, look_a, look_b, lag=0.5):
    return {'from': t0, 'to': t1, 'anchor': 'drone', 'lag': lag, 'keys': [K(0, a, look_a), K(t1 - t0, b, look_b)]}
# The north route split in two (2026-10-08 real-time runs): the foot of the Bellagio drive has a step (-199, 465) a standing
# jeep cannot climb, and around (-75..-50, 546..562) the road runs through the Bellagio block's raised driveway collision
# (0.5-1.8 m), which throws the jeep off its line into the bollards. A: the drive under the trees, ending before it;
# B: from x -40, the curve onto the Boulevard and north past Paris to the turn onto Flamingo Road.
nA = north2[next(i for i, p in enumerate(north2) if p[1] > 472):next(i for i, p in enumerate(north2) if p[0] > -84)]
nB = north2[next(i for i, p in enumerate(north2) if p[0] > -42):next(i for i, p in enumerate(north2) if p[0] > 120)]
def seat(path): return {'seat': {'at': [path[0][0], 0.6, path[0][1]], 'heading': heading([p[:2] for p in path[:2]])}, 'warm': 6}
write('drive45a', {'start': seat(nA), 'subframes': 1, 'maxSeconds': 20,
    'steps': [{'drive': {'path': nA, 'scale': 0.9, 'speed': 20, 'stop': False}}],
    'camera': [seg(0, 20, [4.5, 1.7, -2.0], [5.0, 1.9, 2.0], [0, 1.0, 3], [0, 1.0, 1])]})        # beside it under the trees
write('drive45b', {'start': seat(nB), 'subframes': 1, 'maxSeconds': 40,
    'steps': [{'drive': {'path': nB, 'scale': 0.9, 'speed': 20, 'stop': False}}],
    'camera': [
        seg(0, 11,  [0, 3.0, -9.0],   [0, 13.0, -15.0], [0, 1.5, 12], [0, 3.0, 40]),    # rise behind through the turn onto the Boulevard
        seg(11, 18, [-6.0, 1.8, 1.5], [-6.0, 2.2, -1.5],[0, 1.0, 1],  [0, 1.0, 2]),     # alongside, Paris and the Eiffel beyond it
        seg(18, 25, [1.6, 1.5, 11.0], [2.0, 1.9, 9.0],  [0, 1.0, 0],  [0, 1.0, 0]),     # in front, pulling back as it comes at us
        seg(25, 40, [6.0, 4.0, -6.0], [10.0, 20.0, -12.0], [0, 1.2, 6], [0, 2.0, 20]),  # crane up over the turn onto Flamingo Road
    ]})


# ══ camera runs (2026-10-08: the owner asked for spline camera runs from outside through the hotel entrance
#    and lobby, up the stairs, along a corridor into a room and to its window). Points carry their
#    own speed; the camera looks along the path (lookahead grows with speed) unless a point names a target; the view is
#    eased over 0.15 s so turns lead smoothly. Interiors stream around the camera (focus) and doors open ahead of it.
TOWERS = {t['id']: t for f in ('towers', 'highrise-towers', 'landmark-towers') for t in json.load(open(os.path.join(ROOT, f'src/work/hotels/{f}.json')))}
def tower_world(t, p):
    """HotelLayout.worldPoint: tower-local (x across, y up, z along the corridor) to world."""
    x, y, z = p; o = t['origin']
    if t.get('linear'): a, b, c, d = t['linear']; return [o[0] + a * x + b * z, o[1] + y, o[2] + c * x + d * z]
    cy, sy = math.cos(t['yaw']), math.sin(t['yaw']); return [o[0] + cy * x + sy * z, o[1] + y, o[2] - sy * x + cy * z]

def camera_run(points, ramp_in=0.6, ramp_out=1.2, dt=1 / 30, look_ease=0.15):
    """points: [(world pos, speed m/s, look target or None)]. Returns camera keys (t, pos, look)."""
    P = [list(map(float, p)) for p, _, _ in points]; V = [v for _, v, _ in points]; L = [l for _, _, l in points]
    ext = [[2 * a - b for a, b in zip(P[0], P[1])]] + P + [[2 * a - b for a, b in zip(P[-1], P[-2])]]
    dense, par = [], []
    for i in range(len(P) - 1):
        for k in range(60):
            dense.append(_cr(ext[i], ext[i + 1], ext[i + 2], ext[i + 3], k / 60)); par.append(i + k / 60)
    dense.append(P[-1]); par.append(len(P) - 1)
    S = [0.0]
    for a, b in zip(dense, dense[1:]): S.append(S[-1] + math.dist(a, b))
    total = S[-1]
    def speed_at(u):
        i = min(int(u), len(V) - 2); f = u - i; f = f * f * (3 - 2 * f); return V[i] + (V[i + 1] - V[i]) * f
    # integrate time along the path, with eased start and stop
    T = [0.0]
    for j in range(1, len(dense)):
        v = max(0.4, speed_at(par[j]))
        T.append(T[-1] + (S[j] - S[j - 1]) / v)
    # ramps: stretch the first/last stretches of time so speed eases from/to ~0
    def at_s(s):
        s = min(max(s, 0), total); j = max(1, next((k for k in range(1, len(S)) if S[k] >= s), len(S) - 1))
        f = (s - S[j - 1]) / max(1e-9, S[j] - S[j - 1])
        return [a + (b - a) * f for a, b in zip(dense[j - 1], dense[j])], par[j - 1] + (par[j] - par[j - 1]) * f
    dur = T[-1]
    # resample at fixed dt over time (with the ease applied to the time->distance map)
    out_t, out_s = [], []
    n = int((dur + ramp_in + ramp_out) / dt) + 1
    # build distance(t) by inverting T, then warp with smooth ramps (speed ~0 at both ends)
    import bisect
    def s_of_time(tt):
        k = bisect.bisect_left(T, tt); k = min(max(k, 1), len(T) - 1); f = (tt - T[k - 1]) / max(1e-9, T[k] - T[k - 1]); return S[k - 1] + (S[k] - S[k - 1]) * f
    total_t = dur + (ramp_in + ramp_out) / 2
    keys, looks = [], []
    for i in range(n + 1):
        t = min(i * dt, dur + ramp_in + ramp_out)
        # time warp: a trapezoid speed profile in "path time"
        if t < ramp_in: tau = t * t / (2 * ramp_in)
        elif t > ramp_in + dur: x = t - ramp_in - dur; tau = ramp_in / 2 + dur + (x - x * x / (2 * ramp_out))
        else: tau = ramp_in / 2 + (t - ramp_in)
        tau = min(tau, dur); s = s_of_time(tau); pos, u = at_s(s)
        v = speed_at(u); ahead, _ = at_s(s + max(2.2, 0.55 * v))
        if s + 0.5 >= total:   # at the end: keep the last direction
            a, _ = at_s(total - 1.0); ahead = [p + (p - q) * 2 for p, q in zip(pos, a)]
        i0 = min(int(u), len(P) - 2); f = u - i0; f = f * f * (3 - 2 * f)
        l0 = L[i0] or ahead; l1 = L[i0 + 1] or ahead
        look = [a + (b - a) * f for a, b in zip(l0, l1)]
        d = [b - a for a, b in zip(pos, look)]; dl = math.sqrt(sum(c * c for c in d)) or 1
        keys.append((t, pos)); looks.append([c / dl for c in d])
    # ease the view direction (Gaussian over look_ease seconds) so it leads turns smoothly
    k = max(1, int(look_ease / dt)); smooth = []
    for i in range(len(looks)):
        acc = [0, 0, 0]; wsum = 0
        for j in range(max(0, i - 3 * k), min(len(looks), i + 3 * k + 1)):
            w = math.exp(-0.5 * ((j - i) / k) ** 2); wsum += w; acc = [a + w * b for a, b in zip(acc, looks[j])]
        l = math.sqrt(sum(c * c for c in acc)) or 1; smooth.append([c / l for c in acc])
    return [{'t': round(t, 4), 'pos': [round(c, 3) for c in p], 'look': [round(c + 10 * d, 3) for c, d in zip(p, dv)]} for (t, p), dv in zip(keys, smooth)]

# The Cromwell (vanderpump-1, The Vanderpump Hotel): its level-3 rooms see out over the neighbours (the LINQ, tried first,
# has its level-3 rooms inside its 17 m podium); south they face the Eiffel Tower (278 m) but into the low sun, north the
# High Roller, 20-30 m behind the Flamingo's facade. Its street portal on
# the Boulevard (tower-local z -71.5, 5 x 4.5 m) sits behind a pedestrian-bridge stair; under that stair there is 2.1 m of
# clear height on the portal's line, so the camera dives from over the Boulevard and skims under it into the arrival hall, a
# casino floor (tables to ~2 m) that runs straight to the hotel lobby's glass door (z -23.25). Tower-local frame: x across, z
# along the corridor; U-stairs: first flight on x -1.9 rising toward +z, half landing at z +3.6, second flight on x +1.9 back
# toward -z, landings at z -2.5..-5; stair door z -4.98 (1.78 m wide); room doors at x +-1.85 (1.3 m), bay z = -8.1 - 6*bay;
# room side -1 faces south; its window at x -9.45. Guest rooms from level 3 (floor 2).
HT = TOWERS['vanderpump-1']
def W(x, y, z): return tower_world(HT, (x, y, z))
def storey(y0, v):
    """One storey of the U-stair from the landing at floor height y0 (eye 1.6 m up) to the next landing."""
    e = y0 + 1.6
    return [(W(-1.2, e + .05, -3.0), v, None), (W(-1.9, e + .2, -2.0), v, None), (W(-1.9, e + 1.55, 1.8), v, None),
            (W(-1.35, e + 1.8, 3.35), v * .62, None), (W(0, e + 1.85, 3.85), v * .55, None), (W(1.35, e + 1.8, 3.35), v * .62, None),
            (W(1.9, e + 1.6, 1.8), v, None), (W(1.9, e + 3.25, -2.0), v, None)]
# The south rooms: the Eiffel Tower and Paris across Flamingo Road (the north ones face the Flamingo's facade 20-30 m off).
EIFFEL_VIEW = [74.5, 68, 400.5]
# Height and line vary with the space (the owner asked for runs that start high, swoop to the
# floor and up again, curving and tilting): dive from the street under the bridge stair, rise and S-curve over the
# casino floor, swoop down to the lobby door, up across the lobby and down again to the stair door.
run = [(W(0, 12.0, -114), 13, None), (W(0, 6.0, -98), 12, None), (W(0, 1.7, -86), 10.5, None), (W(0, 1.45, -78), 10, None),
       (W(0, 1.5, -71.5), 10, None),                                           # under the bridge stair, through the portal
       (W(-1.6, 3.2, -62), 11, None), (W(1.6, 3.5, -52), 11, None), (W(3.0, 3.6, -42), 11, None),    # rise and S-curve over
       (W(1.8, 2.8, -33), 10, None), (W(0.4, 1.9, -26.5), 9, None),                                   # the casino floor, swoop
       (W(0, 1.8, -23.25), 9, None),                                                                  # down to the lobby door,
       (W(-1.4, 3.3, -17.5), 8.5, None), (W(-0.6, 3.6, -12.5), 7.5, None), (W(0.3, 2.3, -8.5), 6.5, None), # up over the lobby,
       (W(0, 1.65, -4.98), 5.5, None)]                                                                # down to the stair door
run += storey(0.0, 6.0)
run += [(W(1.2, 5.25, -3.45), 3.6, None), (W(0, 5.25, -3.9), 3.4, None)]
run += storey(3.6, 6.0)[1:]
run += [(W(1.1, 8.7, -3.6), 5.5, None), (W(0.15, 8.65, -4.98), 6.0, None),        # out through the level-3 stair door
        (W(0.2, 8.65, -8.0), 7.0, None), (W(0.45, 8.65, -11.2), 5.5, None),       # down the corridor, drifting right
        (W(0.0, 8.65, -13.75), 3.6, None), (W(-1.1, 8.7, -14.1), 3.3, None),      # swing left, square to the room door,
        (W(-1.85, 8.7, -14.1), 3.3, None), (W(-2.7, 8.75, -14.1), 3.2, None),     # straight through its 1.3 m opening
        (W(-4.6, 8.8, -14.1), 3.0, None), (W(-7.0, 8.9, -14.1), 2.0, EIFFEL_VIEW),     # across the room, the view opening up:
        (W(-8.85, 8.95, -14.1), 0.5, EIFFEL_VIEW)]                                      # the Eiffel Tower across Flamingo Road
keys = add_bank(camera_run(run, ramp_in=0.5, ramp_out=1.4, look_ease=0.38))
secs = keys[-1]['t']
# recorded at 120 frames a second (2 sub-frames, NOT blended) so the cut can play stretches at 1.5x or 2x with every
# output frame a real, sharp render
write('hotel-run', {'start': {'at': W(0, 0.3, -50), 'dir': [1, 0], 'view': 'first', 'warm': 5, 'hotelPin': ['vanderpump-1', 2, 1, -1]},
    'seconds': round(secs + 1.5, 2), 'maxSeconds': round(secs + 4, 2), 'subframes': 2, 'blend': False, 'steps': [{'wait': round(secs + 1.5, 2)}],
    'camera': [{'from': 0, 'to': round(secs + 1.5, 2), 'focus': 'camera', 'doors': True, 'keys': keys}]})
print('hotel-run', round(secs, 1), 's,', len(keys), 'keys')
