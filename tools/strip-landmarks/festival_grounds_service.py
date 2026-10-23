"""Mapped Festival Grounds service building. Roof corroborated; concealed walls estimated."""
from common import *
from forum_shops import facade_frame
KEY='festivalGroundsService';YAW=-math.atan2(1.336,47.392)
def exterior(B):
 B.property=KEY+'-exterior';B.source='podium/festival-grounds-service';B.detail=0
 p=footprint('way/568597552');F=Frame(B,1144.416,-3044.655,YAW,y=0)
 B.shell(p,.18,4.15,'fgs-tan-stucco',roof=False);B.planar('fgs-roof-paint',p,4.02,True)
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  G,L,nx,nz=facade_frame(B,a,b,p,.01)
  G.box('fgs-red-plinth-paint',(L/2,.39,-.035),(L,.42,.08))
  G.box('fgs-cream-coping-paint',(L/2,4.19,-.02),(L,.14,.16))
  if L>6:
   # Solid metal service doors; no invented commercial storefront or signage.
   for u in [L*.22,L*.78]:
    G.box('fgs-frame-paint',(u,1.43,-.055),(1.22,2.5,.1))
    G.box('fgs-door-paint',(u,1.42,-.12),(1.07,2.33,.06))
    G.tube('fgs-hardware-paint',(u+.34,1.24,-.19),(u+.34,1.52,-.19),.016,6)
    G.box('fgs-light-paint',(u,2.87,-.15),(.3,.18,.24))
   for u in [L*.43,L*.58]:
    G.box('fgs-vent-paint',(u,2.9,-.06),(.9,.38,.08))
    for yy in [2.77,2.85,2.93,3.01]:G.box('fgs-hardware-paint',(u,yy,-.11),(.88,.016,.025))
  if L>15:
   for u in [1,L-1]:G.tube('fgs-drain-paint',(u,.2,-.13),(u,4.05,-.13),.04,8)
 # Membrane roof, two central fan units and small circular vents visible in aerial.
 for w in [4.0,10.3]:
  F.box('fgs-curb-paint',(24,4.13,w),(3.1,.23,3.1))
  F.box('fgs-service-paint',(24,4.56,w),(2.45,.75,2.6))
  F.lathe('fgs-vent-paint',24,w,[(4.94,.76),(5.01,.76)],24)
  for ang in np.arange(0,math.tau,math.tau/10):
   F.tube('fgs-grille-paint',(24,5.035,w),(24+.73*math.cos(ang),5.035,w+.73*math.sin(ang)),.018,5)
  F.box('fgs-vent-paint',(25.245,4.55,w),(.025,.52,1.8))
  for yy in np.arange(4.33,4.8,.085):F.box('fgs-grille-paint',(25.27,float(yy),w),(.03,.018,1.78))
 for u,w in [(2,1.1),(9,1.2),(17,12.4)]:
  F.lathe('fgs-service-paint',u,w,[(4.02,.18),(4.4,.18),(4.45,.32),(4.55,.24)],12)
 # South recess is the shallow green strip in aerial imagery, interpreted as covered frontage.
 F.box('fgs-canopy-paint',(24,3.35,14.25),(30.2,.15,1.25))
 for u in [9.2,19.2,29.2,39.0]:F.box('fgs-frame-paint',(u,1.75,14.7),(.12,3.2,.12),True)
 # Narrow concrete building apron only. Preserve festival grounds and roads.
 apron=p.buffer(1.3,join_style=2).difference(p);B.planar('fgs-concrete',apron,.18,True)
 samples=[]
 for x in np.arange(p.bounds[0]+.5,p.bounds[2],1.2):
  for z in np.arange(p.bounds[1]+.5,p.bounds[3],1.2):
   if p.buffer(-.25).contains(Point(x,z)):samples.append([float(x),4.9,float(z)])
 Path('build/city-exteriors/festival-grounds-service-samples.json').write_text(json.dumps(samples))
 return dict(key=KEY,name='Festival grounds service building',center=[1169,0,-3037],bounds=[1141,-3047,1198,-3025],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
