"""Disjoint render surfaces for overlapping, axis-aligned architectural slabs.

Collision boxes can overlap for reliable capsule traversal. Their visible surfaces
must instead describe the union: one top/soffit per point, no internal side faces.
All coordinates use game Y-up metres. No Blender dependency, so this is testable.
"""
from collections import defaultdict

BOX_FACES = [(1,2,3,0),(7,6,5,4),(4,5,1,0),(5,6,2,1),(6,7,3,2),(7,4,0,3)]

def slab_union(slabs):
    groups = defaultdict(list)
    for s in slabs:
        groups[(s['top'], s['depth'], s['material'], s['role'])].append(s)
    for (top, depth, material, role), records in groups.items():
        xs = sorted({v for s in records for v in (s['x0'], s['x1'])})
        zs = sorted({v for s in records for v in (s['z0'], s['z1'])})
        occupied = {}
        for i, (x0, x1) in enumerate(zip(xs, xs[1:])):
            for j, (z0, z1) in enumerate(zip(zs, zs[1:])):
                x, z = (x0+x1)/2, (z0+z1)/2
                owner = next((s['owner'] for s in records if s['x0'] < x < s['x1'] and s['z0'] < z < s['z1']), None)
                if owner is not None:
                    occupied[(i, j)] = owner
        for (i, j), owner in occupied.items():
            x0, x1, z0, z1 = xs[i], xs[i+1], zs[j], zs[j+1]
            vertices = [(x,y,z) for y in (top-depth, top) for x,z in ((x0,z0),(x1,z0),(x1,z1),(x0,z1))]
            faces = BOX_FACES[:2].copy()
            for neighbor, face in zip(((i,j-1),(i+1,j),(i,j+1),(i-1,j)), BOX_FACES[2:]):
                if neighbor not in occupied:
                    faces.append(face)
            yield owner, material, role, vertices, faces


def subtract_rectangle(rect, cover):
    """Return disjoint parts of rect outside cover, in (x0,x1,z0,z1) order."""
    x0,x1,z0,z1 = rect
    a,b,c,d = max(x0,cover[0]),min(x1,cover[1]),max(z0,cover[2]),min(z1,cover[3])
    if b-a < 1e-7 or d-c < 1e-7:
        return [rect]
    return [r for r in ((x0,a,z0,z1),(b,x1,z0,z1),(a,b,z0,c),(a,b,d,z1))
            if r[1]-r[0] > 1e-7 and r[3]-r[2] > 1e-7]
