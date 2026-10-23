"""Promenade upper glazing and low-rise roof detail, Earth/KJW references 2026-10-14.
Equipment sizes and elevations are estimated; original footprint and circulation retained.
"""
from common import *
def exterior(B):
 B.property='linq-exterior';B.detail=0
 route=LineString([(36,-160),(109,-161),(140,-171),(235,-174),(319,-177),(400,-183)])
 tower=footprint('way/115773426')
 for ident,h in [('way/115771295',17),('way/402543936',8.8),('way/402543935',8.8)]:
  p=footprint(ident);B.source='linq-lowrise-service'
  safe=p.buffer(-3).difference(tower.buffer(2))
  # Actual parapet edges and low mechanical screens; no invented public rooftop floor.
  for poly in parts(p.buffer(-.3)):
   pts=list(poly.exterior.coords)
   for a,b in zip(pts,pts[1:]):
    if tower.buffer(.7).intersects(LineString([a,b])):continue
    if ident=='way/115771295' and min(a[0],b[0])<85:continue
    B.tube('linq-membrane-paint',(a[0],h+.25,a[1]),(b[0],h+.25,b[1]),.22,4)
  # Group service plant at sampled roof locations; retain a generous edge setback.
  for x,z,w,d in [(95,-241,7,5),(161,-253,8,4),(196,-249,5,4),(265,-255,7,4),(65,-190,6,5),(102,-193,5,4),(160,-197,6,4),(208,-196,5,4),(258,-200,6,4),(315,-199,7,4),(357,-201,5,4),(167,-160,5,4),(247,-143,10,7),(275,-127,8,5),(292,-147,5,4),(348,-168,5,3)]:
   if not safe.contains(box(x-w/2-.5,z-d/2-.5,x+w/2+.5,z+d/2+.5)):continue
   B.box('linq-service-paint',(x,h+.15,z),(w+.4,.3,d+.4))
   B.box('linq-membrane-paint',(x,h+.85,z),(w,1.4,d))
   for dx in [-w*.27,w*.27]:B.lathe('charcoal',(x+dx,z),[(h+1.56,.65),(h+1.64,.65),(h+1.64,.02)],16)
   for yy in np.arange(h+.4,h+1.4,.2):B.box('steel',(x,yy,z-d/2-.025),(w-.4,.055,.05))
  if ident=='way/115771295':continue
  B.source='linq-promenade-upper'
  pts=list(p.exterior.coords)
  for a,b in zip(pts,pts[1:]):
   line=LineString([a,b]);L=line.length;mid=line.interpolate(.5,normalized=True)
   if L<6 or route.distance(mid)>13:continue
   ux,uz=(b[0]-a[0])/L,(b[1]-a[1])/L;nx,nz=-uz,ux
   if p.contains(Point(mid.x+nx*.1,mid.y+nz*.1)):nx,nz=-nx,-nz
   F=Frame(B,mid.x+nx*.19,mid.y+nz*.19,math.atan2(-nx,-nz),y=0)
   # Architect photo: repeated inset upper glass, horizontal metal bands and projecting fins.
   F.box('linq-service-paint',(0,5.85,-.09),(L,.2,.22))
   F.box('linq-service-paint',(0,8.4,-.09),(L,.22,.22))
   count=max(1,int(L/3.2));bay=L/count
   for i in range(count):
    x=-L/2+(i+.5)*bay
    F.box('linq-glass',(x,7.1,0),(bay-.28,2.2,.08))
    for xx in [x-bay/2+.1,x+bay/2-.1]:F.box('silver',(xx,7.1,-.07),(.10,2.35,.15))
    F.box('silver',(x,7.1,-.08),(.055,2.2,.16))
    if i%4==0:F.box('linq-service-paint',(x-bay/2,7.2,-.22),(.22,3.3,.44))
   # Lower storefront mullions/door frames, flush with existing opaque glazing.
   count=max(1,int(L/13))
   for i in range(count):
    x=(i-(count-1)/2)*12
    for dx in [-3.3,-1.65,0,1.65,3.3]:F.box('steel',(x+dx,2.8,-.08),(.065,4.8,.14))
    F.box('steel',(x,3.2,-.09),(10,.07,.16))
