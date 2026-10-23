"""Footprint-owned public arrivals and continuous connections to resident cores."""
from common import *
from shapely.ops import transform
from heapq import heappush,heappop
# Share authoring helpers without executing the landmark build.
exec(Path('tools/strip-landmarks/build.py').read_text().split('# LINQ:')[0])
configs=[('park','park-mgm','Park MGM','way/115080290',(-32,1230),42,88,10),('palazzo','palazzo','The Palazzo','way/180584269',(300,-920),38,65,12),('ti','treasure-island','Treasure Island','way/33959894',(250,-980),34,42,8),('harrahs','harrahs','Harrah’s Las Vegas','way/128622185',(53,-385),34,65,7.6)]
plans=json.load(open('build/highrises/plan.json'));result=[]
for key,building,name,ident,near,w,d,h in configs:
 p=footprint(ident)
 plan=next(v for v in plans if v['key']==building)
 towershape=unary_union([footprint(f['id']) for f in plan['features']])
 candidates=[]
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  L=math.dist(a,b)
  if L<w+2:continue
  for dist in np.linspace(w/2+1,L-w/2-1,max(2,int(L/10))):
   q=LineString([a,b]).interpolate(dist);nx,nz=-(b[1]-a[1])/L,(b[0]-a[0])/L
   if not p.contains(Point(q.x+nx*.1,q.y+nz*.1)):nx,nz=-nx,-nz
   J=Frame(B,q.x,q.y,math.atan2(nx,nz))
   for dep in np.arange(d,23,-2):
    ar=J.poly([(-w/2,.3),(w/2,.3),(w/2,dep),(-w/2,dep)])
    if p.buffer(.4).covers(ar) and ar.intersection(towershape.buffer(.7)).area<.01:
     candidates.append((q.distance(Point(*near))+.5*(d-dep),J,ar,float(dep)));break
 if not candidates:raise Exception('No arrival fit '+key)
 _,F,atr,d=min(candidates,key=lambda v:v[0])
 connections=[];masks=[]
 for t in plan['towers']:
  a,b,c,dd=t['linear'];ox,oy,oz=t['origin'];old=t.get('publicAccessFront',t['lobbyFront']);front=-5.25-6*t['bays']
  def W(x,z):return (ox+a*x+b*z,oz+c*x+dd*z)
  side=1 if key in ['park','ti'] else -1;at=front+30
  target=W(side*12,at);end=W(side*9.4,at)
  access=Polygon([W(x,z) for x,z in [(side*9.1,at-2.5),(side*25,at-2.5),(side*25,at+2.5),(side*9.1,at+2.5)]])
  free=p.buffer(-2.8).difference(towershape.buffer(2.8)).union(access.buffer(-.35)).union(atr.buffer(-1)).buffer(.02)
  # Visibility graph through the interior free-space polygon, with 4.2 m-wide galleries.
  source=F.p(0,0,d-3);source=(source[0],source[2]);nodes=[source,target]
  for pp in parts(free.simplify(.25)):
   for ring in [pp.exterior,*pp.interiors]:nodes+=list(ring.coords)[:-1]
  graph=[[] for _ in nodes];test=free.buffer(.35)
  for i in range(len(nodes)):
   for j in range(i):
    line=LineString([nodes[i],nodes[j]])
    if test.covers(line):graph[i].append((j,line.length));graph[j].append((i,line.length))
  heap=[(0,0)];dist={0:0};prev={}
  while heap:
   score,i=heappop(heap)
   if i==1:break
   if score>dist[i]:continue
   for j,L in graph[i]:
    v=score+L
    if v<dist.get(j,1e20):dist[j]=v;prev[j]=i;heappush(heap,(v,j))
  if 1 not in dist:raise Exception('No guest connection '+t['id'])
  route=[1];i=1
  while i: i=prev[i];route.append(i)
  path=[nodes[i] for i in reversed(route)]+[end];connections.append(dict(tower=t['id'],points=path,length=dist[1],side=side,at=at,yaw=math.atan2(-side*a,-side*c),width=4.4))
  masks.append(access)
  t['publicArrival']=key;t['publicConnection']={'side':side,'at':at,'width':4.4}
 result.append(dict(key=key,building=building,name=name,source=ident,width=w,depth=d,height=h,frame=[F.x,F.z,F.yaw],connections=connections))
 print(key,'atrium',w,d,'connections',[(v['tower'],round(v['length'])) for v in connections])
Path('build/strip-landmarks/next-plan.json').write_text(json.dumps(result,indent=2))
Path('build/highrises/plan.json').write_text(json.dumps(plans,indent=2));Path('src/work/hotels/highrise-towers.json').write_text(json.dumps([t for p in plans for t in p['towers']],indent=2))
