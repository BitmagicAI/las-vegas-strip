"""Original shared 2640 Highland exterior, based on dated Jan 2021 frontage.
Tenant divisions, unseen service elevations and equipment dimensions are inferred.
No reference artwork or photographs are embedded in the asset.
"""
from common import *
from shapely.geometry.polygon import orient
KEY='chrome-gypsy'
def build(B):
 B.property=KEY+'-exterior';B.source='commercial/'+KEY;B.detail=0
 p=orient(footprint('way/464694106'),sign=1)
 F=Frame(B,263.3995,-2831.155,1.0686,y=0)
 # Three recessed tenant bays; north end only carries the documented tattoo identity.
 bays=[(-10,7.9),(-.1,8.5),(10,8.0)]
 cuts=[dict(p=F.p(u,.15,0),yaw=F.yaw,width=w,height=3.4)for u,w in bays]
 B.shell(p,0,4.9,'cg-stucco',openings=cuts,roof=False);B.planar('cg-membrane',p,4.75)
 for u,w in bays:
  F.box('cg-glass',(u,1.85,.35),(w,3.4,.035),True)
  F.box('cg-threshold',(u,.075,.15),(w,.15,.65),True)
  for du in [-w/2,-w/4,0,w/4,w/2]:F.box('cg-alloy',(u+du,1.85,.29),(.06,3.45,.08))
  for yy in [.15,2.55,3.55]:F.box('cg-alloy',(u,yy,.29),(w,.055,.08))
  # Recessed opaque glass is intentional until there is sufficient interior evidence.
  for du in [-.18,.18]:F.tube('cg-alloy',(u+du,1,.2),(u+du,1.5,.2),.023,8)
  for du in [-w/2,w/2]:F.box('cg-charcoal',(u+du,1.8,0),(.25,3.6,.7),True)
  F.box('cg-soffit',(u,3.6,.12),(w,.12,.7))
 for u,w in [(-14.5,1.0),(-5.2,1.65),(4.95,1.8),(14.55,.9)]:F.box('cg-charcoal',(u,1.8,-.09),(w,3.6,.24),True)
 F.box('cg-charcoal',(0,4.25,-.07),(30.15,1.3,.45),True)
 F.box('cg-coping',(0,4.94,-.08),(30.3,.1,.58))
 F.text('TATTOO',(10,3.88,-.33),.63,'cg-red')
 F.box('cg-sign',(10,4.72,-.32),(4.9,.3,.06));F.text('CHROME GYPSY',(10,4.61,-.37),.23,'cg-charcoal')
 F.text('2640',(-10,2.78,.23),.28,'cg-gold')
 F.text('CHROME GYPSY',(10,2.86,.23),.31,'cg-gold');F.text('TATTOO',(10,1.95,.23),.42,'cg-gold')
 # Abstract coloured lower window bands, original shapes rather than copied artwork.
 colors=['cg-red','cg-yellow','cg-blue','cg-teal','cg-pink']
 for i in range(29):
  u=6.15+i*.27
  if abs(u-10)<.65:continue
  F.box(colors[i%5],(u,.66,.26),(.20,.93,.018))
 for u in [-12,-5,3,12]:
  F.tube('cg-charcoal',(u,4.7,-.3),(u,4.7,-.73),.04,8)
  F.box('cg-charcoal',(u,4.65,-.75),(.3,.17,.23));F.box('cg-lamp',(u,4.56,-.75),(.24,.025,.16))
 # Finish all edges using their actual mapped orientation, retaining the skewed plan.
 coords=list(p.exterior.coords)
 for a,b in zip(coords,coords[1:]):
  dx,dz=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dz)
  R=Frame(B,(a[0]+b[0])/2,(a[1]+b[1])/2,math.atan2(-dz,dx),y=0)
  R.box('cg-coping',(0,4.94,0),(length,.1,.3))
 # Roof curbs, exhausts, ducts and wall-mounted service boxes inferred from aerial.
 for u,v in [(-9,8),(1,9),(10,8),(-7,17),(7,18)]:
  F.box('cg-curb',(u,4.92,v),(2.5,.34,1.9));F.box('cg-equipment',(u,5.4,v),(2.2,.65,1.6))
  for du in [-.55,.55]:B.lathe('cg-charcoal',(F.p(u+du,0,v)[0],F.p(u+du,0,v)[2]),[(5.74,.37),(5.8,.37)],16)
  for q in range(6):F.box('cg-alloy',(u-1.12,5.39,v-.6+q*.23),(.025,.4,.045))
 for u in [-12,12]:
  F.box('cg-service',(u,1.25,22.0),(1.1,2.5,.10),True)
  F.box('cg-equipment',(u-1.1,1.5,22.0),(.6,.85,.2))
 # Only local front landing; no road or parking replacement.
 F.box('cg-paving',(0,.035,-.48),(29.8,.07,.8),True)
 routes=[dict(name='Shared storefront approach',points=[F.p(u,0,-1.6)for u in [-14,-7,0,7,14]]),dict(name='Tattoo entry approach',points=[F.p(10,0,v)for v in [-7,-4,-1.6,-.8]])]
 return dict(key=KEY,name='2640 Highland shared storefront',center=F.p(0,0,11),bounds=list(p.buffer(8).bounds),structural=True,hotelSources=[],exteriorOnly=True,portals=[],zones=[],lights=[],routes=routes)
if __name__=='__main__':
 B=Meshes();m=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(m,indent=2)+'\n');print(KEY,sum(len(g['faces'])for g in B.groups.values()),'triangles')
