"""The missing Forum Shops exterior, in mapped metres (no legacy-site transform).

OSM way/34068416 owns the connected plan. Simon's 2021 Terrace Level plan
corroborates its stepped east/west organization. Heights and Roman frontage
details are photograph estimates, not surveyed construction dimensions.
No public interior is invented or replaced by this exterior correction.
"""
from common import *

KEY='forumShops'
def facade_frame(B,a,b,shape,offset=.08):
 L=math.dist(a,b);ux,uz=(b[0]-a[0])/L,(b[1]-a[1])/L;nx,nz=-uz,ux
 if shape.contains(Point((a[0]+b[0])/2+nx*.1,(a[1]+b[1])/2+nz*.1)):nx,nz=-nx,-nz
 F=Frame(B,a[0]+nx*offset,a[1]+nz*offset,math.atan2(-nx,-nz),y=0)
 if F.co*ux-F.si*uz<0:F=Frame(B,b[0]+nx*offset,b[1]+nz*offset,F.yaw,y=0)
 return F,L,nx,nz

def arch_panel(F,x,y,z,w,h,mat='forum-glass'):
 r=w/2;spring=y+h-r
 pts=[F.p(x-r,y,z),F.p(x+r,y,z),F.p(x+r,spring,z)]
 pts.extend(F.p(x+r*math.cos(a),spring+r*math.sin(a),z) for a in np.linspace(0,math.pi,21)[1:])
 F.b.face(mat,pts[::-1])
 F.arch(x,z-.13,w,y+h,'forum-limestone',.15,y)

def cornice(B,shape,y):
 for poly in parts(shape):
  ps=list(poly.exterior.coords)
  for a,b in zip(ps,ps[1:]):
   if math.dist(a,b)<.1:continue
   if min(a[0],b[0])>-25 and -392<(a[1]+b[1])/2<-308:continue # entrance owns its cornices
   F,L,_,_=facade_frame(B,a,b,shape,.06)
   for yy,h,d in [(y-.65,.22,.48),(y-.22,.18,.68),(y+.10,.18,.86)]:F.box('forum-limestone',(L/2,yy,-d/2),(L,h,d))

def exterior(B):
 B.property=KEY+'-exterior';B.detail=0
 p=footprint('way/34068416')
 # The survey has stair/column micro-outlines along the east edge. They are not
 # vertical walls through all storeys: let the photographed concave facade own
 # this edge, or the footprint extrusion hides its windows and arches.
 front=[]
 for t in np.linspace(41,9,17):front.append((-8+.012*(t-9)**2,-350-t))
 front.append((-8,-341))
 for t in np.linspace(9,41,17)[1:]:front.append((-8+.004*(t-9)**2,-350+t))
 entrance_plan=Polygon([(-35,-391),*front,(-35,-309)])
 p=p.difference(box(-35,-391,30,-309)).union(entrance_plan).buffer(0)
 # Nested roof footprints prevent stacked roofs or duplicate coincident faces.
 mid=p.intersection(box(-335,-430,30,-220))
 high=p.intersection(box(-100,-422,30,-288))
 # Earth top-down: the atrium is a cross with a rounded western apse, not
 # the old rectangular extrusion. Fit remains approximate to the mapped shell.
 crown=unary_union([box(-62,-361,-8,-341),box(-47,-378,-25,-324),Point(-62,-351).buffer(10,resolution=48)]).intersection(high)
 dome_center=(-36,-351);dome_r=7.5;dome_base=32.55;dome_rise=4.05
 tiers=[(p,.24,12.8,mid),(mid,12.8,16.8,high),(high,16.8,24.4,crown),(crown,24.4,32,None)]
 entrance=dict(p=[-9,.24,-350],yaw=-math.pi/2,width=17.5,height=27.2)
 for idx,(shape,lo,hi,nextshape) in enumerate(tiers):
  B.source='mall-shell-'+str(idx)
  B.shell(shape,lo,hi,'forum-limestone',openings=[entrance],roof=False,solid=True)
  roof=shape.difference(nextshape) if nextshape is not None else shape
  if idx==3:roof=roof.difference(Point(*dome_center).buffer(dome_r,resolution=48))
  B.planar('forum-flat-roof',roof,hi,True)
  # Exposed parapets and the roof's actual inward ledge.
  B.shell(shape,hi,hi+.75,'forum-limestone',openings=[entrance],roof=False,solid=False)
  rim=shape.difference(shape.buffer(-.42))
  if nextshape is not None:rim=rim.difference(nextshape.buffer(.01))
  B.planar('forum-limestone',rim,hi+.75)
  B.detail=1;cornice(B,shape,hi+.72)
  # Separate roofing panels and service equipment belong to this roof tier only.
  inset=roof.buffer(-4.5)
  for x in np.arange(p.bounds[0]+9,p.bounds[2],19):
   for z in np.arange(p.bounds[1]+10,p.bounds[3],19):
    if not inset.contains(Point(x,z)):continue
    if (round(x)*7+round(z)*11)%5==0 and inset.contains(Point(x,z).buffer(4)):
     B.box('forum-service',(x,hi+.82,z),(3.8,1.5,2.8))
     B.box('forum-shadow',(x,hi+1.59,z),(3.5,.07,2.5))
     for t in [-.85,.85]:
      B.lathe('forum-service',(x+t,z),[(hi+1.61,.65),(hi+1.69,.65)],16)
      B.lathe('forum-shadow',(x+t,z),[(hi+1.70,.55),(hi+1.71,.55)],16)
  B.detail=0
 # A segmented glazed skylight sits over the atrium. Glass panels share one
 # batched material; fine metal ribs are geometry only, without extra colliders.
 B.source='forum-atrium-skylight';B.detail=0
 cx,cz=dome_center
 B.lathe('forum-limestone',(cx,cz),[(32,dome_r+.38),(32.28,dome_r+.38),(32.45,dome_r+.16),(dome_base,dome_r+.16)],96)
 profile=[(dome_base+dome_rise*math.sin(t),dome_r*math.cos(t)) for t in np.linspace(0,math.pi/2,17)[:-1]]
 B.lathe('forum-skylight',(cx,cz),profile,96)
 # A single apex fan avoids zero-area pole triangles.
 y,r=profile[-1]
 for j in range(96):
  a=j*math.tau/96;b=(j+1)*math.tau/96
  B.upface('forum-skylight',[(cx+r*math.cos(a),y,cz+r*math.sin(a)),(cx+r*math.cos(b),y,cz+r*math.sin(b)),(cx,dome_base+dome_rise,cz)])
 B.detail=1
 for j in range(24):
  a=j*math.tau/24
  B.path('forum-roof-trim',[(cx+(dome_r+.045)*math.cos(t)*math.cos(a),dome_base+(dome_rise+.045)*math.sin(t),cz+(dome_r+.045)*math.cos(t)*math.sin(a)) for t in np.linspace(0,math.pi/2,25)],.035,6)
 for t in [.18,.38,.60,.84,1.10]:
  r=(dome_r+.045)*math.cos(t);yy=dome_base+(dome_rise+.045)*math.sin(t)
  B.path('forum-roof-trim',[(cx+r*math.cos(a),yy,cz+r*math.sin(a)) for a in np.linspace(0,math.tau,97)],.035,6)
 B.detail=0
 # Massive perimeter walls are articulated with set-back blind panels, engaged
 # piers, rustication and relief bands, not rows of hotel-room windows.
 B.source='mall-perimeter';B.detail=1
 for poly in parts(p.simplify(.25,preserve_topology=True)):
  ps=list(poly.exterior.coords)
  for a,b in zip(ps,ps[1:]):
   if math.dist(a,b)<4:continue
   F,L,nx,nz=facade_frame(B,a,b,p)
   midpt=Point((a[0]+b[0])/2,(a[1]+b[1])/2)
   h=24.4 if midpt.x>-100 else 16.8 if midpt.x>-335 else 12.8
   if midpt.x>-25:continue # curved public entrance owns this street face
   step=L/max(1,round(L/8.5));n=round(L/step)
   F.box('forum-plinth',(L/2,1.15,-.08),(L,1.8,.32))
   for yy in [3.1,8.5,h-.9]:F.box('forum-limestone',(L/2,yy,-.2),(L,.32,.54))
   for j in range(n):
    x=(j+.5)*step;ww=max(1.1,step-1.6)
    F.box('forum-shadow',(x,5.8,-.04),(ww,4.5,.07))
    F.box('forum-panel',(x,5.8,-.11),(ww-.30,4.2,.06))
    for xx in [x-step/2+.28,x+step/2-.28]:
     F.box('forum-limestone',(xx,5.65,-.23),(.55,8.8,.55))
     F.box('forum-limestone',(xx,9.8,-.32),(.86,.30,.72))
    if h>18:
     F.box('forum-glass',(x,17.8,-.10),(ww,3.9,.08))
     for yy in [15.7,19.9]:F.box('forum-limestone',(x,yy,-.24),(ww+.55,.26,.55))
     F.box('forum-bronze',(x,17.8,-.19),(.08,3.9,.10))
   for yy in np.arange(2.4,3,.38):F.box('forum-joint',(L/2,yy,-.27),(L,.016,.022))
 B.detail=0
 # Concave two-storey entrance wings. The recess and projecting end piers are
 # photographed features; registration stays within the mapped Strip setback.
 B.source='forum-strip-front'
 for side in [-1,1]:
  def point(t):return(-8+(0.012 if side<0 else .004)*(t-9)**2,-350+side*t)
  for j in range(5):
   t0=9+j*6.4;t1=t0+6.4;a,b=point(t0),point(t1)
   # Force an east-facing frame regardless of path winding.
   L=math.dist(a,b);ux,uz=(b[0]-a[0])/L,(b[1]-a[1])/L
   if uz<0:a,b=b,a;ux,uz=-ux,-uz
   F=Frame(B,a[0],a[1],math.atan2(-uz,ux),y=0)
   F.box('forum-limestone',(L/2,11.55,.42),(L,22.62,.82))
   F.box('forum-plinth',(L/2,1,.02),(L,1.52,1.12))
   for y,h,d in [(3.4,.28,1.2),(11.8,.62,1.30),(12.4,.2,1.5),(22.6,.48,1.5),(23.1,.28,1.8)]:F.box('forum-limestone',(L/2,y,-.16),(L,h,d))
   arch_panel(F,L/2,1.8,-.07,3.8,7.2)
   F.box('forum-glass',(L/2,17.7,-.05),(L-1.15,5.1,.06))
   for y in [15,20.4]:F.box('forum-limestone',(L/2,y,-.22),(L-.8,.23,.58))
   for x in [.4,L-.4]:
    F.box('forum-limestone',(x,17.7,-.22),(.22,5.1,.55))
    F.box('forum-limestone',(x,6.1,-.24),(.50,10.3,.8))
    F.box('forum-limestone',(x,11.1,-.34),(.85,.4,1))
   F.box('forum-bronze',(L/2,17.7,-.12),(.09,5.1,.10))
   F.box('forum-bronze',(L/2,17.7,-.12),(L-1.3,.09,.10))
   B.detail=1
   for x in np.arange(.18,L,.50):F.box('forum-limestone',(x,22.24,-.62),(.22,.38,.44))
   for y in np.arange(1.1,11,.65):
    for x in [.4,L-.4]:F.box('forum-joint',(x,y,-.65),(.5,.018,.022))
   # Relief panels beneath the upper window sill, warm stone in the photo.
   F.box('forum-relief',(L/2,13.8,-.26),(L-1.9,1.15,.18))
   B.detail=0
 # Tall central glazed arch and layered stone archivolts, actual geometry.
 F=Frame(B,-7.9,-350,-math.pi/2,y=0)
 arch_panel(F,0,.24,-.06,17,29.0)
 # Stone spandrels close the space above the curved glazing. A rectangular
 # opening in the mapped shell alone leaves triangular sky/black gaps here.
 arch=[(-8.5,.24),(8.5,.24),(8.5,20.74)]+[(8.5*math.cos(a),20.74+8.5*math.sin(a)) for a in np.linspace(0,math.pi,21)[1:]]
 for poly in parts(box(-13.3,.24,13.3,31.15).difference(Polygon(arch))):
  for tri in triangles(poly):
   pts=[F.p(x,y,-.02) for x,y in list(tri.exterior.coords)[:-1]]
   if np.cross(np.subtract(pts[1],pts[0]),np.subtract(pts[2],pts[0]))[0]<0:pts.reverse()
   B.face('forum-limestone',pts)
 for w,dy in [(18,.35),(19,.65),(20,.92)]:F.arch(0,-dy,w,29.45+(w-18)*.18,'forum-limestone',.22,.24)
 for side in [-1,1]:
  x=side*11.2
  F.box('forum-limestone',(x,15.8,.02),(3.1,31.15,1.8))
  for xx in [x-1.2,x+1.2]:F.box('forum-limestone',(xx,16,-1.12),(.26,29,.35))
  F.box('forum-relief',(x,25,-1),(1.6,8.1,.20))
  for yy in [20.6,29.4]:F.box('forum-limestone',(x,yy,-1.1),(2.15,.26,.38))
  for yy in [2.0,14.7,30.8,31.5]:F.box('forum-limestone',(x,yy,-.7),(3.9,.45,2))
 for xx in np.arange(-7.3,7.4,2.45):F.box('forum-bronze',(xx,11.3,-.27),(.10,21.8,.10))
 for yy in [4,8,12,16,20]:F.box('forum-bronze',(0,yy,-.27),(16.7,.11,.10))
 for yy in [1.9,4.1]:F.box('forum-bronze',(0,yy,-.36),(15,.16,.12))
 for xx in [-6,-3,0,3,6]:F.box('forum-bronze',(xx,2.12,-.36),(.11,3.85,.12))
 F.box('forum-limestone',(0,31.4,.04),(26.5,.48,2.3))
 F.box('forum-limestone',(0,31.85,-.15),(27.2,.30,2.7))
 B.detail=1
 for yy,h,d,w in [(30.3,.18,2.35,26.8),(30.6,.24,2.6,27.0),(31.03,.20,2.82,27.4),(32.13,.22,3.1,27.8)]:
  F.box('forum-limestone',(0,yy,-.26),(w,h,d))
 for xx in np.arange(-13.1,13.2,.56):F.box('forum-limestone',(xx,31.1,-1.67),(.24,.32,.34))
 for side in [-1,1]:
  # Layered inset relief fields and oval medallions follow the architect photo.
  for yy in [22.2,24.3,26.4,28.5]:
   F.box('forum-limestone',(side*11.2,yy,-1.16),(1.78,.16,.12))
  F.path('forum-limestone',[(side*11.2+.66*math.cos(t),17.5+1.15*math.sin(t),-1.08) for t in np.linspace(0,math.tau,49)],.105,8)
 B.detail=0
 F.text('THE FORUM SHOPS',(0,20.9,-.65),1.12,'forum-bronze')
 F.text('AT CAESARS PALACE',(0,19.8,-.64),.42,'forum-bronze')
 # Roof skylights follow the shopping spine, kept off raised roof tiers.
 B.source='mall-roof-detail';B.detail=1
 for x,z,w,d,y in [(-414,-348,42,13,12.8),(-245,-347,50,13,16.8),(-137,-362,24,11,16.8),(-61,-378,18,9,24.4)]:
  F=Frame(B,x,z,y=y)
  F.box('forum-limestone',(0,.55,0),(w+1,1.1,d+1))
  B.face('forum-glass',[F.p(-w/2,.85,-d/2),F.p(w/2,.85,-d/2),F.p(w/2,3,0),F.p(-w/2,3,0)])
  B.face('forum-glass',[F.p(-w/2,3,0),F.p(w/2,3,0),F.p(w/2,.85,d/2),F.p(-w/2,.85,d/2)])
  for xx in np.arange(-w/2,w/2+.1,2.5):F.path('forum-roof-trim',[(xx,.9,-d/2),(xx,3.05,0),(xx,.9,d/2)],.07,6)
 B.detail=0
 return dict(key=KEY,name='The Forum Shops at Caesars',center=[p.centroid.x,0,p.centroid.y],bounds=list(p.bounds),structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={'strip':dict(eye=[42,3,-363],target=[-10,16,-350]),'facade-aerial':dict(eye=[174,168,-110],target=[-210,14,-347])})
