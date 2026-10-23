"""Local, metre-scale landmark authoring; batched surfaces, separate collision."""
import sys,math,json,random
from pathlib import Path
sys.path.insert(0,'build/south-strip/python')
sys.path.insert(0,'tools/south-strip')
sys.path.insert(0,'tools/geographic-strip')
import numpy as np
from shapely.geometry import Polygon,LineString,Point,box
from shapely.ops import unary_union
from shapely.affinity import rotate,translate,scale
from geometry import Builder
from surface_geometry import triangles
from building_surfaces import parts
OUT=Path('build/strip-landmarks');OUT.mkdir(parents=True,exist_ok=True)
SURVEY=json.load(open('build/strip-survey/survey.json'))['buildings'];BYID={f['id']:f for f in SURVEY}
def footprint(ident):
 f=BYID[ident]
 return unary_union([Polygon([(x,-z) for x,z in a[0]],[[(x,-z) for x,z in r] for r in a[1:]]).buffer(0) for a in f['polygons']])
class Meshes(Builder):
 def __init__(self):super().__init__();self.routes=[];self.portals=[];self.lights=[];self.zones=[];self.views={};self.seats=[]
 def upface(self,mat,pts,solid=False):
  a=np.array(pts,float)
  if np.cross(a[1]-a[0],a[2]-a[0])[1]<0:pts=list(reversed(pts))
  self.face(mat,pts,solid)
 def planar(self,mat,p,y,solid=False):
  for poly in parts(p):
   for tri in triangles(poly):self.upface(mat,[(x,y,z) for x,z in list(tri.exterior.coords)[:-1]],solid)
 def shell(self,p,lo,hi,mat,openings=(),roof=True,solid=True,interior=None):
  for poly in parts(p):
   for ring in [poly.exterior,*poly.interiors]:
    for a,b in zip(list(ring.coords),list(ring.coords)[1:]):
     line=LineString([a,b]);length=line.length
     if length<.01:continue
     region=box(0,lo,length,hi)
     for o in openings:
      point=Point(o['p'][0],o['p'][2])
      if 'yaw' in o:
       frame=Frame(self,point.x,point.y,o['yaw'])
       mask=frame.poly([(-o['width']/2,-3),(o['width']/2,-3),(o['width']/2,3),(-o['width']/2,3)])
       clipped=line.intersection(mask)
       pieces=list(clipped.geoms) if hasattr(clipped,'geoms') else [clipped]
       for piece in pieces:
        if piece.geom_type!='LineString' or piece.is_empty:continue
        ds=[line.project(Point(q)) for q in piece.coords];region=region.difference(box(min(ds),max(0,o['p'][1]-.15),max(ds),o['p'][1]+o['height']+.1))
      elif line.distance(point)<.75:
       at=line.project(point);region=region.difference(box(at-o['width']/2,0,at+o['width']/2,o['height']+.3))
     if interior:
      clipped=line.intersection(interior[0]);pieces=list(clipped.geoms) if hasattr(clipped,'geoms') else [clipped]
      for piece in pieces:
       if piece.geom_type!='LineString' or piece.is_empty:continue
       ds=[line.project(Point(q)) for q in piece.coords];region=region.difference(box(min(ds),0,max(ds),interior[1]))
     for q in parts(region):
      for tri in triangles(q):self.face(mat,[(line.interpolate(x).x,y,line.interpolate(x).y) for x,y in list(tri.exterior.coords)[:-1]],solid)
   if roof:self.planar('roof',poly,hi)
 def path(self,mat,points,r=.05,n=8):
  for a,b in zip(points,points[1:]):self.tube(mat,a,b,r,n)
 def arc(self,mat,c,r,lo=0,hi=math.tau,yaw=0,thick=.12,n=32):
  x,y,z=c;co,si=math.cos(yaw),math.sin(yaw)
  pts=[(x+co*r*math.cos(a),y+r*math.sin(a),z-si*r*math.cos(a)) for a in np.linspace(lo,hi,n+1)];self.path(mat,pts,thick)
 def save_all(self):
  for key in sorted(set(g['property'] for g in self.groups.values())):
   (OUT/(key+'.json')).write_text(json.dumps({'meshes':[g for g in self.groups.values() if g['property']==key],'labels':[g for g in self.labels if g['property']==key]},separators=(',',':')))
   (OUT/(key+'-collision.json')).write_text(json.dumps(self.solids[key],separators=(',',':')))
class Frame:
 def __init__(self,b,x,z,yaw=0,y=.24):self.b=b;self.x=x;self.z=z;self.y=y;self.yaw=yaw;self.co=math.cos(yaw);self.si=math.sin(yaw)
 def p(self,x,y,z):return (self.x+self.co*x+self.si*z,self.y+y,self.z-self.si*x+self.co*z)
 def poly(self,p):return Polygon([(self.p(x,0,z)[0],self.p(x,0,z)[2]) for x,z in p])
 def box(self,mat,c,size,solid=False):self.b.box(mat,self.p(*c),size,solid,self.yaw)
 def tube(self,mat,a,b,r=.05,n=8,r2=None):self.b.tube(mat,self.p(*a),self.p(*b),r,n,r2)
 def path(self,mat,p,r=.05,n=8):self.b.path(mat,[self.p(*q) for q in p],r,n)
 def text(self,text,p,size=.45,mat='letter',back=False):self.b.text(text,self.p(*p),size,-self.yaw+(math.pi if back else 0),mat)
 def lathe(self,mat,x,z,profile,n=20):p=self.p(x,0,z);self.b.lathe(mat,(p[0],p[2]),[(self.y+y,r) for y,r in profile],n)
 def arch(self,x,z,w,h,mat='ivory',thick=.14,base=0):
  r=w/2;spring=h-r
  for s in [-1,1]:self.box(mat,(x+s*r,(base+spring)/2,z),(thick*2,spring-base,thick*2))
  self.path(mat,[(x+r*math.cos(a),spring+r*math.sin(a),z) for a in np.linspace(0,math.pi,25)],thick)
 def portal(self,x=0,z=0,w=5,h=4.5,name='Entrance'):
  p=self.p(x,0,z);o=dict(p=p,yaw=self.yaw,width=w,height=h,name=name,venue=self.b.property.split('-')[0]);self.b.portals.append(o)
  for s in [-1,1]:self.box('steel',(x+s*(w/2+.06),h/2,z),(.12,h,.24))
  self.box('steel',(x,h+.06,z),(w+.24,.12,.24));return o
 def floor(self,w,d,z=0,mat='tile',y=0):self.box(mat,(0,y-.14,z),(w,.28,d),True)
 def rail(self,a,b,y=1.1,glass=False):
  self.tube('steel',(a[0],y,a[1]),(b[0],y,b[1]),.045)
  L=math.dist(a,b)
  for t in np.linspace(0,1,max(2,math.ceil(L/2.2)+1)):
   x,z=a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t;self.tube('steel',(x,0,z),(x,y,z),.037)
  if glass:self.b.face('glass',[self.p(a[0],.12,a[1]),self.p(b[0],.12,b[1]),self.p(b[0],y-.06,b[1]),self.p(a[0],y-.06,a[1])],True)
 def stairs(self,x,z,w,rise,run,y=0):
  steps=math.ceil(rise/.165)
  # Walkable ramp collision; visual treads do not create hundreds of colliders.
  self.b.face('stone',[self.p(x-w/2,y,z),self.p(x-w/2,y+rise,z+run),self.p(x+w/2,y+rise,z+run),self.p(x+w/2,y,z)],True)
  for i in range(steps):
   depth=run/steps;h=rise/steps
   self.box('stone',(x,y+(i+1)*h-.025,z+(i+.5)*depth),(w,.05,depth+.005))
   self.box('stone',(x,y+(i+.5)*h,z+i*depth),(w,h,.04))
  for side in [-1,1]:
   xx=x+side*(w/2-.08);self.tube('steel',(xx,y+1.05,z),(xx,y+rise+1.05,z+run),.055)
   for i in range(0,steps,4):
    zz=z+run*i/steps;yy=y+rise*i/steps;self.tube('steel',(xx,yy,zz),(xx,yy+1.05,zz),.045)
 def bench(self,x,z,mat='walnut'):
  self.box(mat,(x,.45,z),(2.2,.16,.65),True);self.box(mat,(x,.81,z+.26),(2.2,.65,.12))
  for s in [-1,1]:self.box('steel',(x+s*.8,.19,z),(.09,.38,.5))
 def plant(self,x,z,palm=False):
  self.lathe('charcoal',x,z,[(0,.65),(.1,.72),(.8,.61)],16)
  if palm:
   self.lathe('bark',x,z,[(.6,.19),(5.8,.12),(6.1,.1)],10)
   for j in range(11):
    a=j*math.tau/11
    for k in range(5):
     t=k/5;tt=(k+1)/5;rr=3*t;rr2=3*tt;yy=6.2+.9*math.sin(t*math.pi)-.9*t;yy2=6.2+.9*math.sin(tt*math.pi)-.9*tt
     self.b.face('foliage',[self.p(x+rr*math.cos(a)-.24*math.sin(a),yy,z+rr*math.sin(a)+.24*math.cos(a)),self.p(x+rr*math.cos(a)+.24*math.sin(a),yy,z+rr*math.sin(a)-.24*math.cos(a)),self.p(x+rr2*math.cos(a),yy2,z+rr2*math.sin(a))])
  else:
   for j in range(15):
    a=j*2.399;r=.3+(j%3)*.18;self.b.sphere('foliage',self.p(x+r*math.cos(a),1.1+(j%4)*.16,z+r*math.sin(a)),.35,8,5)
 def light(self,x,y,z,color=0xffe0b0,power=160,range=18):self.b.lights.append(dict(venue=self.b.property.split('-')[0],p=self.p(x,y,z),color=color,power=power,range=range))
 def chandelier(self,x,z,y=5):
  self.tube('brass',(x,y+.9,z),(x,y,z),.025)
  for radius,yy in [(1.0,y),(.65,y-.3),(.32,y-.6)]:
   self.path('brass',[(x+radius*math.cos(a),yy,z+radius*math.sin(a)) for a in np.linspace(0,math.tau,33)],.03)
   for a in np.linspace(0,math.tau,18,endpoint=False):self.box('warm',(x+radius*math.cos(a),yy-.17,z+radius*math.sin(a)),(.055,.30,.055))
 def slot(self,x,z,yaw=0):
  self.box('charcoal',(x,.61,z),(.68,1.22,.64),True);self.box('steel',(x,1.39,z+.15),(.66,.67,.14));self.box('screen',(x,1.41,z+.065),(.53,.51,.016));self.box('warm',(x,.97,z-.36),(.51,.05,.03));self.lathe('steel',x,z-.8,[(0,.23),(.06,.23),(.08,.045),(.48,.045)],12);self.box('velvet',(x,.52,z-.8),(.48,.1,.42))
 def reception(self,x,z,w=8,brand='WELCOME'):
  self.box('walnut',(x,.66,z),(w,1.32,1.15),True);self.box('marble',(x,1.34,z),(w+.2,.12,1.3));self.box('brass',(x,.18,z-.585),(w,.10,.03))
  for xx in np.arange(x-w/2+.8,x+w/2-.3,2):self.box('charcoal',(xx,1.62,z+.17),(.5,.36,.06));self.box('steel',(xx,1.42,z+.18),(.12,.18,.1))
  self.box('panel',(x,2.8,z+2),(w+1,5.3,.2));self.text(brand,(x,3.2,z+1.85),min(.6,w/(len(brand)*.6)))
 def lounge(self,x,z):
  for dx,dz in [(-1.6,0),(1.6,0)]:
   self.box('velvet',(x+dx,.44,z+dz),(.96,.26,.9),True);self.box('velvet',(x+dx,.87,z+dz+.35),(.96,.9,.2))
   for s in [-1,1]:self.box('velvet',(x+dx+s*.45,.66,z+dz),(.13,.37,.9))
  self.lathe('brass',x,z,[(0,.35),(.08,.35),(.1,.055),(.48,.055)],16);self.lathe('marble',x,z,[(.48,.64),(.55,.64)],32)
