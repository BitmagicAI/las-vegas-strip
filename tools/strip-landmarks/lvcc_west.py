"""LVCC West Hall: mapped roof outline, 2024 Earth and architect/engineer photos.
Physical heights are estimated; the source's 6m default is not a surveyed height.
"""
from common import *
from forum_shops import facade_frame
KEY='lvccWest';IDS=['relation/19515850']
def roof_y(x,z):
 return 24+20*math.exp(-((x-1348)/54)**2-((z+1880)/67)**2)+3.3*math.exp(-((x-1308)/30)**2-((z+2158)/42)**2)
def exterior(B):
 B.property=KEY+'-exterior';B.source='lvcc-west';B.detail=0
 outline=footprint(IDS[0]);body=outline.buffer(-2,join_style=2).difference(box(1293,-1893,1410,-1830));base=body
 # The exhibition hall has opaque service elevations; public west/south faces are glazed.
 for pp in parts(body):
  ps=list(pp.exterior.coords)
  for a,b in zip(ps,ps[1:]):
   F,L,nx,nz=facade_frame(B,a,b,pp,0)
   if L<.1:continue
   public=(nx<-.30 or nz>.65 or (a[1]+b[1])/2>-1910);line=LineString([a,b]);segments=max(1,math.ceil(L/2.8))
   for j in range(segments):
    t0=j/segments;t1=(j+1)/segments;ax,az=a[0]+(b[0]-a[0])*t0,a[1]+(b[1]-a[1])*t0;bx,bz=a[0]+(b[0]-a[0])*t1,a[1]+(b[1]-a[1])*t1;ha,hb=roof_y(ax,az)-.8,roof_y(bx,bz)-.8
    B.face('lvw-glass' if public else 'lvw-panel',[(ax,0,az),(bx,0,bz),(bx,hb,bz),(ax,ha,az)],True)
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
   for pp in parts(outline.intersection(box(x,z,min(x+5,maxx),min(z+5,maxz)))):
    for tri in triangles(pp):
     pts=[(xx,roof_y(xx,zz),zz) for xx,zz in list(tri.exterior.coords)[:-1]];B.upface('lvw-roof',pts,True)
     B.face('lvw-soffit',list(reversed([(xx,yy-.65,zz) for xx,yy,zz in pts])))
 # A closed white fascia joins the top and underside around the entire roof edge.
 for pp in parts(outline):
  ps=list(pp.exterior.coords)
  for a,b in zip(ps,ps[1:]):
   count=max(1,math.ceil(math.dist(a,b)/3))
   for j in range(count):
    ax,az=a[0]+(b[0]-a[0])*j/count,a[1]+(b[1]-a[1])*j/count;bx,bz=a[0]+(b[0]-a[0])*(j+1)/count,a[1]+(b[1]-a[1])*(j+1)/count;ha,hb=roof_y(ax,az),roof_y(bx,bz)
    B.face('lvw-white',[(ax,ha-.7,az),(bx,hb-.7,bz),(bx,hb,bz),(ax,ha,az)])
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
