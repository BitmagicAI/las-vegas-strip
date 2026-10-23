"""The Grand Canal Shoppes, Level 2 of the Venetian (2026-10-23): the canal from the gondola dock south past St Mark's
Square to a loop round an island of palazzi, quays and streets of Venetian house fronts under a painted sky, stone
bridges, gondolas, lamps and cafe tables, the Rialto street to the lobby's landing, and the passage east to the
terrace door. Streamed as its own venue, 'grandCanal' (build_venetian_interior.py shoppes).

Layout: venetian_interior_plan.py (the canal follows the official Level 2 map, registered to the world). The public
area is one polygon (streets + quays + square + canal); every edge of its boundary becomes a row of house fronts
facing into it, so corners and the island close by themselves. Original geometry from the shared kit
(venetian_kit.py) and materials (venetian_materials.py).
"""
import math
import numpy as np
from shapely.geometry import Polygon, LineString, Point, box as sbox
from shapely.geometry.polygon import orient
from shapely.ops import unary_union
from surface_geometry import triangles
from building_surfaces import parts
from common import Frame
import venetian_kit as K
from venetian_interior_plan import L2, CANAL, CANAL_WIDTH, ESCALATOR

Y = L2
SKY = Y + 9.6                 # 16.84: the painted sky, just under the podium roof (17.0)
WATER = Y - .55               # 6.69
BED = 6.3                     # the casino's ceiling (6.04) is under it
HALF = CANAL_WIDTH / 2

# ------------------------------------------------------------------ plan
NORTH_WALL = -805.0
DOCK = (322.6, -803.0)                                  # the canal's north end: the gondola dock
REACH = [DOCK] + CANAL[:6]                              # north reach to the loop's north-west corner
LOOP = CANAL[4:] + [CANAL[4]]                           # the loop round the island (closed)
SQUARE = (334.0, -764.0, 377.0, -733.0)                 # St Mark's Square (x0, z0, x1, z1)
BLOCK_S = (334.0, -733.0, 363.0, -721.5)                # the palazzi between the square and the loop
TERRACE_X = 437.5                                       # our inner wall; the podium shell's door is at x 438.6
TERRACE_Z = -734.0
STREETS = {
    'west quay': sbox(309.0, NORTH_WALL, 322.0, -718.0),
    'west street': sbox(316.0, -718.0, 331.5, -666.0),
    'east quay': sbox(322.0, NORTH_WALL, SQUARE[0], SQUARE[1]),
    'square': sbox(*SQUARE),
    'square quay': sbox(322.0, SQUARE[1], SQUARE[0], -737.0),               # the square opens onto the canal
    'loop south quay': sbox(328.0, -676.0, 369.0, -666.0),
    'loop north quay': sbox(325.0, BLOCK_S[3], 369.0, -712.0),
    'bend quay': sbox(322.0, -737.0, BLOCK_S[0], -716.0),
    'passage': sbox(363.0, -748.0, TERRACE_X, -724.0),        # (north of the escalator opening: 6 m to walk past it)
    'loop east quay': sbox(355.0, -724.0, 369.0, -652.0),
    'rialto street': sbox(288.0, -666.0, 369.0, -652.0),
    # over the Great Hall (x < 288, its south wall's inner face at z -666.2) the north row stands back to z -664.8, so
    # its shopfronts' 1.1 m display recesses stay out of the hall
    'rialto street over the hall': sbox(243.0, -664.8, 288.5, -652.0),
    # west of x 243 the podium's notch (an outdoor canal slot, x 224.5..242.5, z -657.8..-650.6, walls to 17 m) cuts
    # the band: the street keeps north of it to meet the Scenic Overlook (x 230.5..236, north of z -666; the palace's
    # floor bands reach x 230.15)
    'rialto street west': sbox(230.5, -664.8, 243.5, -658.2),
    'overlook landing': sbox(230.5, -666.0, 236.0, -664.5),
}
# open edges: the overlook's south end (lobby, at 7.24) and the steps down to the Rialto gallery landing (lobby, 6.24)
OPEN_EDGES = [((230.5, -666.0), (236.0, -666.0)), ((243.0, -652.0), (252.0, -652.0))]


def canal_polygon():
    reach = LineString(REACH).buffer(HALF, cap_style=2, join_style=2, mitre_limit=3)
    loop = LineString(LOOP).buffer(HALF, cap_style=2, join_style=2, mitre_limit=3)
    c = unary_union([reach, loop])
    # square the dock end against the north wall
    return unary_union([c, sbox(REACH[0][0] - HALF, NORTH_WALL, REACH[0][0] + HALF, REACH[0][1] + 1)]).intersection(sbox(200, NORTH_WALL, 450, -600))


def island_polygons():
    inner = Polygon(LOOP).buffer(-HALF, join_style=2)
    buildings = inner.buffer(-3.5, join_style=2)     # a 3.5 m fondamenta: bridges land on it with room to walk round
    return inner, buildings


def public_polygon():
    canal = canal_polygon(); inner, buildings = island_polygons()
    pub = unary_union(list(STREETS.values()) + [canal, inner]).difference(buildings)
    pub = pub.difference(sbox(*BLOCK_S))
    return orient(pub.buffer(0), 1.0), canal, buildings


# ------------------------------------------------------------------ helpers
def edge_frame(B, a, b, y=Y):
    """Facade frame on boundary edge a->b of a CCW-oriented public polygon: local x along the edge, +z into the area."""
    dx, dz = b[0] - a[0], b[1] - a[1]; L = math.hypot(dx, dz)
    nx, nz = -dz / L, dx / L
    return Frame(B, a[0], a[1], math.atan2(nx, nz), y=y), L


def floor(B, mat, poly, y, solid=True):
    G = Frame(B, 0, 0, 0, y=0)
    for q in parts(poly):
        for t in triangles(q):
            pts = [(px, y, pz) for px, pz in list(t.exterior.coords)[:-1]]
            K.face(G, mat, pts, solid)


def statue(F, x, y, z, s=1.0):
    """A small classical figure on a pedestal (stylised): limestone."""
    K.box(F, 'vi-limestone', (x, y + .25 * s, z), (.5 * s, .5 * s, .5 * s))
    K.lathe(F, 'vi-limestone', x, z, [(.5 * s, .2 * s), (.9 * s, .24 * s), (1.3 * s, .17 * s), (1.55 * s, .2 * s), (1.65 * s, .1 * s)], 8, y=y)
    K.sphere(F, 'vi-limestone', (x, y + 1.82 * s, z), .12 * s, 8, 6)
    K.tube(F, 'vi-limestone', (x - .18 * s, y + 1.5 * s, z), (x - .32 * s, y + 1.95 * s, z + .05), .04 * s, 5)


def procuratie(F, x0, x1, seed=0):
    """St Mark's Square's two-storey arcades: a ground-floor arcade of shops, an upper storey of arched windows between
    engaged columns, a cornice and a balustraded roofline with statues. Facade frame, face at z=0, base at 0."""
    rng = np.random.default_rng(seed)
    w = x1 - x0; n = max(1, int(round(w / 4.4))); bay = w / n
    gh, uh = 4.4, 2.75          # ground arcade, upper storey: the roofline (with statues) stays under the sky
    rings = []
    for i in range(n):
        cx = x0 + bay * (i + .5); ow = bay - 1.1
        ring = K.opening('arch', cx, 0, ow, gh - .55, 14); rings.append(ring)
        K.pane(F, K.SHOPS[int(rng.integers(0, len(K.SHOPS)))], ring, -1.6)
        K.pane(F, 'vi-shop-glass', ring, -1.2)
        K.arch_ring(F, cx, gh - .55 - ow / 2, ow, 0, 'vi-limestone')
        for s in (-1, 1): K.box(F, 'vi-limestone', (cx + s * (ow / 2 + .1), gh - .55 - ow / 2 - .1, .05), (.24, .22, .12))
        if i % 2 == 0:
            name = K.SHOP_NAMES[int(rng.integers(0, len(K.SHOP_NAMES)))]
            K.box(F, 'vi-wood-dark', (cx, gh - .55 - ow / 2 - .55, -1.1), (min(ow - .4, len(name) * .22 + .4), .36, .05))
            K.text(F, name, cx, gh - .55 - ow / 2 - .68, -1.06, .2, 'vi-sign-gold')
    K.wall(F, 'vi-rustication', [(x0, 0), (x1, 0), (x1, gh), (x0, gh)], rings, 0, 1.62, 'vi-limestone')
    K.sweep_facade(F, 'vi-limestone', x0, x1, 0, K.P_SKIRT)
    for i in range(n + 1):
        K.pilaster(F, x0 + bay * i, 0, gh - .1, .5, 'vi-limestone', 'vi-limestone', 0, .14)
    top = K.entablature(F, x0, x1, gh, 'vi-limestone', 'vi-limestone', None, 0, .7, True)
    # upper storey
    yu = top; rings = []
    for i in range(n):
        cx = x0 + bay * (i + .5)
        rings.append(K.window(F, 'arch', cx, yu + .4, 1.4, 1.95, 0, .25, 'vi-window-lit' if rng.random() < .35 else 'vi-window-dark',
                              'vi-limestone', True, None, True, None, True, 'stone' if i % 3 == 1 else None))
    K.wall(F, 'vi-stucco-white', [(x0, yu), (x1, yu), (x1, yu + uh), (x0, yu + uh)], rings, 0, .25, 'vi-limestone')
    for i in range(n + 1):
        x = x0 + bay * i
        K.column(F, x, .22, uh, .17, 'vi-limestone', 'vi-limestone', 'vi-limestone', 'tuscan', 10, solid=False, plinth=False)
        K.box(F, 'vi-limestone', (x, yu + uh / 2, .04), (.3, uh, .08))
    yc = yu + uh
    K.sweep_facade(F, 'vi-limestone', x0, x1, yc, K.P_CORNICE)
    # roofline balustrade with statues
    yb = yc + .48
    K.balustrade_line(F, (x0, .3), (x1, .3), yb, .7, solid=False)
    for i in range(0, n + 1, 2): statue(F, x0 + bay * i, yb + .7, .3, .42)
    return yb + .7


def terrace_wall(F, L, x):
    """The east end of the passage: the terrace door (7 x 5 m, centred at x along the wall) in a rusticated wall with an
    archway frame and a sign."""
    ring = K.opening('rect', x, 0, 7.0, 5.0)
    K.wall(F, 'vi-rustication', [(0, 0), (L, 0), (L, 9.4), (0, 9.4)], [ring], 0, 1.25, 'vi-limestone')
    K.sweep_ring(F, 'vi-limestone', ring, [(0, 0), (0, .08), (.3, .1), (.5, .18), (.7, .18), (.72, 0)], 0)
    K.entablature(F, x - 5.2, x + 5.2, 5.25, 'vi-limestone', 'vi-limestone', 'vi-gilt-plain', 0, .9, True)
    K.text(F, 'TERRACE  ·  EXPO', x, 5.75, .14, .42, 'vi-sign-gold')
    for s in (-1, 1):
        K.column(F, x + s * 4.4, .55, 6.6, .32, 'vi-marble-cream', 'vi-gilt-plain', 'vi-limestone', 'corinthian', 16, solid=True)
    K.arch_ring(F, x, 6.4, 7.4, .05, 'vi-limestone')
    K.pane(F, 'vi-fresco-b', K.opening('segment', x, 6.6, 6.6, 2.2)[:-0] if False else [(x - 3.3, 6.65), (x + 3.3, 6.65)] +
           [(x + 3.3 * math.cos(a), 6.65 + 3.3 * math.sin(a)) for a in np.linspace(0, math.pi, 13)][1:-1] + [(x - 3.3, 6.65)], .02)
    K.sweep_facade(F, 'vi-limestone', 0, L, 9.0, K.P_CORNICE_SMALL)


def bridge_house(B, x, z0, z1, depth=6.0):
    """A house spanning a street on a low basket arch (the Shoppes' archway buildings, built to fit under the sky):
    street along z from z0 to z1 (z0 < z1) at world x; limestone arch storey, a brick floor of windows above, a
    soffit following the arch, piers that close against the street's own fronts."""
    w = z1 - z0; r = w / 2 - .7; crown = 6.0; rise = r * .36; spring = crown - rise; top = SKY - Y - .25
    def arch_pt(a): return (r * math.cos(a), spring + rise * math.sin(a))
    A = np.linspace(0, math.pi, 21)
    for side in (-1, 1):
        if side > 0: F = Frame(B, x + depth / 2, z1, math.pi / 2, y=Y)
        else: F = Frame(B, x - depth / 2, z0, -math.pi / 2, y=Y)
        ring = [(w / 2 - r, 0), (w / 2 + r, 0)] + [(w / 2 + px, py) for px, py in (arch_pt(a) for a in A)]
        yb = crown + .7
        K.wall(F, 'vi-limestone', [(0, 0), (w, 0), (w, yb), (0, yb)], [ring], 0)
        pts = [np.array([w / 2 + px, py, 0]) for px, py in (arch_pt(a) for a in A)]
        ns = [np.array([math.cos(a) / r, math.sin(a) / rise, 0]) for a in A]; ns = [v / np.linalg.norm(v) for v in ns]
        K.sweep_frames(F, 'vi-limestone', pts, ns, [np.array([0, 0, 1.])] * len(pts), K.P_ARCHIVOLT)
        K.box(F, 'vi-limestone', (w / 2, crown + .22, .08), (.5, .55, .16))
        for s_ in (-1, 1): K.pilaster(F, w / 2 + s_ * (r + .35), 0, spring, .55, 'vi-limestone', 'vi-limestone', 0, .1)
        K.sweep_facade(F, 'vi-limestone', 0, w, yb, K.P_STRING)
        holes = []
        for i in range(5):
            cx = (i + .5) * w / 5
            holes.append(K.window(F, 'arch', cx, yb + .35, .95, 1.45, 0, .22, 'vi-window-lit' if i % 2 else 'vi-window-dark', 'vi-limestone', True,
                                  None, True, None, True, 'flowers' if i == 2 else None))
        K.wall(F, 'vi-brick', [(0, yb + .18), (w, yb + .18), (w, top - .3), (0, top - .3)], holes, 0, .22, 'vi-limestone')
        K.sweep_facade(F, 'vi-limestone', 0, w, top - .3, K.P_CORNICE_SMALL)
        K.text(F, 'CALLE DEL PONTE', w / 2, crown + .4, .17, .22, 'vi-sign-gold')
    G = Frame(B, 0, 0, 0, y=Y)
    zc = (z0 + z1) / 2
    for a0, a1 in zip(A, A[1:]):   # the soffit follows the arch through the house's depth
        p = lambda a, xx: (xx, arch_pt(a)[1], zc + arch_pt(a)[0])
        K.quad(G, 'vi-limestone-shade', p(a0, x - depth / 2), p(a1, x - depth / 2), p(a1, x + depth / 2), p(a0, x + depth / 2))
    for s_ in (-1, 1):
        K.quad(G, 'vi-limestone-shade', (x - depth / 2, 0, zc + s_ * r), (x + depth / 2, 0, zc + s_ * r), (x + depth / 2, spring, zc + s_ * r), (x - depth / 2, spring, zc + s_ * r))
        K.solid_box(G, (x, (SKY - Y) / 2, zc + s_ * (r + (w / 2 - r) / 2)), (depth, SKY - Y, w / 2 - r))
    G.light(x, crown - .5, zc, 0xffe2c0, 160, 10)


# ------------------------------------------------------------------ build
def front(B, a, b, n_edge, ri):
    """The facade on one boundary piece a->b: the terrace door wall, St Mark's arcades, a short plain wall, or a row of
    house fronts."""
    F, L = edge_frame(B, a, b)
    mx, mz = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    if abs(mx - TERRACE_X) < .3 and -748 <= mz <= -724:
        terrace_wall(F, L, math.dist(a, (TERRACE_X, TERRACE_Z))); return
    on_square = (SQUARE[0] - .3 <= mx <= SQUARE[2] + .3 and SQUARE[1] - .3 <= mz <= SQUARE[3] + .3 and
                 (abs(mz - SQUARE[1]) < .3 or abs(mz - SQUARE[3]) < .3 or abs(mx - SQUARE[2]) < .3))
    if on_square and L > 6:
        procuratie(F, 0, L, n_edge)
        K.solid_quad(F, (0, 0, -.15), (L, 0, -.15), (L, SKY - Y, -.15), (0, SKY - Y, -.15))
        return
    if L < 4.5:
        K.wall(F, K.STUCCO[n_edge % len(K.STUCCO)], [(0, 0), (L, 0), (L, 9.3), (0, 9.3)])
        K.sweep_facade(F, 'vi-limestone', 0, L, 4.2, K.P_STRING); K.sweep_facade(F, 'vi-limestone', 0, L, 8.8, K.P_CORNICE_SMALL)
        K.solid_quad(F, (0, 0, -.15), (L, 0, -.15), (L, 9.3, -.15), (0, 9.3, -.15))
        return
    K.house_row(F, 0, L, SKY - Y - .2, seed=n_edge * 5 + ri)


def build(B):
    B.property = 'grandCanal-interior'; B.detail = 0
    G = Frame(B, 0, 0, 0, y=0)
    pub, canal, island_buildings = public_polygon()
    walk = pub.difference(canal)
    square = sbox(*SQUARE).difference(canal)
    esc = sbox(ESCALATOR['x0'], -742.0, ESCALATOR['x1'], -733.5)

    # floors: St Mark's pavers, flagstone streets and quays; the escalator opening is cut out
    B.source = 'grand-canal-floor'
    floor(B, 'vi-square-pavers', square.difference(esc), Y)
    floor(B, 'vi-street-flags', walk.difference(square).difference(esc), Y)
    # the escalator opening: balustrade on three sides (the escalator arrives from the south)
    ex0, ex1 = ESCALATOR['x0'], ESCALATOR['x1']
    K.balustrade_line(G, (ex0, -742.0), (ex0, -733.5), Y, 1.05)
    K.balustrade_line(G, (ex1, -733.5), (ex1, -742.0), Y, 1.05)
    K.balustrade_line(G, (ex0, -733.5), (ex1, -733.5), Y, 1.05)
    # the slab's edges lined from the casino's ceiling (6.04, its well has a gilt fascia) up to the street; the north side is
    # the escalators' top landing (the casino's plate)
    for x, s_ in ((ex0, -1), (ex1, 1)):
        K.box(G, 'vi-limestone', (x + s_ * .1, (6.04 + Y) / 2, -737.75), (.2, Y - 6.04, 8.5))
    K.box(G, 'vi-limestone', ((ex0 + ex1) / 2, (6.04 + Y) / 2, -733.4), (ex1 - ex0 + .4, Y - 6.04, .2))

    # the canal: water, bed, brick walls with coping along every bank, invisible barriers at the banks
    B.source = 'grand-canal-water'
    floor(B, 'water', canal, WATER, False)
    floor(B, 'vi-limestone-shade', canal, BED, True)
    bridges = bridge_specs()
    def deck(b):
        F = Frame(None, b['c'][0], b['c'][1], b['yaw'], y=Y); L = b['span'] / 2 + .3; W = b['width'] / 2 + .4
        return Polygon([(F.p(x, 0, z)[0], F.p(x, 0, z)[2]) for x, z in [(-L, -W), (L, -W), (L, W), (-L, W)]])
    bridge_zone = unary_union([deck(b) for b in bridges])
    ring_lines = [canal.exterior] + list(canal.interiors)
    for ring in ring_lines:
        pts = list(ring.coords)
        for a, b in zip(pts, pts[1:]):
            seg = LineString([a, b])
            if seg.length < .05: continue
            mid = seg.interpolate(.5, normalized=True)
            if mid.y <= NORTH_WALL + .2: continue                    # the dock end against the north wall
            K.canal_edge(G, a, b, Y, WATER) if Polygon(ring).exterior.is_ccw else K.canal_edge(G, b, a, Y, WATER)
            # barrier (not under bridges)
            for piece in [seg.difference(bridge_zone)]:
                for s in (list(piece.geoms) if hasattr(piece, 'geoms') else [piece]):
                    if s.is_empty or s.length < .1: continue
                    (ax, az), (bx, bz) = list(s.coords)[0], list(s.coords)[-1]
                    K.solid_quad(G, (ax, Y, az), (bx, Y, bz), (bx, Y + 1.15, bz), (ax, Y + 1.15, az))
    # the dock end: a brick base under the north wall across the canal
    K.box(G, 'vi-brick', (DOCK[0], (BED + Y) / 2, NORTH_WALL + .15), (CANAL_WIDTH + .4, Y - BED, .3))

    # house fronts on every boundary edge
    B.source = 'grand-canal-fronts'
    n_edge = 0
    rings = [pub.exterior] + list(pub.interiors)
    open_zone = unary_union([LineString([p, q]).buffer(.08, cap_style=2) for p, q in OPEN_EDGES])
    for ri, ring in enumerate(rings):
        pts = list(ring.coords)
        for a0, b0 in zip(pts, pts[1:]):
            seg = LineString([a0, b0])
            if seg.length < .3: continue
            rest = seg.difference(open_zone)
            pieces = [g for g in (rest.geoms if hasattr(rest, 'geoms') else [rest]) if not g.is_empty and g.length >= .3]
            for piece in pieces:
                c = list(piece.coords); a, b = c[0], c[-1]
                # keep the ring's direction (difference may return the piece reversed)
                if (b[0] - a[0]) * (b0[0] - a0[0]) + (b[1] - a[1]) * (b0[1] - a0[1]) < 0: a, b = b, a
                n_edge += 1
                front(B, a, b, n_edge, ri)

    # the archway house over the Rialto street
    B.source = 'grand-canal-archway'
    bridge_house(B, 296.0, -666.0, -652.0)

    # bridges
    B.source = 'grand-canal-bridges'
    for bs in bridges:
        F = Frame(B, bs['c'][0], bs['c'][1], bs['yaw'], y=Y)
        K.stone_bridge(F, bs['span'], bs['width'], bs['rise'], 0, WATER - Y, HALF + .1)
        for s in (-1, 1): K.lamp_post(F, s * (bs['span'] / 2 + .3), s * (bs['width'] / 2 + .45), 0, 1, 3.0)

    # gondolas, mooring poles, the dock
    B.source = 'grand-canal-gondolas'
    for (x, z, yaw) in [(320.3, -790.0, 0.12), (319.6, -772.0, -.08), (319.8, -748.0, .1), (346.0, -674.6, math.pi / 2), (358.6, -694.0, 0.0)]:
        K.gondola_at(B, x, z, yaw, WATER - .38)
    for z in np.arange(-800, -742, 6.5):
        K.mooring_pole(G, REACH[0][0] + HALF - .5 + (REACH[1][0] - REACH[0][0]) * (z - REACH[0][1]) / (REACH[1][1] - REACH[0][1]) if z > -766 else 324.2, z, BED, Y + 2.2)
    K.box(G, 'vi-wood-dark', (DOCK[0], Y - .2, -801.0), (CANAL_WIDTH - .6, .12, 3.0))   # the boarding pontoon
    K.box(G, 'vi-wood-honey', (330.6, Y + 1.1, -802.6), (1.6, 2.2, 1.2), True)            # ticket booth
    K.box(G, 'vi-awning-red', (330.6, Y + 2.35, -802.6), (2.0, .2, 1.6))
    K.text(Frame(B, 330.6, -802.6 + .61, 0, y=Y), 'GONDOLA RIDES', 0, 1.6, 0, .18, 'vi-sign-gold')

    # lamps along the quays and Murano lamps in the square; cafe tables; planters
    B.source = 'grand-canal-furniture'
    lamp_line(G, walk, canal)
    for x, z in [(342, -757), (360, -757), (342, -740), (360, -740), (370, -750)]:
        K.murano_lamp(G, x, z, Y)
    for i, (x, z) in enumerate([(338, -760), (338, -754), (344, -761), (350, -760), (356, -761), (365, -759), (371, -760), (371, -754)]):
        K.cafe_set(G, x, z, Y, 4, 'vi-umbrella-blue' if i % 3 == 0 else None)
    for i, (x, z) in enumerate([(312, -770), (312, -756), (312, -742), (327, -700), (327, -688), (366, -700), (366, -686), (300, -660), (280, -660), (258, -660)]):
        K.cafe_set(G, x, z, Y, 3 if i % 2 else 4)
    for x, z in [(311, -780), (311, -730), (318, -680), (320, -667), (365, -720), (366, -668), (258, -655), (270, -663.5), (304, -655), (312, -664),
                 (380, -728), (400, -742), (420, -726), (430, -742)]:
        K.planter(G, x, z, Y, .42, .55, topiary=(x + z) % 2 == 0)

    # the painted sky over the whole level
    B.source = 'grand-canal-sky'
    floor(B, 'vi-sky-day', pub.buffer(6.0, join_style=2).simplify(.5), SKY, False)

    # light pools
    for x, z in [(316, -795), (316, -775), (316, -755), (318, -735), (322, -705), (322, -683), (345, -760), (365, -748), (345, -742),
                 (395, -734), (420, -734), (362, -705), (362, -680), (345, -716), (345, -670), (325, -659), (310, -659), (275, -659),
                 (250, -659), (330, -790), (345, -692)]:
        G.light(x, SKY - 2.6, z, 0xffe9cc, 280, 22)

    zones = zones_for(pub)
    access = [[x, Y, z] for x, z in [(234, -662), (248, -655), (438, -734), (379, -743), (300, -659), (322, -790), (355, -750), (345, -716),
                                     (366, -690), (318, -700)]]
    views = {
        'vi-gcs-canal-north': dict(eye=[312.5, Y + 1.7, -803], target=[320, Y + 3.5, -760]),
        'vi-gcs-canal-bridge': dict(eye=[324.5, Y + 1.7, -772], target=[318, Y + 2.5, -735]),
        'vi-gcs-square': dict(eye=[330, Y + 1.7, -748], target=[377, Y + 4, -752]),
        'vi-gcs-square-north': dict(eye=[360, Y + 1.7, -736], target=[355, Y + 4.5, -764]),
        'vi-gcs-loop': dict(eye=[367, Y + 1.7, -664], target=[350, Y + 3, -690]),
        'vi-gcs-island': dict(eye=[318, Y + 1.7, -690], target=[345, Y + 4, -692]),
        'vi-gcs-rialto-street': dict(eye=[358, Y + 1.7, -659], target=[240, Y + 3.5, -662]),
        'vi-gcs-passage': dict(eye=[370, Y + 1.7, -734], target=[437, Y + 3, -734]),
        'vi-gcs-high': dict(eye=[312, Y + 6.5, -803], target=[340, Y + 1, -745], lens=20),
        'vi-gcs-archway': dict(eye=[324, Y + 1.7, -656], target=[291, Y + 4.5, -660]),
        'vi-gcs-facade': dict(eye=[316.5, Y + 2.2, -760], target=[309, Y + 4.5, -770], lens=22),
        'vi-gcs-west-street': dict(eye=[322, Y + 1.7, -667], target=[322, Y + 3, -720]),
    }
    def walk(pts): return [[x, Y + .08, z] for x, z in pts]
    routes = [dict(points=walk([(233, -662), (248, -660), (300, -659), (323, -662), (323, -712), (312, -730), (312, -774)]) +
                   over(bridges[0], (312, -774)) + walk([(330, -770), (330, -750), (372, -750), (380, -745.5), (437, -736)])),
              dict(points=walk([(345.4, -662)]) + over(bridges[3], (345.4, -662), approach=1.0) + walk([(352.2, -681.0), (352.2, -693.1)]) +
                   over(bridges[4], (352.2, -693.1), approach=1.0) + walk([(366, -700)]))]
    portals = [{"p": [438.6, 7.24, -734.0], "yaw": -1.5707963267948966, "width": 7, "height": 5, "name": "Grand Canal Shoppes east terrace",
                "venue": "grandCanal"}]
    minx, minz, maxx, maxz = pub.bounds
    return [dict(key='grandCanal', name='The Venetian · Grand Canal Shoppes', bounds=[round(minx, 2), round(minz, 2), round(maxx, 2), round(maxz, 2)],
                 portals=portals, levelY=Y, preloadDistance=40, anchor=(380.0, 12.0, -700.0), zones=zones, accessPoints=access,
                 routes=routes, views=views)]


def bridge_specs():
    """Bridges across the canal: centre, yaw (local x across the water), span, width, rise."""
    out = []
    def across(p, q, t, span=11.6, width=3.6, rise=1.6):
        x, z = p[0] + (q[0] - p[0]) * t, p[1] + (q[1] - p[1]) * t
        dx, dz = q[0] - p[0], q[1] - p[1]; L = math.hypot(dx, dz); tx, tz = dx / L, dz / L
        nx, nz = -tz, tx                                     # across the water
        out.append(dict(c=(x, z), yaw=math.atan2(-nz, nx), span=span, width=width, rise=rise))
    across(REACH[1], REACH[2], .55)                          # by the gondola dock
    across(REACH[2], REACH[3], .45)                          # St Mark's
    across(REACH[3], REACH[4], .5, 12.4)                     # the bend
    across(LOOP[4], LOOP[5], .5)                             # loop south (Rialto street to the island)
    across(LOOP[2], LOOP[3], .5)                             # loop east
    across(LOOP[6], LOOP[7], .5)                             # loop west (the west street to the island)
    return out


def over(b, start, k=12, approach=1.6):
    """Route waypoints across bridge b, starting from the foot nearer `start` (x, z): in along the bridge's axis from
    `approach` metres before the foot, over the deck, and out the same distance past the far foot."""
    F = Frame(None, b['c'][0], b['c'][1], b['yaw'], y=Y); L = b['span'] / 2
    ends = [F.p(-L, 0, 0), F.p(L, 0, 0)]
    near = -1 if math.dist((ends[0][0], ends[0][2]), start) < math.dist((ends[1][0], ends[1][2]), start) else 1
    xs = [near * (L + approach)] + list(np.linspace(near * L, -near * L, k + 1)) + [-near * (L + approach)]
    pts = []
    for x in xs:
        t = max(-1, min(1, x / L)); p = F.p(x, b['rise'] * (1 - t * t) + .08, 0); pts.append([p[0], p[1], p[2]])
    return pts


def lamp_line(G, walk, canal):
    """Street lamps along every quay, 1.3 m from the water, every ~13 m."""
    edge = canal.boundary
    for ring in ([canal.exterior] + list(canal.interiors)):
        line = LineString(ring.coords)
        d = 6.0
        while d < line.length:
            p = line.interpolate(d); q = line.interpolate(min(line.length, d + .5))
            tx, tz = q.x - p.x, q.y - p.y; L = math.hypot(tx, tz) or 1
            for s in (-1, 1):
                x, z = p.x - s * tz / L * 1.3, p.y + s * tx / L * 1.3
                if walk.contains(Point(x, z).buffer(.4)) and z > NORTH_WALL + 3:
                    K.lamp_post(G, x, z, Y, 3 if int(d / 13) % 2 else 5, 3.8); break
            d += 13.0
    _ = edge


def zones_for(pub):
    """Axis-aligned zones covering the public area (one per street rectangle, overlapping by a metre)."""
    out = []
    for name, r in STREETS.items():
        x0, z0, x1, z1 = r.bounds
        out.append(dict(origin=[round((x0 + x1) / 2, 2), Y, round(z0 - .5, 2)], yaw=0, width=round(x1 - x0 + 1, 2), depth=round(z1 - z0 + 1, 2), height=9.6))
    inner = Polygon(LOOP).buffer(-HALF + .1)
    x0, z0, x1, z1 = inner.bounds
    out.append(dict(origin=[round((x0 + x1) / 2, 2), Y, round(z0 - .5, 2)], yaw=0, width=round(x1 - x0 + 1, 2), depth=round(z1 - z0 + 1, 2), height=9.6))
    return out
