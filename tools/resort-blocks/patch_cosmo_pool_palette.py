"""Scoped original pool furniture palette; preserves every triangle and collider.

Uses the current authored source, never the old frontage backup. Lounge bases
are recognized by the generator's exact .8 x .1 x 2 metre box signature;
subsequent cabanas, plants, bars and Marquee are excluded. Sizes/layout remain
legacy inferences. See cosmopolitan-terraces-refinement/research.md.
"""
import argparse, copy, hashlib, json
from collections import Counter
from pathlib import Path

KEYS = {'cosmoL4-exterior':17.04, 'cosmoL14-exterior':22.64}

def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def triangles(d):
 return Counter(tuple(tuple(m['vertices'][i]) for i in face)
                for m in d['meshes'] for face in m['faces'])

def patch(d, key, y):
 centers=[]
 for m in d['meshes']:
  if m['source']!='deck-loungers' or m['material']!='walnut': continue
  for start in range(0,len(m['faces']),12):
   faces=m['faces'][start:start+12]
   pts=[m['vertices'][i] for f in faces for i in f]
   if not pts: continue
   lo=[min(p[a] for p in pts) for a in range(3)]
   hi=[max(p[a] for p in pts) for a in range(3)]
   if len(faces)!=12 or any(abs(hi[a]-lo[a]-size)>1e-5 for a,size in enumerate([.8,.1,2])):continue
   x,z=(lo[0]+hi[0])/2,(lo[2]+hi[2])/2
   if abs(lo[1]-y-.25)>1e-5:continue
   if key=='cosmoL4-exterior' and not(-68<x<-37 and 629<z<690):continue
   centers.append((x,z))
 assert centers, key
 out=[];changed=Counter()
 for m in d['meshes']:
  if m['source']!='deck-loungers' or m['material'] not in ('walnut','ivory','velvet','steel'):
   out.append(m);continue
  keep=[];selected=[]
  for face in m['faces']:
   pts=[m['vertices'][i] for i in face]
   hit=any(all(abs(p[0]-x)<=.43 and abs(p[2]-z)<=1.001 and y-.001<=p[1]<=y+.851 for p in pts) for x,z in centers)
   (selected if hit else keep).append(face)
  if keep:out.append({**m,'faces':keep})
  if selected:
   mat='cm-pool-purple' if m['material'] in ('ivory','velvet') else 'cm-pool-white'
   out.append({**m,'source':'pool-lounger-reference-palette','material':mat,'faces':selected})
   changed[m['material']]+=len(selected)
 assert dict(changed)=={mat:len(centers)*count for mat,count in [('walnut',12),('ivory',20),('velvet',12),('steel',80)]}, 'Selection includes non-lounger geometry'
 result={**d,'meshes':out}
 assert triangles(d)==triangles(result), 'Geometry changed'
 assert d['labels']==result['labels']
 return result,{'loungers':len(centers),'centers':centers,'recoloredTriangles':dict(changed),'allTrianglesPreserved':True,'labelsPreserved':True}

if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--source',type=Path,required=True);ap.add_argument('--out',type=Path,default=Path('build/resort-blocks/cosmo'));ap.add_argument('--backup',type=Path,default=Path('.bitmagic/city-exterior-backups/cosmo-pool-palette-2026-11-07'));args=ap.parse_args()
 args.backup.mkdir(parents=True,exist_ok=True);args.out.mkdir(parents=True,exist_ok=True)
 report={}
 for key,y in KEYS.items():
  src=args.source/(key+'.json');backup=args.backup/src.name
  if not backup.exists():backup.write_bytes(src.read_bytes())
  collision=args.out/(key+'-collision.json');before=digest(collision)
  old=json.loads(backup.read_text());new,audit=patch(copy.deepcopy(old),key,y)
  (args.out/src.name).write_text(json.dumps(new,separators=(',',':')))
  audit.update(sourceSHA256=digest(backup),collisionSHA256=before,collisionUnchanged=before==digest(collision))
  report[key]=audit
 (args.out/'pool-palette-audit.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(report,indent=2))
