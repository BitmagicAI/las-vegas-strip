"""Chayo corner patio and upper terrace, official photo/aerial-guided exterior."""
from common import *
from forum_shops import facade_frame
KEY='chayoTerraces';IDS=['way/402543937']
def exterior(B):
 B.property=KEY+'-exterior';B.source='chayo-terraces';B.detail=0
 p=footprint(IDS[0]);parent=footprint('way/402543936');deck=4.7
 B.planar('chy-tile',p,.24,True);B.planar('chy-tile',p,deck,True)
 # Upper floor has thickness and a downward-facing soffit.
 for t in triangles(p):B.face('chy-cream-paint',[(x,deck-.25,z)for x,z in list(t.exterior.coords)[:-1]][::-1])
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  F,L,nx,nz=facade_frame(B,a,b,p,.025);mid=Point((a[0]+b[0])/2,(a[1]+b[1])/2)
  if parent.distance(mid)<.2:continue
  F.box('chy-cream-paint',(L/2,deck-.12,0),(L,.25,.25))
  # Lower glazed restaurant edge, set within the deck perimeter.
  F.box('chy-glass',(L/2,2.25,.10),(max(.1,L-.1),3.9,.08),True)
  for x in np.linspace(.12,L-.12,max(2,int(L/1.8)+1)):
   F.box('chy-black-paint',(x,2.3,-.04),(.09,4.1,.16))
  F.box('chy-black-paint',(L/2,4.2,-.06),(L,.18,.18))
  for y in [deck+.35,deck+.72,deck+1.1]:F.tube('chy-rail-paint',(0,y,0),(L,y,0),.035,8)
  for x in np.linspace(0,L,max(2,int(L/1.4)+1)):F.box('chy-rail-paint',(x,deck+.55,0),(.065,1.1,.065))
  # Invisible simple upper guard collider; the horizontal rail stays visually open.
  F.box('chy-collision',(L/2,deck+.5,0),(L,1,.06),True)
 # West facade's canopy, a short sloped translucent roof over the upper bar edge.
 for z in [-184.5,-180,-176.7]:
  B.box('chy-black-paint',(120.2,6.15,z),(.23,2.9,.23))
  for y in [5.65,6.75]:B.box('chy-orange-paint',(120.2,y,z),(.25,.06,.25))
 for za,zb in [(-185.6,-181),(-181,-176.4)]:
  B.face('chy-canopy-glass',[(119.5,7.7,za),(119.5,7.7,zb),(122,7.1,zb),(122,7.1,za)])
  B.path('chy-black-paint',[(119.5,7.7,za),(122,7.1,za),(122,7.1,zb)],.08,6)
 # Glazed upper bar frontage sits clear of the retained parent wall.
 B.box('chy-glass',(119.98,6.3,-181),(.12,2.8,9.2))
 for z in np.arange(-185.5,-176.3,1.5):
  B.box('chy-black-paint',(120.08,6.3,z),(.10,2.9,.08))
 for z in np.arange(-185.6,-176.3,1.15):
  B.path('chy-black-paint',[(119.5,7.7,z),(122,7.1,z)],.045,6)
 # Lower timber pergola occupies only the patio side; leave promenade centerline clear.
 lower=Polygon([(120,-175.5),(125,-175.3),(129.6,-179.5),(132,-177),(127,-172.8),(120,-172.8)])
 B.planar('chy-tile',lower.buffer(.8,join_style=2).difference(p.buffer(.01)),.24,True)
 for x,z in [(120.2,-173),(126.3,-173),(131.4,-176.7)]:B.box('chy-timber-paint',(x,1.9,z),(.25,3.3,.25),True)
 for a,b in [((120.2,-173),(126.3,-173)),((126.3,-173),(131.4,-176.7))]:
  F,L,_,_=facade_frame(B,a,b,lower,0);F.box('chy-timber-paint',(L/2,3.52,0),(L+.25,.25,.27))
 for t in triangles(lower.buffer(-.15)):
  B.face('chy-red-fabric',[(x,3.42,z)for x,z in list(t.exterior.coords)[:-1]])
 # Open lower patio railing leaves a 1.8 m entrance gap between timber bays.
 for a,b in [((120.2,-172.9),(122.1,-172.9)),((123.9,-172.9),(126.3,-172.9)),((126.3,-172.9),(131.4,-176.7))]:
  F,L,_,_=facade_frame(B,a,b,lower,0)
  F.box('chy-black-paint',(L/2,1.15,0),(L,.06,.06))
  for xx in np.arange(.06,L,.24):F.box('chy-black-paint',(xx,.7,0),(.03,.9,.03))
  F.box('chy-collision',(L/2,.7,0),(L,.9,.06),True)
 B.text('CHAYO',(125.1,3.72,-172.64),.6,math.pi,'chy-white-letter')
 # Tables and slatted metal chairs are batched decorative geometry.
 def chair(x,z,y,yaw):
  F=Frame(B,x,z,yaw=yaw,y=y)
  F.box('chy-tan-paint',(0,.48,0),(.43,.07,.44))
  for xx in [-.2,.2]:
   for zz in [-.18,.18]:F.box('chy-black-paint',(xx,.23,zz),(.035,.46,.035))
   F.box('chy-black-paint',(xx,.72,.2),(.035,.48,.035))
  for yy in [.66,.79,.92]:F.box('chy-tan-paint',(0,yy,.21),(.43,.10,.035))
 for x,z in [(123.6,-183.7),(127.4,-183.7),(123.6,-179.6),(126.1,-177.5)]:
  B.box('chy-table-stone',(x,deck+.78,z),(1.1,.06,.72))
  for dx in [-.45,.45]:
   for dz in [-.27,.27]:B.box('chy-black-paint',(x+dx,deck+.38,z+dz),(.035,.76,.035))
  chair(x,z-.68,deck,0);chair(x,z+.68,deck,math.pi)
 for x,z in [(121.5,-173.8),(128.6,-176.4)]:
  B.box('chy-table-stone',(x,1.02,z),(.7,.06,.7));B.box('chy-black-paint',(x,.62,z),(.06,.76,.06))
  chair(x-.7,z,.24,-math.pi/2);chair(x+.7,z,.24,math.pi/2)
 # Potted agave uses broad tapered leaves rather than spherical proxy foliage.
 for x,z,y in [(128.8,-181,deck),(120.8,-184.9,deck),(120.5,-173.7,.24)]:
  B.lathe('chy-timber-paint',(x,z),[(y,.28),(y+.55,.35)],16)
  for j in range(11):
   a=j*2.4;r=.48;tip=(x+r*math.cos(a),y+1.2+(j%3)*.13,z+r*math.sin(a))
   B.face('chy-leaf',[(x-.06*math.sin(a),y+.48,z+.06*math.cos(a)),(x+.06*math.sin(a),y+.48,z-.06*math.cos(a)),tip])
 # Collision-only guards never render as opaque panels.
 for k in list(B.groups):
  if B.groups[k]['material']=='chy-collision':del B.groups[k]
 samples=[]
 for x in np.arange(p.bounds[0],p.bounds[2],.75):
  for z in np.arange(p.bounds[1],p.bounds[3],.75):
   if p.buffer(-.25).contains(Point(x,z)):samples.append([float(x),deck+.35,float(z)])
 routes=[[[121.2,deck,-184.8],[121.2,deck,-177.1]],[[124.7,deck,-185],[124.7,deck,-176.3]],[[121,.24,-172.3],[124,.24,-172.3]],[[123,.24,-172.2],[123,.24,-174.8]]]
 Path('build/city-exteriors/chayo-terraces-samples.json').write_text(json.dumps(samples));Path('build/city-exteriors/chayo-terraces-stairs.json').write_text(json.dumps(routes))
 return dict(key=KEY,name='Chayo terrace exterior',center=[124,0,-181],bounds=list(p.buffer(3).bounds),structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
