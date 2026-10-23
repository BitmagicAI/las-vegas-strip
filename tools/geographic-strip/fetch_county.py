"""Read-only, bounded download of Clark County's public pavement GIS layers."""
import datetime, json, urllib.parse, urllib.request
from pathlib import Path

OUT = Path(__file__).resolve().parents[2] / 'build/geographic-strip/county'
OUT.mkdir(parents=True, exist_ok=True)
ROOT = 'https://maps.clarkcountynv.gov/arcgis/rest/services/GISMO/Pavement/MapServer/'
BBOX = '-115.193,36.079,-115.147,36.153'

def get(url, parameters):
    with urllib.request.urlopen(url + '?' + urllib.parse.urlencode(parameters), timeout=60) as r:
        data = json.load(r)
    if 'error' in data:
        raise RuntimeError(data['error'])
    return data

for name, layer, fields in [
    ('concrete', 1, 'OBJECTID,TYPE,SWMAT,SWWIDTH,CGTYPE,CGMAT,UPDATED'),
    ('pavement', 2, 'OBJECTID,STREET,LANE,TOTALWIDTH,PAVEWDTH,PAVETYPE,UPDATED')
]:
    url = ROOT + str(layer)
    meta = get(url, {'f': 'json'})
    (OUT / (name + '-metadata.json')).write_text(json.dumps(meta, indent=2))
    features = []
    offset = 0
    while True:
        page = get(url + '/query', dict(f='geojson', where='1=1', geometry=BBOX,
            geometryType='esriGeometryEnvelope', inSR=4326, outSR=4326,
            spatialRel='esriSpatialRelIntersects', outFields=fields,
            returnGeometry='true', orderByFields='OBJECTID',
            resultOffset=offset, resultRecordCount=1000))
        batch = page.get('features', [])
        features.extend(batch)
        if len(batch) < 1000:
            break
        offset += len(batch)
    ids = [f['properties']['OBJECTID'] for f in features]
    assert len(ids) == len(set(ids)), 'Server pagination repeated a page'
    (OUT / (name + '.geojson')).write_text(json.dumps(dict(type='FeatureCollection', features=features), separators=(',', ':')))
    print(name, len(features), flush=True)
(OUT / 'source.json').write_text(json.dumps(dict(source='Clark County GISMO / Public Works',
    url=ROOT.rstrip('/'), bbox=BBOX, retrievedAt=datetime.datetime.now(datetime.timezone.utc).isoformat(),
    notes='Public reference data; no accuracy warranty. OSM supplies topology where county coverage is absent.'), indent=2))
