import json,subprocess
from pathlib import Path
root=Path('docs/project-records/oakey-neighbors-refinement')
commands=[r['command'] for r in json.loads(Path('docs/project-records/cosmopolitan-terraces-refinement/local-checks.json').read_text())]
commands[6:7]=[['node','tools/city-exteriors/test-'+s+'.mjs'] for s in ['peppermint-hippo','oakey-service-compound','courtyard-525']]
commands[9:9]=[['node','tools/city-exteriors/stairs-courtyard-525.mjs']]
results=[]
for i,cmd in enumerate(commands):
 p=root/('final-check-'+str(i)+'.txt')
 with p.open('w') as f:r=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT)
 results.append({'command':cmd,'exitCode':r.returncode,'log':str(p)})
 print(i,r.returncode,cmd,flush=True)
 (root/'local-checks.json').write_text(json.dumps(results,indent=2)+'\n')
 if r.returncode:raise SystemExit(r.returncode)
