"""SAHARA 2022 porte cochere. Columns: Moz project dimensions; plan/roof estimated.
Reference images are visual evidence only, not textures. No new scene lights.
"""
from common import *
CX,CZ=1371,-2904
RX,RZ=31,28
EDGE=7.55

def ceiling(x,z):
 r=min(1,math.hypot((x-CX)/RX,(z-CZ)/RZ))
 return EDGE+3.5*(1-r*r)

def arrival(B):
 B.source='sahara-arrival'
 # Closed roof section: finished soffit under the shallow curving membrane.
 for i in range(128):
  a=i*math.tau/128;b=(i+1)*math.tau/128
  def p(t,r,dy=0):
   x,z=CX+RX*r*math.cos(t),CZ+RZ*r*math.sin(t)
   return (x,ceiling(x,z)+dy,z)
  for lo,hi in zip(np.linspace(0,1,17)[:-1],np.linspace(0,1,17)[1:]):
   top=[p(a,lo,.55),p(a,hi,.55),p(b,hi,.55),p(b,lo,.55)]
   bottom=[p(a,lo),p(a,hi),p(b,hi),p(b,lo)]
   B.upface('sa-flat-roof',top,True)
   # Downward normal, including collision from underneath.
   if np.cross(np.array(bottom[1])-bottom[0],np.array(bottom[2])-bottom[0])[1]>0:bottom.reverse()
   B.face('sa-soffit',bottom,True)
  B.face('sa-trim',[p(a,1),p(a,1,.55),p(b,1,.55),p(b,1)])
 # Deep diamond ceiling ribs clipped to the elliptical roof; local architectural beams.
 roof=scale(Point(CX,CZ).buffer(1,96),xfact=RX*.97,yfact=RZ*.97,origin=(CX,CZ))
 for direction in [-1,1]:
  for off in np.arange(-42,43,8):
   line=LineString([(CX-50,CZ+off-direction*50),(CX+50,CZ+off+direction*50)]).intersection(roof)
   if line.is_empty or line.geom_type!='LineString':continue
   count=max(2,math.ceil(line.length/1.8));points=[line.interpolate(i/count,normalized=True) for i in range(count+1)]
   for aa,bb in zip(points,points[1:]):
    dx,dz=bb.x-aa.x,bb.y-aa.y;L=math.hypot(dx,dz);nx,nz=-dz/L*.18,dx/L*.18
    A=[(aa.x-nx,ceiling(aa.x,aa.y)-.52,aa.y-nz),(aa.x+nx,ceiling(aa.x,aa.y)-.52,aa.y+nz)]
    C=[(bb.x-nx,ceiling(bb.x,bb.y)-.52,bb.y-nz),(bb.x+nx,ceiling(bb.x,bb.y)-.52,bb.y+nz)]
    B.face('sa-wood',[A[0],C[0],C[1],A[1]])
    for k in range(2):B.face('sa-wood',[A[k],C[k],(C[k][0],C[k][1]+.50,C[k][2]),(A[k][0],A[k][1]+.50,A[k][2])])
 # Ten tapered wood-look column covers, 24ft tall, diameter3ft10in ->6ft.
 # Positions estimated from completed photos; each is outside the drive-through lanes.
 for i in range(10):
  a=(i+.5)*math.tau/10;x=CX+28.25*math.cos(a);z=CZ+25.5*math.sin(a)
  for j in range(32):
   t=j*math.tau/32;tt=(j+1)*math.tau/32
   B.face('sa-wood',[(x+.5842*math.cos(t),0,z+.5842*math.sin(t)),(x+.5842*math.cos(tt),0,z+.5842*math.sin(tt)),(x+.9144*math.cos(tt),7.3152,z+.9144*math.sin(tt)),(x+.9144*math.cos(t),7.3152,z+.9144*math.sin(t))],True)
  B.lathe('sa-champagne',(x,z),[(7.28,.94),(ceiling(x,z),.94)],32)
  # Narrow geometric diagonal reveals, not dynamically created lights.
  for sign in [-1,1]:
   pts=[]
   for y in np.linspace(.16,7.16,35):
    t=sign*y*.58+i*.31;r=.5842+(.9144-.5842)*y/7.3152+.018
    pts.append((x+r*math.cos(t),y,z+r*math.sin(t)))
   B.path('sa-blue-reveal',pts,.018,4)
 # Four champagne columns surround the central shallow water feature.
 island=scale(Point(CX,CZ).buffer(1,64),xfact=6.2,yfact=4.8,origin=(CX,CZ))
 B.shell(island,0,.72,'sa-basin',roof=False)
 B.planar('sa-basin',island.buffer(.15).difference(island.buffer(-.3)),.76,True)
 B.planar('sa-basin',island,.18,True)
 B.planar('sahara_pool',island.buffer(-.3),.60)
 for a in [math.pi*.25,math.pi*.75,math.pi*1.25,math.pi*1.75]:
  x=CX+4.8*math.cos(a);z=CZ+3.5*math.sin(a)
  col=Point(x,z).buffer(.3048,16);B.shell(col,.65,10.3632,'sa-champagne',roof=False)
  for y in [3.5,7]:B.lathe('sa-joint',(x,z),[(y,.311),(y+.035,.311)],32)
 # Ringed suspended tubes visible in supplier photo, architectural water feature.
 ring=Point(CX,CZ).buffer(5.8,48).difference(Point(CX,CZ).buffer(4.0,48))
 B.planar('sa-champagne',ring,10.35)
 for j in range(24):
  a=j*math.tau/24;r=2.2+(j%3)*.55;x=CX+r*math.cos(a);z=CZ+r*math.sin(a);bottom=5.7+(j%5)*.44
  B.tube('sa-champagne',(x,bottom+1.1,z),(x,10.35,z),.045,8)
  B.lathe('sa-blue-reveal',(x,z),[(bottom,.24),(bottom+1.1,.24)],16)
 # Separate boulevard pylon, restrained branded content rather than invented advertising.
 B.source='sahara-pylon';F=Frame(B,1360,-2937,math.pi/2,y=0)
 for x in [-2.9,2.9]:F.box('sa-white',(x,7.2,0),(2.7,14.4,2.1),True)
 F.box('sa-white',(0,15.3,0),(8.5,1.8,2.1),True)
 F.box('sa-screen',(0,25.4,-.01),(8.5,18.4,2.13),True)
 F.box('sa-white',(0,35.8,0),(8.5,2.4,2.1),True)
 F.text('SAHARA',(0,35.7,-1.12),1.2,'sa-gold')
 F.text('S',(0,26,-1.13),4.2,'sa-gold')
 F.text('LAS VEGAS',(0,21,-1.13),.55,'sa-white')
