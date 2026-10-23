"""Fast look at the two Bellagio towers alone (no lakefront, garage or interiors): build, then
blender -b --python tools/resort-blocks/render_bellagio_towers.py -- [view ...]
Output: build/resort-blocks/bellagio-tower-preview/."""
import sys
sys.path.insert(0,'tools/strip-landmarks')
from common import *
import common
OUT=Path('build/resort-blocks/bellagio-tower-preview');OUT.mkdir(parents=True,exist_ok=True);common.OUT=OUT
import bellagio_towers
b=Meshes();b.property='towerPreview-exterior'
site=footprint('relation/1599958');tower=footprint('way/25723909')
b.source='podium';b.planar('sandstone',site,12.4);b.shell(site,.24,12.4,'sandstone',roof=False,solid=False)
bellagio_towers.main(b,tower);bellagio_towers.spa(b,footprint('way/25723910'))
b.save_all()
print('preview:',len(b.groups),'batches,',sum(len(g['faces']) for g in b.groups.values()),'triangles;',
      {s:sum(len(g['faces']) for g in b.groups.values() if g['source']==s) for s in sorted({g['source'] for g in b.groups.values()})})
