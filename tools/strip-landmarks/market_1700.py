"""White Cross Market: closed blue/white frontage observed January2026."""
from common import *
from forum_shops import facade_frame
KEY='market1700'
def exterior(B):
 B.property=KEY+'-exterior';B.source='podium/market';B.detail=0;W=Frame(B,0,0,y=0)
 p=footprint('way/316303724');B.shell(p,.18,4.45,'mk-blue-paint',roof=False);B.planar('mk-roof-paint',p,4.3,True)
 front=None
 for a,b in zip(list(p.exterior.coords),list(p.exterior.coords)[1:]):
  G,L,nx,nz=facade_frame(B,a,b,p,.045)
  G.box('mk-blue-paint',(L/2,4.5,-.05),(L,.2,.25))
  if nx>.8:
   front=G, L
   # Broad corrugated fascia over boarded shop openings.
   G.box('mk-peeling-white-paint',(L/2,3.55,-.48),(L,1.7,.85))
   for u in np.arange(.15,L,.31):G.box('mk-panel-joint-paint',(float(u),3.55,-.92),(.025,1.66,.035))
   G.box('mk-blue-paint',(L/2,4.49,-.55),(L+.2,.23,1.1))
   for u in np.arange(.75,L,3.4):
    G.box('mk-board-paint',(float(u),1.7,-.1),(3.2,2.05,.13))
    for y in [.85,1.5,2.2]:G.box('mk-blue-shadow-paint',(float(u),y,-.18),(3.18,.018,.02))
   for u in np.arange(0,L+.1,7.5):
    G.box('mk-peeling-white-paint',(float(u),1.5,-.65),(.16,2.7,.16),True)
    G.tube('mk-metal-paint',(float(u),2.15,-.65),(float(u),2.76,-1),.025,8)
   G.box('mk-blue-paint',(L/2,.35,-1.25),(L,.34,2.5),True)
   G.box('mk-paving',(L/2,.53,-1.25),(L,.06,2.5),True)
   # Permanent black handrail. Temporary site fence remains visible and physically closed.
   for y in [.65,1.52]:G.tube('mk-black-paint',(.1,y,-2.4),(L-.1,y,-2.4),.025,8)
   for u in np.arange(.15,L,1.8):G.tube('mk-black-paint',(float(u),.5,-2.4),(float(u),1.55,-2.4),.026,8)
   for u in np.arange(.1,L,3):
    G.tube('mk-metal-paint',(float(u),.55,-2.3),(float(u),2.2,-2.3),.025,8)
    G.tube('mk-metal-paint',(float(u),2.2,-2.3),(min(L,float(u)+3),2.2,-2.3),.025,8)
   # Mesh wire is real thin geometry, clipped to panel boundaries; no opaque blocking visual sheet.
   for u in np.arange(.1,L,.38):
    for slope in [-1,1]:
     end=min(L,max(.1,float(u)+slope*1.65));height=.55+abs(end-float(u))
     if abs(end-float(u))<.001:continue
     G.tube('mk-wire-paint',(float(u),.55,-2.3),(end,height,-2.3),.007,4)
   B.face('mk-collision',[G.p(0,.5,-2.3),G.p(L,.5,-2.3),G.p(L,2.2,-2.3),G.p(0,2.2,-2.3)],True)
   # Major surviving sign layout, no fabricated active-tenant claim or personal telephone number.
   G.text('MARKET',(L*.53,3.02,-.99),1.04,'mk-blue-letter')
   G.box('mk-red-sign-paint',(L*.17,3.6,-.99),(6.6,1.05,.08));G.text('LIQUOR',(L*.17,3.55,-1.05),.62,'mk-white-letter');G.text('FINE WINE  CRAFT BEER',(L*.17,3.25,-1.05),.22,'mk-white-letter')
   G.box('mk-green-sign-paint',(L*.8,3.55,-.99),(5.2,.95,.08));G.text('FOR SALE',(L*.8,3.32,-1.06),.5,'mk-white-letter')
   G.text('1700',(1,2.96,-1),.31,'mk-blue-letter')
   # Roof sign: narrow mast and suspended White Cross Market board.
   u=L*.52;G.tube('mk-metal-paint',(u,4.5,-.15),(u,8.55,-.15),.075,10)
   G.box('mk-white-paint',(u,6.1,-.15),(2.1,1.25,.18));G.text('WHITE CROSS',(u,6.14,-.27),.23,'mk-blue-letter');G.text('MARKET',(u,5.74,-.27),.3,'mk-blue-letter')
   G.box('mk-green-sign-paint',(u,8,-.15),(1.3,1.55,.2));G.text('MARKET',(u,7.9,-.28),.22,'mk-white-letter')
   for uu in np.arange(1,L,7):G.path('mk-metal-paint',[(float(uu),4.65,.3),(float(uu),5,-.8),(float(uu),4.65,-1.5)],.025,8)
  elif L>8:
   G.box('mk-service-paint',(L*.6,1.45,-.08),(1.2,2.5,.12));G.box('mk-vent',(L*.25,2.8,-.1),(1.1,.5,.14))
 if front:
  G,L=front
  # Northern steps have yellow nosings but remain behind the closed site's fence.
  for j in range(3):
   G.box('mk-step',(1,.18+(j+.5)*.12,-2.75+j*.3),(3,.12,.3),True)
   G.box('mk-yellow-paint',(1,.18+(j+1)*.12+.008,-2.88+j*.3),(3,.016,.045))
 B.groups={k:g for k,g in B.groups.items() if g['material']!='mk-collision'}
 for x,z in [(1781,-3876),(1790,-3873)]:W.box('mk-service-paint',(x,4.65,z),(1.4,.7,1.8))
 # Public outside approach; fenced property is not marked as an accessible interior.
 G,L=front
 B.upface('mk-paving',[G.p(0,.18,-2.55),G.p(L,.18,-2.55),G.p(L,.18,-4.1),G.p(0,.18,-4.1)],True)
 samples=[list(G.p(float(u),.18,-3.25)) for u in np.arange(.5,L-.4,.75)]
 Path('build/city-exteriors/market-1700-samples.json').write_text(json.dumps(samples))
 return dict(key=KEY,name='White Cross Market exterior',center=[1791,0,-3870],bounds=[1772,-3887,1817,-3849],structural=True,exteriorOnly=True,portals=[],zones=[],lights=[],routes=[],hotelSources=[],views={})
