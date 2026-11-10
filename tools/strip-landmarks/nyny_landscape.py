"""Original south arrival island, fitted to January 2025 Street View.
Dimensions, species and plant counts are estimates. Existing pavement is retained.
"""
from common import *
TREES=[(-167.2,1648.3,6.5,.4),(-136.0,1648.3,6.1,2.0)]
def landscape(B):
 B.source='nyny-arrival-landscape';B.detail=0
 # Narrow island stays between the existing canopy and outer arrival drive.
 # A low elliptical grass mound rises behind the south-facing flower letters.
 cx,cz=-151.7,1649.1;rx,rz=17.0,3.1;D=.25;n=64
 outer=[(cx+rx*math.cos(a),D,cz+rz*math.sin(a)) for a in np.linspace(0,math.tau,n,endpoint=False)]
 inner=[(cx+rx*.80*math.cos(a),D+.55,cz+rz*.67*math.sin(a)) for a in np.linspace(0,math.tau,n,endpoint=False)]
 top=(cx,D+.9,cz-.65)
 for i in range(n):
  j=(i+1)%n
  B.upface('nyl-grass',[outer[i],outer[j],inner[j],inner[i]],True)
  B.upface('nyl-grass',[inner[i],inner[j],top],True)
  a,b=outer[i],outer[j]
  B.face('nyl-curb',[(a[0],D-.12,a[2]),(b[0],D-.12,b[2]),b,a],True)
 # Fit flower bases to the actual triangulated mound, avoiding buried strokes.
 grass=[g for g in B.groups.values() if g['material']=='nyl-grass'][0]
 def ground(x,z):
  for f in grass['faces']:
   a,b,c=[grass['vertices'][i] for i in f]
   den=(b[2]-c[2])*(a[0]-c[0])+(c[0]-b[0])*(a[2]-c[2])
   if abs(den)<1e-10:continue
   u=((b[2]-c[2])*(x-c[0])+(c[0]-b[0])*(z-c[2]))/den
   v=((c[2]-a[2])*(x-c[0])+(a[0]-c[0])*(z-c[2]))/den
   if u>=-1e-6 and v>=-1e-6 and u+v<=1.000001:return u*a[1]+v*b[1]+(1-u-v)*c[1]
  raise ValueError((x,z))
 # Hand-authored flower letter strokes on the sloping lawn, not image textures.
 glyphs={'N':[(0,0,0,1),(0,1,.8,0),(.8,0,.8,1)],'Y':[(0,1,.4,.5),(.8,1,.4,.5),(.4,.5,.4,0)]}
 for index,ch in enumerate('NYNY'):
  x0=cx-6.1+index*3.25
  for x1,y1,x2,y2 in glyphs[ch]:
   L=math.hypot((x2-x1)*2.7,(y2-y1)*1.7)
   for t in np.linspace(0,1,max(2,math.ceil(L/.17))):
    x=x0+(x1+(x2-x1)*t)*2.7;u=y1+(y2-y1)*t;z=1651.25-u*1.75;y=ground(x,z)
    B.sphere('nyl-flower',(x,y+.09,z),.13,6,4,scale=(1,.65,1))
 # Rear low fence and small upright shrubs. No gate or entrance is blocked.
 for x in np.arange(-163.5,-139.4,.65):B.tube('nyl-fence',(x,D,1646.7),(x,D+1.05,1646.7),.022,6)
 for y in [D+.15,D+.95]:B.tube('nyl-fence',(-163.7,y,1646.7),(-139.5,y,1646.7),.025,6)
 for x in [-161.8,-151.8,-141.8]:
  for j in range(8):
   y=D+.35+j*.22;r=.43*(1-j/10)
   B.sphere('nyl-shrub',(x,y,1647.1),r,8,5,scale=(1,1.15,1))
 for side in [-1,1]:
  for j in range(8):
   x=cx+side*(10.5+(j%3)*1.35);z=1648.4+(j//3)*.85
   B.sphere('nyl-rock',(x,D+.2,z),.35+(j%3)*.1,7,4,scale=(1.35,.7,1))
  for j in range(5):
   x=cx+side*(11.0+j*.9);z=1649.5+(j%2)*.7
   for k in range(9):
    a=k*math.tau/9;dx,dz=math.cos(a),math.sin(a)
    B.face('nyl-sage',[(x-.06*dz,D+.12,z+.06*dx),(x+.06*dz,D+.12,z-.06*dx),(x+.48*dx,D+.65,z+.48*dz)])
 # Tree visual meshes are imported from tools/foliage/models at export.
 for x,z,h,yaw in TREES:
  # Collision-only trunk; the imported source supplies its own visible bark.
  helper=Meshes();helper.property=B.property;helper.source=B.source
  helper.shell(Point(x,z).buffer(.17,resolution=8),D,D+2.5,'nyl-bark',roof=False)
  solid=B.solids[B.property];new=helper.solids[B.property];off=len(solid['vertices'])//3
  solid['vertices'].extend(new['vertices']);solid['indices'].extend(i+off for i in new['indices'])
 Path('build/city-exteriors/nyny-landscape-trees.json').write_text(json.dumps(TREES))

 # Shared sphere helper emits collapsed pole triangles; remove only new visual faces.
 for g in B.groups.values():
  if g["source"]!="nyny-arrival-landscape":continue
  g["faces"]=[f for f in g["faces"] if np.linalg.norm(np.cross(np.array(g["vertices"][f[1]])-g["vertices"][f[0]],np.array(g["vertices"][f[2]])-g["vertices"][f[0]]))>1e-8]
