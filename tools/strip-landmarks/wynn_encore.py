"""Wynn/Encore connected site, mapped outlines with Earth-guided facade sections."""
from common import *
from building_surfaces import BuildingSurfaces
from luxor_facades import Access
from forum_shops import facade_frame
KEY='wynnEncoreExterior'
class BothAccess:
 def __init__(self):self.items=[Access(p) for p in json.load(open('build/highrises/plan.json')) if p['key'] in ['wynn','encore']]
 def wall(self,a,b,lo,hi):
  line=LineString([a,b]);reg=box(0,lo,line.length,hi)
  for item in self.items:
   ts=item.wall(a,b,lo,hi);q=unary_union([Polygon([(line.project(Point(v[0],v[2])),v[1]) for v in t]) for t in ts]);reg=reg.intersection(q)
  return [[[line.interpolate(x).x,y,line.interpolate(x).y] for x,y in list(t.exterior.coords)[:-1]] for p in parts(reg) for t in triangles(p)]
def exterior(B):
 B.property=KEY+'-exterior';B.detail=0
 heights={'way/27910891':192,'way/205501268':187,'way/111322055':14,'way/111322079':23,'way/111322083':20,'way/111413431':14,'way/111413433':20,'way/128266659':22,'way/135291730':14,'way/142899198':18,'way/142899199':10,'way/156626862':12,'way/886592894':8,'way/886592897':9.35}
 pools=unary_union([box(774,-1415,786,-1380).buffer(3),Point(811,-1348).buffer(18,resolution=24).difference(Point(811,-1348).buffer(7,resolution=20)),Point(781,-1160).buffer(10,resolution=24),Point(792,-1096).buffer(11,resolution=24),LineString([(781,-1160),(792,-1096)]).buffer(2.2)])
 club=footprint('way/156626862')
 # The coarse Encore podium outline includes this separate open-air pool court.
 # Subtract its envelope before surface ownership/clipping and collision generation.
 club_envelope=club.convex_hull.buffer(.12,join_style=2)
 rs=[dict(BYID[i],shape=footprint(i).difference(club_envelope.union(club.buffer(2.5))) if i=='way/135291730' else footprint(i),height=h) for i,h in heights.items()]
 surf=BuildingSurfaces(rs);access=BothAccess()
 for r in rs:
  p=r['shape'];h=r['height'];tower=h>100;garage=r['id'] in ['way/128266659','way/111322083'];B.source=('tower/encore' if r['id']=='way/27910891' else 'tower/wynn') if tower else 'podium/'+r['id']
  for poly in parts(p):
   if r['id']=='way/886592897':
    # North Encore porte-cochere: building=roof, not an enclosed pavilion.
    B.shell(poly,7.6,8.5,'wy-white',roof=False)
    B.planar('wy-white',poly,7.6,True)
    B.planar('wy-roof',poly,8.5,True)
    for inset,lo,hi in [(1.2,8.5,9.1),(2.8,9.1,9.35)]:
     q=poly.buffer(-inset,join_style=2)
     B.shell(q,lo,hi,'wy-trim',roof=False)
     B.planar('wy-white',q,hi,True)
    for x,z in [(773,-1512),(797,-1501),(786,-1478),(762,-1490)]:
     B.box('wy-stone',(x,3.8,z),(1.3,7.6,1.3),True)
     B.box('wy-white',(x,7.35,z),(2.1,.5,2.1))
    c=poly.centroid
    B.planar('wy-theater-center-paint',Point(c.x,c.y).buffer(7.2,resolution=24),9.37)
    continue
   if r['id']=='way/886592894':
    # West motor-court porte-cochere: shallow roof over an open driveway.
    B.shell(poly,7.2,8,'wy-rim',roof=False)
    B.planar('wy-theater-roof-paint',poly,8,True)
    B.planar('wy-trim',poly,7.2,True)
    for x,z in [(552,-1238),(550,-1222),(574,-1228)]:
     B.box('wy-stone',(x,3.6,z),(1.15,7.2,1.15),True)
     B.box('wy-trim',(x,.25,z),(1.6,.5,1.6),True)
     B.box('wy-trim',(x,6.95,z),(1.8,.5,1.8))
    c=poly.centroid
    B.lathe('wy-trim',(c.x,c.y),[(8,.1),(8,7.2),(8.2,7.2),(8.2,6.8)],8)
    B.planar('wy-theater-center-paint',Point(c.x,c.y).buffer(6.8,resolution=2),8.21)
    continue
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
     lakefront = r['id']=='way/111322055' and nx < -.45 and -1190 < (a[1]+b[1])/2 < -1122 and L>4
     if lakefront:
      # Dedicated two-level lake dining elevation replaces generic windows, not an overlay.
      patch('wlf-ochre-stucco',0,0,L,h)
      for yy in [.7,5.8,6.15,10.8,13.7]:patch('wlf-cream-stucco',0,yy,L,min(h,yy+.24),.40)
      for xx in np.arange(.5,L-1,3.6):
       for yy in [1.0,6.6]:
        patch('wlf-window-glass',xx,yy,min(L-.3,xx+2.7),yy+3.7,.27)
        for u in [xx,xx+1.35,xx+2.7]:patch('wlf-cream-stucco',u-.05,yy-.1,min(L,u+.05),yy+3.8,.38)
       patch('wlf-cream-stucco',xx-.22,.7,xx,10.6,.44)
      # Sloping striped upper-level awning, authored as disjoint fabric strips.
      for xx in np.arange(0,L,.28):
       F.b.face('wlf-awning-dark-paint' if int(xx/.28)%2 else 'wlf-fabric-paint',[F.p(xx,10.5,-.3),F.p(min(L,xx+.28),10.5,-.3),F.p(min(L,xx+.28),9.8,-2.0),F.p(xx,9.8,-2.0)])
      for tri in surf.wall(r['id'],a,b,0,h,access):
       c=B.solids[B.property];n=len(c['vertices'])//3;c['vertices'].extend(float(v)for pt in tri for v in pt);c['indices'].extend([n,n+1,n+2])
      continue
     patch('wy-bronze' if tower else 'wy-stone',0,0,L,h)
     if tower:
      for y in np.arange(8,h-4,6.3):patch('wy-band',0,y,L,y+.28,.35)
      for y in np.arange(4.8,h-4,3.15):patch('wy-joint',0,y,L,y+.045,.27)
      for x in np.arange(.9,L,1.65):patch('wy-joint',x,3,min(x+.035,L),h-3,.27)
      patch('wy-rim',0,h-2.5,L,h,.32)
      if L<4:patch('wy-rim',0,0,L,h,.35)
     elif garage:
      for y in np.arange(3,h-1,3.1):patch('wy-shadow',.3,y-1.7,max(.3,L-.3),y-.25,.26)
      for x in np.arange(0,L,8):patch('wy-white',x,0,min(x+.7,L),h,.38)
     elif r['id']=='way/156626862':
      # Two tiers of cabana bays replace the former single generic window row.
      for y in [.45,5.8,6.15,10.9,11.6]:patch('wy-trim',0,y,L,min(h,y+.28),.4)
      if nx<.25:
       for y in [1.05,6.55]:
        patch('wy-window',.25,y,max(.25,L-.25),y+3.65,.30)
        for x in np.arange(.15,L,4.8):
         patch('wy-white',x,y-.25,min(x+.45,L),y+4.0,.55)
         patch('wy-red-fabric',min(x+.55,L),y+.18,min(x+1.0,L),y+3.5,.59)
         patch('wy-red-fabric',min(x+3.8,L),y+.18,min(x+4.25,L),y+3.5,.59)
       # Balustrade strip between the levels; single material batch.
       for x in np.arange(.7,L,.55):patch('wy-white',x,4.65,min(x+.13,L),5.55,.57)
       patch('wy-trim',0,5.48,L,5.65,.60)
      else:
       for x in np.arange(.3,L,6):
        patch('wy-shadow',x,1,min(x+4.2,L-.1),5.2,.30)
        patch('wy-trim',x-.15,.8,min(x+.15,L),10.8,.5)
     else:
      for y in [1,6.3,h-1.1]:patch('wy-trim',0,y,L,min(h,y+.3),.37)
      for x in np.arange(.7,L-2,5.2):
       patch('wy-window',x,1.4,min(x+3.5,L-.3),min(h-1.5,5.7),.3)
       patch('wy-trim',x-.18,1.2,x,6.1,.4)
       patch('wy-trim',min(x+3.5,L-.3),1.2,min(x+3.68,L-.15),6.1,.4)
       patch('wy-trim',x-.18,5.7,min(x+3.68,L-.15),6.05,.4)
      for x in np.arange(0,L,15):patch('wy-white',x,0,min(x+.9,L),h,.45)
     F.box('wy-trim' if not tower else 'wy-rim',(L/2,h+.18,0),(L,.36,.6))
     if not tower:
      for tri in surf.wall(r['id'],a,b,0,h,access):
       c=B.solids[B.property];n=len(c['vertices'])//3;c['vertices'].extend(float(v) for pt in tri for v in pt);c['indices'].extend([n,n+1,n+2])
   roof=surf.roof(r['id'],poly,h)
   if h==14:roof=roof.difference(pools)
   B.planar('wy-theater-roof-paint' if r['id'] in ['way/111322079','way/142899198'] else 'wy-roof',roof,h+.04,not tower)
   if r['id']=='way/142899198':
    c=poly.centroid
    B.lathe('wy-trim',(c.x,c.y),[(h+.08,2.3),(h+.5,2.1)],24)
    B.planar('wy-skylight',Point(c.x,c.y).buffer(2.05,resolution=12),h+.51)
   if r['id']=='way/111322079':
    # Primary aerial shows a pale central roof over a darker perimeter service ring.
    inset=poly.buffer(-15.5,join_style=2)
    B.shell(inset,h+.04,h+2.4,'wy-theater-wall-paint',roof=False,solid=True)
    B.planar('wy-theater-center-paint',inset,h+2.4,True)
    for q in parts(inset):
     for a,b in zip(list(q.exterior.coords),list(q.exterior.coords)[1:]):
      B.tube('wy-trim',(a[0],h+2.45,a[1]),(b[0],h+2.45,b[1]),.10,6)
    B.detail=1
    for q in parts(poly.buffer(-4)):
     line=q.exterior
     for dist in np.arange(6,line.length,18):
      pt=line.interpolate(dist)
      if inset.buffer(2).contains(pt):continue
      B.box('wy-equipment-paint',(pt.x,h+.7,pt.y),(2.8,1.3,1.7))
      B.box('wy-shadow',(pt.x,h+1.37,pt.y),(2.3,.045,1.3))
    B.detail=0
   if r['id']=='way/111322055':
    for a,b in zip(list(poly.exterior.coords),list(poly.exterior.coords)[1:]):
     line=LineString([a,b]);mid=line.interpolate(.5,normalized=True)
     if mid.x>560 or mid.y<-1180 or line.length<10:continue
     F,L,nx,nz=facade_frame(B,a,b,poly,.1)
     if not roof.contains(Point(mid.x-nx*5,mid.y-nz*5)):continue
     for t in range(12):
      aa,bb=math.pi*t/12,math.pi*(t+1)/12
      B.face('wy-skylight',[F.p(1,h+3*math.sin(aa),5+3*math.cos(aa)),F.p(L-1,h+3*math.sin(aa),5+3*math.cos(aa)),F.p(L-1,h+3*math.sin(bb),5+3*math.cos(bb)),F.p(1,h+3*math.sin(bb),5+3*math.cos(bb))])
   if tower:
    inner=poly.buffer(-2.2);B.planar('wy-roof',inner,h+.5)
 # The open courtyard must have a physical floor, not the old 14 m podium roof.
 B.source='podium/way/156626862'
 court=club_envelope.difference(club).buffer(-.2)
 water=LineString([(640,-1527),(629,-1505),(615,-1482),(602,-1460)]).buffer(5.5,resolution=24).union(Point(640,-1527).buffer(7.5,resolution=24)).union(Point(602,-1460).buffer(7.5,resolution=24)).intersection(court.buffer(-3.5))
 B.planar('wy-stone',court.difference(water),.28,True)
 B.planar('hgv_pool',water,.12)
 B.planar('hgv-pool-tile',water,-1.25,True)
 B.planar('wy-white',water.buffer(.3).difference(water),.30,True)
 B.shell(water,-1.25,.28,'hgv-pool-tile',roof=False)
 # Long eastern glazed roof, following the court's straight rear edge.
 hull=list(club.convex_hull.exterior.coords)
 rear=[]
 for a,b in zip(hull,hull[1:]):
  F,L,nx,nz=facade_frame(B,a,b,club.convex_hull,.3)
  if nx>.6 and L>50:rear.append((L,a,b,nx,nz))
 if rear:
  L,a,b,nx,nz=max(rear)
  def rp(t,d,y):return (a[0]+(b[0]-a[0])*t+nx*d,y,a[1]+(b[1]-a[1])*t+nz*d)
  B.face('wy-skylight',[rp(0,.6,14.4),rp(1,.6,14.4),rp(1,24,19.2),rp(0,24,19.2)])
  for t in np.linspace(0,1,math.ceil(L/2.1)+1):B.tube('wy-white',rp(t,.6,14.45),rp(t,24,19.25),.065,6)
  for d in [.6,8.4,16.2,24]:
   y=14.4+(d-.6)/23.4*4.8
   B.tube('wy-white',rp(0,d,y+.05),rp(1,d,y+.05),.1,6)
  for t in [0,1]:B.face('wy-stone',[rp(t,.6,14),rp(t,.6,14.4),rp(t,24,19.2),rp(t,24,14)])
 # Framed Beach Club identity on the middle of the west-facing wall.
 B.source='podium/way/156626862'
 club=footprint('way/156626862')
 F=Frame(B,594.2,-1502,math.atan2(.915,.404),y=0);L=0
 w=16
 F.box('wy-white',(L/2,7.2,1.5),(w,6.8,3.3))
 F.box('wy-trim',(L/2,7.2,-.33),(w-.35,6.4,.08))
 F.box('wy-white',(L/2,7.2,-.4),(w-.7,5.9,.07))
 F.text('ENCORE',(L/2,8.1,-.46),1.1,'wy-shadow')
 F.text('BEACH CLUB',(L/2,6.5,-.46),1.4,'wy-shadow')
 B.source='pool-courts'
 for q in parts(pools):
  B.planar('hgv_pool',q,13.82);B.planar('hgv-pool-tile',q,12.8,True);B.planar('wy-trim',q.buffer(.45).difference(q),14.08,True)
  for ring in [q.exterior,*q.interiors]:
   for a,b in zip(list(ring.coords),list(ring.coords)[1:]):B.face('hgv-pool-tile',[(a[0],12.8,a[1]),(b[0],12.8,b[1]),(b[0],14.08,b[1]),(a[0],14.08,a[1])],True)
 return dict(key=KEY,name='Wynn and Encore exterior site',center=[680,0,-1320],bounds=[415,-1572,960,-785],building='wynn-encore',structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
