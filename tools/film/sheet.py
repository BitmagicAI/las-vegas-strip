#!/usr/bin/env python3
"""Contact sheet of a recorded take: python3 tools/film/sheet.py <take> [cols=5] [rows=3] → build/film/sheets/<take>.png (time labels in s)."""
import glob, os, sys
from PIL import Image, ImageDraw
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
take = sys.argv[1]; cols = int(sys.argv[2]) if len(sys.argv) > 2 else 5; rows = int(sys.argv[3]) if len(sys.argv) > 3 else 3
fs = sorted(glob.glob(os.path.join(ROOT, '.bitmagic/trailer/recordings', take, '*.png')))
n = cols * rows; W, H = 400, 225
out = Image.new('RGB', (W * cols, H * rows)); d = ImageDraw.Draw(out)
for k in range(n):
    i = min(len(fs) - 1, round(k * (len(fs) - 1) / (n - 1)))
    out.paste(Image.open(fs[i]).convert('RGB').resize((W, H)), ((k % cols) * W, (k // cols) * H))
    d.text(((k % cols) * W + 6, (k // cols) * H + 4), f'{i / 60:.1f}s', fill='yellow')
os.makedirs(os.path.join(ROOT, 'build/film/sheets'), exist_ok=True)
p = os.path.join(ROOT, 'build/film/sheets', take + '.png'); out.save(p); print(p, len(fs), 'frames')
