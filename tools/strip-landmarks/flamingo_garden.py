"""Mapped Flamingo garden structures. Heights/pond edges are documented estimates.
Plans follow OSM footprints and paths; Google aerial/ground photos establish forms.
The retained casino mask is shared with the scoped legacy cut, not a bounding-box wipe.
"""
from common import *
from forum_shops import facade_frame
KEY='flamingoGarden';D=.4
ROTUNDA_IDS=['way/115767967','way/115767969','way/115767971']
CAP_IDS=['way/115767964','way/115767970','way/115767972']
IDS=ROTUNDA_IDS+CAP_IDS+['way/402543931','way/402543939','way/402543938','way/116761280']
MAIN_IDS=['way/116761428','way/310585854','way/116761035']
def main_plan():return unary_union([footprint(i)for i in MAIN_IDS])
def garden_mask():
 return box(110,-125,240,10).difference(main_plan()).union(unary_union([footprint(i).buffer(.06)for i in ROTUNDA_IDS]))
def garden_paths():
 raw=json.loads(Path('build/strip-survey/osm.json').read_text());els=raw['elements']if isinstance(raw,dict)else raw;lines=[]
 for e in els:
  if e.get('type')!='way'or'geometry'not in e or not e.get('tags',{}).get('highway'):continue
  c=[((v['lon']+115.173)*89950,-(v['lat']-36.116)*111319)for v in e['geometry']]
  if len(c)>1 and all(85<x<255 and -130<z<45 for x,z in c):lines.append((e['id'],LineString(c),e.get('tags',{})))
 return lines

def slab(B,p,y,mat='fg-path',th=.16):
 B.planar(mat,p,y,True);B.shell(p,y-th,y,mat,roof=False)

def exterior(B):
 B.property=KEY+'-exterior';B.source='garden/flamingo';B.detail=0
 main=main_plan();mask=garden_mask();buildings=unary_union([footprint(i)for i in ROTUNDA_IDS+['way/402543931','way/402543939','way/402543938']]);garden=mask.difference(buildings)
 lines=garden_paths();paths=unary_union([l.buffer(1.45,join_style=1)for _,l,_ in lines]).intersection(garden)
 # Mapped paths constrain inferred pond edges. Pond shape is an aerial-guided estimate,
 # never a claim of a surveyed wildlife enclosure or a reconstruction of the2025 GO Pool.
 ponds=unary_union([scale(Point(141,-83).buffer(10,32),1.1,.65),scale(Point(140,-53).buffer(10,32),1.0,1.45),scale(Point(194,-64).buffer(13,32),.75,1.1),scale(Point(211,-42).buffer(9,32),.8,1.2)]).intersection(garden.buffer(-1)).difference(paths.buffer(.7)).difference(buildings.buffer(1))
 lawn=garden.difference(paths).difference(ponds.buffer(.35))
 slab(B,lawn,D-.025,'fg-soil-paint');slab(B,paths,D,'fg-path')
 for pond in parts(ponds):
  B.planar('fg-pond_water',pond,D-.3);B.planar('fg-basin-paint',pond,D-.85,True)
  B.shell(pond,D-.85,D-.1,'fg-stone',roof=False)
  B.planar('fg-stone',pond.buffer(.35).difference(pond),D-.02,True)
 # Three full-height glazed rotundas.8m outer roof /10.1m cap estimated from photos.
 # Their northern junction inherits the12.8m existing podium datum; returns seal it.
 routes=[];samples=[]
 for ident,capid in zip(ROTUNDA_IDS,CAP_IDS):
  p=footprint(ident);cap=footprint(capid);B.source='lakefront-rotundas/'+ident;H=8.0
  slab(B,p,D,'fg-floor');slab(B,p,H,'fg-roof-paint',.22)
  B.shell(p,H-.82,H+.1,'fg-white-stucco',roof=False)
  slab(B,p.buffer(.12).difference(p.buffer(-.08)),H+.12,'fg-coping-paint',.08)
  B.shell(cap,H,10.05,'fg-white-stucco',roof=False);slab(B,cap,10.1,'fg-roof-paint',.12)
  slab(B,cap.buffer(.1).difference(cap.buffer(-.06)),10.18,'fg-coping-paint',.08)
  exposed=p.boundary.difference(main.buffer(.04));c=p.centroid
  # South-facing public opening leads to mapped garden paths; no dummy opaque door.
  sy=p.bounds[3];portal=box(c.x-1.5,sy-1, c.x+1.5,sy+1)
  for seg in line_parts(exposed):
   cc=list(seg.coords)
   for a,b in zip(cc,cc[1:]):
    line=LineString([a,b]);L=line.length
    if L<.03:continue
    F,_,_,_=facade_frame(B,a,b,p,0);F.y=0
    for piece in line_parts(line.difference(portal)):
     aa,bb=list(piece.coords)[0],list(piece.coords)[-1]
     B.face('fg-glass',[(aa[0],D,aa[1]),(bb[0],D,bb[1]),(bb[0],H-.82,bb[1]),(aa[0],H-.82,aa[1])],True)
    for u in np.linspace(0,L,max(2,math.ceil(L/1.3)+1)):
     q=line.interpolate(float(u))
     if portal.contains(q):continue
     F.box('fg-frame-paint',(float(u),(D+H-.82)/2,-.035),(.055,H-.82-D,.08))
    for y in [D+.12,3.1,H-.9]:F.box('fg-frame-paint',(L/2,y,-.04),(L,.07,.09))
  # Roof step against retained casino, with no wall at the circulation level.
  for seg in line_parts(p.boundary.intersection(main.buffer(-.03))):
   cc=list(seg.coords)
   for a,b in zip(cc,cc[1:]):B.face('fg-white-stucco',[(a[0],H,a[1]),(b[0],H,b[1]),(b[0],12.8,b[1]),(a[0],12.8,a[1])],True)
  connector=LineString([(c.x,sy-.2),(c.x,sy+3)]).buffer(1.5,cap_style=2)
  slab(B,connector.difference(p),D,'fg-path');routes.append([[c.x,D,sy-4],[c.x,D,sy+2.5]])
  samples.extend([[x,H+.2,z]for x in np.arange(p.bounds[0]+.5,p.bounds[2],1.5)for z in np.arange(p.bounds[1]+.5,p.bounds[3],1.5)if p.buffer(-.2).contains(Point(x,z)) and not cap.buffer(.1).contains(Point(x,z))])
 # Octagonal chapel pavilion, mapped two-part plan with pale radial hip roof.
 B.source='lakefront-pavilions/way/402543931';p=footprint('way/402543931');slab(B,p,D,'fg-floor');c=p.centroid
 B.shell(p,D,3.7,'fg-white-stucco',roof=False,openings=[{'p':[c.x,D,p.bounds[3]],'width':2.4,'height':2.7}])
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  F,L,_,_=facade_frame(B,a,b,p,0);F.y=0
  if L>3 and not (abs((a[1]+b[1])/2-p.bounds[3])<2.5):
   F.box('fg-frame-paint',(L/2,2,-.07),(max(.4,L-1.2),2.5,.12));F.box('fg-glass',(L/2,2,-.15),(max(.3,L-1.4),2.3,.035))
  B.face('fg-roof-paint',[(a[0],3.8,a[1]),(b[0],3.8,b[1]),(c.x,6.9,c.y)],True)
  B.tube('fg-coping-paint',(a[0],3.82,a[1]),(c.x,6.92,c.y),.045,6)
 # Hexagonal garden gazebo is open between columns, not another solid box.
 B.source='lakefront-pavilions/way/402543939';p=footprint('way/402543939');c=p.centroid;slab(B,p,D,'fg-floor')
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  B.box('fg-white-stucco',(a[0],1.95,a[1]),(.18,3.1,.18),True)
  B.face('fg-green-roof-paint',[(a[0],3.55,a[1]),(b[0],3.55,b[1]),(c.x,5.8,c.y)],True)
  B.tube('fg-coping-paint',(a[0],3.57,a[1]),(c.x,5.82,c.y),.045,6)
 # South garden pavilion: mapped L-shaped building, shallow green hipped roof.
 B.source='lakefront-pavilions/way/402543938';p=footprint('way/402543938');slab(B,p,D,'fg-floor');B.shell(p,D,3.5,'fg-tan-stucco',roof=False)
 slab(B,p,3.6,'fg-green-roof-paint');inner=p.buffer(-1.5)
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  F,L,_,_=facade_frame(B,a,b,p,0);F.y=0
  for u in np.arange(1.4,L-1,2.8):
   F.box('fg-frame-paint',(float(u),1.9,-.07),(2.3,2.5,.14));F.box('fg-glass',(float(u),1.9,-.15),(2.1,2.3,.03))
  F.box('fg-wood-paint',(L/2,3.45,-.1),(L,.25,.3))
 if not inner.is_empty:
  slab(B,inner,4.4,'fg-green-roof-paint')
  for q in parts(p.difference(inner)):
   for t in triangles(q):B.upface('fg-green-roof-paint',[(x,3.6+min(1,p.boundary.distance(Point(x,z))/1.5)*.8,z)for x,z in list(t.exterior.coords)[:-1]],True)
 # West mapped part is roof-contained in the23m podium; do not turn levels9 into29m.
 B.source='way/116761280';p=footprint(B.source);slab(B,p.buffer(-.25),23.09,'fg-roof-paint',.04)
 for x,z in [(58,-55),(67,-55),(72,-49)]:
  B.box('fg-equipment-paint',(x,23.6,z),(2.5,1,3.2));B.box('fg-dark-paint',(x,24.11,z),(2.1,.025,2.7))
  for dx in np.arange(-1,1.1,.18):B.box('fg-frame-paint',(x+float(dx),24.14,z),(.045,.04,2.7))
 # Retained legacy escalator had been stretched to70m through the outdoor garden.
 # Restore its14m run inside the casino and keep its6.075m upper-gallery endpoint.
 B.source='garden-gallery-stair';G=Frame(B,195.31,9,0,.075);rise=6;run=14;w=3.0
 B.upface('fg-floor',[G.p(-w/2,0,0),G.p(w/2,0,0),G.p(w/2,rise,run),G.p(-w/2,rise,run)],True)
 slab(B,box(193.7,8.5,196.9,10.2),.075,'fg-floor')
 for k in range(35):
  h=rise/35;dep=run/35;G.box('fg-dark-paint',(0,(k+1)*h-.025,(k+.5)*dep),(w,.05,dep+.003));G.box('fg-dark-paint',(0,(k+.5)*h,k*dep),(w,h,.025))
 for side in [-1,1]:
  x=side*(w/2+.04);G.tube('fg-frame-paint',(x,1.05,0),(x,rise+1.05,run),.04,8)
  B.face('fg-glass',[G.p(x,.1,0),G.p(x,rise+.1,run),G.p(x,rise+1,run),G.p(x,1,0)],True)
 routes.append([[195.31,.075,7],[195.31,.075,9],[195.31,6.075,23],[195.31,6.075,25]])
 # Pooled-tree exporter supplies existing CC0 leaf geometry; keep paths clear.
 rng=random.Random(9031);trees=[]
 for x in np.arange(114,237,6):
  for z in np.arange(-116,7,6):
   q=Point(float(x)+rng.uniform(-1.6,1.6),float(z)+rng.uniform(-1.6,1.6))
   if lawn.buffer(-1.2).contains(q)and q.distance(paths)>2.0 and q.distance(buildings)>2.0 and rng.random()<.5:trees.append([q.x,q.y,rng.uniform(3.2,6.5),rng.random()*math.tau])
 for x,z,h,yaw in trees:B.box('fg-trunk-collision',(x,D+min(h*.3,2)/2,z),(.24,min(h*.3,2),.24),True)
 for key in list(B.groups):
  if B.groups[key]['material']=='fg-trunk-collision':del B.groups[key]
 Path('build/city-exteriors/flamingo-garden-trees.json').write_text(json.dumps(trees))
 # Walk the mapped center route (ground datum, not generic bridge height6m).
 for _,l,tags in lines:
  if garden.buffer(-.5).covers(l)and l.length>4:routes.append([[x,D,z]for x,z in l.coords])
 for q in parts(paths):samples.extend([[x,D+.2,z]for x in np.arange(q.bounds[0]+.3,q.bounds[2],2)for z in np.arange(q.bounds[1]+.3,q.bounds[3],2)if q.buffer(-.15).contains(Point(x,z))])
 Path('build/city-exteriors/flamingo-garden-samples.json').write_text(json.dumps(samples));Path('build/city-exteriors/flamingo-garden-routes.json').write_text(json.dumps(routes))
 return dict(key=KEY,name='Flamingo garden pavilions and rotundas',center=[174,0,-65],bounds=[52,-125,241,26],building='flamingo',structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})

def line_parts(g):
 if g.is_empty:return []
 if g.geom_type=='LineString':return [g]
 return [p for q in getattr(g,'geoms',[])for p in line_parts(q)]
