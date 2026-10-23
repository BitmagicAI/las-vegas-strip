"""Westin Las Vegas: mapped component plans, Google Earth front/rear reference."""
from common import *
from building_surfaces import BuildingSurfaces
from forum_shops import facade_frame
KEY='westin';IDS=['way/135020970','way/543423252','way/135020971']
class Closed:
 def wall(self,a,b,lo,hi):return [[(a[0],lo,a[1]),(b[0],lo,b[1]),(b[0],hi,b[1])],[(a[0],lo,a[1]),(b[0],hi,b[1]),(a[0],hi,a[1])]]
def exterior(B):
 B.property=KEY+'-exterior';B.source='westin';B.detail=0
 tower=footprint(IDS[1]);podium=footprint(IDS[0]);garage=footprint(IDS[2]);rs=[dict(id='tower',shape=tower,base=0,height=50),dict(id='podium',shape=podium,base=0,height=7.5)]
 surf=BuildingSurfaces(rs)
 for r in rs:
  p,h=r['shape'],r['height'];kind=r['id']
  for pp in parts(p):
   ps=list(pp.exterior.coords)
   for a,b in zip(ps,ps[1:]):
    L=math.dist(a,b)
    if L<.05:continue
    F,_,nx,nz=facade_frame(B,a,b,pp,0);line=LineString([a,b]);ux,uz=(b[0]-a[0])/L,(b[1]-a[1])/L
    ts=surf.wall(kind,a,b,0,h,Closed());region=unary_union([Polygon([(line.project(Point(v[0],v[2])),v[1]) for v in t]) for t in ts])
    def patch(mat,x0,y0,x1,y1,off=.06):
     if x1<=x0 or y1<=y0:return
     for q in parts(region.intersection(box(x0,y0,x1,y1))):
      for t in triangles(q):B.face(mat,[(a[0]+ux*x+nx*off,y,a[1]+uz*x+nz*off) for x,y in list(t.exterior.coords)[:-1]])
    for t in ts:B.face('we-shadow',t,True)
    patch('we-white',0,0,L,h)
    if kind=='tower':
     if L>25:
      patch('we-gray',0,37.1,L,49.5,.1)
      n=max(1,round(L/2.4));w=L/n
      for k in range(n):
       x=(k+.5)*w;wx=a[0]+ux*x
       if abs(wx-655)<5.5:continue
       for y in np.arange(8.2,37,2.85):
        patch('we-glass',x-.57,y,x+.57,y+1.65,.13)
        patch('we-sill',x-.63,y-.09,x+.63,y,.16)
       patch('we-glass',x-w*.39,38.0,x+w*.39,48.7,.14)
       for y in np.arange(39,49,1.1):patch('we-mullion',x-w*.39,y,x+w*.39,y+.045,.2)
       patch('we-mullion',x-.025,38,x+.025,48.7,.2)
      for y in [37.1,41.0,48.9]:patch('we-white',0,y,L,y+.28,.25)
      # Central dark core and stepped crown on both major elevations.
      core=line.project(Point(655,(a[1]+b[1])/2))
      if min(a[0],b[0])<655<max(a[0],b[0]):patch('we-gray',core-5.3,7.5,core+5.3,50,.28)
      if nz>.7 and min(a[0],b[0])<655<max(a[0],b[0]):
       patch('we-glass',core-1.7,20,core+1.7,46.8,.33)
       for y in np.arange(20,47,1.45):patch('we-mullion',core-1.7,y,core+1.7,y+.05,.37)
       for x in [core-1.7,core,core+1.7]:patch('we-mullion',x-.025,20,x+.025,46.8,.37)
     else:patch('we-gray',0,0,L,h,.1)
    else:
     patch('we-stone',0,0,L,h-.35,.1)
     if L>8:
      n=max(1,round(L/5));w=L/n
      for k in range(n):
       x=(k+.5)*w
       patch('we-glass',x-w*.35,.7,x+w*.35,5.8,.14)
       for y in [.7,3.0,5.8]:patch('we-mullion',x-w*.35,y,x+w*.35,y+.07,.19)
       patch('we-mullion',x-.04,.7,x+.04,5.8,.2)
      patch('we-sill',0,6.4,L,6.7,.3)
   B.planar('we-roof',surf.roof(kind,pp,h).difference(box(595.45,97.45,603.55,108.55)) if kind=='podium' else surf.roof(kind,pp,h),h+.025,True)
   for a,b in zip(ps,ps[1:]):
    F,L,_,_=facade_frame(B,a,b,pp,0);F.box('we-white',(L/2,h+.25,0),(L,.5,.3))
 # Open garage: slabs, recessed dark bays and piers, not a filled gray box.
 for floor in range(5):
  y=floor*3.1+.15;B.planar('we-roof',garage,y,True)
  for pp in parts(garage):
   ps=list(pp.exterior.coords)
   for a,b in zip(ps,ps[1:]):
    F,L,_,_=facade_frame(B,a,b,pp,0)
    F.box('we-white',(L/2,y+.5,0),(L,.85,.28),True)
    if floor<4:
     F.box('we-shadow',(L/2,y+1.8,.4),(L,1.7,.08))
     for x in np.arange(.25,L,4.3):B.shell(F.poly([(x-.2,-.225),(x+.2,-.225),(x+.2,.225),(x-.2,.225)]),y,y+3.1,'we-white',roof=False)
 # Plant and the raised central stair/lift overrun follow the actual tower footprint.
 B.box('we-gray',(655,51,74),(10,2,18),True)
 for x in np.arange(605,716,13):B.box('we-service',(x,50.65,73),(3.4,1.2,3.4))
 for yaw,z in [(math.pi,83.4),(0,64.3)]:
  F=Frame(B,655,z,yaw,y=0);F.text('WESTIN',(0,48.8,-.5),1.5,'we-letter')
 # Reference pool on the southwest podium roof; dimensions estimated from aerial.
 pool=box(596,98,603,108);B.planar('we-coping',pool.buffer(.55),7.66,True);B.planar('westin_pool',pool,7.68)
 for x in [594.5,605]:
  for z in [99,102,105,108]:B.box('we-chair',(x,7.95,z),(1.1,.45,1.8))
 return dict(key=KEY,name='The Westin Las Vegas',center=[655,0,75],bounds=[576,40,782,132],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],views={})
