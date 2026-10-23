"""Shake Shack north Strip corner: April2025 street reference, retaining hotel structure."""
from common import *
def exterior(B):
 B.source='shake-shack-frontage';B.detail=0;F=Frame(B,-50.943,1431.246,-math.pi/2,y=0)
 # Replace the previous generic frontage skin only; hotel shell/interiors remain.
 F.box('ssk-cladding-paint',(12,4.65,-.46),(24,8.7,.12))
 for u in np.arange(.1,24,.24):F.box('ssk-rib-paint',(float(u),4.5,-.54),(.025,8.5,.035))
 # Glazing and folded metal awning at pedestrian scale.
 for lo,hi in [(1,6.5),(7,12.5),(13,18.5),(19,23.5)]:
  F.box('ssk-frame-paint',((lo+hi)/2,2.55,-.59),(hi-lo,2.8,.12));F.box('ssk-glass',((lo+hi)/2,2.55,-.68),(hi-lo-.12,2.66,.06))
  for u in [lo,(lo+hi)/2,hi]:F.box('ssk-frame-paint',(u,2.55,-.74),(.065,2.8,.12))
  for y in [1.15,3.2,3.95]:F.box('ssk-frame-paint',((lo+hi)/2,y,-.76),(hi-lo,.07,.12))
 for u in [8,9.3]:
  F.box('ssk-frame-paint',(u,2.4,-.81),(1.2,2.45,.1));F.box('ssk-glass',(u,2.4,-.88),(1.07,2.31,.04));F.tube('ssk-steel-paint',(u+.4,1.9,-.96),(u+.4,2.5,-.96),.025,8)
 B.face('ssk-awning-paint',[F.p(0,4.7,-.6),F.p(24,4.7,-.6),F.p(24,4.05,-1.8),F.p(0,4.05,-1.8)])
 # Broad pale metal canopy has a sloped soffit, no solid 5m wall beneath.
 for mat,dy in [('ssk-soffit-paint',0),('ssk-roof-paint',.13)]:
  pts=[F.p(0,6.05+dy,0),F.p(30.2,6.05+dy,0),F.p(30.2,5.45+dy,-4.15),F.p(0,5.45+dy,-4.15)]
  if dy>0:B.upface(mat,pts,True)
  else:B.face(mat,pts)
 F.tube('ssk-frame-paint',(0,5.48,-4.15),(30.2,5.48,-4.15),.08,8)
 for u in np.arange(.1,30,.55):F.tube('ssk-seam-paint',(float(u),6.02,0),(float(u),5.42,-4.15),.012,5)
 # Return facade uses the same cladding vocabulary; concealed tenant bays estimated.
 N=Frame(B,-72.166,1431.101,0,y=0)
 N.box('ssk-cladding-paint',(10.6,4.65,-.46),(21.2,8.7,.12))
 for u in np.arange(.12,21.2,.24):N.box('ssk-rib-paint',(float(u),4.5,-.54),(.025,8.5,.035))
 for lo,hi in [(1,6),(7,12),(13,20.2)]:
  N.box('ssk-frame-paint',((lo+hi)/2,2.15,-.59),(hi-lo,3.7,.12));N.box('ssk-glass',((lo+hi)/2,2.15,-.68),(hi-lo-.12,3.56,.06))
  for u in np.arange(lo,hi+.01,1.4):N.box('ssk-frame-paint',(float(u),2.15,-.74),(.065,3.7,.12))
  for y in [.3,3.15,4.0]:N.box('ssk-frame-paint',((lo+hi)/2,y,-.76),(hi-lo,.07,.12))
  N.box('ssk-frame-paint',((lo+hi)/2,4.3,-1.05),(hi-lo+.15,.14,1.5))
 N.text('SHAKE SHACK',(10.6,4.8,-.68),.65,'ssk-letter-paint')
 # Raised terrace and access: curb wall broken for real stairs and a north ramp.
 F.box('ssk-deck-concrete',(12,.69,-3.6),(24,.92,6.1),True)
 for lo,hi in [(0,18.3),(21.6,24)]:
  F.box('ssk-wall-concrete',((lo+hi)/2,.6,-6.7),(hi-lo,.86,.28),True)
  for y in [1.38,1.62,1.86,2.13]:F.tube('ssk-frame-paint',(lo,y,-6.7),(hi,y,-6.7),.022,6)
  for u in np.arange(lo,hi+.01,1.5):F.box('ssk-frame-paint',(float(u),1.7,-6.7),(.075,1.15,.075),True)
 # Five shallow treads; smooth collision ramp tracks their noses.
 for k in range(5):
  F.box('ssk-step-concrete',(19.95,.18+(k+1)*.194/2,-8.5+(k+.5)*.36),(3.1,(k+1)*.194,.36))
 B.upface('ssk-collision',[F.p(18.4,.18,-8.5),F.p(21.5,.18,-8.5),F.p(21.5,1.15,-6.7),F.p(18.4,1.15,-6.7)],True)
 for u in [18.4,21.5]:F.tube('ssk-frame-paint',(u,1.16,-8.5),(u,2.13,-6.7),.035,8)
 # North terrace access ramp, 9.7m run for .97m rise.
 B.upface('ssk-step-concrete',[F.p(-9.7,.18,-6.5),F.p(-9.7,.18,-3.8),F.p(0,1.15,-3.8),F.p(0,1.15,-6.5)],True)
 for w in [-6.5,-3.8]:
  F.tube('ssk-frame-paint',(-9.7,1.18,w),(0,2.15,w),.035,8)
  for u in np.arange(-9.7,.1,1.6):F.tube('ssk-frame-paint',(float(u),.18+(u+9.7)*.1,w),(float(u),1.18+(u+9.7)*.1,w),.035,8)
 # Outdoor seating and the long window bar seen at street level.
 F.box('ssk-counter-paint',(16,2.18,-1.5),(12,.1,.55))
 for u in [11,13.1,15.2,17.3,19.4,21.5]:
  F.box('ssk-seat-paint',(u,1.89,-2.2),(.42,.08,.42))
  for dx in [-.16,.16]:
   for dz in [-.16,.16]:F.tube('ssk-steel-paint',(u+dx,1.15,-2.2+dz),(u+dx,1.87,-2.2+dz),.022,6)
  F.tube('ssk-steel-paint',(u-.18,1.88,-2.4),(u-.18,2.4,-2.4),.022,6);F.tube('ssk-steel-paint',(u+.18,1.88,-2.4),(u+.18,2.4,-2.4),.022,6);F.tube('ssk-steel-paint',(u-.18,2.4,-2.4),(u+.18,2.4,-2.4),.022,6)
 F.box('ssk-frame-paint',(9.2,4.75,-4.22),(15,.65,.12));F.text('SHAKE SHACK',(9.2,4.74,-4.31),.73,'ssk-letter-paint')
 F.text('BURGERS   FROZEN CUSTARD   FRIES   SHAKES',(15,4.13,-1.85),.24,'ssk-letter-paint')
 # Access apron avoids changing city pavements outside this entrance.
 apron=F.poly([(-10.5,-9),(24,-9),(24,-6.7),(-10.5,-6.7)]);B.planar('ssk-paving-concrete',apron,.18,True)
 B.groups={k:g for k,g in B.groups.items() if g['material']!='ssk-collision'}
