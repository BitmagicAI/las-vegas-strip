import sys
from pathlib import Path
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
import bpy
E.colors.update({'wga-white-paint':'dce0d9','wga-blue-roof-paint':'328bb3','wga-blue-trim-paint':'24749c','wga-blue-fabric':'243558','wga-curtain':'ece8dd','wga-wicker':'524b40','wga-cushion':'dfdcd1','wga-bark':'82765a','wga-leaf':'5c7546','wga-planter':'b7a385'})
E.colors.update({'wga-deck':'b9b2a5','wga-soil':'5a5840','wga-pool-tile':'71999b','trump_pool':'5f9da5'})
bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add('trumpAmenities-exterior')
p=E.OUT/'trumpAmenities-exterior.glb';bpy.ops.export_scene.gltf(filepath=str(p.resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
