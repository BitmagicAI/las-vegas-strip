"""Original folded fan-palm leaves, inferred scale; no decorative collision."""
from common import *
def fan_palm(B,x,z,h=4.2,y=.34):
 F=Frame(B,x,z,y=y)
 F.lathe('bark',0,0,[(0,.22),(h*.75,.18),(h,.24)],12)
 for j in range(18):
  a=j*2.399963;co,si=math.cos(a),math.sin(a);r=1.2+(j%3)*.16
  base=(co*r,h+.5-(j%4)*.16,si*r)
  F.tube('om-leaf',(0,h,0),base,.025,6)
  # Eleven tapered fingers form a folded fan rather than a sphere/card crown.
  for k in range(11):
   ang=a+(k-5)*.17;dx,dz=math.cos(ang),math.sin(ang)
   tip=(base[0]+dx*.95,base[1]-.32-abs(k-5)*.04,base[2]+dz*.95)
   mid=(base[0]+dx*.55,base[1]+.05,base[2]+dz*.55)
   for side in [-1,1]:
    edge=(mid[0]-dz*.07*side,mid[1]-.04,mid[2]+dx*.07*side)
    B.face('om-leaf',[F.p(*base),F.p(*edge),F.p(*mid)])
    B.face('om-leaf',[F.p(*mid),F.p(*edge),F.p(*tip)])
