"""Export original amenities only; existing shells are preserved by installation."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
import bpy
E.colors.update({'ha-paving':'cbbca6','ha_pool':'579cae','ha-tile':'6f9eaa','ha-coping':'e3d5bd','ha-stone':'a69e92','ha-white':'e5e1d8','ha-roof':'bcbcb7','ha-wood':'6f5140','ha-frame':'686b66','ha-lime':'b5c36c','ha-blue':'4997b5','ha-pebbles':'b2aaa0','wda-paving':'cdbda5','wda_pool':'4b9ead','wda-tile':'8ba7a8','wda-coping':'b9ad9b','wda-white':'eeeae3','wda-screen':'9b9990','wda-dark':'333b3a','wda-cushion':'c0c4c0','wda-guard':'a0b3b7','wda-metal':'899493'})
for key in ['waldorfAmenities','hgvFlamingoAmenities']:
 bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add(key+'-exterior')
 bpy.ops.export_scene.gltf(filepath=str((E.OUT/(key+'-exterior.glb')).resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
