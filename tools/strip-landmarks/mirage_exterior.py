"""Mirage-era hotel exterior, guided by Google Earth November 2022 imagery."""
from common import *
from building_surfaces import BuildingSurfaces
from luxor_facades import Access
from forum_shops import facade_frame
KEY='mirageExterior'
def exterior(B):
 B.property=KEY+'-exterior';B.detail=0
 heights={'way/27727143':102,'way/33957359':14,'way/33957718':19,'way/136524187':14}
 rs=[dict(BYID[i],shape=footprint(i),height=h) for i,h in heights.items()];surf=BuildingSurfaces(rs);access=Access(next(p for p in json.load(open('build/highrises/plan.json')) if p['key']=='mirage'))
 dome=Point(-95.5,-587.7).buffer(22.5,resolution=48)
 for r in rs:
  p=r['shape'];h=r['height'];tower=h>50;garage=r['id']=='way/33957718';B.source='tower/mirage' if tower else 'podium/'+r['id']
  for poly in parts(p):
   for ring in [poly.exterior,*poly.interiors]:
    ps=list(ring.coords)
    for a,b in zip(ps,ps[1:]):
     line=LineString([a,b]);L=line.length
     if L<.1:continue
     F,L,nx,nz=facade_frame(B,a,b,p,.1);ux,uz=(b[0]-a[0])/L,(b[1]-a[1])/L
     region=unary_union([Polygon([(line.project(Point(v[0],v[2])),v[1]) for v in t]) for t in surf.wall(r['id'],a,b,0,h,access)])
     def patch(mat,x0,y0,x1,y1,offset=.2):
      for q in parts(region.intersection(box(x0,y0,x1,y1))):
       for t in triangles(q):B.face(mat,[(a[0]+ux*x+nx*offset,y,a[1]+uz*x+nz*offset) for x,y in list(t.exterior.coords)[:-1]])
     patch('mi-glass' if tower else 'mi-cream',0,0,L,h)
     if tower:
      if L<9:patch('mi-white',0,0,L,h,.3)
      else:
       for y in np.arange(15,h-8,3.1):patch('mi-white',0,y,L,y+.63,.32)
       for x in np.arange(1,L,1.55):patch('mi-frame',x,14,min(x+.04,L),h-8,.28)
       for x in [0,max(0,L-1.2)]:patch('mi-white',x,0,min(x+1.2,L),h,.38)
       patch('mi-banner',0,h-9,L,h-3,.3)
       if L>60:F.text('THE MIRAGE',(L/2,h-2.8,-.42),1.8,'mi-letter')
      patch('mi-white',0,h-3,L,h,.35)
     elif garage:
      for y in np.arange(3,h,3.1):patch('mi-shadow',.4,y-1.8,max(.4,L-.4),y-.3,.27)
      for x in np.arange(0,L,8):patch('mi-white',x,0,min(x+.7,L),h,.37)
     else:
      for y in [1,5.8,h-.8]:patch('mi-white',0,y,L,y+.35,.34)
      if nx>.15 or nz>.5:
       for x in np.arange(.7,L-1,5):
        patch('mi-window',x,1,min(x+3.5,L-.3),5.5,.28)
        patch('mi-awning',x,5,min(x+3.5,L-.3),6.2,.4)
       for x in np.arange(0,L,10):patch('mi-white',x,0,min(x+.75,L),h,.38)
     F.box('mi-white',(L/2,h+.16,0),(L,.32,.55))
     if not tower:
      for tri in surf.wall(r['id'],a,b,0,h,access):
       c=B.solids[B.property];n=len(c['vertices'])//3;c['vertices'].extend(float(v) for pt in tri for v in pt);c['indices'].extend([n,n+1,n+2])
   roof=surf.roof(r['id'],poly,h)
   if not tower:roof=roof.difference(dome)
   B.planar('mi-roof',roof,h+.04,not tower)
 B.source='podium/way/136524187'
 # Raised glass conservatory dome: curved panels and eight broad radial ribs.
 for i in range(64):
  aa,bb=math.tau*i/64,math.tau*(i+1)/64
  for j in range(16):
   ta,tb=math.pi/2*j/16,math.pi/2*(j+1)/16
   def pt(a,t):return(-95.5+22.5*math.cos(t)*math.cos(a),14.1+16*math.sin(t),-587.7+22.5*math.cos(t)*math.sin(a))
   B.face('mi-dome',[pt(aa,ta),pt(bb,ta),pt(bb,tb),pt(aa,tb)])
 for i in range(8):
  a=math.tau*i/8;pts=[(-95.5+22.65*math.cos(t)*math.cos(a),14.22+16.15*math.sin(t),-587.7+22.65*math.cos(t)*math.sin(a)) for t in np.linspace(0,math.pi/2,25)];B.path('mi-white',pts,.28,8)
 B.source='arrival'
 B.box('mi-white',(-43,6.3,-587.7),(17,.7,28),True)
 for z in [-599.7,-575.7]:B.box('mi-white',(-36,3,z),(.7,6,.7),True)
 from mirage_lagoon import lagoon
 lagoon(B)
 return dict(key=KEY,name='Mirage-era tower casino and arrival exterior',center=[-180,0,-600],bounds=[-535,-865,-20,-425],building='mirage',structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
