"""Public meeting rooms from the official dimensioned plan; ceiling/furniture inferred.
No claim of an indoor connection to reception or of an identified boardroom.
"""
from common import *
KEY='mardi-gras'
FLOOR=.16
CEILING=3.18  # Photo-fitted estimate, independent of the unresolved terrace height.
DIVIDER=1694.14+17.6784  # 58 ft New Orleans; combined plan 103 x 38 ft.
def entries():
 return [
 dict(p=[x,FLOOR,z],yaw=yaw,width=w,height=2.25,name=name,venue=KEY)
 for x,z,yaw,w,name in [(1694,-1053.9,-math.pi/2,2,'Meeting rooms west entrance'),
 (1713,-1048.1,0,1.6,'Baton Rouge north exit'),(1713,-1059.73,math.pi,1.6,'Baton Rouge south exit'),
 (1702,-1059.73,math.pi,1.6,'New Orleans side exit')]]
def build_interior(B,meta,q):
 B.property=KEY+'-interior';B.source='public/'+KEY;B.detail=0
 inside=q.buffer(-.16,join_style=2)
 B.shell(inside,FLOOR,CEILING,'mg-room-wall',openings=meta['portals'],roof=False,solid=False)
 B.planar('mg-carpet',inside,FLOOR+.008)
 # Downward-facing ceiling is deliberately below the existing terrace structure.
 for poly in parts(inside):
  for tri in triangles(poly):
   pts=[(x,CEILING,z) for x,z in list(tri.exterior.coords)[:-1]]
   a=np.array(pts);pts=pts if np.cross(a[1]-a[0],a[2]-a[0])[1]<0 else list(reversed(pts))
   B.face('mg-ceiling',pts)
 # Continuous trim is cut around every exit, never stretched across an opening.
 for lo,hi in [(FLOOR,.28),(1.02,1.09),(3.07,3.14)]:
  B.shell(inside.buffer(-.018),lo,hi,'mg-room-trim',openings=meta['portals'],roof=False,solid=False)
 # Foldable wall in its divided configuration; two open doorways match the plan.
 for za,zb in [(-1059.55,-1058.95),(-1057.35,-1050.45),(-1048.85,-1048.26)]:
  B.box('mg-partition',(DIVIDER,1.67,(za+zb)/2),(.14,3.02,zb-za),True)
  for z in np.arange(za+.05,zb,.65):B.box('mg-room-trim',(DIVIDER-.078,1.67,float(z)),(.018,3.02,.018))
 for z in [-1058.15,-1049.65]:B.box('mg-partition',(DIVIDER,2.83,z),(.14,.7,1.6),True)
 B.box('mg-room-trim',(DIVIDER,3.13,-1053.9),(.22,.08,11.2))
 # Baton Rouge North/South divider, with no invented door through it.
 B.box('mg-partition',((DIVIDER+1725.5)/2,1.67,-1053.9),(1725.5-DIVIDER,3.02,.14),True)
 B.box('mg-room-trim',((DIVIDER+1725.5)/2,3.13,-1053.9),(1725.5-DIVIDER,.08,.22))
 # Plantation shutters fitted behind the existing long-side window bays.
 for z in [-1048.32,-1059.51]:
  for x in [1697.85,1701.85,1705.85,1709.85,1713.85,1717.85,1721.85]:
   if any(abs(x-o['p'][0])<2.2 and abs(z-o['p'][2])<.5 for o in meta['portals']):continue
   B.box('mg-room-trim',(x,1.6,z),(2.7,2.05,.06))
   for dx in [-.67,.67]:
    B.box('mg-door',(x+dx,1.6,z),(1.23,1.88,.065))
    for y in np.arange(.73,2.53,.12):B.box('mg-room-trim',(x+dx,float(y),z),(1.2,.065,.1))
 # Sparse event setting from official dual-set photo; circulation stays open.
 for x in [1698,1704,1708,1717,1722]:
  for z in [-1051.9,-1056.1]:
   F=Frame(B,x,z,y=FLOOR)
   F.lathe('mg-iron',0,0,[(0,.33),(.06,.33),(.68,.06)],12)
   F.lathe('mg-table-cloth',0,0,[(.08,.82),(.65,.82),(.76,.83)],48)
   B.planar('mg-table-cloth',Point(x,z).buffer(.83,resolution=12),FLOOR+.76)
   # Solid low footprint prevents walking through table/chairs.
   F.box('mg-table-cloth',(0,.37,0),(1.1,.74,1.1),True)
   for a in [0,math.pi/2,math.pi,3*math.pi/2]:
    C=Frame(B,x+1.15*math.cos(a),z+1.15*math.sin(a),-a+math.pi/2,y=FLOOR)
    C.box('mg-seat',(0,.46,0),(.46,.12,.48),True)
    C.box('mg-seat',(0,.24,0),(.47,.44,.49))
    C.box('mg-seat',(0,.73,.22),(.46,.57,.06),True)
    for dx in [-.19,.19]:
     for dz in [-.18,.18]:C.box('mg-iron',(dx,.22,dz),(.025,.44,.025))
 # Recessed fixtures and borrowed fixed-pool lighting (no runtime light creation).
 for x in [1698,1704,1709,1716,1722]:
  for z in [-1051.2,-1056.8]:
   B.box('mg-frame',(x,3.135,z),(.64,.05,1.24));B.box('mg-ceiling-light',(x,3.104,z),(.55,.012,1.15))
 meta['lights']=[dict(p=[x,2.9,z],color=0xffead3,power=22,range=13) for x,z in [(1701,-1053.9),(1708,-1053.9),(1719,-1051),(1719,-1056.8)]]
 meta['routes'] += [dict(name='New Orleans west entry and south exit',points=[[1692,FLOOR,-1053.9],[1696,FLOOR,-1053.9],[1702,FLOOR,-1053.9],[1702,FLOOR,-1058],[1702,FLOOR,-1061]]),
 dict(name='Baton Rouge north room',points=[[1713,FLOOR,-1046.8],[1713,FLOOR,-1049.65],[1710,FLOOR,-1049.65],[1708,FLOOR,-1049.65]]),
 dict(name='Baton Rouge south room',points=[[1713,FLOOR,-1061],[1713,FLOOR,-1058.15],[1710,FLOOR,-1058.15],[1708,FLOOR,-1058.15]])]
 return meta
