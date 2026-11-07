"""Append only the new roof glazing to the retained authored source."""
import argparse
import hashlib
import json
from pathlib import Path
from common import Meshes
from crystals_roof import POINTS
from crystals_glazing import roof_glazing


def patch(source):
    assert not any(m['source']=='crystals-central-roof-glazing-2026-11' for m in source['meshes']), 'Already patched'
    builder=Meshes();builder.property='crystalsRoof-exterior'
    roof_glazing(builder, POINTS)
    additions=list(builder.groups.values())
    assert not builder.labels and not any(v.get('indices') for v in builder.solids.values())
    result={**source,'meshes':source['meshes']+additions}
    assert result['meshes'][:len(source['meshes'])]==source['meshes']
    assert result['labels']==source['labels']
    report={'retainedGroups':len(source['meshes']),'addedTriangles':sum(len(m['faces']) for m in additions),'labelsUnchanged':True,'collisionAdded':False,'panelCount':2,'scope':'Opaque exterior glazing on two inferred central roof facets; existing roof and interior retained'}
    return result,report


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    for name in ['source','output','audit']:parser.add_argument('--'+name,type=Path,required=True)
    args=parser.parse_args();source=json.loads(args.source.read_text());result,report=patch(source)
    report['sourceSHA256']=hashlib.sha256(args.source.read_bytes()).hexdigest()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,separators=(',',':')))
    args.audit.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
