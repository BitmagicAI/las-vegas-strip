"""Export original rooftop meshes and separately streamed Platinum public interior."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
import bpy
E.colors.update({'wpa-deck':'d8cbb7','wpa_pool':'499ba8','wpa-coping':'e3dccf','wpa-gray':'8b8e90','wpa-dark':'343236','wpa-cream':'dcd2be','wpa-navy':'24344e','wpa-teal':'40a7ad','ppa-deck':'d1bea4','ppa_pool':'498f9b','ppa-coping':'bfb4a1','ppa-interior-wall':'78888f','ppa-interior-ceiling':'deded8','ppa-frame':'b7b5a9','ppa-dark':'37444c','ppa-roof':'c2b6a5','ppa-gray':'8e9496','ppa-lime':'a4b635'})
for key in ['westinAmenities-exterior','platinumAmenities-exterior','platinum-interior']:
 bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add(key)
 bpy.ops.export_scene.gltf(filepath=str((E.OUT/(key+'.glb')).resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
