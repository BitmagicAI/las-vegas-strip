import bpy,json,hashlib,math,bmesh
from pathlib import Path
OUT=Path('build/highrises');plans=json.loads((OUT/'plan.json').read_text());bykey={p['key']:p for p in plans}
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
materials={}
def mat(key,kind):
 if (key,kind) in materials:return materials[key,kind]
 p=bykey[key];hexcolor=p['glass'] if kind=='glass' else p['accent'] if kind=='accent' else '#7e8583' if kind=='roof' else p['stone']
 if kind.startswith('stone-'):hexcolor=['#bdb1a2','#b29073','#928879','#c8bbb0','#746f60'][int(kind.split('-')[1])%5]
 rgb=tuple(int(hexcolor[i:i+2],16)/255 for i in (1,3,5));rgb=tuple(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in rgb);m=bpy.data.materials.new(key+'/'+kind);m.use_nodes=True;m.diffuse_color=(*rgb,1);bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*rgb,1);bs.inputs['Metallic'].default_value=.65 if kind=='glass' else .25 if kind=='frame' else 0;bs.inputs['Roughness'].default_value=.22 if kind=='glass' else .5
 materials[key,kind]=m;return m
for g in json.loads((OUT/'meshes.json').read_text()):
 v=[(x,-z,y) for x,y,z in g['vertices']];me=bpy.data.meshes.new(g['property']);me.from_pydata(v,[],g['faces']);me.update();ob=bpy.data.objects.new(g['property']+'/'+g['source']+'/'+g['material'],me);bpy.context.collection.objects.link(ob);me.materials.append(mat(g['property'],g['material']));ob['property']=g['property'];ob['source']=g['source'];ob['detail']=g['lod']
 # Two-sided wall patches use material convention in runtime; no volume normals guessed.
for s in json.loads((OUT/'signs.json').read_text()):
 a,b=s['a'],s['b'];dx,dz=b[0]-a[0],b[1]-a[1];L=math.hypot(dx,dz);nx,nz=-dz/L,dx/L
 center=bykey[s['property']]['centroid'];mx,mz=(a[0]+b[0])/2,(a[1]+b[1])/2
 if (mx-center[0])*nx+(mz-center[1])*nz<0:nx=-nx;nz=-nz;dx=-dx;dz=-dz
 cu=bpy.data.curves.new('Roof lettering','FONT');cu.body=s['text'];cu.align_x='CENTER';cu.size=min(3,s['width']/max(len(s['text'])*.65,1));cu.extrude=.025
 ob=bpy.data.objects.new(s['property']+' roof lettering',cu);bpy.context.collection.objects.link(ob);ob.location=(mx+nx*.28,-mz-nz*.28,s['height']);ob.rotation_euler=(math.pi/2,0,math.atan2(-dz,dx));cu.materials.append(mat(s['property'],'stone'));ob['property']=s['property'];ob['source']=s['source'];ob['detail']=0
bpy.ops.wm.save_as_mainfile(filepath=str((OUT/'exteriors.blend').resolve()))
bpy.ops.export_scene.gltf(filepath=str((OUT/'exteriors.glb').resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
(OUT/'version.json').write_text(json.dumps(dict(revision=hashlib.sha256((OUT/'exteriors.glb').read_bytes()).hexdigest()[:16])))

# Preserve the authored south-Strip replacements whenever the generic towers rebuild.
import runpy
runpy.run_path("tools/south-strip/export.py",run_name="__main__")
