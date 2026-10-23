"""Photo-informed south Strip replacements, confined to surveyed footprints."""
import sys,json,math
sys.path.insert(0,'build/south-strip/python');sys.path.insert(0,'tools/geographic-strip')
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon,Point,LineString,box
from shapely.ops import unary_union
from shapely.affinity import scale
from geometry import Builder
from building_surfaces import BuildingSurfaces,parts
from surface_geometry import triangles
B=Builder();out=Path('build/south-strip');survey=json.load(open('build/strip-survey/survey.json'))['buildings'];byid={f['id']:f for f in survey}
def shape(f):return unary_union([Polygon([(x,-z) for x,z in p[0]], [[(x,-z) for x,z in ring] for ring in p[1:]]).buffer(0) for p in f['polygons']])
class WallAccess:
 def wall(self,a,b,lo,hi):return [[(a[0],lo,a[1]),(b[0],lo,b[1]),(b[0],hi,b[1])],[(a[0],lo,a[1]),(b[0],hi,b[1]),(a[0],hi,a[1])]]
def facade(poly,lo,hi,wall,glass='window',mode='windows',step=3.3,spacing=2.5,surface=None,source=None):
 for ring in [poly.exterior,*poly.interiors]:
  for a,b in zip(list(ring.coords),list(ring.coords)[1:]):
   L=math.dist(a,b)
   if L<.3:continue
   ux,uz=(b[0]-a[0])/L,(b[1]-a[1])/L;nx,nz=-uz,ux
   if poly.contains(Point((a[0]+b[0])/2+nx*.02,(a[1]+b[1])/2+nz*.02)):nx,nz=-nx,-nz
   vis=surface.wall(source,a,b,lo,hi,WallAccess()) if surface else [[(a[0],lo,a[1]),(b[0],lo,b[1]),(b[0],hi,b[1])],[(a[0],lo,a[1]),(b[0],hi,b[1]),(a[0],hi,a[1])]]
   # Architectural collision excludes individual mullions and window panes.
   for tri in vis:B.face(wall,tri,True)
   reg=unary_union([Polygon([((p[0]-a[0])*ux+(p[2]-a[1])*uz,p[1]) for p in tri]) for tri in vis])
   def patch(mat,x0,y0,x1,y1,off=.09):
    if x1<=x0 or y1<=y0:return
    for q in parts(reg.intersection(box(x0,y0,x1,y1))):
     for tr in triangles(q):B.face(mat,[(a[0]+ux*x+nx*off,y,a[1]+uz*x+nz*off) for x,y in list(tr.exterior.coords)[:-1]])
   cols=max(1,round(L/spacing));cw=L/cols;B.detail=1
   if mode=='glass':
    for x in np.arange(0,L,cw):patch('bronze' if wall=='oxblood' else 'silver',x,lo,min(x+.12,L),hi,.13)
    for y in np.arange(lo,hi,step):patch('bronze' if wall=='oxblood' else 'silver',0,y,L,min(y+.17,hi),.15)
   elif mode=='bands':
    for y in np.arange(lo+.6,hi-1,step):
     patch(glass,.3,y,L-.3,min(y+step*.58,hi))
     for x in np.arange(0,L,cw):patch(wall,x,y,min(x+.15,L),min(y+step-.75,hi),.14)
   else:
    for y in np.arange(lo+.65,hi-1.3,step):
     for j in range(cols):
      x=j*cw;w=cw*(.42 if mode=='castle' else .57);mid=x+cw/2
      patch(glass,mid-w/2,y,mid+w/2,min(y+step*.64,hi))
      patch('trim',mid-w/2-.08,y-.14,mid+w/2+.08,y-.04,.19)
      if mode=='castle':
       patch('white',mid-w/2-.14,y,mid-w/2-.02,y+step*.8,.20);patch('white',mid+w/2+.02,y,mid+w/2+.14,y+step*.8,.20)
    if mode!='castle':
     for x in np.arange(0,L,cw):patch(wall,x,lo,min(x+.18,L),hi,.16)
   B.detail=0
   patch('trim' if mode=='castle' else wall,0,hi-.55,L,hi,.22)
 for roof in parts(surface.roof(source,poly,hi) if surface else poly):
  for t in triangles(roof):B.face('roof',[(x,hi,z) for x,z in list(t.exterior.coords)[:-1]])
# Map footprints of crowns are not towers: body capped below the stepped crown.
styles={791:('bronze','blackglass','bands',99),792:('ivory','window','windows',109),795:('limestone','window','windows',90),796:('ivory','window','windows',127),797:('emerald','emerald','glass',71),798:('pink','blackglass','bands',116),799:('sandstone','window','windows',123),800:('teal','teal','glass',86),801:('white','blueglass','bands',108),802:('teal','teal','glass',86),805:('oxblood','redglass','glass',107)}
records=[]
for suffix,sty in styles.items():
 f=dict(byid['way/115661'+str(suffix)],height=sty[3]);f['shape']=shape(f);records.append(f)
surface=BuildingSurfaces(records)
for f in records:
 suffix=int(f['id'][-3:]);wall,glass,mode,h=styles[suffix];B.source=f['id'];p=f['shape']
 for q in parts(p):facade(q,9,h,wall,glass,mode,3.25,2.3,surface,B.source)
# Empire State: broad tiered limestone setbacks, ribbed lantern and mast.
p=shape(byid['way/115661796']);c=p.centroid;B.source='way/115661796'
for lo,hi,fac in [(127,137,.76),(137,143,.53),(143,152,.28),(152,156,.15)]:
 q=scale(p,xfact=fac,yfact=fac,origin='centroid')
 for poly in parts(q):facade(poly,lo,hi,'ivory',spacing=1.8,step=3.0)
B.lathe('silver',(c.x,c.y),[(156,1.4),(158,.7),(161,.1)],20)
# Chrysler: stainless Art Deco crown, seven overlapping arched chevrons.
p=shape(byid['way/115661792']);c=p.centroid;B.source='way/115661792'
for i in range(6):
 lo=109+i*4.65;hi=lo+5.1;fac=.98-i*.14;q=scale(p,xfact=fac,yfact=fac,origin='centroid')
 for poly in parts(q):
  B.extrude('silver',poly,lo,hi,False)
  for a,b in zip(list(poly.exterior.coords),list(poly.exterior.coords)[1:]):
   L=math.dist(a,b)
   if L<3:continue
   ux,uz=(b[0]-a[0])/L,(b[1]-a[1])/L;nx,nz=-uz,ux
   if poly.contains(Point((a[0]+b[0])/2+nx*.1,(a[1]+b[1])/2+nz*.1)):nx,nz=-nx,-nz
   # The Chrysler's roof reads as stacked stainless arches, not a pyramid.
   arc=[]
   for q in np.linspace(0,1,25):
    x=q*L;arc.append((a[0]+ux*x+nx*.22,lo+1.2+5.0*math.sin(math.pi*q),a[1]+uz*x+nz*.22))
   B.face('silver',[(a[0]+nx*.22,lo,a[1]+nz*.22),(b[0]+nx*.22,lo,b[1]+nz*.22),*arc[::-1]])
   for aa,bb in zip(arc,arc[1:]):B.tube('trim',aa,bb,.14,6)
   for j in range(max(1,round(L/2.3))):
    x=(j+.5)*L/max(1,round(L/2.3));B.face('blackglass',[(a[0]+ux*(x-.7)+nx*.06,lo+.6,a[1]+uz*(x-.7)+nz*.06),(a[0]+ux*(x+.7)+nx*.06,lo+.6,a[1]+uz*(x+.7)+nz*.06),(a[0]+ux*x+nx*.06,hi-.4,a[1]+uz*x+nz*.06)])
B.lathe('silver',(c.x,c.y),[(137,1.7),(140,.8),(146,.04)],24)
# Salmon Art Deco vertical fins and rounded rooftop shoulders.
p=shape(byid['way/115661798']);c=p.centroid;B.source='way/115661798'
for i in range(-4,5):B.box('pink',(c.x+i*.9,118+2*(1-abs(i)/5),c.y),( .42,7,6))
# Podium has genuine circulation openings and station stair void, not a filled box.
B.source='way/115661793';pod=shape(byid[B.source]);access=LineString([(-29,1464),(-69,1464),(-95,1479),(-103,1485)]).buffer(4.5,cap_style=2)
# Keep the existing procedural guest lobby's broad entrance passage open.
t=json.load(open('src/work/hotels/highrise-towers.json'));t=next(t for t in t if t['id']=='new-york-1');a,b,c,d=t['linear'];ox,_,oz=t['origin']
def guest_rectangle(x0,z0,x1,z1):return Polygon([(ox+a*x+b*z,oz+c*x+d*z) for x,z in [(x0,z0),(x1,z0),(x1,z1),(x0,z1)]])
guest=unary_union([guest_rectangle(-3,t['lobbyFront']-13,3,6),guest_rectangle(-10.3,-8.4-6*t['bays'],10.3,6)])
# Guest modules own their floors/ceilings; the outer podium roof must not add
# a second collision ceiling through the first streamed guest floor.
B.extrude('sandstone',pod.difference(unary_union([access,guest,box(-167,1609.7,-136,1643.1),box(-52.5,1549,-34,1573)])),.1,8.8,roof_solid=False)
# Street-front miniature Manhattan: stone/brick bays, cornices, recessed storefronts.
for iz,z in enumerate(np.arange(1507,1630,12)):
 if any(abs(z-q)<.01 for q in [1555,1567]):continue  # Mapped Irish kiosk owns this open terrace bay.
 x=-43.5;h=[14,18,15,21,17][iz%5];B.box(['brick','limestone','sandstone'][iz%3],(x,h/2,z),(12,h,11.4));B.box('trim',(x,h,z),(12.5,.6,12));B.box('window',(x+6.08,4,z),(.12,5,8.4));B.box('canopy',(x+7.2,6.9,z),(2.8,.35,9.2))
 for y in np.arange(9,h-1,3):
  for zz in [-3,0,3]:B.box('window',(x+6.08,y,z+zz),(.12,1.7,1.3))
 B.text(['NEW YORK','PARK AVENUE','BROADWAY','MANHATTAN'][iz%4],(x+6.23,7.6,z),.5,math.pi/2)
B.text('NEW YORK  NEW YORK',(-27.8,17.2,1584),1.2,math.pi/2)
# Excalibur: retain its surveyed diagonal massing, not freehand scaled blocks.
B.property='excalibur';exc=[]
base=shape(byid['relation/8086330'])
for f in survey:
 p=shape(f);cx,cz=p.centroid.coords[0]
 if f['id']=='relation/8086330' or ((f['part'] or f['id'].startswith('way/399352')) and -350<cx<-40 and 1710<cz<2035 and (base.buffer(10).intersects(p) or f['id'].startswith('way/399352'))):exc.append(f)
B.source='relation/8086330';gate=LineString([(-57,1736),(-137,1814),(-180,1858)]).buffer(7,cap_style=2)
B.extrude('castlebrick',base.difference(gate),.1,8)
B.extrude('paving',gate,.06,.3,True)
# Castle wings have brick bases, white vertically articulated rooms, battlement roofs.
for id in ['way/114859870','way/114857390']:
 B.source=id;p=shape(byid[id])
 for poly in parts(p):
  facade(poly,.2,14,'castlebrick','window','windows',3.3,2.8)
  facade(poly,14,60,'white','window','castle',2.9,2.5)
  for a,b in zip(list(poly.exterior.coords),list(poly.exterior.coords)[1:]):
   L=math.dist(a,b);ux,uz=(b[0]-a[0])/max(.1,L),(b[1]-a[1])/max(.1,L);yaw=math.atan2(-uz,ux)
   for dist in np.arange(1,L,3.4):B.box('white',(a[0]+ux*dist,61,a[1]+uz*dist),(1.65,2.2,1.2),False,yaw)
   if L>20:
    for dist in [2,L-2]:
     x,z=a[0]+ux*dist,a[1]+uz*dist;B.box('white',(x,59,z),(3.6,8,3.6));B.lathe('redroof',(x,z),[(62,3.1),(67,1.5),(67.2,0)],4)
# Turrets: mapped cylindrical/corner footprints, colorful steep conical roofs.
roofcolors=['redroof','excalibur-blue-paint','redroof','goldroof','excalibur-blue-paint']
for i,f in enumerate(exc):
 if f['id'] in ['relation/8086330','way/114859870','way/114857390']:continue
 p=shape(f);c=p.centroid;r=min(9,max(1.2,math.sqrt(p.area/math.pi)));h=f['height'];B.source='castle-turrets'
 if p.area>1500:continue
 if h<8:h=10
 roofh=min(19,max(5,h*.38));body=h-roofh
 B.lathe('white',(c.x,c.y),[(.2,r),(body-2,r),(body-1,r*1.12),(body,r*1.12)],28)
 # Banded machicolations and paired lancet openings.
 for j in range(max(8,int(r*4))):
  t=j*math.tau/max(8,int(r*4));x,z=c.x+(r+.06)*math.cos(t),c.y+(r+.06)*math.sin(t);yaw=math.pi/2-t
  B.box('window',(x,body-3,z),(.75,2.5,.12),False,yaw)
  B.box('white',(c.x+r*1.1*math.cos(t),body+.2,c.y+r*1.1*math.sin(t)),(.8,1.1,.9),False,yaw)
 B.lathe(roofcolors[i%5],(c.x,c.y),[(body+.5,r*1.2),(body+1,r*1.15),(h,.12)],32)
 B.tube('goldroof',(c.x,h,c.y),(c.x,h+1.5,c.y),.10)
# Forecourt gatehouse: open central arch between turrets; drawbridge continues through.
for x,z in [(-75,1742),(-57,1760)]:
 B.lathe('white',(x,z),[(.3,4),(11,3.5),(12,4.2)],24);B.lathe('redroof',(x,z),[(12,4.7),(22,0)],32)
B.box('castlebrick',(-66,13.7,1751),(24,4,4),False,-math.pi/4)
B.text('EXCALIBUR',(-62,13.5,1747),1.6,math.pi/4)
# Castle entrance at the head of the public approach, still open down its center.
for off in [-10,10]:
 x,z=-137+off*.707,1814+off*.707;B.lathe('white',(x,z),[(.3,4),(18,4),(20,5)],32);B.lathe('excalibur-blue-paint',(x,z),[(20,5.8),(33,.1)],32)
B.box('white',(-137,19,1814),(27,4,7),False,-math.pi/4)
B.text('EXCALIBUR',(-131,18.4,1808),1.3,math.pi/4)
# The licensed scan is appended by export.py. Only a simple hidden pedestal
# collision is authored here; the sculptural mesh never becomes a triangle collider.
B.property='new-york';B.source='liberty'
B.box('pedestal',(-49.87,6.8,1636.67),(11.0,13.0,11.0),True,math.pi/4)
B.save(out/'architecture.json')
for k,v in B.solids.items():Path('build/highrises/'+k+'-collision.json').write_text(json.dumps(v,separators=(',',':')))
ids={f['id'] for f in exc}|{'way/115661793','way/115661806','way/115661807'}
(out/'replacement-ids.json').write_text(json.dumps(sorted(ids)))
print('Architecture',len(B.groups),'batches',sum(len(g['faces']) for g in B.groups.values()),'triangles',len(exc),'Excalibur footprints')
