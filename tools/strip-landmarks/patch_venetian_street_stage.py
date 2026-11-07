"""Apply only recognized old/new street-stage triangle differences to retained source.

Avoid regenerating the resort, its interiors, collision or later ownership cuts.
"""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
from common import Meshes
from venetian_frontage import palazzi


def key(mesh, points):
    p = tuple(tuple(round(float(v), 7) for v in q) for q in points)
    oriented = min(p, p[1:]+p[:1], p[2:]+p[:2])
    return mesh['material'], mesh['detail'], oriented


def rows(meshes):
    for mesh in meshes:
        for face in mesh['faces']:
            points = [mesh['vertices'][i] for i in face]
            yield key(mesh, points), mesh, points


def delta():
    before, after = Meshes(), Meshes()
    before.property = after.property = 'venetian-exterior'
    palazzi(before, refine_street=False)
    palazzi(after, refine_street=True)
    assert before.labels == after.labels
    assert dict(before.solids) == dict(after.solids)
    old = Counter(k for k, _, _ in rows(before.groups.values()))
    new = Counter(k for k, _, _ in rows(after.groups.values()))
    return old-new, new-old, after


def patch(data):
    remove, add, generated = delta()
    expected = sum(remove.values())
    output = []
    retained = 0
    for mesh in data['meshes']:
        if mesh['source'] != 'palazzo-front':
            output.append(mesh)
            retained += 1
            continue
        faces = []
        for face in mesh['faces']:
            k = key(mesh, [mesh['vertices'][i] for i in face])
            if remove[k]:
                remove[k] -= 1
            else:
                faces.append(face)
        output.append({**mesh, 'faces': faces})
    missing = sum(remove.values())
    assert missing == 0, f'{missing}/{expected} old triangles unrecognized; refusing replacement'
    additions = {}
    for k, mesh, points in rows(generated.groups.values()):
        if not add[k]:
            continue
        add[k] -= 1
        groupkey = mesh['material'], mesh['detail']
        g = additions.setdefault(groupkey, {**mesh, 'source': 'palazzo-front-street-stage-2026-11',
                                            'vertices': [], 'faces': []})
        n = len(g['vertices'])
        g['vertices'].extend(points)
        g['faces'].append([n, n+1, n+2])
    assert not sum(add.values())
    result = {**data, 'meshes': output+list(additions.values())}
    assert result['labels'] == data['labels']
    report = {'removedRecognizedTriangles': expected,
              'addedTriangles': sum(len(m['faces']) for m in additions.values()),
              'untouchedGroups': retained, 'labelsUnchanged': True, 'generatedCollisionUnchanged': True,
              'scope': 'way/33996627 west/north upper stage only; ground and adjacent buildings retained'}
    return result, report


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    for name in ['source', 'output', 'audit']:
        p.add_argument('--'+name, type=Path, required=True)
    a = p.parse_args()
    result, report = patch(json.loads(a.source.read_text()))
    report['sourceSHA256'] = hashlib.sha256(a.source.read_bytes()).hexdigest()
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(result, separators=(',', ':')))
    a.audit.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(report, indent=2))
