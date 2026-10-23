"""Materials for the Venetian's public interiors (2026-10-23), used by export.py for every material named 'vi-*'.

All textures are original: procedural (numpy, here) or generated with `bitmagic generate image` for this project (the
painted skies, frescoes and casino carpet in build/strip-landmarks/textures/vi-*.png; tools/strip-landmarks/
venetian_textures.py prepares them). Nothing is copied from photographs.

UV modes (the last SPEC column): 'world:S' projects onto the dominant axis plane at S metres per repeat (export.py's
default is 2); 'panel' maps each connected piece (a painted panel, a medallion, a shop display) to the whole image;
'sky:SU:SV' projects from above at SU x SV metres per repeat.
"""
import math
from pathlib import Path
import numpy as np

TEXTURES = Path('build/strip-landmarks/textures')

# name: (hex colour, roughness, metallic, emission strength, kind, uv)
SPEC = {
    # stucco washes for the house fronts, ivory/limestone trims, brick and rustication
    'vi-stucco-cream': ('e6d6b4', .9, 0, 0, 'stucco', 'world:3'),
    'vi-stucco-ochre': ('d6a35a', .9, 0, 0, 'stucco', 'world:3'),
    'vi-stucco-rose': ('d79a8a', .9, 0, 0, 'stucco', 'world:3'),
    'vi-stucco-terracotta': ('bd6a4d', .9, 0, 0, 'stucco', 'world:3'),
    'vi-stucco-pink': ('e2a9a6', .9, 0, 0, 'stucco', 'world:3'),
    'vi-stucco-sage': ('b6b78f', .9, 0, 0, 'stucco', 'world:3'),
    'vi-stucco-grey': ('b8b2a6', .9, 0, 0, 'stucco', 'world:3'),
    'vi-stucco-yellow': ('e7cd87', .9, 0, 0, 'stucco', 'world:3'),
    'vi-stucco-white': ('eee6d6', .9, 0, 0, 'stucco', 'world:3'),
    'vi-limestone': ('e9dfca', .82, 0, 0, 'stone', 'world:1.5'),
    'vi-limestone-shade': ('cfc3aa', .85, 0, 0, 'stone', 'world:1.5'),
    'vi-brick': ('a35a45', .92, 0, 0, 'brick', 'world:1.2'),
    'vi-rustication': ('ddd2bb', .88, 0, 0, 'rustication', 'world:1.8'),
    'vi-roof-tile': ('b26a4c', .86, 0, 0, 'rooftile', 'world:1.6'),
    'vi-chimney': ('cdbfa6', .9, 0, 0, 'stucco', 'world:2'),
    # floors
    'vi-tumbling': ('e7dcc4', .32, 0, 0, 'tumbling', 'world:1.3856:1.2'),   # two cubes across, 0.69 m each (s = 0.4)
    'vi-checker': ('e9dfcc', .3, 0, 0, 'checker', 'world:2.4'),              # the lobby colonnade: cream/oxblood diagonal checker
    'vi-diag-grid': ('ece7dc', .28, 0, 0, 'diaggrid', 'world:3.6'),          # the Waterfall Atrium: white marble, dark diagonal fillets
    'vi-waterfall': ('3b4447', .12, .2, 0, 'waterfall', 'world:2'),          # dark stone behind a sheet of water
    'vi-street-flags': ('d8ccb3', .55, 0, 0, 'flags', 'world:2.4'),
    'vi-square-pavers': ('cfc4ae', .45, 0, 0, 'squarepavers', 'world:4'),
    'vi-marble-cream': ('ebe2cf', .28, 0, 0, 'marble', 'world:2'),
    'vi-marble-rust': ('a2553b', .26, 0, 0, 'marble', 'world:1.5'),
    'vi-marble-green': ('3f5a4a', .26, 0, 0, 'marble', 'world:1.5'),
    'vi-marble-black': ('2c2a29', .24, 0, 0, 'marble', 'world:1.5'),
    'vi-carpet': ('7a2027', .95, 0, 0, 'image', 'world:3.2'),
    # metal, gilt, iron, wood, textiles
    'vi-gilt': ('c9a14b', .34, .85, 0, 'gilt', 'world:.8'),
    'vi-gilt-plain': ('c19a46', .3, .9, 0, 'plain', 'world:2'),
    'vi-bronze': ('8a6a43', .38, .8, 0, 'plain', 'world:2'),
    'vi-iron': ('1d2523', .5, .55, 0, 'plain', 'world:2'),
    'vi-chrome': ('c8cdcf', .18, .95, 0, 'plain', 'world:2'),
    'vi-wood-dark': ('4a2f22', .45, 0, 0, 'wood', 'world:1.2'),
    'vi-wood-honey': ('9a6a3e', .5, 0, 0, 'wood', 'world:1.2'),
    'vi-felt': ('25553a', .95, 0, 0, 'plain', 'world:2'),
    'vi-velvet-red': ('7d1d26', .85, 0, 0, 'plain', 'world:2'),
    'vi-leather': ('3a2622', .6, 0, 0, 'plain', 'world:2'),
    'vi-cloth-white': ('efebe2', .9, 0, 0, 'plain', 'world:2'),
    'vi-umbrella-blue': ('2e4f7a', .85, 0, 0, 'plain', 'world:2'),
    'vi-awning-red': ('9d2e2c', .85, 0, 0, 'stripes', 'world:1.0'),
    'vi-awning-green': ('2f5a43', .85, 0, 0, 'stripes', 'world:1.0'),
    'vi-pole-red': ('a8262c', .5, 0, 0, 'spiral', 'world:1.0'),
    'vi-plant': ('3e5f35', .9, 0, 0, 'plain', 'world:2'),
    'vi-flower-red': ('b8333a', .8, 0, 0, 'plain', 'world:2'),
    'vi-flower-pink': ('d47a9b', .8, 0, 0, 'plain', 'world:2'),
    'vi-soil': ('4a3a2a', .95, 0, 0, 'plain', 'world:2'),
    'vi-shutter-green': ('35523e', .7, 0, 0, 'louver', 'world:.6'),
    'vi-shutter-brown': ('5a3b29', .7, 0, 0, 'louver', 'world:.6'),
    # painted ceilings: vault ornament panels (procedural) and fresco paintings (generated originals)
    'vi-coffer-red': ('8c2b25', .8, 0, .12, 'image', 'panel'),
    'vi-coffer-green': ('35583f', .8, 0, .12, 'image', 'panel'),
    'vi-coffer-cream': ('e3d6b6', .85, 0, 0, 'ornament', 'panel'),
    'vi-fresco-a': ('a0a8b8', .9, 0, .25, 'image', 'panel'),
    'vi-fresco-b': ('a0a8b8', .9, 0, .25, 'image', 'panel'),
    'vi-fresco-oval': ('a0a8b8', .9, 0, .25, 'image', 'panel'),
    'vi-sky-day': ('9ec3e6', 1, 0, 1.15, 'image', 'sky:46:31'),       # 1024 x 690 (venetian_textures.py)
    'vi-sky-dusk': ('4a5a8a', 1, 0, .95, 'image', 'panel'),           # one painting per ceiling (St Mark's)
    # light: lamp glass, shop displays, slot screens, signs
    'vi-lantern': ('ffd9a0', .3, 0, 3.0, 'plain', 'world:2'),
    'vi-lantern-amber': ('ff9e48', .4, 0, 1.3, 'plain', 'world:2'),
    'vi-crystal': ('fff1d8', .1, 0, 2.2, 'plain', 'world:2'),
    'vi-shop-display': ('e9c99a', .7, 0, 1.0, 'display', 'panel'),
    'vi-shop-fashion': ('e9d6b0', .7, 0, .85, 'image', 'panel'),
    'vi-shop-glass-art': ('d9b48a', .7, 0, .85, 'image', 'panel'),
    'vi-shop-masks': ('c9905a', .7, 0, .85, 'image', 'panel'),
    'vi-shop-sweets': ('e9c4c0', .7, 0, .85, 'image', 'panel'),
    'vi-shop-glass': ('c4d0d2', .05, .1, 0, 'glass', 'world:2'),
    'vi-window-dark': ('3a454c', .12, .35, 0, 'plain', 'world:2'),
    'vi-window-lit': ('f1c98a', .5, 0, .8, 'windowlit', 'panel'),
    'vi-slot-screen': ('3a4f9a', .3, 0, 1.0, 'image', 'panel'),          # generated slot screens (venetian_textures.py)
    'vi-slot-topper': ('b01e3a', .35, 0, .9, 'plain', 'world:2'),
    'vi-sign-gold': ('e6c56a', .35, .7, .35, 'plain', 'world:2'),
    'vi-sign-white': ('f4efe2', .5, 0, .6, 'plain', 'world:2'),
    # the casino (venetian_casino.py): slot cabinets, toppers, LED trim, mirrors, escalator metal and rubber, table felt
    'vi-casino-cabinet': ('2a1c28', .3, .6, 0, 'plain', 'world:2'),
    'vi-casino-cabinet-red': ('5c1420', .3, .55, 0, 'plain', 'world:2'),
    'vi-casino-screen-b': ('3a4f9a', .3, 0, 1.0, 'image', 'panel'),
    'vi-casino-topper-blue': ('1f4fc0', .35, 0, .9, 'plain', 'world:2'),
    'vi-casino-topper-gold': ('d8952a', .35, 0, .9, 'plain', 'world:2'),
    'vi-casino-topper-green': ('17805a', .35, 0, .8, 'plain', 'world:2'),
    'vi-casino-led': ('ffe2a8', .4, 0, 2.4, 'plain', 'world:2'),
    'vi-casino-sign-red': ('d8263c', .4, 0, 1.4, 'plain', 'world:2'),
    'vi-casino-mirror': ('96a0a6', .08, .7, 0, 'plain', 'world:2'),
    'vi-casino-steel': ('a9afb2', .32, .9, 0, 'plain', 'world:2'),
    'vi-casino-tread': ('8f9598', .38, .85, 0, 'louver', 'world:.4'),
    'vi-casino-rubber': ('151515', .55, 0, 0, 'plain', 'world:2'),
    'vi-casino-yellow': ('e2b915', .5, 0, 0, 'plain', 'world:2'),
    'vi-casino-felt-blue': ('1d3e6b', .95, 0, 0, 'plain', 'world:2'),
    # the lobby (venetian_lobby.py): the fountain's rose marble, siena marble, the colonnade's warm stucco, painted
    # ornament panels, mirror glass, glowing silk lamp shades
    'vi-lobby-marble-rose': ('c98f78', .25, 0, 0, 'marble', 'world:1.5'),
    'vi-lobby-marble-siena': ('d8b56e', .25, 0, 0, 'marble', 'world:1.5'),
    'vi-lobby-stucco-gold': ('e6d3a6', .85, 0, 0, 'stucco', 'world:3'),
    'vi-lobby-ornament-blue': ('2e4a5e', .8, 0, 0, 'ornament', 'panel'),
    'vi-lobby-ornament-red': ('7e2a26', .8, 0, 0, 'ornament', 'panel'),
    'vi-lobby-mirror': ('c7cdcf', .05, .95, 0, 'plain', 'world:2'),
    'vi-lobby-lampshade': ('f6ddb0', .6, 0, 1.4, 'plain', 'world:2'),
}
# Bitmagic-generated originals (venetian_textures.py writes these; see the module docstring)
IMAGES = {'vi-slot-screen': 'vi-slot-a.png', 'vi-casino-screen-b': 'vi-slot-b.png',
          'vi-coffer-red': 'vi-ornament-red.png', 'vi-coffer-green': 'vi-ornament-green.png', 'vi-shop-fashion': 'vi-shop-fashion.png',
          'vi-shop-glass-art': 'vi-shop-glass-art.png', 'vi-shop-masks': 'vi-shop-masks.png', 'vi-shop-sweets': 'vi-shop-sweets.png',
          'vi-carpet': 'vi-carpet.png', 'vi-fresco-a': 'vi-fresco-a.png', 'vi-fresco-b': 'vi-fresco-b.png',
          'vi-fresco-oval': 'vi-fresco-oval.png', 'vi-sky-day': 'vi-sky-day.png', 'vi-sky-dusk': 'vi-sky-dusk.png'}
COLORS = {k: v[0] for k, v in SPEC.items()}
SMOOTH = {'vi-gilt-plain', 'vi-bronze', 'vi-iron', 'vi-chrome', 'vi-lantern', 'vi-crystal', 'vi-marble-cream', 'vi-marble-rust',
          'vi-marble-green', 'vi-marble-black', 'vi-wood-dark', 'vi-velvet-red', 'vi-leather', 'vi-plant', 'vi-pole-red'}


def _noise(n, cells_amp, seed):
    rng = np.random.default_rng(seed); acc = np.zeros((n, n))
    for cells, amp in cells_amp:
        g = rng.random((cells + 1, cells + 1)); g[-1, :] = g[0, :]; g[:, -1] = g[:, 0]
        t = np.linspace(0, cells, n, endpoint=False); i = t.astype(int); f = t - i; f = f * f * (3 - 2 * f)
        rows = g[i] * (1 - f)[:, None] + g[i + 1] * f[:, None]
        acc += amp * (rows[:, i] * (1 - f)[None, :] + rows[:, i + 1] * f[None, :])
    return acc / sum(a for _, a in cells_amp)


def _veins(u, v, seed, k=1.0):
    rng = np.random.default_rng(seed); phase = rng.uniform(0, 6.28, 4)
    w = np.sin(u * 9 * k + np.sin(v * 5 * k + phase[0]) * 2.4 + np.sin(u * 3 + v * 7 + phase[1]) * 1.6 + phase[2])
    return np.exp(-np.abs(w) * 14)


def albedo_height(k, rgb, n=1024):
    """(albedo HxWx3, height HxW or None) for a procedural kind."""
    kind = SPEC[k][4]
    v, u = np.mgrid[0:n, 0:n] / n
    seed = sum(map(ord, k))
    base = np.ones((n, n, 3)) * rgb
    if kind == 'stucco':
        wash = _noise(n, [(3, 1), (7, .6), (17, .3), (41, .15)], seed) - .5
        trowel = _noise(n, [(60, 1), (120, .5)], seed + 1) - .5
        a = base * (1 + wash[..., None] * .16 + trowel[..., None] * .03)
        return a, trowel * .5 + wash * .2
    if kind in ('stone', 'marble'):
        grain = _noise(n, [(20, 1), (60, .4)], seed) - .5
        veins = _veins(u, v, seed) * (.28 if kind == 'marble' else .06)
        dark = np.array([.45, .42, .40]) if kind == 'marble' and rgb.mean() > .5 else np.array([.9, .86, .8])
        a = base * (1 + grain[..., None] * .06)
        a = a * (1 - veins[..., None]) + dark * veins[..., None] * (1 if kind == 'marble' else .2) * rgb.mean()
        return a, grain * .2
    if kind == 'brick':
        rows = v * 16; col = u * 8 + (np.floor(rows) % 2) * .5
        mortar = (rows % 1 < .07) | (col % 1 < .035)
        brickvar = .10 * np.sin(np.floor(col) * 12.9 + np.floor(rows) * 78.2) + .06 * np.cos(np.floor(col) * 3.1 + np.floor(rows) * 7.7)
        a = base * (1 + brickvar[..., None]) * (1 - .04 * (_noise(n, [(40, 1)], seed) - .5)[..., None])
        a[mortar] = [.78, .74, .66]
        return a, np.where(mortar, 0., 1.)
    if kind == 'rustication':
        rows = v * 4; col = u * 2 + (np.floor(rows) % 2) * .5
        fu = col % 1; fv = rows % 1; edge = np.minimum(np.minimum(fu, 1 - fu) * 2.2, np.minimum(fv, 1 - fv) * 4.4)
        h = np.clip(edge * 6, 0, 1)
        a = base * (1 + .05 * (_noise(n, [(16, 1), (50, .5)], seed) - .5)[..., None]) * (.86 + .14 * h[..., None])
        return a, h
    if kind == 'rooftile':
        fu = (u * 6) % 1; fv = (v * 4) % 1
        a = base * (.9 + .1 * np.cos(fu * math.tau)[..., None]) * (1 - .18 * (fv < .06)[..., None])
        a *= 1 + .08 * (np.sin(np.floor(u * 6) * 9.1 + np.floor(v * 4) * 4.3))[..., None]
        return a, np.cos(fu * math.tau) * .5 + .5 - (fv < .06) * .5
    if kind == 'tumbling':
        # tumbling blocks: pointy-top hexagons (size s) split into three rhombi, a cube seen from above. The tile holds two
        # hexagon columns and one double row: 2 sqrt(3) s by 3 s (the 'world:1.3856:1.2' UV scale for s = 0.4 m).
        x = u * 2 * math.sqrt(3); y = v * 3.0
        q = (math.sqrt(3) / 3 * x - y / 3); r = 2 / 3 * y
        cx_, cz_ = q, r; cy_ = -q - r
        rx, ry, rz = np.round(cx_), np.round(cy_), np.round(cz_)
        dx_, dy_, dz_ = np.abs(rx - cx_), np.abs(ry - cy_), np.abs(rz - cz_)
        fix_x = (dx_ > dy_) & (dx_ > dz_); fix_y = ~fix_x & (dy_ > dz_)
        rx = np.where(fix_x, -ry - rz, rx); ry = np.where(fix_y, -rx - rz, ry); rz = np.where(~fix_x & ~fix_y, -rx - ry, rz)
        hx = math.sqrt(3) * (rx + rz / 2); hy = 1.5 * rz
        ddx = x - hx; ddy = y - hy
        ang = np.degrees(np.arctan2(ddy, ddx)) % 360
        cream = np.array([.91, .87, .78]); rust = np.array([.58, .30, .21]); dark = np.array([.22, .2, .19])
        top = (ang >= 30) & (ang < 150); left = (ang >= 150) & (ang < 270)
        a = np.where(top[..., None], cream, np.where(left[..., None], rust, dark))
        veins = _veins(u * 2, v * 2, seed, 1.4)
        a = a * (1 - .2 * veins[..., None]) + .2 * veins[..., None] * np.array([.95, .93, .9])
        rad = np.hypot(ddx, ddy); w = .035
        seam = np.zeros_like(rad, bool)
        for sp in (30, 150, 270):          # the spokes from the centre to alternate vertices
            t = np.radians(ang - sp); seam |= (np.abs(rad * np.sin(t)) < w) & (np.cos(t) > 0)
        edge = np.maximum(np.maximum(np.abs(ddx), np.abs(ddx * .5 + ddy * math.sqrt(3) / 2)), np.abs(-ddx * .5 + ddy * math.sqrt(3) / 2))
        seam |= edge > math.sqrt(3) / 2 - w
        a[seam] *= .7
        return a, np.where(seam, 0., 1.)
    if kind == 'checker':
        # diagonal checker of cream and oxblood squares (0.85 m) with charcoal fillets
        x = (u + v) * 2; y = (u - v) * 2
        sq = (np.floor(x) + np.floor(y)) % 2 == 0
        a = np.where(sq[..., None], np.array([.9, .86, .77]), np.array([.47, .17, .14]))
        fillet = (np.abs(x - np.round(x)) < .03) | (np.abs(y - np.round(y)) < .03)
        a = a * (1 - .18 * _veins(u * 2, v * 2, seed)[..., None])
        a[fillet] = [.16, .14, .13]
        return a, np.where(fillet, 0., 1.)
    if kind == 'diaggrid':
        x = (u + v) * 2; y = (u - v) * 2
        fillet = (np.abs(x - np.round(x)) < .022) | (np.abs(y - np.round(y)) < .022)
        a = base * (1 - .14 * _veins(u * 3, v * 3, seed)[..., None]) * (1 + .03 * (_noise(n, [(8, 1)], seed) - .5)[..., None])
        a[fillet] = [.13, .13, .14]
        return a, np.where(fillet, 0., 1.)
    if kind == 'waterfall':
        streak = .5 + .5 * np.sin(u * 140 + np.sin(v * 3 + u * 9) * 1.5)
        a = base * (.8 + .35 * streak[..., None] * (.6 + .4 * _noise(n, [(6, 1), (30, .4)], seed)[..., None]))
        return np.clip(a, 0, 1), streak * .3
    if kind == 'flags':
        rows = v * 5; col = u * 3 + (np.floor(rows) % 2) * .37
        joint = (rows % 1 < .018) | (col % 1 < .012)
        tone = .07 * np.sin(np.floor(col) * 7.3 + np.floor(rows) * 5.1)
        a = base * (1 + tone[..., None] + .05 * (_noise(n, [(24, 1), (80, .4)], seed) - .5)[..., None])
        a[joint] *= .62
        return a, np.where(joint, 0., 1.)
    if kind == 'squarepavers':
        # St Mark's: light squares framed by grey bands with dark diamond insets, polished
        fu = (u * 4) % 1; fv = (v * 4) % 1
        band = (fu < .1) | (fv < .1)
        diamond = (np.abs(fu - .55) + np.abs(fv - .55)) < .18
        a = base.copy(); a[band] = [.55, .54, .52]; a[diamond] = [.33, .31, .30]
        veins = _veins(u * 4, v * 4, seed)
        a = a * (1 - .12 * veins[..., None])
        return a, np.where(band, .3, 1.)
    if kind == 'wood':
        grain = .05 * np.sin(u * 180 + np.sin(v * 9) * 2.5) + .03 * np.sin(u * 520 + v)
        return base * (1 + grain[..., None]), grain
    if kind == 'gilt':
        # repeating acanthus-like scroll relief: height drives both the normal map and a darker recess tone
        ang = np.arctan2(v - .5, u - .5); rad = np.hypot(u - .5, v - .5)
        scroll = np.sin(ang * 3 + rad * 22) * np.exp(-((rad - .3) / .18) ** 2)
        leaf = np.sin(u * math.tau * 4) * np.sin(v * math.tau * 2) * .5
        h = np.clip(scroll + leaf * .4, -1, 1)
        a = base * (.82 + .18 * (h * .5 + .5))[..., None]
        return a, h * .5 + .5
    if kind == 'ornament':
        # painted grotesque ornament: a cream/gold arabesque on the panel colour
        ang = np.arctan2(v - .5, u - .5); rad = np.hypot(u - .5, v - .5)
        motif = np.exp(-((rad - (.28 + .07 * np.cos(ang * 6))) / .03) ** 2) + np.exp(-((rad - .12) / .025) ** 2)
        border = (np.minimum(np.minimum(u, 1 - u), np.minimum(v, 1 - v)) < .05)
        a = base * (1 - .05 * (_noise(n, [(10, 1)], seed) - .5)[..., None])
        gold = np.array([.80, .66, .34])
        a = a * (1 - np.clip(motif, 0, 1)[..., None]) + gold * np.clip(motif, 0, 1)[..., None]
        a[border] = gold
        return a, np.clip(motif, 0, 1) + border * .6
    if kind == 'stripes':
        s = (np.floor(u * 6) % 2 == 0)
        a = np.where(s[..., None], base, np.array([.93, .9, .84]))
        return a, None
    if kind == 'spiral':
        s = (np.floor((v * 4 + u) * 2) % 2 == 0)
        return np.where(s[..., None], base, np.array([.95, .93, .9])), None
    if kind == 'louver':
        fv = (v * 16) % 1
        return base * (.82 + .18 * fv)[..., None], fv
    if kind == 'display':
        # an out-of-focus lit shop interior: warm back wall, shelves, merchandise colour blobs
        rng = np.random.default_rng(seed)
        a = np.ones((n, n, 3)) * np.array([.55, .42, .30]) * (.7 + .3 * v)[..., None]
        for shelf in (.28, .52, .76):
            a[np.abs(v - shelf) < .012] = [.25, .2, .16]
        for _ in range(90):
            cx, cy, r = rng.random(), rng.random(), rng.uniform(.015, .05)
            col = rng.choice([[.85, .2, .25], [.95, .85, .7], [.2, .25, .45], [.9, .7, .2], [.3, .3, .3], [.95, .95, .95], [.6, .1, .4]])
            m = np.exp(-(((u - cx) ** 2 + (v - cy) ** 2) / (r * r)))
            a = a * (1 - m[..., None] * .8) + np.array(col) * m[..., None] * .8
        a += np.exp(-((u - .5) ** 2 * 3 + (v - .1) ** 2 * 20))[..., None] * np.array([.35, .3, .2])
        return np.clip(a, 0, 1), None
    if kind == 'windowlit':
        a = np.ones((n, n, 3)) * np.array([.9, .7, .45]) * (.6 + .4 * np.exp(-((u - .5) ** 2 * 4 + (v - .3) ** 2 * 3)))[..., None]
        a[(np.abs(u - .5) < .02) | (np.abs(v - .55) < .015)] = [.2, .15, .1]   # glazing bars
        return a, None
    if kind == 'slotscreen':
        rng = np.random.default_rng(seed)
        a = np.ones((n, n, 3)) * np.array([.08, .1, .25])
        a += np.exp(-((u - .5) ** 2 * 6 + (v - .35) ** 2 * 10))[..., None] * np.array([.5, .3, .6])
        for r_ in range(3):
            for c_ in range(5):
                cx, cy = .14 + c_ * .18, .45 + r_ * .16
                col = rng.choice([[.95, .8, .2], [.9, .2, .3], [.3, .8, .9], [.4, .9, .4], [.95, .5, .9]])
                m = (np.abs(u - cx) < .06) & (np.abs(v - cy) < .055)
                a[m] = col
        return np.clip(a, 0, 1), None
    return base, None


def build(bpy, m, bs, k, linear):
    """Fill the Principled BSDF `bs` of material `m` for vi-* name `k`."""
    hexc, rough, metal, emit, kind, _ = SPEC[k]
    bs.inputs['Roughness'].default_value = rough
    bs.inputs['Metallic'].default_value = metal
    nt = m.node_tree
    if kind == 'glass':
        bs.inputs['Alpha'].default_value = .1; m.diffuse_color = (*linear, .1); m.surface_render_method = 'DITHERED'
        return
    if kind == 'plain':
        if emit:
            bs.inputs['Emission Color'].default_value = (*linear, 1); bs.inputs['Emission Strength'].default_value = emit
        return
    if kind == 'image':
        path = TEXTURES / IMAGES[k]
        im = bpy.data.images.load(str(path.resolve()), check_existing=True); im.pack()
        tex = nt.nodes.new('ShaderNodeTexImage'); tex.image = im
        if SPEC[k][5] == 'panel': tex.extension = 'EXTEND'
        bs.inputs['Base Color'].default_value = (1, 1, 1, 1)
        nt.links.new(tex.outputs['Color'], bs.inputs['Base Color'])
        if emit:
            nt.links.new(tex.outputs['Color'], bs.inputs['Emission Color']); bs.inputs['Emission Strength'].default_value = emit
        return
    rgb = np.array([int(hexc[i:i + 2], 16) / 255 for i in (0, 2, 4)])
    n = 1024 if kind in ('tumbling', 'checker', 'diaggrid', 'squarepavers', 'ornament', 'display', 'slotscreen') else 512
    albedo, height = albedo_height(k, rgb, n)
    # colour images are sRGB: write the sRGB values as they are (export.py's own pattern images do the same)
    pix = np.ones((n, n, 4), dtype=np.float32); pix[:, :, :3] = np.clip(albedo, 0, 1)
    im = bpy.data.images.new('Original Venetian ' + k, width=n, height=n)
    im.pixels.foreach_set(pix.flatten()); im.pack()
    tex = nt.nodes.new('ShaderNodeTexImage'); tex.image = im
    bs.inputs['Base Color'].default_value = (1, 1, 1, 1)
    nt.links.new(tex.outputs['Color'], bs.inputs['Base Color'])
    if emit:
        nt.links.new(tex.outputs['Color'], bs.inputs['Emission Color']); bs.inputs['Emission Strength'].default_value = emit
    if height is not None:
        h = np.asarray(height, dtype=np.float64)
        dy, dx = np.gradient(h)
        strength = {'checker': 1.0, 'diaggrid': 1.0, 'waterfall': 1.5, 'brick': 2.5, 'rustication': 3.0, 'tumbling': 1.2, 'flags': 2.0, 'squarepavers': 1.5, 'gilt': 4.0,
                    'ornament': 1.2, 'stucco': 6.0, 'rooftile': 2.5, 'louver': 1.5, 'wood': 1.0}.get(kind, 1.0) * n / 1024
        nx = -dx * strength; ny = -dy * strength; nz = np.ones_like(nx)
        L = np.sqrt(nx * nx + ny * ny + nz * nz)
        npix = np.ones((n, n, 4), dtype=np.float32)
        npix[:, :, 0] = nx / L * .5 + .5; npix[:, :, 1] = ny / L * .5 + .5; npix[:, :, 2] = nz / L * .5 + .5
        ni = bpy.data.images.new('Original Venetian normal ' + k, width=n, height=n)
        ni.colorspace_settings.name = 'Non-Color'; ni.pixels.foreach_set(npix.flatten()); ni.pack()
        nt2 = nt.nodes.new('ShaderNodeTexImage'); nt2.image = ni
        nm = nt.nodes.new('ShaderNodeNormalMap'); nm.inputs['Strength'].default_value = .8
        nt.links.new(nt2.outputs['Color'], nm.inputs['Color']); nt.links.new(nm.outputs['Normal'], bs.inputs['Normal'])


def uvs(me, k):
    """Give mesh `me` (material `k`) its 'Metres' UVs, and smooth its curved surfaces (sharp at 40 degrees and above)."""
    me.validate(clean_customdata=False)        # drop duplicate and degenerate faces left by merged coordinates
    for poly in me.polygons: poly.use_smooth = True
    me.set_sharp_from_angle(angle=math.radians(40))
    uv = me.uv_layers.new(name='Metres')
    mode = SPEC[k][5]
    if mode == 'panel':
        panel_uvs(me, uv); return
    kind, *nums = mode.split(':'); su = float(nums[0]); sv = float(nums[1]) if len(nums) > 1 else su
    for poly in me.polygons:
        axis = max(range(3), key=lambda i: abs(poly.normal[i]))
        for li in poly.loop_indices:
            p = me.vertices[me.loops[li].vertex_index].co
            if kind == 'sky': uv.data[li].uv = (p.x / su, p.y / sv)
            else:
                a, b = world_uv(p, axis, 1.0); uv.data[li].uv = (a / su, b / sv)


def panel_uvs(me, uv):
    """'panel': every connected piece of the mesh shows the whole image once. The piece is projected on the plane of its
    area-weighted mean normal (a curved vault panel or a shallow dish counts as one plane), with u along its longer side."""
    parent = list(range(len(me.vertices)))
    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]; a = parent[a]
        return a
    for poly in me.polygons:
        vs = list(poly.vertices)
        for a in vs[1:]:
            ra, rb = find(vs[0]), find(a)
            if ra != rb: parent[rb] = ra
    groups = {}
    for poly in me.polygons:
        groups.setdefault(find(poly.vertices[0]), []).append(poly)
    for polys in groups.values():
        n = np.zeros(3)
        for poly in polys: n += np.array(poly.normal) * poly.area
        if np.linalg.norm(n) < 1e-9: n = np.array(polys[0].normal)
        n /= max(1e-9, np.linalg.norm(n))
        if abs(n[2]) > .7:
            ax_u = np.array([1., 0, 0]); ax_v = np.array([0, 1., 0])
        else:
            ax_u = np.cross([0, 0, 1.], n); ax_u /= np.linalg.norm(ax_u); ax_v = np.array([0, 0, 1.])
        pts = []
        for poly in polys:
            for li in poly.loop_indices:
                co = np.array(me.vertices[me.loops[li].vertex_index].co); pts.append((li, float(ax_u @ co), float(ax_v @ co)))
        us = [p[1] for p in pts]; vs = [p[2] for p in pts]
        u0, u1, v0, v1 = min(us), max(us), min(vs), max(vs)
        swap = abs(n[2]) > .7 and (v1 - v0) > (u1 - u0) * 1.05
        for li, a, b in pts:
            fu = (a - u0) / max(1e-6, u1 - u0); fv = (b - v0) / max(1e-6, v1 - v0)
            uv.data[li].uv = (fv, 1 - fu) if swap else (fu, fv)


def world_uv(p, axis, scale):
    return (p.y / scale, p.z / scale) if axis == 0 else (p.x / scale, p.z / scale) if axis == 1 else (p.x / scale, p.y / scale)
