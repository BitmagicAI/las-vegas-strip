"""Scoped patch: replace curtain group, recolor cushion group, retain everything else."""
import argparse,copy,hashlib,json
from pathlib import Path
from common import Meshes,Frame
from vanderpump_curtains import cabana_curtains

def patch(source):
    old=[m for m in source['meshes'] if m['material']=='vp-fabric']
    cushions=[m for m in source['meshes'] if m['material']=='vp-cushion']
    assert len(old)==len(cushions)==1 and len(old[0]['faces'])==240
    b=Meshes();b.property='vanderpump-exterior';b.source='soleia-cabana-curtains-2026-11';b.detail=0
    for level in [35.2,39.0]:
        for x in [49,57,65,73,81]:cabana_curtains(Frame(b,x,86,0,y=level))
    retained=[m for m in source['meshes'] if m is not old[0] and m is not cushions[0]]
    recolored=copy.deepcopy(cushions[0]);recolored['material']='vp-soleia-cushion-paint'
    result={**source,'meshes':retained+[recolored]+list(b.groups.values())}
    assert not any(s.get('indices') for s in b.solids.values())
    return result,{'retainedGroups':len(retained),'recoloredGroups':1,'cabanaCount':10,'curtainPanels':20,'removedTriangles':240,'addedTriangles':sum(len(m['faces']) for m in b.groups.values()),'collisionAdded':False,'labelsUnchanged':result['labels']==source['labels']}

if __name__=='__main__':
    p=argparse.ArgumentParser()
    for n in ['source','output','audit']:p.add_argument('--'+n,type=Path,required=True)
    a=p.parse_args();result,audit=patch(json.loads(a.source.read_text()));audit['sourceSHA256']=hashlib.sha256(a.source.read_bytes()).hexdigest();a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,separators=(',',':')));a.audit.write_text(json.dumps(audit,indent=2)+'\n');print(audit)
