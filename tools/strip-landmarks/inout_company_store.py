"""Original Company Store exterior from mapped footprint and linked photographic references."""
from common import *
KEY='inout-company-store';IDS=['way/432534216','way/432534217']
def build(B):
 p=footprint(IDS[0]);canopy=footprint(IDS[1]);B.property=KEY+'-exterior';B.source='podium/'+KEY;B.detail=0
 B.shell(p,.04,5.8,'store-stucco',roof=False);B.planar('store-roof',p,5.54)
 B.shell(p,.04,.24,'store-base',roof=False,solid=False)
 # Low continuous parapet with proper cap and inward return.
 B.shell(p.buffer(-.20,join_style=2),5.54,5.8,'store-stucco',roof=False,solid=False)
 B.planar('store-cap',p.difference(p.buffer(-.23,join_style=2)),5.85)
 # Canopy is the separately mapped west polygon, not a new neighboring building.
 B.shell(canopy,3.15,3.43,'store-red',solid=False,roof=False);B.planar('store-cap',canopy,3.43);B.planar('store-soffit',canopy,3.15)
 for x,z in list(canopy.exterior.coords)[:-1][2:]:B.box('store-stucco',(x,1.58,z),(.32,3.15,.32),True)
 # Front wraps the south and southwest faces; exact bay divisions are photographic estimates.
 fronts=[((-800.635,1608.244),(-824.52,1593.772)),((-824.52,1593.772),(-818.081,1584.344))]
 routes=[]
 for j,(a,b) in enumerate(fronts):
  L=math.dist(a,b);F=Frame(B,*a,math.atan2(-(b[1]-a[1]),b[0]-a[0]),y=0)
  for yy in [3.30,3.51,3.72]:F.box('store-red',(L/2,yy,-.64),(L+.16,.19,1.45))
  F.box('store-soffit',(L/2,3.16,-.64),(L+.10,.08,1.4))
  # The existing shell backs unopened retail glazing; accessible interior needs additional evidence.
  bays=5 if j==0 else 2;pitch=L/bays
  for k in range(bays):
   x=(k+.5)*pitch;w=pitch-.56
   F.box('store-recess',(x,1.58,-.035),(w,2.82,.06))
   F.box('store-glass',(x,1.58,-.09),(w-.09,2.70,.035))
   for xx in [x-w/2,x,x+w/2]:F.box('store-metal',(xx,1.58,-.14),(.055,2.80,.08))
   for yy in [.20,1.55,2.98]:F.box('store-metal',(x,yy,-.14),(w,.055,.08))
  # Closed door skins: photograph supports service door; retail entrance position estimated.
  if j==0:
   dx=L*.45
   F.box('store-stucco',(dx,1.58,-.17),(1.45,2.85,.13))
   F.box('store-door',(dx,1.33,-.25),(.96,2.48,.06))
   F.box('store-metal',(dx,.35,-.29),(.89,.48,.025))
   F.box('store-metal',(dx-.34,1.25,-.31),(.035,.26,.06))
   F.text('STAFF',(dx,1.85,-.30),.11,'store-joint')
  else:
   dx=pitch*.5
   for xx in [dx-1.1,dx,dx+1.1]:F.box('store-metal',(xx,1.53,-.19),(.07,2.67,.10))
   for xx in [dx-.14,dx+.14]:F.tube('store-metal',(xx,1.04,-.28),(xx,1.47,-.28),.022,8)
   F.text('4838',(dx,2.78,-.23),.18,'store-letter')
  # Photographed high circular Company Store emblem represented with original lettered geometry.
  if j==0:
   cx=L*.59
   B.arc('store-sign-edge',F.p(cx,4.76,-.12),.64,yaw=F.yaw,thick=.035,n=48)
   for t in np.linspace(0,math.tau,49)[:-1]:
    B.face('store-sign-face',[F.p(cx,4.76,-.145),F.p(cx+.61*math.cos(t),4.76+.61*math.sin(t),-.145),F.p(cx+.61*math.cos(t+math.tau/48),4.76+.61*math.sin(t+math.tau/48),-.145)])
   for r in [.61,.57]:B.arc('store-sign-face',F.p(cx,4.76,-.10),r,yaw=F.yaw,thick=.035,n=48)
   F.text('IN-N-OUT',(cx,4.87,-.19),.31,'store-red');F.text('COMPANY STORE',(cx,4.45,-.19),.23,'store-red')
   F.text('MERCHANDISE',(L*.32,2.18,-.19),.32,'store-letter')
  # Original pedestrian apron; single support layer outside existing shell.
  F.box('store-paving',(L/2,.015,-1.55),(L,.15,3.08),True)
  routes.append(dict(name=('South' if j==0 else 'West')+' covered frontage',points=[F.p(t,.09,-2.0) for t in [1,L/2,L-1]]))
 # Northern service frontage retains closed access and receives panel joints, vents and roof equipment.
 coords=list(p.exterior.coords)
 for a,b in zip(coords,coords[1:]):
  L=math.dist(a,b);F=Frame(B,*a,math.atan2(-(b[1]-a[1]),b[0]-a[0]),y=0)
  if L<2:continue
  for t in np.arange(2,L,4):F.box('store-joint',(t,2.85,.025),(.022,5.55,.025))
 # Equipment placement approximate, roof dimensions mapped.
 for x,z in [(-801,1569),(-805,1578),(-803,1597),(-814,1592)]:
  B.box('store-equipment',(x,5.92,z),(1.7,.76,1.3));B.box('store-cap',(x,6.32,z),(1.82,.07,1.42))
  for dz in [-.36,-.18,0,.18,.36]:B.box('store-joint',(x,6.02,z+dz),(1.73,.035,.055))
 return dict(key=KEY,name='In-N-Out Company Store',center=[-803,0,1584],bounds=[-834,1552,-778,1612],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=routes,hotelSources=[])
if __name__=='__main__':
 B=Meshes();meta=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(meta,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
