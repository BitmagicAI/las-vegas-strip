"""Siegel Suites Paradise, five mapped wings and January2026 frontage."""
from common import *
from forum_shops import facade_frame
KEY='siegelParadise';IDS=['way/364846'+str(i) for i in range(561,566)]
def rail(F,a,b,y):
 L=math.dist(a,b)
 for t in np.linspace(0,1,math.ceil(L/.20)+1):
  u=a[0]+(b[0]-a[0])*t;w=a[1]+(b[1]-a[1])*t;F.box('spad-rail-paint',(u,y+.54,w),(.025,1.08,.025))
 for yy in [.12,1.08]:F.tube('spad-rail-paint',(a[0],y+yy,a[1]),(b[0],y+yy,b[1]),.027,6)
 F.b.face('spad-collision',[F.p(a[0],y,a[1]),F.p(b[0],y,b[1]),F.p(b[0],y+1.08,b[1]),F.p(a[0],y+1.08,a[1])],True)
def window(F,u,y):
 F.box('spad-frame-paint',(u,y,-.065),(1.38,1.48,.12));F.box('spad-glass',(u,y,-.14),(1.22,1.32,.04));F.box('spad-frame-paint',(u,y,-.18),(.045,1.32,.03));F.box('spad-sill-paint',(u,y-.79,-.12),(1.5,.09,.25))
 # Narrow white vertical side panels visible on the dark upper floor.
 for x in [u-.79,u+.79]:F.box('spad-frame-paint',(x,y,-.05),(.14,1.75,.06))
def door(F,u,y):
 F.box('spad-frame-paint',(u,y+1.08,-.065),(1.04,2.16,.12));F.box('spad-door-paint',(u,y+1.08,-.14),(.90,2.02,.05));F.box('spad-hardware-paint',(u+.32,y+1.0,-.18),(.04,.17,.04))
def exterior(B):
 B.property=KEY+'-exterior';B.source='podium/siegel-paradise';B.detail=0;ps=[footprint(i) for i in IDS];samples=[];routes=[];W=Frame(B,0,0,y=0)
 for idx,p in enumerate(ps):
  edges=[]
  for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
   G,L,nx,nz=facade_frame(B,a,b,p,0);edges.append((nx,G,L,nz,a,b))
  _,F,L,_,_,_=max(edges,key=lambda e:e[0]);c=L/2
  recess=F.poly([(c-2.4,-.03),(c+2.4,-.03),(c+2.4,4.3),(c-2.4,4.3)])
  body=p.difference(recess)
  B.shell(body,.18,6.35,'spad-yellow-stucco',roof=False);B.shell(body,6.35,9.5,'spad-charcoal-paint',roof=False)
  B.planar('spad-roof-paint',p.buffer(-.12),9.36,True)
  # Thin horizontal floor lines, white windows and lower-wall ventilation grilles.
  for nx,G,ell,nz,a,b in edges:
   front=G is F
   for yy in [3.25,6.35,9.5]:G.box('spad-trim-paint',(ell/2,yy,-.035),(ell,.12,.15))
   n=max(2,round(ell/3.8));spacing=ell/n
   for j in range(n):
    u=(j+.5)*spacing
    if front and abs(u-c)<3.2:continue
    for floor in range(3):
     y=.18+floor*3.1
     if front:
      door(G,u-.7,y);window(G,u+.75,y+1.53)
     else:window(G,u,y+1.53)
   for u in [.6,ell-.6]:G.tube('spad-downpipe-paint',(u,.18,-.13),(u,9.42,-.13),.035,8)
  # Recessed stairs: two half flights per storey, with clear turning landings.
  B.planar('spad-concrete',recess.intersection(p),.18,True)
  for level in range(2):
   y=.18+level*3.1
   F.stairs(c-.85,0,1.45,1.55,2.7,y=y)
   F.box('spad-gallery-concrete',(c,y+1.45,3.4),(3.55,.20,1.4),True)
   q=F.p(c+.85,0,2.7);R=Frame(B,q[0],q[2],F.yaw+math.pi,y=0)
   R.stairs(0,0,1.45,1.55,2.7,y=y+1.55)
   F.box('spad-gallery-concrete',(L/2,y+3.0,-.72),(L,.20,1.44),True)
   rail(F,(0,-1.44),(L,-1.44),y+3.1)
   for u in [0,L]:rail(F,(u,-1.44),(u,0),y+3.1)
   rail(F,(c-1.78,4.10),(c+1.78,4.10),y+1.55)
  for u in [.25,L-.25]:F.box('spad-frame-paint',(u,3.28,-1.2),(.11,6.2,.11),True)
  path=[(c-.85,.18,-.7)]
  for level in range(2):
   y=.18+level*3.1
   path += [(c-.85,y+1.55,3.35),(c+.85,y+1.55,3.35),(c+.85,y+3.1,-.7)]
   if level==0:path += [(c-.85,y+3.1,-.7)]
  path += [(min(L-.8,c+4),6.38,-.7)]
  routes.append([F.p(u,y,w) for u,y,w in path])
  # Roof membrane and sparse vents seen in the aerial.
  minx,minz,maxx,maxz=p.bounds
  for x in np.arange(minx+2,maxx-1,5):
   for z in np.arange(minz+2,maxz-1,7):
    if p.buffer(-1.5).contains(Point(x,z)):
     W.box('spad-service-paint',(float(x),9.63,float(z)),(.65,.5,.7));W.box('spad-vent-paint',(float(x),9.90,float(z)),(.48,.025,.5))
  for x in np.arange(minx+.5,maxx,1.5):
   for z in np.arange(minz+.5,maxz,1.5):
    if p.buffer(-.25).contains(Point(x,z)):samples.append([float(x),10.0,float(z)])
 # Shared courtyard, with a real basin rather than water over a duplicate floor.
 allp=unary_union(ps);site=allp.convex_hull.buffer(2.0,join_style=2);pool=LineString([(1763,-3463),(1760,-3456)]).buffer(1.9,resolution=24)
 court=site.difference(allp).difference(pool)
 B.planar('spad-concrete',court,.18,True)
 B.shell(pool,-1.1,.18,'spad-pool-tile',roof=False);B.planar('spad-pool-tile',pool,-1.1,True);B.planar('spad_pool',pool.buffer(-.02),.06)
 B.planar('spad-coping-paint',pool.buffer(.22).difference(pool),.20,True)
 # Pool perimeter guard follows the basin; a 1.4m break on west allows approach.
 pp=pool.buffer(1.0);coords=list(pp.exterior.coords)
 for a,b in zip(coords,coords[1:]):
  if a[0]<1758.4 and -3460.7<a[1]<-3459.3:continue
  rail(W,a,b,.18)
 # Entry number/sign on roadside small wing; no invented lit signage.
 G=Frame(B,1801,-3492,math.pi/2,y=0);G.box('spad-sign-paint',(0,2.2,0),(3,1.35,.12));G.text('SIEGEL SUITES',(0,2.25,-.08),.28,'spad-white-letter');G.text('PARADISE',(0,1.86,-.08),.23,'spad-white-letter')
 B.groups={k:g for k,g in B.groups.items() if g['material']!='spad-collision'}
 Path('build/city-exteriors/siegel-paradise-samples.json').write_text(json.dumps(samples));Path('build/city-exteriors/siegel-paradise-stairs.json').write_text(json.dumps(routes))
 return dict(key=KEY,name='Siegel Suites Paradise exterior',center=[1778,0,-3476],bounds=list(site.bounds),structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
