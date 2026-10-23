"""Luxor: mapped stepped wings and pyramid, Earth 2022 reference. Exterior only."""
from common import *
from building_surfaces import BuildingSurfaces
KEY='luxorExterior'
class Access:
 def __init__(self,plan):self.plan=plan
 def wall(self,a,b,lo,hi):
  line=LineString([a,b]);L=line.length;region=box(0,lo,L,hi)
  for t in self.plan['towers']:
   aa,bb,cc,dd=t['linear'];ox,oy,oz=t['origin'];det=aa*dd-bb*cc
   def local(x,z):return ((dd*(x-ox)-bb*(z-oz))/det,(aa*(z-oz)-cc*(x-ox))/det)
   dl=LineString([local(*a),local(*b)]);zone=box(-2.5,t['lobbyFront']-12,2.5,-5)
   for seg in parts(dl.intersection(zone),'LineString'):
    u=[dl.project(Point(q))/max(dl.length,.001)*L for q in seg.coords];region=region.difference(box(min(u),0,max(u),4.7))
  return [[[line.interpolate(x).x,y,line.interpolate(x).y] for x,y in list(tri.exterior.coords)[:-1]] for poly in parts(region) for tri in triangles(poly)]

def exterior(B):
 B.property=KEY+'-exterior';B.detail=0
 ids=[f['id'] for f in SURVEY if f['id'].startswith(('way/1365166','way/1365201'))]
 ids=[i for i in ids if 20<=BYID[i]['height']<=80]
 records=[dict(BYID[i],shape=footprint(i)) for i in ids]
 surface=BuildingSurfaces(records);plan=next(p for p in json.load(open('build/highrises/plan.json')) if p['key']=='luxor');access=Access(plan)
 for r in records:
  ident=r['id'];p=r['shape'];h=r['height'];lo=r['base'];podium=h==20
  if podium:continue # Authored low lobby and service section below owns this shell.
  B.source='podium/'+ident if podium else 'tower/luxor'
  for poly in parts(p):
   for ring in [poly.exterior,*poly.interiors]:
    ps=list(ring.coords)
    for a,b in zip(ps,ps[1:]):
     line=LineString([a,b]);L=line.length
     if L<.1:continue
     ux,uz=(b[0]-a[0])/L,(b[1]-a[1])/L;nx,nz=-uz,ux;mid=line.interpolate(.5,normalized=True)
     if p.contains(Point(mid.x+nx*.05,mid.y+nz*.05)):nx,nz=-nx,-nz
     vis=surface.wall(ident,a,b,lo,h,access)
     region=unary_union([Polygon([(line.project(Point(v[0],v[2])),v[1]) for v in tri]) for tri in vis])
     def patch(mat,x0,y0,x1,y1,offset=.18):
      for q in parts(region.intersection(box(x0,y0,x1,y1))):
       for tri in triangles(q):B.face(mat,[(a[0]+ux*x+nx*offset,y,a[1]+uz*x+nz*offset) for x,y in list(tri.exterior.coords)[:-1]])
     cheek=not podium and L<25 and abs(nx)>.8
     patch('luxor-stone' if podium or cheek else 'luxor-glass',0,lo,L,h)
     if not podium:
      for y in np.arange(4,h,3.15):patch('luxor-joint' if cheek else 'luxor-band',0,y,L,y+.045 if cheek else y+.13,.24)
      # White side cheeks outline each progressively stepped wing.
      for x in [0,L-.45]:patch('luxor-stone',x,lo,x+.45,h,.31)
      patch('luxor-stone',0,h-.8,L,h,.33)
      B.detail=1
      for x in ([] if cheek else np.arange(1.55,L,1.55)):patch('luxor-mullion',x,lo,x+.025,h,.26)
      B.detail=0
     else:
      for x in np.arange(1,L-1,4.6):
       patch('luxor-glass',x,1,min(x+3.6,L-.3),6.2,.27)
       patch('luxor-band',x,6.25,min(x+3.6,L-.3),6.38,.30)
      for y in [7,15,19.4]:patch('luxor-band',0,y,L,y+.18,.30)
      B.detail=1
      for y in np.arange(1,19,1.5):patch('luxor-joint',0,y,L,y+.025,.21)
      B.detail=0
   roof=surface.roof(ident,poly,h)
   B.planar('luxor-membrane-paint',roof,h+.04)
   if not podium:
    for x in np.arange(p.bounds[0]+2,p.bounds[2]-1,14):
     for z in np.arange(p.bounds[1]+2,p.bounds[3]-1,15):
      if roof.contains(box(x-1,z-1,x+1,z+1)):B.box('ph-metal',(x,h+.5,z),(2.0,.9,2.0))
 # Pyramid panels: one clear envelope and fine mullions, no duplicate overlay.
 B.source='tower/luxor';p=footprint('way/27858544')
 for poly in parts(p):
  c=poly.centroid;ps=list(poly.exterior.coords)
  for a,b in zip(ps,ps[1:]):
   L=math.dist(a,b)
   def point(u,t,lift=0):return ((a[0]*(1-u)+b[0]*u)*(1-t)+c.x*t,111*t+lift,(a[1]*(1-u)+b[1]*u)*(1-t)+c.y*t)
   B.face('luxor-pyramid',[point(0,0),point(1,0),point(.5,1)])
 # Full rebuild uses the same site section as the surgical city-design pass.
 from luxor_north_detail import exterior as north,ID
 from luxor_service_detail import exterior as service
 from luxor_sphinx import exterior as sphinx
 from luxor_pool_detail import exterior as pool
 towerids=north(B);replacement=[ID,'way/115647257']+service(B)+sphinx(B)+pool(B)
 owned=set(json.load(open('build/highrises/replacement-ids.json')))
 for ident in towerids:
  if ident in owned:continue
  p=footprint(ident);r=BYID[ident];C=Meshes();C.property=KEY+'-exterior'
  C.shell(p,r['base'],r['height'],'x',roof=False);C.planar('x',p,r['height'],True)
  target=B.solids[KEY+'-exterior'];other=C.solids[KEY+'-exterior'];offset=len(target['vertices'])//3
  target['vertices'].extend(other['vertices']);target['indices'].extend(i+offset for i in other['indices']);replacement.append(ident)
 ledger=OUT/'replacement-ids.json';ids=set(json.loads(ledger.read_text()));ids.update(replacement);ledger.write_text(json.dumps(sorted(ids)))
 return dict(key=KEY,name='Luxor exterior',center=[-250,0,2240],bounds=[-545,2050,-70,2440],building='luxor',structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
