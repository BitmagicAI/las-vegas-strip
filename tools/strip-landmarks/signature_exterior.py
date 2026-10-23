"""Signature's three towers and mapped lower structures, Earth 2022 references.
All bays/elevations other than mapped tower/low-building heights are estimates.
"""
from common import *
from building_surfaces import BuildingSurfaces
from luxor_facades import Access
from forum_shops import facade_frame
KEY='signatureExterior'
TOWERS=['way/95223224','way/95223232','way/95223231']
CANOPIES=['way/135029773','way/135029777','way/135029783']
LOW=['way/401340339','way/435343331','way/435490984','way/435490985','way/435490986','way/435490987']
def exterior(B):
 B.property=KEY+'-exterior';B.detail=0
 records=[dict(BYID[i],shape=footprint(i).simplify(.1,preserve_topology=True)) for i in TOWERS+LOW]
 surf=BuildingSurfaces(records);access=Access(next(p for p in json.load(open('build/highrises/plan.json')) if p['key']=='signature'))
 for r in records:
  p=r['shape'];tower=r['id'] in TOWERS;h=r['height'];B.source='tower/signature' if tower else 'podium/'+r['id']
  rect=list(p.minimum_rotated_rectangle.exterior.coords);major=max(zip(rect,rect[1:]),key=lambda e:math.dist(*e));dx,dz=major[1][0]-major[0][0],major[1][1]-major[0][1];l=math.hypot(dx,dz);dx/=l;dz/=l
  for poly in parts(p):
   ps=list(poly.exterior.coords)
   for a,b in zip(ps,ps[1:]):
    F,L,nx,nz=facade_frame(B,a,b,p,.08)
    if L<.15:continue
    line=LineString([a,b]);ux,uz=(b[0]-a[0])/L,(b[1]-a[1])/L
    region=unary_union([Polygon([(line.project(Point(v[0],v[2])),v[1]) for v in t]) for t in surf.wall(r['id'],a,b,0,h,access)])
    def patch(mat,x0,y0,x1,y1,offset=.16):
     if x1<=x0 or y1<=y0:return
     for q in parts(region.intersection(box(x0,y0,x1,y1))):
      for t in triangles(q):B.face(mat,[(a[0]+ux*x+nx*offset,y,a[1]+uz*x+nz*offset) for x,y in list(t.exterior.coords)[:-1]])
    patch('sg-stone',0,0,L,h)
    if tower:
     broad=abs(ux*dx+uz*dz)>.85
     if broad:
      bays=max(1,round(L/3.7));pitch=L/bays
      patch('sg-glass',.35,5,L-.35,140,.20)
      for j in range(bays):
       x=j*pitch
       patch('sg-white',x,4,min(x+.35,L),141,.26)
       # Recessed room glazing behind projecting balcony slabs and metal guards.
       for y in np.arange(6.2,139,3.55):
        F.box('sg-white',(x+pitch/2,y,-.66),(max(.1,pitch-.22),.20,1.30))
        F.box('sg-rail',(x+pitch/2,y+1.05,-1.25),(max(.1,pitch-.25),.065,.06))
        for t in np.arange(.2,pitch-.1,.42):B.face('sg-rail',[F.p(x+t-.0125,y+.08,-1.25),F.p(x+t+.0125,y+.08,-1.25),F.p(x+t+.0125,y+1.03,-1.25),F.p(x+t-.0125,y+1.03,-1.25)])
        patch('sg-frame',x+.35,y+2.7,min(x+pitch-.1,L),y+2.78,.28)
      for x in [0,L]:F.box('sg-white',(x,72,0),(.55,138,.75))
      patch('sg-white',0,140,L,145,.32)
      # Raised central crown with gentle arch across the principal long elevation.
      if L>30:
       for j in range(20):
        x0=L*j/20;x1=L*(j+1)/20;top0=145+2.7*math.sin(math.pi*j/20);top1=145+2.7*math.sin(math.pi*(j+1)/20)
        B.face('sg-white',[F.p(x0,145,0),F.p(x1,145,0),F.p(x1,top1,0),F.p(x0,top0,0)])
     else:
      patch('sg-white',0,3,L,145,.22)
      if L>9:
       patch('sg-gold',L*.36,5,L*.64,141,.26)
       patch('sg-glass',L*.44,5,L*.56,140,.30)
       for y in np.arange(6.2,139,3.55):patch('sg-stone',L*.36,y,L*.64,y+.24,.34)
     patch('sg-glass',.5,.4,L-.5,3.8,.25)
     for x in np.arange(0,L,2):patch('sg-frame',x,.3,min(x+.06,L),4,.3)
    else:
     bays=max(1,round(L/3));pitch=L/bays
     for j in range(bays):patch('sg-glass',j*pitch+.35,.5,min((j+1)*pitch-.35,L-.2),h-.5,.25)
     F.box('sg-white',(L/2,h+.18,0),(L,.36,.5))
     for t in surf.wall(r['id'],a,b,0,h,access):
      c=B.solids[B.property];n=len(c['vertices'])//3;c['vertices'].extend(v for pt in t for v in pt);c['indices'].extend([n,n+1,n+2])
   B.planar('sg-roof',surf.roof(r['id'],poly,h),h+.03,not tower)
  if tower:
   c=p.centroid;B.box('sg-white',(c.x,146.3,c.y),(11,2.5,9));B.box('sg-vent',(c.x,147.6,c.y),(9,.15,7))
 # Roof-only porte-cocheres keep the drop-offs physically open.
 towers=unary_union([r['shape'] for r in records if r['id'] in TOWERS])
 for ident in CANOPIES:
  B.source='arrival/'+ident;roof=footprint(ident).difference(towers);B.planar('sg-white',roof,3.7,True);B.planar('sg-roof',roof,3.98)
  for poly in parts(roof):
   ps=list(poly.exterior.coords)
   for a,b in zip(ps,ps[1:]):B.face('sg-white',[(a[0],3.7,a[1]),(b[0],3.7,b[1]),(b[0],3.98,b[1]),(a[0],3.98,a[1])],True)
   # Columns only at free outer corners, away from the hotel entrance face.
   for x,z in ps[:-1]:
    if towers.distance(Point(x,z))>4:B.box('sg-stone',(x,1.85,z),(.45,3.7,.45),True)
 # West-side pools. Plans locate them; exact outlines and planting remain estimates.
 from shapely.geometry import shape
 layers=json.load(open('build/geographic-strip/surface-layers.geojson'))['features'];roads=unary_union([shape(f['geometry']).buffer(.3) for f in layers if f['properties']['kind'] in ['road','sidewalk']]);occupied=unary_union([r['shape'] for r in records])
 B.source='pool-courts'
 for x,z in [(527,942),(529,1024),(511,1105)]:
  deck=box(x-14,z-20,x+14,z+20).difference(roads).difference(occupied.buffer(.5));pool=box(x-5,z-10,x+5,z+10).intersection(deck.buffer(-1))
  B.planar('sg-paving',deck.difference(pool),.32,True);B.planar('water',pool,.25);B.planar('sg-white',pool,.02,True);B.planar('sg-white',pool.buffer(.4).difference(pool),.35,True)
  # Pool edges have real submerged sides; the deck is not a paper plane.
  for area,lo,hi,mat in [(pool,.02,.32,'sg-white'),(deck,0,.32,'sg-paving')]:
   for part in parts(area):
    ps=list(part.exterior.coords)
    for a,b in zip(ps,ps[1:]):B.face(mat,[(a[0],lo,a[1]),(b[0],lo,b[1]),(b[0],hi,b[1]),(a[0],hi,a[1])],True)
  # Perimeter metal enclosure with a two-metre opening on the hotel side.
  for part in parts(deck):
   ps=list(part.exterior.coords)
   for a,b in zip(ps,ps[1:]):
    line=LineString([a,b]);L=line.length
    for d in np.arange(0,L,.15):
     pt=line.interpolate(d)
     if pt.x>x+12 and abs(pt.y-z)<1.2:continue
     B.face('sg-rail',[(pt.x-.014,.35,pt.y),(pt.x+.014,.35,pt.y),(pt.x+.014,1.55,pt.y),(pt.x-.014,1.55,pt.y)])
    for d in np.arange(0,L,2):
     q=line.interpolate(d);end=line.interpolate(min(d+2,L));mid=line.interpolate(min(d+1,L))
     if mid.x>x+12 and abs(mid.y-z)<2:continue
     B.tube('sg-rail',(q.x,1.55,q.y),(end.x,1.55,end.y),.025,6)
     B.box('sg-rail',(q.x,.95,q.y),(.065,1.2,.065))
  # Paired canvas cabanas at the quiet end, retaining the main circulation aisle.
  for xx in [x-8,x,x+8]:
   zz=z-16;pad=box(xx-2,zz-1.8,xx+2,zz+1.8)
   if not deck.contains(pad):continue
   for dx in [-1.8,1.8]:
    for dz in [-1.6,1.6]:B.box('sg-frame',(xx+dx,1.7,zz+dz),(.09,2.75,.09))
   top=(xx,3.55,zz)
   corners=[(xx-2,3.05,zz-1.8),(xx+2,3.05,zz-1.8),(xx+2,3.05,zz+1.8),(xx-2,3.05,zz+1.8)]
   for j in range(4):B.face('sg-white',[corners[j],corners[(j+1)%4],top])
   B.box('sg-white',(xx,.67,zz),(2.7,.25,1.8));B.box('sg-frame',(xx,.45,zz),(2.5,.3,1.6))
  for xx in [x-9,x+9]:
   for zz in np.arange(z-15,z+16,3):
    if deck.contains(box(xx-.6,zz-1.1,xx+.6,zz+1.1)):
     B.box('sg-white',(xx,.58,zz),(.7,.12,1.8));B.box('sg-frame',(xx,.38,zz-.55),(.55,.28,.1));B.box('sg-frame',(xx,.38,zz+.55),(.55,.28,.1))
 return dict(key=KEY,name='Signature three towers pools and arrival exterior',center=[572,0,1020],bounds=[485,912,665,1317],building='signature',structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
