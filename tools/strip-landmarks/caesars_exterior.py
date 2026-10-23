"""Seven mapped Caesars tower volumes. Earth Nov2022; detail dimensions estimated.
Public casino and Forum geometry are retained. The roof cut follows the relocated
existing guest stair; no room content or floor schedule is regenerated.
"""
from common import *
from building_surfaces import BuildingSurfaces
from forum_shops import facade_frame,arch_panel
KEY='caesarsExterior'
IDS=['way/134944648','way/134949098','way/134949101','way/134949102','way/134949402','way/126267789','way/1176928048']
HEIGHTS=[133,52,45,71,40,107,111]
LOW=['way/134949710','way/134949713','way/134949715']
class Access:
 def wall(self,a,b,lo,hi):
  line=LineString([a,b]);region=box(0,lo,line.length,hi)
  # Keep the existing occupied casino volume and public circulation unobstructed.
  for seg in parts(line.intersection(box(-354,-128.1,-179,-8.2)),'LineString'):
   ds=[line.project(Point(v)) for v in seg.coords];region=region.difference(box(min(ds),0,max(ds),8.6))
  return [[[line.interpolate(x).x,y,line.interpolate(x).y] for x,y in list(t.exterior.coords)[:-1]] for q in parts(region) for t in triangles(q)]
def exterior(B):
 B.property=KEY+'-exterior';B.detail=0
 rs=[dict(BYID[i],shape=footprint(i),height=h,base=0) for i,h in zip(IDS,HEIGHTS)];surf=BuildingSurfaces(rs)
 for k,r in enumerate(rs):
  p=r['shape'];h=r['height']-(3.8 if k in (0,5,6) else 0);B.source='tower/caesars' if k==0 else 'caesars/tower-'+str(k)
  for poly in parts(p):
   ps=list(poly.exterior.coords)
   for a,b in zip(ps,ps[1:]):
    L=math.dist(a,b)
    if L<.1:continue
    F,_,nx,nz=facade_frame(B,a,b,p,.06);ux,uz=(b[0]-a[0])/L,(b[1]-a[1])/L;line=LineString([a,b]);ts=surf.wall(r['id'],a,b,0,h,Access())
    region=unary_union([Polygon([(line.project(Point(v[0],v[2])),v[1]) for v in t]) for t in ts])
    def patch(mat,x0,y0,x1,y1,off=.12):
     if x1<=x0 or y1<=y0:return
     for q in parts(region.intersection(box(x0,y0,x1,y1))):
      for t in triangles(q):B.face(mat,[(a[0]+ux*x+nx*off,y,a[1]+uz*x+nz*off) for x,y in list(t.exterior.coords)[:-1]])
    patch('cp-stone' if k==4 else 'cp-white',0,0,L,h)
    for xx in np.arange(2,L-2,4.3):
     patch('cp-glass',xx,1,min(xx+2.5,L),5,.22)
     patch('cp-stone',xx-.15,.7,min(xx+2.65,L),1,.35)
    if k in (1,2):
     # Original curved Julius wings have broad horizontal window ribbons.
     for y in np.arange(10,h-2,3):
      patch('cp-glass',.5,y,L-.5,y+1.7,.21);patch('cp-sill',0,y-.24,L,y-.06,.42)
      for x in np.arange(1,L,2.7):patch('cp-frame',x,y,min(x+.09,L),y+1.7,.26)
    elif k==4:
     for x in np.arange(1,L-1,3.6):
      for y in np.arange(10,h-1,3):
       patch('cp-shadow',x-.15,y-.15,min(x+2.3,L),y+1.9,.2);patch('cp-glass',x,y,min(x+2.15,L),y+1.75,.23)
       patch('cp-stone',x-.2,y-.3,min(x+2.4,L),y-.15,.45)
    else:
     end=L<34
     count=max(1,round(L/(4.3 if k==0 else 4.0)));w=L/count
     for j in range(count):
      x=j*w
      # Palace ends are largely white shafts; south tower ends retain tall slots.
      if not (k==0 and end):
       for y in np.arange(11,h-13,3.35):
        patch('cp-shadow',x+.42,y-.12,x+w-.42,y+2.57,.18)
        patch('cp-glass',x+.6,y,x+w-.6,y+2.4,.21)
        patch('cp-frame',x+w*.5-.04,y,x+w*.5+.04,y+2.4,.25)
        patch('cp-sill',x+.4,y-.25,x+w-.4,y-.1,.35)
       F.box('cp-white',(x+.18,(h+8.6)/2,-.30),(.3,h-8.6,.45))
     # Deep crown cornices and paired upper arched windows.
     for yy,depth in [(h-13,.65),(h-2,.8),(h-.5,1.1)]:F.box('cp-white',(L/2,yy,-depth/2),(L,.55,depth))
     if k==0:
      if end:F.text('CAESARS PALACE',(L/2,h-19,-.5),1.3,'cp-gold')
      else:
       for x in np.arange(w*.5,L,w):
        for yy in [h-11.5,h-6.8]:patch('cp-glass',x-w*.32,yy,x+w*.32,yy+3.5,.25)
       for x in np.arange(0,L,12.9):F.box('cp-white',(x+.4,(h+8.6)/2,-.5),(.85,h-8.6,.8))
       for yy in [h*.33,h*.66]:F.box('cp-white',(L/2,yy,-.45),(L,.9,.7))
     else:
      for x in np.arange(w*.5,L,w):
       width=min(w*.67,2.8);radius=width/2;bottom=h-12.4;spring=bottom+9.4-radius
       arc=[(x+radius*math.cos(t),spring+radius*math.sin(t)) for t in np.linspace(0,math.pi,13)]
       pts=[(x-radius,bottom),(x+radius,bottom),*arc]
       B.face('cp-glass',[F.p(u,v,-.35) for u,v in pts[::-1]])
       for aa,bb in zip(np.linspace(0,math.pi,13),np.linspace(0,math.pi,13)[1:]):
        B.face('cp-white',[F.p(x+r*math.cos(t),spring+r*math.sin(t),-.50) for r,t in [(radius,aa),(radius,bb),(radius+.18,bb),(radius+.18,aa)]])
       for side in [-1,1]:F.box('cp-white',(x+side*(radius+.09),(bottom+spring)/2,-.44),(.18,spring-bottom,.18))
    F.box('cp-white',(L/2,h+.12,0),(L,.24,.48))
    for t in ts:
     c=B.solids[B.property];n=len(c['vertices'])//3;c['vertices'].extend(v for pt in t for v in pt);c['indices'].extend([n,n+1,n+2])
   B.planar('cp-roof',surf.roof(r['id'],poly,h),h+.02,True)
  # Red hip crowns: separate pavilions, not one enormous roof over the footprint.
  if k in (0,5,6):
   xmin,zmin,xmax,zmax=p.bounds
   zones=[(xmin,xmin+(xmax-xmin)*.25),(xmin+(xmax-xmin)*.38,xmin+(xmax-xmin)*.63),(xmin+(xmax-xmin)*.75,xmax)] if k==0 else [(xmin,xmax)]
   for left,right in zones:
    roof=p.intersection(box(left,zmin,right,zmax)).buffer(-.8)
    for q in parts(roof):
     # Inset ridge follows each pavilion's long axis; hip edges meet at fixed heights.
     xs,zs,xe,ze=q.bounds;zc=(zs+ze)/2;ridge=LineString([(xs+(ze-zs)*.45,zc),(xe-(ze-zs)*.45,zc)]) if xe-xs>ze-zs else LineString([((xs+xe)/2,zs+1),((xs+xe)/2,ze-1)])
     coords=list(q.exterior.coords)
     for a,b in zip(coords,coords[1:]):
      ra=ridge.interpolate(ridge.project(Point(a)));rb=ridge.interpolate(ridge.project(Point(b)))
      B.face('cp-tile',[(a[0],h+.3,a[1]),(b[0],h+.3,b[1]),(rb.x,h+3.8,rb.y),(ra.x,h+3.8,ra.y)])
  if k in (1,2,3,4):
   for x in np.arange(p.bounds[0]+5,p.bounds[2]-4,15):
    for z in np.arange(p.bounds[1]+5,p.bounds[3]-4,15):
     if p.contains(box(x-1.7,z-1.5,x+1.7,z+1.5)):B.box('cp-service',(x,h+.65,z),(3.4,1.2,3));B.box('cp-shadow',(x,h+1.27,z),(3,.04,2.6))
 # Surveyed service blocks: two open parking structures and west conference wing.
 for ident in LOW:
  p=footprint(ident);garage=ident!=LOW[2];h=23 if garage else 6;B.source='caesars/'+ident
  B.planar('cp-roof',p,h,True)
  for poly in parts(p):
   ps=list(poly.exterior.coords)
   for a,b in zip(ps,ps[1:]):
    if math.dist(a,b)<.1:continue
    F,L,_,_=facade_frame(B,a,b,p,.02)
    if garage:
     F.box('cp-shadow',(L/2,h/2,0),(L,h,.16),True)
     for yy in np.arange(0,h,3.2):F.box('cp-white',(L/2,yy+.65,-.18),(L,1.3,.42))
     for xx in np.arange(0,L,7.5):F.box('cp-white',(xx,h/2,-.3),(.7,h,.6))
    else:
     F.box('cp-stone',(L/2,h/2,0),(L,h,.2),True)
     for xx in np.arange(2,L-3,6):
      F.box('cp-shadow',(xx,2.1,-.18),(3,3.7,.09));F.box('cp-white',(xx-2.3,3,-.3),(.6,6,.5))
     F.box('cp-white',(L/2,5.5,-.3),(L,.65,.65))
    F.box('cp-white',(L/2,h+.4,0),(L,.8,.4))
  if not garage:
   for x in np.arange(p.bounds[0]+8,p.bounds[2]-6,18):
    for z in np.arange(p.bounds[1]+8,p.bounds[3]-6,23):
     if p.contains(box(x-2,z-1.5,x+2,z+1.5)):B.box('cp-service',(x,h+.6,z),(4,1.2,3));B.box('cp-shadow',(x,h+1.22,z),(3.5,.04,2.5))
 from caesars_poolcourt import exterior as poolcourt
 poolcourt(B)
 from caesars_colosseum import exterior as colosseum
 report=colosseum(B)
 from caesars_podium import exterior as podium
 podium(B,IDS,LOW)
 from caesars_frontage import exterior as frontage
 front=frontage(B)
 from caesars_absinthe import exterior as absinthe, purple_zebra, roman_plaza, mojito
 garden=dict(absinthe=absinthe(B),purpleZebra=purple_zebra(B),romanPlaza=roman_plaza(B),mojito=mojito(B))
 from caesars_rotunda import exterior as rotunda
 Path('build/city-exteriors/caesars-rotunda-plan.json').write_text(json.dumps(rotunda(B),indent=2))
 Path('build/city-exteriors/caesars-garden-plan.json').write_text(json.dumps(garden,indent=2))
 Path('build/city-exteriors/caesars-frontage-plan.json').write_text(json.dumps(front,indent=2))
 (Path("build/city-exteriors")/"caesars-colosseum-plan.json").write_text(json.dumps(report,indent=2))
 return dict(key=KEY,name='Caesars individual tower exteriors',center=[-300,0,-40],bounds=[-585,-252,-10,121],building='caesars',structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=['caesars'],views={})
