"""Crystals roof refinement from Google Earth 2022-11-09 oblique/plan.
Metre-scale photo estimates, not a measured survey. The existing mall perimeter
and public interior datum are retained. Broad diagonal folds replace the repeated
pyramid grid. Paired upper/soffit faces preserve a closed roof thickness.
"""
from common import *
KEY='crystalsRoof'
# Irregular shared control net: each vertex is shared by neighboring facets.
# South roof terminates around the existing Veer tower masses, which remain owners.
POINTS=[(-180.3,18,824.3),(-123,23,824.3),(-78,30,824.3),(-40.99,18,824.3),
 (-180.3,24,856),(-138,32,844),(-94,22,862),(-40.99,26,855),
 (-180.3,18,896),(-148,25,890),(-116,34,879),(-67,20,892),(-40.99,18,892),
 (-180.3,26,932),(-129,20,926),(-88,32,924),(-40.99,30,935),
 (-180.3,18,967),(-149,24,958),(-110,18,968),(-73,25,963),(-40.99,18,970),
 (-180.3,18,1001),(-127,21,1001),(-79,27,1001),(-40.99,18,1001)]
FACES=[(0,1,5),(0,5,4),(1,2,6),(1,6,5),(2,3,7),(2,7,6),
 (4,5,9,8),(5,6,10,9),(6,7,11,10),(7,12,11),
 (8,9,14,13),(9,10,14),(10,11,15,14),(11,12,16,15),
 (13,14,18,17),(14,15,19,18),(15,16,20,19),(16,21,20),
 (17,18,23,22),(18,19,23),(19,20,24,23),(20,21,25,24)]
def exterior(B):
 B.property=KEY+'-exterior';B.source='crystals-irregular-roof';B.detail=0
 panels=[]
 # 63 CityCenter is a separate, newer building on the north edge. Its mapped
 # footprint replaces the formerly overextended approximation of this roof.
 northwing=footprint('way/1422113646')
 cut=unary_union([footprint('way/1421481100'),footprint('way/1422113647')]).buffer(.05).union(northwing)
 def roof_face(mat,pts,solid=False):
  projected=Polygon([(v[0],v[2]) for v in pts])
  if projected.area<1e-8:return
  kept=projected.difference(cut)
  a,b,c=np.array(pts[:3],float)
  coeff=np.linalg.solve(np.array([[v[0],v[2],1] for v in (a,b,c)]),np.array([a[1],b[1],c[1]]))
  for poly in parts(kept):
   for tri in triangles(poly):
    B.upface(mat,[(x,float(coeff[0]*x+coeff[1]*z+coeff[2]),z) for x,z in list(tri.exterior.coords)[:-1]],solid)

 for fi,ids in enumerate(FACES):
  # Split quads into explicit triangles; never rely on non-planar quad tessellation.
  for k in range(1,len(ids)-1):
   pts=[POINTS[i] for i in [ids[0],ids[k],ids[k+1]]];p=np.array(pts,float)
   mat='cr-metal-light-paint' if fi%5==0 else 'cr-metal-paint'
   roof_face(mat,pts,True)
   below=[(x,y-.28,z) for x,y,z in pts]
   if np.cross(np.array(below[1])-below[0],np.array(below[2])-below[0])[1]>0:below.reverse()
   roof_face('cr-soffit',below,True)
   panels.append(p)
   # Standing seam direction follows the long facet edge; sparse physically small
   # raised strips, rather than black lines that alias at street distance.
   a,b,c=p
   for t in np.arange(.14,.99,.14):
    p0=a*(1-t)+c*t;p1=b*(1-t)+c*t
    if np.linalg.norm(p1-p0)<2:continue
    normal=np.cross(b-a,c-a);normal/=np.linalg.norm(normal)
    if normal[1]<0:normal=-normal
    width=np.cross(normal,p1-p0);width/=np.linalg.norm(width);width*=.017
    p0+=normal*.015;p1+=normal*.015
    roof_face('cr-seam-paint',[tuple(p0-width),tuple(p1-width),tuple(p1+width),tuple(p0+width)])
 # Close only exposed perimeter edges; internal shared facets have no duplicate walls.
 edges={}
 for ids in FACES:
  for a,b in zip(ids,ids[1:]+ids[:1]):
   e=tuple(sorted((a,b)));edges[e]=edges.get(e,0)+1
 for (a,b),count in edges.items():
  if count==1:
   x,y,z=POINTS[a];u,v,w=POINTS[b]
   edge=LineString([(x,z),(u,w)]);outside=edge.difference(cut)
   pieces=list(outside.geoms) if hasattr(outside,'geoms') else [outside]
   for segment in pieces:
    if segment.geom_type!='LineString' or segment.length<.01:continue
    q0,q1=list(segment.coords)[0],list(segment.coords)[-1]
    t0=edge.project(Point(q0))/edge.length;t1=edge.project(Point(q1))/edge.length
    B.face('cr-soffit',[(q0[0],y+(v-y)*t0,q0[1]),(q1[0],y+(v-y)*t1,q1[1]),(q1[0],17.72,q1[1]),(q0[0],17.72,q0[1])],True)
 # Broad northern wing: footprint traced in mapping and corroborated by
 # satellite/Kalzip photograph. 18–27m roof elevations remain estimates.
 B.source='crystals-northwest-wing'
 def height(x,z):return 19.0+(855.5-z)*.125
 oldcoverage=unary_union([Polygon([(POINTS[i][0],POINTS[i][2]) for i in ids]) for ids in FACES])
 for poly in parts(northwing):
  for tri in triangles(poly):
   vs=[(x,height(x,z),z) for x,z in list(tri.exterior.coords)[:-1]]
   B.upface('cr-metal-paint',vs,True)
   below=[(x,y-.28,z) for x,y,z in vs];B.face('cr-soffit',list(reversed(below)),True)
 # Long physical seam strips follow the broad plane, clipped to its perimeter.
 for x in np.arange(-202,-117,1.15):
  line=LineString([(x,790),(x+8,866)]).intersection(northwing)
  for segment in ([line] if line.geom_type=='LineString' else list(getattr(line,'geoms',[]))):
   if segment.length<.3:continue
   (xx,zz),(xxx,zzz)=list(segment.coords)[0],list(segment.coords)[-1]
   B.upface('cr-seam-paint',[(u,height(u,v)+.02,v) for u,v in [(xx-.022,zz),(xxx-.022,zzz),(xxx+.022,zzz),(xx+.022,zz)]])
 # Close joins against each retained roof facet instead of leaving open cuts.
 for ids in FACES:
  for k in range(1,len(ids)-1):
   pts=[POINTS[i] for i in [ids[0],ids[k],ids[k+1]]]
   projected=Polygon([(v[0],v[2]) for v in pts])
   edge=northwing.boundary.intersection(projected)
   coeff=np.linalg.solve(np.array([[v[0],v[2],1] for v in pts]),np.array([v[1] for v in pts]))
   for seg in ([edge] if edge.geom_type=='LineString' else list(getattr(edge,'geoms',[]))):
    if seg.geom_type!='LineString' or seg.length<.01:continue
    a,b=list(seg.coords)[0],list(seg.coords)[-1]
    ya,yb=height(*a),height(*b);oa=float(coeff[0]*a[0]+coeff[1]*a[1]+coeff[2]);ob=float(coeff[0]*b[0]+coeff[1]*b[1]+coeff[2])
    if max(abs(ya-oa),abs(yb-ob))<.04:continue
    if (ya-oa)*(yb-ob)<0:
     t=(ya-oa)/((ya-oa)-(yb-ob));q=(a[0]+(b[0]-a[0])*t,ya+(yb-ya)*t,a[1]+(b[1]-a[1])*t)
     B.face('cr-soffit',[(a[0],ya,a[1]),q,(a[0],oa,a[1])],True)
     B.face('cr-soffit',[q,(b[0],yb,b[1]),(b[0],ob,b[1])],True)
    else:
     B.face('cr-soffit',[(a[0],ya,a[1]),(b[0],yb,b[1]),(b[0],ob,b[1]),(a[0],oa,a[1])],True)
 # Exterior-only returns where this wing extends beyond the previous mall shell.
 from forum_shops import facade_frame
 for a,b in zip(list(northwing.exterior.coords),list(northwing.exterior.coords)[1:]):
  edge=LineString([a,b]);exposed=edge.difference(oldcoverage.buffer(.02))
  for seg in ([exposed] if exposed.geom_type=='LineString' else list(getattr(exposed,'geoms',[]))):
   if seg.geom_type!='LineString' or seg.length<.1:continue
   aa,bb=list(seg.coords)[0],list(seg.coords)[-1];G,L,_,_=facade_frame(B,aa,bb,northwing,.015)
   # Glazed north/west volume under the metal plane; no interior replacement.
   B.face('cr-nw-glass',[(aa[0],.24,aa[1]),(bb[0],.24,bb[1]),(bb[0],height(*bb)-.28,bb[1]),(aa[0],height(*aa)-.28,aa[1])],True)
   for u in np.arange(0,L+.01,2.5):
    x,_,z=G.p(u,0,0);h=height(x,z)-.28
    G.box('cr-nw-frame',(u,(h+.24)/2,-.04),(.075,h-.24,.12))
   for y in [1,5,9,13,17]:G.box('cr-nw-frame',(L/2,y,-.04),(L,.07,.12))
 # Roof panel coverage evidence for replacement collision tests.
 Path('build/city-exteriors/crystals-roof-triangles.json').write_text(json.dumps([p.tolist() for p in panels]))
 return dict(key=KEY,name='Crystals folded metal roof',center=[-110,0,913],bounds=[-203,792,-41,1002],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],views={})
