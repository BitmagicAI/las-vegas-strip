"""Paris arrival correction from creator's close aerial and original design account.
Metres, Y up. Ornament is independently modeled, not extracted photogrammetry.
The forecourt is a real exterior void in both the new and retained casino shells.
"""
from common import *
from paris_facades import build as build_parisian_facades
CX,CZ=126.8,482.0
R=46.2
LOUVRE_START=math.pi+.72

def sector(r0,r1,lo=math.pi,hi=math.tau,n=96):
 return Polygon([(CX+r1*math.cos(a),CZ+r1*math.sin(a)) for a in np.linspace(lo,hi,n+1)]+[(CX+r0*math.cos(a),CZ+r0*math.sin(a)) for a in np.linspace(hi,lo,n+1)])
def arrival_void():
 # Includes the central motor court all the way to its street-facing mouth.
 return Point(CX,CZ).buffer(R+.05,quad_segs=32).intersection(box(65,420,190,523))
def build(c):
 b,F,source,slab,col,rail,tree,archbay,mansard,G=[c[k] for k in ['b','F','source','slab','col','rail','tree','archbay','mansard','G']]
 def p(a,r,y):return(CX+r*math.cos(a),y,CZ+r*math.sin(a))
 operaMask=box(74.5,445.7,104.3,475.8).union(Point(74.8,466).buffer(7))
 def band(r,y,w=.2,h=.18,mat='paris-cream',lo=LOUVRE_START,hi=math.tau):
  footprint=sector(r-w/2,r+w/2,lo,hi).difference(operaMask)
  if y<4.8:footprint=footprint.difference(box(CX-3,CZ-R-1,CX+3,CZ-R+1))
  b.shell(footprint,y,y+h,mat,solid=False)
 def framed(f,x,y,z,w,h,arched=False):
  # A dark inset with stone reveal, actual projecting sill and transom geometry.
  f.box('paris-window',(x,y+h/2,z),(w,h,.10))
  for dx in [-w/2-.09,w/2+.09]:f.box('paris-cream',(x+dx,y+h/2,z+.13),(.17,h+.32,.24))
  for yy in [y-.12,y+h+.1]:f.box('paris-cream',(x,yy,z+.18),(w+.5,.18,.38))
  for xx in [-w/4,0,w/4]:f.box('paris-copper',(x+xx,y+h/2,z+.20),(.045,h,.055))
  for yy in [y+h*.42,y+h*.78]:f.box('paris-copper',(x,yy,z+.20),(w,.06,.055))
  if arched:f.path('paris-cream',[(x+math.cos(a)*(w/2+.18),y+h+.12+math.sin(a)*.65,z+.20) for a in np.linspace(0,math.pi,17)],.12)
 def urn(f,x,y,z,s=.65):
  f.lathe('paris-cream',x,z,[(y,.36*s),(y+.2*s,.38*s),(y+.35*s,.21*s),(y+.55*s,.42*s),(y+.95*s,.48*s),(y+1.25*s,.23*s),(y+1.4*s,.31*s)],12)
  b.sphere('paris-cream',f.p(x,y+1.62*s,z),.23*s,10,6)
 def dentils(f,length,y,z,pitch=.64):
  for x in np.arange(-length/2+.25,length/2,pitch):f.box('paris-cream',(x,y,z),(.26,.29,.34))
 def figure(f,x,y,z,s=1,winged=False):
  # Original sculptural masses with draped folds; no collider per ornament.
  f.lathe('paris-relief',x,z,[(y,.40*s),(y+.25*s,.44*s),(y+1.3*s,.24*s),(y+1.75*s,.34*s),(y+1.95*s,.15*s)],10)
  b.sphere('paris-relief',f.p(x,y+2.17*s,z),.23*s,12,8,scale=(.85,1.12,.85))
  for dx in [-1,1]:
   f.tube('paris-relief',(x+dx*.2*s,y+1.7*s,z),(x+dx*.7*s,y+1.2*s,z+.18*s),.11*s,8)
   for k in [-.2,0,.2]:f.path('paris-cream',[(x+k*s,y+.08*s,z+.38*s),(x+k*.6*s,y+1*s,z+.28*s),(x+k*.4*s,y+1.65*s,z+.2*s)],.035*s)
   if winged:
    for j in range(6):f.tube('paris-relief',(x+dx*.1*s,y+1.8*s,z-.1*s),(x+dx*(1.3-.12*j)*s,y+(2.8-.12*j)*s,z-.08*s),.12*s,8)
 # Curved Louvre-inspired entrance block; roof closes the whole annular volume.
 source('arrival-louvre-shell')
 main=dict(p=[CX,G,CZ-R],yaw=0,width=5.6,height=4.8,name='PARIS MAIN ENTRANCE')
 ring=sector(R,R+9,LOUVRE_START).difference(operaMask)
 b.shell(ring,G,17.7,'paris-stone',openings=[main,dict(main,p=[CX,G,CZ-R-9])],roof=False)
 # Facade correction: adjoining Parisian houses, detailed by shared static meshes.
 build_parisian_facades(c,operaMask)
 # Arrival door surround and recognizable first room. No false doors in the recess.
 source('arrival-vestibule')
 for x in [-3.25,3.25]:col(F(CX+x,CZ-R+.36,G),0,0,6,.30)
 F(CX,CZ-R+.65,0).text('PARIS',(0,6.15,0),.65,'paris-gold',back=True)
 slab(box(CX-4.2,CZ-R-11,CX+4.2,CZ-R+.65),G,'marble')
 for x in [CX-4.15,CX+4.15]:b.box('paris-stone',(x,3.8,CZ-R-5),(.18,7.2,10),True)
 b.box('paris-cream',(CX,7.3,CZ-R-5),(8.3,.22,10))
 for z in np.arange(CZ-R-9,CZ-R,2.2):
  for x in [-3.85,3.85]:
   f=F(CX+x,z,G,math.pi/2 if x<0 else -math.pi/2);f.box('paris-gold',(0,3.1,0),(.2,.8,.18));f.box('warm',(0,3.65,.12),(.25,.45,.2))
 for z in [CZ-R-3,CZ-R-7]:F(CX,z,G).chandelier(0,0,6)
 # Curving canopy: small pale-blue glass panes, continuous orthogonal metal grid.
 source('arrival-canopy')
 def height(r):return 7.8+2.6*math.sin((r-29)/16*math.pi)
 angles=np.linspace(math.pi+.40,math.tau,81);radii=np.linspace(29,45,15)
 for a,aa in zip(angles,angles[1:]):
  for rr,ss in zip(radii,radii[1:]):b.face('paris-canopy',[p(a,rr,height(rr)),p(aa,rr,height(rr)),p(aa,ss,height(ss)),p(a,ss,height(ss))])
 for a in angles:b.path('paris-canopy-frame',[p(a,r,height(r)+.045) for r in radii],.055,6)
 for r in radii:b.path('paris-canopy-frame',[p(a,r,height(r)+.045) for a in angles],.045,6)
 for r in [29,45]:
  b.path('paris-canopy-frame',[p(a,r,height(r)) for a in angles],.16)
  band(r,7.48,.30,.30,'paris-canopy-frame',math.pi+.40)
 for i,a in enumerate(np.linspace(math.pi+.44,math.tau-.04,18)):
  if abs(a-1.5*math.pi)<.1:continue
  x,_,z=p(a,29,0);f=F(x,z,G);col(f,0,0,7.5,.19)
  b.box('paris-stone',(x,3.85,z),(.28,7.22,.28),True)
  if i%2==0:
   f.box('paris-iron',(0,7.35,0),(1.3,.12,.8));f.box('warm',(0,7.27,0),(1.0,.045,.52))
 # Driveway has visible asphalt beneath the glazing; the drop-off curb is a real slab.
 source('arrival-forecourt')
 court=Point(CX,CZ).buffer(R,quad_segs=48).intersection(box(70,430,187,519))
 slab(court,G-.10,'paris-asphalt')
 # Drop-off promenade follows facade; gap-free central walk joins the door.
 # Continuous curb ramp: a capsule cannot step onto even this 10cm curb.
 rampEnd=CZ-41.75;rampStart=CZ-39.7
 slab(sector(41.2,R+.1).difference(box(CX-2,rampEnd,CX+2,rampStart)),G,'paris-paving')
 b.face('paris-paving',[(CX-2,G-.10,rampStart),(CX+2,G-.10,rampStart),(CX+2,G,rampEnd),(CX-2,G,rampEnd)],True)
 for r in [41.4,42.1]:band(r,G+.012,.08,.018,'paris-cream')
 for a in np.linspace(math.pi+.1,math.tau-.1,27):
  if abs(a-1.5*math.pi)<.08:continue
  x,_,z=p(a,40.8,0);F(x,z,G).lathe('paris-iron',0,0,[(0,.15),(.08,.18),(.13,.10),(.9,.10),(1.04,.16)],10)
 # End pavilion on the east side: side-street returns, blue roof and tall arched bays.
 source('arrival-east-pavilion')
 east=box(166.8,465.4,183.8,486.5);b.shell(east,G,20.5,'paris-stone',solid=True)
 mansard(east.buffer(.45,join_style=2),20.5,4.5,2.4)
 for x,z,length,yaw in [(175.3,486.65,17,0),(183.95,475.95,21.1,math.pi/2),(166.65,475.95,21.1,-math.pi/2)]:
  f=F(x,z,0,yaw)
  for xx in np.linspace(-length/2+2.6,length/2-2.6,3):
   framed(f,xx,1.0,.01,2.9,5.9,True);framed(f,xx,8.8,.01,2.6,6.5,True);framed(f,xx,17.25,.01,2.5,2.0)
   urn(f,xx,24.4,-2,.65)
  for yy,d in [(7.7,.48),(16.4,.7),(20.1,.65),(20.5,.95)]:f.box('paris-cream',(0,yy,d/2),(length+.4,.28,d))
  dentils(f,length,19.77,.5)
  for xx in np.linspace(-length/2+.35,length/2-.35,4):f.box('paris-cream',(xx,10.2,.19),(.65,19.3,.55))
 # Enclosed Opera-inspired pavilion. Broad copper roof, tall attic/frieze and apse.
 source('arrival-opera-shell')
 opera=box(74.8,446,104,475.5);apse=Point(74.8,466).buffer(6.7,quad_segs=16)
 body=opera.union(apse);b.shell(opera,G,18.6,'paris-stone',roof=False,solid=True)
 b.shell(apse.difference(opera),G,14.5,'paris-stone',solid=True)
 slab(opera,18.6,'paris-cream',False)
 # Large rectangular attic over the main volume, distinct from the adjacent round apse.
 attic=box(79,446.5,103.2,468);b.shell(attic,18.6,23.0,'paris-stone',solid=False)
 for yy,d in [(18.55,.45),(19,.65),(22.2,.4),(22.8,.85),(23.2,1.1)]:b.shell(attic.buffer(d,join_style=2),yy,yy+.24,'paris-cream',solid=False)
 # Low hipped orange metal roof matches the shallow rectangle in the aerial reference.
 mansard(attic.buffer(.9,join_style=2),23.35,2.7,2.5)
 # Replace slate hip with warm pale copper on this pavilion only.
 for group in b.groups.values():
  if group['source']==b.source and group['material'] in ['paris-slate','roof']:group['material']='paris-opera-roof'
 # Apse has masonry windows under its dome, not a freestanding gazebo.
 for angle in np.linspace(math.pi/2,math.pi*1.5,13):
  x,z=74.8+6.75*math.cos(angle),466+6.75*math.sin(angle);f=F(x,z,0,math.pi/2-angle)
  for yy,hh in [(1.0,5.2),(8,5.2)]:framed(f,0,yy,0,1.65,hh,True)
 b.lathe('paris-stone',(74.8,466),[(14.5,7),(15,7.4),(15.4,7.1),(16.2,7.1)],48)
 dome=[(16.2,7.1),(17.8,6.85),(19.6,5.6),(21.1,3.4),(21.7,.5)]
 b.lathe('paris-opera-roof',(74.8,466),dome,48)
 for angle in np.linspace(0,math.tau,20,endpoint=False):b.path('paris-gold',[(74.8+(r+.04)*math.cos(angle),y,466+(r+.04)*math.sin(angle)) for y,r in dome],.065)
 F(74.8,466,0).lathe('paris-cream',0,0,[(21.6,.5),(22.1,.45),(23,.18)],12)
 source('arrival-opera-detail',1)
 for x,z,length,yaw in [(104.12,460.75,29.5,math.pi/2),(89.4,475.65,29.2,0),(74.65,452.5,13,-math.pi/2)]:
  f=F(x,z,0,yaw)
  for xx in np.arange(-length/2+2.5,length/2-1,4.8):
   framed(f,xx,1.0,0,2.55,5.2,True);framed(f,xx,8.3,0,2.6,6.1,True)
   for dx in [-1.73,1.73]:f.lathe('paris-cream',xx+dx,.37,[(7.6,.37),(8,.30),(14.3,.26),(14.65,.46)],12)
   f.path('paris-cream',[(xx-1.7,15.1,.4),(xx,16.3,.4),(xx+1.7,15.1,.4)],.15)
   f.path('paris-gold',[(xx+.44*math.cos(a),16.9+.4*math.sin(a),.26) for a in np.linspace(0,math.tau,17)],.07)
  for yy,dd in [(G+.18,.6),(6.8,.6),(7.35,.85),(14.7,.6),(17.5,.8),(18.2,1.15)]:f.box('paris-cream',(0,yy,dd/2),(length+.5,.27,dd))
  dentils(f,length,17.9,.7)
 for x in [79,103]:
  for z in [446.5,468]:
   f=F(x,z,0);f.box('paris-cream',(0,23.8,0),(2.0,1.1,2.0));figure(f,0,24.35,0,.85,True)
 # Arc: approximate 60%-scale proportions with a deep, open main vault.
 source('arrival-arc')
 ax,az=127.3,490.7;halfwidth=13.5;depth=13.2;spring=12.5;radius=4.6;height=29.7
 # Coordinate u runs along Z; v runs along X through the main arch.
 f=F(ax,az,0,math.pi/2)
 profile=Polygon([(-halfwidth,G),(halfwidth,G),(halfwidth,height),(-halfwidth,height)]).difference(Polygon([(-radius,G),(radius,G),(radius,spring)]+[(radius*math.cos(a),spring+radius*math.sin(a)) for a in np.linspace(0,math.pi,33)]+[(-radius,G)]))
 # Triangulated front/back and full curved tunnel soffit, not a rectangle with a ring pasted on.
 for tri in triangles(profile):
  q=list(tri.exterior.coords)[:-1]
  for v in [-depth/2,depth/2]:b.face('paris-stone',[f.p(u,y,v) for u,y in q],True)
 for poly in parts(profile):
  for ring0 in [poly.exterior,*poly.interiors]:
   for a,aa in zip(list(ring0.coords),list(ring0.coords)[1:]):b.face('paris-stone',[f.p(a[0],a[1],-depth/2),f.p(aa[0],aa[1],-depth/2),f.p(aa[0],aa[1],depth/2),f.p(a[0],a[1],depth/2)],True)
 for side in [-1,1]:
  ff=F(ax+side*(depth/2+.035),az,0,side*math.pi/2)
  for rr in [radius+.10,radius+.42,radius+.75]:
   ff.path('paris-cream',[(rr*math.cos(a),spring+rr*math.sin(a),0) for a in np.linspace(0,math.pi,49)],.13)
  for xx in [-8.9,8.9]:
   ff.box('paris-relief',(xx,7.4,.11),(5.9,8.5,.28))
   # Each pier relief is a grouped composition, original geometric approximation.
   figure(ff,xx,7.7,.56,1.35,True)
   for dx,dy,scale0 in [(-1.65,3.9,1.25),(0,3.4,1.4),(1.7,4.1,1.1)]:figure(ff,xx+dx,dy,.63,scale0)
   ff.box('paris-cream',(xx,2.75,.15),(6.25,.35,.52))
   ff.box('paris-relief',(xx,21.5,.16),(6,3.2,.24))
   for dx in np.arange(-2.3,2.31,.77):figure(ff,xx+dx,20.1,.36,.62)
  # Upper frieze has raised wreaths, a continuous battle band and inscribed attic.
  for xx in np.arange(-12.7,12.8,.9):
   ff.path('paris-relief',[(xx+.22*math.cos(a),25.9+.20*math.sin(a),.10) for a in np.linspace(0,math.tau,12)],.06)
  ff.text('PARIS',(0,27.3,.2),.65,'paris-relief',back=True)
  for yy in np.arange(1,19,.72):
   for xx in [-11.85,11.85]:ff.box('paris-joint',(xx,yy,.025),(2.7,.035,.02))
  dentils(ff,27.6,24.65,.35,.45)
 for y,w,d,h in [(.4,27.8,14,.35),(18.5,27.7,13.8,.35),(24.6,28.6,14.6,.5),(25.2,29.2,15.2,.35),(28.9,29.4,15.4,.45),(29.55,30,16,.35)]:f.box('paris-cream',(0,y,0),(w,h,d))
 # Recessed rooftop and a real parapet rim.
 b.planar('roof',box(ax-7,az-13,ax+7,az+13),29.55)
 for x in [ax-7.65,ax+7.65]:b.box('paris-stone',(x,30.1,az),(.5,.8,29))
 for z in [az-14.5,az+14.5]:b.box('paris-stone',(ax,30.1,z),(15.6,.8,.5))
 source('arrival-island')
 island=Point(ax,az).buffer(19,quad_segs=48);slab(island,G+.05,'paris-paving')
 # Keep the axial walk and open vault entirely clear.
 for a in np.linspace(0,math.tau,48,endpoint=False):
  if abs(math.sin(a))<.32:continue
  x,z=ax+18.3*math.cos(a),az+18.3*math.sin(a);F(x,z,G+.05).lathe('paris-iron',0,0,[(0,.15),(.12,.15),(.8,.11),(.95,.18)],10)
 for x,z in [(94,510),(157,511),(183,492),(165,520)]:
  plant=Point(x,z).buffer(2.7,quad_segs=12);slab(plant,G+.12,'paris-stone',False);b.planar('paris-leaf',plant.buffer(-.2),G+.14)
  tree(x,z,G,2.8)
 # Montgolfier balloon: squat neck, ornate ivory/gold crown, scalloped ribbons and red script.
 source('arrival-balloon');bx,bz=42,511.5
 b.box('paris-stone',(bx,3.65,bz),(7.2,7.3,7.2),True)
 b.box('paris-iron',(bx,10.1,bz),(12.5,7,12.5))
 for yaw in [0,math.pi/2,math.pi,math.pi*1.5]:
  f=F(bx,bz,0,yaw);f.box('paris-display',(0,10.1,6.3),(11.7,6.1,.12))
  for yy in [6.8,13.4]:f.box('paris-gold',(0,yy,6.36),(12.65,.22,.25))
  for xx in [-6.2,6.2]:f.box('paris-gold',(xx,10.1,6.36),(.22,6.7,.25))
  f.text('PARIS LAS VEGAS',(0,11.3,6.42),.6,'letter',back=True);f.text('BONJOUR',(0,9.0,6.42),.78,'paris-gold',back=True)
 profile=[(13.7,3.8),(15.0,4.1),(17.1,3.5),(19.0,4.5),(21.5,7.9),(25,10.1),(29,11.45),(33,11.35),(36.5,10.2),(39.5,8.3),(42,5.9),(44,3),(44.9,.25)]
 # Smooth radial rings rather than coarse faceted cone with a long neck.
 dense=[]
 for (ya,ra),(yb,rb) in zip(profile,profile[1:]):
  for t in np.linspace(0,1,5,endpoint=False):dense.append((ya+(yb-ya)*t,ra+(rb-ra)*t))
 dense.append(profile[-1]);b.lathe('paris-blue',(bx,bz),dense,96)
 def rr(y):return float(np.interp(y,[v[0] for v in profile],[v[1] for v in profile]))+.055
 for a in np.linspace(0,math.tau,24,endpoint=False):
  b.path('paris-gold',[(bx+(r+.065)*math.cos(a),y,bz+(r+.065)*math.sin(a)) for y,r in dense],.065,6)
 for lo,hi,mat in [(19,19.5,'paris-gold'),(33,34.1,'paris-cream'),(34.1,34.6,'paris-gold'),(37.3,38.1,'paris-red'),(38.15,38.55,'paris-gold'),(42.0,44.9,'paris-cream')]:b.lathe(mat,(bx,bz),[(y,rr(y)+.035) for y in np.linspace(lo,hi,9)],96)
 # Ivory crown gores and gold teardrop scrolls. Individual geometry, shared materials.
 for i in range(24):
  aa=i*math.tau/24;ab=(i+1)*math.tau/24
  for lo,hi in [(38.6,39.7),(39.7,41),(41,41.9)]:b.face('paris-cream',[(bx+rr(y)*math.cos(a),y,bz+rr(y)*math.sin(a)) for a,y in [(aa+.028,lo),(ab-.028,lo),(ab-.028,hi),(aa+.028,hi)]])
  ac=(aa+ab)/2
  for mat,rad,off in [('paris-gold',.085,.00),('paris-red',.06,.035)]:
   pts=[]
   for t in np.linspace(0,math.pi,19):
    a=aa+(ab-aa)*t/math.pi;y=33.05-1.05*math.sin(t);r=rr(y)+.09+off;pts.append((bx+r*math.cos(a),y,bz+r*math.sin(a)))
   b.path(mat,pts,rad,6)
  # Radiating medallions on the blue panels below the scallops.
  if i%3==0:
   x,z=bx+rr(28.5)*math.cos(ac),bz+rr(28.5)*math.sin(ac);f=F(x,z,28.5,math.pi/2-ac)
   f.path('paris-gold',[(1.05*math.cos(t),1.5*math.sin(t),.08) for t in np.linspace(0,math.tau,33)],.045)
   for t in np.linspace(0,math.tau,24,endpoint=False):f.tube('paris-gold',(.38*math.cos(t),.52*math.sin(t),.1),(.92*math.cos(t),1.37*math.sin(t),.1),.025,6)
 # Exporter sets a script face and white raised outline on these actual mesh letters.
 for yaw in [-math.pi/2,0]:
  f=F(bx,bz,0,yaw);f.text('Paris',(0,26.9,11.7),5.3,'paris-script',back=True)
 return main
