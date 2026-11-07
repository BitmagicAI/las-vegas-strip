"""Original low-poly Beach Club furnishings; photograph-supported style, inferred layout."""
from common import *

def furnish_club(B,court,water):
 lane=LineString([(645,-1510),(620,-1460)]).buffer(1.5)
 clear=court.buffer(-.6).difference(water.buffer(1.5)).difference(lane)
 placements=[]
 # Beds follow the diagonal pool axis, outside its circulation lane.
 for x,z in [(625,-1530),(620,-1520),(615,-1510),(600,-1480),(595,-1470),
             (650,-1510),(645,-1500),(640,-1490),(635,-1480),(630,-1470)]:
  F=Frame(B,x,z,math.atan2(-.447,.894),y=.28)
  mask=F.poly([(-1.1,-1.4),(1.75,-1.4),(1.75,1.4),(-1.1,1.4)])
  if not clear.covers(mask):continue
  F.box('wy-white',(0,.25,0),(1.9,.5,2.35),True)
  F.box('wy-white',(0,.57,0),(1.8,.14,2.2))
  F.box('wy-red-fabric',(0,.72,.8),(1.75,.28,.48))
  for side in [-1,1]:F.box('wy-red-fabric',(side*.58,.75,.4),(.42,.22,.42))
  F.box('wy-white',(1.45,.3,0),(.45,.6,.45),True)
  placements.append([x,z])
  # Four sparse parasols, with poles outside the bed and a two-tone octagonal canopy.
  if len(placements)%2==0:
   pole=F.p(-1.5,0,0)
   if clear.covers(Point(pole[0],pole[2]).buffer(.35)):
    F.box('wy-white',(-1.5,.08,0),(.55,.16,.55),True)
    F.box('wy-white',(-1.5,1.45,0),(.08,2.9,.08),True)
    for i in range(8):
     a,b=i*math.tau/8,(i+1)*math.tau/8
     rim=[(-1.5+1.55*math.cos(t),2.48,1.55*math.sin(t)) for t in [a,b]]
     B.face('wy-white',[F.p(-1.5,2.98,0),F.p(*rim[0]),F.p(*rim[1])])
     B.face('wy-red-fabric',[F.p(*rim[0]),F.p(*rim[1]),F.p(rim[1][0],2.30,rim[1][2]),F.p(rim[0][0],2.30,rim[0][2])])
 return placements
