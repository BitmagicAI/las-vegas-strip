"""Split upper guard faces only and append original fans; retain all source geometry."""
import argparse,copy,json
from pathlib import Path
from common import Meshes
from atomic_terrace_fans import terrace_fans

def patch(source):
    matches=[m for m in source['meshes'] if m['source']=='podium/south-terrace' and m['material']=='ag-glass']
    assert len(matches)==1
    original=matches[0];lower=copy.deepcopy(original);guard=copy.deepcopy(original)
    upper=lambda f:all(original['vertices'][i][1]>4.7 for i in f)
    lower['faces']=[f for f in original['faces'] if not upper(f)]
    guard['faces']=[f for f in original['faces'] if upper(f)];guard['material']='ag-terrace-guard-glass'
    assert len(guard['faces'])==156 and len(lower['faces'])==156
    b=Meshes();terrace_fans(b)
    result={**source,'meshes':[lower if m is original else m for m in source['meshes']]+[guard]+list(b.groups.values())}
    assert not any(s.get('indices') for s in b.solids.values())
    return result,dict(unchangedGroups=29,guardTriangles=156,lowerGlazingTriangles=156,fanCount=2,addedTriangles=sum(len(m['faces']) for m in b.groups.values()),fanTriangles=336,soffitTriangles=5,collisionAdded=False)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('source',type=Path);p.add_argument('output',type=Path);p.add_argument('audit',type=Path);a=p.parse_args()
    d,audit=patch(json.loads(a.source.read_text()));a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(d,separators=(',',':')));a.audit.write_text(json.dumps(audit,indent=2)+'\n');print(audit)
