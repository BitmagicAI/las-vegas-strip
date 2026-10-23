#!/usr/bin/env python3
"""Pack the CC0 PBR sets in .bitmagic/pbr-sources/<set>/{diff,nor,arm}.jpg (Poly Haven 2K downloads, manifest.json there) into three vertical strips (one 1024x1024 layer per set, in
SETS order) for the game's detail texture arrays: build/pbr/strips/{albedo,normal,arm}.webp, plus build/pbr/strips/sets.json
with each set's mean albedo (linear) used to turn the scan into a colour modulation around 1.

The albedo is flattened first: its low frequencies (stains, dirt gradients, lighting falloff across the photo, anything
wider than about a sixth of the tile) are divided out in linear light with a wrap-around Gaussian, so a tile repeated over
a wall shows its joints, grain and block-to-block tone but no repeating dark bands.
Run: python3 tools/pbr/pack-strips.py"""
import json, os
import numpy as np
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SETS = ['clean_asphalt','concrete_pavement','concrete_floor_02','white_stucco','concrete_wall_008','sandstone_blocks_08','marble_01',
        'brick_wall_02','metal_plate','aerial_grass_rock','gravel_floor_02','clay_roof_tiles_02','bitumen','dry_ground_01','granite_tile_03']
S = 1024
out = os.path.join(ROOT, 'build/pbr/strips'); os.makedirs(out, exist_ok=True)
strips = {k: Image.new('RGB', (S, S * len(SETS))) for k in ('albedo', 'normal', 'arm')}
means = []
def lin(c): c /= 255; return c / 12.92 if c <= .04045 else ((c + .055) / 1.055) ** 2.4
def to_lin(a): a = a / 255.0; return np.where(a <= .04045, a / 12.92, ((a + .055) / 1.055) ** 2.4)
def to_srgb(a): a = np.clip(a, 0, 1); return np.where(a <= .0031308, a * 12.92, 1.055 * a ** (1 / 2.4) - .055) * 255
def flatten(im, sigma=S / 6, keep=.15):
    """Divide out the albedo's low frequencies (periodic Gaussian via FFT), keeping `keep` of them."""
    a = to_lin(np.asarray(im, dtype=np.float64))
    f = np.fft.fftfreq(S)[:, None] ** 2 + np.fft.fftfreq(S)[None, :] ** 2
    g = np.exp(-2 * (np.pi * sigma) ** 2 * f)
    low = np.stack([np.real(np.fft.ifft2(np.fft.fft2(a[..., c]) * g)) for c in range(3)], -1)
    mean = a.reshape(-1, 3).mean(0)
    out = a * (mean / np.maximum(low, 1e-4)) ** (1 - keep)
    return Image.fromarray(to_srgb(out).round().astype(np.uint8))
for i, s in enumerate(SETS):
    for k, f in (('albedo', 'diff'), ('normal', 'nor'), ('arm', 'arm')):
        im = Image.open(os.path.join(ROOT, f'.bitmagic/pbr-sources/{s}/{f}.jpg')).convert('RGB').resize((S, S), Image.LANCZOS)
        if k == 'albedo': im = flatten(im)
        strips[k].paste(im, (0, i * S))
        if k == 'albedo':
            small = im.resize((64, 64), Image.BOX); px = list(small.getdata())
            means.append([round(sum(lin(p[c]) for p in px) / len(px), 5) for c in range(3)])
for k, im in strips.items():
    im.save(os.path.join(out, f'{k}.webp'), quality=92, method=6)
json.dump({'size': S, 'sets': SETS, 'meanLinear': means}, open(os.path.join(out, 'sets.json'), 'w'), indent=1)
print('packed', len(SETS), 'sets;', {k: round(os.path.getsize(os.path.join(out, f'{k}.webp')) / 1e6, 1) for k in strips}, 'MB')
