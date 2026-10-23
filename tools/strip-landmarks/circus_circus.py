"""Circus Circus exteriors, mapped plans and Google Earth November2022–March2024.
No public interior regeneration. Roof profiles and bay spacings are estimates.
"""
from common import *
from building_surfaces import BuildingSurfaces
from luxor_facades import Access
from forum_shops import facade_frame
from circus_frontage import frontage,glass
KEY='circusExterior'
def exterior(B):
 B.property=KEY+'-exterior';B.detail=0
 ids=['way/135332955','way/135332956','way/135332957','way/135332958','way/135332959','way/135332960','way/135332961','way/135448025','way/135448016','way/180250447','way/180250495','way/364843230']
 records=[dict(BYID[i],shape=footprint(i)) for i in ids];surface=BuildingSurfaces(records);plan=next(p for p in json.load(open('build/highrises/plan.json')) if p['key']=='circus-circus');access=Access(plan)
 for r in records:
  ident=r['id'];p=r['shape'];h=r['height'];tower=h>=40;garage=ident in ['way/135332958','way/135332960'];motel=ident=='way/364843230';slots=ident=='way/180250495';food=ident=='way/180250447'
  B.source='tower/circus-circus' if tower else 'podium/'+ident
  if motel or slots or food:
   frontage(B,ident,p,h)
   continue
  for poly in parts(p):
   ps=list(poly.exterior.coords)
   for a,b in zip(ps,ps[1:]):
    line=LineString([a,b]);L=line.length
    if L<.1:continue
    F,L,nx,nz=facade_frame(B,a,b,p,.23);ux,uz=(b[0]-a[0])/L,(b[1]-a[1])/L
    region=unary_union([Polygon([(line.project(Point(v[0],v[2])),v[1]) for v in tri]) for tri in surface.wall(ident,a,b,r['base'],h,access)])
    def patch(mat,x0,y0,x1,y1,offset=.23):
     for q in parts(region.intersection(box(x0,y0,x1,y1))):
      for tri in triangles(q):B.face(mat,[(a[0]+ux*x+nx*offset,y,a[1]+uz*x+nz*offset) for x,y in list(tri.exterior.coords)[:-1]])
    patch('cc-white',0,0,L,h)
    if tower:
     end=L<22
     if end:patch('cc-pink',1,0,L-1,h-.7,.27)
     else:
      count=max(1,round(L/3.25));step=L/count
      for x in np.arange(step*.5,L,step):
       for y in np.arange(4.5,h-2,2.8):
        patch('cc-window',x-.65,y,x+.65,y+1.55,.27)
        patch('cc-sill',x-.73,y-.14,x+.73,y,.32)
      for x in np.arange(0,L,step):patch('cc-sill',x,3,x+.22,h-2,.35)
     patch('cc-white',0,h-1.0,L,h,.4)
     if end and h>60 and L>12:
      for j,ch in enumerate('CIRCUS'):F.text(ch,(L/2,h-10-j*4,-.15),2.4,'cc-white')
    elif garage:
     for y in np.arange(2,h-1,3.2):patch('cc-shadow',0,y,L,y+1.4,.28)
     for x in np.arange(0,L,10):patch('cc-white',x,0,min(L,x+.6),h,.35)
    elif ident=='way/135332959' and (a[0]+b[0])/2>850 and (a[1]+b[1])/2>-2350:
     patch('cc-white',0,0,L,h)
     count=max(1,round(L/4.2));step=L/count
     for j in range(count):
      x=(j+.5)*step
      if line.distance(Point(915.6965,-2295.191))<.2 and abs(x-L/2)<5:continue
      if step>1.2:F.arch(x,-.36,min(3.1,step-.3),min(6.2,h-.3),'cc-gold',.085,.25)
      F.box('cc-sill',(x,.45,-.28),(step-.1,.35,.18))
     for yy in [h-.2,h-.65]:F.box('cc-sill',(L/2,yy,-.32),(L,.18,.3))
    else:
     for x in np.arange(1,L-2,4.6):
      patch('cc-window',x,.65,min(x+3.4,L-.5),min(4.8,h-.5),.28)
      patch('cc-sill',x-.1,.55,min(x+3.5,L-.4),.72,.34)
     patch('cc-blue' if motel else 'cc-yellow' if food else 'cc-pink',0,h-.5,L,h,.33)
     if motel:patch('cc-blue',0,2.7,L,3.0,.34)
     elif not garage and nx>.2 and L>15:
      for x in np.arange(4,L-3,11):F.box('cc-pink',(x,4.9,-.8),(6,.18,1.7))
     if slots and nx>.4 and L>20:F.text('SLOTS A FUN',(L/2,h+.4,-.15),1.25,'cc-pink')
     if food and nx>.4 and L>15:F.text("McDonald's",(L/2,h+.4,-.15),1,'cc-yellow')
   if ident!='way/135448016':B.planar('cc-flat-roof',surface.roof(ident,poly,h),h+.055)
 # Adventuredome: clipped triangulated shell over the real nonrectangular plan.
 B.source='podium/way/135448016';p=footprint('way/135448016');xmin,zmin,xmax,zmax=p.bounds;cx,cz=(xmin+xmax)/2,(zmin+zmax)/2;rx,rz=(xmax-xmin)/2,(zmax-zmin)/2
 def dome(x,z):return (x,6.2+34*math.sqrt(max(0,1-((x-cx)/rx)**2-((z-cz)/rz)**2)),z)
 edges=set()
 for x in np.arange(xmin,xmax,8):
  for z in np.arange(zmin,zmax,8):
   for q in parts(p.intersection(box(x,z,x+8,z+8))):
    for tri in triangles(q):
     coords=list(tri.exterior.coords)[:-1];pts=[dome(*q) for q in coords];B.upface('cc-dome-glass',pts)
     for a,b in zip(coords,coords[1:]+coords[:1]):edges.add(tuple(sorted((tuple(a),tuple(b)))))
 B.detail=1
 for a,b in edges:B.tube('cc-dome-frame',dome(*a),dome(*b),.065,5)
 B.detail=0
 # Casino tent roof: broad oval with a small flattened ridge, alternating pink/white gores.
 B.source='podium/way/135448025';p=footprint('way/135448025');c=p.centroid
 rings=[p,p.buffer(-12),p.buffer(-24)]
 def at(r,t,y):
  ray=LineString([(c.x,c.y),(c.x+200*math.cos(t),c.y+200*math.sin(t))]);q=ray.intersection(r.boundary)
  if q.geom_type!='Point':q=Point(c.x,c.y)
  return (q.x,y,q.y)
 for i in range(96):
  t0=i*math.tau/96;t1=(i+1)*math.tau/96;mat='cc-pink' if (i//4)%2==0 else 'cc-white'
  for j,(y0,y1) in enumerate([(7,13),(13,20)]):B.upface(mat,[at(rings[j],t0,y0),at(rings[j],t1,y0),at(rings[j+1],t1,y1),at(rings[j+1],t0,y1)])
 B.planar('cc-flat-roof',rings[-1],20)
 # Front porte-cochere follows the mapped southeast entrance edge.
 B.source='podium/way/135332959';F,L,nx,nz=facade_frame(B,(909.033,-2281.76),(922.36,-2308.622),footprint('way/135332959'),0)
 # Framed closed entrance under the porte-cochere; interior routes are retained.
 for u in [L/2-2.7,L/2-1.35,L/2,L/2+1.35,L/2+2.7]:
  glass(F,u,1.8,1.25,3.2)
  F.tube('cc-metal',(u+.4,1,-.44),(u+.4,2,-.44),.026,6)
 F.box('cc-shadow',(L/2,4.25,-.35),(9,.9,.12));F.text('CIRCUS CIRCUS',(L/2,4.25,-.45),.68,'cc-white')
 F.box('cc-white',(L/2,5.8,-8),(L,.38,16));F.box('cc-pink',(L/2,5.63,-16),(L,.28,.35))
 for x in (1,L-1):
  for z in (-2,-14):F.box('cc-white',(x,2.8,z),(.6,5.6,.6))
 return dict(key=KEY,name='Circus Circus exterior and roadside buildings',center=[720,0,-2380],bounds=[430,-2595,1005,-2160],building='circus-circus',structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
