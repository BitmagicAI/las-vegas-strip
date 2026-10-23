"""Three distinct small courtyard buildings; January2026 Street View and satellite."""
from common import *
from forum_shops import facade_frame
from courtyard_525 import palm
KEY='santaPaulaCourtyard'
IDS=['way/1236725789','way/1236725788','way/1236725787']
def hip(B,p,y=2.85,rise=1.15):
 # Explicit rotating-edge bounding rectangle avoids GEOS warnings on nearly parallel clipped edges.
 pts=list(p.convex_hull.exterior.coords)[:-1];best=None
 for a,b in zip(pts,pts[1:]+pts[:1]):
  angle=math.atan2(b[1]-a[1],b[0]-a[0]);co,si=math.cos(angle),math.sin(angle)
  uv=[(co*(x-a[0])+si*(z-a[1]),-si*(x-a[0])+co*(z-a[1])) for x,z in pts]
  u0,u1=min(q[0] for q in uv),max(q[0] for q in uv);v0,v1=min(q[1] for q in uv),max(q[1] for q in uv);area=(u1-u0)*(v1-v0)
  if best is None or area<best[0]:best=(area,[(a[0]+co*u-si*v,a[1]+si*u+co*v) for u,v in [(u0,v0),(u1,v0),(u1,v1),(u0,v1)]])
 r=best[1]
 lengths=[math.dist(r[i],r[(i+1)%4]) for i in range(4)];i=max(range(4),key=lambda j:lengths[j]);a=r[i];b=r[(i+1)%4]
 yaw=-math.atan2(b[1]-a[1],b[0]-a[0]);G=Frame(B,a[0],a[1],yaw=yaw,y=0)
 co,si=math.cos(yaw),math.sin(yaw);coords=[(co*(x-a[0])-si*(z-a[1]),si*(x-a[0])+co*(z-a[1])) for x,z in r]
 u0=min(q[0] for q in coords)-.3;u1=max(q[0] for q in coords)+.3;w0=min(q[1] for q in coords)-.3;w1=max(q[1] for q in coords)+.3;d=(w1-w0)/2
 ridgea=(u0+d,y+rise,(w0+w1)/2);ridgeb=(u1-d,y+rise,(w0+w1)/2)
 faces=[[(u0,y,w0),(u1,y,w0),ridgeb,ridgea],[(u1,y,w0),(u1,y,w1),ridgeb],[(u1,y,w1),(u0,y,w1),ridgea,ridgeb],[(u0,y,w1),(u0,y,w0),ridgea]]
 for f in faces:B.upface('spc-roof-paint',[G.p(*q) for q in f])
 for aa,bb in zip([(u0,y,w0),(u1,y,w0),(u1,y,w1),(u0,y,w1)],[(u1,y,w0),(u1,y,w1),(u0,y,w1),(u0,y,w0)]):G.tube('spc-fascia-paint',aa,bb,.09,4)
def rail(B,a,b,y=.15,h=1.3,white=False):
 G=Frame(B,a[0],a[1],yaw=-math.atan2(b[1]-a[1],b[0]-a[0]),y=0);L=math.dist(a,b);mat='spc-white-rail-paint' if white else 'spc-fence-paint'
 for u in np.arange(0,L,.16):G.box(mat,(float(u),y+h/2,0),(.027,h,.027))
 for yy in [y+.1,y+h]:G.box(mat,(L/2,yy,0),(L,.045,.045))
 for u in np.arange(0,L,2.4):G.box(mat,(float(u),y+h/2,0),(.065,h+.1,.065))
 B.face('spc-collision',[G.p(0,y,0),G.p(L,y,0),G.p(L,y+h,0),G.p(0,y+h,0)],True)
def exterior(B):
 B.property=KEY+'-exterior';B.source='podium/courtyard-houses';B.detail=0;W=Frame(B,0,0,y=0);ps=[footprint(i) for i in IDS];allp=unary_union(ps)
 for index,p in enumerate(ps):
  B.shell(p,.12,2.8,'spc-tan-stucco' if index==0 else 'spc-white-stucco',roof=False)
  if index==1:
   for area in [p.intersection(box(1900,-3900,2000,-3806.65)),p.intersection(box(1900,-3806.65,2000,-3750))]:hip(B,area)
  elif index==2:
   # Main angled hip roof and shallower northern extension follow the actual setbacks.
   origin=(1917.7103,-3789.8341);yaw=math.atan2(12.47194,32.0537);G=Frame(B,*origin,yaw=yaw,y=0)
   main=p.intersection(G.poly([(-1,-10.45),(36,-10.45),(36,1),(-1,1)]));annex=p.intersection(G.poly([(-1,-20),(36,-20),(36,-10.45),(-1,-10.45)]))
   hip(B,main)
   for poly in parts(annex):hip(B,poly,y=2.82,rise=.55)
  else:hip(B,p)
  for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
   G,L,nx,nz=facade_frame(B,a,b,p,.02)
   G.box('spc-base-stucco',(L/2,.3,-.04),(L,.35,.08))
   if L<3:continue
   for at in np.arange(1.8,L-1,4.4):
    u=float(at);G.box('spc-frame-paint',(u,1.62,-.085),(1.6,1.25,.16));G.box('spc-glass',(u,1.62,-.18),(1.43,1.1,.03))
    for dx in [-.47,0,.47]:G.box('spc-frame-paint',(u+dx,1.62,-.21),(.025,1.1,.025))
    G.box('spc-frame-paint',(u,1.62,-.21),(1.43,.025,.025));G.box('spc-sill-paint',(u,.96,-.16),(1.73,.09,.26))
   if (nz>.7 and index in [0,2]) or (nx>.7 and index==1):
    u=L*.55;G.box('spc-frame-paint',(u,1.21,-.11),(1.12,2.15,.18));G.box('spc-door-paint',(u,1.2,-.23),(.95,2.04,.04));G.box('spc-handle-paint',(u+.34,1.14,-.27),(.035,.16,.04))
    G.box('spc-step-concrete',(u,.19,-.65),(1.7,.18,1.3),True)
    if index==2 and L>15:
     # White veranda on the south facade; keep a central entry gap.
     G.box('spc-veranda-concrete',(L/2,.15,-1.1),(L,.16,2.2),True)
     G.box('spc-veranda-roof-paint',(L/2,2.55,-1.2),(L,.15,2.4))
     for at in np.arange(.2,L,3.5):G.box('spc-frame-paint',(float(at),1.35,-2.1),(.10,2.4,.10),True)
     for aa,bb in [(0,u-.9),(u+.9,L)]:
      pa,pb=G.p(aa,0,-2.1),G.p(bb,0,-2.1);rail(B,(pa[0],pa[2]),(pb[0],pb[2]),y=.23,h=.85,white=True)
  x,z=p.centroid.x,p.centroid.y
  for dx in [-2,2]:W.box('spc-service-paint',(x+dx,4.08,z),(1.1,.65,1.0));W.box('spc-vent-paint',(x+dx,4.41,z),(.9,.025,.8))
 # Northern shared courtyard bounded by its own office wing and neighboring private yards.
 north=box(1938,-3840,1982,-3819).difference(allp)
 B.planar('spc-courtyard-concrete',north,.11,True)
 for za,zb in [(-3835,-3828),(-3823,-3819)]:rail(B,(1981,za),(1981,zb),h=1.6)
 for a,b in [((1938,-3819),(1975,-3819)),((1975,-3819),(1975,-3833))]:
  dx=b[0]-a[0];dz=b[1]-a[1];L=math.hypot(dx,dz);G=Frame(B,a[0],a[1],yaw=-math.atan2(dz,dx),y=0);G.box('spc-private-fence-paint',(L/2,1,0),(L,1.8,.09),True)
 # Two stepped small houses' side entry and grass court, clipped around their footprints.
 east=box(1951,-3818,1982,-3790).difference(allp)
 B.planar('spc-lawn',east,.10,True)
 B.planar('spc-path-concrete',box(1969,-3818,1972,-3790),.12,True)
 for a,b in [((1981,-3818),(1981,-3798)),((1981,-3795),(1981,-3790)),((1951,-3818),(1975,-3818))]:rail(B,a,b,h=1.7)
 # Angled southern parking apron and white veranda approach; no resident vehicles recreated.
 G=Frame(B,1917.7103,-3789.8341,yaw=math.atan2(12.47194,32.0537),y=0)
 parking=G.poly([(-1,0),(35,0),(35,10.3),(-1,10.3)]).difference(allp)
 B.planar('spc-parking-concrete',parking,.11,True)
 for u in [2,7,12,17,22,27,32]:G.box('spc-joint-paint',(u,.118,6),(.018,.005,8.5))
 for u,h in [(5,9),(13,7),(22,10)]:palm(B,G,u,8.8,h)
 B.groups={k:g for k,g in B.groups.items() if g['material'] not in ['spc-collision','c525-collision']}
 samples=[]
 for x in np.arange(1940,1980,1.3):
  for z in [-3838,-3820]:
   if north.contains(Point(x,z)) and not allp.buffer(.7).contains(Point(x,z)):samples.append([float(x),.11,z])
 for u in np.arange(1,34,1.3):samples.append(G.p(float(u),.11,5))
 Path('build/city-exteriors/santa-paula-courtyard-samples.json').write_text(json.dumps(samples))
 return dict(key=KEY,name='Santa Paula courtyard buildings',center=[1950,0,-3817],bounds=[1909,-3841,1983,-3775],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
