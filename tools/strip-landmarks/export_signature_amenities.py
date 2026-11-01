import sys
from pathlib import Path
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
import bpy
E.colors.update({'sga-paving':'bfb5a3','sga-joint':'a79e8e','sga-coping':'c9c1ae','sga-tile':'6f9c9f','signature_pool':'528f98','sga-bark':'817258','sga-leaf':'597445','sga-soil':'5a5540','sga-cushion':'d5cbb6','sga-white':'d9d9cf','sga-rail':'685d4b','sga-burgundy':'6b3f3e','sga-curtain':'cec6b6'})
bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add('signatureAmenities-exterior')
p=E.OUT/'signatureAmenities-exterior.glb';bpy.ops.export_scene.gltf(filepath=str(p.resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
