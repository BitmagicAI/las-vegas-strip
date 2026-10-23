"""Blender-only export and daylight review of local south-Strip assets."""
import bpy,json,math,hashlib,shutil,sys
from pathlib import Path
from mathutils import Vector
OUT=Path('build/south-strip');HI=Path('build/highrises')
colors={'ivory':'dfd7c5','white':'e5e3d7','trim':'d5c8b2','sandstone':'c9aa83','limestone':'c3bca9','pink':'c58e84','bronze':'9b7250','oxblood':'762637','redglass':'4b2130','teal':'195051','emerald':'15533d','blueglass':'467687','window':'26302e','blackglass':'253b3b','silver':'b7c6c6','roof':'999184','brick':'a16f54','castlebrick':'dbd8cd','redroof':'942d35','navy':'133f55','excalibur-blue-paint':'239bc3','goldroof':'a19035','copper':'6baf9a','copperlight':'80bda7','copperdark':'43877b','torch':'e2ae40','pedestal':'a9aa91','paving':'b6aa95','concrete':'d1c5ac','support':'d6c6a5','trackred':'b61c32','yellow':'edb931','black':'22282b','steel':'6c787c','seat':'393d41','stationroof':'224443','canopy':'163c37'}
materials={}
def material(key):
 if key in materials:return materials[key]
 rgb=[int(colors[key][i:i+2],16)/255 for i in (0,2,4)];rgb=[v/12.92 if v<.04045 else ((v+.055)/1.055)**2.4 for v in rgb];m=bpy.data.materials.new('South Strip / '+('castle-limestone' if key=='castlebrick' else key));m.use_nodes=True;m.diffuse_color=(*rgb,1);bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*rgb,1);metal=key in ['silver','bronze','steel','copper','copperlight','copperdark'];glass=key in ['window','blackglass','teal','emerald','blueglass','redglass'];bs.inputs['Metallic'].default_value=.65 if metal or glass else .05;bs.inputs['Roughness'].default_value=.3 if metal else .22 if glass else .62;materials[key]=m;return m
def add(file):
 data=json.load(open(OUT/file))
 for g in data['meshes']:
  me=bpy.data.meshes.new(g['material']);me.from_pydata([(x,-z,y) for x,y,z in g['vertices']],[],g['faces']);me.update();me.materials.append(material(g['material']));o=bpy.data.objects.new(g['property']+'/'+g['source']+'/'+g['material'],me);bpy.context.collection.objects.link(o);o['property']=g['property'];o['source']=g['source'];o['detail']=g['detail']
 for s in data['labels']:
  cu=bpy.data.curves.new(s['text'],'FONT');cu.body=s['text'];cu.align_x='CENTER';cu.size=s['size'];cu.extrude=.012;cu.materials.append(material(s['material']));o=bpy.data.objects.new(s['text'],cu);bpy.context.collection.objects.link(o);x,y,z=s['position'];o.location=(x,-z,y);o.rotation_euler=(math.pi/2,0,-s['yaw']+math.pi);o['property']=s['property'];o['source']=s['source'];o['detail']=1
 return data
def export(directory,name):
 bpy.ops.wm.save_as_mainfile(filepath=str((directory/(name+'.blend')).resolve()));bpy.ops.export_scene.gltf(filepath=str((directory/(name+'.glb')).resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
if not (HI/'exteriors-before-south-strip.blend').exists():shutil.copy2(HI/'exteriors.blend',HI/'exteriors-before-south-strip.blend')
bpy.ops.wm.open_mainfile(filepath=str((HI/'exteriors.blend').resolve()))
for o in list(bpy.data.objects):
 if o.get('property') in ['new-york','excalibur']:bpy.data.objects.remove(o,do_unlink=True)
add('architecture.json')
# Use the credited scan for the figure, with no overlapping primitive stand-in.
for o in list(bpy.data.objects):
 if o.get('source')=='liberty':bpy.data.objects.remove(o,do_unlink=True)
with bpy.data.libraries.load(str((OUT/'liberty-optimized.blend').resolve()),link=False) as (source,target):
 target.objects=[name for name in source.objects if name.startswith('Liberty /')]
for o in target.objects:
 bpy.context.collection.objects.link(o);o.location=(-49.87,-1636.67,.30);o.rotation_euler=(0,0,math.pi/4)
export(HI,'exteriors');(HI/'version.json').write_text(json.dumps(dict(revision=hashlib.sha256((HI/'exteriors.glb').read_bytes()).hexdigest()[:16])))
for name in ['coaster','train']:
 bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False);materials.clear();add(name+'.json');export(OUT,name)
(OUT/'version.json').write_text(json.dumps(dict(revision=hashlib.sha256((OUT/'coaster.glb').read_bytes()+(OUT/'route.json').read_bytes()).hexdigest()[:16])))
print('SOUTH STRIP EXPORTED',flush=True)
