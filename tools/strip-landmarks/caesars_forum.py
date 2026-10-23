"""Caesars Forum exhibition complex. Earth Nov2022 plan/elevations.
Single-level hall, separate perimeter prefunction roof and projecting entry bays.
All physical elevations below are photo estimates, not official floor heights.
"""
from common import *
from forum_shops import facade_frame
KEY='caesarsForum';IDS=['way/762169780']
def exterior(B):
 B.property=KEY+'-exterior';B.source='caesars-forum';B.detail=0
 p=footprint(IDS[0]).simplify(.18,preserve_topology=True)
 east=p.intersection(box(714,-440,790,-210));base=p.difference(east)
 B.shell(base,.24,13.4,'white',roof=False);B.planar('lvw-roof',base,13.4,True)
 B.shell(east,.24,14,'lvw-frame',roof=False);B.planar('lvw-roof',east,14,True)
 hall=box(482,-359,710,-254).intersection(p)
 B.shell(hall,13.4,16,'white',roof=False);B.planar('lvw-roof',hall,16,True)
 # Roof edge and service/expansion panel joints respect the actual irregular outline.
 for pp in parts(p):
  pts=list(pp.exterior.coords)
  for a,b in zip(pts,pts[1:]):
   F,L,nx,nz=facade_frame(B,a,b,p,.08);mx,mz=(a[0]+b[0])/2,(a[1]+b[1])/2
   h=14 if mx>=714 else 13.4
   F.box('white',(L/2,h+.13,0),(L,.26,.34),True)
   dark=(mx>=714 and (nz>.4 or nx>.5)) or (nx<-.5 and mz>-350)
   if dark:
    F.box('wf-glass',(L/2,h/2,-.12),(L,h-.25,.1))
    for y in np.arange(.8,h,1.55):F.box('lvw-frame',(L/2,y,-.2),(L,.24,.2))
    for x in np.arange(2,L,4):F.box('silver',(x,h/2,-.25),(.055,h-.3,.08))
   else:
    for x in np.arange(2,L,5):F.box('lvw-joint',(x,h/2,-.07),(.035,h-.4,.045))
    if nz<-.5 or nx>.5:
     for x in np.arange(8,L-4,18):
      F.box('lvw-loading',(x,2.6,-.12),(4.4,5,.1))
      F.box('silver',(x,5.2,-.35),(4.8,.15,.7))
      for y in np.arange(.5,5,.42):F.box('lvw-frame',(x,y,-.19),(4.2,.04,.04))
 # Two south entrance bays: glass above recessed doors, flanked by deep charcoal fins.
 for x,z in [(505,-241.6),(612,-235.4)]:
  F=Frame(B,x,z,math.pi,y=0)
  F.box('wf-glass',(0,10,-.50),(17,12,.15))
  for dx in np.arange(-8,8.1,1.4):F.box('silver',(dx,10,-.63),(.07,12,.10))
  for y in [5,7.5,10,12.5,15.5]:F.box('silver',(0,y,-.64),(17,.07,.1))
  for dx in [-9,9]:
   F.box('lvw-loading',(dx,9,-.4),(1.5,18,2.2),True)
   for y in np.arange(1,18,.7):F.box('lvw-frame',(dx,y,-1.53),(1.52,.12,.08))
  F.box('white',(0,17.5,-.35),(20,.7,2.7),True)
  F.box('lvw-frame',(0,4.2,-2.0),(20,.45,5.6),True)
  F.box('darkglass',(0,1.95,-.24),(15,3.9,.1))
  for dx in np.arange(-6,7,3):
   F.box('silver',(dx,1.95,-.35),(.09,3.9,.1));F.box('silver',(dx+.8,1.3,-.43),(.04,.7,.05))
  for dx in [-8.5,8.5]:F.box('lvw-frame',(dx,2,-4.4),(.2,4,.2),True)
 # South solid bays have recessed glazed openings and restrained event-banner panels.
 for x,z in [(466,-242),(480,-242),(536,-242),(553,-235.5),(570,-235.5),(587,-235.5),(644,-235.5),(662,-235.5),(680,-235.5),(698,-235.5)]:
  F=Frame(B,x,z,math.pi,y=0)
  F.box('lvw-loading',(0,6.2,-.10),(5.5,7.4,.1))
  F.box('wf-glass',(0,6.2,-.19),(5.1,7.1,.08))
  F.box('silver',(0,6.2,-.25),(.07,7.1,.07));F.box('silver',(0,4,-.25),(5.1,.07,.07))
  # Neutral permanent branding instead of copying temporary event advertisements.
  if x not in [480,587,698]:
   F.box('harrahs-purple',(0,7,-.30),(4.6,4.7,.04));F.text('FORUM',(0,7,-.36),.43,'white')
 # West bridge arrival volume, leaving the existing external bridge untouched.
 q=box(452,-302,475,-275).intersection(p)
 B.shell(q,13.4,18,'white',roof=False);B.planar('lvw-roof',q,18,True)
 F=Frame(B,451.2,-288,math.pi/2,y=0);F.box('wf-glass',(0,9,-.2),(21,13,.1))
 for x in np.arange(-10,10.1,1.5):F.box('silver',(x,9,-.29),(.07,13,.09))
 # Perimeter mechanical units, with the vast main roof deliberately clear.
 for x in np.arange(486,710,18):
  for z in [-365,-246]:
   if p.contains(box(x-2,z-2,x+2,z+2)):
    B.box('lvw-service',(x,14.1,z),(3,1.4,3));B.box('lvw-loading',(x,14.84,z),(2.4,.08,2.4))
 for z in np.arange(-410,-240,25):
  B.box('lvw-service',(762,14.7,z),(4,1.4,3));B.box('lvw-frame',(762,15.45,z),(4.3,.1,3.3))
 for x in np.arange(490,704,24):B.planar('lvw-joint',box(x,-356,x+.05,-257),16.009)
 F=Frame(B,654,-235.5,math.pi,y=0);F.text('CAESARS FORUM',(0,12.2,-.55),.9,'lvw-loading')
 # Continuous entrance apron ends well before the mapped road; the broad event
 # plaza/parking beyond remains a separate landscape reconstruction.
 apron=p.buffer(5,join_style=2).difference(p).intersection(box(450,-250,714,-220))
 B.planar('tile',apron,.28,True)
 return dict(key=KEY,name='Caesars Forum convention center',center=[620,0,-310],bounds=list(p.bounds),structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],views={})
