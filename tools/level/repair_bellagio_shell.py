"""Restore cut tower visuals in the staged level without changing its physics.

Uses the intact authored source, preserving all subsequent podium/stair repairs.
prepare_hotel_shells.py applies the same policy to future builds.
"""
import bpy,json,sys,hashlib
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
sys.path.insert(0,str(Path(__file__).resolve().parent))
from hotel_shell_policy import preserve_render_shell

OUT=Path('build/hotels/bellagio-shell-repair');OUT.mkdir(exist_ok=True)
stage=Path('build/hotels/staged-vegas.blend')
metadata=Path('build/hotels/staged-vegas.mesh-level.json')
physics_digest=hashlib.sha256(metadata.read_bytes()).hexdigest()
bpy.ops.wm.open_mainfile(filepath=str(stage.resolve()))

def shell_tree(objects):
    vertices=[];faces=[]
    for ob in objects:
        if not preserve_render_shell(ob):continue
        base=len(vertices)
        vertices.extend(ob.matrix_world@v.co for v in ob.data.vertices)
        faces.extend(tuple(base+i for i in p.vertices) for p in ob.data.polygons)
    return BVHTree.FromPolygons(vertices,faces)

def sample(tree):
    hits=[]
    # Street-to-facade rays across both curved wings, including the exposed
    # junctions beside the rotunda, and throughout the streamed floor range.
    for side in [-1,1]:
        for bay in range(24):
            u=side*(10+(bay+.5)*3.54)
            for height in [12,20,32,45,58,70,78]:
                p=Vector((-100,18-u,height))
                hit,normal,index,distance=tree.ray_cast(p,Vector((-1,0,0)),100)
                hits.append(None if hit is None else {'distance':distance,'normal':list(normal)})
    return hits

before=sample(shell_tree(list(bpy.data.objects)))
print('Sampled staged facade',flush=True)
changed=json.loads(Path('build/hotels/shell-report.json').read_text())['renderCandidates']
names=[name for name in changed if name.startswith('Bellagio ')]
existing={name:bpy.data.objects.get(name) for name in names}
with bpy.data.libraries.load(str(Path('build/level/vegas.blend').resolve()),link=False) as (source,target):
    target.objects=[name for name in names if name in source.objects]
print('Loaded source candidates',len(target.objects),flush=True)
for ob in target.objects:bpy.context.scene.collection.objects.link(ob)
# Appended objects with transforms (window frames/cornices) need evaluation
# before their world-space bounds are usable for the upper-shell policy.
bpy.context.view_layer.update()
restored=[];remove=[]
for name,ob in zip([name for name in names if name in source.objects],target.objects):
    if not preserve_render_shell(ob):
        remove.append(ob);continue
    old=existing[name]
    if old:remove.append(old)
    # Reuse existing materials/textures instead of duplicating packed maps.
    for slot in ob.material_slots:
        mat=slot.material
        if mat and mat.name.rsplit('.',1)[-1].isdigit():
            original=bpy.data.materials.get(mat.name.rsplit('.',1)[0])
            if original:slot.material=original
    restored.append((name,ob))
bpy.data.batch_remove(remove)
for name,ob in restored:
    ob.name=name
print('Restored source geometry',len(restored),flush=True)
bpy.context.view_layer.update()
after=sample(shell_tree(list(bpy.data.objects)))
assert all(hit is not None for hit in after),'Exterior still has missing faces'
bad=[{'index':i,**hit} for i,hit in enumerate(after) if hit['normal'][0]<=0]
assert not bad,f'Exterior faces must point toward the street: {bad[:15]}'
changed_rays=sum(a is None or abs(a['distance']-b['distance'])>.05 for a,b in zip(before,after))
assert restored,'No source geometry restored'
assert hashlib.sha256(metadata.read_bytes()).hexdigest()==physics_digest,'Collision metadata changed'
bpy.ops.wm.save_as_mainfile(filepath=str(stage.resolve()))
report={'restoredObjects':len(restored),'facadeRays':len(after),'repairedRays':changed_rays,'physicsUnchanged':True,'restoredNames':[n for n,_ in restored]}
(OUT/'report.json').write_text(json.dumps(report,indent=2))
print('BELLAGIO SHELL', {k:v for k,v in report.items() if k!='restoredNames'},flush=True)
