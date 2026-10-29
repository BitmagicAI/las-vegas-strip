"""Original mapped Hilton Garden Inn architecture; public room layout is fitted."""
from common import *
KEY='hilton-garden-city-center'; IDS=['way/494974483','way/495532040','way/495532043']
def build(B):
 B.property=KEY+'-exterior';B.source='hotel/'+KEY;B.detail=0
 p=footprint(IDS[0]);lobby=footprint(IDS[1]);poolhouse=footprint(IDS[2]);height=21.5
 B.shell(p,.02,height,'hg-ivory',roof=False);B.planar('hg-membrane',p,height)
 ring=list(p.exterior.coords)
 for a,b in zip(ring,ring[1:]):
  dx,dz=b[0]-a[0],b[1]-a[1];L=math.hypot(dx,dz);F=Frame(B,(a[0]+b[0])/2,(a[1]+b[1])/2,math.atan2(-dz,dx),y=0)
  F.box('hg-coping',(0,height,0),(L,.28,.35))
  if L<3:continue
  n=max(1,int(L/3.55));positions=np.linspace(-L/2+1.7,L/2-1.7,n) if n>1 else [0]
  for u in positions:
   u=float(u)
   for s in [-1,1]:
    F.box('hg-gray',(u,10.5,s*.055),(2.8,20.4,.10))
    for y in [2,5.45,8.9,12.35,15.8,19.25]:
     F.box('hg-frame',(u,y,s*.13),(2.05,2.16,.08));F.box('hg-glass',(u,y+.04,s*.19),(1.87,1.96,.03))
     F.box('hg-frame',(u,y+.04,s*.22),(.05,1.96,.02));F.box('hg-frame',(u,y+.04,s*.22),(1.87,.05,.02))
     F.box('hg-sill',(u,y-1.18,s*.16),(2.15,.2,.2))
    for y in [3.7,7.15,10.6,14.05,17.5]:F.box('hg-joint',(u,y,s*.12),(2.8,.025,.02))
  for s in [-1,1]:F.box('hg-dark',(0,20.9,s*.1),(L,.75,.15))
 # Public lobby uses its mapped outline. East entry into a fitted central hall.
 R=Frame(B,-804.43,1183.7,-math.pi/2,y=0)
 op=dict(p=R.p(0,.22,0),yaw=R.yaw,width=8,height=3.7)
 B.shell(lobby,.02,5.0,'hg-brick',roof=False,openings=[op]);B.planar('hg-membrane',lobby,5.0)
 # Lantern above the photographed tall lobby, proportion fitted to the mapped narrow north arm.
 Q=Frame(B,-814.4,1170.5,0,y=0)
 Q.box('hg-ivory',(0,5.8,0),(8.2,1.6,11));Q.box('hg-coping',(0,6.68,0),(8.6,.18,11.4))
 for u in [-3,-1,1,3]:
  for s in [-1,1]:Q.box('hg-glass',(u,5.95,s*5.52),(1.6,.9,.05))
 for v in [-4,-2,0,2,4]:
  for s in [-1,1]:Q.box('hg-glass',(s*4.12,5.95,v),(.05,.9,1.6))
 for shape in [lobby,poolhouse]:
  if shape is poolhouse:B.shell(shape,.02,3.3,'hg-brick',roof=False);B.planar('hg-dark',shape,3.3)
  ring=list(shape.exterior.coords)
  for a,b in zip(ring,ring[1:]):
   dx,dz=b[0]-a[0],b[1]-a[1];L=math.hypot(dx,dz);F=Frame(B,(a[0]+b[0])/2,(a[1]+b[1])/2,math.atan2(-dz,dx),y=0)
   h=3.3 if shape is poolhouse else 5
   F.box('hg-dark',(0,h,0),(L,.22,.35))
   # Brick courses stop on the east lobby entry edge.
   x,_,z=F.p(0,0,0)
   if -806<x<-802 and 1178<z<1190:continue
   for y in np.arange(.2,h,.23):F.box('hg-mortar',(0,float(y),.045),(L,.012,.02))
   if L>5:
    for u in np.linspace(-L/2+1.3,L/2-1.3,max(1,int(L/3))):
     F.box('hg-frame',(float(u),1.75,.09),(1.85,2.5,.1));F.box('hg-glass',(float(u),1.75,.16),(1.65,2.3,.025))
 R.box('hg-dark',(0,3.97,-2),(9,.30,4.8))
 for u in [-4.1,4.1]:R.box('hg-stone',(u,1.9,-3.3),(.45,3.8,.45),True)
 for u in [-2.6,2.6]:R.box('hg-clear',(u,1.96,.03),(2.8,3.4,.035),True)
 for u in [-4,-1.2,1.2,4]:R.box('hg-frame',(u,1.96,.03),(.07,3.4,.12),True)
 R.box('hg-frame',(0,3.66,.03),(8,.08,.12))
 B.upface('hg-paving',[R.p(-1.5,.01,-5),R.p(1.5,.01,-5),R.p(1.5,.22,.2),R.p(-1.5,.22,.2)],True)
 S=Frame(B,-793,1221.1,0,y=0);S.text('Hilton Garden Inn',(0,20.7,.25),.63,'hg-sign',back=True)
 for x in [-823,-808,-790,-771]:
  F=Frame(B,x,1207,0,y=0);F.box('hg-equipment',(0,22.1,0),(3.2,1.2,2));F.box('hg-dark',(0,22.72,0),(2.8,.03,1.6))
 B.property=KEY+'-interior';B.source='interior/'+KEY;B.detail=1
 room=R.poly([(-4,.05),(4,.05),(4,17),(-4,17)])
 B.shell(room,.22,3.9,'hg-wall',roof=False,openings=[{k:v for k,v in op.items() if k!='yaw'}]);B.planar('hg-floor',room,.22,True);B.planar('hg-ceiling',room,3.9)
 # Plank joints and shallow ceiling coves retain clear circulation.
 for u in np.arange(-3.9,4,.24):R.box('hg-floor-joint',(float(u),.223,8.5),(.006,.004,16.8))
 for v in np.arange(.2,17,1.6):
  for u in np.arange(-3.9,4,.48):R.box('hg-floor-joint',(float(u),.223,float(v)),(.24,.004,.006))
 for u in [-3.7,3.7]:
  R.box('hg-ceiling',(u,3.7,8.5),(.6,.3,17));R.box('hg-wood',(u,3.53,8.5),(.58,.025,17))
 for v in [1.5,10.5]:
  R.box('hg-stone',(3.72,1.15,v),(.3,1.86,.48))
  for y in np.arange(2.12,3.5,.10):R.box('hg-wood',(3.72,float(y),v),(.3,.035,.48))
 # Reception has two countertop heights, timber surround and original faceted relief.
 R.box('hg-wood',(-1.9,2.1,14.8),(3.8,3.7,.18));R.box('hg-wood',(-1.9,3.72,13.4),(4,.20,3))
 R.box('hg-stone',(-1.9,.95,12.7),(3.4,1.46,.8),True);R.box('hg-counter',(-1.9,1.72,12.7),(3.6,.09,.96))
 R.box('hg-stone',(.4,.7,12.7),(1.1,.96,.8),True);R.box('hg-counter',(.4,1.22,12.7),(1.25,.09,.96))
 for u in np.arange(-3.6,-.1,.35):
  for y in np.arange(.6,3.5,.35):R.box('hg-relief',(float(u),float(y),14.68),(.33,.33,.10 if int((u+4)*3+y*3)%2 else .18))
 for u in [-3,-1.8,-.6]:
  R.box('hg-wood',(u,2.4,14.48),(.8,1.05,.04));R.box('hg-art',(u,2.4,14.44),(.68,.93,.03));R.box('hg-teal',(u+.12,2.55,14.41),(.18,.42,.015))
 R.box('hg-frame',(-2,1.93,12.85),(.5,.32,.08))
 # Public lounge, original furniture derived from visible colors/types rather than private plan.
 for u,v in [(-2.9,4),(-2.9,7)]:
  R.box('hg-seat',(u,.49,v),(1.5,.26,2.1),True);R.box('hg-seat',(u-.55,1.06,v),(.32,.7,2.1))
  for side in [-1,1]:
   R.box('hg-seat',(u,.91,v+side*.96),(1.5,.6,.20))
   R.box('hg-seat',(u+.08,.71,v+side*.43),(1.15,.19,.83))
   for du in [-.5,.5]:R.box('hg-dark',(u+du,.3,v+side*.8),(.07,.16,.07))
  for off in [-.68,.68]:R.box('hg-orange',(u-.27,1.0,v+off),(.32,.46,.43))
 for v in [4,7]:
  R.box('hg-wood',(-.7,.65,v),(1.2,.08,1.0));R.box('hg-dark',(-.7,.43,v),(.55,.44,.55),True)
  R.lathe('hg-teal',.8,v,[(.22,0),(.22,.32),(.7,.32),(.74,.29),(.74,0)],24)
 R.box('hg-stone',(3.72,1.8,7),(.30,3.16,3));R.box('hg-dark',(3.54,.95,7),(.04,.65,1.8))
 for u in [-2,0,2]:
  for v in [2,6,10,15]:R.box('hg-lamp',(u,3.88,v),(.16,.02,.16))
 door=dict(p=R.p(0,.22,0),yaw=R.yaw,width=2.4,height=3.4,name='Hilton Garden Inn lobby',venue=KEY)
 return dict(key=KEY,name='Hilton Garden Inn City Center',center=[-811,0,1184],bounds=list(unary_union([p,lobby,poolhouse]).bounds),structural=True,hotelSources=[],exteriorOnly=False,portals=[door],zones=[dict(origin=R.p(0,.22,0),yaw=R.yaw,width=8.2,depth=17.2,height=4)],lights=[dict(p=R.p(u,3.5,v),color=0xffefd8,power=4,range=8) for u,v in [(-2,3),(2,3),(-2,11),(2,11)]],routes=[dict(name='Arrival to reception',points=[R.p(0,.22,v) for v in [-8,-5,-1,1,5,9,11]]),dict(name='Lounge approach',points=[R.p(u,.22,8.7) for u in [0,-1,-2]])])
if __name__=='__main__':
 B=Meshes();m=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(m,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
