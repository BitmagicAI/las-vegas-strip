"""Original solid-leaf planting; inferred sizes, no decorative collision."""
from common import *
import random

def leaf(B,F,center,length,width,angle,mat):
 x,y,z=center;co,si=math.cos(angle),math.sin(angle)
 pts=[(x-co*length,y,z-si*length),(x-si*width,y-.025,z+co*width),(x+co*length,y+.035,z+si*length),(x+si*width,y-.025,z-co*width)]
 for a,b in zip(pts,pts[1:]+pts[:1]):B.face(mat,[F.p(*a),F.p(x,y+.06,z),F.p(*b)])

def hedge(B,x,z,y=.56,width=2.3,height=1.8,seed=0):
 F=Frame(B,x,z,y=y);rng=random.Random(seed)
 F.box('om-leaf',(0,height*.45,0),(width*.75,height*.88,width*.75))
 for i in range(850):
  side=i%5;a=rng.uniform(-width/2,width/2);b=rng.uniform(0,height)
  if side==0:c=(a,height+rng.uniform(-.06,.06),rng.uniform(-width/2,width/2))
  elif side==1:c=(a,b,-width/2)
  elif side==2:c=(a,b,width/2)
  elif side==3:c=(-width/2,b,a)
  else:c=(width/2,b,a)
  leaf(B,F,c,rng.uniform(.08,.16),.055,rng.random()*math.tau,'om-leaf')

def palm(B,x,z,h=5,y=.32,scale=1):
 F=Frame(B,x,z,y=y)
 F.lathe('bark',0,0,[(0,.28*scale),(h*.7,.22*scale),(h,.19*scale)],12)
 for j in range(24):
  a=j*2.399963;co,si=math.cos(a),math.sin(a);droop=(j%6)/5
  points=[]
  for k in range(9):
   t=k/8;r=3.0*scale*t;yy=h+1.25*scale*math.sin(math.pi*t)-droop*scale*t
   points.append((co*r,yy,si*r))
  F.path('om-leaf',points,.022*scale,5)
  for k in range(1,9):
   t=k/9;r=3*scale*t;yy=h+1.25*scale*math.sin(math.pi*t)-droop*scale*t
   for side in [-1,1]:
    length=.65*scale*(1-t*.65);base=(co*r,yy,si*r);tip=(base[0]-si*side*length+co*.25*scale,yy-.22*scale,base[2]+co*side*length+si*.25*scale)
    B.face('om-leaf',[F.p(*base),F.p(base[0]+co*.08,yy+.025,base[2]+si*.08),F.p(*tip)])
    B.face('om-leaf',[F.p(*base),F.p(*tip),F.p(base[0]-co*.06,yy-.025,base[2]-si*.06)])
