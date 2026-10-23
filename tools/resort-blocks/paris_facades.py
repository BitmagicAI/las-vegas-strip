"""Parisian arrival streetscape. Original mesh ornament; photograph-derived style.
All decoration shares static material/cell batches and adds no physics bodies.
The retained curved shell owns the collision and the central entrance opening.
"""
from common import *

def build(c,opera_mask):
 b,F,source,G=[c[k] for k in ['b','F','source','G']]
 cx,cz,r=126.8,482.0,46.2
 start=math.pi+.72
 # Small adjoining facades, not one giant pilastered hall. Architectural heights
 # are fitted estimates; the real resort is a theatrical Parisian streetscape.
 ends=np.linspace(start,math.tau,8)
 rises=[3.5,4.2,3.6,4.5,3.4,4.05,3.5]
 finishes=['paris-ashlar','paris-ivory','paris-ashlar','paris-rose','paris-ivory','paris-ashlar','paris-ivory']
 def pos(a,rr,y):return(cx+rr*math.cos(a),y,cz+rr*math.sin(a))
 def frame(a,rr=r-.10):
  x,_,z=pos(a,rr,0);return F(x,z,0,-a-math.pi/2)
 def strip(lo,hi,rr,y,w,h,mat):
  angles=np.linspace(lo,hi,max(3,math.ceil((hi-lo)*r/1.3)))
  poly=Polygon([(cx+(rr+w/2)*math.cos(a),cz+(rr+w/2)*math.sin(a)) for a in angles]+[(cx+(rr-w/2)*math.cos(a),cz+(rr-w/2)*math.sin(a)) for a in angles[::-1]])
  b.shell(poly.difference(opera_mask),y,y+h,mat,solid=False)
 def scroll(f,x,y,z,scale=.22):
  # Paired curled C motifs, each made of short shared iron tubes.
  for sign in [-1,1]:
   f.path('paris-iron',[(x+sign*scale*(.35+math.cos(t)),y+scale*math.sin(t),z) for t in np.linspace(-math.pi*.8,math.pi*.8,13)],.016,5)
 def balcony(f,x,y,w,depth=.62):
  f.box('paris-cream',(x,y-.08,depth/2),(w+.28,.18,depth+.2))
  for yy,thick in [(y+.15,.023),(y+.98,.035),(y+1.06,.05)]:f.tube('paris-iron',(x-w/2,yy,depth),(x+w/2,yy,depth),thick,6)
  for xx in np.linspace(x-w/2,x+w/2,max(3,round(w/.28))):f.tube('paris-iron',(xx,y+.13,depth),(xx,y+1.03,depth),.018,5)
  for xx in np.arange(x-w/2+.4,x+w/2,.65):scroll(f,xx,y+.56,depth+.025)
  for xx in [x-w/2,x+w/2]:
   f.path('paris-iron',[(xx,y+.1,.02),(xx,y+.1,depth),(xx,y+1.07,depth),(xx,y+1.07,.02)],.034,6)
   f.tube('paris-iron',(xx,y+.12,.1),(xx,y+1.04,.1),.022,5)
  for xx in [x-w*.3,x+w*.3]:f.path('paris-cream',[(xx,y-.7,.02),(xx,y-.33,.35),(xx,y-.14,depth-.1)],.095,6)
 def french_window(f,x,y,w,h,z=.12,style=0):
  # Opaque recessed-looking backing keeps unloaded interior geometry unnecessary.
  f.box('paris-window',(x,y+h/2,z),(w,h,.08))
  for s in [-1,1]:
   f.box('paris-cream',(x+s*(w/2+.12),y+h/2,z+.16),(.22,h+.30,.34))
   f.box('paris-iron',(x+s*(w/2-.04),y+h/2,z+.19),(.065,h,.07))
  for yy in [y-.08,y+h+.09]:f.box('paris-cream',(x,yy,z+.20),(w+.52,.18,.42))
  # Paired casements, six blue-grey panes, fine timber muntins, dark reveals.
  f.box('paris-ivory',(x,y+h/2,z+.22),(.07,h,.07))
  for yy in [y+h*.32,y+h*.66]:f.box('paris-ivory',(x,yy,z+.22),(w,.045,.07))
  if style==1:
   # Inset panelled shutters on selected houses, as in the resort's side returns.
   for s in [-1,1]:
    xx=x+s*(w/2+.48);f.box('paris-shutter',(xx,y+h/2,z+.06),(.44,h,.09))
    for yy in np.arange(y+.12,y+h-.05,.13):f.box('paris-copper',(xx,yy,z+.13),(.35,.045,.045))
  # Projecting molded lintel and keystone establish depth in grazing daylight.
  f.box('paris-cream',(x,y+h+.27,z+.30),(w+.72,.19,.52))
  f.box('paris-cream',(x,y+h+.42,z+.24),(.22,.42,.40))
 def awning(f,x,y,w,z=.12):
  top=y;front=y-.55;d=1.02
  b.face('paris-red',[f.p(x-w/2,top,z),f.p(x+w/2,top,z),f.p(x+w/2,front,z+d),f.p(x-w/2,front,z+d)])
  for xx in [x-w/2,x+w/2]:b.face('paris-red',[f.p(xx,top,z),f.p(xx,front,z+d),f.p(xx,front,z)])
  f.box('paris-red',(x,front-.12,z+d),(w,.24,.055))
  f.box('paris-cream',(x,front-.23,z+d+.035),(w,.035,.035))
  for xx in [x-w*.43,x+w*.43]:f.tube('paris-iron',(xx,front-.2,z),(xx,front-.1,z+d),.023,5)
 def dormer(f,x,y,arched):
  # Dormer stands ahead of the sloping roof, with enclosed cheeks and cap.
  f.box('paris-cream',(x,y+.9,-.08),(1.65,1.95,1.65))
  french_window(f,x,y+.12,1.01,1.50,.79)
  if arched:
   f.path('paris-cream',[(x+.98*math.cos(t),y+1.99+.6*math.sin(t),.91) for t in np.linspace(0,math.pi,17)],.12,6)
   # Close the curved pediment instead of floating decorative ribs.
   b.face('paris-stone',[f.p(x+.96*math.cos(t),y+1.99+.58*math.sin(t),.84) for t in np.linspace(0,math.pi,17)])
  else:
   for zz in [-.95,1.02]:b.face('paris-stone',[f.p(x-.98,y+1.98,zz),f.p(x+.98,y+1.98,zz),f.p(x,y+2.72,zz)])
   for dx in [-1,1]:b.face('paris-slate',[f.p(x,y+2.77,-.98),f.p(x+dx*1.07,y+1.96,-.98),f.p(x+dx*1.07,y+1.96,1.08),f.p(x,y+2.77,1.08)])
  f.lathe('paris-cream',x,0,[(y+2.60,.11),(y+2.93,.085),(y+3.09,.025)],8)
 # Tint existing curved wall triangles by adjoining house group. No overlapping
 # cladding surface, duplicated collision, or one runtime object per house.
 original=[(k,g) for k,g in b.groups.items() if g['source']=='arrival-louvre-shell' and g['material']=='paris-stone']
 for key,g in original:
  del b.groups[key]
  for ids in g['faces']:
   pts=[g['vertices'][j] for j in ids];xx=sum(q[0] for q in pts)/3;zz=sum(q[2] for q in pts)/3
   a=math.atan2(zz-cz,xx-cx)%math.tau;j=min(6,max(0,int((a-start)/(math.tau-start)*7)))
   b.face(finishes[j],pts)
 # Retain full-height shell in coarse LOD; silhouettes/balconies/awnings are
 # architectural masses, fine scrolls/casements can drop at long distance.
 for house,(lo,hi) in enumerate(zip(ends,ends[1:])):
  mat=finishes[house];eave=17.7;rise=rises[house]
  source('arrival-parisian-roofs')
  aa=np.linspace(lo,hi,17)
  # Mask the neighboring Opera mass consistently at every roof height.
  for a,z in zip(aa,aa[1:]):
   for ra,ya,rb,yb in [(45.85,eave,49,eave+rise),(49,eave+rise,52.7,eave+rise),(52.7,eave+rise,55.5,eave)]:
    quad=Polygon([(cx+rr*math.cos(t),cz+rr*math.sin(t)) for t,rr in [(a,ra),(z,ra),(z,rb),(a,rb)]])
    clipped=quad.difference(opera_mask)
    if clipped.is_empty:continue
    for poly in parts(clipped):
     for tri in triangles(poly):
      pts=[]
      for xx,zz in list(tri.exterior.coords)[:-1]:
       rr=math.hypot(xx-cx,zz-cz);yy=ya+(yb-ya)*(rr-ra)/(rb-ra);pts.append((xx,yy,zz))
      b.face('paris-slate',pts)
  # Each shared roof join has one owner and only its exposed height step.
  # Two full-height gables on the same plane would shimmer at the seams.
  boundaries=[(hi,rises[house+1] if house<6 else 0)]
  if house==0:boundaries.append((lo,0))
  for angle,neighbor_rise in boundaries:
   for ra,rb in [(45.85,49),(49,52.7),(52.7,55.5)]:
    fa=1 if ra in [49,52.7] else 0;fb=1 if rb in [49,52.7] else 0
    lower,upper=min(rise,neighbor_rise),max(rise,neighbor_rise)
    if not opera_mask.contains(Point(cx+50*math.cos(angle),cz+50*math.sin(angle))):
     b.face('paris-slate',[pos(angle,ra,eave+lower*fa),pos(angle,rb,eave+lower*fb),pos(angle,rb,eave+upper*fb),pos(angle,ra,eave+upper*fa)])
  for y,w,h in [(5.9,.46,.2),(6.32,.66,.16),(11.45,.46,.18),(16.55,.38,.16),(17.1,.7,.22),(17.55,1.05,.22)]:strip(lo,hi,r-.14,y,w,h,'paris-cream')
  # Boundary quoins plus narrow stone coursing articulate attached facades.
  source('arrival-parisian-detail',1)
  for angle in [lo+.012,hi-.012]:
   f=frame(angle);wp=f.p(0,0,0)
   if opera_mask.buffer(.3).contains(Point(wp[0],wp[2])):continue
   for y in np.arange(.7,17.1,.65):f.box('paris-cream',(0,y,.16),(.64 if round(y/.65)%2 else .88,.46,.28))
   f.path('paris-copper',[(.48,17.3,.12),(.48,16.8,.35),(.48,.5,.35)],.055,6)
  angles=np.linspace(lo+.05,hi-.05,4)
  for j,a in enumerate(angles):
   f=frame(a);wp=f.p(0,0,0)
   if opera_mask.buffer(1.3).contains(Point(wp[0],wp[2])):continue
   door=abs(a-1.5*math.pi)<.075
   for y,h in [(1.0,4.3),(6.85,3.60),(12.15,3.62)]:
    if y==1.0 and door:continue
    french_window(f,0,y,1.65,h,style=1 if house in [1,4] and y>6 else 0)
    if y>6:
     balcony(f,0,y-.15,2.22,.63 if y<10 else .29)
     if (house+j)%3==0:awning(f,0,y+h+.32,2.33)
     if (house+j)%2==0:
      f.path('paris-cream',[(-1.14,y+h+.44,.4),(0,y+h+.99,.4),(1.14,y+h+.44,.4)],.095,6)
   dormer(f,0,17.88,house%2==0)
  # Dormer details use near detail, roof silhouette/chimneys persist in low LOD.
  source('arrival-parisian-roofs')
  for a in [lo+.035,hi-.035]:
   f=frame(a,51);wp=f.p(0,0,0)
   if opera_mask.buffer(1).contains(Point(wp[0],wp[2])):continue
   f.box(mat,(0,21.1,-.2),(1.25,3.2,.95));f.box('paris-cream',(0,22.72,-.2),(1.5,.16,1.13))
   for xx in [-.39,0,.39]:f.lathe('paris-chimney',xx,-.2,[(22.76,.115),(23.24,.115),(23.31,.155),(23.41,.155)],8)
