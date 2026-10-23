"""Folded Boulevard curtain wall, fitted to Earth2022-11-09.
Keep existing public floor/collision/portal ownership. Recessed glazing lies behind
that facade's collision envelope. Width and depth are photographic estimates.
"""
from common import *
from forum_shops import facade_frame
SOURCE='boulevard-folded-facade'
from cosmo_palette import COLORS
A=(-37.221,736.757);C=(-36.420,625.838)
# Door and bridge openings in the existing elevation system.
OPENINGS=[(703,.24,9.6,4.65),(639,.24,7.6,4.65),(719,5.84,8.6,4.65)]
def build(b):
 b.property='cosmo-exterior';b.source=SOURCE;b.detail=0
 F,L,nx,nz=facade_frame(b,A,C,footprint('way/1212809711'),.02)
 # facade_frame follows north-to-south here; local x grows towards the bridge.
 holes=unary_union([box(z-C[1]-w/2,y-.02,z-C[1]+w/2,y+h) for z,y,w,h in OPENINGS])
 def patch(mat,u0,u1,y0,y1,depth0,depth1):
  if y1<=y0:return
  region=box(u0,y0,u1,y1).difference(holes)
  for poly in parts(region):
   for tri in triangles(poly):
    b.face(mat,[F.p(u,y,depth0+(depth1-depth0)*(u-u0)/(u1-u0)) for u,y in list(tri.exterior.coords)[:-1]])
 #24bays preserve the characteristic stepped crown; south end glazing curves
 # in shallow vertical scallops rather than a flat mirrored rectangular grid.
 count=24;pitch=L/count
 for i in range(count):
  lo=i*pitch;hi=(i+1)*pitch
  top=[8.9,9.6,10.3,11.0,11.7,12.4,13.1,13.8,14.5,15.2,15.9,16.6,16.6,16.6,16.6,16.6,15.9,15.2,14.5,13.8,13.1,12.4,11.7,11.0][23-i]
  patch('cm-spandrel',lo,hi,top,17.04,.02,.02)
  for seg in range(6):
   u0=lo+pitch*seg/6;u1=lo+pitch*(seg+1)/6
   #Positive local depth is inside the retained mapped enclosure.
   dep0=.06+.65*math.sin(math.pi*seg/6);dep1=.06+.65*math.sin(math.pi*(seg+1)/6)
   patch('cm-glass-light' if i>15 and seg in [1,2] else 'cm-glass',u0,u1,.24,top,dep0,dep1)
   for y in np.arange(2.5,top-.1,2.65):patch('cm-frame',u0,u1,y,y+.11,dep0-.035,dep1-.035)
   patch('cm-frame',u0,u1,top-.10,top,dep0-.04,dep1-.04)
  for u in [lo,hi]:patch('cm-frame',max(0,u-.065),min(L,u+.065),.24,top+.06,-.04,-.04)
 # Continuous upper coping and modest shadow gap keep the pool slab legible.
 patch('cm-reveal',0,L,16.97,17.10,-.05,-.05)
 patch('cm-frame',0,L,17.10,17.22,-.075,-.075)

def replace_front(meshes):
 """Delete the replaced front triangles only; no coplanar blanket offset."""
 removed=0;out=[]
 for m in meshes:
  if m['source']==SOURCE:continue
  target=(m['source']=='podium' and m['material']=='cosmo-mirror') or m['source'] in ['podium-mirror-grid','podium-columns']
  if target:
   keep=[]
   for f in m['faces']:
    pts=[m['vertices'][i] for i in f]
    front=all(p[0]>-38.05 and 625.4<p[2]<737.1 and p[1]<17.25 for p in pts)
    if front:removed+=1
    else:keep.append(f)
   m={**m,'faces':keep}
  if m['faces']:out.append(m)
 return out,removed

def update_builder(b):
 existing,removed=replace_front(list(b.groups.values()))
 b.groups={(m['property'],m['source'],m['material'],m['detail']):m for m in existing}
 build(b)
 for key in ['cosmoL4','cosmoL14']:
  old=key+'-interior';new=key+'-exterior'
  for k,m in list(b.groups.items()):
   if m['property']!=old:continue
   del b.groups[k];m['property']=new;b.groups[(new,m['source'],m['material'],m['detail'])]=m
  for label in b.labels:
   if label['property']==old:label['property']=new
  c=b.solids[old];dst=b.solids[new];offset=len(dst['vertices'])//3
  dst['vertices'].extend(c['vertices']);dst['indices'].extend(offset+i for i in c['indices']);b.solids[old]={'vertices':[],'indices':[]}
  b.property=old;b.source='interior-anchor';b.detail=0;b.box('charcoal',(-300,-2,710),(.01,.01,.01))
 return removed
