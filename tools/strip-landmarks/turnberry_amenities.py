"""Original paired court furnishings and open tennis enclosures; dimensions inferred."""
from common import *
KEY='turnberryAmenities'
POOLS=[(1741,-2734),(1854,-2734)]
def build(B):
 B.property=KEY+'-exterior';B.source='turnberry-amenities';B.detail=0
 trees=[];routes=[]
 def lounger(x,z,yaw):
  F=Frame(B,x,z,yaw,y=.3)
  F.box('tta-seat',(0,.4,0),(.72,.1,1.8));F.box('tta-frame-paint',(0,.19,0),(.5,.38,1.4),True)
  B.face('tta-seat',[F.p(-.36,.45,-.4),F.p(.36,.45,-.4),F.p(.36,.9,-.95),F.p(-.36,.9,-.95)])
  for xx in [-.33,.33]:F.path('tta-frame-paint',[(xx,.42,.85),(xx,.42,-.4),(xx,.88,-.95)],.025,6)
 def umbrella(x,z):
  B.tube('tta-frame-paint',(x,.3,z),(x,2.7,z),.05,8)
  B.box('tta-frame-paint',(x,.35,z),(.55,.1,.55),True)
  for j in range(12):
   a=j*math.tau/12;b=(j+1)*math.tau/12
   B.face('tta-canopy',[(x,3.1,z),(x+1.6*math.cos(a),2.6,z+1.6*math.sin(a)),(x+1.6*math.cos(b),2.6,z+1.6*math.sin(b))])
 def palm(x,z,i):
  h=7+(i%4)*1.1;B.lathe('tta-bark',(x,z),[(.08,.22),(h,.11)],12);B.box('tta-bark',(x,h/2,z),(.3,h,.3),True)
  for j in range(12):
   a=j*math.tau/12+i*.6;pts=[]
   for k in range(7):
    t=k/6;r=3.2*t;yy=h+1.4*math.sin(t*math.pi)-1.25*t;w=.33*math.sin(t*math.pi)
    pts.append([(x+r*math.cos(a)-w*math.sin(a),yy,z+r*math.sin(a)+w*math.cos(a)),(x+r*math.cos(a)+w*math.sin(a),yy,z+r*math.sin(a)-w*math.cos(a))])
   for k,(aa,bb) in enumerate(zip(pts,pts[1:])):
    if k==0:B.face('tta-leaf',[aa[0],bb[1],bb[0]])
    elif k==5:B.face('tta-leaf',[aa[0],aa[1],bb[0]])
    else:B.face('tta-leaf',[aa[0],aa[1],bb[1],bb[0]])
 for index,(cx,cz) in enumerate(POOLS):
  water=unary_union([Point(cx-4,cz).buffer(6,resolution=16),Point(cx+4,cz+1).buffer(7,resolution=16),Point(cx+1,cz-6).buffer(5,resolution=16)])
  deck=water.buffer(5)
  B.planar('tta-grass',deck.buffer(3).difference(deck.buffer(.2)).intersection(box(cx-17,cz-16,cx+9,cz+17)),.08)
  for dx in [-6,-3,0,3,6]:lounger(cx+dx,cz+11,0)
  for dz in [-4,0,4]:
   lounger(cx-13.5,cz+dz,math.pi/2);lounger(cx+13.5,cz+dz,-math.pi/2)
  for dx in [-5,5]:umbrella(cx+dx,cz+13)
  for i,(dx,dz) in enumerate([(-15,-12),(-20,1),(-13,16),(13,16),(16,-11),(0,-17)]):palm(cx+dx,cz+dz,index*6+i)
  for dx,dz in [(-18,-8),(-18,8),(-8,17),(6,-16)]:trees.append([cx+dx,cz+dz,5+(index*.4)])
  routes.extend([{'name':f'pool-{index}-south','points':[[cx-4,.3,cz+9.3],[cx+6,.3,cz+9.3]]},{'name':f'pool-{index}-north','points':[[cx-3,.3,cz-12.5],[cx+4,.3,cz-12.5]]}])
 def fence(a,b,h=3):
  dx,dz=b[0]-a[0],b[1]-a[1];L=math.hypot(dx,dz);ux,uz=dx/L,dz/L
  # Thin geometry mesh replaces a high-resolution alpha texture. Density deliberately reduced.
  for t in np.linspace(0,L,max(2,math.ceil(L/.28)+1)):
   x,z=a[0]+ux*t,a[1]+uz*t
   B.face('tta-fence-paint',[(x-ux*.007,.3,z-uz*.007),(x+ux*.007,.3,z+uz*.007),(x+ux*.007,h+.3,z+uz*.007),(x-ux*.007,h+.3,z-uz*.007)])
  for y in np.arange(.3,h+.31,.25):
   B.face('tta-fence-paint',[(a[0],y-.007,a[1]),(b[0],y-.007,b[1]),(b[0],y+.007,b[1]),(a[0],y+.007,a[1])])
  # Independent coarse collision plane; not rendered as an opaque wall.
  c=B.solids[B.property];n=len(c['vertices'])//3;c['vertices'] += [a[0],.3,a[1],b[0],.3,b[1],b[0],h+.3,b[1],a[0],h+.3,a[1]];c['indices'] += [n,n+1,n+2,n,n+2,n+3]
  for t in np.linspace(0,L,max(2,math.ceil(L/3)+1)):
   x,z=a[0]+ux*t,a[1]+uz*t;B.tube('tta-fence-paint',(x,.3,z),(x,h+.38,z),.045,6)
  B.tube('tta-fence-paint',(a[0],h+.3,a[1]),(b[0],h+.3,b[1]),.035,6)
 for i,z in enumerate([-2815,-2742]):
  x=1687
  # Keep existing white lines above the new blue inset and preserve the old court slab.
  B.planar('tta-court-blue',box(x-5.49,z-11.885,x+5.49,z+11.885),.283)
  fence((x-8.8,z-17.8),(x+8.8,z-17.8));fence((x-8.8,z+17.8),(x+8.8,z+17.8));fence((x-8.8,z-17.8),(x-8.8,z+17.8))
  fence((x+8.8,z-17.8),(x+8.8,z+6.8));fence((x+8.8,z+9.2),(x+8.8,z+17.8))
  fence((x-5.7,z),(x+5.7,z),.91)
  B.box('tta-seat',(x,1.23,z),(11.4,.05,.035))
  routes.append({'name':f'tennis-{i}-gate','points':[[x+10,.28,z+8],[x+6.5,.28,z+8],[x-6.5,.28,z+8]]})
 Path('build/city-exteriors/turnberry-amenities-trees.json').write_text(json.dumps(trees))
 Path('docs/project-records/turnberry-towers-amenities/routes.json').write_text(json.dumps(routes,indent=2)+'\n')
 return {'authoredScope':'22 loungers,4 umbrellas,12 palms,8 reused broadleaf trees,two tennis fences/nets/blue insets','fenceHeightM':3,'openGateWidthM':2.4,'countsAndPlacement':'Reduced and photo-fitted,not surveyed; original pool/tower/court geometry remains unchanged.'}
if __name__=='__main__':
 B=Meshes();m=build(B);B.save_all();Path('docs/project-records/turnberry-towers-amenities/geometry.json').write_text(json.dumps(m,indent=2)+'\n');print(sum(len(g['faces'])for g in B.groups.values()),'triangles')
