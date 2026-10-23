"""Exterior-only revision from Earth and July2026 Caesars photograph.
Retains mapped occupied envelope, doors and all authored interiors. No whole-city build.
"""
from common import *
from forum_shops import facade_frame
import copy,hashlib,gzip
BACK=Path('tools/strip-landmarks/retained-source')
def clipwest(pts,edge=161.2):
 out=[]
 for a,b in zip(pts,pts[1:]+pts[:1]):
  ina,inb=a[0]<=edge,b[0]<=edge
  if ina:out.append(a)
  if ina!=inb:
   t=(edge-a[0])/(b[0]-a[0]);out.append([a[i]+t*(b[i]-a[i]) for i in range(3)])
 return out
def source(name):
 return gzip.decompress((BACK/(name+'.gz')).read_bytes()).decode()
old=json.loads(source('vanderpump-exterior.json'))
B=Meshes();B.property='vanderpump-exterior';B.source='guest-vanderpump';B.detail=0
p=footprint('way/61239326');upper=p.intersection(box(35,77,135,128))
# Same occupied shell and physical heights as retained guest rooms.
B.shell(upper,7.14,34,'vp-stucco',roof=False,solid=False)
B.planar('vp-deck',upper,35.2,True)
for poly in parts(upper):
 cc=list(poly.exterior.coords)
 for a,b in zip(cc,cc[1:]):
  if math.dist(a,b)<.05:continue
  F,L,nx,nz=facade_frame(B,a,b,poly,.10)
  # West end is the large flat sign panel, not a wall of balconies.
  west=max(a[0],b[0])<39
  for y in [7.3,33.5,34.2,35.0]:F.box('vp-cream',(L/2,y,-.08),(L,.22,.38))
  if west:continue
  if L<2.7:continue
  n=max(1,round(L/4.4));w=L/n
  for col in range(n):
   x=(col+.5)*w
   # Window centres retain the established guest-floor rhythm.
   for y in np.arange(8.94,32.1,3.2):
    F.box('vp-shadow',(x,y,-.015),(w*.66,2.5,.07))
    F.box('vp-glass',(x,y,-.07),(w*.57,2.25,.04))
    for dx in [-w*.31,0,w*.31]:F.box('vp-frame',(x+dx,y,-.11),(.065,2.4,.08))
    for yy in [-1.27,1.27]:F.box('vp-cream',(x,y+yy,-.05),(w*.76,.16,.30))
    F.box('vp-metal-paint',(x,y-1.0,-.34),(w*.74,.10,.6))
    for yy in [y-.95,y-.18]:F.box('vp-metal-paint',(x,yy,-.63),(w*.74,.055,.055))
    for dx in np.linspace(-w*.35,w*.35,9):F.box('vp-metal-paint',(x+dx,y-.57,-.63),(.035,.76,.035))
  # Narrow pilasters articulate bays without uniform thick storey stripes.
  for col in range(n+1):F.box('vp-cream',(col*w,20.0,0),(.12,25.1,.16))
# West end inset name panel faces the Strip, with a real perimeter moulding.
F=Frame(B,35.25,101,1.5220136204841,y=0)
for x in [-8.5,8.5]:
 F.box('vp-cream',(x,20,-.38),(.25,22,.20))
 F.box('vp-cream',(x*.92,20,-.42),(.065,20.5,.13))
for y in [9,31]:F.box('vp-cream',(0,y,-.38),(17.25,.25,.20))
F.text('THE',(0,21.7,-.56),.65,'vp-letter');F.text('VANDERPUMP',(0,20.1,-.56),2.1,'vp-letter');F.text('HOTEL',(0,18.8,-.56),.66,'vp-letter')
# GIADA street frontage. Follow actual mapped curved corners; avoid public entrance.
B.source='vanderpump-podium-detail'
portal=json.loads(source('vanderpump-venues.json'));portal=next(v for v in portal if v['key']=='vanderpump')['portals'][0];q=Point(portal['p'][0],portal['p'][2])
for poly in parts(p):
 cc=list(poly.exterior.coords)
 for a,b in zip(cc,cc[1:]):
  segment=LineString([a,b]).intersection(box(-10000,-10000,161.2,10000))
  if segment.is_empty or segment.geom_type!='LineString':continue
  a,b=segment.coords[0],segment.coords[-1]
  if math.dist(a,b)<.05:continue
  F,L,nx,nz=facade_frame(B,a,b,poly,.12)
  line=LineString([a,b]);public=(nx<-.55 or nz>.4)
  nearentry=line.distance(q)<9
  for y in [6.2,6.8]:F.box('vp-cream',(L/2,y,-.06),(L,.18,.28))
  if public and not nearentry:
   for lo,hi in [(1.0,2.75),(3.2,5.7)]:
    F.box('vp-glass',(L/2,(lo+hi)/2,0),(L,hi-lo,.08))
    for xx in np.arange(.25,L,.95):F.box('vp-frame',(xx,(lo+hi)/2,-.07),(.045,hi-lo,.1))
    for y in [lo,hi]:F.box('vp-frame',(L/2,y,-.08),(L,.06,.10))
   F.box('vp-cream',(L/2,2.98,-.12),(L,.34,.32))
  elif not public and L>5:
   for xx in np.arange(2,L-1,6):F.box('vp-service-paint',(xx,2,.04),(2.2,3.6,.06))
   for y in [2.9,5.0]:F.box('vp-joint',(L/2,y,-.01),(L,.035,.04))
F=Frame(B,48,126.1,math.pi,y=0);F.text('GIADA',(0,6.7,-.4),.95,'vp-letter')
# Roof: open western pool terrace with two north cabana tiers, eastern raised club.
B.source='guest-vanderpump'
club=upper.intersection(box(91,77,135,129)).buffer(-.5)
# Curved western club front seen in Earth, preserving rather than cutting guest floors.
curve=Point(107,101).buffer(17,resolution=24).intersection(box(88,77,107,129))
club=unary_union([club,curve]).intersection(upper.buffer(-.5))
B.shell(club,35.2,43.2,'vp-stucco',roof=False)
B.planar('vp-roof-paint',club,43.2,True)
for poly in parts(club):
 cc=list(poly.exterior.coords)
 for a,b in zip(cc,cc[1:]):
  F,L,nx,nz=facade_frame(B,a,b,poly,.05)
  if L<.01:continue
  for y in [35.7,42.7]:F.box('vp-cream',(L/2,y,-.08),(L,.28,.3))
  if nx<-.2:F.box('vp-glass',(L/2,38.0,0),(L,4.0,.09))
  elif L>4:
   for xx in np.arange(2,L-1,5):
    for dx in [-1.6,1.6]:F.box('vp-cream',(xx+dx,39,0),(.14,6,.18))
    for y in [36,42]:F.box('vp-cream',(xx,y,0),(3.3,.14,.18))
# Pool and tiled surround stay entirely on the retained tower roof.
pool=box(53,94,81,112).buffer(2,resolution=12)
B.planar('vp-cream',pool.buffer(.55),35.24)
B.planar('vanderpump_pool',pool,35.28)
# Solid deck remains below water; no game lake or unrelated pool changes.
for level in [35.2,39.0]:
 for x in [49,57,65,73,81]:
  R=Frame(B,x,86,0,y=level)
  R.box('vp-cream',(0,3.5,0),(7.8,.26,7.0),True)
  R.box('vp-deck',(0,.12,0),(7.8,.24,7.0),True)
  for dx in [-3.6,3.6]:
   R.box('vp-cream',(dx,1.75,-3),( .22,3.5,.22),True)
   R.box('vp-fabric',(dx*.87,1.8,0),(.7,3.2,5.7))
  R.box('vp-cushion',(0,.62,1.1),(4,.30,1.7));R.box('vp-cushion',(0,1.2,1.8),(4,1.2,.25))
  R.box('vp-table-wood',(0,.72,-1.1),(2,.14,1.0))
  if level>36:
   R.box('vp-metal-paint',(0,1,-3.5),(7.7,.06,.06))
   for xx in np.arange(-3.5,3.6,.5):R.box('vp-metal-paint',(xx,.6,-3.5),(.03,.85,.03))
# Poolside daybeds and separate parasols, kept as batched decorative architecture.
for x in [48,56,64,72,80,88]:
 for z in [117.5,121]:
  if not upper.contains(box(x-1,z-1,x+1,z+1)):continue
  B.box('vp-cushion',(x,35.75,z),(1.8,.35,2.5));B.box('vp-metal-paint',(x,35.4,z),(1.7,.35,2.4))
for x in [50,63,76,87]:
 B.tube('vp-metal-paint',(x,35.2,115.5),(x,38.0,115.5),.06,8)
 B.lathe('vp-parasol-fabric',(x,115.5),[(37.7,2.1),(38.3,.05)],16)
# Roof perimeter parapet, with a single dark fascia over the open terrace.
for poly in parts(upper):
 for a,b in zip(list(poly.exterior.coords),list(poly.exterior.coords)[1:]):
  F,L,nx,nz=facade_frame(B,a,b,poly,-.1)
  F.box('vp-cream',(L/2,35.8,0),(L,1.2,.2),True)
  if max(a[0],b[0])<91:F.box('vp-metal-paint',(L/2,34.6,-.18),(L,1.0,.08))
# Mechanical roof equipment on the rear enclosed club.
for x,z in [(112,88),(121,89),(124,109)]:
 B.box('vp-service-paint',(x,43.8,z),(3,1.2,3))
 for dz in [-.7,.7]:B.lathe('vp-shadow',(x,z+dz),[(44.4,.55),(44.46,.55)],12)
# Eastern porte-cochere is an open drive-under canopy, not occupied casino mass.
B.source='vanderpump-east-canopy'
canopy=p.intersection(box(161.2,0,250,200))
B.shell(canopy,6.1,7.0,'vp-cream',roof=False)
B.planar('vp-roof-paint',canopy,7.0,True)
for poly in parts(canopy):
 for t in triangles(poly):B.face('vp-cream',[(x,6.1,z) for x,z in reversed(list(t.exterior.coords)[:-1])],True)
for x,z in [(167,98),(167,123),(197,101),(197,120)]:
 B.box('vp-stucco',(x,3.05,z),(.8,6.1,.8),True)
 B.box('vp-cream',(x,.35,z),(1.15,.7,1.15))
B.planar('vp-deck',canopy,.18,True)
# Keep the retained podium/entrance meshes. Replace all old guest-source exterior,
# including its unsupported rooftop furniture and old sign, in one ownership operation.
retained=[]
for g in old['meshes']:
 if g['source']=='guest-vanderpump':continue
 q=copy.deepcopy(g)
 if q['source']=='vanderpump-podium':
  vertices=[];faces=[]
  for f in q['faces']:
   pts=clipwest([q['vertices'][i] for i in f]);at=len(vertices);vertices+=pts
   faces.extend([[at,at+i,at+i+1] for i in range(1,len(pts)-1)])
  q['vertices']=vertices;q['faces']=faces
 retained.append(q)
new={'meshes':retained+list(B.groups.values()),'labels':[l for l in old['labels'] if l.get('source')!='guest-vanderpump']+B.labels}
# Source labels have the same ownership metadata; no interior file is read for mutation.
for g in new['meshes']:
 v=np.asarray(g['vertices']);g['faces']=[f for f in g['faces'] if np.linalg.norm(np.cross(v[f[1]]-v[f[0]],v[f[2]]-v[f[0]]))>1e-9]
(OUT/'vanderpump-exterior.json').write_text(json.dumps(new,separators=(',',':')))
c=json.loads(source('vanderpump-exterior-collision.json'));v=np.asarray(c['vertices']).reshape(-1,3);ix=np.asarray(c['indices']).reshape(-1,3);keep=np.min(v[ix][:,:,1],axis=1)<34.9
# Retain occupied structural collisions; remove only old above-roof furniture/rails.
cv=[];ret=[]
for f in ix[keep]:
 pts=clipwest(v[f].tolist());at=len(cv)//3;cv.extend(n for pt in pts for n in pt)
 ret.extend(j for i in range(1,len(pts)-1) for j in [at,at+i,at+i+1])
c['vertices']=cv
nc=B.solids[B.property];off=len(c['vertices'])//3
c['indices']=ret+[i+off for i in nc['indices']];c['vertices']+=nc['vertices'];(OUT/'vanderpump-exterior-collision.json').write_text(json.dumps(c,separators=(',',':')))
print('Vanderpump exterior',len(new['meshes']),'batches',sum(len(g['faces']) for g in new['meshes']),'triangles; retained occupied collisions',sum(keep))
