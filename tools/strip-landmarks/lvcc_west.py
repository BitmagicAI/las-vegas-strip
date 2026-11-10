"""LVCC West Hall: mapped roof outline, 2024 Earth and architect/engineer photos.
Physical heights are estimated; the source's 6m default is not a surveyed height.
"""
from common import *
from forum_shops import facade_frame
KEY='lvccWest';IDS=['relation/19515850']
TERRACE_Y=16.0
def terrace_plan(body):
 # Third-level southwest terrace; register against existing mapped wing.
 # Boundary/elevation are inferred, not a surveyed plan.
 return unary_union([Polygon(p.exterior) for p in parts(body)]).buffer(-2,join_style=2).intersection(box(1210,-1871,1285,-1830))
def roof_y(x,z):
 return 24+20*math.exp(-((x-1348)/54)**2-((z+1880)/67)**2)+3.3*math.exp(-((x-1308)/30)**2-((z+2158)/42)**2)
def exterior(B):
 B.property=KEY+'-exterior';B.source='lvcc-west';B.detail=0
 outline=footprint(IDS[0]);body=outline.buffer(-2,join_style=2).difference(box(1293,-1893,1410,-1830));base=body
 terrace=terrace_plan(outline)
 notch=unary_union([Polygon(r) for p in parts(outline) for r in p.interiors])
 roof_outline=outline
 # The exhibition hall has opaque service elevations; public west/south faces are glazed.
 for pp in parts(body):
  ps=list(pp.exterior.coords)
  for a,b in zip(ps,ps[1:]):
   F,L,nx,nz=facade_frame(B,a,b,pp,0)
   if L<.1:continue
   public=(nx<-.30 or nz>.65 or (a[1]+b[1])/2>-1910);line=LineString([a,b]);segments=max(1,math.ceil(L/2.8))
   for j in range(segments):
    t0=j/segments;t1=(j+1)/segments;ax,az=a[0]+(b[0]-a[0])*t0,a[1]+(b[1]-a[1])*t0;bx,bz=a[0]+(b[0]-a[0])*t1,a[1]+(b[1]-a[1])*t1;ha,hb=roof_y(ax,az)-.8,roof_y(bx,bz)-.8
    # Clip only the upper facade facing the terrace, splitting at the exact boundary.
    wall=LineString([(ax,az),(bx,bz)]);inside=wall.intersection(terrace.buffer(.001))
    if not inside.is_empty:
     for q in ([inside] if inside.geom_type=='LineString' else getattr(inside,'geoms',[])):
      if q.is_empty or q.geom_type!='LineString':continue
      ca,cb=q.coords[0],q.coords[-1]
      B.face('lvw-glass',[(ca[0],0,ca[1]),(cb[0],0,cb[1]),(cb[0],TERRACE_Y,cb[1]),(ca[0],TERRACE_Y,ca[1])],True)
     rest=wall.difference(terrace.buffer(.001))
     for q in ([rest] if rest.geom_type=='LineString' else getattr(rest,'geoms',[])):
      if q.is_empty or q.geom_type!='LineString':continue
      ca,cb=q.coords[0],q.coords[-1];B.face('lvw-glass',[(ca[0],0,ca[1]),(cb[0],0,cb[1]),(cb[0],roof_y(*cb)-.8,cb[1]),(ca[0],roof_y(*ca)-.8,ca[1])],True)
     # The frames below this level retain the established facade rhythm.
     ha=hb=TERRACE_Y
    if inside.is_empty:B.face('lvw-glass' if public else 'lvw-panel',[(ax,0,az),(bx,0,bz),(bx,hb,bz),(ax,ha,az)],True)
    if public:
     B.tube('lvw-frame',(ax+nx*.07,.2,az+nz*.07),(ax+nx*.07,ha,az+nz*.07),.055,6)
     for y in np.arange(3.4,min(ha,hb),3.4):B.tube('lvw-frame',(ax+nx*.09,y,az+nz*.09),(bx+nx*.09,y,bz+nz*.09),.042,6)
     if j%4==0:B.tube('lvw-white',(ax-.3*nx,0,az-.3*nz),(ax-.3*nx,ha,az-.3*nz),.22,10)
    else:
     B.tube('lvw-joint',(ax+nx*.02,.4,az+nz*.02),(ax+nx*.02,ha,az+nz*.02),.025,4)
     if j%5==1:
      mid=(j+.5)*L/segments;F.box('lvw-loading',(mid,2.25,-.08),(2.5,4.5,.07));F.box('lvw-frame',(mid,4.65,-.2),(2.8,.18,.4))
   if public and L>100 and nx<-.3:F.text('LAS VEGAS CONVENTION CENTER',(L/2,18,-.3),1.55,'lvw-letter')
   if public and L>30:
    for x in np.arange(3,L-3,6):
     F.box('lvw-doorframe',(x,1.5,-.19),(2.5,3,.12));F.box('lvw-door',(x,1.5,-.27),(2.25,2.8,.06));F.box('lvw-frame',(x,1.5,-.33),(.06,2.8,.05))
 # Tessellated continuous ribbon: both roof and soffit follow the same smooth profile.
 minx,minz,maxx,maxz=outline.bounds
 for x in np.arange(minx,maxx,5):
  for z in np.arange(minz,maxz,5):
   for pp in parts(roof_outline.intersection(box(x,z,min(x+5,maxx),min(z+5,maxz)))):
    for tri in triangles(pp):
     pts=[(xx,roof_y(xx,zz),zz) for xx,zz in list(tri.exterior.coords)[:-1]];B.upface('lvw-roof',pts,True)
     B.face('lvw-soffit',list(reversed([(xx,yy-.65,zz) for xx,yy,zz in pts])))
 # A closed white fascia joins the top and underside around the entire roof edge.
 for pp in parts(roof_outline):
  ps=list(pp.exterior.coords)
  for a,b in zip(ps,ps[1:]):
   count=max(1,math.ceil(math.dist(a,b)/3))
   for j in range(count):
    ax,az=a[0]+(b[0]-a[0])*j/count,a[1]+(b[1]-a[1])*j/count;bx,bz=a[0]+(b[0]-a[0])*(j+1)/count,a[1]+(b[1]-a[1])*(j+1)/count;ha,hb=roof_y(ax,az),roof_y(bx,bz)
    B.face('lvw-white',[(ax,ha-.7,az),(bx,hb-.7,bz),(bx,hb,bz),(ax,ha,az)])
 # Terrace slab and inward return wall; the outer third level is open air.
 B.planar('lvw-terrace-paving',terrace,TERRACE_Y,True)
 B.planar('lvw-soffit',terrace,TERRACE_Y-.3)
 B.shell(terrace,TERRACE_Y-.3,TERRACE_Y,'lvw-white',roof=False,solid=True)
 body_outer=unary_union([p.exterior for p in parts(body)])
 outer=terrace.boundary.intersection(body_outer.buffer(.01))
 rear=terrace.boundary.difference(body_outer.buffer(.02))
 for line in ([rear] if rear.geom_type=='LineString' else getattr(rear,'geoms',[])):
  if line.geom_type!='LineString':continue
  for a,b in zip(list(line.coords),list(line.coords)[1:]):
   B.face('lvw-glass',[(a[0],TERRACE_Y,a[1]),(b[0],TERRACE_Y,b[1]),(b[0],roof_y(*b)-.8,b[1]),(a[0],roof_y(*a)-.8,a[1])],True)
 for line in ([outer] if outer.geom_type=='LineString' else getattr(outer,'geoms',[])):
  if line.geom_type!='LineString':continue
  for a,b in zip(list(line.coords),list(line.coords)[1:]):
   B.face('lvw-terrace-glass',[(a[0],TERRACE_Y,a[1]),(b[0],TERRACE_Y,b[1]),(b[0],TERRACE_Y+1.15,b[1]),(a[0],TERRACE_Y+1.15,a[1])],True)
   B.tube('lvw-frame',(a[0],TERRACE_Y+1.16,a[1]),(b[0],TERRACE_Y+1.16,b[1]),.035,6)
 # Square paver joints remain a single batch, not thousands of objects.
 for axis in [0,1]:
  lo,hi=(terrace.bounds[0],terrace.bounds[2]) if axis==0 else (terrace.bounds[1],terrace.bounds[3])
  for at in np.arange(math.floor(lo),hi,1.2):
   strip=box(at,-1900,at+.018,-1800) if axis==0 else box(1200,at,1300,at+.018)
   B.planar('lvw-joint',terrace.intersection(strip),TERRACE_Y+.006)
 for x,z in [(1221,-1843),(1243,-1842),(1265,-1842)]:
  for dx in [-1.2,1.2]:B.tube('lvw-white',(x,TERRACE_Y,z),(x+dx,roof_y(x+dx,z)-.7,z),.24,8)
 for x in np.arange(1222,1272,6):
  for z in [-1845,-1853,-1865]:
   if terrace.buffer(-1).contains(Point(x,z)) and not notch.buffer(.5).contains(Point(x,z)):
    B.box('lvw-fixture',(x,roof_y(x,z)-.68,z),(.25,.035,.25))
 for poly in parts(notch):
  ps=list(poly.exterior.coords)
  for a,b in zip(ps,ps[1:]):
   B.face('lvw-white',[(a[0],roof_y(*a)-.65,a[1]),(b[0],roof_y(*b)-.65,b[1]),(b[0],roof_y(*b),b[1]),(a[0],roof_y(*a),a[1])])
 (Path('docs/project-records/convention-area-refinement')/'lvcc-terrace-geometry.json').write_text(json.dumps({'floorY':TERRACE_Y,'floorAreaM2':terrace.area,'roofOpeningAreaM2':notch.area,'bounds':list(terrace.bounds),'limitations':['Inferred registration and elevation, not survey.','No invented event furniture.','Internal access and connection to public stairs remain unimplemented; review deck by direct probe only.','Existing approach roads unchanged.','Not installed or visually accepted.']},indent=2)+'\n')
 # Primary atrium roof ribs and triangulated support below the curved main span.
 for z in np.arange(-1900,-1865,7):
  pts=[]
  for x in np.linspace(1298,1400,35):
   if outline.contains(Point(x,z)):pts.append((x,roof_y(x,z)-1.15,z))
  B.path('lvw-white',pts,.3,8)
  for j in range(0,len(pts)-3,3):
   a,c=pts[j],pts[j+3];mid=((a[0]+c[0])/2,min(a[1],c[1])-3.5,z)
   B.tube('lvw-white',a,mid,.12,8);B.tube('lvw-white',mid,c,.12,8)
 # Roof service equipment follows the flat hall grid, outside the expressive front ribbon.
 for x in np.arange(1350,1538,27):
  for z in np.arange(-2180,-1925,28):
   if outline.contains(box(x-2,z-2,x+2,z+2)):
    y=roof_y(x,z);B.box('lvw-service',(x,y+.7,z),(2.4,1.4,2.4));B.box('lvw-frame',(x,y+1.43,z),(2.7,.12,2.7))
 # Western meeting wing has a repeated diagonal white exoskeleton at its stepped edge.
 for x,z in [(1226,-1874),(1239,-1890),(1252,-1906),(1265,-1923)]:
  B.tube('lvw-white',(x,0,z),(x-7,23.4,z+12),.42,10)
 # Main sign and sheltered entry apron; no changes to mapped roads.
 F=Frame(B,1350,-1892.8,math.pi,y=0);F.text('LAS VEGAS CONVENTION CENTER WEST HALL',(0,6.5,-.35),.75,'lvw-letter');F.box('lvw-white',(0,5.4,-2.5),(70,.32,5),True)
 for x in [-32,-16,0,16,32]:F.box('lvw-frame',(x,2.65,-4.4),(.25,5.3,.25),True)
 B.planar('lvw-paving',box(1313,-1892,1387,-1885),.22,True)
 return dict(key=KEY,name='Las Vegas Convention Center West Hall',center=[1400,0,-2025],bounds=list(outline.bounds),structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],views={})
