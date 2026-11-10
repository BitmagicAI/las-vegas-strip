"""Original pool courts fitted to observed aerial anchors; dimensions remain estimates."""
from common import *
import panorama_exterior as P
import martin_exterior as M
Y=.31
OUTREC=Path('docs/project-records/panorama-martin-amenities')
def build(B):
 refs=json.loads((OUTREC/'research.json').read_text())['courts'];routes=[];trees=[];stats={}
 for r in refs:
  name=r['name'];martin=name=='martin';key='martinAmenities' if martin else 'panoramaAmenities';B.property=key+'-exterior';B.source=name+'-amenities';B.detail=0
  ids=[M.TOWER]+M.LOW if martin else P.TOWERS+P.GARAGES+P.LOW
  occupied=unary_union([footprint(i) for i in ids]);pool=Polygon(r['pool']);deck=Polygon(r['deck']).buffer(2 if martin else .8,join_style=2).difference(occupied.buffer(.3));x,z=r['anchorWorld']
  # Preserve the existing streamed lobby planter and its approach clearance.
  # The aerial-fitted east tip approached that retained furnishing too closely in the reverse walk.
  if martin:pool=pool.intersection(box(-2000,-2000,-870,2000))
  # Separate spa follows observed aerial placement; exact raised platform elevation deferred.
  sx,sz=(x-8.3,z+6) if martin else (x+9.5,z-18.8) if name.endswith('north') else (x+8,z+17.5)
  spa=box(sx-2,sz-1.7,sx+2,sz+1.7);water=pool.union(spa)
  assert water.intersection(occupied).area<.01
  deck=deck.union(water.buffer(2,join_style=2)).difference(occupied.buffer(.3))
  ring=list(pool.buffer(1.1,join_style=2).exterior.coords);route=LineString(ring)
  assert deck.buffer(.01).covers(route.buffer(.42)),name
  routes.append(dict(name=name+'-pool-circuit',points=[[xx,Y,zz] for xx,zz in ring]))
  furnishing=deck.difference(water.buffer(.7)).difference(route.buffer(.8))
  B.planar('pma-paving',deck.difference(water),Y,True);B.planar('pma_pool',water,.23);B.planar('pma-tile',water,.01,True);B.shell(water,.01,Y,'pma-tile',roof=False,solid=True);B.planar('pma-coping',water.buffer(.32).difference(water),Y+.025,True)
  for xx in np.arange(deck.bounds[0],deck.bounds[2],2):B.planar('pma-joint',box(xx-.012,deck.bounds[1],xx+.012,deck.bounds[3]).intersection(deck.difference(water)),Y+.003)
  for zz in np.arange(deck.bounds[1],deck.bounds[3],2):B.planar('pma-joint',box(deck.bounds[0],zz-.012,deck.bounds[2],zz+.012).intersection(deck.difference(water)),Y+.003)
  count=dict(loungers=0,palms=0,cabanas=0,trees=0)
  def chair(xx,zz,yaw=0):
   F=Frame(B,xx,zz,yaw,y=Y);F.box('pma-cream',(0,.46,0),(.7,.13,1.8));F.box('pma-dark',(0,.23,0),(.55,.46,1.5),True);B.face('pma-cream',[F.p(-.35,.53,-.3),F.p(.35,.53,-.3),F.p(.35,.95,-.9),F.p(-.35,.95,-.9)]);count['loungers']+=1
  # Furniture only occupies space outside the measured circulation loop.
  for xx in np.arange(deck.bounds[0]+1,deck.bounds[2]-1,2.6):
   for zz in np.arange(deck.bounds[1]+1,deck.bounds[3]-1,3.4):
    if furnishing.contains(box(xx-.55,zz-1.1,xx+.55,zz+1.1)) and Point(xx,zz).distance(pool)<5:chair(xx,zz)
  if martin:
   # Dark square pergolas with cream daybeds from the official pool photograph.
   for xx in np.arange(pool.bounds[0]+3,pool.bounds[2]-2,5.3):
    cut=pool.intersection(LineString([(xx,pool.bounds[1]-10),(xx,pool.bounds[3]+10)]))
    zz=cut.bounds[1]-3.9
    if not deck.contains(box(xx-1.8,zz-1.3,xx+1.8,zz+1.3)) or box(xx-1.8,zz-1.3,xx+1.8,zz+1.3).intersects(route.buffer(.6)):continue
    for dx in [-1.6,1.6]:
     for dz in [-1.1,1.1]:B.box('pma-dark',(xx+dx,Y+1.35,zz+dz),(.14,2.7,.14),True)
    B.box('pma-dark',(xx,Y+2.75,zz),(3.5,.18,2.5));B.box('pma-cream',(xx,Y+.45,zz),(2.8,.2,1.9),True);count['cabanas']+=1
   for i,xx in enumerate(np.arange(pool.bounds[0]+1,pool.bounds[2],5)):
    zz=deck.bounds[1]+.8
    if occupied.distance(Point(xx,zz))>1 and route.distance(Point(xx,zz))>1:
     trees.append([xx,zz,4.8+(i%2)*.6]);B.box('pma-bark',(xx,Y+2,zz),(.25,4,.25),True);count['trees']+=1
  else:
   # Palm rows on west and end margins, with modest original leaf geometry.
   for j,dist in enumerate(np.arange(1,deck.exterior.length,6)):
    q=deck.exterior.interpolate(dist);xx,zz=q.x,q.y
    if xx>x+3 or route.distance(q)<1.6 or occupied.distance(q)<1:continue
    h=5.8+j%3;B.lathe('pma-bark',(xx,zz),[(Y,.24),(Y+h,.12)],10);B.box('pma-bark',(xx,Y+h/2,zz),(.3,h,.3),True)
    for a in np.arange(0,math.tau,math.tau/10):
     ps=[]
     for k in range(7):
      t=k/6;rr=2.5*t;yy=Y+h+math.sin(t*math.pi)-t;w=.32*math.sin(t*math.pi);ps.append([(xx+rr*math.cos(a)-w*math.sin(a),yy,zz+rr*math.sin(a)+w*math.cos(a)),(xx+rr*math.cos(a)+w*math.sin(a),yy,zz+rr*math.sin(a)-w*math.cos(a))])
     for k,(a,b) in enumerate(zip(ps,ps[1:])):B.face('pma-leaf',[a[0],b[1],b[0]] if k==0 else [a[0],a[1],b[0]] if k==5 else [a[0],a[1],b[1],b[0]])
    count['palms']+=1
  # Basin access handrails, outside the circulation centreline.
  q=list(pool.exterior.coords)[0];B.path('pma-metal',[(q[0],.01,q[1]),(q[0],1.2,q[1]),(q[0]+.7,1.2,q[1]),(q[0]+.7,Y,q[1])],.035,8)
  stats[name]=dict(**count,poolAreaEstimateM2=pool.area,deckAreaEstimateM2=deck.area)
 (OUTREC/'routes.json').write_text(json.dumps(routes,indent=2)+'\n');Path('build/city-exteriors/panorama-martin-trees.json').write_text(json.dumps(trees));return stats
if __name__=='__main__':
 B=Meshes();stats=build(B);B.save_all();stats['triangles']=sum(len(g['faces']) for g in B.groups.values());(OUTREC/'geometry.json').write_text(json.dumps(stats,indent=2)+'\n');print(stats)
