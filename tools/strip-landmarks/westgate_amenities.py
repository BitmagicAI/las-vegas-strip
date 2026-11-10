"""Original Westgate roof-pool furniture and pavilions, photo-fitted, not surveyed."""
from common import *
KEY='westgateAmenities'
Y=12.04

def build(B):
 B.property=KEY+'-exterior';B.source='westgate-pool-amenities';B.detail=0
 def pavilion(x,z,r=4.2):
  for j in range(8):
   a=(j+.5)*math.tau/8;b=(j+1.5)*math.tau/8
   xx,zz=x+(r-.5)*math.cos(a),z+(r-.5)*math.sin(a)
   B.box('wga-white-paint',(xx,Y+1.5,zz),(.24,3,.24),True)
   B.box('wga-white-paint',(xx,Y+.18,zz),(.45,.36,.45))
   edge=(x+r*math.cos(a),Y+3.2,z+r*math.sin(a));end=(x+r*math.cos(b),Y+3.2,z+r*math.sin(b))
   B.upface('wga-blue-roof-paint',[edge,end,(x,Y+5,z)])
   B.tube('wga-blue-trim-paint',edge,end,.10,6)
   B.tube('wga-blue-trim-paint',edge,(x,Y+5,z),.045,6)
  B.lathe('wga-blue-trim-paint',(x,z),[(Y+5,.18),(Y+5.6,.03)],8)
 def lounger(x,z,yaw):
  F=Frame(B,x,z,yaw,y=Y)
  F.box('wga-blue-fabric',(0,.42,0),(.75,.12,1.8));F.box('wga-white-paint',(0,.2,0),(.55,.4,1.5),True)
  B.face('wga-blue-fabric',[F.p(-.375,.48,-.4),F.p(.375,.48,-.4),F.p(.375,.95,-.95),F.p(-.375,.95,-.95)])
  for xx in [-.36,.36]:F.path('wga-white-paint',[(xx,.46,.85),(xx,.46,-.4),(xx,.95,-.95)],.025,6)
 def cabana(x,z,yaw):
  F=Frame(B,x,z,yaw,y=Y)
  for xx in [-1.8,1.8]:
   for zz in [-1.8,1.8]:
    F.box('wga-white-paint',(xx,1.5,zz),(.12,3,.12),True)
    # Tied, pleated curtains preserve the open front and walkable doorway.
    for i in range(5):F.box('wga-curtain',(xx+(i-2)*.06,1.5,zz),(.055,2.7,.16))
    F.box('wga-blue-fabric',(xx,1.35,zz),(.38,.12,.21))
  F.box('wga-curtain',(0,3.06,0),(3.9,.14,3.9))
  F.box('wga-wicker',(0,.35,-1.25),(2.7,.7,.75),True)
  F.box('wga-cushion',(0,.76,-1.25),(2.6,.15,.7))
  F.box('wga-cushion',(0,1.05,-1.6),(2.6,.6,.13))
  F.box('wga-wicker',(0,.3,.4),(1.1,.6,.65),True)
 def palm(x,z,i):
  h=6+i%3
  B.lathe('wga-bark',(x,z),[(Y,.23),(Y+h,.11)],12);B.box('wga-bark',(x,Y+h/2,z),(.3,h,.3),True)
  for j in range(12):
   a=j*math.tau/12+i*.4;ps=[]
   for k in range(7):
    t=k/6;r=3*t;yy=Y+h+1.2*math.sin(t*math.pi)-t;w=.32*math.sin(t*math.pi)
    ps.append([(x+r*math.cos(a)-w*math.sin(a),yy,z+r*math.sin(a)+w*math.cos(a)),(x+r*math.cos(a)+w*math.sin(a),yy,z+r*math.sin(a)-w*math.cos(a))])
   for k,(a,b) in enumerate(zip(ps,ps[1:])):
    B.face('wga-leaf',[a[0],b[1],b[0]] if k==0 else [a[0],a[1],b[0]] if k==5 else [a[0],a[1],b[1],b[0]])
  B.lathe('wga-planter',(x,z),[(Y,.8),(Y+.5,.8)],16)
 for x,z in [(1970,-2167),(2015,-2170),(1991,-2137)]:pavilion(x,z)
 for z,yaw in [(-2188,0),(-2127,math.pi)]:
  for x in [1976,1986,1996,2006]:cabana(x,z,yaw)
 for z,yaw in [(-2180,0),(-2143,math.pi)]:
  for x in [1977,1980,1983,1986,1989,1992,1995,1998,2001,2004,2007,2010]:lounger(x,z,yaw)
 for i,(x,z) in enumerate([(1962,-2179),(1962,-2154),(2023,-2180),(2023,-2154),(1969,-2126),(2014,-2126),(1969,-2190),(2014,-2190)]):palm(x,z,i)
 routes=[{'name':'south-deck','points':[[1973,Y,-2184],[2012,Y,-2184]]},{'name':'north-deck','points':[[1973,Y,-2132],[2012,Y,-2132]]},{'name':'east-pavilion','points':[[2015,Y,-2178],[2015,Y,-2170],[2015,Y,-2162]]},{'name':'cabana','points':[[1986,Y,-2183],[1986,Y,-2187]]}]
 Path('docs/project-records/westgate-amenities/routes.json').write_text(json.dumps(routes,indent=2)+'\n')
 return dict(pavilions=3,cabanas=8,loungers=24,palms=8,elevation=Y,uncertainty='Photo-fitted sizes and reduced density. Existing pool footprint, elevation, podium and towers preserved. No interior connection inferred.')
if __name__=='__main__':
 B=Meshes();d=build(B);B.save_all();d['triangles']=sum(len(g['faces']) for g in B.groups.values());Path('docs/project-records/westgate-amenities/geometry.json').write_text(json.dumps(d,indent=2)+'\n');print(d)
