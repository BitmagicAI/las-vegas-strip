"""Regression: the small pavilion and shorter wing must not inherit 123m."""
import json,sys
sys.path.insert(0,'tools/strip-landmarks')
from common import *
data=json.load(open('build/strip-landmarks/hgvExterior-exterior.json'))
points=[v for m in data['meshes'] if m['source']=='tower/hgv-boulevard' for v in m['vertices']]
result=[]
for p in parts(footprint('relation/6138877')):
 h=14 if p.area<800 else (90 if p.bounds[3]-p.bounds[1]>p.bounds[2]-p.bounds[0] else 123)
 selected=[v[1] for v in points if p.buffer(.9).covers(Point(v[0],v[2]))]
 assert selected and h<=max(selected)<=h+3,(h,max(selected))
 result.append({'height':h,'maxVertex':max(selected)})
t=next(t for t in json.load(open('src/work/hotels/highrise-towers.json')) if t['building']=='hgv-boulevard')
assert t['floors']*3.6+.24<90
c=json.load(open('build/highrises/hgv-boulevard-collision.json'))
assert max(c['vertices'][1::3])==123
print(json.dumps({'parts':result,'guestFloors':t['floors'],'collisionTriangles':len(c['indices'])//3},indent=2))
