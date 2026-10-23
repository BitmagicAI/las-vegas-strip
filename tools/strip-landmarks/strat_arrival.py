"""South motor-court marquee from Google Earth 2022-11-09 and entry photos.
Position follows the two mapped projecting wings. Elevations are photo estimates.
No road, hotel interior, portal or observation geometry is changed.
"""
from common import *
from forum_shops import facade_frame

def arrival(B):
 B.source='strat-south-arrival';B.detail=0
 shape=footprint('way/135456188')
 # This chord sits outside a concave facade, so polygon containment cannot
 # infer its outward normal. Use the surveyed south-east arrival direction.
 L=math.dist((1503.565,-3425.679),(1533.367,-3444.526))
 F=Frame(B,1533.367,-3444.526,math.atan2(-.5344933184,-.8451726999),y=0)
 # Two tapered masonry shoulders flank a tall clear vehicle undercroft.
 for x in [1.7,L-1.7]:
  a=[F.p(x-1.65,0,-12.2),F.p(x+1.65,0,-12.2),F.p(x+1.65,0,2),F.p(x-1.65,0,2)]
  b=[F.p(x-1.8,5.8,-12.2),F.p(x+1.8,5.8,-12.2),F.p(x+1.8,18.7,2),F.p(x-1.8,18.7,2)]
  for i in range(4):B.face('st-white',[a[i],a[(i+1)%4],b[(i+1)%4],b[i]],True)
  B.face('st-white',b,True)
 # Canopy slab sits over the drive, leaving the lane clear underneath.
 canopy=F.poly([(3.35,-8.5),(L-3.35,-8.5),(L-3.35,2),(3.35,2)])
 B.planar('st-flat-roof',canopy,8.65,True)
 for poly in parts(canopy):
  for t in triangles(poly):B.face('st-grey',[(x,8.15,z) for x,z in list(t.exterior.coords)[:-1]][::-1],True)
 for z in [-8.5,2]:F.box('st-white',(L/2,8.4,z),(L-6.7,.5,.45),True)
 # Concave digital marquee above the arrival; a static, subdued panel avoids
 # both billboarding and adding lights to the running scene.
 steps=24
 def front(t,y):return F.p(3.6+(L-7.2)*t,y,-2.65-2.0*math.sin(math.pi*t))
 for i in range(steps):
  t=i/steps;u=(i+1)/steps
  B.face('st-panel-dark',[front(t,9.2),front(u,9.2),front(u,16.4),front(t,16.4)])
  for y in [9.0,16.5]:B.tube('st-grey',front(t,y),front(u,y),.13,6)
 F.text('THE STRAT',(L/2,17.3,-8.8),1.7,'st-blue')
 # Two bounded planting pockets outside the centre vehicle lane.
 for x in [0,L]:
  p=F.p(x,.25,-14.3)
  ring=Point(p[0],p[2]).buffer(2.05,resolution=16)
  B.shell(ring,.12,.5,'st-planter',solid=True)
  B.planar('st-soil',ring.buffer(-.2),.53)
 # Minimal downlight lenses are geometry only; existing site light pool owns illumination.
 for x in np.linspace(6,L-6,5):
  F.box('st-white',(x,8.10,-4.5),(.35,.035,.7))
