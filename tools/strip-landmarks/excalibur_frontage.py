"""Excalibur's remaining castle podium and tram buildings, preserving circulation."""
from common import *
from forum_shops import facade_frame
from building_surfaces import BuildingSurfaces
from luxor_facades import Access
KEY='excaliburFrontage'
def arch_panel(F,x,y,z,w,h,mat):
 r=w/2;spring=y+h-r
 pts=[F.p(x-r,y,z),F.p(x+r,y,z),F.p(x+r,spring,z)]
 pts.extend(F.p(x+r*math.cos(a),spring+r*math.sin(a),z) for a in np.linspace(0,math.pi,13)[1:])
 F.b.face(mat,pts[::-1])
 for dx in [-r-.1,r+.1]:F.box('nyny-white',(x+dx,(y+spring)/2,z-.12),(.2,spring-y,.28))
 for a,b in zip(np.linspace(0,math.pi,13),np.linspace(0,math.pi,13)[1:]):
  pts=[(x+rr*math.cos(t),spring+rr*math.sin(t)) for rr,t in [(r,a),(r,b),(r+.2,b),(r+.2,a)]]
  F.b.face('nyny-white',[F.p(px,py,z-.26) for px,py in pts])
  for rr in [r,r+.2]:F.b.face('nyny-white',[F.p(x+rr*math.cos(t),spring+rr*math.sin(t),zz) for t,zz in [(a,z-.26),(b,z-.26),(b,z+.02),(a,z+.02)]])

def exterior(B):
 B.property=KEY+'-exterior';B.detail=0
 # Mapped central hall was dropped by the old turret-only generator's
 # area>1500 filter. Earth (2022-11-09) shows white curtain walls and a
 # flat crenellated roof connecting the surrounding conical towers.
 # 29m is mapped height, not a measured parapet elevation.
 hall=footprint('way/114870395');B.source='castle-hall/way/114870395'
 B.shell(hall,8.05,27.6,'castle-limestone',roof=False,solid=True)
 B.planar('forum-flat-roof',hall,27.6,True)
 for poly in parts(hall):
  ps=list(poly.exterior.coords)
  for a,b in zip(ps,ps[1:]):
   F,L,_,_=facade_frame(B,a,b,hall,.08)
   if L<.3:continue
   for y,h,d in [(8.4,.45,.5),(19.4,.35,.5),(26.9,.4,.65),(28,.8,.55)]:
    F.box('nyny-white',(L/2,y,0),(L,h,d))
   n=max(1,int(L/2.4))
   for j in range(n):F.box('nyny-white',((j+.5)*L/n,28.65,0),(min(1.2,L/n*.52),.7,.65))
   n=int(L/5.5)
   for j in range(n):
    u=(j+.5)*L/n
    for y in [12,21]:arch_panel(F,u,y,-.06,1.6,3.5,'nyny-window')
    F.box('castle-limestone',(u,11.7,-.14),(2,.3,.55))
 ids=['relation/8086330','way/114977805','way/114977810','way/567108265']
 records=[dict(BYID[i],shape=footprint(i),height=8 if i=='relation/8086330' else BYID[i]['height']) for i in ids]
 towers=[dict(BYID[i],shape=footprint(i)) for i in ['way/114859870','way/114857390']]
 surface=BuildingSurfaces(records+towers);access=Access({'towers':[]})
 gate=LineString([(-57,1736),(-137,1814),(-180,1858)]).buffer(7.15,cap_style=2)
 for r in records:
  p=r['shape'];h=r['height'];ident=r['id'];B.source='podium/'+ident
  for poly in parts(p):
   ps=list(poly.exterior.coords)
   for a,b in zip(ps,ps[1:]):
    F,L,nx,nz=facade_frame(B,a,b,p,.23)
    if L<.2:continue
    line=LineString([a,b]);ux,uz=(b[0]-a[0])/L,(b[1]-a[1])/L
    region=unary_union([Polygon([(line.project(Point(v[0],v[2])),v[1]) for v in tri]) for tri in surface.wall(ident,a,b,0,h,access)])
    for seg in parts(line.intersection(gate),'LineString'):
     ds=[line.project(Point(q)) for q in seg.coords];region=region.difference(box(min(ds),0,max(ds),h+.3))
    def patch(mat,x0,y0,x1,y1,offset=.25):
     for q in parts(region.intersection(box(x0,y0,x1,y1))):
      for tri in triangles(q):B.face(mat,[(a[0]+ux*x+nx*offset,y,a[1]+uz*x+nz*offset) for x,y in list(tri.exterior.coords)[:-1]])
    patch('castle-limestone',0,0,L,h)
    for y in [.5,h-1.2,h-.25]:patch('nyny-white',0,y,L,y+.18,.35)
    count=max(1,int(L/5.5));step=L/count
    for j in range(count):
     u=(j+.5)*step
     # Avoid adding ornament across the existing open entry route.
     world=F.p(u,0,0)
     if gate.buffer(2).contains(Point(world[0],world[2])):continue
     if not region.contains(Point(line.project(Point(world[0],world[2])),min(2,h/2))):continue
     w=min(3.3,step-1.1);height=min(4.2,h-1.1)
     arch_panel(F,u,.65,-.13,w,height,mat='nyny-window')
     F.box('castle-limestone',(u,.6,-.28),(w+.4,.2,.65))
     if h>6:F.box('nyny-white',(u,h-.7,-.15),(.8,.38,.26))
    # Buttresses cast shallow relief, with a broad cap above each group.
    for u in np.arange(.4,L-.3,11):
     world=F.p(u,0,0)
     if gate.buffer(1).contains(Point(world[0],world[2])):continue
     if not region.contains(Point(line.project(Point(world[0],world[2])),h/2)):continue
     F.box('castle-limestone',(u,h/2,-.1),(.6,h,.6))
     F.box('nyny-white',(u,h-.1,-.13),(.88,.28,.82))
   # Do not overlay the existing podium roof: its cutouts belong to legacy geometry.
   if ident!='relation/8086330':B.planar('ph-roof',surface.roof(ident,poly,h),h+.07)
 return dict(key=KEY,name='Excalibur lower facades',center=[-190,0,1870],bounds=[-350,1720,-25,2035],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
