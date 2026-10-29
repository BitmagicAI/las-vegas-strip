"""Original Buca Flamingo architecture. Public room placement and heights inferred.
References are linked in the block record; no photographic artwork is reproduced.
"""
from common import *
KEY='buca-flamingo';ID='way/390004031';YAW=math.atan2(5.132,30.323)
def build(B):
 p=footprint(ID);F=Frame(B,1903.4605,127.244,YAW,y=0);w=30.75
 B.property=KEY+'-exterior';B.source='retail/'+KEY;B.detail=0
 door=dict(p=F.p(-10,.20,0),yaw=YAW,width=2.3,height=2.7,name='Public dining entrance',venue=KEY)
 windows=[dict(p=F.p(u,1.025,0),yaw=YAW,width=2.65,height=1.8) for u in [-3,2,7,12]]
 B.shell(p,.02,5.4,'bf-stucco',roof=False,openings=[door,*windows]);B.planar('bf-roof-paint',p.buffer(-.15),5.18)
 B.planar('bf-floor',p,.20,True)
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  R=Frame(B,(a[0]+b[0])/2,(a[1]+b[1])/2,math.atan2(a[1]-b[1],b[0]-a[0]),y=0)
  R.box('bf-coping',(0,5.43,0),(math.dist(a,b)+.08,.12,.28))
 # Southwest entrance tower and projected porch, fitted to tourism photograph.
 F.box('bf-stone',(-6.5,3.15,-.12),(4.0,6.3,.45))
 F.box('bf-stucco',(-10.5,3.15,1.25),(7.1,.36,2.6))
 for u in [-13.6,-8.2]:
  for v in [1.9,2.2]:F.tube('bf-cream',(u,.2,v),(u,3,v),.065,12)
 for u in [-11.2,-8.8]:F.box('bf-door-paint',(u,1.55,.10),(.10,2.7,.20))
 F.box('bf-door-paint',(-10,2.93,.1),(2.5,.12,.2))
 F.text('Welcome',(-10.5,3.35,2.60),.46,'bf-cream',back=True)
 # Local entry apron, connects existing grade to the public floor; no road regeneration.
 B.upface('bf-concrete',[F.p(-13.8,.20,0),F.p(-7.5,.20,0),F.p(-7.5,.03,4),F.p(-13.8,.03,4)],True)
 # Glazed windows and green/cream striped fabric awnings.
 def awning(R,u,width,transparent=False):
  R.box('bf-glass' if transparent else 'bf-back-glass',(u,1.9,.02),(width,2.05,.045),True)
  if transparent:
   for x in [u-width/2,u+width/2]:R.box('bf-cream',(x,1.9,-.09),(.065,2.14,.30))
   for yy in [.85,2.95]:R.box('bf-cream',(u,yy,-.09),(width,.065,.30))
  for x in [u-width/2,u,u+width/2]:R.box('bf-door-paint',(x,1.9,.13),(.055,2.14,.08))
  for yy in [.85,2.95]:R.box('bf-door-paint',(u,yy,.13),(width,.06,.08))
  n=round(width/.2)
  for i in range(n):
   a=u-width/2+i*width/n;b=a+width/n;mat='bf-green'
   B.upface(mat,[R.p(a,3.28,.03),R.p(b,3.28,.03),R.p(b,2.65,1.05),R.p(a,2.65,1.05)])
   B.face(mat,[R.p(a,2.65,1.05),R.p(b,2.65,1.05),R.p(b,2.42,1.05),R.p(a,2.42,1.05)])
 for u in [-3,2,7,12]:awning(F,u,2.65,True)
 W=Frame(B,1886.46,118.923,YAW-math.pi/2,y=0)
 for u in [-6,0,6]:awning(W,u,2.5)
 F.text('BUCA',(-6.5,4.6,.20),.9,'bf-sign-red',back=True)
 F.text('di BEPPO',(-6.5,3.65,.20),.48,'bf-cream',back=True)
 # Pale stone base below window sills, interrupted at the public door.
 for a,b in [(-15.2,-11.25),(-8.75,15.2)]:F.box('bf-stone',((a+b)/2,.38,-.025),(b-a,.72,.20))
 W.text('Buca di Beppo',(0,4.0,.20),.9,'bf-sign-red',back=True)
 # Retro freestanding sign: original simplified lettering and curved side blade.
 S=Frame(B,*[F.p(-13.7,0,3.4)[i] for i in [0,2]],YAW,y=0)
 S.box('bf-door-paint',(0,3,0),(.38,6,.38),True);S.box('bf-sign-red',(0,7.2,0),(1.7,5.2,.35))
 for i,c in enumerate('BUCA'):S.text(c,(0,8.65-i*.75,.22),.72,'bf-cream',back=True)
 S.text('di Beppo',(0,5.8,.22),.29,'bf-cream',back=True)
 S.box('bf-sign-red',(0,4.8,.05),(2.6,1.15,.5));S.text('ITALIAN',(0,4.9,.34),.38,'bf-cream',back=True);S.text('Restaurant',(0,4.45,.34),.29,'bf-cream',back=True)
 for t in np.linspace(0,1,24):
  S.box('bf-sign-red',(1.0+.25*math.sin(t*math.pi),5.6+t*4.1,0),(.24,.19,.4))
 for u in [-4,2,8,14]:
  F.box('bf-planter',(u,.28,1.7),(1.9,.5,1.05),True)
  for dx in [-.5,0,.5]:B.sphere('bf-leaf',F.p(u+dx,.85,1.7),.55,10,6)
 for u,v in [(-10,-5),(-10,-10),(-5,-15),(-11,-18)]:
  F.box('bf-roof-paint',(u,5.55,v),(2,.7,1.55));F.box('bf-door-paint',(u,5.94,v),(1.8,.06,1.35))
 # Public dining zone only; the full service/kitchen layout is not known.
 B.property=KEY+'-interior';B.source='public/'+KEY
 room=F.poly([(-14.8,-.18),(14.8,-.18),(14.8,-12),(-14.8,-12)])
 B.shell(room,.2,3.75,'bf-rust',roof=False,openings=[door,*windows],solid=True);B.shell(room.buffer(-.03),.2,1.25,'bf-wood',roof=False,openings=[door,*windows],solid=False)
 B.planar('bf-carpet',room,.211)
 # Barrel vault in the main room, as seen in owner photo; fitted elevation, not surveyed.
 for i in range(32):
  a=math.pi*i/32;b=math.pi*(i+1)/32
  B.face('bf-vault',[F.p(-14.8,3.65+1.05*math.sin(a),-6.09+5.91*math.cos(a)),F.p(-14.8,3.65+1.05*math.sin(b),-6.09+5.91*math.cos(b)),F.p(14.8,3.65+1.05*math.sin(b),-6.09+5.91*math.cos(b)),F.p(14.8,3.65+1.05*math.sin(a),-6.09+5.91*math.cos(a))])
 # Original abstract framed decoration, not copies of the wall photographs.
 for u in np.arange(-13.5,14,1.8):
  for y in [1.9,2.9]:
   F.box('bf-gold',(float(u),y,-11.89),(1.25,.76,.09));F.box('bf-art',(float(u),y,-11.83),(1.09,.61,.035))
 def chair(u,v,back):
  F.box('bf-wood',(u,.62,v),(.52,.1,.52),True)
  for dx in [-.21,.21]:
   for dz in [-.21,.21]:F.box('bf-wood',(u+dx,.36,v+dz),(.065,.52,.065))
  F.box('bf-wood',(u,1,v+back*.23),(.52,.72,.075))
 def table(u,v):
  F.box('bf-checkcloth',(u,1.19,v),(1.7,.055,1.05),True)
  for dx in [-.63,.63]:
   for dz in [-.35,.35]:F.box('bf-wood',(u+dx,.69,v+dz),(.09,1.0,.09))
  for dx in [-.48,.48]:
   chair(u+dx,v-.92,-1);chair(u+dx,v+.92,1)
  F.lathe('bf-cream',u,v,[(1.22,.15),(1.24,.19),(1.26,.19)],20)
  B.upface('bf-cream',[F.p(u+.19*math.cos(a),1.261,v+.19*math.sin(a)) for a in np.linspace(0,math.tau,20,endpoint=False)])
  F.box('bf-menu',(u+.5,1.38,v),(.19,.3,.04))
 for u in [-5,0,5,10]:
  for v in [-3.1,-7.3]:table(u,v)
 # Reference-supported booth type; placement is inferred, outside the circulation route.
 for v in [-3.1,-7.3]:
  F.box('bf-wood',(13.85,.50,v),(.9,.6,2.8),True)
  F.box('bf-upholstery',(13.75,.83,v),(.95,.18,2.65))
  F.box('bf-upholstery',(14.23,1.25,v),(.20,1.0,2.65))
  for z in [v-1.35,v+1.35]:F.box('bf-wood',(13.8,.9,z),(1.1,1.0,.12),True)
 # Host counter to the side of the entry, keeping a generous central route.
 F.box('bf-wood',(-13.5,.75,-2.6),(1.1,1.1,1.9),True);F.box('bf-gold',(-13.5,1.33,-2.6),(1.2,.08,2))
 for u in [-9,0,9]:
  F.tube('bf-gold',(u,4.6,-6),(u,3.4,-6),.025,10)
  for a in np.linspace(0,math.tau,8,endpoint=False):
   x=u+.55*math.cos(a);z=-6+.55*math.sin(a);F.tube('bf-gold',(u,3.4,-6),(x,3.5,z),.025,8);F.lathe('bf-lamp',x,z,[(3.45,.1),(3.68,.18),(3.75,.08)],12)
 lights=[dict(p=F.p(u,3.3,-6),color=0xffd6a0,power=12,range=11) for u in [-9,0,9]]
 route=[F.p(-10,.20,v) for v in [3,1,-1,-5,-10]]+[F.p(0,.20,-10),F.p(10,.20,-10)]
 return dict(key=KEY,name='Buca di Beppo Flamingo',center=[p.centroid.x,0,p.centroid.y],bounds=list(p.bounds),structural=True,exteriorOnly=False,portals=[door],zones=[dict(origin=F.p(0,.2,0),yaw=YAW+math.pi,width=30,depth=12.2,height=4.6)],lights=lights,hotelSources=[],routes=[dict(name='Entrance and public dining circulation',points=route)])
if __name__=='__main__':
 B=Meshes();m=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(m,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
