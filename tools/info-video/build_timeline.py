"""Place the narration lines on one master timeline and find each line's speech segments (between pauses), so the story can
hit individual words (after the character-pipeline video's build_timeline.py). Reads tools/info-video/script.json and
.bitmagic/info-video/audio/lines/NN.mp3; writes tools/info-video/timeline.json.
python3 tools/info-video/build_timeline.py"""
import json, re, subprocess
from pathlib import Path
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
LINES = ROOT / '.bitmagic/info-video/audio/lines'
LEAD = 3.6            # the cover holds, then the first word
GAP = 0.7
GAPS = {'02': 1.4, '04': 2.6, '05': 1.2, '08': 1.2, '09': 1.0, '11': 1.4, '13': 1.0, '14': 1.2, '14b': 1.0, '15': 1.4}   # scene changes breathe longer
TAIL = 4.0


def duration(p):
    return float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', str(p)], capture_output=True, text=True).stdout)


def segments(p, dur):
    log = subprocess.run(['ffmpeg', '-hide_banner', '-i', str(p), '-af', 'silencedetect=noise=-38dB:d=0.11', '-f', 'null', '-'], capture_output=True, text=True).stderr
    starts = [float(x) for x in re.findall(r'silence_start: ([\d.]+)', log)]; ends = [float(x) for x in re.findall(r'silence_end: ([\d.]+)', log)]
    segs, at = [], 0.0
    for s, e in zip(starts, ends):
        if s - at > 0.05: segs.append([round(at, 3), round(s, 3)])
        at = e
    if dur - at > 0.08: segs.append([round(at, 3), round(dur, 3)])
    return segs


script = json.loads((HERE / 'script.json').read_text())
out, t = [], LEAD
for i, line in enumerate(script['lines']):
    if i: t += GAPS.get(line['id'], GAP)
    p = LINES / f"{line['id']}.mp3"; d = duration(p)
    out.append(dict(id=line['id'], scene=line['scene'], start=round(t, 3), dur=round(d, 3), text=line['text'],
                    segs=[[round(t + a, 3), round(t + b, 3)] for a, b in segments(p, d)]))
    t += d
total = round(t + TAIL, 3)
(HERE / 'timeline.json').write_text(json.dumps(dict(fps=60, total=total, lines=out), indent=1))
for L in out: print(L['id'], L['scene'], L['start'], L['dur'], len(L['segs']), [s[0] for s in L['segs']])
print('total', total, 'frames', round(total * 60))
