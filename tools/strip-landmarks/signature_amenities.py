"""Three original pool courts aligned to observed satellite basin centers, not surveyed dimensions."""
from common import *
from signature_exterior import TOWERS,LOW
from shapely.geometry import shape
KEY='signatureAmenities';Y=.32

def build(B):
 B.property=KEY+'-exterior';B.source='signature-pool-amenities';B.detail=0
 roads=unary_union([shape(f['geometry']).buffer(.3) for f in json.load(open('build/geographic-strip/surface-layers.geojson'))['features'] if f['properties']['kind'] in ['road','sidewalk']]);occupied=unary_union([footprint(i) for i in TOWERS+LOW]).buffer(.5)
 refs=json.load(open('docs/project-records/signature-amenities/research.json'))['poolCenters'];routes=[];counts=dict(palms=0,cabanas=0,loungers=0,parasols=0)
 access=[]
 for t in next(p for p in json.load(open('build/highrises/plan.json')) if p['key']=='signature')['towers']:
  a,b,c,d=t['linear'];ox,_,oz=t['origin'];f=t['lobbyFront']
  access.append(Polygon([(ox+a*xx+b*zz,oz+c*xx+d*zz) for xx,zz in [(-3,f-12),(3,f-12),(3,-5),(-3,-5)]]))
 access=unary_union(access)
 def palm(x,z,i):
  h=5+i%3;B.lathe('sga-bark',(x,z),[(Y,.21),(Y+h,.12)],10);B.box('sga-bark',(x,Y+h/2,z),(.3,h,.3),True)
  for j in range(10):
   a=j*math.tau/10+i;ps=[]
   for k in range(7):
    t=k/6;r=2.5*t;yy=Y+h+math.sin(t*math.pi)-t;w=.3*math.sin(t*math.pi)
    ps.append([(x+r*math.cos(a)-w*math.sin(a),yy,z+r*math.sin(a)+w*math.cos(a)),(x+r*math.cos(a)+w*math.sin(a),yy,z+r*math.sin(a)-w*math.cos(a))])
   for k,(a,b) in enumerate(zip(ps,ps[1:])):B.face('sga-leaf',[a[0],b[1],b[0]] if k==0 else [a[0],a[1],b[0]] if k==5 else [a[0],a[1],b[1],b[0]])
  B.box('sga-coping',(x,Y+.15,z),(1.6,.3,1.6),True);B.box('sga-soil',(x,Y+.31,z),(1.4,.02,1.4));counts['palms']+=1
 def chair(x,z,yaw):
  F=Frame(B,x,z,yaw,y=Y);F.box('sga-cushion',(0,.4,0),(.7,.12,1.8));F.box('sga-white',(0,.2,0),(.55,.4,1.4),True);B.face('sga-cushion',[F.p(-.35,.46,-.35),F.p(.35,.46,-.35),F.p(.35,.9,-.9),F.p(-.35,.9,-.9)]);counts['loungers']+=1
 for i,r in enumerate(refs):
  x,z,w,l=r['x'],r['z'],r['widthEstimateM'],r['lengthEstimateM'];name=r['name']
  deck=box(x-18,z-25,x+18,z+25).difference(roads).difference(occupied)
  pool=box(x-w/2,z-l/2,x+w/2,z+l/2)
  if i==2:pool=pool.union(box(x-1.7,z+l/2,x+1.7,z+l/2+2))
  spa=box(x-4,z+(17 if i==1 else -16)-1.5,x+4,z+(17 if i==1 else -16)+1.5) if i else Polygon()
  water=pool.union(spa);assert water.intersection(roads.union(occupied)).area<.01
  furnishing=deck.difference(access)
  paving=deck.difference(water)
  B.planar('sga-paving',paving,Y,True);B.planar('signature_pool',water,.25);B.planar('sga-tile',water,.02,True);B.shell(water,.02,Y,'sga-tile',roof=False,solid=True)
  B.planar('sga-coping',water.buffer(.35).difference(water),Y+.025,True)
  for xx in np.arange(x-18,x+18,2):B.planar('sga-joint',box(xx-.012,z-25,xx+.012,z+25).intersection(paving),Y+.003)
  for zz in np.arange(z-25,z+25,2):B.planar('sga-joint',box(x-18,zz-.012,x+18,zz+.012).intersection(paving),Y+.003)
  # Keep rails away from retained building faces and their existing lobby doorways.
  # The broad east-side opening connects the court to retained site circulation.
  for poly in parts(deck):
   for a,b in zip(list(poly.exterior.coords),list(poly.exterior.coords)[1:]):
    line=LineString([a,b]).difference(box(x+8,z-2,x+100,z+2)).difference(occupied.buffer(2)).difference(access);lines=list(line.geoms) if hasattr(line,'geoms') else [line]
    for edge in lines:
     if edge.is_empty or edge.length<.1:continue
     pts=list(edge.coords)
     for aa,bb in zip(pts,pts[1:]):
      B.tube('sga-rail',(aa[0],Y+1.1,aa[1]),(bb[0],Y+1.1,bb[1]),.035,6)
      B.face('sga-rail',[(aa[0],Y+.95,aa[1]),(bb[0],Y+.95,bb[1]),(bb[0],Y+1.1,bb[1]),(aa[0],Y+1.1,aa[1])],True)
     for dist in np.arange(0,edge.length,.5):
      q=edge.interpolate(dist);B.box('sga-rail',(q.x,Y+.55,q.y),(.025,1.1,.025))
  # West cabanas and burgundy parasols are fitted inside retained road/building masks.
  for dz in [-15,-5,5,15]:
   xx,zz=x-14,z+dz
   if not furnishing.contains(box(xx-2.3,zz-2,xx+2.3,zz+2)):continue
   for dx in [-2.1,2.1]:
    for dd in [-1.8,1.8]:B.box('sga-white',(xx+dx,Y+1.35,zz+dd),(.08,2.7,.08),True)
   cs=[(xx-2.3,Y+2.7,zz-2),(xx+2.3,Y+2.7,zz-2),(xx+2.3,Y+2.7,zz+2),(xx-2.3,Y+2.7,zz+2)]
   for a,b in zip(cs,cs[1:]+cs[:1]):B.face('sga-burgundy',[a,b,(xx,Y+3.1,zz)])
   B.box('sga-curtain',(xx-2.1,Y+1.3,zz),(.04,2.6,3.6));chair(xx,zz,-math.pi/2);counts['cabanas']+=1
  for dz in np.arange(-l/2+1,l/2,2.6):
   xx,zz=x-w/2-5,z+dz
   if furnishing.contains(box(xx-1,zz-.5,xx+1,zz+.5)):chair(xx,zz,-math.pi/2)
  for dz in [-12,-6,6,12]:
   xx,zz=x+12,z+dz
   for dx in [-1.2,1.2]:
    if furnishing.contains(box(xx+dx-.5,zz-1,xx+dx+.5,zz+1)):chair(xx+dx,zz,math.pi/2)
   if furnishing.contains(Point(xx,zz)):
    B.tube('sga-white',(xx,Y,zz),(xx,Y+2.5,zz),.035,6);B.lathe('sga-burgundy',(xx,zz),[(Y+2.1,1.4),(Y+2.55,.04)],8);counts['parasols']+=1
  for j,(dx,dz) in enumerate([(-8,-21),(8,-21),(-8,21),(8,21),(16,-18),(16,18)]):
   if furnishing.contains(box(x+dx-1,z+dz-1,x+dx+1,z+dz+1)):palm(x+dx,z+dz,j)
  for dz in [-l/2+2,l/2-2]:B.path('sga-white',[(x+w/2-1,.02,z+dz),(x+w/2-1,1.2,z+dz),(x+w/2+1,1.2,z+dz),(x+w/2+1,Y,z+dz)],.04,8)
  for side,xx in [('west',x-w/2-2),('east',x+w/2+2)]:routes.append(dict(name=name+'-'+side,points=[[xx,Y,z-l/2-2],[xx,Y,z+l/2+3.3]]))
  routes.append(dict(name=name+'-gate',points=[[x+20,Y,z],[x+w/2+2,Y,z]]))
  routes.append(dict(name=name+'-south',points=[[x-w/2-2,Y,z+l/2+3.3],[x+w/2+2,Y,z+l/2+3.3]]))
 Path('docs/project-records/signature-amenities/routes.json').write_text(json.dumps(routes,indent=2)+'\n')
 return dict(**counts,pools=3,spas=2,uncertainty='Satellite-selected centers; basin sizes, spa depths, furniture density, deck boundaries and planting inferred. Fire pits, interior door links and exact street boundary masonry remain deferred.')
if __name__=='__main__':
 B=Meshes();d=build(B);B.save_all();d['triangles']=sum(len(g['faces']) for g in B.groups.values());Path('docs/project-records/signature-amenities/geometry.json').write_text(json.dumps(d,indent=2)+'\n');print(d)
