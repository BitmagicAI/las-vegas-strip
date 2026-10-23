"""Tod Motor Motel: mapped U plan, January 2026 boarded street elevation.
Rear heights estimated; no claim of operating accommodation or interior access.
"""
from common import *
from forum_shops import facade_frame
KEY='todMotel'
def exterior(B):
 B.property=KEY+'-exterior';B.source='podium/frontage';B.detail=0;W=Frame(B,0,0,y=0)
 p=footprint('way/364846570');front=p.intersection(box(1920,-4125,1940,-4090));rear=p.difference(front)
 for poly,h in [(front,10.1),(rear,3.65)]:
  B.shell(poly,.18,h,'tm-blue-stucco',roof=False);B.planar('tm-flat-roof-paint',poly,h-.12,True)
  polys=list(poly.geoms) if hasattr(poly,'geoms') else [poly]
  for shape in polys:
   cs=list(shape.exterior.coords)
   for a,b in zip(cs,cs[1:]):
    G,L,nx,nz=facade_frame(B,a,b,shape,.035)
    G.box('tm-coping',(L/2,h,0),(L,.13,.18))
    if h>8 and nx>.7:
     for y in [5.05,8.15]:
      for u in [L*.25,L*.75]:
       G.box('tm-trim',(u,y,-.07),(2.55,1.75,.06));G.box('tm-board',(u,y,-.12),(2.4,1.6,.05))
     for u in [L*.17,L*.51,L*.82]:
      G.box('tm-trim',(u,1.75,-.08),(3.15,2.25,.06));G.box('tm-dark-panel',(u,1.75,-.13),(3,2.1,.05))
    elif h<5 and L>8:
     # Low motor-court bays visible through entry; exact rear rhythm uncertain.
     for u in np.arange(2.1,L-1.3,4.2):
      G.box('tm-trim',(u,1.6,-.06),(1.05,2.5,.08));G.box('tm-board',(u,1.6,-.12),(.92,2.35,.05))
      G.box('tm-trim',(u+1.3,2,-.07),(1.2,1.25,.08));G.box('tm-dark-panel',(u+1.3,2,-.13),(1.08,1.12,.05))
 # Thin sloping entry canopy: open underside, no slab across the vehicle route.
 for z in [-4098.8,-4091.2]:
  W.box('tm-blue-stucco',(1923.5,1.8,z),(.3,3.25,.3),True)
 for x in [1916.2,1923.5]:
  W.tube('tm-trim',(x,3.05,-4091.2),(x,3.8,-4098.8),.10,8)
 corners=[(1916,3.05,-4091),(1925,3.05,-4091),(1925,3.8,-4099),(1916,3.8,-4099)]
 B.face('tm-canopy-paint',list(reversed(corners)))
 B.face('tm-canopy-paint',[(x,y+.16,z) for x,y,z in corners])
 for a,b in zip(corners,corners[1:]+corners[:1]):
  B.face('tm-canopy-paint',[a,b,(b[0],b[1]+.16,b[2]),(a[0],a[1]+.16,a[2])])
 for a,b in [((1916,3.05,-4091),(1925,3.05,-4091)),((1916,3.8,-4099),(1925,3.8,-4099))]:W.tube('tm-trim',a,b,.12,8)
 # Surviving roadside sign, dimensions estimated against three-storey wing.
 S=Frame(B,1925,-4086,y=0,yaw=math.pi/2)
 for u in [-1.6,1.6]:S.tube('tm-trim',(0,4.2,0),(u,8.1,0),.14,10)
 S.box('tm-trim',(0,3,0),(.25,5.5,.25),True)
 for y,label,width in [(9.8,'TOD',3.3),(8.8,'MOTOR',4.1),(7.8,'MOTEL',3.9)]:
  S.box('tm-sign',(0,y,0),(width,.85,.18));S.text(label,(0,y-.04,-.13),.55,'tm-letter');S.text(label,(0,y-.04,.13),.55,'tm-letter',True)
 court=box(1893.9,-4111,1927,-4086).difference(p);B.planar('tm-paving',court,.18,True)
 B.planar('tm-paving',p.buffer(1,join_style=2).difference(p).difference(court),.18,True)
 for x,z in [(1889,-4095),(1889,-4107),(1905,-4115)]:W.box('tm-service',(x,4,z),(1.3,.8,1.1))
 samples=[]
 for x in np.arange(1895,1926,1.2):
  for z in np.arange(-4109,-4088,1.2):
   if court.buffer(-.5).covers(Point(x,z)) and not (1923<x<1924 and z<-4090):samples.append([float(x),.18,float(z)])
 Path('build/city-exteriors/tod-motel-samples.json').write_text(json.dumps(samples))
 return dict(key=KEY,name='Tod Motor Motel exterior',center=[1908,0,-4105],bounds=[1884,-4120,1929,-4085],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
