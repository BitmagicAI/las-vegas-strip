"""Share repeated vertices in local collision cells; precision is 0.1 mm."""
import json
from pathlib import Path
p=Path('build/geographic-strip/city-colliders.json')
cells=json.loads(p.read_text());before=after=0
for cell in cells:
    values=cell['vertices'];before+=len(values)//3
    vertices=[];lookup={};remap=[]
    for i in range(0,len(values),3):
        point=tuple(round(v,4) for v in values[i:i+3])
        if point not in lookup:
            lookup[point]=len(vertices)//3;vertices.extend(point)
        remap.append(lookup[point])
    indices=[]
    for i in range(0,len(cell['indices']),3):
        face=[remap[v] for v in cell['indices'][i:i+3]]
        if len(set(face))==3:indices.extend(face)
    cell['vertices']=vertices;cell['indices']=indices;after+=len(vertices)//3
p.write_text(json.dumps(cells,separators=(',',':')))
print(json.dumps(dict(verticesBefore=before,verticesAfter=after,bytes=p.stat().st_size)))
