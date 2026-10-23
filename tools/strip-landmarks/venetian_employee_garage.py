"""Employee garage: Earth Nov2022. Approx42m height, mapped stepped footprint.
Private deck connections not asserted; exterior floor slabs and rails are physical.
"""
from common import *
from forum_shops import facade_frame
KEY='venetianEmployeeGarage';IDS=['way/111367849']
def exterior(B):
 B.property=KEY+'-exterior';B.source='venetian-employee-garage';B.detail=0
 p=footprint(IDS[0]);h=42;pitch=3
 for level in range(15):
  y=.24+level*pitch
  B.shell(p,max(.01,y-.25),y,'skg-slab',roof=False)
  B.planar('skg-deck',p,y,True)
 for pp in parts(p):
  ps=list(pp.exterior.coords)
  for a,b in zip(ps,ps[1:]):
   F,L,nx,nz=facade_frame(B,a,b,p,0)
   if nz>.8:
    # South screen is deliberately solid, with tall shallow pilasters.
    F.box('st-stone',(L/2,h/2,0),(L,h,.28),True)
    for x in np.arange(.3,L,8):
     F.box('st-grey',(x,h/2,-.17),(.11,h,.06))
     F.box('st-stone',(x+.22,h/2,-.23),(.32,h,.18))
   else:
    for level in range(1,15):F.box('st-stone',(L/2,.24+level*pitch+.42,-.07),(L,.84,.2),True)
    for x in np.linspace(.2,max(.2,L-.2),max(2,round(L/7.5)+1)):F.box('st-stone',(x,h/2,0),(.4,h,.45),True)
    # East end has two tall opaque panels separated by open deck slots.
    if nx>.8 and L>30:
     for x in [L*.12,L*.7]:F.box('st-stone',(x,h/2,-.23),(L*.22,h,.25),True)
   F.box('st-white',(L/2,h+.72,0),(L,.2,.35))
 # Long rooftop solar strip, as visible in both oblique references.
 for x in np.arange(468,587,3.3):
  for z in np.arange(-406,-398,1.6):
   B.box('st-grey',(x,42.7,z),(3.1,.12,1.45))
   B.box('darkglass',(x,42.78,z),(3,.04,1.35))
 # Roof parking striping stays entirely inside the nonrectangular plan.
 for x in np.arange(435,607,2.7):
  for z in [-432,-418,-394]:B.planar('skg-line',box(x,z,x+.075,z+5).intersection(p.buffer(-.7)),42.26)
 for x,z in [(470,-432),(599,-427)]:
  B.box('st-stone',(x,43.1,z),(5,1.7,5),True)
  B.box('st-white',(x,44,z),(5.3,.14,5.3))
 return dict(key=KEY,name='Venetian employee parking structure',center=[520,0,-410],bounds=list(p.bounds),structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],views={})
