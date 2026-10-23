"""Mandalay Bay/W: surveyed footprints, Earth-observed gold piers and mint roofs."""
from common import *
from luxor_facades import Access
from forum_shops import facade_frame
from building_surfaces import BuildingSurfaces
from mandalay_pool_detail import structure
KEY='mandalayExterior'
TOWERS=['way/27858550','way/118347176']
PODIUMS=['way/116660358','way/502624676','way/116660354','way/27858551']
def exterior(B):
 B.property=KEY+'-exterior';B.detail=0
 plans=json.load(open('build/highrises/plan.json'));plan={'towers':[t for p in plans if p['key'] in ['mandalay-bay','w-las-vegas'] for t in p['towers']]}
 access=Access(plan);ids=TOWERS+PODIUMS
 records=[dict(BYID[i],shape=structure(i)) for i in ids];surface=BuildingSurfaces(records)
 for r in records:
  ident=r['id'];p=r['shape'];h=r['height'];tower=ident in TOWERS;convention=ident=='way/116660354';arena=ident=='way/27858551'
  B.source='tower/'+('mandalay-bay' if ident==TOWERS[0] else 'w-las-vegas') if tower else 'podium/'+ident
  for poly in parts(p):
   for ring in [poly.exterior,*poly.interiors]:
    ps=list(ring.coords)
    for a,b in zip(ps,ps[1:]):
     line=LineString([a,b]);L=line.length
     if L<.2:continue
     ux,uz=(b[0]-a[0])/L,(b[1]-a[1])/L;nx,nz=-uz,ux;mid=line.interpolate(.5,normalized=True)
     if p.contains(Point(mid.x+nx*.05,mid.y+nz*.05)):nx,nz=-nx,-nz
     vis=surface.wall(ident,a,b,r['base'],h,access)
     # Replace generic city collision with the same clipped structural walls.
     if not tower:
      for tri in vis:
       c=B.solids[B.property];n=len(c['vertices'])//3;c['vertices'].extend(float(v) for pt in tri for v in pt);c['indices'].extend([n,n+1,n+2])
     region=unary_union([Polygon([(line.project(Point(v[0],v[2])),v[1]) for v in tri]) for tri in vis])
     def patch(mat,x0,y0,x1,y1,offset=.2):
      for q in parts(region.intersection(box(x0,y0,x1,y1))):
       for tri in triangles(q):B.face(mat,[(a[0]+ux*x+nx*offset,y,a[1]+uz*x+nz*offset) for x,y in list(tri.exterior.coords)[:-1]])
     patch('mandalay-glass' if tower else 'mandalay-stone',0,r['base'],L,h)
     if tower:
      # Broad pale vertical ribs, finer horizontal bronze spandrels.
      count=max(1,round(L/7.5));step=L/count
      for j in range(count+1):patch('mandalay-white',max(0,j*step-.36),8,min(L,j*step+.36),h-5,.37)
      for y in np.arange(10,h-5,3.6):patch('mandalay-bronze',0,y,L,y+.085,.28)
      for y,w in [(7,1.0),(h-7,.65),(h-4,.65),(h-1.0,1.0)]:patch('mandalay-white',0,y,L,y+w,.4)
      # Raised white cornices and lettering read above the glass envelope.
      F,_,_,_=facade_frame(B,a,b,p,.42)
      F.box('mandalay-white',(L/2,h+.3,0),(L+.12,.6,.9))
      if L>55:
       F.text('MANDALAY BAY' if ident==TOWERS[0] else 'W',(L/2,h-3.1,-.2),2.0,'mandalay-white')
      # Decorative crown apertures remain part of the envelope, not emissive.
      for x in np.arange(1,L-1,3.4):patch('mandalay-bronze',x,h-3.3,min(x+1.8,L),h-1.7,.44)
     else:
      street=nx>.25 and mid.x>-220 and not convention
      if street or arena:
       for x in np.arange(.7,L-1,5.2):
        patch('mandalay-window',x,1,min(x+3.8,L-.4),min(h-1.2,5.2),.30)
        patch('mandalay-white',x-.12,.4,x+.10,h-.3,.36)
      elif convention:
       for x in np.arange(1,L-1,9.5):patch('mandalay-white',x,.5,x+.35,h-.6,.32)
       for y in [1.0,h*.48,h-1.0]:patch('mandalay-band',0,y,L,y+.35,.33)
      else:
       for x in np.arange(.5,L,7):patch('mandalay-band',x,.5,min(x+.20,L),h-.3,.30)
      patch('mandalay-white',0,h-.5,L,h,.4)
      if convention:
       F,_,_,_=facade_frame(B,a,b,p,.5)
       # Earth 2022: glazing belongs to the recessed arrival/courtyard faces.
       # The southeast hall's Strip-facing wall is opaque precast.
       courtyard=nx>.2 and mid.x< -225 and 2870<mid.y<3090
       if courtyard and L>9:
        for x in np.arange(4.5,L-3,7.5):
         for lo,hi in [(1,6),(9,15.5),(18,24)]:
          patch('mandalay-window',x-2.45,lo,x+2.45,hi,.30)
          patch('mandalay-white',x-2.65,lo-.2,x+2.65,lo,.48)
          for yy in np.arange(lo+1.8,hi,1.8):patch('mandalay-bronze',x-2.45,yy,x+2.45,yy+.06,.39)
          patch('mandalay-bronze',x-.045,lo,x+.045,hi,.4)
         F.box('mandalay-white',(x-3.45,h/2,-.1),(.5,h,1.1))
       elif L>12:
        for x in np.arange(2,L-1,12):
         F.box('mandalay-white',(x,h/2,0),(.48,h,.85))
        # Service bays face the rear/service roads, not the public Strip.
        if nx<-.5 or nz>.7:
         for x in np.arange(9,L-7,21):
          patch('mandalay-band',x-3.2,.15,x+3.2,5.2,.42)
          for yy in np.arange(.4,5.1,.35):patch('mandalay-bronze',x-3.1,yy,x+3.1,yy+.045,.49)
          F.box('mandalay-white',(x,5.5,-1.4),(7.4,.32,3.2))
          for dx in [-3.6,3.6]:F.lathe('mandalay-bronze',x+dx,-1,[(0,.13),(1,.13)],8)
   roof=surface.roof(ident,poly,h)
   B.planar('mandalay-roof',roof,h+.10,not tower)
   # Roof arrays are observed on the convention hall; panel spacing is estimated.
   if convention:
    # Large panel fields with narrow joints and explicit service aisles.
    for x in np.arange(p.bounds[0]+7,p.bounds[2]-5,18):
     for z in np.arange(p.bounds[1]+7,p.bounds[3]-5,24):
      panel=box(x-8.5,z-11.5,x+8.5,z+11.5)
      if roof.buffer(-3).contains(panel):
       B.planar('mandalay-solar',panel,h+.20)
   elif not tower:
    for x in np.arange(p.bounds[0]+10,p.bounds[2]-10,29):
     for z in np.arange(p.bounds[1]+10,p.bounds[3]-10,31):
      if roof.contains(box(x-2,z-1.5,x+2,z+1.5)):B.box('ph-metal',(x,h+.65,z),(4,1.1,3))
 # Mapped east entrance roof: open canopy, no solid volume added below it.
 B.source='arrival';p=footprint('way/364846553');inner=p.buffer(-4.0)
 B.planar('mandalay-mint',inner,9.5,True)
 for poly in parts(p):
  ps=list(poly.exterior.coords)
  for a,b in zip(ps,ps[1:]):
   c=inner.boundary.interpolate(inner.boundary.project(Point(*a)));d=inner.boundary.interpolate(inner.boundary.project(Point(*b)))
   B.face('mandalay-mint',[(a[0],7.5,a[1]),(b[0],7.5,b[1]),(d.x,9.5,d.y),(c.x,9.5,c.y)],True)
   L=math.dist(a,b)
   if L>5:
    for t in np.linspace(0,1,max(2,math.ceil(L/8))):
     x=a[0]+(b[0]-a[0])*t;z=a[1]+(b[1]-a[1])*t
     B.box('mandalay-white',(x,4,z),(.65,7,.65),True)
 # Roofed southern Four Seasons perimeter: fascia depth and roof pitches estimated.
 B.source='four-seasons';p=structure('way/502624676');inner=p.buffer(-4)
 band=p.difference(inner);B.planar('mandalay-mint',band,6.2)
 from mandalay_pool_detail import exterior as pool_detail
 pool_detail(B)
 return dict(key=KEY,name='Mandalay Bay and W exterior',center=[-285,0,2730],bounds=[-610,2370,-40,3250],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
