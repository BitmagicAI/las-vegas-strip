"""Two cooling fan cells within mapped Forum Shops roof well; visual reference only."""
from common import *
from forum_shops import facade_frame
KEY='forumCoolingTowers';IDS=['way/1380575885']
def exterior(B):
 B.property=KEY+'-exterior';B.source='forum-roof-cooling';B.detail=0
 p=footprint(IDS[0]);base=16.8
 B.planar('fct-roof-paint',p,base,True)
 # South/east edges share the mall walls; north/west exposed service walls
 # support the roof platform. Match only those exposed edges, no duplicate shell.
 parent=footprint('way/34068416')
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  line=LineString([a,b])
  if line.difference(parent.boundary.buffer(.02)).length<.1:continue
  B.face('fct-concrete-paint',[(a[0],.24,a[1]),(b[0],.24,b[1]),(b[0],base,b[1]),(a[0],base,a[1])],True)
  F,L,_,_=facade_frame(B,a,b,p,.035)
  for y in [4.2,8.4,12.6,16.65]:F.box('fct-foot-paint',(L/2,y,0),(L,.12,.08))
  if L>8:
   for x in np.arange(1,L-1,2):
    F.box('fct-louver-paint',(x,2.3,-.04),(1.5,2.7,.07))
    for y in np.arange(1.05,3.6,.18):F.box('fct-metal-paint',(x,y,-.10),(1.45,.07,.08))
 for z in [-416.35,-409.8]:
  F=Frame(B,-160.8,z,yaw=-.021,y=base)
  F.box('fct-metal-paint',(0,1.25,0),(10.2,2.5,5.6),True)
  F.box('fct-dark-paint',(0,2.53,0),(9.7,.06,5.1))
  for u in [-4.85,4.85]:F.box('fct-rail-paint',(u,2.64,0),(.16,.2,5.5))
  for w in [-2.62,2.62]:F.box('fct-rail-paint',(0,2.64,w),(10,.2,.16))
  F.lathe('fct-metal-paint',.5,0,[(2.55,2.3),(2.9,2.3),(3.0,2.2)],48)
  # Dark fan opening with a recessed hub and six pitched blades.
  F.lathe('fct-dark-paint',.5,0,[(2.56,2.18),(2.58,2.18)],48)
  F.lathe('fct-rail-paint',.5,0,[(2.6,.4),(2.86,.4)],24)
  for a in np.arange(6)*math.tau/6:
   def pt(r,t,y):return F.p(.5+r*math.cos(a+t),y,r*math.sin(a+t))
   B.face('fct-fan-paint',[pt(.4,-.08,2.83),pt(2.1,-.06,2.76),pt(2.0,.23,2.92),pt(.4,.20,2.91)])
  for w in [-2.81,2.81]:
   for y in np.arange(.35,2.4,.18):F.box('fct-louver-paint',(0,y,w),(9.7,.075,.10))
  for u in [-3.7,-2.6]:
   F.path('fct-pipe-paint',[(u,.25,-3),(u,2.15,-3),(u,2.15,-2.6),(u,2.15,-.8)],.12,8)
  for u in [-4.7,4.7]:
   for w in [-2.3,2.3]:F.box('fct-foot-paint',(u,.12,w),(.7,.24,.7))
 # Edge handrail on roof-service side only; fan housings remain closed solid objects.
 for z in np.arange(-419,-406,1.5):B.box('fct-rail-paint',(-167.15,17.35,z),(.07,1.1,.07))
 for y in [17.35,17.9]:B.path('fct-rail-paint',[(-167.15,y,-419.3),(-167.15,y,-406.4)],.045,8)
 samples=[]
 for x in np.arange(-165.8,-155.7,.7):
  for z in np.arange(-419,-406.5,.7):
   if p.buffer(-.2).contains(Point(x,z)):samples.append([float(x),20.3,float(z)])
 # Exterior roof-maintenance lane, not a public entrance or interior access claim.
 route=[[-166.65,base,-418.8],[-166.65,base,-406.8]]
 Path('build/city-exteriors/forum-cooling-towers-samples.json').write_text(json.dumps(samples));Path('build/city-exteriors/forum-cooling-towers-stairs.json').write_text(json.dumps([route]))
 return dict(key=KEY,name='Forum Shops twin cooling towers',center=[-161,17,-413],bounds=list(p.bounds),structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
