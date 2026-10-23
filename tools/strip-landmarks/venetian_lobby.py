"""The Venetian's lobby (2026-10-23): the interior of venue 'venetian', rebuilt at full detail to the resort map
(venetian_interior_plan.py) and the lead's routing of 2026-10-23 around the palace's south wing and the canal notch.

  Great Hall      x 225.8..288, z -707.5..-666, floor 0.26 (2 cm over the palace's own marble), ceiling 12.24: tumbling-block
                  floor, giant marble pilasters, arched shopfronts, painted panels, entablature and cove, a coffered gilt
                  ceiling with a 22 x 14 m oval fresco and two round medallions, chandeliers, the GRAND CANAL SHOPPES sign,
                  a two-flight grand stair along the south wall, the 16 m arch east into the casino.
  Scenic Overlook a balcony at L2 (7.24), x 230.5..236 (clear of the palace's floor bands, which reach x 230.15), along
                  the hall's west side over a coffered loggia with the entrance fresco; it ends at z -666.0, where the
                  Shoppes' Rialto street (lead) begins.
  Rialto gallery  from the Rialto door (225.85, 6.24, -644) east through the palace south wing's open passage
                  (z -646.6..-641.4) as a vaulted corridor, into a landing hall (x 238..252), whose steps rise north 1 m
                  to the street at z -652 (x 243..252) through a gateway facade.
  Arrivals        under the gallery: x 229..252, z -646.4..-631, ceiling 5.94; glazed door opening x 229..235 (the lead cuts
                  the podium wall); opens east into the colonnade.
  Colonnade       x 253..316, z -647..-633: checker floor, paired Corinthian columns on pedestals, entablatures, a painted
                  barrel vault (crown 11.24), lunettes, mirrors, doors, chandeliers.
  Rotunda         centre (328, -640), r 11: ring of paired columns, painted dome to 15.24, the Armillary Sphere over a
                  rose-marble fountain; openings west (colonnade), north (casino, z -652) and east (front desk).
  Front desk      x 339..372, z -652..-630, ceiling 7.24: marble-and-gilt counter with lamps, THE VENETIAN, queue, lounges.

All geometry goes through common.Frame and venetian_kit.py with 'vi-*' materials; collision is a few quads and boxes.
"""
import math
import numpy as np
from shapely.geometry import Polygon, Point, box as sbox
from shapely.ops import unary_union
from surface_geometry import triangles
from building_surfaces import parts
from common import Frame
import venetian_kit as K

TAU = math.tau
FL = 0.26            # Great Hall floor (the palace's marble lies at 0.24 under its west strip)
L1 = 0.24
L2 = 7.24
RIALTO_Y = 6.26      # gallery floor (the Rialto bridge's own landing is at 6.24 under its east end)
CEIL = 12.24         # Great Hall ceiling
SOFFIT = 6.74        # under the overlook

SHOP_IMAGES = ['vi-shop-fashion', 'vi-shop-glass-art', 'vi-shop-masks', 'vi-shop-sweets']
NAMES = ['GIOIELLERIA', 'VETRERIA MURANO', 'MASCHERE', 'PASTICCERIA', 'PROFUMERIA', 'SARTORIA', 'OROLOGERIA',
         'PELLETTERIA', 'CIOCCOLATERIA', 'ARGENTERIA', 'GALLERIA', 'MERLETTI', 'CAPPELLI', 'CARTOLERIA', 'CERAMICHE',
         'LIBRERIA', 'OTTICA', 'TESSUTI', 'ENOTECA', 'CAFFE']
_shop = [0]


def next_shop():
    i = _shop[0]; _shop[0] += 1
    return SHOP_IMAGES[(i * 3) % len(SHOP_IMAGES)], NAMES[i % len(NAMES)]


# ------------------------------------------------------------------ small helpers
def facade(B, a, b, y=0.0):
    """A frame on a wall from plan point a to b (world x, z): local x runs a->b, local +z is the left normal (the room)."""
    dx, dz = b[0] - a[0], b[1] - a[1]; L = math.hypot(dx, dz)
    return Frame(B, a[0], a[1], math.atan2(-dz / L, dx / L), y=y), L


def poly_faces(F, mat, poly, z=0.0):
    """A polygon in facade (x, y) coordinates at depth z."""
    for q in parts(poly):
        for t in triangles(q): K.face(F, mat, [(px, py, z) for px, py in list(t.exterior.coords)[:-1]])


def plan_faces(W, mat, poly, y):
    """A polygon in plan (x, z) at height y (W is the world frame)."""
    for q in parts(poly):
        for t in triangles(q): K.face(W, mat, [(px, y, pz) for px, pz in list(t.exterior.coords)[:-1]])


def solid_poly(F, poly, z=0.0):
    for q in parts(poly):
        for t in triangles(q): K._solid(F, [(px, py, z) for px, py in list(t.exterior.coords)[:-1]])


def wall(F, mat, x0, x1, y0, y1, holes=(), z=0.0, reveal=0.0, reveal_mat=None, floor_y=None):
    """A flat wall with openings. A hole is a ring, or dict(ring, reveal, floor, mat) for its own reveal depth (toward -z),
    floor height (edges lying on it get no reveal: doors) and reveal material."""
    hs = [(h['ring'], h.get('reveal', reveal), h.get('floor', floor_y), h.get('mat', reveal_mat)) if isinstance(h, dict)
          else (h, reveal, floor_y, reveal_mat) for h in holes]
    poly = sbox(x0, y0, x1, y1)
    if hs: poly = poly.difference(unary_union([Polygon(r).buffer(0) for r, *_ in hs]))
    poly_faces(F, mat, poly, z)
    for r, rev, fy, rm in hs:
        if not rev: continue
        ring = list(r) + [r[0]]
        for (ax, ay), (bx, by) in zip(ring, ring[1:]):
            if fy is not None and abs(ay - fy) < 1e-6 and abs(by - fy) < 1e-6: continue
            K.quad(F, rm or mat, (ax, ay, z), (bx, by, z), (bx, by, z - rev), (ax, ay, z - rev))


def segments(x0, x1, gaps):
    out = []; cur = x0
    for g0, g1 in sorted(gaps):
        if g0 > cur + .02: out.append((cur, g0))
        cur = max(cur, g1)
    if cur < x1 - .02: out.append((cur, x1))
    return out


def dado(F, x0, x1, y, h=.9, gaps=(), mat='vi-marble-cream', d=.06):
    """A marble dado band with a moulded cap, interrupted at doorways."""
    for a, b in segments(x0, x1, gaps):
        K.box(F, mat, ((a + b) / 2, y + h / 2, d / 2), (b - a, h, d))
        K.sweep_facade(F, mat, a, b, y + h, K.P_STRING[:5] + [(0, .1)])


def solid_wall(F, x0, x1, y0, y1, gaps=(), z=0.0):
    """Collision quads for a wall with rectangular gaps [(gx0, gx1, top)] from the floor."""
    cur = x0
    for gx0, gx1, top in sorted(gaps):
        if gx0 > cur + 1e-6: K.solid_quad(F, (cur, y0, z), (gx0, y0, z), (gx0, y1, z), (cur, y1, z))
        if top < y1: K.solid_quad(F, (gx0, top, z), (gx1, top, z), (gx1, y1, z), (gx0, y1, z))
        cur = max(cur, gx1)
    if cur < x1 - 1e-6: K.solid_quad(F, (cur, y0, z), (x1, y0, z), (x1, y1, z), (cur, y1, z))


def open_path(ring):
    """An opening ring (BL, BR, ..., counter-clockwise) as an open path up the left jamb, over the top, down the right."""
    return [ring[0]] + list(ring[2:])[::-1] + [ring[1]]


def surround(F, ring, mat='vi-limestone', prof=K.P_SURROUND, z=0.0):
    K.sweep_ring(F, mat, open_path(ring), prof, z, closed=False)


def skirting(F, x0, x1, y, gaps=(), mat='vi-marble-black', prof=K.P_SKIRT, z=0.0):
    cur = x0
    for g0, g1 in sorted(gaps):
        if g0 > cur + .05: K.sweep_facade(F, mat, cur, g0, y, prof, z)
        cur = max(cur, g1)
    if cur < x1 - .05: K.sweep_facade(F, mat, cur, x1, y, prof, z)


def gilt_panel(F, x0, y0, x1, y1, mat, z=0.0, frame='vi-gilt-plain', prof=K.P_GILT_FRAME, lift=.012):
    ring = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    K.pane(F, mat, ring, z + lift)
    K.sweep_ring(F, frame, ring, prof, z + lift)


def arched_panel(F, xc, y0, w, h, mat, z=0.0, frame='vi-gilt-plain', lift=.012):
    ring = K.opening('arch', xc, y0, w, h, 12)
    K.pane(F, mat, ring, z + lift)
    K.sweep_ring(F, frame, ring, K.P_GILT_FRAME, z + lift)
    return ring


def pilaster(F, x, y0, y1, w=.8, d=.16, z=0.0, mat='vi-marble-cream', cap='vi-gilt-plain', base='vi-marble-cream',
             flutes=5, flute_mat='vi-limestone-shade'):
    """A Corinthian pilaster: moulded base, fluted shaft, gilt capital with leaves and volutes."""
    hc = min(.78, w * .95)
    K.box(F, base, (x, y0 + .14, z + (d + .1) / 2), (w + .2, .28, d + .1))
    K.box(F, base, (x, y0 + .33, z + (d + .07) / 2), (w + .13, .1, d + .07))
    K.box(F, base, (x, y0 + .4, z + (d + .03) / 2), (w + .06, .04, d + .03))
    ys0, ys1 = y0 + .42, y1 - hc
    K.box(F, mat, (x, (ys0 + ys1) / 2, z + d / 2), (w, ys1 - ys0, d))
    if flutes:
        for i in range(flutes):
            fx = x - w / 2 + w * (i + .5) / flutes
            K.box(F, flute_mat, (fx, (ys0 + ys1) / 2, z + d + .006), (w / flutes * .45, ys1 - ys0 - .5, .012))
    # capital
    K.box(F, cap, (x, ys1 + .03, z + (d + .04) / 2), (w + .04, .06, d + .04))
    K.box(F, cap, (x, ys1 + .06 + (hc - .2) / 2, z + (d + .05) / 2), (w + .02, hc - .2, d + .05))
    zf = z + d + .05
    for row, (ly, lh) in enumerate([(.08, .42), (.3, .4)]):
        for i in range(3):
            lx = x + (i - 1) * w * .32
            yb = ys1 + ly; yt = yb + lh * hc
            K.face(F, cap, [(lx - .11, yb, zf), (lx + .11, yb, zf), (lx + .08, yt - .12, zf + .05), (lx, yt, zf + .09),
                            (lx - .08, yt - .12, zf + .05)])
    for s in (-1, 1):
        cx, cy = x + s * (w / 2 - .02), y1 - .24
        K.path(F, cap, [(cx + s * .1 * (1 - t * .55) * math.cos(a), cy + .1 * (1 - t * .55) * math.sin(a), zf + .02)
                        for t, a in zip(np.linspace(0, 1, 9), np.linspace(math.pi / 2, math.pi / 2 + TAU * .85, 9))], .022, 4)
    K.box(F, cap, (x, y1 - .05, z + (d + .12) / 2), (w + .2, .1, d + .12))


def shopfront(F, xc, w, h, y0, z=0.0, trim='vi-limestone', depth=1.1, shop=None, name=None):
    """An arched shopfront: lit display, glass, bronze frame with a fanlight, name band, archivolt. Returns the ring
    (a hole for the wall, with a `depth` reveal)."""
    if shop is None: shop, name = next_shop()
    ring = K.opening('arch', xc, y0, w, h, 16)
    r = w / 2; ys = y0 + h - r
    K.pane(F, shop, ring, z - depth)
    K.pane(F, 'vi-shop-glass', ring, z - .34)
    fr = 'vi-bronze'
    for s in (-1, 1): K.box(F, fr, (xc + s * (r - .05), (y0 + ys) / 2, z - .3), (.1, ys - y0, .1))
    K.box(F, fr, (xc, ys, z - .3), (w, .12, .12))
    K.box(F, fr, (xc, y0 + .3, z - .3), (w, .6, .06))
    for s in (-1, 1): K.box(F, fr, (xc + s * w / 6, (y0 + .6 + ys) / 2, z - .3), (.06, ys - y0 - .6, .06))
    for a in np.radians([30, 60, 90, 120, 150]):
        K.tube(F, fr, (xc, ys, z - .3), (xc + (r - .06) * math.cos(a), ys + (r - .06) * math.sin(a), z - .3), .022, 4)
    K.path(F, fr, [(xc + r * .42 * math.cos(a), ys + r * .42 * math.sin(a), z - .3) for a in np.linspace(0, math.pi, 9)], .022, 4)
    K.path(F, fr, [(xc + (r - .05) * math.cos(a), ys + (r - .05) * math.sin(a), z - .3) for a in np.linspace(0, math.pi, 13)], .03, 4)
    K.box(F, 'vi-wood-dark', (xc, ys - .32, z - .25), (w - .24, .42, .03))
    size = min(.26, (w - .6) / (len(name) * .7))
    K.text(F, name, xc, ys - .44, z - .225, size, 'vi-sign-gold')
    K.arch_ring(F, xc, ys, w, z, trim, keystone=True)
    for s in (-1, 1): K.box(F, trim, (xc + s * (r + .08), ys - .1, z + .05), (.3, .22, .1))
    return ring


def balustrade_slope(W, a, b, ya, yb, h=1.0, mat='vi-limestone', pitch=.32, solid=True):
    """A balustrade along plan a->b whose base rises from ya to yb (stair flights)."""
    ax, az = a; bx, bz = b; L = math.hypot(bx - ax, bz - az)
    ux, uz = (bx - ax) / L, (bz - az) / L
    G = Frame(W.b, ax, az, math.atan2(ux, uz) - math.pi / 2, y=0)
    dy = yb - ya
    def Y(x): return ya + dy * x / L
    N2 = [np.array([0, 0, 1.])] * 2; U2 = [np.array([0, 1., 0])] * 2
    K.sweep_frames(G, mat, [np.array([0, ya, 0.]), np.array([L, yb, 0.])], N2, U2, [(-.15, 0), (.15, 0), (.15, .14), (-.15, .14), (-.15, 0)])
    K.sweep_frames(G, mat, [np.array([0, ya + h - .1, 0.]), np.array([L, yb + h - .1, 0.])], N2, U2,
                   [(-.16, 0), (.16, 0), (.16, .04), (.12, .1), (-.12, .1), (-.16, .04), (-.16, 0)])
    hb = h - .26
    prof = [(0, .05), (.06 * hb, .05), (.1 * hb, .036), (.3 * hb, .085), (.55 * hb, .045), (.68 * hb, .032), (.78 * hb, .052),
            (.86 * hb, .036), (hb, .05)]
    n = max(1, int(L / pitch))
    for i in range(n):
        x = (i + .5) * L / n
        K.lathe(G, mat, x, 0, prof, 8, y=Y(x) + .14)
    if solid: K.solid_quad(G, (0, ya, 0), (L, yb, 0), (L, yb + h, 0), (0, ya + h, 0))


def newel(W, x, z, y, h=1.25, mat='vi-marble-cream', lamp=False):
    K.box(W, mat, (x, y + h / 2, z), (.5, h, .5))
    K.box(W, mat, (x, y + .1, z), (.62, .2, .62))
    K.box(W, mat, (x, y + h - .05, z), (.62, .1, .62))
    K.box(W, 'vi-gilt-plain', (x, y + h - .14, z), (.54, .06, .54))
    if lamp:
        K.lathe(W, 'vi-gilt-plain', x, z, [(0, .2), (.08, .14), (.3, .06), (1.2, .045), (1.3, .09), (1.38, .04)], 10, y=y + h)
        for i in range(5):
            a = i * TAU / 5
            K.path(W, 'vi-gilt-plain', [(x, y + h + 1.1, z), (x + .3 * math.cos(a), y + h + 1.15, z + .3 * math.sin(a)),
                                        (x + .38 * math.cos(a), y + h + 1.35, z + .38 * math.sin(a))], .02, 4)
            K.sphere(W, 'vi-crystal', (x + .38 * math.cos(a), y + h + 1.48, z + .38 * math.sin(a)), .13, 8, 6)
        K.sphere(W, 'vi-crystal', (x, y + h + 1.62, z), .16, 8, 6)
    K.solid_box(W, (x, y + h / 2, z), (.62, h, .62))


def flight(W, x_bot, x_top, y_bot, y_top, z0, z1, n, mat='vi-marble-cream', runner='vi-velvet-red', axis='x'):
    """Steps (blocks one riser tall) from x_bot (low) to x_top (high), z0..z1 wide; with a carpet runner and brass rods.
    axis 'z' swaps the roles of x and z."""
    r = (y_top - y_bot) / n; t = (x_top - x_bot) / n; s = 1 if t > 0 else -1
    zc = (z0 + z1) / 2; wz = z1 - z0
    def P(x, y, z): return (x, y, z) if axis == 'x' else (z, y, x)
    def bx(c, size): K.box(W, mat, P(*c), size if axis == 'x' else (size[2], size[1], size[0]))
    for i in range(n):
        xa = x_bot + i * t; xb = xa + t; yt = y_bot + (i + 1) * r
        bx(((xa + xb) / 2, yt - r / 2, zc), (abs(t), r, wz))
        K.box(W, 'vi-marble-cream', P(xa - s * .015, yt - .025, zc), (.05, .04, wz) if axis == 'x' else (wz, .04, .05))
        if runner:
            rw = min(1.7, wz * .45)
            K.quad(W, runner, P(xa, yt + .006, zc - rw), P(xb, yt + .006, zc - rw), P(xb, yt + .006, zc + rw), P(xa, yt + .006, zc + rw))
            K.quad(W, runner, P(xa - s * .006, yt - r, zc - rw), P(xa - s * .006, yt + .006, zc - rw), P(xa - s * .006, yt + .006, zc + rw),
                   P(xa - s * .006, yt - r, zc + rw))
            K.tube(W, 'vi-gilt-plain', P(xa + s * .03, yt + .02, zc - rw - .08), P(xa + s * .03, yt + .02, zc + rw + .08), .012, 4)


def coffer_field(W, x0, x1, z0, z1, y, nx, nz, depth=.28, beam=.34, panel=lambda i, j: 'vi-coffer-cream',
                 side='vi-gilt-plain', plane='vi-gilt', skip=lambda i, j: False, holes=(), rosette=True):
    """A coffered ceiling at height y (beam undersides) over x0..x1, z0..z1: nx x nz cells, skipping some; `holes` are
    plan polygons left open in the beam plane (for frescoes and their frames)."""
    dx = (x1 - x0) / nx; dz = (z1 - z0) / nz
    cut = []
    for i in range(nx):
        for j in range(nz):
            if skip(i, j): continue
            a, b = x0 + i * dx + beam / 2, x0 + (i + 1) * dx - beam / 2
            c, d = z0 + j * dz + beam / 2, z0 + (j + 1) * dz - beam / 2
            cut.append(sbox(a, c, b, d))
            yp = y + depth
            K.quad(W, panel(i, j), (a, yp, c), (b, yp, c), (b, yp, d), (a, yp, d))
            for (p, q) in [((a, c), (b, c)), ((b, c), (b, d)), ((b, d), (a, d)), ((a, d), (a, c))]:
                K.quad(W, side, (p[0], yp, p[1]), (q[0], yp, q[1]), (q[0], y, q[1]), (p[0], y, p[1]))
            if rosette:
                K.lathe(W, 'vi-gilt-plain', (a + b) / 2, (c + d) / 2, [(yp - .002, .2), (yp - .05, .15), (yp - .09, .06), (yp - .1, .001)], 8)
    region = sbox(x0, z0, x1, z1).difference(unary_union(cut + [Polygon(h).buffer(0) if not hasattr(h, 'area') else h for h in holes]))
    plan_faces(W, plane, region, y)
    return dx, dz


def vault(F, x0, x1, z0, z1, spring, rise, bays, frescoes=('vi-fresco-a', 'vi-fresco-b'), side=('vi-coffer-red', 'vi-coffer-green'),
          field='vi-stucco-white', rib='vi-gilt', frame='vi-gilt-plain', n=20, gap=.3):
    """A segmental (or, with rise = half the span, semicircular) barrel vault over local x0..x1 running along z: per bay a
    fresco at the crown, an ornament panel each side, a cream field near the springing, gilt frames and transverse ribs."""
    w = (x1 - x0) / 2; cx = (x0 + x1) / 2
    R = (w * w + rise * rise) / (2 * rise); yc = spring + rise - R
    a0 = math.atan2(spring - yc, w); a1 = math.pi - a0
    def P(a, z): return (cx + R * math.cos(a), yc + R * math.sin(a), z)
    sp = a1 - a0
    c0, c1 = a0 + sp * .3, a0 + sp * .7
    s0, s1 = a0 + sp * .12, a0 + sp * .88
    L = (z1 - z0) / bays
    ang = np.linspace(a0, a1, n + 1)
    for b in range(bays):
        za, zb = z0 + b * L + gap, z0 + (b + 1) * L - gap
        def strip(mat, aa, ab, k):
            A = np.linspace(aa, ab, k + 1)
            for i in range(k): K.quad(F, mat, P(A[i], za), P(A[i + 1], za), P(A[i + 1], zb), P(A[i], zb))
        strip(frescoes[b % len(frescoes)], c0, c1, 6)
        strip(side[b % len(side)], s0, c0, 4); strip(side[(b + 1) % len(side)], c1, s1, 4)
        strip(field, a0, s0, 3); strip(field, s1, a1, 3)
        for a in [s0, c0, c1, s1]: K.tube(F, frame, P(a, za), P(a, zb), .045, 6)
        for zz in [za, zb]: K.path(F, frame, [P(a, zz) for a in np.linspace(s0, s1, 12)], .04, 6)
        for zz0, zz1 in [(z0 + b * L, za), (zb, z0 + (b + 1) * L)]:
            for i in range(n): K.quad(F, field, P(ang[i], zz0), P(ang[i + 1], zz0), P(ang[i + 1], zz1), P(ang[i], zz1))
    for b in range(bays + 1):
        zz = z0 + b * L
        K.sweep_frames(F, rib, [np.array(P(a, zz)) for a in ang], [-np.array([math.cos(a), math.sin(a), 0]) for a in ang],
                       [np.array([0, 0, 1.])] * len(ang), [(0, -.22), (.12, -.22), (.17, -.13), (.17, .13), (.12, .22), (0, .22)])
    return P, a0, a1


def ellipse(cx, cz, rx, rz, n=64):
    return Polygon([(cx + rx * math.cos(a), cz + rz * math.sin(a)) for a in np.linspace(0, TAU, n, endpoint=False)])


def ring_band(W, mat, c, u, v, r, prof, n=48):
    """A circular band (armillary ring) of radius r about c in the plane spanned by unit vectors u, v; profile (radial, axial)."""
    c = np.array(c, float); u = np.array(u, float); v = np.array(v, float); ax = np.cross(u, v); ax /= np.linalg.norm(ax)
    A = np.linspace(0, TAU, n, endpoint=False)
    pts = [c + r * (math.cos(a) * u + math.sin(a) * v) for a in A]
    ns = [math.cos(a) * u + math.sin(a) * v for a in A]
    K.sweep_frames(W, mat, pts, ns, [ax] * n, prof, closed=True)


def chandelier(W, x, y, z, r=1.2, tiers=3, arms=10, drop=1.6):
    K.tube(W, 'vi-gilt-plain', (x, y, z), (x, y - .25, z), .03, 5)
    K.chandelier(W, x, y - .2, z, r, tiers, arms, 'vi-crystal', 'vi-gilt-plain', drop)


def sofa(B, x, z, yaw, w=2.2, mat='vi-velvet-red', solid=True, y=L1):
    G = Frame(B, x, z, yaw, y=y)
    K.box(G, mat, (0, .42, 0), (w, .2, .85))
    K.box(G, mat, (0, .78, -.36), (w, .6, .16))
    for s in (-1, 1):
        K.box(G, mat, (s * (w / 2 - .07), .62, 0), (.16, .26, .85))
        K.box(G, 'vi-gilt-plain', (s * (w / 2 - .1), .14, .3), (.06, .28, .06)); K.box(G, 'vi-gilt-plain', (s * (w / 2 - .1), .14, -.3), (.06, .28, .06))
    for k in range(max(1, int(w / .9))):
        cx = -w / 2 + .16 + (k + .5) * (w - .32) / max(1, int(w / .9))
        K.box(G, mat, (cx, .56, .02), ((w - .32) / max(1, int(w / .9)) - .04, .1, .76))
    K.box(G, 'vi-gilt-plain', (0, .33, .43), (w, .04, .02))
    if solid: K.solid_box(G, (0, .45, 0), (w, .9, .85))


def mirror(F, x0, y0, x1, y1, z=0.0):
    """A gilt-framed mirror with gilt muntins (so it reads as glass, not a grey panel)."""
    gilt_panel(F, x0, y0, x1, y1, 'vi-lobby-mirror', z)
    for k in (1, 2): K.box(F, 'vi-gilt-plain', (x0 + (x1 - x0) * k / 3, (y0 + y1) / 2, z + .025), (.03, y1 - y0, .02))
    for k in (1, 2, 3): K.box(F, 'vi-gilt-plain', ((x0 + x1) / 2, y0 + (y1 - y0) * k / 4, z + .025), (x1 - x0, .03, .02))


def arched_mirror(F, xc, y0, w, h, z=0.0):
    arched_panel(F, xc, y0, w, h, 'vi-lobby-mirror', z)
    r = w / 2; ys = y0 + h - r
    for s in (-1, 1):
        xb = xc + s * w / 6; yt = ys + math.sqrt(r * r - (w / 6) ** 2)
        K.box(F, 'vi-gilt-plain', (xb, (y0 + yt) / 2, z + .025), (.03, yt - y0, .02))
    for k in (1, 2): K.box(F, 'vi-gilt-plain', (xc, y0 + (ys - y0) * k / 3, z + .025), (w, .03, .02))
    K.box(F, 'vi-gilt-plain', (xc, ys, z + .025), (w, .04, .02))
    for a in np.radians([30, 60, 120, 150]):
        K.tube(F, 'vi-gilt-plain', (xc, ys, z + .025), (xc + r * math.cos(a), ys + r * math.sin(a), z + .025), .014, 4)


def atlas(B, cx, cz, deg, ybase, mat='vi-gilt-plain', rad=.62):
    """A kneeling atlas (gilt), back to the fountain's axis, arms raised to the sphere: tapered limbs, head, drapery."""
    t = math.radians(deg)
    G = Frame(B, cx + rad * math.cos(t), cz + rad * math.sin(t), math.atan2(math.cos(t), math.sin(t)), y=ybase)
    T = lambda a, b, r, r2=None, n=8: K.tube(G, mat, a, b, r, n, r2)
    T((.12, .52, .02), (.14, .1, .3), .1, .075)              # kneeling leg: thigh, shin, foot
    T((.14, .1, .3), (.14, .08, -.2), .07, .045)
    T((.14, .08, -.2), (.14, .03, -.32), .045, .03)
    T((-.12, .52, .02), (-.16, .56, .38), .1, .075)           # raised leg
    T((-.16, .56, .38), (-.16, .08, .42), .07, .045)
    T((-.16, .06, .4), (-.16, .03, .56), .045, .03)
    T((0, .48, 0), (0, .95, -.02), .15, .18, 10)              # torso
    T((0, .95, -.02), (0, 1.12, -.04), .18, .12, 10)
    T((0, 1.1, -.04), (0, 1.22, -.03), .055)                 # neck, head
    K.sphere(G, mat, (0, 1.33, 0), .11, 10, 7, (1, 1.15, 1.05))
    T((-.22, 1.07, -.04), (.22, 1.07, -.04), .07)             # shoulders, arms raised to the sphere
    for s in (-1, 1):
        T((s * .22, 1.07, -.04), (s * .3, 1.33, -.1), .065, .05)
        T((s * .3, 1.33, -.1), (s * .17, 1.58, -.2), .05, .04)
        K.sphere(G, mat, (s * .16, 1.62, -.21), .055, 6, 4)
    K.lathe(G, 'vi-gilt', 0, 0, [(.34, .18), (.46, .21), (.56, .19), (.6, .15)], 10)   # drapery
    T((-.34, .05, .1), (.34, .05, .1), .09, None, 8)           # the rock he kneels on


def coffee_table(W, x, z, w=1.4, d=.8):
    K.box(W, 'vi-marble-green', (x, .48, z), (w, .05, d))
    K.box(W, 'vi-gilt-plain', (x, .44, z), (w - .1, .04, d - .1))
    for sx in (-1, 1):
        for sz in (-1, 1): K.tube(W, 'vi-gilt-plain', (x + sx * (w / 2 - .12), L1, z + sz * (d / 2 - .1)), (x + sx * (w / 2 - .12), .44, z + sz * (d / 2 - .1)), .025, 5)
    K.solid_box(W, (x, .36, z), (w, .26, d))


def flowers(W, x, z, y, r=.6, seed=0):
    """A loose arrangement: a mound of leaves with many small blooms."""
    rng = np.random.default_rng(seed)
    for i in range(7):
        a = i * TAU / 7; K.sphere(W, 'vi-plant', (x + r * .45 * math.cos(a), y + .12, z + r * .45 * math.sin(a)), r * .3, 7, 4, (1, .6, 1))
    for i in range(26):
        a = i * 2.39996; rr = r * math.sqrt((i + .5) / 26) * .85
        h = y + .2 + r * .55 * (1 - (rr / r) ** 2) + .06 * rng.random()
        K.sphere(W, ['vi-flower-red', 'vi-flower-pink', 'vi-flower-red', 'vi-cloth-white'][i % 4], (x + rr * math.cos(a), h, z + rr * math.sin(a)), r * .13, 6, 4)


def urn(W, x, z, y=L1, s=1.0, seed=0):
    K.lathe(W, 'vi-marble-cream', x, z, [(0, .3 * s), (.12 * s, .3 * s), (.16 * s, .16 * s), (.3 * s, .14 * s), (.55 * s, .36 * s),
                                          (.85 * s, .42 * s), (1.0 * s, .3 * s), (1.05 * s, .36 * s), (1.1 * s, .34 * s)], 12, y=y)
    K.disc(W, 'vi-soil', x, y + 1.08 * s, z, .32 * s, 12)
    flowers(W, x, z, y + 1.05 * s, .55 * s, seed)
    K.solid_box(W, (x, y + .55 * s, z), (.8 * s, 1.1 * s, .8 * s))


# ------------------------------------------------------------------ Great Hall and Scenic Overlook
HX0, HX1, HZ0, HZ1 = 226.0, 287.8, -707.3, -666.2       # inner faces
BACK_X = 230.45                                         # the overlook's back wall (palace bands behind it)
OVL_X1 = 236.0                                          # the overlook's edge
ENT_Y = 10.0                                            # entablature base
STAIR_Z = -670.3                                        # the stair's open side (stringer face)
SA_BOT, SA_TOP, SB_BOT, SB_TOP = 257.8, 251.5, 247.5, 241.2   # flight A (floor -> 3.74), flight B (3.74 -> 7.24)
MID_Y = 3.74


def great_hall(B, W):
    B.source = 'lobby-hall'
    # ---- floor: tumbling blocks in a cream marble border with a black fillet
    outer = sbox(HX0, HZ0, HX1, HZ1); inner = sbox(HX0 + 1.2, HZ0 + 1.2, HX1 - 1.2, HZ1 - 1.2)
    field = sbox(HX0 + 1.34, HZ0 + 1.34, HX1 - 1.34, HZ1 - 1.34)
    plan_faces(W, 'vi-marble-cream', outer.difference(inner), FL)
    plan_faces(W, 'vi-marble-black', inner.difference(field), FL)
    plan_faces(W, 'vi-tumbling', field, FL)
    plan_faces(W, 'vi-marble-black', sbox(225.1, -690.64, HX0, -679.64), FL)       # palace door threshold
    plan_faces(W, 'vi-marble-black', sbox(HX1, -695.0, 288.0, -679.0), FL)        # casino arch threshold (the casino floor starts at 288)
    K.solid_quad(W, (225.1, FL, HZ0), (HX1, FL, HZ0), (HX1, FL, HZ1), (225.1, FL, HZ1))
    K.solid_quad(W, (HX1 - .05, FL, -695.0), (288.05, FL, -695.0), (288.05, FL, -679.0), (HX1 - .05, FL, -679.0))   # the arch threshold walks too

    # ---- north wall (facing south); local x = X - 226
    Fn, Ln = facade(B, (HX0, HZ0), (HX1, HZ0))
    piers = [11.0 + 7.15 * k for k in range(8)]
    holes = [shopfront(Fn, 5.0, 3.8, 5.0, FL)]
    for k in range(7): holes.append(shopfront(Fn, piers[k] + 3.575, 4.6, 5.6, FL))
    wall(Fn, 'vi-stucco-cream', 0, Ln, FL, CEIL, holes, 0, 1.1, 'vi-limestone')
    for x in piers: pilaster(Fn, x, FL, ENT_Y)
    for k in range(7):
        xc = piers[k] + 3.575
        K.sweep_facade(Fn, 'vi-limestone', xc - 3.1, xc + 3.1, 6.25, K.P_STRING)
        gilt_panel(Fn, xc - 2.3, 6.75, xc + 2.3, 9.45, ['vi-lobby-ornament-blue', 'vi-coffer-red', 'vi-coffer-green'][k % 3])
    gilt_panel(Fn, 5.25, 7.7, 9.35, 9.6, 'vi-lobby-ornament-red')
    skirting(Fn, 0, Ln, FL, [(xc - 2.4, xc + 2.4) for xc in [5.0] + [p + 3.575 for p in piers[:7]]])
    K.entablature(Fn, BACK_X - HX0, Ln, ENT_Y, 'vi-limestone', 'vi-gilt', 'vi-gilt-plain', 0, 1.0, True)
    K.solid_quad(Fn, (0, FL, 0), (Ln, FL, 0), (Ln, CEIL, 0), (0, CEIL, 0))

    # ---- east wall (facing west); local x = Z + 707.3; the 16 m arch into the casino
    Fe, Le = facade(B, (HX1, HZ0), (HX1, HZ1))
    arch = K.opening('segment', 20.3, FL, 16.0, 6.58, 24)
    holes = [dict(ring=arch, reveal=.2, floor=FL, mat='vi-marble-cream'), shopfront(Fe, 5.5, 4.6, 5.6, FL), shopfront(Fe, 35.6, 4.6, 5.6, FL)]
    wall(Fe, 'vi-stucco-cream', 0, Le, FL, CEIL, holes, 0, 1.1, 'vi-limestone')
    K.sweep_ring(Fe, 'vi-limestone', open_path(arch), K.P_ARCHIVOLT, 0, closed=False)
    K.box(Fe, 'vi-limestone', (20.3, FL + 6.58 + .2, .1), (.7, .8, .2))
    K.box(Fe, 'vi-gilt-plain', (20.3, FL + 6.58 + .2, .21), (.4, .5, .02))
    # a gilt sunburst grille fills the arch above 5.24, where the casino's header and ceiling edge are (its openings are <= 5.0 m)
    YT = 5.24
    crown = Polygon(arch).buffer(0).intersection(sbox(0, YT, Le, 9))
    poly_faces(Fe, 'vi-iron', crown, -.18)
    hw = 8 * math.sqrt(1 - ((YT - 4.04) / 2.8) ** 2)
    K.box(Fe, 'vi-gilt-plain', (20.3, YT, -.12), (2 * hw, .16, .12))
    for a in np.radians([28, 40, 52, 64, 77, 90, 103, 116, 128, 140, 152]):
        K.tube(Fe, 'vi-gilt-plain', (20.3, YT, -.12), (20.3 + 7.92 * math.cos(a), 4.04 + 2.77 * math.sin(a), -.12), .03, 5)
    K.path(Fe, 'vi-gilt-plain', [(20.3 + 3.2 * math.cos(a), YT + .62 * math.sin(a), -.12) for a in np.linspace(0, math.pi, 13)], .035, 5)
    K.sphere(Fe, 'vi-gilt-plain', (20.3, YT + .05, -.1), .22, 10, 6)
    for x in [.65, 10.4, 11.4, 29.2, 30.2, 40.45]: pilaster(Fe, x, FL, ENT_Y)
    for x in [5.5, 35.6]:
        K.sweep_facade(Fe, 'vi-limestone', x - 3.1, x + 3.1, 6.25, K.P_STRING)
        gilt_panel(Fe, x - 2.3, 6.75, x + 2.3, 9.45, 'vi-lobby-ornament-blue')
    K.box(Fe, 'vi-velvet-red', (20.3, 8.05, .04), (5.6, 1.15, .08))
    K.sweep_ring(Fe, 'vi-gilt-plain', [(17.5, 7.47), (23.1, 7.47), (23.1, 8.63), (17.5, 8.63)], K.P_GILT_FRAME, .08)
    K.text(Fe, 'CASINO', 20.3, 7.72, .1, .78, 'vi-sign-gold')
    gilt_panel(Fe, 14.8, 8.95, 25.8, 9.75, 'vi-lobby-ornament-red')
    skirting(Fe, 0, Le, FL, [(3.1, 7.9), (12.0, 28.6), (33.2, 38.0)])
    K.entablature(Fe, 0, Le, ENT_Y, 'vi-limestone', 'vi-gilt', 'vi-gilt-plain', 0, 1.0, True)
    solid_wall(Fe, 0, Le, FL, CEIL, [(12.3, 28.3, 6.6)])
    for s in (-1, 1): K.lamp_post(W, HX1 - 1.4, -687 + s * 9.6, FL, 5, 4.2, 'vi-gilt-plain', 'vi-lantern')

    # ---- south wall (facing north); local x = 287.8 - X
    Fs, Ls = facade(B, (HX1, HZ1), (HX0, HZ1))
    sp = [HX1 - x for x in [258.45, 265.6, 272.75, 279.9, 287.05]]
    holes = [shopfront(Fs, x - 3.575, 4.6, 5.6, FL) for x in sp[:4]]
    holes.append(shopfront(Fs, HX1 - 231.0, 3.8, 5.0, FL))
    l2 = [(HX1 - OVL_X1, L2), (HX1 - 230.5, L2), (HX1 - 230.5, 9.85), (HX1 - OVL_X1, 9.85)]
    holes.append(dict(ring=l2, reveal=.2, floor=L2, mat='vi-limestone'))
    wall(Fs, 'vi-stucco-cream', 0, Ls, FL, CEIL, holes, 0, 1.1, 'vi-limestone')
    surround(Fs, l2, 'vi-limestone')
    K.box(Fs, 'vi-limestone', ((l2[0][0] + l2[1][0]) / 2, 9.97, .1), (6.0, .2, .2))
    for x in sp: pilaster(Fs, x, FL, ENT_Y)
    for k, x in enumerate(sp[:4]):
        xc = x - 3.575
        K.sweep_facade(Fs, 'vi-limestone', xc - 3.1, xc + 3.1, 6.25, K.P_STRING)
        gilt_panel(Fs, xc - 2.3, 6.75, xc + 2.3, 9.45, ['vi-coffer-green', 'vi-lobby-ornament-blue', 'vi-coffer-red', 'vi-lobby-ornament-blue'][k])
    # the GRAND CANAL SHOPPES sign over the stair, a painting over the mid landing, panels
    sx = HX1 - 247.5
    K.box(Fs, 'vi-velvet-red', (sx, 8.95, .05), (11.2, 1.34, .1))
    K.sweep_ring(Fs, 'vi-gilt-plain', [(sx - 5.6, 8.28), (sx + 5.6, 8.28), (sx + 5.6, 9.62), (sx - 5.6, 9.62)],
                 [(-.1, 0), (-.1, .05), (-.05, .09), (.06, .09), (.12, .05), (.12, 0)], .1)
    K.text(Fs, 'GRAND CANAL SHOPPES', sx, 8.66, .12, .8, 'vi-sign-gold')
    for s in (-1, 1): K.sphere(Fs, 'vi-gilt-plain', (sx + s * 5.3, 8.95, .14), .09, 8, 6)
    gilt_panel(Fs, HX1 - 256.0, 4.9, HX1 - 248.0, 7.7, 'vi-fresco-b', prof=[(-.16, 0), (-.16, .06), (-.08, .12), (.08, .12), (.16, .06), (.16, 0)])
    gilt_panel(Fs, HX1 - 241.0, 7.9, HX1 - 236.8, 9.5, 'vi-coffer-red')
    skirting(Fs, 0, HX1 - SA_BOT - .3, FL, [(x - 3.575 - 2.4, x - 3.575 + 2.4) for x in sp[:4]])
    skirting(Fs, HX1 - OVL_X1, Ls, FL, [(HX1 - 231.0 - 2.0, HX1 - 231.0 + 2.0)])
    K.entablature(Fs, 0, HX1 - BACK_X, ENT_Y, 'vi-limestone', 'vi-gilt', 'vi-gilt-plain', 0, 1.0, True)
    K.solid_quad(Fs, (0, FL, 0), (Ls, FL, 0), (Ls, L2, 0), (0, L2, 0))
    solid_wall(Fs, 0, Ls, L2, CEIL, [(HX1 - OVL_X1, HX1 - 230.5, 9.85)])

    # ---- west wall under the overlook (facing east); local x = -666.2 - Z; the palace door (11 x 6.2 m)
    Fw, Lw = facade(B, (HX0, HZ1), (HX0, HZ0))
    door = [(13.44, FL), (24.44, FL), (24.44, 6.44), (13.44, 6.44)]
    holes = [dict(ring=door, reveal=.9, floor=FL, mat='vi-marble-cream'), shopfront(Fw, 6.4, 3.8, 5.0, FL), shopfront(Fw, 33.0, 3.8, 5.0, FL)]
    wall(Fw, 'vi-stucco-cream', 0, Lw, FL, SOFFIT, holes, 0, 1.1, 'vi-limestone')
    surround(Fw, door, 'vi-gilt-plain', [(0, 0), (0, .06), (.12, .08), (.16, .12), (.3, .12), (.34, .06), (.34, 0)])
    K.sweep_facade(Fw, 'vi-limestone', 12.9, 24.98, 6.6, [(0, 0), (.1, 0), (.1, .04), (0, .12)])
    for x in [.6, 12.4, 25.5, 40.5]: pilaster(Fw, x, FL, SOFFIT - .02, w=.7)
    skirting(Fw, 0, Lw, FL, [(13.44, 24.44), (6.4 - 2.0, 6.4 + 2.0), (33.0 - 2.0, 33.0 + 2.0)])
    solid_wall(Fw, 0, Lw, FL, SOFFIT, [(13.44, 24.44, 6.44)])

    # ---- the overlook: soffit, beam, columns, floor, back wall, balustrade
    dzs = (HZ1 - HZ0) / 15
    hole = sbox(HX0, HZ0 + 6 * dzs, 235.0, HZ0 + 10 * dzs)
    coffer_field(W, HX0, 235.0, HZ0, HZ1, SOFFIT, 4, 15, depth=.2, beam=.3, panel=lambda i, j: 'vi-coffer-cream',
                 skip=lambda i, j: 6 <= j <= 9, rosette=False, holes=[hole])
    plan_faces(W, 'vi-gilt', hole.difference(ellipse(230.5, -685.14, 3.0, 4.4)), SOFFIT)
    K.oval_fresco(W, 230.5, SOFFIT, -685.14, 3.0, 4.4, 'vi-fresco-oval', 'vi-gilt', 36, .3)
    K.box(W, 'vi-limestone', (235.5, 6.49, (HZ0 + HZ1) / 2), (1.0, .5, HZ1 - HZ0))
    Fbe, Lbe = facade(B, (OVL_X1, STAIR_Z), (OVL_X1, HZ0))
    K.entablature(Fbe, 0, Lbe, 6.24, 'vi-limestone', 'vi-gilt', 'vi-gilt-plain', 0, .7, True)
    Fp = Frame(B, 0, 0, 0, y=.96)
    for z in [-704.6, -698.6, -692.6, -677.7, -672.0]:
        K.box(W, 'vi-marble-cream', (235.5, .61, z), (1.0, .7, 1.0))
        K.box(W, 'vi-marble-cream', (235.5, .32, z), (1.12, .12, 1.12)); K.box(W, 'vi-marble-cream', (235.5, .92, z), (1.1, .08, 1.1))
        K.column(Fp, 235.5, z, 6.24 - .96, .3, 'vi-marble-cream', 'vi-gilt-plain', 'vi-limestone', 'corinthian', 18, solid=False, plinth=False)
        K.solid_box(W, (235.5, 3.25, z), (1.0, 6.0, 1.0))
    ovl = sbox(BACK_X, HZ0, 235.62, -666.0).union(sbox(BACK_X, STAIR_Z, OVL_X1, -666.0))
    plan_faces(W, 'vi-tumbling', ovl, L2)
    plan_faces(W, 'vi-marble-cream', sbox(235.62, HZ0, OVL_X1, STAIR_Z), L2)
    K.solid_quad(W, (BACK_X, L2, HZ0), (OVL_X1, L2, HZ0), (OVL_X1, L2, -666.0), (BACK_X, L2, -666.0))
    K.balustrade_line(W, (235.82, HZ0), (235.82, STAIR_Z + .02), L2, 1.0, 'vi-limestone', .3, True)
    # back wall (facing east, 7.24..12.24) with painted arched niches
    Fb, Lb = facade(B, (BACK_X, HZ1), (BACK_X, HZ0))
    wall(Fb, 'vi-stucco-cream', 0, Lb, L2, CEIL)
    bp = [.5 + 6.683 * k for k in range(7)]
    for x in bp: pilaster(Fb, x, L2, ENT_Y, w=.6, flutes=3)
    for k in range(6):
        xc = (bp[k] + bp[k + 1]) / 2
        arched_panel(Fb, xc, 7.5, 2.4, 2.25, ['vi-fresco-a', 'vi-fresco-b'][k % 2])
        K.box(Fb, 'vi-limestone', (xc, 7.44, .08), (2.8, .1, .16))
        K.arch_ring(Fb, xc, 7.5 + 2.25 - 1.2, 2.4, 0, 'vi-limestone', keystone=True)
    skirting(Fb, 0, Lb, L2)
    K.entablature(Fb, 0, Lb, ENT_Y, 'vi-limestone', 'vi-gilt', 'vi-gilt-plain', 0, 1.0, True)
    K.solid_quad(Fb, (0, L2, 0), (Lb, L2, 0), (Lb, CEIL, 0), (0, CEIL, 0))
    # the overlook's end walls above the floor (north and south) are the hall walls; the hidden strip behind the back
    # wall is closed by the soffit below and the ceiling above.

    # ---- grand stair along the south wall
    zs0, zs1 = STAIR_Z + .2, HZ1
    flight(W, SA_BOT, SA_TOP, FL, MID_Y, zs0, zs1, 21)
    flight(W, SB_BOT, SB_TOP, MID_Y, L2, zs0, zs1, 21)
    K.box(W, 'vi-marble-cream', ((SA_TOP + SB_BOT) / 2, MID_Y - .1, (zs0 + zs1) / 2), (SA_TOP - SB_BOT, .2, zs1 - zs0))
    K.quad(W, 'vi-velvet-red', (SB_BOT, MID_Y + .006, -669.55), (SA_TOP, MID_Y + .006, -669.55), (SA_TOP, MID_Y + .006, -666.85), (SB_BOT, MID_Y + .006, -666.85))
    plan_faces(W, 'vi-tumbling', sbox(OVL_X1, zs0, SB_TOP, zs1), L2)
    plan_faces(W, 'vi-marble-cream', sbox(OVL_X1, STAIR_Z, SB_TOP, zs0), L2)
    K.solid_quad(W, (SA_BOT, FL, zs0), (SA_TOP, MID_Y, zs0), (SA_TOP, MID_Y, zs1), (SA_BOT, FL, zs1))
    K.solid_quad(W, (SA_TOP, MID_Y, zs0), (SB_BOT, MID_Y, zs0), (SB_BOT, MID_Y, zs1), (SA_TOP, MID_Y, zs1))
    K.solid_quad(W, (SB_BOT, MID_Y, zs0), (SB_TOP, L2, zs0), (SB_TOP, L2, zs1), (SB_BOT, MID_Y, zs1))
    K.solid_quad(W, (OVL_X1, L2, STAIR_Z), (SB_TOP, L2, STAIR_Z), (SB_TOP, L2, zs1), (OVL_X1, L2, zs1))
    # the stringer face (facing north): local x = 258.1 - X
    Fst, Lst = facade(B, (SA_BOT + .3, STAIR_Z), (OVL_X1, STAIR_Z))
    def u(X): return SA_BOT + .3 - X
    sil = Polygon([(u(SA_BOT + .3), FL), (u(SA_BOT + .3), FL + .2), (u(SA_BOT), FL + .2), (u(SA_TOP), MID_Y + .2), (u(SB_BOT), MID_Y + .2),
                   (u(SB_TOP), L2 + .2), (u(SB_TOP), L2), (u(OVL_X1), L2), (u(OVL_X1), FL)])
    poly_faces(Fst, 'vi-limestone', sil)
    solid_poly(Fst, sil)
    K.sweep_frames(Fst, 'vi-gilt-plain', [np.array([u(SA_BOT), FL + .02, 0]), np.array([u(SA_TOP), MID_Y + .02, 0])],
                   [np.array([0, 0, 1.])] * 2, [np.array([0, 1., 0])] * 2, [(0, 0), (.05, 0), (.05, .06), (0, .06)])
    K.sweep_frames(Fst, 'vi-gilt-plain', [np.array([u(SB_BOT), MID_Y + .02, 0]), np.array([u(SB_TOP), L2 + .02, 0])],
                   [np.array([0, 0, 1.])] * 2, [np.array([0, 1., 0])] * 2, [(0, 0), (.05, 0), (.05, .06), (0, .06)])
    arched_panel(Fst, u(238.6), 1.0, 3.4, 5.2, 'vi-lobby-ornament-blue')
    K.arch_ring(Fst, u(238.6), 1.0 + 5.2 - 1.7, 3.4, 0, 'vi-limestone', keystone=True)
    gilt_panel(Fst, u(251.3), 1.0, u(247.7), 3.1, 'vi-coffer-red')
    gilt_panel(Fst, u(246.9), 1.0, u(242.2), 3.3, 'vi-lobby-ornament-red')
    gilt_panel(Fst, u(254.7), .6, u(252.3), 1.85, 'vi-lobby-ornament-red')
    # west end of the stair base (facing west, into the loggia)
    Fsw, Lsw = facade(B, (OVL_X1, STAIR_Z), (OVL_X1, HZ1))
    wall(Fsw, 'vi-stucco-cream', 0, Lsw, FL, 6.24)
    gilt_panel(Fsw, .6, 1.4, Lsw - .6, 5.2, 'vi-fresco-a')
    K.solid_quad(Fsw, (0, FL, 0), (Lsw, FL, 0), (Lsw, 6.24, 0), (0, 6.24, 0))
    # balustrades and newels
    zb = STAIR_Z + .1
    balustrade_slope(W, (SA_BOT, zb), (SA_TOP, zb), FL + .2, MID_Y + .2)
    K.balustrade_line(W, (SA_TOP, zb), (SB_BOT, zb), MID_Y + .2, 1.0, 'vi-limestone', .3, True, posts=False)
    balustrade_slope(W, (SB_BOT, zb), (SB_TOP, zb), MID_Y + .2, L2 + .2)
    K.balustrade_line(W, (SB_TOP, zb), (OVL_X1 + .2, zb), L2, 1.0, 'vi-limestone', .3, True, posts=False)
    newel(W, SA_BOT + .1, zb, FL, 1.35, lamp=True)
    for x, y in [(SA_TOP, MID_Y + .2), (SB_BOT, MID_Y + .2), (SB_TOP, L2)]: newel(W, x, zb, y, 1.25)
    newel(W, OVL_X1 - .18, zb, L2, 1.2)

    # ---- entablature cove and the coffered, gilded ceiling
    ring = [(BACK_X, HZ0), (HX1, HZ0), (HX1, HZ1), (BACK_X, HZ1)]
    Rc = .84
    cove = [(Rc - Rc * math.cos(t), Rc * math.sin(t)) for t in np.linspace(0, math.pi / 2, 7)]
    K.sweep_plan(W, 'vi-stucco-white', ring, cove, 11.4, closed=True)
    K.sweep_plan(W, 'vi-gilt-plain', ring, [(.0, -.0), (.0, .07), (.08, .07), (.1, 0)], 11.4, closed=True)
    K.sweep_plan(W, 'vi-gilt-plain', ring, [(Rc - .04, 0), (Rc - .04, -.07), (Rc + .1, -.07), (Rc + .14, 0)], CEIL, closed=True)
    cx0, cx1, cz0, cz1 = BACK_X + Rc, HX1 - Rc, HZ0 + Rc, HZ1 - Rc
    nx, nz = 19, 13
    dx, dz = (cx1 - cx0) / nx, (cz1 - cz0) / nz
    ccx, ccz = (cx0 + cx1) / 2, (cz0 + cz1) / 2
    C = (cx0 + 5 * dx, cz0 + 4 * dz, cx0 + 14 * dx, cz0 + 9 * dz)
    MW = (cx0 + 1 * dx, cz0 + 5 * dz, cx0 + 4 * dx, cz0 + 8 * dz)
    ME = (cx0 + 15 * dx, cz0 + 5 * dz, cx0 + 18 * dx, cz0 + 8 * dz)
    def inside(i, j, R): return R[0] - 1e-6 <= cx0 + i * dx and cx0 + (i + 1) * dx <= R[2] + 1e-6 and R[1] - 1e-6 <= cz0 + j * dz and cz0 + (j + 1) * dz <= R[3] + 1e-6
    coffer_field(W, cx0, cx1, cz0, cz1, CEIL, nx, nz, depth=.28, beam=.36,
                 panel=lambda i, j: ['vi-coffer-red', 'vi-coffer-green'][(i + j) % 2],
                 skip=lambda i, j: inside(i, j, C) or inside(i, j, MW) or inside(i, j, ME),
                 holes=[sbox(*C), sbox(*MW), sbox(*ME)])
    ov = ellipse(ccx, ccz, 11.0, 7.0, 72)
    spand = sbox(*C).difference(ov)
    for qx, qz in [(-1, -1), (1, -1), (1, 1), (-1, 1)]:
        quad = spand.intersection(sbox(ccx + min(0, qx * 20), ccz + min(0, qz * 20), ccx + max(0, qx * 20), ccz + max(0, qz * 20)))
        plan_faces(W, 'vi-gilt', quad, CEIL)
    K.oval_fresco(W, ccx, CEIL, ccz, 11.0, 7.0, 'vi-fresco-oval', 'vi-gilt', 64, .32)
    K.sweep_plan(W, 'vi-gilt-plain', [(C[0], C[1]), (C[2], C[1]), (C[2], C[3]), (C[0], C[3])],
                 [(-.1, 0), (-.1, -.1), (0, -.22), (.25, -.26), (.4, -.16), (.45, 0)], CEIL, closed=True)
    for R, mat in [(MW, 'vi-fresco-a'), (ME, 'vi-fresco-b')]:
        mx, mz = (R[0] + R[2]) / 2, (R[1] + R[3]) / 2; rr = min(R[2] - R[0], R[3] - R[1]) / 2 - .75
        plan_faces(W, 'vi-coffer-green', sbox(*R).difference(Point(mx, mz).buffer(rr, 32)), CEIL)
        K.oval_fresco(W, mx, CEIL, mz, rr, rr, mat, 'vi-gilt', 40, .26)
        K.sweep_plan(W, 'vi-gilt-plain', [(R[0], R[1]), (R[2], R[1]), (R[2], R[3]), (R[0], R[3])],
                     [(-.08, 0), (-.08, -.08), (0, -.16), (.2, -.18), (.3, 0)], CEIL, closed=True)
    for x, z in [(240.4, -699.6), (240.4, -673.9), (277.8, -699.6), (277.8, -673.9), (ccx, -702.0), (ccx, -671.5)]:
        chandelier(W, x, CEIL, z, 1.5, 3, 12, 2.3)
    # banquettes under the oval's corners
    for x, z in [(247.5, -696.3), (270.7, -696.3), (247.5, -677.2), (270.7, -677.2)]:
        K.lathe(W, 'vi-velvet-red', x, z, [(FL, 1.3), (FL + .3, 1.35), (FL + .46, 1.3), (FL + .48, .62)], 20)
        K.lathe(W, 'vi-gilt-plain', x, z, [(FL, 1.34), (FL + .08, 1.36)], 20)
        K.lathe(W, 'vi-velvet-red', x, z, [(FL + .48, .62), (FL + 1.0, .5), (FL + 1.05, .3)], 16)
        K.planter(W, x, z, FL + 1.05, .34, .5, 'vi-gilt-plain', 'vi-plant', True)
        K.solid_box(W, (x, FL + .5, z), (2.4, 1.0, 2.4))
    # lights: a 4 x 3 grid under the ceiling, two in the loggia
    for x in [238.0, 252.0, 266.0, 280.0]:
        for z in [-700.0, -686.75, -673.5]: W.light(x, 10.2, z, 0xffe6c4, 280, 20)
    for z in [-697.0, -675.0]: W.light(231.0, 5.4, z, 0xffe2bc, 200, 14)


# ------------------------------------------------------------------ Rialto gallery, landing hall, steps to the street
GX0, GX1, GZ0, GZ1 = 226.05, 238.0, -646.5, -641.5      # corridor through the palace wing's passage
LX0, LX1, LZ0, LZ1 = 238.0, 252.0, -648.0, -636.0        # landing hall
SX0, SX1, SZ1 = 243.0, 252.0, -652.0                     # steps recess (to the street at z -652)
PORTAL_Z = -651.75                                       # gateway facade plane (mouldings reach z -652)
LCEIL = 11.24


def rialto(B, W):
    B.source = 'lobby-rialto'
    y = RIALTO_Y
    # ---- floors
    plan_faces(W, 'vi-marble-rust', sbox(GX0, GZ0, GX1, GZ1).difference(sbox(GX0, GZ0 + .45, GX1, GZ1 - .45)), y)
    plan_faces(W, 'vi-checker', sbox(GX0, GZ0 + .45, GX1, GZ1 - .45), y)
    hall = sbox(LX0, LZ0, LX1, LZ1)
    plan_faces(W, 'vi-marble-rust', hall.difference(sbox(LX0 + .5, LZ0 + .5, LX1 - .5, LZ1 - .5)).difference(sbox(SX0, LZ0, SX1, LZ0 + .5)), y)
    plan_faces(W, 'vi-checker', sbox(LX0 + .5, LZ0 + .5, LX1 - .5, LZ1 - .5), y)
    plan_faces(W, 'vi-marble-cream', sbox(SX0, LZ0, SX1, LZ0 + .5), y)
    K.solid_quad(W, (225.85, y, GZ0), (GX1, y, GZ0), (GX1, y, GZ1), (225.85, y, GZ1))
    K.solid_quad(W, (LX0, y, LZ0), (LX1, y, LZ0), (LX1, y, LZ1), (LX0, y, LZ1))
    # ---- corridor walls (6.26..9.3), segmental painted vault (crown 10.175, under the bridge's roof at 10.7)
    spring = 9.3
    for a, b in [((GX0, GZ0), (GX1, GZ0)), ((GX1, GZ1), (GX0, GZ1))]:
        F, Lw = facade(B, a, b)
        wall(F, 'vi-lobby-stucco-gold', 0, Lw, y, spring + .3)
        K.box(F, 'vi-marble-cream', (Lw / 2, y + .5, .03), (Lw, 1.0, .06))
        K.sweep_facade(F, 'vi-marble-cream', 0, Lw, y + 1.0, K.P_STRING[:5] + [(0, .1)])
        skirting(F, 0, Lw, y)
        bays = [Lw * (k + .5) / 3 for k in range(3)]
        for k, xc in enumerate(bays):
            gilt_panel(F, xc - 1.5, y + 1.3, xc + 1.5, y + 2.25, ['vi-fresco-a', 'vi-fresco-b', 'vi-fresco-a'][k])
        for k in range(4): pilaster(F, Lw * k / 3 + (.3 if k == 0 else -.3 if k == 3 else 0), y, spring - .62, w=.5, d=.12, flutes=3)
        K.entablature(F, 0, Lw, spring - .62, 'vi-limestone', 'vi-gilt', None, 0, .45, False)
        K.solid_quad(F, (0, y, 0), (Lw, y, 0), (Lw, spring, 0), (0, spring, 0))
    Fv = Frame(B, 0, -644.0, math.pi / 2, y=0)          # local x = -(Z + 644), local z = X
    vault(Fv, -2.5, 2.5, GX0, GX1, spring, .875, 3)
    for k in range(3): chandelier(W, GX0 + (GX1 - GX0) * (k + .5) / 3, spring + .875, -644.0, .6, 2, 7, 1.1)
    # west end wall with the Rialto door (local x = -641.5 - Z)
    Fw, Lw = facade(B, (GX0, GZ1), (GX0, GZ0))
    door = [(.2, y), (4.8, y), (4.8, 9.54), (.2, 9.54)]
    lun = K.opening('segment', 2.5, y, 5.0, spring + .875 - y, 16)
    poly_faces(Fw, 'vi-lobby-stucco-gold', Polygon(lun).buffer(0).difference(Polygon(door)))
    for (ax, ay), (bx, by) in [((.2, y), (.2, 9.54)), ((.2, 9.54), (4.8, 9.54)), ((4.8, 9.54), (4.8, y))]:
        K.quad(Fw, 'vi-marble-cream', (ax, ay, 0), (bx, by, 0), (bx, by, -.2), (ax, ay, -.2))
    surround(Fw, door, 'vi-gilt-plain', [(0, 0), (0, .05), (.1, .07), (.12, .1), (.18, .1), (.2, 0)])
    # ---- landing hall: walls 6.26..11.24, entablature 9.9, cove, coffered ceiling with an oval fresco
    ENT = 9.9
    walls = []
    # west (facing east): local x = -636 - Z; the corridor opening
    F, Lw = facade(B, (LX0, LZ1), (LX0, LZ0))
    cor = K.opening('segment', -636.0 - (GZ0 + GZ1) / 2, y, 5.0, spring + .875 - y, 16)
    walls.append((F, Lw, [cor], [(5.5, 10.5, LCEIL)]))
    # south (facing north): local x = 252 - X
    F2, L2w = facade(B, (LX1, LZ1), (LX0, LZ1))
    walls.append((F2, L2w, [], []))
    # east (facing west): local x = Z + 652 (z -652..-636, includes the steps recess)
    F3, L3w = facade(B, (LX1, PORTAL_Z), (LX1, LZ1))
    walls.append((F3, L3w, [], []))
    # north stub (facing south, x 238..243) and the recess's west wall (facing east, z -648..-652)
    F4, L4w = facade(B, (LX0, LZ0), (SX0, LZ0))
    walls.append((F4, L4w, [], []))
    F5, L5w = facade(B, (SX0, LZ0), (SX0, PORTAL_Z))
    walls.append((F5, L5w, [], []))
    for F, Lw, holes, gaps in walls:
        wall(F, 'vi-lobby-stucco-gold', 0, Lw, y, LCEIL, holes, 0, 0)
        K.entablature(F, 0, Lw, ENT, 'vi-limestone', 'vi-gilt', 'vi-gilt-plain', 0, .7, True)
        solid_wall(F, 0, Lw, y, LCEIL, gaps)
    surround(walls[0][0], cor, 'vi-gilt-plain', [(0, 0), (0, .05), (.1, .07), (.12, .1), (.18, .1), (.2, 0)])
    skirting(walls[0][0], 0, walls[0][1], y, [(5.5, 10.5)])
    for x in [.35, 4.9, 11.1, 11.65]: pilaster(walls[0][0], x, y, ENT, w=.6, flutes=3)
    mirror(walls[0][0], .95, 6.9, 4.3, 9.5)
    # south wall: a large painting between pilasters, benches
    skirting(F2, 0, L2w, y)
    for x in [.35, 2.9, 11.1, 13.65]: pilaster(F2, x, y, ENT, w=.6, flutes=3)
    gilt_panel(F2, 3.6, 6.95, 10.4, 9.45, 'vi-fresco-b', prof=[(-.16, 0), (-.16, .06), (-.08, .12), (.08, .12), (.16, .06), (.16, 0)])
    for x in [242.0, 248.0]: sofa(B, x, LZ1 - .6, math.pi, 2.4, 'vi-velvet-red', y=RIALTO_Y)
    # east wall: mirror and panels
    skirting(F3, 0, L3w, y)
    for x in [4.35, 9.0, 15.65]: pilaster(F3, x, y, ENT, w=.6, flutes=3)
    mirror(F3, 5.2, 6.9, 8.2, 9.5)
    gilt_panel(F3, 9.8, 6.9, 14.9, 9.5, 'vi-lobby-ornament-blue')
    gilt_panel(F3, .6, 8.6, 3.8, 9.6, 'vi-coffer-green')
    skirting(F4, 0, L4w, y); gilt_panel(F4, .8, 7.0, 4.2, 9.4, 'vi-lobby-ornament-red')
    skirting(F5, 0, L5w, y)
    # cove + ceiling
    ring = [(LX0, PORTAL_Z), (LX1, PORTAL_Z), (LX1, LZ1), (LX0, LZ1)]
    Rc = .36
    K.sweep_plan(W, 'vi-stucco-white', ring, [(Rc - Rc * math.cos(t), Rc * math.sin(t)) for t in np.linspace(0, math.pi / 2, 5)], LCEIL - Rc, closed=True)
    coffer_field(W, LX0 + Rc, LX1 - Rc, PORTAL_Z + Rc, LZ1 - Rc, LCEIL, 5, 6, depth=.24, beam=.3,
                 panel=lambda i, j: ['vi-coffer-red', 'vi-coffer-green'][(i + j) % 2], skip=lambda i, j: 1 <= i <= 3 and 2 <= j <= 4,
                 holes=[sbox(LX0 + Rc + (LX1 - LX0 - 2 * Rc) / 5, PORTAL_Z + Rc + 2 * (LZ1 - PORTAL_Z - 2 * Rc) / 6,
                             LX0 + Rc + 4 * (LX1 - LX0 - 2 * Rc) / 5, PORTAL_Z + Rc + 5 * (LZ1 - PORTAL_Z - 2 * Rc) / 6)])
    ox0, oz0 = LX0 + Rc + (LX1 - LX0 - 2 * Rc) / 5, PORTAL_Z + Rc + 2 * (LZ1 - PORTAL_Z - 2 * Rc) / 6
    ox1, oz1 = LX0 + Rc + 4 * (LX1 - LX0 - 2 * Rc) / 5, PORTAL_Z + Rc + 5 * (LZ1 - PORTAL_Z - 2 * Rc) / 6
    ocx, ocz = (ox0 + ox1) / 2, (oz0 + oz1) / 2
    plan_faces(W, 'vi-gilt', sbox(ox0, oz0, ox1, oz1).difference(ellipse(ocx, ocz, (ox1 - ox0) / 2 - .5, (oz1 - oz0) / 2 - .4)), LCEIL)
    K.oval_fresco(W, ocx, LCEIL, ocz, (ox1 - ox0) / 2 - .5, (oz1 - oz0) / 2 - .4, 'vi-fresco-oval', 'vi-gilt', 40, .35)
    chandelier(W, ocx, LCEIL, ocz, 1.1, 3, 10, 1.9)
    # ---- steps up 1 m to the street (rising north, x 243..252, z -648 -> -651.75)
    flight(W, LZ0, PORTAL_Z, y, L2, SX0 + .1, SX1 - .1, 6, axis='z')
    plan_faces(W, 'vi-marble-cream', sbox(SX0, SZ1, SX1, PORTAL_Z), L2)
    K.solid_quad(W, (SX0, y, LZ0), (SX1, y, LZ0), (SX1, L2, PORTAL_Z), (SX0, L2, PORTAL_Z))
    K.solid_quad(W, (SX0, L2, PORTAL_Z), (SX1, L2, PORTAL_Z), (SX1, L2, SZ1), (SX0, L2, SZ1))
    for xh in [SX0 + .08, SX1 - .08]:
        K.tube(W, 'vi-gilt-plain', (xh, y + .95, LZ0 + .2), (xh, L2 + .95, PORTAL_Z + .1), .03, 6)
        for t in [.1, .5, .9]:
            zz = LZ0 + (PORTAL_Z - LZ0) * t; yy = y + (L2 - y) * t
            K.tube(W, 'vi-gilt-plain', (xh, yy + .95, zz), (xh + (.08 if xh < 247 else -.08), yy + .95, zz), .015, 4)
    K.lamp_post(W, SX0 - .5, LZ0 + .5, y, 3, 3.4, 'vi-gilt-plain', 'vi-lantern')
    # ---- gateway facade toward the street (facing north; local x = 252 - X)
    Fg, Lg = facade(B, (SX1, PORTAL_Z), (SX0, PORTAL_Z))
    gate = K.opening('segment', Lg / 2, L2, 7.6, 3.9, 16)
    wins = []
    for k, xc in enumerate([1.6, Lg / 2, Lg - 1.6]):
        wins.append(K.window(Fg, 'arch', xc, 13.1, 1.15, 2.3, 0, .22, 'vi-window-lit' if k == 1 else 'vi-window-dark', 'vi-limestone',
                             True, None, True, None, True, 'iron' if k != 1 else 'stone'))
    wall(Fg, 'vi-stucco-ochre', 0, Lg, L2, 16.8, [gate] + wins, 0, .25, 'vi-limestone', floor_y=L2)
    K.sweep_ring(Fg, 'vi-limestone', open_path(gate), K.P_ARCHIVOLT, 0, closed=False)
    K.box(Fg, 'vi-limestone', (Lg / 2, L2 + 3.9 + .25, .1), (.5, .6, .2))
    K.sweep_facade(Fg, 'vi-limestone', 0, Lg, L2, K.P_PLINTH)
    K.sweep_facade(Fg, 'vi-limestone', 0, Lg, 11.75, K.P_STRING)
    K.box(Fg, 'vi-wood-dark', (Lg / 2, 12.3, .06), (5.2, .55, .08))
    K.text(Fg, 'HOTEL LOBBY  ·  CASINO', Lg / 2, 12.16, .11, .3, 'vi-sign-gold')
    K.sweep_facade(Fg, 'vi-limestone', 0, Lg, 16.3, K.P_CORNICE_SMALL)
    for x in [.25, Lg - .25]:
        for kq, yy in enumerate(np.arange(L2 + .3, 16.2, .5)): K.box(Fg, 'vi-limestone', (x, yy, .03), (.5 if kq % 2 == 0 else .34, .42, .06))
    solid_wall(Fg, 0, Lg, L2, 16.8, [((Lg - 7.6) / 2, (Lg + 7.6) / 2, 10.0)])
    # ---- lights
    W.light(232.0, 9.0, -644.0, 0xffe2bc, 200, 12)
    W.light(ocx, 9.7, ocz, 0xffe6c4, 260, 16)
    W.light(247.5, 9.6, -650.0, 0xffe6c4, 200, 12)


# ------------------------------------------------------------------ Arrivals vestibule (under the gallery)
VX0, VX1, VZ0, VZ1, VCEIL = 229.0, 252.0, -646.4, -631.0, 5.94


def arrivals(B, W):
    B.source = 'lobby-rialto'
    y = L1
    # floor: cream field, rose border, black fillet, compass star
    out = sbox(228.6, VZ0, VX1, VZ1).difference(sbox(228.6, VZ0, VX0, -637.6))
    inner = sbox(229.6, VZ0 + .6, VX1 - .6, VZ1 - .6); fil = sbox(229.72, VZ0 + .72, VX1 - .72, VZ1 - .72)
    sc = (240.5, -638.7)
    disc = Point(*sc).buffer(2.2, 48); disc_in = Point(*sc).buffer(2.02, 48)
    star = []
    for i in range(16):
        a = i * TAU / 16; rr = 1.9 if i % 2 == 0 else (.6 if i % 4 == 1 else .6)
        star.append((sc[0] + rr * math.cos(a), sc[1] + rr * math.sin(a)))
    starp = Polygon(star)
    plan_faces(W, 'vi-lobby-marble-rose', out.difference(inner), y)
    plan_faces(W, 'vi-marble-black', inner.difference(fil), y)
    plan_faces(W, 'vi-diag-grid', fil.difference(disc), y)
    plan_faces(W, 'vi-marble-black', disc.difference(disc_in), y)
    plan_faces(W, 'vi-marble-cream', disc_in.difference(starp), y)
    for i in range(16):
        a = (i // 2) * TAU / 8; tip = (sc[0] + 1.9 * math.cos(a), sc[1] + 1.9 * math.sin(a))
        side = a + (1 if i % 2 else -1) * TAU / 16; inn = (sc[0] + .6 * math.cos(side), sc[1] + .6 * math.sin(side))
        K.face(W, 'vi-marble-rust' if i % 2 else 'vi-marble-black', [(sc[0], y + .001, sc[1]), (tip[0], y + .001, tip[1]), (inn[0], y + .001, inn[1])])
    plan_faces(W, 'vi-marble-black', sbox(229.0, VZ1, 235.0, -630.75), y)
    K.solid_quad(W, (228.6, y, VZ0), (VX1, y, VZ0), (VX1, y, -630.75), (228.6, y, -630.75))
    # walls
    ENT = 5.0
    specs = []
    Fs, Ls = facade(B, (VX1, VZ1), (228.6, VZ1))                    # south, local x = 252 - X
    door = [(VX1 - 235.0, y), (VX1 - 229.0, y), (VX1 - 229.0, 4.74), (VX1 - 235.0, 4.74)]
    specs.append((Fs, Ls, [door], [(VX1 - 235.0, VX1 - 229.0, 4.74)], .25))
    Fn, Ln = facade(B, (VX0, VZ0), (VX1, VZ0))                       # north, local x = X - 229
    specs.append((Fn, Ln, [], [], 0))
    Fe, Le = facade(B, (VX1, VZ0), (VX1, VZ1))                       # east, local x = Z + 646.4
    edoor = [(2.9, y), (9.9, y), (9.9, 5.0), (2.9, 5.0)]
    specs.append((Fe, Le, [edoor], [(2.9, 9.9, 5.0)], 1.0))
    Fw1, Lw1 = facade(B, (VX0, -637.6), (VX0, VZ0))                  # west (north part)
    specs.append((Fw1, Lw1, [], [], 0))
    Fj, Lj = facade(B, (228.6, -637.6), (VX0, -637.6))               # the jog (facing south)
    specs.append((Fj, Lj, [], [], 0))
    Fw2, Lw2 = facade(B, (228.6, VZ1), (228.6, -637.6))              # west (south part)
    specs.append((Fw2, Lw2, [], [], 0))
    for F, Lw, holes, gaps, rev in specs:
        wall(F, 'vi-stucco-cream', 0, Lw, y, VCEIL, holes, 0, rev, 'vi-marble-cream', floor_y=y)
        if Lw > 1:
            dado(F, 0, Lw, y, .9, [(h[0][0], h[1][0]) for h in holes])
            K.entablature(F, 0, Lw, ENT, 'vi-limestone', 'vi-gilt', 'vi-gilt-plain', 0, .5, True)
        skirting(F, 0, Lw, y, [(h[0][0], h[1][0]) for h in holes])
        solid_wall(F, 0, Lw, y, VCEIL, gaps)
    surround(Fs, door, 'vi-bronze', [(0, 0), (0, .06), (.08, .08), (.12, .12), (.2, .12), (.22, 0)])
    surround(Fe, edoor, 'vi-limestone')
    K.text(Fe, 'GRAND COLONNADE', 6.4, 5.27, .045, .17, 'vi-sign-gold')
    # pilasters and panels
    for x in [.4, 8.0, 15.6, 22.6]: pilaster(Fn, x, y + .9, ENT, w=.6, flutes=3)
    for k, (x0, x1) in enumerate([(1.1, 7.3), (8.7, 14.9), (16.3, 21.9)]):
        if k == 1: gilt_panel(Fn, x0, 1.5, x1, 4.4, 'vi-fresco-a', prof=[(-.14, 0), (-.14, .05), (-.07, .1), (.07, .1), (.14, .05), (.14, 0)])
        else: mirror(Fn, x0, 1.5, x1, 4.4)
    for x in [.4, 5.3, 10.2, 15.4]: pilaster(Fs, x, y + .9, ENT, w=.6, flutes=3)
    for k, xc in enumerate([2.85, 7.75, 12.8]):
        arched_mirror(Fs, xc, 1.2, 2.6, 3.5)
    for x in [.4, 2.3, 10.5, 15.0]: pilaster(Fe, x, y + .9, ENT, w=.6, flutes=3)
    gilt_panel(Fe, 11.7, 1.5, 14.6, 4.3, 'vi-lobby-ornament-blue')
    gilt_panel(Fw1, 1.0, 1.4, 7.8, 4.4, 'vi-fresco-b', prof=[(-.14, 0), (-.14, .05), (-.07, .1), (.07, .1), (.14, .05), (.14, 0)])
    gilt_panel(Fw2, 1.2, 1.5, 5.4, 4.3, 'vi-lobby-ornament-red')
    # ceiling: coffers and the entrance's oval fresco
    coffer_field(W, VX0, VX1, VZ0, VZ1, VCEIL, 9, 6, depth=.18, beam=.28,
                 panel=lambda i, j: 'vi-coffer-cream', skip=lambda i, j: 3 <= i <= 5 and 1 <= j <= 4, rosette=True,
                 holes=[sbox(VX0 + 3 * 23 / 9, VZ0 + 15.4 / 6, VX0 + 6 * 23 / 9, VZ0 + 5 * 15.4 / 6)])
    plan_faces(W, 'vi-gilt', sbox(VX0 + 3 * 23 / 9, VZ0 + 15.4 / 6, VX0 + 6 * 23 / 9, VZ0 + 5 * 15.4 / 6).difference(ellipse(sc[0], sc[1], 3.4, 4.6)), VCEIL)
    K.oval_fresco(W, sc[0], VCEIL, sc[1], 3.4, 4.6, 'vi-fresco-oval', 'vi-gilt', 40, .25)
    K.sweep_plan(W, 'vi-gilt-plain', [(228.6, VZ0), (VX1, VZ0), (VX1, VZ1), (228.6, VZ1)], [(0, 0), (0, -.08), (.1, -.08), (.12, 0)], VCEIL, closed=True)
    chandelier(W, sc[0], VCEIL + .2, sc[1], .75, 2, 8, .9)
    # furniture: a round table with flowers on the star, benches, lamps by the door
    K.lathe(W, 'vi-gilt-plain', sc[0], sc[1], [(y, .45), (y + .1, .4), (y + .2, .14), (y + .7, .1), (y + .76, .2)], 12)
    K.lathe(W, 'vi-marble-green', sc[0], sc[1], [(y + .76, .001), (y + .76, .95), (y + .82, .95), (y + .82, .001)], 24)
    K.lathe(W, 'vi-gilt-plain', sc[0], sc[1], [(y + .82, .3), (y + .9, .34), (y + 1.2, .26), (y + 1.3, .32)], 12)
    flowers(W, sc[0], sc[1], y + 1.25, .8, 3)
    K.solid_box(W, (sc[0], y + .45, sc[1]), (1.9, .9, 1.9))
    for x in [244.5, 249.0]: sofa(B, x, VZ0 + .75, 0, 2.2)
    K.lamp_post(W, 236.4, VZ1 - .75, y, 3, 3.2, 'vi-gilt-plain', 'vi-lantern', True)
    for k, zz in enumerate((-645.3, -634.7)): urn(W, 250.9, zz, y, .9, 11 + k)
    plan_faces(W, 'vi-gilt', sbox(228.6, -637.6, VX0, VZ1), VCEIL)
    W.light(sc[0], 5.0, sc[1], 0xffe2bc, 240, 16)
    W.light(248.5, 4.9, -638.7, 0xffe2bc, 180, 12)


# ------------------------------------------------------------------ Colonnade
CX0, CX1, CZ0, CZ1 = 253.0, 316.0, -646.8, -633.2       # inner faces
CN, CS = -644.21, -635.79                               # column lines; vault span 8.42, spring 7.03, crown 11.24
CSPRING = 7.03
BAY = 6.3


def colonnade(B, W):
    B.source = 'lobby-colonnade'
    y = L1
    # floor: diagonal checker with a rust border
    plan_faces(W, 'vi-marble-rust', sbox(CX0, CZ0, CX1, CZ1).difference(sbox(CX0 + .45, CZ0 + .45, CX1 - .45, CZ1 - .45)), y)
    plan_faces(W, 'vi-checker', sbox(CX0 + .45, CZ0 + .45, CX1 - .45, CZ1 - .45), y)
    plan_faces(W, 'vi-marble-black', sbox(252.0, -643.5, CX0, -636.5), y)
    K.solid_quad(W, (252.0, y, CZ0), (CX1, y, CZ0), (CX1, y, CZ1), (252.0, y, CZ1))
    # paired columns on pedestals
    Fp = Frame(B, 0, 0, 0, y=1.14)
    for k in range(1, 10):
        X = CX0 + BAY * k
        for zl in (CN, CS):
            K.box(W, 'vi-marble-cream', (X, .69, zl), (2.2, .9, .95))
            K.box(W, 'vi-marble-cream', (X, .32, zl), (2.36, .16, 1.11)); K.box(W, 'vi-marble-cream', (X, 1.08, zl), (2.36, .12, 1.11))
            for s in (-1, 1):
                K.box(W, 'vi-lobby-marble-siena', (X, .69, zl + s * .48), (1.7, .5, .02))
            for s in (-1, 1):
                K.column(Fp, X + s * .62, zl, 5.9 - 1.14, .27, 'vi-marble-cream', 'vi-gilt-plain', 'vi-limestone', 'corinthian', 18, solid=False)
            K.solid_box(W, (X, y + 2.85, zl), (2.2, 5.7, .95))
    # entablatures over the column lines, beams behind, aisle soffits, caps
    Fen, Lc = facade(B, (CX0, CN + .25), (CX1, CN + .25))
    Fes, _ = facade(B, (CX1, CS - .25), (CX0, CS - .25))
    for F in (Fen, Fes): K.entablature(F, 0, Lc, 5.9, 'vi-limestone', 'vi-lobby-stucco-gold', 'vi-gilt-plain', 0, .8, True)
    for face, back, wallz in ((CN + .25, CN + .25 - .54, CZ0), (CS - .25, CS - .25 + .54, CZ1)):
        K.box(W, 'vi-limestone', ((CX0 + CX1) / 2, 6.46, (face + back) / 2), (Lc, 1.12, .54))
        K.quad(W, 'vi-limestone', (CX0, 7.022, wallz), (CX1, 7.022, wallz), (CX1, 7.022, face), (CX0, 7.022, face))
    for z0, z1 in ((CZ0, CN - .29), (CS + .29, CZ1)):
        coffer_field(W, CX0, CX1, z0, z1, 5.9, 30, 1, depth=.16, beam=.26, panel=lambda i, j: 'vi-coffer-cream',
                     plane='vi-stucco-white', side='vi-gilt-plain', rosette=False)
    # the painted barrel vault
    Fv = Frame(B, 0, -640.0, math.pi / 2, y=0)          # local x = -(Z + 640), local z = X
    K.barrel_vault(Fv, -4.21, 4.21, CX0, CX1, CSPRING, 10, n=24)
    for k in range(10):
        chandelier(W, CX0 + BAY * (k + .5), 11.24 - .02, -640.0, .95, 2, 9, 1.9)
    # end walls with lunettes: west (facing east; local x = -633.2 - Z), east (facing west; local x = Z + 646.8)
    Fw, Lw = facade(B, (CX0, CZ1), (CX0, CZ0))
    Fe, Le = facade(B, (CX1, CZ0), (CX1, CZ1))
    for F, Lx, op, fresco, sign, pil in [(Fw, Lw, [(3.3, y), (10.3, y), (10.3, 5.0), (3.3, 5.0)], 'vi-fresco-b', 'RIALTO BRIDGE  ·  ARRIVALS', (2.59, 11.01, .5, Lw - .5)),
                                          (Fe, Le, [(.8, y), (12.8, y), (12.8, 5.9), (.8, 5.9)], 'vi-fresco-a', None, (.4, Le - .4))]:
        wall(F, 'vi-lobby-stucco-gold', 0, Lx, y, CSPRING, [op], 0, 0)
        mid = Lx / 2
        lun = [(mid + 4.21 * math.cos(a), CSPRING + 4.21 * math.sin(a)) for a in np.linspace(0, math.pi, 25)]
        K.pane(F, fresco, lun, .01)
        K.sweep_arc(F, 'vi-gilt', mid, CSPRING, .0, 4.21, 0, math.pi, [(0, 0), (-.06, .03), (-.1, .1), (-.22, .14), (-.3, .1), (-.32, 0)], 24)
        K.entablature(F, 0, Lx, 5.9, 'vi-limestone', 'vi-lobby-stucco-gold', 'vi-gilt-plain', 0, .8, True)
        surround(F, op, 'vi-limestone')
        for x in pil: pilaster(F, x, y, 5.9, w=.5, flutes=3)
        skirting(F, 0, Lx, y, [(op[0][0], op[1][0])])
        solid_wall(F, 0, Lx, y, CSPRING, [(op[0][0], op[1][0], op[2][1])])
        if sign:
            K.box(F, 'vi-velvet-red', (mid, 5.45, .03), (5.0, .4, .04))
            K.text(F, sign, mid, 5.35, .06, .22, 'vi-sign-gold')
    # side walls (aisles), 0.24..5.9: dado, wall responds, mirrors / doors / paintings
    for a, b, flip in [((CX0, CZ0), (CX1, CZ0), False), ((CX1, CZ1), (CX0, CZ1), True)]:
        F, Lx = facade(B, a, b)
        wall(F, 'vi-lobby-stucco-gold', 0, Lx, y, 5.95)
        def lx(X): return (X - CX0) if not flip else (CX1 - X)
        doors = [(lx(CX0 + BAY * (k + .5)) - 1.45, lx(CX0 + BAY * (k + .5)) + 1.45) for k in range(10) if (k % 4 if not flip else (k + 2) % 4) == 1]
        dado(F, 0, Lx, y, .9, doors, d=.08)
        skirting(F, 0, Lx, y, doors)
        K.sweep_facade(F, 'vi-gilt-plain', 0, Lx, 5.72, [(0, 0), (.06, 0), (.06, .06), (.1, .1), (.1, .18), (0, .18)])
        for k in range(1, 10):
            for s in (-1, 1): pilaster(F, lx(CX0 + BAY * k + s * .62), y + .9, 5.72, w=.5, d=.12, flutes=3)
        for k in range(10):
            xc = lx(CX0 + BAY * (k + .5))
            kind = k % 4 if not flip else (k + 2) % 4
            if kind in (0, 2):
                arched_mirror(F, xc, 1.25, 2.5, 3.95)
                K.box(F, 'vi-limestone', (xc, 1.2, .07), (2.9, .1, .14))
            elif kind == 1:
                ring = K.opening('arch', xc, y, 2.3, 3.5, 12)
                K.pane(F, 'vi-wood-dark', ring, .02)
                K.box(F, 'vi-gilt-plain', (xc, y + 1.6, .05), (.04, 2.4, .04))
                for s in (-1, 1): K.box(F, 'vi-gilt-plain', (xc + s * .18, 1.35, .07), (.05, .3, .05))
                surround(F, ring, 'vi-limestone')
                gilt_panel(F, xc - 1.3, 4.15, xc + 1.3, 5.1, 'vi-lobby-ornament-blue')
            else:
                gilt_panel(F, xc - 1.6, 2.0, xc + 1.6, 4.4, ['vi-fresco-a', 'vi-fresco-b'][k % 2],
                           prof=[(-.14, 0), (-.14, .05), (-.07, .1), (.07, .1), (.14, .05), (.14, 0)])
        K.solid_quad(F, (0, y, 0), (Lx, y, 0), (Lx, 5.9, 0), (0, 5.9, 0))
    # urns of flowers by the pedestals
    for k, zl, s in [(2, CN, 1), (2, CS, -1), (7, CN, 1), (7, CS, -1)]:
        urn(W, CX0 + BAY * k, zl + s * 1.1, y, 1.0, k)
    for k in range(5): W.light(CX0 + BAY * (2 * k + 1), 9.4, -640.0, 0xffe6c4, 270, 18)


# ------------------------------------------------------------------ Rotunda and the Armillary Sphere
RCX, RCZ, RR = 328.0, -640.0, 10.8
OPEN = {'E': (-33.75, 33.75), 'W': (146.25, 213.75), 'N': (236.25, 303.75)}
WALLS = [(33.75, 146.25), (213.75, 236.25), (303.75, 326.25)]


def rp(r, deg, y=0.0):
    a = math.radians(deg); return (RCX + r * math.cos(a), y, RCZ + r * math.sin(a))


def rotunda(B, W):
    B.source = 'lobby-rotunda'
    y = L1
    # floor rings and the passages
    def ringf(mat, r0, r1, n=64, a0=0, a1=TAU):
        K.lathe(W, mat, RCX, RCZ, [(y, r0), (y, r1)], n, 0, a0, a1)
    ringf('vi-marble-black', 3.78, 4.35)
    for i in range(24):
        ringf(['vi-lobby-marble-rose', 'vi-marble-cream'][i % 2], 4.35, 8.2, 4, i * TAU / 24, (i + 1) * TAU / 24)
    ringf('vi-marble-rust', 8.2, 8.6)
    ringf('vi-checker', 8.6, RR, 72)
    circ = Point(RCX, RCZ).buffer(RR, 96)
    for rect in [sbox(316.0, -646.0, 320.0, -634.0), sbox(322.0, -652.0, 334.0, -648.0), sbox(336.0, -646.0, 339.2, -634.0)]:
        plan_faces(W, 'vi-checker', rect.difference(circ), y)
    K.solid_quad(W, (316.0, y, -652.0), (339.2, y, -652.0), (339.2, y, -629.0), (316.0, y, -629.0))
    # drum wall r 10.8, 0.24..6.4, openings W/E to 5.9 and N to 4.6 (the casino's header on its side starts at 5.24)
    tops = {'E': 5.9, 'W': 5.9, 'N': 4.6}
    def drum(mat, r, y0, y1, a0, a1, step=3.0):
        n = max(1, int(round((a1 - a0) / step)))
        A = np.linspace(a0, a1, n + 1)
        for i in range(n):
            p0, p1 = rp(r, A[i]), rp(r, A[i + 1])
            K.quad(W, mat, (p0[0], y0, p0[2]), (p1[0], y0, p1[2]), (p1[0], y1, p1[2]), (p0[0], y1, p0[2]))
    for a0, a1 in WALLS:
        drum('vi-lobby-stucco-gold', RR, y, 6.4, a0, a1)
        K.lathe(W, 'vi-marble-cream', RCX, RCZ, [(y, RR - .07), (y + .9, RR - .07), (y + .9, RR)], max(2, int((a1 - a0) / 3)), 0, math.radians(a0), math.radians(a1))
        K.lathe(W, 'vi-marble-cream', RCX, RCZ, [(y + .9, RR - .09), (y + .96, RR - .09), (y + 1.0, RR - .05), (y + 1.0, RR)], max(2, int((a1 - a0) / 3)), 0, math.radians(a0), math.radians(a1))
        K.lathe(W, 'vi-marble-black', RCX, RCZ, [(y, RR - .1), (y + .2, RR - .1), (y + .22, RR - .07)], max(2, int((a1 - a0) / 3)), 0, math.radians(a0), math.radians(a1))
        n = max(2, int((a1 - a0) / 3)); A = np.linspace(a0, a1, n + 1)
        for i in range(n):
            p0, p1 = rp(RR, A[i]), rp(RR, A[i + 1])
            K.solid_quad(W, (p0[0], y, p0[2]), (p1[0], y, p1[2]), (p1[0], 6.4, p1[2]), (p0[0], 6.4, p0[2]))
    for k, (a0, a1) in OPEN.items():
        drum('vi-lobby-stucco-gold', RR, tops[k], 6.4, a0, a1)
    # passages: W (x 316..drum), N (z -652..drum), E (drum..339.2)
    zw = math.sqrt(RR ** 2 - 36)
    for a, b, top in [((316.0, -646.0), (RCX - zw, -646.0), 5.9), ((RCX - zw, -634.0), (316.0, -634.0), 5.9),
                      ((322.0, -648.9), (322.0, -652.0), 4.6), ((334.0, -652.0), (334.0, -648.9), 4.6),
                      ((RCX + zw, -646.0), (339.2, -646.0), 5.9), ((339.2, -634.0), (RCX + zw, -634.0), 5.9)]:
        F, Lp = facade(B, a, b)
        wall(F, 'vi-lobby-stucco-gold', 0, Lp, y, top)
        K.box(F, 'vi-marble-cream', (Lp / 2, y + .45, .03), (Lp, .9, .06))
        K.solid_quad(F, (0, y, 0), (Lp, y, 0), (Lp, top, 0), (0, top, 0))
    for rect, top in [(sbox(316.0, -646.0, 320.0, -634.0), 5.9), (sbox(322.0, -652.0, 334.0, -648.0), 4.6), (sbox(336.0, -646.0, 339.2, -634.0), 5.9)]:
        plan_faces(W, 'vi-coffer-cream', rect.difference(circ), top)
        b = rect.difference(circ).bounds
        K.sweep_plan(W, 'vi-gilt-plain', [(b[0], b[1]), (b[2], b[1]), (b[2], b[3]), (b[0], b[3])], [(0, 0), (0, -.08), (.12, -.08), (.14, 0)], top, closed=True)
    # the casino side of the north passage (facing north, plane z -651.75; local x = 339 - X)
    Fc, Lcf = facade(B, (339.0, -651.75), (317.0, -651.75))
    op = [(5.0, y), (17.0, y), (17.0, 4.6), (5.0, 4.6)]
    wall(Fc, 'vi-lobby-stucco-gold', 0, Lcf, y, 6.04, [op], 0, .1, 'vi-marble-cream', floor_y=y)
    surround(Fc, op, 'vi-gilt-plain', [(0, 0), (0, .05), (.1, .07), (.12, .1), (.2, .1), (.22, 0)])
    for x in [.4, 4.3, 17.7, 21.6]: pilaster(Fc, x, y, 5.95, w=.6, d=.14, flutes=3)
    for x0, x1 in [(1.0, 3.7), (18.3, 21.0)]: mirror(Fc, x0, 1.2, x1, 4.9)
    K.box(Fc, 'vi-velvet-red', (11.0, 4.93, .04), (6.0, .36, .06))
    K.text(Fc, 'HOTEL LOBBY  ·  REGISTRATION', 11.0, 4.84, .08, .2, 'vi-sign-gold')
    skirting(Fc, 0, Lcf, y, [(5.0, 17.0)])
    solid_wall(Fc, 0, Lcf, y, 6.04, [(5.0, 17.0, 4.6)])
    # south wall: a painting in an aedicule, two framed panels (each on a plane tangent to the drum)
    def tframe(deg, w):
        px, _, pz = rp(RR - (RR - math.sqrt(RR * RR - w * w / 4)) - .03, deg)
        return Frame(B, px, pz, math.atan2(-math.cos(math.radians(deg)), -math.sin(math.radians(deg))), y=0)
    for deg, mat, w, h, y0 in [(90, 'vi-fresco-a', 4.6, 3.2, 1.7), (64, 'vi-lobby-ornament-blue', 1.8, 3.0, 1.6), (116, 'vi-lobby-ornament-blue', 1.8, 3.0, 1.6)]:
        gilt_panel(tframe(deg, w + .3), -w / 2, y0, w / 2, y0 + h, mat, prof=[(-.14, 0), (-.14, .05), (-.07, .1), (.07, .1), (.14, .05), (.14, 0)])
    for s in (-1, 1): pilaster(tframe(90 + s * 15.5, .7), 0, y + .9, 5.6, w=.5, d=.14, flutes=3)
    K.lathe(W, 'vi-limestone', RCX, RCZ, [(5.6, RR), (5.6, RR - .1), (5.68, RR - .16), (5.76, RR - .28), (5.84, RR - .28), (5.84, RR)], 12, 0,
            math.radians(90 - 18), math.radians(90 + 18))
    sofa(B, *[rp(RR - 1.4, 90)[i] for i in (0, 2)], math.atan2(-math.cos(math.radians(90)), -math.sin(math.radians(90))), 2.6)
    # column ring: pairs at the diagonals, pedestals facing the centre
    for d0 in (45, 135, 225, 315):
        for dd in (-6, 6):
            deg = d0 + dd; px, _, pz = rp(9.6, deg)
            F = Frame(B, px, pz, math.atan2(-math.cos(math.radians(deg)), -math.sin(math.radians(deg))), y=0)
            K.box(F, 'vi-marble-cream', (0, .69, 0), (.95, .9, .95))
            K.box(F, 'vi-marble-cream', (0, .32, 0), (1.1, .16, 1.1)); K.box(F, 'vi-marble-cream', (0, 1.08, 0), (1.1, .12, 1.1))
            K.box(F, 'vi-lobby-marble-siena', (0, .69, .48), (.6, .5, .02))
            K.column(Frame(B, px, pz, 0, y=1.14), 0, 0, 6.4 - 1.14, .3, 'vi-marble-cream', 'vi-gilt-plain', 'vi-limestone', 'corinthian', 18, solid=False)
            K.solid_box(W, (px, y + 3.1, pz), (.95, 6.2, .95))
        # an urn in a niche-like panel on the wall behind each pair
        px, _, pz = rp(RR - .05, d0)
        F = Frame(B, px, pz, math.atan2(-math.cos(math.radians(d0)), -math.sin(math.radians(d0))), y=0)
        arched_panel(F, 0, 1.3, 1.5, 3.6, 'vi-lobby-ornament-red')
    # ring entablature (inner face r 9.35), its soffit, the ambulatory ceiling, attic, cornice
    circle = [(RCX + 9.35 * math.cos(a), RCZ + 9.35 * math.sin(a)) for a in np.linspace(0, TAU, 72, endpoint=False)]
    K.sweep_plan(W, 'vi-limestone', circle, [(0, 0), (.04, 0), (.04, .2), (.07, .22), (.07, .4), (.1, .44), (0, .44)], 6.4, closed=True)
    K.sweep_plan(W, 'vi-gilt', circle, [(0, 0), (.03, 0), (.03, .42), (0, .42)], 6.84, closed=True)
    K.sweep_plan(W, 'vi-limestone', circle, [(0, 0), (.05, 0), (.05, .06), (.16, .16), (.3, .2), (.36, .26), (.36, .33), (0, .33)], 7.26, closed=True)
    K.lathe(W, 'vi-limestone', RCX, RCZ, [(6.4, 9.85), (7.59, 9.85)], 72)
    K.lathe(W, 'vi-limestone', RCX, RCZ, [(6.4, 9.35), (6.4, 9.85)], 72)
    K.lathe(W, 'vi-stucco-white', RCX, RCZ, [(6.4, 9.85), (6.4, RR)], 72)
    for rr in (9.95, 10.65): K.lathe(W, 'vi-gilt-plain', RCX, RCZ, [(6.399, rr - .04), (6.36, rr), (6.399, rr + .04)], 72)
    K.lathe(W, 'vi-lobby-stucco-gold', RCX, RCZ, [(7.59, 9.36), (8.64, 9.36)], 72)
    for i in range(16):
        a0, a1 = math.radians(i * 22.5 + 3.5), math.radians((i + 1) * 22.5 - 3.5)
        K.lathe(W, 'vi-lobby-ornament-blue', RCX, RCZ, [(7.76, 9.34), (8.44, 9.34)], 3, 0, a0, a1)
        pts = [(RCX + 9.32 * math.cos(a), yy, RCZ + 9.32 * math.sin(a)) for a, yy in
               [(a0, 7.76), (a1, 7.76), (a1, 8.44), (a0, 8.44), (a0, 7.76)]]
        arc = []
        for (p, q) in zip(pts, pts[1:]):
            arc.append(p)
            if abs(p[1] - q[1]) < 1e-6:
                aa, bb = math.atan2(p[2] - RCZ, p[0] - RCX), math.atan2(q[2] - RCZ, q[0] - RCX)
                if bb - aa > math.pi: bb -= TAU
                if aa - bb > math.pi: bb += TAU
                for t in np.linspace(0, 1, 4)[1:-1]:
                    aa2 = aa + (bb - aa) * t; arc.append((RCX + 9.32 * math.cos(aa2), p[1], RCZ + 9.32 * math.sin(aa2)))
        arc.append(pts[-1])
        K.path(W, 'vi-gilt-plain', arc, .03, 4)
    K.sweep_plan(W, 'vi-limestone', circle, [(0, 0), (.04, 0), (.12, .08), (.2, .12), (.2, .2), (0, .2)], 8.64, closed=True)
    # the dome: base r 9.15 at 8.84, top 15.24; 16 ornament panels, gilt ribs, a painted sky, a fresco at the crown
    yb, Rd, rise = 8.84, 9.15, 6.4
    def D(phi, deg, inset=0.0):
        a = math.radians(deg); r = (Rd - inset) * math.cos(phi); return (RCX + r * math.cos(a), yb + (rise - inset * .7) * math.sin(phi), RCZ + r * math.sin(a))
    p0, p1, p2 = 0.0, math.radians(38), math.radians(72)
    for i in range(16):
        d0, d1 = i * 22.5 + 1.3, (i + 1) * 22.5 - 1.3
        PH = np.linspace(p0 + .01, p1 - .01, 6); AZ = np.linspace(d0, d1, 4)
        for j in range(5):
            for k in range(3):
                K.quad(W, ['vi-coffer-red', 'vi-coffer-green'][i % 2], D(PH[j], AZ[k]), D(PH[j], AZ[k + 1]), D(PH[j + 1], AZ[k + 1]), D(PH[j + 1], AZ[k]))
        # the rib between this panel and the next
        dr = (i + 1) * 22.5
        PH2 = np.linspace(p0, p2, 14)
        pts = [np.array(D(ph, dr)) for ph in PH2]
        ns = []
        for ph in PH2:
            a = math.radians(dr); nrm = np.array([-math.cos(ph) * math.cos(a) / Rd, -math.sin(ph) / rise, -math.cos(ph) * math.sin(a) / Rd])
            ns.append(nrm / np.linalg.norm(nrm))
        tang = np.array([-math.sin(math.radians(dr)), 0, math.cos(math.radians(dr))])
        K.sweep_frames(W, 'vi-gilt', pts, ns, [tang] * len(pts), [(0, -.19), (.1, -.19), (.15, -.1), (.15, .1), (.1, .19), (0, .19)])
        # gaps between panels: a strip of field behind the rib
        PHg = np.linspace(p0, p1, 6)
        for j in range(5):
            K.quad(W, 'vi-stucco-white', D(PHg[j], dr - 1.3), D(PHg[j], dr + 1.3), D(PHg[j + 1], dr + 1.3), D(PHg[j + 1], dr - 1.3))
    PH = np.linspace(p1, p2, 7)
    for j in range(6):
        K.lathe(W, 'vi-sky-day', RCX, RCZ, [(yb + rise * math.sin(PH[j]), Rd * math.cos(PH[j])), (yb + rise * math.sin(PH[j + 1]), Rd * math.cos(PH[j + 1]))], 48)
    for ph in (p0 + .005, p1, p2):
        rr, yy = Rd * math.cos(ph), yb + rise * math.sin(ph)
        K.lathe(W, 'vi-gilt', RCX, RCZ, [(yy - .12, rr + .02), (yy - .06, rr - .14), (yy + .06, rr - .14), (yy + .12, rr + .02)], 64)
    rr, yy = Rd * math.cos(p2), yb + rise * math.sin(p2)
    K.oval_fresco(W, RCX, yy, RCZ, rr, rr, 'vi-fresco-oval', 'vi-gilt', 40, 15.24 - yy)
    # lights
    W.light(RCX, 10.0, RCZ, 0xffe6c4, 320, 22)
    W.light(320.5, 5.3, -633.5, 0xffe2bc, 200, 14)
    W.light(335.5, 5.3, -646.5, 0xffe2bc, 200, 14)


def armillary(B, W):
    B.source = 'lobby-rotunda'
    x, z = RCX, RCZ
    rose = 'vi-lobby-marble-rose'
    # the fountain: outer basin, water, upper basin, water
    K.lathe(W, rose, x, z, [(L1, 3.8), (.36, 3.8), (.4, 3.68), (.72, 3.62), (.78, 3.72), (.86, 3.74), (.92, 3.62), (.94, 3.44), (.86, 3.4), (.6, 3.4)], 48)
    K.disc(W, 'water', x, .66, z, 3.41, 48)
    K.lathe(W, rose, x, z, [(.6, 2.1), (1.26, 2.1), (1.34, 2.22), (1.42, 2.22), (1.48, 2.06), (1.42, 1.98), (1.3, 1.98)], 36)
    K.disc(W, 'water', x, 1.36, z, 1.99, 36)
    for i in range(8):
        a = i * TAU / 8 + TAU / 16
        K.box(W, 'vi-gilt-plain', (x + 3.78 * math.cos(a), .56, z + 3.78 * math.sin(a)), (.04, .16, .04))
    # the gilt base and four kneeling atlantes
    K.lathe(W, 'vi-gilt', x, z, [(1.3, 1.25), (1.55, 1.25), (1.62, 1.12), (1.85, 1.0), (1.95, 1.18), (2.04, 1.28), (2.1, 1.28), (2.12, 1.0)], 28)
    K.lathe(W, 'vi-gilt-plain', x, z, [(2.0, .32), (2.2, .24), (2.6, .15), (2.9, .22), (3.05, .13), (3.2, .2), (3.38, .16)], 12)
    for k in range(4):
        atlas(B, x, z, 45 + 90 * k, 2.1)
        b = math.radians(90 * k); cb, sb = math.cos(b), math.sin(b)
        K.tube(W, 'vi-gilt', (x + .74 * cb, 2.3, z + .74 * sb), (x + .9 * cb, 2.3, z + .9 * sb), .34, 14)
        K.path(W, 'vi-gilt-plain', [(x + .92 * cb - sb * .28 * (1 - t * .8) * math.cos(t * 9), 2.3 + .28 * (1 - t * .8) * math.sin(t * 9),
                                     z + .92 * sb + cb * .28 * (1 - t * .8) * math.cos(t * 9)) for t in np.linspace(0, 1, 14)], .035, 5)
        K.sphere(W, 'vi-gilt-plain', (x + .94 * cb, 2.3, z + .94 * sb), .07, 6, 4)
    # the armillary: rings about the centre, the celestial axis tilted 36 degrees toward the north
    C = np.array([x, 5.4, z]); R = 1.85
    lat = math.radians(36); obl = math.radians(23.4)
    ax = np.array([0, math.cos(lat), -math.sin(lat)]); e1 = np.array([1., 0, 0]); e2 = np.cross(ax, e1); e2 /= np.linalg.norm(e2)
    band = lambda w, t: [(-t, -w), (t, -w), (t, w), (-t, w), (-t, -w)]
    ring_band(W, 'vi-gilt', C, [0, 1, 0], [0, 0, 1], R + .12, band(.08, .035), 56)            # meridian
    ring_band(W, 'vi-gilt', C, [1, 0, 0], [0, 0, 1], R + .12, [(-.15, -.025), (.15, -.025), (.15, .025), (-.15, .025), (-.15, -.025)], 56)  # horizon
    ring_band(W, 'vi-gilt-plain', C, e1, e2, R, band(.05, .03), 48)                            # equator
    ring_band(W, 'vi-gilt', C, e1, math.cos(obl) * e2 + math.sin(obl) * ax, R, band(.13, .03), 48)   # ecliptic (zodiac band)
    for s in (-1, 1):
        ring_band(W, 'vi-gilt-plain', C + s * ax * R * math.sin(obl), e1, e2, R * math.cos(obl), band(.03, .025), 40)     # tropics
        ring_band(W, 'vi-gilt-plain', C + s * ax * R * math.cos(obl), e1, e2, R * math.sin(obl), band(.025, .02), 24)     # polar circles
    ring_band(W, 'vi-gilt-plain', C, ax, e1, R - .03, band(.04, .03), 48)                      # colure
    K.tube(W, 'vi-gilt-plain', tuple(C - ax * (R + .45)), tuple(C + ax * (R + .45)), .045, 8)
    for s in (-1, 1): K.sphere(W, 'vi-gilt-plain', tuple(C + s * ax * (R + .5)), .1, 8, 6)
    K.sphere(W, 'vi-gilt', tuple(C), .38, 14, 9)
    # zodiac studs on the ecliptic
    v2 = math.cos(obl) * e2 + math.sin(obl) * ax; nrm = np.cross(e1, v2)
    for i in range(12):
        a = i * TAU / 12 + TAU / 24; p = C + (R + .04) * (math.cos(a) * e1 + math.sin(a) * v2)
        K.sphere(W, 'vi-gilt-plain', tuple(p), .06, 6, 4)
    # cradle and crown finial
    K.lathe(W, 'vi-gilt', x, z, [(3.3, .16), (3.36, .26), (3.44, .2), (3.48, .1)], 10)
    top = 5.4 + R + .12 + .035
    K.lathe(W, 'vi-gilt-plain', x, z, [(top, .08), (top + .08, .15), (top + .22, .09), (top + .36, .17), (top + .5, .06), (top + .66, .001)], 10)
    # collision: an octagon around the basin
    for i in range(8):
        a0, a1 = i * TAU / 8, (i + 1) * TAU / 8
        K.solid_quad(W, (x + 3.9 * math.cos(a0), L1, z + 3.9 * math.sin(a0)), (x + 3.9 * math.cos(a1), L1, z + 3.9 * math.sin(a1)),
                     (x + 3.9 * math.cos(a1), 1.3, z + 3.9 * math.sin(a1)), (x + 3.9 * math.cos(a0), 1.3, z + 3.9 * math.sin(a0)))


# ------------------------------------------------------------------ Front desk hall
DX0, DX1, DZ0, DZ1, DCEIL = 339.2, 371.8, -651.8, -630.2, 7.24


def front_desk(B, W):
    B.source = 'lobby-desk'
    y = L1
    plan_faces(W, 'vi-marble-rust', sbox(DX0, DZ0, DX1, DZ1).difference(sbox(DX0 + .5, DZ0 + .5, DX1 - .5, DZ1 - .5)), y)
    plan_faces(W, 'vi-diag-grid', sbox(DX0 + .5, DZ0 + .5, DX1 - .5, DZ1 - .5), y)
    K.solid_quad(W, (DX0, y, DZ0), (DX1, y, DZ0), (DX1, y, DZ1), (DX0, y, DZ1))
    ENT = 5.95
    Fw, Lw = facade(B, (DX0, DZ1), (DX0, DZ0))      # west, local x = -630.2 - Z
    Fn, Ln = facade(B, (DX0, DZ0), (DX1, DZ0))      # north, local x = X - 339.2
    Fe, Le = facade(B, (DX1, DZ0), (DX1, DZ1))      # east, local x = Z + 651.8
    Fs, Ls = facade(B, (DX1, DZ1), (DX0, DZ1))      # south, local x = 371.8 - X
    wop = [(3.8, y), (15.8, y), (15.8, 5.9), (3.8, 5.9)]
    piers = [.4 + 5.36 * k for k in range(7)]
    sdoors = [((piers[k] + piers[k + 1]) / 2 - 1.35, (piers[k] + piers[k + 1]) / 2 + 1.35) for k in (1, 4)]
    edoors = [(3.55 - .95, 3.55 + .95), (18.05 - .95, 18.05 + .95)]
    for F, Lx, holes, gaps, dgaps in [(Fw, Lw, [wop], [(3.8, 15.8, 5.9)], [(3.8, 15.8)]), (Fn, Ln, [], [], []), (Fe, Le, [], [], edoors), (Fs, Ls, [], [], sdoors)]:
        wall(F, 'vi-lobby-stucco-gold', 0, Lx, y, DCEIL, holes, 0, 0)
        dado(F, 0, Lx, y, .9, dgaps)
        skirting(F, 0, Lx, y, dgaps)
        K.entablature(F, 0, Lx, ENT, 'vi-limestone', 'vi-gilt', 'vi-gilt-plain', 0, .8, True)
        solid_wall(F, 0, Lx, y, DCEIL, gaps)
    surround(Fw, wop, 'vi-gilt-plain', [(0, 0), (0, .05), (.1, .07), (.12, .1), (.2, .1), (.22, 0)])
    for x in [.4, 3.2, 16.4, 21.2]: pilaster(Fw, x, y + .9, ENT, w=.6, flutes=3)
    mirror(Fw, .9, 1.5, 2.7, 5.1); mirror(Fw, 16.9, 1.5, 20.7, 5.1)
    # north and south walls: pilasters, mirrors and paintings; tower doors on the south
    for F, Lx, south in [(Fn, Ln, False), (Fs, Ls, True)]:
        for x in piers: pilaster(F, min(x, Lx - .4), y + .9, ENT, w=.6, flutes=3)
        for k in range(6):
            xc = (piers[k] + min(piers[k + 1], Lx - .4)) / 2
            if south and k in (1, 4):
                ring = K.opening('rect', xc, y, 2.4, 3.2)
                K.pane(F, 'vi-bronze', ring, .02)
                for s in (-1, 1): K.box(F, 'vi-gilt-plain', (xc + s * .15, 1.4, .05), (.04, .5, .04))
                K.box(F, 'vi-gilt-plain', (xc, y + 1.6, .035), (.02, 3.2, .03))
                surround(F, ring, 'vi-limestone')
                K.box(F, 'vi-wood-dark', (xc, 3.95, .05), (2.6, .38, .06))
                K.text(F, 'VENETIAN TOWER', xc, 3.86, .09, .2, 'vi-sign-gold')
                gilt_panel(F, xc - 1.4, 4.4, xc + 1.4, 5.5, 'vi-lobby-ornament-blue')
            elif k % 2 == 0:
                arched_mirror(F, xc, 1.4, 2.6, 4.0)
            else:
                gilt_panel(F, xc - 1.8, 2.0, xc + 1.8, 4.6, ['vi-fresco-a', 'vi-fresco-b'][(k // 2 + south) % 2],
                           prof=[(-.14, 0), (-.14, .05), (-.07, .1), (.07, .1), (.14, .05), (.14, 0)])
    # the back wall: THE VENETIAN, a painting, clocks, staff doors
    for x in [.5, 6.6, 15.0, 21.1]: pilaster(Fe, x, y + .9, ENT, w=.6, flutes=3)
    gilt_panel(Fe, 7.6, 2.3, 14.0, 4.7, 'vi-fresco-oval', prof=[(-.18, 0), (-.18, .06), (-.09, .13), (.09, .13), (.18, .06), (.18, 0)])
    K.box(Fe, 'vi-velvet-red', (10.8, 5.36, .04), (6.4, .78, .06))
    K.text(Fe, 'THE VENETIAN', 10.8, 5.12, .08, .6, 'vi-sign-gold')
    for xc, label in [(3.55, 'LAS VEGAS'), (18.05, 'VENEZIA')]:
        door = K.opening('rect', xc, y, 1.6, 2.8)
        K.pane(Fe, 'vi-wood-dark', door, .02); surround(Fe, door, 'vi-limestone')
        K.box(Fe, 'vi-gilt-plain', (xc + .5, 1.3, .05), (.04, .3, .04))
        cy = 4.35
        K.tube(Fe, 'vi-gilt-plain', (xc, cy, 0), (xc, cy, .12), .6, 24)
        K.tube(Fe, 'vi-cloth-white', (xc, cy, .12), (xc, cy, .125), .5, 24)
        for ang, ln in [(math.radians(60), .26), (math.radians(150), .38)]:
            K.tube(Fe, 'vi-iron', (xc, cy, .135), (xc + ln * math.cos(ang), cy + ln * math.sin(ang), .135), .015, 4)
        for i in range(12):
            a = i * TAU / 12
            K.box(Fe, 'vi-iron', (xc + .43 * math.cos(a), cy + .43 * math.sin(a), .13), (.04, .04, .01))
        K.text(Fe, label, xc, 3.42, .08, .2, 'vi-sign-gold')
    # the counter: marble and gilt, lamps
    cx0, cx1, cz0, cz1 = 367.6, 368.9, -647.5, -632.5
    K.box(W, 'vi-marble-black', ((cx0 + cx1) / 2 + .05, y + .08, (cz0 + cz1) / 2), (cx1 - cx0 - .1, .16, cz1 - cz0))
    K.box(W, 'vi-marble-cream', ((cx0 + cx1) / 2 + .03, .72, (cz0 + cz1) / 2), (cx1 - cx0 - .06, .8, cz1 - cz0))
    K.box(W, 'vi-marble-green', ((cx0 + cx1) / 2, 1.16, (cz0 + cz1) / 2), (cx1 - cx0 + .14, .08, cz1 - cz0 + .14))
    K.box(W, 'vi-gilt-plain', (cx0 - .06, 1.1, (cz0 + cz1) / 2), (.03, .05, cz1 - cz0 + .14))
    for k in range(10):
        zc = cz0 + (cz1 - cz0) * (k + .5) / 10
        K.box(W, 'vi-lobby-marble-siena', (cx0 + .04, .72, zc), (.03, .44, 1.15))
        for s in (-1, 1): K.box(W, 'vi-gilt-plain', (cx0 + .03, .72, zc + s * .6), (.04, .58, .04))
        K.box(W, 'vi-gilt-plain', (cx0 + .03, .96, zc), (.04, .03, 1.2)); K.box(W, 'vi-gilt-plain', (cx0 + .03, .48, zc), (.04, .03, 1.2))
    K.solid_box(W, ((cx0 + cx1) / 2, .7, (cz0 + cz1) / 2), (cx1 - cx0 + .14, .92, cz1 - cz0 + .14))
    for zc in np.linspace(cz0 + 1.2, cz1 - 1.2, 6):
        K.lathe(W, 'vi-gilt-plain', 368.3, zc, [(1.2, .11), (1.24, .11), (1.27, .04), (1.62, .022), (1.65, .035)], 10)
        K.lathe(W, 'vi-lobby-lampshade', 368.3, zc, [(1.6, .19), (1.84, .11)], 12)
    # queue: brass stanchions and velvet ropes
    for zr in (-643.0, -637.0):
        xs = [356.5, 359.0, 361.5, 364.0]
        for xp in xs:
            K.lathe(W, 'vi-gilt-plain', xp, zr, [(y, .17), (y + .04, .17), (y + .06, .04), (1.18, .025), (1.2, .05), (1.26, .05), (1.3, .001)], 10)
        for xa, xb in zip(xs, xs[1:]):
            K.path(W, 'vi-velvet-red', [(xa, 1.1, zr), (xa + (xb - xa) * .25, .98, zr), ((xa + xb) / 2, .94, zr), (xa + (xb - xa) * .75, .98, zr), (xb, 1.1, zr)], .025, 6)
        K.solid_box(W, ((xs[0] + xs[-1]) / 2, .7, zr), (xs[-1] - xs[0] + .3, .9, .3))
    # lounges with rugs, and a round table of flowers
    for zc, yaw in [(-648.6, 0.0), (-631.8, math.pi)]:
        K.box(W, 'vi-carpet', (347.5, y + .01, zc + (1.5 if yaw == 0 else -1.5)), (5.6, .02, 4.2))
        sofa(B, 347.5, zc, yaw, 2.6)
        sgn = 1 if yaw == 0 else -1
        sofa(B, 344.6, zc + sgn * 2.0, math.pi / 2, 1.0); sofa(B, 350.4, zc + sgn * 2.0, -math.pi / 2, 1.0)
        coffee_table(W, 347.5, zc + sgn * 1.9, 1.5, .8)
    K.lathe(W, 'vi-gilt-plain', 352.5, -640.0, [(y, .5), (y + .1, .44), (y + .2, .16), (y + .74, .12), (y + .8, .22)], 12)
    K.lathe(W, 'vi-marble-cream', 352.5, -640.0, [(y + .8, .001), (y + .8, 1.1), (y + .86, 1.1), (y + .86, .001)], 28)
    K.lathe(W, 'vi-gilt-plain', 352.5, -640.0, [(y + .86, .32), (y + .95, .36), (y + 1.3, .28), (y + 1.4, .34)], 12)
    flowers(W, 352.5, -640.0, y + 1.35, .9, 7)
    K.solid_box(W, (352.5, .6, -640.0), (2.2, 1.2, 2.2))
    # ceiling: cove, coffers, three paintings down the middle, chandeliers
    Rc = .17
    ring = [(DX0, DZ0), (DX1, DZ0), (DX1, DZ1), (DX0, DZ1)]
    K.sweep_plan(W, 'vi-stucco-white', ring, [(Rc - Rc * math.cos(t), Rc * math.sin(t)) for t in np.linspace(0, math.pi / 2, 4)], DCEIL - Rc, closed=True)
    fx0, fx1, fz0, fz1 = DX0 + Rc, DX1 - Rc, DZ0 + Rc, DZ1 - Rc
    nx, nz = 12, 8; ddx, ddz = (fx1 - fx0) / nx, (fz1 - fz0) / nz
    strip = (fx0 + ddx, fz0 + 3 * ddz, fx0 + 10 * ddx, fz0 + 5 * ddz)
    coffer_field(W, fx0, fx1, fz0, fz1, DCEIL, nx, nz, depth=.22, beam=.3, panel=lambda i, j: ['vi-coffer-cream', 'vi-lobby-ornament-blue'][(i + j) % 2 if (j in (0, 7) or i in (0, 11)) else 0],
                 skip=lambda i, j: 1 <= i <= 9 and 3 <= j <= 4, holes=[sbox(*strip)])
    sx = [(strip[0] + strip[2]) / 2 + d * 3 * ddx for d in (-1, 0, 1)]
    plan_faces(W, 'vi-gilt', sbox(*strip).difference(unary_union([sbox(sx[0] - 1.35 * ddx, strip[1] + .25, sx[0] + 1.35 * ddx, strip[3] - .25),
                                                                   ellipse(sx[1], -641.0, 1.3 * ddx, (strip[3] - strip[1]) / 2 - .3),
                                                                   sbox(sx[2] - 1.35 * ddx, strip[1] + .25, sx[2] + 1.35 * ddx, strip[3] - .25)])), DCEIL)
    for xc, mat in [(sx[0], 'vi-fresco-a'), (sx[2], 'vi-fresco-b')]:
        ring2 = [(xc - 1.35 * ddx, strip[1] + .25), (xc + 1.35 * ddx, strip[1] + .25), (xc + 1.35 * ddx, strip[3] - .25), (xc - 1.35 * ddx, strip[3] - .25)]
        K.face(W, mat, [(px, DCEIL + .002, pz) for px, pz in ring2])
        K.sweep_plan(W, 'vi-gilt-plain', ring2, [(-.08, 0), (-.08, -.08), (0, -.14), (.12, -.14), (.16, 0)], DCEIL, closed=True)
    K.oval_fresco(W, sx[1], DCEIL, (strip[1] + strip[3]) / 2, 1.3 * ddx, (strip[3] - strip[1]) / 2 - .3, 'vi-fresco-oval', 'vi-gilt', 40, .22)
    for xc in sx: chandelier(W, xc, DCEIL, (strip[1] + strip[3]) / 2, 1.0, 2, 10, 1.4)
    for x in [345.0, 355.5, 366.0]:
        for z in [-646.0, -634.0]: W.light(x, 6.3, z, 0xffe6c4, 240, 16)


# ------------------------------------------------------------------ the venue
def build(B):
    B.property = 'venetian-interior'; B.detail = 0; B.source = 'lobby'
    _shop[0] = 0
    W = Frame(B, 0, 0, 0, y=0)
    great_hall(B, W)
    rialto(B, W)
    arrivals(B, W)
    colonnade(B, W)
    rotunda(B, W)
    armillary(B, W)
    front_desk(B, W)

    def zone(x0, z0, x1, z1, y, h):
        return dict(origin=[(x0 + x1) / 2, y, z0], yaw=0, width=round(x1 - x0, 3), depth=round(z1 - z0, 3), height=h)
    zones = [zone(225.8, -707.5, 288.0, -665.0, L1, 12.0),          # Great Hall with the overlook
             zone(225.6, -652.5, 252.4, -635.5, 6.24, 6.0),          # Rialto gallery, landing hall, steps
             zone(228.4, -646.6, 252.6, -630.5, L1, 5.7),            # arrivals
             zone(251.8, -647.4, 316.6, -632.6, L1, 11.0),           # colonnade
             zone(315.6, -653.0, 339.8, -628.7, L1, 15.0),           # rotunda (and its casino passage)
             zone(338.6, -652.2, 372.2, -629.8, L1, 7.0)]            # front desk
    portals = [{"p": [225.85, 6.24, -644.0], "yaw": 1.5707963267948966, "width": 4.6, "height": 3.3, "name": "Rialto / Grand Canal gallery", "venue": "venetian"},
               {"p": [232.0, 0.24, -630.75], "yaw": math.pi, "width": 6.0, "height": 4.5, "name": "Venetian hotel arrivals", "venue": "venetian"}]
    access = [[287.6, FL, -687.0], [226.4, FL, -685.14], [226.3, RIALTO_Y, -644.0], [232.0, L1, -631.4],
              [248.0, L2, -653.0], [233.0, L2, -664.0], [328.0, L1, -652.4]]
    routes = [dict(points=[[225.6, FL, -685.14], [240.0, FL, -685.5], [259.5, FL, -672.5], [258.4, FL, -668.2], [SA_TOP, MID_Y, -668.2],
                           [SB_BOT, MID_Y, -668.2], [SB_TOP, L2, -668.2], [233.2, L2, -668.2], [233.2, L2, -665.5]]),
              dict(points=[[240.0, FL, -687.0], [288.5, L1, -687.0]]),
              dict(points=[[232.0, L1, -631.6], [240.5, L1, -636.0], [252.5, L1, -640.0], [316.0, L1, -640.0], [323.5, L1, -645.6],
                           [332.5, L1, -645.6], [339.5, L1, -640.0], [350.5, L1, -642.4], [354.5, L1, -642.4], [356.5, L1, -640.0], [366.5, L1, -640.0]]),
              dict(points=[[226.2, RIALTO_Y, -644.0], [238.0, RIALTO_Y, -644.0], [247.5, RIALTO_Y, -645.5], [247.5, RIALTO_Y, -648.0],
                           [247.5, L2, -651.75], [247.5, L2, -653.0]]),
              dict(points=[[328.0, L1, -646.5], [328.0, L1, -652.5]])]
    views = {
        'vi-lobby-hall': dict(eye=[284.0, 1.7, -686.75], target=[232.0, 5.5, -686.75], lens=18),
        'vi-lobby-hall-ceiling': dict(eye=[276.0, 1.7, -671.0], target=[259.1, 12.2, -687.5], lens=18),
        'vi-lobby-hall-entry': dict(eye=[229.0, 1.7, -685.1], target=[287.0, 4.0, -688.0], lens=18),
        'vi-lobby-overlook': dict(eye=[234.6, 8.95, -704.0], target=[268.0, 5.0, -684.0], lens=18),
        'vi-lobby-shoppes-sign': dict(eye=[268.0, 1.7, -687.0], target=[248.0, 7.2, -666.2], lens=18),
        'vi-lobby-rialto': dict(eye=[250.6, 7.95, -640.2], target=[228.0, 7.9, -644.0], lens=18),
        'vi-lobby-arrivals': dict(eye=[250.5, 1.7, -645.0], target=[232.0, 2.6, -631.5], lens=18),
        'vi-lobby-colonnade': dict(eye=[255.0, 1.7, -640.0], target=[316.0, 4.6, -640.0], lens=18),
        'vi-lobby-vault': dict(eye=[268.0, 1.6, -640.0], target=[292.0, 10.6, -640.0], lens=18),
        'vi-lobby-armillary': dict(eye=[318.6, 1.7, -643.6], target=[328.0, 4.4, -640.0], lens=18),
        'vi-lobby-dome': dict(eye=[325.0, 1.6, -634.8], target=[328.2, 13.0, -641.6], lens=18),
        'vi-lobby-front-desk': dict(eye=[341.0, 1.7, -640.6], target=[370.0, 2.6, -640.0], lens=18),
    }
    return [dict(key='venetian', portals=portals, zones=zones, accessPoints=access, routes=routes, views=views)]
