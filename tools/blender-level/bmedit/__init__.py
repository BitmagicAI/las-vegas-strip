"""bmedit — edit a game's GLBs and make new low-poly props in a short Blender script.

    from bmedit import load, palette, recolor, cone, box, join, export
    ground = load('ground')                       # the game's asset, imported
    palette(ground)                               # its face colours, most used first
    recolor(ground, '#eef3f7', where=lambda p, n, c: n[1] > 0.6)   # snow on everything flat
    export('ground', ground)                      # replaces the asset, same id

    post = join([box('post', (0.2, 1.2, 0.2), color='#6b4a2f'),
                 box('cap', (0.3, 0.1, 0.3), at=(0, 1.2, 0), color='#4a3220')], 'post')
    export('fence-post', post)                    # a new asset, 1.3 m tall

Positions, sizes and normals are in GAME coordinates — metres, Y up, +Z forward, yaw in radians
about +Y — the same as bmlevel; the Blender axis flip happens inside. Colours are sRGB: '#rrggbb',
0-255 or 0-1 triples. Painting is per face (flat low-poly look), stored as the mesh's COLOR_0.

`load()` and `export()` are the only file access a script has. The host decides where they point
(`configure()`): the Asset Forger's job directory, or the GDK project's `build/` folder.
"""
try:  # inside Blender
    import bpy  # noqa: F401
except ImportError:  # plain python3: only bmedit.colour is usable (its tests run here)
    __all__: list[str] = []
else:
    from bmedit.blender import *  # noqa: F401,F403
    from bmedit.blender import __all__, configure, exports  # noqa: F401
