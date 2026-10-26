#!/usr/bin/env python3
"""The continuous camera: one take, one camera, no cuts (tools/film/takes/tour.json).

2026-10-08, after the 45-second preview 2: the owner wanted one continuous camera, the opening run through the arc
speeding up into the path that follows the car, and fast camera runs linking each area to the next; the route covers
everything, ordered spatially.

  Paris: through the Arc de Triomphe, speeding up, round onto the Boulevard behind the jeep
  the jeep: catch it and ride beside it (the camera looks at the jeep itself), then peel off left
  the Bellagio lake: low over the water, the hotel across it
  the Cromwell: over the Boulevard, under the bridge stair, the casino, the lobby, two storeys of stairs, the level-3
      corridor, room 301, the window and the Eiffel Tower, then out through the window
  the High Roller: up and across the wheel's face
  the Sphere: round it, close to its skin
  the Venetian: over the roof, down to the canal, in through the colonnade, a climbing U-turn under the fresco, out the
      same doors (the upper gallery's Rialto exit has 2 m of headroom under a stone slab, over the bridge's rail)
  the Strip: south down the Boulevard, round the Eiffel Tower
  the Big Apple Coaster: down behind the train as it crawls over the top, into the front seat for the drop

Every leg is one world-anchored camera path (points with their own speed, the view along the path or at a target, banked
into its turns); segments split it only to change what the camera looks at (the jeep), to keep the Cromwell's exterior
hidden while the camera leaves through its own wall, and to hand over to the coaster's front seat (blended).
Run: python3 tools/film/make-tour.py [--report]   (then tools/film/clearance.py tour, plan-slice.py, record.mjs)
"""
import bisect, json, math, os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, 'tools/film/takes')
DT = 1 / 30

# ── path tools ────────────────────────────────────────────────────────────────────────────────────────────────────────────
def _cr(p0, p1, p2, p3, u):
    """Centripetal Catmull-Rom between p1 and p2 (no overshoot or cusps on uneven control spacing)."""
    def tj(ti, a, b): return ti + max(1e-6, math.dist(a, b)) ** 0.5
    t0 = 0; t1 = tj(t0, p0, p1); t2 = tj(t1, p1, p2); t3 = tj(t2, p2, p3); t = t1 + (t2 - t1) * u
    def L(a, b, ta, tb): return [(tb - t) / (tb - ta) * x + (t - ta) / (tb - ta) * y for x, y in zip(a, b)]
    A1, A2, A3 = L(p0, p1, t0, t1), L(p1, p2, t1, t2), L(p2, p3, t2, t3)
    B1, B2 = L(A1, A2, t0, t2), L(A2, A3, t1, t3)
    return L(B1, B2, t1, t2)

def camera_path(points, ramp_in=0.0, ramp_out=1.0, look_ease=0.3, calm=None, calm_rate=55.0, calm_max=1.1):
    """points: [(pos, speed m/s, look target or None)]. The camera moves along a centripetal Catmull-Rom through the points at
    the speeds given (eased between points), looking along the path (lookahead grows with speed) or at a point's target
    (blended between points); the view direction is eased over `look_ease` s, and wherever it would still turn faster than
    `calm_rate` deg/s (a target handing back to the path, a turn at speed) over up to `calm_max` s, except on points whose
    `calm` flag is False (the stairs, where the turns are the point). Speed ramps from 0 over `ramp_in` s and to 0 over
    `ramp_out` s (0 = start/end at speed). Returns (keys every DT s, the time each point is passed)."""
    P = [list(map(float, p)) for p, _, _ in points]; V = [v for _, v, _ in points]; Lk = [l for _, _, l in points]
    ext = [[2 * a - b for a, b in zip(P[0], P[1])]] + P + [[2 * a - b for a, b in zip(P[-1], P[-2])]]
    dense, par = [], []
    for i in range(len(P) - 1):
        n = max(12, int(math.dist(P[i], P[i + 1]) / 0.4))
        for k in range(n):
            dense.append(_cr(ext[i], ext[i + 1], ext[i + 2], ext[i + 3], k / n)); par.append(i + k / n)
    dense.append(P[-1]); par.append(len(P) - 1)
    S = [0.0]
    for a, b in zip(dense, dense[1:]): S.append(S[-1] + math.dist(a, b))
    total = S[-1]
    def speed_at(u):
        i = min(int(u), len(V) - 2); f = u - i; f = f * f * (3 - 2 * f); return V[i] + (V[i + 1] - V[i]) * f
    T = [0.0]
    for j in range(1, len(dense)): T.append(T[-1] + (S[j] - S[j - 1]) / max(0.3, speed_at((par[j] + par[j - 1]) / 2)))
    dur = T[-1]
    def at_s(s):
        s = min(max(s, 0.0), total); j = min(max(1, bisect.bisect_left(S, s)), len(S) - 1)
        f = (s - S[j - 1]) / max(1e-9, S[j] - S[j - 1])
        return [a + (b - a) * f for a, b in zip(dense[j - 1], dense[j])], par[j - 1] + (par[j] - par[j - 1]) * f
    def s_of_tau(tau):
        k = min(max(1, bisect.bisect_left(T, tau)), len(T) - 1); f = (tau - T[k - 1]) / max(1e-9, T[k] - T[k - 1]); return S[k - 1] + (S[k] - S[k - 1]) * f
    # time warp: ease the path's own clock in and out (speed ~0 at a ramped end), unchanged in between
    def tau_of(t):
        if ramp_in and t < ramp_in: return t * t / (2 * ramp_in)
        tau = t - ramp_in / 2; end_start = dur - ramp_out / 2
        if ramp_out and tau > end_start:
            x = min(t - (end_start + ramp_in / 2), ramp_out); tau = end_start + (x - x * x / (2 * ramp_out))
        return min(tau, dur)
    t_end = dur + ramp_in / 2 + ramp_out / 2
    n = int(math.ceil(t_end / DT))
    poss, looks, times = [], [], []
    for i in range(n + 1):
        t = min(i * DT, t_end); tau = tau_of(t); s = s_of_tau(tau); pos, u = at_s(s)
        v = speed_at(u); ahead, _ = at_s(s + max(2.2, 0.55 * v))
        if s + 0.6 >= total:
            a, _ = at_s(total - 1.0); ahead = [p + (p - q) * 3 for p, q in zip(pos, a)]
        i0 = min(int(u), len(P) - 2); f = u - i0; f = f * f * (3 - 2 * f)
        l0 = Lk[i0] or ahead; l1 = Lk[i0 + 1] or ahead
        look = [a + (b - a) * f for a, b in zip(l0, l1)]
        d = [b - a for a, b in zip(pos, look)]; dl = math.sqrt(sum(c * c for c in d)) or 1
        poss.append(pos); looks.append([c / dl for c in d]); times.append(round(i * DT, 4))
    def gauss(src, sig):
        out = []
        for i in range(len(src)):
            k = max(1.0, sig[i] / DT); r = int(3 * k); acc = [0.0, 0.0, 0.0]
            for j in range(max(0, i - r), min(len(src), i + r + 1)):
                w = math.exp(-0.5 * ((j - i) / k) ** 2); acc = [a + w * b for a, b in zip(acc, src[j])]
            l = math.sqrt(sum(c * c for c in acc)) or 1; out.append([c / l for c in acc])
        return out
    smooth = gauss(looks, [look_ease] * len(looks))
    # calm the remaining whips: the turn rate of the eased view, its peak within +-0.6 s, sets a wider ease there
    rate = [0.0] + [math.degrees(math.acos(max(-1, min(1, sum(a * b for a, b in zip(smooth[i - 1], smooth[i])))))) / DT for i in range(1, len(smooth))]
    calm_ok = [True] * len(smooth)
    if calm is not None:
        for i in range(len(smooth)):
            u = 0.0
            _, u = at_s(s_of_tau(tau_of(min(i * DT, t_end))))
            calm_ok[i] = calm[min(int(round(u)), len(calm) - 1)]
    w = int(0.6 / DT); sig = []
    for i in range(len(smooth)):
        peak = max(rate[max(0, i - w):i + w + 1])
        sig.append(look_ease if not calm_ok[i] or peak <= calm_rate else min(calm_max, look_ease * peak / calm_rate))
    sig = [sum(sig[max(0, i - w):i + w + 1]) / len(sig[max(0, i - w):i + w + 1]) if calm_ok[i] else look_ease for i in range(len(sig))]
    smooth = gauss(looks, sig)
    keys = [{'t': t, 'pos': [round(c, 3) for c in p], 'look': [round(c + 10 * d, 3) for c, d in zip(p, dv)]} for t, p, dv in zip(times, poss, smooth)]
    # when each point is passed (path clock -> film clock)
    point_t = []
    for i in range(len(P)):
        j = min(range(len(par)), key=lambda q: abs(par[q] - i)) if i in (0, len(P) - 1) else bisect.bisect_left(par, i)
        j = min(j, len(T) - 1); tau = T[j]
        point_t.append(round(tau + ramp_in / 2, 2))
    return keys, point_t

def add_bank(keys, gain=0.35, max_deg=15.0, ease=0.3):
    """Bank into turns (the owner asked for a slight tilt in turns): roll from the path's curvature and speed, like a
    drone or a plane (bank = atan(gain * v * turn rate / g)), capped and eased. Right turns roll right (negative)."""
    n = len(keys)
    hd, sp = [], []
    for i in range(n):
        a, b = keys[max(0, i - 1)], keys[min(n - 1, i + 1)]
        dx, dz = b['pos'][0] - a['pos'][0], b['pos'][2] - a['pos'][2]; dtt = max(1e-6, b['t'] - a['t'])
        hd.append(math.atan2(dx, -dz)); sp.append(math.hypot(dx, dz) / dtt)
    for i in range(1, n):
        while hd[i] - hd[i - 1] > math.pi: hd[i] -= 2 * math.pi
        while hd[i] - hd[i - 1] < -math.pi: hd[i] += 2 * math.pi
    raw = []
    for i in range(n):
        a, b = max(0, i - 2), min(n - 1, i + 2); rate = (hd[b] - hd[a]) / max(1e-6, keys[b]['t'] - keys[a]['t'])
        bank = -math.atan(gain * sp[i] * rate / 9.81) if sp[i] > 1 else 0.0
        raw.append(max(-math.radians(max_deg), min(math.radians(max_deg), bank)))
    k = max(1, int(ease / DT))
    for i in range(n):
        acc = wsum = 0.0
        for j in range(max(0, i - 3 * k), min(n, i + 3 * k + 1)):
            w = math.exp(-0.5 * ((j - i) / k) ** 2); acc += w * raw[j]; wsum += w
        keys[i]['roll'] = round(acc / wsum, 4)
    return keys

# ── places ────────────────────────────────────────────────────────────────────────────────────────────────────────────────
TOWERS = {t['id']: t for f in ('towers', 'highrise-towers', 'landmark-towers') for t in json.load(open(os.path.join(ROOT, f'src/work/hotels/{f}.json')))}
HT = TOWERS['vanderpump-1']
def W(x, y, z):
    """The Cromwell's tower-local frame (x across, y up from its floor 0, z along the corridor) to world (HotelLayout.worldPoint)."""
    a, b, c, d = HT['linear']; o = HT['origin']; return [o[0] + a * x + b * z, o[1] + y, o[2] + c * x + d * z]
EIFFEL = (74.5, 400.5)
EIFFEL_VIEW = [74.5, 68, 400.5]
HUB = [437.1, 85.1, -182.0]
SPHERE = (983.04, 38.0, -583.71); SPHERE_R = 78.6

# the coaster: the ride clock and the front car's pose, as BigAppleCoaster / CoasterTrack / CoasterRun compute them
ROUTE = json.load(open(os.path.join(ROOT, 'build/south-strip/route.json')))
RP = ROUTE['points']; RS = [p['s'] for p in RP]; RL = ROUTE['length']; PUB = ROUTE['published']
LIFT_END = max([p['s'] for p in RP if p['lift']] + [0])
def _norm(v): l = math.sqrt(sum(c * c for c in v)) or 1; return [c / l for c in v]
def _cross(a, b): return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]
def track(distance):
    """Front car: position and the car frame (right, up, forward) as CoasterTrack.sample builds the train's orientation."""
    s = distance % RL; i = max(0, bisect.bisect_right(RS, s) - 1); j = min(len(RP) - 1, i + 1)
    a, b = RP[i], RP[j]; t = (s - a['s']) / max(1e-5, b['s'] - a['s'])
    lerp = lambda u, v: [x + (y - x) * t for x, y in zip(u, v)]
    pos = lerp(a['position'], b['position']); right = _norm(lerp(a['right'], b['right'])); up = _norm(lerp(a['up'], b['up']))
    fwd = _norm(_cross(up, right)); up = _norm(_cross(right, fwd)); right = [-c for c in right]
    return pos, right, up, fwd, a['lift']
def ride(elapsed):
    """Distance along the track `elapsed` seconds into a ride (CoasterRun, 1/120 s steps)."""
    d = v = e = 0.0; dispatch = 4.0; step = 1 / 120
    while e < elapsed - 1e-9:
        e += step
        if dispatch > 0: dispatch -= step; continue
        pos, _, _, _, lift = track(d); left = RL - d
        target = 2.2 if lift else min(PUB['speed'], math.sqrt(16 + 2 * 9.81 * max(0, PUB['height'] - pos[1])))
        if d < LIFT_END and not lift: target = 4
        if left < 115: target = min(target, max(2.4, math.sqrt(left * .55)))
        acc = 6 if target > v else 10; v += max(-acc * step, min(acc * step, target - v)); d += v * step
    return d, v
# the camera rides 0.8 m ahead of the front car's nose (z +2.2), so the car (too plain close up, the owner) stays out of view
SEAT, SEAT_LOOK = [0.0, 1.45, 3.0], [0.0, 1.05, 15.0]
def car_point(distance, local):
    """A point in the front car's frame (x right, y up, z forward) at `distance` along the track, in world space."""
    pos, r, u, f, _ = track(distance); return [pos[k] + r[k] * local[0] + u[k] * local[1] + f[k] * local[2] for k in range(3)]

# ── the jeep: seated on the Boulevard after the Bellagio drive's curve, driven north at 24 m/s to the Flamingo turn ────────────
north2 = json.load(open(os.path.join(ROOT, 'build/film/route-north2-clear.json')))
i0 = next(i for i, p in enumerate(north2) if p[0] > -42)
i1 = next(i for i, p in enumerate(north2) if p[0] > 120)
nb = north2[i0:i1]
JEEP_START_Z = 528.0
nc = [list(p) for p in nb if p[1] < JEEP_START_Z or p[0] > 30]
JEEP_V = 24.0
for p in nc:
    if p[1] > 300: p[2] = JEEP_V            # the straight: one speed (the route slows for the Bellagio curve behind us)
    else: p[2] = round(min(JEEP_V, p[2] * 1.1), 2)
def jeep_model(path, accel=5.0):
    """Expected (t, x, z) of the jeep from rest along `path` (a guess until a recording's track.json replaces it)."""
    out, t, v = [(0.0, path[0][0], path[0][1])], 0.0, 0.0
    for a, b in zip(path, path[1:]):
        d = math.dist(a[:2], b[:2]); vt = b[2]
        v2 = min(vt, math.sqrt(v * v + 2 * accel * d)) if vt > v else vt
        t += d / max(0.5, (v + v2) / 2); v = v2; out.append((t, b[0], b[1]))
    return out
JEEP = jeep_model(nc)
# measured beats modelled: the first recording showed the jeep at 23 m/s within 1.5 s (the model's 5 m/s^2 left it 50 m ahead)
_measured = os.path.join(ROOT, 'tools/film/jeep-tour-track.json')
if os.path.exists(_measured):
    _m = json.load(open(_measured))
    if _m['startZ'] == JEEP_START_Z and _m['speed'] == JEEP_V: JEEP = [(t, x, z) for t, x, z, _ in _m['samples']]
def jeep_time_at_z(z):
    for (t0, _, z0), (t1, _, z1) in zip(JEEP, JEEP[1:]):
        if z1 <= z <= z0: return t0 + (t1 - t0) * (z0 - z) / max(1e-6, z0 - z1)
    return JEEP[-1][0]

# ── the legs ──────────────────────────────────────────────────────────────────────────────────────────────────────────────
legs = {}
# Paris: in over the porte-cochere, through the Arc's vault at 9 m, speeding up; a hard right round onto the Boulevard
legs['arc'] = [((154, 12.4, 491.3), 14, None), ((140, 10.8, 491.0), 15.5, None), ((127, 9.3, 490.7), 17, None),
               ((110, 9.0, 490.7), 18, None), ((95, 9.2, 490.7), 19, None), ((72, 8.4, 490.2), 21, None),
               ((50, 7.0, 486.5), 22.5, None), ((32, 5.6, 474.0), 24, None), ((21, 4.6, 455.0), 25.5, None)]
# the jeep (northbound right lane, x ~17.5): catch it from behind-left, ride low beside it, then peel off over the balustrade
legs['chase'] = [((15.0, 3.6, 428.0), 27, None), ((13.4, 2.4, 398.0), 28, None), ((12.8, 1.9, 370.0), 27, None),
                 ((12.0, 2.1, 346.0), 26, None)]
# the lake: over the west lanes and the balustrade, low over the water, the Bellagio across it on the left
BELL = [-230, 30, 330]
# (the promenade's trees stand on x -21 every ~24 m: the camera crosses between the ones at z 282 and 306, at a shallow
# angle, so the view's hand-back from the jeep to the lake is not a whip)
legs['lake'] = [((6.0, 3.2, 332.0), 26, None), ((-4, 4.6, 316.0), 26, None), ((-14, 5.4, 303.0), 26, None),
                ((-21, 5.4, 294.0), 26, None), ((-33, 3.8, 282.0), 26, [-220, 26, 280]), ((-46, 2.9, 266.0), 27, [-220, 28, 262]),
                ((-55, 2.8, 250.0), 27, [-210, 30, 240]), ((-55, 3.0, 236.0), 26, None)]
# to the Cromwell: rise off the lake's north end, north over the Flamingo crossing, a right turn onto the portal's line
# east of the lakefront pavilions (x -70..-28, z 175-215, ~24 m tall), over the Flamingo crossing's bridges (all < 11 m)
legs['cromwell-approach'] = [((-44, 6.5, 224.0), 24, None), ((-26, 11.5, 207.0), 23, None), ((-19, 12.4, 184.0), 22, None),
                             ((-21, 12.4, 150.0), 20, None), ((-23, 12.3, 122.0), 16.5, None),
                             ((-16, 12.3, 105.5), 14.5, None)]
# the hotel run (tower-local points; world speeds = what preview 2 played: street 1x, casino 2x, lobby to room 1.5x)
def storey(y0, v):
    e = y0 + 1.6
    return [(W(-1.2, e + .05, -3.0), v, None), (W(-1.9, e + .2, -2.0), v, None), (W(-1.9, e + 1.55, 1.8), v, None),
            (W(-1.35, e + 1.8, 3.35), v * .62, None), (W(0, e + 1.85, 3.85), v * .55, None), (W(1.35, e + 1.8, 3.35), v * .62, None),
            (W(1.9, e + 1.6, 1.8), v, None), (W(1.9, e + 3.25, -2.0), v, None)]
run = [(W(0, 12.0, -114), 13, None), (W(0, 6.0, -98), 12, None), (W(0, 1.7, -86), 10.5, None), (W(0, 1.45, -78), 10, None),
       (W(0, 1.5, -71.5), 10.5, None),
       (W(-1.6, 3.2, -62), 20, None), (W(1.6, 3.5, -52), 22, None), (W(3.0, 3.6, -42), 22, None),
       (W(1.8, 2.8, -33), 18, None), (W(0.4, 1.9, -26.5), 14, None),
       (W(0, 1.8, -23.25), 13, None),
       (W(-1.4, 3.3, -17.5), 12.5, None), (W(-0.6, 3.6, -12.5), 11, None), (W(0.3, 2.3, -8.5), 9.5, None),
       (W(0, 1.65, -4.98), 8.25, None)]
run += storey(0.0, 9.0)
run += [(W(1.2, 5.25, -3.45), 5.4, None), (W(0, 5.25, -3.9), 5.1, None)]
run += storey(3.6, 9.0)[1:]
run += [(W(1.1, 8.7, -3.6), 8.25, None), (W(0.15, 8.65, -4.98), 9.0, None),
        (W(0.2, 8.65, -8.0), 10.5, None), (W(0.45, 8.65, -11.2), 8.25, None),
        (W(0.0, 8.65, -13.75), 5.4, None), (W(-1.1, 8.7, -14.1), 4.95, None),
        (W(-1.85, 8.7, -14.1), 4.95, None), (W(-2.7, 8.75, -14.1), 4.8, None),
        (W(-4.6, 8.8, -14.1), 4.2, None), (W(-7.0, 8.9, -14.1), 2.4, EIFFEL_VIEW),
        (W(-8.3, 8.95, -14.1), 0.9, EIFFEL_VIEW),                    # a breath at the window: the Eiffel Tower across the road
        (W(-9.0, 9.0, -14.1), 1.6, EIFFEL_VIEW)]
legs['hotel'] = run
# out through the window's centre pane (mullions at +-0.79 m), through the tower's own exterior shell (hidden), climbing
# fast toward the High Roller (2026-10-08 review: "too slow ... it unnecessarily slows down at the ferris wheel. It could
# just quickly and smoothly zoom through the wheel and all the way to the sphere")
legs['window-out'] = [(W(-9.7, 9.05, -14.1), 3.6, None), (W(-12.0, 9.3, -14.1), 9, None), (W(-19.0, 10.6, -13.6), 17, None),
                      (W(-27.0, 12.6, -11.0), 26, None), (W(-35.0, 15.2, -5.0), 36, None)]
# through the wheel: 60 m out from the hub at 54.6 degrees, midway between two of its 56 spokes (every 6.43 degrees from 0;
# ~3.3 m to either), well inside the cabins (79 m); the wheel is held at its authored pose while filming
_wn = (0.0798, 0.0, 0.9968); _wr = (0.9968, 0.0, -0.0798)
WHEEL_GAP = [HUB[0] + 60 * (math.cos(math.radians(54.6)) * _wr[0]), HUB[1] + 60 * math.sin(math.radians(54.6)), HUB[2] + 60 * math.cos(math.radians(54.6)) * _wr[2]]
def through_wheel(d):   # a point d m along the wheel's axis from the gap (negative: in front, the south side)
    return tuple(c - d * n for c, n in zip(WHEEL_GAP, _wn))
# (east along Flamingo Road first: the Flamingo is a 69 m block over x 22-250, z -181..83; then north between it and the
# LINQ tower (x 352-366, 63 m), over that tower, to the wheel)
legs['highroller'] = [((150, 30, 136), 55, None), ((230, 44, 150), 75, None), ((285, 66, 95), 95, None), ((318, 96, 10), 105, None),
                      ((365, 120, -75), 105, None),
                      (through_wheel(-46), 95, None), (through_wheel(-16), 90, None), (tuple(WHEEL_GAP), 90, None),
                      (through_wheel(18), 92, None), (through_wheel(50), 100, None)]
# the Sphere: round its south and east side ~25 m off its skin, leaving on its north-east toward the Venetian (2026-10-08:
# "it also goes a little too far around the sphere so it has to turn back a little"), looking a little past its centre
def sphere_at(deg, y, r=SPHERE_R + 26):
    a = math.radians(deg); return (SPHERE[0] + r * math.cos(a), y, SPHERE[2] + r * math.sin(a))
def sphere_look(deg):
    a = math.radians(deg - 55); return [SPHERE[0] + 40 * math.cos(a), 44, SPHERE[2] + 40 * math.sin(a)]
legs['sphere'] = [((620, 118, -330), 120, None), ((770, 88, -430), 115, None), ((880, 64, -490), 92, None)]
legs['sphere'] += [(sphere_at(d, y), 80, sphere_look(d)) for d, y in [(125, 54), (88, 50), (50, 48), (12, 50), (-26, 54), (-60, 56)]]
# the Venetian (2026-10-08: the owner wanted a flight through the Shoppes to the casino and through the lobby): west to the
# terrace door on its east face, along the Grand Canal Shoppes over the water (rising over its two bridges), over the
# balustrade and down the well into the casino, along its main aisle between the slot banks, through the lobby's arch and
# down the fresco hall, out through the colonnade (under the bridge deck, between its pier and the columns) to the Strip
legs['venetian'] = [((860, 52, -700), 105, None), ((700, 40, -716), 115, None), ((560, 24, -728), 90, None),
                    ((480, 12.4, -733), 48, None), ((452, 10.5, -734), 22, None), ((438.6, 9.6, -734), 16, None),
                    ((428, 9.3, -734), 15, [360, 9, -734]), ((416, 9.4, -734.2), 15, None), ((408.6, 10.9, -734), 14.5, None),
                    ((401, 9.6, -733.6), 15, None), ((388, 9.3, -733.6), 15, None), ((380.6, 10.9, -734), 14.5, None),
                    ((373, 9.6, -734), 15, None), ((362, 9.6, -734), 14.5, None), ((353.6, 9.9, -734), 14, None),
                    ((347, 7.6, -733.4), 13, [300, 2, -700]), ((341, 5.0, -732), 13, None),
                    ((334, 3.4, -727), 14, None), ((322, 3.1, -715.5), 15, None), ((310, 3.1, -703.5), 15, None),
                    ((299, 3.3, -692.5), 14.5, None), ((290, 3.6, -685.2), 14, None),
                    ((280, 4.6, -685.1), 13.5, [230, 7, -685]), ((262, 5.4, -685.3), 13.5, [220, 6, -685]), ((245, 4.6, -685.6), 13.5, None),
                    ((233, 3.8, -685.4), 13.5, None), ((225, 3.2, -685.2), 13.5, None), ((221, 3.2, -685.3), 14, None),
                    ((215, 3.4, -685.9), 15, None), ((204, 4.4, -686.6), 17, None), ((190, 7.5, -689.0), 20, None)]
# the Strip: out over the canal, left over the Boulevard west of the campanile (x 140-165, z -630..-608), down it at speed,
# then through the Eiffel Tower (2026-10-08: "fly through the tower (through a hole, not flying through a bar)"): between the
# first and second platforms at 40 m, in through its north-west face and out through the south-east (the legs stand at the
# compass points; 4.3 m from the lattice), and on south to New York-New York
legs['strip'] = [((176, 12, -688), 24, None), ((158, 21, -671), 38, None), ((136, 35, -640), 62, None), ((114, 48, -594), 100, None),
                 ((100, 58, -548), 140, None),
                 ((62, 62, -440), 200, None), ((34, 70, -300), 250, None), ((20, 72, -120), 250, None), ((18, 70, 60), 220, None),
                 ((22, 62, 220), 130, None), ((32, 50, 330), 70, None), ((42.7, 42, 368.7), 52, None), ((56.8, 40.4, 382.8), 50, None),
                 ((74.5, 40.0, 400.5), 50, None), ((92.2, 40.4, 418.2), 50, None), ((106.3, 43, 432.3), 54, None),
                 ((114, 54, 470), 80, None), ((86, 68, 560), 150, None), ((36, 78, 700), 230, None), ((16, 80, 860), 260, None),
                 ((8, 80, 1040), 220, None), ((-40, 78, 1220), 140, None)]
# the coaster: in from the north-east, down behind the train as it crawls over the top, along it to the front seat
MERGE_ELAPSED = 109.0          # the ride clock when the camera sits in the front seat (the release is at ~112.5 s)
DROP_SECONDS = 9.0             # front-seat ride after the merge
def coaster_leg(merge_elapsed):
    d_m, _ = ride(merge_elapsed)
    pts = []
    # back along the track (behind and above the train), approaching faster than the train's 2.2 m/s
    for back, up, side, v in [(64, 13, 5, 42), (32, 6, 2, 17), (12, 2.4, 0.3, 6.5), (0, 0, 0, 2.2)]:
        p = car_point(d_m - back, [SEAT[0] + side, SEAT[1] + up, SEAT[2]])
        pts.append((p, v, None))
    pts[-1] = (car_point(d_m, SEAT), 2.2, car_point(d_m, SEAT_LOOK))
    return pts, d_m
coaster_pts, merge_distance = coaster_leg(MERGE_ELAPSED)
legs['coaster'] = [((-110, 76, 1340), 100, None), ((-170, 74, 1420), 65, None)] + coaster_pts

ORDER = ['arc', 'chase', 'lake', 'cromwell-approach', 'hotel', 'window-out', 'highroller', 'sphere', 'venetian', 'strip', 'coaster']
points, owner = [], []
for name in ORDER:
    for p in legs[name]: points.append(p); owner.append(name)
keys, point_t = camera_path(points, ramp_in=0.0, ramp_out=0.0, look_ease=0.3, calm=[o != 'hotel' for o in owner])
add_bank(keys)
def leg_time(name, which=0):
    idx = [i for i, o in enumerate(owner) if o == name]; return point_t[idx[which]]
T_WORLD = keys[-1]['t']

# the jeep's timing: be ~14 m ahead of the camera as the chase starts (its start waits for that)
t_chase0 = leg_time('chase', 0)
jeep_wait = max(0.0, t_chase0 - jeep_time_at_z(428.0 - 14.0))
# windows (film clock)
FOLLOW = (leg_time('chase', 0) - 0.6, leg_time('chase', -1))                  # look at the jeep (let go as it peels off)
HIDE = (leg_time('hotel', -1), leg_time('highroller', 1))                      # the Cromwell's shell, from the window out
T_MERGE = T_WORLD                                                              # the world path ends in the front seat
BLEND = 2.2
T_END = round(T_MERGE + DROP_SECONDS, 2)
COASTER_START = round(MERGE_ELAPSED - T_MERGE, 3)                             # ride clock at the take's start

def piece(t0, t1, **extra):
    """World keys for [t0, t1] (film clock), re-timed to the segment."""
    sel = [k for k in keys if t0 - DT / 2 <= k['t'] <= t1 + DT / 2]
    return dict({'from': round(sel[0]['t'], 4), 'to': round(sel[-1]['t'], 4), 'focus': 'camera', 'doors': True,
                 'keys': [dict(k, t=round(k['t'] - sel[0]['t'], 4)) for k in sel]}, **extra)
snap = lambda t: round(round(t / DT) * DT, 4)
f0, f1, h0, h1 = snap(FOLLOW[0]), snap(FOLLOW[1]), snap(HIDE[0]), snap(HIDE[1])
O_IN, O_OUT = snap(1.0), snap(2.6)                                             # the look blends to the jeep, and back to the path
segments = [piece(0, f0 + O_IN), piece(f0, f1 + O_OUT, follow=True), piece(f1, h0 + 2 * DT), piece(h0, h1 + 2 * DT, hide='guest-vanderpump'),
            piece(h1, T_WORLD)]
segments.append({'from': snap(T_MERGE - BLEND), 'to': T_END, 'anchor': 'coaster', 'focus': 'camera',
                 'keys': [{'t': 0, 'pos': SEAT, 'look': SEAT_LOOK, 'fov': 72}, {'t': round(T_END - (T_MERGE - BLEND), 3), 'pos': SEAT, 'look': SEAT_LOOK, 'fov': 72}]})
# a fixed 60-degree view, widening toward the front seat's 72 over the world path's last 6 s (the blend has nothing to swing)
for seg in segments[:-1]:
    for k in seg['keys']:
        t = k['t'] + seg['from']; w = min(1, max(0, (t - (T_MERGE - 6)) / 6)); k['fov'] = round(60 + 12 * w * w * (3 - 2 * w), 2)

take = {'name': 'tour', 'seconds': T_END, 'maxSeconds': T_END + 6, 'subframes': 1, 'blend': False,
        'start': {'seat': {'at': [nc[0][0], 0.6, nc[0][1]], 'heading': round(math.atan2(nc[1][0] - nc[0][0], nc[1][1] - nc[0][1]), 4)},
                  'warm': 8, 'hotelPin': ['vanderpump-1', 2, 1, -1], 'venues': ['vanderpump', 'venetian'], 'coaster': COASTER_START},
        # (the take ends at `seconds` once the steps are done: no trailing wait, or it runs to maxSeconds)
        'steps': [{'wait': round(jeep_wait, 2)}, {'drive': {'path': nc, 'speed': JEEP_V, 'stop': False}}],
        'camera': segments}
with open(os.path.join(OUT, 'tour.json'), 'w') as f: json.dump(take, f, indent=0)
print(f'tour: {T_END:.1f} s ({len(keys)} keys, world path {T_WORLD:.1f} s); jeep waits {jeep_wait:.2f} s; coaster starts {COASTER_START} s into a ride')
for name in ORDER: print(f'  {leg_time(name):6.1f} s  {name}')
print(f'  follow {f0}-{f1}  hide {h0}-{h1}  coaster seat from {T_MERGE - BLEND:.1f} (in at {T_MERGE:.1f}), end {T_END}')

if '--report' in sys.argv:
    # speed, turn rate (deg/s, of the view) and height, every half second
    def yaw(k): d = [b - a for a, b in zip(k['pos'], k['look'])]; return math.atan2(d[0], -d[2]), math.atan2(d[1], math.hypot(d[0], d[2]))
    step = int(0.5 / DT)
    for i in range(0, len(keys) - step, step):
        a, b = keys[i], keys[i + step]; (y0, p0), (y1, p1) = yaw(a), yaw(b)
        dy = (y1 - y0 + math.pi) % (2 * math.pi) - math.pi
        print(f"{a['t']:6.1f}  v {math.dist(a['pos'], b['pos']) / 0.5:6.1f}  turn {math.degrees(dy) / 0.5:7.1f}  pitch {math.degrees(p0):6.1f}  "
              f"y {a['pos'][1]:6.1f}  roll {math.degrees(a.get('roll', 0)):5.1f}  {owner[min(len(owner) - 1, bisect.bisect_right(point_t, a['t']) - 1)]}")
