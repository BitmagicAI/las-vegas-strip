"""Original Starbucks cafe geometry from linked photo references; fitted plan."""
from common import *
KEY='starbucks-flamingo';IDS=['way/308291919'];YAW=.0178

def build(B):
 p=footprint(IDS[0]);F=Frame(B,1391,144.3,YAW,y=0)
 B.property=KEY+'-exterior';B.source='retail/'+KEY;B.detail=0
 door=dict(p=F.p(2,.22,0),yaw=YAW,width=2.2,height=2.6,name='Starbucks cafe entrance',venue=KEY)
 front=dict(p=F.p(2,.22,0),yaw=YAW,width=16.7,height=5.3)
 side=dict(p=[1401.6,.22,139],yaw=math.pi/2,width=8,height=5.3)
 B.shell(p,.02,6,'sb-stucco',roof=False,openings=[front,side]);B.planar('sb-membrane',p,5.9)
 F.box('sb-fascia',(0,5.85,.25),(22,.65,1.6));F.box('sb-stone',(-8.2,2.6,.15),(4.3,5.2,.25),True)
 # A real glazed curtain wall with clear entry opening and matched collision panes.
 for a,b in [(-6.3,.85),(3.15,10.3)]:
  F.box('sb-clear',((a+b)/2,2.8,0),(b-a,5.15,.035),True)
 F.box('sb-clear',(2,4.1,0),(2.2,2.5,.035),True)
 for u in np.arange(-6.3,10.5,1.4):
  F.box('sb-metal',(float(u),4.25 if abs(u-2)<1.1 else 3,.08),(.055,2.5 if abs(u-2)<1.1 else 5.5,.11))
 for y in [2.9,4.7,5.55]:F.box('sb-metal',(2,y,.08),(16.7,.065,.11))
 for u in [.85,3.15]:F.box('sb-metal',(u,1.6,.08),(.08,2.8,.12))
 R=Frame(B,1401.63,139,math.pi/2,y=0)
 R.box('sb-clear',(0,2.8,.05),(8,5.15,.035),True)
 for u in np.arange(-4,4.1,1.35):R.box('sb-metal',(float(u),2.9,.1),(.06,5.4,.1))
 for y in [.25,2.9,4.7,5.55]:R.box('sb-metal',(0,y,.1),(8.1,.06,.1))
 F.text('STARBUCKS',(5.0,5.72,1.1),.56,'sb-letter',back=True)
 F.text('340',(9.3,6.06,1.08),.24,'sb-black',back=True)
 # Original round green identity marker with wordmark, no copied image artwork.
 pts=[F.p(-8.2+1.0*math.cos(t),3.4+1.0*math.sin(t),.3) for t in np.linspace(0,math.tau,49)[:-1]]
 for i in range(48):B.face('sb-green',[F.p(-8.2,3.4,.3),pts[i],pts[(i+1)%48]])
 F.text('COFFEE',(-8.2,3.4,.34),.25,'sb-letter',back=True)
 B.upface('sb-paving',[F.p(.85,.22,0),F.p(3.15,.22,0),F.p(3.15,.12,2),F.p(.85,.12,2)],True)
 # East patio stays within immediate forecourt, leaving road untouched.
 E=Frame(B,1401.7,140,math.pi/2,y=.18)
 for a,b in [((-4,1),(-4,4)),((-4,4),(3,4)),((3,4),(3,1))]:E.rail(a,b)
 for u in [-2,1]:
  E.lathe('sb-black',u,2.5,[(0,.3),(.06,.3),(.07,.045),(.74,.045)],12);E.lathe('sb-wood',u,2.5,[(.74,.5),(.81,.5)],24)
  for v in [1.6,3.4]:E.box('sb-black',(u,.48,v),(.45,.08,.45),True)
 for u,v in [(-6,-8),(1,-8),(6,-8)]:
  F.box('sb-equipment',(u,6.42,v),(1.7,1,1.2))
  for yy in np.arange(6,6.8,.13):F.box('sb-black',(u,float(yy),v+.61),(1.4,.03,.025))
 # Public cafe, front seating and rear counter. Exact counter position is inferred.
 B.property=KEY+'-interior';B.source='interior/'+KEY;B.detail=1
 room=F.poly([(-9.5,-.1),(10.2,-.1),(10.2,-9),(-9.5,-9)]).intersection(p.buffer(-.15))
 B.shell(room,.22,5.6,'sb-wall',roof=False,openings=[front,side]);B.planar('sb-floor',room,.22,True);B.planar('sb-ceiling',room,5.6)
 F.box('sb-wood',(-3,.8,-6.8),(11,1.15,1.1),True);F.box('sb-stone',(-3,1.42,-6.8),(11.2,.11,1.25),True)
 # White vertical mosaic backsplash and wood framed menu panels.
 F.box('sb-tile',(-3,2.8,-8.82),(12,4.3,.05))
 for u,t in [(-7.7,'ESPRESSO'),(-5.8,'COFFEE'),(-3.9,'TEA'),(-2,'COLD BREW'),(-.1,'BAKERY'),(1.8,'FAVORITES')]:
  F.box('sb-wood',(u,3.2,-8.73),(1.75,1.2,.08));F.box('sb-paper',(u,3.2,-8.67),(1.62,1.07,.04));F.text(t,(u,3.52,-8.62),.115,'sb-black',back=True)
  for y in [3.27,3.08,2.89]:F.box('sb-ink',(u,y,-8.63),(1.3,.018,.015))
 F.box('sb-wood',(-5.5,.8,-8.05),(5.8,1.15,1.2),True)
 F.box('sb-steel',(-5.5,1.42,-8.05),(5.9,.11,1.3),True)
 for u in [-7,-4]:
  F.box('sb-steel',(u,1.75,-7.8),(1,.65,.55));F.box('sb-black',(u,1.85,-7.5),(.83,.3,.07))
  for dx in [-.25,.25]:F.tube('sb-steel',(u+dx,1.7,-7.45),(u+dx,1.53,-7.45),.035,8)
  F.box('sb-black',(u,1.48,-7.3),(1.1,.06,.45))
 # Glass pastry cabinet, open lower shelves, original pastries and drink containers.
 F.box('sb-black',(4,.65,-6.8),(2.2,.85,1.1),True)
 for y in [.4,.78,1.18]:F.box('sb-steel',(4,y,-6.8),(2.15,.05,1.05))
 F.box('sb-clear',(4,1.63,-6.25),(2.2,.85,.025));F.box('sb-clear',(4,2.06,-6.8),(2.2,.025,1.1))
 for u in [3,5]:F.box('sb-clear',(u,1.63,-6.8),(.025,.85,1.1))
 for u in [3.25,3.75,4.25,4.75]:
  F.lathe('sb-bread',u,-6.7,[(1.22,.17),(1.36,.15),(1.43,.08)],12)
  for y in [.45,.84]:F.lathe('sb-green',u,-6.5,[(y,.07),(y+.22,.07),(y+.25,.04)],10)
 # Tables and curved wood chair backs beside the tall windows.
 for u in [-6,-2,6]:
  for v in [-2,-4.5]:
   F.lathe('sb-black',u,v,[(.22,.32),(.27,.32),(.28,.045),(.92,.045)],16);F.lathe('sb-wood',u,v,[(.92,.58),(.98,.58)],28)
   for dx in [-.9,.9]:
    cx=u+dx;F.box('sb-wood',(cx,.65,v),(.48,.09,.5),True)
    for a in np.linspace(-.8,.8,9)[:-1]:
     a2=a+.2
     B.face('sb-wood',[F.p(cx+math.copysign(.28*math.cos(a),dx),.82,v+.35*math.sin(a)),F.p(cx+math.copysign(.28*math.cos(a2),dx),.82,v+.35*math.sin(a2)),F.p(cx+math.copysign(.28*math.cos(a2),dx),1.2,v+.35*math.sin(a2)),F.p(cx+math.copysign(.28*math.cos(a),dx),1.2,v+.35*math.sin(a))])
    for sz in [-.2,.2]:
     F.tube('sb-wood',(cx+math.copysign(.2,dx),.66,v+sz),(cx+math.copysign(.25,dx),.89,v+sz),.025,8)
    for sx in [-.18,.18]:
     for sz in [-.18,.18]:F.tube('sb-metal',(cx+sx,.22,v+sz),(cx+sx,.62,v+sz),.022,6)
   F.lathe('sb-paper',u,v,[(.99,.065),(1.16,.08)],14)
 # Wood wall liner and low storage at west end, simple track lights and diffusers.
 F.box('sb-wood',(-9.3,2.5,-4),(.08,4.5,7))
 for u in [-6,0,6]:
  F.box('sb-black',(u,5.48,-5),(3,.04,.18))
  for dx in [-1,0,1]:F.lathe('sb-lamp',u+dx,-5,[(5.15,.08),(5.4,.08)],12)
  F.box('sb-black',(u,5.55,-7),(2,.02,.18))
 routes=[dict(name='Entry and order counter',points=[F.p(2,.12,2),F.p(2,.22,-1),F.p(2,.22,-3.2),F.p(2,.22,-5.4),F.p(-6,.22,-5.4)]),dict(name='Window seating aisle',points=[F.p(u,.22,-3.2) for u in [2,-2,-6,-8]]),dict(name='East seating aisle',points=[F.p(u,.22,-3.2) for u in [2,6,8.7]])]
 return dict(key=KEY,name='Starbucks Flamingo',center=[p.centroid.x,0,p.centroid.y],bounds=list(p.bounds),structural=True,hotelSources=[],exteriorOnly=False,portals=[door],zones=[dict(origin=F.p(0,.22,0),yaw=YAW+math.pi,width=21,depth=10,height=6)],lights=[dict(p=F.p(u,4.6,v),color=0xffe7c8,power=7,range=9) for u,v in [(-6,-3),(2,-3),(7,-5),(-4,-7)]],routes=routes)
if __name__=='__main__':
 B=Meshes();m=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(m,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
