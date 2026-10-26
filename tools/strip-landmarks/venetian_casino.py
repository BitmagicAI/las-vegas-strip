"""The Venetian casino and Restaurant Row, Level 1, rebuilt to the resort map at full detail (2026-10-23).

The previous interiors looked low in detail and blocky to the owner. This
module is the streamed sub-venue 'venetianCasino' (build: build_venetian_interior.py casino). World metres, X east,
Y up, Z south; floor L1 = 0.24; the ceiling stays under 6.04 (the Shoppes' canal bed above sits at 6.3) except the
escalators, which rise to Level 2 (7.24).

  casino          x 288..392, z -760..-652 (inner wall faces 0.5 m in). Openings: the Great Hall arch (west wall,
                  z -695..-679; the lobby builds the arch), the rotunda (south wall, x 317..339), Restaurant Row (north
                  wall, x 336..352).
  structure       marble Corinthian columns on 7 x 7 grid lines (XL, ZL) under gilt girders. Each bay: a coffered
                  ceiling (cream, red and green ornament panels), or over the aisles a fresco in an oval dish with a gilt
                  frame; a Murano chandelier in every bay; one pool light per bay.
  aisles          marble with a rust border and a black fillet: W1 east-west from the Great Hall arch, W2 north-south
                  from the rotunda to Restaurant Row (compass rose at the crossing), the rotunda foyer, the Restaurant
                  Row plaza, the escalator walk, the salon walk and the cage apron. Burgundy and gold carpet elsewhere.
  gaming          slot banks (6-9 machines a side, back to back, ornate end caps with lit signs) packed into the fields
                  between the aisles with 3.8 m aisles; a blackjack pit (SW); a roulette and craps pit (SE); the
                  cashier's cage on the south wall; a round bar around the column at (355, -706); the high-limit salon
                  in the NW corner (glass walls, drapes, baccarat, its own fresco and chandelier).
  escalators      an up and a down escalator at x 375..383 from the floor at z -726 to Level 2 at z -742.5 (30 degrees
                  between the transitions). The ceiling well over them is x 374.75..383.25, z -742.75..-733.35; the
                  Level 2 opening (the Shoppes') needs to reach z -734 for the riders' heads (see WELL below).
  Restaurant Row  x 336..352, z -806..-760: restaurant fronts on both sides, a ristorante closing the north end against
                  the podium wall, lamps, cafe tables and planters under a painted dusk sky.
"""
import math
import numpy as np
from shapely.geometry import Polygon, Point, box as sbox
from shapely.ops import unary_union
from common import Frame
import venetian_kit as K
from surface_geometry import triangles
from building_surfaces import parts
import venetian_interior_plan as PLAN

TAU = math.tau
Y0 = PLAN.L1
TOP = 6.04 - Y0                         # 5.8 (local): no casino surface above this
GIRDER_Y, COFFER_Y = 4.75, 5.3          # girder soffits and the coffer lattice (local heights)
HW = .35                                # girder half width
X0, Z0, X1, Z1 = 288.0, -760.0, 392.0, -652.0
WX0, WZ0, WX1, WZ1 = 288.5, -759.5, 391.5, -652.5
XL = [301.5, 316.0, 330.5, 341.5, 355.0, 368.5, 386.0]
ZL = [-747.0, -733.5, -720.0, -706.0, -692.5, -681.5, -667.0]
SALON = (288.5, -759.5, 316.0, -733.5)
ESC_X, ESC_Z = 379.0, -726.0            # the escalators' axis and the bottom comb plates
WELL = (374.75, -742.75, 383.25, -733.35)
BAR = (355.0, -706.0)
RR = (336.0, -806.0, 352.0, -760.0)
WALKS = [(288.0, -691.0, 391.5, -683.0),   # W1: from the Great Hall arch
         (332.0, -750.0, 340.0, -662.0),   # W2: from the rotunda to Restaurant Row
         (315.0, -662.0, 341.0, -652.0),   # the rotunda foyer
         (330.0, -760.0, 354.0, -749.0),   # the Restaurant Row plaza
         (340.0, -726.0, 391.5, -721.0),   # the escalator walk
         (306.5, -733.5, 310.5, -691.0),   # the salon walk
         (290.5, -660.0, 315.0, -656.5)]   # the cage apron
CROSSING = (336.0, -687.0)
WARM = 0xffe2b8
SLOT_NAMES = ['MURANO', 'CARNEVALE', 'PALAZZO', 'GONDOLA', 'RIALTO', 'DUCATS', 'LEONE', 'BELLA', 'MAGNIFICO', 'CASANOVA',
              'SEVENS', 'LAGUNA', 'TESORO', 'MASCHERA', 'FORTUNA', 'DOGE']      # short: every letter is ~500 triangles
SLOT_STYLES = [('vi-casino-cabinet', 'vi-casino-topper-blue', 'vi-slot-screen'),
               ('vi-casino-cabinet-red', 'vi-casino-topper-gold', 'vi-casino-screen-b'),
               ('vi-iron', 'vi-slot-topper', 'vi-slot-screen'),
               ('vi-casino-cabinet', 'vi-casino-topper-green', 'vi-casino-screen-b'),
               ('vi-casino-cabinet-red', 'vi-slot-topper', 'vi-slot-screen')]
PITCH = .76                             # slot machine pitch along a bank


# ------------------------------------------------------------------ small helpers
def oface(F, mat, pts, hint, solid=False):
    """A planar face with its normal (Newell) turned toward the local direction `hint`."""
    n = np.zeros(3)
    P = [np.asarray(p, float) for p in pts]
    for i in range(len(P)):
        a, b = P[i], P[(i + 1) % len(P)]
        n += np.array([(a[1] - b[1]) * (a[2] + b[2]), (a[2] - b[2]) * (a[0] + b[0]), (a[0] - b[0]) * (a[1] + b[1])])
    pts = [tuple(map(float, p)) for p in pts]
    if float(np.dot(n, hint)) < 0: pts = pts[::-1]
    K.face(F, mat, pts, solid)


def fill(F, mat, geom, y=0.0, up=True, solid=False):
    """Triangulate a plan polygon (local x, z) into a horizontal surface."""
    for q in parts(geom):
        for t in triangles(q):
            oface(F, mat, [(x, y, z) for x, z in list(t.exterior.coords)[:-1]], (0, 1 if up else -1, 0), solid)


def prism(F, mat, sec, axis, lo, hi, caps=True):
    """Extrude a 2D section along a local axis: 'x' (section in z, y), 'y' (x, z) or 'z' (x, y)."""
    def P(u, v, t):
        return (t, v, u) if axis == 'x' else (u, t, v) if axis == 'y' else (u, v, t)
    poly = Polygon(sec)
    ccw = poly.exterior.is_ccw
    for (ua, va), (ub, vb) in zip(sec, sec[1:] + sec[:1]):
        eu, ev = ub - ua, vb - va
        nu, nv = (ev, -eu) if ccw else (-ev, eu)
        oface(F, mat, [P(ua, va, lo), P(ub, vb, lo), P(ub, vb, hi), P(ua, va, hi)], P(nu, nv, 0))
    if caps:
        for q in parts(poly.buffer(0)):
            for t in triangles(q):
                pts = list(t.exterior.coords)[:-1]
                oface(F, mat, [P(u, v, hi) for u, v in pts], P(0, 0, 1))
                oface(F, mat, [P(u, v, lo) for u, v in pts], P(0, 0, -1))


def seg_frame(B, a, b, y=Y0):
    """A frame at plan point a with local x running to b (local +z is to the right of a->b, seen from above, north up)."""
    dx, dz = b[0] - a[0], b[1] - a[1]; L = math.hypot(dx, dz)
    return Frame(B, a[0], a[1], math.atan2(-dz / L, dx / L), y=y), L


def face_yaw(dx, dz):
    """Relative yaw that turns a child frame's +z toward the local direction (dx, dz)."""
    return math.atan2(dx, dz)


def ellipse(cx, cz, rx, rz, n, a0=0.0):
    return [(cx + rx * math.cos(a0 + a), cz + rz * math.sin(a0 + a)) for a in np.linspace(0, TAU, n, endpoint=False)]


def stadium(a, r, n=10):
    """Plan outline of a stadium: straight half length a along x, end radius r (counter-clockwise in x, z)."""
    pts = [(a + r * math.cos(t), r * math.sin(t)) for t in np.linspace(-math.pi / 2, math.pi / 2, n + 1)]
    pts += [(-a + r * math.cos(t), r * math.sin(t)) for t in np.linspace(math.pi / 2, 1.5 * math.pi, n + 1)]
    return pts


def ring_sweep(F, mat, pts, profile, y, closed=True):
    """A horizontal moulding along a plan ring; profile (out, up) with `out` away from the ring's inside."""
    ring = list(pts)
    if Polygon(ring).exterior.is_ccw: ring = ring[::-1]     # sweep_plan offsets to the left of travel: make that outward
    K.sweep_plan(F, mat, ring, profile, y, closed)


# ------------------------------------------------------------------ floors
def floors(B, G):
    B.source = 'floor'
    casino = sbox(X0, Z0, X1, Z1)
    walk = unary_union([sbox(*r) for r in WALKS]).intersection(casino)
    rose = Point(*CROSSING).buffer(3.6, 64)
    border = walk.difference(walk.buffer(-.4, join_style=2))
    fillet = walk.buffer(-.4, join_style=2).difference(walk.buffer(-.48, join_style=2))
    field = walk.buffer(-.48, join_style=2)
    fill(G, 'vi-carpet', casino.difference(walk))
    fill(G, 'vi-marble-rust', border)
    fill(G, 'vi-marble-black', fillet.difference(rose))
    fill(G, 'vi-diag-grid', field.difference(rose))
    # the compass rose where the main aisles cross
    cx, cz = CROSSING
    r1, r2, r3 = Point(cx, cz).buffer(3.6, 64), Point(cx, cz).buffer(3.4, 64), Point(cx, cz).buffer(2.9, 64)
    fill(G, 'vi-marble-black', r1.difference(r2))
    fill(G, 'vi-marble-green', r2.difference(r3))
    star = []
    for i in range(16):
        a = i * TAU / 16; r = 2.75 if i % 2 == 0 else (1.15 if i % 4 == 1 else .95)
        star.append((cx + r * math.cos(a), cz + r * math.sin(a)))
    star = Polygon(star)
    fill(G, 'vi-marble-cream', r3.difference(star))
    for i in range(8):
        a = i * TAU / 8
        tip = (cx + 2.75 * math.cos(a), cz + 2.75 * math.sin(a))
        for s, mat in ((-1, 'vi-marble-rust'), (1, 'vi-marble-black' if i % 2 else 'vi-gilt-plain')):
            side = (cx + 1.05 * math.cos(a + s * TAU / 16), cz + 1.05 * math.sin(a + s * TAU / 16))
            oface(G, mat, [(cx, 0, cz), (tip[0], 0, tip[1]), (side[0], 0, side[1])], (0, 1, 0))
    # Restaurant Row: polished stone flags
    fill(G, 'vi-street-flags', sbox(*RR))
    # an underlay so no hairline crack shows the void, and the walkable floor (one collider)
    oface(G, 'vi-iron', [(X0, -.02, Z0), (X1, -.02, Z0), (X1, -.02, Z1), (X0, -.02, Z1)], (0, 1, 0))
    oface(G, 'vi-iron', [(RR[0], -.02, RR[1]), (RR[2], -.02, RR[1]), (RR[2], -.02, RR[3]), (RR[0], -.02, RR[3])], (0, 1, 0))
    K.solid_quad(G, (X0, 0, Z0), (X1, 0, Z0), (X1, 0, Z1), (X0, 0, Z1))
    K.solid_quad(G, (RR[0], 0, RR[1]), (RR[2], 0, RR[1]), (RR[2], 0, RR[3]), (RR[0], 0, RR[3]))


# ------------------------------------------------------------------ ceiling: girders, coffers, ovals, chandeliers
def girder(B, a, b):
    F, L = seg_frame(B, a, b)
    if L < .2: return
    oface(F, 'vi-gilt', [(0, GIRDER_Y, -HW), (L, GIRDER_Y, -HW), (L, GIRDER_Y, HW), (0, GIRDER_Y, HW)], (0, -1, 0))
    for s in (-1, 1):
        oface(F, 'vi-stucco-cream', [(0, GIRDER_Y, s * HW), (L, GIRDER_Y, s * HW), (L, COFFER_Y, s * HW), (0, COFFER_Y, s * HW)], (0, 0, s))
        S = F if s > 0 else K.rot_frame(F, L, 0, math.pi)
        K.sweep_facade(S, 'vi-gilt-plain', 0, L, GIRDER_Y, [(0, 0), (.05, 0), (.05, .025), (.03, .05), (.06, .09), (0, .12)], HW)
        K.sweep_facade(S, 'vi-gilt-plain', 0, L, COFFER_Y - .16, [(0, 0), (.03, .03), (.03, .07), (.09, .12), (.12, .16), (0, .16)], HW)
    k = max(1, int(L / 2.4))
    for i in range(k):
        x = (i + .5) * L / k
        K.lathe(F, 'vi-gilt-plain', x, 0, [(GIRDER_Y, .15), (GIRDER_Y - .03, .13), (GIRDER_Y - .05, .07), (GIRDER_Y - .065, .001)], 8)


def coffer_field(G, ax, az, bx, bz, tint, cell=2.5):
    def panel(i, j):
        return 'vi-coffer-cream' if (i + j) % 2 == 0 else tint
    K.coffers(G, ax, bx, az, bz, COFFER_Y, cell=cell, beam=.28, depth=.4, field='vi-gilt', beam_mat='vi-gilt-plain', panel=panel)
    nx = max(1, round((bx - ax) / cell)); nz = max(1, round((bz - az) / cell))
    return COFFER_Y + (.4 if nx % 2 and nz % 2 else 0)        # the hanging height at the field's centre


def oval_bay(B, G, ax, az, bx, bz, mat, y=5.2, dish=.5, n=48, chand=(1.3, 3, 10, 1.6)):
    cx, cz = (ax + bx) / 2, (az + bz) / 2; W, D = bx - ax, bz - az
    rx, rz = W * .37, D * .37
    rx = min(rx, rz * 1.55); rz = min(rz, rx * 1.15)
    hole = Polygon(ellipse(cx, cz, rx, rz, n))
    c = min(W, D) * .15; inset = .3
    corners = [(ax + inset, az + inset), (bx - inset - c, az + inset), (ax + inset, bz - inset - c), (bx - inset - c, bz - inset - c)]
    soffit = sbox(ax, az, bx, bz).difference(hole)
    for x, z in corners: soffit = soffit.difference(sbox(x - .1, z - .1, x + c + .1, z + c + .1))
    fill(G, 'vi-stucco-white', soffit, y, up=False)
    K.oval_fresco(G, cx, y, cz, rx, rz, mat, 'vi-gilt', n, dish)
    ring_sweep(G, 'vi-gilt-plain', ellipse(cx, cz, rx + .72, rz + .72, n), [(-.05, 0), (-.05, -.03), (0, -.06), (.05, -.03), (.05, 0)], y)
    ring_sweep(G, 'vi-gilt-plain', [(ax + .2, az + .2), (bx - .2, az + .2), (bx - .2, bz - .2), (ax + .2, bz - .2)],
               [(-.07, 0), (-.07, -.04), (0, -.08), (.07, -.04), (.07, 0)], y)
    for k, (x, z) in enumerate(corners):
        tint = 'vi-coffer-red' if k in (0, 3) else 'vi-coffer-green'
        K.coffers(G, x, x + c, z, z + c, y - .015, cell=c, beam=.16, depth=.25, field='vi-gilt', beam_mat='vi-gilt-plain', panel=lambda i, j, t=tint: t)
    if chand: K.chandelier(G, cx, y + dish - .01, cz, chand[0], chand[1], chand[2], drop=chand[3])
    return cx, cz


def ceiling(B, G):
    B.source = 'ceiling'
    xs = [WX0] + XL + [WX1]; zs = [WZ0] + ZL + [WZ1]
    sx0, sz0, sx1, sz1 = SALON
    in_salon = lambda x, z: sx0 - .01 < x < sx1 + .01 and sz0 - .01 < z < sz1 + .01
    # girders: along z on the x-lines, along x on the z-lines, cut at the bosses; none inside the salon or over the well
    for xc in XL:
        for za, zb in zip(zs, zs[1:]):
            if xc == 301.5 and zb <= sz1 + .01: continue
            girder(B, (xc, za + (.46 if za in ZL else 0)), (xc, zb - (.46 if zb in ZL else 0)))
    for zc in ZL:
        for xa, xb in zip(xs, xs[1:]):
            if zc == -747.0 and xb <= sx1 + .01: continue
            a, b = xa + (.46 if xa in XL else 0), xb - (.46 if xb in XL else 0)
            if zc == -733.5 and xa == 368.5:
                girder(B, (a, zc), (WELL[0] - .02, zc)); girder(B, (WELL[2] + .02, zc), (b, zc)); continue
            girder(B, (a, zc), (b, zc))
    for xc in XL:
        for zc in ZL:
            if xc == 301.5 and zc == -747.0: continue
            K.box(G, 'vi-gilt-plain', (xc, (4.68 + TOP) / 2, zc), (.92, TOP - 4.68, .92))
            K.sweep_plan(G, 'vi-gilt', [(xc - .46, zc - .46), (xc - .46, zc + .46), (xc + .46, zc + .46), (xc + .46, zc - .46)],
                         [(0, 0), (.06, 0), (.06, .05), (0, .1)], 4.68, True)
    # bays
    ovals = {(i, j) for i in range(len(xs) - 1) for j in range(len(zs) - 1)
             if (zs[j], zs[j + 1]) == (-692.5, -681.5) or (xs[i], xs[i + 1]) == (330.5, 341.5)}
    ovals |= {(xs.index(316.0), zs.index(-667.0)), (xs.index(341.5), 0)}
    paintings = ['vi-fresco-oval', 'vi-fresco-a', 'vi-fresco-b']
    k = 0
    for i, (xa, xb) in enumerate(zip(xs, xs[1:])):
        for j, (za, zb) in enumerate(zip(zs, zs[1:])):
            ax, bx = xa + (HW if xa in XL else 0), xb - (HW if xb in XL else 0)
            az, bz = za + (HW if za in ZL else 0), zb - (HW if zb in ZL else 0)
            cx, cz = (xa + xb) / 2, (za + zb) / 2
            if in_salon(cx, cz): continue
            tint = 'vi-coffer-red' if (i + j) % 2 == 0 else 'vi-coffer-green'
            if (i, j) in ovals:
                oval_bay(B, G, ax, az, bx, bz, paintings[k % 3]); k += 1
            elif (xa, xb, za, zb) == (368.5, 386.0, -747.0, -733.5):
                wx0, wz0, wx1, wz1 = WELL
                coffer_field(G, ax, az, wx0, bz, tint, 2.0)
                coffer_field(G, wx1, az, bx, bz, tint, 2.3)
                coffer_field(G, wx0, az, wx1, wz0, tint, 2.1)
                # the well's fascia (gilt) on the west, east and north edges
                for x in (wx0 + .1, wx1 - .1):
                    K.box(G, 'vi-gilt-plain', (x, (4.9 + TOP) / 2, (wz0 + wz1) / 2), (.2, TOP - 4.9, wz1 - wz0))
                K.box(G, 'vi-gilt-plain', ((wx0 + wx1) / 2, (4.9 + TOP) / 2, wz0 + .1), (wx1 - wx0, TOP - 4.9, .2))
                K.box(G, 'vi-gilt-plain', ((wx0 + wx1) / 2, (COFFER_Y + TOP) / 2, wz1 - .1), (wx1 - wx0, TOP - COFFER_Y, .2))
                G.light(cx - 5, 5.16, cz, WARM, 260, 20)
                continue
            else:
                yh = coffer_field(G, ax, az, bx, bz, tint)
                if not (xb - xa < 7):
                    K.chandelier(G, cx, yh - .01, cz, .95, 2, 8, drop=1.25)
            G.light(cx, 5.16, cz, WARM, 280 if (i, j) in ovals else 240, 20)
    # the high-limit salon: one bay under a large oval fresco and its own chandelier
    oval_bay(B, G, sx0, sz0, sx1 - HW, sz1 - HW, 'vi-fresco-oval', y=5.2, dish=.55, n=64, chand=None)
    K.chandelier(G, (sx0 + sx1) / 2, 5.74, (sz0 + sz1) / 2, 2.0, 3, 14, drop=1.9)
    K.chandelier(G, (sx0 + sx1) / 2, 5.74, (sz0 + sz1) / 2, 1.1, 2, 10, glass='vi-lantern', drop=1.0)
    G.light((sx0 + sx1) / 2, 4.6, (sz0 + sz1) / 2, 0xffd9a8, 320, 22)


# ------------------------------------------------------------------ columns and walls
def columns(B, G):
    B.source = 'columns'
    for x in XL:
        for z in ZL:
            if x == 301.5 and z == -747.0: continue      # the salon's centre: its chandelier hangs there
            K.column(G, x, z, 4.66, .3, 'vi-marble-cream', 'vi-gilt-plain', 'vi-marble-rust', 'corinthian', 16)
            K.box(G, 'vi-marble-black', (x, .03, z), (.98, .06, .98))
            K.sweep_plan(G, 'vi-gilt-plain', [(x - .42, z - .42), (x - .42, z + .42), (x + .42, z + .42), (x + .42, z - .42)],
                         [(0, 0), (.03, 0), (.03, .04), (0, .06)], .3, True)


def pilaster(F, x, z=0.0, w=.62, sconce=False):
    K.box(F, 'vi-marble-rust', (x, .5, z + .07), (w + .16, 1.0, .14))
    K.box(F, 'vi-gilt-plain', (x, 1.03, z + .08), (w + .1, .06, .16))
    K.box(F, 'vi-marble-cream', (x, 2.37, z + .07), (w, 2.62, .14))
    for dx in (-w * .28, 0, w * .28):
        K.box(F, 'vi-limestone-shade', (x + dx, 2.37, z + .142), (.05, 2.3, .006))
    K.box(F, 'vi-gilt-plain', (x, 3.79, z + .08), (w + .06, .22, .16))
    K.box(F, 'vi-gilt-plain', (x, 4.0, z + .09), (w + .18, .2, .18))
    for s in (-1, 1):
        K.path(F, 'vi-gilt-plain', [(x + s * (w / 2 - .02) + s * .06 * math.cos(t), 3.86 + .06 * math.sin(t), z + .19)
                                    for t in np.linspace(0, TAU * .85, 7)], .018, 4)
    if sconce:
        K.box(F, 'vi-gilt-plain', (x, 2.75, z + .15), (.16, .3, .03))
        K.path(F, 'vi-gilt-plain', [(x, 2.65, z + .16), (x, 2.6, z + .3), (x, 2.7, z + .42)], .018, 5)
        K.lathe(F, 'vi-gilt-plain', x, z + .42, [(2.68, .001), (2.72, .07), (2.76, .05)], 8)
        K.lathe(F, 'vi-crystal', x, z + .42, [(2.76, .045), (2.92, .055), (2.97, .001)], 8)


def wall_panel(F, s0, s1, kind):
    ring = [(s0, 1.3), (s1, 1.3), (s1, 3.6), (s0, 3.6)]
    mat = 'vi-casino-mirror' if kind == 0 else 'vi-coffer-red' if kind == 1 else 'vi-coffer-green'
    K.quad(F, mat, (s0, 1.3, .02), (s1, 1.3, .02), (s1, 3.6, .02), (s0, 3.6, .02))
    K.sweep_ring(F, 'vi-gilt-plain', ring, K.P_GILT_FRAME, .02)
    if kind == 0:
        K.sweep_arc(F, 'vi-gilt-plain', (s0 + s1) / 2, 3.6, .02, min(.4, (s1 - s0) * .2), 0, math.pi, [(0, 0), (.05, 0), (.05, .05), (0, .05)], 8)
    K.sweep_ring(F, 'vi-gilt-plain', [(s0 + .05, .25), (s1 - .05, .25), (s1 - .05, .8), (s0 + .05, .8)],
                 [(-.02, 0), (-.02, .02), (.02, .02), (.02, 0)], .06)


def perimeter_wall(B, a, b, k):
    F, L = seg_frame(B, a, b)
    horiz = abs(a[1] - b[1]) < .01
    st = [0.0, L]
    for v in (XL if horiz else ZL):
        t = (v - a[0]) / (b[0] - a[0]) * L if horiz else (v - a[1]) / (b[1] - a[1]) * L
        if .8 < t < L - .8: st.append(t)
    st = sorted(st); stations = []
    for s0, s1 in zip(st, st[1:]):
        m = max(1, round((s1 - s0) / 4.4))
        stations += [s0 + (s1 - s0) * i / m for i in range(m)]
    stations.append(L)
    oface(F, 'vi-stucco-cream', [(0, 0, 0), (L, 0, 0), (L, TOP, 0), (0, TOP, 0)], (0, 0, 1))
    K.box(F, 'vi-marble-rust', (L / 2, .5, .03), (L, 1.0, .06))
    K.sweep_facade(F, 'vi-marble-black', 0, L, 0, [(0, 0), (.1, 0), (.1, .14), (.08, .18), (0, .2)])
    K.sweep_facade(F, 'vi-gilt-plain', 0, L, .98, [(0, 0), (.09, 0), (.09, .03), (.07, .07), (0, .08)])
    for i, (s0, s1) in enumerate(zip(stations, stations[1:])):
        wall_panel(F, s0 + .45, s1 - .45, [0, 1, 0, 2][(i + k) % 4])
    for i, s in enumerate(stations):
        pilaster(F, min(max(s, .36), L - .36), 0, .62, sconce=(0 < i < len(stations) - 1))
    K.box(F, 'vi-limestone', (L / 2, 4.66, .07), (L, 1.12, .14))
    K.entablature(F, 0, L, 4.1, 'vi-limestone', 'vi-gilt', 'vi-gilt-plain', z=.14, scale=.8)
    K.solid_quad(F, (0, 0, 0), (L, 0, 0), (L, TOP, 0), (0, TOP, 0))
    return F, L


def walls(B, G):
    B.source = 'walls'
    runs = [((288.5, -759.5), (336.0, -759.5)), ((352.0, -759.5), (391.5, -759.5)), ((391.5, -759.5), (391.5, -652.5)),
            ((391.5, -652.5), (339.0, -652.5)), ((317.0, -652.5), (288.5, -652.5)), ((288.5, -652.5), (288.5, -679.0)),
            ((288.5, -695.0), (288.5, -759.5))]
    for k, (a, b) in enumerate(runs): perimeter_wall(B, a, b, k)
    # jambs and headers of the three openings (the neighbouring venues draw their own sides)
    for (x, z, w, d) in [(288.25, -679.0, .5, 0), (288.25, -695.0, .5, 0), (317.0, -652.25, 0, .5), (339.0, -652.25, 0, .5),
                         (336.0, -759.75, 0, .5), (352.0, -759.75, 0, .5)]:
        K.box(G, 'vi-marble-cream', (x, TOP / 2, z), (max(w, .04), TOP, max(d, .04)))
    K.box(G, 'vi-limestone', (288.25, (5.0 + TOP) / 2, -687.0), (.5, TOP - 5.0, 16.0))
    K.sweep_facade(Frame(B, 288.5, -679.0, math.pi / 2, y=Y0), 'vi-gilt-plain', 0, 16, 5.0, [(0, 0), (.08, 0), (.08, .06), (.04, .1), (0, .12)])
    K.box(G, 'vi-limestone', (328.0, (5.0 + TOP) / 2, -652.25), (22.0, TOP - 5.0, .5))
    K.sweep_facade(Frame(B, 339.0, -652.5, math.pi, y=Y0), 'vi-gilt-plain', 0, 22, 5.0, [(0, 0), (.08, 0), (.08, .06), (.04, .1), (0, .12)])
    # Restaurant Row's portal: a header with an entablature and the name on both faces
    K.box(G, 'vi-limestone', (344.0, (4.3 + TOP) / 2, -759.75), (16.0, TOP - 4.3, .5))
    K.box(G, 'vi-limestone', (344.0, (TOP + 5.89) / 2, -760.03), (16.0, 5.89 - TOP, .06))    # Restaurant Row side, up to its sky
    for F, name in [(Frame(B, 336.0, -759.5, 0, y=Y0), 'RESTAURANT ROW'), (Frame(B, 352.0, -760.0, math.pi, y=Y0), 'RISTORANTI')]:
        K.entablature(F, 0, 16, 4.3, 'vi-limestone', 'vi-gilt', 'vi-gilt-plain', z=0, scale=.7, dentils=True)
        K.box(F, 'vi-marble-green', (8, 4.72, .08), (5.6, .36, .04))
        K.text(F, name, 8, 4.6, .11, .24, 'vi-sign-gold')
        if name == 'RISTORANTI':
            for x in (.35, 15.65): pilaster(F, x, 0, .62)


# ------------------------------------------------------------------ slot machines and banks
def slot_machine(M, style):
    cab, accent, screen = style
    K.box(M, 'vi-iron', (0, .06, 0), (.72, .12, .6))
    K.box(M, cab, (0, .55, -.01), (.74, .86, .64))
    K.box(M, 'vi-chrome', (0, .16, .31), (.7, .03, .012))
    K.box(M, accent, (0, .62, .318), (.52, .3, .01))
    prism(M, 'vi-iron', [(.31, .92), (.46, .96), (.46, 1.0), (.16, 1.09)], 'x', -.37, .37)
    for bx in (-.24, -.15, -.06, .03):
        K.box(M, 'vi-slot-topper' if bx < -.1 else 'vi-casino-topper-gold', (bx, 1.03, .385), (.055, .018, .035))
    K.lathe(M, 'vi-casino-led', .2, .37, [(1.02, .045), (1.05, .045), (1.06, .001)], 8)
    K.box(M, cab, (0, 1.43, -.06), (.74, .68, .5))
    for c, s in [((0, 1.13, .2), (.64, .04, .025)), ((0, 1.73, .2), (.64, .04, .025)), ((-.31, 1.43, .2), (.04, .6, .025)), ((.31, 1.43, .2), (.04, .6, .025))]:
        K.box(M, 'vi-chrome', c, s)
    K.quad(M, screen, (-.29, 1.15, .206), (.29, 1.15, .206), (.29, 1.71, .206), (-.29, 1.71, .206))
    K.box(M, cab, (0, 2.0, -.08), (.72, .46, .44))
    K.quad(M, 'vi-casino-screen-b' if screen == 'vi-slot-screen' else 'vi-slot-screen', (-.27, 1.82, .146), (.27, 1.82, .146), (.27, 2.18, .146), (-.27, 2.18, .146))
    K.box(M, 'vi-chrome', (0, 1.795, .15), (.62, .03, .02)); K.box(M, 'vi-chrome', (0, 2.205, .15), (.62, .03, .02))
    for s in (-1, 1): K.box(M, 'vi-casino-led', (s * .36, .53, .318), (.018, .74, .012))
    arch = [(-.33, 2.23), (.33, 2.23)] + [(.33 * math.cos(a), 2.4 + .33 * math.sin(a)) for a in np.linspace(0, math.pi, 9)][:-1] + [(-.33, 2.4)]
    prism(M, accent, arch, 'z', -.12, .1)
    K.sweep_arc(M, 'vi-chrome', 0, 2.4, .1, .33, 0, math.pi, [(0, 0), (.025, 0), (.025, .025), (0, .025)], 8)
    K.lathe(M, 'vi-casino-sign-red', .24, -.04, [(2.6, .03), (2.74, .03), (2.75, .001)], 6)
    K.lathe(M, 'vi-chrome', .24, -.04, [(2.52, .035), (2.6, .035)], 6)
    K.face(M, 'vi-sign-gold', [(-.2, 2.3, .103), (.2, 2.3, .103)] + [(.2 * math.cos(a), 2.42 + .2 * math.sin(a), .103) for a in np.linspace(0, math.pi, 7)][:-1] + [(-.2, 2.42, .103)])
    # the stool
    K.lathe(M, 'vi-bronze', 0, .98, [(0, .19), (.025, .19), (.05, .035), (.6, .032)], 8)
    K.lathe(M, 'vi-leather', 0, .98, [(.6, .2), (.66, .23), (.72, .21), (.74, .001)], 10)
    K.box(M, 'vi-leather', (0, .95, 1.2), (.34, .28, .05))
    K.tube(M, 'vi-bronze', (0, .72, 1.17), (0, .82, 1.19), .015, 4)


def bank_cap(E, cab, sign, name=None, w=1.5):
    """An ornate end cap on frame E (front toward +z, the bank behind), `w` wide, with a lit sign on top."""
    h = w / 2
    K.box(E, 'vi-marble-black', (0, .07, .02), (w + .12, .14, .58))
    K.box(E, cab, (0, 1.25, 0), (w, 2.22, .5))
    pw = h - .25
    K.quad(E, 'vi-coffer-red', (-pw, .5, .26), (pw, .5, .26), (pw, 1.9, .26), (-pw, 1.9, .26))
    K.sweep_ring(E, 'vi-gilt-plain', [(-pw, .5), (pw, .5), (pw, 1.9), (-pw, 1.9)], K.P_GILT_FRAME, .25)
    for s in (-1, 1):
        K.box(E, 'vi-gilt-plain', (s * (h - .03), 1.25, .26), (.07, 2.2, .04))
        K.box(E, 'vi-casino-led', (s * (h - .13), 1.25, .26), (.025, 1.9, .02))
        K.lathe(E, 'vi-gilt-plain', s * (h - .15), 0, [(3.0, .06), (3.1, .09), (3.2, .05), (3.28, .001)], 8)
    K.sweep_facade(E, 'vi-gilt-plain', -h - .03, h + .03, 2.36, K.P_CORNICE_SMALL, .25)
    K.box(E, 'vi-gilt-plain', (0, 2.43, 0), (w + .12, .12, .6))
    sw = w - .2
    K.box(E, sign, (0, 2.74, 0), (sw, .5, .32))
    K.sweep_ring(E, 'vi-gilt-plain', [(-sw / 2, 2.49), (sw / 2, 2.49), (sw / 2, 2.99), (-sw / 2, 2.99)], [(-.03, 0), (-.03, .03), (.03, .03), (.03, 0)], .16)
    if name:
        K.box(E, 'vi-iron', (0, 2.74, .17), (sw - .1, .38, .01))
        K.text(E, name, 0, 2.66, .185, min(.2, (sw - .18) / max(1, len(name) * .62)), 'vi-sign-gold')


def slot_bank(B, cx, cz, yaw, n, style_i, name=None, double=True, solid=True):
    """n machines a side along the bank's local x, back to back (rows face +z and -z), centred at (cx, cz)."""
    F = Frame(B, cx, cz, yaw, y=Y0)
    style = SLOT_STYLES[style_i % len(SLOT_STYLES)]
    L = n * PITCH
    for side in ((1, -1) if double else (1,)):
        for i in range(n):
            x = -L / 2 + (i + .5) * PITCH
            slot_machine(K.rot_frame(F, x, side * .36 if double else .36, 0 if side == 1 else math.pi), style)
    zc = 0 if double else .36
    K.box(F, 'vi-iron', (0, 1.2, zc - (0 if double else .36)), (L, 2.3, .06))
    K.tube(F, 'vi-gilt-plain', (-L / 2, 2.33, zc - (0 if double else .36)), (L / 2, 2.33, zc - (0 if double else .36)), .03, 6)
    sign = 'vi-casino-sign-red' if style_i % 2 == 0 else 'vi-casino-topper-gold'
    for s in (-1, 1):
        E = K.rot_frame(F, s * (L / 2 + .26), 0 if double else .36, s * math.pi / 2)
        bank_cap(E, style[0], sign, name if s == 1 else None, 1.5 if double else .74)
    if solid:
        K.solid_box(F, (0, 1.2, 0 if double else .3), (L + 1.1, 2.4, 1.48 if double else .74))
    return 2 * n if double else n


def pack(field, along, pitch=8.0, gap=5.0, nmax=8, nmin=4, avoid=()):
    """Bank positions in a rectangle (bank footprints incl. stools must fit inside), long axes along 'x' or 'z'.
    Rows sit `pitch` apart; a row is split around anything in `avoid` [(x, z, r)]. Returns [(cx, cz, yaw, n)]."""
    x0, z0, x1, z1 = field
    a0, a1, b0, b1 = (x0, x1, z0, z1) if along == 'x' else (z0, z1, x0, x1)
    depth = 3.2; capL = 1.1
    rows = max(0, int((b1 - b0 - depth) // pitch) + 1)
    if rows == 0: return []
    span = (rows - 1) * pitch + depth
    out = []
    for r in range(rows):
        b = b0 + (b1 - b0 - span) / 2 + depth / 2 + r * pitch
        blocked = []
        for (px, pz, rad) in avoid:
            pa, pb = (px, pz) if along == 'x' else (pz, px)
            if abs(pb - b) < depth / 2 + rad + 1.4: blocked.append((pa - rad - 3.0, pa + rad + 3.0))
        free = [(a0, a1)]
        for lo, hi in blocked:
            nxt = []
            for fa, fb in free:
                if hi <= fa or lo >= fb: nxt.append((fa, fb)); continue
                if lo > fa: nxt.append((fa, lo))
                if hi < fb: nxt.append((hi, fb))
            free = nxt
        for fa, fb in free:
            L = fb - fa
            if L < nmin * PITCH + capL: continue
            k = max(1, int((L + gap) // (nmax * PITCH + capL + gap)))
            while k > 0:
                n = min(nmax, int(((L - (k - 1) * gap) / k - capL) / PITCH))
                if n >= nmin: break
                k -= 1
            if k == 0: continue
            bl = n * PITCH + capL
            gapk = (L - k * bl) / (k - 1) if k > 1 else 0
            start = fa + (bl / 2 if k > 1 else L / 2)
            for i in range(k):
                a = start + i * (bl + gapk) if k > 1 else start
                cx, cz = (a, b) if along == 'x' else (b, a)
                out.append((cx, cz, 0.0 if along == 'x' else -math.pi / 2, n))
    return out


def column_avoid():
    return [(x, z, .5) for x in XL for z in ZL if not (x == 301.5 and z == -747.0)]


def slots(B, G):
    B.source = 'slots'
    fields = [((292.0, -729.8, 305.5, -694.0), 'z'),      # NW, west of the salon walk
              ((311.5, -729.8, 329.2, -694.0), 'z'),      # NW, east of the salon walk
              ((318.5, -756.0, 329.2, -735.5), 'z'),      # beside the salon
              ((342.8, -746.0, 372.0, -727.2), 'x'),      # north of the escalator walk, west of the escalators
              ((356.0, -756.0, 386.0, -748.6), 'x'),      # along the north wall
              ((363.0, -719.5, 386.0, -694.0), 'z'),      # east of the bar
              ((292.0, -680.0, 301.0, -661.2), 'z'),      # SW corner
              ((342.5, -665.8, 386.0, -655.8), 'x'),      # along the south wall, east of the rotunda
              ((370.2, -680.0, 386.0, -668.5), 'z')]      # SE corner
    banks = []
    for f, along in fields: banks += pack(f, along, avoid=column_avoid())
    total = 0
    for i, (cx, cz, yaw, n) in enumerate(banks):
        total += slot_bank(B, cx, cz, yaw, n, i, SLOT_NAMES[i % len(SLOT_NAMES)])
    return banks, total


# ------------------------------------------------------------------ tables and pits
def chair(F, x, z, yaw, seat=.62, mat='vi-leather', ring=False):
    C = K.rot_frame(F, x, z, yaw)
    K.lathe(C, 'vi-bronze', 0, 0, [(0, .2), (.025, .2), (.05, .05), (.08, .035), (seat - .06, .032)], 8)
    K.lathe(C, mat, 0, 0, [(seat - .06, .2), (seat, .23), (seat + .05, .22), (seat + .07, .001)], 10)
    K.box(C, mat, (0, seat + .3, -.21), (.4, .34, .07))
    K.box(C, 'vi-gilt-plain', (0, seat + .48, -.21), (.42, .03, .08))
    K.tube(C, 'vi-bronze', (0, seat + .04, -.17), (0, seat + .13, -.2), .015, 4)
    if ring:
        K.path(C, 'vi-gilt-plain', [(.2 * math.cos(a), .3, .2 * math.sin(a)) for a in np.linspace(0, TAU, 9)], .012, 4)


def armchair(F, x, z, yaw, mat='vi-velvet-red'):
    C = K.rot_frame(F, x, z, yaw)
    K.box(C, 'vi-wood-dark', (0, .22, 0), (.6, .3, .56))
    K.box(C, mat, (0, .43, .02), (.56, .12, .52))
    K.box(C, mat, (0, .78, -.24), (.6, .6, .1))
    for s in (-1, 1):
        K.box(C, mat, (s * .27, .6, 0), (.08, .22, .5))
        K.box(C, 'vi-gilt-plain', (s * .27, .72, .02), (.1, .03, .52))
    for sx in (-.25, .25):
        for sz in (-.22, .22): K.box(C, 'vi-gilt-plain', (sx, .04, sz), (.05, .08, .05))


def blackjack(B, x, z, yaw, seats=6, felt='vi-felt'):
    """A half-moon table: the dealer's straight edge at the origin, the players toward local +z."""
    T = Frame(B, x, z, yaw, y=Y0)
    R = 1.05; n = 14
    arc = [(R * math.cos(a), R * math.sin(a)) for a in np.linspace(0, math.pi, n + 1)]
    K.box(T, 'vi-wood-dark', (0, .33, .38), (1.2, .66, .42))
    K.box(T, 'vi-marble-black', (0, .03, .38), (1.4, .06, .6))
    for (ax, az), (bx, bz) in zip(arc, arc[1:]):
        mx, mz = (ax + bx) / 2, (az + bz) / 2
        oface(T, 'vi-wood-dark', [(ax * .97, .6, az * .97), (bx * .97, .6, bz * .97), (bx * .97, .77, bz * .97), (ax * .97, .77, az * .97)], (mx, 0, mz))
    oface(T, 'vi-wood-dark', [(-R, .6, 0), (R, .6, 0), (R, .78, 0), (-R, .78, 0)], (0, 0, -1))
    oface(T, felt, [(0, .78, 0)] + [(px, .78, pz) for px, pz in arc], (0, 1, 0))
    oface(T, 'vi-wood-dark', [(0, .6, 0)] + [(px * .97, .6, pz * .97) for px, pz in arc], (0, -1, 0))
    pts = [np.array([px, .78, pz]) for px, pz in arc]
    ns = [np.array([px / R, 0, pz / R]) for px, pz in arc]
    K.sweep_frames(T, 'vi-leather', pts, ns, [np.array([0, 1., 0])] * len(pts),
                   [(-.1, 0), (-.1, .05), (-.06, .09), (.04, .1), (.1, .06), (.12, 0), (.1, -.06), (0, -.08)])
    K.sweep_frames(T, 'vi-gilt-plain', [np.array([px * .62, .782, pz * .62]) for px, pz in arc], ns,
                   [np.array([0, 1., 0])] * len(pts), [(-.012, 0), (-.012, .003), (.012, .003), (.012, 0)])
    for i in range(seats):
        a = math.pi * (i + .5) / seats
        K.disc(T, 'vi-sign-gold', .78 * math.cos(a), .783, .78 * math.sin(a), .075, 10)
        chair(T, 1.55 * math.cos(a), 1.55 * math.sin(a), face_yaw(-math.cos(a), -math.sin(a)))
    K.box(T, 'vi-iron', (0, .8, .17), (.66, .04, .18))
    for i, m in enumerate(['vi-flower-red', 'vi-plant', 'vi-iron', 'vi-umbrella-blue', 'vi-cloth-white', 'vi-casino-topper-gold']):
        K.box(T, m, (-.27 + i * .108, .84, .17), (.09, .05, .14))
    K.box(T, 'vi-wood-honey', (.55, .83, .16), (.12, .09, .24))
    K.tube(T, 'vi-chrome', (-.92, .78, .08), (-.92, 1.05, .08), .012, 4)
    K.box(T, 'vi-sign-white', (-.92, 1.12, .08), (.24, .14, .03))
    K.solid_box(T, (0, .45, .45), (2.2, .9, 1.05))


def roulette(B, x, z, yaw):
    """Wheel at local -x, layout toward +x, players on +z."""
    T = Frame(B, x, z, yaw, y=Y0)
    K.box(T, 'vi-wood-dark', (0, .37, -.05), (2.6, .62, .95))
    K.box(T, 'vi-marble-black', (0, .03, -.05), (2.7, .06, 1.05))
    K.box(T, 'vi-felt', (.15, .76, 0), (2.4, .04, 1.2))
    K.box(T, 'vi-wood-dark', (.15, .7, 0), (2.42, .08, 1.22))
    rail = [(-1.05, -.6), (-1.05, .6), (1.35, .6), (1.35, -.6)]
    ring_sweep(T, 'vi-leather', rail, [(0, 0), (.1, 0), (.12, .05), (.08, .09), (0, .1)], .78)
    reds = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}
    for c in range(12):
        for r in range(3):
            num = c * 3 + (3 - r)
            x0 = .02 + c * .105; z0 = -.12 + r * .15
            K.quad(T, 'vi-flower-red' if num in reds else 'vi-marble-black', (x0, .782, z0 + .13), (x0 + .093, .782, z0 + .13), (x0 + .093, .782, z0), (x0, .782, z0))
    K.quad(T, 'vi-plant', (-.12, .782, .31), (.0, .782, .31), (.0, .782, -.12), (-.12, .782, -.12))
    for i in range(6):
        x0 = .02 + i * .21
        K.quad(T, 'vi-cloth-white', (x0, .782, .5), (x0 + .19, .782, .5), (x0 + .19, .782, .35), (x0, .782, .35))
    wx = -.62
    K.lathe(T, 'vi-wood-dark', wx, 0, [(.74, .5), (.86, .5), (.89, .47), (.88, .4), (.85, .33)], 16)
    K.lathe(T, 'vi-wood-honey', wx, 0, [(.85, .33), (.84, .28)], 16)
    for i in range(37):
        a0, a1 = i * TAU / 37, (i + 1) * TAU / 37 - .01
        m = 'vi-plant' if i == 0 else ('vi-flower-red' if i % 2 else 'vi-marble-black')
        K.quad(T, m, (wx + .28 * math.cos(a0), .843, .28 * math.sin(a0)), (wx + .28 * math.cos(a1), .843, .28 * math.sin(a1)),
               (wx + .2 * math.cos(a1), .838, .2 * math.sin(a1)), (wx + .2 * math.cos(a0), .838, .2 * math.sin(a0)))
    K.lathe(T, 'vi-chrome', wx, 0, [(.838, .2), (.87, .09), (.9, .03), (.97, .02), (1.0, .001)], 10)
    for i in range(4):
        a = i * math.pi / 2
        K.tube(T, 'vi-chrome', (wx, .95, 0), (wx + .11 * math.cos(a), .95, .11 * math.sin(a)), .008, 4)
        K.sphere(T, 'vi-chrome', (wx + .12 * math.cos(a), .95, .12 * math.sin(a)), .015, 5, 3)
    for i, sx in enumerate([-.2, .35, .9, 1.45]):
        chair(T, sx, 1.05, math.pi)
    chair(T, 1.85, .2, face_yaw(-1, 0))
    K.solid_box(T, (.15, .45, 0), (2.7, .9, 1.3))


def oval_table(B, x, z, yaw, a, r, felt='vi-felt', top=.76, rail_h=.0, mat='vi-wood-dark'):
    T = Frame(B, x, z, yaw, y=Y0)
    out = stadium(a, r, 10)
    inner = [(px * (a + r - .12) / (a + r), pz * (r - .12) / r) for px, pz in out]
    for (ax, az), (bx, bz) in zip(out, out[1:] + out[:1]):
        mx, mz = (ax + bx) / 2, (az + bz) / 2
        oface(T, mat, [(ax, .08, az), (bx, .08, bz), (bx, top + rail_h, bz), (ax, top + rail_h, az)], (mx, 0, mz))
    fill(T, felt, Polygon(inner), top - .04 if rail_h else top)
    fill(T, 'vi-marble-black', Polygon(out), .08, up=False)
    ring_sweep(T, 'vi-leather', out, [(-.14, 0), (-.14, .06), (-.08, .11), (.04, .12), (.1, .07), (.11, 0), (.08, -.05), (0, -.06)], top + rail_h)
    if rail_h:
        for (ax, az), (bx, bz) in zip(inner, inner[1:] + inner[:1]):
            mx, mz = (ax + bx) / 2, (az + bz) / 2
            oface(T, 'vi-marble-black', [(ax, top - .04, az), (bx, top - .04, bz), (bx, top + rail_h, bz), (ax, top + rail_h, az)], (-mx, 0, -mz))
    K.box(T, 'vi-marble-black', (0, .04, 0), (a * 2, .08, r * 1.2))
    return T


def craps(B, x, z, yaw):
    T = oval_table(B, x, z, yaw, 1.25, .85, 'vi-felt', .72, .24)
    ring_sweep(T, 'vi-cloth-white', stadium(.95, .48, 10), [(-.02, 0), (-.02, .003), (.02, .003), (.02, 0)], .684)
    for s in (-1, 1):
        K.quad(T, 'vi-casino-felt-blue', (s * 1.0, .683, -.25), (s * 1.0, .683, .25), (s * 1.55, .683, .25), (s * 1.55, .683, -.25))
        K.box(T, 'vi-cloth-white', (s * .55, .684, 0), (.25, .004, .5))
    K.box(T, 'vi-iron', (0, .98, -.92), (.9, .05, .18))
    for i, m in enumerate(['vi-flower-red', 'vi-plant', 'vi-iron', 'vi-umbrella-blue', 'vi-cloth-white']):
        K.box(T, m, (-.32 + i * .16, 1.02, -.92), (.13, .04, .12))
    K.box(T, 'vi-flower-red', (.3, .7, .1), (.03, .03, .03)); K.box(T, 'vi-flower-red', (.36, .7, .14), (.03, .03, .03))
    K.tube(T, 'vi-wood-honey', (-.8, 1.0, .9), (.6, 1.0, .9), .012, 4)
    chair(T, 0, -1.45, 0.0, .75)
    K.solid_box(T, (0, .5, 0), (4.25, 1.0, 1.75))


def baccarat(B, x, z, yaw):
    T = oval_table(B, x, z, yaw, .9, .8, 'vi-felt', .76)
    for i in range(9):
        a = math.pi * (i + .5) / 9
        px, pz = 1.55 * math.cos(a) * 1.25, 1.35 * math.sin(a)
        armchair(T, px, pz, face_yaw(-px, -pz))
        K.disc(T, 'vi-sign-gold', .85 * math.cos(a) * 1.4, .763, .55 * math.sin(a), .07, 8)
    K.box(T, 'vi-iron', (0, .79, -.45), (.7, .04, .2))
    K.solid_box(T, (0, .45, 0), (3.5, .9, 1.7))


def podium(B, x, z, w=2.6):
    T = Frame(B, x, z, 0, y=Y0)
    K.box(T, 'vi-wood-dark', (0, .52, 0), (w, .96, .9))
    K.box(T, 'vi-marble-green', (0, 1.03, 0), (w + .12, .06, 1.02))
    K.box(T, 'vi-gilt-plain', (0, .1, 0), (w + .06, .08, .96))
    for s in (-1, 1):
        K.box(T, 'vi-window-dark', (s * .5, 1.3, s * .1), (.5, .32, .03))
        K.box(T, 'vi-iron', (s * .5, 1.12, s * .12), (.08, .14, .08))
    K.lathe(T, 'vi-gilt-plain', 0, 0, [(1.06, .09), (1.12, .03), (1.5, .02)], 8)
    K.lathe(T, 'vi-lantern', 0, 0, [(1.42, .16), (1.62, .1), (1.64, .001)], 10)
    K.solid_box(T, (0, .55, 0), (w, 1.1, .9))


def hanging_sign(B, x, z, yaw, text, w=4.2):
    T = Frame(B, x, z, yaw, y=Y0)
    for s in (-1, 1): K.tube(T, 'vi-gilt-plain', (s * (w / 2 - .3), 3.9, 0), (s * (w / 2 - .3), GIRDER_Y + .55, 0), .012, 4)
    K.box(T, 'vi-marble-green', (0, 3.62, 0), (w, .56, .12))
    for S in (T, K.rot_frame(T, 0, 0, math.pi)):
        K.sweep_ring(S, 'vi-gilt-plain', [(-w / 2, 3.34), (w / 2, 3.34), (w / 2, 3.9), (-w / 2, 3.9)], [(-.04, 0), (-.04, .03), (.04, .03), (.04, 0)], .06)
        K.text(S, text, 0, 3.52, .075, .26, 'vi-sign-gold')


def pits(B, G):
    B.source = 'tables'
    # blackjack pit (SW): two rows of six back to back around a podium
    for x in [306.0, 310.0, 314.0, 318.0, 322.0, 326.0]:
        blackjack(B, x, -672.3, 0.0, 6, 'vi-felt' if x != 326.0 else 'vi-casino-felt-blue')
        blackjack(B, x, -676.7, math.pi, 6, 'vi-felt' if x != 306.0 else 'vi-casino-felt-blue')
    podium(B, 316.0, -674.5, 3.2)
    hanging_sign(B, 309.0, -674.5, 0.0, 'BLACKJACK')
    hanging_sign(B, 323.0, -674.5, 0.0, 'BLACKJACK')
    # roulette and craps pit (SE)
    roulette(B, 346.4, -671.6, 0.0); craps(B, 353.6, -671.3, 0.0); roulette(B, 361.0, -671.6, 0.0)
    craps(B, 347.4, -677.7, math.pi); roulette(B, 354.6, -677.4, math.pi); craps(B, 362.0, -677.7, math.pi)
    podium(B, 354.6, -674.5, 2.0)
    hanging_sign(B, 348.5, -674.5, 0.0, 'ROULETTE')
    hanging_sign(B, 360.5, -674.5, 0.0, 'CRAPS')


# ------------------------------------------------------------------ cashier's cage
def cage(B, G):
    B.source = 'cage'
    C = Frame(B, 302.0, -656.5, math.pi, y=Y0)       # local +z faces the casino (north), x runs west
    W = 11.0; D = 3.9
    K.box(C, 'vi-marble-black', (0, .06, .3), (2 * W, .12, .6))
    K.box(C, 'vi-wood-dark', (0, .58, .28), (2 * W, .92, .56))
    K.box(C, 'vi-marble-green', (0, 1.08, .22), (2 * W + .2, .07, .8))
    K.sweep_facade(C, 'vi-gilt-plain', -W, W, 1.04, [(0, 0), (.04, 0), (.04, .03), (0, .04)], .62)
    for i in range(20):
        x0 = -W + .15 + i * (2 * W - .3) / 20; x1 = x0 + (2 * W - .3) / 20 - .15
        K.sweep_ring(C, 'vi-gilt-plain', [(x0, .25), (x1, .25), (x1, .88), (x0, .88)], [(-.02, 0), (-.02, .025), (.02, .025), (.02, 0)], .56)
    pitch = 2 * W / 9; holes = []
    for i in range(9):
        cx = -W + pitch * (i + .5)
        ring = K.opening('arch', cx, 1.16, 1.6, 1.62, 10); holes.append(ring)
        K.sweep_ring(C, 'vi-gilt-plain', ring, K.P_GILT_FRAME, .05)
        K.box(C, 'vi-gilt-plain', (cx, 2.86, .1), (.2, .24, .1))
        for gx in np.arange(cx - .72, cx + .74, .12):
            top = 1.16 + 1.62 - .8 + math.sqrt(max(0, .8 ** 2 - (gx - cx) ** 2)) - .02
            K.tube(C, 'vi-bronze', (gx, 1.42, 0), (gx, top, 0), .008, 4)
        for y in (1.42, 2.0): K.box(C, 'vi-bronze', (cx, y, 0), (1.56, .03, .03))
        K.box(C, 'vi-window-dark', (cx - .35, 1.32, -.7), (.42, .3, .04))
    K.wall(C, 'vi-marble-cream', [(-W, 1.11), (W, 1.11), (W, 3.2), (-W, 3.2)], holes, .05, .1, 'vi-gilt-plain')
    K.wall(C, 'vi-stucco-cream', [(-W, 3.2), (W, 3.2), (W, 4.4), (-W, 4.4)], [], .05)
    for i in range(10):
        x = -W + pitch * i
        K.box(C, 'vi-marble-cream', (x, 2.15, .13), (.34, 2.1, .16))
        K.box(C, 'vi-gilt-plain', (x, 3.12, .15), (.42, .16, .2))
    K.box(C, 'vi-marble-green', (0, 3.75, .1), (6.0, .7, .06))
    K.sweep_ring(C, 'vi-gilt-plain', [(-3, 3.4), (3, 3.4), (3, 4.1), (-3, 4.1)], K.P_GILT_FRAME, .13)
    K.text(C, 'CASHIER', 0, 3.56, .16, .44, 'vi-sign-gold')
    for s in (-1, 1):
        for k in range(3):
            px = s * (4.6 + k * 2.2)
            K.quad(C, 'vi-coffer-red' if k % 2 == 0 else 'vi-coffer-green', (px - .75, 3.45, .08), (px + .75, 3.45, .08), (px + .75, 4.1, .08), (px - .75, 4.1, .08))
            K.sweep_ring(C, 'vi-gilt-plain', [(px - .75, 3.45), (px + .75, 3.45), (px + .75, 4.1), (px - .75, 4.1)], K.P_GILT_FRAME, .08)
    K.box(C, 'vi-limestone', (0, 4.45, -D / 2 + .1), (2 * W + .2, .1, D + .2))
    K.entablature(C, -W - .1, W + .1, 4.4, 'vi-limestone', 'vi-gilt', 'vi-gilt-plain', z=.06, scale=.5)
    for s in (-1, 1):
        S = K.rot_frame(C, s * W, -D / 2, s * math.pi / 2)
        oface(S, 'vi-marble-cream', [(-D / 2, 0, 0), (D / 2, 0, 0), (D / 2, 4.4, 0), (-D / 2, 4.4, 0)], (0, 0, 1))
    K.box(C, 'vi-wood-honey', (0, .45, -.9), (2 * W - .4, .9, .6))
    K.box(C, 'vi-stucco-cream', (0, 3.0, -1.4), (2 * W - .2, .04, 2.5))
    for x in np.linspace(-W + 1, W - 1, 6):           # queue posts and velvet ropes
        K.lathe(C, 'vi-gilt-plain', x, 2.6, [(0, .14), (.04, .14), (.06, .03), (.92, .03), (.96, .05), (1.0, .001)], 8)
    xs = np.linspace(-W + 1, W - 1, 6)
    for a, b in zip(xs, xs[1:]):
        K.path(C, 'vi-velvet-red', [(a + (b - a) * t, .86 - .22 * math.sin(math.pi * t), 2.6) for t in np.linspace(0, 1, 7)], .02, 5)
    K.solid_box(C, (0, 2.2, -D / 2 + .3), (2 * W, 4.4, D + .6))
    G.light(302.0, 3.4, -654.2, 0xffe6c4, 200, 12)


# ------------------------------------------------------------------ the round bar
def round_bar(B, G):
    B.source = 'bar'
    T = Frame(B, BAR[0], BAR[1], 0, y=Y0); n = 36
    K.lathe(T, 'vi-marble-black', 0, 0, [(0, 4.72), (.13, 4.72)], n)
    K.lathe(T, 'vi-wood-dark', 0, 0, [(.13, 4.74), (.9, 4.8), (1.0, 4.84)], n)
    K.lathe(T, 'vi-marble-green', 0, 0, [(1.02, 4.98), (1.07, 5.04), (1.12, 4.98), (1.12, 3.92), (1.02, 3.92)], n)
    K.lathe(T, 'vi-casino-steel', 0, 0, [(0, 3.9), (1.02, 3.9)], n)
    K.lathe(T, 'vi-casino-led', 0, 0, [(.98, 4.86), (1.0, 4.86)], n)
    for i in range(n):
        a = i * TAU / n
        S = K.rot_frame(T, 4.8 * math.cos(a), 4.8 * math.sin(a), face_yaw(math.cos(a), math.sin(a)))
        K.box(S, 'vi-gilt-plain', (0, .55, .02), (.07, .8, .04))
        if i % 3 == 0: K.tube(T, 'vi-gilt-plain', (4.85 * math.cos(a), .24, 4.85 * math.sin(a)), (5.07 * math.cos(a), .24, 5.07 * math.sin(a)), .015, 4)
    K.path(T, 'vi-gilt-plain', [(5.07 * math.cos(a), .24, 5.07 * math.sin(a)) for a in np.linspace(0, TAU, 37)], .03, 6)
    # the back bar: a drum of lit shelves with bottles round the column
    K.lathe(T, 'vi-wood-dark', 0, 0, [(0, 2.3), (1.0, 2.3), (1.04, 2.36), (1.06, 2.2)], 24)
    K.lathe(T, 'vi-marble-green', 0, 0, [(1.0, 2.36), (1.06, 2.36), (1.06, 1.95)], 24)
    k = 12; rng = np.random.default_rng(7)
    for i in range(k):
        a0, a1 = i * TAU / k + .02, (i + 1) * TAU / k - .02
        p0 = (1.95 * math.cos(a0), 1.95 * math.sin(a0)); p1 = (1.95 * math.cos(a1), 1.95 * math.sin(a1))
        am = (a0 + a1) / 2
        oface(T, 'vi-shop-display', [(p0[0], 1.1, p0[1]), (p1[0], 1.1, p1[1]), (p1[0], 2.75, p1[1]), (p0[0], 2.75, p0[1])], (math.cos(am), 0, math.sin(am)))
        K.box(K.rot_frame(T, 1.98 * math.cos(a0 - .02), 1.98 * math.sin(a0 - .02), face_yaw(math.cos(a0), math.sin(a0))), 'vi-gilt-plain', (0, 1.95, 0), (.07, 1.75, .06))
        for sh in (1.1, 1.62, 2.14):
            for b in range(5):
                a = a0 + (a1 - a0) * (b + .5) / 5; r = 2.07
                m = ['vi-lantern-amber', 'vi-plant', 'vi-crystal', 'vi-bronze', 'vi-flower-red'][int(rng.integers(0, 5))]
                hb = .26 + .08 * rng.random()
                K.lathe(T, m, r * math.cos(a), r * math.sin(a), [(sh, .035), (sh + hb * .62, .038), (sh + hb * .78, .016), (sh + hb, .012)], 6)
    for sh in (1.1, 1.62, 2.14, 2.66):
        K.lathe(T, 'vi-gilt-plain', 0, 0, [(sh - .025, 2.15), (sh, 2.15), (sh, 1.94)], 24)
    K.lathe(T, 'vi-gilt-plain', 0, 0, [(2.75, 2.25), (2.82, 2.32), (2.95, 2.32), (3.05, 2.2), (3.1, .45)], 24)
    # the halo over the counter: a gilt ring hung from the ceiling, lit underneath, with pendant lamps
    K.lathe(T, 'vi-gilt', 0, 0, [(3.4, 5.36), (3.45, 5.3), (3.85, 5.3), (3.9, 5.38), (3.95, 5.3)], n)          # outer fascia
    K.lathe(T, 'vi-gilt', 0, 0, [(3.95, 3.7), (3.85, 3.7), (3.45, 3.7), (3.4, 3.64)], n)                      # inner fascia
    K.lathe(T, 'vi-stucco-cream', 0, 0, [(3.45, 5.3), (3.45, 3.7)], n)                                        # soffit
    K.lathe(T, 'vi-gilt-plain', 0, 0, [(3.4, 5.36), (3.4, 5.1), (3.43, 5.1)], n)
    K.lathe(T, 'vi-casino-led', 0, 0, [(3.44, 4.0), (3.44, 3.85)], n)
    for i in range(6):
        a = i * TAU / 6 + .2
        K.tube(T, 'vi-gilt-plain', (5.0 * math.cos(a), 3.95, 5.0 * math.sin(a)), (5.0 * math.cos(a), COFFER_Y, 5.0 * math.sin(a)), .015, 4)
    for i in range(12):
        a = i * TAU / 12
        px, pz = 4.45 * math.cos(a), 4.45 * math.sin(a)
        K.tube(T, 'vi-iron', (px, 3.45, pz), (px, 2.75, pz), .005, 3)
        K.lathe(T, 'vi-lantern-amber', px, pz, [(2.55, .001), (2.6, .09), (2.72, .11), (2.76, .03), (2.78, .001)], 8)
    for i in range(28):
        a = (i + .5) * TAU / 28
        chair(T, 5.55 * math.cos(a), 5.55 * math.sin(a), face_yaw(-math.cos(a), -math.sin(a)), .78, 'vi-leather', True)
    for i in range(8):
        a0, a1 = i * TAU / 8, (i + 1) * TAU / 8
        R = 5.05 / math.cos(math.pi / 8)
        K.solid_quad(T, (R * math.cos(a0), 0, R * math.sin(a0)), (R * math.cos(a1), 0, R * math.sin(a1)),
                     (R * math.cos(a1), 1.12, R * math.sin(a1)), (R * math.cos(a0), 1.12, R * math.sin(a0)))
    K.solid_box(T, (0, .56, 0), (6.5, 1.12, 6.5))
    G.light(BAR[0] + 2, 3.2, BAR[1], 0xffc98a, 200, 12)


# ------------------------------------------------------------------ high-limit salon
def drape(F, x0, x1, z, y0, y1, side, folds=5, tie=1.15):
    """A gathered velvet curtain between x0..x1 at depth z (folds toward `side`), tied back at `tie` to the x1 side."""
    rows = [y0 + (y1 - y0) * t for t in np.linspace(0, 1, 7)]
    cols = 10
    def P(u, y):
        squeeze = 1 - .55 * math.exp(-((y - tie) / .5) ** 2)
        x = x1 - (x1 - x0) * u * squeeze
        return (x, y, z + side * (.05 + .05 * math.sin(u * folds * TAU)))
    for (ya, yb) in zip(rows, rows[1:]):
        for i in range(cols):
            ua, ub = i / cols, (i + 1) / cols
            oface(F, 'vi-velvet-red', [P(ua, ya), P(ub, ya), P(ub, yb), P(ua, yb)], (0, 0, side))
    K.tube(F, 'vi-gilt-plain', (x1 - .05, tie, z + side * .08), (x1 - (x1 - x0) * .45, tie, z + side * .12), .02, 5)


def glass_wall(B, a, b, inside, door=None, stops=()):
    """The salon's two-sided wall on a->b: marble dado, glass in bronze bars, a gilt transom, a frieze up to the girder;
    velvet drapes on the `inside` (+1/-1 local z)."""
    F, L = seg_frame(B, a, b)
    stops = tuple(min(L, t) for t in stops)
    cuts = sorted(set([0.0, L] + list(stops)))
    bays = []
    for s0, s1 in zip(cuts, cuts[1:]):
        if s1 - s0 < .5: continue
        m = max(1, round((s1 - s0) / 4.4))
        bays += [(s0 + (s1 - s0) * i / m, s0 + (s1 - s0) * (i + 1) / m) for i in range(m)]
    for s0, s1 in bays:
        e0 = s0 + (.42 if s0 in stops else .2); e1 = s1 - (.42 if s1 in stops else .2)
        if door and e0 < door[1] and e1 > door[0]:
            parts_ = [(e0, door[0]), (door[1], e1)]
        else:
            parts_ = [(e0, e1)]
        for p0, p1 in parts_:
            if p1 - p0 < .2: continue
            K.box(F, 'vi-marble-rust', ((p0 + p1) / 2, .45, 0), (p1 - p0, .9, .3))
            for s in (-1, 1): K.box(F, 'vi-gilt-plain', ((p0 + p1) / 2, .91, s * .155), (p1 - p0, .04, .02))
            K.quad(F, 'vi-shop-glass', (p0, .9, 0), (p1, .9, 0), (p1, 3.3, 0), (p0, 3.3, 0))
            k = max(1, round((p1 - p0) / 1.2))
            for i in range(1, k): K.box(F, 'vi-bronze', (p0 + (p1 - p0) * i / k, 2.1, 0), (.04, 2.4, .05))
            K.box(F, 'vi-bronze', ((p0 + p1) / 2, 2.25, 0), (p1 - p0, .04, .05))
            for x in (p0, p1): K.box(F, 'vi-bronze', (x, 2.1, 0), (.06, 2.4, .07))
            K.solid_box(F, ((p0 + p1) / 2, 1.7, 0), (p1 - p0, 3.4, .3))
            if p1 - p0 > 1.6:
                drape(F, p0 + .05, p0 + .05 + min(.9, (p1 - p0) * .3), inside * .3, .05, 3.3, inside)
                Fr = K.rot_frame(F, p1 - .05, 0, math.pi)
                drape(Fr, 0, min(.9, (p1 - p0) * .3), -inside * .3, .05, 3.3, -inside)
                pts = [((p0 + (p1 - p0) * t), 3.3 - .35 * math.sin(math.pi * t), inside * .34) for t in np.linspace(0, 1, 9)]
                for (xa, ya, za), (xb, yb, zb) in zip(pts, pts[1:]):
                    oface(F, 'vi-velvet-red', [(xa, ya, za), (xb, yb, zb), (xb, 3.45, zb), (xa, 3.45, za)], (0, 0, inside))
        lo, hi = s0 + (.42 if s0 in stops else 0), s1 - (.42 if s1 in stops else 0)
        K.box(F, 'vi-gilt', ((lo + hi) / 2, 3.42, 0), (hi - lo, .24, .32))
        K.box(F, 'vi-stucco-cream', ((lo + hi) / 2, (3.54 + GIRDER_Y) / 2, 0), (hi - lo, GIRDER_Y - 3.54, .3))
        for s in (-1, 1):
            if hi - lo > 1.2:
                ring = [(lo + .35, 3.75), (hi - .35, 3.75), (hi - .35, 4.5), (lo + .35, 4.5)]
                S = F if s > 0 else K.rot_frame(F, L, 0, math.pi)
                rr = ring if s > 0 else [(L - x, y) for x, y in ring]
                oface(S, 'vi-coffer-red', [(x, y, .162) for x, y in rr], (0, 0, 1))
                K.sweep_ring(S, 'vi-gilt-plain', rr, K.P_GILT_FRAME, .162)
        if s0 not in stops and s0 > 0:
            K.box(F, 'vi-marble-cream', (s0, 2.3, 0), (.4, 4.6, .42))
            K.box(F, 'vi-gilt-plain', (s0, 3.4, 0), (.5, .3, .5))
    for x in (0.0, L):
        if x not in stops: K.box(F, 'vi-marble-cream', (x + (.2 if x == 0 else -.2), GIRDER_Y / 2, 0), (.4, GIRDER_Y, .42))
    return F, L


def salon(B, G):
    B.source = 'salon'
    sx0, sz0, sx1, sz1 = SALON
    # south wall (outside = casino = local +z), door on the salon walk
    F, L = glass_wall(B, (sx0, sz1), (sx1, sz1), -1, door=(306.5 - sx0, 310.5 - sx0), stops=(301.5 - sx0, sx1 - sx0))
    d0, d1 = 306.5 - sx0, 310.5 - sx0
    for S, flip in ((F, False), (K.rot_frame(F, L, 0, math.pi), True)):
        a, b = (L - d1, L - d0) if flip else (d0, d1)
        ring = [(a, 0), (b, 0), (b, 3.3), (a, 3.3)]
        K.sweep_ring(S, 'vi-gilt-plain', ring, K.P_SURROUND, .15)
        for x in (a - .45, b + .45):
            pilaster(S, x, .15, .5)
        K.box(S, 'vi-marble-green', ((a + b) / 2, 3.9, .17), (3.6, .5, .04))
        K.text(S, 'HIGH LIMIT SALON' if not flip else 'SALON PRIVE', (a + b) / 2, 3.8, .2, .26, 'vi-sign-gold')
    # east wall (inside = west = local +z for a run going south)
    glass_wall(B, (sx1, sz0), (sx1, sz1), 1, stops=(-747.0 - sz0, sz1 - sz0))
    # inside: baccarat, blackjack, high-limit slots on the west wall, a lounge by the door
    baccarat(B, 295.5, -741.5, math.pi); baccarat(B, 309.0, -741.5, math.pi)
    blackjack(B, 295.5, -753.0, 0.0, 5); blackjack(B, 309.0, -753.0, 0.0, 5)
    hanging_sign(B, 302.25, -741.5, 0.0, 'BACCARAT', 3.6)
    slot_bank(B, sx0 + .22, -742.5, math.pi / 2, 9, 1, None, double=False)
    slot_bank(B, sx0 + .22, -751.7, math.pi / 2, 9, 4, None, double=False)
    armchair(G, 312.3, -737.6, face_yaw(1, 0)); armchair(G, 314.5, -737.6, face_yaw(-1, 0))
    K.lathe(G, 'vi-gilt-plain', 313.4, -737.6, [(0, .2), (.05, .2), (.08, .05), (.5, .05), (.52, .3), (.56, .3)], 12)
    K.planter(G, 304.6, -735.0, 0, .38, .55); K.planter(G, 312.4, -731.6, 0, .38, .55); K.planter(G, 304.6, -731.6, 0, .38, .55)


# ------------------------------------------------------------------ the escalators to St Mark's Square
T30 = math.tan(math.radians(30))
ESC_FLAT, ESC_EASE, ESC_RISE, ESC_END = 1.2, .9, PLAN.L2 - PLAN.L1, 16.5
ESC_RUN = ESC_RISE / T30 + ESC_EASE


def esc_y(d):
    s = d - ESC_FLAT
    if s <= 0: return 0.0
    if s >= ESC_RUN: return ESC_RISE
    if s < ESC_EASE: return T30 * s * s / (2 * ESC_EASE)
    if s > ESC_RUN - ESC_EASE: u = ESC_RUN - s; return ESC_RISE - T30 * u * u / (2 * ESC_EASE)
    return T30 * ESC_EASE / 2 + T30 * (s - ESC_EASE)


def esc_strip(E, mat, xa, xb, da, db, ya, yb, hint, step=.3, solid=False):
    """Quads between two lines that follow the profile: from x=xa (height esc_y+ya) to x=xb (esc_y+yb), d da..db."""
    ds = list(np.arange(da, db, step)) + [db]
    for d0, d1 in zip(ds, ds[1:]):
        oface(E, mat, [(xa, esc_y(d0) + ya, d0), (xa, esc_y(d1) + ya, d1), (xb, esc_y(d1) + yb, d1), (xb, esc_y(d0) + yb, d0)], hint, solid)


def esc_side(E, mat, x, da, db, ylo, yhi, hint, step=.3, solid=False, floor=False):
    ds = list(np.arange(da, db, step)) + [db]
    for d0, d1 in zip(ds, ds[1:]):
        lo0, lo1 = (0.0, 0.0) if floor else (max(0.0, esc_y(d0) + ylo), max(0.0, esc_y(d1) + ylo))
        oface(E, mat, [(x, lo0, d0), (x, lo1, d1), (x, esc_y(d1) + yhi, d1), (x, esc_y(d0) + yhi, d0)], hint, solid)


def handrail(E, x, d0, d1, h=.95, low=.3):
    rc = (h - low) / 2; pts = []
    for t in np.linspace(1.5 * math.pi, .5 * math.pi, 9):        # bottom loop: from the return, round the back, to the top
        pts.append((d0 + rc * math.cos(t), esc_y(d0) + low + rc + rc * math.sin(t)))
    for d in np.arange(d0 + .3, d1, .3): pts.append((d, esc_y(d) + h))
    for t in np.linspace(.5 * math.pi, -.5 * math.pi, 9):
        pts.append((d1 + rc * math.cos(t), esc_y(d1) + low + rc + rc * math.sin(t)))
    P = [np.array([x, y, d]) for d, y in pts]
    ns, bs = [], []
    for i in range(len(P)):
        a, b = P[max(0, i - 1)], P[min(len(P) - 1, i + 1)]
        t = b - a; t /= np.linalg.norm(t)
        bs.append(np.array([0, t[2], -t[1]]))
        ns.append(np.array([1., 0, 0]))
    K.sweep_frames(E, 'vi-casino-rubber', P, ns, bs, [(-.045, -.02), (.045, -.02), (.05, 0), (.045, .03), (0, .042), (-.045, .03), (-.05, 0), (-.045, -.02)])


def escalators(B, G):
    B.source = 'escalator'
    E = Frame(B, ESC_X, ESC_Z, math.pi, y=Y0)      # local +z (d) runs north up the slope; local +x is west
    for ux in (-2.0, 2.0):
        # steps: noses on the profile, treads level, cleated risers, yellow demarcation
        for i in range(39):
            d = i * .4; h = esc_y(d) + .015; hn = esc_y(d + .4) + .015
            K.box(E, 'vi-casino-tread', (ux, h - .02, d + .2), (.98, .04, .385))
            K.box(E, 'vi-casino-yellow', (ux, h + .003, d + .03), (.98, .008, .05))
            for s in (-1, 1): K.box(E, 'vi-casino-yellow', (ux + s * .47, h + .003, d + .2), (.04, .008, .38))
            if hn - h > .005: oface(E, 'vi-casino-steel', [(ux - .49, h, d + .4), (ux + .49, h, d + .4), (ux + .49, hn, d + .4), (ux - .49, hn, d + .4)], (0, 0, -1))
        esc_strip(E, 'vi-iron', ux - .52, ux + .52, 1.7, 15.7, -.3, -.3, (0, 1, 0))
        for d0, d1, y in ((-.9, .02, 0.0), (15.58, ESC_END, ESC_RISE)):
            K.box(E, 'vi-casino-tread', (ux, y + .007, (d0 + d1) / 2), (1.2, .016, d1 - d0))
            K.box(E, 'vi-casino-yellow', (ux, y + .012, d1 - .03 if y else d1 - .05), (1.0, .012, .05))
        for s in (-1, 1):
            xs = ux + s * .52
            esc_side(E, 'vi-casino-steel', xs, -.9, ESC_END, -.06, .22, (-s, 0, 0))
            esc_strip(E, 'vi-casino-steel', xs, ux + s * .7, -.9, ESC_END, .22, .3, (0, 1, 0))
            esc_side(E, 'vi-shop-glass', ux + s * .7, -.4, 16.1, .3, .92, (s, 0, 0))
            esc_side(E, 'vi-casino-steel', ux + s * .7, -.4, 16.1, .9, .93, (s, 0, 0))
            handrail(E, ux + s * .7, -.4, 16.1)
            esc_strip(E, 'vi-marble-cream', ux + s * .7, ux + s * 1.0, -.9, ESC_END, .3, .26, (0, 1, 0))
            # collision: the balustrade
            ds = list(np.arange(-.9, ESC_END, .5)) + [ESC_END]
            for d0, d1 in zip(ds, ds[1:]):
                K.solid_quad(E, (ux + s * .7, esc_y(d0), d0), (ux + s * .7, esc_y(d1), d1), (ux + s * .7, esc_y(d1) + 1.05, d1), (ux + s * .7, esc_y(d0) + 1.05, d0))
        # the walkable ramp (collision)
        ds = list(np.arange(-.9, ESC_END, .3)) + [ESC_END]
        for d0, d1 in zip(ds, ds[1:]):
            K.solid_quad(E, (ux - .55, esc_y(d0), d0), (ux + .55, esc_y(d0), d0), (ux + .55, esc_y(d1), d1), (ux - .55, esc_y(d1), d1))
    # the central deck and the outer cladding (stucco, gilt mouldings, marble plinth) round a closed truss
    esc_strip(E, 'vi-marble-cream', -1.0, 1.0, -.9, ESC_END, .26, .26, (0, 1, 0))
    for d in np.arange(.8, 14.0, 1.8):
        esc_strip(E, 'vi-coffer-green', -.5, .5, d + .16, d + 1.64, .27, .27, (0, 1, 0), step=.37)
    for d in np.arange(.8, 15.6, 1.8):
        K.lathe(E, 'vi-gilt-plain', 0, d, [(esc_y(d) + .265, .07), (esc_y(d) + .31, .05), (esc_y(d) + .34, .001)], 8)
    ds = np.arange(-.9, ESC_END + .01, .3)
    for x in (-.6, .6, -1.0, 1.0, -3.0, 3.0):
        pts = [np.array([x, esc_y(d) + .26, d]) for d in ds]
        K.sweep_frames(E, 'vi-gilt-plain', pts, [np.array([1., 0, 0])] * len(pts), [np.array([0, 1., 0])] * len(pts), [(-.025, 0), (-.025, .02), (.025, .02), (.025, 0)])
    for s in (-1, 1):
        x = s * 3.93
        esc_strip(E, 'vi-marble-cream', s * 3.0, x, -.9, ESC_END, .26, .26, (0, 1, 0))
        esc_side(E, 'vi-stucco-cream', x, -.9, ESC_END, 0, .26, (s, 0, 0), floor=True)
        esc_side(E, 'vi-casino-steel', s * 1.0, -.9, ESC_END, -.3, .26, (s, 0, 0))
        esc_side(E, 'vi-casino-steel', s * 3.0, -.9, ESC_END, -.3, .26, (-s, 0, 0))
        S = E if s > 0 else K.rot_frame(E, 0, ESC_END, math.pi)
        # mouldings along the slope on the outer face
        for off, prof in ((.1, [(0, 0), (.06, 0), (.06, .04), (.03, .08), (0, .1)]), (-.75, [(0, 0), (.04, 0), (.04, .06), (0, .06)])):
            d0 = -.9 if off > 0 else next(d for d in np.arange(0, ESC_END, .05) if esc_y(d) + off >= .56)
            ds = np.arange(d0, ESC_END + .01, .3)
            pts = [np.array([x, esc_y(d) + off, d]) for d in ds]
            K.sweep_frames(E, 'vi-gilt-plain', pts, [np.array([s * 1., 0, 0])] * len(pts), [np.array([0, 1., 0])] * len(pts), prof)
        K.box(E, 'vi-marble-rust', (x + s * .03, .25, (ESC_END - .9) / 2), (.06, .5, ESC_END + .9))
        for d in np.arange(.6, ESC_END - .3, 2.2):
            top = esc_y(d) - .9
            if top > 1.0: K.box(E, 'vi-gilt-plain', (x + s * .025, (.55 + top) / 2, d), (.05, top - .55, .07))
        for d in np.arange(-.9, ESC_END, .5):
            d1 = min(ESC_END, d + .5)
            K.solid_quad(E, (x, 0, d), (x, 0, d1), (x, esc_y(d1) + 1.05, d1), (x, esc_y(d) + 1.05, d))
    # the north end under the top landing, and the newels' end panels at the bottom
    oface(E, 'vi-stucco-cream', [(-3.93, 0, ESC_END), (3.93, 0, ESC_END), (3.93, TOP, ESC_END), (-3.93, TOP, ESC_END)], (0, 0, 1))
    K.box(E, 'vi-marble-rust', (0, .5, ESC_END + .03), (7.86, 1.0, .06))
    K.quad(E, 'vi-casino-mirror', (2.6, 1.3, ESC_END + .02), (-2.6, 1.3, ESC_END + .02), (-2.6, 3.8, ESC_END + .02), (2.6, 3.8, ESC_END + .02))
    K.sweep_ring(K.rot_frame(E, 0, ESC_END, math.pi), 'vi-gilt-plain', [(-2.6, 1.3), (2.6, 1.3), (2.6, 3.8), (-2.6, 3.8)], K.P_GILT_FRAME, -.02)
    K.solid_quad(E, (-4, 0, ESC_END), (4, 0, ESC_END), (4, TOP, ESC_END), (-4, TOP, ESC_END))
    for x0, x1 in ((-3.93, -2.7), (-1.3, 1.3), (2.7, 3.93)):
        oface(E, 'vi-marble-rust', [(x0, 0, -.9), (x1, 0, -.9), (x1, .26, -.9), (x0, .26, -.9)], (0, 0, -1))
    oface(E, 'vi-casino-steel', [(-3.93, ESC_RISE + .26, ESC_END), (3.93, ESC_RISE + .26, ESC_END), (3.93, ESC_RISE, ESC_END), (-3.93, ESC_RISE, ESC_END)], (0, 0, 1))
    K.solid_quad(E, (-4, ESC_RISE, 15.0), (4, ESC_RISE, 15.0), (4, ESC_RISE, ESC_END), (-4, ESC_RISE, ESC_END))
    # lights over the bottom and along the well
    G.light(ESC_X, 4.6, ESC_Z + 3.5, WARM, 220, 16)


# ------------------------------------------------------------------ Restaurant Row
REST_W = ['TRATTORIA', 'OSTERIA', 'CAFFE', 'GELATERIA']
REST_E = ['STEAKHOUSE', 'ENOTECA', 'PIZZERIA', 'PASTICCERIA']


def blade_sign(F, x, y, mat='vi-casino-sign-red'):
    """A hanging oval sign on an iron bracket, perpendicular to the facade (both faces painted gold)."""
    K.path(F, 'vi-iron', [(x, y + .55, .02), (x, y + .5, .5), (x, y + .48, 1.05)], .02, 5)
    K.path(F, 'vi-iron', [(x, y + .1, .02), (x, y + .42, .55), (x, y + .5, .95)], .015, 4)
    for zz in (.35, .95): K.tube(F, 'vi-iron', (x, y + .49, zz), (x, y + .36, zz), .006, 3)
    ring = [(.65 + .32 * math.cos(a), y + .02 + .34 * math.sin(a)) for a in np.linspace(0, TAU, 16, endpoint=False)]
    prism(F, mat, ring, 'x', x - .025, x + .025)
    inner = [(.65 + .25 * math.cos(a), y + .02 + .27 * math.sin(a)) for a in np.linspace(0, TAU, 16, endpoint=False)]
    for sx in (-1, 1): oface(F, 'vi-sign-gold', [(x + sx * .028, v, u) for u, v in inner], (sx, 0, 0))


def restaurant(F, x0, x1, name, seed, H=5.65):
    """A restaurant front on facade frame F from x0 to x1 (street at +z): a glazed arched or square main opening with
    doors, two windows with flower boxes, a rusticated base, oculi or relief panels, an entablature carrying the name,
    lanterns or an awning, a blade sign, planters and a menu easel."""
    w = x1 - x0; c = (x0 + x1) / 2
    colour = ['vi-stucco-ochre', 'vi-stucco-rose', 'vi-stucco-cream', 'vi-stucco-terracotta', 'vi-stucco-sage', 'vi-stucco-yellow', 'vi-stucco-pink'][seed % 7]
    trim = 'vi-limestone'
    style = seed % 3
    ow = min(4.0, w - 5.0)
    main = K.opening('rect', c, 0, ow, 3.2) if style == 1 else K.opening('arch', c, 0, ow, 3.75, 14)
    holes = [main]; side = []; oculi = []
    wh = 2.35 if style == 1 else 2.5
    for s_ in (-1, 1):
        sx = c + s_ * (ow / 2 + (w / 2 - ow / 2) / 2)
        r = K.opening('rect' if style == 1 else 'arch', sx, .9, 1.25, wh, 10)
        side.append((sx, r)); holes.append(r)
        if style == 0:
            o = K.opening('round', sx, 3.62, .62, .62, 10); oculi.append((sx, o)); holes.append(o)
    K.wall(F, colour, [(x0, .9), (x1, .9), (x1, H), (x0, H)], [h for h in holes if h is not main] + [main], 0, 1.2, trim)
    # the rusticated base (the wall above starts at 0.9; the main opening cuts through it)
    for a, b in ((x0, c - ow / 2), (c + ow / 2, x1)):
        K.wall(F, 'vi-rustication', [(a, 0), (b, 0), (b, .9), (a, .9)], [], .0)
        K.sweep_facade(F, trim, a, b, .86, [(0, 0), (.08, 0), (.08, .04), (.05, .08), (0, .1)])
        K.sweep_facade(F, 'vi-marble-black', a, b, 0, [(0, 0), (.06, 0), (.06, .12), (0, .15)])
    disp = ['vi-shop-sweets', 'vi-shop-display', 'vi-window-lit', 'vi-shop-display'][seed % 4]
    K.pane(F, disp, main, -1.19)
    for k, (sx, r) in enumerate(side):
        K.pane(F, 'vi-window-lit' if disp != 'vi-window-lit' else 'vi-shop-display', r, -1.19)
        K.pane(F, 'vi-shop-glass', r, -.25)
        K.box(F, 'vi-wood-dark', (sx, .9 + wh / 2 - (.3 if style != 1 else 0), -.24), (.05, wh - (.6 if style != 1 else 0), .04))
        K.box(F, 'vi-wood-dark', (sx, .9 + wh * .62, -.24), (1.25, .05, .04))
        K.sweep_ring(F, trim, r, K.P_SURROUND, 0)
        K.box(F, trim, (sx, .86, .08), (1.6, .1, .2))
        K.box(F, 'vi-soil', (sx, .97, .16), (1.3, .14, .22))
        for i, fx in enumerate(np.linspace(sx - .55, sx + .55, 6)):
            K.sphere(F, ['vi-flower-red', 'vi-plant', 'vi-flower-pink'][i % 3], (fx, 1.1, .18), .11, 6, 4)
        if style == 1:
            K.sweep_facade(F, trim, sx - .85, sx + .85, .9 + wh + .2, K.P_CORNICE_SMALL)
        elif style == 2:
            K.quad(F, 'vi-coffer-red' if k == 0 else 'vi-coffer-green', (sx - .55, 3.65, .03), (sx + .55, 3.65, .03), (sx + .55, 4.25, .03), (sx - .55, 4.25, .03))
            K.sweep_ring(F, 'vi-gilt-plain', [(sx - .55, 3.65), (sx + .55, 3.65), (sx + .55, 4.25), (sx - .55, 4.25)], K.P_GILT_FRAME, .03)
    for sx, o in oculi:
        K.pane(F, 'vi-window-lit', o, -.3)
        K.sweep_ring(F, trim, o, K.P_SURROUND, 0)
        K.box(F, trim, (sx, 3.62 + .62 + .1, .05), (.2, .26, .1))
    # glazed double doors in the main opening
    dh = 3.2 if style == 1 else 3.75 - ow / 2
    for x in (c - ow / 2 + .05, c, c + ow / 2 - .05):
        K.box(F, 'vi-bronze', (x, dh / 2, -.3), (.07, dh, .07))
    K.box(F, 'vi-bronze', (c, 2.6, -.3), (ow, .07, .07))
    for s_ in (-1, 1): K.box(F, 'vi-gilt-plain', (c + s_ * .14, 1.1, -.25), (.03, .45, .04))
    K.pane(F, 'vi-shop-glass', main, -.32)
    if style == 1:
        K.sweep_ring(F, trim, main, K.P_SURROUND, 0)
        aw = 'vi-awning-red' if seed % 2 else 'vi-awning-green'
        oface(F, aw, [(c - ow / 2 - .4, 3.55, .05), (c + ow / 2 + .4, 3.55, .05), (c + ow / 2 + .4, 3.0, 1.3), (c - ow / 2 - .4, 3.0, 1.3)], (0, 1, .5))
        for s_ in (-1, 1): oface(F, aw, [(c + s_ * (ow / 2 + .4), 3.55, .05), (c + s_ * (ow / 2 + .4), 3.0, 1.3), (c + s_ * (ow / 2 + .4), 2.85, 1.3)], (s_, 0, 0))
        K.box(F, aw, (c, 2.92, 1.3), (ow + .8, .16, .02))
        K.box(F, 'vi-wood-dark', (c, 4.0, .07), (min(w - 1.5, len(name) * .34 + .8), .52, .08))
        K.sweep_ring(F, 'vi-gilt-plain', [(c - min(w - 1.5, len(name) * .34 + .8) / 2, 3.74), (c + min(w - 1.5, len(name) * .34 + .8) / 2, 3.74),
                                          (c + min(w - 1.5, len(name) * .34 + .8) / 2, 4.26), (c - min(w - 1.5, len(name) * .34 + .8) / 2, 4.26)],
                     [(-.03, 0), (-.03, .03), (.03, .03), (.03, 0)], .11)
        K.text(F, name, c, 3.86, .12, .3, 'vi-sign-gold')
        for s_ in (-1, 1):
            K.lantern_head(F, c + s_ * (ow / 2 + .9), 2.25, .2, .6)
            K.box(F, 'vi-iron', (c + s_ * (ow / 2 + .9), 2.2, .1), (.12, .12, .2))
    else:
        K.arch_ring(F, c, 3.75 - ow / 2, ow, 0, trim, keystone=True)
        for s_ in (-1, 1): K.box(F, trim, (c + s_ * (ow / 2 + .16), (3.75 - ow / 2) / 2, .06), (.3, 3.75 - ow / 2, .12))
        for s_ in (-1, 1):
            lx = c + s_ * (ow / 2 + .55)
            K.path(F, 'vi-iron', [(lx, 2.85, .05), (lx, 2.95, .35), (lx, 3.0, .45)], .02, 5)
            K.lantern_head(F, lx, 2.62, .45, .7)
    K.entablature(F, x0, x1, 4.45, trim, 'vi-gilt' if style == 2 else colour, 'vi-gilt-plain', 0, .62, True)
    if style != 1:
        K.box(F, 'vi-marble-green', (c, 4.87, .05), (min(w - 1.2, len(name) * .3 + .8), .3, .04))
        K.text(F, name, c, 4.78, .08, .23, 'vi-sign-gold')
    K.sweep_facade(F, trim, x0, x1, H - .2, K.P_CORNICE_SMALL[:-1] + [(0, .2)])
    for x in (x0 + .32, x1 - .32): K.pilaster(F, x, 0, 4.45, .5, trim, 'vi-gilt-plain', 0, .12)
    blade_sign(F, x1 - .9 if seed % 2 else x0 + .9, 3.0, 'vi-casino-sign-red' if style != 1 else 'vi-wood-dark')
    for s_ in (-1, 1):
        K.planter(F, c + s_ * (ow / 2 + .75), .55, 0, .3, .5)
    ex = c - ow / 2 - 1.5 if seed % 2 else c + ow / 2 + 1.5
    for s_ in (-1, 1): K.tube(F, 'vi-wood-dark', (ex + s_ * .22, 0, .75), (ex + s_ * .2, 1.25, .62), .02, 4)
    K.box(F, 'vi-iron', (ex, .95, .68), (.5, .62, .03))
    K.box(F, 'vi-cloth-white', (ex, .97, .7), (.4, .48, .005))
    return name


def restaurant_row(B, G):
    B.source = 'restaurants'
    x0, z0, x1, z1 = RR
    zA = -760.0; zN = -805.5
    for side, names in ((-1, REST_W), (1, REST_E)):
        if side < 0: F, L = seg_frame(B, (x0, zA), (x0, zN))       # west fronts face east
        else: F, L = seg_frame(B, (x1, zN), (x1, zA))              # east fronts face west
        widths = [11.0, 12.5, 10.5, 11.5] if side < 0 else [12.0, 10.5, 11.5, 11.5]
        x = 0.0
        for k, w in enumerate(widths):
            w = w if k < 3 else L - x
            nm = names[k] if side < 0 else names[3 - k]
            restaurant(F, x, x + w, nm, k * 2 + (0 if side < 0 else 1))
            x += w
        K.solid_quad(F, (0, 0, 0), (L, 0, 0), (L, 6.0, 0), (0, 6.0, 0))
        K.sweep_facade(F, 'vi-gilt-plain', 0, L, 5.55, [(0, 0), (.2, .05), (.3, .15), (.42, .25), (0, .35)])
    # the north end: a ristorante's loggia against the podium wall
    F, L = seg_frame(B, (x0, zN), (x1, zN))
    K.arcade(F, .8, L - .8, 3, 0, 4.1, 5.65, 'vi-limestone', 'vi-stucco-ochre', .9, 0, 1.0, 'vi-limestone', 'vi-shop-display', True, True, .2)
    for x in (0, L - .8):
        K.box(F, 'vi-stucco-ochre', ((x + .4 if x == 0 else x + .4), 2.85, -.05), (.8, 5.7, .1))
    K.entablature(F, 0, L, 4.55, 'vi-limestone', 'vi-gilt', 'vi-gilt-plain', 0, .6, True)
    K.box(F, 'vi-marble-green', (L / 2, 4.86, .05), (8.6, .46, .04))
    K.sweep_ring(F, 'vi-gilt-plain', [(L / 2 - 4.3, 4.63), (L / 2 + 4.3, 4.63), (L / 2 + 4.3, 5.09), (L / 2 - 4.3, 5.09)], [(-.03, 0), (-.03, .03), (.03, .03), (.03, 0)], .07)
    K.text(F, 'RISTORANTE SAN MARCO', L / 2, 4.73, .09, .3, 'vi-sign-gold')
    for x in (3.2, L - 3.2): K.planter(F, x, 1.0, 0, .45, .6)
    K.solid_quad(F, (0, 0, 0), (L, 0, 0), (L, 6.0, 0), (0, 6.0, 0))
    # the painted sky in three panels between gilt beams, a gilt cornice along both sides
    zs = [zA, -775.0, -790.0, zN]
    for za, zb in zip(zs, zs[1:]):
        oface(G, 'vi-sky-dusk', [(x0, 5.9, zb + .2), (x1, 5.9, zb + .2), (x1, 5.9, za - .2), (x0, 5.9, za - .2)], (0, -1, 0))
    for z in zs[1:-1]:
        K.box(G, 'vi-gilt', ((x0 + x1) / 2, 5.78, z), (x1 - x0, .24, .3))
        for zz, yaw in ((z + .15, 0), (z - .15, math.pi)):
            K.sweep_facade(Frame(B, x0 if yaw == 0 else x1, zz, yaw, y=Y0), 'vi-gilt-plain', 0, x1 - x0, 5.6, [(0, 0), (.05, 0), (.05, .04), (0, .08)])
    # street: lamps on the centre line, cafe tables, planters and benches
    for z in (-768.0, -783.0, -798.0):
        K.lamp_post(G, (x0 + x1) / 2, z, 0, 3, 3.9)
    for z in (-766.0, -771.5, -787.0, -793.0):
        K.cafe_set(G, x0 + 2.3, z, 0, 4); K.cafe_set(G, x1 - 2.3, z + 2.0, 0, 4)
    for z in (-775.5, -790.5):
        for x in (x0 + 2.0, x1 - 2.0): K.planter(G, x, z, 0, .42, .55)
        K.planter(G, (x0 + x1) / 2, z, 0, .55, .6, topiary=False)
    for z in (-768.0, -783.0, -798.0):
        G.light((x0 + x1) / 2, 5.16, z, 0xffd6a0, 240, 18)


# ------------------------------------------------------------------ the venue
def build(B):
    B.property = 'venetianCasino-interior'; B.source = 'floor'; B.detail = 0
    G = Frame(B, 0, 0, 0, y=Y0)
    floors(B, G)
    ceiling(B, G)
    columns(B, G)
    walls(B, G)
    banks, machines = slots(B, G)
    pits(B, G)
    cage(B, G)
    round_bar(B, G)
    salon(B, G)
    escalators(B, G)
    restaurant_row(B, G)
    print(f'venetianCasino: {len(banks)} slot banks, {machines + 18} slot machines (18 in the salon)')
    xs, zs = [], []
    for g in B.groups.values():
        if g['property'] != B.property: continue
        v = np.array(g['vertices']); xs += [v[:, 0].min(), v[:, 0].max()]; zs += [v[:, 2].min(), v[:, 2].max()]
    bounds = [round(min(xs), 2), round(min(zs), 2), round(max(xs), 2), round(max(zs), 2)]
    zones = [dict(origin=[340.0, Y0, -760.5], yaw=0, width=105.0, depth=109.0, height=TOP),
             dict(origin=[344.0, Y0, -806.5], yaw=0, width=17.0, depth=47.5, height=6.0),
             dict(origin=[379.0, Y0, -743.5], yaw=0, width=10.0, depth=19.0, height=7.5 - Y0)]
    access = [[x, Y0, z] for x in (298.0, 320.0, 342.0, 364.0, 386.0) for z in (-660.0, -682.0, -705.0, -728.0, -752.0)]
    access += [[344.0, Y0, -772.0], [344.0, Y0, -792.0], [288.0, Y0, -687.0], [328.0, Y0, -652.0], [320.0, Y0, -652.0],
               [337.0, Y0, -652.0], [379.0, PLAN.L2, -742.0], [379.0, 3.7, -734.0]]
    views = {
        'vi-casino-arch': dict(eye=[290.5, 1.7, -687.0], target=[340.0, 2.6, -687.0], lens=18),
        'vi-casino-rotunda': dict(eye=[328.0, 1.7, -653.5], target=[336.0, 2.4, -700.0], lens=18),
        'vi-casino-slots': dict(eye=[314.6, 1.65, -696.0], target=[315.6, 1.9, -728.0], lens=18),
        'vi-casino-blackjack': dict(eye=[304.0, 1.75, -664.0], target=[314.0, .9, -674.5], lens=18),
        'vi-casino-craps': dict(eye=[344.5, 1.75, -664.5], target=[355.0, .9, -674.5], lens=18),
        'vi-casino-bar': dict(eye=[342.5, 1.7, -712.5], target=[355.0, 1.9, -706.0], lens=18),
        'vi-casino-cage': dict(eye=[306.0, 1.7, -668.0], target=[301.0, 2.3, -655.0], lens=18),
        'vi-casino-salon': dict(eye=[308.5, 1.7, -735.0], target=[299.0, 1.8, -751.0], lens=18),
        'vi-casino-restaurant-row': dict(eye=[344.0, 1.7, -761.0], target=[344.0, 2.9, -805.0], lens=18),
        'vi-casino-escalator': dict(eye=[379.5, 1.7, -715.0], target=[379.0, 5.4, -742.0], lens=18),
        'vi-casino-escalator-top': dict(eye=[377.0, PLAN.L2 + 1.7, -742.2], target=[377.0, 1.5, -722.0], lens=18),
        'vi-casino-overview': dict(eye=[290.6, 4.0, -662.0], target=[350.0, .6, -722.0], lens=18),
    }
    # (the escalator leg rides the east unit, local x -2 = world x 381, along its own step profile)
    ride = [[ESC_X + 2.0, Y0 + esc_y(d) + .08, ESC_Z - d] for d in list(np.arange(-.9, ESC_END, .5)) + [ESC_END - .05]]
    routes = [dict(points=[[288.0, Y0, -687.0], [336.0, Y0, -687.0], [336.0, Y0, -755.0], [341.0, Y0, -770.0], [341.0, Y0, -800.0]]),
              dict(points=[[328.0, Y0, -652.0], [336.0, Y0, -662.0], [336.0, Y0, -723.5], [381.0, Y0, -723.5]] + ride)]
    return [dict(key='venetianCasino', name='The Venetian · casino', bounds=bounds, portals=[], levelY=3.74, preloadDistance=40,
                 anchor=(379.0, 2.0, -738.0), zones=zones, accessPoints=access, routes=routes, views=views)]
