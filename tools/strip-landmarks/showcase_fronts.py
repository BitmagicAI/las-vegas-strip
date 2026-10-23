"""Older Showcase architecture, fitted to mapped western frontage.
Guitar panel silhouette follows the official Hard Rock exterior photograph.
Sign dimensions and relief depths are photographic estimates, not survey values.
"""
from common import *

def north_front(B):
 B.source='podium/north'; F=Frame(B,35.7,1305,math.pi/2,y=.24)
 # Three-floor Hard Rock south half: opaque blue upper frame around a recessed window.
 for u,v,y,h in [(-14,22,17.2,1.8),(-14,22,9.8,1.3),(-24.5,1,13.5,6.5),(-3.5,1,13.5,6.5)]:
  F.box('sc-blue-paint',(u,y,-.65),(v,h,.35))
 F.box('ph-glass',(-14,13.5,-.48),(20,5.8,.10))
 for x in np.arange(-23,-4,2.2):F.box('ph-metal',(x,13.5,-.75),(.07,5.8,.12))
 F.text('Hard Rock Cafe',(-14,19.05,-.8),1.65,'sc-gold-paint')
 # Smooth closed guitar-body outline with six rising strings, as on the real sign.
 outline=[(-5,5),(-7,8),(-7.6,11),(-6.8,14),(-4.5,16),(-2.5,18),(-1.4,20),(-.4,20.8),(.2,19),(1.5,17.8),(3.7,17.3),(5.5,17.8),(5.2,15.3),(3.7,13.8),(3.3,11.5),(4.6,8.5),(3.1,5.6),(1.5,3.8),(-1.8,4.5)]
 smooth=[]
 for i,p1 in enumerate(outline):
  p0=outline[i-1];p2=outline[(i+1)%len(outline)];p3=outline[(i+2)%len(outline)]
  for t in np.linspace(0,1,5,endpoint=False):
   smooth.append(tuple(.5*((2*p1[k])+(-p0[k]+p2[k])*t+(2*p0[k]-5*p1[k]+4*p2[k]-p3[k])*t*t+(-p0[k]+3*p1[k]-3*p2[k]+p3[k])*t*t*t) for k in range(2)))
 poly=Polygon(smooth).buffer(0)
 for tri in triangles(poly):
  B.face('sc-blue-paint',[F.p(x, y,-1.5) for x,y in list(tri.exterior.coords)[:-1]])
 ps=list(poly.exterior.coords)
 for a,b in zip(ps,ps[1:]):B.face('sc-rim-paint',[F.p(a[0],a[1],-.7),F.p(b[0],b[1],-.7),F.p(b[0],b[1],-1.5),F.p(a[0],a[1],-1.5)])
 F.path('ph-silver',[(x,y,-1.55) for x,y in ps],.065,8)
 # Fine diamond relief retains the metallic skin rather than a flat blue decal.
 B.detail=1
 for y in np.arange(5,20,.48):
  for x in np.arange(-7,5,.48):
   q=Polygon([(x,y+.17),(x+.17,y),(x,y-.17),(x-.17,y)])
   if poly.contains(q):B.face('sc-blue-relief',[F.p(xx,yy,-1.56) for xx,yy in list(q.exterior.coords)[:-1]])
 B.detail=0
 for i in range(6):F.tube('ph-letter',(-1.1+i*.28,18.2,-1.6),(1.4+i*.28,24,-1.6),.045,6)
 F.path('ph-letter',[(.2+3.0*math.cos(a),10.9+3.0*math.sin(a),-1.68) for a in np.linspace(0,math.tau,65)],.08,8)
 F.text('Hard Rock',(.2,11.3,-1.8),1.28,'ph-letter');F.text('CAFE',(.2,9.65,-1.8),.9,'ph-letter')
 F.box('ph-led-blue',(15,12.6,-.4),(19,3.5,.4));F.text('ROSS',(15,12.7,-.65),2.3,'ph-letter')
 F.text('DRESS FOR LESS',(15,10.3,-.65),.55,'ph-letter')
 # Distinct low shop fascia; glass behind the shared existing city exterior only.
 for u,w,label in [(-16,10,'ABC STORES'),(-4,10,'ROCK SHOP'),(15,17,'ROSS')]:
  F.box('sc-rim-paint',(u,4.6,-.8),(w,1.05,.4));F.text(label,(u,4.65,-1.05),.7,'ph-letter')
  for dx in [-w*.3,w*.3]:
   F.box('ph-black',(u+dx,1.9,-.35),(2.3,3.8,.1))
   for j in [-1.15,0,1.15]:F.box('ph-silver',(u+dx+j,1.9,-.48),(.07,3.8,.1))
   F.box('ph-silver',(u+dx,3.8,-.48),(2.4,.08,.1))
 F.box('ph-metal',(0,5.2,-1),(51,.2,2.2))
