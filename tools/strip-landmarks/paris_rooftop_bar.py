"""Small mapped rooftop bar pavilion. Floor datum matches retained Paris terrace.
Placement mapped; dimensions/ornament estimated from aerial and official Chéri photos.
"""
from common import *
KEY='parisRooftopBar';IDS=['way/1424222076'];D=6.64

def exterior(B):
 B.property=KEY+'-exterior';B.source='paris-rooftop-bar';B.detail=0
 p=footprint(IDS[0]);x0,z0,x1,z1=p.bounds;cz=(z0+z1)/2;W=Frame(B,0,0,y=0)
 # Open serving face on west, solid sides/back and real roof/soffit.
 B.shell(p,D,10.15,'prb-wall-stucco',openings=[dict(p=[x0,D,cz],yaw=math.pi/2,width=z1-z0-.65,height=3.15)],roof=False)
 B.planar('prb-roof-paint',p.buffer(.12,join_style=2),10.28,True)
 B.shell(p.buffer(.12,join_style=2),10.15,10.28,'prb-coping-paint',roof=False)
 for t in triangles(p):B.face('prb-ceiling-paint',[(x,10.02,z)for x,z in list(t.exterior.coords)[:-1]][::-1],True)
 # Existing terrace provides the floor; only the northern overhang needs a closure.
 floor=p.intersection(box(x0-1,z0-1,x1+1,417));B.planar('prb-floor-tile',floor,D,True)
 B.shell(floor,D-.25,D,'prb-wall-stucco',roof=False)
 F=Frame(B,x0,cz,math.pi/2,y=D);L=z1-z0
 for u in [-L/2+.16,L/2-.16]:F.box('prb-trim-paint',(u,1.72,.02),(.22,3.44,.28),True)
 F.box('prb-trim-paint',(0,3.24,-.12),(L,.26,.36))
 # Venue identity of this small mapped roof is uncertain; omit speculative branding.
 # Dark stone countertop over pale framed panels, as in venue photographs.
 F.box('prb-panel-paint',(0,.55,.9),(L-1,1.1,.7),True)
 F.box('prb-counter-paint',(0,1.14,.9),(L-.8,.12,.92),True)
 for u in np.arange(-L/2+.7,L/2-.5,1.15):
  for y in [.12,.96]:F.box('prb-trim-paint',(u,y,.53),(1.02,.045,.035))
  for du in [-.51,.51]:F.box('prb-trim-paint',(u+du,.54,.53),(.035,.84,.035))
 # Green-backed open shelves with brass uprights, no extra runtime lights.
 back=x1-x0-.35
 F.box('prb-green-paint',(0,1.92,back),(L-.75,2.65,.10))
 for u in np.arange(-L/2+.5,L/2,.9):F.box('prb-brass-paint',(u,1.92,back-.1),(.055,2.65,.10))
 for y in [.72,1.5,2.3,3.1]:F.box('prb-brass-paint',(0,y,back-.22),(L-.7,.045,.42))
 for row,y in enumerate([.77,1.55,2.35]):
  for j,u in enumerate(np.arange(-L/2+.65,L/2-.5,.31)):
   h=.23+.05*((j+row)%3);F.lathe('prb-bottle-paint',float(u),back-.22,[(y,.045),(y+h*.65,.045),(y+h*.77,.018),(y+h,.018)],8)
   F.box('prb-label-paint',(u,y+h*.35,back-.269),(.063,.082,.007))
 # Slender framed stools leave an uninterrupted public aisle in front.
 for u in np.arange(-L/2+1,L/2-.5,1.35):
  F.box('prb-seat-paint',(u,.77,-.55),(.42,.06,.4))
  for a in [-.19,.19]:
   for b in [-.17,.17]:F.tube('prb-metal-paint',(u+a,.02,-.55+b),(u+a,.76,-.55+b),.022,7)
  F.path('prb-metal-paint',[(u-.2,.78,-.75),(u-.2,1.1,-.77),(u+.2,1.1,-.77),(u+.2,.78,-.75)],.023,8)
  F.box('prb-seat-paint',(u,.98,-.77),(.38,.19,.025))
  F.path('prb-metal-paint',[(u-.19,.28,-.72),(u+.19,.28,-.72),(u+.19,.28,-.38),(u-.19,.28,-.38)],.019,6)
 # Flat roof perimeter flashing and compact mechanical units visible in aerial.
 for zz in [z0+2.4,z1-2.3]:
  W.box('prb-service-paint',(x1-1,10.62,zz),(1.1,.65,1.55))
  for j in range(7):W.box('prb-vent-paint',(x1-1,10.956,zz-.58+j*.18),(.85,.016,.06))
 samples=[[x,D+.7,z]for x in [x0+.3,x0+2,x1-.3]for z in np.arange(z0+.3,z1,.65)]
 routes=[[[38.5,D,418],[38.5,D,425]],[[x0+2.5,D,417.5],[x0+2.5,D,425]]]
 Path('build/city-exteriors/paris-rooftop-bar-samples.json').write_text(json.dumps(samples));Path('build/city-exteriors/paris-rooftop-bar-stairs.json').write_text(json.dumps(routes))
 return dict(key=KEY,name='Paris small rooftop bar pavilion',center=[(x0+x1)/2,0,cz],bounds=list(p.buffer(2).bounds),structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
