"""Original photo-fitted Stirling pool court and Turnberry Place arrival; not a survey."""
from common import *
KEY='turnberryPlaceAmenities'
CX,CZ=1481,-2397
WATER=scale(Point(CX,CZ).buffer(1,resolution=48),14,9.2,origin=(CX,CZ))
DECK=box(1462,-2422,1505,-2372)
def build(B):
 B.property=KEY+'-exterior';B.source='turnberry-place-amenities';B.detail=0
 def lounger(x,z,yaw):
  F=Frame(B,x,z,yaw,y=.6)
  F.box('tpa-seat',(0,.4,0),(.72,.1,1.8));F.box('tpa-frame-paint',(0,.19,0),(.5,.38,1.4),True)
  B.face('tpa-seat',[F.p(-.36,.45,-.4),F.p(.36,.45,-.4),F.p(.36,.9,-.95),F.p(-.36,.9,-.95)])
  for xx in [-.33,.33]:F.path('tpa-frame-paint',[(xx,.42,.85),(xx,.42,-.4),(xx,.88,-.95)],.025,6)
 def umbrella(x,z):
  B.tube('tpa-frame-paint',(x,.3,z),(x,2.7,z),.05,8)
  B.box('tpa-frame-paint',(x,.35,z),(.55,.1,.55),True)
  for j in range(12):
   a=j*math.tau/12;b=(j+1)*math.tau/12
   B.face('tpa-canopy',[(x,3.1,z),(x+1.6*math.cos(a),2.6,z+1.6*math.sin(a)),(x+1.6*math.cos(b),2.6,z+1.6*math.sin(b))])
 def palm(x,z,i):
  h=7+(i%4)*1.1;B.lathe('tpa-bark',(x,z),[(.08,.22),(h,.11)],12);B.box('tpa-bark',(x,h/2,z),(.3,h,.3),True)
  for j in range(12):
   a=j*math.tau/12+i*.6;pts=[]
   for k in range(7):
    t=k/6;r=3.2*t;yy=h+1.4*math.sin(t*math.pi)-1.25*t;w=.33*math.sin(t*math.pi)
    pts.append([(x+r*math.cos(a)-w*math.sin(a),yy,z+r*math.sin(a)+w*math.cos(a)),(x+r*math.cos(a)+w*math.sin(a),yy,z+r*math.sin(a)-w*math.cos(a))])
   for k,(aa,bb) in enumerate(zip(pts,pts[1:])):
    if k==0:B.face('tpa-leaf',[aa[0],bb[1],bb[0]])
    elif k==5:B.face('tpa-leaf',[aa[0],aa[1],bb[0]])
    else:B.face('tpa-leaf',[aa[0],aa[1],bb[1],bb[0]])
 # Raised shallow basin avoids altering the existing mapped ground/clubhouse.
 B.planar('tpa-deck',DECK.difference(WATER.buffer(.45)),.6,True)
 B.planar('tpa-coping',WATER.buffer(.45).difference(WATER),.6,True)
 B.planar('tpa-pool-tile',WATER,.08,True)
 B.shell(WATER,.08,.6,'tpa-pool-tile',roof=False,solid=True)
 B.planar('stirling_pool',WATER,.43)
 # Original compass rose, explicitly supported by the official pool photograph.
 for j in range(16):
  a=j*math.tau/16;length=8.2 if j%2==0 else 4.7
  tip=(CX+length*math.cos(a),.46,CZ+length*.75*math.sin(a))
  l=(CX+2.8*math.cos(a-.23),.46,CZ+2.8*math.sin(a-.23));r=(CX+2.8*math.cos(a+.23),.46,CZ+2.8*math.sin(a+.23))
  B.upface('tpa-compass-paint',[l,tip,(CX,.46,CZ)]);B.upface('tpa-compass-light',[(CX,.46,CZ),tip,r])
 B.planar('tpa-compass-paint',Point(CX,CZ).buffer(1.25).difference(Point(CX,CZ).buffer(1.05)),.439)
 # Broad north/south access ramps, no road or historic clubhouse edits.
 for z,sgn in [(-2372,1),(-2422,-1)]:
  B.upface('tpa-deck',[(1475,.6,z),(1487,.6,z),(1487,.04,z+sgn*4),(1475,.04,z+sgn*4)],True)
 for z in [-2414,-2410,-2406,-2388,-2384,-2380]:
  for x in [1466,1500]:lounger(x,z,math.pi/2 if x<1480 else -math.pi/2)
 for x,z in [(1466,-2417),(1500,-2417),(1466,-2377),(1500,-2377)]:umbrella(x,z)
 palms=[(1463,-2419),(1471,-2420),(1494,-2420),(1503,-2419),(1463,-2374),(1471,-2374),(1494,-2374),(1503,-2374)]
 for i,(x,z) in enumerate(palms):palm(x,z,i)
 # Pool entry handrails; fixture positions inferred, photographed stepped ends retained as motif.
 for z in [CZ-9,CZ+9]:
  for x in [CX-1,CX+1]:B.path('tpa-frame-paint',[(x,.1,z),(x,1.35,z),(x,1.35,z+(2 if z>CZ else -2)),(x,.6,z+(2 if z>CZ else -2))],.045,8)
 # Gatehouse portico across the existing arrival lanes: three open arches.
 gx,gz=1595,-2395
 for z in [gz-18,gz-6,gz+6,gz+18]:
  for x in [gx-2,gx+2]:
   B.box('tpa-stone',(x,2.7,z),(.65,5.4,.65),True)
   B.box('tpa-coping',(x,.3,z),(.95,.6,.95),True)
   B.box('tpa-coping',(x,5.3,z),(1.1,.3,1.1))
 # Elliptical arch spandrels, leaving >=4.8 m clearance at the sides.
 for center in [gz-12,gz,gz+12]:
  pts=[(center-5.7,7.8),(center+5.7,7.8)]
  pts += [(center+5.7*math.cos(a),4.8+1.7*math.sin(a)) for a in np.linspace(0,math.pi,25)]
  poly=Polygon(pts)
  for x in [gx-2.45,gx+2.45]:
   for t in triangles(poly):B.face('tpa-stone',[(x,y,z) for z,y in list(t.exterior.coords)[:-1]],True)
 B.box('tpa-coping',(gx,7.9,gz),(5.3,.35,37.5),True)
 # Low open rooftop balustrade.
 for z in np.arange(gz-18,gz+18,.65):
  for x in [gx-2.5,gx+2.5]:B.box('tpa-coping',(x,8.45,z),(.12,.8,.12))
 for x in [gx-2.5,gx+2.5]:B.box('tpa-coping',(x,8.9,gz),(.2,.16,37))
 B.box('tpa-stone',(gx,10.5,gz),(5,5,5),True)
 B.box('tpa-coping',(gx,13,gz),(5.6,.3,5.6))
 B.box('tpa-stone',(gx,14,gz),(3.3,2,3.3))
 # Dark upper niche and clock on east face; hands/markers are original geometry.
 B.box('tpa-shadow',(gx+1.67,14,gz),(.04,1.5,1.0))
 for j in range(48):
  a=j*math.tau/48;b=(j+1)*math.tau/48
  B.face('tpa-coping',[(gx+2.53,10.7,gz),(gx+2.53,10.7+1.65*math.cos(a),gz+1.65*math.sin(a)),(gx+2.53,10.7+1.65*math.cos(b),gz+1.65*math.sin(b))])
 for j in range(12):
  a=j*math.tau/12;B.tube('tpa-shadow',(gx+2.56,10.7+1.35*math.cos(a),gz+1.35*math.sin(a)),(gx+2.56,10.7+1.5*math.cos(a),gz+1.5*math.sin(a)),.035,6)
 B.tube('tpa-shadow',(gx+2.58,10.7,gz),(gx+2.58,11.8,gz),.05,6);B.tube('tpa-shadow',(gx+2.58,10.7,gz),(gx+2.58,10.3,gz+.7),.05,6)
 for a,b in [((-2,-2),(2,-2)),((2,-2),(2,2)),((2,2),(-2,2)),((-2,2),(-2,-2))]:
  B.upface('tpa-tile',[(gx+a[0],15.1,gz+a[1]),(gx+b[0],15.1,gz+b[1]),(gx,16,gz)])
 for i,(x,z) in enumerate([(1604,gz-23),(1604,gz+23),(1587,gz-24),(1587,gz+24)]):palm(x,z,i+8)
 trees=[(1459,-2422,5),(1504,-2427,5),(1459,-2371,5),(1504,-2367,5),(1591,gz-28,7),(1591,gz+28,7),(1604,gz-30,6),(1604,gz+30,6)]
 Path('build/city-exteriors/turnberry-place-trees.json').write_text(json.dumps(trees))
 routes=[{'name':'pool-north-ramp','points':[[1481,.04,-2368],[1481,.6,-2372],[1481,.6,-2384]]},{'name':'pool-south-ramp','points':[[1481,.04,-2426],[1481,.6,-2422],[1481,.6,-2410]]},{'name':'arrival-north','points':[[1586,0,gz-12],[1605,0,gz-12]]},{'name':'arrival-south','points':[[1586,0,gz+12],[1605,0,gz+12]]}]
 Path('docs/project-records/turnberry-place-amenities/routes.json').write_text(json.dumps(routes,indent=2)+'\n')
 return {'poolCenter':[CX,CZ],'poolRadii':[14,9.2],'deckElevation':.6,'waterElevation':.43,'basinBottom':.08,'gatehouseCenter':[gx,gz],'clockTowerHeight':16,'uncertainty':'Dimensions/elevations photo-fitted. Shallow basin avoids replacing mapped ground. Compass ornament is raised to the water surface because the existing opaque water shader hides floor graphics. Three arches and clock tower are reference-supported; detailed portals and full landscape remain approximate.'}
if __name__=='__main__':
 B=Meshes();d=build(B);B.save_all();Path('docs/project-records/turnberry-place-amenities/geometry.json').write_text(json.dumps(d,indent=2)+'\n');print(sum(len(g['faces'])for g in B.groups.values()),'triangles')
