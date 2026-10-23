"""Doge's Palace T-shaped canal plaza, from closed OSM pedestrian outlines.
Deck height and decorative dimensions are photo estimates. Fixed world metre datum.
"""
import math
import numpy as np
from shapely.geometry import Polygon,LineString,Point,box
from common import Frame,parts
from venetian_waterways import plaza_height as deck_y,plaza_soffit,surface

BAR=[(225.761,-723.621),(208.270,-723.688),(207.929,-701.157),(207.785,-691.405),(207.659,-683.223),(207.335,-661.995),(209.817,-659.056),(210.761,-659.156),(215.060,-659.023),(220.239,-658.856),(224.457,-657.820)]
STEM=[(182.758,-701.157),(182.488,-691.628),(182.254,-683.413),(207.659,-683.223),(207.929,-701.157)]
DECK=Polygon(BAR).buffer(.02,join_style=2).union(Polygon(STEM).buffer(.02,join_style=2)).buffer(-.02,join_style=2);Y=1.10

def rail(B,a,b,y=Y,end_y=None,posts=(-1,1)):
 dx,dz=b[0]-a[0],b[1]-a[1];L=math.hypot(dx,dz)
 if L<.08:return
 end_y=y if end_y is None else end_y
 F=Frame(B,(a[0]+b[0])/2,(a[1]+b[1])/2,math.atan2(-dz,dx),y=y)
 def dy(x):return (x/L+.5)*(end_y-y)
 for low,high,w in [(0,.28,.48),(.99,1.17,.52)]:
  pts=[F.p(x,dy(x)+h,z) for x,h,z in [(-L/2,low,-w/2),(L/2,low,-w/2),(L/2,high,-w/2),(-L/2,high,-w/2),(-L/2,low,w/2),(L/2,low,w/2),(L/2,high,w/2),(-L/2,high,w/2)]]
  for ids in [(0,3,2,1),(4,5,6,7),(0,4,7,3),(1,2,6,5),(3,7,6,2),(0,1,5,4)]:B.face('ivory',[pts[i] for i in ids],low==0)
 from palazzo_steps import barrier
 barrier(B,[F.p(x,dy(x)+h,0) for x,h in [(-L/2,.25),(L/2,.25),(L/2,1.17),(-L/2,1.17)]])
 for x in np.linspace(-L/2+.25,L/2-.25,max(2,math.ceil(L/.62))):
  F.lathe('ivory',x,0,[(h+dy(x),r) for h,r in [(.28,.065),(.34,.105),(.48,.075),(.64,.13),(.83,.065),(1,.09)]],8)
 for x in [side*L/2 for side in posts]:
  F.box('ivory',(x,dy(x)+.59,0),(.65,1.18,.65),True);F.box('marble',(x,dy(x)+1.24,0),(.83,.16,.83))

def column(B,x,z,lion=False):
 C=Frame(B,x,z,y=.24)
 for yy,w,h in [(.23,2.5,.46),(.61,2.05,.3),(.94,1.7,.36),(1.4,1.4,.58),(10.9,1.45,.35),(11.22,1.8,.28),(11.54,2.35,.35)]:C.box('ivory',(0,yy,0),(w,h,w),yy<1)
 C.lathe('pinkstone',0,0,[(1.65,.69),(1.86,.58),(9.95,.47),(10.3,.58),(10.7,.64)],24)
 for a in np.linspace(0,math.tau,13)[:-1]:
  C.path('ivory',[(.57*math.cos(a),10.30,.57*math.sin(a)),(.8*math.cos(a),10.75,.8*math.sin(a))],.11,6)
 B.detail=1
 # Small figurative silhouettes are approximate sculptural masses, not scans.
 if lion:
  B.sphere('ivory',C.p(0,12.1,0),1,16,10,(.9,.46,.36));B.sphere('ivory',C.p(-.64,12.45,0),.40,12,8)
  for xx in [-.60,.56]:
   for zz in [-.25,.25]:C.tube('ivory',(xx,12.1,zz),(xx-.12,11.76,zz),.12,8)
  for side in [-1,1]:
   for j in range(7):C.tube('ivory',(.15,12.3,side*.15),(.9-j*.12,12.9+j*.06,side*(.8-j*.05)),.10,6)
 else:
  C.lathe('ivory',0,0,[(11.7,.27),(12.1,.36),(12.9,.22),(13.2,.30)],12);B.sphere('ivory',C.p(0,13.53,0),.24,12,8)
  C.tube('ivory',(-.25,13,0),(-.56,12.55,.1),.12,8);C.tube('ivory',(.25,13,0),(.53,13.2,0),.12,8)
 B.detail=0

def plaza(B):
 B.source='venetian-canal-plaza';B.detail=0
 # A navigable arch replaces the former solid retaining wall across the basin.
 surface(B,'plaza-paving-dark',DECK,solid=True)
 surface(B,'ivory',Polygon(STEM).intersection(box(186,-1000,204,0)),solid=True,underside=True)
 for p in parts(DECK):
  q=list(p.exterior.coords)
  for a,b in zip(q,q[1:]):
   n=max(1,math.ceil(math.dist(a,b)/.5))
   for j in range(n):
    u=j/n;v=(j+1)/n;x=a[0]+u*(b[0]-a[0]);z=a[1]+u*(b[1]-a[1]);xx=a[0]+v*(b[0]-a[0]);zz=a[1]+v*(b[1]-a[1])
    B.face('ivory',[(x,plaza_soffit(x),z),(xx,plaza_soffit(xx),zz),(xx,deck_y(xx),zz),(x,deck_y(x),z)],True)
 # Raised arch moulding visibly frames the open waterway on both sides.
 for a,b in [(STEM[0],STEM[-1]),(STEM[2],STEM[3])]:
  points=[]
  for x in np.linspace(186.02,203.98,65):
   z=a[1]+(b[1]-a[1])*(x-a[0])/(b[0]-a[0]);points.append((x,plaza_soffit(x)+.06,z))
  B.path('ivory',points,.105,8)
 # Western approach stays flush with existing city path and climbs gently.
 ramp=Polygon([(176.5,-701.16),(176.5,-683.41),(182.254,-683.413),(182.758,-701.157)])
 for p in parts(ramp):
  from common import triangles
  for tri in triangles(p):B.upface('plaza-paving-dark',[(x,.24+(x-176.5)/(182.254+(-z-683.413)/(701.157-683.413)*.504-176.5)*(Y-.24),z) for x,z in list(tri.exterior.coords)[:-1]],True)
 # Double pale inlaid borders and rectangular maze motifs visible in references.
 for d in [.75,1.03]:
  inner=DECK.buffer(-d,join_style=2).intersection(box(0,-1000,215.5,0))
  surface(B,'ivory',inner.difference(inner.buffer(-.13,join_style=2)),.016)
 for z in np.arange(-719,-660,9.2):
  for x in [212.3,220.0]:
   p=box(x-2.65,z-3.2,x+2.65,z+3.2);band=p.difference(p.buffer(-.14,join_style=2)).intersection(DECK.buffer(-1.4)).intersection(box(0,-1000,215.5,0))
   surface(B,'ivory',band,.017)
 for x in np.arange(187,206,7):
  p=box(x-2.5,-698.4,x+2.5,-686.0);surface(B,'ivory',p.difference(p.buffer(-.13)),.017)
 # Rail exposed water edges only; exclude palace threshold and street connection.
 coords=list(DECK.exterior.coords)
 for a,b in zip(coords,coords[1:]):
  mx,mz=(a[0]+b[0])/2,(a[1]+b[1])/2
  if mx>223 or mx<184:continue
  # Keep the side-stair approach genuinely open through the plaza balustrade.
  edge=LineString([a,b]).difference(box(212.4,-660,217.6,-656))
  for part in (list(edge.geoms) if hasattr(edge,'geoms') else [edge]):
   if part.is_empty or part.geom_type!='LineString':continue
   aa,bb=list(part.coords)[0],list(part.coords)[-1]
   n=max(1,math.ceil(math.dist(aa,bb)/1.6)) if min(aa[0],bb[0])<208 else 1
   for j in range(n):
    u=j/n;v=(j+1)/n;pa=tuple(aa[k]+(bb[k]-aa[k])*u for k in range(2));pb=tuple(aa[k]+(bb[k]-aa[k])*v for k in range(2))
    rail(B,pa,pb,deck_y(pa[0]),deck_y(pb[0]),posts=tuple(side for side in [-1,1] if (side<0 and j==0) or (side>0 and j==n-1)))
 # Columns flank approach and sit outside its clear lane, as in Google Earth.
 column(B,180.0,-704.7,False);column(B,179.5,-679.7,True)
 # Square-ticket pavilion north of the approach, with stepped entablature/hip roof.
 # Coping tangent from mapped shore. Keep the complete base on the dry side.
 dx,dz=191.679-178.513,-731.258+707.012
 angle=math.atan2(-dz,dx);length=math.hypot(dx,dz)
 kx,kz=184.82+dz/length*2.55,-718.62-dx/length*2.55
 K=Frame(B,kx,kz,angle,y=.24)
 for y,w,h in [(.25,4.8,.5),(.8,4.1,.6),(3.15,3.7,4.1),(5.4,4.8,.45),(6.0,3.85,.72),(6.55,4.65,.24)]:K.box('ivory',(0,y,0),(w,h,w),y<5.5)
 for side in range(4):
  F=Frame(B,kx,kz,angle+side*math.pi/2,y=.24)
  F.box('darkglass',(0,3.3,-1.89),(2.4,2.45,.10));F.box('blue',(0,5.99,-1.95),(2.9,.54,.08))
  F.box('ivory',(0,3.6,-2.05),(.15,2.65,.15))
  for q in [-1,1]:F.box('ivory',(q*1.5,3.2,-2),( .25,4.1,.25))
 for a,b in zip([(-2.1,-2.1),(2.1,-2.1),(2.1,2.1),(-2.1,2.1)],[ (2.1,-2.1),(2.1,2.1),(-2.1,2.1),(-2.1,-2.1)]):B.face('copper',[K.p(a[0],6.7,a[1]),K.p(b[0],6.7,b[1]),K.p(0,8.05,0)])
 K.lathe('gold',0,0,[(8.05,.11),(8.3,.3),(8.65,.14),(8.9,0)],12)
 B.detail=0
 return {'eye':[121,64,-788],'target':[221,14,-693]}
