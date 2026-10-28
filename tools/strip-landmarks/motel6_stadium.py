"""Original photo-supported motel exterior and inferred public-room plan.
December2022 Street View fixes the east arrival facade; hidden room subdivisions
and public-room depths are estimates, never an as-built floorplan.
"""
from common import *
KEY='motel6-stadium'
def build(B):
 B.property=KEY+'-exterior';B.source='podium/'+KEY;B.detail=0
 F=Frame(B,0,0,y=0);p=footprint('way/1036271486');y=.18;upper=3.20
 entry=dict(p=[-781.50,y,2002.3],yaw=math.pi/2,width=1.55,height=2.52,name='Motel6 lobby entry',venue=KEY)
 windows=[dict(p=[-781.50,1.05,z],yaw=math.pi/2,width=w,height=1.47) for z,w in [(2006.3,3.2)]]
 B.shell(p,.02,6.18,'m6-white-stucco',openings=[entry,*windows],roof=False)
 B.planar('m6-membrane-paint',p,6.18)
 B.shell(p,6.17,6.57,'m6-shingle',roof=False,solid=False)
 ring=p.buffer(.65,join_style=2).difference(p.buffer(.12,join_style=2))
 for tri in triangles(ring):
  pts=[(x,6.57-.64*min(1,max(0,(p.distance(Point(x,z))-.12)/.53)),z) for x,z in list(tri.exterior.coords)[:-1]]
  B.upface('m6-shingle',pts)
 # Every bay is separate glazing, jambs, sill, blue door and projecting AC cabinet.
 coords=list(p.exterior.coords)
 for a,b in zip(coords,coords[1:]):
  L=math.dist(a,b);G=Frame(B,*a,math.atan2(-(b[1]-a[1]),b[0]-a[0]),y=0)
  outside=1 if not p.covers(Point(G.p(L/2,0,.2)[::2])) else -1
  q=G.p(L/2,0,0);long=L>20
  # Shallow mansard fascia: sloped gray shingle band and white drip edge.
  # Continuous mitred ring above closes every fascia corner.
  G.box('m6-white-paint',(L/2,5.89,outside*.5),(L+.05,.14,.65))
  G.box('m6-white-paint',(L/2,6.59,outside*.10),(L+.08,.10,.20))
  if not long:continue
  count=max(2,round(L/4.1));pitch=L/count
  for i in range(count):
   u=(i+.5)*pitch;world=G.p(u,0,0);lobby=world[0]>-782 and world[2]<2011
   for base in [y,upper]:
    if lobby and base==y:continue
    door=u-pitch*.30;win=u+pitch*.12
    G.box('m6-frame-paint',(door,base+1.10,outside*.07),(.99,2.22,.10))
    G.box('m6-blue-paint',(door,base+1.08,outside*.14),(.88,2.12,.06))
    G.box('m6-metal-paint',(door+.30,base+1.02,outside*.19),(.045,.10,.05))
    G.box('m6-number',(door,base+1.82,outside*.185),(.24,.09,.012))
    G.box('m6-frame-paint',(win,base+1.58,outside*.085),(1.80,1.46,.13))
    G.box('m6-glass',(win,base+1.58,outside*.17),(1.68,1.34,.04))
    G.box('m6-frame-paint',(win,base+1.58,outside*.21),(.035,1.35,.035))
    G.box('m6-ac',(win,base+.56,outside*.28),(1.12,.58,.47))
    for j in range(9):G.box('m6-vent',(win,base+.33+j*.055,outside*.53),(1.01,.018,.025))
   # Gallery supports are spaced to room bays, inside outer rail line.
   G.box('m6-white-paint',(u,1.62,outside*1.75),(.10,3.24,.10),True)
  # Walkable upper external gallery with substantial slab; ground apron kept local.
  G.box('m6-deck-concrete',(L/2,upper-.11,outside*1.03),(L,.22,2.12),True)
  G.box('m6-deck-concrete',(L/2,.09,outside*.95),(L,.18,1.92),True)
  # Rail gap at east stair arrival, all other gallery edges guarded.
  spans=[(0,L)]
  if q[0]>-782:
   at=LineString([a,b]).project(Point(-781.5,2032.6));spans=[(0,max(0,at-1.0)),(min(L,at+1),L)]
  for lo,hi in spans:
   if hi<=lo:continue
   for yy in [upper+.12,upper+1.08]:G.box('m6-white-paint',((lo+hi)/2,yy,outside*2.05),(hi-lo,.045,.045))
   for u in np.arange(lo,hi,.16):G.box('m6-white-paint',(float(u),upper+.59,outside*2.05),(.025,.99,.025))
   # Invisible simple collision curtain; no per-bar collision objects.
   pts=[G.p(lo,upper,outside*2.05),G.p(hi,upper,outside*2.05),G.p(hi,upper+1.1,outside*2.05),G.p(lo,upper+1.1,outside*2.05)]
   col=B.solids[B.property];off=len(col['vertices'])//3;col['vertices'].extend(v for pt in pts for v in pt);col['indices'].extend(off+j for j in [0,1,2,0,2,3])
 # East entry bay: blue architectural surround, real opening and broad lobby window.
 E=Frame(B,-781.5,2004.9,math.pi/2,y=0)
 E.box('m6-blue-paint',(0,4.68,.10),(11.8,2.9,.17))
 B.shell(box(-781.49,1999.05,-781.29,2010.8),.02,3.16,'m6-blue-paint',openings=[entry,*windows],roof=False,solid=False)
 E.box('m6-blue-paint',(0,2.96,.18),(8.4,.30,.40));E.box('m6-blue-paint',(0,6.2,.46),(9.2,.72,.9))
 E.text('welcome',(0,6.18,.94),.61,'m6-letter',back=True)
 E.text('5085',(2.60,2.87,.42),.17,'m6-letter',back=True)
 # Single straight gallery stair visible on the street wing; exact run inferred.
 S=Frame(B,-777.4,2025.6,y=0);S.stairs(0,0,1.60,upper-y,6.4,y=y)
 S.box('m6-deck-concrete',(-.9,upper-.10,7.0),(3.45,.20,1.25),True)
 for sign in [-1,1]:
  pts=[S.p(sign*.80,y,0),S.p(sign*.80,upper,6.4),S.p(sign*.80,upper+1.05,6.4),S.p(sign*.80,y+1.05,0)]
  col=B.solids[B.property];off=len(col['vertices'])//3;col['vertices'].extend(v for pt in pts for v in pt);col['indices'].extend(off+j for j in [0,1,2,0,2,3])
 # Public room plan: northeast lobby, small laundry behind; explicit inference.
 room=box(-797.0,1999.15,-781.50,2010.5)
 B.planar('m6-lobby-tile',room,y,True)
 F.box('m6-glass',(-781.25,1.785,2006.3),(.035,1.47,3.2),True)
 B.property=KEY+'-interior';B.source='public/'+KEY
 B.shell(room,y,3.02,'m6-interior',openings=[entry,*windows],roof=False);B.planar('m6-ceiling',room,3.01)
 # Original tile seams, dark central strip and entry mat follow official lobby photos.
 for x in np.arange(-796.8,-781.5,.6):F.box('m6-grout',(float(x),y+.008,2004.8),(.009,.012,11.2))
 for z in np.arange(1999.2,2010.5,.6):F.box('m6-grout',(-789.25,y+.008,float(z)),(15.3,.012,.009))
 F.box('m6-dark-tile',(-785.7,y+.018,2005.0),(1.8,.012,10.6))
 F.box('m6-mat',(-782.4,y+.03,2002.3),(1.7,.012,1.7))
 for x in [-784,-787,-793]:
  for z in [2001.5,2007.5]:F.lathe('m6-light-trim',x,z,[(2.965,.11),(3.005,.11)],12)
 # Internal partition leaves a 1.8m passage at z2003.0.
 for z,d in [(2000.4,2.5),(2007.2,6.6)]:F.box('m6-interior',(-790,1.59,z),(.16,2.82,d),True)
 F.box('m6-coffee-wood',(-789.3,.75,2007.7),(.7,1.14,2.2),True);F.box('m6-counter',(-789.3,1.35,2007.7),(.78,.08,2.28))
 for z in [2007.05,2008.3]:
  F.box('m6-control',(-788.93,.78,z),(.025,.92,.018));F.box('m6-metal-paint',(-788.90,.95,z+.12),(.045,.27,.025))
 for z in [2007.2,2008.1]:F.lathe('m6-metal-paint',-789.3,z,[(1.39,.17),(1.78,.17),(1.80,.13)],12)
 F.box('m6-screen',(-789.85,2.22,2007.7),(.08,.65,1.0))
 for z in [2005.8,2008.8]:
  F.box('m6-chair',(-783.2,.65,z),(.58,.14,.58),True);F.box('m6-chair',(-782.95,1.02,z),(.09,.70,.58))
  for x in [-783.42,-782.98]:
   for zz in [z-.22,z+.22]:F.tube('m6-metal-paint',(x,y,zz),(x,.60,zz),.022,6)
 F.lathe('m6-metal-paint',-783.3,2007.3,[(y,.28),(.24,.28),(.25,.04),(.85,.04)],12);F.lathe('m6-counter',-783.3,2007.3,[(.85,.39),(.91,.39)],20)
 # Laundry equipment with round inset doors, control strips and rear service clearance.
 for z in [2006.1,2007.3,2008.5]:
  F.box('m6-appliance',(-795.9,.75,z),(1.1,1.14,1.0),True)
  F.box('m6-control',(-795.32,1.18,z),(.04,.18,.91))
  G=Frame(B,-795.30,z,math.pi/2,y=0);G.tube('m6-metal-paint',(0,.68,0),(0,.68,.04),.34,24);G.tube('m6-glass',(0,.68,.045),(0,.68,.06),.27,24)
 F.box('m6-vending',(-795.8,1.15,2000.1),(1.2,1.94,1.0),True)
 F.box('m6-glass',(-795.17,1.28,2000.1),(.045,1.45,.75))
 for z in [2001,2004,2007]:F.light(-786,2.80,z,power=16,range=8)
 routes=[dict(name='Lobby arrival',points=[[-777,y,2002.3],[-782.4,y,2002.3],[-786,y,2002.3]]),dict(name='Lobby coffee and seating',points=[[-786,y,2002.3],[-786,y,2007.3],[-784.2,y,2007.3]]),dict(name='Laundry passage',points=[[-786,y,2002.3],[-789,y,2003],[-792,y,2003],[-793.5,y,2007.7]]),dict(name='East gallery stairs',points=[[-777.4,y,2025.2],[-777.4,y,2025.6],[-777.4,1.69,2028.8],[-777.4,upper,2032],[-777.4,upper,2032.65],[-780.1,upper,2032.65],[-780.1,upper,2015]])]
 from motel6_pool import add_pool
 routes.extend(add_pool(B,F))
 from motel6_arrival import add_arrival
 routes.extend(add_arrival(B,F))
 return dict(key=KEY,name='Motel 6 I-15 Stadium',center=[p.centroid.x,0,p.centroid.y],bounds=[-846,1985,-768,2069],structural=True,exteriorOnly=False,portals=[entry],zones=[dict(origin=[-797,y,1999.15],yaw=0,width=15.5,depth=11.35,height=2.83)],lights=B.lights,routes=routes,hotelSources=[])
if __name__=='__main__':
 B=Meshes();m=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(m,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
