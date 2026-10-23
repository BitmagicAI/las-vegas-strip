"""South arrival: mapped alignments, fitted grades and original sign architecture.
Google Earth screenshots supplied 2026-10-06 establish the visual section, not
survey heights. Keep the known bridge datum, with continuous road-node heights.
"""
import json,math
from pathlib import Path
from common import *
from arrival_trees import tree
from road_splines import sample_road
from ramp_barriers import barrier
from bellagio_garage import GARAGE,ROAD
AREA=box(-222,398,-22,595)
WALK={'footway','path','pedestrian','steps'}
def network():
 roads=[]
 for r in json.load(open('build/geographic-strip/road-network.json'))['roads']:
  line=LineString([(p[0],p[2]) for p in r['points']])
  if r['highway'] in WALK or not line.intersects(AREA):continue
  if r['id'] in [25718282,25718290,25718292,25718294,1234768418,1234768419,1234768421,1002539038]:continue
  if r['highway'] in ['primary','secondary','motorway']:continue
  # Preserve mapped alignments; fit the ramp toe to the ground-level junction.
  ps=[[x,y,z] for x,y,z in r['points']]
  if r['id']==374989475:
   old=ps[0][1];ps=[[x,y+(.4203287950753534)*max(0,1-(x-ps[0][0])/14),z] for x,y,z in ps]
  if r['id']==1234768417:
   ps=[[x,.135,z] for x,y,z in ps]
  if r['id']==25718280:
   start,end=ps[0][1],ps[-1][1]
   ps=[[x,.135+(y-start)/(end-start)*(end-.135),z] for x,y,z in ps]
  ps=sample_road(ps)
  line=LineString([(p[0],p[2]) for p in ps])
  roads.append(dict(r,points=ps,width=max(4.5,r['width']),line=line))
 return roads

def build(b,site,lake,routes):
 b.property='bellagioBlock-exterior';roads=network();mask=AREA.difference(site).difference(lake).difference(GARAGE).difference(ROAD)
 b.source='south-arrival-ground';b.detail=0;b.planar('lake-paving',mask,.02,True)
 # Union equal-grade ribbons into junction surfaces. Elevated network is a
 # separate layer so the lower service road remains open beneath the bridge.
 upper=[r for r in roads if max(p[1] for p in r['points'])>.4]
 lower=[r for r in roads if r not in upper]
 unions=[];height_functions=[];segments=[]
 for layer,rs in [('lower',lower),('upper',upper)]:
  ribbons=unary_union([r['line'].buffer(r['width']/2,join_style=1,cap_style=1) for r in rs])
  # Round tiny union cusps before clipping the site endpoints. Both pavement
  # and guards use this outline, so there is no invisible collision shortcut.
  if layer=='upper':ribbons=ribbons.buffer(-1.2,quad_segs=12).buffer(2.4,quad_segs=12).buffer(-1.2,quad_segs=12)
  poly=ribbons.intersection(mask)
  seg=[]
  for r in rs:
   for a,c in zip(r['points'],r['points'][1:]):seg.append((np.array(a),np.array(c),LineString([(a[0],a[2]),(c[0],c[2])]),r['id']))
  # A continuous spatial field: never switch height ownership to the nearest
  # road. Nearby ramps used to win that switch by centimetres and move a
  # pavement vertex vertically by metres, even with smooth centrelines.
  samples=np.array([p for r in rs for p in r['points']],float)
  anchors=[]
  for r in rs:
   for p in [r['points'][0],r['points'][-1]]:
    if not any(math.dist(p,q)<.01 for q in anchors):anchors.append(p)
  def raw(x,z,samples=samples):
   d=(samples[:,0]-x)**2+(samples[:,2]-z)**2
   w=np.exp(-(d-d.min())/128.)
   return float(np.dot(w,samples[:,1])/w.sum())
  # Smooth compact corrections retain junction/floor landing datums exactly.
  anchors=np.array(anchors);corrections=np.array([p[1]-raw(p[0],p[2]) for p in anchors])
  def elev(x,z,raw=raw,anchors=anchors,corrections=corrections):
   d=np.sqrt((anchors[:,0]-x)**2+(anchors[:,2]-z)**2)
   t=np.maximum(0,1-d/6.)
   w=t**4*(1+4*d/6.)
   return raw(x,z)+float(np.dot(w,corrections))
  unions.append(poly);height_functions.append(elev);segments+=seg
  b.source='south-arrival-'+layer+'-pavement'
  # Subdivide triangulation: grade changes follow source centreline samples,
  # rather than one large diagonal triangle spanning an entire curved ramp.
  x0,z0,x1,z1=poly.bounds
  for x in np.arange(math.floor(x0),x1,1):
   for z in np.arange(math.floor(z0),z1,1):
    # Clip planar grid triangles, not curved-height polygon slivers. The
    # latter can turn nearly collinear boundary vertices into vertical spikes.
    for corners in [[(x,z),(x+1,z),(x+1,z+1)],[(x,z),(x+1,z+1),(x,z+1)]]:
     ys=np.array([elev(xx,zz) for xx,zz in corners])
     plane=np.linalg.solve(np.array([[xx-x,zz-z,1] for xx,zz in corners]),ys)
     for p in parts(poly.intersection(Polygon(corners))):
      for tri in triangles(p):
       if tri.area<1e-9:continue
       b.upface('charcoal',[(xx,float(plane[0]*(xx-x)+plane[1]*(zz-z)+plane[2]),zz) for xx,zz in list(tri.exterior.coords)[:-1]],True)
  # Continuous curb/wall at union boundaries only: no rails across branches.
  b.source='south-arrival-'+layer+'-retaining-walls'
  other=unary_union([r['line'].buffer(r['width']/2+.6) for r in roads if r not in rs])
  for p in parts(poly):
   for ring in [p.exterior,*p.interiors]:
    for a,c in zip(list(ring.coords),list(ring.coords)[1:]):
     count=max(1,math.ceil(math.dist(a,c)/2))
     for i in range(count):
      u=np.array(a)+(np.array(c)-a)*i/count;v=np.array(a)+(np.array(c)-a)*(i+1)/count
      y0,y1=elev(*u),elev(*v);mid=(u+v)/2
      if AREA.boundary.distance(Point(*mid))<.1 or GARAGE.boundary.distance(Point(*mid))<.35:continue
      # Lower crossing retains at least 4.8 m clear headroom; no embankment
      # below the elevated road at the actual underpass.
      crossing=layer=='upper' and other.buffer(1).contains(Point(*mid)) and min(y0,y1)>4
      bottom0,bottom1=(y0-.65,y1-.65) if crossing else (.02,.02)
      b.face('lake-stone',[(u[0],bottom0,u[1]),(v[0],bottom1,v[1]),(v[0],y1,v[1]),(u[0],y0,u[1])],not crossing)
      # Remove curb where roads merge at matching elevation.
      joins=any(r['line'].distance(Point(*mid))<r['width']/2+.8 and abs(min(r['points'],key=lambda p:math.hypot(p[0]-mid[0],p[2]-mid[1]))[1]-(y0+y1)/2)<1 for r in roads if r not in rs)
      if not joins:
       b.tube('lake-stone',(u[0],y0+.12,u[1]),(v[0],y1+.12,v[1]),.17,6)
       if layer=='upper' and min(y0,y1)>1:
        barrier(b,(u[0],y0,u[1]),(v[0],y1,v[1]),material='lake-stone')
        b.tube('ivory',(u[0],y0+.9,u[1]),(v[0],y1+.9,v[1]),.13,6)
  # Underside follows the bridge instead of exposing a single-sided road.
  if layer=='upper':
   bridge=poly.intersection(other.buffer(1.2))
   for p in parts(bridge):
    for tri in triangles(p):
     pts=[(x,elev(x,z)-.65,z) for x,z in list(tri.exterior.coords)[:-1]]
     if min(v[1] for v in pts)>4:b.face('lake-stone',list(reversed(pts)))
 # Lane markings stop before connecting branches, avoiding a starburst at nodes.
 b.source='south-arrival-lane-markings';b.detail=1
 for r in roads:
  if r['width']<9:continue
  line=r['line'];layer=1 if r in upper else 0;h=height_functions[layer]
  for d in np.arange(8,line.length-7,9):
   p=line.interpolate(d);q=line.interpolate(min(d+3,line.length));dx,dz=q.x-p.x,q.y-p.y;le=math.hypot(dx,dz)
   if le<.1 or not mask.covers(p):continue
   nx,nz=-dz/le*.075,dx/le*.075
   b.face('white',[(p.x+nx,h(p.x,p.y)+.018,p.y+nz),(q.x+nx,h(q.x,q.y)+.018,q.y+nz),(q.x-nx,h(q.x,q.y)+.018,q.y-nz),(p.x-nx,h(p.x,p.y)+.018,p.y-nz)])
 # Full crown clearance against architecture and other trees, not just trunk points.
 walk=[(-57,588),(-106,583),(-137,565),(-167,545),(-190,529)]
 protected=unary_union([box(-66,536,-51,548),site,GARAGE,ROAD,LineString(walk).buffer(3),box(-57,581,-35,591),box(-93,582,-87,603),box(-255,424,-202,468)])
 b.source='south-arrival-landscape';b.detail=0
 # Landscaping is a physical raised surface, including the sanctuary area.
 dry=mask.difference(unary_union(unions).buffer(2.3)).buffer(-1).buffer(1)
 planted=[]
 for p in parts(dry):
  if p.area<24:continue
  b.source='south-arrival-landscape';b.shell(p,.02,.51,'lake-earth',roof=False,solid=True);b.planar('sage',p,.51,True)
  x0,z0,x1,z1=p.bounds
  for x in np.arange(x0+3.5,x1,8.5):
   for z in np.arange(z0+3.5,z1,8.5):
    crown=Point(x,z).buffer(4.0)
    if not p.covers(crown) or protected.intersects(crown) or any(math.hypot(x-t['position'][0],z-t['position'][2])<8.0 for t in planted):continue
    planted.append(tree(b,x,z,.51,int(abs(x*113+z*311))))
 Path('build/resort-blocks/bellagio/tree-placement.json').write_text(json.dumps(dict(trees=planted,clearanceRadiusM=4.0,lodDistancesM=[100,240,650],cellSizeM=40),indent=2))
 # Covered pedestrian arcade, with actual bays instead of solid OSM boxes.
 b.source='south-covered-arcade';b.detail=0
 walk=[(-57,588),(-106,583),(-137,565),(-167,545),(-190,529)]
 for a,c in zip(walk,walk[1:]):
  le=math.dist(a,c);yaw=-math.atan2(c[1]-a[1],c[0]-a[0]);y=6.8
  f=Frame(b,(a[0]+c[0])/2,(a[1]+c[1])/2,yaw,y)
  f.box('lake-stone',(0,-.25,0),(le,.5,4.4),True)
  f.box('lake-cream',(0,3.4,0),(le,.4,4.4))
  for side in [-1,1]:
   b.face('lake-terracotta',[f.p(-le/2,3.65,side*2.65),f.p(le/2,3.65,side*2.65),f.p(le/2,4.8,0),f.p(-le/2,4.8,0)])
   f.box('lake-cream',(0,.55,side*2.12),(le,1.1,.18),True)
  for xx in np.linspace(-le/2,le/2,max(2,round(le/4.5)+1)):
   for zz in [-2,2]:f.box('lake-cream',(xx,1.75,zz),(.38,3.5,.38),True)
 # The fitted sign sits on the southern pedestrian strip, clear of road routes.
 b.source='south-entrance-sign';b.detail=0;f=Frame(b,-46,586,0,.135)
 # Hollow base: broad billboard faces run east/west; short west end admits stairs.
 for zz in [-4,4]:f.box('lake-cream',(0,8.5,zz),(21,17,.4),True)
 f.box('lake-cream',(10.3,8.5,0),(.4,17,8),True)
 f.box('lake-cream',(-10.3,13.25,0),(.4,7.5,8),True)
 # Ground and upper short-side openings; return gallery beside ascending flight.
 f.box('lake-stone',(0,-.15,0),(21,.3,8),True)
 stair=Frame(b,-55,584.5,math.pi/2,.135);stair.stairs(0,0,2.3,6.665,16)
 f.box('lake-stone',(8.6,6.515,0),(3.4,.3,7.5),True)
 f.box('lake-stone',(-1.5,6.515,2.3),(17.7,.3,2.4),True)
 Frame(b,-57,588.3,y=6.8).box('lake-stone',(0,-.15,0),(3,.3,3),True)
 f.box('warm',(0,9,3.72),(12,.12,.08))
 routes.append(dict(name='Sign interior stairs to arcade',points=[[-60,.135,584.5],[-55,.135,584.5],[-39,6.8,584.5],[-38,6.8,588.3],[-57,6.8,588.3],[-65,6.8,587.2]]))
 for y,w,d in [(16.8,23,8),(18,21.8,7),(39,20,6.8),(40,21,7)]:f.box('ivory',(0,y,0),(w,.55,d))
 f.box('lake-cream',(0,29,0),(18,22,5.6),True)
 for xx in [-9,9]:f.box('lake-stone',(xx,28,-.3),(1.3,22,6.8))
 for side in [-1,1]:
  zz=side*3.1;f.box('blackiron',(0,28,zz),(15.8,16.8,.18));f.box('darkglass',(0,28,zz+side*.12),(14.8,15.8,.08))
  f.box('lake-gold',(0,18.7,side*3.65),(18,.22,.18))
  for xx in [-5,5]:f.box('darkglass',(xx,10,side*4.25),(8.8,7.2,.12))
 # Tall asymmetric bell-tower and ribbed cupola silhouette.
 f.box('lake-cream',(10,39,0),(5.2,21,5.2),True)
 for y in np.arange(30,46,1.2):f.box('ivory',(10,y,0),(5.35,.12,5.35))
 f.box('ivory',(10,48.6,0),(6,.6,6))
 for xx,zz,yaw in [(10,-2.67,0),(10,2.67,math.pi),(7.33,0,-math.pi/2),(12.67,0,math.pi/2)]:
  g=Frame(b,*[f.p(xx,43,zz)[i] for i in [0,2]],yaw-math.pi/2,f.p(xx,43,zz)[1]);g.box('darkglass',(0,1.8,0),(2.3,3.2,.1));g.arch(0,.12,2.6,3.6,'ivory',.22)
 f.lathe('lake-bronze',10,0,[(49,3.1),(50,2.9),(51.6,1.9),(52.2,.6),(52.6,.2)],24)
 f.text('BELLAGIO',(0,37.8,-3.35),1.5,'blackiron')
 f.text('BELLAGIO',(0,28,-3.28),1.05,'lake-gold');f.text('LAS VEGAS',(0,25.7,-3.28),.52,'ivory')
 f.text('O',( -5,10,-4.4),3.2,'lake-gold');f.text('DINING',(5,10,-4.4),.65,'ivory')
 for x in [-10,-7,7]:f.box('ivory',(x,7,-4.25),(.45,13,.45))
 for x in [-10,10]:f.lathe('lake-terracotta',x,0,[(17.1,3.5),(18.2,2.8)],4)
 # Road route records are separate from walking routes: vehicle headroom audit.
 for r in roads:
  h=height_functions[1 if r in upper else 0]
  r['points']=[[x,h(x,z),z] for x,y,z in r['points']]
 report=dict(estimatedGrades=True,bridgeTopM=6.035,bridgeSlabM=.65,roads=[dict(id=r['id'],width=r['width'],points=r['points']) for r in roads],replacementMask=list(AREA.exterior.coords),sign=dict(position=[-46,.24,586],heightM=52.6,estimatedDimensions=True))
 Path('build/resort-blocks/bellagio/south-arrival-report.json').write_text(json.dumps(report,indent=2))
 return report
