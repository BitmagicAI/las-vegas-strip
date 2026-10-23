#!/usr/bin/env python3
"""Frame-by-frame sanity of a recorded take (or any video): black frames, freezes and flashes.
python3 tools/film/frame-check.py <take | video.mp4> [--fps 60]

Decodes the take's capture.mp4 (or the given video) at 160x90 grey and reports, per frame: brightness and the mean change
from the previous frame. Flags:
  BLACK   brightness under 6 (of 255)
  FREEZE  a frame identical to the one before (change under 0.05) while the take's camera is moving (poses.json), i.e. the
          game was held (a streaming load) and the recorder repeated the frame
  FLASH   a change over 4x the median of the surrounding second and above 18: a jump (a wrong camera, a pop)
"""
import json, os, subprocess, sys
import numpy as np
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
a = sys.argv[1:]; src = a[0]; fps = float(a[a.index('--fps') + 1]) if '--fps' in a else 60.0
video = src if src.endswith('.mp4') else os.path.join(ROOT, '.bitmagic/trailer/recordings', src, 'capture.mp4')
poses = None
if not src.endswith('.mp4'):
    pp = os.path.join(ROOT, '.bitmagic/trailer/recordings', src, 'poses.json')
    if os.path.exists(pp): poses = np.array(json.load(open(pp)), dtype=np.float64).reshape(-1, 6)
W, H = 160, 90
raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', video, '-vf', f'scale={W}:{H},format=gray', '-f', 'rawvideo', '-'], capture_output=True, check=True).stdout
F = np.frombuffer(raw, np.uint8).reshape(-1, H, W).astype(np.float32)
bright = F.mean((1, 2)); diff = np.concatenate([[0], np.abs(np.diff(F, axis=0)).mean((1, 2))])
moving = np.ones(len(F), bool)
if poses is not None:
    sp = np.concatenate([[0], np.linalg.norm(np.diff(poses[:, :3], axis=0), axis=1) * fps])
    moving[:] = False; n = min(len(F), len(sp)); moving[:n] = sp[:n] > 0.3
flags = []
for i in range(len(F)):
    lo, hi = max(0, i - int(fps / 2)), min(len(F), i + int(fps / 2)); med = float(np.median(diff[lo:hi])) or 0.01
    if bright[i] < 6: flags.append((i, 'BLACK', bright[i]))
    elif i and diff[i] < 0.05 and moving[i]: flags.append((i, 'FREEZE', diff[i]))
    elif diff[i] > 18 and diff[i] > 4 * med: flags.append((i, 'FLASH', diff[i]))
print(f'{os.path.basename(video)}: {len(F)} frames ({len(F) / fps:.1f} s), brightness {bright.min():.0f}-{bright.max():.0f}, '
      f'median change {np.median(diff):.2f}')
runs, cur = [], None
for i, kind, v in flags:
    if cur and cur[1] == kind and i == cur[2] + 1: cur[2] = i; cur[3] = max(cur[3], v)
    else:
        if cur: runs.append(cur)
        cur = [i, kind, i, v]
if cur: runs.append(cur)
for s, kind, e, v in runs: print(f'  {kind:6s} frames {s}-{e} ({s / fps:.2f}-{(e + 1) / fps:.2f} s)  {v:.2f}')
if not runs: print('  no black frames, freezes or flashes')
