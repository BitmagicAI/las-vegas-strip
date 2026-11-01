import sys
from pathlib import Path
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
import bpy
E.colors.update({'ela-deck':'c5bdad','ela-coping':'e4e0d4','ela-pool-tile':'6d999b','elara_pool':'528f98','ela-soffit':'d1c9b5','ela-post':'b5a27b','ela-rail-glass':'b3c2ba','ela-stair':'c8c3b7','ela-cushion':'e4dfcc','ela-bark':'817258','ela-leaf':'5b7649','ela-planter':'baad91','ela-yellow-fabric':'d9b64b','ela-curtain':'d9d5c8'})
bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add('elaraAmenities-exterior')
m=E.materials['ela-rail-glass'];bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Alpha'].default_value=.22;bs.inputs['Roughness'].default_value=.22;m.diffuse_color=(*m.diffuse_color[:3],.22);m.surface_render_method='DITHERED'
p=E.OUT/'elaraAmenities-exterior.glb';bpy.ops.export_scene.gltf(filepath=str(p.resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
