"""Carnaval Court open pavilion, satellite plan and official Caesars photograph."""
from common import *
KEY='carnavalCourt';CX=100.515;CZ=-303.66

def exterior(B):
 B.property=KEY+'-exterior';B.source='podium/carnaval-court';B.detail=0;F=Frame(B,CX,CZ,y=0);p=footprint('way/402543932')
 def q(r,a,y):return F.p(r*math.cos(a),y,r*math.sin(a))
 # Open radial canopy with painted perimeter fascia, not a solid cylindrical shell.
 for j in range(12):
  a=j*math.tau/12;b=(j+1)*math.tau/12
  B.upface('ccourt-roof-paint',[q(12.8,a,5.6),q(12.8,b,5.6),q(4.2,b,7.35),q(4.2,a,7.35)],True)
  B.upface('ccourt-roof-paint',[q(4.2,a,7.35),q(4.2,b,7.35),q(0,0,8.0)],True)
  # Separate inward underside faces and one colourful outer band.
  B.face('ccourt-soffit-paint',[q(12.8,a,5.47),q(12.8,b,5.47),q(4.2,b,7.22),q(4.2,a,7.22)])
  B.face('ccourt-soffit-paint',[q(4.2,a,7.22),q(4.2,b,7.22),q(0,0,7.87)])
  B.face('ccourt-fascia-paint',[q(12.8,a,4.6),q(12.8,b,4.6),q(12.8,b,5.6),q(12.8,a,5.6)])
  for yy in [4.59,5.61]:B.tube('ccourt-trim-paint',q(12.81,a,yy),q(12.81,b,yy),.045,8)
  for yy in [5.38,5.08]:B.tube('ccourt-steel-paint',q(11.8,a,yy),q(2.0,a,7.4),.055,8)
  for rr in np.arange(3,11.5,1.3):
   B.tube('ccourt-steel-paint',q(float(rr),a,7.4-(rr-2)*.205),q(float(rr)+.65,a,7.4-(rr-2)*.205-.3),.025,6)
  # Black fascia fixtures, not real-time light objects.
  aa=(a+b)/2;G=Frame(B,CX+12.5*math.cos(aa),CZ+12.5*math.sin(aa),-aa-math.pi/2,y=0)
  G.box('ccourt-fixture-paint',(0,5.02,-.05),(.33,.34,.15))
 # Tapered columns remain outside the clear circulation ring.
 for j in range(6):
  a=(j+.5)*math.tau/6;x,z=11.5*math.cos(a),11.5*math.sin(a)
  F.lathe('ccourt-column-stone',x,z,[(.24,.60),(4.55,.86)],32)
  F.lathe('ccourt-column-color-paint',x,z,[(3.6,.805),(4.55,.865)],32)
  F.box('ccourt-collision',(x,2.4,z),(1.05,4.3,1.05),True)
  F.lathe('ccourt-steel-paint',x,z,[(5.7,.28),(6.1,.21)],16)
  B.sphere('ccourt-gold-paint',F.p(x,6.3,z),.19,16,10)
 B.sphere('ccourt-gold-paint',F.p(0,8.75,0),.72,32,20)
 F.lathe('ccourt-steel-paint',0,0,[(7.6,.25),(8.05,.20)],20)
 # Ground-level open-air bar and fitted counter, with a staff gap toward the east.
 floor=p.buffer(1.4,join_style=2);B.planar('ccourt-floor-stone',floor,.24,True)
 ring=Point(CX,CZ).buffer(4.4,resolution=48).difference(Point(CX,CZ).buffer(3.5,resolution=48)).difference(box(CX+3,CZ-.65,CX+5,CZ+.65))
 B.shell(ring,.24,1.2,'ccourt-bar-purple',roof=False);B.planar('ccourt-counter-paint',ring.buffer(.08),1.24,True)
 F.lathe('ccourt-service-paint',0,0,[(.24,1.3),(2.0,1.3)],32)
 # Stock/sink units and shelves are restrained, batched geometry.
 for j in range(8):
  a=j*math.tau/8;G=Frame(B,CX+1.9*math.cos(a),CZ+1.9*math.sin(a),-a-math.pi/2,y=0)
  G.box('ccourt-steel-paint',(0,1.1,0),(1.2,.12,.55))
  for u in [-.42,-.14,.14,.42]:G.lathe('ccourt-bottle-paint',u,0,[(1.16,.05),(1.38,.05),(1.43,.025),(1.52,.025)],8)
 for j in range(22):
  a=j*math.tau/22
  if abs(a)<.2 or abs(a-math.tau)<.2:continue
  G=Frame(B,CX+5.2*math.cos(a),CZ+5.2*math.sin(a),-a,y=0)
  G.lathe('ccourt-seat-paint',0,0,[(1.02,.27),(1.1,.27)],16)
  for u in [-.17,.17]:
   for w in [-.17,.17]:G.tube('ccourt-steel-paint',(u,.24,w),(u,1.02,w),.025,6)
  G.path('ccourt-steel-paint',[(-.25,1.1,.23),(-.25,1.65,.23),(.25,1.65,.23),(.25,1.1,.23)],.025,6)
 # Outer guard with broad west and south public openings.
 for j in range(60):
  a=j*math.tau/60;b=(j+1)*math.tau/60;mid=(a+b)/2
  if abs(mid-math.pi)<.22 or abs(mid-1.82)<.16:continue
  for y in [.4,1.35]:B.tube('ccourt-rail-paint',q(13.1,a,y),q(13.1,b,y),.03,6)
  B.tube('ccourt-rail-paint',q(13.1,a,.24),q(13.1,a,1.35),.03,6)
  B.face('ccourt-collision',[q(13.1,a,.24),q(13.1,b,.24),q(13.1,b,1.35),q(13.1,a,1.35)],True)
 # West entrance lettering with a single purple backing.
 G=Frame(B,CX-12.7,CZ,math.pi/2,y=0)
 G.box('ccourt-sign-purple',(0,5.45,-.12),(6.4,1.18,.18));G.text('CARNAVAL',(0,5.38,-.24),.86,'ccourt-white-letter');G.text('Court',(0,4.77,-.25),.62,'ccourt-gold-letter')
 # Public entry apron connects to existing promenade without rebuilding roads.
 B.planar('ccourt-floor-stone',box(CX-17,CZ-3,CX-12,CZ+3),.24,True)
 B.planar('ccourt-floor-stone',box(CX-5,CZ+12,CX-1,CZ+15),.24,True)
 B.groups={k:g for k,g in B.groups.items() if g['material']!='ccourt-collision'}
 samples=[]
 for r in [2,5,8,11]:
  for a in np.linspace(0,math.tau,36,endpoint=False):
   y=8-r*.65/4.2 if r<=4.2 else 7.35-(r-4.2)*1.75/8.6
   samples.append(list(q(r,float(a),y+.55)))
 Path('build/city-exteriors/carnaval-court-samples.json').write_text(json.dumps(samples))
 return dict(key=KEY,name='Carnaval Court open-air bar',center=[CX,0,CZ],bounds=[CX-18,CZ-15,CX+15,CZ+15],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
