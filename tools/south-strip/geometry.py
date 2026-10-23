"""Batched, metre-scale mesh primitives. Coordinates are game X/Y/Z."""
import math,json,numpy as np
from collections import defaultdict
from shapely.geometry import Polygon
from shapely.ops import triangulate
from pathlib import Path
class Builder:
 def __init__(self): self.groups={};self.solids=defaultdict(lambda:dict(vertices=[],indices=[]));self.property='new-york';self.source='';self.detail=0;self.labels=[]
 def face(self,mat,pts,solid=False):
  g=self.groups.setdefault((self.property,self.source,mat,self.detail),dict(property=self.property,source=self.source,material=mat,detail=self.detail,vertices=[],faces=[]));n=len(g['vertices']);g['vertices'].extend([list(map(float,p)) for p in pts]);fs=[[n,n+i,n+i+1] for i in range(1,len(pts)-1)];g['faces'].extend(fs)
  if solid:
   c=self.solids[self.property];n=len(c['vertices'])//3;c['vertices'].extend(float(v) for p in pts for v in p);c['indices'].extend(j for i in range(1,len(pts)-1) for j in [n,n+i,n+i+1])
 def box(self,mat,c,size,solid=False,yaw=0):
  cx,cy,cz=c;w,h,d=[v/2 for v in size];co,si=math.cos(yaw),math.sin(yaw);pts=[(cx+x*co+z*si,cy+y,cz-x*si+z*co) for x,y,z in [(-w,-h,-d),(w,-h,-d),(w,h,-d),(-w,h,-d),(-w,-h,d),(w,-h,d),(w,h,d),(-w,h,d)]]
  for ids in [(0,3,2,1),(4,5,6,7),(0,4,7,3),(1,2,6,5),(3,7,6,2),(0,1,5,4)]:self.face(mat,[pts[i] for i in ids],solid)
 def tube(self,mat,a,b,r=.15,n=8,r2=None):
  a,b=np.array(a,float),np.array(b,float);v=b-a;v/=max(.0001,np.linalg.norm(v));up=np.array([0.,1.,0.]) if abs(v[1])<.95 else np.array([1.,0.,0.]);u=np.cross(v,up);u/=np.linalg.norm(u);w=np.cross(v,u);r2=r if r2 is None else r2
  aa=[a+r*(u*math.cos(t)+w*math.sin(t)) for t in np.linspace(0,math.tau,n,endpoint=False)];bb=[b+r2*(u*math.cos(t)+w*math.sin(t)) for t in np.linspace(0,math.tau,n,endpoint=False)]
  for i in range(n):j=(i+1)%n;self.face(mat,[aa[i],aa[j],bb[j],bb[i]])
  self.face(mat,aa[::-1]);self.face(mat,bb)
 def lathe(self,mat,c,profile,n=32):
  x,z=c
  for (y,r),(yy,rr) in zip(profile,profile[1:]):
   for i in range(n):
    a=i*math.tau/n;b=(i+1)*math.tau/n;self.face(mat,[(x+r*math.cos(a),y,z+r*math.sin(a)),(x+r*math.cos(b),y,z+r*math.sin(b)),(x+rr*math.cos(b),yy,z+rr*math.sin(b)),(x+rr*math.cos(a),yy,z+rr*math.sin(a))])
 def sphere(self,mat,c,r,n=20,m=12,scale=(1,1,1)):
  cx,cy,cz=c
  def pt(a,b):return (cx+r*scale[0]*math.cos(a)*math.cos(b),cy+r*scale[1]*math.sin(b),cz+r*scale[2]*math.sin(a)*math.cos(b))
  for j in range(m):
   b=-math.pi/2+j*math.pi/m;bb=b+math.pi/m
   for i in range(n):a=i*math.tau/n;aa=a+math.tau/n;self.face(mat,[pt(a,b),pt(aa,b),pt(aa,bb),pt(a,bb)])
 def extrude(self,mat,poly,lo,hi,solid=True,roof_solid=None):
  if poly.is_empty:return
  if poly.geom_type!='Polygon':
   for q in poly.geoms:self.extrude(mat,q,lo,hi,solid,roof_solid)
   return
  for ring in [poly.exterior,*poly.interiors]:
   ps=list(ring.coords)
   for a,b in zip(ps,ps[1:]):self.face(mat,[(a[0],lo,a[1]),(b[0],lo,b[1]),(b[0],hi,b[1]),(a[0],hi,a[1])],solid)
  for t in triangulate(poly):
   if poly.covers(t.representative_point()):self.face(mat,[(x,hi,z) for x,z in list(t.exterior.coords)[:-1]],solid if roof_solid is None else roof_solid)
 def text(self,text,p,size=1,yaw=0,mat='ivory'):self.labels.append(dict(property=self.property,source=self.source,text=text,position=p,size=size,yaw=yaw,material=mat))
 def save(self,path):Path(path).write_text(json.dumps(dict(meshes=list(self.groups.values()),labels=self.labels),separators=(',',':'),default=lambda v:v.item()))
