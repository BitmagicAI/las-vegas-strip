"""Build the pool and ride-only source; requires preservation backups documented in the checkpoint."""
import sys,json
from pathlib import Path
sys.path.insert(0,str(Path('tools/strip-landmarks').resolve()))
from common import Meshes,footprint
from strat_pool_deck import exterior
from strat_thrill_rides import rides
b=Meshes();exterior(b);b.save_all()
p=Path('build/strip-landmarks');original=Path('build/city-exteriors/strat-pool-rooftop-refinement/source-before');assert json.loads((p/'stratPoolDeck-exterior-collision.json').read_text())==json.loads((original/'stratPoolDeck-exterior-collision.json').read_text())
b=Meshes();b.property='stratRidesRefinement-exterior';cx,cz=footprint('way/135457469').centroid.coords[0];rides(b,cx,cz);b.save_all()
f=p/'stratRidesRefinement-exterior.json';d=json.loads(f.read_text())
for g in d['meshes']:g['property']='stratExterior-exterior'
f.write_text(json.dumps(d))
print('Pool collision unchanged; ride-only source emitted')
