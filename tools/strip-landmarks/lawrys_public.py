"""Public lounge/bar: reference-supported sequence, fitted dimensions, original decor."""
from common import *
def build_public(B,F,door):
 B.property='lawrys-hughes-interior';B.source='public/lawrys-hughes'
 lounge=F.poly([(-3,1.95),(3,1.95),(3,-14),(-3,-14)])
 bar=F.poly([(2.98,-5),(13,-5),(13,-13),(2.98,-13)])
 room=lounge.union(bar)
 B.shell(room,.24,3.55,'lh-panel',roof=False,openings=[door,dict(p=F.p(0,.24,-14),yaw=F.yaw,width=5.6,height=3.3)]);B.planar('lh-carpet',lounge,.24,True);B.planar('lh-plank',bar.difference(lounge),.24,True)
 # Actual bar is to the right of the entrance lounge; this doorway is fitted.
 for a,b in [(-5,-5.4),(-8.4,-13)]:F.box('lh-panel',(3,1.895,(a+b)/2),(.15,3.31,abs(b-a)),True)
 F.box('lh-panel',(3,3.23,-6.9),(.15,.64,3),True)
 # Elliptical stepped ceiling tray, modelled as a real recessed opening.
 rings=[]
 for rx,rz,y in [(1.15,4.8,3.55),(.96,4.55,3.69),(.77,4.3,3.83)]:
  q=F.poly([(rx*math.cos(a),-5.3+rz*math.sin(a)) for a in np.linspace(0,math.tau,64,endpoint=False)]);rings.append((q,y))
 B.planar('lh-ceiling',lounge.difference(rings[0][0]),3.55)
 for i,(q,y) in enumerate(rings):
  B.shell(q,y,y+.14,'lh-gold',roof=False,solid=False)
  B.planar('lh-ceiling',q.difference(rings[i+1][0]) if i<2 else q,y+.14)
 B.planar('lh-ceiling',bar,3.55)
 # Fine metal inlays and base moulding in the lounge walls, not coplanar decals.
 for u in [-2.96,2.96]:
  for y in [.34,1.65,2.65]:
   for a,b in ([(-13.9,1.85)] if u<0 else [(-13.9,-8.5),(-5.3,1.85)]):F.box('lh-metal',(u,y,(a+b)/2),(.035,.025,b-a))
  for v in [-12,-10,-8,-6,-4,-2,0]:
   if u>0 and -8.5<v<-5.3:continue
   F.box('lh-metal',(u,1.95,v),(.03,3.1,.022))
 # Sofa and armchair geometry: independent cushions, arms, tapered-looking legs.
 def seat(u,v,mat,side,width=1.25):
  F.box('lh-darkwood',(u,.47,v),(.8,.26,width),True)
  F.box(mat,(u-side*.04,.67,v),(.80,.2,width-.1))
  F.box(mat,(u+side*.34,1.0,v),(.18,.78,width-.05))
  for z in [v-width/2,v+width/2]:F.box(mat,(u,.85,z),(.88,.50,.15))
  for x in [u-.29,u+.29]:
   for z in [v-width*.36,v+width*.36]:F.box('lh-metal',(x,.33,z),(.055,.18,.055))
 for side in [-1,1]:
  seat(side*2.35,-2.4,'lh-redseat',side,2.4)
  seat(side*2.2,-8.7,'lh-tealseat',side,1.25)
  seat(side*2.2,-10.5,'lh-tealseat',side,1.25)
  seat(side*1.65,-.5,'lh-blueseat',side,.9)
  F.box('lh-darkwood',(side*1.65,.76,-4.1),(.75,.08,1.1),True)
  for dz in [-.4,.4]:F.box('lh-metal',(side*1.65,.49,-4.1+dz),(.5,.5,.035))
 # Stone fireplace on left, non-emissive dark firebox.
 F.box('lh-stone',(-2.55,1.45,-5.7),(.8,2.4,2.25),True)
 F.box('lh-darkwood',(-2.12,1.05,-5.7),(.045,.9,1.55))
 F.box('lh-stone',(-2.35,.38,-5.7),(1.3,.22,2.6),True)
 # Host desk ahead, flanked by wood columns with softly luminous capitals.
 F.box('lh-panel',(0,.84,-12.3),(1.35,1.2,.7),True);F.box('lh-darkwood',(0,1.47,-12.3),(1.5,.08,.85))
 for y in [.50,.67,.84]:F.box('lh-metal',(0,y,-11.94),(1.12,.025,.025))
 for u in [-2,2]:
  for v in [-11.6,-13.4]:
   F.lathe('lh-panel',u,v,[(.24,.26),(.35,.29),(2.65,.29),(2.85,.35)],20)
   F.lathe('lh-lamp',u,v,[(2.85,.35),(3.35,.42)],20)
   for y in [.4,1.2,2,2.8,3.36]:F.lathe('lh-metal',u,v,[(y,.30 if y<2.8 else .43),(y+.025,.30 if y<2.8 else .43)],20)
 # Bar coffers and mirrors: original material, no borrowed photographs.
 for u in [3.1,5.55,8,10.45,12.9]:F.box('lh-darkwood',(u,3.44,-9),(.16,.20,8))
 for v in [-5.1,-7.7,-10.3,-12.9]:F.box('lh-darkwood',(8,3.44,v),(10,.20,.16))
 F.box('lh-panel',(11.8,.83,-9),(1.1,1.18,6.4),True);F.box('lh-darkwood',(11.8,1.47,-9),(1.3,.10,6.6))
 F.box('lh-mirror',(12.91,2.2,-9),(.035,1.9,6.5))
 for y in [1.3,1.8,2.4,3.1]:F.box('lh-darkwood',(12.6,y,-9),(.62,.08,6.6))
 for v in np.arange(-11.8,-6,.35):
  for y in [1.84,2.44]:
   F.lathe('lh-bottle',12.48,float(v),[(y,.045),(y+.22,.045),(y+.25,.02),(y+.34,.02)],10)
 for v in [-11.2,-9.8,-8.4,-7]:
  F.lathe('lh-metal',10.4,v,[(.24,.28),(.30,.28),(.32,.045),(1.02,.045)],16)
  F.box('lh-tealseat',(10.4,1.06,v),(.55,.12,.55),True);F.box('lh-tealseat',(10.12,1.35,v),(.08,.56,.55))
 # Long communal table on visible slender legs, with open circulation on both sides.
 table=F.poly([(7+.9*math.cos(a),-8.6+2.1*math.sin(a)) for a in np.linspace(0,math.tau,40,endpoint=False)])
 B.planar('lh-darkwood',table,1.22,True);B.shell(table,1.14,1.22,'lh-darkwood',roof=False,solid=False)
 for v in [-10,-7.2]:F.box('lh-darkwood',(7,.69,v),(.14,.9,.14),True)
 for u in [5.8,8.2]:
  for v in [-9.8,-8.5,-7.2]:seat(u,v,'lh-redseat',-1 if u<7 else 1,.65)
 # Original abstract framed panels; inferred placement, no copied tour artwork.
 for u in [5,8,11]:
  F.box('lh-gold',(u,2.1,-12.91),(1.4,1.7,.05));F.box('lh-art',(u,2.1,-12.87),(1.26,1.55,.03))
 result=dict(portals=[door],exteriorOnly=False,zones=[dict(origin=F.p(0,.24,1.95),yaw=F.yaw+math.pi,width=6.1,depth=16,height=4),dict(origin=F.p(8,.24,-5),yaw=F.yaw+math.pi,width=10.1,depth=8.1,height=4)],lights=[dict(p=F.p(0,3.1,v),color=0xffd5a6,power=9,range=8) for v in [-2,-9]]+[dict(p=F.p(8,3.1,-8),color=0xffd5a6,power=10,range=9)],routes=[dict(name='Entrance lounge and bar',points=[F.p(0,.24,v) for v in [6,2.4,1,-3,-6.9]]+[F.p(4.2,.24,-6.9),F.p(4.2,.24,-11.5)])])

 from lawrys_dining import build_dining
 dining=build_dining(B,F);result['zones'].append(dining['zone']);result['routes'].append(dining['route']);result['lights'].append(dining['light'])
 return result
