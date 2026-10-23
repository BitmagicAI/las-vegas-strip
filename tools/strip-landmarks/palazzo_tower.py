"""Palazzo facade: photographic proportions on inherited mapped footprint/height.
No surveyed crown setbacks are claimed. Collision and rooms remain HighriseCity.
"""
import json,math
import numpy as np
from shapely.geometry import Polygon,Point
from shapely.ops import unary_union
from common import parts,Frame

def tower(B):
 plan=next(p for p in json.load(open('build/highrises/plan.json')) if p['key']=='palazzo')
 B.source='tower/way/30424125';B.detail=0
 for g in json.load(open('build/highrises/meshes.json')):
  if g['property']!='palazzo' or g['lod']!=0:continue
  for f in g['faces']:B.face({'glass':'palazzo-glass','roof':'roof'}.get(g['material'],'ivory'),[g['vertices'][i] for i in f])
 feature=plan['features'][0];h=feature['height']
 shape=unary_union([Polygon([(x,-z) for x,z in q[0]]) for q in feature['polygons']]).buffer(0)
 for poly in parts(shape):
  pts=list(poly.exterior.coords)
  for a,b in zip(pts,pts[1:]):
   L=math.dist(a,b)
   if L<.5:continue
   ux,uz=(b[0]-a[0])/L,(b[1]-a[1])/L;nx,nz=-uz,ux
   if shape.contains(Point((a[0]+b[0])/2+nx*.1,(a[1]+b[1])/2+nz*.1)):nx,nz=-nx,-nz
   def p(x,y,o):return (a[0]+ux*x+nx*o,y,a[1]+uz*x+nz*o)
   def q(mat,x,lo,xx,hi,o=.10):B.face(mat,[p(x,lo,o),p(xx,lo,o),p(xx,hi,o),p(x,hi,o)])
   def band(y,thick,depth):
    q('ivory',0,y,L,y+thick,depth)
    B.face('ivory',[p(0,y,.03),p(L,y,.03),p(L,y,depth),p(0,y,depth)])
    B.face('ivory',[p(0,y+thick,depth),p(L,y+thick,depth),p(L,y+thick,.03),p(0,y+thick,.03)])
   lo=18.;top=h-7
   q('palazzo-stone',0,lo,L,h)
   # Broad blind end panels match photographed wings; narrow survey chamfers
   # remain stone. Long wing faces retain tall blue glazing with grouped piers.
   end=24<L<35
   if L>=12 and not end:
    count=max(2,round(L/6.8));step=L/count
    for j in range(count):
     x=j*step+.85;xx=(j+1)*step-.85
     for y0,y1 in [(lo,43),(47,154),(158,top)]:
      if y1<=y0:continue
      q('palazzo-glass',x,y0,xx,y1,.14)
      for edge in [x-.14,xx]:q('ivory',edge,y0,edge+.14,y1,.29)
      B.detail=1
      for yy in np.arange(y0+3.4,y1,3.4):q('champagne',x,yy,xx,min(yy+.065,y1),.19)
      for k in range(1,4):q('champagne',x+(xx-x)*k/4-.025,y0,x+(xx-x)*k/4+.025,y1,.19)
      B.detail=0
     # Projecting capitals and warm piers at crown distinguish the upper order.
     q('palazzo-warm',j*step,158,j*step+.7,h-2,.36)
     q('ivory',j*step-.12,h-3,min(L,j*step+.90),h-1.6,.53)
   elif end:
    q('plaster',1.2,47,L-1.2,154,.18)
    for x in [1.,L-1.45]:q('palazzo-warm',x,47,x+.45,154,.38)
    # Letters sit on the outward-facing side, one glyph per line as photographed.
    yaw=math.atan2(uz,ux)+math.pi
    for j,c in enumerate('PALAZZO'):B.text(c,p(L/2,145-j*9,.48),5.2,yaw,'charcoal')
   for yy,thick,depth in [(lo,.8,.50),(42.6,1.0,.7),(46,1.0,.9),(153.6,1.0,.65),(157,1.0,.9),(h-6,.65,.7),(h-2.2,.7,1.05),(h-.65,.65,1.3)]:band(yy,thick,depth)
   B.detail=1
   for x in np.arange(1,L-1,3.6):
    q('palazzo-glass',x,44,x+1.3,45.3,.19)
    q('palazzo-warm',x,155.2,x+1.3,156.1,.19)
   B.detail=0
 # Raised central attic and terminal caps: photo-led, not surveyed roof levels.
 # Keep guest-room envelope and inherited roof/collision unchanged.
 pts=list(list(parts(shape))[0].exterior.coords)
 for index in [4,6,8]:
  a,b=pts[index],pts[index+1];L=math.dist(a,b);ux,uz=(b[0]-a[0])/L,(b[1]-a[1])/L
  nx,nz=-uz,ux
  if shape.contains(Point((a[0]+b[0])/2+nx*.1,(a[1]+b[1])/2+nz*.1)):nx,nz=-nx,-nz
  # Frame +z points out of the wall; text is turned toward the exterior.
  yaw=math.atan2(nx,nz);cx,cz=(a[0]+b[0])/2,(a[1]+b[1])/2
  if index!=6:
   t=7/L if index==4 else 1-7/L;cx,cz=a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t
  F=Frame(B,cx,cz,yaw,y=0);w=L if index==6 else 14
  if index==6:
   F.box('palazzo-warm',(0,h-3.5,.65),(w,9,1.1))
   for x in [-w*.31,0,w*.31]:
    ring=[(x+1.05*math.cos(t),h-4+1.05*math.sin(t),1.24) for t in np.linspace(0,math.tau,33)]
    F.path('ivory',ring,.16,6)
    for j in range(32):B.face('palazzo-glass',[F.p(x,h-4,1.20),F.p(*ring[j]),F.p(*ring[j+1])])
    F.box('ivory',(x,h-4,1.29),(.055,1.95,.06));F.box('ivory',(x,h-4,1.29),(1.95,.055,.06))
   F.text('P A L A Z Z O',(0,h+1,1.42),1.7,'ivory',back=True)
  rise=3.8 if index==6 else 1.8
  for yy,ww,depth,thick in [(h-.4,w+1.2,3.4,.5),(h+.35,w+2,4.0,.55),(h+rise,w+3.2,4.8,.55)]:
   F.box('ivory',(0,yy,-.15),(ww,thick,depth))
  F.box('palazzo-warm',(0,h+rise/2,-.6),(w+1, rise,2.5))
  B.detail=1
  for x in np.arange(-w/2,w/2,.9):F.box('ivory',(x,h+rise-.75,1.2),(.3,.8,.6))
  B.detail=0
 B.source='venetian-podium';B.detail=0
