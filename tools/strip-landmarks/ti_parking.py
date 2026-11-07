"""Three individually surveyed TI/Mirage-era garages. Roof/ramp elevations estimated."""
from common import *
from forum_shops import facade_frame
from luxor_parking import soffit
KEY='tiParking';IDS=['way/111367820','way/403004627','way/33992535']
SPECS=[(IDS[0],[.24,3.64],(-330,-963,-307,-944)),(IDS[1],[.24,3.44,6.34,9.24,12.14,15.04,17.94],(-124,-961,-98,-944)),(IDS[2],[.24,3.24,6.24,9.24],(59,-818,82,-801))]
def exterior(B):
 B.property=KEY+'-exterior';B.detail=0
 polys=[]
 for ident,levels,ramp in SPECS:
  B.source='ti-parking-'+ident.split('/')[-1];p=footprint(ident);polys.append(p);hole=box(*ramp);top=levels[-1]
  x0,z0,x1,z1=ramp
  for i,y in enumerate(levels):
   deck=p if i==0 else p.difference(hole)
   if ident==IDS[1] and i==2:deck=deck.difference(box(-39,-987.3,-30,-981.4))
   B.planar('skg-deck',deck,y,True);B.shell(deck,max(.01,y-.23),y,'skg-slab',roof=False)
   if i:soffit(B,deck,y-.23)
  for ya,yb in zip(levels,levels[1:]):
   B.upface('skg-deck',[(x0,ya,z0),(x1,yb,z0),(x1,yb,z1),(x0,ya,z1)],True)
   B.face('skg-slab',[(x0,ya-.23,z0),(x1,yb-.23,z0),(x1,yb-.23,z1),(x0,ya-.23,z1)])
   for z in [z0,z1]:B.face('st-white',[(x0,ya-.23,z),(x1,yb-.23,z),(x1,yb+.9,z),(x0,ya+.9,z)],True)
   B.upface('skg-line',[(x0,ya+.016,(z0+z1)/2-.04),(x1,yb+.016,(z0+z1)/2-.04),(x1,yb+.016,(z0+z1)/2+.04),(x0,ya+.016,(z0+z1)/2+.04)])
  for pp in parts(p):
   cc=list(pp.exterior.coords)
   for a,b in zip(cc,cc[1:]):
    F,L,_,_=facade_frame(B,a,b,pp,0)
    for y in levels[1:]:
     edge=LineString([a,b]);cut=box(-34,-987.4,-28,-981.3) if ident==IDS[1] and abs(y-6.34)<.01 else Polygon()
     for seg in parts(edge.difference(cut),'LineString'):
      aa,bb=list(seg.coords)[0],list(seg.coords)[-1];G,ll,_,_=facade_frame(B,aa,bb,pp,0);G.box('st-white',(ll/2,y+.35,0),(ll,.7,.3),True)
      if ident==IDS[1]:
       for dy in [.12,.30,.48,.66]:G.box('st-white',(ll/2,y+dy,-.19),(ll,.035,.08))
    for x in np.linspace(.25,max(.25,L-.25),max(2,round(L/7.5)+1)):
     q=F.p(x,0,0)
     if ident==IDS[1] and q[0]>-34 and -987.5<q[2]<-981.2:continue
     # Reference-supported guest entry aperture: retain all upper column sections.
     lo=3.44 if ident==IDS[1] and q[0]>-34.5 and -965<q[2]<-947 else 0
     F.box('st-white',(x,(top+lo)/2,0),(.5,top-lo,.55),True)
    F.box('st-white',(L/2,top+.94,0),(L,.14,.3),True)
  usable=p.buffer(-1).difference(hole.buffer(.6));minx,minz,maxx,maxz=p.bounds
  for x in np.arange(minx+7,maxx-2,8):
   for z in np.arange(minz+7,maxz-2,17):
    if usable.contains(Point(x,z)):B.box('skg-slab',(x,top/2,z),(.45,top,.45),True)
  for z in np.arange(minz+5,maxz-3,17):
   for x in np.arange(minx+3,maxx-2,2.7):B.planar('skg-line',box(x,z,x+.075,z+5).intersection(usable),top+.014)
  for x in np.arange(minx+20,maxx-10,45):
   for z in np.arange(minz+20,maxz-10,43):
    if not usable.contains(Point(x,z)):continue
    B.box('st-grey',(x,top+2.3,z),(.09,4.6,.09));B.box('st-grey',(x,top+4.65,z),(.75,.15,.3))
 # Match the retained bridge deck at6.035m without adding a second bridge.
 B.upface('skg-deck',[(-39,6.34,-987.3),(-32.6,6.035,-987.3),(-32.6,6.035,-981.4),(-39,6.34,-981.4)],True)
 # Guest garage roof plant, six round fan housings and parapet returns.
 B.source='ti-parking-403004627';roof=17.94
 plant=box(-95,-964,-65,-945);B.shell(plant,roof,roof+2.6,'st-white',roof=False);B.planar('skg-slab',plant,roof+2.6)
 for x in [-88,-74]:
  for z in [-960,-954,-948]:
   disk=Point(x,z).buffer(1.8,resolution=16);B.shell(disk,roof+2.6,roof+3,'st-grey',roof=False);B.planar('darkglass',disk,roof+3)
 # North advertising panel and elevator core. No invented commercial artwork.
 F=Frame(B,-103,-1036,0,y=0)
 F.box('st-white',(0,9,0),(14,18,.55),True);F.box('darkglass',(0,11,-.32),(11,10,.06));F.text('TI',(0,11,-.38),2.2,'st-white');F.text('PARKING',(0,7,-.38),.6,'st-white')
 # Modest entrance awnings observed along north perimeter; underside kept open.
 for x in [-92,-78,-64]:
  G=Frame(B,x,-1035,0,y=0);G.box('ri-letter',(0,2.8,-1.2),(5,.3,2.4));G.text('PARK',(0,2.42,-2.43),.32,'st-white')
 # Dated east-entry canopy: original curved fabric, ribs and scalloped valance.
 # Dimensions inferred; see ti-parking-refinement/research.md.
 B.source='ti-parking-403004627'
 def canopy_point(t,z):
  wall=-33.354+(z+950.49)*(-1.034/49.615)
  return (wall+3.4*math.sin(t),3.10+.95*math.cos(t),z)
 profile=np.linspace(0,math.pi/2,17)
 for a,b in zip(profile,profile[1:]):
  pts=[canopy_point(a,-965),canopy_point(b,-965),canopy_point(b,-947),canopy_point(a,-947)]
  B.upface('ti-canopy-fabric',pts);B.face('ti-canopy-fabric',[(x,y-.035,z) for x,y,z in reversed(pts)])
 for z in np.linspace(-965,-947,13):
  B.path('ti-canopy-frame',[canopy_point(t,z) for t in profile],.025,6)
 for z0 in np.arange(-965,-947,.6):
  for a,b in zip(np.linspace(0,math.pi,9),np.linspace(0,math.pi,9)[1:]):
   za=z0+.6*a/math.pi;zb=z0+.6*b/math.pi
   pa=canopy_point(math.pi/2,za);pb=canopy_point(math.pi/2,zb)
   pts=[pa,pb,(pb[0],2.98-.13*math.sin(b),zb),(pa[0],2.98-.13*math.sin(a),za)]
   B.face('ti-canopy-fabric',pts);B.face('ti-canopy-fabric',[(x-.012,y,z) for x,y,z in reversed(pts)])
 for z,label,size,width in [(-961.5,'EXIT',.29,3.0),(-956,'TREASURE ISLAND',.31,6.2),(-950.5,'ENTRANCE',.29,3.0)]:
  x=canopy_point(math.pi/2,z)[0]+.035
  G=Frame(B,x,z,-math.pi/2,y=0)
  G.box('ti-canopy-frame',(0,3.14,0),(width,.44,.04))
  G.text(label,(0,3.02,-.035),size,'st-white')
 return dict(key=KEY,name='TI and neighboring parking structures',center=[-115,0,-925],bounds=list(unary_union(polys).bounds),structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],views={})
