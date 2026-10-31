#!/usr/bin/env python3
"""Read-only baseline for the approved 800m city-file split. Never rewrites assets."""
import argparse
import hashlib
import json
import struct
from collections import Counter
from pathlib import Path


def audit(path):
    data = path.read_bytes()
    magic, version, length = struct.unpack_from('<III', data)
    if magic != 0x46546C67 or version != 2 or length != len(data):
        raise ValueError(f'{path}: invalid GLB 2 header (or unresolved LFS pointer)')
    size, kind = struct.unpack_from('<II', data, 12)
    if kind != 0x4E4F534A:
        raise ValueError('Missing GLB JSON chunk')
    doc = json.loads(data[20:20 + size])
    cells = {}
    materials = doc.get('materials', [])
    for node in doc.get('nodes', []):
        if 'mesh' not in node:
            continue
        extras = node.get('extras', {})
        cell = extras.get('osmCell')
        if cell is None:
            raise ValueError(f'Mesh without osmCell: {node.get("name")}')
        if cell != 'base':
            x, z = map(int, cell.split(','))
            if cell != f'{x},{z}':
                raise ValueError(f'Noncanonical cell: {cell}')
        record = cells.setdefault(cell, {'nodes': [], 'materials': Counter(), 'triangles': 0})
        record['nodes'].append(node.get('name', ''))
        for primitive in doc['meshes'][node['mesh']]['primitives']:
            if primitive.get('mode', 4) != 4:
                raise ValueError('Nontriangle city primitive')
            count = doc['accessors'][primitive['indices']]['count']
            record['triangles'] += count // 3
            material = materials[primitive['material']]['name']
            record['materials'][material] += 1
    return {'input': str(path), 'sha256': hashlib.sha256(data).hexdigest(),
            'bytes': len(data), 'cellSizeMetres': 800, 'cellCount': len(cells),
            'meshNodes': sum(len(c['nodes']) for c in cells.values()),
            'triangles': sum(c['triangles'] for c in cells.values()),
            'cells': dict(sorted(cells.items()))}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input', type=Path)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    report = audit(args.input)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'cells'}))
