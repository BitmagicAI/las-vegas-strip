from pathlib import Path
import shutil,json,hashlib
root=Path.cwd();cand=root/'.bitmagic/oakey-neighbors-candidate';dest=root/'build/strip-landmarks';backup=root/'.bitmagic/city-exterior-backups/oakey-neighbors-2026-11-08';backup.mkdir(parents=True,exist_ok=True)
assert not (backup/'installed.json').exists(),'Already installed; follow checkpoint'
shutil.copytree(root/'build/baked/cells','/tmp/oakey-neighbors-base-cells',dirs_exist_ok=False)
mp=root/'build/optimized/manifest.json';manifest=json.loads(mp.read_text())
for key in ['peppermintHippo','oakeyService','courtyard525']:
 name=key+'-exterior';sourceopt=root/'.bitmagic/optimize/.bitmagic/oakey-neighbors-candidate'/name;destopt=root/'.bitmagic/optimize/build/strip-landmarks'/name
 report='report.json';selected='out.glb'
 r=json.loads((sourceopt/report).read_text());assert r['exitCode']==0 and not r['failed'];assert r['sourceSha256']==hashlib.sha256((cand/(name+'.glb')).read_bytes()).hexdigest()
 for suffix in ['.glb','-collision.json','-runtime-collision.json']:
  p=dest/(name+suffix)
  if p.exists():shutil.copy2(p,backup/p.name)
 shutil.copy2(Path('/Users/janisun/Development/GitFork/vegas-afterlight/build/strip-landmarks')/(name+'.json'),backup/(name+'.json'))
 assert (cand/(name+'-collision.json')).read_bytes()==(dest/(name+'-collision.json')).read_bytes()
 destopt.mkdir(parents=True,exist_ok=True)
 for f in sourceopt.iterdir():
  if f.is_file():shutil.copy2(f,destopt/f.name)
 for suffix in ['.glb','.json']:shutil.copy2(cand/(name+suffix),dest/(name+suffix))
 rel='build/strip-landmarks/'+name+'.glb';out=root/'build/optimized'/rel;out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(sourceopt/selected,out)
 st=(root/rel).stat();manifest['files'][rel]={'size':st.st_size,'modified':st.st_mtime_ns/1000000,'optimized':str(out.relative_to(root)),'sourceSha256':hashlib.sha256((root/rel).read_bytes()).hexdigest(),'bytes':out.stat().st_size,'preset':'level','overrides':[],'variant':'level'}
mp.write_text(json.dumps(manifest,indent=1));shutil.copy2(dest/'version.json',backup/'version.json')
h=hashlib.sha256()
for f in sorted(dest.glob('*.glb')):h.update(f.read_bytes())
h.update((dest/'venues.json').read_bytes());(dest/'version.json').write_text(json.dumps({'revision':h.hexdigest()[:16]}))
(backup/'installed.json').write_text(json.dumps({'keys':['peppermintHippo','oakeyService','courtyard525'],'collisionUnchanged':True}))
print('Installed three optimized candidates; collision unchanged.')
