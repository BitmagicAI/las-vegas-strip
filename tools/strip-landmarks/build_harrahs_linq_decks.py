"""Scoped original pool-court geometry; estimates and sources in harrahs-linq-decks.
Retains pre-pass labels/colliders; clips only conflicting Harrahs roof surface and sampled service units. Does not invent hotel lift access.
"""
from common import *
import copy
BASE=Path('.bitmagic/city-exterior-backups/harrahs-linq-decks')

def chair(B,x,z,y,yaw=0,accent='white'):
 F=Frame(B,x,z,yaw,y=y)
 F.box('charcoal',(0,.35,0),(.76,.12,1.9),True)
 for xx in [-.31,.31]:
  for zz in [-.7,.7]:F.box('charcoal',(xx,.17,zz),(.06,.34,.06),True)
 F.box('white',(0,.46,.30),(.72,.13,1.25))
 B.face('white',[F.p(-.36,.51,-.32),F.p(.36,.51,-.32),F.p(.36,1.02,-.88),F.p(-.36,1.02,-.88)])
 F.box(accent,(0,.65,-.38),(.5,.15,.34))

def bed(B,x,z,y,accent):
 B.box('charcoal',(x,y+.25,z),(2.2,.5,2.2),True)
 B.box('white',(x,y+.55,z),(2.15,.2,2.15))
 B.box(accent,(x,y+.85,z-.75),(1.8,.4,.35))

def parasol(B,x,z,y):
 B.tube('silver',(x,y,z),(x,y+2.7,z),.035,8)
 B.lathe('white',(x,z),[(y+2.3,1.6),(y+2.75,.05)],12)
 B.box('charcoal',(x,y+.07,z),(.45,.14,.45),True)

def basin(B,p,y,lanes=False):
 B.planar('ice',p,y-1.0,True)
 B.shell(p,y-1.0,y,'ice',roof=False)
 B.planar('water',p.buffer(-.04),y-.15)
 B.planar('white',p.buffer(.35).difference(p),y+.02,True)
 if lanes:
  xmin,zmin,xmax,zmax=p.bounds
  for z in np.linspace(zmin+2,zmax-2,3):B.planar('blue',box(xmin+1,z-.12,xmax-1,z+.12),y-.99)
 xmin,zmin,xmax,zmax=p.bounds
 for x in [xmin+1.5,xmax-1.5]:
  for z in [zmin-.12,zmin+.5]:B.path('silver',[(x,y-1,z),(x,y+.65,z),(x+.45,y+.75,z),(x+.75,y+.4,z)],.035,8)

def build(key):
 old=json.loads((BASE/(key+'-exterior.json')).read_text());collision=json.loads((BASE/(key+'-exterior-collision.json')).read_text())
 B=Meshes();B.property=key+'-exterior';B.source=key+'-pool-court';B.detail=0
 if key=='harrahs':
  y=8.6;deck=box(112,-360,213,-326)
  pools=[box(170,-352,196,-340),Polygon([(124,-354),(134,-354),(141,-347),(141,-340),(124,-340)])]
  loop=[[116,y,-357],[209,y,-357],[209,y,-329],[116,y,-329],[116,y,-357]]
 else:
  y=17.0;deck=box(212.2,-243.3,280.3,-211.5)
  pools=[box(220,-233,243,-219),box(258,-231,268,-221)]
  loop=[[215,y,-239.5],[277,y,-239.5],[277,y,-214],[215,y,-214],[215,y,-239.5]]
 # Replace only the Harrahs generic roof under the documented pool court.
 removed=0
 if key=='harrahs':
  for g in old['meshes']:
   faces=[]
   for f in g['faces']:
    pts=[g['vertices'][i] for i in f]
    if g['source']=='harrahs-roof' and deck.contains(Point(sum(p[0] for p in pts)/3,sum(p[2] for p in pts)/3)):
     removed+=1;continue
    if g['source']=='harrahs-podium' and all(abs(p[1]-y)<.001 for p in pts):
     poly=Polygon([(p[0],p[2]) for p in pts])
     if poly.area>1e-8 and poly.intersection(deck).area>1e-8:
      removed+=1
      for t in [t for piece in parts(poly.difference(deck)) for t in triangles(piece)]:
       coords=list(t.exterior.coords)[:-1];n=len(g['vertices']);g['vertices'] += [[x,y,z] for x,z in coords];faces.append([n,n+2,n+1])
      continue
    faces.append(f)
   g['faces']=faces
 B.shell(deck,y-.3,y,'tile',roof=False)
 B.planar('tile',deck.difference(unary_union(pools)),y,True)
 for p in pools:basin(B,p,y,key=='harrahs')
 # Guard the free deck edges; no new route is presented as a verified hotel connection.
 F=Frame(B,0,0,y=y)
 xmin,zmin,xmax,zmax=deck.bounds
 for a,b in [((xmin,zmin),(xmax,zmin)),((xmax,zmin),(xmax,zmax)),((xmax,zmax),(xmin,zmax)),((xmin,zmax),(xmin,zmin))]:
  F.rail(a,b,1.1)
  c=B.solids[B.property];n=len(c['vertices'])//3
  for x,yy,z in [(a[0],y,a[1]),(b[0],y,b[1]),(b[0],y+1.1,b[1]),(a[0],y+1.1,a[1])]:c['vertices'].extend([x,yy,z])
  c['indices'].extend([n,n+1,n+2,n,n+2,n+3])
 B.source=key+'-pool-furniture';B.detail=1
 if key=='harrahs':
  for x in [173,177,181,185,189,193]:
   chair(B,x,-355,y,math.pi,'velvet');chair(B,x,-336,y,0,'velvet')
  for x in [146,153,160]:
   bed(B,x,-347,y,'velvet')
   for xx in [x-1.2,x+1.2]:B.box('white',(xx,y+1.2,-347),(.08,2.4,2.5),True)
  # White open trellis along the south court, above the clear perimeter route.
  for x in [169,176,183,190,197,204]:B.box('white',(x,y+1.4,-327),(.12,2.8,.12),True)
  B.box('white',(186.5,y+2.8,-327),(35,.15,1.1))
  for x in np.arange(169,205,.65):B.box('white',(x,y+2.9,-327),(.08,.1,1.3))
 else:
  for x in [222,226,230,234,238,242]:
   bed(B,x,-236.5,y,'blue');parasol(B,x,-237.8,y)
   bed(B,x,-215.7,y,'blue');parasol(B,x,-213,y)
  # The official image shows circular daybeds at the shallow end; no branded fabric.
  for z in [-229,-223]:
   B.lathe('white',(222,z),[(y-.12,1.45),(y+.22,1.45),(y+.22,.01)],24)
   B.box('blue',(222,y+.35,z-.3),(.8,.25,.5))
  for x in [259,263,267]:chair(B,x,-234.5,y,0,'blue')
 B.detail=0
 additions=list(B.groups.values());newc=B.solids[B.property];n=len(collision['vertices'])//3
 collision['vertices']+=newc['vertices'];collision['indices'] += [i+n for i in newc['indices']]
 (OUT/(key+'-exterior.json')).write_text(json.dumps({'meshes':old['meshes']+additions,'labels':old['labels']+B.labels},separators=(',',':')))
 (OUT/(key+'-exterior-collision.json')).write_text(json.dumps(collision,separators=(',',':')))
 meta={'key':key,'deckY':y,'routes':[{'name':'Pool court perimeter','points':loop}],'deckBounds':list(deck.bounds),'poolBounds':[list(p.bounds) for p in pools], 'addedTriangles':sum(len(g['faces']) for g in additions),'retainedGroups':len(old['meshes']),'replacedRoofTriangles':removed}
 (OUT/(key+'-deck-metadata.json')).write_text(json.dumps(meta,indent=2)+'\n');print(meta)
for key in ['harrahs','linq']:build(key)
