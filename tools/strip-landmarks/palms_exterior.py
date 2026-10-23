"""Palms: three photo-fitted towers replacing the erroneous whole-site 78m prism.
Earth March2024, CVU Fantasy139.6m/Place157.8m; other dimensions estimated.
"""
from common import *
from building_surfaces import BuildingSurfaces
from luxor_facades import Access
from forum_shops import facade_frame
def courtyard():
 return box(-1880,139,-1780,184).buffer(-3).buffer(3)
KEY='palmsExterior';LOW=['way/27504257'];PARENT='relation/7655651'
def records():
 parent=footprint(PARENT)
 ivory=Polygon([(-1920,124),(-1912,103),(-1827,103),(-1809,113),(-1807,124),(-1817,136),(-1908,136)])
 # Curved shallow slab: front bows toward the south, rear follows it.
 xs=np.linspace(-1945,-1855,25);front=[(x,228+12*math.sin((x+1945)/90*math.pi)) for x in xs];back=[(x,207+12*math.sin((x+1945)/90*math.pi)) for x in xs]
 fantasy=Polygon(front+list(reversed(back)))
 place=Polygon([(-2330,171),(-2305,163),(-2289,238),(-2313,245)])
 garage=parent.intersection(box(-2276,155,-2150,255))
 rs=[dict(id=PARENT,shape=parent.difference(courtyard()),base=0,height=14),dict(id='palms-ivory',shape=ivory,base=0,height=121),dict(id='palms-fantasy',shape=fantasy,base=0,height=139.6),dict(id='palms-place',shape=place,base=0,height=157.8),dict(id='palms-garage',shape=garage,base=0,height=19)]
 rs.append(dict(id=LOW[0],shape=footprint(LOW[0]),base=0,height=19))
 return rs
def exterior(B):
 B.property=KEY+'-exterior';B.detail=0
 rs=records();surf=BuildingSurfaces(rs);plan=next(p for p in json.load(open('build/highrises/plan.json')) if p['key']=='palms');access=Access(plan)
 for r in rs:
  ident=r['id'];p=r['shape'];h=r['height'];tower=ident in ['palms-ivory','palms-fantasy','palms-place'];ivory=ident=='palms-ivory';garage=ident in ['palms-garage',LOW[0]]
  B.source='tower/palms' if tower else 'podium/'+ident
  for poly in parts(p):
   for ring in [poly.exterior,*poly.interiors]:
    ps=list(ring.coords)
    for a,b in zip(ps,ps[1:]):
     line=LineString([a,b]);L=line.length
     if L<.08:continue
     F,_,nx,nz=facade_frame(B,a,b,p,.08);ux,uz=(b[0]-a[0])/L,(b[1]-a[1])/L
     tris=surf.wall(ident,a,b,0,h,access);region=unary_union([Polygon([(line.project(Point(v[0],v[2])),v[1]) for v in t]) for t in tris])
     def patch(mat,x0,y0,x1,y1,off=.13):
      if x1<=x0 or y1<=y0:return
      for q in parts(region.intersection(box(x0,y0,x1,y1))):
       for t in triangles(q):B.face(mat,[(a[0]+ux*x+nx*off,y,a[1]+uz*x+nz*off) for x,y in list(t.exterior.coords)[:-1]])
     patch('pm-white' if ivory else 'pm-glass' if tower else 'pm-stone',0,0,L,h)
     if ivory:
      for x in np.arange(.85,L-1,2.65):
       for y in np.arange(15,118,3.5):
        patch('pm-glass',x,y,min(x+1.55,L-.6),y+2.65,.20)
        patch('pm-sill',x,y-.13,min(x+1.55,L-.6),y,.24)
      patch('pm-white',0,h-1,L,h,.3)
     elif tower:
      for y in np.arange(16,h-1,3.3):patch('pm-white' if ident=='palms-fantasy' else 'pm-frame',0,y,L,y+(.22 if ident=='palms-fantasy' else .1),.23)
      for x in np.arange(.8,L,1.65):patch('pm-frame',x,14,min(x+.045,L),h,.24)
      if L>22 and ident=='palms-place':
       for x in np.arange(0,L,13):F.box('pm-white',(x,h/2,0),(.65,h,.6))
      if L<23 and ident=='palms-place':patch('pm-white',0,14,L,h,.25)
      patch('pm-white',0,h-1.2,L,h,.27)
      # White center spine on Fantasy south face, clipped per segment.
      if ident=='palms-fantasy' and nz>.6:
       for q in parts(region.intersection(box(0,0,L,h))):
        spine=box(-1904,0,-1896,h)
        xlo=max(0,(-1904-a[0])/ux) if ux>0 else 0
        xhi=min(L,(-1896-a[0])/ux) if ux>0 else 0
        if xhi>xlo:patch('pm-white',xlo,14,xhi,h,.35)
     elif garage:
      for y in np.arange(1,18,3.5):patch('pm-shadow',0,y,L,y+2,.2)
      for x in np.arange(0,L,7):patch('pm-white',x,0,min(x+.65,L),h,.3)
     else:
      patch('pm-plinth',0,0,L,.8,.19)
      for x in np.arange(.6,L-1,5.4):
       patch('pm-glass',x,.8,min(x+4.1,L-.3),6.4,.22)
       for edge in [x,x+4.1]:patch('pm-frame',edge,.8,min(edge+.09,L),6.4,.25)
       patch('pm-stone',x,3.2,min(x+4.1,L-.3),3.32,.27)
      for y in [7,12.5]:patch('pm-white',0,y,L,y+.35,.3)
     F.box('pm-white',(L/2,h+.15,0),(L,.3,.45))
     # Coarse shell collision only; windows do not become individual colliders.
     for t in tris:
      c=B.solids[B.property];n=len(c['vertices'])//3;c['vertices'].extend(v for pt in t for v in pt);c['indices'].extend([n,n+1,n+2])
   roof=surf.roof(ident,poly,h);B.planar('pa-parking' if garage else 'pm-roof',roof,h+.025,True)
   if garage:
    for z in np.arange(poly.bounds[1]+5,poly.bounds[3]-3,15):
     for x in np.arange(poly.bounds[0]+3,poly.bounds[2]-3,2.7):B.planar('pa-line',box(x,z,x+.08,z+5).intersection(roof.buffer(-1)),h+.06)
   elif not tower:
    B.detail=1
    for x in np.arange(poly.bounds[0]+12,poly.bounds[2]-8,27):
     for z in np.arange(poly.bounds[1]+10,poly.bounds[3]-8,24):
      if roof.contains(box(x-2,z-2,x+2,z+2)):B.box('pm-white',(x,h+.75,z),(4,1.45,3.2));B.box('pm-vent',(x,h+1.5,z),(3.6,.08,2.8))
    B.detail=0
 # Ivory's barrel crown is a curved roof, not an extra rectangular storey.
 B.source='tower/palms'
 for x0,x1 in zip(np.linspace(-1912,-1827,41)[:-1],np.linspace(-1912,-1827,41)[1:]):
  y0=121+8*math.sin((x0+1912)/85*math.pi);y1=121+8*math.sin((x1+1912)/85*math.pi)
  B.face('pm-white',[(x0,121,103),(x1,121,103),(x1,y1,103),(x0,y0,103)])
  B.face('pm-white',[(x0,121,136),(x1,121,136),(x1,y1,136),(x0,y0,136)])
  B.upface('pm-roof',[(x0,y0,103),(x1,y1,103),(x1,y1,136),(x0,y0,136)])
 # Roof pavilion / white penthouse bands visible in both oblique references.
 B.box('pm-white',(-1900,139.2,223),(38,.6,25));B.box('pm-glass',(-1900,136.8,223),(30,4.2,19))
 Frame(B,-1870,104,0).text('PALMS',(0,115,-.4),4.0,'pm-letter')
 # Preserve the guest approach at its relocated exterior endpoint.
 t=plan['towers'][0];F=Frame(B,t['origin'][0],t['origin'][2],t['yaw']);e=t['lobbyFront']
 F.box('pm-stone',(0,-.4,e-5.8),(4.8,.8,12),True);F.box('pm-white',(0,4.8,e-1.5),(8,.25,3.8),True)
 for side in [-1,1]:F.box('pm-stone',(side*3.5,2.34,e-2.8),(.3,4.68,.3),True)
 # Arrival canopy on the east; posts kept out of the central driveway.
 B.source='arrival';B.box('pm-white',(-1772,7.4,148),(25,.6,18),True)
 for z in [140,156]:B.box('pm-stone',(-1761,3.55,z),(.65,7.1,.65),True)
 # Mapped pool voids: leave actual holes in the podium, no water on its roof.
 parent=footprint(PARENT)
 B.planar('pm-stone',courtyard().intersection(parent),.32,True)
 for poly in parts(parent):
  for ring in poly.interiors:
   pool=Polygon(ring)
   if pool.area<100:continue
   B.source='pool-court';B.planar('water',pool,.18);B.planar('pm-white',pool,-1.1,True)
   for a,b in zip(list(ring.coords),list(ring.coords)[1:]):B.face('pm-white',[(a[0],-1.1,a[1]),(b[0],-1.1,b[1]),(b[0],.18,b[1]),(a[0],.18,a[1])],True)
 return dict(key=KEY,name='Palms Ivory, Fantasy and Place with lower resort',center=[-2040,0,180],bounds=[-2360,95,-1750,260],building='palms',structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
