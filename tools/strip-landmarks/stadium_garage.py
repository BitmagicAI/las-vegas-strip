"""Original open-deck garage on mapped way/790044912.
March 2020 Street View establishes three raised parapet bands and ground entry.
Elevations and hidden circulation are estimates, explicitly recorded separately.
"""
from common import *
from home2_stadium import frame,YAW
KEY='stadium-garage'
def build(B):
 B.property=KEY+'-exterior';B.source='podium/'+KEY;B.detail=0
 F=frame(B);p=footprint('way/790044912');levels=[.12,3.36,6.60,9.84]
 # Open decks, not a textured solid box. Upper access remains unverified.
 for y in levels:
  B.planar('sg-deck',p,y,True)
  if y>.2:B.planar('sg-soffit',p,y-.24)
  B.shell(p,y-.24,y,'sg-concrete',roof=False)
 coords=list(p.exterior.coords)
 for a,b in zip(coords,coords[1:]):
  L=math.dist(a,b)
  G=Frame(B,*a,math.atan2(-(b[1]-a[1]),b[0]-a[0]),y=0)
  q=G.p(L/2,0,0);lx=F.co*(q[0]-F.x)-F.si*(q[2]-F.z);lz=F.si*(q[0]-F.x)+F.co*(q[2]-F.z)
  outside=1 if not p.covers(Point(G.p(L/2,0,.2)[::2])) else -1
  screen=(abs(lz+8.68)<.2 and L>20) or (lx>76 and L<7)
  if screen:
   # Hotel-facing vertical painted precast screen, white fins and ochre accents.
   G.box('sg-white',(L/2,5.5,0),(L,11,.22),True)
   for i,u in enumerate(np.arange(.15,L,.98)):
    G.box('sg-ochre' if i%7==2 else 'sg-gray',(float(u)+.29,5.49,outside*.14),(.57,10.96,.045))
    G.box('sg-white',(float(u),5.52,0),(.14,11.04,.48))
  else:
   for y in levels[1:]:G.box('sg-gray',(L/2,y+.78,0),(L,1.56,.28),True)
   if L>3:
    for u in np.linspace(.25,L-.25,max(2,round(L/7)+1)):
     G.box('sg-concrete',(float(u),5.5,0),(.42,11,.48),True)
   # Ground edge protection; south east facade is the vehicle opening.
   if not (lx>76 and L>10):G.box('sg-concrete',(L/2,.5,0),(L,.76,.22),True)
 # Internal columns and beam soffits within footprint.
 for x in [30,43,56,69]:
  for z in [-18,-32]:
   if p.buffer(-1).covers(Point(F.p(x,0,z)[::2])):
    F.box('sg-concrete',(x,4.9,z),(.5,9.8,.5),True)
    for y in levels[1:]:F.box('sg-soffit',(x,y-.44,z),(6,.4,.35))
 # Original parking striping clipped to the actual irregular plan.
 for y in levels:
  for z in [-42,-29,-15]:
   for x in np.arange(27,75,2.65):
    stripe=F.poly([(x,z),(x+.09,z),(x+.09,z+4.6),(x,z+4.6)]).intersection(p.buffer(-.65))
    B.planar('sg-line',stripe,y+.012)
 # Ground-level entrance hardware seen in Street View; gate held open for access.
 F.box('sg-green',(76.7,.95,-10.7),(1.3,1.9,1.0),True)
 for z in [-11.8,-9.6]:F.tube('sg-yellow',(77.2,0,z),(77.2,1.1,z),.055,10)
 F.box('sg-white',(76.8,.55,-20),(.45,1.1,.45),True)
 F.box('sg-red',(76.8,2.5,-20),(.08,3.1,.08))
 F.box('sg-yellow',(77.2,2.85,-26),(.12,.17,6.2))
 # No fictional ramps: parking circulation on the ground is accessible; upper access pending survey.
 routes=[dict(name='Garage entry and ground aisle',points=[F.p(x,.12,z) for x,z in [(81,-25),(74,-25),(65,-25),(54,-25),(40,-25),(30,-25)]]),dict(name='Ground cross aisle',points=[F.p(x,.12,z) for x,z in [(54,-25),(54,-19),(62,-19),(70,-19)]])]
 xmin,zmin,xmax,zmax=p.bounds
 return dict(key=KEY,name='Stadium District parking garage',center=[p.centroid.x,0,p.centroid.y],bounds=[xmin,zmin,xmax,zmax],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=routes,hotelSources=[])
if __name__=='__main__':
 B=Meshes();m=build(B);B.save_all();(OUT/(KEY+'-metadata.json')).write_text(json.dumps(m,indent=2)+'\n');print(KEY,sum(len(g['faces']) for g in B.groups.values()),'triangles')
