"""1502 S Las Vegas Boulevard: mapped L-plan and Jan2026 frontage."""
from common import *
from forum_shops import facade_frame
KEY='travelersFrontage'
def exterior(B):
 B.property=KEY+'-exterior';B.source='podium/frontage';B.detail=0;W=Frame(B,0,0,y=0)
 p=footprint('way/364846574');B.shell(p,.18,7.15,'tf-cream-stucco',roof=False);B.planar('tf-flat-roof-paint',p,7.02,True)
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  G,L,nx,nz=facade_frame(B,a,b,p,.035)
  G.box('tf-coping',(L/2,7.17,0),(L,.15,.24))
  G.box('tf-sage',(L/2,4.9,-.08),(L,1.8,.12))
  G.box('tf-green',(L/2,3.96,-.12),(L,.12,.2));G.box('tf-green',(L/2,5.87,-.12),(L,.12,.2))
  for u in np.arange(1.6,L-1,2.65):
   G.box('tf-frame',(u,4.9,-.18),(1.45,1.55,.1));G.box('tf-glass',(u,4.9,-.25),(1.3,1.4,.04))
   for dx in [-.94,.94]:G.box('tf-maroon',(u+dx,4.9,-.17),(.32,1.55,.08))
   G.box('tf-frame',(u,4.9,-.29),(.04,1.4,.04))
  if nx>.7 and L>20:
   # Local positive U runs south along this east-facing facade.
   G.box('tf-fascia',(L/2,3.3,-.11),(L,1.1,.12))
   G.box('tf-gold',(L*.82,3.3,-.2),(L*.34,1.05,.1))
   G.box('tf-black',(L*.82,3.3,-.27),(L*.31,.75,.04))
   G.text('TATTOO',(L*.82,3.25,-.31),.65,'tf-letter')
   G.text('NEW LIFE',(L*.35,3.28,-.22),.68,'tf-green')
   for u in np.arange(2,L-1,3.1):
    G.box('tf-frame',(u,1.6,-.12),(2.65,2.45,.1));G.box('tf-cream-stucco' if 5<u<21 else 'tf-glass',(u,1.6,-.2),(2.5,2.3,.06))
   for u in [L*.84,L*.35]:
    G.box('tf-maroon',(u,1.55,-.27),(1.15,2.5,.1));G.box('tf-glass',(u,1.8,-.34),(.95,1.8,.04))
    G.tube('tf-metal',(u+.35,1.05,-.4),(u+.35,1.8,-.4),.025,8)
   G.box('tf-sage',(L/2,.4,-.18),(L,.35,.15))
  else:
   for u in np.arange(2,L-1,3.8):
    G.box('tf-frame',(u,1.8,-.1),(1.5,1.5,.08));G.box('tf-glass',(u,1.8,-.16),(1.35,1.35,.04))
 # Courtyard open to west, continuous pedestrian surface; roof plant behind parapet.
 court=box(1901,-4149,1932,-4116).difference(p);B.planar('tf-paving',court,.18,True)
 for x,z in [(1923,-4143),(1924,-4133),(1908,-4143)]:W.box('tf-service',(x,7.5,z),(1.8,.8,1.5));W.box('tf-black',(x,7.93,z),(1.5,.04,1.2))
 site=p.buffer(1.5,join_style=2).difference(p);B.planar('tf-paving',site.difference(court),.18,True)
 samples=[]
 for x in np.arange(1901,1931,1):
  for z in np.arange(-4148,-4117,1):
   if court.buffer(-.5).covers(Point(x,z)):samples.append([float(x),.18,float(z)])
 Path('build/city-exteriors/travelers-frontage-samples.json').write_text(json.dumps(samples))
 return dict(key=KEY,name='Travelers / 1502 Strip frontage',center=[1919,0,-4136],bounds=[1901,-4151,1932,-4116],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
