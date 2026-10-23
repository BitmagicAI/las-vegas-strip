"""Former Jackalope bar, February2026 Street View. Tall pylon absent in this view."""
from common import *
from forum_shops import facade_frame
KEY='laughingJackalope'
def exterior(B):
 B.property=KEY+'-exterior';B.source='podium/former-bar';B.detail=0
 p=footprint('way/457939128');F=Frame(B,39.55,2789.43,math.pi/2,y=.32)
 solid=p.intersection(box(38,2764,60,2782));arcade=p.difference(solid)
 B.shell(solid,.32,5.7,'lj-stucco',roof=False);B.planar('lj-roof',p,5.7,True);B.planar('lj-soffit',arcade,5.35,True)
 # Front wall with boarded double doors and shallow arched surrounds.
 for u in [10.2,17.1,22.1]:
  F.box('lj-shadow',(u,1.8,-.11),(1.5,2.7,.12));F.box('lj-board',(u,1.8,-.2),(1.37,2.57,.08))
  for dx in [-.4,0,.4]:F.box('lj-board-joint',(u+dx,1.8,-.25),(.018,2.56,.02))
  F.arch(u,-.28,1.75,3.45,'lj-trim',.07,.42)
  if u!=17.1:
   for y in [1,1.55,2.05,2.5]:
    F.box('lj-poster',(u+.08*math.sin(y*20),y,-.27),(.85,.32,.025));F.box('lj-poster-ink',(u,y+.03,-.29),(.7,.045,.015))
 # Central classical door surround: true projecting pediment and engaged piers.
 for u in [15.7,18.5]:F.box('lj-trim',(u,1.9,-.35),(.24,3.4,.48))
 F.box('lj-trim',(17.1,3.61,-.37),(3.3,.22,.62))
 for x in [-1.7,1.7]:F.path('lj-gray',[(17.1+x,3.8,-.5),(17.1,4.8,-.5)],.12,8)
 B.face('lj-trim',[F.p(15.4,3.8,-.42),F.p(18.8,3.8,-.42),F.p(17.1,4.8,-.42)])
 # Narrow raised central pier, canopy and round-headed blind niche.
 F.box('lj-stucco',(10.2,3.3,-.25),(1.8,6.6,.5),True)
 F.box('lj-trim',(10.2,6.65,-.25),(2.1,.2,.66))
 F.box('lj-recess',(10.2,1.8,-.54),(1.2,2.6,.08));F.arch(10.2,-.62,1.2,3.4,'lj-trim',.07,.45)
 F.box('lj-trim',(10.2,3.7,-.6),(2.2,.15,1.2))
 for a,b in [((-1.1,-1.3),(1.1,-1.3)),((1.1,-1.3),(1.1,0)),((1.1,0),(-1.1,0)),((-1.1,0),(-1.1,-1.3))]:B.face('lj-metal-roof',[F.p(10.2+a[0],3.8,a[1]),F.p(10.2+b[0],3.8,b[1]),F.p(10.2,4.35,-.65)])
 # Blank weathered marquees: the 2026 photograph has no readable tenant lettering.
 for u,w in [(17.3,11),(3.4,5.8)]:
  F.box('lj-gold',(u,5.1,-.23),(w,.9,.18));F.box('lj-sign-paint',(u,5.1,-.34),(w-.22,.68,.06))
  for dx in np.arange(-w/2+.1,w/2,.24):
   for y in [4.72,5.48]:F.box('lj-bulb',(u+dx,y,-.35),(.055,.055,.055))
 # South arcade: open arched spandrels and real clearance underneath.
 def arched_wall(G,length,count):
  panel=box(0,0,length,5.4);step=length/count
  for i in range(count):
   mid=(i+.5)*step;w=step-.7;r=w/2
   opening=Polygon([(mid-r,-.1),(mid+r,-.1)]+[(mid+r*math.cos(a),2.25+1.0*math.sin(a)) for a in np.linspace(0,math.pi,33)])
   panel=panel.difference(opening)
  for t in triangles(panel):
   q=list(t.exterior.coords)[:-1]
   for z in [-.35,.35]:B.face('lj-stucco',[G.p(x,y,z) for x,y in q],True)
  for ring in [panel.exterior,*panel.interiors]:
   for a,b in zip(list(ring.coords),list(ring.coords)[1:]):
    B.face('lj-stucco',[G.p(*a,-.35),G.p(*b,-.35),G.p(*b,.35),G.p(*a,.35)],True)
  for i in range(count+1):
   u=i*step;G.box('lj-trim',(u,.18,0),(.74,.36,.6),True)
   for y in np.arange(.65,2.6,.5):G.box('lj-joint',(u,y,-.37),(.68,.025,.025))
 arched_wall(Frame(B,39.55,2789.43,math.pi/2,y=.32),7.43,1)
 arched_wall(Frame(B,58.75,2789.43,math.pi,y=.32),19.2,3)
 # Flat side/rear service facades remain distinct from the street arcade.
 for a,b in zip(list(solid.exterior.coords),list(solid.exterior.coords)[1:]):
  G,L,_,_=facade_frame(B,a,b,solid,.32)
  if a[0]<40 and b[0]<40:continue
  G.box('lj-trim',(L/2,5.3,-.04),(L,.18,.15))
  for u in np.arange(2,L-1,4):G.box('lj-joint',(u,2.6,-.035),(.024,5.1,.02))
  if L>8:G.box('lj-door',(L*.55,1.2,-.08),(1,2.35,.1))
 W=Frame(B,0,0,y=0)
 for x,z in [(47,2770),(53,2776)]:W.box('lj-metal',(x,6,z),(1.4,.6,1.1))
 # Corner quoins and expansion joints ground the masonry proportions.
 for u in [0,23.8]:
  for y in np.arange(.55,5.5,.48):F.box('lj-trim',(u,y,-.4),(.48,.42,.22))
 # Keep mapped street kerb; local apron links portico and side access.
 site=box(34,2763,64,2795).difference(solid)
 for x in range(34,64,3):
  for z in range(2763,2795,3):B.planar('lj-paving',site.intersection(box(x,z,x+3,z+3)),.34,True)
 return dict(key=KEY,name='Former Laughing Jackalope bar exterior',center=[49,0,2777],bounds=[33,2762,65,2796],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
