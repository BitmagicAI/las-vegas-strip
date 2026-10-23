import bpy,os,sys
sys.path.insert(0,'tools/level')
from visibility_export import export_visibility
bpy.ops.wm.open_mainfile(filepath=os.path.abspath('build/level/vegas.blend'))
export_visibility('build/level/vegas.glb')
