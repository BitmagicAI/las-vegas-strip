import sys,json,math
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon,box,mapping
from shapely.ops import unary_union,transform
sys.path.insert(0,'tools/highrises');from catalog import records
root=Path('build/highrises');root.mkdir(exist_ok=True,parents=True)
survey=json.loads(Path('build/strip-survey/survey.json').read_text());byid={f['id']:f for f in survey['buildings']}
plans=[];towers=[]
for p in records():
 fs=[byid[i] for i in p['ids'] if i in byid];shapes={f['id']:unary_union([Polygon([(x,-z) for x,z in poly[0]],[[(x,-z) for x,z in ring] for ring in poly[1:]]).buffer(0) for poly in f['polygons']]) for f in fs}
 p['features']=fs;p['centroid']=list(unary_union(list(shapes.values())).centroid.coords)[0];p['towers']=[]
 # One independently addressable core per disconnected tower. Prefer the actual
 # tower part over a same-height, larger parent podium (Trump/Sky/Grand Chateau).
 ordered=sorted(fs,key=lambda f:shapes[f['id']].area)
 selected=[]
 for f in ordered:
  poly=shapes[f['id']]
  if poly.area<500 or f['height']<65 or f['base']>30:continue
  if p['key']=='luxor' and f['id']=='way/27858544':continue
  if p['key']=='strat' and f['height']>200:continue
  if any(poly.intersection(shapes[q['id']]).area>min(poly.area,shapes[q['id']].area)*.3 for q in selected):continue
  selected.append(f)
 for f in selected:
  poly=shapes[f['id']];coords=list(poly.minimum_rotated_rectangle.exterior.coords);best=None
  if p['key']=='bellagio-spa':
   # Existing playable munitions arcade occupies the south end of this footprint.
   # Keep its collision and play area intact; fit this guest wing clear of it.
   poly=poly.difference(box(-400,574,-350,601));coords=list(poly.minimum_rotated_rectangle.exterior.coords)
  if p['key']=='new-york':
   poly=unary_union(list(shapes.values()));coords=list(poly.minimum_rotated_rectangle.exterior.coords)
  angles={round(math.atan2(b[1]-a[1],b[0]-a[0]),3) for a,b in zip(coords,coords[1:])}
  angles.update(math.radians(a) for a in range(0,360,15))
  for angle in angles:
   dx,dz=math.cos(angle),math.sin(angle);xx,zz=dz,-dx;cx,cz=poly.centroid.coords[0]
   local=transform(lambda x,z:((x-cx)*xx+(z-cz)*zz,(x-cx)*dx+(z-cz)*dz),poly)
   for width in [19.2,16,14.5]:
    for bays in [14,10,8,6,4,3,2]:
     length=10.5+6*bays;score=length*width
     if best and score<=best[0]:continue
     x0,z0,x1,z1=local.bounds
     if x1-x0<width or z1-z0<length:continue
     for x in np.arange(x0+width/2,x1-width/2+.1,4):
      for z in np.arange(z0+length/2,z1-length/2+.1,4):
       rect=box(x-width/2,z-length/2,x+width/2,z+length/2)
       if not local.covers(rect):continue
       origin=[cx+xx*x+dx*(z+length/2-5.25),.24,cz+zz*x+dz*(z+length/2-5.25)]
       best=(score,origin,[xx*width/19.2,dx,zz*width/19.2,dz],bays)
  if not best:
   print('NO FIT',p['key'],f['id'],round(poly.area));continue
  length,origin,linear,bays=best;localfront=-5.25-6*bays
  # Extend the approach from the fitted wing to the first exterior boundary.
  direction=np.array([linear[1],linear[3]]);op=np.array([origin[0],origin[2]])
  from shapely.geometry import LineString
  # Continue through a contiguous low resort podium to a real outdoor boundary.
  # Tower footprints alone often terminate at an internal wall, not a street door.
  podiums=[poly]
  for other in survey['buildings']:
   if other['height']>65 or other['id']==f['id']:continue
   for rings in other['polygons']:
    candidate=Polygon([(x,-z) for x,z in rings[0]],[[(x,-z) for x,z in ring] for ring in rings[1:]]).buffer(0)
    if candidate.distance(poly)<1:podiums.append(candidate)
  envelope=unary_union(podiums).buffer(.15)
  ray=LineString([op-direction*5,op-direction*800]);intersection=ray.intersection(envelope.boundary)
  points=[q for q in getattr(intersection,'geoms',[intersection]) if q.geom_type=='Point']
  distances=sorted(float(np.dot(op-np.array(q.coords[0]),direction)) for q in points)
  extent=next((d for d in distances if d>=-localfront-.1),-localfront)
  floors=max(3,int((f['height']-.24)//3.6))
  if p['key']=='new-york':floors=23
  if p['key']=='hgv-boulevard':floors=24 # fitted core lies in the 90m southern wing
  ident=p['key']+'-'+str(len(p['towers'])+1)
  t=dict(id=ident,name=p['name']+(' · Tower '+str(len(p['towers'])+1) if len(selected)>1 else ''),building=p['key'],origin=origin,yaw=math.atan2(linear[1],linear[0]),linear=linear,floors=floors,firstGuestFloor=2,bays=bays,kind=p['kind'],set=p['key'],roomDepth=7.6,lazy=True,source=f['id'],lobbyFront=-extent,windowWidth=19.2)
  if p['key']=='palms':t.update(json.loads(Path('tools/highrises/palms-core-fit.json').read_text()))
  p['towers'].append(t);towers.append(t)
 plans.append(p)
# Preserve authored connections from public podiums when regenerating tower fits.
connection_file=Path('build/strip-landmarks/next-plan.json')
if connection_file.exists():
 for venue in json.loads(connection_file.read_text()):
  for link in venue['connections']:
   for t in towers:
    if t['id']==link['tower']:
     t['publicArrival']=venue['key'];t['publicConnection']={k:link[k] for k in ['side','at','width']}
(root/'plan.json').write_text(json.dumps(plans,indent=2));Path('src/work/hotels/highrise-towers.json').write_text(json.dumps(towers,indent=2))
(root/'replacement-ids.json').write_text(json.dumps([f['id'] for p in plans for f in p['features']]))
print(len(plans),'properties',len(towers),'cores',sum((t['floors']-2)*t['bays']*2 for t in towers),'virtual rooms')
