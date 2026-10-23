"""Build only Venetian exterior from shared authoritative generator, preserving all interiors/metadata."""
from pathlib import Path
import sys,json
sys.path.insert(0,'tools/strip-landmarks')
s=Path('tools/strip-landmarks/build.py').read_text()
pre=s[:s.index("enter('linq');")]
a=s.index("enter('venetian');");b=s.index("enter('venetian','interior');",a)
namespace={}
exec(compile(pre+s[a:b],'<Venetian exterior only>','exec'),namespace)
B=namespace['B']
from venetian_surface_ownership import reconcile
print('Surface ownership cut area:',reconcile(B))
B.save_all()
# Merge review cameras only; keep existing interior zones/portals/venue metadata.
vp=Path('build/strip-landmarks/venues.json');venues=json.loads(vp.read_text())
for venue in venues:
 if venue['key']=='venetian':
  venue['views'].update(namespace['spec']['views'])
  # Only the exterior approach changes; the indoor part of the Rialto route belongs to the interior builder (2026-10-23).
  r=venue['routes'][1];r['points']=[list(p) for p in namespace['route_points']()]+r.get('interior',r['points'][-3:])
vp.write_text(json.dumps(venues,separators=(',',':')))
print('Venetian exterior:',len(B.groups),'groups,',sum(len(g['faces']) for g in B.groups.values()),'triangles. Interiors preserved; exterior review cameras merged.')
