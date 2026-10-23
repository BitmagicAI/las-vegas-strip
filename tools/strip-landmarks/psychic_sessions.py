"""3953 S Las Vegas Blvd. Dec2022 StreetView and owner sign photo.
Mapped plan preserved; height/sign dimensions are estimates, wear unresolved.
"""
from common import *
from forum_shops import facade_frame
KEY='psychicSessions'
def exterior(B):
 B.property=KEY+'-exterior';B.source='podium/shop';B.detail=0
 p=footprint('way/457939130');W=Frame(B,0,0,y=0)
 B.shell(p,.24,6.1,'ps-stucco',roof=False);B.planar('ps-roof',p,6.1,True)
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  G,L,_,_=facade_frame(B,a,b,p,.03)
  for y,h in [(3.12,.1),(5.98,.16),(6.15,.12)]:G.box('ps-trim',(L/2,y,-.08),(L+.15,h,.25))
  for u in np.arange(.18,L,.22):G.box('ps-dentil',(u,6.05,-.18),(.065,.1,.05))
  if a[0]<72 and b[0]<72:
   for u in [5.9,8.7]:
    G.box('ps-door',(u,1.4,-.07),(1.08,2.4,.13))
    G.box('ps-glass',(u,1.75,-.15),(.83,1.5,.035))
    for dx in [-.59,.59]:G.box('ps-trim',(u+dx,1.45,-.18),(.08,2.5,.09))
    G.box('ps-metal',(u-.36,1.35,-.2),(.035,.25,.04))
   for u,w in [(2.9,2.6),(11.5,2.5)]:
    G.box('ps-glass',(u,1.95,-.08),(w,1.5,.12))
    for dx in [-w/2,0,w/2]:G.box('ps-frame',(u+dx,1.95,-.16),(.055,1.6,.07))
    for y in [1.18,2.72]:G.box('ps-frame',(u,y,-.16),(w+.1,.06,.08))
    G.box('ps-sill',(u,1.1,-.22),(w+.2,.12,.4))
   # Paired signboards occupy the southern portion of the parapet.
   G.box('ps-burgundy',(6,4.6,-.18),(6.6,2.35,.27))
   G.box('ps-sign-paint',(6,4.6,-.335),(4.1,2.13,.035))
   G.text('PSYCHIC SESSIONS',(6,5.25,-.38),.34,'ps-red')
   G.text('PALM AND CARD READINGS',(6,3.91,-.38),.18,'ps-ink')
   for center in [5.25,6.75]:
    pts=[(center+.58*math.cos(t),4.63+.22*math.sin(t),-.39) for t in np.linspace(0,math.tau,33)];G.path('ps-ink',pts,.025,5)
    G.path('ps-ink',[(center+.16*math.cos(t),4.63+.16*math.sin(t),-.4) for t in np.linspace(0,math.tau,25)],.035,5)
    for j in range(5):G.tube('ps-ink',(center-.4+j*.2,4.82,-.39),(center-.45+j*.22,4.96,-.39),.018,5)
   for u in [3.25,8.75]:
    G.box('ps-purple',(u,4.6,-.34),(1,2.13,.04))
    for yy,rr in [(4.1,.19),(5.1,.22)]:
     pts=[(u+rr*(1 if k%2==0 else .42)*math.sin(k*math.pi/5),yy+rr*(1 if k%2==0 else .42)*math.cos(k*math.pi/5),-.39) for k in range(11)]
     G.path('ps-blue',pts,.022,5)
    G.path('ps-gold',[(u+.28*math.cos(t),4.62+.28*math.sin(t),-.39) for t in np.linspace(-1.5,1.5,20)],.026,5)
   G.box('ps-burgundy',(6,3.34,-.65),(7.5,.66,1.2),True)
   G.box('ps-sign-paint',(6,3.34,-1.265),(7.3,.5,.04))
   G.text('PSYCHIC READINGS',(6,3.34,-1.31),.43,'ps-red')
   for u in np.arange(2.4,9.7,.18):G.box('ps-bulb',(u,3.03,-1.28),(.045,.045,.04))
   G.text('PSYCHIC',(11.5,2.52,-.2),.25,'ps-white')
   G.text('OPEN',(2.9,2.17,-.2),.3,'ps-red')
   # Painted security panel, rainpipe and entry lamps.
   G.box('ps-panel',(1.2,1.7,-.08),(1.25,2.05,.14))
   for u in [1,14.7]:G.box('ps-metal',(u,2.8,-.24),(.18,.28,.28))
  else:
   for u in np.arange(3,L-1,5):
    G.box('ps-joint',(u,1.6,-.035),(.02,2.9,.018))
   if L>17:
    G.box('ps-service',(L*.7,1.4,-.08),(1,2.3,.12))
    G.box('ps-vent',(L*.3,2,-.1),(1.2,.8,.15))
    for y in np.arange(1.65,2.4,.08):G.box('ps-metal',(L*.3,y,-.2),(1.08,.025,.03))
 for x,z in [(77,2655),(86,2661)]:W.box('ps-metal',(x,6.47,z),(1.5,.64,1.2))
 # Forecourt ends before Nirvana's existing apron; no overlapping pavement.
 site=box(35,2647,96,2677.5).difference(p.buffer(.1))
 for x in range(35,96,3):
  for z in range(2647,2678,3):B.planar('ps-asphalt',site.intersection(box(x,z,x+3,z+3)),.26,True)
 for z in np.arange(2652,2666,2.8):W.box('ps-line',(67.6,.275,z),(5,.015,.07))
 W.box('ps-paving',(69.7,.31,2658.5),(2.6,.1,16),True)
 # Low security rail beside northern window, kept off the door approach.
 for z in np.arange(2652,2655.4,.17):W.box('ps-frame',(68.7,.85,z),(.025,1.08,.025))
 W.box('ps-frame',(68.7,1.4,2653.6),(.06,.055,3.4),True)
 return dict(key=KEY,name='Psychic Sessions frontage',center=[78,0,2658],bounds=[34,2646,97,2678],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
