"""Coverage regression: pavement must tile completely, while islands stay open."""
import json, math
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon, shape, box
from shapely.ops import unary_union
from surface_geometry import triangles, tiles, ROAD_Y, WALK_Y, BED_Y, SLAB_BOTTOM, street_y

OUT=Path('build/geographic-strip')
# Concave entrance throat with a traffic island; the old Delaunay/contains
# filter loses triangles here. Check geometry coverage, not triangle counts.
p=Polygon([(0,0),(22,0),(22,7),(8,7),(8,22),(0,22)],
          [[(2,2),(2,5),(5,5),(5,2)]])
rebuilt=unary_union([t for tile in tiles(p,6) for t in triangles(tile)])
assert p.symmetric_difference(rebuilt).area<1e-9
assert abs(street_y(0)-ROAD_Y)<1e-9 and abs(street_y(6.05)-6.085)<1e-9
assert abs(WALK_Y-ROAD_Y-.145)<1e-9

layers={f['properties']['kind']:shape(f['geometry']) for f in json.loads((OUT/'surface-layers.geojson').read_text())['features']}
for a,first in layers.items():
    for b,second in layers.items():
        if a>=b:continue
        overlap=first.intersection(second).area
        assert overlap<.01,(a,b,'overlapping surface area',overlap)

meshes=json.loads((OUT/'city-meshes.json').read_text())
source=layers['road']
missing=excess=0
ground_triangles=side_faces=0
floor_samples=[]
for g in meshes:
    if g['material']!='road':continue
    v=np.array(g['vertices']);f=np.array(g['faces'],dtype=np.int64);coords=v[f]
    is_top=np.all(np.abs(coords[:,:,1]-ROAD_Y)<1e-7,axis=1)
    faces=coords[is_top]
    if not len(faces):continue
    ground_triangles+=len(faces)
    dy=np.ptp(coords[:,:,1],axis=1)
    side_faces+=int(np.count_nonzero(dy>.2))
    # Vertex winding must face upward, otherwise WebGPU culls the asphalt.
    e1=faces[:,1]-faces[:,0];e2=faces[:,2]-faces[:,0]
    cross=np.cross(e1,e2)[:,1]
    assert np.min(cross)>-1e-7
    rendered=unary_union([Polygon(t[:,[0,2]]) for t in faces])
    ix,iz=map(int,g['cell'].split(','))
    expected=source.intersection(box(ix*160,iz*160,(ix+1)*160,(iz+1)*160))
    gap=expected.difference(rendered).area
    leak=rendered.difference(expected).area
    missing+=gap;excess+=leak
    assert gap<.01 and leak<.01,(g['cell'],gap,leak)
    # Deterministic distributed probes, away from curbs; physics test consumes
    # them after collision compaction/export. Includes former missing wedges.
    # Boolean GIS boundaries contain near-zero-width sliver triangles. Their
    # exact centroids aren't stable through Float32 Rapier coordinates and
    # 0.1 mm collision compaction. Probe actual floor interiors at least 1 cm
    # from each triangle edge; the coverage check above still tests every face.
    edges=np.stack([faces[:,1]-faces[:,0],faces[:,2]-faces[:,1],faces[:,0]-faces[:,2]])
    max_edge=np.max(np.linalg.norm(edges,axis=2),axis=0)
    safe=faces[cross/np.maximum(max_edge,1e-12)>.03]
    for tri in safe[::max(1,len(safe)//8)]:
        center=np.mean(tri,axis=0)
        floor_samples.append(center.tolist())
assert ground_triangles>1000 and side_faces>1000
report=dict(roadArea=round(source.area,2),missingRoadArea=missing,excessRoadArea=excess,
    groundRoadTriangles=ground_triangles,roadSideTriangles=side_faces,
    roadTop=ROAD_Y,sidewalkTop=WALK_Y,plantingTop=BED_Y,slabBottom=SLAB_BOTTOM,
    independentLayers=list(layers),physicsProbes=len(floor_samples))
(OUT/'surface-test.json').write_text(json.dumps(report,indent=2))
(OUT/'surface-physics-probes.json').write_text(json.dumps(floor_samples,separators=(',',':')))
print(json.dumps(report,indent=2))
