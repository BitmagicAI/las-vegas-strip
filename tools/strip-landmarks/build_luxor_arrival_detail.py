"""Reference-supported north-arrival beam and pier ornament.

February2025 Street View establishes slotted stone beams and inset relief panels.
Decorative strokes here are original approximations, not transcribed hieroglyphs.
Existing geometry, collision, roads and public connector are retained verbatim.
"""
from common import *
BASE=Path('.bitmagic/city-exterior-backups/luxor-arrival')

def ornament(F,y,kind):
 # Shallow original carved-line motifs; intentionally no claimed historical text.
 if kind%3==0:
  lines=[[(-.25,y,0),(-.08,y+.24,0),(.14,y+.19,0),(.24,y+.35,0)], [(-.08,y+.24,0),(-.12,y+.47,0),(.02,y+.52,0),(.09,y+.43,0)], [(-.18,y,0),(.17,y,0)],[(.04,y+.18,0),(.04,y,0)]]
 elif kind%3==1:
  lines=[[(0,y,0),(0,y+.52,0)],[(-.24,y+.35,0),(0,y+.2,0),(.23,y+.35,0)],[(-.21,y+.51,0),(0,y+.38,0),(.20,y+.51,0)],[(-.24,y,0),(.24,y,0)]]
 else:
  lines=[[(-.23,y,0),(-.23,y+.47,0),(.23,y+.47,0),(.23,y,0)],[(-.1,y+.04,0),(-.1,y+.33,0),(.1,y+.33,0),(.1,y+.04,0)],[(-.25,y-.04,0),(.25,y-.04,0)]]
 for line in lines:
  for a,b in zip(line,line[1:]):
   dx,dy=b[0]-a[0],b[1]-a[1];length=math.hypot(dx,dy);nx,ny=-dy/length*.014,dx/length*.014
   F.b.face('luxor-arrival-carve',[F.p(a[0]+nx,a[1]+ny,0),F.p(b[0]+nx,b[1]+ny,0),F.p(b[0]-nx,b[1]-ny,0),F.p(a[0]-nx,a[1]-ny,0)])

def panel(F,mat,width,lo,hi,depth=0):
 F.b.face(mat,[F.p(-width/2,lo,depth),F.p(-width/2,hi,depth),F.p(width/2,hi,depth),F.p(width/2,lo,depth)])

def build():
 old=json.loads((BASE/'luxorExterior-exterior.json').read_text())
 B=Meshes();B.property='luxorExterior-exterior';B.source='luxor-north-arrival-detail';B.detail=1
 count=0
 for xa,xb in [(-387,-335),(-309,-281),(-228,-197),(-171,-122)]:
  for z in [2100,2123]:
   # Deep frieze on the existing high frame; no new ground obstruction.
   B.box('luxor-arrival-stone',((xa+xb)/2,14.65,z),(xb-xa+.8,1.9,1.12))
   for side in [-1,1]:
    for x in np.arange(xa+.55,xb-.1,.65):
     panel(Frame(B,x,z+side*.577,0 if side<0 else math.pi,y=0),'luxor-arrival-slot',.21,14.09,15.31)
    for y in [13.76,15.54]:B.box('luxor-band',((xa+xb)/2,y,z+side*.59),(xb-xa+.85,.13,.10))
   for x in np.linspace(xa,xb,max(2,round((xb-xa)/8)+1)):
    count+=1
    for side in [-1,1]:
     F=Frame(B,x,z+side*.43,0 if side<0 else math.pi,y=0)
     for row,y in enumerate(np.arange(2.25,13.1,1.2)):
      panel(F,'luxor-arrival-stone',.76,y-.215,y+.735,-.02)
      for yy in [y-.18,y+.72]:panel(F,'luxor-arrival-carve',.75,yy-.0125,yy+.0125,-.03)
      G=Frame(B,x,z+side*.46,0 if side<0 else math.pi,y=0)
      ornament(G,y, row+count)
 groups=list(B.groups.values())
 (OUT/'luxorExterior-exterior.json').write_text(json.dumps({'meshes':old['meshes']+groups,'labels':old['labels']},separators=(',',':')))
 (OUT/'luxorExterior-exterior-collision.json').write_bytes((BASE/'luxorExterior-exterior-collision.json').read_bytes())
 report={'piersDetailed':count,'preservedGroups':len(old['meshes']),'preservedTriangles':sum(len(g['faces']) for g in old['meshes']),'addedTriangles':sum(len(g['faces']) for g in groups),'collision':'byte-identical','remaining':'Frame dimensions and carved ornament are approximate. No new indoor stairs, pool renovation or continuous whole-resort route is claimed.'}
 Path('docs/project-records/luxor-arrival/source.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
if __name__=='__main__':build()
