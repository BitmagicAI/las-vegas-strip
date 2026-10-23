"""City Market & Liquor: mapped footprint, January2022 storefront reference.
Roof heights estimated. No interior, advertising or private contact details.
"""
from common import *
from forum_shops import facade_frame
KEY='cityMarketLiquor'
def exterior(B):
 B.property=KEY+'-exterior';B.source='podium/store';B.detail=0
 p=footprint('way/364845148');B.shell(p,.18,3.35,'cm-white-brick-paint',roof=False);B.planar('cm-roof-paint',p,3.36,True)
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  F,L,nx,nz=facade_frame(B,a,b,p,.025)
  front=nz>.7
  F.box('cm-white-paint',(L/2,3.25,-.09),(L,.36,.22))
  if nz>-.7:
   # Miter both roof corners; independent full-width slopes intersect visibly.
   def near(poly,v):return min(list(poly.exterior.coords)[:-1],key=lambda q:math.dist(q,v))
   outer=p.buffer(.45,join_style=2);inner=p.buffer(-1.2,join_style=2)
   oa,ob=near(outer,a),near(outer,b);ia,ib=near(inner,a),near(inner,b)
   B.upface('cm-red-roof-paint',[(oa[0],3.45,oa[1]),(ob[0],3.45,ob[1]),(ib[0],4.65,ib[1]),(ia[0],4.65,ia[1])])
   for t in np.linspace(0,1,7):
    aa=(oa[0]+(ia[0]-oa[0])*t,3.46+1.2*t,oa[1]+(ia[1]-oa[1])*t)
    bb=(ob[0]+(ib[0]-ob[0])*t,3.46+1.2*t,ob[1]+(ib[1]-ob[1])*t)
    B.tube('cm-seam-paint',aa,bb,.018,4)
  if front:
   for u0,u1 in [(.65,L/2-1.05),(L/2+1.05,L-.65)]:
    c=(u0+u1)/2;width=u1-u0
    F.box('cm-gray-paint',(c,.65,-.14),(width,.85,.08))
    for y,h,mat in [(1.35,.55,'cm-red-paint'),(1.76,.25,'cm-white-paint'),(2.18,.6,'cm-blue-paint'),(2.7,.45,'cm-glass')]:F.box(mat,(c,y,-.17),(width,h,.06))
    for u in np.linspace(u0,u1,4):F.box('cm-aluminum-paint',(u,1.65,-.23),(.055,2.85,.1))
   c=L/2
   F.box('cm-dark-paint',(c,1.64,-.17),(2.05,2.92,.1))
   for u in [c-.47,c+.47]:
    F.box('cm-aluminum-paint',(u,1.43,-.24),(.93,2.5,.08));F.box('cm-glass',(u,1.48,-.3),(.81,2.29,.03));F.tube('cm-aluminum-paint',(u,1,-.35),(u,1.6,-.35),.025,8)
   F.text('515',(c,3.04,-.22),.17,'cm-dark-letter')
   F.box('cm-white-paint',(c,4.12,-.52),(6.5,1.55,.15))
   F.text('CITY MARKET & LIQUOR',(c,4.5,-.61),.41,'cm-red-letter');F.text('BEER • WINE',(c,4.02,-.61),.32,'cm-red-letter');F.text('GROCERIES',(c,3.66,-.61),.25,'cm-blue-letter')
   B.source='podium/parking'
   for u in np.arange(1,L-1,3):
    F.box('cm-wheelstop-concrete',(u,.28,-3),(1.7,.2,.18),True)
    F.box('cm-line-paint',(u+1.4,.115,-5.3),(.08,.015,5.6))
   for u in [.3,L-.3]:F.tube('cm-bollard-paint',(u,.1,-2.4),(u,1,-2.4),.08,10)
   B.source='podium/store'
  else:
   F.box('cm-gray-paint',(L/2,.48,-.09),(L,.6,.12))
   # Masonry coursing and a simple rear service opening; inferred, unbranded.
   for y in np.arange(.9,3.1,.25):F.box('cm-mortar-paint',(L/2,y,-.13),(L,.012,.02))
   if nz<-.7:
    F.box('cm-door-paint',(L*.7,1.3,-.16),(1.05,2.24,.08));F.box('cm-vent-paint',(L*.23,2.3,-.15),(1,.45,.1))
 W=Frame(B,0,0,y=0)
 for x,z in [(1961,-3959),(1973,-3958)]:
  W.box('cm-service-paint',(x,3.72,z),(1.3,.7,1.1));W.box('cm-vent-paint',(x,4.08,z),(1,.025,.8))
 site=p.buffer(1.4,join_style=2).difference(p);parking=box(1956,-3949,1977,-3940).difference(p)
 B.planar('cm-paving-concrete',site,.18,True);B.planar('cm-asphalt',parking.difference(site),.1,True)
 samples=[]
 for x in np.arange(1956,1978,.6):
  for z in np.arange(-3964,-3940,.6):
   q=Point(x,z)
   if site.buffer(-.36).contains(q):samples.append([float(x),.18,float(z)])
 Path('build/city-exteriors/city-market-liquor-samples.json').write_text(json.dumps(samples))
 return dict(key=KEY,name='City Market & Liquor',center=[1967,0,-3955],bounds=[1955,-3965,1979,-3940],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
