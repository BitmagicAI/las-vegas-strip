"""Peppermill/Ross retail row from Earth2022/2024; heights photo estimates."""
from common import *
from forum_shops import facade_frame
KEY='peppermillRetail';IDS=['way/'+i for i in ['160585815','160585816','160585820','1381561598','160585814']]
def exterior(B):
 B.property=KEY+'-exterior';B.detail=0
 shapes=[footprint(i) for i in IDS]
 corner=box(807,-1858,818,-1847)
 shapes[4]=shapes[4].difference(corner).union(Point(818,-1858).buffer(10,resolution=12).intersection(corner).intersection(shapes[4]))
 allp=unary_union(shapes)
 for idx,p in enumerate(shapes):
  B.source='retail/'+IDS[idx];h=[4,8,5.6,6,7][idx];mat=['sandstone','ochre','pinkstone','pinkstone','white'][idx]
  # Trim the shared walls: only exposed boundary segments receive facades.
  neighbors=unary_union([q for j,q in enumerate(shapes) if j!=idx])
  B.planar('tile',p,.24,True);B.planar('st-roof',p,h,True)
  for poly in parts(p):
   coords=list(poly.exterior.coords)
   for a,b in zip(coords,coords[1:]):
    line=LineString([a,b]);L=line.length
    if L<.4 or neighbors.buffer(.1).contains(line.interpolate(.5,normalized=True)):continue
    F,L,nx,nz=facade_frame(B,a,b,p,.03)
    west=nx<-.4;front=west or (idx==4 and nz>.7)
    # Solid wall portions leave a recessed entrance opening at selected frontage.
    entry=front and L>12
    opening=4 if entry else 0
    for lo,hi in ([(0,L/2-opening/2),(L/2+opening/2,L)] if entry else [(0,L)]):
     F.box(mat,((lo+hi)/2,h/2,0),(hi-lo,h,.3),True)
    if entry:
     F.box(mat,(L/2,(h+3.2)/2,0),(4,h-3.2,.3),True)
     F.box('darkglass',(L/2,1.7,.5),(3.8,2.9,.12))
     for x in [L/2-1.9,L/2,L/2+1.9]:F.box('silver',(x,1.7,.4),(.08,2.9,.08))
     F.box('tile',(L/2,.12,.8),(4,.24,2),True)
    F.box('white',(L/2,h-.1,-.16),(L,.22,.5))
    if front:
     if idx==4 and L<4:
      F.box('darkglass',(L/2,4.3,-.19),(L,3.2,.08))
      F.box('silver',(0,4.3,-.25),(.06,3.2,.06))
      for y in [2.7,4.3,5.9]:F.box('silver',(L/2,y,-.25),(L,.06,.06))
     for x in np.arange(2,L-1,3.3):
      if entry and abs(x-L/2)<3:continue
      F.box('darkglass',(x,2,-.19),(2.9,2.6,.1))
      for u in [-1.45,0,1.45]:F.box('silver',(x+u,2,-.27),(.05,2.6,.05))
      F.box('sandstone',(x,.48,-.3),(3,.18,.4))
     if idx in [2,3]:
      # Burgundy projecting shop awnings, not a repeating hotel window grid.
      F.b.face('venetian-burgundy',[F.p(0,3.7,-.25),F.p(L,3.7,-.25),F.p(L,3.2,-1.8),F.p(0,3.2,-1.8)])
      F.box('venetian-burgundy',(L/2,3.08,-1.8),(L,.24,.08))
     if idx==1 and L>20:
      F.box('sandstone',(L/2,7.3,-.32),(L*.72,4.6,.45),True)
      for x in [L*.14,L*.86]:F.box('stone',(x,5.1,-.5),(1,10.2,.9),True)
      F.box('white',(L/2,9.65,-.5),(L*.76,.35,.8))
      F.box('white',(L/2,9.8,-.9),(L*.76,.22,1.6))
      for u in [L*.14,L*.86]:
       F.box('stone',(u,10.0,-.5),(1.5,.5,1.3))
       F.box('white',(u,10.3,-.5),(1.7,.15,1.5))
      F.text('ROSS',(L/2,7.3,-.6),2.1,'blue');F.text('DRESS FOR LESS',(L/2,6.2,-.6),.75,'blue')
     elif idx==4 and L>20:
      F.text('Walgreens',(L/2,5.1,-.5),1.7,'red')
      F.box('white',(L/2,4.5,-.2),(L,.15,.35))
     elif idx==3 and L>12:
      F.text("Denny's",(L/2,4.35,-.35),1.1,'yellowled')
     elif idx==2 and L>12:
      F.box('white',(L/2,4.5,-.25),(4.5,1.3,.15));F.text('7 ELEVEN',(L/2,4.1,-.38),.55,'red')
    else:
     for x in np.arange(1,L,5):F.box('st-grey',(x,h/2,-.18),(.035,h-.4,.04))
     if L>15:
      F.box('st-grey',(L/2,1.7,-.2),(1.5,3,.1));F.box('silver',(L/2+.5,1.6,-.28),(.08,.3,.08))
  if idx==0:
   # Truncated steep hip roof with recessed equipment well.
   inner=p.buffer(-7);roofp=p.buffer(.7)
   for poly in parts(roofp):
    pts=list(poly.exterior.coords)
    for a,b in zip(pts,pts[1:]):
     c=inner.boundary.interpolate(inner.boundary.project(Point(a)));d=inner.boundary.interpolate(inner.boundary.project(Point(b)))
     B.face('roof',[(a[0],4,a[1]),(b[0],4,b[1]),(d.x,9,d.y),(c.x,9,c.y)],True)
   B.planar('st-roof',inner,8.6,True)
   F=Frame(B,871.7,-1965,math.pi/2,y=0)
   F.text('PEPPERMILL',(0,4.3,-.5),1.2,'white')
   F.box('sandstone',(0,3.1,-1.5),(9,.4,3),True)
   for x in [-4,4]:F.box('stone',(x,1.6,-2.5),(.35,3.2,.35),True)
  else:
   for x in np.arange(p.bounds[0]+6,p.bounds[2]-3,12):
    for z in np.arange(p.bounds[1]+6,p.bounds[3]-3,13):
     if p.contains(box(x-1.5,z-1,x+1.5,z+1)):
      B.box('st-grey',(x,h+.55,z),(3,1.1,2));B.box('silver',(x,h+1.16,z),(3.1,.12,2.1))
 return dict(key=KEY,name='Peppermill and Strip retail row',center=[855,0,-1915],bounds=list(allp.bounds),structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],views={})
