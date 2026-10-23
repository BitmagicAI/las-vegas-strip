"""Fontainebleau exterior, official July 2026 map + 2025 arrival photograph.
Map is schematic: pool plan fitted to surveyed podium, height 16 m estimated.
Existing guest circulation and tower collision remain their original owners.
"""
from common import *
from building_surfaces import BuildingSurfaces
from luxor_facades import Access
KEY='fontainebleauExterior'
def exterior(B):
 B.property=KEY+'-exterior';B.detail=0
 ids=['way/134068317','way/543641007','way/1418135381','way/134068318']
 records=[dict(BYID[i],shape=footprint(i),height=16 if i=='way/134068317' else BYID[i]['height']) for i in ids]
 surface=BuildingSurfaces(records);plan=next(p for p in json.load(open('build/highrises/plan.json')) if p['key']=='fontainebleau');access=Access(plan)
 for r in records:
  ident=r['id'];p=r['shape'];h=r['height'];tower=ident=='way/134068318';garage=ident=='way/543641007'
  B.source='tower/fontainebleau' if tower else 'podium/'+ident
  for poly in parts(p):
   for ring in [poly.exterior,*poly.interiors]:
    ps=list(ring.coords)
    for a,b in zip(ps,ps[1:]):
     line=LineString([a,b]);L=line.length
     if L<.1:continue
     ux,uz=(b[0]-a[0])/L,(b[1]-a[1])/L;nx,nz=-uz,ux;mid=line.interpolate(.5,normalized=True)
     if p.contains(Point(mid.x+nx*.1,mid.y+nz*.1)):nx,nz=-nx,-nz
     region=unary_union([Polygon([(line.project(Point(v[0],v[2])),v[1]) for v in tri]) for tri in surface.wall(ident,a,b,r['base'],h,access)])
     def patch(mat,x0,y0,x1,y1,offset=.24):
      for q in parts(region.intersection(box(x0,y0,x1,y1))):
       for tri in triangles(q):B.face(mat,[(a[0]+ux*x+nx*offset,y,a[1]+uz*x+nz*offset) for x,y in list(tri.exterior.coords)[:-1]])
     patch('fb-glass' if tower else 'fb-limestone',0,0,L,h)
     if tower:
      # Narrow dark joints, not the old brilliant stair-stepped grille.
      for y in np.arange(19,h,3.35):patch('fb-joint',0,y,L,y+.055,.26)
      for y,w in [(112,2.8),(h-1.1,1.1)]:patch('fb-silver',0,y,L,y+w,.34)
      B.detail=1
      for x in np.arange(1.55,L,1.55):patch('fb-joint',x,16,x+.035,h,.27)
      B.detail=0
     elif garage:
      for y in np.arange(2.5,h-1,3.5):patch('fb-shadow',0,y,L,y+1.65,.28)
      for x in np.arange(0,L,9):patch('fb-limestone',x,0,min(x+.6,L),h,.38)
     else:
      west=nx<-.25;public=west or nz<-.5 or nz>.7
      for y in [0.6,6.4,12.2,h-.6]:patch('fb-silver',0,y,L,min(h,y+.25),.31)
      if public:
       for x in np.arange(.7,L-.8,4.4):
        patch('fb-glass',x,.8,min(x+3.7,L-.3),5.9,.29)
        patch('fb-metal',x,.8,min(x+.07,L),5.9,.34)
        patch('fb-glass',x,7.3,min(x+3.7,L-.3),11.6,.29)
      B.detail=1
      for x in np.arange(0,L,1.8):patch('fb-joint',x,0,x+.018,h,.25)
      B.detail=0
   if tower or garage:B.planar('fb-flat-roof',surface.roof(ident,poly,h),h+.045)
 # Level 3: map-derived connected, angular pools; schematic map is not a survey.
 podium=footprint('way/134068317');roof=surface.roof('way/134068317',podium,16)
 def mapped(points):return Polygon([(1023+(x-317)*.60,-2540+(z-160)*.694) for x,z in points]).buffer(0)
 poolpaths=[[(614,286),(628,286),(640,315),(679,317),(710,326),(703,337),(655,338),(656,350),(679,385),(686,407),(676,413),(665,399),(649,373),(644,353),(622,368),(609,377),(620,392),(620,406),(602,409),(581,395),(564,400),(558,391),(560,383),(610,349)],[(815,304),(841,296),(837,310),(824,323),(810,322)],[(594,212),(602,212),(611,235),(602,238)],[(618,438),(637,431),(660,434),(675,446),(674,459),(650,462),(638,451),(620,451)]]
 pools=unary_union([mapped(q) for q in poolpaths]).intersection(roof.buffer(-2))
 B.source='podium/way/134068317'
 terrace=mapped([(588,180),(632,249),(736,280),(889,250),(873,423),(705,430),(688,481),(532,475),(521,395),(558,330)]).intersection(roof)
 B.planar('fb-paving',terrace.difference(pools),16.07,True)
 B.planar('fb-flat-roof',roof.difference(terrace).difference(pools),16.07,True)
 B.planar('fb_pool',pools,15.82)
 B.planar('fb-limestone',pools.buffer(.65).difference(pools),16.10)
 for poly in parts(pools):
  ps=list(poly.exterior.coords)
  for a,b in zip(ps,ps[1:]):B.face('fb-pool-tile',[(a[0],15.5,a[1]),(b[0],15.5,b[1]),(b[0],16.1,b[1]),(a[0],16.1,a[1])],True)
  B.planar('fb-pool-tile',poly,14.9,True)
 # Low-rise volumes indicated on the official deck plan: Oasis Room, La Cote,
 # and the LIV mass along the south edge; fitted schematic footprints.
 for outline,height in [([(479,329),(529,338),(512,394),(455,382)],6), ([(723,342),(774,342),(780,392),(725,393)],4.5), ([(420,484),(663,478),(660,523),(411,525)],7)]:
  q=mapped(outline).intersection(roof).difference(pools.buffer(1))
  B.shell(q,16.12,16.12+height,'fb-limestone',roof=False,solid=False)
  B.planar('fb-flat-roof',q,16.12+height)
 # Reuse the existing PH chaise design, placed around the pool boundaries.
 B.detail=1
 clear=terrace.difference(pools.buffer(2.2))
 for poly in parts(pools):
  for distance in np.arange(0,poly.exterior.length,3.2):
   p=poly.exterior.interpolate(distance);near=poly.exterior.interpolate((distance+.1)%poly.exterior.length)
   dx,dz=near.x-p.x,near.y-p.y;length=math.hypot(dx,dz)
   if length<.01:continue
   nx,nz=-dz/length,dx/length
   if poly.contains(Point(p.x+nx*.1,p.y+nz*.1)):nx,nz=-nx,-nz
   x,z=p.x+nx*3.1,p.y+nz*3.1
   if not clear.contains(Point(x,z)):continue
   F=Frame(B,x,z,math.atan2(nx,nz),y=16.1)
   F.box('ph-awning',(0,.42,0),(.68,.13,1.95));F.box('ph-metal',(0,.3,0),(.72,.08,2))
   for xx in [-.28,.28]:F.box('ph-metal',(xx,.14,.1),(.035,.28,1.65))
   B.face('ph-awning',[F.p(-.34,.49,-.3),F.p(.34,.49,-.3),F.p(.34,.95,-.94),F.p(-.34,.95,-.94)])
 B.detail=0
 # Terrace edge parapet and pool-side planting beds; keep tower/garage boundaries clear.
 for poly in parts(roof):
  ps=list(poly.exterior.coords)
  for a,b in zip(ps,ps[1:]):
   if podium.boundary.distance(LineString([a,b]).interpolate(.5,normalized=True))>.6:continue
   B.face('fb-limestone',[(a[0],16.05,a[1]),(b[0],16.05,b[1]),(b[0],17.12,b[1]),(a[0],17.12,a[1])],True)
 from fontainebleau_arrival import arrival
 arrival(B)
 return dict(key=KEY,name='Fontainebleau exterior and pool terrace',center=[1210,0,-2390],bounds=[1020,-2560,1410,-2260],building='fontainebleau',structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
