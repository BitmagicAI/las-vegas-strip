"""Visible upper service blocks retained from OSM, detailed against Earth2022.
No interior/road ownership changes. Roof finish, parapets and mechanical housings.
"""
from common import *
from forum_shops import facade_frame
from building_surfaces import BuildingSurfaces
IDS=['way/111367834','way/114718020','way/114718021','way/114718022','way/114718023','way/114718350','way/114718353','way/114721151']
def build(b):
 b.property='bellagioBlock-exterior';b.source='service-refinement';b.detail=0
 records=[dict(BYID[i],shape=footprint(i)) for i in IDS+['relation/1599958','way/25723909','way/25723910']];surfaces=BuildingSurfaces(records)
 for ident in IDS:
  r=BYID[ident];p=footprint(ident);h=r['height'];roof=surfaces.roof(ident,p,h)
  b.planar('bellagio-flat-roof',roof,h+.035)
  for pp in parts(p):
   cs=list(pp.exterior.coords)
   for a,c in zip(cs,cs[1:]):
    f,L,nx,nz=facade_frame(b,a,c,p,.08)
    if L<.4:continue
    # Keep the mapped wall. Add only the exposed upper podium's joints and coping.
    f.box('bel-service-trim',(L/2,h+.12,0),(L,.24,.38))
    for u in np.arange(2,L,5.5):f.box('bel-service-joint',(u,(12.6+h)/2,0),(.035,max(.1,h-12.6),.055))
    if h>=20 and L>7:
     for u in np.arange(3,L-2,5):
      f.box('bel-service-vent',(u,h-1.5,-.03),(2.5,1.4,.10))
      for y in np.arange(h-2.1,h-.9,.22):f.box('bel-service-trim',(u,y,-.1),(2.5,.035,.10))
  for x in np.arange(p.bounds[0]+9,p.bounds[2]-6,34):
   for z in np.arange(p.bounds[1]+9,p.bounds[3]-6,31):
    if roof.contains(box(x-2,z-1.5,x+2,z+1.5)):
     b.box('bel-service-trim',(x,h+.65,z),(4,1.3,3));b.box('bel-service-vent',(x,h+1.31,z),(3.8,.035,2.8))
