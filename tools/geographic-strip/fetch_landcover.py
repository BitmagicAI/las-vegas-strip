"""Cache public OSM ground cover separately from the building/highway survey."""
import json
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'build/geographic-strip/landcover'
OUT.mkdir(exist_ok=True)
bounds = json.loads((ROOT / 'build/strip-survey/survey.json').read_text())['summary']['bbox']
bbox = ','.join(map(str, bounds))
query = f'''[out:json][timeout:120];(
nwr[landuse~"^(grass|meadow|forest|flowerbed|shrubbery)$"]({bbox});
nwr[landcover]({bbox});
nwr[natural~"^(wood|scrub|grassland|heath|tree|tree_row)$"]({bbox});
nwr[leisure~"^(garden|park)$"]({bbox});
way[golf~"^(fairway|green|rough|tee)$"]({bbox});
);out geom;'''
(OUT / 'query.overpass').write_text(query)
url = 'https://overpass-api.de/api/interpreter'
request = urllib.request.Request(url, urllib.parse.urlencode({'data': query}).encode(),
                                headers={'User-Agent': 'VegasAfterlight-local-map-study/1.0'})
with urllib.request.urlopen(request, timeout=150) as response:
    data = json.load(response)
if 'elements' not in data or data.get('remark'):
    raise RuntimeError(data.get('remark', 'Invalid OSM response'))
(OUT / 'osm.json').write_text(json.dumps(data, separators=(',', ':')))
(OUT / 'source.json').write_text(json.dumps(dict(url=url, bbox=bounds,
    timestamp=data.get('osm3s', {}).get('timestamp_osm_base'),
    attribution='© OpenStreetMap contributors; ODbL', features=len(data['elements'])), indent=2))
print('Cached', len(data['elements']), 'OSM landcover features')
