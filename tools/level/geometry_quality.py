"""Normalize closed authored solids before Blender save and GLB export.
Open panes/petals keep their authored facing. Imported assets keep their authored normals.
"""
import bpy
import bmesh


def orient_closed_solids():
    checked = repaired = 0
    seen = set()
    for obj in bpy.data.objects:
        if obj.type != 'MESH' or obj.get('preserve_uv') or obj.data.as_pointer() in seen:
            continue
        seen.add(obj.data.as_pointer())
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        if bm.faces and all(edge.is_manifold for edge in bm.edges):
            checked += 1
            before = bm.calc_volume(signed=True)
            original = [tuple(f.normal) for f in bm.faces]
            bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
            after = bm.calc_volume(signed=True)
            if after < -1e-8:
                bm.free()
                raise ValueError(f'Inward-facing solid after normal repair: {obj.name}')
            if before < -1e-8:
                repaired += 1
            if before < -1e-8 or any(tuple(f.normal) != normal for f, normal in zip(bm.faces, original)):
                bm.to_mesh(obj.data)
                obj.data.update()
        bm.free()
    print(f'GEOMETRY ORIENTATION: {checked} closed solids checked; {repaired} inward shells repaired', flush=True)
