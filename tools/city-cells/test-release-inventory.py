"""Full authoring-checkout check: package selection and optimized manifest integrity."""
import importlib.util
import json
spec = importlib.util.spec_from_file_location('pack', 'tools/release/asset-pack.py')
pack = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pack)
baseline, cells = pack.runtime_files(), pack.runtime_files(True)
old = {'build/geographic-strip/city.glb', 'build/geographic-strip/city-colliders.bin', 'build/baked/city-lod.bin'}
new = {p for p in cells if '/cells/' in p or '/collision-cells/' in p}
assert old.issubset(baseline) and not old.intersection(cells)
assert not any('/cells/' in p or '/collision-cells/' in p for p in baseline)
assert set(baseline) - old == set(cells) - new, 'unrelated release inventory changed'
manifest = pack.optimized_files()
for path in sorted(new):
    if not path.endswith('/manifest.json'):
        continue
    source, _ = pack.source_for(path, manifest)
    before = source.read_bytes()
    assert pack.source_for(path, manifest)[0].read_bytes() == before, 'non-deterministic manifest'
    doc = json.loads(before)
    for entry in doc['cells']:
        item, _ = pack.source_for(path.rsplit('/', 1)[0] + '/' + entry['file'], manifest)
        assert entry['sha256'] == pack.sha256(item)
        assert entry['bytes'] == item.stat().st_size
print(f'PASS: {len(new)} cell files/manifests replace only three combined assets; optimized manifest hashes and no-op verified')
