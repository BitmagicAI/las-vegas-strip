#!/usr/bin/env python3
"""How a recorded (or planned) camera moves, from the film director's poses (x, y, z, dir x, dir y, dir z per 1/60 s):
python3 tools/film/camera-check.py <take> [<take> ...] [--from S --to S] [--plan]

For each take: the view's turn rate (deg/s, smoothed over 0.1 s), its angular acceleration, how often the turn direction
reverses (the camera "hunting" left and right), how steeply it looks down (straight-down views spin under lookAt), and
the camera speed. Flags:
  TURN    turn rate above 70 deg/s       (a whip pan)
  JERK    angular acceleration above 500 deg/s^2 (a sudden turn)
  HUNT    the yaw rate changes sign more than twice within 2 s while turning faster than 8 deg/s (left-right searching)
  DOWN    looking more than 70 degrees down (heading becomes unstable)
--plan computes the poses of world-anchored camera tracks straight from tools/film/takes/<take>.json (no recording).
"""
import json, math, os, sys
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RECS = os.path.join(ROOT, '.bitmagic/trailer/recordings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def planned(take):
    from clearance import cr
    t = json.load(open(os.path.join(ROOT, 'tools/film/takes', take + '.json')))
    out = []
    for seg in t.get('camera', []):
        if seg.get('anchor', 'world') != 'world': continue
        keys = seg['keys']; n = int(keys[-1]['t'] * 60)
        lk = [{'t': k['t'], 'pos': k['look']} for k in keys]
        for i in range(n + 1):
            p = cr(keys, i / 60); l = cr(lk, i / 60); d = l - p; d /= np.linalg.norm(d)
            out.append([*p, *d])
    return np.array(out)

def cut_times(take):
    """Segment starts of a take's camera track: cuts, where a jump is intended."""
    base = take[:-3] if take.endswith('-rt') else take
    f = os.path.join(ROOT, 'tools/film/takes', base + '.json')
    if not os.path.exists(f): return []
    return [c['from'] for c in json.load(open(f)).get('camera', [])[1:]]

def analyse(name, P, t0=0.0, t1=None, cuts=()):
    if t1 is not None: P = P[int(t0 * 60):int(t1 * 60)]
    elif t0: P = P[int(t0 * 60):]
    pos, d = P[:, :3], P[:, 3:6] / np.linalg.norm(P[:, 3:6], axis=1)[:, None]
    yaw = np.unwrap(np.arctan2(d[:, 0], -d[:, 2])); pitch = np.arcsin(np.clip(d[:, 1], -1, 1))
    k = 6   # 0.1 s smoothing
    def sm(x): return np.convolve(x, np.ones(k) / k, mode='same')
    ang = np.degrees(np.arccos(np.clip((d[1:] * d[:-1]).sum(1), -1, 1))) * 60
    rate = sm(np.concatenate([[0], ang]))
    yr = sm(np.degrees(np.gradient(yaw)) * 60)
    acc = np.abs(np.gradient(sm(rate))) * 60
    speed = np.linalg.norm(np.diff(pos, axis=0), axis=1) * 60
    flags = []
    def spans(mask, label, values, unit):
        i = 0
        while i < len(mask):
            if mask[i]:
                j = i
                while j + 1 < len(mask) and mask[j + 1]: j += 1
                if j - i >= 2: flags.append(f'{label} {(i) / 60 + t0:.1f}-{(j) / 60 + t0:.1f} s (max {values[i:j + 1].max():.0f} {unit})')
                i = j + 1
            else: i += 1
    # ignore the 0.2 s around each cut between camera segments
    tt = np.arange(len(P)) / 60 + t0; near = np.zeros(len(P), bool)
    for c in cuts: near |= np.abs(tt - c) < 0.2
    rate = np.where(near, 0, rate); acc = np.where(near, 0, acc)
    spans(rate > 70, 'TURN', rate, 'deg/s')
    spans(acc > 500, 'JERK', acc, 'deg/s2')
    spans(np.degrees(-pitch) > 70, 'DOWN', np.degrees(-pitch), 'deg')
    # hunting: sign changes of a significant yaw rate inside 2 s windows
    s = np.sign(np.where(np.abs(yr) > 8, yr, 0)); ch = np.where((s[1:] * s[:-1]) < 0)[0]
    hunts = [c for c in ch if ((ch >= c) & (ch < c + 120)).sum() >= 3]
    if hunts:
        groups = [hunts[0]]
        for c in hunts[1:]:
            if c - groups[-1] > 120: groups.append(c)
        flags += [f'HUNT {g / 60 + t0:.1f} s' for g in groups]
    print(f'{name}: {len(P) / 60:.1f} s, turn rate median {np.median(rate):.0f} / p95 {np.percentile(rate, 95):.0f} / max {rate.max():.0f} deg/s,'
          f' ang.acc p95 {np.percentile(acc, 95):.0f} deg/s2, speed median {np.median(speed):.1f} m/s, steepest down {np.degrees(-pitch).max():.0f} deg')
    for f in flags[:14]: print('   ', f)
    if len(flags) > 14: print(f'    ... {len(flags) - 14} more')
    return flags

if __name__ == '__main__':
    a = sys.argv[1:]
    t0 = float(a[a.index('--from') + 1]) if '--from' in a else 0.0
    t1 = float(a[a.index('--to') + 1]) if '--to' in a else None
    skip = {i + 1 for i, x in enumerate(a) if x in ('--from', '--to')}
    takes = [x for i, x in enumerate(a) if not x.startswith('--') and i not in skip]
    bad = False
    for t in takes:
        P = planned(t) if '--plan' in a else np.array(json.load(open(os.path.join(RECS, t, 'poses.json')))).reshape(-1, 6)
        bad |= bool(analyse(t, P, t0, t1, cut_times(t)))
    sys.exit(1 if bad else 0)
