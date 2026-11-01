"""Original arrival detail informed by official August2025 lookbook page2.
Dimensions and registration are inferred within the existing canopy. Water is a
static rippled face; no new runtime lights, animated shaders or indoor route.
"""
from common import *
KEY='fontainebleauExterior-exterior'
def detail(B):
 B.property=KEY;B.source='arrival/entry-detail';B.detail=0
 F=Frame(B,1220,-2544,0,y=0)
 # Close the low entrance soffit back to the existing curved branding band.
 for i in range(64):
  a,b=i*math.pi/64,(i+1)*math.pi/64
  tri=[(1220,5.29,-2541),(1220+15.2*math.cos(a),5.29,-2541-7.296*math.sin(a)),(1220+15.2*math.cos(b),5.29,-2541-7.296*math.sin(b))]
  B.upface('fb-entry-dark',tri,True);B.face('fb-entry-dark',list(reversed(tri)))
 # Central framed water panel; closed solid core, recessed basin and raised lip.
 F.box('fb-entry-dark',(0,2.65,0),(9.2,5.3,1.0),True)
 F.box('fb-entry-stone',(0,.25,-.95),(9.55,.5,1.4),True)
 F.box('fb-entry-water',(0,.51,-1),(8.8,.025,1.0))
 for x in [-4.7,4.7]:F.box('fb-entry-bronze',(x,2.8,-.3),(.34,5.05,1.3),True)
 F.box('fb-entry-bronze',(0,5.17,-.3),(9.75,.26,1.3))
 # Small original staggered relief, built as one material batch; no copied image.
 B.detail=1
 for row in range(44):
  y=.66+row*.095
  for col in range(80):
   x=-4.35+col*.108+(row%2)*.054
   if x+.108>4.36:continue
   depth=-.535-.018*math.sin(col*1.7+row*.8)
   B.face('fb-entry-water',[F.p(x,y,depth),F.p(x,y+.09,depth-.025),F.p(x+.103,y+.09,depth-.025),F.p(x+.103,y,depth)])
 B.detail=0
 # Original bowtie silhouette (two flared trapezoids), projected off panel.
 def bowtie(x,y,z,s):
  for side in [-1,1]:
   pts=[(x+side*.03*s,y-.09*s,z),(x+side*.03*s,y+.09*s,z),(x+side*.45*s,y+.28*s,z),(x+side*.45*s,y-.28*s,z)]
   B.face('fb-entry-gold',[F.p(*p) for p in (pts if side>0 else reversed(pts))])
 bowtie(0,3.3,-.60,1.5)
 # Side entrance glazing is closed facade detail, not a newly claimed portal.
 for side in [-1,1]:
  center=side*9.6
  F.box('fb-entry-dark',(center,2.65,.28),(8.6,5.3,.28),True)
  for i in range(7):
   x=center-4.05+i*1.16
   F.box('fb-entry-glass',(x+.54,2.65,.08),(1.08,4.85,.06))
   F.box('fb-entry-gold',(x,2.65,-.01),(.045,5.0,.08))
  for y in [.25,1.1,4.55,5.15]:F.box('fb-entry-gold',(center,y,-.02),(8.3,.055,.09))
  # Paired central door frames and pull bars; existing openings elsewhere retained.
  for x in [center-.92,center,center+.92]:F.box('fb-entry-gold',(x,1.65,-.08),(.055,2.95,.09))
  for x in [center-.18,center+.18]:F.box('fb-entry-bronze',(x,1.5,-.18),(.04,.8,.05))
  F.box('fb-entry-gold',(center,3.1,-.08),(1.9,.06,.09))
  # Flared pale supports join the lower branding band without changing upper ribs.
  for x in [side*14.45]:
   rings=[]
   for y,half in [(0,.48),(3.4,.48),(4.5,.78),(5.3,1.38)]:
    rings.append([F.p(x+dx*half,y,dz*.45) for dx,dz in [(-1,-1),(-1,1),(1,1),(1,-1)]])
   for lo,hi in zip(rings,rings[1:]):
    for k in range(4):B.face('fb-canopy-white',[lo[k],lo[(k+1)%4],hi[(k+1)%4],hi[k]],True)
   B.upface('fb-canopy-white',rings[-1],True)
  bowtie(side*12.1,5.61,3-7.296*math.sqrt(1-(12.1/15.2)**2)-.05,.75)

def build():
 base=Path('.bitmagic/city-exterior-backups/fontainebleau-entry')
 old=json.loads((base/(KEY+'.json')).read_text());collision=json.loads((base/(KEY+'-collision.json')).read_text())
 B=Meshes();detail(B);extra=B.solids[KEY];offset=len(collision['vertices'])//3
 collision['vertices']+=extra['vertices'];collision['indices'] += [i+offset for i in extra['indices']]
 (OUT/(KEY+'.json')).write_text(json.dumps({'meshes':old['meshes']+list(B.groups.values()),'labels':old['labels']+B.labels},separators=(',',':')))
 (OUT/(KEY+'-collision.json')).write_text(json.dumps(collision,separators=(',',':')))
 print('Added',sum(len(g['faces']) for g in B.groups.values()),'triangles;',len(extra['indices'])//3,'collision triangles')
if __name__=='__main__':build()
