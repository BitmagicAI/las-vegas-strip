"""Original shallow coffer frames; additive decoration with no collision changes.

Reference and inferred dimensions: paris-frontage-refinement/research.md.
The existing faceted barrel remains the recessed backing. No source image is used
as a texture, and no older mesh or label is replaced.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path

SOURCE = 'arrival-arc-coffers-2026-11'


def ornament():
    mesh = dict(property='parisBlock-exterior', source=SOURCE,
                material='paris-stone', detail=1, vertices=[], faces=[])

    def point(a, v, r):
        return [127.3 + v, 12.5 + r * math.sin(a), 490.7 - r * math.cos(a)]

    def wedge(a, b, v, w):
        pts = [point(t, z, r) for r in [4.47, 4.64]
               for z in [v, w] for t in [a, b]]
        center = [sum(p[k] for p in pts) / 8 for k in range(3)]
        base = len(mesh['vertices'])
        mesh['vertices'].extend(pts)
        for face in [(0,1,3,2),(4,6,7,5),(0,4,5,1),
                     (2,3,7,6),(0,2,6,4),(1,5,7,3)]:
            q = list(face)
            u = [pts[q[1]][k]-pts[q[0]][k] for k in range(3)]
            v0 = [pts[q[2]][k]-pts[q[0]][k] for k in range(3)]
            normal = [u[1]*v0[2]-u[2]*v0[1],u[2]*v0[0]-u[0]*v0[2],u[0]*v0[1]-u[1]*v0[0]]
            outward = [sum(pts[i][k] for i in q)/4-center[k] for k in range(3)]
            if sum(normal[k]*outward[k] for k in range(3)) < 0:
                q.reverse()
            mesh['faces'].extend([[base+q[0],base+q[1],base+q[2]],
                                  [base+q[0],base+q[2],base+q[3]]])

    def strip(a, b, v, w):
        n = max(1, math.ceil((b-a)/.06))
        for k in range(n):
            wedge(a+(b-a)*k/n, a+(b-a)*(k+1)/n, v, w)

    for row in range(9):
        a = .04 + row*(math.pi-.08)/9 + .025
        b = .04 + (row+1)*(math.pi-.08)/9 - .025
        for col in range(5):
            v = -6.35 + col*12.7/5 + .10
            w = -6.35 + (col+1)*12.7/5 - .10
            strip(a,a+.032,v,w)
            strip(b-.032,b,v,w)
            strip(a+.032,b-.032,v,v+.14)
            strip(a+.032,b-.032,w-.14,w)
    return mesh


def patch(data):
    old = [m for m in data['meshes'] if not m['source'].startswith(SOURCE)]
    added = ornament()
    cells = {}
    for face in added['faces']:
        points = [added['vertices'][i] for i in face]
        cell = (math.floor(sum(p[0] for p in points)/192),
                math.floor(sum(p[2] for p in points)/192))
        group = cells.setdefault(cell, {**added, 'source': SOURCE+f'@{cell[0]}_{cell[1]}',
                                        'vertices': [], 'faces': []})
        n = len(group['vertices'])
        group['vertices'].extend(points)
        group['faces'].append([n,n+1,n+2])
    result = {**data, 'meshes': old+list(cells.values())}
    assert result['labels'] == data['labels']
    pts = added['vertices']
    assert all(120.7 < p[0] < 133.9 and 12.5 < p[1] < 17.15
               and 486 < p[2] < 495.4 for p in pts)
    return result, dict(coffers=45, retainedGroups=len(old),
                       addedTriangles=len(added['faces']), newCollisionTriangles=0,
                       existingGroupsAndLabelsPreserved=True,
                       bounds=[[min(p[k] for p in pts),max(p[k] for p in pts)] for k in range(3)])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    for name in ['source','output','audit']:
        parser.add_argument('--'+name,type=Path,required=True)
    args = parser.parse_args()
    result,audit = patch(json.loads(args.source.read_text()))
    audit['sourceSHA256'] = hashlib.sha256(args.source.read_bytes()).hexdigest()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,separators=(',',':')))
    args.audit.write_text(json.dumps(audit,indent=2)+'\n')
    print(json.dumps(audit,indent=2))
