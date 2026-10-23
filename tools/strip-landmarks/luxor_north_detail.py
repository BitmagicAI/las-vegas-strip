"""Luxor low north lobby, tower plinths and open colonnades; Earth2022/map.
Dimensions above datum are estimates; hotel towers and guest access are retained.
"""
from common import *
from building_surfaces import BuildingSurfaces
from forum_shops import facade_frame
from luxor_facades import Access
ID='way/136520122'
def exterior(B):
 B.property='luxorExterior-exterior';B.source='podium/'+ID;B.detail=0
 p=footprint(ID);lobby=p.intersection(box(-278.3,2090,-230,2127.9));rest=p.difference(lobby)
 records=[dict(id='north-lobby',shape=lobby,height=10,base=0),dict(id=ID,shape=rest,height=20,base=0)]
 towerids=[f['id'] for f in SURVEY if f['id'].startswith(('way/1365166','way/1365201')) and 20< f['height']<=80]
 records += [dict(BYID[i],shape=footprint(i)) for i in towerids]
 surface=BuildingSurfaces(records);access=Access(next(p for p in json.load(open('build/highrises/plan.json')) if p['key']=='luxor'))
 for r in records[:2]:
  h=r['height']
  for pp in parts(r['shape']):
   cc=list(pp.exterior.coords)
   for a,b in zip(cc,cc[1:]):
    F,L,nx,nz=facade_frame(B,a,b,pp,0);line=LineString([a,b])
    vis=surface.wall(r['id'],a,b,.24,h,access)
    reg=unary_union([Polygon([(line.project(Point(v[0],v[2])),v[1]) for v in tri]) for tri in vis])
    if r['id']=='north-lobby' and nz<-.8:
     at=line.project(Point(-254,2094));reg=reg.difference(box(at-4,.24,at+4,9.0))
    def patch(mat,region,offset=0,solid=False):
     for q in parts(region):
      for tri in triangles(q):B.face(mat,[(line.interpolate(x).x+nx*offset,y,line.interpolate(x).y+nz*offset) for x,y in list(tri.exterior.coords)[:-1]],solid)
    patch('luxor-stone',reg,solid=True)
    for y in [1,h-.9,h-.25]:patch('luxor-band',reg.intersection(box(0,y,L,y+.16)),.18)
    for x in np.arange(1,L-2,4.6):
     patch('luxor-glass',reg.intersection(box(x,1.25,min(x+3.6,L-.3),min(h-1.4,6.3))),.24)
     for yy in [2.6,4.3]:patch('luxor-band',reg.intersection(box(x,yy,min(x+3.6,L-.3),yy+.08)),.28)
    for y in np.arange(1,h-1,1.5):patch('luxor-joint',reg.intersection(box(0,y,L,y+.025)),.035)
   roof=surface.roof(r['id'],pp,h);B.planar('luxor-membrane-paint',roof,h+.025,True)
   for poly in parts(roof.buffer(-.35)):
    for a,b in zip(list(poly.exterior.coords),list(poly.exterior.coords)[1:]):B.tube('luxor-band',(a[0],h+.25,a[1]),(b[0],h+.25,b[1]),.22,4)
 # The mapped connector is an elevated enclosed bridge, not a solid ground box.
 B.source='luxor-excalibur-connector'
 bridge=footprint('way/115647257')
 B.planar('luxor-stone',bridge,5.24,True)
 B.planar('luxor-membrane-paint',bridge,9.8,True)
 B.planar('luxor-stone',lobby,5.24,True)
 for pp in parts(bridge):
  cc=list(pp.exterior.coords)
  for a,b in zip(cc,cc[1:]):
   if math.dist(a,b)<10:continue # Both ends connect to occupied lobbies.
   F,L,nx,nz=facade_frame(B,a,b,pp,0)
   F.box('luxor-stone',(L/2,5.5,0),(L,.52,.24),True)
   F.box('luxor-glass',(L/2,7.4,0),(L,3.25,.12),True)
   F.box('luxor-band',(L/2,9.55,0),(L,.5,.3))
   for x in np.arange(0,L,1.3):F.box('luxor-band',(x,7.55,-.1),(.075,3.6,.14))
 B.source='luxor-north-colonnade' 
 # Four open courtyard frames between the stepped wings. No solid courtyard roof.
 for xa,xb in [(-387,-335),(-309,-281),(-228,-197),(-171,-122)]:
  for z in [2100,2123]:
   B.box('luxor-stone',((xa+xb)/2,15.2,z),(xb-xa+.8,.95,.95))
   for x in np.linspace(xa,xb,max(2,round((xb-xa)/8)+1)):
    B.box('luxor-stone',(x,7.5,z),(.8,14.6,.8),True)
    B.box('luxor-band',(x,1,z),(1.3,1.5,1.3),True)
    B.box('luxor-band',(x,14.35,z),(1.35,.8,1.35))
    B.box('luxor-stone',(x,15.2,2111.5),(.75,.8,23))
 B.source='luxor-north-roof-detail'
 for x,z in [(-262,2160),(-245,2160),(-262,2176),(-245,2176)]:
  B.box('luxor-service-paint',(x,20.35,z),(3.8,.7,3.8))
  for a,b in zip([(-2,-2),(2,-2),(2,2),(-2,2)],[ (2,-2),(2,2),(-2,2),(-2,-2)]):B.face('luxor-glass',[(x+a[0],20.7,z+a[1]),(x+b[0],20.7,z+b[1]),(x,22,z)])
 return towerids
