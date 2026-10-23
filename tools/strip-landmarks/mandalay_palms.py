"""Mapped palms; batched pinnate leaflets and persistent trunk silhouettes."""
from common import *
def plant(B,water,buildings,deck):
 count=0
 for j,(x,z) in enumerate(json.load(open('tools/strip-landmarks/mandalay-palm-positions.json'))):
  p=Point(x,z)
  if water.buffer(.65).contains(p) or buildings.buffer(.8).contains(p) or water.distance(p)>30:continue
  B.source='mandalay-pool-palms';B.detail=0;y=.64 if deck.contains(p) else .24;F=Frame(B,x,z,y=y)
  h=6.5+(j%7)*.35;F.lathe('bark',0,0,[(0,.28),(.5,.25),(h-.4,.16),(h,.24)],10)
  B.detail=1
  for k in range(15):
   a=k*2.39996+j*.4;length=2.4+(k%3)*.35;lift=.9+(k%4)*.18
   def point(t,off=0):return (length*t*math.cos(a)-off*math.sin(a),h+lift*math.sin(math.pi*t)-.9*t,length*t*math.sin(a)+off*math.cos(a))
   F.path('sage',[point(t/6) for t in range(7)],.018,4)
   for k2 in range(1,15):
    t=k2/16;w=.55*math.sin(math.pi*t)**.7
    for side in [-1,1]:
     q=point(t);end=point(min(1,t+.16),side*w);mid=point(t+.04,side*w*.45)
     B.face('foliage',[F.p(*q),F.p(mid[0],mid[1]+.05,mid[2]),F.p(end[0],end[1]-.15,end[2])])
     B.face('sage',[F.p(*q),F.p(end[0],end[1]-.15,end[2]),F.p(*point(t+.05,side*w*.3))])
  count+=1
 B.detail=0
 return count
