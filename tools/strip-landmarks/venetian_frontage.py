"""Photograph-guided Venetian street palazzi and campanile, Oct 9 2026.
Source: archived Expedia frontage photograph. Dimensions inherited or estimated.
Decorative relief is simplified, not a scan. Shared static material/detail batches.
"""
import math
import numpy as np
from shapely.geometry import Point,LineString
from common import Frame,footprint,parts

def campanile(B):
 c=footprint('way/43875964').centroid;cx,cz=c.x,c.y
 B.source='campanile';B.detail=0;T=Frame(B,cx,cz,y=0)
 T.box('campanile-brick',(0,33,0),(15,66,15),True)
 T.box('ivory',(0,3,0),(17,6,17),True)
 # The substantial ornamented loggetta/base and roof balustrade.
 for side in range(4):
  J=Frame(B,cx,cz,side*math.pi/2,y=0)
  for x in [-6.6,-3.3,0,3.3,6.6]:
   J.box('campanile-brick-light',(x,35,-7.61),(.40,56,.26))
   J.arch(x,-7.69,2.5,65.35,'ivory',.13,64.2)
  for y in [1.0,5.5,6.0,9.0,9.45,65.6,66.1,69.5,78.0,78.5,82.1]:
   J.box('ivory',(0,y,-8.02),(16.9,.32,.70))
  for x in [-6,-3,0,3,6]:
   J.box('darkglass',(x,2.65,-8.55),(1.8,3.6,.08));J.arch(x,-8.65,2.05,4.8,'ivory',.12,.9)
   J.lathe('ivory',x-1.25,-8.65,[(.3,.20),(.5,.27),(4.85,.17),(5.12,.32),(5.32,.32)],12)
   J.box('campanile-brick',(x,7.5,-8.13),(2.8,2.4,.08))
   J.box('ivory',(x,7.5,-8.20),(2.48,2.08,.07));J.box('plaster',(x,7.5,-8.25),(2.17,1.75,.035))
   B.detail=1
   # Low-relief rosettes, not a claim to replicate the original sculpture.
   for a in np.arange(0,math.tau,math.pi/4):
    J.path('ivory',[(x,7.5,-8.31),(x+.62*math.cos(a),7.5+.62*math.sin(a),-8.32)],.07,5)
   B.detail=0
  for x in np.arange(-8,8.1,.42):J.lathe('ivory',x,-8.12,[(9.6,.07),(10,.12),(10.45,.065)],8)
  J.box('ivory',(0,10.55,-8.12),(16.8,.16,.23))
  # Narrow arched shaft windows on the reference tower.
  for y in [15,24,33,42,51]:
   J.box('darkglass',(-4.9,y,-7.54),(.67,1.55,.05));J.arch(-4.9,-7.64,.81,y+1.15,'ivory',.10,y-.78)
  J.box('ivory',(0,67.7,-7.67),(15.6,3,.40))
  # Open belfry: dark backing recessed behind dimensional columns and arches.
  J.box('darkglass',(0,73.8,-6.3),(13.5,7.5,.10))
  for x in [-5.4,-1.8,1.8,5.4]:
   J.arch(x,-7.65,3.15,77.25,'ivory',.21,70.0)
  for x in [-7.2,-3.6,0,3.6,7.2]:
   J.lathe('ivory',x,-7.65,[(69.7,.30),(70,.38),(75.35,.25),(75.65,.44),(75.95,.44)],16)
  J.box('campanile-brick',(0,80.35,-7.1),(14.3,3.1,.25))
  for x in [-6.9,6.9]:J.box('ivory',(x,80.35,-7.29),(.34,3.4,.34))
  # Recessed attic relief panel; figurative lion remains a separate refinement.
  J.box('plaster',(0,80.25,-7.28),(7.3,1.85,.08))
  for y in [79.25,81.25]:J.box('ivory',(0,y,-7.39),(7.7,.14,.14))
 T.box('ivory',(0,82.25,0),(15.8,.5,15.8))
 corners=[(-7.7,-7.7),(7.7,-7.7),(7.7,7.7),(-7.7,7.7)]
 for (x,z),(xx,zz) in zip(corners,corners[1:]+corners[:1]):
  B.face('campanile-patina',[T.p(x,82.5,z),T.p(xx,82.5,zz),T.p(0,94,0)])
  T.tube('ivory',(x,82.5,z),(0,94,0),.15,6)
  B.detail=1
  for y in np.arange(83,94,.38):
   t=(94-y)/11.5;T.tube('campanile-patina',(x*t,y,z*t),(xx*t,y,zz*t),.025,4)
  B.detail=0
 T.lathe('gold',0,0,[(94,.13),(94.3,.24),(94.6,.11),(95.7,0)],12)

def palazzi(B):
 for ident in ['way/33996627','way/543728945','way/115776190']:
  poly=footprint(ident);B.source='palazzo-front';B.detail=0
  from venetian_rialto import START,END
  yaw=math.atan2(END[0]-START[0],END[1]-START[1])
  opening=dict(p=[START[0],.24,START[1]],yaw=yaw,width=8.2,height=5.5)
  B.shell(poly,.24,13.5,'plaster',[opening] if ident=='way/543728945' else [])
  for q in parts(poly):
   for a,b in zip(list(q.exterior.coords),list(q.exterior.coords)[1:]):
    L=math.dist(a,b)
    if L<1:continue
    ux,uz=(b[0]-a[0])/L,(b[1]-a[1])/L;nx,nz=-uz,ux
    if q.contains(Point((a[0]+b[0])/2+nx*.1,(a[1]+b[1])/2+nz*.1)):nx,nz=-nx,-nz
    F=Frame(B,a[0]+nx*.13,a[1]+nz*.13,math.atan2(-nx,-nz),y=0)
    if F.co*ux-F.si*uz<0:F=Frame(B,b[0]+nx*.13,b[1]+nz*.13,F.yaw,y=0)
    entryEdge=ident=='way/543728945' and Point(*START).distance(LineString([a,b]))<.1
    cols=max(1,round(L/4.0));cw=L/cols
    for y,h,d in [(.5,.4,.35),(4.55,.32,.48),(8.85,.42,.55),(12.9,.25,.50),(13.35,.4,.8)]:
     if not (entryEdge and y<5.6):F.box('ivory',(L/2,y,-d/2),(L,h,d))
    for j in range(cols):
     x=(j+.5)*cw
     for y,top in [(1.0,4.1),(5.0,8.35),(9.3,12.45)]:
      if entryEdge and y<5.6:continue
      w=cw*.64
      F.box('darkglass',(x,(y+top)/2,-.08),(w,top-y,.06))
      F.arch(x,-.22,w+.13,top,'ivory',.10,y)
      for s in [-1,1]:
       F.lathe('ivory',x+s*cw*.43,-.25,[(y-.25,.16),(y,.23),(top-.45,.13),(top-.2,.26)],10)
      F.box('ivory',(x,y-.18,-.27),(cw*.84,.19,.56))
      B.detail=1
      F.box('champagne',(x,(y+top)/2,-.16),(.055,top-y,.06))
      F.box('champagne',(x,top-.8,-.16),(w,.055,.06))
      if y>4:
       for xx in np.arange(x-w/2,x+w/2,.26):F.lathe('ivory',xx,-.53,[(y-.03,.045),(y+.33,.08),(y+.58,.045)],8)
       F.box('ivory',(x,y+.64,-.53),(w+.3,.10,.17))
      B.detail=0
     # Parapet balusters remain at near detail, cornice keeps the skyline.
     B.detail=1
     for xx in np.arange(x-cw*.45,x+cw*.46,.38):F.lathe('ivory',xx,-.15,[(13.55,.055),(13.9,.10),(14.3,.055)],8)
     F.box('ivory',(x,14.36,-.15),(cw,.14,.23));B.detail=0
     # Recessed street-shop glazing with actual door/mullion scale and stone reveals.
     if not entryEdge and nx<-.3:
      ww=cw*.66
      for xx in [x-ww/2,x+ww/2]:F.box('palace-limestone',(xx,2.2,-.24),(.20,3.6,.30))
      F.box('palace-limestone',(x,.35,-.29),(ww+.30,.25,.42))
      F.box('blackiron',(x,1.85,-.17),(.055,2.9,.075))
      F.box('blackiron',(x,3.3,-.17),(ww,.065,.075))
      for side in [-1,1]:F.tube('brass',(x+side*.13,1.1,-.24),(x+side*.13,1.75,-.24),.022,8)
      # Red vertical museum banners are characteristic of the Strip palazzo.
      if ident=='way/33996627' and j%3==1:
       F.box('venetian-burgundy',(x,8.9,-.67),(cw*.60,5.3,.08))
       for k,word in enumerate(['MADAME','TUSSAUDS']):F.text(word,(x,10.0-k*.5,-.72),min(.36,cw*.095),'letter')
       F.text('LAS VEGAS',(x,7.1,-.72),.22,'letter')
       F.tube('blackiron',(x-cw*.38,11.66,-.65),(x+cw*.38,11.66,-.65),.045,8)
     # Reflected green/cream striped shop canopies seen in the street photograph.
     B.detail=1
     for k in range(0 if entryEdge else 14):
      xx=x-cw*.44+(k+.5)*cw*.88/14
      mat='ivory' if k%2 else 'bottle'
      pts=[F.p(xx-cw*.88/28,4.25,0),F.p(xx+cw*.88/28,4.25,0),F.p(xx+cw*.88/28,3.7,-1.35),F.p(xx-cw*.88/28,3.7,-1.35)]
      B.face(mat,pts)
     B.detail=0
