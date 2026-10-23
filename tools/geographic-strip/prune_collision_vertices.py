"""Remove unreferenced collision vertices exactly, without rounding or retessellation."""
def prune_cells(cells):
    before=after=0
    for cell in cells:
        source=cell['vertices'];before+=len(source)//3
        vertices=[];remap={};indices=[]
        for old in cell['indices']:
            new=remap.get(old)
            if new is None:
                new=len(vertices)//3;remap[old]=new;vertices.extend(source[old*3:old*3+3])
            indices.append(new)
        # Exact positional correspondence for every triangle corner is the invariant.
        assert len(indices)==len(cell['indices'])
        for old,new in remap.items():assert source[old*3:old*3+3]==vertices[new*3:new*3+3]
        cell['vertices']=vertices;cell['indices']=indices;after+=len(vertices)//3
    return dict(verticesBefore=before,verticesAfter=after,removed=before-after,trianglePositions='exactly preserved')
if __name__=='__main__':
    import json
    from pathlib import Path
    p=Path('build/geographic-strip/city-colliders.json');cells=json.loads(p.read_text());report=prune_cells(cells);p.write_text(json.dumps(cells,separators=(',',':')));report['bytes']=p.stat().st_size
    Path('build/geographic-strip/collision-prune-report.json').write_text(json.dumps(report,indent=2)+'\n');print(report)
