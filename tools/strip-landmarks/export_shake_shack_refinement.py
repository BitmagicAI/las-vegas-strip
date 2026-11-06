"""Export the scoped sign addition; existing frontage comes from its saved GLB."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
import bpy
E.colors['ssk-emblem-green']='75a947'
bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add('shakeShackRefinement-exterior')
bpy.ops.export_scene.gltf(filepath=str((E.OUT/'shakeShackRefinement-exterior.glb').resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
