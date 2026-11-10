"""Original TI court from linked official photographs and approximate aerial registration.
No guest-interior edits, terrain replacement, lights or geographic-city regeneration.
"""
from common import *
BASE=Path('.bitmagic/city-exterior-backups/ti-pool-court')
y=.24

def chair(B,x,z,yaw=0):
 F=Frame(B,x,z,yaw,y=y)
 F.box('walnut',(0,.32,0),(.75,.10,1.9),True)
 for xx in [-.30,.30]:
  for zz in [-.72,.72]:F.box('walnut',(xx,.15,zz),(.06,.30,.06),True)
 F.box('sandstone',(0,.43,.3),(.70,.15,1.25))
 B.face('sandstone',[F.p(-.35,.5,-.32),F.p(.35,.5,-.32),F.p(.35,1,-.88),F.p(-.35,1,-.88)])

def palm(B,x,z,h,phase):
 # Original folded leaf geometry; no external/source foliage asset is copied.
 B.source='ti-pool-palms';B.detail=0
 B.path('bark',[(x,y,z),(x+.35,y+h*.5,z),(x+.9,y+h,z+.35)],.24,10)
 B.box('bark',(x,y+1,z),(.38,2,.38),True)
 B.detail=1
 for j in range(18):
  a=phase+j*2.39996;length=2.8+(j%4)*.25
  def p(t,offset=0):return (x+.9+length*t*math.cos(a)-offset*math.sin(a),y+h+1.1*math.sin(math.pi*t)-1.1*t,z+.35+length*t*math.sin(a)+offset*math.cos(a))
  B.path('sage',[p(k/8) for k in range(9)],.025,4)
  for k in range(1,17):
   t=k/18;w=.55*math.sin(math.pi*t)
   for sign in [-1,1]:
    a0=p(t);a1=p(t+.03,sign*w*.45);a2=p(min(1,t+.16),sign*w)
    B.face('foliage',[a0,(a1[0],a1[1]+.06,a1[2]),a2]);B.face('sage',[a0,a2,p(t+.06,sign*w*.3)])
 B.detail=0

def build():
 old=json.loads((BASE/'ti-exterior.json').read_text());c=json.loads((BASE/'ti-exterior-collision.json').read_text())
 B=Meshes();B.property='ti-exterior';B.source='ti-pool-court';B.detail=0
 raw=Polygon([(10,-929),(115,-929),(97,-912),(96,-906),(108,-895),(111,-885),(95,-873),(10,-873)])
 deck=raw.difference(footprint('way/33959894').buffer(.45)).difference(footprint('way/27727145').buffer(.45))
 # Aerial lobe centers fitted at roughly .241m/pixel; deliberately recorded estimates.
 pool=unary_union([Point(58,-904).buffer(7,quad_segs=12),Point(62,-910).buffer(4.8,quad_segs=12),Point(68,-906).buffer(5.5,quad_segs=12),Point(53,-895).buffer(7.0,quad_segs=12),Point(66,-894).buffer(4.5,quad_segs=12)])
 pool=pool.buffer(1.4).buffer(-1.4).difference(Point(65,-900).buffer(3.0)).difference(Point(49,-903).buffer(2.7))
 hot=Point(41,-909).buffer(2.3,quad_segs=20);wet=unary_union([pool,hot]);assert deck.buffer(-1).covers(wet)
 B.shell(deck,y-.20,y,'tile',roof=False);B.planar('tile',deck.difference(wet.buffer(.35)),y,True)
 for p in [pool,hot]:
  B.planar('blue',p,y-.9,True);B.shell(p,y-.9,y-.12,'blue',roof=False)
  B.planar('water',p.buffer(-.025),y-.12);B.planar('stone',p.buffer(.35).difference(p),y+.025,True)
 for x,z in [(58,-916),(48,-891),(69,-893),(39,-909)]:
  for dx in [-.32,.32]:B.path('silver',[(x+dx,y-.8,z),(x+dx,y+.6,z),(x+dx,y+.7,z+.4),(x+dx,y,z+1)],.035,8)
 # Perimeter shade cabanas match the blue hipped silhouettes in official photos.
 B.source='ti-pool-cabanas'
 for x in [25,33,41,49,57,65,73,81,89]:
  z=-876
  for dx in [-1.7,1.7]:
   for dz in [-1.4,1.4]:B.box('white',(x+dx,y+1.3,z+dz),(.10,2.6,.10),True)
  for a,b in [((-1.9,-1.6),(1.9,-1.6)),((1.9,-1.6),(1.9,1.6)),((1.9,1.6),(-1.9,1.6)),((-1.9,1.6),(-1.9,-1.6))]:B.face('blue',[(x+a[0],y+2.6,z+a[1]),(x+b[0],y+2.6,z+b[1]),(x,y+3.5,z)])
  B.box('ivory',(x,y+1.25,z+1.4),(3.4,2.5,.04),True);B.box('walnut',(x,y+.3,z), (2.4,.6,1.5),True);B.box('sandstone',(x,y+.67,z),(2.35,.14,1.45))
 B.source='ti-pool-loungers';B.detail=1
 for z in [-914,-910,-906,-902,-898,-894]:
  for x in [25,29,33]:chair(B,x,z,math.pi/2)
 for z in [-913,-909,-905,-901,-897,-893]:
  for x in [80,84,88]:chair(B,x,z,-math.pi/2)
 for x,z in [(39,-893),(39,-898),(74,-919),(80,-919)]:
  B.lathe('walnut',(x,z),[(y,.8),(y+.4,1.1),(y+.5,1.05)],20)
  B.lathe('blue',(x,z),[(y+.5,1.02),(y+.62,1.02),(y+.62,.01)],20)
  B.box('walnut',(x,y+.25,z),(1.3,.5,1.3),True)
 for i,(x,z) in enumerate([(14,-918),(14,-909),(14,-895),(15,-878),(24,-882),(35,-882),(48,-883),(62,-883),(75,-883),(88,-883),(92,-917),(92,-907),(94,-891),(48,-903),(65,-900),(44,-920),(59,-920)]):
  # Low original planting beds; exact species/positions are inferred.
  if not deck.buffer(-.6).covers(Point(x,z).buffer(1.15)) or wet.buffer(.4).intersects(Point(x,z).buffer(1.15)):continue
  B.source='ti-pool-planting';B.planar('bark',Point(x,z).buffer(1.15,quad_segs=12),y+.035)
  palm(B,x,z,9.5+(i%5)*1.0,i*.7)
 B.detail=0
 nc=B.solids[B.property];offset=len(c['vertices'])//3;c['vertices']+=nc['vertices'];c['indices'] += [i+offset for i in nc['indices']]
 adds=list(B.groups.values());(OUT/'ti-exterior.json').write_text(json.dumps({'meshes':old['meshes']+adds,'labels':old['labels']},separators=(',',':')));(OUT/'ti-exterior-collision.json').write_text(json.dumps(c,separators=(',',':')))
 meta={'deckY':y,'poolBounds':list(pool.bounds),'deckBounds':list(deck.bounds),'addedTriangles':sum(len(m['faces']) for m in adds),'routes':[{'name':'Pool court perimeter','points':[[18,y,-923],[91,y,-923],[91,y,-880],[18,y,-880],[18,y,-923]]}],'remaining':['Ground terrain beneath basins retained; no swimming/deep-water physics claim','Courtyard dimensions and elevations inferred; continuous hotel access unverified']};(OUT/'ti-deck-metadata.json').write_text(json.dumps(meta,indent=2)+'\n');print(meta)
if __name__=='__main__':build()
