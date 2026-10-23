"""A complete small level — a two-room hut with a porch and a walled courtyard — exercising every
bmlevel helper once. It is the reference a level script starts from, and the fixture the tests
run through the null backend.

    "$BLENDER" -b --python tools/blender-level/example_level.py -- --out build/level
    python3 tools/blender-level/example_level.py --dry-run          # counts and JSON only
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from bmlevel import (  # noqa: E402
    box, context, decor, door, export, glazing, lamp, landmark, link, mat, prism, slab, spawn, spot, stairs, text, volume, wall,
)


def build() -> None:
    mat('plaster', (0.82, 0.78, 0.7))
    mat('timber', (0.45, 0.3, 0.16), roughness=0.7)
    mat('stone', (0.42, 0.42, 0.4), roughness=0.9)
    mat('deck', (0.3, 0.25, 0.18), roughness=0.8)
    mat('glass_pane', (0.55, 0.75, 0.9), alpha=0.25)
    mat('emissive_lamp', (1.0, 0.85, 0.55), glow=4.0)
    mat('brass', (0.75, 0.6, 0.3), metal=0.8, roughness=0.35)

    with context('hut', origin=(0, 0, 0)):
        # Two rooms, 8 x 6 m and 5 x 6 m, sharing an internal wall with a doorway.
        slab('hut floor', (2.5, 0), (13, 6), 'deck', y=0.0, thickness=0.4)
        slab('hut ceiling', (2.5, 0), (13, 6), 'timber', y=3.2, thickness=0.2)
        wall('west', (-4, -3), (-4, 3), 3.0, 'plaster')
        wall('east', (9, -3), (9, 3), 3.0, 'plaster')
        wall('south', (-4, 3), (9, 3), 3.0, 'plaster')
        wall('north', (-4, -3), (9, -3), 3.0, 'plaster', opening={'at': 4, 'width': 1.4, 'height': 2.2})
        door('front', (0, 0, -3), yaw=0, jamb='timber')
        wall('partition', (4, -3), (4, 3), 3.0, 'plaster', opening={'at': 3, 'width': 1.2, 'height': 2.1})
        door('inner', (4, 0, 0), yaw=1.5707963, width=1.2, height=2.1, animation='hinge', jamb='timber')
        glazing('south window', (5, 3.01), (8, 3.01), 3.0, 'glass_pane', 'plaster', thickness=0.28)
        box('table', (-2.2, 0.4, 1.6), (1.6, 0.8, 0.9), 'timber', group='environment', bevel=0.02)  # off the walk line: the audit marches room centre to door
        decor('rug', (0, 0.006, 0.5), (3, 0.012, 2.4), 'stone')
        decor('lamp shade', (0, 2.9, 0), (0.5, 0.15, 0.5), 'emissive_lamp')
        lamp('hut lamp', (0, 2.7, 0), '#ffd9a0', intensity=10, distance=12)
        lamp('back room lamp', (6.5, 2.7, 0), '#ffe0b0', intensity=8, distance=10)
        text('sign', 'HUT', (0, 2.55, -3.2), 'brass', size=0.35, both_faces=True)
        volume('front room', (0, 1.6, 0), (8, 3.2, 6), tags=['indoors'])
        volume('back room', (6.5, 1.6, 0), (5, 3.2, 6), tags=['indoors'])
        link('front room', 'back room', door='inner')
        landmark('table', (-2.2, 0.8, 1.6), tags=['prop'])

    with context('porch', origin=(0, 0, -3)):
        # Porch deck 1.2 m below the hut floor, four steps up to the door.
        slab('porch deck', (0, -4.5), (6, 3), 'deck', y=-1.2, thickness=0.3)
        stairs('porch steps', (0, -1.2, -3.05), rise=1.2, run=3.05, material='stone', width=2.0, rail='brass')  # overlaps the hut floor edge by 5 cm: abutting edges leave a seam
        # A mitred corner piece: a convex prism, the way angled junctions are built.
        prism('porch corner', [(-3, -3), (-3, -6), (-4.5, -6)], -1.5, -0.9, 'stone')
        spot('porch spot', (0, 2.8, -4.5), (0, 0, -1.5), '#cfe6ff', intensity=18)
        volume('porch', (0, -0.3, -4.5), (6, 2.6, 3), roofed=False)
        link('porch', 'front room', door='front')

    with context('courtyard', origin=(0, -1.2, -15)):  # starts where the porch deck ends (z = -9), no overlapping slabs
        slab('courtyard ground', (0, 0), (16, 12), 'stone', y=0.0, thickness=0.4)
        for name, a, b in (('yard west', (-8, -6), (-8, 6)), ('yard east', (8, -6), (8, 6)), ('yard south', (-8, -6), (8, -6))):
            wall(name, a, b, 1.2, 'stone', thickness=0.4)
        box('well', (5, 0.5, -2), (1.4, 1.0, 1.4), 'stone', group='environment', bevel=0.05)
        lamp('yard lamp', (-4, 2.5, 0), '#ffffff', intensity=6, distance=16)
        volume('courtyard', (0, 1.0, 0), (16, 2.0, 12), roofed=False)
        link('courtyard', 'porch')
        landmark('well', (5, 1.0, -2), tags=['prop'])
        landmark('guard post', (-5, 0.1, 3), yaw=0.0, tags=['guard'])
        spawn((0, 0.1, 4), yaw=3.14159)


def main() -> None:
    argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else sys.argv[1:]
    out = argv[argv.index('--out') + 1] if '--out' in argv else 'build/level'
    build()
    export(out, 'hut')


if __name__ == '__main__':
    main()
