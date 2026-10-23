"""Luxor southwest service/theatre volumes from Earth 2022 obliques.
Footprints surveyed; 22/26/6m heights and mechanical details are estimates.
"""
from common import *
from forum_shops import facade_frame
from building_surfaces import BuildingSurfaces
from luxor_facades import Access
IDS=['way/127712208','way/115646918','way/399368725','way/399368722']
def exterior(B):
 B.property='luxorExterior-exterior';B.source='luxor-service';B.detail=0
 heights=[22,26,6,12];records=[dict(BYID[i],shape=footprint(i),height=h) for i,h in zip(IDS,heights)]
 surfaces=BuildingSurfaces(records)
 for r in records:
  p=r['shape'];h=r['height'];ident=r['id']
  for pp in parts(p):
   cc=list(pp.exterior.coords)
   for a,b in zip(cc,cc[1:]):
    visible=surfaces.wall(ident,a,b,.24,h,Access(dict(towers=[])))
    for tri in visible:B.face('luxor-stone',tri,True)
    F,L,nx,nz=facade_frame(B,a,b,pp,0)
    # Only exposed wall gets architectural bands; shared annex wall stays absent.
    mid=LineString([a,b]).interpolate(.5,normalized=True)
    if any(o['id']!=ident and o['shape'].buffer(.05).contains(Point(mid.x+nx*.3,mid.y+nz*.3)) for o in records):continue
    for y in [.75,h-.8,h]:F.box('luxor-band',(L/2,y,-.13),(L,.18,.28))
    if h>10 and ident!='way/399368722':
     # Deep rectangular Egyptian relief panels, observed on the theatre end wall.
     for x in np.arange(9,L-7,15):
      for xx in [x-3.4,x+3.4]:F.box('luxor-shadow',(xx,h*.55,-.12),(.18,h*.52,.10));F.box('luxor-stone',(xx+.22,h*.55,-.22),(.25,h*.52,.25))
      F.box('luxor-shadow',(x,h*.81,-.12),(7,.18,.1))
    else:
     for x in np.arange(4,L-3,9):
      F.box('luxor-service-paint',(x,1.8,-.16),(3,3.1,.14))
      for yy in np.arange(.4,3.2,.3):F.box('luxor-shadow',(x,yy,-.25),(2.9,.045,.05))
   roof=surfaces.roof(ident,pp,h);B.planar('luxor-membrane-paint',roof,h+.035,True)
   B.shell(pp.buffer(-.3),h,h+.5,'luxor-stone',roof=False,solid=False)
   safe=roof.buffer(-3)
   if ident=='way/399368722':
    for x in np.arange(-531,-500,10):
     for z in np.arange(2200,2250,10):
      if not safe.contains(box(x-3.8,z-3.8,x+3.8,z+3.8)):continue
      B.box('luxor-service-paint',(x,h+1.8,z),(7.5,3.6,7.5))
      B.lathe('luxor-shadow',(x,z),[(h+3.6,2.5),(h+3.7,2.5)],24)
      for a in np.linspace(0,math.tau,6,endpoint=False):B.tube('luxor-band',(x,h+3.76,z),(x+2.3*math.cos(a),h+3.76,z+2.3*math.sin(a)),.10,4)

   for x in np.arange(p.bounds[0]+5,p.bounds[2]-3,13):
    for z in [p.bounds[1]+4,p.bounds[3]-4]:
     if not safe.contains(box(x-1.5,z-1,x+1.5,z+1)):continue
     B.box('luxor-service-paint',(x,h+.38,z),(2.8,.7,1.7))
     B.box('luxor-shadow',(x,h+.75,z),(2.4,.055,1.3))
 return IDS
