"""Original shallow sign plates in a facade frame; no image textures or collision."""
from common import *

def plate(F, shape, material, front, depth=.08):
 # Shapely triangles have positive XY winding; the visible facade faces -Z.
 for t in triangles(shape):
  pts=list(t.exterior.coords)[:-1]
  area=sum(a[0]*b[1]-b[0]*a[1] for a,b in zip(pts,pts[1:]+pts[:1]))
  if area<0:pts.reverse()
  F.b.face(material,[F.p(x,y,front) for x,y in pts[::-1]])
  F.b.face(material,[F.p(x,y,front+depth) for x,y in pts])
 for ring in [shape.exterior,*shape.interiors]:
  pts=list(ring.coords)
  for (x,y),(u,v) in zip(pts,pts[1:]):
   F.b.face(material,[F.p(x,y,front),F.p(u,v,front),F.p(u,v,front+depth),F.p(x,y,front+depth)])

def star(x,y,r):
 return Polygon([(x+(r if i%2==0 else r*.23)*math.cos(i*math.pi/4),y+(r if i%2==0 else r*.23)*math.sin(i*math.pi/4)) for i in range(8)])

def welcome(F,x):
 # Photographic scale estimate: 8.6m wide by 3.7m tall, north showroom wall.
 shape=Polygon([(x-4.3,6.7),(x,8.55),(x+4.3,6.7),(x,4.85)])
 plate(F,shape,'hd-cream',-.32,.12)
 plate(F,scale(shape,xfact=.94,yfact=.90,origin=(x,6.7)),'hd-letter',-.35,.025)
 plate(F,star(x,9.1,.70),'hd-orange',-.38,.08)
 plate(F,star(x,9.1,.46),'hd-red',-.41,.025)
 for i,c in enumerate('WELCOME'):
  u=x+(3-i)*.63
  plate(F,Point(u,8.05).buffer(.33,resolution=12),'hd-cream',-.40,.06)
  plate(F,Point(u,8.05).buffer(.27,resolution=12),'hd-letter',-.43,.02)
  F.text(c,(u,7.84,-.46),.44,'hd-red')
 F.text('LAS VEGAS',(x,6.65,-.41),.77,'hd-red')
 F.text('HARLEY-DAVIDSON',(x,5.91,-.41),.36,'hd-charcoal')
