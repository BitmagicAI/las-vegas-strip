"""Original shared industrial exterior and photo-supported gym; tenant layout inferred."""
from common import *
from shapely.geometry.polygon import orient
KEY='martinez-boxing'
def build(B):
 p=orient(footprint('way/464695953'),sign=1);F=Frame(B,160.35,-2585.15,1.078,y=0)
 B.property=KEY+'-exterior';B.source='industrial/'+KEY;B.detail=0
 door=dict(p=F.p(6,.65,0),yaw=F.yaw,width=2.4,height=3.2,name='Boxing gym entrance',venue=KEY)
 B.shell(p,0,5.5,'mb-stucco',openings=[door],roof=False);B.planar('mb-membrane',p,5.48)
 # Front tenant division follows the visible dark gym / blue tile shop, not the full OSM envelope.
 for lo,hi,mat in [(-15,-4,'mb-blue'),(-4,15,'mb-charcoal')]:
  if mat=='mb-charcoal':
   for a,b in [(lo,4.8),(7.2,hi)]:F.box(mat,((a+b)/2,2.75,-.055),(b-a,5.5,.11))
   F.box(mat,(6,4.7,-.055),(2.4,1.6,.11));F.box(mat,(6,.28,-.055),(2.4,.56,.11))
  else:F.box(mat,((lo+hi)/2,2.75,-.055),(hi-lo,5.5,.11))
 F.text('MARTINEZ',(6,4.25,-.15),.55,'mb-letter');F.text('LEGACY BOXING',(6,3.96,-.15),.27,'mb-letter');F.text('2800',(14,4.85,-.15),.38,'mb-letter')
 F.text('MOROCCAN MOSAIC',(-9.5,4.4,-.15),.24,'mb-dark');F.text('& TILE HOUSE',(-9.5,4.05,-.15),.24,'mb-dark')
 for u in [-1.8,13.1]:
  F.box('mb-door',(u,1.85,-.14),(1.1,2.4,.08),True);F.box('mb-alloy',(u-.35,1.8,-.2),(.08,.04,.06))
 for u in [-.6,.6]:
  F.box('mb-clear',(6+u,2.25,.025),(1.16,3.18,.025))
  for dx in [-.59,.59]:F.box('mb-alloy',(6+u+dx,2.25,-.04),(.045,3.2,.1))
  for yy in [.65,2.9,3.85]:F.box('mb-alloy',(6+u,yy,-.04),(1.2,.045,.1))
  F.tube('mb-alloy',(6+u*.3,1.5,-.12),(6+u*.3,2.05,-.12),.025,10)
 for u in [-10.5,-8.5]:
  F.box('mb-glass',(u,2,-.14),(1.85,2.8,.05),True)
  for du in [-.95,0,.95]:F.box('mb-alloy',(u+du,2,-.2),(.055,2.9,.09))
  for yy in [.55,2.85,3.45]:F.box('mb-alloy',(u,yy,-.2),(1.9,.055,.09))
 # Raised approach, central landing and accessible sloping run. No city pavement edits.
 F.box('mb-concrete',(5.5,.325,-1.35),(19,.65,2.7),True)
 B.upface('mb-concrete',[F.p(-3.5,0,-4.5),F.p(8.5,.65,-4.5),F.p(8.5,.65,-2.7),F.p(-3.5,0,-2.7)],True)
 F.box('mb-concrete',(10.5,.325,-3.6),(4,.65,1.8),True)
 for v in [-4.5,-2.7]:
  for u in np.arange(-3.5,8.6,2):
   y=(u+3.5)/12*.65;F.tube('mb-alloy',(float(u),y,v),(float(u),y+1,v),.035,10)
  F.tube('mb-alloy',(-3.5,1,v),(8.5,1.65,v),.035,10)
  F.tube('mb-alloy',(-3.5,.55,v),(8.5,1.2,v),.025,8)
 for u in [-3.5,0,3,6,9,12,15]:
  if 8<u<13:continue
  F.tube('mb-alloy',(u,.65,-2.65),(u,1.65,-2.65),.035,10)
 for lo,hi in [(-3.5,0),(0,3),(3,6),(6,8.5),(12.5,15)]:
  F.path('mb-rope',[(lo,1.6,-2.65),((lo+hi)/2,1.42,-2.65),(hi,1.6,-2.65)],.018,8)
 # Coping and roof equipment across the preserved irregular shell.
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  R=Frame(B,(a[0]+b[0])/2,(a[1]+b[1])/2,math.atan2(a[1]-b[1],b[0]-a[0]),y=0);R.box('mb-coping',(0,5.55,0),(math.dist(a,b)+.03,.12,.28))
 for x,z in [(181,-2580),(197,-2584),(183,-2608),(204,-2620),(193,-2630)]:
  B.box('mb-equipment',(x,6,z),(2,.9,2.8));B.lathe('mb-dark',(x,z),[(6.46,.55),(6.5,.55)],16)
  for dz in np.arange(-1.1,1.2,.2):B.box('mb-alloy',(x+1.015,6,z+float(dz)),(.025,.5,.07))
 # Public training room, inferred 18 x 25 metres within the visible gym bay.
 B.property=KEY+'-interior';B.source='public/'+KEY
 room=Polygon([(F.p(u,0,v)[0],F.p(u,0,v)[2])for u,v in [(-3,.2),(15,.2),(15,25),(-3,25)]])
 room=room.intersection(p.buffer(-.05))
 F.box('mb-concrete',(6,.575,.1),(2.4,.15,.5),True)
 B.planar('mb-rubber',room,.65,True);B.shell(room,.65,5.1,'mb-cream',openings=[door],roof=False,solid=True)
 for t in triangles(room):
  pts=[(x,5.1,z)for x,z in list(t.exterior.coords)[:-1]];ar=np.array(pts);B.face('mb-ceiling',pts if np.cross(ar[1]-ar[0],ar[2]-ar[0])[1]<0 else list(reversed(pts)))
 for v in [4,9,14,19,24]:
  F.box('mb-steel',(6,4.8,v),(17.8,.3,.14))
  F.box('mb-lamp',(6,4.5,v),(6,.05,.14))
  for u in [3,9]:F.tube('mb-steel',(u,4.5,v),(u,5,v),.012,8)
 # Ring with separate deck, corner pads, tensioned ropes, steps and apron.
 F.box('mb-apron',(6,1.1,12),(7.6,.9,7.6),True);F.box('mb-mat',(6,1.58,12),(7.5,.05,7.5),True)
 for u in [2.3,9.7]:
  for v in [8.3,15.7]:
   F.tube('mb-steel',(u,.65,v),(u,3.05,v),.065,12)
   F.box('mb-red' if u<6 else 'mb-blue',(u,2.35,v),(.24,1.25,.24))
 for y,mat in [(1.9,'mb-blue'),(2.25,'mb-letter'),(2.6,'mb-red'),(2.95,'mb-blue')]:
  for v in [8.35,15.65]:F.tube(mat,(2.35,y,v),(9.65,y,v),.027,10)
  for u in [2.35,9.65]:F.tube(mat,(u,y,8.35),(u,y,15.65),.027,10)
 for i in range(4):F.box('mb-concrete',(6,.65+(i+1)*.115,7.1+i*.3),(1.1,(i+1)*.23,.32),True)
 # Photo-supported trophy/belt wall; abstract original decorations, no portrait textures.
 def plaque(mat,u,y,v,ry,rz,n=32):
  pts=[F.p(u,y+ry*math.sin(j*math.tau/n),v+rz*math.cos(j*math.tau/n))for j in range(n)]
  B.face(mat,pts);B.face(mat,list(reversed(pts)))
 for row,y in enumerate([1.85,2.55,3.25]):
  for j,v in enumerate([5,7,9,11,13,15,17,19,21]):
   mat=['mb-dark','mb-red','mb-blue'][(row+j)%3]
   pts=[F.p(14.86,y+dy,v+dz)for dz,dy in [(-.8,-.09),(-.45,-.12),(-.28,-.24),(.28,-.24),(.45,-.12),(.8,-.09),(.8,.09),(.45,.12),(.28,.24),(-.28,.24),(-.45,.12),(-.8,.09)]]
   B.face(mat,pts);B.face(mat,list(reversed(pts)))
   plaque('mb-gold',14.80,y,v,.23,.3);plaque('mb-dark',14.78,y,v,.17,.235);plaque('mb-gold',14.76,y,v,.14,.2)
   for dv in [-.48,.48]:plaque('mb-gold',14.79,y,v+dv,.105,.12,20)
   for dv in [-.7,.7]:
    for dy in [-.04,.04]:plaque('mb-alloy',14.78,y+dy,v+dv,.013,.013,8)
 F.box('mb-wood',(14.6,3.75,13),(.75,.1,19))
 for j,v in enumerate(np.arange(4.5,22,.85)):
  y=4.15+(j%3)*.14
  F.box('mb-dark',(14.55,3.86,float(v)),(.35,.15,.35));F.lathe('mb-gold',14.55,float(v),[(3.94,.13),(4,.07),(y,.045),(y+.04,.1),(y+.12,.16),(y+.2,.18),(y+.22,.18)],16)
  for dv in [-1,1]:F.path('mb-gold',[(14.55,y+.07,float(v)+dv*.11),(14.55,y+.09,float(v)+dv*.25),(14.55,y+.2,float(v)+dv*.25),(14.55,y+.2,float(v)+dv*.17)],.018,8)
 # Low mirror panels and framed abstract memorabilia, without source photography.
 for v in [6,10,14,18]:
  F.box('mb-alloy',(14.86,1.08,v),(.08,.65,3.7));F.box('mb-mirror',(14.80,1.08,v),(.025,.58,3.6))
 for v in [4,8,12,16,20]:
  F.box('mb-dark',(-2.87,2.7,v),(.08,1.1,.8));F.box('mb-letter',(-2.81,2.7,v),(.035,.98,.68))
  for k in range(4):F.box('mb-red' if k==0 else 'mb-dark',(-2.78,2.98-k*.16,v),(.025,.06,.48))
 # Hanging bags with seams and suspension chains, away from central circulation.
 for v in [5,10,15,20]:
  F.lathe('mb-bag',-.5,v,[(1,.28),(1.1,.32),(2.5,.32),(2.65,.23)],20)
  for du in [-.2,.2]:F.tube('mb-alloy',(-.5+du,2.6,v),(-.5,4.8,v),.012,8)
  for y in [1.12,2.45]:F.lathe('mb-dark',-.5,v,[(y,.326),(y+.05,.326)],20)
 F.box('mb-dark',(6,4,.25),(1,.24,.04));F.text('EXIT',(6,3.92,.3),.18,'mb-red',True)
 routes=[dict(name='Ramp and gym entry',points=[F.p(u,y,v)for u,y,v in [(-4.5,0,-3.6),(-3.5,0,-3.6),(2.5,.325,-3.6),(8.5,.65,-3.6),(10.5,.65,-3.6),(10.5,.65,-1.4),(6,.65,-1.4),(6,.65,1.5),(6,.65,5)]]),dict(name='Training aisle',points=[F.p(u,.65,v)for u,v in [(6,5),(11.5,5),(11.5,12),(11.5,20),(6,20)]])]
 return dict(key=KEY,name='Martinez Boxing',center=[187,0,-2599],bounds=list(p.buffer(8).bounds),structural=True,hotelSources=[],exteriorOnly=False,portals=[door],zones=[dict(origin=F.p(6,.65,.2),yaw=F.yaw,width=18,depth=24.8,height=4.5)],lights=[dict(p=F.p(u,4.5,v),color=0xfff1db,power=4,range=12)for u,v in [(2,5),(10,5),(2,18),(10,18)]],routes=routes)
if __name__=='__main__':
 B=Meshes();m=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(m,indent=2)+'\n');print(KEY,sum(len(g['faces'])for g in B.groups.values()),'triangles')
