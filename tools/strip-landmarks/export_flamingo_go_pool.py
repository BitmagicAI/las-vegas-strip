"""Export original pool geometry without reference textures or runtime lights."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
import bpy
E.colors.update({'fgp-paving':'d8cbbb','fgp-stone':'c1afa0','fgp-tile':'8bbabb','fgp_pool':'56b8c3','fgp-coping':'e8dfcf','fgp-pink':'d6b3b3','fgp-waterfall':'9dcfd4','fgp-speaker':'393c39','fgp-canopy':'ece6d9','fgp-metal':'aeaa98','fgp-bar':'ad9388','fgp-seat':'e6d7c3','fgp-yellow':'d8b85c','fgp-bark':'86735a','fgp-leaf':'607c45'})
bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add('flamingoGoPool-exterior')
bpy.ops.export_scene.gltf(filepath=str((E.OUT/'flamingoGoPool-exterior.glb').resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
