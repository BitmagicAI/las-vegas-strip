"""Mapped MGM Grand exterior architecture, official MGM photo/map references.
Shells/interiors/collision stay with their current owners. Facade layers use the
same footprint edges, with positive offsets and clipped shared-wall ownership.
"""
from common import *
from forum_shops import facade_frame
from planet_hollywood import panel,screen
from building_surfaces import BuildingSurfaces
KEY='mgmGrand'
CANOPY={'way/116765496','way/116765497','way/116765498'}
class Closed:
 def wall(self,a,b,lo,hi):return [[(a[0],lo,a[1]),(b[0],lo,b[1]),(b[0],hi,b[1])],[(a[0],lo,a[1]),(b[0],hi,b[1]),(a[0],hi,a[1])]]

def exterior(B):
 B.property=KEY+'-exterior';B.detail=0
 ids=['way/116770006','way/115665216','way/115665218','way/73540518','way/116765496','way/116765497','way/116765498','way/116766731','way/116766732','way/115645149','way/116770005','way/116873544','way/116873546','way/116873547']
 ids+=['way/'+str(i) for i in range(115095160,115095175)]
 ids+=['way/115093734']
 ids.remove('way/115095165')
 records=[dict(BYID[i],shape=footprint(i)) for i in ids]
 surface=BuildingSurfaces(records)
 for r in records:
  p=r['shape'];h=r['height'];lo=r['base'];ident=r['id'];tower=h>35
  if ident in CANOPY:lo=h-.65
  B.source='tower/mgm-grand' if tower else 'podium/'+ident
  garage=ident=='way/73540518'
  for poly in parts(p):
   ps=list(poly.exterior.coords)
   for a,b in zip(ps,ps[1:]):
    L=math.dist(a,b)
    if L<.3:continue
    F,L,nx,nz=facade_frame(B,a,b,p,.16)
    vis=surface.wall(ident,a,b,lo,h,Closed())
    line=LineString([a,b]);region=unary_union([Polygon([(line.project(Point(v[0],v[2])),v[1]) for v in tri]) for tri in vis])
    def patch(mat,x0,y0,x1,y1,depth=-.04):
     clipped=region.intersection(box(x0,y0,x1,y1))
     for pp in parts(clipped):
      for tri in triangles(pp):
       pts=[]
       for xx,yy in list(tri.exterior.coords)[:-1]:
        q=line.interpolate(xx);pts.append((q.x+nx*(.16-depth),yy,q.y+nz*(.16-depth)))
       B.face(mat,pts)
    if tower:
     patch('mgm-glass',0,max(lo,9),L,h-.4)
     for y in np.arange(max(lo,9),h-2,3.2):patch('mgm-green',0,y,L,min(y+.95,h),-.09)
     B.detail=1
     for x in np.arange(0,L,1.65):patch('mgm-frame',x,lo,x+.035,h,-.13)
     B.detail=0
     patch('mgm-green',0,h-4.7,L,h,-.16)
    elif garage:
     patch('ph-stone',0,lo,L,h)
     for y in np.arange(2,h,3):
      patch('ph-black',0,y,L,min(y+1.65,h-.3),-.08)
      for x in np.arange(.4,L,7):patch('ph-stone',x,y,x+.4,min(y+1.7,h),-.14)
    else:
     patch('mgm-stone',0,lo,L,h)
     # Public south and Strip edges: actual low-rise retail/show frontage.
     mx,mz=(a[0]+b[0])/2,(a[1]+b[1])/2
     public=(mx<100 and nx<-.2) or (mz>1580 and nz>.2)
     if public:
      for x in np.arange(.6,L-1,3.6):patch('mgm-glass',x,max(lo,.5),min(x+3.05,L-.3),min(h-1,5.2),-.08)
      patch('mgm-bronze',0,max(lo,h-1.4),L,h-.7,-.18)
     B.detail=1
     for y in np.arange(max(lo,.8),h,1.25):patch('mgm-joint',0,y,L,y+.018,-.10)
     for x in np.arange(1,L,3.2):patch('mgm-joint',x,lo,x+.018,h,-.10)
     B.detail=0
     patch('mgm-stone',0,h-.35,L,h+.0,-.2)
   # Finish every exposed flat roof with parapet coping, screened equipment.
   roof=surface.roof(ident,p,h)
   B.planar('ph-roof',roof,h+.025)
   B.detail=1
   for x in np.arange(p.bounds[0]+8,p.bounds[2]-4,22):
    for z in np.arange(p.bounds[1]+8,p.bounds[3]-4,23):
     if tower or not roof.contains(box(x-3,z-2,x+3,z+2)):continue
     B.box('ph-metal',(x,h+.8,z),(5,1.5,3));B.box('ph-black',(x,h+1.57,z),(4.7,.06,2.7))
     for dx in [-1.4,1.4]:B.lathe('ph-metal',(x+dx,z),[(h+1.6,.72),(h+1.69,.72)],16)
   B.detail=0
 # Strip corner art-deco screen wall, white stepped piers and bronze bowl caps.
 # Site and elevations follow mapped southwest facade; piers stay on the podium.
 B.source='podium/strip-court'
 for x,z,yaw,w in [(51,1537,math.pi/2,72),(57,1595,math.pi/2,35),(91,1633,math.pi,57)]:
  F=Frame(B,x,z,yaw,y=.24)
  for u in np.arange(-w/2,w/2,10):
   F.box('mgm-stone',(u,10.5,0),(1.5,21,1.1))
   F.box('mgm-stone',(u,20.8,-.3),(2.1,.7,1.7))
   F.lathe('mgm-bronze',u,-.3,[(21.1,.22),(21.5,.4),(21.9,1.2),(22.1,1.25)],20)
  for u in np.arange(-w/2+5,w/2,10):
   screen(F,u,11,7.6,14,'MGM GRAND','mgm-screen')
   B.detail=1
   for xx in np.arange(u-3.5,u+3.5,.72):
    for yy in np.arange(5,17,.72):F.box('mgm-lit',(xx,yy,-.76),(.08,.08,.018))
   B.detail=0
 # Freestanding Strip marquee, behind the public sidewalk.
 B.source='podium/marquee';F=Frame(B,52,1495,math.pi/2,y=.24)
 F.box('mgm-bronze',(0,20.5,0),(12,41,5),True)
 F.box('mgm-glass',(0,22.5,-2.6),(14,37,.35))
 F.box('mgm-screen',(0,21,-2.82),(11.8,22,.06))
 F.text('MGM',(0,37,-2.9),3.2,'ph-letter')
 F.text('GRAND',(0,33.5,-2.9),1.15,'ph-letter')
 F.text('LAS VEGAS',(0,12,-2.9),.75,'ph-letter')
 for y in [16,22,28]:
  F.box('mgm-bronze',(0,y,-2.9),(10.5,.07,.05))
 # The real porte cochere has three nested octagonal roof tiers, not a box lobby.
 B.source='podium/arrival'
 outer=footprint('way/116765496')
 for poly in parts(outer):
  coords=list(poly.exterior.coords)[:-1]
  for x,z in coords:
   B.box('mgm-stone',(x,5.17,z),(1.0,10.34,1.0),True)
   B.box('mgm-bronze',(x,.65,z),(1.35,1.3,1.35))
  for a,b in zip(coords,coords[1:]+coords[:1]):
   B.tube('mgm-bronze',(a[0],10.35,a[1]),(b[0],10.35,b[1]),.12,8)
 F=Frame(B,414,1616,math.pi/4,y=.24)
 F.text('MGM GRAND',(0,9.15,-.8),1.3,'mgm-bronze')
 # Ground substrate stays below the existing roads and sidewalks. It closes only
 # this site's unmeshed earth; no city road, median or collision is regenerated here.
 B.source='podium/site-ground'
 B.planar('ph-stone',unary_union([footprint('way/116770006'),footprint('relation/6022477')]).buffer(18,join_style=2),.04)
 mansion(B)
 # Existing entry access at the tower's lobby stays open, no new collision.
 return dict(key=KEY,name='MGM Grand exterior',center=[300,0,1495],bounds=[40,1300,792,1660],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})


def mansion(B):
 # Tuscan villas and glass-roofed atrium, traced from the OSM rings and Earth.
 B.source='podium/mansion';p=footprint('relation/6022477')
 B.shell(p,.0,6.0,'mgm-stone',roof=False,solid=True)
 B.planar('terracotta',p,6.05)
 # The surveyed villa ring has an open courtyard: fill its ground separately,
 # without capping the atrium or changing surrounding streets.
 for villa in parts(p):
  for ring in villa.interiors:
   court=Polygon(ring)
   B.planar('tile',court,.12,True)
   inset=court.buffer(-3.0)
   cx,cz=court.centroid.x,court.centroid.y
   walks=unary_union([box(cx-1.6,cz-50,cx+1.6,cz+50),box(cx-50,cz-1.6,cx+50,cz+1.6),Point(cx,cz).buffer(5.5,resolution=32)])
   beds=inset.difference(walks)
   B.planar('sage',beds,.14)
   for bed in parts(beds):
    edging=bed.buffer(.16).difference(bed)
    B.planar('stone',edging,.18)
   # Low central stone basin, distinct from the walkable court.
   basin=Point(cx,cz).buffer(2.25,resolution=40)
   B.shell(basin,.12,.58,'stone',roof=False,solid=True)
   B.planar('water',basin.buffer(-.22),.44)
   B.planar('marble',basin.difference(basin.buffer(-.22)),.58)
 for poly in parts(p):
  for ring in [poly.exterior,*poly.interiors]:
   ps=list(ring.coords)
   for a,b in zip(ps,ps[1:]):
    L=math.dist(a,b)
    if L<2:continue
    F,L,nx,nz=facade_frame(B,a,b,p,.15)
    for yy in [2.8,5.5]:
     F.box('ivory',(L/2,yy,-.02),(L,.12,.14))
    B.detail=1
    for x in np.arange(1.4,L-1,3.6):
     for yy in [.65,3.35]:
      F.box('mgm-glass',(x,yy+.9,-.04),(1.45,1.8,.035))
      for dx in [-.82,.82]:F.box('ivory',(x+dx,yy+.92,-.10),(.11,2.02,.12))
      F.box('ivory',(x,yy+1.96,-.10),(1.78,.12,.18))
      F.box('ivory',(x,yy-.06,-.12),(1.9,.14,.28))
    B.detail=0
    # Shallow pitched red-tile eaves along the irregular villa outline.
    B.face('terracotta',[F.p(0,6.05,-.4),F.p(L,6.05,-.4),F.p(L,7.35,3.2),F.p(0,7.35,3.2)])
 atrium=footprint('way/115095165')
 for poly in parts(atrium):
  c=poly.centroid;ps=list(poly.exterior.coords)[:-1]
  for a,b in zip(ps,ps[1:]+ps[:1]):
   B.face('mgm-glass',[(a[0],6.1,a[1]),(b[0],6.1,b[1]),(c.x,17.1,c.y)])
   B.tube('mgm-frame',(a[0],6.16,a[1]),(c.x,17.16,c.y),.09,8)
   for t in np.arange(.125,1,.125):
    aa=(a[0]*(1-t)+c.x*t,6.16+11*t,a[1]*(1-t)+c.y*t)
    bb=(b[0]*(1-t)+c.x*t,6.16+11*t,b[1]*(1-t)+c.y*t)
    B.tube('mgm-frame',aa,bb,.06,6)
   for t in np.arange(.08,1,.08):
    B.tube('mgm-frame',(a[0]*(1-t)+b[0]*t,6.16,a[1]*(1-t)+b[1]*t),(c.x,17.16,c.y),.035,6)
