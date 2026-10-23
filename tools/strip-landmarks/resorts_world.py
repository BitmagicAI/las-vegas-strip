"""Resorts World: surveyed bent tower, bronze curtainwall and red core/end panels.
Podium fitted to existing footprint using Earth 2022–24 + Enclos built references.
"""
from common import *
from building_surfaces import BuildingSurfaces
from luxor_facades import Access
from forum_shops import facade_frame
KEY='resortsWorldExterior'
def exterior(B):
 B.property=KEY+'-exterior';B.detail=0
 # Affine fit of official Level 5 schematic: two tower anchors + infinity tip.
 from shapely.affinity import affine_transform
 src=np.array([[480,150,1],[930,180,1],[718,651,1]],float)
 cx=np.linalg.solve(src,np.array([530,678,550]));cz=np.linalg.solve(src,np.array([-2115,-2040,-1950]))
 def mapped(q):return affine_transform(q,[cx[0],cx[1],cz[0],cz[1],cx[2],cz[2]])
 main=Point(553,310).buffer(49,resolution=32).difference(Point(553,310).buffer(24,resolution=32)).difference(box(580,296,615,342))
 main=main.union(LineString([(575,365),(605,416),(677,438),(747,426),(784,413)]).buffer(14,resolution=24))
 shapes=[main,Point(573,500).buffer(23,resolution=32),Polygon([(425,394),(501,426),(491,442),(418,411)]),LineString([(875,437),(875,529)]).buffer(11,resolution=16),box(688,585,746,610),Polygon([(668,644),(760,644),(746,663),(695,670)])]
 pools=unary_union([mapped(q) for q in shapes]).intersection(footprint('way/972129019').buffer(-1)).difference(footprint('way/316303708').buffer(.3))
 terrace=mapped(Polygon([(310,350),(400,200),(590,140),(730,160),(1020,260),(1035,610),(820,615),(800,672),(680,685),(630,614),(530,613),(493,490),(403,452),(310,443)])).intersection(footprint('way/972129019')).difference(footprint('way/316303708'))
 ids=['way/316303708','way/972129019','way/972129020','way/972129022']
 records=[dict(BYID[i],shape=footprint(i),height=20 if i=='way/972129019' else 24 if i=='way/972129022' else BYID[i]['height']) for i in ids]
 surface=BuildingSurfaces(records);plan=next(p for p in json.load(open('build/highrises/plan.json')) if p['key']=='resorts-world');access=Access(plan)
 for r in records:
  ident=r['id'];p=r['shape'];h=r['height'];tower=ident=='way/316303708';garage=ident=='way/972129020';theatre=ident=='way/972129022'
  B.source='tower/resorts-world' if tower else 'podium/'+ident
  for poly in parts(p):
   for ring in [poly.exterior,*poly.interiors]:
    ps=list(ring.coords)
    for a,b in zip(ps,ps[1:]):
     line=LineString([a,b]);L=line.length
     if L<.1:continue
     F,L,nx,nz=facade_frame(B,a,b,p,.27);ux,uz=(b[0]-a[0])/L,(b[1]-a[1])/L;mid=line.interpolate(.5,normalized=True)
     region=unary_union([Polygon([(line.project(Point(v[0],v[2])),v[1]) for v in tri]) for tri in surface.wall(ident,a,b,r['base'],h,access)])
     def patch(mat,x0,y0,x1,y1,offset=.24):
      for q in parts(region.intersection(box(x0,y0,x1,y1))):
       for tri in triangles(q):B.face(mat,[(a[0]+ux*x+nx*offset,y,a[1]+uz*x+nz*offset) for x,y in list(tri.exterior.coords)[:-1]])
     if tower:
      end=L<24 and (mid.x<512 or mid.x>697 or 595<mid.x<633)
      patch('rw-red' if end else 'rw-bronze',0,0,L,h)
      patch('rw-red',0,h-2,L,h,.35)
      if not end:
       for y in np.arange(22,h-2,3.35):patch('rw-mullion',0,y,L,y+.11,.28)
       B.detail=1
       for x in np.arange(1.8,L,1.8):patch('rw-mullion',x,20,x+.03,h-2,.28)
       B.detail=0
      # The western wing display follows the actual bent facade, not a flat board.
      if nz>.5 and mid.x<600:
       patch('rw-led',1,44,L-1,133,.40)
       for y in [43.5,133]:patch('rw-metal',0,y,L,y+.5,.43)
      if end and mid.x>697:patch('rw-led',2,70,L-2,180,.4)
      if L>30 and mid.x>650 and nx>.3:F.text('CONRAD',(L*.5,h-8,-.16),2.6,'rw-white')
      if 550<mid.x<585 and nz>.5:F.text('Hilton',(L*.5,h-8,-.16),3,'rw-white')
     elif garage:
      patch('rw-white',0,0,L,h)
      for y in np.arange(2,h-1,3.3):patch('rw-shadow',0,y,L,y+1.5,.3)
      for x in np.arange(0,L,12):patch('rw-white',x,0,min(x+.9,L),h,.35)
     else:
      from resorts_world_frontage import facade
      facade(B,F,L,nx,nz,mid,ident,h,patch)
   if not tower:B.planar('rw-flat-roof',surface.roof(ident,poly,h).difference(terrace) if ident=='way/972129019' else surface.roof(ident,poly,h),h+.055)
   else:B.planar('rw-flat-roof',poly,h+.04)
 B.source='podium/way/972129019'
 B.planar('fb-paving',terrace.difference(pools),20.07,True)
 B.planar('fb_pool',pools,19.82)
 B.planar('rw-white',pools.buffer(.6).difference(pools),20.1)
 for q in parts(pools):
  B.planar('fb-pool-tile',q,18.8,True)
  ps=list(q.exterior.coords)
  for a,b in zip(ps,ps[1:]):B.face('fb-pool-tile',[(a[0],18.8,a[1]),(b[0],18.8,b[1]),(b[0],20.1,b[1]),(a[0],20.1,a[1])],True)
 from resorts_world_frontage import entry
 entry(B)
 # Existing podium roof service equipment with shared batches, away from tower.
 B.detail=1
 roof=surface.roof('way/972129019',footprint('way/972129019'),20)
 for x in np.arange(430,745,22):
  for z in np.arange(-2110,-1780,24):
   if roof.contains(box(x-2,z-2,x+2,z+2)) and not terrace.buffer(2).contains(Point(x,z)):
    B.box('rw-metal',(x,20.8,z),(3.2,1.5,3.2));B.box('rw-shadow',(x,21.57,z),(2.8,.06,2.8))
 B.detail=0
 return dict(key=KEY,name='Resorts World exterior',center=[590,0,-1980],bounds=[360,-2270,790,-1750],building='resorts-world',structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
