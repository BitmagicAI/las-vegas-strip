"""Upper Strip roof service enclosures from Earth reference; dimensions estimated."""
from common import *
def exterior(B):
 B.property='harrahs-exterior';B.source='harrahs-upper-roof';B.detail=0
 path=LineString([(76.1,-449.4),(65.1,-441),(62.4,-432),(57.8,-414.7),(54.3,-399.3),(53,-374.3),(53.7,-361.2),(55.1,-345),(58,-330.1),(69.8,-320.6)])
 def p(s,y,d):
  a=path.interpolate(max(0,s-.1));b=path.interpolate(min(path.length,s+.1));u=(b.x-a.x)/a.distance(b);v=(b.y-a.y)/a.distance(b);c=path.interpolate(s);return(c.x-v*d,y,c.y+u*d)
 # The existing upper marquee roof is19.2m; units stay on that13m-wide band.
 for s in [24,54,84,110]:
  x,y,z=p(s,19.2,-7)
  B.box('harrahs-service-paint',(x,y+.55,z),(3.3,1.1,5))
  for dz in [-1.4,1.4]:
   B.lathe('charcoal',(x,z+dz),[(20.32,.68),(20.42,.68),(20.42,.01)],16)
  for yy in np.arange(19.5,20.2,.18):B.box('harrahs-joint',(x-1.67,yy,z),(.05,.055,4.5))
  B.box('harrahs-service-paint',(x+2.1,19.65,z),(1.2,.7,3.2))
 # Pale parapet follows inner roof edge, broken at service access gaps.
 for s in np.arange(1,path.length-1,2):
  if any(abs(s-gap)<2.5 for gap in [42,92]):continue
  a=p(s,19.65,-12.65);b=p(min(path.length-.1,s+2),19.65,-12.65)
  B.tube('harrahs-membrane-paint',a,b,.3,4)

 # Lettered show/restaurant panels in existing recessed marquee openings.
 B.source='harrahs-showbill'
 for fraction,lines,size in [(.22,['DONNY'],1.65),(.76,["RAMSAY’S",'KITCHEN'],.7)]:
  at=path.length*fraction;x,y,z=p(at,0,1.16);a=p(at-.1,0,1.16);b=p(at+.1,0,1.16)
  F=Frame(B,x,z,math.atan2(b[2]-a[2],-(b[0]-a[0])),y=0)
  for i,line in enumerate(lines):F.text(line,(0,13.7-i*.95,-.03),size,'white')
