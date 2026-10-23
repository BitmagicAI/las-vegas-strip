"""Export only the validated staged variant; retain the original level files."""
import bpy,sys,json,hashlib
from pathlib import Path
sys.path.insert(0,'tools/level')
from visibility_export import export_visibility
report=json.loads(Path('build/hotels/shell-report.json').read_text())
for name,digest in report['sourceSHA256'].items():
 with open('build/level/'+name,'rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==digest,'Source changed since staging'
validation=json.loads(Path('build/hotels/validation.json').read_text())
assert validation['checks']>=20000 and not validation['failures'],'Validate circulation first'
arrival_validation=Path('build/arrival-reconstruction/routes-test.json')
if arrival_validation.exists():
 arrival=json.loads(arrival_validation.read_text())
 assert len(arrival['report'])==14 and not arrival['failures'],'Validate all arrival routes first'
bpy.ops.wm.open_mainfile(filepath=str(Path('build/hotels/staged-vegas.blend').resolve()))
export_visibility('build/hotels/staged-vegas.next.glb',data_path='build/hotels/staged-vegas.mesh-level.json',manifest_path='build/hotels/staged-visibility.json',stats_path='build/hotels/staged-visibility-stats.json',version_path='build/hotels/staged-asset-version.json',interior_cell=16)
Path('build/hotels/staged-vegas.next.glb').replace('build/hotels/staged-vegas.glb')
