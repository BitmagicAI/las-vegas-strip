"""Original fabric detailing for nine mapped north-lagoon cabanas.
Official MGM gazebo photograph supports valances, rear screens and tied curtains.
Mapped footprints retained; tan palette and fabric dimensions are inferred.
"""
from common import *
IDS={'way/'+s for s in ['399554413','399554417','399554437','399554441','399554415','399554421','399554439','399554436','399554438']}
def detail(B,ident,p,water):
 if ident not in IDS:return
 # The closest edge faces the lagoon; leave its central entrance completely open.
 for poly in parts(p):
  ps=list(poly.exterior.coords)[:-1]
  edges=list(zip(ps,ps[1:]+ps[:1]))
  front=min(range(len(edges)),key=lambda i:LineString(edges[i]).centroid.distance(water))
  for i,(a,b) in enumerate(edges):
   dx,dz=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dz)
   # Closed thin boxes give fabric backs/undersides without alpha shaders.
   yaw=math.atan2(-dz,dx);F=Frame(B,a[0],a[1],yaw,0)
   F.box('mcr-valance',(length/2,3.36,0),(length,.28,.045))
   if i!=front:
    F.box('mcr-screen',(length/2,1.98,0),(length-.14,2.56,.035))
   else:
    # Bunched curtains at the two posts; no geometry crosses the opening.
    for x in [.12,length-.12]:
     F.box('mcr-curtain',(x,1.98,0),(.19,2.56,.12))
     F.box('mcr-tie',(x,1.55,-.075),(.21,.07,.035))
