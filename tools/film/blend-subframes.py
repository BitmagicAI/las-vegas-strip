#!/usr/bin/env python3
"""Motion blur for a take recorded with sub-frames (take "subframes": n; the game ran at 1/(60 n) s a frame):
python3 tools/film/blend-subframes.py <take> [--n 4] [--shutter 3] [--keep]

Every output frame k averages sub-frames n*k .. n*k+shutter-1 (n = 4, shutter = 3: a 270-degree film shutter at 60 fps),
written back into the take's directory under the recorder's own name pattern, so build.py and sheet.py read the take as a
plain 60 fps recording. A take with no PNGs is blended straight from its capture.mp4 (every recorded frame, in order). The sub-frames are deleted afterwards (--keep moves them to <take>/subframes/ instead).
subframes.json in the take records what was done; a take that has one is skipped.
"""
import glob, json, os, re, shutil, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RECS = os.path.join(ROOT, '.bitmagic/trailer/recordings')
args = sys.argv[1:]
def opt(name, default):
    return type(default)(args[args.index('--' + name) + 1]) if '--' + name in args else default
positional, i = [], 0
while i < len(args):
    if args[i] in ('--n', '--shutter'): i += 2; continue
    if not args[i].startswith('--'): positional.append(args[i])
    i += 1
take = positional[0]
n, shutter, keep = opt('n', 4), opt('shutter', 3), '--keep' in args
d = os.path.join(RECS, take)
info = os.path.join(d, 'subframes.json')
if os.path.exists(info): print(take, 'already blended:', open(info).read().strip()); sys.exit(0)
files = sorted(glob.glob(os.path.join(d, '*.png')))
video = os.path.join(d, 'capture.mp4')
if files:
    m = re.match(r'(.*)_(\d{6})\.png$', os.path.basename(files[0]))
    name, first = m.group(1), int(m.group(2))
    source = ['-framerate', str(60 * n), '-start_number', str(first), '-i', os.path.join(d, f'{name}_%06d.png')]
elif os.path.exists(video):
    # no PNGs (a long take whose extraction never finished): blend straight from the recorder's capture video, every
    # recorded frame in order, so nothing needs extracting first
    tl = os.path.join(d, 'timeline.json')
    name = json.load(open(tl)).get('recording', {}).get('name') if os.path.exists(tl) else None
    name = name or 'capture'
    count = int(subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-count_packets', '-show_entries', 'stream=nb_read_packets',
                                '-of', 'csv=p=0', video], capture_output=True, text=True, check=True).stdout.strip())
    files = [video] * count
    source = ['-i', video]
else:
    sys.exit(f'no frames in {d}')
tmp = d + '.blend'
shutil.rmtree(tmp, ignore_errors=True); os.makedirs(tmp)
weights = ' '.join(['1'] * shutter)
vf = f"tmix=frames={shutter}:weights='{weights}',select='eq(mod(n\\,{n})\\,{shutter - 1})'"
cmd = ['ffmpeg', '-v', 'error', *source,
       '-vf', vf, '-fps_mode', 'passthrough', '-start_number', '0', '-compression_level', '3', os.path.join(tmp, f'{name}_%06d.png')]
subprocess.run(cmd, check=True)
out = sorted(glob.glob(os.path.join(tmp, '*.png')))
if len(out) < len(files) // n - 1: sys.exit(f'blend produced {len(out)} frames from {len(files)}; left the sub-frames in place')
if files[0] != video:
    if keep:
        os.makedirs(os.path.join(d, 'subframes'), exist_ok=True)
        for f in files: os.rename(f, os.path.join(d, 'subframes', os.path.basename(f)))
    else:
        for f in files: os.remove(f)
for f in out: os.rename(f, os.path.join(d, os.path.basename(f)))
os.rmdir(tmp)
json.dump({'subframes': n, 'shutter': shutter, 'sourceFrames': len(files), 'frames': len(out), 'fps': 60}, open(info, 'w'))
print(f'{take}: {len(files)} sub-frames -> {len(out)} frames at 60 fps ({shutter}/{n} shutter)')
