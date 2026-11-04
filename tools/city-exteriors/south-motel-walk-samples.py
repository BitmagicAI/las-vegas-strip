"""Reproducible support/headroom strips along the reviewed exterior approaches."""
import json
from pathlib import Path
out=Path('build/city-exteriors');out.mkdir(parents=True,exist_ok=True)
diamond=[[x,.02,z] for x in range(42,113,2) for z in [3155,3156,3157]]
diamond += [[x,.02,z] for x in [110,111,112] for z in range(3158,3199,2)]
diamond += [[x,.02,z] for x in range(51,110,2) for z in [3196,3197,3198]]
nirvana=[[x,.02,z] for x in [40,42,44,46,48] for z in range(2680,2707,2)]
(out/'diamond-samples.json').write_text(json.dumps(diamond))
(out/'nirvana-samples.json').write_text(json.dumps(nirvana))
print('Diamond',len(diamond),'Nirvana',len(nirvana))
