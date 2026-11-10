"""Prove the scoped candidate preserves the prior resort and adds no collision."""
import json
import sys
from pathlib import Path
from common import np
from crystals_glazing import HOSTS
from crystals_roof import POINTS
from patch_crystals_glazing import patch

before=json.loads(Path(sys.argv[1]).read_text())
after=json.loads(Path(sys.argv[2]).read_text())
expected,report=patch(before)
assert after==expected
added=after['meshes'][len(before['meshes']):]
# Every added vertex must lie near one of the two host planes, inside its inset.
for mesh in added:
    for vertex in mesh['vertices']:
        p=np.array(vertex)
        valid=False
        for ids in HOSTS:
            tri=np.array([POINTS[i] for i in ids],dtype=float)
            n=np.cross(tri[1]-tri[0],tri[2]-tri[0]);n/=np.linalg.norm(n)
            if n[1]<0:n=-n
            distance=np.dot(p-tri[0],n)
            weights=np.linalg.lstsq(np.column_stack((tri[1]-tri[0],tri[2]-tri[0])),p-tri[0]-distance*n,rcond=None)[0]
            if -.03<=distance<=.22 and min(weights)>=.09 and weights.sum()<=.91:
                valid=True;break
        assert valid, vertex
report['allAddedVerticesWithinInsetHostFacets']=True
print(json.dumps(report,indent=2))
