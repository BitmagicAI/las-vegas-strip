"""Original Barry's Boxing reconstruction; measured footprint, inferred public layout."""
from common import *
from shapely.geometry.polygon import orient
KEY='barrys-boxing'
def build(B):
 p=orient(footprint('way/464694107'),sign=1);F=Frame(B,246.1925,-2811.7965,1.0947,y=0)
 B.property=KEY+'-exterior';B.source='industrial/'+KEY;B.detail=0
 door=dict(p=F.p(-4,.24,0),yaw=F.yaw,width=1.6,height=2.65,name="Barry's Boxing entrance",venue=KEY)
 B.shell(p,0,4.9,'bb-cream',openings=[door],roof=False);B.planar('bb-membrane',p,4.88)
 # Narrow red/blue parapet banner, raised lettering and original simple stars.
 F.box('bb-red',(0,4.56,-.065),(18.5,.64,.1));F.box('bb-blue',(0,4.56,-.13),(18.25,.47,.045))
 F.text('AMATEUR BOXING',(-4.8,4.48,-.18),.25,'bb-letter');F.text('PROFESSIONAL BOXING',(4.8,4.48,-.18),.22,'bb-letter')
 F.box('bb-red',(0,4.56,-.19),(2.4,.75,.08));F.text("BARRY'S",(0,4.62,-.25),.3,'bb-letter');F.text('BOXING',(0,4.3,-.25),.28,'bb-letter')
 F.text('BOXING',(3,3.65,-.13),.6,'bb-red');F.text('2664',(-8,3.1,-1.85),.4,'bb-red')
 for u in [-8.6,-7.9,-1.5,1.5,7.8,8.6]:
  pts=[F.p(u+(.09 if i%2==0 else .035)*math.sin(i*math.pi/5),4.56+(.09 if i%2==0 else .035)*math.cos(i*math.pi/5),-.18)for i in range(10)]
  B.face('bb-letter',pts);B.face('bb-letter',list(reversed(pts)))
 # Recessed doorway with a shallow canopy, low front annex and barred window.
 F.box('bb-red',(-4,2.99,-.7),(2.6,.15,1.6))
 for u in [-4.81,-3.19]:F.box('bb-alloy',(u,1.57,-.04),(.05,2.66,.08))
 F.box('bb-clear',(-4,1.57,.02),(1.5,2.6,.025));F.box('bb-red',(-4,.65,-.05),(1.55,.8,.05))
 for y in [.24,2.12,2.89]:F.box('bb-red',(-4,y,-.06),(1.6,.055,.08))
 F.tube('bb-alloy',(-3.5,1.2,-.15),(-3.5,1.65,-.15),.025,10)
 F.box('bb-cream',(-7,1.65,-.85),(4.4,3.3,1.7),True);F.box('bb-red',(-7,3.34,-.85),(4.5,.1,1.8))
 F.box('bb-glass',(-7,1.9,-1.72),(2.4,1.25,.03))
 for u in np.arange(-8.2,-5.79,.2):F.box('bb-alloy',(float(u),1.9,-1.78),(.02,1.27,.04))
 for y in [1.26,2.54]:F.box('bb-red',(-7,y,-1.77),(2.5,.055,.05))
 F.box('bb-concrete',(-4,.12,-1.1),(1.8,.24,2.2),True)
 B.upface('bb-concrete',[F.p(-4.9,0,-3.2),F.p(-3.1,0,-3.2),F.p(-3.1,.24,-2.2),F.p(-4.9,.24,-2.2)],True)
 # Subtle original masonry courses, kept clear of the entrance opening.
 for row,y in enumerate(np.arange(.3,4.21,.3)):
  for lo,hi in [(-9.2,-4.85),(-3.15,9.2)]:
   F.box('bb-mortar',((lo+hi)/2,float(y),-.018),(hi-lo,.012,.015))
   for u in np.arange(lo+.3*(row%2),hi,.6):F.box('bb-mortar',(float(u),float(y)-.15,-.019),(.012,.29,.015))
 # Roof coping, membrane seams, vents and packaged air units.
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  R=Frame(B,(a[0]+b[0])/2,(a[1]+b[1])/2,math.atan2(a[1]-b[1],b[0]-a[0]),y=0);R.box('bb-coping',(0,4.96,0),(math.dist(a,b),.13,.24))
 for u,v in [(-4,8),(5,20),(-3,29)]:
  F.box('bb-equipment',(u,5.3,v),(1.5,.8,2));F.lathe('bb-dark',u,v,[(5.71,.45),(5.74,.45)],16)
  for vv in np.arange(v-.8,v+.81,.2):F.box('bb-alloy',(u+.76,5.3,float(vv)),(.025,.5,.06))
 for v in [6,14,24,31]:F.box('bb-coping',(0,4.9,v),(17,.015,.035))
 # Southern side service door, conduit and narrow upper glazing.
 for v in [7,24,31]:
  F.box('bb-glass',(-9.24,3.7,v),(.04,.65,2.3));F.box('bb-coping',(-9.28,3.34,v),(.12,.07,2.4))
 F.box('bb-door',(-9.25,1.5,29),(.08,2.5,1.2),True)
 F.tube('bb-alloy',(-9.3,.4,30),(-9.3,4.6,30),.035,10)
 B.property=KEY+'-interior';B.source='public/'+KEY
 room=Polygon([(F.p(u,0,v)[0],F.p(u,0,v)[2])for u,v in [(-8.9,.2),(8.9,.2),(8.9,34),(-8.9,34)]]).intersection(p.buffer(-.08))
 B.planar('bb-rubber',room,.24,True);B.shell(room,.24,4.55,'bb-cream',openings=[door],roof=False,solid=True)
 F.box('bb-concrete',(-4,.12,.12),(1.6,.24,.5),True)
 for t in triangles(room):
  pts=[(x,4.55,z)for x,z in list(t.exterior.coords)[:-1]];ar=np.array(pts);B.face('bb-wood',pts if np.cross(ar[1]-ar[0],ar[2]-ar[0])[1]<0 else list(reversed(pts)))
 for v in np.arange(1.2,34,1.2):F.box('bb-wood',(0,4.4,float(v)),(17.7,.25,.11))
 for v in [4,10,16,22,28,32]:
  for u in [-4,4]:F.box('bb-lamp',(u,4.1,v),(.1,.07,2.3))
 # Red canvas boxing ring with dark ropes and padded corners.
 F.box('bb-red',(2,.69,13),(7.5,.9,7.5),True);F.box('bb-mat',(2,1.16,13),(7.45,.04,7.45),True)
 for u in [-1.7,5.7]:
  for v in [9.3,16.7]:F.tube('bb-steel',(u,.24,v),(u,2.65,v),.065,12);F.box('bb-red',(u,1.95,v),(.23,1.25,.23))
 for y in [1.5,1.83,2.16,2.49]:
  for v in [9.35,16.65]:F.tube('bb-dark',(-1.65,y,v),(5.65,y,v),.03,10)
  for u in [-1.65,5.65]:F.tube('bb-dark',(u,y,9.35),(u,y,16.65),.03,10)
 for i in range(4):F.box('bb-concrete',(2,.24+(i+1)*.115,8.1+i*.3),(1.1,(i+1)*.23,.32),True)
 # Hanging bags, suspension chains, original abstract framed memorabilia.
 for v in [6,11,16,21,26]:
  F.lathe('bb-bag',-6,v,[(.8,.27),(.9,.31),(2.3,.31),(2.45,.22)],20)
  for du in [-.2,.2]:F.tube('bb-alloy',(-6+du,2.4,v),(-6,4.3,v),.012,8)
  for y in [.95,2.25]:F.lathe('bb-gold',-6,v,[(y,.316),(y+.07,.316)],20)
 for v in [4,8,12,16,20,24,28,32]:
  F.box('bb-dark',(8.82,2.7,v),(.06,1,.8));F.box('bb-letter',(8.77,2.7,v),(.03,.9,.7))
  for k in range(4):F.box('bb-red' if k==0 else 'bb-dark',(8.74,2.95-k*.16,v),(.02,.06,.5))
 # Distinct red diamond-mesh lockers evidenced in August2026; original lattice.
 for u in [-6,-5.2,-4.4,-3.6,-2.8]:
  F.box('bb-red',(u,1.3,32.8),(.74,2.1,.6),True);F.box('bb-dark',(u,1.4,32.485),(.61,1.65,.02))
  for sign in [-1,1]:
   for y in np.arange(.5,2.3,.18):
    F.tube('bb-red',(u-.29,float(y),32.46),(u+.29,float(y)+sign*.2,32.46),.012,6)
  F.box('bb-alloy',(u+.25,1.3,32.43),(.05,.12,.035))
 F.box('bb-wood',(0,.65,29),(3,.12,.65),True)
 for u in [-1.2,1.2]:F.box('bb-steel',(u,.43,29),(.1,.5,.55),True)
 routes=[dict(name='Entry and training aisle',points=[F.p(u,y,v)for u,y,v in [(-4,0,-3.6),(-4,0,-3.2),(-4,.24,-2.2),(-4,.24,1),(-4,.24,6),(-4,.24,20)]]),dict(name='Rear lockers and ring aisle',points=[F.p(u,.24,v)for u,v in [(-4,20),(-4,28),(3,28),(7,28),(7,20),(7,7),(2,7)]])]
 return dict(key=KEY,name="Barry's Boxing",center=[260,0,-2807],bounds=list(p.buffer(5).bounds),structural=True,hotelSources=[],exteriorOnly=False,portals=[door],zones=[dict(origin=F.p(0,.24,.2),yaw=F.yaw,width=17.8,depth=33.8,height=4.3)],lights=[dict(p=F.p(u,4,v),color=0xfff1db,power=4,range=13)for u,v in [(-4,6),(4,6),(-4,25),(4,25)]],routes=routes)
if __name__=='__main__':
 B=Meshes();m=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(m,indent=2)+'\n');print(KEY,sum(len(g['faces'])for g in B.groups.values()),'triangles')
