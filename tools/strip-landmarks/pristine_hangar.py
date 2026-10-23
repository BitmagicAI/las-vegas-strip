"""Pristine Flight hangar: mapped shell and satellite roof, facade details estimated."""
from common import *
from forum_shops import facade_frame
KEY='pristineHangar'
def exterior(B):
 B.property=KEY+'-exterior';B.source='podium/hangar';B.detail=0;W=Frame(B,0,0,y=0)
 p=footprint('way/457939133');B.shell(p,.18,11,'pf-white-metal-paint',roof=False);B.planar('pf-roof-paint',p,10.9,True)
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  G,L,nx,nz=facade_frame(B,a,b,p,.025)
  G.box('pf-coping',(L/2,11.02,-.06),(L,.18,.3));G.box('pf-base',(L/2,.65,-.06),(L,1,.12))
  for u in np.arange(.4,L,.55):G.box('pf-seam',(u,5.65,-.065),(.025,10.1,.03))
  if nx>.6:
   G.box('pf-door',(L/2,4.8,-.12),(L-1.8,9.2,.13),True)
   for u in np.arange(1,L-1,2.3):G.box('pf-door-seam',(u,4.8,-.21),(.065,9.2,.06))
   for y in [1.5,3,4.5,6,7.5,9]:G.box('pf-door-seam',(L/2,y,-.21),(L-1.8,.045,.04))
   G.box('pf-track',(L/2,9.55,-.3),(L-.6,.28,.4))
  elif nx<-.6:
   for u in [5,L-5]:
    G.box('pf-frame',(u,1.65,-.13),(1.25,2.7,.14));G.box('pf-service-door',(u,1.65,-.22),(1.1,2.55,.04));G.box('pf-glass',(u,2.1,-.26),(.65,.8,.02))
    G.box('pf-canopy',(u,3.2,-.6),(2.4,.18,1.6))
   for u in np.arange(8,L-7,3):G.box('pf-glass',(u,2.3,-.13),(1.6,1,.08))
 # Roof equipment positions follow visible perimeter rows; exact plant type unknown.
 for z in [3725.6,3751.9]:
  for x in np.arange(191,229,4):
   W.box('pf-service',(x,11.25,z),(1.3,.7,1));W.box('pf-grille',(x,11.62,z),(1.1,.04,.8))
 for x,z in [(202,3734),(216,3742),(194,3743)]:W.box('pf-service',(x,11.3,z),(2,.8,2))
 apron=box(184,3719,258,3769);B.planar('pf-concrete',apron,.15,True)
 for x in np.arange(184,258,5):W.box('pf-paving-joint',(x,.166,3759),(.025,.012,20))
 for z in np.arange(3754,3769,5):W.box('pf-paving-joint',(220,.167,z),(74,.014,.025))
 for z in [3728,3749]:W.box('pf-bollard',(185.5,.65,z),(.2,1,.2),True)
 samples=[[float(x),.15,float(z)] for x in np.arange(184,258,2) for z in np.arange(3755,3768,2)]
 Path('build/city-exteriors/pristine-hangar-samples.json').write_text(json.dumps(samples))
 return dict(key=KEY,name='Pristine Flight hangar',center=[210,0,3739],bounds=[184,3719,258,3769],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
