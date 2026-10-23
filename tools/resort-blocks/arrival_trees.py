"""Reusable deterministic broadleaf tree; authored LODs batched by 40m grove cell."""
from common import *
def tree(b,x,z,y,seed=1):
 rng=random.Random(seed);cell=f'{math.floor(x/40)},{math.floor(z/40)}'
 phase=rng.random()*math.tau;clusters=[]
 for i in range(22):
  a=phase+i*2.399;r=math.sqrt((i+.5)/22)*2.25
  clusters.append((x+math.cos(a)*r,y+4.8+rng.uniform(-.45,1.05),z+math.sin(a)*r,rng.uniform(.7,1.05)))
 for lod in range(3):
  b.source=f'arrival-tree/{cell}/{lod}';b.detail=0
  if lod==0:
   b.tube('bark',(x,y,z),(x+.14,y+3.9,z),.28,9,.14)
   for i,(cx,cy,cz,r) in enumerate(clusters):
    start=(x+.1,y+2.5+(i%4)*.3,z);end=(cx,cy-.35,cz)
    b.tube('bark',start,end,.085,6,.018)
    # Branchlets and uneven leaf sprays preserve gaps and a soft silhouette.
    for j in range(9):
     a=rng.random()*math.tau;rr=math.sqrt(rng.random())*r
     p=(cx+math.cos(a)*rr,cy+rng.uniform(-.4,.4),cz+math.sin(a)*rr)
     b.sphere(['tree-shadow','tree-leaf','tree-tip'][j%3],p,.38+rng.random()*.2,6,4,scale=(1,.7,1))
  elif lod==1:
   b.tube('bark',(x,y,z),(x,y+4,z),.26,6,.10)
   for i,(cx,cy,cz,r) in enumerate(clusters[::2]):b.sphere(['tree-shadow','tree-leaf','tree-tip'][i%3],(cx,cy,cz),r,7,4,scale=(1,.8,1))
  else:
   b.tube('bark',(x,y,z),(x,y+4,z),.24,4,.12)
   for i in range(3):
    a=phase+i*math.tau/3;b.sphere('tree-leaf',(x+math.cos(a),y+5,z+math.sin(a)),1.9,6,3,scale=(1,.72,1))
 return dict(position=[x,y,z],crownRadius=4.0,cell=cell,seed=seed)
