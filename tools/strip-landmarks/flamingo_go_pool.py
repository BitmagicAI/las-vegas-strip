"""Original GO Pool reconstruction, 2025 photos and current seating-plan reference.
Plan positions/levels are inferred; preserve all adjacent garden and hotel assets.
"""
from common import *
KEY='flamingoGoPool';Y=1.2;VIP=1.8

def plans():
 # World fit of observed arrangement; no third-party geometry or textures.
 main=Polygon([(273,-87),(281,-89),(291,-88),(299,-83),(305,-75),(307,-65),(303,-56),(297,-51),(288,-48),(280,-49),(273,-53),(270,-60),(269,-68),(272,-75)]).buffer(1.1).buffer(-1.1)
 north=LineString([(280,-97),(285,-99),(293,-99),(299,-97),(304,-94)]).buffer(3.2,resolution=12)
 east=rotate(box(314,-51,332.288,-44.5),25,origin=(323.144,-47.75))
 west=Point(257,-38).buffer(6.096,resolution=32)
 grotto=box(264,-74,270,-58.76)
 return main,north,east,west,grotto

def exterior(B):
 B.property=KEY+'-exterior';B.detail=0;B.source='go-pool/deck'
 main,north,east,west,grotto=plans();water=unary_union([main,north,east,west,grotto])
 # Stay east of the preserved casino/garden boundary and west of HGV structures.
 ground=Polygon([(247,-111),(309,-111),(314,-85),(336,-65),(341,-39),(326,-24),(299,-22),(278,-19),(246,-23)])
 raised=unary_union([north.buffer(4),east.buffer(4),west.buffer(4)]).intersection(ground)
 entrycut=box(277.9,-25,282.1,-16.9)
 deck=ground.difference(water.buffer(.4)).difference(raised).difference(entrycut)
 B.planar('fgp-paving',deck,Y,True);B.shell(ground.difference(entrycut),.08,Y,'fgp-stone',roof=False)
 rampcuts=unary_union([box(281.9,-93.1,286.1,-88.8),box(305.9,-42.1,313.1,-37.9),box(262.9,-35.1,267.1,-30.9)])
 B.planar('fgp-paving',raised.difference(water.buffer(.4)).difference(rampcuts),VIP,True);B.shell(raised.difference(rampcuts),Y,VIP,'fgp-stone',roof=False)
 for i,p in enumerate([main,north,east,west,grotto]):
  top=VIP if i in [1,2,3] else Y
  B.source='go-pool/basin-'+str(i)
  B.planar('fgp-tile',p,top-.85,True)
  B.planar('fgp_pool',p,top-.18)
  B.shell(p,top-.85,top,'fgp-tile',roof=False,solid=True)
  B.planar('fgp-coping',p.buffer(.4).difference(p),top+.025,True)
  # Broad submerged ledge around the edge gives a physical way back to deck.
  B.planar('fgp-tile',p.difference(p.buffer(-1.15)),top-.28,True)
  B.shell(p.buffer(-1.15),top-.85,top-.28,'fgp-tile',roof=False,solid=True)
 # Entry and VIP connections are explicit inferred ramps; no closed pretend doors.
 ramps=[([(278,Y,-25),(282,Y,-25),(282,.08,-17),(278,.08,-17)],'south-entry'),
        ([(282,Y,-88.9),(286,Y,-88.9),(286,VIP,-93),(282,VIP,-93)],'north-vip'),
        ([(306,Y,-42),(306,Y,-38),(313,VIP,-38),(313,VIP,-42)],'east-vip'),
        ([(267,Y,-35),(267,Y,-31),(263,VIP,-31),(263,VIP,-35)],'west-vip')]
 for vertices,name in ramps:
  B.source='go-pool/ramp-'+name;B.upface('fgp-paving',vertices,True)
 # Grotto canopy and DJ platform above its15.24m frontage; column openings face pool.
 B.source='go-pool/grotto'
 B.box('fgp-pink',(267,4.35,-66.38),(7.4,.4,16.4),True)
 for z in [-74.3,-58.5]:B.box('fgp-pink',(264.5,2.6,z),(.5,2.8,.5),True)
 B.box('fgp-pink',(263.6,2.6,-66.38),(.35,2.8,16),True)
 # Static narrow translucent-looking ribbons approximate the rain curtain; no new runtime effect.
 for z in np.arange(-73.9,-59,.28):B.box('fgp-waterfall',(270.12,2.7,z),(.025,3,.035))
 B.box('fgp-pink',(266,4.9,-66.38),(1.1,.7,4.8),True)
 for z in [-73.3,-59.4]:B.box('fgp-speaker',(267,5.4,z),(.6,1.6,.6))
 B.box('fgp-canopy',(265.8,6.5,-66.38),(3.2,.16,6.6))
 for z in [-69.3,-63.4]:B.box('fgp-metal',(264.6,5.5,z),(.1,2,.1))
 # Covered swim-up bar, open public water side, with original stepped circular crown.
 B.source='go-pool/swim-up-bar';cx,cz=278.5,-79.5
 for yy,r in [(4.4,5.8),(4.65,5.2),(5,4.2),(5.4,3.2),(5.8,2.1)]:
  B.lathe('fgp-pink',(cx,cz),[(yy,r),(yy+.22,r)],48)
  B.planar('fgp-pink',Point(cx,cz).buffer(r,resolution=12),yy+.22)
 for a in [0,math.pi/2,math.pi,math.pi*1.5]:
  x,z=cx+4.3*math.cos(a),cz+4.3*math.sin(a);B.lathe('fgp-pink',(x,z),[(Y-.5,.24),(4.4,.24)],16);B.box('fgp-pink',(x,2.6,z),(.42,3,.42),True)
 B.lathe('fgp-bar',(cx,cz),[(Y-.65,2),(Y+.6,2)],32)
 B.planar('fgp-coping',Point(cx,cz).buffer(2.2,resolution=16),Y+.65)
 for a in np.linspace(0,math.tau,18,endpoint=False):
  x,z=cx+3*math.cos(a),cz+3*math.sin(a);B.lathe('fgp-metal',(x,z),[(Y-.8,.06),(Y-.15,.06)],8);B.lathe('fgp-seat',(x,z),[(Y-.15,.26),(Y-.03,.26)],12)
 # Cabanas and umbrellas remain open, with collision only on posts/furniture bases.
 def cabana(x,z,yaw=0,base=VIP):
  F=Frame(B,x,z,yaw,base)
  for xx in [-1.8,1.8]:
   for zz in [-1.5,1.5]:F.box('fgp-metal',(xx,1.4,zz),(.09,2.8,.09),True)
  for a,b in [((-2,-1.7),(2,-1.7)),((2,-1.7),(2,1.7)),((2,1.7),(-2,1.7)),((-2,1.7),(-2,-1.7))]:B.face('fgp-canopy',[F.p(a[0],2.8,a[1]),F.p(b[0],2.8,b[1]),F.p(0,3.8,0)])
  F.box('fgp-seat',(0,.42,.8),(3,.55,1.0),True);F.box('fgp-seat',(0,.9,1.22),(3,.7,.16))
  for xx in [-1.7,1.7]:F.box('fgp-canopy',(xx,1.4,1.1),(.16,2.7,.6))
 for x,z,yaw in [(277,-104,0),(283,-106,0),(290,-107,0),(297,-105,0),(304,-102,-.3),(314,-56,.4),(320,-60,.4),(327,-58,.4),(334,-52,.6),(337,-44,1),(333,-35,2),(250,-30,0),(257,-28,0),(263,-29,0),(248,-44,1.5)]:cabana(x,z,yaw)
 def umbrella(x,z,base=Y):
  B.lathe('fgp-metal',(x,z),[(base,.06),(base+2.6,.06)],8)
  for j in range(12):
   a=j*math.tau/12;b=(j+1)*math.tau/12
   B.face('fgp-canopy'if j%2 else'fgp-yellow',[(x,base+3.1,z),(x+2*math.cos(a),base+2.55,z+2*math.sin(a)),(x+2*math.cos(b),base+2.55,z+2*math.sin(b))])
 def lounger(x,z,yaw=0,base=Y):
  F=Frame(B,x,z,yaw,base);F.box('fgp-seat',(0,.32,0),(.75,.16,1.9));F.box('fgp-metal',(0,.15,0),(.55,.3,1.5),True)
  B.face('fgp-seat',[F.p(-.375,.4,.45),F.p(.375,.4,.45),F.p(.375,.9,.95),F.p(-.375,.9,.95)])
 B.source='go-pool/furniture'
 for x,z in [(277,-44),(284,-42),(291,-43),(299,-45),(311,-61),(313,-69),(311,-79),(309,-86),(272,-91)]:
  umbrella(x,z)
  for dx in [-1,1]:lounger(x+dx,z+1)
 # Original palm meshes fitted to open soil islands, with no imported imagery.
 B.source='go-pool/planting'
 palmpts=[(249,-102),(253,-95),(255,-86),(251,-76),(252,-53),(247,-48),(247,-27),(266,-25),(272,-24),(292,-24),(303,-27),(329,-27),(338,-32),(340,-55),(333,-65),(320,-76),(312,-97),(310,-108),(295,-110),(280,-109),(265,-107),(258,-101)]
 for i,(x,z) in enumerate(palmpts):
  h=8+(i%5)*1.4;B.lathe('fgp-bark',(x,z),[(Y,.22),(Y+h,.12)],10);B.box('fgp-bark',(x,Y+h/2,z),(.3,h,.3),True)
  for j in range(11):
   a=j*math.tau/11+i*.7;pts=[]
   for k in range(7):
    t=k/6;r=3.5*t;yy=Y+h+1.2*math.sin(t*math.pi)-1.5*t;w=.38*math.sin(t*math.pi)
    pts.append([(x+r*math.cos(a)-w*math.sin(a),yy,z+r*math.sin(a)+w*math.cos(a)),(x+r*math.cos(a)+w*math.sin(a),yy,z+r*math.sin(a)-w*math.cos(a))])
   for k,(aa,bb) in enumerate(zip(pts,pts[1:])):
    if k==0:B.face('fgp-leaf',[aa[0],bb[1],bb[0]])
    elif k==5:B.face('fgp-leaf',[aa[0],aa[1],bb[0]])
    else:B.face('fgp-leaf',[aa[0],aa[1],bb[1],bb[0]])
 routes=[{'name':'south-entry','points':[[280,.08,-17],[280,Y,-25],[280,Y,-32]]},{'name':'east-main-promenade','points':[[305.2,Y,-34],[305.2,Y,-57]]},{'name':'west-garden-edge','points':[[249,Y,-52],[249,Y,-68]]}]
 meta=dict(key=KEY,name='Flamingo GO Pool public exterior',center=[289,0,-65],bounds=[246,-112,342,-14],building='flamingo',structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=routes,hotelSources=[],views={})
 Path('build/city-exteriors/flamingo-go-pool-routes.json').write_text(json.dumps(routes,indent=2));return meta
if __name__=='__main__':
 B=Meshes();meta=exterior(B)
 # GEOS may emit collinear ring triangles; omit only zero-area visual faces.
 for g in B.groups.values():
  g['faces']=[f for f in g['faces'] if np.linalg.norm(np.cross(np.array(g['vertices'][f[1]])-g['vertices'][f[0]],np.array(g['vertices'][f[2]])-g['vertices'][f[0]]))>1e-8]
 B.save_all();(OUT/(KEY+'-venue.pending.json')).write_text(json.dumps(meta));print(sum(len(g['faces'])for g in B.groups.values()),'triangles')
