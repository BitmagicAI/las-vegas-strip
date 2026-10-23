"""Treasure Island tower: mapped three-wing plan, red masonry and white bay frames.
Photo reference: CTBUH exterior photograph; facade dimensions photo-fitted.
The mapped 112 m envelope, original guest cuts and collision stay authoritative.
"""
import json,math
from common import np,footprint,parts,Point,Frame

def exterior(B):
 B.detail=0
 for g in B.groups.values():
  if g['property']=='ti-exterior' and g['material']=='roof':g['material']='ti-roof'
 for g in json.load(open('build/highrises/meshes.json')):
  if g['property']!='treasure-island' or g['lod']!=0:continue
  B.source='tower/'+g['source']
  for f in g['faces']:B.face('ti-stone' if g['material']!='roof' else 'ti-roof',[g['vertices'][i] for i in f])
 shape=footprint('way/27727145');B.source='tower/way/27727145'
 for poly in parts(shape):
  coords=list(poly.simplify(.15,preserve_topology=True).exterior.coords)
  for a,b in zip(coords,coords[1:]):
   L=math.dist(a,b)
   if L<.2:continue
   ux,uz=(b[0]-a[0])/L,(b[1]-a[1])/L;nx,nz=-uz,ux
   if shape.contains(Point((a[0]+b[0])/2+nx*.1,(a[1]+b[1])/2+nz*.1)):nx,nz=-nx,-nz
   def p(x,y,d):return (a[0]+ux*x+nx*d,y,a[1]+uz*x+nz*d)
   def q(mat,x,y,xx,yy,d):B.face(mat,[p(x,y,d),p(xx,y,d),p(xx,yy,d),p(x,yy,d)])
   def band(y,h,depth):
    q('ti-stone',0,y,L,y+h,depth)
    for yy in [y,y+h]:B.face('ti-stone',[p(0,yy,.03),p(L,yy,.03),p(L,yy,depth),p(0,yy,depth)])
   q('ti-brick',0,12,L,111.4,.11)
   for yy,h,d in [(12,.75,.42),(98.3,.55,.48),(110.9,.48,.62),(111.65,.35,.90)]:band(yy,h,d)
   if L<11:
    # Red blade ends and white quoin strips, not windows across service ends.
    for xx in [.2,max(.2,L-.9)]:
     q('ti-stone',xx,12,xx+.55,111.7,.28)
     B.detail=1
     for yy in np.arange(13,110,1.0):q('ti-stone',xx-.14,yy,xx+.70,yy+.30,.38)
     B.detail=0
    continue
   count=max(2,round((L-1.6)/3.38));step=(L-1.6)/count
   for j in range(count):
    x=.8+(j+.5)*step;w=step*.70
    for row in range(28):
     y=12.9+row*3.02
     q('ti-window',x-w/2,y,x+w/2,y+2.35,.19)
     for side in [-1,1]:
      edge=x+side*w/2
      B.face('ti-stone',[p(edge,y-.10,.19),p(edge,y+2.47,.19),p(edge,y+2.47,.47),p(edge,y-.10,.47)])
      q('ti-stone',edge-.10,y-.10,edge+.10,y+2.47,.49)
     q('ti-stone',x-w/2-.17,y-.17,x+w/2+.17,y+.03,.52)
     q('ti-stone',x-w/2-.13,y+2.33,x+w/2+.13,y+2.51,.48)
     B.detail=1
     q('ti-mullion',x-.025,y+.05,x+.025,y+2.30,.25)
     q('ti-mullion',x-w/2,y+1.65,x+w/2,y+1.70,.25)
     B.detail=0
    # Crown windows span two storeys and terminate in a shallow arch.
    lo,hi=99.1,106.8;r=w/2;spring=hi-r
    ring=[(x-r,lo),(x+r,lo),(x+r,spring)]+[(x+r*math.cos(t),spring+r*math.sin(t)) for t in np.linspace(0,math.pi,17)[1:]]
    B.face('ti-window',[p(xx,yy,.20) for xx,yy in ring])
    for aa,bb in zip(ring,ring[1:]+ring[:1]):B.face('ti-stone',[p(*aa,.20),p(*bb,.20),p(*bb,.45),p(*aa,.45)])
    B.path('ti-stone',[p(xx,yy,.48) for xx,yy in ring+[ring[0]]],.15,8)
    q('ti-mullion',x-.035,lo,x+.035,hi-.15,.31)
    for yy in [101.4,103.7]:q('ti-mullion',x-r,yy,x+r,yy+.06,.31)
   for yy in np.arange(15.4,98,3.02):band(yy,.16,.34)
   if L>60 and nx>.4:
    B.text('TREASURE ISLAND',p(L/2,108.4,.68),min(2.15,L/32),math.atan2(uz,ux)+math.pi,'ti-stone')
 B.detail=1
 for poly in parts(shape.buffer(-1.3)):
  B.shell(poly,112,113,'ti-stone',roof=False,solid=False)
 for x in np.arange(15,156,12):
  for z in np.arange(-1020,-905,12):
   if shape.contains(Point(x,z).buffer(3)):
    B.box('ti-roof',(x,112.7,z),(4.2,1.4,3.0));B.box('charcoal',(x,113.43,z),(3.8,.05,2.6))
 B.detail=0
