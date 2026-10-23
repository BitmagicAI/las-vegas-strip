"""Prepare the Venetian interiors' generated textures (2026-10-23) for export.py.

The originals were made for this project with `bitmagic generate image` (prompts and URLs in
build/venetian-interiors/generated/*.json) and are kept as WebP next to them. This writes PNGs into
build/strip-landmarks/textures/: the day sky and the carpet made seamless (offset cross-fade), the
day sky cropped clear of the painted cornice in its lower right; the dusk sky and frescoes as made.

Run with any Python that has Pillow and numpy: python3 tools/strip-landmarks/venetian_textures.py
"""
from pathlib import Path
import numpy as np
from PIL import Image

SRC = Path('build/venetian-interiors/generated')
SHOP_CROPS = {'vi-shop-fashion': (75, 101, 947, 892), 'vi-shop-glass-art': (67, 45, 956, 945), 'vi-shop-masks': (120, 46, 967, 925),
              'vi-shop-sweets': (92, 33, 943, 965)}
OUT = Path('build/strip-landmarks/textures')


def seamless(a, border=.22):
    """Make an image tile: cross-fade it with itself shifted by half, one axis at a time (a shift in both at once leaves the
    shifted copy's own seams showing near the edges). Each shifted copy's seam lands mid-image, where its weight is zero."""
    for axis in (1, 0):
        n = a.shape[axis]
        d = np.minimum(np.arange(n), n - 1 - np.arange(n)) / (n * border)
        w = np.clip(d, 0, 1) ** 1.5
        w = w[None, :, None] if axis == 1 else w[:, None, None]
        a = a * w + np.roll(a, n // 2, axis) * (1 - w)
    return a


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    day = np.asarray(Image.open(SRC / 'vi-sky-day.webp').convert('RGB'), float)
    for r in (133, 510):                      # paint out the joints: interpolate across a 10 px band
        t = np.linspace(0, 1, 10)[:, None, None]; day[r - 4:r + 6] = day[r - 5] * (1 - t) + day[r + 6] * t
    t = np.linspace(0, 1, 10)[None, :, None]; day[:, 506:516] = day[:, 505:506] * (1 - t) + day[:, 516:517] * t
    day = seamless(day[:690], .25)            # above the cornice
    Image.fromarray(np.clip(day, 0, 255).astype(np.uint8)).save(OUT / 'vi-sky-day.png')
    carpet = np.asarray(Image.open(SRC / 'vi-carpet.webp').convert('RGB'), float)
    Image.fromarray(np.clip(seamless(carpet, .12), 0, 255).astype(np.uint8)).save(OUT / 'vi-carpet.png')
    for n in ['vi-sky-dusk', 'vi-fresco-a', 'vi-fresco-b', 'vi-fresco-oval', 'vi-ornament-red', 'vi-ornament-green']:
        Image.open(SRC / f'{n}.webp').convert('RGB').save(OUT / f'{n}.png')
    # shop windows: the generator painted a window frame round each interior; keep the interior only
    for n, crop in SHOP_CROPS.items():
        Image.open(SRC / f'{n}.webp').convert('RGB').crop(crop).resize((768, 768), Image.LANCZOS).save(OUT / f'{n}.png')
    for n in ['vi-slot-a', 'vi-slot-b']:              # slot machine screens
        Image.open(SRC / f'{n}.webp').convert('RGB').resize((512, 512), Image.LANCZOS).save(OUT / f'{n}.png')
    print('wrote', sorted(p.name for p in OUT.glob('vi-*.png')))


if __name__ == '__main__':
    main()
