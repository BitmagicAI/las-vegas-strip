"""Original 2320 South Rancho envelope from dated Street View and mapped footprint.
Recess heights and unseen bays estimated. No claim of surveyed interior geometry.
"""
from common import *
from shapely.geometry.polygon import orient
KEY='rancho-2320'
def build(B):
 B.property=KEY+'-exterior';B.source='office/'+KEY;B.detail=0
 p=orient(footprint('way/384612530'),sign=1)
 W=Frame(B,127.25,-3296.4,math.pi/2-.023,y=0)
 E=Frame(B,174.85,-3295.2,-math.pi/2-.023,y=0)
 N=Frame(B,151,-3308.35,-.023,y=0)
 S=Frame(B,150.4,-3282.55,math.pi-.023,y=0)
 frames=[W,E,N,S];cuts=[]
 # Use real recesses with backs and jambs, not glazed planes over solid walls.
 bays=[]
 for side,R in enumerate(frames):
  us=[-9,-4,4,9]if side<2 else[-21,-8,8,21]
  for u in us:
   for y,h in [(.8,2.7),(4.9,2.45)]:
    door=side==0 and u==-4 and y<1
    balcony=side==0 and u==-4 and y>4
    yy=0 if door else 4.5 if balcony else y;hh=3.5 if door else 2.85 if balcony else h
    width=2.1 if door or balcony else 4.5 if side>=2 and abs(u)<10 else 3.65
    cuts.append(dict(p=R.p(u,yy,0),yaw=R.yaw,width=width,height=hh));bays.append((side,R,u,yy,width,hh,door,balcony))
 B.shell(p,0,8.7,'r23-stucco',openings=cuts,roof=False)
 B.planar('r23-membrane',p,8.45)
 for side,R,u,y,w,h,door,balcony in bays:
  d=1.15 if door or balcony else .55
  # The masking helper leaves a small extra margin; jamb slabs bridge the exact cut.
  for du in [-w/2,w/2]:R.box('r23-reveal',(u+du,y+h/2,.2),(.12,h+.3,d+.8))
  for yy in [y-.12,y+h+.08]:R.box('r23-reveal',(u,yy,.2),(w+.12,.14,d+.8))
  if balcony:
   R.box('r23-floor',(u,4.5,.42),(w,.18,1.9),True)
   for yy in np.arange(4.75,5.65,.17):R.tube('r23-alloy',(u-w/2,float(yy),-.45),(u+w/2,float(yy),-.45),.025,8)
   for du in [-w/2,0,w/2]:R.tube('r23-alloy',(u+du,4.6,-.45),(u+du,5.7,-.45),.035,8)
  blank=side==0 and (u>0 or(u==-4 and y<1))and not door
  mat='r23-infill'if blank else'r23-glass'
  R.box(mat,(u,y+h/2,d),(w,h,.08),True)
  if not blank:
   for du in [-w/2,-w/6,w/6,w/2]:R.box('r23-mullion',(u+du,y+h/2,d-.06),(.045,h,.05))
   for yy in [y+.08,y+.48,y+h-.04]:R.box('r23-mullion',(u,yy,d-.06),(w,.045,.05))
   if door:
    for du in [-.12,.12]:R.tube('r23-alloy',(u+du,1,d-.15),(u+du,1.5,d-.15),.022,8)
 # Paired tall entry fins with narrow central vertical reveal.
 for R in [W,E]:
  for du in [-1.4,1.4]:
   R.box('r23-pier',(du,4.85,-.32),(2.55,9.7,.72),True)
   for yy in np.arange(.6,9.5,.6):R.box('r23-joint',(du,float(yy),-.69),(2.55,.012,.018))
   for yy in np.arange(.6,9.5,1.2):R.box('r23-joint',(du,.3+float(yy),-.70),(.012,.6,.018))
  R.text('2320',(8.5,7.6,-.12),.7,'r23-dark')
 # North/south projecting piers follow mapped projections instead of stretching an entire box.
 for R in [N,S]:
  for u in [-15.2,0,15.3]:
   width=7.15 if u==0 else 5.8
   R.box('r23-pier',(u,4.65,-.35),(width,9.3,.9),True)
   R.box('r23-coping',(u,9.32,-.35),(width+.05,.1,1))
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  L=math.dist(a,b);R=Frame(B,(a[0]+b[0])/2,(a[1]+b[1])/2,math.atan2(a[1]-b[1],b[0]-a[0]),y=0)
  R.box('r23-coping',(0,8.73,0),(L+.025,.1,.2))
 # HVAC array from aerial; visible fan grilles and simple curb stands.
 for x,z in [(136,-3304),(136,-3297),(136,-3287),(164,-3303),(164,-3297),(164,-3287),(151,-3297)]:
  B.box('r23-curb',(x,8.6,z),(2.8,.3,2.2));B.box('r23-equipment',(x,9.1,z),(2.5,.85,1.9))
  for dx in [-.65,.65]:
   B.lathe('r23-dark',(x+dx,z),[(9.53,.36),(9.57,.36)],16)
   for dz in np.arange(-.3,.31,.1):B.box('r23-alloy',(x+dx,9.59,z+float(dz)),(.6,.02,.02))
 # Local west entry path and side ramp; inferred flat datum, no road edits.
 W.box('r23-paving',(-4,.06,-4.6),(2.7,.12,8.2),True)
 B.upface('r23-paving',[W.p(-5.35,0,-9.3),W.p(-2.65,0,-9.3),W.p(-2.65,.12,-8.7),W.p(-5.35,.12,-8.7)],True)
 for u in [-11.7,11.7]:
  W.box('r23-block',(u,.32,-1.6),(2,.64,3.4),True)
  for yy in [.8,1.1,1.4]:W.tube('r23-alloy',(u-1,yy,-3.25),(u+1,yy,-3.25),.025,8)
  for du in [-1,0,1]:W.tube('r23-alloy',(u+du,.65,-3.25),(u+du,1.45,-3.25),.03,8)
 # Desert beds and individual shrubs, stone chips, not solid green blocks.
 for u in [-9,-.5,4.7,9]:
  W.box('r23-gravel',(u,.025,-4),(3.6,.05,4.1))
  for j in range(7):
   a=j*2.399;xx=u+.48*math.cos(a);zz=-4+.48*math.sin(a)
   B.sphere('r23-leaf',W.p(xx,.75+(j%3)*.1,zz),.48,10,6)
  for j in range(5):
   a=j*1.8;B.sphere('r23-rock',W.p(u+1.5*math.cos(a),.12,-4+1.5*math.sin(a)),.18,6,4)
 W.box('r23-bin',(-.7,.48,-1.6),(.65,.96,.65),True);W.box('r23-dark',(-.7,.98,-1.6),(.42,.04,.42))
 routes=[dict(name='West entry approach',points=[W.p(-4,0,-10),W.p(-4,0,-9.3),W.p(-4,.12,-8.5),W.p(-4,.12,-5),W.p(-4,.12,-1.4)]),dict(name='South perimeter approach',points=[[132,0,-3277],[141,0,-3277],[153,0,-3277],[165,0,-3277]])]
 return dict(key=KEY,name='2320 South Rancho offices',center=[151,0,-3296],bounds=[116,-3311,178,-3275],structural=True,hotelSources=[],exteriorOnly=True,portals=[],zones=[],lights=[],routes=routes)
if __name__=='__main__':
 B=Meshes();m=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(m,indent=2)+'\n');print(KEY,sum(len(g['faces'])for g in B.groups.values()),'triangles')
