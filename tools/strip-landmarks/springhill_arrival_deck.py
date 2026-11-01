"""Original arrival and deck details; reference register in springhill-refinement.
The east canopy does not relocate the existing generic west hotel entrance.
"""
from common import *

def details(B):
 B.source='springhill-arrival';B.detail=0
 F=Frame(B,1598.65,-2134.2,-math.pi/2,y=.24)
 F.box('sh-white',(0,2.5,-.45),(13,5,.12))
 F.box('sh-sill',(0,4.5,-2.7),(12.6,.3,5.8),True)
 F.box('sh-shadow',(0,4.8,-5.59),(12.6,.5,.12))
 F.text('SPRINGHILL SUITES',(1.1,4.64,-5.68),.52,'sh-white')
 F.text('BY MARRIOTT',(-4.7,4.69,-5.68),.21,'sh-white')
 # Cantilevered upper louvers and supports, no new runtime lights.
 for x in [-6,-3,0,3,6]:F.box('sh-frame',(x,5.15,-4.95),(.07,.65,1.3))
 for z in [-5.55,-5.1,-4.65]:F.box('sh-frame',(0,5.18,z),(12.6,.06,.09))
 for x in [-4,0,4]:
  for z in [-1.1,-3.4]:F.box('sh-white',(x,4.335,z),(.16,.015,.16))
 for x in [-5.9,-2.1,2.1,5.9]:
  F.box('sh-white',(x,2.1,-.52),(.36,4.2,.35))
 for x,w in [(-4,3.2),(0,2.9),(4,3.2)]:
  F.box('sh-frame',(x,1.65,-.54),(w+.12,2.95,.10))
  F.box('sh-window',(x,1.65,-.61),(w,2.83,.035))
  for yy in [.65,1.65,2.65]:F.box('sh-frame',(x,yy,-.64),(w,.04,.04))
  F.box('sh-frame',(x,1.65,-.64),(.04,2.83,.04))
 F.text('2989',(0,3.55,-.7),.27,'sh-shadow')
 for x in [-4,4]:F.box('sh-shadow',(x,.2,-.55),(3.2,.4,.65),True)
 # Keep the apron clear and preserve the existing ground collision under it.
 B.source='springhill-roof-furniture';B.detail=1
 def lounger(x,z,yaw):
  G=Frame(B,x,z,yaw,y=74.04)
  for xx in [-.32,.32]:
   G.path('sh-frame',[(xx,.12,-.85),(xx,.4,-.7),(xx,.4,.8),(xx,.12,.9)],.025,6)
  G.box('sh-window',(0,.4,.25),(.59,.045,1.1))
  G.b.face('sh-window',[G.p(-.295,.42,-.3),G.p(.295,.42,-.3),G.p(.295,.93,-.83),G.p(-.295,.93,-.83)])
  for xx in [-.32,.32]:G.tube('sh-frame',(xx,.4,-.3),(xx,.95,-.85),.025,6)
  # Low conservative collider prevents walking through the furniture.
  c=G.b.solids[G.b.property];start=len(c['vertices'])//3
  for xx,yy,zz in [(-.31,.04,-.86),(.31,.04,-.86),(.31,.38,-.86),(-.31,.38,-.86),(-.31,.04,.86),(.31,.04,.86),(.31,.38,.86),(-.31,.38,.86)]:c['vertices'].extend(G.p(xx,yy,zz))
  for face in [(0,1,2,3),(4,7,6,5),(0,4,5,1),(3,2,6,7),(0,3,7,4),(1,5,6,2)]:
   for i in [face[0],face[1],face[2],face[0],face[2],face[3]]:c['indices'].append(start+i)
 for x in [1541.5,1544,1546.5,1549,1551.5]:lounger(x,-2130.0,math.pi)
 for x in [1542,1544.5,1547,1549.5]:lounger(x,-2141.0,0)
 for x,z in [(1542.8,-2130),(1547.8,-2130),(1550.8,-2141)]:
  B.box('sh-window',(x,74.28,z),(.45,.48,.45),True)
 # Ladder rails at opposite short ends; pool shape/depth retained.
 for x,z in [(1543.0,-2136.0),(1551.0,-2135.0)]:
  for dz in [-.3,.3]:
   B.tube('sh-frame',(x,73.0,z+dz),(x,74.7,z+dz),.035,8)
 return [dict(name='East court to canopy',points=[F.p(0,0,-8),F.p(0,0,-2.3)]),dict(name='East arrival canopy frontage',points=[F.p(-5,0,-2.3),F.p(5,0,-2.3)]),dict(name='Roof deck perimeter',points=[[1540.2,74.04,-2127.8],[1554,74.04,-2127.8],[1554,74.04,-2142.7],[1540.2,74.04,-2142.7],[1540.2,74.04,-2127.8]])]
