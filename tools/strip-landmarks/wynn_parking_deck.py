"""Original inferred roof parking paint, scoped to Wynn garage111322083.
Aerial-guided rows; no surveyed stall count or verified garage circulation claim.
Paint has no collision and is clipped inside the existing visible roof.
"""
from common import Polygon,parts

def mark_deck(B,roof,height):
 safe=roof.buffer(-2.0)
 def point(u,v):return (565.18+.95633*u-.29227*v,-1395.326+.29227*u+.95633*v)
 def stripe(u0,v0,u1,v1):
  q=Polygon([point(u0,v0),point(u1,v0),point(u1,v1),point(u0,v1)]).intersection(safe)
  if not q.is_empty:B.planar('wy-parking-line-paint',q,height+.055)
 # Long aisles between perimeter and paired banks. Dimensions inferred in metres.
 for v0,v1 in [(5,10.2),(21,26.2),(26.2,31.4),(42.2,47.4),(47.4,52.6),(63.4,68.6)]:
  for i in range(47):
   u=8+i*2.7
   stripe(u-.055,v0,u+.055,v1)
  stripe(8,v0-.055,132.2,v0+.055)
