"""Panorama's curved balcony towers, recessed sky courts and parking bases.
Earth 2022-11-09 establishes forms; 12m garages and recess dimensions are estimates.
"""
from common import *
from building_surfaces import BuildingSurfaces
from luxor_facades import Access
from forum_shops import facade_frame
KEY='panoramaExterior'
TOWERS=['way/495545499','way/495545514']
GARAGES=['way/495545498','way/495545510']
LOW=['way/495545500','way/495545502','way/495545517','way/495545518']
DETAIL=['way/495545503','way/495545504','way/495545507','way/495545508','way/495545509','way/495545511','way/495545512','way/495545513','way/495545515','way/495545516','way/495545519','way/495545520']
def exterior(B):
 B.property=KEY+'-exterior';B.detail=0
 records=[dict(BYID[i],shape=footprint(i).simplify(.14,preserve_topology=True),height=12 if i in GARAGES else BYID[i]['height']) for i in TOWERS+GARAGES+LOW]
 surf=BuildingSurfaces(records);access=Access(next(p for p in json.load(open('build/highrises/plan.json')) if p['key']=='panorama'))
 for r in records:
  p=r['shape'];h=r['height'];tower=r['id'] in TOWERS;garage=r['id'] in GARAGES;cz=p.centroid.y;B.source='tower/panorama' if tower else 'podium/'+r['id']
  recessY=72 if r['id']==TOWERS[0] else 39
  for poly in parts(p):
   ps=list(poly.exterior.coords)
   for a,b in zip(ps,ps[1:]):
    F,L,nx,nz=facade_frame(B,a,b,p,.06)
    if L<.1:continue
    line=LineString([a,b]);ux,uz=(b[0]-a[0])/L,(b[1]-a[1])/L
    region=unary_union([Polygon([(line.project(Point(v[0],v[2])),v[1]) for v in t]) for t in surf.wall(r['id'],a,b,0,h,access)])
    broad=tower and abs(nx)>.65
    cut=Polygon()
    if broad:
     # The opening is recessed four metres; it is not a dark decal on the skin.
     x0=max(0,min(L,(cz-10-a[1])/uz));x1=max(0,min(L,(cz+10-a[1])/uz))
     lo,hi=sorted([x0,x1])
     if hi-lo>.05:
      coords=[(x,recessY+3*((a[1]+uz*x-cz)/10)**2) for x in np.linspace(lo,hi,7)]
      cut=Polygon(coords+[(hi,recessY+8),(lo,recessY+8)]).intersection(region)
    visible=region.difference(cut)
    def patch(mat,x0,y0,x1,y1,offset=.13,mask=None):
     if x1<=x0 or y1<=y0:return
     for q in parts((visible if mask is None else mask).intersection(box(x0,y0,x1,y1))):
      for t in triangles(q):B.face(mat,[(a[0]+ux*x+nx*offset,y,a[1]+uz*x+nz*offset) for x,y in list(t.exterior.coords)[:-1]])
    patch('pa-glass' if tower else 'pa-white',0,0,L,h)
    if tower:
     for y in np.arange(5,100,3.05):
      patch('pa-spandrel',0,y,L,y+.75,.18)
      patch('pa-white',0,y+.65,L,y+.93,.80)
      patch('pa-glass',0,y+.95,L,y+1.82,.78)
      patch('pa-metal',0,y+1.8,L,y+1.85,.85)
      for q in parts(visible.intersection(box(0,y+.65,L,y+.66))):
       left,_,right,_=q.bounds
       B.upface('pa-white',[(a[0]+ux*t+nx*d,y+.65,a[1]+uz*t+nz*d) for t,d in [(left,.13),(right,.13),(right,.80),(left,.80)]])
     for x in np.arange(.3,L,1.65):patch('pa-metal',x,4,min(x+.055,L),100,.23)
     if broad:
      patch('pa-white',0,3,min(.16,L),100,.28)
     else:
      for x in np.arange(0,L,3.5):patch('pa-white',x,3,min(x+.24,L),100,.25)
     if not cut.is_empty:
      patch('pa-glass',0,0,L,h,-4,cut)
      for c in parts(cut):
       ring=list(c.exterior.coords)
       for v,w in zip(ring,ring[1:]):
        # Adjacent curved facade segments share the same hollow court: no bulkhead there.
        if abs(v[0]-w[0])<.001 and (abs(v[0])<.001 or abs(v[0]-L)<.001):continue
        B.face('pa-white',[(a[0]+ux*t+nx*d,y,a[1]+uz*t+nz*d) for (t,y),d in [(v,.13),(w,.13),(w,-4),(v,-4)]])
     F.box('pa-white',(L/2,101.12,0),(L,.24,.5))
    elif garage:
     for y in [1.0,4.5,8.0]:
      patch('pa-shadow',0,y,L,y+2.0,.16)
      for x in np.arange(0,L,5.8):patch('pa-white',x,y,min(x+.5,L),y+2.1,.21)
     F.box('pa-white',(L/2,12.55,0),(L,1.1,.4))
    else:
     for y in [.6,4.1]:
      for x in np.arange(.5,L,3.4):patch('pa-glass',x,y,min(x+2.5,L-.2),min(y+2.4,h-.3),.18)
     F.box('pa-white',(L/2,h+.2,0),(L,.4,.35))
    if not tower:
     for t in surf.wall(r['id'],a,b,0,h,access):
      c=B.solids[B.property];n=len(c['vertices'])//3;c['vertices'].extend(v for pt in t for v in pt);c['indices'].extend([n,n+1,n+2])
   roof=surf.roof(r['id'],poly,h);B.planar('pa-parking' if garage else 'pa-roof',roof,h+.02,not tower)
   if garage:
    # Parking stripes only on the uncovered portion of the actual mapped roof.
    for z in np.arange(poly.bounds[1]+8,poly.bounds[3]-5,16):
     for x in np.arange(poly.bounds[0]+5,poly.bounds[2]-4,2.7):
      stripe=box(x,z,x+.08,z+5).intersection(roof.buffer(-1));B.planar('pa-line',stripe,h+.045)
  if tower:
   # Curved white parapet lip follows the tower, with actual rooftop services.
   B.planar('pa-white',p.buffer(.3).difference(p.buffer(-.4)),101.3)
   for z in np.arange(cz-24,cz+25,8):B.box('pa-vent',(p.centroid.x,102.1,z),(6,2,3.5))
   B.box('pa-white',(p.centroid.x,102.9,cz),(5,3.8,16))
 # Mapped rooftop access/vent huts and small gate shelters get explicit replacements.
 garages=unary_union([r['shape'] for r in records if r['id'] in GARAGES])
 for ident in DETAIL:
  B.source='utility/'+ident;hut=footprint(ident);base=12.02 if garages.covers(hut.centroid) else 0
  height=2.6 if base else min(3.5,BYID[ident]['height'])
  B.shell(hut,base,base+height,'pa-white',solid=True,roof=False)
  B.planar('pa-roof',hut,base+height+.02)
 # Western courts are between the low apartment wings and the towers.
 B.source='pool-courts';occupied=unary_union([r['shape'] for r in records])
 for cz in [935,1024]:
  deck=box(-901,cz-22,-871,cz+22).difference(occupied.buffer(.25))
  pool=rotate(box(-894,cz-12,-881,cz+12),-12,origin=(-887.5,cz)).intersection(deck.buffer(-1.5))
  B.planar('pa-paving',deck.difference(pool),.31,True);B.planar('water',pool,.22);B.planar('pa-white',pool,.01,True);B.planar('pa-white',pool.buffer(.45).difference(pool),.34,True)
  for z in np.arange(cz-17,cz+18,3):
   for x in [-898,-875]:
    pad=box(x-.5,z-1,x+.5,z+1)
    if deck.difference(pool.buffer(1)).contains(pad):B.box('pa-white',(x,.55,z),(.75,.15,1.8));B.box('pa-metal',(x,.4,z),(.6,.15,1.5))
 return dict(key=KEY,name='Panorama Towers exteriors and parking courts',center=[-851,0,980],bounds=[-920,895,-767,1068],building='panorama',structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
