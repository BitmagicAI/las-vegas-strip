"""Original photo-informed Peppermill public rooms; dimensions/layout are inferred.

Official homepage/photos establish Fireside furniture; Link17 Summer2024 p23
establishes diner counter, blue booths, floral canopy and stained-glass lamps.
No photograph is used as a texture. No surveyed seating plan is claimed.
"""
from common import *

def interior(B):
 B.property='peppermillRetail-interior';B.source='peppermill-public';B.detail=0
 room=footprint('way/160585815').buffer(-.25)
 B.planar('pmr-carpet',room,.265)
 # The old shell remains the structural floor/ceiling. Reversible finish below it.
 for poly in parts(room):
  for tri in triangles(poly):B.face('pmr-ceiling',[ (x,3.88,z) for x,z in list(tri.exterior.coords)[:-1]][::-1])
 # Lower wall liners do not cross the west entrance at z=-1965.3.
 for x in [872.7,909.2]:
  for lo,hi in ([(-1977,-1967.4),(-1963.2,-1953)] if x<880 else [(-1977,-1953)]):
   B.box('pmr-wall', (x,1.7,(lo+hi)/2),(.12,2.9,hi-lo))
 for z in [-1977,-1952.7]:B.box('pmr-wall',(891,1.7,z),(36,2.9,.12))
 # Open-ended divider leaves the central east/west route and both room entries clear.
 for xa,xb in [(880,887),(893,907)]:
  B.box('pmr-wall',((xa+xb)/2,1.7,-1967.2),(xb-xa,2.9,.16),True)
  B.box('pmr-pink-led',((xa+xb)/2,3.16,-1967.06),(xb-xa,.045,.045))
 for z in [-1976.7,-1967.55,-1962.7,-1953]:
  B.box('pmr-pink-led',(891,3.65,z),(35,.055,.055))
  B.box('pmr-blue-led',(891,3.52,z),(35,.04,.04))
 # Fireside basin: opaque original blue ceramic/water finish avoids costly mirror pass.
 cx,cz=884.5,-1972.1
 B.lathe('pmr-basin',(cx,cz),[(.27,2.18),(.72,2.18),(.82,2.05),(.82,1.76),(.53,1.7)],48)
 B.planar('pmr-water',Point(cx,cz).buffer(1.71,resolution=20),.55)
 B.shell(Point(cx,cz).buffer(2.15,resolution=16),.27,.78,'pmr-basin',roof=False)
 B.lathe('pmr-dark',(cx,cz),[(.55,.63),(.72,.57),(.76,.43)],24)
 for j in range(9):
  a=j*math.tau/9;x=cx+.27*math.cos(a);z=cz+.27*math.sin(a)
  B.tube('pmr-flame',(x,.74,z),(x+.07,1.27+.22*(j%3),z-.04),.085,5,.015)
 # Curved upholstered seats, with a wide south-facing approach.
 for lo in np.linspace(math.radians(190),math.radians(336.7),12):
  sofa(B,cx,cz,2.75,3.48,lo,lo+math.radians(13.0),'pmr-rose')
 for x in [880.8,888.2]:
  B.tube('pmr-chrome',(x,.27,-1975.4),(x,2.9,-1975.4),.055,10)
 B.tube('pmr-chrome',(880.8,2.9,-1975.4),(888.2,2.9,-1975.4),.065,10)
 # Backbar with shelves, original bottles, countertop and stools.
 B.box('pmr-dark',(899.6,.8,-1974.6),(12.8,1.08,1.1),True)
 B.box('pmr-table',(899.6,1.38,-1974.6),(13.1,.13,1.35))
 B.box('pmr-mirror',(899.6,2.4,-1976.65),(13,2.25,.08))
 for y in [1.55,2.15,2.75]:
  B.box('pmr-chrome',(899.6,y,-1976.25),(12.8,.065,.5))
  B.box('pmr-pink-led',(899.6,y-.05,-1976.0),(12.8,.035,.03))
  for x in np.arange(894,906,.55):
   B.tube('pmr-bottle',(x,y+.04,-1976.23),(x,y+.29,-1976.23),.075,8)
   B.tube('pmr-bottle',(x,y+.29,-1976.23),(x,y+.41,-1976.23),.031,8)
 for x in np.arange(894,906,1.5):stool(B,x,-1973.1,'pmr-rose')
 # Dining room: long service counter and curved blue booths, as in primary photo.
 B.box('pmr-dark',(892.5,.77,-1962.2),(26,1.02,.8),True)
 B.box('pmr-table',(892.5,1.32,-1962.2),(26.3,.12,1.0))
 B.box('pmr-mirror',(892.5,2.75,-1962.72),(26,1.05,.06))
 for x in np.arange(880.5,905,1.65):stool(B,x,-1960.9,'pmr-blue')
 for x in [880.5,886.5,892.5,898.5,904.5]:
  # Horseshoe booth leaves the north aisle open.
  for lo in np.linspace(0,math.radians(160),9):
   sofa(B,x,-1955.4,1.02,1.68,lo,lo+math.radians(19.7),'pmr-blue',stripe=True)
  B.tube('pmr-chrome',(x,.27,-1955.1),(x,.94,-1955.1),.12,10)
  B.lathe('pmr-table',(x,-1955.1),[(.94,.86),(1.02,.86)],24)
  B.planar('pmr-table',Point(x,-1955.1).buffer(.86,resolution=12),1.02)
  # Faceted coloured-glass shade is an original floral-color interpretation.
  B.tube('pmr-chrome',(x,1.05,-1954.2),(x,1.72,-1954.2),.035,8)
  B.lathe('pmr-lamp-blue',(x,-1954.2),[(1.72,.65),(2.24,.32),(2.38,.13)],12)
  for a in np.linspace(0,math.tau,12,endpoint=False):
   # Original coloured-glass petals on each shade panel, not a copied image.
   v=a+math.pi/12
   B.face('pmr-lamp-pink',[(x+.49*math.cos(v-.12),1.94,-1954.2+.49*math.sin(v-.12)),(x+.49*math.cos(v+.12),1.94,-1954.2+.49*math.sin(v+.12)),(x+.28*math.cos(v),2.28,-1954.2+.28*math.sin(v))])
   B.tube('pmr-chrome',(x+.65*math.cos(a),1.72,-1954.2+.65*math.sin(a)),(x+.13*math.cos(a),2.38,-1954.2+.13*math.sin(a)),.012,4)
  canopy(B,x,-1953.4)
 # Host desk beside, not across, the existing entrance axis.
 B.box('pmr-dark',(876, .86,-1962.4),(1.5,1.2,.9),True)
 B.box('pmr-table',(876,1.5,-1962.4),(1.65,.08,1.0))
 return dict(zones=[dict(origin=[891,.24,-1977],yaw=0,width=36,depth=24.2,height=3.65)],lights=[dict(p=p,color=c,power=4,range=11) for p,c in [([884,3,-1972],0xb773ce),([900,3,-1972],0xbf80c9),([883,3,-1957],0xf3e3d0),([901,3,-1957],0xe9c9e8)]])

def stool(B,x,z,mat):
 B.tube('pmr-chrome',(x,.27,z),(x,.92,z),.065,10)
 B.lathe('pmr-chrome',(x,z),[(.28,.32),(.32,.32)],12)
 B.lathe(mat,(x,z),[(.88,.34),(1.02,.34)],16)
 B.planar(mat,Point(x,z).buffer(.34,resolution=8),1.02)
 B.box(mat,(x,1.24,z+.27),(.65,.55,.14),True)

def canopy(B,x,z):
 B.tube('pmr-bark',(x,.28,z),(x,3.45,z),.12,8,.06)
 rng=np.random.default_rng(round(x))
 for j in range(8):
  a=j*math.tau/8;xx=x+1.9*math.cos(a);zz=z+1.5*math.sin(a)
  B.tube('pmr-bark',(x,2.3,z),(xx,3.45,zz),.055,6,.02)
  for k in range(18):
   p=(xx+rng.uniform(-.5,.5),3.45+rng.uniform(-.15,.12),zz+rng.uniform(-.4,.4))
   xx,yy,zz=p
   ring=[(xx+.25,yy,zz),(xx,yy,zz+.16),(xx-.25,yy,zz),(xx,yy,zz-.16)]
   for a,b in zip(ring,ring[1:]+ring[:1]):
    B.face('pmr-blossom',[a,b,(xx,yy+.09,zz)])
    B.face('pmr-blossom',[b,a,(xx,yy-.09,zz)])


def band(B,mat,x,z,profile,lo,hi,solid=True):
 steps=max(3,math.ceil((hi-lo)*14))
 for (r,y),(rr,yy) in zip(profile,profile[1:]+profile[:1]):
  for a,b in zip(np.linspace(lo,hi,steps+1),np.linspace(lo,hi,steps+1)[1:]):
   B.face(mat,[(x+r*math.cos(a),y,z+r*math.sin(a)),(x+r*math.cos(b),y,z+r*math.sin(b)),(x+rr*math.cos(b),yy,z+rr*math.sin(b)),(x+rr*math.cos(a),yy,z+rr*math.sin(a))],solid)
 for a,rev in [(lo,True),(hi,False)]:
  pts=[(x+r*math.cos(a),y,z+r*math.sin(a)) for r,y in profile]
  B.face(mat,pts[::-1] if rev else pts,solid)

def sofa(B,x,z,inner,outer,lo,hi,mat,stripe=False):
 # Bevelled continuous upholstered arcs, with narrow cushion seams.
 band(B,mat,x,z,[(inner+.08,.31),(outer-.05,.31),(outer,.38),(outer,.59),(outer-.06,.67),(inner+.06,.67),(inner,.59),(inner,.39)],lo,hi)
 band(B,mat,x,z,[(outer-.16,.55),(outer+.12,.55),(outer+.15,1.16),(outer+.09,1.24),(outer-.06,1.24),(outer-.15,1.16)],lo,hi)
 if stripe:band(B,'pmr-cyan',x,z,[(outer-.153,1.06),(outer-.153,1.16),(outer-.16,1.16),(outer-.16,1.06)],lo,hi,False)
