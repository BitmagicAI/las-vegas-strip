"""Subtract the mapped water basin from flat city visuals and collision.
Idempotent, local polygon clipping; does not regenerate the road network.
"""
import sys,json
from pathlib import Path
sys.path.insert(0,'tools/strip-landmarks')
from common import *
out=Path('build/geographic-strip')
water=Polygon(json.loads(Path('tools/resort-blocks/references/bellagio/lake-outline.json').read_text())['coordinates'])
def clip(vertices):
    if max(p[1] for p in vertices)>.45 or min(p[1] for p in vertices)<-.1:return None
    poly=Polygon([(p[0],p[2]) for p in vertices])
    if poly.area<1e-9 or not poly.intersects(water):return None
    if poly.intersection(water).area<1e-8:return None
    plane=np.linalg.solve(np.array([[p[0],p[2],1] for p in vertices]),np.array([p[1] for p in vertices]))
    result=[]
    for piece in parts(poly.difference(water)):
        for tri in triangles(piece):
            pts=list(tri.exterior.coords)[:-1]
            if Polygon(pts).exterior.is_ccw!=poly.exterior.is_ccw:pts.reverse()
            result.append([[x,float(plane[0]*x+plane[1]*z+plane[2]),z] for x,z in pts])
    return result
count=0;groups=json.loads((out/'city-meshes.json').read_text())
for g in groups:
    if g['material'] not in ['ground','plaza','paving','verge','sidewalk','road','gutter','grass','planting','gravel','paint']:continue
    v=g['vertices'];faces=[]
    for face in g['faces']:
        pieces=clip([v[i] for i in face])
        if pieces is None:faces.append(face);continue
        count+=1
        for piece in pieces:n=len(v);v.extend(piece);faces.append([n,n+1,n+2])
    g['faces']=faces
(out/'city-meshes.json').write_text(json.dumps(groups,separators=(',',':')))
cells=json.loads((out/'city-colliders.json').read_text());physics=0
for c in cells:
    x,z=c['center']
    if not -300<x<100 or not 80<z<640:continue
    v=c['vertices'];idx=[]
    for j in range(0,len(c['indices']),3):
        face=c['indices'][j:j+3];pieces=clip([v[i*3:i*3+3] for i in face])
        if pieces is None:idx.extend(face);continue
        physics+=1
        for piece in pieces:n=len(v)//3;v.extend(n for p in piece for n in p);idx.extend([n,n+1,n+2])
    c['indices']=idx
(out/'city-colliders.json').write_text(json.dumps(cells,separators=(',',':')))
Path('build/resort-blocks/bellagio/lake-city-cut.json').write_text(json.dumps(dict(source='OSM way/22971030',areaM2=water.area,visualFacesCut=count,collisionFacesCut=physics),indent=2))
print('Bellagio lake cut:',count,'visual and',physics,'collision faces',flush=True)
