"""Venetian Expo exterior, mapped plan and Earth 2022 / official hall maps.
Roof elevations are estimates; no replacement of the existing hotel/interiors.
"""
from common import *
from forum_shops import facade_frame
KEY='venetianExpo';IDS=['way/111367819']
def exterior(B):
 B.property=KEY+'-exterior';B.source='venetian-expo';B.detail=0
 p=footprint(IDS[0]);wing=p.intersection(box(400,-900,577,-650));hall=p.difference(wing)
 # January 2025 Street View shows an open lower colonnade, not full-height glass.
 # Cut only the mapped public frontage; preserve all other shell faces and roofs.
 openings=[];public_lines=[]
 for pp in parts(p):
  ps=list(pp.exterior.coords)
  for a,b in zip(ps,ps[1:]):
   F,L,nx,nz=facade_frame(B,a,b,p,.04)
   if nz<-.25 and (a[0]+b[0])/2>575:
    public_lines.append(LineString([a,b]))
    openings.append(dict(p=[(a[0]+b[0])/2,.24,(a[1]+b[1])/2],yaw=F.yaw,width=L+.02,height=5.05,boundaryOnly=True))
 # Continuous paved strip includes the small wedges between curved facade segments.
 public_edge=LineString([public_lines[0].coords[0]]+[line.coords[-1] for line in public_lines])
 arcade=public_edge.buffer(4.65,cap_style=2,join_style=2).intersection(p)
 B.planar('lvw-arcade-paving',arcade,.24,True)
 # The estimated hall/meeting-wing split is not a public corridor wall.
 # Open only its intersection with this covered approach, on both shell owners.
 for segment in parts(arcade.intersection(LineString([(577,-900),(577,-650)])),'LineString'):
  zs=[q[1] for q in segment.coords]
  openings.append(dict(p=[577,.24,(min(zs)+max(zs))/2],yaw=math.pi/2,width=max(zs)-min(zs)+.02,height=5.05,boundaryOnly=True))
 # Upper hall clear height 32ft5in, lower Hall G13ft5in. Structure/plenum estimated.
 B.shell(hall,.24,18,'lvw-panel',roof=False,openings=openings);B.planar('lvw-roof',hall,18,True)
 B.shell(wing,.24,22,'white',roof=False,openings=openings);B.planar('lvw-roof',wing,22,True)
 for pp in parts(p):
  ps=list(pp.exterior.coords)
  for a,b in zip(ps,ps[1:]):
   F,L,nx,nz=facade_frame(B,a,b,p,.04);mx,mz=(a[0]+b[0])/2,(a[1]+b[1])/2
   h=22 if wing.buffer(.1).contains(Point(mx,mz)) else 18
   public=nz<-.25 and mx>575
   # Curving street front has deep dark glazing under a broad pale fascia.
   if public:
    # Public covered approach stays outside the closed exhibition boundary.
    # Depth4.5m and underside5.4m are reference-derived estimates, not a survey.
    F.box('st-glass',(L/2,9.1,-.08),(L,6.8,.12))
    for x in np.linspace(0,L,max(2,math.ceil(L/3.2)+1)):
     F.box('white',(x,9.1,-.20),(.12,6.8,.25))
    for y in [7.95,10.25]:F.box('silver',(L/2,y,-.23),(L,.07,.1))
    F.box('white',(L/2,15.5,-.30),(L,5,.6))
    F.box('white',(L/2,5.5,2.15),(L,.2,4.7),True)
    F.box('lvw-panel',(L/2,2.76,4.5),(L,5.04,.16),True)
    F.box('darkglass',(L/2,2.7,4.39),(max(.1,L-.24),4.7,.04))
    for x in np.linspace(0,L,max(2,math.ceil(L/3)+1)):
     F.box('silver',(x,2.7,4.33),(.07,4.7,.08))
    # Pale structural columns leave the central walking line clear.
    if L>10:
     for x in np.arange(4,L-2,9):
      F.tube('white',(float(x),.24,.75),(float(x),5.4,.75),.36,16)
      F.box('lvw-arcade-collision',(float(x),2.82,.75),(.64,5.16,.64),True)
   else:
    F.box('white',(L/2,h-.15,-.16),(L,.45,.32))
    for x in np.arange(2,L,6):F.box('lvw-joint',(x,h/2,-.075),(.045,h-.6,.04))
    if nx>.6 or nz>.6:
     for x in np.arange(9,L-6,22):
      F.box('lvw-loading',(x,3,-.10),(5.5,5.6,.12));F.box('white',(x,5.9,-.6),(6.1,.23,1.2))
      for y in np.arange(.5,5.7,.45):F.box('lvw-frame',(x,y,-.19),(5.3,.045,.04))
      for dx in [-3,3]:F.box('charcoal',(x+dx,1,-.5),(.18,2,.22),True)
   # Parapet has genuine thickness and an inset upper roof edge.
   F.box('white',(L/2,h+.24,-.04),(L,.48,.32),True)
 # Repeating rooftop vents follow the visible exhibition roof grid. Not random clutter.
 for x in np.arange(481,775,22):
  for z in np.arange(-807,-487,24):
   if not p.buffer(-6).contains(box(x-2,z-2,x+2,z+2)):continue
   h=22 if wing.contains(Point(x,z)) else 18
   B.box('lvw-service',(x,h+.6,z),(2.6,1.2,2.2));B.box('lvw-roof',(x,h+1.26,z),(3,.12,2.6))
   B.box('lvw-loading',(x,h+.65,z-1.12),(1.9,.65,.03))
 # Expansion seams and larger duct banks are separate from the roof membrane.
 for x in np.arange(480,780,44):B.planar('lvw-joint',box(x,-820,x+.09,-480).intersection(hall.buffer(-1)),18.012)
 for x,z in [(587,-603),(650,-564),(708,-601),(608,-676)]:
  B.box('lvw-service',(x,19.25,z),(8,2.5,6))
  for dx in [-2.4,0,2.4]:B.lathe('lvw-loading',(x+dx,z),[(20.5,1),(20.62,1)],12)
  B.box('lvw-frame',(x+9,18.7,z),(11,1.4,1.5))
 F=Frame(B,633,-731,math.radians(-44),y=0)
 F.text('THE VENETIAN',(0,16.1,-1.5),1.25,'charcoal');F.text('EXPO',(0,14.45,-1.5),.95,'charcoal')
 B.groups={k:g for k,g in B.groups.items() if g['material']!='lvw-arcade-collision'}
 return dict(key=KEY,name='Venetian Expo exhibition halls',center=[620,0,-640],bounds=list(p.bounds),structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],views={})
