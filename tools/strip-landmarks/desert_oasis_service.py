"""Detached mapped 3965 service building. Roof based on aerial; facade inferred.
No tenant branding or claim of surveyed openings. Existing surrounding paving retained.
"""
from common import *
from forum_shops import facade_frame
from local_pavement import local_pavement
KEY='desertOasisService';IDS=['way/364846551']
def exterior(B):
 B.property=KEY+'-exterior';B.source=IDS[0];B.detail=0;p=footprint(IDS[0]);D=.24
 B.shell(p,.12,5.8,'dos-wall-paint',roof=False);B.planar('dos-roof-paint',p,5.8,True)
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  F,L,nx,nz=facade_frame(B,a,b,p,0);F.y=D
  F.box('dos-base-paint',(L/2,.25,-.04),(L,.5,.08));F.box('dos-coping-paint',(L/2,5.65,-.055),(L+.10,.22,.22))
  if L>8:
   # Minimal service openings are explicitly inferred, not copied from an unrelated street photo.
   u=L*.27;F.box('dos-trim-paint',(u,1.13,-.07),(1.06,2.26,.14));F.box('dos-door-paint',(u,1.1,-.16),(.9,2.1,.06));F.box('dos-metal-paint',(u+.3,1.12,-.21),(.035,.17,.035))
   u=L*.72;F.box('dos-dark-paint',(u,3.6,-.06),(1.1,.85,.12))
   for y in np.arange(3.24,4,.095):F.box('dos-metal-paint',(u,float(y),-.14),(1.06,.045,.07))
  for u in [.24,L-.24]:
   F.tube('dos-coping-paint',(u,.12,-.17),(u,5.5,-.17),.045,8)
 # White flat membrane roof with individually framed plant and small vents visible from above.
 for x,z,w,d,h in [(145.2,2739.4,1.25,1.65,.55),(145.4,2736.9,.85,.75,.4)]:
  B.box('dos-base-paint',(x,5.91,z),(w+.2,.22,d+.2));B.box('dos-equipment-paint',(x,6.05+h/2,z),(w,h,d))
  B.lathe('dos-dark-paint',(x,z),[(6.05+h,.24),(6.08+h,.24)],16)
  for dz in np.arange(-d/2+.1,d/2,.12):B.box('dos-metal-paint',(x,6.15,z+float(dz)),(w+.02,.035,.04))
 for x,z in [(144,2733.5),(146.8,2741.3)]:
  B.lathe('dos-metal-paint',(x,z),[(5.8,.09),(6.2,.09),(6.23,.16),(6.29,.16)],12)
 local_pavement(B,box(119,2718,166,2765).difference(p),.14,'dos-paving')
 for z in [2725,2728,2747,2750,2753]:B.box('dos-line-paint',(154,.155,z),(5,.012,.09))
 samples=[[x,6.05,z]for x in np.arange(p.bounds[0]+.2,p.bounds[2],.6)for z in np.arange(p.bounds[1]+.2,p.bounds[3],.6)if p.buffer(-.15).contains(Point(x,z))]
 Path('build/city-exteriors/desert-oasis-service-samples.json').write_text(json.dumps(samples))
 Path('build/city-exteriors/desert-oasis-service-stairs.json').write_text(json.dumps([[[140,.24,2731],[140,.24,2744]],[[150,.24,2731],[150,.24,2744]]]))
 return dict(key=KEY,name='3965 detached service building',center=[145,0,2738],bounds=[141,2731,149,2745],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
