"""Original shallow segmented hip/ridge caps; inferred .26m width/.10m rise.
Visual only: fit existing roof heights, never modify support/collision geometry.
"""
from common import *
def caps(B,mat,points):
 for start,end in zip(points,points[1:]):
  a=np.array(start,float);b=np.array(end,float);delta=b-a;length=float(np.linalg.norm(delta))
  if length<.01:continue
  side=np.array([-delta[2],0,delta[0]],float);side/=np.linalg.norm(side)
  count=max(1,math.ceil(length/.45))
  for i in range(count):
   lo=a+delta*(i/count);hi=a+delta*((i+1)/count-.008/count)
   profile=[(-.13,.015),(-.085,.085),(0,.115),(.085,.085),(.13,.015)]
   front=[tuple(lo+side*x+np.array([0,y,0])) for x,y in profile]
   back=[tuple(hi+side*x+np.array([0,y,0])) for x,y in profile]
   for j in range(4):B.face(mat,[front[j],front[j+1],back[j+1],back[j]])
