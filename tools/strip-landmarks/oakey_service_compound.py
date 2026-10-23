"""Retained service wing and exposed framing behind 505 E Oakey; dated reference reconstruction."""
from common import *
from forum_shops import facade_frame
KEY='oakeyService'
def exterior(B):
 B.property=KEY+'-exterior';B.source='podium/service';B.detail=0;W=Frame(B,0,0,y=0)
 p=footprint('way/364845144')
 # The mapped envelope predates partial demolition. Keep only the visible eastern shed and southern kink.
 south=p.intersection(box(1890,-3856,1940,-3830));shed=Polygon([(1920,-3888),(1931,-3888),(1931.7,-3853),(1920.7,-3853)])
 B.shell(south,.16,3.8,'ocs-stucco',roof=False);B.planar('ocs-roof-paint',south,3.8,True)
 B.shell(shed,.16,3.6,'ocs-metal-paint',roof=False)
 B.upface('ocs-metal-roof-paint',[(1920,3.63,-3888),(1925.5,4.1,-3888),(1926.2,4.1,-3853),(1920.7,3.63,-3853)])
 B.upface('ocs-metal-roof-paint',[(1925.5,4.1,-3888),(1931,3.63,-3888),(1931.7,3.63,-3853),(1926.2,4.1,-3853)])
 for z in [-3888,-3853]:
  dx=(z+3888)*.02
  B.face('ocs-metal-paint',[(1920+dx,3.6,z),(1931+dx,3.6,z),(1925.5+dx,4.1,z)])
 for z in np.arange(-3887.7,-3853,.65):
  dx=(z+3888)*.02
  W.path('ocs-roof-seam-paint',[(1920+dx,3.66,float(z)),(1925.5+dx,4.13,float(z)),(1931+dx,3.66,float(z))],.018,5)
 for shape in [shed,south]:
  for a,b in zip(list(shape.exterior.coords),list(shape.exterior.coords)[1:]):
   G,L,nx,nz=facade_frame(B,a,b,shape,.035)
   G.box('ocs-cap-paint',(L/2,3.65,-.07),(L,.14,.22))
   if nx<-.65 and L>15:
    for u in [L*.25,L*.72]:
     G.box('ocs-door-paint',(u,1.65,-.09),(3.2,2.85,.12))
     for yy in np.arange(.3,3,.22):G.box('ocs-door-seam',(u,float(yy),-.16),(3.15,.025,.02))
     for du in [-1.66,1.66]:G.box('ocs-frame-paint',(u+du,1.7,-.18),(.1,3.1,.18))
     G.box('ocs-frame-paint',(u,3.24,-.18),(3.4,.12,.18))
    G.box('ocs-door-paint',(L*.5,1.2,-.1),(.95,2.15,.15))
   if nx>.7:
    for u in np.arange(.3,L,.55):G.box('ocs-wall-seam-paint',(float(u),1.85,-.04),(.02,3.5,.04))
   if nz>.4 and L>8:
    G.box('ocs-door-paint',(L*.5,1.2,-.09),(1,2.15,.14));G.box('ocs-vent',(L*.22,2.8,-.1),(1,.5,.14))
 # Northern retained masonry and open timber roof frame; no invented intact roof over the cleared portion.
 W.box('ocs-block',(1930,1.65,-3901),( .25,3.0,16),True)
 W.box('ocs-block',(1916.4,1.15,-3909),(27,2.1,.3),True)
 W.box('ocs-block',(1903.1,.75,-3901),(.3,1.3,16),True)
 for z in np.arange(-3908,-3893,2):
  W.tube('ocs-timber',(1903,3.2,float(z)),(1916.5,4.5,float(z)),.085,4)
  W.tube('ocs-timber',(1916.5,4.5,float(z)),(1930,3.2,float(z)),.085,4)
  W.tube('ocs-timber',(1903,3.2,float(z)),(1930,3.2,float(z)),.075,4)
  for x in np.arange(1907,1929,5):W.tube('ocs-timber',(float(x),3.2,float(z)),(1916.5,4.5,float(z)),.04,4)
 for x in [1903,1916.5,1930]:W.tube('ocs-timber',(x,3.2 if x!=1916.5 else 4.5,-3909),(x,3.2 if x!=1916.5 else 4.5,-3893),.075,4)
 # Patch only this site's exposed slab/soil, preserving street and chapel geometry.
 site=box(1897,-3915,1933,-3838).difference(unary_union([shed,south]))
 B.planar('ocs-yard-gravel',site,.12,True)
 slab=box(1903,-3909,1930,-3893);B.planar('ocs-slab',slab,.15,True)
 for x,z,sx,sz in [(1907,-3884,3,5),(1910,-3871,5,8),(1909,-3858,4,3)]:
  W.box('ocs-slab',(x,.155,z),(sx,.035,sz),True)
 # Street boundary / gate: bars retained close to camera, one broad collision plane.
 G=Frame(B,1897,-3915,y=0)
 for u in np.arange(0,36.01,.2):G.tube('ocs-fence-paint',(float(u),.14,0),(float(u),2.65,0),.016,5)
 for y in [.3,2.35]:G.tube('ocs-fence-paint',(0,y,0),(36,y,0),.028,6)
 for u in np.arange(0,36.01,4):G.box('ocs-fence-paint',(float(u),1.4,0),(.075,2.7,.075))
 B.face('ocs-collision',[G.p(0,.1,0),G.p(36,.1,0),G.p(36,2.7,0),G.p(0,2.7,0)],True)
 G.box('ocs-sign-paint',(25,1.4,-.05),(1.15,1.1,.06));G.text('NO ENTRY',(25,1.6,-.1),.12,'ocs-red-letter');G.text('WORK SITE',(25,1.2,-.1),.11,'ocs-dark-letter')
 B.groups={k:g for k,g in B.groups.items() if g['material']!='ocs-collision'}
 # Roof membrane patches and service penetrations follow the retained southern plan.
 for x,z in [(1910,-3850),(1922,-3847)]:
  if south.covers(Point(x,z)):W.box('ocs-service-paint',(x,4.15,z),(1.1,.7,.9));W.box('ocs-vent',(x,4.51,z),(.9,.03,.7))
 W.box('ocs-slab',(1916,.12,-3917.5),(38,.16,5),True)
 samples=[]
 for x in np.arange(1897,1935,1):
  for z in np.arange(-3920,-3916,1):samples.append([float(x),.1,float(z)])
 Path('build/city-exteriors/oakey-service-compound-samples.json').write_text(json.dumps(samples))
 return dict(key=KEY,name='Oakey retained service compound',center=[1919,0,-3876],bounds=[1896,-3921,1935,-3837],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
