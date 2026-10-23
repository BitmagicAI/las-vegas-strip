import os,subprocess,sys
from pathlib import Path
env=os.environ.copy()
raise SystemExit(subprocess.call(['bitmagic',*sys.argv[1:],'--original-prompt',Path('build/geographic-strip/request.txt').read_text().rstrip()],env=env))
