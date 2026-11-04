"""Reproducible public-route support/headroom samples; no private rooms."""
import json
from pathlib import Path
out=Path('build/city-exteriors');out.mkdir(exist_ok=True)
rows={'akita-plaza':[[x,.32,z] for x in [56.5,57,57.5] for z in range(2830,2903,2)]+[[x,.32,2909] for x in range(66,93,2)],'desert-oasis':[[x,.34,2736.5] for x in range(45,63)]+[[62,.34,z] for z in [2737,2738,2739,2740,2741,2742,2743,2744]]+[[x,.34,2744] for x in range(63,86)]+[[x,3.12,2738.4] for x in range(64,86)]}
for key,v in rows.items():(out/(key+'-samples.json')).write_text(json.dumps(v)+'\n')
