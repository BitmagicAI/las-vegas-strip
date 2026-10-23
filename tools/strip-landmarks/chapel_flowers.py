"""Chapel of the Flowers exterior campus; mapped plan, January2026 references."""
from common import *
from forum_shops import facade_frame
KEY='chapelFlowers'
def arch(G,u,base,width,height,w=-.08):
 r=width/2;spring=base+height-r
 pts=[(u-r,base,w),(u+r,base,w)]+[(u+r*math.cos(a),spring+r*math.sin(a),w) for a in np.linspace(0,math.pi,13)]
 G.b.face('cf-glass',[G.p(*v) for v in reversed(pts)])
 G.path('cf-white-paint',pts+[pts[0]],.055,8)
 G.tube('cf-white-paint',(u,base,w-.025),(u,base+height,w-.025),.028,6)
 for y in [base+height*.35,spring]:G.tube('cf-white-paint',(u-r,y,w-.025),(u+r,y,w-.025),.025,6)
def roof(G,width,depth,base,rise,z=0):
 for side in [-1,1]:
  G.b.face('cf-tile-paint',[G.p(side*width/2,base,z),G.p(0,base+rise,z),G.p(0,base+rise,z+depth),G.p(side*width/2,base,z+depth)])
 for zz in [z,z+depth]:
  G.b.face('cf-stucco',[G.p(-width/2,base,zz),G.p(width/2,base,zz),G.p(0,base+rise,zz)])
  G.path('cf-white-paint',[(-width/2,base,zz),(0,base+rise,zz),(width/2,base,zz)],.1,8)
 for yy in np.arange(.12,rise,.25):
  xx=width/2*(1-yy/rise)
  for side in [-1,1]:G.tube('cf-roof-seam-paint',(side*xx,base+yy+.012,z),(side*xx,base+yy+.012,z+depth),.015,5)
 for side in [-1,1]:G.box('cf-white-paint',(side*width/2,base,z+depth/2),(.14,.15,depth))
def fence(G,length,height=1.2):
 for u in np.arange(0,length+.05,.22):G.tube('cf-iron-paint',(float(u),.24,0),(float(u),height+.24,0),.016,5)
 for y in [.32,height+.24]:G.tube('cf-iron-paint',(0,y,0),(length,y,0),.025,6)
 for u in np.arange(.6,length,1.2):
  pts=[(float(u)+.18*math.cos(a),height+.24+.17*math.sin(a),0) for a in np.linspace(0,math.tau,17)]
  G.path('cf-iron-paint',pts,.012,5)
 # Broad collision surface; decoration has no individual colliders.
 G.b.face('cf-collision',[G.p(0,.2,0),G.p(length,.2,0),G.p(length,height+.25,0),G.p(0,height+.25,0)],True)
def exterior(B):
 B.property=KEY+'-exterior';B.source='podium/chapel';B.detail=0
 small=footprint('way/364845143');rear=footprint('way/316303726');wing=footprint('way/364845145');allbuild=unary_union([small,rear,wing])
 B.shell(small,.18,3.5,'cf-stucco',roof=False);B.planar('cf-roof-paint',small,3.5)
 F=Frame(B,1832.36,-3851.409,yaw=2.676,y=0)
 roof(F,6.25,14.7,3.5,2.55,-.2)
 # Street side arcade windows, entrance in the garden-facing return.
 for side in [-1,1]:
  for z in [1.7,4.45,7.2,10,12.7]:
   a=F.p(side*3.02,0,z);G=Frame(B,a[0],a[2],yaw=F.yaw-side*math.pi/2,y=0);arch(G,0,.62,.85,2.35,-.04)
 F.box('cf-door-paint',(0,1.35,-.06),(1.6,2.35,.12));arch(F,0,3.98,.65,.75,-.06)
 F.text('Chapel of the',(0,2.7,-.15),.25,'cf-gold-paint');F.text('Flowers',(0,2.37,-.15),.34,'cf-gold-paint')
 # Four-sided louvered belfry, octagonal tapered spire and finial.
 tz=10.9;F.box('cf-white-paint',(0,6.5,tz),(1.3,1.55,1.3));F.box('cf-white-paint',(0,5.78,tz),(1.62,.17,1.62))
 for side in [-1,1]:
  for yy in np.arange(6,6.9,.12):
   F.box('cf-louver-paint',(0,float(yy),tz+side*.67),(.85,.045,.05));F.box('cf-louver-paint',(side*.67,float(yy),tz),(.05,.045,.85))
 F.lathe('cf-white-paint',0,tz,[(7.2,.95),(7.4,.72),(10.45,.04)],8);F.tube('cf-gold-paint',(0,10.4,tz),(0,11,tz),.022,6)
 # Flat service/reception wings retain distinct mapped footprints.
 for p,h in [(rear,4.6),(wing,3.55)]:
  B.shell(p,.18,h,'cf-stucco',roof=False);B.planar('cf-roof-paint',p,h,True)
  for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
   G,L,nx,nz=facade_frame(B,a,b,p,.04);G.box('cf-white-paint',(L/2,h,-.07),(L,.2,.22))
   if nz>.6:
    for u in np.arange(2,L-1,3.2):arch(G,float(u),.7,1.45,2.3,-.08)
   elif L>8:G.box('cf-door-paint',(L*.55,1.4,-.08),(1.15,2.4,.12))
  c=p.representative_point();W=Frame(B,0,0,y=0)
  for dx in [-5,0,5]:W.box('cf-service-paint',(c.x+dx,h+.35,c.y),(1.1,.7,1.4))
 # Small projecting central glazed gable seen at the end of the motor court.
 E=Frame(B,1875.4,-3837.67,yaw=2.65,y=0)
 E.box('cf-stucco',(0,2.25,1),(5.9,4.2,2.1),True);roof(E,6.25,2.5,4.35,2.3,-.25)
 arch(E,0,.38,3.6,5.25,-.34)
 E.box('cf-paving',(0,.2,-1.4),(6.2,.08,2.8),True)
 for u in [-1.15,-.55,.55,1.15]:E.box('cf-white-paint',(u,2.6,-.43),(.07,4.4,.09))
 E.box('cf-white-paint',(0,6.9,1),(1.0,1.4,1));E.lathe('cf-tile-paint',0,1,[(7.55,.8),(9.8,.02)],4)
 # Single continuous motor court with garden pocket, independent of existing roads.
 site=Polygon([(1834,-3867),(1876,-3866),(1923,-3840),(1902,-3796),(1818,-3841)])
 garden=Polygon([(1834,-3867),(1871,-3860),(1863,-3845),(1854,-3836),(1830,-3841),(1818,-3841)]).difference(allbuild)
 apron=site.difference(allbuild);B.planar('cf-pavers',apron.difference(garden),.18,True);B.planar('cf-grass',garden,.2,True)
 # Garden walk connects small chapel to court without enclosed blocked test routes.
 path=LineString([(1836,-3849),(1846,-3844),(1854,-3840),(1860,-3843)]).buffer(.9)
 B.planar('cf-paving',path.intersection(apron),.225,True)
 streetA=F.p(4.2,0,-.6);streetB=F.p(4.2,0,14.7)
 for a,b in [((streetA[0],streetA[2]),(streetB[0],streetB[2])),((1821,-3840),(1849,-3824))]:
  dx,dz=b[0]-a[0],b[1]-a[1];H=Frame(B,a[0],a[1],yaw=math.atan2(-dz,dx),y=0);fence(H,math.hypot(dx,dz))
 # Road sign has its own white gable outline, not a luminous billboard.
 S=Frame(B,1823,-3839,yaw=1.08,y=0)
 for u in [-1,1]:S.box('cf-white-paint',(u,2.7,0),(.18,5,.18),True)
 S.box('cf-white-paint',(0,4.3,0),(2.6,1.9,.2));roof(S,2.85,.3,5.3,.7,-.15)
 for text,y,size in [('CHAPEL',4.8,.3),('OF THE',4.4,.2),('FLOWERS',3.98,.29)]:S.text(text,(0,y,-.14),size,'cf-gold-paint')
 # Southern shade canopy is an open tent, not an enclosed additional building.
 T=Frame(B,1840,-3828,yaw=.49,y=0)
 for u in [-4,4]:
  for w in [-2,2]:T.tube('cf-white-paint',(u,.18,w),(u,2.7,w),.04,6)
 for a,b in [((-4,-2),(4,-2)),((4,-2),(4,2)),((4,2),(-4,2)),((-4,2),(-4,-2))]:B.face('cf-fabric-paint',[T.p(a[0],2.7,a[1]),T.p(b[0],2.7,b[1]),T.p(0,4.1,0)])
 B.groups={k:g for k,g in B.groups.items() if g['material']!='cf-collision'}
 samples=[]
 excluded=allbuild.buffer(.65).union(Point(1823,-3839).buffer(1.6)).union(E.poly([(-3.4,-.3),(3.4,-.3),(3.4,2.3),(-3.4,2.3)]))
 for x in np.arange(1822,1920,1.7):
  for z in np.arange(-3865,-3800,1.7):
   pt=Point(x,z)
   if apron.buffer(-1).covers(pt) and not excluded.covers(pt):samples.append([float(x),.18,float(z)])
 Path('build/city-exteriors/chapel-flowers-samples.json').write_text(json.dumps(samples))
 return dict(key=KEY,name='Chapel of the Flowers campus exterior',center=[1866,0,-3835],bounds=[1817,-3868,1924,-3795],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
