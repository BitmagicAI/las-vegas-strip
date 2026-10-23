"""Two mapped tiled roof volumes above the retained Bellagio podium.
Aerial reference establishes hip profiles and the southern concave arc.
Eave13.2/ridge17m are estimates; podium/interior geometry is retained.
"""
from common import *
KEY='bellagioCurvedRoofs';IDS=['way/114719022','way/114719023']
def exterior(B):
 B.property=KEY+'-exterior';B.detail=0;samples=[]
 for index,ident in enumerate(IDS):
  p=footprint(ident);B.source=ident
  roof=p.difference(Point(-215.4,294.85).buffer(11.2,quad_segs=40)) if index==0 else p
  roof=roof.buffer(.16,join_style=2)
  B.shell(roof.buffer(-.16,join_style=2),12.43,13.2,'bcr-cream-stucco',roof=False)
  for y,h,off in [(12.56,.14,.04),(12.86,.16,.12),(13.12,.16,.20)]:B.shell(roof.buffer(off,join_style=2),y,y+h,'bcr-cornice-paint',roof=False,solid=False)
  lo,hi=0,12
  for _ in range(32):
   mid=(lo+hi)/2
   if roof.buffer(-mid,join_style=2).is_empty:hi=mid
   else:lo=mid
  maxd=lo;boundary=roof.boundary
  def height(x,z):return 13.2+3.8*min(1,boundary.distance(Point(x,z))/maxd)
  mat='bcr-curved-tile-paint' if index==0 else 'bcr-tile-paint'
  offsets=list(np.arange(0,maxd,.30))+[maxd+.001]
  for d,e in zip(offsets,offsets[1:]):
   band=roof.buffer(-d,join_style=2).difference(roof.buffer(-e,join_style=2))
   for tri in triangles(band):B.face(mat,[(x,height(x,z),z)for x,z in list(tri.exterior.coords)[:-1]],True)
  # Pale service vent/skylight on the rectangular roof, visible in the aerial.
  if index==1:
   x,z=-206.1,260.4;pts=[(x-.65,z-.75),(x+.65,z-.75),(x+.65,z+.75),(x-.65,z+.75)]
   verts=[(xx,height(xx,zz)+.075,zz)for xx,zz in pts];B.face('bcr-rooflight-glass',verts)
   for a,b in zip(verts,verts[1:]+verts[:1]):B.tube('bcr-metal-paint',a,b,.065,8)
  else:
   for x,z in [(-194.8,291.5),(-195.6,300.5)]:
    y=height(x,z);B.box('bcr-service-paint',(x,y+.25,z),(.65,.7,.8));B.box('bcr-cap-paint',(x,y+.65,z),(.88,.16,1.0))
  for x in np.arange(p.bounds[0],p.bounds[2],.65):
   for z in np.arange(p.bounds[1],p.bounds[3],.65):
    if roof.buffer(-.2).contains(Point(x,z)):samples.append([x,height(x,z)+.25,z])
 Path('build/city-exteriors/bellagio-curved-roofs-samples.json').write_text(json.dumps(samples))
 return dict(key=KEY,name='Bellagio lakefront roof volumes',center=[-201,0,280],bounds=[-210,252,-191,309],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
