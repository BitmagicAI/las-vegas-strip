"""Satellite-led adjacent service annex. Elevation details remain inferred."""
from common import *
from forum_shops import facade_frame
KEY='southCommercialAnnex';ID='way/364846559'
def exterior(B):
 B.property=KEY+'-exterior';B.source='south-commercial-annex';B.detail=0
 p=footprint(ID);B.shell(p,.18,3.8,'san-tan-brick-paint',roof=False);B.planar('san-membrane-paint',p.buffer(-.13),3.5,True)
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  F,L,nx,nz=facade_frame(B,a,b,p,.025)
  F.box('san-coping-paint',(L/2,3.83,0),(L,.12,.30))
  F.box('san-brown-paint',(L/2,.48,-.07),(L,.6,.10))
  for y in np.arange(.85,3.6,.23):F.box('san-mortar-paint',(L/2,y,-.135),(L,.012,.02))
  if nx<-.8:
   # West canopy is visible in satellite; exact doorway layout remains inferred.
   mid=L*.76;F.box('san-awning-paint',(mid,2.85,-1.4),(9.2,.18,2.8))
   for u in [mid-4.35,mid+4.35]:F.box('san-frame-paint',(u,1.52,-2.5),(.10,2.65,.10),True)
   for u in [mid-2.2,mid+2.2]:
    F.box('san-frame-paint',(u,1.55,-.17),(1.2,2.65,.10));F.box('san-door-paint',(u,1.55,-.24),(1.04,2.48,.04));F.box('san-glass',(u,1.92,-.265),(.72,1.05,.018));F.box('san-handle-paint',(u+.35,1.1,-.28),(.035,.16,.04))
   for u in [L*.15,L*.35]:F.box('san-glass',(u,2.35,-.17),(2.1,.65,.06))
   F.box('san-paving-concrete',(mid,.17,-1.5),(10,.16,3),True)
   # Painted hatching on the north west access strip, not collision barriers.
   for u in np.arange(.5,L*.5,1.2):F.box('san-line-paint',(u,.135,-2),(.065,.014,3))
  elif nx>.8:
   for u in [L*.18,L*.52,L*.85]:
    F.box('san-frame-paint',(u,1.45,-.16),(1.15,2.5,.1));F.box('san-door-paint',(u,1.45,-.22),(1,2.35,.04))
    F.tube('san-conduit-paint',(u+1.1,.3,-.22),(u+1.1,3.5,-.22),.028,6)
    F.box('san-service-paint',(u+1.1,1.4,-.25),(.32,.55,.18))
  elif nz>.7:
   F.box('san-vent-paint',(L*.3,2.5,-.17),(1.6,.7,.12))
   for y in np.arange(2.2,2.8,.09):F.box('san-shadow-paint',(L*.3,y,-.24),(1.5,.024,.02))
 # White membrane with fine panel seams and three separate rooftop mechanical units.
 W=Frame(B,0,0,y=0)
 for x,z in [(-99.8,3405),(-100.2,3415),(-97.4,3427)]:
  W.box('san-curb-paint',(x,3.62,z),(1.6,.24,1.9));W.box('san-service-paint',(x,4.03,z),(1.3,.6,1.6));W.box('san-vent-paint',(x,4.35,z),(1.08,.035,1.3))
  W.tube('san-conduit-paint',(x,3.55,z),(x+3,3.55,z),.035,6)
 for z in np.arange(3402.5,3431.5,2):
  q=p.buffer(-.3).intersection(box(-107,z-.012,-90,z+.012));B.planar('san-roof-seam-paint',q,3.515)
 B.lathe('san-service-paint',(-102,3424),[(3.5,.18),(4,.18),(4,.26),(4.1,.26)],16)
 site=p.buffer(3.1,join_style=2).difference(p);B.planar('san-asphalt',site,.12,True)
 # Keep podium apron clear of the adjoining property's boundary.
 B.planar('san-paving-concrete',p.buffer(.55,join_style=2).difference(p),.18,True)
 return dict(key=KEY,name='South Strip commercial service annex',center=[-99,0,3417],bounds=[-110,3398,-88,3436],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
