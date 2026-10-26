"""Preserve local research and review evidence in the project's local archive.

docs/project-records/archive/ and its index (archive/reference-index.json) are ignored by git: research media and
the owner's material stay on the maintainer's machine.

No network, credentials, session transcripts, game binaries or source mutations.
Original paths and hashes make the copies traceable. Existing archived files are
never deleted when an output disappears; index history is retained separately.
"""
from pathlib import Path
import hashlib, json, shutil

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs/project-records'
EXT = {'.md', '.json', '.txt', '.pdf', '.png', '.jpg', '.jpeg', '.webp', '.html', '.svg'}
EXCLUDED = {'node_modules', '__pycache__', 'python', 'before', 'textures'}

def selected(p):
    rel = p.relative_to(ROOT)
    if p.suffix.lower() not in EXT or any(s in EXCLUDED for s in rel.parts):
        return False
    # Research assets and manifests; archived generated review images are evidence,
    # not third-party sources. Never sweep raw GLBs, blends or terrain buffers.
    return ('reference' in str(rel).lower() or
            ('city-exteriors' in rel.parts and p.suffix.lower() in {'.png','.jpg','.json'}) or
            p.name in {'sources.json', 'plan.json', 'next-plan.json'} or
            ('resort-blocks' in rel.parts and p.name in {
                'walkthrough.json', 'performance.json', 'ownership-report.json',
                'proof.html', 'test-results.json', 'geometry-audit.json', 'geometry-report.json',
                'route-audit.json', 'routes.json', 'version.json','render-cameras.json','runtime-review.json',
                'verify-webgpu.json', 'verify-webgl.json',
                'tower-pool-proof.html','tower-pool-validation.json','tower-pool-verify.json','tower-pool-measurements.json','tower-pool-runtime.json',
                'facade-proof.html', 'facade-validation.json', 'facade-verify.json', 'entrance-proof.html', 'entrance-walkthrough.json', 'arrival-verify.json', 'arrival-cut-report.json',
                'physics-repair-verify.json','dynamic-ground-audit.json','garage-report.json','garage-proof.html','garage-verify.json','tree-placement.json','tree-lod-audit.json','garage-runtime.json','arrival-proof.html','south-arrival-report.json','south-arrival-drive-audit.json','south-arrival-cut.json','lakefront-report.json','lake-city-cut.json','sanctuary-relocation.json','lakefront-validation.json'} ) or
            ('resort-blocks' in rel.parts and p.suffix.lower() in {'.png','.jpg','.jpeg','.svg'}))

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    entries=[]
    old_index=OUT/'archive'/'reference-index.json'
    if old_index.exists():
        old_digest=hashlib.sha256(old_index.read_bytes()).hexdigest()[:12]
        history=OUT/'index-history';history.mkdir(exist_ok=True)
        shutil.copy2(old_index,history/(old_digest+'.json'))
    for p in sorted((ROOT/'build').rglob('*')):
        if not p.is_file() or not selected(p): continue
        rel=p.relative_to(ROOT); dest=OUT/'archive'/rel
        digest=hashlib.sha256(p.read_bytes()).hexdigest()
        dest.parent.mkdir(parents=True,exist_ok=True)
        if not dest.exists() or hashlib.sha256(dest.read_bytes()).hexdigest()!=digest:
            shutil.copy2(p,dest)
        entries.append(dict(original=str(rel),archive=str(dest.relative_to(ROOT)),
                            bytes=p.stat().st_size,sha256=digest,
                            provenance='See adjacent source manifest; visual research, not a licensed game texture.'
                              if ('reference' in str(rel).lower() or p.name.startswith('google-earth-')) else 'Project-generated review evidence.'))
    # Also index the existing tracked source registers, without duplicating them.
    registers=[str(p.relative_to(ROOT)) for p in sorted((ROOT/'tools').rglob('*'))
               if p.is_file() and p.suffix in EXT|{'.py'}
               and ('reference' in p.name.lower() or 'resort-blocks' in p.parts)]
    (OUT/'archive').mkdir(exist_ok=True)
    (OUT/'archive'/'reference-index.json').write_text(json.dumps(dict(
        version=1,sourceRegisters=registers,files=entries),indent=2)+'\n')
    print(f'Archived {len(entries)} reference/evidence files ({sum(v["bytes"] for v in entries)/1e6:.1f} MB).')

if __name__=='__main__':main()
