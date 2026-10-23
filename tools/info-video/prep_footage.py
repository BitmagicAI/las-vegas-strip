"""Footage frames for the story page: each recording's capture.mp4 (2880x1620 H.264 from tools/film/record.mjs) decoded to
JPEG frames in .bitmagic/info-video/footage/<take>/fNNNNN.jpg, at 1920x1080 (preview) or 2880x1620 (--final, q 2).
Writes build/info-video/page/data/footage.json. python3 tools/info-video/prep_footage.py [--final] [take ...]"""
import json, os, subprocess, sys
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
REC = os.path.join(ROOT, '.bitmagic/trailer/recordings')
FINAL = '--final' in sys.argv
TAKES = [a for a in sys.argv[1:] if not a.startswith('--')] or ['info-establish-info', 'info-boxmatch-info', 'info-bellagio-info', 'info-north-info', 'info-south-info', 'tour-info', 'info-night-info', 'info-rain-info',
                                                               'info-shoppes-info', 'info-casino-info']
base = '.bitmagic/info-video/footage' + ('-final' if FINAL else '') + '/'
idx_p = os.path.join(ROOT, 'build/info-video/page/data/footage.json')
idx = json.load(open(idx_p)) if os.path.exists(idx_p) else {}
for take in TAKES:
    src = os.path.join(REC, take, 'capture.mp4')
    if not os.path.exists(src): print('missing', src); continue
    out = os.path.join(ROOT, base, take); os.makedirs(out, exist_ok=True)
    scale = '2880:1620' if FINAL else '1920:1080'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-vf', f'scale={scale}:flags=lanczos', '-q:v', '2' if FINAL else '3', '-start_number', '0',
                    os.path.join(out, 'f%05d.jpg')], check=True)
    n = len([f for f in os.listdir(out) if f.endswith('.jpg')])
    idx[take] = dict(dir=base + take + '/', frames=n, fps=60)
    print(take, n, 'frames')
json.dump(idx, open(idx_p, 'w'), indent=1)
