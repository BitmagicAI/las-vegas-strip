"""Replace only the existing terrace canopy group, preserving all other source data."""
import argparse, hashlib, json
from pathlib import Path
from common import Meshes, Frame, np
from citycenter63_shades import terrace_shade

def patch(source):
    groups = source['meshes']
    selected = [m for m in groups if m['source']=='ocean-prime-terrace' and m['material']=='blue']
    assert len(selected)==1, 'Expected the original canopy group exactly once'
    old = selected[0]
    vertices = np.asarray(old['vertices'])
    assert len(vertices)==576 and len(old['faces'])==288
    builder=Meshes();builder.property=old['property'];builder.source='ocean-prime-shades-2026-11';builder.detail=old['detail']
    centers=[]
    for chunk in vertices.reshape(12,48,3):
        center=chunk.mean(axis=0)
        assert np.isclose(chunk[:,1].min(),20.83) and np.isclose(chunk[:,1].max(),21.28)
        centers.append([float(center[0]),float(center[2])])
        terrace_shade(Frame(builder,center[0],center[2],0,y=18.68))
    retained=[m for m in groups if m is not old]
    result={**source,'meshes':retained+list(builder.groups.values())}
    assert result['labels']==source['labels']
    assert not any(s.get('indices') for s in builder.solids.values())
    return result,dict(retainedGroups=len(retained),shadeCount=12,centers=centers,
        replacedTriangles=288,addedTriangles=sum(len(g['faces']) for g in builder.groups.values()),
        labelsUnchanged=True,collisionAdded=False)

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    for n in ['source','output','audit']:parser.add_argument('--'+n,type=Path,required=True)
    args=parser.parse_args();result,audit=patch(json.loads(args.source.read_text()))
    audit['sourceSHA256']=hashlib.sha256(args.source.read_bytes()).hexdigest()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,separators=(',',':')))
    args.audit.write_text(json.dumps(audit,indent=2)+'\n');print(json.dumps(audit))
