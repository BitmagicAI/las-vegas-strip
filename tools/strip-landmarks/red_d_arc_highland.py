"""Original 2620 Highland industrial frontage from January 2026 Street View.
Mapped outline retained; heights, concealed elevations and roof equipment inferred.
"""
from common import *
from shapely.geometry.polygon import orient
KEY='red-d-arc-highland'
def build(B):
 B.property=KEY+'-exterior';B.source='commercial/'+KEY;B.detail=0
 p=orient(footprint('way/464694105'),sign=1)
 F=Frame(B,286.628,-2888.1395,1.02055,y=0)
 # Each frontage panel follows its own mapped edge, including the recessed north bay.
 edges=[((278.674,-2875.171),(287.496,-2891.947)),((289.393,-2890.9),(294.582,-2901.108))]
 panels=[]
 for a,b in edges:
  dx,dz=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dz)
  panels.append((Frame(B,(a[0]+b[0])/2,(a[1]+b[1])/2,math.atan2(-dz,dx),y=0),length))
 features=[(0,-5.5,2.15,'window'),(0,0,2.15,'window'),(0,6.3,2.15,'window'),(1,3.0,2.15,'window'),(1,-3.2,1.3,'door')]
 cuts=[]
 for edge,u,w,kind in features:
  R=panels[edge][0];lo=.9 if kind=='window' else .15;h=1.65 if kind=='window' else 2.4
  cuts.append(dict(p=R.p(u,lo,0),yaw=R.yaw,width=w,height=h))
 B.shell(p,0,4.35,'ra-stucco',openings=cuts,roof=False);B.planar('ra-membrane',p,4.28)
 for edge,u,w,kind in features:
  R=panels[edge][0];lo=.9 if kind=='window' else .15;h=1.65 if kind=='window' else 2.4
  R.box('ra-glass',(u,lo+h/2-.025,.14),(w,h+.25,.04),True)
  for du in [-w/2,w/2]:R.box('ra-alloy',(u+du,lo+h/2,.09),(.055,h+.1,.075))
  for yy in [lo,lo+h]:R.box('ra-alloy',(u,yy,.09),(w+.13,.07,.1))
  if kind=='window':
   R.box('ra-alloy',(u,lo+h/2,.09),(.055,h,.075));R.box('ra-coping',(u,.83,-.05),(w+.2,.12,.4))
  else:
   R.tube('ra-alloy',(u+.45,1,-.04),(u+.45,1.45,-.04),.022,8)
   R.text('2620',(u,2.85,-.06),.32,'ra-charcoal')
 # Fine horizontal block joints are face-aligned and stop at openings.
 for edge,(R,length) in enumerate(panels):
  for row in range(1,10):
   yy=row*.36;spans=[(-length/2+.05,length/2-.05)]
   for ei,u,w,kind in features:
    if ei!=edge or yy>=2.65 or (kind=='window' and yy<=.8):continue
    lo,hi=u-w/2-.1,u+w/2+.1
    spans=[t for a,b in spans for t in ([(a,min(b,lo))] if a<lo else [])+([(max(a,hi),b)] if b>hi else []) if t[1]-t[0]>.01]
   for a,b in spans:R.box('ra-joint',((a+b)/2,yy,-.012),(b-a,.012,.012))
 # A single broad cantilever follows the frontage; no roadside geometry is changed.
 F.box('ra-soffit',(0,4.0,-.55),(30.5,.20,3.0),True)
 F.box('ra-coping',(0,4.2,-1.95),(30.6,.25,.22),True)
 F.box('ra-coping',(0,4.36,-.55),(30.7,.09,3.2))
 for u in [-15.2,15.2]:F.box('ra-coping',(u,4.2,-.55),(.2,.25,3.0))
 R=panels[1][0]
 R.box('ra-sign',(-.7,3.35,-.07),(10.3,.9,.06))
 R.text('Red-D-Arc', (1.9,3.17,-.12),.51,'ra-blue')
 R.text('Welderentals',(-2.8,3.17,-.12),.45,'ra-red')
 # Finish the real skewed perimeter instead of imposing a rectangular side wall.
 coords=list(p.exterior.coords)
 for a,b in zip(coords,coords[1:]):
  dx,dz=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dz)
  R=Frame(B,(a[0]+b[0])/2,(a[1]+b[1])/2,math.atan2(-dz,dx),y=0)
  R.box('ra-coping',(0,4.4,0),(length,.12,.25))
 for u,v in [(-8,9),(2,12),(9,18)]:
  F.box('ra-curb',(u,4.48,v),(2.4,.36,1.8));F.box('ra-equipment',(u,4.94,v),(2.15,.6,1.6))
  for du in [-.5,.5]:B.lathe('ra-charcoal',(F.p(u+du,0,v)[0],F.p(u+du,0,v)[2]),[(5.25,.34),(5.3,.34)],16)
  for q in range(6):F.box('ra-alloy',(u-1.08,4.93,v-.6+q*.22),(.025,.4,.04))
 for u in [-10,10]:
  F.box('ra-service',(u,1.25,25.8),(1.2,2.5,.1),True)
  F.box('ra-equipment',(u-1.1,1.5,25.8),(.55,.8,.2))
 F.box('ra-paving',(0,.035,-.55),(30,.07,.9),True)
 routes=[dict(name='Frontage beneath canopy',points=[F.p(u,0,-2.1)for u in [-14,-7,0,7,14]]),dict(name='Public entrance approach',points=[F.p(0,0,-3.2),F.p(0,0,-2.1),F.p(5.3,0,-2.1),panels[1][0].p(-3.2,0,-.8)])]
 return dict(key=KEY,name='Red-D-Arc Highland',center=F.p(0,0,12),bounds=list(p.buffer(8).bounds),structural=True,hotelSources=[],exteriorOnly=True,portals=[],zones=[],lights=[],routes=routes)
if __name__=='__main__':
 B=Meshes();m=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(m,indent=2)+'\n');print(KEY,sum(len(g['faces'])for g in B.groups.values()),'triangles')
