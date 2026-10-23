"""Fill only missing local pavement, independently audit visual and physical coverage."""
from common import *
def local_pavement(B,apron,D,material):
 covered=[]
 for g in json.loads(Path('build/geographic-strip/city-meshes.json').read_text()):
  if not g['faces']:continue
  q=np.asarray(g['vertices'])[np.asarray(g['faces'])];xs=q[:,:,0];zs=q[:,:,2];ys=q[:,:,1];a=apron.bounds
  mask=(xs.max(1)>a[0])&(xs.min(1)<a[2])&(zs.max(1)>a[1])&(zs.min(1)<a[3])&(ys.max(1)<.6)&(ys.min(1)>-.1)
  for t in q[mask]:
   poly=Polygon(t[:,[0,2]])
   if poly.area>.001:covered.append(poly.intersection(apron).buffer(.015))
 paving=apron.difference(unary_union(covered));B.planar(material,paving,D,True)
 # Some retained city pavement is visual-only. Supply its missing collision,
 # subtracting any actual existing near-ground collider triangles first.
 physical=[]
 for c in json.loads(Path('build/geographic-strip/city-colliders.json').read_text()):
  if not c['indices']:continue
  q=np.asarray(c['vertices']).reshape(-1,3)[np.asarray(c['indices']).reshape(-1,3)];xs=q[:,:,0];zs=q[:,:,2];ys=q[:,:,1];a=apron.bounds
  mask=(xs.max(1)>a[0])&(xs.min(1)<a[2])&(zs.max(1)>a[1])&(zs.min(1)<a[3])&(ys.max(1)<.6)&(ys.min(1)>-.1)
  for t in q[mask]:
   poly=Polygon(t[:,[0,2]])
   if poly.area>.001:physical.append(poly.intersection(apron))
 missing=apron.difference(paving).difference(unary_union(physical))
 B.planar('local-paving-collision-only',missing,D,True)
 for k in list(B.groups):
  if B.groups[k]['material']=='local-paving-collision-only':del B.groups[k]
