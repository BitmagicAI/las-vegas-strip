"""Former SuperPawn1700Main: closed2026 exterior, mapped L plan."""
from common import *
from forum_shops import facade_frame
KEY='main1700'
def exterior(B):
 B.property=KEY+'-exterior';B.source='podium/closed-commercial';B.detail=0
 p=footprint('way/725949470');north=p.intersection(Polygon([(1600,-3950),(1720,-3950),(1720,-3883),(1600,-3883)]));south=p.intersection(box(1600,-3883,1720,-3800))
 for part,h in [(north,4.7),(south,6.9)]:
  B.shell(part,.15,h,'mp-white-paint',roof=False);B.planar('mp-roof-paint',part,h-.18,True)
  for a,b in zip(list(part.exterior.coords),list(part.exterior.coords)[1:]):
   G,L,nx,nz=facade_frame(B,a,b,part,.025)
   # Boundary between heights is retained only above the lower roof.
   internal=abs(a[1]+3883)<.01 and abs(b[1]+3883)<.01
   if internal:continue
   G.box('mp-fascia-paint',(L/2,h-.38,-.06),(L,.78,.16))
   G.box('mp-coping-paint',(L/2,h+.025,-.015),(L,.07,.24))
   for u in np.arange(0,L,2.5):G.box('mp-joint-paint',(float(u),h/2,-.035),(.014,h-.8,.018))
   if nx<-.65 or nz>.7:
    G.box('mp-turquoise-paint',(L/2,.43,-.045),(L,.55,.12))
    for u in np.arange(1,L,7):G.box('mp-drain-paint',(float(u),h/2,-.11),(.09,h-.6,.13))
   if nx>.7 and h>6 and L>5:
    u=L*.62
    G.box('mp-door-paint',(u,1.66,-.07),(1.2,2.25,.14));G.box('mp-handle-paint',(u+.4,1.6,-.16),(.07,.14,.06))
    G.text('1700',(u-1,2.1,-.11),.28,'mp-ink-letter')
    # Real ramp follows the facade: two boundaries, open ends and landing.
    # The ramp rises from north toward the southern door.
    start=max(.5,u-6);end=u+1.3;w0=-2.2;w1=-.3
    verts=[G.p(start,.18,w0),G.p(end,.7,w0),G.p(end,.7,w1),G.p(start,.18,w1)]
    B.upface('mp-ramp',verts,True)
    for w in [w0,w1]:
     for a0 in np.arange(start,end+.01,.18):
      y=.18+.52*(a0-start)/(end-start);G.tube('mp-rail-paint',(float(a0),y,w),(float(a0),y+1.05,w),.013,6)
     for offset in [.15,1.05]:G.tube('mp-rail-paint',(start,.18+offset,w),(end,.7+offset,w),.03,8)
    # Landing is against the door at the elevated end.
    G.box('mp-ramp',(end+.65,.63,-1.25),(1.3,.14,1.9),True)
   if nz>.7 and h>6:
    G.box('mp-vent',(L*.15,5.25,-.075),(1.2,.55,.15))
 W=Frame(B,0,0,y=0)
 site=Polygon([(1635,-3914),(1683,-3911),(1684,-3866),(1679,-3849),(1635,-3852)]).difference(p)
 B.planar('mp-asphalt',site,.12,True)
 approach=Polygon([(1677.6,-3908),(1682,-3907),(1682,-3864),(1677,-3864),(1676,-3883)])
 B.planar('mp-paving',approach.difference(p),.16,True)
 # Shallow cyan planters parallel the street, not an invented active storefront.
 for x,z,w,d in [(1678.7,-3898,1.8,6),(1678.2,-3890,1.8,3),(1680,-3885,.8,2.5)]:
  W.box('mp-turquoise-paint',(x,.43,z),(w,.54,d),True);W.box('mp-soil',(x,.708,z),(w-.18,.025,d-.18))
 for x in np.arange(1638,1655,2.8):W.box('mp-line-paint',(float(x),.135,-3880),(.06,.02,4.5))
 for z in np.arange(-3874,-3852,2.8):W.box('mp-line-paint',(1640,.135,float(z)),(4.5,.02,.06))
 for x,z in [(1650,-3903),(1654,-3897),(1663,-3900),(1668,-3892),(1660,-3890)]:
  W.box('mp-service-paint',(x,5,z),(1.3,.8,1.1));W.box('mp-vent',(x,5.42,z),(1.1,.04,.9))
 for x,z in [(1664,-3876),(1672,-3875)]:W.box('mp-service-paint',(x,7.15,z),(.7,.5,.7))
 # Existing sign frame is retained without obsolete business branding.
 S=Frame(B,1680,-3906,yaw=-math.pi/2,y=0)
 S.box('mp-post-paint',(0,4.3,0),(.38,8.4,.4),True);S.box('mp-fascia-paint',(0,7.8,0),(4.5,1.9,.35));S.box('mp-sign-paint',(0,8.15,-.19),(4.3,.9,.04));S.text('FOR SALE',(0,8,-.23),.42,'mp-white-letter')
 samples=[]
 for x in np.arange(1637,1682,1.2):
  for z in np.arange(-3911,-3852,1.2):
   pt=Point(x,z)
   if site.buffer(-.7).covers(pt) and not p.buffer(5).covers(pt) and pt.distance(Point(1680,-3906))>1:samples.append([float(x),.12,float(z)])
 Path('build/city-exteriors/main-1700-samples.json').write_text(json.dumps(samples))
 return dict(key=KEY,name='1700Main closed commercial exterior',center=[1663,0,-3889],bounds=[1634,-3915,1685,-3848],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
