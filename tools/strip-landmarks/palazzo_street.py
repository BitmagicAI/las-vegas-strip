"""Palazzo lower street elevation, Google Earth 2022-11-09 + owner aerial.

Mapped walls and existing entrances remain authoritative. Heights and ornamental
sections are photo estimates. This replaces the generic repeated arch dressing.
"""
from common import *

def decorate(B,shape,h,holes,gallery_mask):
 B.source='palazzo-street-facades';B.detail=0
 mask=unary_union([gallery_mask,*[Point(o['p'][0],o['p'][2]).buffer(o['width']/2+1) for o in holes]])
 for pp in parts(shape):
  for a,b in zip(list(pp.exterior.coords),list(pp.exterior.coords)[1:]):
   L=math.dist(a,b)
   if L<1:continue
   ux,uz=(b[0]-a[0])/L,(b[1]-a[1])/L;nx,nz=-uz,ux
   mx,mz=(a[0]+b[0])/2,(a[1]+b[1])/2
   if pp.contains(Point(mx+nx*.1,mz+nz*.1)):nx,nz=-nx,-nz
   F=Frame(B,mx,mz,math.atan2(-nx,-nz),y=0)
   street=mx<400 and (nx<-.25 or nz<-.5)
   # Cornice stays present in far views. No coplanar overlays on the shell.
   for y,th,depth in [(h-.9,.25,.45),(h-.4,.35,.7),(h+.05,.25,.9)]:
    F.box('ivory',(0,y,-depth/2),(L,th,depth))
   if not street:continue
   count=max(1,round(L/5.8));step=L/count
   for j in range(count):
    x=-L/2+(j+.5)*step;wx,_,wz=F.p(x,0,0)
    if mask.distance(Point(wx,wz))<step*.45:continue
    width=min(3.5,step*.64)
    # Shops have rectangular upper bays with recessed black awnings below;
    # round medallions and pilasters distinguish the Palazzo from palazzi.
    for lo,hi in [(.5,4.1),(5.6,10.2)]:
     F.box('darkglass',(x,(lo+hi)/2,-.09),(width,hi-lo,.10))
     for side in [-1,1]:F.box('ivory',(x+side*(width/2+.13),(lo+hi)/2,-.22),(.22,hi-lo+.35,.35))
     for yy in [lo-.12,hi+.12]:F.box('ivory',(x,yy,-.26),(width+.5,.22,.45))
     for dx in [-width/3,0,width/3]:F.box('bronze',(x+dx,(lo+hi)/2,-.17),(.055,hi-lo,.07))
     F.box('bronze',(x,(lo+hi)/2,-.17),(width,.055,.07))
    B.face('blackiron',[F.p(x-width*.58,4.6,-.3),F.p(x+width*.58,4.6,-.3),F.p(x+width*.58,3.9,-1.45),F.p(x-width*.58,3.9,-1.45)])
    F.box('blackiron',(x,3.8,-1.45),(width*1.16,.2,.08))
    for side in [-1,1]:
     xx=x+side*step*.46
     F.box('sandstone',(xx,6.25,-.22),(.5,12.2,.40))
     F.box('ivory',(xx,.45,-.28),(.72,.55,.55))
     F.box('ivory',(xx,11.9,-.30),(.74,.35,.60))
    F.path('ivory',[(x+.37*math.cos(t),11.25+.37*math.sin(t),-.27) for t in np.linspace(0,math.tau,17)],.08,6)
    B.detail=1
    for yy in np.arange(.9,11.6,.55):
     for side in [-1,1]:F.box('ivory',(x+side*step*.46,yy,-.445),(.5,.025,.025))
    B.detail=0
 # Two roof elements read clearly above the lower street wall. Locations are
 # fitted to surveyed bends; no new occupied floors or hidden interior routes.
 for x,z,r,base,top,roofmat in [(351,-1002,5.2,13.2,22,'sage'),(336,-947,7.3,13.2,18,'palazzo-slate-paint')]:
  T=Frame(B,x,z,y=0)
  T.lathe('ivory',0,0,[(base,r+.5),(base+.35,r+.5),(base+.5,r)],48)
  if top-base>3:
   for k in range(16):
    a=k*math.tau/16;xx,zz=r*math.cos(a),r*math.sin(a)
    U=Frame(B,x+xx,z+zz,-a-math.pi/2,y=0)
    U.box('darkglass',(0,(base+top)/2,0),(r*.31,top-base-.65,.12))
    U.box('ivory',(r*.18,(base+top)/2,-.08),(.26,top-base,.38))
  T.lathe('ivory',0,0,[(top-.15,r+.2),(top+.05,r+.5),(top+.35,r+.5),(top+.5,r+.2)],48)
  profile=[(top+.5+3.0*math.sin(t),max(.08,r*math.cos(t))) for t in np.linspace(0,math.pi/2,13)]
  T.lathe(roofmat,0,0,profile,48)
  for a in np.linspace(0,math.tau,17)[:-1]:
   T.path('bronze',[(rr*math.cos(a),yy+.025,rr*math.sin(a)) for yy,rr in profile],.035,5)
  T.lathe('ivory',0,0,[(top+3.5,.12),(top+3.85,.08)],12)
 B.detail=0

def canopy(B):
 """Mapped southern porte-cochere; open drive under an octagonal skylight."""
 B.source='palazzo-mapped-canopy';B.detail=0
 p=footprint('way/180584267');c=p.centroid
 F=Frame(B,c.x,c.y,math.atan2(28.327,15.295),y=0)
 # The mapped canopy had no drivable floor over its bare-earth footprint.
 # A low stone apron joins the existing 0.135 m paving without coplanar faces.
 B.shell(p,-.12,.08,'sandstone',roof=False,solid=True)
 B.planar('sandstone',p,.08,True)
 octagon=F.poly([(11.8*math.cos(a),11.8*math.sin(a)) for a in np.linspace(math.pi/8,math.tau+math.pi/8,9)[:-1]])
 # Bordered flat roof with open skylight; no overlapping solid roof below glass.
 B.shell(p,9.2,10.1,'ivory',roof=False)
 B.planar('ivory',p.difference(octagon),10.1)
 B.planar('ivory',p.difference(octagon),9.2)
 for x in [-14,14]:
  for z in [-13,13]:
   F.box('sandstone',(x,4.6,z),(1.2,9.2,1.2),True)
   F.box('ivory',(x,.45,z),(1.6,.9,1.6),True)
   F.box('ivory',(x,8.9,z),(1.7,.6,1.7))
 ring=list(octagon.exterior.coords)[:-1]
 top=(c.x,12.5,c.y)
 for a,b in zip(ring,ring[1:]+ring[:1]):
  B.face('skyglass',[(a[0],10.2,a[1]),(b[0],10.2,b[1]),top])
  B.tube('bronze',(a[0],10.25,a[1]),top,.10,8)
  B.tube('bronze',(a[0],10.25,a[1]),(b[0],10.25,b[1]),.14,8)
  for t in [.25,.5,.75]:
   aa=(a[0]*(1-t)+c.x*t,10.25+2.25*t,a[1]*(1-t)+c.y*t)
   bb=(b[0]*(1-t)+c.x*t,10.25+2.25*t,b[1]*(1-t)+c.y*t)
   B.tube('bronze',aa,bb,.045,6)
