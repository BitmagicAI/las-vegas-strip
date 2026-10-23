"""Boston Pizza: January 2026 street-view facade, mapped angled footprint."""
from common import *
from forum_shops import facade_frame
KEY='bostonPizza'
def exterior(B):
 B.property=KEY+'-exterior';B.source='podium/restaurant';B.detail=0;W=Frame(B,0,0,y=0)
 p=footprint('way/1363694313');B.shell(p,.15,4.4,'bp-stucco',roof=False);B.planar('bp-flat-roof-paint',p,4.3,True)
 ps=list(p.exterior.coords)
 for a,b in zip(ps,ps[1:]):
  G,L,nx,nz=facade_frame(B,a,b,p,.035)
  G.box('bp-coping',(L/2,4.43,-.02),(L,.13,.22));G.box('bp-base',(L/2,.30,-.04),(L,.22,.1))
  west=nx<-.7
  if west and L>9:
   G.box('bp-black',(L/2,1.75,-.11),(L-.5,2.8,.13))
   G.box('bp-gray-panel',(L*.27,1.75,-.2),(L*.45,2.65,.04))
   G.box('bp-red',(L*.68,1.6,-.22),(1.12,2.6,.06))
   G.box('bp-glass',(L*.68,2,-.27),(.9,1.65,.025))
   G.box('bp-glass',(L*.85,1.75,-.22),(2.0,2.6,.04))
   G.text('BOSTON PIZZA',(L*.70,3.62,-.18),.52,'bp-red-letter')
   G.text('385-2595',(L*.20,3.62,-.18),.46,'bp-red-letter')
   G.box('bp-fascia',(L/2,3.15,-.3),(L,.12,.6))
   for u in np.arange(.5,L,.35):
    if .57*L<u<.77*L:continue
    G.box('bp-rail',(u,.75,-1.1),(.025,1.15,.025))
   for lo,hi in [(.3,L*.57),(L*.77,L-.3)]:
    for y in [.3,1.3]:G.box('bp-rail',((lo+hi)/2,y,-1.1),(hi-lo,.035,.035))
   for u in [L*.85,L*.52]:G.text('PIZZA',(u,2.4,-.26),.28,'bp-letter')
  elif west and L>5:
   G.box('bp-stucco',(L/2,4.68,0),(L,.55,.12),True)
   G.box('bp-coping',(L/2,4.98,0),(L,.1,.22))
   G.box('bp-frame',(L*.78,1.55,-.10),(1.16,2.65,.1));G.box('bp-red',(L*.78,1.55,-.17),(1.02,2.5,.05))
   G.box('bp-glass',(L*.78,2.35,-.21),(.35,.35,.03))
   for u,w in [(L*.22,2.0),(L*.94,.45)]:
    G.box('bp-frame',(u,1.75,-.09),(w+.15,1.4,.1));G.box('bp-glass',(u,1.75,-.17),(w,1.25,.04));G.box('bp-frame',(u,1.75,-.22),(.045,1.3,.04))
   G.box('bp-red',(L*.23,3.7,-.1),(2.8,1.1,.1));G.box('bp-sign',(L*.23,3.7,-.17),(2.65,.95,.03))
   G.text('BOSTON PIZZA',(L*.23,3.65,-.2),.21,'bp-red-letter');G.text('385-2595',(L*.23,3.97,-.2),.3,'bp-black')
   G.text('1507',(L*.85,4.35,-.1),.24,'bp-red-letter')
   for u in [1,L-1]:
    G.tube('bp-metal',(u,4.9,0),(u,5.3,-.55),.025,8);G.box('bp-light',(u,5.25,-.55),(.32,.15,.22))
  elif nx>.5:
   G.box('bp-service',(L*.5,1.5,-.09),(1,2.5,.1))
 for x,z in [(1986,-4128),(1988,-4122)]:
  W.box('bp-service',(x,4.8,z),(2.8,1,2));W.box('bp-black',(x,5.32,z),(2.4,.04,1.6))
 W.tube('bp-metal',(1981,4.3,-4128),(1981,5.5,-4128),.23,16)
 site=p.buffer(1.8,join_style=2).difference(p);B.planar('bp-paving',site,.15,True)
 # Door approach is unobstructed; rail stops on either side of storefront entry.
 samples=[]
 for x in np.arange(1964,1996,.8):
  for z in np.arange(-4139,-4114,.8):
   if site.buffer(-.4).covers(Point(x,z)):samples.append([float(x),.15,float(z)])
 Path('build/city-exteriors/boston-pizza-samples.json').write_text(json.dumps(samples))
 return dict(key=KEY,name='Boston Pizza Vegas',center=[1982,0,-4126],bounds=[1964,-4139,1996,-4114],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
