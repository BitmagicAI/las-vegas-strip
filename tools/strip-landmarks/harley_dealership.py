"""5191 S Las Vegas Boulevard. Contractor exterior photo, mapped footprint.
Dimensions beyond mapped ten-metre shell are estimates. Retain city structure.
Photograph is research only; materials, lettering and panels are authored here.
"""
from common import *
from forum_shops import facade_frame
KEY='harleyDealership'

def exterior(B):
 B.property=KEY+'-exterior';B.source='podium/dealership';B.detail=0
 p=unary_union([footprint('way/674358786'),footprint('way/816094564')]);ps=list(p.exterior.coords)
 B.shell(p,.2,10.2,'hd-concrete',roof=False)
 # Site subgrade sits below surveyed city paving, so no shared coplanar face.
 B.source='podium/forecourt';B.planar('hd-asphalt',box(35,3598,182,3710),-.12,True)
 B.source='podium/dealership'
 for a,b in zip(ps,ps[1:]):
  if math.dist(a,b)<.2:continue
  F,L,nx,nz=facade_frame(B,a,b,p,.18)
  west=nx<-.7;south=nz>.7
  mx,mz=(a[0]+b[0])/2,(a[1]+b[1])/2
  striped=west and 3647<mz<3679
  mat='hd-silver' if west or nz<-.7 else 'hd-concrete'
  F.box(mat,(L/2,5.2,0),(L,10,.12))
  if striped:
   for i,y in enumerate(np.arange(.4,10,.38)):
    F.box(['hd-orange','hd-red','hd-cream','hd-charcoal'][i%4],(L/2,y,-.08),(L,.32,.08))
  else:
   for y in np.arange(1.8,10,1.8):F.box('hd-joint',(L/2,y,-.08),(L,.035,.035))
   for u in np.arange(3,L,3):F.box('hd-joint',(u,5.2,-.08),(.035,9.9,.035))
  F.box('hd-charcoal',(L/2,.38,-.10),(L,.30,.26))
  F.box('hd-silver',(L/2,10.24,-.10),(L,.22,.4))
  if west and L>20 and mz<3679:
   if mz<3647:
    F.text('LAS VEGAS',(L/2,7.4,-.18),1.05,'hd-letter')
    F.text('HARLEY-DAVIDSON',(L/2,5.8,-.18),.7,'hd-letter')
    F.text('5191',(2,9,-.18),.46,'hd-charcoal')
   else:
    # Full-height showroom window panels in front of the striped wall.
    for u in [L*.22,L*.72]:
     F.box('hd-glass',(u,4.3,-.17),(4.4,7.2,.12))
     for dx in [-2.2,0,2.2]:F.box('hd-silver',(u+dx,4.3,-.26),(.08,7.3,.18))
     for y in [.7,3.2,5.6,7.9]:F.box('hd-silver',(u,y,-.26),(4.5,.08,.18))
  elif (nx>.7 or south) and L>15:
   for u in np.arange(5,L-3,8):
    F.box('hd-charcoal',(u,2.6,-.13),(4.8,4.7,.12))
    for y in np.arange(.4,4.8,.32):F.box('hd-silver',(u,y,-.21),(4.6,.025,.04))
   F.text('SERVICE',(L/2,7,-.17),1.1,'hd-charcoal')
 # Central west entry glazed tower, steel canopy and paired doors.
 F=Frame(B,95.95,3648,math.pi/2,y=0)
 F.box('hd-glass',(0,5.1,-.1),(9.2,9.8,.18))
 for x in np.arange(-4.6,4.7,1.53):F.box('hd-silver',(x,5.1,-.25),(.11,9.9,.25))
 for y in np.arange(.25,10,1.65):F.box('hd-silver',(0,y,-.25),(9.3,.10,.25))
 F.box('hd-silver',(0,11.8,-2),(12,.32,6),True)
 F.box('hd-red',(0,12.02,-2),(12.2,.12,6.2))
 for x in [-4.8,4.8]:
  F.box('hd-silver',(x,5.9,-3.2),(.22,11.8,.22),True)
  F.tube('hd-silver',(x,9.6,-3.2),(x,11.6,-4.8),.08,8)
 for y in [9.9,10.6,11.3]:F.box('hd-silver',(0,y,-1.9),(10,.10,4.8))
 for x in [-1.8,0,1.8]:F.box('hd-silver',(x,1.7,-.38),(.09,3.1,.18))
 for x in [-.18,.18]:F.tube('hd-silver',(x,1,-.55),(x,1.9,-.55),.035,8)
 F.text('WELCOME',(0,3.9,-.4),.44,'hd-letter')
 # Separate roof skin clears retained city shell; equipment only near range.
 B.source='roof/service';B.planar('hd-flat-roof-paint',p,10.4,True)
 B.detail=1
 for x,z in [(125,3634),(142,3634),(135,3660),(149,3660)]:
  B.box('hd-silver',(x,11.05,z),(4.8,1.3,3.2));B.box('hd-charcoal',(x,11.72,z),(4.4,.04,2.8))
 B.detail=0
 return dict(key=KEY,name='Las Vegas Harley-Davidson exterior',center=[128,0,3650],bounds=[89,3621,161,3704],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
