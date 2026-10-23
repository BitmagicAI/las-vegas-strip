"""Twin swept terrace stairs. Reference-led silhouette, provisional dimensions.
Smooth ramp colliders are separate from noncolliding visual treads.
"""
import math
import numpy as np

def barrier(B,pts):
 """Collision-only balustrade infill; independent of visual/LOD geometry."""
 c=B.solids[B.property];n=len(c['vertices'])//3
 c['vertices'].extend(float(v) for p in pts for v in p)
 c['indices'].extend(j for i in range(1,len(pts)-1) for j in [n,n+i,n+i+1])

def center(t,side):
 u=1-t
 x=2*u**3+3*10*u*u*t+3*12*u*t*t+12*t**3
 z=-18*u**3-3*18*u*u*t-3*14*u*t*t-8.45*t**3
 return side*x,z

def edge(t,side,across):
 x,z=center(t,side);a=center(max(0,t-.001),side);b=center(min(1,t+.001),side)
 dx,dz=b[0]-a[0],b[1]-a[1];L=math.hypot(dx,dz)
 return x-dz/L*across,z+dx/L*across

def stairs(B,F):
 routes=[]
 for side in [-1,1]:
  route=[]
  for t in np.linspace(0,1,81):
   x,z=center(t,side);route.append(F.p(x,3*t,z))
  routes.append(route)
  for t,q in zip(np.linspace(0,1,81),np.linspace(0,1,81)[1:]):
   a,b=edge(t,side,-1.55),edge(t,side,1.55);c,d=edge(q,side,-1.55),edge(q,side,1.55)
   B.upface('stone',[F.p(a[0],3*t,a[1]),F.p(c[0],3*q,c[1]),F.p(d[0],3*q,d[1]),F.p(b[0],3*t,b[1])],True)
  # 19 even risers; treads are visual only, avoiding collision snags.
  for i in range(19):
   t,q=i/19,(i+1)/19;hi=3*q;lo=3*t
   a,b=edge(t,side,-1.55),edge(t,side,1.55);c,d=edge(q,side,-1.55),edge(q,side,1.55)
   B.upface('marble',[F.p(a[0],hi+.012,a[1]),F.p(c[0],hi+.012,c[1]),F.p(d[0],hi+.012,d[1]),F.p(b[0],hi+.012,b[1])])
   B.face('ivory',[F.p(a[0],lo,a[1]),F.p(b[0],lo,b[1]),F.p(b[0],hi,b[1]),F.p(a[0],hi,a[1])])
  for across in [-1.7,1.7]:
   for t,q in zip(np.linspace(0,1,65),np.linspace(0,1,65)[1:]):
    a,b=edge(t,side,across),edge(q,side,across)
    # Solid low parapet and narrow coping following the same smooth sweep.
    B.face('sandstone',[F.p(a[0],0,a[1]),F.p(b[0],0,b[1]),F.p(b[0],3*q+.20,b[1]),F.p(a[0],3*t+.20,a[1])],True)
    barrier(B,[F.p(a[0],3*t+.18,a[1]),F.p(b[0],3*q+.18,b[1]),F.p(b[0],3*q+1.15,b[1]),F.p(a[0],3*t+1.15,a[1])])
    F.tube('ivory',(a[0],3*t+1.15,a[1]),(b[0],3*q+1.15,b[1]),.10,6)
   B.detail=1
   for t in np.linspace(0,1,35):
    x,z=edge(t,side,across);y=3*t
    F.lathe('ivory',x,z,[(y+.2,.1),(y+.35,.14),(y+.6,.07),(y+.9,.11),(y+1.08,.07)],10)
   B.detail=0
 return routes
