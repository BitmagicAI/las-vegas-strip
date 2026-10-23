#!/usr/bin/env python3
"""Print the Blender executable to use, or say how to install one and exit 1.

    BLENDER="$(python3 tools/blender-level/find_blender.py)"
    python3 tools/blender-level/find_blender.py --check     # also runs `blender -b --version`

Order: $BLENDER, `blender` on PATH, the macOS app bundle, the Windows install directory.
"""
import glob
import os
import shutil
import subprocess
import sys

CANDIDATES = [
    '/Applications/Blender.app/Contents/MacOS/Blender',
    os.path.expanduser('~/Applications/Blender.app/Contents/MacOS/Blender'),
    '/usr/bin/blender',
    '/snap/bin/blender',
]
INSTALL_HINT = (
    'Blender was not found. `building-levels-in-blender` builds the level with it — install it '
    '(macOS: brew install --cask blender · Debian/Ubuntu: sudo apt install blender · '
    'Windows: winget install BlenderFoundation.Blender) and set BLENDER=<path> if it lives somewhere else. '
    'If installing it is not an option here, take the forge route instead: `bitmagic forge` builds the level '
    'without Blender (see the level rows in choosing-asset-pipelines).'
)


def find_blender() -> str | None:
    env = os.environ.get('BLENDER')
    if env and os.path.isfile(env):
        return env
    on_path = shutil.which('blender')
    if on_path:
        return on_path
    for c in CANDIDATES:
        if os.path.isfile(c):
            return c
    for pattern in ('C:/Program Files/Blender Foundation/Blender*/blender.exe',):
        hits = sorted(glob.glob(pattern))
        if hits:
            return hits[-1]
    return None


def main() -> int:
    path = find_blender()
    if not path:
        print(INSTALL_HINT, file=sys.stderr)
        return 1
    if '--check' in sys.argv:
        probe = subprocess.run([path, '-b', '--version'], capture_output=True, text=True)
        if probe.returncode != 0:
            print(f'{path} exists but `-b --version` failed:\n{probe.stderr.strip()}', file=sys.stderr)
            return 1
        version = next((line for line in probe.stdout.splitlines() if line.startswith('Blender')), '').strip()
        print(f'{version} at {path}', file=sys.stderr)
    print(path)
    return 0


if __name__ == '__main__':
    sys.exit(main())
