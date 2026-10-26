"""Hofbrauhaus surveyed-envelope study. Dimensions estimated from February 2026 Street View.

Exterior only in this pass. Public interior installation waits for layout corroboration.
No Google imagery or geometry is embedded; all geometry is original on the OSM footprint.
"""
from common import *
from forum_shops import facade_frame
KEY='hofbrauhaus'
ID='way/111339182'
YAW=1.7868214428245313

def window(G,u,bottom,w,h,arched=False,flower=False,depth=-.075):
 B=G.b; z=depth
 if arched:
  r=w/2; spring=bottom+h-r
  pts=[(u-r,bottom),(u+r,bottom)]+[(u+r*math.cos(a),spring+r*math.sin(a)) for a in np.linspace(0,math.pi,25)]
  B.face('hb-glass',[G.p(x,y,z) for x,y in pts])
  G.arch(u,z-.055,w,h+bottom,'hb-frame',.045,bottom)
 else:
  G.box('hb-frame',(u,bottom+h/2,z),(w+.16,h+.16,.1))
  G.box('hb-glass',(u,bottom+h/2,z-.065),(w,h,.04))
 G.box('hb-frame',(u,bottom+h/2,z-.10),(.045,h,.05))
 for yy in [bottom+h*.38,bottom+h*.72]:G.box('hb-frame',(u,yy,z-.12),(w,.045,.04))
 G.box('hb-stone',(u,bottom-.10,z-.09),(w+.3,.16,.38))
 if flower:
  G.box('hb-planter',(u,bottom+.05,-.34),(w+.2,.28,.4))
  # Small original leaf clusters, batched, only on sill boxes; no sphere trees.
  for i in range(14):
   x=u-w/2+w*(i+.5)/14;yy=bottom+.25+.08*math.sin(i*2.4)
   B.face('hb-leaf',[G.p(x-.08,yy,-.40),G.p(x,yy+.16,-.5),G.p(x+.1,yy,-.47)])
   if i%3==0:G.box('hb-flower',(x,yy+.08,-.48),(.07,.06,.07))

def gable(G,u,w=7):
 B=G.b
 # Stepped concave outline with curved scroll shoulders, not a flat triangle.
 half=[(w/2,11.8),(w/2,12.8),(w*.36,12.8),(w*.33,13.8),(w*.26,14.15),(w*.22,15.4),(w*.12,15.65),(0,16.3)]
 pts=[(u-w/2,11.8)]+[(u-x,y) for x,y in half[1:]]+[(u+x,y) for x,y in reversed(half[:-1])]
 shape=Polygon(pts).buffer(0)
 for tri in triangles(shape):B.face('hb-plaster',[G.p(x,y,-.18) for x,y in list(tri.exterior.coords)[:-1]])
 G.path('hb-stone',[(u-x,y,-.25) for x,y in half],.11)
 G.path('hb-stone',[(u+x,y,-.25) for x,y in half],.11)
 for x in [-w*.21,0,w*.21]:window(G,u+x,12.0,min(1.05,w*.19),1.6,depth=-.34)
 window(G,u,14.05,.85,1.2,True,depth=-.34)
 G.text('HOFBRÄUHAUS',(u,13.8,-.34),.48,'hb-blue')
 for x in [-w*.35,w*.35,0]:
  yy=16.4 if x==0 else 13.3
  G.lathe('hb-stone',u+x,-.15,[(yy,.12),(yy+.15,.24),(yy+.38,.12),(yy+.52,.04)],12)

def exterior(B):
 B.property=KEY+'-exterior';B.source='podium/hofbrauhaus';B.detail=0
 p=footprint(ID);F=Frame(B,1922.741,969.671,YAW,y=0)
 # Envelope remains solid in the staged exterior study; public openings are installed with interior later.
 B.shell(p,.15,11.65,'hb-plaster',roof=False)
 pts=list(p.exterior.coords)
 for a,b in zip(pts,pts[1:]):
  G,L,nx,nz=facade_frame(B,a,b,p,.05);G.y=0
  for yy,hh,depth in [(.45,.65,.13),(11.05,.18,.22),(11.4,.35,.34),(11.67,.12,.5)]:G.box('hb-stone',(L/2,yy,-.03),(L+.05,hh,depth))
  front=nx<-.7; north=nz<-.6
  if front:
   # February 2026 west view: tall hall arches occupy the northern half;
   # the southern half retains two smaller tiers above the entry arcade.
   for u in [34,41,48]:window(G,u,.7,4.0,5.6,True)
   for u in [4,9,14,19,24,57]:
    window(G,u,.35,2.65,3.65,True)
    window(G,u,5.1,1.35,1.75,False,True)
   for u in [3,6,11,14,18,34,36.4,41,43.4,48,50.4,55,57.4]:
    window(G,u,7.9,1.15,2.25,True,True)
   for u in [23,28]:window(G,u,7.5,3.15,2.8,True)
   G.text('BAVARIAN RESTAURANT',(43,7.1,-.24),.53,'hb-blue')
   G.text('MORE THAN BRATS & BEER',(17,7.1,-.24),.45,'hb-blue')
   G.text('HOFBRAUHAUS LAS VEGAS',(56,7.1,-.24),.32,'hb-blue')
   gable(G,L-4.2,7.8)
   gable(G,30,4.3)
  else:
   n=max(1,round(L/3.65))
   for j in range(n):
    u=(j+.5)*L/n
    if north:
     window(G,u,7.8,1.2,2.45,True,True)
     window(G,u,5.0,1.28,1.8,False,True)
     window(G,u,.4,2.45,3.55,True)
    else:
     window(G,u,7.2,1.15,2.0)
     if j%2==0:window(G,u,2,1.4,2.1)
   if north:G.text('HOFBRÄUHAUS LAS VEGAS',(L*.5,7.15,-.24),.48,'hb-blue')
  # Roof dormers on street elevations.
  if front or north:
   for u in np.arange(4,L-5,5.8):
    if front and abs(u-30)<3:continue
    G.box('hb-plaster',(u,12.5,1),(2.05,1.35,1.9))
    window(G,u,12.0,1.5,.9)
    # Pitched dormer roof and triangular cheek: no floating flat slab.
    B.face('hb-plaster',[G.p(u-1.025,13.175,.05),G.p(u+1.025,13.175,.05),G.p(u,13.82,.05)])
    for side in [-1,1]:
     B.upface('hb-roof',[G.p(u,13.86,-.15),G.p(u+side*1.25,13.15,-.15),G.p(u+side*1.25,13.15,2.15),G.p(u,13.86,2.15)])
 # Clipped pitched roof retains every OSM setback. Ridge/slope heights are estimates.
 local=[]
 for x,z in list(p.exterior.coords)[:-1]:
  dx,dz=x-F.x,z-F.z;local.append((F.co*dx-F.si*dz,F.si*dx+F.co*dz))
 lp=Polygon(local)
 def roofheight(v):return max(11.65,16.1-abs(v-12.4)*.36)
 # Split at both slope breaks as well as the ridge; triangulating across
 # the rear flat transition created an artificial diagonal roof slope.
 breaks=[-1,12.4,12.4+(16.1-11.65)/.36,40]
 for lo,hi in zip(breaks,breaks[1:]):
  section=lp.intersection(box(-2,lo,65,hi))
  for tri in triangles(section):B.upface('hb-roof',[F.p(u,roofheight(v),v) for u,v in list(tri.exterior.coords)[:-1]])
 for a,b in zip(local,local[1:]+local[:1]):
  cuts=[a,b]
  for boundary in breaks[1:-1]:
   if (a[1]-boundary)*(b[1]-boundary)<0:
    t=(boundary-a[1])/(b[1]-a[1]);cuts.append((a[0]+t*(b[0]-a[0]),boundary))
  cuts.sort(key=lambda q:(q[0]-a[0])**2+(q[1]-a[1])**2)
  for aa,bb in zip(cuts,cuts[1:]):B.face('hb-plaster',[F.p(aa[0],11.65,aa[1]),F.p(bb[0],11.65,bb[1]),F.p(bb[0],roofheight(bb[1]),bb[1]),F.p(aa[0],roofheight(aa[1]),aa[1])])
 # Northwest corner projecting two-storey polygonal bay.
 cx,cz=F.p(60.5,0,.35)[::2]
 Q=Frame(B,cx,cz,YAW,y=0)
 for y in [4.1,7.0]:
  poly=Q.poly([(-1.5,-.3),(-1.2,-1.45),(0,-2),(1.2,-1.45),(1.5,-.3)])
  B.shell(poly,y,y+2.65,'hb-bay',roof=False,solid=False)
  B.planar('hb-bay',poly.buffer(.13),y+.1)
  B.planar('hb-stone',poly.buffer(.13),y+2.68)
  for aa,bb in zip(list(poly.exterior.coords),list(poly.exterior.coords)[1:]):
   G,L,_,_=facade_frame(B,aa,bb,poly,.03);G.y=0
   if L<3:window(G,L/2,y+.35,max(.4,L-.3),1.9)
 roof=Q.poly([(-1.7,-.3),(-1.4,-1.6),(0,-2.2),(1.4,-1.6),(1.7,-.3)])
 for aa,bb in zip(list(roof.exterior.coords),list(roof.exterior.coords)[1:]):B.face('hb-copper',[(aa[0],9.9,aa[1]),(bb[0],9.9,bb[1]),Q.p(0,11.1,-.65)])
 return dict(key=KEY,name='Hofbrauhaus Las Vegas',center=[1933,0,940],bounds=list(p.bounds),structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
