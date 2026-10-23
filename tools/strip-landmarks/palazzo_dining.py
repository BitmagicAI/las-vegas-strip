"""Outdoor dining on the photographed left retail terrace.
Furniture positions are adapted to provisional frontage dimensions, not surveyed.
"""
import math
from common import Frame

def patio(B,F):
 B.detail=0
 # Keep the front 2 m of terrace clear for the stair arrivals and cross-route.
 for x in [13.7,10.4]:
  z=-4.35;y=3.0
  F.lathe('bronze',x,z,[(y,.32),(y+.07,.32),(y+.08,.055),(y+.72,.055)],16)
  F.lathe('marble',x,z,[(y+.72,.65),(y+.78,.65)],32)
  F.tube('walnut',(x,y,z),(x,y+2.9,z),.035,8)
  # Eight slightly curved cloth gores: real low-poly surface, near-detail ribs.
  for k in range(8):
   a=k*math.tau/8;b=(k+1)*math.tau/8
   for r,rr,hh,h in [(0,.5,2.88,2.78),(.5,1.4,2.78,2.38)]:
    B.face('red',[F.p(x+r*math.cos(a),y+hh,z+r*math.sin(a)),F.p(x+rr*math.cos(a),y+h,z+rr*math.sin(a)),F.p(x+rr*math.cos(b),y+h,z+rr*math.sin(b)),F.p(x+r*math.cos(b),y+hh,z+r*math.sin(b))])
   B.face('red',[F.p(x+1.4*math.cos(a),y+2.38,z+1.4*math.sin(a)),F.p(x+1.4*math.cos(b),y+2.38,z+1.4*math.sin(b)),F.p(x+1.4*math.cos(b),y+2.25,z+1.4*math.sin(b)),F.p(x+1.4*math.cos(a),y+2.25,z+1.4*math.sin(a))])
   B.detail=1;F.tube('bronze',(x,y+2.82,z),(x+1.36*math.cos(a),y+2.33,z+1.36*math.sin(a)),.014,4);B.detail=0
  for a in [0,math.pi/2,math.pi,math.pi*1.5]:
   cx,cz=x+math.cos(a),z+math.sin(a);p=F.p(cx,y,cz);T=Frame(B,p[0],p[2],F.yaw-a+math.pi/2,y=p[1])
   T.box('walnut',(0,.44,0),(.47,.08,.47),True)
   for side in [-1,1]:
    for zz in [-.2,.2]:T.tube('bronze',(side*.20,.02,zz),(side*.20,.45,zz),.022,6)
    T.tube('bronze',(side*.22,.42,.22),(side*.22,.91,.22),.023,6)
   B.detail=1
   for yy in [.58,.70,.82]:T.box('walnut',(0,yy,.22),(.46,.065,.045))
   B.detail=0
 B.detail=0
