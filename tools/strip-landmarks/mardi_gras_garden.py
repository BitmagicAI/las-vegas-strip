"""Original courtyard garden fitted to overhead and oblique references, not surveyed planting."""
from common import *

def leaves(B,c,radii,count,seed,mat):
 rng=random.Random(seed)
 for _ in range(count):
  a=rng.random()*math.tau;v=rng.uniform(-1,1);r=rng.random()**(1/3);s=math.sqrt(1-v*v)
  x,y,z=(c[0]+radii[0]*r*s*math.cos(a),c[1]+radii[1]*r*v,c[2]+radii[2]*r*s*math.sin(a))
  angle=rng.random()*math.tau;l=rng.uniform(.07,.15);w=l*.4
  dx,dz=l*math.cos(angle),l*math.sin(angle);wx,wz=-w*math.sin(angle),w*math.cos(angle)
  B.face(mat,[(x-dx,y,z-dz),(x+wx,y+.045,z+wz),(x+dx,y+.07,z+dz),(x-wx,y+.025,z-wz)])

def shade_tree(B,x,z,seed):
 B.tube('mg-bark',(x,.12,z),(x+.18,2.8,z-.15),.15,10,.085)
 for i in range(7):
  a=i*2.399;tip=(x+1.3*math.cos(a),3.7+.35*(i%3),z+1.3*math.sin(a))
  B.tube('mg-bark',(x+.18,2.3,z-.15),tip,.065,7,.015)
  leaves(B,tip,(1.25,1.0,1.25),520,seed+i,'mg-leaf')

def build_garden(B):
 center=(1768,-1054.3)
 patio=scale(Point(*center).buffer(1,resolution=48),4.2,3.2,origin=center)
 site=box(1760.5,-1062.8,1785.5,-1047.0)
 access=LineString([(1768,-1064),(1768,-1045)]).buffer(.95)
 path=patio.union(access).intersection(site)
 B.planar('mg-garden-paving',path,.15,True)
 B.planar('mg-lawn',site.difference(path.buffer(.15)),.09)
 B.planar('mg-coping',path.buffer(.12).difference(path),.14)
 # Clipped oval hedge with two clear openings aligned to the public path.
 ring=patio.buffer(.45).difference(patio.buffer(.06)).difference(access.buffer(.12))
 B.shell(ring,.16,.92,'mg-hedge',roof=False)
 B.planar('mg-hedge',ring,.92)
 # Leaf silhouette instead of perfectly rectangular hedge edges.
 for i in range(68):
  a=i*math.tau/68;x=center[0]+4.45*math.cos(a);z=center[1]+3.45*math.sin(a)
  if abs(x-center[0])>1.12:leaves(B,(x,.83,z),(.28,.25,.28),45,770+i,'mg-leaf')
 for x,z,seed in [(1761.8,-1059.1,180),(1778.3,-1057.5,260)]:
  basin=Point(x,z).buffer(.95,resolution=24)
  B.planar('mg-gravel',basin,.13);shade_tree(B,x,z,seed)
 # Two seating groups keep the north-south walk clear. Loose furniture positions inferred.
 for x0 in [1765.7,1770.3]:
  z=-1054.3
  F=Frame(B,x0,z,0,y=.15)
  F.lathe('mg-chair-frame',0,0,[(0,.3),(.05,.3),(.07,.045),(.70,.045),(.71,.65),(.76,.65)],32)
  F.tube('mg-iron',(0,.76,0),(0,2.55,0),.025,8)
  for i in range(24):
   a=i*math.tau/24;b=(i+1)*math.tau/24
   B.face('mg-shade' if i%2 else 'mg-shade-light',[F.p(0,2.58,0),F.p(1.25*math.cos(a),2.15,1.25*math.sin(a)),F.p(1.25*math.cos(b),2.15,1.25*math.sin(b))])
  for side in [-1,1]:
   C=Frame(B,x0,z+side*1.05,0 if side<0 else math.pi,y=.15)
   C.box('mg-chair-frame',(0,.43,0),(.48,.06,.45))
   for x in [-.2,.2]:
    C.path('mg-chair-frame',[(x,.03,.18),(x,.43,.18),(x,.9,.26)],.025,8)
    C.path('mg-chair-frame',[(x,.03,-.18),(x,.43,-.18),(x,.43,.18)],.025,8)
   for x in [-.16,-.08,0,.08,.16]:C.box('mg-chair-frame',(x,.7,.25),(.035,.36,.045))
 return dict(name='Garden seating approach',points=[(1768,.15,-1063),(1768,.15,-1058),(1768,.15,-1054.3),(1768,.15,-1050),(1768,.15,-1047)])
