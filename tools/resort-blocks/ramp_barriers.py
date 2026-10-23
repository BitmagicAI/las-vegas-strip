"""Continuous concrete guard strips; no exposed end caps at segment seams."""
import math

def barrier(b,a,c,height=1.05,thickness=.36,material='lake-cream'):
 if math.hypot(c[0]-a[0],c[2]-a[2])<1e-6:return
 if not hasattr(b,'guard_sections'):b.guard_sections=[]
 b.guard_sections.append(dict(a=a,c=c,height=height,thickness=thickness,material=material,source=b.source,detail=b.detail,property=b.property))

def finish_barriers(b):
 sections=b.guard_sections;ends={};b.ramp_barriers=[]
 def key(p):return tuple(round(v,4) for v in p)
 for s in sections:
  dx,dz=s['c'][0]-s['a'][0],s['c'][2]-s['a'][2];le=math.hypot(dx,dz);s['normal']=(-dz/le,dx/le)
  for name in ['a','c']:ends.setdefault(key(s[name]),[]).append(s)
 for s in sections:
  b.source=s['source'];b.detail=s['detail'];b.property=s['property']
  offsets=[]
  for name in ['a','c']:
   linked=ends[key(s[name])];nx,nz=s['normal']
   if len(linked)==2:
    other=next(v for v in linked if v is not s);ox,oz=other['normal']
    # Align by traversal, not by angle: an obtuse bend is still
    # continuous. Flipping based on dot product split its shared corners.
    other_name='a' if key(other['a'])==key(s[name]) else 'c'
    if other_name==name:ox,oz=-ox,-oz
    mx,mz=nx+ox,nz+oz;le=math.hypot(mx,mz);mx,mz=mx/le,mz/le
    scale=min(2,1/max(.5,mx*nx+mz*nz));nx,nz=mx*scale,mz*scale
   offsets.append((nx*s['thickness']/2,nz*s['thickness']/2))
  pts=[]
  for dy in [-.06,s['height']]:
   for index,side in [(0,-1),(1,-1),(1,1),(0,1)]:
    p=s['a' if index==0 else 'c'];nx,nz=offsets[index];pts.append((p[0]+side*nx,p[1]+dy,p[2]+side*nz))
  faces=[(0,3,2,1),(4,5,6,7),(0,1,5,4),(2,3,7,6)]
  if len(ends[key(s['c'])])!=2:faces.append((1,2,6,5))
  if len(ends[key(s['a'])])!=2:faces.append((3,0,4,7))
  for face in faces:b.face(s['material'],[pts[i] for i in reversed(face)],True)
  b.ramp_barriers.append(dict(a=list(s['a']),c=list(s['c']),source=s['source'],mid=[(s['a'][i]+s['c'][i])/2-.06*(i==1) for i in range(3)],normal=s['normal'],height=s['height'],thickness=s['thickness']))
