"""Machine-specific programs the Python tools call, found on this machine instead of hard-coded.

python312()  - a Python 3.12 (the strip-landmark and city builders need it): $VEGAS_PYTHON312, `uv python find 3.12`,
               then python3.12 on PATH.
bitmagic()   - the Bitmagic CLI: $BITMAGIC_BIN, then `bitmagic` on PATH.
blender()    - Blender 4.2+: $BLENDER, `blender` on PATH, then the macOS app bundle.
ROOT         - the repository root.
"""
import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _first(*candidates):
    for c in candidates:
        if c and Path(c).exists():
            return str(c)
    return None


def python312():
    env = os.environ.get('VEGAS_PYTHON312')
    if env:
        return env
    try:
        found = subprocess.run(['uv', 'python', 'find', '3.12'], capture_output=True, text=True, check=True).stdout.strip()
        if found:
            return found
    except (OSError, subprocess.CalledProcessError):
        pass
    found = shutil.which('python3.12')
    if found:
        return found
    raise SystemExit('Python 3.12 not found: install it (`uv python install 3.12`) or set VEGAS_PYTHON312.')


def bitmagic():
    found = os.environ.get('BITMAGIC_BIN') or shutil.which('bitmagic')
    if not found:
        raise SystemExit('The Bitmagic CLI was not found: `npm i -g @bitmagic/cli`, or set BITMAGIC_BIN.')
    return found


def blender():
    found = _first(os.environ.get('BLENDER'), shutil.which('blender'), '/Applications/Blender.app/Contents/MacOS/Blender')
    if not found:
        raise SystemExit('Blender not found: put `blender` on PATH or set BLENDER.')
    return found
