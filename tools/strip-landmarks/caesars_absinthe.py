"""Absinthe's mapped tent and garden kiosks. Exterior only, no theater rebuild.
2022 Earth roof layout and2023 Spiegelworld photographs. Heights estimated.
"""
from common import *
from forum_shops import facade_frame
IDS=['way/364846541','way/1340330691','way/1340330690']
def exterior(B):
 B.source='caesars-absinthe';B.detail=0
 cx,cz=-89.42,77.62;r=15.15;base=.15;eave=3.8;peak=10.1
 # Circular canvas roof has curved radial sections; dark red and warm ivory gores.
 for j in range(144):
  a=j*math.tau/144;b=(j+1)*math.tau/144;mat='velvet' if (j//12)%2==0 else 'cp-white'
  mat='venetian-burgundy' if mat=='velvet' else mat
  for k in range(12):
   t=k/12;u=(k+1)/12
   def pt(t,aa):
    rr=r*(1-t);y=eave+(peak-eave)*(t**1.55)
    return (cx+rr*math.cos(aa),y,cz+rr*math.sin(aa))
   B.upface(mat,[pt(t,a),pt(t,b),pt(u,b)] if k==11 else [pt(t,a),pt(t,b),pt(u,b),pt(u,a)],True)
  # Wall canvas remains open at the northern entrance, occupied interiors untouched.
  if not (math.sin((a+b)/2)<-.98):
   B.face(mat,[(cx+r*math.cos(a),base,cz+r*math.sin(a)),(cx+r*math.cos(b),base,cz+r*math.sin(b)),(cx+r*math.cos(b),eave,cz+r*math.sin(b)),(cx+r*math.cos(a),eave,cz+r*math.sin(a))],True)
 B.planar('stone',Point(cx,cz).buffer(r,resolution=48),base,True)
 # North vestibule, dark green folding entrance doors, canvas cap.
 F=Frame(B,-88.8,61.6,0,y=0)
 for side in [-1,1]:F.box('red',(side*2.7,1.9,0),(.2,3.8,4),True)
 F.box('red',(0,3.9,0),(5.6,.2,4.2),True)
 F.box('darkglass',(0,1.6,-1.6),(4.5,3.2,.08))
 for x in [-2.25,0,2.25]:F.box('brass',(x,1.6,-1.68),(.075,3.2,.1))
 F.box('brass',(0,3.15,-1.68),(4.6,.09,.1))
 F.text('ABSINTHE',(0,3.45,-2.16),.48,'cp-white')
 # Seams and tension cables are batched decorative geometry, not per-rope collision.
 B.detail=1
 for j in range(12):
  a=j*math.tau/12
  B.path('cp-white',[(cx+r*(1-t)*math.cos(a),eave+(peak-eave)*t**1.55+.035,cz+r*(1-t)*math.sin(a)) for t in np.linspace(0,.995,18)],.028,5)
  B.tube('steel',(cx+r*math.cos(a),eave,cz+r*math.sin(a)),(cx+(r+.6)*math.cos(a),.2,cz+(r+.6)*math.sin(a)),.025,5)
 B.detail=0
 for ident,sign in [(IDS[1],'NO PANTS'),(IDS[2],'GREEN FAIRY')]:
  B.source='caesars-garden-kiosk-'+ident.split('/')[-1]
  p=footprint(ident);h=2.8
  B.shell(p,0,h,'sage',roof=False);B.planar('cp-flat-roof',p,h,True)
  # Mapped narrow container plan, corrugated panels, hatch and deep awning.
  for poly in parts(p):
   ps=list(poly.exterior.coords)
   for a,b in zip(ps,ps[1:]):
    F,L,nx,nz=facade_frame(B,a,b,p,.025)
    for x in np.arange(.15,L,.19):F.box('sage',(x,h/2,-.06),(.035,h-.12,.1))
    if L>4 and (nz>.5 if ident==IDS[1] else nx<-.5):
     F.box('cp-shadow',(L*.42,1.68,-.12),(L*.65,1.25,.1))
     F.box('walnut',(L*.42,1.05,-.36),(L*.68,.12,.66))
     F.box('sage',(L/2,2.75,-.48),(L,.1,1.05))
     F.text(sign,(L/2,2.4,-.2),min(.32,L/25),'cp-white')
 B.detail=0
 return dict(ids=IDS,roofPeakM=peak,eaveM=eave,remaining='Canvas dimensions estimated; detailed artwork, garden vegetation, gate and occupied theater not rebuilt. No emissive light pool changed.')

def purple_zebra(B):
 """Open colonnaded bar, not a solid6m generic building. Sections estimated."""
 ident='way/364846540';p=footprint(ident);B.source='caesars-purple-zebra';B.detail=0
 B.planar('stone',p,.16,True)
 B.planar('cp-flat-roof',p,5.5,True)
 for t in triangles(p):
  pts=[(x,4.9,z) for x,z in list(t.exterior.coords)[:-1]]
  if np.cross(np.array(pts[1])-pts[0],np.array(pts[2])-pts[0])[1]>0:pts.reverse()
  B.face('cp-white',pts)
 B.shell(p,4.9,5.5,'cp-white',roof=False)
 # White pyramidal vent lantern observed on Earth above the low flat roof.
 x,z=p.centroid.x,p.centroid.y
 for a,b in zip([(-2,-2),(2,-2),(2,2),(-2,2)],[ (2,-2),(2,2),(-2,2),(-2,-2)]):
  B.upface('cp-white',[(x+a[0],5.5,z+a[1]),(x+b[0],5.5,z+b[1]),(x,7,z)])
 for xx in [-59.7,-51.9,-44.2]:
  for zz in [72,88.5]:
   B.lathe('blackiron',(xx,zz),[(.16,.65),(.35,.65),(.5,.44),(4.35,.36),(4.55,.7),(4.9,.7)],24)
   B.box('blackiron',(xx,2.5,zz),(.63,4.7,.63),True)
   for a in np.linspace(0,math.tau,16,endpoint=False):B.tube('blackiron',(xx+.43*math.cos(a),.55,zz+.43*math.sin(a)),(xx+.36*math.cos(a),4.3,zz+.36*math.sin(a)),.024,4)
 # Rear service wall and signage pier observed in the ground photograph.
 B.box('cr-purple-stucco',(-45.2,2.55,80),(3.6,4.8,5.5),True)
 B.box('cp-white',(-45.2,.31,80),(3.8,.3,5.7))
 S=Frame(B,-43.35,80,-math.pi/2,y=0)
 S.text('PURPLE ZEBRA',(0,3.3,-.03),.39,'cp-white');S.text('BAR',(0,2.65,-.03),.6,'cp-white')
 S.text('FROZEN DRINKS',(0,1.9,-.03),.2,'cp-white')
 B.lathe('silver',(-53.7,80),[(1.15,3.4),(1.3,3.4)],64)
 B.planar('silver',Point(-53.7,80).buffer(3.4,resolution=32).difference(Point(-53.7,80).buffer(2.6,resolution=32)),1.3)
 B.shell(Point(-53.7,80).buffer(3.2,resolution=24),.16,1.3,'cp-white',roof=False)
 # Concentric ceiling coves and sculpted white bar front from current photograph.
 for rad in [3.8,4.4,5.0]:
  B.lathe('cp-white',(-53.7,80),[(4.68,rad+.08),(4.9,rad+.08)],96)
  B.path('purple',[(-53.7+rad*math.cos(a),4.65,80+rad*math.sin(a)) for a in np.linspace(0,math.tau,97)],.045,6)
 for y in [.45,.65,.9]:
  B.path('cp-white',[(-53.7+3.23*math.cos(a),y+.08*math.sin(a*8),80+3.23*math.sin(a)) for a in np.linspace(0,math.tau,129)],.035,5)
 for poly in parts(p):
  ps=list(poly.exterior.coords)
  for a,b in zip(ps,ps[1:]):
   F,L,_,_=facade_frame(B,a,b,p,.04)
   F.box('cp-white',(L/2,5.15,-.2),(L,.2,.45))
   F.box('linq-blue',(L/2,4.82,-.12),(L,.18,.24))
   for xx in np.arange(.25,L,.4):F.box('cp-white',(xx,5.32,-.17),(.14,.16,.32))
 return dict(id=ident,roofM=5.5,eaveM=4.9,source='Caesars property map2024, factsheet2025 and VegasChanges Purple Zebra photograph; Google Earth2022 plan',remaining='Detailed stools, decor and route-specific service doors not reproduced.')

def roman_plaza(B):
 """Flamingo-facing red tiled colonnade, Earth oblique2022-11-09.
 Footprint mapped; platform/roof section estimates from frontage proportions.
 """
 ident='way/115672897';p=footprint(ident);B.source='caesars-roman-plaza';B.detail=0
 base=1.8;eave=8.1;ridge=10.4
 B.shell(p,0,base,'cp-stone',roof=False)
 B.planar('stone',p,base,True)
 F=Frame(B,-101.39,105.17,-.0264,y=0)
 # Parallel two rows of fluted classical columns beneath a tiled hip roof.
 for x in np.linspace(-19.1,19.1,10):
  for z in [-4.9,4.9]:
   F.box('cp-white',(x,base+.15,z),(1.45,.3,1.45),True)
   F.lathe('cp-white',x,z,[(base+.3,.68),(base+.5,.56),(eave-1,.45),(eave-.7,.68),(eave-.4,.68)],24)
   F.box('cp-white',(x,(base+eave-.4)/2,z),(.85,eave-.4-base,.85),True)
   F.box('cp-white',(x,eave-.3,z),(1.4,.25,1.4))
   for a in np.linspace(0,math.tau,16,endpoint=False):F.tube('cp-sill',(x+.55*math.cos(a),base+.6,z+.55*math.sin(a)),(x+.46*math.cos(a),eave-1.1,z+.46*math.sin(a)),.03,4)
 # Entablature and covered soffit, real open space below.
 for z in [-5.65,5.65]:
  F.box('cp-white',(0,eave-.18,z),(43,.6,.8),True)
  F.box('cp-white',(0,eave+.12,z),(43.7,.2,1.1))
 for x in [-21.2,21.2]:F.box('cp-white',(x,eave-.18,0),(.8,.6,11.8),True)
 F.box('cp-white',(0,eave-.12,0),(42,.18,11.7),True)
 for pts in [[(-22,-6.6),(22,-6.6),(16,0),(-16,0)],[(22,-6.6),(22,6.6),(16,0)],[(22,6.6),(-22,6.6),(-16,0),(16,0)],[(-22,6.6),(-22,-6.6),(-16,0)]]:
  B.upface('cp-tile',[F.p(x,ridge if z==0 else eave+.24,z) for x,z in pts],True)
 # Central southern stairs connect the elevated colonnade to the plaza.
 S=Frame(B,-101.6,117.4,math.pi-.0264,y=0);S.stairs(0,0,5.4,base,6.15)
 for side in [-1,1]:
  F.box('cp-white',(side*11.95,base+.43,6.35),(18.2,.86,.35),True)
  F.box('cp-white',(side*11.95,base+.94,6.35),(18.35,.16,.55))
 return dict(id=ident,baseM=base,eaveM=eave,ridgeM=ridge,remaining='Statues and carved Corinthian capitals not reproduced; measured elevation unknown.')

def mojito(B):
 ident='way/364846543';p=footprint(ident);B.source='caesars-mojito';B.detail=0;h=3.1
 B.shell(p,0,h,'cp-white',roof=False);B.planar('cp-flat-roof',p,h,True)
 for poly in parts(p):
  ps=list(poly.exterior.coords)
  for a,b in zip(ps,ps[1:]):
   F,L,nx,nz=facade_frame(B,a,b,p,.025)
   F.box('cp-white',(L/2,h-.1,-.15),(L,.24,.4))
   if nx<.45:continue
   F.box('cp-shadow',(L/2,1.75,-.08),(L-.45,1.85,.09))
   for xx in [.16,L-.16]:F.box('cp-white',(xx,1.55,-.18),(.25,3.1,.3))
   F.box('cr-purple-stucco',(L/2,.48,-.18),(L-.5,.85,.1))
   F.box('silver',(L/2,1.05,-.35),(L-.35,.16,.7))
   F.box('sage',(L/2,2.88,-.6),(L+.2,.48,1.2))
   F.text('MARGARITAS & MOJITOS',(L/2,2.74,-1.22),.23,'cp-white')
   for xx in [L*.18,L*.82]:
    F.box('blackiron',(xx,1.9,-.19),(.75,1.3,.03))
    for yy in np.arange(1.5,2.4,.12):F.box('cp-white',(xx,yy,-.212),(.56,.015,.005))
   F.text('PURPLE ZEBRA',(L/2,.4,-.25),.25,'cp-white')
 return dict(id=ident,roofM=h,remaining='Menu lettering, interior equipment and fine graphic artwork approximated.')
