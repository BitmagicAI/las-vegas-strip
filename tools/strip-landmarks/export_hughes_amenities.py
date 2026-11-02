"""Export the original grouped Hughes Center source studies; no live installation."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
import bpy
E.colors.update({'rha-paving':'c9bca8','rha_pool':'388f9e','rha-coping':'cbbda6','rha-tile':'253d65','rha-fabric':'64676a','rha-metal':'45494b','rha-cream':'e5dfd1','rha-yellow':'c5ae43','pha-paving':'d4c9b7','pha_pool':'4298ae','pha-coping':'e3dac8','pha-court-surround':'567659','pha-court':'54765f','pha-line':'eeeae0','pha-metal':'44483e','pha-net':'41433d','pha-fabric':'d8cdb5','wha-lawn':'7b8851','wha-path':'b8b6a8','wha-paving':'a79b88','wha-metal':'514b3f','wha-slat':'77715a','wha-seat':'998875','wha-hedge':'4d6339'})
for key in ['wellsHughesAmenities','parkHughesAmenities','residenceHughesAmenities']:
 bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add(key+'-exterior')
 bpy.ops.export_scene.gltf(filepath=str((E.OUT/(key+'-exterior.glb')).resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
