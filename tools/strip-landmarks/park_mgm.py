"""Park MGM mapped exterior: Earth 2022 and official Marriott/MGM photographs.
Retains public-arrival collision, doors and interiors; all additions are architecture.
"""
from common import *
from forum_shops import facade_frame
KEY='park'
def exterior(B):
 B.property='park-exterior';B.detail=0
 tower=footprint('way/27831695');podium=footprint('way/115080290')
 B.source='tower/park-mgm'
 B.shell(tower,13,110,'park-white',solid=False)
 for p in parts(tower):
  ps=list(p.exterior.coords)
  for a,b in zip(ps,ps[1:]):
   F,L,nx,nz=facade_frame(B,a,b,p,.09)
   if L<1:continue
   # Broad hotel room elevations are pale with punched windows. End faces and
   # projecting corner caps retain the muted olive green identity.
   cap=L<24 and Point((a[0]+b[0])/2,(a[1]+b[1])/2).distance(tower.centroid)>55
   F.box('park-green' if cap else 'park-white',(L/2,61.5,-.03),(L,97,.12))
   if not cap:
    count=max(1,int(L/3.25));pitch=L/count
    for x in np.arange(pitch/2,L,pitch):
     for y in np.arange(15.0,102,3.05):
      F.box('park-shadow',(x,y,-.13),(1.80,1.86,.045))
      F.box('park-window',(x,y+.05,-.16),(1.50,1.59,.032))
     B.detail=1
     F.box('park-trim',(x+pitch*.5,59,-.12),(.075,88,.05))
     B.detail=0
   else:
    for y in np.arange(16,106,3.05):F.box('park-joint',(L/2,y,-.13),(L,.018,.025))
   F.box('park-green',(L/2,106.5,-.14),(L,7,.12))
   for y in [102.9,109.4,110.0]:F.box('park-trim',(L/2,y,-.22),(L+.12,.22,.24))
   if L>40 and nx>.1:F.text('PARK MGM',(L/2,106,-.29),2.15,'ph-letter')
 B.planar('ph-roof',tower,110.08)
 B.source='park-podium-refined'
 cfg=next(v for v in json.load(open('build/strip-landmarks/next-plan.json')) if v['key']==KEY)
 fx,fz,yaw=cfg['frame'];entry=Frame(B,fx,fz,yaw)
 holes=[dict(p=entry.p(0,0,0),yaw=yaw,width=cfg['width']-1,height=cfg['height']-.5)]
 gallery=unary_union([LineString(c['points']).buffer(2.45,cap_style=2,join_style=2) for c in cfg['connections']])
 # Existing guest core access also stays open.
 plan=next(p for p in json.load(open('build/highrises/plan.json')) if p['key']=='park-mgm')
 for t in plan['towers']:
  a,b,c,d=t['linear'];ox,oy,oz=t['origin'];front=t['lobbyFront'];holes.append(dict(p=[ox+b*front,oy,oz+d*front],yaw=math.atan2(b,d),width=5,height=4.8))
 mask=unary_union([gallery,*[Frame(B,o['p'][0],o['p'][2],o['yaw']).poly([(-o['width']/2-.3,-2),(o['width']/2+.3,-2),(o['width']/2+.3,2),(-o['width']/2-.3,2)]) for o in holes]])
 B.shell(podium,.12,11,'park-stone',holes,roof=False,solid=False,interior=(gallery,5.45))
 B.planar('park-membrane-paint',podium.difference(tower),11.08)
 for p in parts(podium):
  ps=list(p.exterior.coords)
  for a,b in zip(ps,ps[1:]):
   F,L,nx,nz=facade_frame(B,a,b,p,.26)
   if L<.4:continue
   mx,mz=(a[0]+b[0])/2,(a[1]+b[1])/2
   theatre=mx< -110 and mz>1335
   street=mx> -105 or theatre
   if street:
    # Trim and glazing stop at the existing public portal; no slab across it.
    line=LineString([a,b]).difference(mask)
    for seg in list(line.geoms) if hasattr(line,'geoms') else [line]:
     if seg.geom_type!='LineString' or seg.length<.2:continue
     G,W,_,_=facade_frame(B,seg.coords[0],seg.coords[-1],p,.28)
     G.box('park-window',(W/2,5.0,-.03),(W,9.5,.05))
     for y in [0.45,4.5,9.5,10.8]:G.box('steel',(W/2,y,-.13),(W,.20,.18))
     for x in np.arange(.15,W,1.5):G.box('steel',(x,5,-.14),(.075,9.5,.18))
    if theatre:
     # Deep pale fascia over the bowed glass lobby; mapped curved perimeter.
     F.box('park-white',(L/2,13.0,-.36),(L+.30,4.3,.8))
     F.box('park-trim',(L/2,15.1,-.5),(L+.32,.18,1.05))
   else:
    B.detail=1
    for y in [1,3,5,7,9]:F.box('park-joint',(L/2,y,-.06),(L,.025,.03))
    for x in np.arange(1,L,5):F.box('park-joint',(x,5.5,-.06),(.025,10.5,.03))
    B.detail=0
   F.box('park-trim',(L/2,11.15,-.05),(L,.25,.45))
 theatreRoof=podium.intersection(box(-260,1298,-109,1400))
 B.shell(theatreRoof,11.08,15.19,'park-white',roof=False,solid=False)
 B.planar('park-theatre-paint',theatreRoof,15.21)
 # Mechanical rooftop: raised screens grouped around service plant, not a tile grid.
 for x,z,w,d in [(-140,1245,22,12),(-205,1227,17,11),(-177,1314,24,14),(-105,1260,12,9)]:
  q=box(x-w/2,z-d/2,x+w/2,z+d/2)
  if not podium.covers(q) or tower.intersects(q):continue
  B.shell(q,11.1,13.0,'ph-metal',roof=False,solid=False)
  for xx in np.arange(x-w/2+2,x+w/2-1,4):B.box('ph-roof',(xx,12,z),(2.5,1.7,d-2))
 # Smaller rooftop ventilation units follow the exposed roof, avoiding tower,
 # theatre and the existing arrival roof; seeded placement stays reproducible.
 rng=random.Random(412)
 for i in range(48):
  x=rng.uniform(-295,-67);z=rng.uniform(1210,1350)
  q=box(x-1.4,z-1,x+1.4,z+1)
  if not podium.buffer(-3).covers(q) or tower.buffer(2).intersects(q) or theatreRoof.intersects(q):continue
  B.box('ph-metal',(x,11.54,z),(2.8,.85,2))
  B.lathe('ph-black',(x,z),[(11.98,.62),(12.04,.62)],16)
 from park_eataly import exterior as eataly_exterior
 eataly_exterior(B)
 # The small CVS parcel north of the resort has its own stepped stone storefront.
 B.source='podium/cvs-strip';p=footprint('way/133885466')
 for poly in parts(p):
  ps=list(poly.exterior.coords)
  for a,b in zip(ps,ps[1:]):
   F,L,nx,nz=facade_frame(B,a,b,p,.24)
   if L<.3:continue
   F.box('park-stone',(L/2,3,-.03),(L,6,.12))
   for y in [.25,4.4,5.7,6.25]:F.box('ivory',(L/2,y,-.13),(L,.21,.22))
   if nx>.3:
    for x in np.arange(1,L-1,3.7):
     F.box('park-window',(x,2.05,-.15),(3.10,3.3,.03))
     for dx in [-1.63,1.63]:F.box('ivory',(x+dx,2.4,-.22),(.20,4.5,.3))
    F.text('CVS/pharmacy',(L/2,5.0,-.31),.82,'ph-red')
   else:
    for x in np.arange(1,L,3.4):F.box('park-joint',(x,3,-.12),(.025,5.4,.02))
 B.planar('ph-roof',p,6.32)
 for x,z in [(-55,1143),(-55,1155),(-65,1151)]:
  B.box('ph-metal',(x,6.82,z),(3.4,1,2.2));B.box('ph-black',(x,7.36,z),(3.1,.06,1.9))
 # Park's slender Strip marquee, on the south side of the CVS access lane.
 F=Frame(B,-50,1190,-math.pi/2,y=.24)
 F.box('park-green',(0,17,0),(8,34,1.8))
 F.box('mgm-screen',(0,16,-.96),(6.8,25,.07))
 F.text('PARK MGM',(0,31.4,-1.04),.75,'ph-letter')
