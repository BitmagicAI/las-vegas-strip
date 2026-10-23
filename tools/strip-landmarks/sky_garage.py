"""Mapped parking tower west of Sky. Google Earth imagery2022-11-09."""
from common import *
from forum_shops import facade_frame
KEY='skyGarage';IDS=['way/396439303']
def exterior(B):
 B.property=KEY+'-exterior';B.source='sky-west-garage';B.detail=0
 p=footprint(IDS[0]);pitch=47/15
 # Source notch forms lower west arm; observed roof is a level below main deck.
 sections=[(p.intersection(box(940,-2780,981.4,-2730)),14),(p.difference(box(940,-2780,981.4,-2730)),15)]
 for poly,n in sections:
  for pp in parts(poly):
   for j in range(n+1):
    y=j*pitch
    B.shell(pp,max(0,y-.25),y+.02,'skg-slab',roof=False)
    B.planar('skg-deck',pp,y+.025,True)
   ps=list(pp.exterior.coords)
   for a,b in zip(ps,ps[1:]):
    # Original boundary only: no opaque wall along interior section split.
    if p.boundary.distance(LineString([a,b]).interpolate(.5,normalized=True))>.2:continue
    F,L,*_=facade_frame(B,a,b,pp,0)
    count=max(1,round(L/7.5))
    for x in np.linspace(.3,L-.3,count+1):
     if L>20 and (x<4.4 or x>L-4.4):continue
     F.box('skg-sand',(x,n*pitch/2,0),(.5,n*pitch,.65),True)
    # Solid end panels and pale deck rails are visible on the Earth elevations.
    if L>20:
     for x in [2.1,L-2.1]:F.box('skg-sand',(x,n*pitch/2,-.08),(4.2,n*pitch,.45),True)
    for j in range(n):F.box('skg-rail',(L/2,j*pitch+.68,-.12),(L,1.05,.22),True)
    F.box('skg-rail',(L/2,n*pitch+.55,0),(L,1.05,.22),True)
   # Top-deck spaces, with shared geometry/material and no per-mark colliders.
   minx,minz,maxx,maxz=pp.bounds
   for x in np.arange(minx+3,maxx-1,2.7):
    for z in [minz+1,maxz-6]:
     stripe=box(x,z,x+.08,z+4.7).intersection(pp.buffer(-.65))
     B.planar('skg-line',stripe,n*pitch+.08)
 # Solid stair tower on the south-east corner is raised above the parking roof.
 core=box(1010.4,-2742.5,1018.9,-2735.3).intersection(p)
 B.shell(core,0,50,'skg-sand',roof=False);B.planar('skg-deck',core,50,True)
 for pp in parts(core):
  for a,b in zip(list(pp.exterior.coords),list(pp.exterior.coords)[1:]):
   F,L,*_=facade_frame(B,a,b,pp,0);F.box('skg-rail',(L/2,50.35,0),(L,.7,.25))
 return dict(key=KEY,name='Sky west parking structure',center=[985,0,-2765],bounds=list(p.bounds),structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],views={})
