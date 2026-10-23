"""Guard faces must point out of the solid, including top and bottom."""
import numpy as np
from ramp_barriers import barrier,finish_barriers
class Collector:
 source='test';detail=0;property='test'
 def __init__(self):self.faces=[]
 def face(self,material,pts,solid):
  assert solid;self.faces.append(np.array(pts))
for a,c in [((0,0,0),(5,0,0)),((5,2,4),(-3,1,-2)),((0,0,0),(0,1,5))]:
 b=Collector();barrier(b,a,c);finish_barriers(b)
 center=(np.array(a)+np.array(c))/2+np.array([0,.495,0])
 for face in b.faces:
  normal=np.cross(face[1]-face[0],face[2]-face[0]);out=face.mean(axis=0)-center
  assert normal@out>0,('Inward collision normal',a,c,face.tolist())
print('18 guard faces point outward; top/bottom and both rail directions passed.')

# Shared corners must match through obtuse bends, including reversed input.
import math
for angle in [35,89,100,139,162]:
 for reverse in [False,True]:
  b=Collector();a=(0,0,0);joint=(5,1,0)
  c=(5+5*math.cos(math.radians(angle)),2,5*math.sin(math.radians(angle)))
  barrier(b,a,joint)
  barrier(b,*( (c,joint) if reverse else (joint,c)))
  finish_barriers(b)
  # Each strip has 4 sides plus one end cap. Compare the shared cross-section.
  def section(faces):
   vertices={tuple(np.round(p,8)) for f in faces for p in f if abs(p[1]-.94)<1e-7 or abs(p[1]-2.05)<1e-7}
   return vertices
  assert section(b.faces[:5])==section(b.faces[5:]),('Split miter',angle,reverse)
print('10 acute/obtuse and reversed-input shared joints are watertight.')
