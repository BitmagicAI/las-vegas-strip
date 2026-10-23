"""Architectural kit for the Venetian's public interiors (2026-10-23): mouldings swept along paths, walls with real
openings, columns, arcades, vaults, Venetian house fronts, lamps, bridges, furniture. Original geometry, metre scale.

Every function draws through a common.Frame `F` (local x right, y up, z forward; F.p() maps to world) and the 'vi-*'
materials of venetian_materials.py. A facade frame has the wall's face at local z = 0 with the street at +z.

Collision: visual faces are never solid here. Each builder that needs one adds a simple collider (solid_box,
solid_quad) so the physics mesh stays small; walkable surfaces are added by the module that owns the floor.
"""
import math
import numpy as np
from shapely.geometry import Polygon, LineString, Point, box as sbox
from shapely.ops import unary_union
from surface_geometry import triangles
from building_surfaces import parts
from common import Frame

TAU = math.tau


# ------------------------------------------------------------------ low level
def face(F, mat, pts, solid=False):
    F.b.face(mat, [F.p(*p) for p in pts], solid)


def quad(F, mat, a, b, c, d, solid=False):
    face(F, mat, [a, b, c, d], solid)


def _solid(F, pts):
    """Collision-only polygon (fan), no visuals."""
    c = F.b.solids[F.b.property]; n = len(c['vertices']) // 3
    for p in pts: c['vertices'].extend(float(v) for v in F.p(*p))
    for i in range(1, len(pts) - 1): c['indices'].extend([n, n + i, n + i + 1])


def solid_quad(F, a, b, c, d):
    _solid(F, [a, b, c, d])


def solid_box(F, c, size):
    """Collision-only box (local centre, size), rotated with the frame."""
    x, y, z = c; w, h, d = size[0] / 2, size[1] / 2, size[2] / 2
    P = [(x + i * w, y + j * h, z + k * d) for i, j, k in
         [(-1, -1, -1), (1, -1, -1), (1, 1, -1), (-1, 1, -1), (-1, -1, 1), (1, -1, 1), (1, 1, 1), (-1, 1, 1)]]
    for ids in [(0, 3, 2, 1), (4, 5, 6, 7), (0, 4, 7, 3), (1, 2, 6, 5), (3, 7, 6, 2), (0, 1, 5, 4)]:
        _solid(F, [P[i] for i in ids])


def box(F, mat, c, size, solid=False):
    F.box(mat, c, size, solid)


def rot_frame(F, x, z, yaw, y=0.0):
    """A child frame at local (x, y, z) of F, turned by `yaw` relative to F."""
    p = F.p(x, y, z)
    return Frame(F.b, p[0], p[2], F.yaw + yaw, y=p[1])


def lathe(F, mat, x, z, profile, n=16, y=0.0, a0=0.0, a1=TAU):
    """Surface of revolution about the local vertical axis at (x, z); profile = [(y, r), ...]; optional sector a0..a1."""
    angles = np.linspace(a0, a1, n + 1)
    for (ya, ra), (yb, rb) in zip(profile, profile[1:]):
        for i in range(n):
            a, b = angles[i], angles[i + 1]
            pts = [(x + ra * math.cos(a), y + ya, z + ra * math.sin(a)), (x + ra * math.cos(b), y + ya, z + ra * math.sin(b)),
                   (x + rb * math.cos(b), y + yb, z + rb * math.sin(b)), (x + rb * math.cos(a), y + yb, z + rb * math.sin(a))]
            face(F, mat, pts)


def disc(F, mat, x, y, z, r, n=24, rz=None):
    rz = r if rz is None else rz
    face(F, mat, [(x + r * math.cos(a), y, z + rz * math.sin(a)) for a in np.linspace(0, TAU, n, endpoint=False)])


def tube(F, mat, a, b, r=.04, n=8, r2=None):
    F.tube(mat, a, b, r, n, r2)


def path(F, mat, pts, r=.04, n=8):
    for a, b in zip(pts, pts[1:]): F.tube(mat, a, b, r, n)


def sphere(F, mat, c, r, n=12, m=8, scale=(1, 1, 1)):
    F.b.sphere(mat, F.p(*c), r, n, m, scale) if F.yaw == 0 else _rot_sphere(F, mat, c, r, n, m, scale)


def _rot_sphere(F, mat, c, r, n, m, scale):
    cx, cy, cz = c
    def pt(a, b): return (cx + r * scale[0] * math.cos(a) * math.cos(b), cy + r * scale[1] * math.sin(b), cz + r * scale[2] * math.sin(a) * math.cos(b))
    for j in range(m):
        b = -math.pi / 2 + j * math.pi / m; bb = b + math.pi / m
        for i in range(n):
            a = i * TAU / n; aa = a + TAU / n; face(F, mat, [pt(a, b), pt(aa, b), pt(aa, bb), pt(a, bb)])


def text(F, label, x, y, z, size=.4, mat='vi-sign-gold'):
    """A sign reading toward the frame's +z (the street side of a facade frame)."""
    F.text(label, (x, y, z), size, mat, True)


# ------------------------------------------------------------------ sweeps
def _norm(v):
    n = np.linalg.norm(v); return v / n if n > 1e-9 else v


def sweep_frames(F, mat, pts, ns, bs, profile, closed=False, miter=None):
    """Sweep a 2D profile [(a, b), ...] along local points `pts`: each section is p + a*N*m + b*B."""
    pts = [np.array(p, float) for p in pts]; k = len(pts)
    miter = miter or [1.0] * k
    secs = [[pts[i] + a * ns[i] * miter[i] + b * bs[i] for a, b in profile] for i in range(k)]
    rng = range(k) if closed else range(k - 1)
    for i in rng:
        A, Bv = secs[i], secs[(i + 1) % k]
        for j in range(len(profile) - 1):
            face(F, mat, [tuple(A[j]), tuple(Bv[j]), tuple(Bv[j + 1]), tuple(A[j + 1])])


def _bisectors(pts2, closed):
    """In-plane outward bisector (left normal of the direction of travel) and miter scale for a 2D polyline."""
    P = [np.array(p, float) for p in pts2]; k = len(P); ns = []; ms = []
    for i in range(k):
        prev = P[i - 1] if (closed or i > 0) else None
        nxt = P[(i + 1) % k] if (closed or i < k - 1) else None
        ds = []
        if prev is not None: ds.append(_norm(P[i] - prev))
        if nxt is not None: ds.append(_norm(nxt - P[i]))
        nn = [np.array([-d[1], d[0]]) for d in ds]
        n = _norm(sum(nn)); m = 1.0
        if len(nn) == 2: m = min(2.5, 1 / max(.2, float(np.dot(n, nn[0]))))
        ns.append(n); ms.append(m)
    return ns, ms


def sweep_plan(F, mat, pts, profile, y=0.0, closed=False):
    """Horizontal moulding along a plan polyline [(x, z), ...] at height y. Profile (o, dy): o along the normal (-dz, dx)
    of the direction of travel (dx, dz): a path running +x offsets toward +z."""
    ns2, ms = _bisectors(pts, closed)
    P = [np.array([p[0], y, p[1]]) for p in pts]
    N = [np.array([n[0], 0, n[1]]) for n in ns2]; Bv = [np.array([0, 1., 0])] * len(P)
    sweep_frames(F, mat, P, N, Bv, profile, closed, ms)


def sweep_facade(F, mat, x0, x1, y, profile, z=0.0):
    """A straight horizontal moulding on a facade frame from x0 to x1 at height y: profile (out, dy), out toward +z."""
    sweep_frames(F, mat, [np.array([x0, y, z]), np.array([x1, y, z])], [np.array([0, 0, 1.])] * 2, [np.array([0, 1., 0])] * 2, profile)
    # end caps (flat)
    for x in (x0, x1):
        face(F, mat, [(x, y + b, z + a) for a, b in profile])


def sweep_ring(F, mat, ring, profile, z=0.0, closed=True):
    """Moulding around an opening in a facade plane: ring [(x, y), ...] (any winding), profile (o, d): o outward from the
    opening into the wall, d toward the street (+z)."""
    ring = list(ring)
    if closed and Polygon(ring).exterior.is_ccw is False: ring = ring[::-1]
    elif not closed:
        pass
    ns2, ms = _bisectors(ring, closed)
    # for a CCW ring the left normal points inward: flip to outward
    if closed: ns2 = [-n for n in ns2]
    P = [np.array([p[0], p[1], z]) for p in ring]
    N = [np.array([n[0], n[1], 0]) for n in ns2]; Bv = [np.array([0, 0, 1.])] * len(P)
    sweep_frames(F, mat, P, N, Bv, profile, closed, ms)


def sweep_arc(F, mat, cx, cy, z, r, a0, a1, profile, n=16, axis='x'):
    """Moulding along a circular arc in a vertical plane: axis 'x' = the arc lies in the local x-y plane at depth z;
    profile (o, d): o radial outward, d along +z (or +x for axis 'z')."""
    A = np.linspace(a0, a1, n + 1)
    if axis == 'x':
        P = [np.array([cx + r * math.cos(a), cy + r * math.sin(a), z]) for a in A]
        N = [np.array([math.cos(a), math.sin(a), 0]) for a in A]; Bv = [np.array([0, 0, 1.])] * len(A)
    else:
        P = [np.array([z, cy + r * math.sin(a), cx + r * math.cos(a)]) for a in A]
        N = [np.array([0, math.sin(a), math.cos(a)]) for a in A]; Bv = [np.array([1., 0, 0])] * len(A)
    sweep_frames(F, mat, P, N, Bv, profile)


# Profiles: (out, up) for horizontal mouldings; (outward, depth) for rings
P_STRING = [(0, 0), (.06, 0), (.06, .04), (.09, .07), (.09, .14), (.05, .18), (0, .18)]
P_CORNICE = [(0, 0), (.05, 0), (.05, .06), (.1, .1), (.1, .16), (.16, .2), (.16, .24), (.34, .3), (.42, .34), (.42, .44), (.36, .48), (0, .48)]
P_CORNICE_SMALL = [(0, 0), (.04, 0), (.04, .05), (.12, .1), (.2, .14), (.2, .2), (0, .2)]
P_SKIRT = [(0, 0), (.04, 0), (.04, .16), (.025, .2), (0, .22)]
P_SURROUND = [(0, .0), (0, .05), (.08, .05), (.1, .07), (.18, .07), (.2, .04), (.2, 0)]
P_ARCHIVOLT = [(0, 0), (0, .06), (.1, .08), (.16, .12), (.26, .12), (.3, .06), (.3, 0)]
P_RAIL = [(-.08, 0), (.08, 0), (.08, .05), (.06, .1), (-.06, .1), (-.08, .05), (-.08, 0)]
P_GILT_FRAME = [(-.08, 0), (-.08, .04), (-.04, .07), (.04, .07), (.08, .04), (.08, 0)]
P_PLINTH = [(0, 0), (.12, 0), (.12, .3), (.08, .34), (.08, .42), (0, .42)]


def entablature(F, x0, x1, y, mat='vi-limestone', frieze='vi-limestone', gilt=None, z=0.0, scale=1.0, dentils=True):
    """Architrave (two fasciae), frieze and cornice along a facade frame from x0 to x1, base at height y."""
    s = scale
    sweep_facade(F, mat, x0, x1, y, [(0, 0), (.05 * s, 0), (.05 * s, .18 * s), (.08 * s, .2 * s), (.08 * s, .4 * s), (.11 * s, .44 * s), (0, .44 * s)], z)
    box(F, frieze, ((x0 + x1) / 2, y + .44 * s + .25 * s, z + .025 * s), (x1 - x0, .5 * s, .05 * s))
    if gilt: sweep_facade(F, gilt, x0, x1, y + .94 * s, [(0, 0), (.06 * s, 0), (.06 * s, .06 * s), (0, .06 * s)], z)
    yc = y + .94 * s
    if dentils:
        for x in np.arange(x0 + .12 * s, x1 - .06 * s, .2 * s): box(F, mat, (x, yc + .14 * s, z + .1 * s), (.1 * s, .12 * s, .2 * s))
    sweep_facade(F, mat, x0, x1, yc, [(0, 0), (.06 * s, 0), (.06 * s, .08 * s), (.2 * s, .2 * s), (.36 * s, .24 * s), (.42 * s, .3 * s), (.42 * s, .4 * s), (.36 * s, .46 * s), (0, .46 * s)], z)
    return yc + .46 * s


# ------------------------------------------------------------------ walls and openings
def opening(kind, x, y0, w, h, n=10):
    """Outline of an opening in facade coordinates (x, y), counter-clockwise."""
    r = w / 2
    if kind == 'rect': return [(x - r, y0), (x + r, y0), (x + r, y0 + h), (x - r, y0 + h)]
    if kind == 'arch':
        s = y0 + h - r
        return [(x - r, y0), (x + r, y0)] + [(x + r * math.cos(a), s + r * math.sin(a)) for a in np.linspace(0, math.pi, n + 1)]
    if kind == 'segment':  # flat segmental arch
        s = y0 + h - r * .35
        return [(x - r, y0), (x + r, y0)] + [(x + r * math.cos(a), s + r * .35 * math.sin(a)) for a in np.linspace(0, math.pi, n + 1)]
    if kind == 'gothic':  # pointed (lancet): two arcs of radius w centred on the opposite jambs
        s = y0 + h - w * math.sin(math.radians(60))
        right = [(x - r + w * math.cos(a), s + w * math.sin(a)) for a in np.linspace(0, math.radians(60), n // 2 + 1)]
        left = [(x + r - w * math.cos(a), s + w * math.sin(a)) for a in np.linspace(math.radians(60), 0, n // 2 + 1)][1:]
        return [(x - r, y0), (x + r, y0)] + right + left
    if kind == 'ogee':
        s = y0 + h - r * 1.4
        pts = [(x - r, y0), (x + r, y0), (x + r, s)]
        for t in np.linspace(0, 1, n + 1)[1:]:
            xx = r * (1 - t); yy = r * 1.4 * (t if t < .5 else t) + .12 * r * math.sin(t * math.pi * 2)
            pts.append((x + xx, s + yy))
        for t in np.linspace(1, 0, n + 1)[1:]:
            xx = r * (1 - t); yy = r * 1.4 * t + .12 * r * math.sin(t * math.pi * 2)
            pts.append((x - xx, s + yy))
        return pts
    if kind == 'round':
        return [(x + r * math.cos(a), y0 + r + r * math.sin(a)) for a in np.linspace(0, TAU, 2 * n, endpoint=False)]
    raise ValueError(kind)


def wall(F, mat, outline, holes=(), z=0.0, reveal=0.0, reveal_mat=None):
    """A flat wall in the facade plane (front face at depth z) with openings; `reveal` draws jambs that deep."""
    poly = Polygon(outline).buffer(0)
    hs = [Polygon(h).buffer(0) for h in holes]
    if hs: poly = poly.difference(unary_union(hs))
    for q in parts(poly):
        for t in triangles(q): face(F, mat, [(px, py, z) for px, py in list(t.exterior.coords)[:-1]])
    if reveal:
        for h in holes:
            ring = list(h) + [h[0]]
            for (ax, ay), (bx, by) in zip(ring, ring[1:]):
                quad(F, reveal_mat or mat, (ax, ay, z), (bx, by, z), (bx, by, z - reveal), (ax, ay, z - reveal))


def pane(F, mat, ring, z):
    """Fill an opening outline at depth z (glass, a lit display, a painted panel)."""
    poly = Polygon(ring).buffer(0)
    for q in parts(poly):
        for t in triangles(q): face(F, mat, [(px, py, z) for px, py in list(t.exterior.coords)[:-1]])


def window(F, kind, x, y0, w, h, wall_z=0.0, depth=.28, glass='vi-window-dark', surround='vi-limestone', sill=True,
           shutters=None, keystone=False, pediment=None, mullions=True, balcony=None, rail_mat='vi-iron'):
    """Return the opening ring (for the wall's holes) and draw the window: reveal is the caller's; glass, glazing bars,
    surround moulding, sill, shutters ('vi-shutter-green' ...), keystone, pediment ('triangle'|'segment'|'cornice'),
    balcony ('stone'|'iron'|'flowers')."""
    ring = opening(kind, x, y0, w, h)
    pane(F, glass, ring, wall_z - depth)
    if mullions:
        top = y0 + h - (w / 2 if kind in ('arch', 'gothic', 'ogee') else 0)
        box(F, 'vi-wood-dark', (x, (y0 + top) / 2, wall_z - depth + .03), (.05, top - y0, .04))
        box(F, 'vi-wood-dark', (x, y0 + (top - y0) * .62, wall_z - depth + .03), (w, .05, .04))
    if surround: sweep_ring(F, surround, ring, P_SURROUND, wall_z)
    if sill: box(F, surround or 'vi-limestone', (x, y0 - .05, wall_z + .07), (w + .36, .1, .2))
    if keystone and kind in ('arch', 'segment'):
        box(F, surround, (x, y0 + h + .12, wall_z + .05), (.22, .34, .12))
    if pediment == 'cornice':
        sweep_facade(F, surround, x - w / 2 - .25, x + w / 2 + .25, y0 + h + .25, P_CORNICE_SMALL, wall_z)
    elif pediment == 'triangle':
        yb = y0 + h + .25; sweep_facade(F, surround, x - w / 2 - .3, x + w / 2 + .3, yb, [(0, 0), (.14, 0), (.14, .1), (0, .1)], wall_z)
        face(F, surround, [(x - w / 2 - .3, yb + .1, wall_z + .08), (x + w / 2 + .3, yb + .1, wall_z + .08), (x, yb + .1 + w * .32, wall_z + .08)])
    elif pediment == 'segment':
        yb = y0 + h + .25; sweep_facade(F, surround, x - w / 2 - .3, x + w / 2 + .3, yb, [(0, 0), (.14, 0), (.14, .08), (0, .08)], wall_z)
        sweep_arc(F, surround, x, yb - w * .6, wall_z, w * .6 + .3, math.radians(35), math.radians(145), [(0, 0), (.1, 0), (.1, .14), (0, .14)], 10)
    if shutters:
        top = y0 + h - (w / 2 if kind in ('arch', 'gothic', 'ogee') else 0)
        for s in (-1, 1):
            box(F, shutters, (x + s * (w / 2 + w * .27), (y0 + top) / 2, wall_z + .05), (w * .52, top - y0, .05))
    if balcony == 'iron':
        bw = w + .5; yb = y0 - .02
        box(F, 'vi-limestone', (x, yb - .06, wall_z + .25), (bw, .12, .5))
        balcony_rail(F, x - bw / 2, x + bw / 2, yb, wall_z + .48, .9, rail_mat)
    elif balcony == 'stone':
        bw = w + 1.1; yb = y0 - .02
        box(F, 'vi-limestone', (x, yb - .09, wall_z + .45), (bw, .18, .9))
        for s in (-1, 1): box(F, 'vi-limestone', (x + s * (bw / 2 - .3), yb - .45, wall_z + .25), (.18, .55, .4))
        balustrade_line(F, (x - bw / 2 + .1, wall_z + .85), (x + bw / 2 - .1, wall_z + .85), yb, .85, solid=False)
        for s in (-1, 1): balustrade_line(F, (x + s * (bw / 2 - .1), wall_z + .1), (x + s * (bw / 2 - .1), wall_z + .85), yb, .85, solid=False, posts=False)
    elif balcony == 'flowers':
        box(F, 'vi-soil', (x, y0 + .1, wall_z + .15), (w + .1, .2, .3))
        for i, fx in enumerate(np.linspace(x - w / 2 + .1, x + w / 2 - .1, max(2, int(w / .22)))):
            sphere(F, ['vi-flower-red', 'vi-plant', 'vi-flower-pink'][i % 3], (fx, y0 + .3, wall_z + .18), .13, 6, 4)
    return ring


def balcony_rail(F, x0, x1, y, z, h=.9, mat='vi-iron'):
    tube(F, mat, (x0, y + h, z), (x1, y + h, z), .025, 6)
    tube(F, mat, (x0, y + .08, z), (x1, y + .08, z), .015, 5)
    for x in np.arange(x0, x1 + 1e-6, .12): tube(F, mat, (x, y, z), (x, y + h, z), .009, 4)
    # a scroll band: a row of small rings
    for x in np.arange(x0 + .12, x1 - .06, .24): path(F, mat, [(x + .1 * math.cos(a), y + .5 + .1 * math.sin(a), z) for a in np.linspace(0, TAU, 9)], .008, 4)


def balustrade_line(F, a, b, y=0.0, h=1.0, mat='vi-limestone', pitch=.3, solid=True, posts=True):
    """A stone balustrade on a plan segment a->b (local x, z) at height y: plinth, vase balusters, handrail, pedestals.
    Adds a collision slab along it when `solid`."""
    ax, az = a; bx, bz = b; L = math.hypot(bx - ax, bz - az)
    if L < .05: return
    ux, uz = (bx - ax) / L, (bz - az) / L
    G = Frame(F.b, *[F.p(ax, y, az)[i] for i in (0, 2)], F.yaw + math.atan2(ux, uz) - math.pi / 2, y=F.p(0, y, 0)[1])
    # G: local x along the balustrade, z across it
    box(G, mat, (L / 2, .07, 0), (L, .14, .3))
    box(G, mat, (L / 2, h - .06, 0), (L + .04, .12, .3))
    sweep_frames(G, mat, [np.array([0, h, 0]), np.array([L, h, 0])], [np.array([0, 0, 1.])] * 2, [np.array([0, 1., 0])] * 2,
                 [(-.16, 0), (.16, 0), (.16, .04), (.12, .08), (-.12, .08), (-.16, .04), (-.16, 0)])
    hb = h - .26
    prof = [(0, .05), (.06 * hb, .05), (.1 * hb, .036), (.3 * hb, .085), (.55 * hb, .045), (.68 * hb, .032), (.78 * hb, .052),
            (.86 * hb, .036), (hb, .05)]
    n = max(1, int(L / pitch))
    for i in range(n):
        x = (i + .5) * L / n
        if posts and n > 6 and i % 8 == 7: continue
        lathe(G, mat, x, 0, prof, 8, y=.14)
    if posts and L > 2.5:
        for x in [0, L] + [((i + 1) * 8 - .5) * L / n for i in range((n + 1) // 8) if ((i + 1) * 8 - .5) * L / n < L - .3]:
            box(G, mat, (x, h / 2, 0), (.32, h, .32))
    if solid: solid_box(G, (L / 2, h / 2, 0), (L, h, .3))


# ------------------------------------------------------------------ columns and piers
def column(F, x, z, h, r=.32, mat='vi-marble-cream', cap='vi-gilt-plain', base='vi-limestone', order='corinthian', n=20,
           solid=True, plinth=True):
    """A classical column standing at local (x, z) from y=0 to y=h (top of the abacus)."""
    ph = .32 if plinth else 0
    if plinth: box(F, base, (x, ph / 2, z), (r * 2.8, ph, r * 2.8))
    lathe(F, mat, x, z, [(ph, r * 1.3), (ph + .05, r * 1.3), (ph + .09, r * 1.22), (ph + .14, r * 1.12), (ph + .18, r * 1.18),
                          (ph + .23, r * 1.05), (ph + .27, r)], n)
    caph = r * 2.4 if order == 'corinthian' else r * 1.1
    y0, y1 = ph + .27, h - caph
    prof = [(y0 + (y1 - y0) * t, r * (1 - .13 * max(0, t - .33) ** 1.4)) for t in np.linspace(0, 1, 6)]
    lathe(F, mat, x, z, prof, n)
    rt = prof[-1][1]
    lathe(F, cap, x, z, [(y1, rt * 1.08), (y1 + .04, rt * 1.08), (y1 + .06, rt)], n)    # astragal
    if order == 'corinthian':
        bell = [(y1 + .06, rt), (y1 + caph * .55, rt * 1.08), (y1 + caph * .85, rt * 1.25)]
        lathe(F, cap, x, z, bell, n)
        for tier, (t0, t1, k) in enumerate([(0, .42, 8), (.3, .7, 8)]):
            for i in range(k):
                a = (i + tier * .5) * TAU / k; ca, sa = math.cos(a), math.sin(a); ta = (-sa, ca)
                ya, yb = y1 + .06 + caph * t0, y1 + .06 + caph * t1
                ra, rb = rt * 1.02, rt * 1.08 + caph * .06
                w0, w1 = rt * .42, rt * .2
                pts0 = [(x + ra * ca - w0 * ta[0], ya, z + ra * sa - w0 * ta[1]), (x + ra * ca + w0 * ta[0], ya, z + ra * sa + w0 * ta[1])]
                pts1 = [(x + rb * ca + w1 * ta[0], yb, z + rb * sa + w1 * ta[1]), (x + rb * ca - w1 * ta[0], yb, z + rb * sa - w1 * ta[1])]
                face(F, cap, [pts0[0], pts0[1], pts1[0], pts1[1]])
                tip = (x + (rb + caph * .1) * ca, yb - caph * .06, z + (rb + caph * .1) * sa)
                face(F, cap, [pts1[1], pts1[0], tip])
        ya = h - .12
        for i in range(4):  # corner volutes
            a = math.pi / 4 + i * math.pi / 2; cx, cz = x + rt * 1.35 * math.cos(a), z + rt * 1.35 * math.sin(a)
            path(F, cap, [(cx + .07 * math.cos(t) * math.cos(a), ya - .07 + .07 * math.sin(t), cz + .07 * math.cos(t) * math.sin(a))
                          for t in np.linspace(0, TAU * .9, 9)], .025, 5)
        box(F, cap, (x, h - .06, z), (rt * 3.0, .12, rt * 3.0))
    else:  # tuscan / doric
        lathe(F, cap, x, z, [(y1 + .06, rt), (y1 + caph * .45, rt * 1.2), (y1 + caph * .7, rt * 1.32)], n)
        box(F, cap, (x, h - caph * .15, z), (rt * 2.9, caph * .3, rt * 2.9))
    if solid: solid_box(F, (x, h / 2, z), (r * 2, h, r * 2))


def pilaster(F, x, y0, y1, w=.6, mat='vi-limestone', cap='vi-gilt-plain', z=0.0, d=.12):
    box(F, mat, (x, (y0 + y1) / 2, z + d / 2), (w, y1 - y0, d))
    box(F, mat, (x, y0 + .15, z + d / 2 + .03), (w + .14, .3, d + .06))
    box(F, cap, (x, y1 - .18, z + d / 2 + .03), (w + .16, .36, d + .06))


# ------------------------------------------------------------------ arches and arcades
def arch_ring(F, x, spring, w, z=0.0, mat='vi-limestone', profile=P_ARCHIVOLT, keystone=True, n=14):
    sweep_arc(F, mat, x, spring, z, w / 2, 0, math.pi, profile, n)
    if keystone: box(F, mat, (x, spring + w / 2 + .18, z + .08), (.34, .44, .16))


def arcade(F, x0, x1, count, y0, h, wall_top, mat='vi-limestone', wall_mat=None, pier=.7, z=0.0, depth=.6,
           inner='vi-limestone', back=None, keystones=True, columns=False, col_r=.2):
    """A wall from x0 to x1, y0..wall_top, pierced by `count` round arches of height h (from y0); piers between them.
    Draws reveals `depth` deep and (optionally) a back panel material per arch. Returns the arch rings."""
    span = (x1 - x0) / count; w = span - pier; rings = []
    for i in range(count):
        cx = x0 + span * (i + .5); rings.append(opening('arch', cx, y0, w, h, 14))
    wall(F, wall_mat or mat, [(x0, y0), (x1, y0), (x1, wall_top), (x0, wall_top)], rings, z, depth, inner)
    for i, ring in enumerate(rings):
        cx = x0 + span * (i + .5)
        arch_ring(F, cx, y0 + h - w / 2, w, z, mat, keystone=keystones)
        if back: pane(F, back, ring, z - depth)
        box(F, mat, (cx - w / 2 - .02, y0 + h - w / 2 - .1, z + .04), (.2, .2, .1))
        box(F, mat, (cx + w / 2 + .02, y0 + h - w / 2 - .1, z + .04), (.2, .2, .1))
    if columns:
        for i in range(count + 1):
            column(F, x0 + span * i, z + col_r * 1.6, y0 + h - w / 2, col_r, 'vi-limestone', 'vi-limestone', 'vi-limestone', 'tuscan', 12, solid=False)
    return rings


# ------------------------------------------------------------------ ceilings
def barrel_vault(F, x0, x1, z0, z1, spring, bays, frescoes=('vi-fresco-a', 'vi-fresco-b'), side=('vi-coffer-red', 'vi-coffer-green'),
                 field='vi-stucco-white', rib='vi-gilt', frame='vi-gilt-plain', n=24, crown_angle=34, side_angle=30):
    """A semicircular barrel vault over local x0..x1 (span), running along z from z0 to z1, springing at height `spring`.
    Each bay: a fresco panel at the crown, an ornament panel each side, a cream field below, gilt transverse ribs."""
    r = (x1 - x0) / 2; cx = (x0 + x1) / 2; L = (z1 - z0) / bays
    ang = np.linspace(0, math.pi, n + 1)
    def P(a, z): return (cx + r * math.cos(a), spring + r * math.sin(a), z)
    c0, c1 = math.radians(90 - crown_angle), math.radians(90 + crown_angle)
    s0, s1 = math.radians(90 - crown_angle - side_angle), math.radians(90 + crown_angle + side_angle)
    for b in range(bays):
        za, zb = z0 + b * L + .35, z0 + (b + 1) * L - .35
        def strip(mat, a0, a1, k, za=za, zb=zb):
            A = np.linspace(a0, a1, k + 1)
            for i in range(k): quad(F, mat, P(A[i], za), P(A[i + 1], za), P(A[i + 1], zb), P(A[i], zb))
        strip(frescoes[b % len(frescoes)], c0, c1, 8)
        for (a0, a1), m in [((s0, c0), side[b % len(side)]), ((c1, s1), side[(b + 1) % len(side)])]:
            strip(m, a0, a1, 5)
        for (a0, a1) in [(0, s0), (s1, math.pi)]:
            strip(field, a0, a1, 6)
        # gilt frames round the fresco and ornament panels
        for a in [s0, c0, c1, s1]: tube(F, frame, P(a, za), P(a, zb), .06, 6)
        for zz in [za, zb]:
            A = np.linspace(s0, s1, 14)
            path(F, frame, [P(a, zz) for a in A], .05, 6)
        # cream field between the bay and the ribs
        for zz0, zz1 in [(z0 + b * L, za), (zb, z0 + (b + 1) * L)]:
            for i in range(n): quad(F, field, P(ang[i], zz0), P(ang[i + 1], zz0), P(ang[i + 1], zz1), P(ang[i], zz1))
    for b in range(bays + 1):  # transverse ribs
        zz = z0 + b * L
        sweep_frames(F, rib, [np.array(P(a, zz)) for a in ang], [-np.array([math.cos(a), math.sin(a), 0]) for a in ang],
                     [np.array([0, 0, 1.])] * len(ang), [(0, -.3), (.18, -.3), (.24, -.2), (.24, .2), (.18, .3), (0, .3)])


def oval_fresco(F, cx, y, cz, rx, rz, mat='vi-fresco-oval', frame='vi-gilt', n=40, dish=.6):
    """An oval painting in a shallow dish (rising `dish` metres at the centre), framed by a gilt ring."""
    rings = [(t, dish * (1 - t * t)) for t in np.linspace(1, 0, 6)]
    A = np.linspace(0, TAU, n + 1)
    for (ta, ha), (tb, hb) in zip(rings, rings[1:]):
        for i in range(n):
            a, b = A[i], A[i + 1]
            quad(F, mat, (cx + rx * ta * math.cos(a), y + ha, cz + rz * ta * math.sin(a)), (cx + rx * ta * math.cos(b), y + ha, cz + rz * ta * math.sin(b)),
                 (cx + rx * tb * math.cos(b), y + hb, cz + rz * tb * math.sin(b)), (cx + rx * tb * math.cos(a), y + hb, cz + rz * tb * math.sin(a)))
    pts = [np.array([cx + rx * math.cos(a), y, cz + rz * math.sin(a)]) for a in A]
    ns = [np.array([math.cos(a) / rx, 0, math.sin(a) / rz]) for a in A]; ns = [v / np.linalg.norm(v) for v in ns]
    sweep_frames(F, frame, pts, ns, [np.array([0, -1., 0])] * len(pts), [(-.05, 0), (-.05, .12), (.1, .2), (.3, .22), (.45, .14), (.5, 0)])


def coffers(F, x0, x1, z0, z1, y, cell=2.4, beam=.32, depth=.3, field='vi-coffer-cream', beam_mat='vi-gilt-plain', panel=None):
    """A coffered ceiling at height y (underside of the beams at y): recessed panels between crossing beams."""
    nx = max(1, round((x1 - x0) / cell)); nz = max(1, round((z1 - z0) / cell))
    cx_ = (x1 - x0) / nx; cz_ = (z1 - z0) / nz
    for i in range(nx):
        for j in range(nz):
            a, b = x0 + i * cx_ + beam / 2, x0 + (i + 1) * cx_ - beam / 2
            c, d = z0 + j * cz_ + beam / 2, z0 + (j + 1) * cz_ - beam / 2
            m = panel(i, j) if panel else field
            quad(F, m, (a, y + depth, c), (b, y + depth, c), (b, y + depth, d), (a, y + depth, d))
            for (p, q) in [((a, c), (b, c)), ((b, c), (b, d)), ((b, d), (a, d)), ((a, d), (a, c))]:
                quad(F, field, (p[0], y + depth, p[1]), (q[0], y + depth, q[1]), (q[0], y, q[1]), (p[0], y, p[1]))
    for i in range(nx + 1): box(F, beam_mat, (x0 + i * cx_, y + .02, (z0 + z1) / 2), (beam, .04, z1 - z0))
    for j in range(nz + 1): box(F, beam_mat, ((x0 + x1) / 2, y + .02, z0 + j * cz_), (x1 - x0, .04, beam))


def chandelier(F, x, y, z, r=1.2, tiers=3, arms=10, glass='vi-crystal', metal='vi-gilt-plain', drop=1.6):
    """A Murano-style chandelier hanging from (x, y) with its lowest tier `drop` below: glass stem, curved arms,
    candle cups with glowing glass, crystal drops."""
    lathe(F, glass, x, z, [(y - drop - .3, 0.001), (y - drop - .2, .08), (y - drop, .12), (y - drop + .4, .06), (y - drop + .7, .1),
                            (y - drop + 1.0, .05), (y, .03)], 10)
    for t in range(tiers):
        rr = r * (1 - t * .3); yy = y - drop + t * .38; k = max(5, arms - 2 * t)
        for i in range(k):
            a = (i + .5 * t) * TAU / k; ca, sa = math.cos(a), math.sin(a)
            pts = [(x + .1 * ca, yy + .05, z + .1 * sa), (x + rr * .5 * ca, yy - .12, z + rr * .5 * sa), (x + rr * .9 * ca, yy - .02, z + rr * .9 * sa),
                   (x + rr * ca, yy + .14, z + rr * sa)]
            path(F, metal, pts, .018, 5)
            lathe(F, glass, x + rr * ca, z + rr * sa, [(0, .03), (.05, .07), (.08, .03), (.22, .025), (.24, 0)], 6, y=yy + .14)
            lathe(F, glass, x + rr * .55 * ca, z + rr * .55 * sa, [(0, 0.001), (.06, .025), (.16, 0.001)], 5, y=yy - .32)


def lantern_head(F, x, y, z, s=1.0, glass='vi-lantern', metal='vi-iron'):
    """A hexagonal street-lamp lantern standing on (x, y, z)."""
    lathe(F, metal, x, z, [(0, .05 * s), (.06 * s, .12 * s), (.08 * s, .12 * s)], 6, y=y)
    lathe(F, glass, x, z, [(.08 * s, .12 * s), (.42 * s, .19 * s)], 6, y=y)
    lathe(F, metal, x, z, [(.42 * s, .21 * s), (.47 * s, .22 * s), (.55 * s, .12 * s), (.62 * s, .04 * s), (.7 * s, .015 * s)], 6, y=y)
    sphere(F, metal, (x, y + .74 * s, z), .03 * s, 5, 3)
    for i in range(6):
        a = i * TAU / 6; tube(F, metal, (x + .12 * s * math.cos(a), y + .08 * s, z + .12 * s * math.sin(a)), (x + .2 * s * math.cos(a), y + .42 * s, z + .2 * s * math.sin(a)), .008 * s, 3)


def lamp_post(F, x, z, y=0.0, heads=3, h=3.6, metal='vi-iron', glass='vi-lantern', solid=True):
    """A cast-iron Venetian street lamp: moulded base, fluted shaft, scroll arms, `heads` (1, 3 or 5) lanterns."""
    lathe(F, metal, x, z, [(0, .26), (.08, .26), (.1, .22), (.32, .2), (.4, .15), (.5, .16), (.56, .1)], 10, y=y)
    lathe(F, metal, x, z, [(.56, .085), (h * .55, .07), (h * .57, .09), (h * .6, .07), (h - .3, .06), (h - .25, .09), (h - .2, .06)], 10, y=y)
    if heads >= 3:
        k = heads - 1 if heads == 5 else heads - 1
        for i in range(k):
            a = i * TAU / k + math.pi / 4
            ca, sa = math.cos(a), math.sin(a); R = .62
            pts = [(x + .05 * ca, y + h - .55, z + .05 * sa), (x + R * .4 * ca, y + h - .7, z + R * .4 * sa), (x + R * .8 * ca, y + h - .55, z + R * .8 * sa),
                   (x + R * ca, y + h - .35, z + R * sa)]
            path(F, metal, pts, .025, 5)
            path(F, metal, [(x + R * .3 * ca + .1 * math.cos(t) * ca, y + h - .45 + .1 * math.sin(t), z + R * .3 * sa + .1 * math.cos(t) * sa) for t in np.linspace(0, TAU * .85, 8)], .012, 4)
            lantern_head(F, x + R * ca, y + h - .35, z + R * sa, .85, glass, metal)
    lantern_head(F, x, y + h - .2, z, 1.0 if heads != 5 else 1.05, glass, metal)
    if solid: solid_box(F, (x, y + 1.0, z), (.3, 2.0, .3))


def murano_lamp(F, x, z, y=0.0, h=4.2, glass='vi-lantern-amber', metal='vi-iron'):
    """St Mark's Square's tall amber glass lamps: a ribbed flame of glass on an iron pole."""
    lathe(F, metal, x, z, [(0, .22), (.12, .2), (.2, .1), (h - 1.4, .07), (h - 1.3, .12), (h - 1.25, .12)], 10, y=y)
    k = 12
    for i in range(k):
        a0, a1 = i * TAU / k, (i + 1) * TAU / k
        prof = [(h - 1.25, .14), (h - .9, .3), (h - .45, .34), (h - .1, .22), (h + .2, .02)]
        for (ya, ra), (yb, rb) in zip(prof, prof[1:]):
            bulge_a = ra * (1 + .06 * math.cos(6 * (a0 + a1) / 2)); bulge_b = rb * (1 + .06 * math.cos(6 * (a0 + a1) / 2))
            quad(F, glass, (x + bulge_a * math.cos(a0), y + ya, z + bulge_a * math.sin(a0)), (x + bulge_a * math.cos(a1), y + ya, z + bulge_a * math.sin(a1)),
                 (x + bulge_b * math.cos(a1), y + yb, z + bulge_b * math.sin(a1)), (x + bulge_b * math.cos(a0), y + yb, z + bulge_b * math.sin(a0)))
    lathe(F, metal, x, z, [(h + .18, .05), (h + .3, .02), (h + .42, 0.001)], 6, y=y)


def mooring_pole(F, x, z, y0, y1, mat='vi-pole-red', cap='vi-gilt-plain'):
    lathe(F, mat, x, z, [(y0, .1), (y1, .09)], 8)
    lathe(F, cap, x, z, [(y1, .11), (y1 + .1, .11), (y1 + .2, .06), (y1 + .32, 0.001)], 8)


def cafe_set(F, x, z, y=0.0, chairs=4, umbrella=None, cloth='vi-cloth-white', metal='vi-iron'):
    lathe(F, metal, x, z, [(0, .22), (.04, .2), (.06, .04), (.7, .04)], 8, y=y)
    lathe(F, cloth, x, z, [(.7, .001), (.72, .42), (.78, .44), (.5, .45)], 14, y=y)
    for i in range(chairs):
        a = i * TAU / chairs + .4; cx, cz = x + .72 * math.cos(a), z + .72 * math.sin(a)
        G = Frame(F.b, *[F.p(cx, y, cz)[k] for k in (0, 2)], F.yaw - a + math.pi / 2, y=F.p(0, y, 0)[1])
        box(G, 'vi-wood-honey', (0, .45, 0), (.42, .04, .42))
        box(G, 'vi-wood-honey', (0, .7, .2), (.42, .45, .03))
        for sx in (-.18, .18):
            for sz in (-.18, .18): tube(G, metal, (sx, 0, sz), (sx, .45, sz), .012, 4)
    if umbrella:
        tube(F, 'vi-wood-honey', (x, y + .7, z), (x, y + 2.5, z), .025, 6)
        lathe(F, umbrella, x, z, [(2.0, 1.25), (2.45, .02)], 12, y=y)
    _ = None


def planter(F, x, z, y=0.0, r=.45, h=.6, mat='vi-limestone', plant='vi-plant', topiary=True):
    lathe(F, mat, x, z, [(0, r * .7), (.08, r * .7), (.1, r * .6), (h - .1, r), (h, r * 1.06), (h + .02, r * .9)], 12, y=y)
    disc(F, 'vi-soil', x, y + h - .03, z, r * .88, 12)
    if topiary:
        sphere(F, plant, (x, y + h + .55, z), r * 1.05, 10, 7)
    else:
        for i in range(7):
            a = i * 2.4; sphere(F, plant, (x + r * .5 * math.cos(a), y + h + .25 + (i % 3) * .15, z + r * .5 * math.sin(a)), r * .45, 6, 4)


# ------------------------------------------------------------------ Venetian house fronts
STUCCO = ['vi-stucco-cream', 'vi-stucco-ochre', 'vi-stucco-rose', 'vi-stucco-terracotta', 'vi-stucco-pink', 'vi-stucco-sage',
          'vi-stucco-yellow', 'vi-stucco-grey', 'vi-stucco-white', 'vi-brick']
SHOPS = ['vi-shop-fashion', 'vi-shop-glass-art', 'vi-shop-masks', 'vi-shop-sweets']
SHOP_NAMES = ['GELATERIA', 'MASCHERE', 'VETRERIA MURANO', 'PROFUMERIA', 'CAFFE', 'GIOIELLERIA', 'LIBRERIA', 'SARTORIA',
              'PASTICCERIA', 'TESSUTI', 'OROLOGERIA', 'CARTOLERIA', 'BOTTEGA', 'GALLERIA', 'MERLETTI', 'CIOCCOLATERIA',
              'ENOTECA', 'CAPPELLI', 'PELLETTERIA', 'ARGENTERIA', 'OTTICA', 'PROFUMI', 'CERAMICHE', 'TRATTORIA']


def house(F, x0, x1, height, seed=0, base=0.0, ground=4.2, floors=(2.8,), colour=None, names=None, window_kind=None,
          roof=True, sky=None, shopfronts=True, arcade_ground=False, lit=.25):
    """One Venetian house front on facade frame F from x0 to x1: shopfronts (or an arcade) on the ground floor, upper
    floors of windows with surrounds, shutters, balconies and flower boxes, string courses, quoins, a cornice, and
    (with `roof`) a tiled eave and chimneys up to `height`. The wall's face is at z = 0. Returns the shop name used."""
    rng = np.random.default_rng(seed)
    w = x1 - x0
    colour = colour or STUCCO[seed % len(STUCCO)]
    window_kind = window_kind or ['arch', 'rect', 'gothic', 'segment', 'arch', 'ogee', 'rect'][seed % 7]
    trim = 'vi-limestone' if colour != 'vi-limestone' else 'vi-limestone-shade'
    top = base + ground + sum(floors)
    eave = min(height - .25, top + .55)
    # --- ground floor
    gh = ground
    holes = []
    nshop = max(1, int(round(w / 4.2)))
    name = None
    if shopfronts:
        span = w / nshop
        for i in range(nshop):
            cx = x0 + span * (i + .5); ow = min(3.2, span - .9); oh = gh - .9
            kind = 'arch' if (arcade_ground or seed % 3 == 0) else 'rect'
            ring = opening(kind, cx, base + .05, ow, oh, 12)
            holes.append(ring)
            pane(F, SHOPS[int(rng.integers(0, len(SHOPS)))], ring, -1.1)
            pane(F, 'vi-shop-glass', ring, -.22)
            for s in (-1, 1): box(F, 'vi-bronze', (cx + s * ow / 2 - s * .04, base + .05 + oh / 2 - (ow / 4 if kind == 'arch' else 0), -.2), (.06, oh - (ow / 2 if kind == 'arch' else 0), .08))
            box(F, 'vi-bronze', (cx, base + .1, -.2), (ow, .1, .1))
            if kind == 'arch': arch_ring(F, cx, base + .05 + oh - ow / 2, ow, 0, trim, keystone=True)
            else: sweep_ring(F, trim, ring, P_SURROUND, 0)
        name = (names or SHOP_NAMES)[int(rng.integers(0, len(names or SHOP_NAMES)))]
        sign_w = min(w - .8, max(2.4, len(name) * .26))
        box(F, 'vi-wood-dark', ((x0 + x1) / 2, base + gh - .42, .08), (sign_w + .3, .5, .08))
        text(F, name, (x0 + x1) / 2, base + gh - .6, .14, .28, 'vi-sign-gold')
        if seed % 4 == 1:   # a striped awning over the shops
            aw = 'vi-awning-red' if seed % 8 == 1 else 'vi-awning-green'
            face(F, aw, [(x0 + .3, base + gh - .05, .05), (x1 - .3, base + gh - .05, .05), (x1 - .3, base + gh - .65, 1.25), (x0 + .3, base + gh - .65, 1.25)])
    ground_mat = 'vi-rustication' if seed % 2 == 0 else trim
    wall(F, ground_mat, [(x0, base), (x1, base), (x1, base + gh), (x0, base + gh)], holes, 0, 1.12, trim)   # reveals reach the display
    sweep_facade(F, trim, x0, x1, base, P_SKIRT)
    sweep_facade(F, trim, x0, x1, base + gh - .02, P_STRING)
    # --- upper floors
    y = base + gh + .16
    nwin = max(1, int(round(w / 2.3)))
    span = w / nwin
    for fi, fh in enumerate(floors):
        holes = []
        ww = min(1.35, span * .48); wh = fh * .62 if fi == 0 else fh * .56
        y0 = y + fh * .2
        for i in range(nwin):
            cx = x0 + span * (i + .5)
            kind = window_kind if not (fi == 1 and seed % 5 == 2) else 'rect'
            lit_glass = 'vi-window-lit' if rng.random() < lit else 'vi-window-dark'
            balcony = None
            if fi == 0 and nwin >= 3 and i == nwin // 2 and seed % 2 == 0: balcony = 'stone'
            elif rng.random() < .3: balcony = 'iron'
            elif rng.random() < .3: balcony = 'flowers'
            shutters = ['vi-shutter-green', 'vi-shutter-brown', None][seed % 3] if kind in ('rect', 'segment') else None
            ring = window(F, kind, cx, y0, ww, wh, 0, .22, lit_glass, trim, True, shutters, kind in ('arch', 'segment'),
                          'cornice' if (fi == 0 and kind == 'rect') else ('triangle' if (fi == 0 and seed % 6 == 3) else None), True, balcony)
            holes.append(ring)
        wall(F, colour, [(x0, y - .16), (x1, y - .16), (x1, y + fh), (x0, y + fh)], holes, 0, .22, trim)
        y += fh
        if fi < len(floors) - 1: sweep_facade(F, trim, x0, x1, y - .06, P_STRING[:5] + [(0, .1)])
    # quoins at both ends
    for x in (x0 + .22, x1 - .22):
        for k, yy in enumerate(np.arange(base + gh + .2, top - .2, .45)):
            box(F, trim, (x, yy, .03), (.44 if k % 2 == 0 else .3, .36, .06))
    # cornice, eave, roof and chimneys
    sweep_facade(F, trim, x0, x1, top, P_CORNICE if seed % 2 == 0 else P_CORNICE_SMALL)
    if roof and eave > top + .3:
        yr = top + (.48 if seed % 2 == 0 else .2)
        face(F, 'vi-roof-tile', [(x0, yr, .3), (x1, yr, .3), (x1, eave, -1.4), (x0, eave, -1.4)])
        for k in range(int(rng.integers(1, 3))):
            cx = x0 + w * (.25 + .5 * rng.random()); ch = height - .15 - eave
            if ch > .35:
                box(F, 'vi-chimney', (cx, eave + ch / 2 - .1, -1.0), (.5, ch, .5))
                lathe(F, 'vi-chimney', cx, -1.0, [(eave + ch - .1, .32), (eave + ch + .02, .32)], 8)
    elif not roof:
        box(F, colour, ((x0 + x1) / 2, (top + height) / 2, -.02), (w, max(.01, height - top - .5), .04))
    return name


def house_row(F, x0, x1, height, seed=0, base=0.0, widths=(7.5, 9.0, 6.5, 10.5, 8.0, 5.5, 9.5), names=None, collide=True,
              **kw):
    """Fill a facade line from x0 to x1 with houses of varying widths and storey heights; one collider for the row."""
    x = x0; k = seed; out = []
    floors_sets = [(2.9, 2.5), (3.1, 2.3), (2.7, 2.7), (3.4,), (2.8, 2.6)]
    while x < x1 - .5:
        w = widths[k % len(widths)]
        if x1 - (x + w) < 4: w = x1 - x
        fl = floors_sets[k % len(floors_sets)]
        room = height - .6 - 4.2
        scale = min(1.0, room / sum(fl)); fl = tuple(f * scale for f in fl)
        out.append(house(F, x, x + w, height, k, base, 4.2, fl, names=names, **kw))
        x += w; k += 1
    if collide: solid_quad(F, (x0, base, -.15), (x1, base, -.15), (x1, base + height, -.15), (x0, base + height, -.15))
    return out


# ------------------------------------------------------------------ bridges, canals, gondolas
def stone_bridge(F, span, width, rise, y=0.0, water=None, opening_half=None, mat='vi-limestone', tread='vi-limestone-shade',
                 n=16, balusters=True):
    """A Venetian stone footbridge along local x from -span/2 to span/2 over a canal running along z, deck `rise` above
    the quays (y) at the middle. A segmental arch springs from the canal walls (half opening `opening_half`, default
    0.4 of the span) a little above the water; spandrel walls with an archivolt and keystone on both faces; stepped
    treads over a walkable collision ramp; parapets (balustrades) that follow the deck."""
    L = span / 2; hw = width / 2
    a = opening_half or span * .4
    water = y - .55 if water is None else water
    def deck(x): return y + rise * (1 - (min(abs(x), L) / L) ** 2)
    ys, yk = water + .3, y + rise - .5          # springing and crown of the intrados
    h = yk - ys; R = (a * a + h * h) / (2 * h); yc = yk - R; half = math.asin(min(1, a / R))
    arc = [(R * math.sin(t), yc + R * math.cos(t)) for t in np.linspace(-half, half, n + 1)]
    xs = np.linspace(-L, L, 2 * n + 1)
    top = [(x, deck(x)) for x in xs]
    # spandrel walls: between the deck line and the intrados, down to the springing outside the arch
    outline = [(-L, y - .25)] + top + [(L, y - .25), (a, y - .25), (a, ys)] + arc[::-1] + [(-a, ys), (-a, y - .25)]
    poly = Polygon(outline).buffer(0)
    for s in (-1, 1):
        for q in parts(poly):
            for t in triangles(q): face(F, mat, [(px, py, s * hw) for px, py in list(t.exterior.coords)[:-1]])
        # archivolt and keystone
        A = np.linspace(-half, half, n + 1)
        sweep_frames(F, mat, [np.array([R * math.sin(t), yc + R * math.cos(t), s * hw]) for t in A],
                     [np.array([math.sin(t), math.cos(t), 0]) for t in A], [np.array([0, 0, s * 1.])] * len(A),
                     [(0, 0), (0, .06), (.08, .08), (.38, .08), (.42, .04), (.42, 0)])
        box(F, mat, (0, yk + .28, s * (hw + .05)), (.36, .5, .14))
        # deck edge moulding following the deck
        sweep_frames(F, mat, [np.array([x, yy - .12, s * hw]) for x, yy in top], [np.array([0, 0, s * 1.])] * len(top),
                     [np.array([0, 1., 0])] * len(top), [(0, -.06), (.08, -.06), (.1, 0), (.08, .06), (0, .06)])
    # soffit (the arch's underside) and the abutment faces
    for (x0, y0), (x1, y1) in zip(arc, arc[1:]): quad(F, mat, (x0, y0, -hw), (x1, y1, -hw), (x1, y1, hw), (x0, y0, hw))
    # treads (visual steps) and the walkable ramp
    k = int(round(rise / .15)); xs_steps = [L * math.sqrt(1 - (i / k)) for i in range(k + 1)]
    for sgn in (-1, 1):
        for i in range(k):
            xa, xb = sgn * xs_steps[i], sgn * xs_steps[i + 1]; yy = y + rise * (i + 1) / k
            lo, hi = min(xa, xb), max(xa, xb)
            box(F, tread, ((lo + hi) / 2, yy - .08, 0), (hi - lo + .03, .16, width - .3))
            box(F, mat, (xb - sgn * .015, yy - .01, 0), (.05, .03, width - .3))
    for (x0, y0), (x1, y1) in zip(top, top[1:]):
        solid_quad(F, (x0, y0, -hw), (x1, y1, -hw), (x1, y1, hw), (x0, y0, hw))
    # parapets
    for s in (-1, 1):
        z = s * (hw - .14)
        rail = [np.array([x, yy + .98, z]) for x, yy in top]
        sweep_frames(F, mat, rail, [np.array([0, 0, 1.])] * len(rail), [np.array([0, 1., 0])] * len(rail),
                     [(-.15, 0), (.15, 0), (.15, .05), (.11, .1), (-.11, .1), (-.15, .05), (-.15, 0)])
        sweep_frames(F, mat, [np.array([x, yy, z]) for x, yy in top], [np.array([0, 0, 1.])] * len(top), [np.array([0, 1., 0])] * len(top),
                     [(-.14, 0), (.14, 0), (.14, .14), (-.14, .14), (-.14, 0)])
        if balusters:
            for x in np.arange(-L + .45, L - .3, .3):
                if abs(abs(x) - L * .55) < .2: continue
                lathe(F, mat, x, z, [(0, .05), (.06, .045), (.22, .085), (.42, .045), (.55, .033), (.64, .05), (.72, .035), (.84, .05)], 6, y=deck(x) + .14)
        for x in (-L + .18, -L * .55, 0, L * .55, L - .18):
            box(F, mat, (x, deck(x) + .55, z), (.32, 1.1, .32))
        for (x0, y0), (x1, y1) in zip(top[::2], top[2::2]):
            solid_quad(F, (x0, y0, z), (x1, y1, z), (x1, y1 + 1.05, z), (x0, y0 + 1.05, z))


def canal_edge(F, a, b, y_top, y_water, mat='vi-limestone', wall_mat='vi-brick'):
    """Quay edge along plan segment a->b (local): an ivory coping stone over a brick wall down to the water."""
    sweep_plan(F, wall_mat, [a, b], [(0, y_water - .6), (0, y_top - .22)])
    sweep_plan(F, mat, [a, b], [(0, y_top - .22), (.12, y_top - .22), (.12, y_top), (-.35, y_top), (-.35, y_top - .05)])


def gondola_at(B, x, z, yaw, y):
    from venetian_gondola import gondola
    gondola(B, x, z, yaw, y)
