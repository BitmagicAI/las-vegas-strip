"""Venetian tower facade from Oct 9 photographic references.
Mapped footprints, heights, original entrance cuts and collision retained.
Facade proportions are photo-fitted estimates; no claim of survey accuracy.
"""
import json,math
import numpy as np
from shapely.geometry import Polygon,Point
from shapely.ops import unary_union
from common import parts

def clip_above(pts,y0):
 """The part of a planar polygon at or above height y0 (Sutherland-Hodgman against one plane)."""
 out=[]
 for i,a in enumerate(pts):
  b=pts[(i+1)%len(pts)];ina=a[1]>=y0;inb=b[1]>=y0
  if ina:out.append(a)
  if ina!=inb:
   t=(y0-a[1])/(b[1]-a[1]);out.append([a[k]+(b[k]-a[k])*t for k in range(3)])
 return out

def towers(B):
 plan=next(p for p in json.load(open('build/highrises/plan.json')) if p['key']=='venetian')
 # Transfer structural render ownership only. Original collision remains HighriseCity.
 old=json.load(open('build/highrises/meshes.json'))
 # Inside the podium the shell starts at the podium roof (17.0): below it the public interiors stand (2026-10-23: the
 # shell's ground-up faces cut through the lobby's rotunda, the front desk and the casino). Faces over the outdoor
 # forecourt keep their full height.
 from common import footprint
 inside=footprint('relation/7770314').difference(unary_union([footprint(i).buffer(.08,join_style=2) for i in ['way/33996627','way/543728945','way/115776190']])).buffer(-.3)
 for g in old:
  if g['property']!='venetian' or g['lod']!=0:continue
  if g['source']=='way/43875964':continue
  B.source='tower/'+g['source'];B.detail=0
  mat={'stone':'ivory','roof':'ivory','frame':'ivory','glass':'darkglass'}.get(g['material'],'ivory')
  for f in g['faces']:
   pts=[g['vertices'][i] for i in f]
   if min(p_[1] for p_ in pts)<17.0 and inside.contains(Point(sum(p_[0] for p_ in pts)/len(pts),sum(p_[2] for p_ in pts)/len(pts))):
    pts=clip_above(pts,17.0)
    if len(pts)<3:continue
   B.face(mat,pts)
 for f in plan['features']:
  if f['id']=='way/43875964':continue
  shape=unary_union([Polygon([(x,-z) for x,z in p[0]]) for p in f['polygons']]).buffer(0)
  h=f['height'];B.source='tower/'+f['id'];B.detail=0
  podium=38. if f['id']=='way/111322067' else 17.;crown=h-16;top=h-4.2
  for poly in parts(shape):
   coords=list(poly.exterior.coords)
   # Collapse collinear survey vertices to keep bay spacing even along a wall.
   clean=[]
   for i,a in enumerate(coords[:-1]):
    b=coords[i-1] if i else coords[-2];c=coords[(i+1)%(len(coords)-1)]
    u=np.subtract(a,b);v=np.subtract(c,a)
    if abs(u[0]*v[1]-u[1]*v[0])>1e-3:clean.append(a)
   for a,b in zip(clean,clean[1:]+clean[:1]):
    L=math.dist(a,b)
    if L<1:continue
    ux,uz=(b[0]-a[0])/L,(b[1]-a[1])/L;nx,nz=-uz,ux
    if shape.contains(Point((a[0]+b[0])/2+nx*.1,(a[1]+b[1])/2+nz*.1)):nx,nz=-nx,-nz
    def p(x,y,o):return (a[0]+ux*x+nx*o,y,a[1]+uz*x+nz*o)
    def quad(mat,x,y,xx,yy,o=.075):B.face(mat,[p(x,y,o),p(xx,y,o),p(xx,yy,o),p(x,yy,o)])
    def cornice(y,height,depth):
     quad('ivory',0,y,L,y+height,depth)
     B.face('ivory',[p(0,y,.02),p(L,y,.02),p(L,y,depth),p(0,y,depth)])
     B.face('ivory',[p(0,y+height,depth),p(L,y+height,depth),p(L,y+height,.02),p(0,y+height,.02)])
    # Venetian's characteristic uninterrupted vertical glass slots, salmon/taupe
    # piers, and two tiers of arched windows replace the old square-window grid.
    if podium>17:
     quad('venetian-taupe',0,17,L,podium,.15)
     for yy in np.arange(19,podium-1,3.1):
      quad('charcoal',1,yy,L-1,yy+1.1,.18)
      quad('ivory',0,yy-1,L,yy-.7,.35)
    end_wall=f['id']=='way/30618090' and 29<L<34
    if end_wall:
     quad('ivory',0,podium,L,h-.7,.28)
     quad('venetian-taupe',2.2,podium+1,L-2.2,crown,.31)
     quad('ivory',L*.31,podium+1,L*.69,h-2,.40)
     for xx in [1.1,L-2.1]:quad('plaster',xx,podium,xx+1,crown,.55)
     # Blind end wall and vertical sign, rather than a third glass facade.
     for j,letter in enumerate('VENETIAN'):
      B.text(letter,p(L/2,h-30-j*7.8,.65),4.4,math.atan2(uz,ux)+math.pi,'venetian-taupe')
     for yy in [podium+1,crown-1,crown+1,h-2]:cornice(yy,.35,.65)
    elif L<9:
     quad('venetian-taupe',.2,podium,L-.2,crown)
     for yy in np.arange(podium,crown,7.6):quad('venetian-salmon',.2,yy,L-.2,min(yy+2.5,crown),.08)
    else:
     count=max(2,round((L-2.4)/4.45));step=(L-2.4)/count
     quad('venetian-taupe',1.2,podium,L-1.2,crown)
     for yy in np.arange(podium,crown,7.6):quad('venetian-salmon',1.2,yy,L-1.2,min(yy+2.5,crown),.08)
     for j in range(count):
      x=1.2+(j+.5)*step;w=step*.52;r=w/2
      def window(lo,hi,arched=False):
       spring=hi-r if arched else hi
       ring=[(x-r,lo),(x+r,lo),(x+r,spring)]
       if arched:ring.extend((x+math.cos(t)*r,spring+math.sin(t)*r) for t in np.linspace(0,math.pi,13)[1:])
       else:ring.append((x-r,hi))
       B.face('palazzo-glass',[p(xx,yy,.12) for xx,yy in ring])
       # Deep reveal surfaces provide actual shadow at glass/stone boundaries.
       for aa,bb in zip(ring,ring[1:]+ring[:1]):B.face('ivory',[p(*aa,.12),p(*bb,.12),p(*bb,.36),p(*aa,.36)])
       # Molded reveal, structural at all LODs; fine mullions near only.
       B.path('ivory',[p(xx,yy,.20) for xx,yy in ring+[ring[0]]],.095,6)
       B.detail=1
       quad('champagne',x-.025,lo,x+.025,hi-.12,.23)
       for yy in np.arange(lo+.8,spring,3.65):quad('champagne',x-r,yy,x+r,yy+.045,.23)
       B.detail=0
      window(podium,crown-1.2)
      window(crown+1.1,top-.8,True)
      # Recessed crown panel and small pilaster capital between the arch bays.
      B.detail=1
      if j:
       bx=x-step/2;quad('plaster',bx-.17,crown+1.2,bx+.17,top-1.1,.21)
       quad('ivory',bx-.36,top-1.8,bx+.36,top-1.35,.32)
      B.detail=0
    for y,hh,d in [(podium-.6,.6,.35),(crown-.55,.35,.42),(crown,.8,.65),(top,.32,.55),(h-2.2,.6,.80),(h-.6,.6,1.0)]:cornice(y,hh,d)
    # Attic frieze and inset panel rhythm below the deep roof cornice.
    for x in np.arange(1,L-1,7.5):quad('plaster',x,h-1.45,min(x+6.5,L-.8),h-.82,.12)
  # Small rooftop mechanical enclosures are static near-detail geometry.
  B.detail=1
  roof=shape.buffer(-4)
  for xx in np.arange(shape.bounds[0]+8,shape.bounds[2]-5,14):
   for zz in np.arange(shape.bounds[1]+8,shape.bounds[3]-5,14):
    if not roof.contains(Point(xx,zz).buffer(3)):continue
    B.box('ivory',(xx,h+.65,zz),(4.8,1.3,3.4))
    B.box('concrete',(xx,h+1.35,zz),(5,.15,3.6))
    for dz in [-.8,0,.8]:B.box('charcoal',(xx,h+1.45,zz+dz),(3.7,.08,.32))
  B.detail=0
 # Major skyline lettering retained, matched to mapped longest edge.
 for s in json.load(open('build/highrises/signs.json')):
  if s['property']!='venetian':continue
  a,b=s['a'],s['b'];L=math.dist(a,b)
  B.source='tower/'+s['source'];B.detail=0
  B.text('VENETIAN',[(a[0]+b[0])/2,s['height']+.2,(a[1]+b[1])/2],min(3.8,L/25),math.atan2(b[1]-a[1],b[0]-a[0])+math.pi,'ivory')
 B.source='venetian-podium';B.detail=0
