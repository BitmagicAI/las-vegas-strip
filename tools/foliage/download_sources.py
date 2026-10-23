"""Fetch official CC0 source assets; manifest includes exact URLs and checksums."""
import json,subprocess,hashlib
from pathlib import Path
root=Path('tools/foliage/sources');root.mkdir(parents=True,exist_ok=True)
for asset in ['tree_small_02','grass_medium_01']:
 out=root/asset;out.mkdir(exist_ok=True)
 api=out/'api-files.json'
 if not api.exists():subprocess.run(['curl','-fsSL','-A','VegasAfterlight/1.0 (local asset integration)','https://api.polyhaven.com/files/'+asset,'-o',str(api)],check=True)
 manifest=json.loads(api.read_text());data=manifest['gltf']['1k']['gltf']
 files={asset+'_1k.gltf':data,**data['include']}
 # Official glTF omits alpha; restore it explicitly for foliage cutouts.
 alpha=manifest['leaves_alpha' if asset.startswith('tree') else 'Alpha']['1k']['png']
 files['textures/alpha.png']=alpha
 for name,info in files.items():
  path=out/name;path.parent.mkdir(parents=True,exist_ok=True)
  if not path.exists():subprocess.run(['curl','-fsSL','-A','VegasAfterlight/1.0 (local asset integration)',info['url'],'-o',str(path)],check=True)
  if hashlib.md5(path.read_bytes()).hexdigest()!=info['md5']:raise ValueError('Checksum mismatch: '+name)
 (out/'source-manifest.json').write_text(json.dumps(dict(asset=asset,page='https://polyhaven.com/a/'+asset,license='CC0-1.0',licenseURL='https://polyhaven.com/license',files=files),indent=2))
 d=json.loads((out/(asset+'_1k.gltf')).read_text());print(asset,[(n.get('name'),n.get('mesh')) for n in d['nodes']],[(m.get('name'),m.get('alphaMode')) for m in d['materials']])
