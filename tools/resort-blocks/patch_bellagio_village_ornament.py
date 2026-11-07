"""Original shallow north-village ornament, fitted to existing pavilion frames.

JERDE's built photograph and June 2020 lakeside panorama corroborate framed
oval medallions and cornice rhythm. Dimensions below are inferred, not surveyed.
Only additive decorative meshes are written; existing groups, labels, circulation
and collision remain immutable. See bellagio-lakefront-refinement/research.md.
"""
import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, 'tools/strip-landmarks')
from common import Frame, Meshes, Point, Polygon, LineString, unary_union
from bellagio_lakefront import PAVILIONS

SOURCE = 'lakefront-pavilion-ornament-2026-11'


def ornament():
    b = Meshes()
    b.property = 'bellagioBlock-exterior'
    b.source = SOURCE
    b.detail = 1
    access = json.loads(Path('build/geographic-strip/access/bellagio-via-plan.json').read_text())
    via = unary_union([Polygon(p) for p in access['upper']] +
                      [LineString(p).buffer(4.2) for p in access['lower']] +
                      [LineString(p).buffer(3.5) for p in access['stairs']]).buffer(.7)
    audit = []
    for index, (x, z, w, d, yaw, h, _, _) in enumerate(PAVILIONS):
        f = Frame(b, x, z, yaw, 0)
        counts = {'pavilion': index, 'center': [x, z], 'dentils': 0, 'medallions': 0}
        # Dentils occupy the existing .29 m gap between the upper two cornice bands.
        # A .10 m back overlap joins the wall; all exposed depth is <= .34 m.
        for axis, span, offset in [('front', w, d / 2), ('end', d, w / 2)]:
            for side in [-1, 1]:
                p = f.p(0, 0, side * offset) if axis == 'front' else f.p(side * offset, 0, 0)
                angle = yaw + (math.pi if side < 0 else 0) if axis == 'front' else yaw + side * math.pi / 2
                face = Frame(b, p[0], p[2], angle, 0)
                n = max(1, round((span - 1.4) / .72))
                for k in range(n):
                    xx = (k + .5) * (span - 1.4) / n - (span - 1.4) / 2
                    q = face.p(xx, 0, 0)
                    if via.covers(Point(q[0], q[2])):
                        continue
                    face.box('lake-stone', (xx, h - .43, .12), (.25, .24, .44))
                    counts['dentils'] += 1
                # End-wall central spandrel: avoids all existing long-face shop signs
                # and the two end-wall window/balcony bays at +/- .26 * depth.
                q = face.p(0, 0, 0)
                if axis != 'end' or via.covers(Point(q[0], q[2])):
                    continue
                yy = h - 2.1
                for xx in [-.76, .76]:
                    face.box('lake-stone', (xx, yy, .09), (.10, 1.42, .22))
                for dy in [-.66, .66]:
                    face.box('lake-stone', (0, yy + dy, .09), (1.52, .10, .22))
                # Two shallow oval rings, no new texture or metallic material.
                for rx, ry, depth, radius in [(.47, .52, .12, .065), (.34, .39, .10, .035)]:
                    points = [(rx * math.cos(k * math.tau / 20),
                               yy + ry * math.sin(k * math.tau / 20), depth)
                              for k in range(21)]
                    face.path('lake-stone', points, radius, 6)
                counts['medallions'] += 1
        audit.append(counts)
    assert not b.solids and not b.labels
    return list(b.groups.values()), audit


def patch(data):
    # Re-applying replaces only our own additive group, preserving every older group.
    old = [m for m in data['meshes'] if m['source'] != SOURCE]
    extra, audit = ornament()
    result = {**data, 'meshes': old + extra}
    assert result['meshes'][:len(old)] == old
    assert result['labels'] == data['labels']
    pts = [p for m in extra for p in m['vertices']]
    assert all(-165 < p[0] < -25 and 179 < p[2] < 261 and 9 < p[1] < 14 for p in pts)
    return result, {'pavilions': audit, 'retainedGroups': len(old),
                    'addedTriangles': sum(len(m['faces']) for m in extra),
                    'bounds': [[min(p[a] for p in pts), max(p[a] for p in pts)] for a in range(3)],
                    'existingGroupsAndLabelsPreserved': True, 'newCollisionTriangles': 0}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--audit', type=Path, required=True)
    args = parser.parse_args()
    data = json.loads(args.source.read_text())
    result, audit = patch(data)
    audit['sourceSHA256'] = hashlib.sha256(args.source.read_bytes()).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, separators=(',', ':')))
    args.audit.write_text(json.dumps(audit, indent=2) + '\n')
    print(json.dumps(audit, indent=2))
