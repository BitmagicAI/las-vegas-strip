"""Wyndham Grand Desert: three mapped towers, corrected adjoining heights, terracotta crowns."""
from common import *
from forum_shops import facade_frame
KEY='grandDesert';IDS=['way/1226448921','relation/6138879']
def hip(B,x,z,w,d,y,rise):
 c=[(x-w/2,y,z-d/2),(x+w/2,y,z-d/2),(x+w/2,y,z+d/2),(x-w/2,y,z+d/2)];r=[(x-w*.15,y+rise,z),(x+w*.15,y+rise,z)]
 for pts in [[c[0],c[1],r[1],r[0]],[c[1],c[2],r[1]],[c[2],c[3],r[0],r[1]],[c[3],c[0],r[0]]]:B.upface('gd-tile',pts,True)
def exterior(B):
 B.property=KEY+'-exterior';B.source='grand-desert';B.detail=0
 east=list(parts(footprint(IDS[1])));east.sort(key=lambda p:p.centroid.y)
 entries=[(footprint(IDS[0]),44,[(862,1046),(936,1046)]),(east[0],46,[(1027,1014),(1027,962),(1054,937),(1104,937)]),(east[1],37,[(1025,1040),(1090,1040),(1115,1015),(1115,966)])]
 for index,(p,h,caps) in enumerate(entries):
  base=3.2 if index==0 else 10
  B.shell(p,0,base,'gd-gray',roof=False);B.shell(p,base,h,'gd-cream',roof=False);B.planar('gd-roof',p,h+.025,True)
  ps=list(p.exterior.coords)
  for a,b in zip(ps,ps[1:]):
   F,L,*_=facade_frame(B,a,b,p,0)
   if L<.3:continue
   for y in [base,h-3.1,h-.18]:F.box('gd-trim',(L/2,y,-.16),(L,.24,.35))
   if L>12:
    n=max(1,round(L/3.65));w=L/n
    for k in range(n):
     x=(k+.5)*w
     for y in np.arange(4.5,h-1.7,3.0):
      F.box('gd-glass',(x,y,-.13),(1.32,1.7,.05))
      F.box('gd-frame',(x,y,-.19),(.06,1.7,.06));F.box('gd-frame',(x,y-.25,-.19),(1.33,.055,.06))
      for xx in [x-.72,x+.72]:F.box('gd-trim',(xx,y,-.17),(.1,1.9,.1))
      F.box('gd-trim',(x,y-.91,-.21),(1.52,.12,.22))
      F.box('gd-reveal',(x,y+.91,-.18),(1.52,.1,.12))
     if index>0 and k%4==0:F.box('gd-trim',(x-w*.48,(h+base)/2,-.15),(.28,h-base,.25))
     F.box('gd-glass',(x,1.5,-.13),(1.55,1.7,.05))
   elif L>4:
    # Blank stair/service end walls are intentional; small ventilation openings.
    for y in np.arange(5,h-3,6):F.box('gd-vent',(L*.5,y,-.15),(.3,.65,.05))
   F.box('gd-trim',(L/2,h+.3,0),(L,.6,.45))
  for x,z in caps:
   # Low roof pavilions, each independent of the nonrectangular tower plan.
   q=p.intersection(box(x-7.5,z-8,x+7.5,z+8))
   if q.is_empty:continue
   B.shell(q,h+.05,h+1.4,'gd-cream',roof=False,solid=False)
   bx,bz,ex,ez=q.bounds;hip(B,(bx+ex)/2,(bz+ez)/2,ex-bx+.4,ez-bz+.4,h+1.4,3.0)
  for t in [.25,.5,.75]:
   q=p.representative_point();x,z=q.x+(t-.5)*6,q.y
   if p.contains(box(x-1.3,z-1.3,x+1.3,z+1.3)):B.box('gd-service',(x,h+.7,z),(2.3,1.3,2.3))
 # Main sheltered arrival facing Harmon, north edge of the north tower.
 p=east[0];a=(1046.954,927.236);b=(1114.282,927.325);F,L,*_=facade_frame(B,a,b,p,0);x=L*.55
 F.box('gd-trim',(x,4.8,-5),(14,.3,10),True)
 for xx in [x-6,x+6]:F.box('gd-gray',(xx,2.33,-8.8),(.7,4.66,.7),True)
 F.text('WYNDHAM GRAND DESERT',(x,4.55,-10.2),.38,'gd-sign')
 # Courtyard pools and paved surrounds observed between the two eastern wings.
 for x,z,rx,rz in [(1060,982,10,14),(1082,1010,11,7)]:
  pool=scale(Point(x,z).buffer(1,24),rx,rz,origin=(x,z));deck=pool.buffer(4)
  B.planar('gd-paving',deck.difference(pool),.28,True);B.planar('gd-coping',pool.buffer(.45).difference(pool),.36,True)
  B.planar('grand_desert_pool',pool,.20);B.planar('gd-pool-tile',pool,-1.1,True)
  ring=list(pool.exterior.coords)
  for a,b in zip(ring,ring[1:]):B.face('gd-pool-tile',[(a[0],-1.1,a[1]),(b[0],-1.1,b[1]),(b[0],.35,b[1]),(a[0],.35,a[1])],True)
 return dict(key=KEY,name='Wyndham Grand Desert three towers',center=[995,0,990],bounds=[840,912,1142,1068],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],views={})
