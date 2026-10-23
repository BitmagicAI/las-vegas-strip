"""Main/Wyoming restaurant exterior from January2026 Street View.
Measured mapped plan; vertical dimensions and rear services are estimates.
"""
from common import *
from forum_shops import facade_frame
KEY='jackMainWyoming';IDS=['way/689003962']
def exterior(B):
 B.property=KEY+'-exterior';B.source='podium/jack-main-wyoming';B.detail=0;p=footprint(IDS[0]);W=Frame(B,0,0,y=0)
 B.shell(p,.18,3.45,'jm-cream-stucco',roof=False)
 outer=p.buffer(.45,join_style=2);inner=p.buffer(-1.3,join_style=2)
 band=outer
 for d in np.arange(.25,1.76,.25):
  inset=outer.buffer(-float(d),join_style=2)
  for poly in parts(band.difference(inset)):
   for t in triangles(poly):B.upface('jm-roof-paint',[(x,3.65+min(1,outer.boundary.distance(Point(x,z))/1.75)*1.2,z)for x,z in list(t.exterior.coords)[:-1]],True)
  band=inset
 B.planar('jm-membrane-paint',inner,4.85,True)
 edges=[facade_frame(B,a,b,p,0)for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:])];F,L,_,_=max([e for e in edges if e[2]<-.6],key=lambda e:e[1]);du=L*.38
 routes=[]
 for G,ll,nx,nz in edges:
  G.box('jm-cream-stucco',(ll/2,3.4,-.17),(ll,.48,.4));G.box('jm-gray-stone',(ll/2,.42,-.06),(ll,.45,.15))
  if ll<2:continue
  if nx<-.6 or nz>.6:
   for u in np.arange(1.2,ll-.7,2.6):
    if G is F and abs(u-du)<2:continue
    G.box('jm-frame-paint',(float(u),1.75,-.15),(2.25,2.05,.12));G.box('jm-glass',(float(u),1.75,-.23),(2.08,1.88,.04));G.box('jm-frame-paint',(float(u),1.75,-.27),(.045,1.88,.04))
    # Original menu poster panels: stylized typography, no copied reference pixels.
    if nx<-.6:
     G.box('jm-menu-white-paint',(float(u),1.45,-.29),(.7,.9,.025));G.box('jm-red-paint',(float(u),1.73,-.31),(.64,.18,.02));G.text('MENU',(float(u),1.7,-.33),.12,'jm-white-letter')
     for yy in [1.2,1.32,1.44]:G.box('jm-menu-ink-paint',(float(u),yy,-.32),(.46,.025,.015))
  elif nx>.6:
   G.box('jm-frame-paint',(ll*.45,1.55,-.15),(1.5,1.15,.12));G.box('jm-glass',(ll*.45,1.55,-.23),(1.34,1,.04));G.box('jm-frame-paint',(ll*.45,1.0,-.35),(1.9,.1,.55))
   G.box('jm-dark-paint',(ll*.45,2.4,-.7),(2.2,.12,1.4))
  elif ll>4:
   G.box('jm-door-paint',(ll*.6,1.3,-.08),(1.05,2.24,.12));G.box('jm-vent-paint',(ll*.22,2.4,-.09),(1.2,.5,.12))
 # Front entrance blade with solid triangular crown, distinct from roof mansard.
 F.box('jm-red-paint',(du,2.7,-.38),(3.6,5.0,.5),True)
 for depth in [-.65,-.11]:B.face('jm-red-paint',[F.p(du-1.8,5.2,depth),F.p(du+1.8,5.2,depth),F.p(du,6.55,depth)])
 for side in [-1,1]:B.face('jm-red-paint',[F.p(du+side*1.8,5.2,-.65),F.p(du,6.55,-.65),F.p(du,6.55,-.11),F.p(du+side*1.8,5.2,-.11)])
 F.box('jm-frame-paint',(du,1.55,-.67),(2.25,2.72,.09));F.box('jm-glass',(du,1.55,-.73),(2.08,2.55,.03));F.box('jm-frame-paint',(du,1.55,-.77),(.06,2.55,.04))
 for u in [du-.12,du+.12]:F.tube('jm-handle-paint',(u,1.1,-.84),(u,1.7,-.84),.025,8)
 F.box('jm-red-sign-paint',(du,4.6,-.69),(1.75,1.5,.08));F.text('Jack',(du,4.58,-.75),.48,'jm-white-letter');F.text('IN THE BOX',(du,4.16,-.75),.13,'jm-white-letter');F.text('1531',(L-.65,3.0,-.4),.18,'jm-dark-letter')
 # Two small hipped/gabled corner markers above the main fascia.
 for u in [1.3,L-1.3]:
  for side in [-1,1]:B.face('jm-roof-paint',[F.p(u+side*.9,4.65,-.05),F.p(u+side*.9,4.65,1.6),F.p(u,5.85,1.6),F.p(u,5.85,-.05)])
  for d in [-.05,1.6]:B.face('jm-red-paint',[F.p(u-.9,4.65,d),F.p(u+.9,4.65,d),F.p(u,5.85,d)])
 # Shallow roof courses, kept off the solid surface.
 for G,ll,nx,nz in edges:
  if ll<3:continue
  for t in [.2,.45,.7]:G.box('jm-roof-seam-paint',(ll/2,3.66+t*1.2,-.45+t*1.75),(max(.2,ll-2*t),.025,.035))
 apron=p.buffer(1.3,join_style=2).difference(p);B.planar('jm-concrete',apron,.18,True)
 path=F.poly([(du-1.25,0),(du+1.25,0),(du+1.25,-11),(du-1.25,-11)]).difference(p);B.planar('jm-concrete',path.difference(apron),.18,True)
 routes.append([F.p(du,.18,-10.5),F.p(du,.18,-2),F.p(du,.18,-1.05)])
 parking=box(1722,-4080,1759,-4062).difference(apron);drive=box(1753,-4062,1759,-4038).difference(apron)
 B.planar('jm-asphalt',parking.union(drive),.1,True)
 for x in np.arange(1724,1757,2.8):W.box('jm-line-paint',(float(x),.115,-4076),(.08,.015,5.1))
 for u in [1.5,L-1.5]:
  F.box('jm-bed-stone',(u,.34,-6.5),(3,.32,3),True);F.box('jm-gravel-paint',(u,.51,-6.5),(2.8,.025,2.8))
 # Detached roadside pylon at south-west setback.
 F.box('jm-dark-paint',(-1,3.6,-9),(.3,7.0,.3),True);F.box('jm-red-sign-paint',(-1,6.65,-9),(2.05,2,.30));F.text('Jack',(-1,6.65,-9.17),.5,'jm-white-letter');F.text('IN THE BOX',(-1,6.12,-9.17),.13,'jm-white-letter');F.box('jm-red-sign-paint',(-1,5.05,-9),(2.4,.65,.3));F.text('DRIVE THRU',(-1,5.0,-9.17),.19,'jm-white-letter')
 for x,z in [(1744,-4049),(1734,-4054)]:W.box('jm-service-paint',(x,5.25,z),(1.6,.8,1.2));W.box('jm-vent-paint',(x,5.66,z),(1.4,.03,1))
 samples=[]
 for x in np.arange(p.bounds[0]+.5,p.bounds[2],.7):
  for z in np.arange(p.bounds[1]+.5,p.bounds[3],.7):
   if p.buffer(-.3).contains(Point(x,z)):samples.append([float(x),min(4.85,3.65+outer.boundary.distance(Point(x,z))/1.75*1.2)+.4,float(z)])
 Path('build/city-exteriors/jack-main-wyoming-samples.json').write_text(json.dumps(samples));Path('build/city-exteriors/jack-main-wyoming-stairs.json').write_text(json.dumps(routes))
 return dict(key=KEY,name='Jack in the Box · Main and Wyoming',center=[1740,0,-4052],bounds=[1714,-4082,1761,-4036],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
