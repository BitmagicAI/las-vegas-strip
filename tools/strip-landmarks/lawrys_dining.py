"""Original main dining room, fitted behind the verified host passage.
Furniture spacing/room dimensions inferred; no claim of a surveyed floor plan.
"""
from common import *
def build_dining(B,F):
 room=F.poly([(-12,-14),(12,-14),(12,-30),(-12,-30)])
 passage=dict(p=F.p(0,.24,-14),yaw=F.yaw,width=5.6,height=3.3)
 B.shell(room,.24,4.15,'lh-panel',roof=False,openings=[passage]);B.planar('lh-plank',room,.24,True)
 # Radial faceted ceiling recess from the official dining panorama.
 perimeter=F.poly([(7.5*math.cos(a),-22+5.5*math.sin(a)) for a in np.linspace(0,math.tau,48,endpoint=False)])
 B.planar('lh-ceiling',room.difference(perimeter),4.15)
 for i in range(48):
  a=math.tau*i/48;b=math.tau*(i+1)/48
  points=[(7.5*math.cos(a),4.15,-22+5.5*math.sin(a)),(7.5*math.cos(b),4.15,-22+5.5*math.sin(b)),(1.0*math.cos(b),5.12,-22+.75*math.sin(b)),(1.0*math.cos(a),5.12,-22+.75*math.sin(a))]
  B.face('lh-ceiling',[F.p(*p) for p in points])
  if i%2==0:F.tube('lh-cream',points[0],points[-1],.04,8)
 for rx,rz,y in [(7.5,5.5,4.13),(7.2,5.2,4.2)]:
  pts=[(rx*math.cos(a),y,-22+rz*math.sin(a)) for a in np.linspace(0,math.tau,65)]
  F.path('lh-cream',pts,.07,8)
 B.planar('lh-ceiling',F.poly([(math.cos(a),-22+.75*math.sin(a)) for a in np.linspace(0,math.tau,32,endpoint=False)]),5.12)
 F.tube('lh-metal',(0,5.1,-22),(0,4.4,-22),.045,12)
 F.lathe('lh-lamp',0,-22,[(4.1,.25),(4.18,.55),(4.37,.7),(4.42,.73)],32)
 # White cloths, tall red upholstered chairs and individually modelled place settings.
 def chair(x,z,side):
  F.box('lh-redseat',(x,.7,z),(.55,.16,.55),True)
  F.box('lh-redseat',(x,1.15,z+side*.26),(.55,.9,.09))
  for dx in [-.22,.22]:
   for dz in [-.22,.22]:F.box('lh-darkwood',(x+dx,.45,z+dz),(.055,.42,.055))
 def table(x,z):
  F.box('lh-cloth',(x,1.22,z),(1.7,.065,1.15),True)
  for dx in [-.7,.7]:
   for dz in [-.43,.43]:F.box('lh-darkwood',(x+dx,.72,z+dz),(.075,.95,.075))
  for dx in [-.47,.47]:
   for side in [-1,1]:
    chair(x+dx,z+side*.95,side)
    q=F.poly([(x+dx+.17*math.cos(a),z+side*.31+.17*math.sin(a)) for a in np.linspace(0,math.tau,20,endpoint=False)])
    B.planar('lh-cloth',q,1.27)
    F.lathe('lh-metal',x+dx+.22,z+side*.29,[(1.25,.04),(1.27,.04),(1.38,.012),(1.4,.04),(1.49,.05)],12)
 for x in [-8,-4,4,8]:
  for z in [-18.4,-23.3,-27.4]:table(x,z)
 # Teal rear banquette and a large original abstract composition.
 for x in [-9,-6,-3,0,3,6,9]:
  F.box('lh-tealseat',(x,.65,-29.35),(2.8,.28,.95),True)
  F.box('lh-tealseat',(x,1.2,-29.78),(2.8,1.1,.18))
 F.box('lh-gold',(0,2.8,-29.9),(13,1.6,.07));F.box('lh-art',(0,2.8,-29.85),(12.8,1.4,.03))
 # Glazed wine/display cabinet behind entry, routes pass to either side.
 F.box('lh-panel',(0,.78,-16.7),(3.8,1.05,.8),True)
 F.box('lh-clear-glass',(0,1.42,-16.7),(3.8,.25,.8))
 for x in np.arange(-1.65,1.7,.3):F.lathe('lh-bottle',float(x),-16.7,[(1.31,.045),(1.5,.045),(1.54,.02),(1.61,.02)],10)
 return dict(zone=dict(origin=F.p(0,.24,-14),yaw=F.yaw+math.pi,width=24.1,depth=16.1,height=5.1),route=dict(name='Host passage into main dining room',points=[F.p(0,.24,-8),F.p(1.2,.24,-10.5),F.p(1.2,.24,-14.8),F.p(2.6,.24,-15.1),F.p(2.6,.24,-18),F.p(0,.24,-21)]),light=dict(p=F.p(0,4,-22),color=0xffdeb8,power=18,range=15))
