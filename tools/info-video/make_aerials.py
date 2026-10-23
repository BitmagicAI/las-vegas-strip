#!/usr/bin/env python3
"""Aerial film takes for the info video (tools/film/takes/info-*.json), recorded with tools/film/record.mjs.
Camera keys use the film director's own interpolation (Catmull-Rom keys every 0.2 s, two-key segments eased smoothstep),
so story.js can rebuild a matching camera for the box-city overlay (info-boxmatch). World metres: X east, Y up, Z south.
Check every take with tools/film/clearance.py before recording.
python3 tools/info-video/make_aerials.py"""
import json, math, os
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUT = os.path.join(ROOT, 'tools/film/takes')


def _cr(p0, p1, p2, p3, u):
    # centripetal Catmull-Rom between p1 and p2
    def tj(ti, a, b): return ti + max(1e-6, math.dist(a, b)) ** 0.5
    t0 = 0; t1 = tj(t0, p0, p1); t2 = tj(t1, p1, p2); t3 = tj(t2, p2, p3); t = t1 + (t2 - t1) * u
    def L(a, b, ta, tb): return [(tb - t) / (tb - ta) * x + (t - ta) / (tb - ta) * y for x, y in zip(a, b)]
    A1 = L(p0, p1, t0, t1); A2 = L(p1, p2, t1, t2); A3 = L(p2, p3, t2, t3)
    B1 = L(A1, A2, t0, t2); B2 = L(A2, A3, t1, t3)
    return L(B1, B2, t1, t2)


def flight(points, speed, ramp=1.5, dt=0.2, fov=50):
    """Constant-speed flight through points [((x, y, z), look)] (look: a world target, eased between points)."""
    P = [list(map(float, p)) for p, _ in points]; looks = [list(map(float, l)) for _, l in points]
    ext = [[2 * a - b for a, b in zip(P[0], P[1])]] + P + [[2 * a - b for a, b in zip(P[-1], P[-2])]]
    dense, owner = [], []
    for i in range(len(P) - 1):
        for k in range(60):
            dense.append(_cr(ext[i], ext[i + 1], ext[i + 2], ext[i + 3], k / 60)); owner.append(i + k / 60)
    dense.append(P[-1]); owner.append(len(P) - 1)
    S = [0.0]
    for a, b in zip(dense, dense[1:]): S.append(S[-1] + math.dist(a, b))
    total = S[-1]

    def at_s(s):
        s = min(max(s, 0), total); j = 0
        while j < len(S) - 2 and S[j + 1] < s: j += 1
        f = (s - S[j]) / max(1e-9, S[j + 1] - S[j])
        return [a + (b - a) * f for a, b in zip(dense[j], dense[j + 1])], owner[j] + (owner[j + 1] - owner[j]) * f
    T = total / speed + ramp
    n = int(T / dt) + 1; vel = []
    for i in range(n + 1):
        t = i * dt; e = max(0, min(1, t / ramp, (T - t) / ramp)); vel.append(e * e * (3 - 2 * e))
    acc = [0.0]
    for v0, v1 in zip(vel, vel[1:]): acc.append(acc[-1] + (v0 + v1) / 2 * dt)
    keys = []
    for i in range(n + 1):
        pos, u = at_s(acc[i] / acc[-1] * total)
        i0 = min(int(u), len(P) - 2); f = u - i0; f = f * f * (3 - 2 * f)
        look = [a + (b - a) * f for a, b in zip(looks[i0], looks[i0 + 1])]
        keys.append({'t': round(i * dt, 3), 'pos': [round(c, 2) for c in pos], 'look': [round(c, 2) for c in look], 'roll': 0, 'fov': fov})
    return keys, round(n * dt, 2), total


def dolly(a, b, look_a, look_b, seconds, fov=50):
    """Two keys: the director eases them (smoothstep), which story.js reproduces exactly."""
    return [{'t': 0, 'pos': a, 'look': look_a, 'roll': 0, 'fov': fov}, {'t': seconds, 'pos': b, 'look': look_b, 'roll': 0, 'fov': fov}], seconds


def write(name, keys, seconds, at, warm=8, look=None):
    take = {'name': name, 'subframes': 1, 'seconds': seconds, 'maxSeconds': seconds + 6,
            'start': {'at': list(at), 'dir': [0, -1], 'view': 'first', 'warm': warm},
            'steps': [{'wait': seconds}], 'camera': [{'from': 0, 'to': seconds, 'focus': 'camera', 'keys': keys}]}
    if look:   # time of day and weather (Film take.look: src/work/film/FilmLook.ts, presets in ScenePreset.ts)
        take['look'] = look
    with open(os.path.join(OUT, name + '.json'), 'w') as f: json.dump(take, f, indent=1)
    print(name, seconds, 's', len(keys), 'keys')


# 1. Establishing: high over the south-east, gliding north with the central Strip ahead (Cosmopolitan, Bellagio, Paris).
# (looking north-north-west: westward views show the map's edge at the horizon 3 km away; northward the haze hides it)
k, s, L = flight([((480, 420, 2300), (-150, 40, 300)), ((300, 300, 1450), (-150, 40, 300)), ((160, 235, 950), (-160, 40, 260))], speed=55, fov=45)
write('info-establish', k, s, (300, 0.5, 900))
# 2. Box-city match move: a slow eased dolly the box-city render repeats with the same camera.
# steep enough (about 34 deg down, fov 45) that the top of the frame meets the ground inside the map
k, s = dolly([420, 820, 1500], [330, 760, 1150], [-60, 0, 380], [-80, 0, 250], 12.0, fov=45)
write('info-boxmatch', k, s, (300, 0.5, 900))
# 3. The Google Earth angle on the Bellagio (owner's reference): from over the Strip looking west, pushing in.
k, s = dolly([90, 300, 365], [-40, 250, 345], [-330, 60, 348], [-330, 62, 348], 9.0, fov=37)
write('info-bellagio', k, s, (-60, 0.5, 300))
# 4. North Strip toward the STRAT, above the towers (Resorts World 205 m, Fontainebleau ~224 m).
k, s, L = flight([((430, 300, -1050), (1574, 230, -3497)), ((800, 310, -1800), (1574, 240, -3497)), ((1120, 320, -2450), (1574, 250, -3497))], speed=70)
write('info-north', k, s, (700, 0.5, -1700))
# 5. South Strip: over MGM Grand toward the Luxor pyramid and Mandalay Bay.
k, s, L = flight([((520, 260, 900), (-261, 60, 2278)), ((420, 240, 1500), (-261, 60, 2278)), ((300, 220, 2050), (-200, 70, 2600))], speed=55)
write('info-south', k, s, (200, 0.5, 1600))

# Any hour, any weather (line 14b): the same city under the film presets, no car and no crowd (take.look).
NIGHT = {'preset': 'neon'}
RAIN = {'preset': 'storm', 'overrides': {'weather': 'rain', 'rain': 0.9, 'wetness': 1, 'neon': 4}}
# 6. Night over the central Strip: the establishing glide at night (lit windows, Eiffel and Bellagio floods).
k, s = dolly([330, 300, 1300], [200, 215, 930], [-120, 40, 330], [-150, 40, 290], 10.0, fov=45)
write('info-night', k, s, (300, 0.5, 900), look=NIGHT)
# 7. Rain on the Boulevard at night: low along the Strip past Planet Hollywood toward Paris and the Bellagio
# (the street-light sites line this stretch, src/work/film/SceneStreetLights.ts).
k, s = dolly([8, 7, 790], [6, 7.5, 640], [0, 5, 520], [-12, 8, 430], 10.0, fov=55)
write('info-rain', k, s, (8, 0.5, 700), look={**RAIN, 'area': [-140, 380, 140, 900]})
# 8. The Bellagio's floodlit facade across the lake, in the rain.
k, s = dolly([-60, 38, 520], [-95, 34, 470], [-250, 70, 330], [-270, 72, 320], 10.0, fov=45)
write('info-rain-lake', k, s, (-60, 0.5, 470), look={**RAIN, 'area': [-300, 300, 20, 560]})
