"""Reference-led main deck planting. Positions are provisional map registration.
Palm leaflets are batched near detail; no per-tree runtime updates or lights.
"""
import math
import random
from shapely.geometry import Point,box
from common import Frame

def gardens(B,deck,wet,world,y,points=None,crown_clearance=0):
 reserved=[]
 for px,py in (points if points is not None else [(570,412),(675,412),(570,491),(675,491),(220,450),(409,453),(263,582),(410,587)]):
  x,z=world((px,py));area=box(x-1.15,z-1.15,x+1.15,z+1.15)
  if not deck.buffer(-.5).covers(area) or wet.buffer(.65).intersects(area):continue
  if crown_clearance and wet.intersects(Point(x,z).buffer(crown_clearance)):continue
  reserved.append(area.buffer(.5));T=Frame(B,x,z,y=y)
  B.detail=0
  T.box('ivory',(0,.32,0),(2.3,.64,2.3),True)
  T.box('bark',(0,.65,0),(2.02,.035,2.02))
  for s in [-1,1]:
   T.box('white',(s*1.08,.70,0),(.17,.16,2.3));T.box('white',(0,.70,s*1.08),(2.13,.16,.17))
  rng=random.Random(px*1000+py);h=5.3+rng.random()*.9
  T.lathe('bark',0,0,[(.67,.28),(1,.25),(h-.6,.21),(h,.30)],10)
  B.detail=1
  # Diamond-shaped old leaf scars on the trunk, avoiding stacked coplanar rings.
  for row in range(int((h-.9)/.15)):
   yy=.9+row*.15
   for j in range(7):
    a=j*math.tau/7+(row%2)*math.pi/7
    T.tube('bark',(.25*math.cos(a),yy,.25*math.sin(a)),(.29*math.cos(a+.16),yy+.11,.29*math.sin(a+.16)),.045,4)
  for j in range(22):
   a=j*2.39996;length=2.5+rng.random()*.8;lift=.8+(j%3)*.55
   def p(t,offset=0):
    r=length*t
    return (r*math.cos(a)-offset*math.sin(a),h+lift*math.sin(math.pi*t)-.60*t,r*math.sin(a)+offset*math.cos(a))
   T.path('sage',[p(k/10) for k in range(11)],.022,4)
   for k in range(1,22):
    t=k/23;w=.55*math.sin(math.pi*t)**.65
    for side in [-1,1]:
     q=p(t);end=p(min(1,t+.13),side*w);mid=p(t+.025,side*w*.40)
     # Folded tapered pinnate leaflets, two real surfaces rather than spheres.
     B.face('foliage',[T.p(*q),T.p(mid[0],mid[1]+.04,mid[2]),T.p(end[0],end[1]-.20,end[2])])
     B.face('sage',[T.p(*q),T.p(end[0],end[1]-.20,end[2]),T.p(*p(t+.045,side*w*.3))])
  # Small planted rosettes and flowers inside planter only.
  for j in range(32):
   a=rng.random()*math.tau;r=.45+rng.random()*.45
   xx,zz=r*math.cos(a),r*math.sin(a)
   for k in range(5):
    b=k*math.tau/5
    B.face('foliage',[T.p(xx,.68,zz),T.p(xx+.1,.82,zz+.05),T.p(xx+.26*math.cos(b),.92,zz+.26*math.sin(b))])
   if j%3==0:T.lathe('rose',xx,zz,[(.84,0),(.89,.06),(.93,0)],5)
 B.detail=0
 return reserved
