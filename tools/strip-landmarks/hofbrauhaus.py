"""Hofbrauhaus surveyed-envelope study. Dimensions estimated from February 2026 Street View.

Public rooms are separately streamed; their connecting layout is an explicit interpretation.
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
 entry=dict(p=F.p(19,.18,0),yaw=YAW,width=2.5,height=3.1,name='Restaurant entrance',venue=KEY)
 B.portals.append(entry)
 B.shell(p,.15,11.65,'hb-plaster',roof=False,openings=[entry])
 # Solid public threshold, with the same datum inside and outside.
 B.planar('hb-stone',p,.18,True)
 apron=F.poly([(1,-1.9),(60,-1.9),(60,0),(1,0)])
 B.planar('hb-stone',apron,.18,True)
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
    if u!=19:window(G,u,.35,2.65,3.65,True)
    else:G.arch(u,-.08,2.8,3.8,'hb-stone',.12,.18)
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
    G.box('hb-stone',(u,13.26,.85),(2.35,.16,2.4))
 # Clipped pitched roof retains every OSM setback. Ridge/slope heights are estimates.
 local=[]
 for x,z in list(p.exterior.coords)[:-1]:
  dx,dz=x-F.x,z-F.z;local.append((F.co*dx-F.si*dz,F.si*dx+F.co*dz))
 lp=Polygon(local)
 # Convex lower envelope of four roof planes: roof-end hips, not blank
 # triangular walls. Clip each plane's region before triangulation.
 planes=[(0,.36,11.65),(0,-.36,20.564),(.65,0,11.65),(-.65,0,51.55)]
 def clip_half(poly,a,b,c):
  coords=list(poly.exterior.coords)[:-1];result=[]
  for q,r in zip(coords,coords[1:]+coords[:1]):
   fq=a*q[0]+b*q[1]+c;fr=a*r[0]+b*r[1]+c
   if fq<=1e-8:result.append(q)
   if (fq<0)!=(fr<0):
    t=fq/(fq-fr);result.append((q[0]+t*(r[0]-q[0]),q[1]+t*(r[1]-q[1])))
  return Polygon(result) if len(result)>2 else Polygon()
 for a,b,c in planes:
  region=lp
  for aa,bb,cc in planes:
   if region.is_empty:break
   region=clip_half(region,a-aa,b-bb,c-cc)
  if region.is_empty:continue
  for tri in triangles(region):B.upface('hb-roof',[F.p(u,max(11.65,a*u+b*v+c),v) for u,v in list(tri.exterior.coords)[:-1]])
 # Street-side waist-high terrace rail, interrupted at the entrance.
 for lo,hi in [(1,17.4),(20.6,59)]:
  for y in [.3,1.25]:F.tube('hb-frame',(lo,y,-1.6),(hi,y,-1.6),.035,8)
  for u in np.arange(lo,hi,.25):F.tube('hb-frame',(u,.18,-1.6),(u,1.25,-1.6),.015,6)
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
 return dict(key=KEY,name='Hofbrauhaus Las Vegas',center=[1933,0,940],bounds=list(p.bounds),structural=True,exteriorOnly=False,portals=[entry],zones=[dict(origin=F.p(30,.18,0),yaw=YAW,width=60,depth=36,height=11)],lights=[],routes=[],hotelSources=[],views={})
