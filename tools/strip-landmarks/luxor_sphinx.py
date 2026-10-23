"""Local Sphinx sculpture from the surveyed outline and Earth2022 frontage.
Anatomy and the 35m crown elevation are authored estimates, not scan geometry.
"""
from common import *
IDS=['way/118344867','way/118344869','way/118344870']
Z=2284.8
def ellipsoid(B,c,r,mat='luxor-sculpt-stone',face=False):
 def point(v,u):
  sy=math.cos(v);sv=math.sin(v);x=c[0]+r[0]*sv*math.cos(u);y=c[1]+r[1]*sy;z=c[2]+r[2]*sv*math.sin(u)
  if face and math.cos(u)>0:
   dz=z-Z
   gauss=lambda yy,zz,wy,wz:math.exp(-((y-yy)/wy)**2-((dz-zz)/wz)**2)
   x+=max(0,math.cos(u))**4*(1.7*gauss(27.8,0,1.8,.65)+.5*gauss(25.1,0,.5,2)-.4*gauss(30,2,.5,1)-.4*gauss(30,-2,.5,1)+.35*gauss(30.8,2,.35,1.5)+.35*gauss(30.8,-2,.35,1.5))
  return x,y,z
 n=72 if face else 48;m=48 if face else 24
 for j in range(m):
  for i in range(n):
   u=i*math.tau/n;un=(i+1)*math.tau/n;v=j*math.pi/m;vn=(j+1)*math.pi/m
   if j==0:B.face(mat,[point(v,u),point(vn,u),point(vn,un)])
   elif j==m-1:B.face(mat,[point(v,u),point(vn,u),point(v,un)])
   else:B.face(mat,[point(v,u),point(vn,u),point(vn,un),point(v,un)])
def loft_body(B,sections):
 # Continuous carved mass with flattened sides, avoiding intersecting round joints.
 n=64
 def ring(q,u):
  x,y,ry,rz=q;co=math.cos(u);si=math.sin(u)
  return (x,y+ry*math.copysign(abs(co)**.7,co),Z+rz*math.copysign(abs(si)**.7,si))
 for a,b in zip(sections,sections[1:]):
  for k in range(n):
   u=k*math.tau/n;v=(k+1)*math.tau/n;B.face('luxor-sculpt-stone',[ring(a,u),ring(b,u),ring(b,v),ring(a,v)])
def face_head(B):
 # Pharaoh's planar cheeks, square jaw, brow ridges, sockets and nasal bridge.
 sections=[(23.3,2.3,2.8),(24,3.6,3.8),(25.4,4.1,4.2),(27,4.6,4.5),(29,4.6,4.5),(31,4.3,4.1),(33,3.8,3.5),(34.4,2.8,2.5),(35,.2,.2)]
 def pt(y,w,d,u):
  z=w*math.sin(u);x=-110+d*math.cos(u)
  if math.cos(u)>0:
   def g(yy,zz,a,b):return math.exp(-((y-yy)/a)**2-((z-zz)/b)**2)
   x+=math.cos(u)**4*(2.5*g(28,0,1.8,.55)+1.1*g(26.8,0,.6,1.05)-.65*g(29.4,2,.65,1.2)-.65*g(29.4,-2,.65,1.2)+.7*g(30.3,2,.35,1.5)+.7*g(30.3,-2,.35,1.5)+.5*g(25.4,0,.45,1.7))
  return (x,y,Z+z)
 for a,b in zip(sections,sections[1:]):
  for j in range(6):
   aa=[a[i]+(b[i]-a[i])*j/6 for i in range(3)];bb=[a[i]+(b[i]-a[i])*(j+1)/6 for i in range(3)]
   for k in range(96):
    u=k*math.tau/96;v=(k+1)*math.tau/96;B.face('luxor-sculpt-stone',[pt(*aa,u),pt(*bb,u),pt(*bb,v),pt(*aa,v)])
 for side in [-1,1]:
  z=side*2
  # Incised eyes sit in the recessed sockets; upper/lower carved lids enclose them.
  outline=[(-106.35,29.4+.3*math.sin(t),Z+z+1.02*math.cos(t)) for t in np.linspace(0,math.tau,25)]
  B.face('luxor-sculpt-shadow',outline[:-1])
  B.path('luxor-sculpt-stone',outline,.13,8)
  ellipsoid(B,(-109,28.6,Z+side*4.7),(.65,1.8,.65))
  ellipsoid(B,(-103.3,26.7,Z+side*.65),(.14,.13,.23),'luxor-sculpt-shadow')
 B.path('luxor-sculpt-shadow',[(-105.1,25.1+.12*math.cos(t*math.pi),Z-1.55+3.1*t) for t in np.linspace(0,1,25)],.085,8)
 B.path('luxor-sculpt-stone',[(-105.02,25.35+.16*math.cos(t*math.pi*2),Z-1.5+3*t) for t in np.linspace(0,1,25)],.16,8)
 B.path('luxor-sculpt-stone',[(-105.12,24.92-.18*math.sin(t*math.pi),Z-1.5+3*t) for t in np.linspace(0,1,25)],.17,8)

def exterior(B):
 B.property='luxorExterior-exterior';B.detail=0;B.source='luxor-sphinx-base'
 p=footprint(IDS[0]);plinth=p.buffer(.65,join_style=2)
 B.extrude('luxor-stone',plinth,.24,1.2,True)
 for pp in parts(plinth):
  for a,b in zip(list(pp.exterior.coords),list(pp.exterior.coords)[1:]):
   B.tube('luxor-band',(a[0],1.28,a[1]),(b[0],1.28,b[1]),.15,4)
 B.source='luxor-sphinx-sculpt'
 loft_body(B,[(-154,7,.3,.3),(-149,8,6.8,10),(-138,9,8,12),(-124,10,9,11.3),(-115,10.5,9.5,10),(-108,9,7.5,8.5),(-106,7,.2,.2)])
 for dz in [-8.2,8.2]:
  ellipsoid(B,(-91.5,3.8,Z+dz),(18,2.6,4.6))
  ellipsoid(B,(-108,7.5,Z+dz),(6.8,6,4.5))
  for off in [-2.8,-.9,.9,2.8]:
   ellipsoid(B,(-75.8,2.8,Z+dz+off),(2.5,1.0,.88))
 ellipsoid(B,(-113.5,21,Z),(4.7,6.3,5.2))
 # Nemes headdress has a face opening; horizontal blue/ochre bands follow its folds.
 rings=[(18,9.2,5),(21,10,6),(25,9,6.6),(29,8.4,6.5),(32,6.8,5.8),(34,5.3,4.5),(35.4,2.4,2.3),(35.6,.15,.15)]
 for j in range(len(rings)-1):
  y0,w0,d0=rings[j];y1,w1,d1=rings[j+1];steps=max(1,round((y1-y0)/.36))
  for k in range(steps):
   t0=k/steps;t1=(k+1)/steps
   def pt(t,u):return (-112+(d0+(d1-d0)*t)*math.cos(u),y0+(y1-y0)*t,Z+(w0+(w1-w0)*t)*math.sin(u))
   lower=j<5;start=.9 if lower else 0;end=math.tau-.9 if lower else math.tau
   for i in range(64):
    u=start+(end-start)*i/64;v=start+(end-start)*(i+1)/64
    B.face('luxor-sculpt-blue' if int((y0+(y1-y0)*t0)*2.5)%2==0 else 'luxor-sculpt-gold',[pt(t0,u),pt(t1,u),pt(t1,v),pt(t0,v)])
 face_head(B)
 # Narrow tapered ceremonial beard, carved collar and forehead cobra.
 B.tube('luxor-sculpt-gold',(-105.8,20,Z),(-105.5,23.7,Z),.55,12,1)
 for y in np.arange(20.3,23.7,.32):B.tube('luxor-sculpt-shadow',(-105.8,y,Z-.45),(-105.8,y,Z+.45),.035,6)
 ellipsoid(B,(-107.2,33.7,Z),(.55,1.2,.55),'luxor-sculpt-gold')
 # Simple body collision, independent of the sculpt's many visual triangles.
 C=Meshes();C.property=B.property
 C.box('x',(-134,6,Z),(37,9.6,24),True)
 for dz in [-8.2,8.2]:C.box('x',(-92,3.4,Z+dz),(34,4.4,9),True)
 c=B.solids[B.property];n=len(c['vertices'])//3;cc=C.solids[B.property];c['vertices'].extend(cc['vertices']);c['indices'].extend(i+n for i in cc['indices'])
 B.source='luxor-sphinx-arrival'
 # Rear entrance attachment is a distinct low roof, not part of the sculpture.
 p=footprint(IDS[2]);B.shell(p,.24,7.4,'luxor-stone',roof=False);B.planar('luxor-membrane-paint',p,7.4)
 return IDS
