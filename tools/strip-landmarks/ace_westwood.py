"""Original ACE exterior. October 2024 street geometry; current owner signage.
Mapped L footprint retained. Heights and unseen service elevations inferred.
No interior access is asserted for this operating automotive workshop.
"""
from common import *
from shapely.geometry.polygon import orient
KEY='ace-westwood'
COLORS={'ace-stucco':'9c9d99','ace-stone':'727570','ace-stone-light':'828680','ace-stone-dark':'6d726d','ace-mortar':'b8b9b0','ace-coping':'333a39','ace-roof':'a6a89e','ace-glass':'1b292c','ace-metal':'484d4b','ace-red':'b92e32','ace-white':'e4e3db','ace-rubber':'292d2c','ace-door':'6b7270'}
def build(B):
 B.property=KEY+'-exterior';B.source='commercial/'+KEY;B.detail=0
 p=orient(footprint('way/464694095'),sign=1)
 coords=list(p.exterior.coords);panels=[]
 for a,b in zip(coords,coords[1:]):
  dx,dz=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dz)
  panels.append((Frame(B,(a[0]+b[0])/2,(a[1]+b[1])/2,math.atan2(-dz,dx),y=0),length))
 # Keep the entrance on the recessed court edge, clear of the north corner pier.
 front=min(range(len(panels)),key=lambda i:panels[i][0].z)
 court=min(range(len(panels)),key=lambda i:abs(panels[i][1]-10.6))
 back=min(range(len(panels)),key=lambda i:abs(panels[i][1]-15.3))
 R=panels[court][0];dooru=2.9
 cuts=[dict(p=R.p(dooru,.12,0),yaw=R.yaw,width=1.05,height=2.35)]
 cuts.append(dict(p=panels[back][0].p(0,.12,0),yaw=panels[back][0].yaw,width=1.15,height=2.35))
 B.shell(p,0,3.95,'ace-stucco',openings=cuts,roof=False);B.planar('ace-roof',p,3.83)
 for i,(F,length) in enumerate(panels):
  F.box('ace-coping',(0,4.02,0),(length+.08,.18,.28),True)
  # Low masonry plinth and vertical piers, relief joints rather than flat stripes.
  spans=[(-length/2,length/2)]
  if i==court:spans=[(-length/2,dooru-.59),(dooru+.59,length/2)]
  if i==back:spans=[(-length/2,-.62),(.62,length/2)]
  for a,b in spans:
   F.box('ace-mortar',((a+b)/2,.34,-.045),(b-a,.68,.08))
   for row in range(3):
    x=a
    while x<b-.03:
     w=min(.48 if row%2==0 else .36,b-x)
     F.box(['ace-stone','ace-stone-dark','ace-stone-light'][(row+int((x-a)*4))%3],(x+w/2,.11+row*.22,-.095),(max(.01,w-.018),.202,.075));x+=w
  for u in [-length/2+.28,length/2-.28]:
   F.box('ace-mortar',(u,2.04,-.05),(.56,3.68,.12))
   for row in range(17):
    for col in range(2):F.box(['ace-stone-light','ace-stone','ace-stone-dark'][(row+col)%3],(u-.135+col*.27,.35+row*.21,-.125),(.253,.19,.09))
 F=panels[front][0]
 F.text('2600',(.6,2.65,-.12),.43,'ace-coping')
 # Current ACE sign replaces the older Protection Plus branding in street imagery.
 for u in [-2.2,2.2]:F.box('ace-metal',(u,4.26,.18),(.08,1.0,.08))
 F.box('ace-coping',(0,4.55,.1),(6.3,1.04,.16))
 F.box('ace-red',(-2.79,4.55,-.001),(.15,.87,.03))
 F.text('AUTO COLLISION',(.15,4.66,-.005),.29,'ace-white')
 F.text('EXPERTS',(.15,4.28,-.005),.32,'ace-white')
 R.box('ace-glass',(dooru,1.25,.13),(1.05,2.55,.06),True)
 for u in [dooru-.54,dooru+.54]:R.box('ace-metal',(u,1.28,.06),(.06,2.55,.1))
 for yy in [.12,2.5]:R.box('ace-metal',(dooru,yy,.06),(1.14,.07,.1))
 R.tube('ace-metal',(dooru+.35,1,-.03),(dooru+.35,1.5,-.03),.025,8)
 T=panels[back][0]
 T.box('ace-door',(0,1.25,.12),(1.15,2.5,.06),True)
 for u in [-.6,.6]:T.box('ace-metal',(u,1.29,.04),(.065,2.55,.1))
 T.box('ace-metal',(0,2.55,.04),(1.25,.09,.1))
 T.box('ace-coping',(0,2.8,-.32),(1.8,.12,.85))
 T.text('2600',(0,3.06,-.08),.28,'ace-coping')
 T.tube('ace-metal',(.42,1.05,-.04),(.42,1.42,-.04),.024,8)
 # Meter, conduit, high ventilation grille and discreet security light.
 for u in [-2.9,-1.7]:
  R.box('ace-metal',(u,2.0,-.14),(.42,.65,.22));R.tube('ace-metal',(u,.2,-.14),(u,3.5,-.14),.024,8)
 R.box('ace-coping',(-.3,3.15,-.07),(1.25,.32,.09))
 for n in range(5):R.box('ace-metal',(-.3,3.02+n*.06,-.13),(1.21,.025,.08))
 R.box('ace-metal',(dooru,2.96,-.18),(.3,.16,.3))
 # Inferred modest roof plant stays wholly inside the mapped footprint.
 F0=Frame(B,248,-3029,0,y=0)
 F0.box('ace-metal',(0,4.12,0),(1.6,.48,1.2));F0.box('ace-coping',(0,4.38,0),(1.7,.06,1.3))
 routes=[dict(name='Court entrance approach',points=[R.p(dooru,0,-3),R.p(dooru,0,-1)])]
 return dict(key=KEY,name='Auto Collision Experts Westwood',center=[247,2,-3036],bounds=list(p.buffer(2).bounds),structural=True,hotelSources=[],exteriorOnly=True,portals=[],zones=[],lights=[],routes=routes)
if __name__=='__main__':
 B=Meshes();m=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(m,indent=2)+'\n');print(KEY,sum(len(g['faces'])for g in B.groups.values()),'triangles')
