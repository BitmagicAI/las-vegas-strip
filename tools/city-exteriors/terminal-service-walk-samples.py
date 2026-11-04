"""Reproducible support/headroom samples along reviewed public approaches."""
import json
from pathlib import Path
out=Path('build/city-exteriors');out.mkdir(exist_ok=True)
samples={'maverick':[[x,.12,z] for x in [62,63,64] for z in range(4100,4149,2)],'south-shell':[[x,.32,2948] for x in range(44,102,2)]+[[103,.32,z] for z in range(2930,2960,2)]}
for key,rows in samples.items():(out/(key+'-samples.json')).write_text(json.dumps(rows)+'\n')
