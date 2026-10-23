"""Pinball Hall of Fame exterior. July2021 and June2026 reference photos.
Mapped warehouse retained, original polygon lettering and sign construction.
"""
from common import *
from forum_shops import facade_frame
KEY='pinballHall'

def letter_shape(c):
 stem=box(0,0,.23,1)
 if c=='I':return box(.18,0,.41,1)
 if c=='L':return stem.union(box(0,0,.70,.2))
 if c=='N':return unary_union([stem,box(.52,0,.75,1),Polygon([(.14,1),(.34,1),(.64,0),(.43,0)])])
 if c=='A':return Polygon([(0,0),(.25,1),(.51,1),(.76,0),(.53,0),(.48,.22),(.27,.22),(.22,0)],holes=[[(.32,.42),(.44,.42),(.38,.71)]]).buffer(0)
 if c in 'PB':
  top=box(.1,.48,.43,1).union(scale(Point(.43,.74).buffer(.26,resolution=16),xfact=1.1,yfact=1,origin=(.43,.74)))
  top=top.difference(box(.23,.66,.44,.82))
  if c=='P':return stem.union(top)
  low=box(.1,0,.43,.55).union(scale(Point(.43,.265).buffer(.265,resolution=16),xfact=1.1,yfact=1,origin=(.43,.265)))
  return stem.union(top).union(low.difference(box(.23,.17,.45,.36)))
 raise ValueError(c)

def bold_word(B,F,word,width,height,y,z,mat):
 gap=.08;glyphs=[letter_shape(c) for c in word];extent=sum(g.bounds[2]-g.bounds[0] for g in glyphs)+gap*(len(word)-1);k=width/extent;x=-width/2
 for g in glyphs:
  lo=g.bounds[0];w=g.bounds[2]-lo
  for t in triangles(g):B.face(mat,[F.p(-(x+(u-lo)*k),y+v*height,z) for u,v in list(t.exterior.coords)[:-1]])
  x+=(w+gap)*k

def exterior(B):
 B.property=KEY+'-exterior';B.source='podium/warehouse';B.detail=0
 p=footprint('way/1038023891');ps=list(p.exterior.coords)
 for a,b in zip(ps,ps[1:]):
  if math.dist(a,b)<.3:continue
  F,L,nx,nz=facade_frame(B,a,b,p,.16)
  F.box('pb-gray',(L/2,3.1,0),(L,5.9,.12))
  for u in np.arange(4,L,4):F.box('pb-joint',(u,3.1,-.08),(.014,5.85,.02))
  F.box('pb-white',(L/2,6.15,-.06),(L,.18,.3))
 B.planar('pb-roof',p,6.3)
 # West front facing the parking lot. 40ft upper signage is planning-derived;
 # supporting ground story is estimated from the dated photograph.
 F=Frame(B,160.6,3472.35,math.pi/2,y=0)
 F.box('pb-white',(0,9.25,-.5),(37.2,12.2,1.2),True)
 bold_word(B,F,'PINBALL',35.5,10.9,3.9,-1.12,'pb-red')
 F.text('4925',(-16.4,14,-1.13),.43,'pb-charcoal')
 for x in [-2.8,-1.4,0,1.4,2.8]:
  F.box('pb-glass',(x,1.65,-.1),(1.32,2.75,.12))
  F.box('pb-metal',(x-.69,1.65,-.22),(.07,2.85,.16))
 F.box('pb-metal',(0,3.05,-.22),(7,.12,.18))
 for x in [-.15,.15]:F.tube('pb-metal',(x,1,-.3),(x,1.8,-.3),.025,8)
 for x in [-8,8,15]:F.box('pb-charcoal',(x,1.5,-.08),(1.25,2.6,.08))
 # Infilled subgrade below existing mapped drives and sidewalks.
 B.source='podium/forecourt';B.planar('hd-asphalt',box(48,3436,238,3505),-.12,True)
 # June2026 pylon: blue cylinder, red blade, round vertical letter medallions.
 B.source='podium/roadside-sign'
 B.lathe('pb-blue',(57,3440),[(0,.7),(21.5,.7)],24)
 B.box('pb-blue',(57,10.75,3440),(.9,21.5,.9),True)
 for yaw in [0,math.pi]:
  F=Frame(B,62,3440,yaw,y=0)
  if yaw==0:F.box('pb-red',(0,14.4,0),(9.5,7.1,.65))
  F.box('pb-charcoal',(0,7.8,-.1),(8,4.3,.7))
  F.box('pb-blue',(0,7.8,-.49),(7.6,3.9,.05))
  F.text('PLAY PINBALL',(0,8.1,-.54),.65,'pb-white')
  F.text('HALL OF FAME',(0,6.9,-.54),.42,'pb-white')
  F.text('HALL OF',(0,15.6,-.36),1.2,'pb-white')
  F.text('FAME',(0,13.8,-.36),1.6,'pb-white')
  # Arrow edge and repeating bulbs are near detail, solid blade is permanent.
  pts=[(-5.8,10.8),(-4,9.6),(4.9,9.6),(5.7,10.8),(4.9,11.8),(-4,11.8)]
  B.face('pb-yellow',[F.p(x,y,-.41) for x,y in pts][::-1])
  for i,c in enumerate('PINBALL'):
   y=20.2-i*1.95;x=-5 if yaw==0 else 5
   F.tube('pb-blue',(x,y,0),(x,y,-.85),1.02,32)
   circle=[F.p(x+1.02*math.cos(a),y+1.02*math.sin(a),-.9) for a in np.linspace(0,math.tau,33)[:-1]]
   B.face('pb-blue',circle[::-1])
   circle=[F.p(x+.88*math.cos(a),y+.88*math.sin(a),-.92) for a in np.linspace(0,math.tau,33)[:-1]]
   B.face('pb-white',circle[::-1])
   F.text(c,(x,y-.56,-.97),1.5,'pb-blue')
  B.detail=1
  for x in np.arange(-4.5,4.6,.35):
   for y in [11,17.7]:F.box('pb-yellow',(x,y,-.38),(.06,.06,.06))
  B.detail=0
 return dict(key=KEY,name='Pinball Hall of Fame exterior',center=[160,0,3472],bounds=[48,3436,238,3505],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
