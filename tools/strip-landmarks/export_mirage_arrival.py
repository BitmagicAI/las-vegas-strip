"""Export original public arrival roof only; preserve resort through targeted installer."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
import bpy
E.colors.update({'ma-cream-paint':'d9d5bf','ma-stone':'a99c82','ma-stone-cap':'baae93','ma-stone-light':'c5baa1','ma-stone-dark':'aea18a','ma-roof-shingle':'8e7554','ma-roof-edge':'655039','ma-timber':'8c643d','ma-rafter':'64452d'})
bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add('mirageArrival-exterior')
bpy.ops.export_scene.gltf(filepath=str((E.OUT/'mirageArrival-exterior.glb').resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
