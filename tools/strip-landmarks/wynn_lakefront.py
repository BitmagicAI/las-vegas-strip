"""Lake of Dreams: aerial-registered water and open lakefront dining terraces.
Heights estimated; no assertion of surveyed accuracy or navigable restaurant interiors.
"""
from common import *
from forum_shops import facade_frame
KEY='wynnLakefront';IDS=['way/142899192','way/142899188','way/142899193']
def lake_shape():
 # Manual tracing of inspected Google aerial, zoom20, centre36.12630,-115.16730.
 px=[(520,240),(650,180),(720,60),(820,65),(860,165),(900,230),(958,240),(980,350),(922,370),(868,520),(790,510),(720,455),(610,450),(550,430),(535,300)]
 p=Polygon([(512.65+(x-640)*.1206,-1146.60+(z-360)*.1206)for x,z in px]).buffer(1.0).buffer(-1.0)
 terraces=unary_union([footprint(i)for i in IDS[:2]])
 joined=p.union(terraces.buffer(2.2)).union(terraces.convex_hull)
 joined=unary_union([Polygon(q.exterior)for q in parts(joined)])
 return joined.difference(footprint('way/111322055')).difference(terraces)
def exterior(B):
 B.property=KEY+'-exterior';B.source='wynn-lakefront';B.detail=0;W=Frame(B,0,0,y=0)
 lake=lake_shape();south=footprint(IDS[2]).buffer(-.45)
 waters=lake.union(south)
 for p in parts(waters):
  B.planar('wlf_water',p,.42);B.planar('wlf-basin-paint',p,-1.4,True)
  B.shell(p,-1.4,.58,'wlf-coping-stone',roof=False)
  B.planar('wlf-coping-stone',p.buffer(.4).difference(p),.60,True)
 # The southern pool has stepped stone cascades, not an enclosed public building.
 edge=LineString([(507,-1103),(507,-1108),(511,-1113),(518,-1117),(525,-1114)])
 for k in range(5):
  band=edge.buffer(.35+k*.42).difference(edge.buffer(max(0,k*.42-.07)))
  B.planar('wlf-rock-stone',band,.65+k*.29,True)
  B.shell(band,.45,.65+k*.29,'wlf-rock-stone',roof=False)
 # Main waterfall screen on the western shore, height from official45ft description.
 wall=LineString([(492,-1162),(494,-1156),(494.5,-1148),(495,-1140)])
 B.shell(wall.buffer(.8,cap_style=2),.45,14.15,'wlf-waterfall-paint',roof=False)
 B.planar('wlf-coping-stone',wall.buffer(.9,cap_style=2),14.15,True)
 # Dining pergolas follow mapped terrace footprints; circulation is kept down centre.
 routes=[];samples=[]
 for ident in IDS[:2]:
  p=footprint(ident);B.planar('wlf-terrace-stone',p,.70,True);B.shell(p,.1,.70,'wlf-coping-stone',roof=False)
  if ident==IDS[0]:a,b=(541.88,-1186.877),(554.785,-1165.938)
  else:a,b=(551.772,-1137.674),(546.224,-1122.724)
  F,L,nx,nz=facade_frame(B,a,b,footprint('way/111322055'),0);F.y=0
  balcony=p.intersection(F.poly([(.5,-2.6),(L-.5,-2.6),(L-.5,-.2),(.5,-.2)]))
  B.planar('wlf-terrace-stone',balcony,5.90,True);B.shell(balcony,5.65,5.9,'wlf-cream-stucco',roof=False)
  for poly in parts(balcony):
   for aa,bb in zip(list(poly.exterior.coords),list(poly.exterior.coords)[1:]):
    mid=LineString([aa,bb]).interpolate(.5,normalized=True)
    if footprint('way/111322055').distance(mid)<.4:continue
    W.tube('wlf-metal-paint',(aa[0],7,aa[1]),(bb[0],7,bb[1]),.035,6)
    B.face('wlf-rail-glass',[(aa[0],6,aa[1]),(bb[0],6,bb[1]),(bb[0],6.95,bb[1]),(aa[0],6.95,aa[1])],True)
  for xx in np.arange(3,L-1,6):
   pt=F.p(xx,0,-1.4)
   if not balcony.contains(Point(pt[0],pt[2])):continue
   B.tube('wlf-metal-paint',(pt[0],5.9,pt[2]),(pt[0],8.6,pt[2]),.025,6)
   for k in range(8):
    a0=k*math.tau/8;a1=(k+1)*math.tau/8
    B.face('wlf-red-fabric',[(pt[0],8.6,pt[2]),(pt[0]+1.2*math.cos(a0),8.15,pt[2]+1.2*math.sin(a0)),(pt[0]+1.2*math.cos(a1),8.15,pt[2]+1.2*math.sin(a1))])
  # All local negative-w coordinates are outside the building.
  for x in np.arange(1,L,3.5):
   pt=F.p(x,0,-2.4)
   if not p.buffer(-.1).contains(Point(pt[0],pt[2])):continue
   F.lathe('wlf-cream-stucco',x,-2.4,[(.7,.33),(.95,.33),(1.05,.23),(4.45,.20),(4.6,.37),(4.8,.37)],12)
   F.box('wlf-cream-stucco',(x,4.9,-1.6),(.20,.22,3.2))
  F.box('wlf-cream-stucco',(L/2,4.85,-2.4),(L,.23,.23))
  for x in np.arange(.6,L-1,1.4):
   for k in range(8):
    w0=-.35-k*.3;w1=w0-.3
    vs=[F.p(x,4.7-.32*math.sin((abs(w0)-.35)/2.4*math.pi),w0),F.p(x+1.1,4.7-.32*math.sin((abs(w0)-.35)/2.4*math.pi),w0),F.p(x+1.1,4.7-.32*math.sin((abs(w1)-.35)/2.4*math.pi),w1),F.p(x,4.7-.32*math.sin((abs(w1)-.35)/2.4*math.pi),w1)]
    if all(p.buffer(.15).covers(Point(v[0],v[2]))for v in vs):B.face('wlf-fabric-paint',vs)
  # Edge rail stops at parent wall; no collision across restaurant access.
  for aa,bb in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
   line=LineString([aa,bb]);mid=line.interpolate(.5,normalized=True)
   if footprint('way/111322055').distance(mid)<.15:continue
   W.tube('wlf-metal-paint',(aa[0],1.8,aa[1]),(bb[0],1.8,bb[1]),.035,6)
   for t in np.linspace(0,1,max(2,int(line.length/1.5)+1)):
    pt=line.interpolate(t,normalized=True);W.tube('wlf-metal-paint',(pt.x,.7,pt.y),(pt.x,1.8,pt.y),.026,6)
   B.face('wlf-rail-glass',[(aa[0],.8,aa[1]),(bb[0],.8,bb[1]),(bb[0],1.72,bb[1]),(aa[0],1.72,aa[1])],True)
  route=[]
  for t in [.2,.4,.6,.8]:
   pt=F.p(L*t,.7,-1.1)
   if p.buffer(-.45).contains(Point(pt[0],pt[2])):route.append(pt)
  if len(route)>1:
   routes.append(route);routes.append([(v[0],5.9,v[2])for v in route])
  # Tables placed only in the wider lobes, away from walking line.
  for x in np.arange(p.bounds[0]+1,p.bounds[2],3):
   for z in np.arange(p.bounds[1]+1,p.bounds[3],3):
    pt=Point(x,z)
    if not p.buffer(-1).contains(pt)or LineString([(v[0],v[2])for v in route]).distance(pt)<1.3:continue
    B.lathe('wlf-fabric-paint',(x,z),[(1.36,.67),(1.43,.72),(1.48,.72)],16)
    for ang in [0,math.pi]:
     C=Frame(B,x+1.05*math.cos(ang),z+1.05*math.sin(ang),ang,y=.7)
     C.box('wlf-fabric-paint',(0,.48,0),(.55,.12,.55));C.box('wlf-metal-paint',(0,.82,.25),(.56,.55,.06))
     for u in [-.22,.22]:
      for w in [-.22,.22]:C.box('wlf-metal-paint',(u,.22,w),(.035,.44,.035))
  for x in np.arange(p.bounds[0],p.bounds[2],1):
   for z in np.arange(p.bounds[1],p.bounds[3],1):
    if p.buffer(-.2).contains(Point(x,z)):samples.append([float(x),1.05,float(z)])
    if balcony.buffer(-.2).contains(Point(x,z)):samples.append([float(x),6.25,float(z)])
 for p in parts(waters):
  for x in np.arange(p.bounds[0],p.bounds[2],2):
   for z in np.arange(p.bounds[1],p.bounds[3],2):
    if p.buffer(-.5).contains(Point(x,z)):samples.append([float(x),-1.05,float(z)])
 Path('build/city-exteriors/wynn-lakefront-samples.json').write_text(json.dumps(samples));Path('build/city-exteriors/wynn-lakefront-stairs.json').write_text(json.dumps(routes))
 Path('build/city-exteriors/wynn-lakefront-water-mask.json').write_text(json.dumps([list(p.exterior.coords)for p in parts(waters)]))
 return dict(key=KEY,name='Wynn lakefront terraces and water',center=[525,0,-1145],bounds=[490,-1190,562,-1090],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
