"""Subtract an axis-aligned box from a convex face, retaining interpolated UVs."""
def subtract_box(face,lo,hi):
 if any(max(p[i] for p in face)<=lo[i] or min(p[i] for p in face)>=hi[i] for i in range(3)):return [face]
 inside=face;out=[]
 for axis,limit,sign in [(i,v,s) for i in range(3) for v,s in [(lo[i],1),(hi[i],-1)]]:
  if not inside:break
  yes=[];no=[]
  for j,a in enumerate(inside):
   b=inside[(j+1)%len(inside)];da=(a[axis]-limit)*sign;db=(b[axis]-limit)*sign
   (yes if da>=0 else no).append(a)
   if (da>=0)!=(db>=0):
    t=da/(da-db);v=[x+(y-x)*t for x,y in zip(a,b)];yes.append(v);no.append(v)
  if len(no)>=3:out.append(no)
  inside=yes
 return out

def subtract_boxes(face,boxes):
 faces=[face]
 for lo,hi in boxes:faces=[p for f in faces for p in subtract_box(f,lo,hi)]
 return faces

def convex_triangles(flat):
 import math,itertools
 v=[flat[i:i+3] for i in range(0,len(flat),3)];faces={}
 sub=lambda a,b:[x-y for x,y in zip(a,b)]
 dot=lambda a,b:sum(x*y for x,y in zip(a,b))
 cross=lambda a,b:[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]]
 for a,b,c in itertools.combinations(range(len(v)),3):
  n=cross(sub(v[b],v[a]),sub(v[c],v[a]));length=math.sqrt(dot(n,n))
  if length<1e-8:continue
  n=[x/length for x in n];ds=[dot(n,sub(p,v[a])) for p in v]
  if min(ds)<-1e-6 and max(ds)>1e-6:continue
  if max(ds)>1e-6:n=[-x for x in n]
  ids=tuple(i for i,d in enumerate(ds) if abs(d)<1e-6)
  if ids in faces:continue
  center=[sum(v[i][k] for i in ids)/len(ids) for k in range(3)];u=sub(v[ids[0]],center);w=cross(n,u)
  ring=sorted(ids,key=lambda i:math.atan2(dot(sub(v[i],center),w),dot(sub(v[i],center),u)))
  faces[ids]=[x for j in range(1,len(ring)-1) for x in [ring[0],ring[j],ring[j+1]]]
 return [i for f in faces.values() for i in f]
