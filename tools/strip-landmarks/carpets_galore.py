"""1601 S Main: January2026 street references and mapped L footprint.
Single-storey exterior. Heights/rear/service equipment estimated.
"""
from common import *
from forum_shops import facade_frame
KEY='carpetsGalore'
def exterior(B):
 B.property=KEY+'-exterior';B.source='podium/store';B.detail=0
 p=footprint('way/689003955');B.shell(p,.18,5.6,'cga-white-paint',roof=False);B.planar('cga-roof-paint',p,5.55,True)
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  F,L,nx,nz=facade_frame(B,a,b,p,.04)
  north=nz<-.7 and (a[1]+b[1])/2<-4000
  west=nx<-.7 or (nz<-.7 and not north)
  F.box('cga-cap-paint',(L/2,5.62,-.03),(L,.12,.22))
  F.box('cga-dark-brick',(L/2,.58,-.06),(L,.8,.14))
  if west:
   count=max(2,round(L/3.7))
   for j in range(count):
    u=(j+.5)*L/count
    F.box('cga-black-paint',(u,2,-.12),(L/count-.17,2.55,.1))
    F.box('cga-glass',(u,2,-.19),(L/count-.38,2.25,.045))
    F.box('cga-frame-paint',(u-L/count/2,2,-.22),(.09,2.7,.1))
    F.box('cga-gray-paint',(u,1.03,-.25),(L/count-.4,.32,.03))
   if L>6:
    F.text('CARPETS GALORE',(L/2,4.68,-.19),min(1.4,L/11),'cga-blue-letter')
    F.text('FLOORING • TILE • WOOD',(L/2,3.69,-.2),min(.34,L/35),'cga-black-letter')
    u=L*.75;F.box('cga-frame-paint',(u,1.55,-.26),(1.14,2.72,.08));F.box('cga-glass',(u,1.55,-.32),(1,2.57,.04));F.tube('cga-frame-paint',(u+.34,1.08,-.36),(u+.34,1.65,-.36),.025,8)
   F.text('1601',(L-.65,5.33,-.17),.23,'cga-black-letter')
  elif north:
   # East narrow masonry bay and western corrugated warehouse wall.
   blue=6.3
   F.box('cga-blue-brick-paint',(L-blue/2,2.87,-.1),(blue,5.35,.13))
   for u in np.arange(.1,L-blue,.27):F.box('cga-rib-paint',(u,3.16,-.14),(.026,4.75,.08))
   door=L-blue-2.2
   F.box('cga-black-paint',(door,1.7,-.21),(3.8,3.15,.12));F.box('cga-shutter-paint',(door,1.72,-.29),(3.55,3.05,.06))
   for y in np.arange(.3,3.2,.12):F.box('cga-shutter-line-paint',(door,y,-.33),(3.5,.015,.012))
   F.box('cga-service-paint',(door-2.55,1.28,-.21),(1,2.2,.1))
   F.box('cga-glass',(L-3,4.7,-.2),(2.4,.56,.08))
   for u in [L-4.3,L-1.1]:F.box('cga-glass',(u,1.6,-.22),(1.55,2.14,.1))
   signwidth=max(5,door-2.5)
   F.text('CARPETS GALORE',(signwidth/2+.5,4.35,-.23),min(1.55,signwidth/8.5),'cga-blue-letter')
   F.text('WOOD • TILE • VINYL',(signwidth/2+.5,2,-.24),.38,'cga-red-letter')
   # Shallow gable at the east masonry section; all ends closed.
   for q,r in [((L-blue,5.6),(L-blue/2,6.25)),((L-blue/2,6.25),(L,5.6))]:
    u,y=q;uu,yy=r
    B.upface('cga-roof-paint',[F.p(u,y,0),F.p(uu,yy,0),F.p(uu,yy,30.1),F.p(u,y,30.1)])
   B.face('cga-white-paint',[F.p(L-blue,5.6,-.08),F.p(L,5.6,-.08),F.p(L-blue/2,6.25,-.08)])
  else:
   for y in np.arange(1,5.4,.3):F.box('cga-mortar-paint',(L/2,y,-.09),(L,.014,.025))
   if L>20:
    for u in [L*.25,L*.7]:
     F.box('cga-service-paint',(u,1.45,-.14),(1.1,2.5,.12));F.box('cga-vent-paint',(u+2,4.5,-.16),(1.4,.6,.16))
 W=Frame(B,0,0,y=0)
 for x,z in [(1725,-3987),(1738,-3992),(1742,-4006)]:
  if p.buffer(-1).contains(Point(x,z)):
   W.box('cga-service-paint',(x,5.93,z),(1.8,.7,1.4));W.box('cga-vent-paint',(x,6.3,z),(1.5,.04,1.1))
 # The forecourt is paved, not a new building across the L-shaped recess.
 site=p.buffer(1.4,join_style=2).union(box(1718,-4013,1733,-3980)).difference(p)
 B.planar('cga-paving-concrete',site,.18,True)
 samples=[]
 for x in np.arange(1718,1759,.7):
  for z in np.arange(-4014,-3978,.7):
   if site.buffer(-.36).contains(Point(x,z)):samples.append([float(x),.18,float(z)])
 Path('build/city-exteriors/carpets-galore-samples.json').write_text(json.dumps(samples))
 return dict(key=KEY,name='Carpets Galore 1601 S Main',center=[1741,0,-3995],bounds=[1717,-4015,1759,-3978],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
