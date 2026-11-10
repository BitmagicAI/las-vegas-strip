"""Original public nave, based on official album; dimensions and rows inferred.
No reproduced mural, private rooms, balcony or invented public side entrances.
"""
from common import *
from guardian_angel import KEY,Z,FRONT,REAR,RIDGE,EAVE

def interior(B,meta):
 B.property=KEY+'-interior';B.source='public/guardian-nave';B.detail=0
 # Existing exterior slab carries collision. Thin finish avoids duplicate solids.
 B.planar('ga-nave-floor',box(833.7,Z-12.3,877.8,Z+12.3),.247)
 for side in [-1,1]:
  B.planar('ga-nave-border',box(834,Z+side*1.55-.09,875,Z+side*1.55+.09),.25)
 for x in np.arange(836,874,2.8):
  B.planar('ga-nave-border',box(x-.12,Z-.12,x+.12,Z+.12),.251)
 # Separate inward faces follow the existing folded roof, inset by 8cm.
 for side in [-1,1]:
  z=Z+side*12.52
  for a,b in [(833.75,836.5)]+[(836.5+i*6.9,min(REAR-.12,836.5+(i+1)*6.9)) for i in range(6)]:
   r0=(a,RIDGE-.08,Z);r1=(b,RIDGE-.08,Z);e0=(a,EAVE,z);e1=(b,EAVE,z)
   faces=[(r0,r1,e1,e0)] if a<836.5 else [(r0,r1,((a+b)/2,11.12,z)),(r0,((a+b)/2,11.12,z),e0),(r1,e1,((a+b)/2,11.12,z))]
   for face in faces:
    points=list(face);v=np.array(points)
    if np.cross(v[1]-v[0],v[2]-v[0])[1]>0:points.reverse()
    B.face('ga-nave-cream',points)
 # Close the inherited low gap beneath the side glazing from inside the nave.
 # Inset plinth stays below the folded roof at its lowest corner.
 for side in [-1,1]:
  B.box('ga-nave-cream',(855.75,.62,Z+side*12.30),(43.9,.76,.12),True)
 # Inner face of the existing opaque entry tympanum; exterior mural remains untouched.
 B.face('ga-nave-cream',[(832.42,3.48,Z+10.8),(832.42,3.48,Z-10.8),(832.42,22.1,Z)])
 # Two banks, 20 rows each. 3.2m central aisle, clear rear and sanctuary cross aisles.
 # Seat height .46m above floor; 1.4m row pitch, .86m clear between backs.
 for x in np.arange(840,868,1.4):
  for side in [-1,1]:
   z=Z+side*5.3
   B.box('ga-pew-wood',(x,.66,z),(.48,.08,7.2),True)
   B.box('ga-pew-wood',(x-.28,1.01,z),(.10,.66,7.2),True)
   for dz in [-3.5,0,3.5]:
    B.box('ga-pew-wood',(x,.44,z+dz),(.38,.40,.10),True)
   for dz in [-3.65,3.65]:
    B.box('ga-pew-wood',(x-.03,.79,z+dz),(.64,1.10,.12),True)
 # Simple level sanctuary furniture. No unsupported reconstruction of steps or mural.
 B.box('ga-nave-dark',(877.65,2.1,Z),(.12,3.7,13))
 B.box('ga-nave-gold',(877.55,2.4,Z),(.05,3.5,3.2))
 B.box('ga-nave-stone',(873.7,1.12,Z),(1.15,.18,3.6),True)
 B.box('ga-nave-stone',(873.7,.67,Z),(.85,.72,2.5),True)
 B.box('ga-nave-stone',(872.8,.79,Z-5),(.7,1.1,.85),True)
 B.box('ga-nave-stone',(872.8,1.38,Z-5),(.9,.12,1.05))
 # Original plain hanging cross; no sculptural figure or copied sacred artwork.
 B.box('ga-pew-wood',(873.8,7.3,Z),(.18,3.7,.18))
 B.box('ga-pew-wood',(873.8,8.05,Z),(.18,.18,2.1))
 B.tube('ga-frame',(873.8,9.15,Z),(873.8,RIDGE-.12,Z),.012,4)
 meta.update(name='Guardian Angel Cathedral and public nave',exteriorOnly=False,
  portals=[dict(p=[833.6,.25,Z],yaw=math.pi/2,width=3.94,height=2.7,name='Cathedral west public entrance')],
  zones=[dict(origin=[833.7,.24,Z],yaw=math.pi/2,width=24.6,depth=44,height=23)])
 return meta
