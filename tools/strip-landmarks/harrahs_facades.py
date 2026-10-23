"""Harrah's 2021+ white towers and striped Strip canopy.
Sources: Caesars press fact sheet exterior, creator's aerial 2026-10-09.
Surveyed footprint/heights; fenestration and canopy heights photo-fitted, not surveyed.
Pure render geometry: existing city collision, guest rooms and public routes retained.
"""
import json,math
from common import np,Polygon,Point,LineString,parts,footprint,Frame,box,triangles

def exterior(B):
 B.detail=0
 plan=next(p for p in json.load(open('build/highrises/plan.json')) if p['key']=='harrahs')
 for g in json.load(open('build/highrises/meshes.json')):
  if g['property']!='harrahs' or g['lod']!=0:continue
  B.source='tower/'+g['source']
  for f in g['faces']:B.face('white' if g['material']!='roof' else 'concrete',[g['vertices'][i] for i in f])
 for feature in plan['features']:
  shape=footprint(feature['id']);h=feature['height'];B.source='tower/'+feature['id']
  for poly in parts(shape):
   for a,b in zip(list(poly.exterior.coords),list(poly.exterior.coords)[1:]):
    L=math.dist(a,b)
    if L<.8:continue
    ux,uz=(b[0]-a[0])/L,(b[1]-a[1])/L;nx,nz=-uz,ux
    if shape.contains(Point((a[0]+b[0])/2+nx*.1,(a[1]+b[1])/2+nz*.1)):nx,nz=-nx,-nz
    def p(x,y,d):return (a[0]+ux*x+nx*d,y,a[1]+uz*x+nz*d)
    def q(mat,x,y,xx,yy,d=.10):B.face(mat,[p(x,y,d),p(xx,y,d),p(xx,yy,d),p(x,yy,d)])
    blank=h>100 and nx<-.9 and 219<min(a[0],b[0])<221
    q('white',0,9,L,h,.09)
    if blank:
     for yy in np.arange(10,h-2,3.1):q('harrahs-joint',0,yy,L,yy+.028,.115)
     for xx in np.arange(1,L,3.1):q('harrahs-joint',xx,9,xx+.035,h,.115)
    else:
     count=max(1,round(L/3.05));step=L/count
     floors=round((h-11)/3.1);dy=(h-11)/floors
     for j in range(count):
      xx=(j+.5)*step;w=min(1.6,step*.66)
      for i in range(floors):
       yy=9.8+i*dy;mat='harrahs-window' if (i*17+j*7)%13 else 'harrahs-curtain'
       q(mat,xx-w/2,yy,xx+w/2,yy+2.25,.145)
       # Reveal and projecting sill create depth without thousands of objects.
       for s in [-1,1]:B.face('concrete',[p(xx+s*w/2,yy,.145),p(xx+s*w/2,yy+2.25,.145),p(xx+s*w/2,yy+2.25,.26),p(xx+s*w/2,yy,.26)])
       q('white',xx-w/2-.10,yy-.12,xx+w/2+.10,yy,.27)
       B.detail=1;q('silver',xx-.026,yy,xx+.026,yy+2.25,.19);q('silver',xx-w/2,yy+1.65,xx+w/2,yy+1.70,.19);B.detail=0
    for yy in [9,h-1.2,h-.4]:q('white',0,yy,L,yy+.35,.38)
  # Flat parapets, roof plant and access cores kept behind the skyline.
  B.detail=1
  for poly in parts(shape.buffer(-3)):
   B.shell(poly,h,h+1.1,'white',roof=False,solid=False)
  for x in np.arange(shape.bounds[0]+6,shape.bounds[2]-3,11):
   for z in np.arange(shape.bounds[1]+6,shape.bounds[3]-3,11):
    if not shape.contains(Point(x,z).buffer(2.5)):continue
    B.box('concrete',(x,h+.6,z),(3.8,1.2,2.6));B.box('charcoal',(x,h+1.24,z),(3.5,.08,2.3))
  B.detail=0
 # Logo spans the two surveyed collinear wall segments, not one half of the sign.
 B.source='tower/way/111367828';B.text("Harrah's",(219.22,102,-382.2),5.15,-math.pi/2,'harrahs-logo')
 B.source='tower/way/128632721';B.text("Harrah's",(152.16,66,-424),3.4,-math.pi/2,'harrahs-logo')

 # The marquee follows the mapped western frontage rather than the old south door.
 B.source='harrahs-strip';path=LineString([(76.1,-449.4),(65.1,-441),(62.4,-432),(57.8,-414.7),(54.3,-399.3),(53,-374.3),(53.7,-361.2),(55.1,-345),(58,-330.1),(69.8,-320.6)])
 length=path.length
 def p(s,y,d=0):
  s=max(0,min(length,s));a=path.interpolate(max(0,s-.15));b=path.interpolate(min(length,s+.15));l=math.hypot(b.x-a.x,b.y-a.y);ux,uz=(b.x-a.x)/l,(b.y-a.y)/l;c=path.interpolate(s)
  return (c.x-uz*d,y,c.y+ux*d)
 def facepoly(mat,poly,offset):
  for shape in parts(poly):
   for tri in triangles(shape):B.face(mat,[p(x,y,offset) for x,y in list(tri.exterior.coords)[:-1]])
 def strip(mat,lo,hi,offset=0):
  for s in np.arange(0,length,.9):
   t=min(length,s+.9);B.face(mat,[p(s,lo,offset),p(t,lo,offset),p(t,hi,offset),p(s,hi,offset)])
 # Shallow entrance/retail recesses below a continuous dark clerestory.
 strip('harrahs-window',.25,10.7,.42)
 for s in np.arange(2,length-1,3.5):
  pts=[p(s,.3,.50),p(s,10.6,.50)];B.path('silver',pts,.065,4)
 for y in [3.0,4.2,7.2,10.7]:strip('white',y,y+.18,.65)
 for j,s in enumerate(np.arange(9,length-4,15)):
  c=p(s,0,.61);a=p(s-.2,0,.61);b=p(s+.2,0,.61);yaw=math.atan2(b[2]-a[2],-(b[0]-a[0]))
  F=Frame(B,c[0],c[2],yaw,y=0)
  F.box('white',(0,5.2,0),(10,.65,.45));F.text(["CASINO","Harrah's","LAS VEGAS"][j%3],(0,5.12,-.26),.46,'harrahs-logo')
  for xx in [-1.2,0,1.2]:F.box('silver',(xx,1.45,-.06),(.07,2.9,.1));F.box('silver',(xx+.13,1.3,-.15),(.025,.6,.035))
 # Stripe panel has two large genuine arched openings, not arches painted over stripes.
 fascia=box(0,10.9,length,18.8)
 for s in [length*.22,length*.76]:
  r=8.5;spring=12.2
  ring=[(s-r,10.9),(s+r,10.9),(s+r,spring)]+[(s+r*math.cos(a),spring+r*.53*math.sin(a)) for a in np.linspace(0,math.pi,40)[1:]]
  opening=Polygon(ring);fascia=fascia.difference(opening);facepoly('harrahs-window',opening,.72)
  B.path('white',[p(x,y,.98) for x,y in ring+[ring[0]]],.29,8)
  B.path('harrahs-purple',[p(x,y,1.04) for x,y in ring+[ring[0]]],.10,8)
 # Clip diagonals to one panel surface; no coplanar duplicate layer.
 for s in np.arange(-10,length+10,.88):
  poly=Polygon([(s,10.9),(s+.44,10.9),(s+5.4,18.8),(s+4.96,18.8)]).intersection(fascia)
  facepoly('harrahs-purple',poly,.80)
  poly=Polygon([(s+.44,10.9),(s+.88,10.9),(s+5.84,18.8),(s+5.4,18.8)]).intersection(fascia)
  facepoly('white',poly,.80)
 for lo,hi,d in [(10.6,10.95,1),(18.8,19.12,1.1),(19.25,19.65,.9),(19.75,20.05,.65)]:strip('white',lo,hi,d)
 for s in np.arange(0,length,.9):
  t=min(length,s+.9)
  B.face('concrete',[p(s,19.2,0),p(t,19.2,0),p(t,19.2,-13),p(s,19.2,-13)])
  B.face('white',[p(s,10.5,.42),p(t,10.5,.42),p(t,10.5,-1),p(s,10.5,-1)])
 for end in [0,length]:
  B.face('white',[p(end,8.6,0),p(end,19.2,0),p(end,19.2,-13),p(end,8.6,-13)])
 # Marquee globes/crest: silhouette and layered metallic rings seen in official photo.
 for s in [length*.48,length*.91]:
  x,_,z=p(s,0,-.4);F=Frame(B,x,z,math.pi/2,y=0)
  F.lathe('white',0,0,[(19.2,1.5),(20.2,1.1),(20.8,.65),(22,.5)],24)
  B.sphere('harrahs-purple',F.p(0,23.6,0),2.4,32,20)
  for yy,rr in [(22.2,2),(23.6,2.5),(25,2)]:F.path('gold',[(rr*math.cos(a),yy,rr*math.sin(a)) for a in np.linspace(0,math.tau,65)],.085,6)
  F.text("Harrah's",(0,23.4,-2.55),1.15,'letter')
  for side in [-1,1]:
   pts=[(side*(2.4+3*t),19.9+2*math.sin(t*math.pi)*math.exp(-t),.2) for t in np.linspace(0,1,36)]
   F.path('white',pts,.3,8)
 B.detail=0

 # Roof service equipment placed within surveyed podium, outside guest towers.
 B.source='harrahs-roof';B.detail=1
 roof=footprint('way/128622185').buffer(-16)
 for feat in plan['features']:roof=roof.difference(footprint(feat['id']).buffer(6))
 for x in np.arange(100,290,22):
  for z in np.arange(-436,-306,22):
   if not roof.contains(Point(x,z).buffer(5)):continue
   B.box('concrete',(x,9.6,z),(7,2,4.5));B.box('silver',(x,10.7,z),(7.2,.2,4.7))
   for dx in [-2.1,0,2.1]:B.lathe('charcoal',(x+dx,z),[(10.8,.85),(10.9,.85)],20)
 B.detail=0

 # Keep the incremental roof detail in future exterior builds.
 from harrahs_roof_detail import exterior as roof_detail
 roof_detail(B)
