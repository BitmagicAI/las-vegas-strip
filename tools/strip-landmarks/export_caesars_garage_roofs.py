"""Export original paired garage roof surfaces and fixtures only."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
import export as E
import bpy
E.colors.update({'cgr-west-concrete':'99968b','cgr-east-concrete':'686965','cgr-line-paint':'e5e0c8','cgr-service-paint':'b6b0a0','cgr-cap-paint':'c5bfaf','cgr-metal-paint':'676b66','cgr-vent-paint':'383d3b','cgr-fixture-paint':'d4d5c9'})
bpy.ops.wm.read_factory_settings(use_empty=True);E.materials.clear();E.add('caesarsGarageRoofs-exterior')
bpy.ops.export_scene.gltf(filepath=str((E.OUT/'caesarsGarageRoofs-exterior.glb').resolve()),export_format='GLB',export_yup=True,export_extras=True,export_lights=False,export_cameras=False)
