"""Audit candidate ornament vertices against retained coplanar facade triangles."""
import sys,json,math
from pathlib import Path
sys.path[:0]=['tools/resort-blocks','tools/strip-landmarks']
from common import Frame,Polygon,unary_union,box,Meshes
from bellagio_lakefront import PAVILIONS
from patch_bellagio_village_ornament import ornament
old=json.loads(Path(sys.argv[1] if len(sys.argv)>1 else 'build/resort-blocks/bellagio/bellagioBlock-exterior.json').read_text())
extra,counts=ornament(); pts=[p for m in extra for p in m['vertices']]
wall=[m for m in old['meshes'] if m['source']=='lakefront-pavilions' and m['material'] in ['lake-cream','lake-ochre']]
report=[]
for index,(x,z,w,d,yaw,h,*_) in enumerate(PAVILIONS):
 f=Frame(Meshes(),x,z,yaw,0)
 for axis,span,offset in [('front',w,d/2),('end',d,w/2)]:
  for side in [-1,1]:
   p=f.p(0,0,side*offset) if axis=='front' else f.p(side*offset,0,0)
   angle=yaw+(math.pi if side<0 else 0) if axis=='front' else yaw+side*math.pi/2
   co,si=math.cos(angle),math.sin(angle)
   def local(v):
    dx,dz=v[0]-p[0],v[2]-p[2]
    return (co*dx-si*dz,v[1],si*dx+co*dz)
   polys=[]
   for m in wall:
    for face in m['faces']:
     q=[local(m['vertices'][i]) for i in face]
     if all(abs(v[2])<1e-4 for v in q):
      poly=Polygon([(v[0],v[1]) for v in q])
      if poly.area>1e-8:polys.append(poly)
   support=unary_union(polys).buffer(.001)
   selected=[local(v) for v in pts if -.101<=local(v)[2]<=.341 and abs(local(v)[0])<span/2-.5 and h-3< v[1]<h]
   unsupported=[v for v in selected if not support.covers(__import__('shapely').geometry.Point(v[0],v[1]))]
   report.append(dict(pavilion=index,axis=axis,side=side,samples=len(selected),unsupported=len(unsupported)))
Path('docs/project-records/bellagio-lakefront-refinement/facade-support-audit.json').write_text(json.dumps(report,indent=2)+'\n')
assert sum(r['samples'] for r in report)==len(pts), 'Every added vertex must have exactly one supporting face'
print(report)
assert not any(r['unsupported'] for r in report)
