"""Mapped north/south PH frontage roof parts as raised canopies, not buildings.
2024SensoryInteractive north photograph establishes silver canopy/stepped pylon.
South component outline from mapping; height/support details inferred.
"""
from common import *
KEY='phFrontageCanopies'
def exterior(B):
 B.property=KEY+'-exterior';B.source='ph-canopy';B.detail=0;W=Frame(B,0,0,y=0)
 for ident,c in [('way/1436534385',(40.1,589.2)),('way/1436534369',(34.5,699))]:
  p=footprint(ident);B.planar('pc-paving-concrete',p,.24,True);B.shell(p,6.85,7.65,'pc-silver-paint',roof=False);B.planar('pc-roof-paint',p,7.66,True)
  for poly in parts(p):
   for t in triangles(poly):B.face('pc-soffit-paint',[(x,6.85,z)for x,z in list(t.exterior.coords)[:-1]],True)
  # Single landmark pylon at the rounded end; no solid extrusion across entry.
  x,z=c;W.lathe('pc-silver-paint',x,z,[(.2,.75),(.35,.85),(3.6,.85),(6.8,.62),(7.7,.95),(9.2,1.04)],32)
  for y in np.arange(4,9.3,.48):
   r=.64+(y-4)*.08;W.lathe('pc-trim-paint',x,z,[(y-.05,r),(y,r+.14),(y+.10,r+.14),(y+.15,r)],32)
  W.box('pc-collision',(x,4.7,z),(1.35,9,1.35),True)
  for poly in parts(p):
   for a,b in zip(list(poly.exterior.coords),list(poly.exterior.coords)[1:]):
    for y in [7.03,7.58]:B.tube('pc-trim-paint',(a[0],y,a[1]),(b[0],y,b[1]),.025,5)
  # Quiet radial metal soffit joints; no new runtime light allocation.
  for q in list(p.exterior.coords)[::3]:
   line=LineString([c,q]).intersection(p)
   if line.geom_type=='LineString' and line.length>1:
    a,b=list(line.coords)[0],list(line.coords)[-1];B.tube('pc-joint-paint',(a[0],6.83,a[1]),(b[0],6.83,b[1]),.015,4)
 for k in list(B.groups):
  if B.groups[k]['material']=='pc-collision':del B.groups[k]
 return dict(key=KEY,name='Planet Hollywood frontage canopies',center=[44,0,642],bounds=[31,585,55,702],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
