"""Art District Apartments: mapped courtyard, Jan2026 frontage; concealed access estimated."""
from common import *
from forum_shops import facade_frame
from rexford_ellen_courtyard import window,door,rail
from courtyard_525 import palm
KEY='casinoCenter1520';IDS=['relation/9575763'];YAW=-math.atan2(1.525,25.144)
def frame(B):return Frame(B,1785.899,-4093.886,YAW,y=0)
def exterior(B):
 B.property=KEY+'-exterior';B.source='podium/casino-center-1520';B.detail=0;F=frame(B);p=footprint(IDS[0]);court=Polygon(p.interiors[0]);passage=F.poly([(14,7.5),(26,7.5),(26,10.5),(14,10.5)])
 B.shell(p.difference(passage),.18,2.98,'ad-white-stucco',roof=False);B.shell(p,2.98,6.2,'ad-white-stucco',roof=False)
 roof=p.buffer(.36,join_style=2);B.shell(roof,6.2,6.42,'ad-fascia-paint',roof=False);B.planar('ad-roof-paint',roof,6.42,True);B.planar('ad-soffit-paint',roof,6.2)
 for ring in [p.exterior,*p.interiors]:
  inner=ring!=p.exterior
  for a,b in zip(list(ring.coords),list(ring.coords)[1:]):
   G,L,nx,nz=facade_frame(B,a,b,p,0)
   if inner:
    for y in [.18,3.18]:
     for u in np.arange(1.4,L-1,3.8):
      q=G.p(float(u),0,0)
      if y<1 and passage.buffer(.6).contains(Point(q[0],q[2])):continue
      door(G,float(u),y)
      if u+1.5<L-.7:window(G,float(u)+1.45,y+1.5,1.0,.8)
   else:
    for y in [2.12,5.6]:
     for u in np.arange(1.25,L-1,2.7):
      q=G.p(float(u),0,0)
      if y<3 and passage.buffer(1).contains(Point(q[0],q[2])):continue
      window(G,float(u),y,2.05,.55)
    G.box('ad-belt-paint',(L/2,3.65,-.04),(L,.13,.08))
    if L>20:
     for u in [1,L-1]:G.tube('ad-downpipe-paint',(u,.3,-.12),(u,6.2,-.12),.035,8)
 # Inferred upper gallery around the open courtyard; one central stair reaches its west side.
 gal=court.difference(court.buffer(-1.18,join_style=2));landing=F.poly([(10.1,21),(13.5,21),(13.5,22.5),(10.1,22.5)]);gal=gal.union(landing)
 B.shell(gal,2.98,3.18,'re-gallery-concrete',roof=False);B.planar('re-gallery-concrete',gal,3.18,True);B.planar('ad-soffit-paint',gal,2.98)
 for poly in parts(gal):
  for ring in [poly.exterior,*poly.interiors]:
   for a,b in zip(list(ring.coords),list(ring.coords)[1:]):
    mid=Point((a[0]+b[0])/2,(a[1]+b[1])/2)
    if p.distance(mid)<.2:continue
    # Cut a 1.7m opening at the stair's upper landing.
    line=LineString([a,b]).difference(F.poly([(11.1,20.9),(12.9,20.9),(12.9,21.1),(11.1,21.1)]))
    for seg in ([line] if line.geom_type=='LineString' else line.geoms):
     if seg.length>.03:rail(B,tuple(seg.coords[0]),tuple(seg.coords[-1]),3.18)
 q=F.p(12,0,15);S=Frame(B,q[0],q[2],YAW,y=0);S.stairs(0,0,1.4,3,6,y=.18)
 site=F.poly([(-7,-1),(28,-1),(28,42.3),(-7,42.3)]).difference(p).union(passage)
 B.planar('ad-paving-concrete',site,.18,True)
 # Planters clear both the entry passage and the central stair route.
 for w in [12,29.5]:
  bed=F.poly([(11.5,w-.9),(14,w-.9),(14,w+.9),(11.5,w+.9)]);B.planar('ad-gravel',bed,.21)
 for w in np.arange(1,41,2.8):F.box('ad-line-paint',(-3.2,.2,float(w)),(5,.015,.07))
 for u in [4.5,20.8]:
  for w in [4,13,22,32,38]:
   q=F.p(u,0,w)
   if p.buffer(-1.5).contains(Point(q[0],q[2])):
    F.box('ad-service-paint',(u,6.7,w),(1.6,.5,1.4));F.box('ad-vent-paint',(u,6.97,w),(1.3,.04,1.1))
 # Distinctive street sign: projecting angular board on two tapered metal fins.
 G=Frame(B,*[F.p(25.2,0,8.9)[i] for i in [0,2]],yaw=YAW-math.pi/2,y=0)
 for u in [-.7,.7]:G.tube('ad-sign-frame-paint',(u,3.1,-.7),(u*1.2,8.5,-.9),.05,8)
 G.box('ad-sign-paint',(0,7.5,-.95),(5.0,1.8,.18));G.text('ART DISTRICT',(0,7.5,-1.06),.49,'ad-white-letter');G.text('APARTMENTS',(0,7.12,-1.06),.24,'ad-white-letter')
 G.box('ad-entry-frame-paint',(0,2.6,-.06),(2.6,.32,.16));G.text('1520',(0,2.5,-.16),.22,'ad-white-letter')
 for w in [12,29.5]:palm(B,F,12.75,w,7.5)
 for u in [-.7,.7]:
  B.face('ad-sign-frame-paint',[G.p(u-.24,6.5,-.82),G.p(u+.24,9.7,-.82),G.p(u+.55,6.5,-.82)])
 # Preserve the tested shared railing and window materials; hidden guard faces are collision-only.
 for k in list(B.groups):
  if B.groups[k]['material']in ['re-collision','c525-collision']:del B.groups[k]
 samples=[]
 for x in np.arange(p.bounds[0]+.5,p.bounds[2],1.4):
  for z in np.arange(p.bounds[1]+.5,p.bounds[3],1.4):
   if p.buffer(-.3).contains(Point(x,z)):samples.append([float(x),6.95,float(z)])
 Path('build/city-exteriors/casino-center-1520-samples.json').write_text(json.dumps(samples))
 return dict(key=KEY,name='1520 Art District Apartments',center=[1797,0,-4073],bounds=[1776,-4097,1815,-4048],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
