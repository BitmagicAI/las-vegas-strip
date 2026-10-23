"""Mix the info video's soundtrack (after the character-pipeline video's mix.py): narration lines (bitmagic generate speech,
narrator voice) at their timeline.json starts, sound effects at the events story.js reports (events.json; the effect files
are the character video's generated set, plus tick/joint/bars/win/boom/stamp synthesised here), the Vegas film's music bed
under it all (looped, ducked under the voice), loudness-normalised to -16 LUFS, 48 kHz 24-bit WAV.
python3 tools/info-video/mix.py  ->  .bitmagic/info-video/audio/soundtrack.wav
"""
import json
import subprocess
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
AUD = ROOT / '.bitmagic/info-video/audio'
SR = 48000
TL = json.loads((HERE / 'timeline.json').read_text())
EV = json.loads((HERE / 'events.json').read_text())
N = int((TL['total'] + 1.0) * SR)


def decode(p):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(p), '-f', 'f32le', '-ac', '2', '-ar', str(SR), '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).reshape(-1, 2).copy()


def peak_norm(x, db=-6.0):
    m = np.abs(x).max() or 1.0
    return x * (10 ** (db / 20) / m)


def env(n, a, d):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d)


def tone(f, dur, a=.004, d=.08, harm=(1, .25, .08)):
    t = np.arange(int(dur * SR)) / SR
    w = sum(h * np.sin(2 * np.pi * f * (k + 1) * t) for k, h in enumerate(harm))
    return w * env(len(t), a, d)


def stereo(x):
    return np.stack([x, x], 1).astype(np.float32)


def resample(x, speed):
    n = int(len(x) / speed)
    idx = np.linspace(0, len(x) - 1, n)
    return np.stack([np.interp(idx, np.arange(len(x)), x[:, c]) for c in range(2)], 1).astype(np.float32)


rng = np.random.default_rng(3)
SFX = {p.stem: peak_norm(decode(p)) for p in sorted((AUD / 'sfx').glob('*.mp3'))}
click = rng.standard_normal(int(.004 * SR)) * env(int(.004 * SR), .0002, .0012)
SFX['tick'] = peak_norm(stereo(np.concatenate([click, np.zeros(int(.03 * SR))])[:int(.034 * SR)] * .6 + tone(2600, .034, .0005, .012, (1,)) * .5))
SFX['joint'] = peak_norm(resample(SFX['pop'], 1.6), -8)
bars = np.zeros(int(1.0 * SR))
for i, f in enumerate([659.3, 784.0, 880.0, 1046.5, 1174.7, 1318.5]):
    b = tone(f, .2, .003, .06); o = int(i * .085 * SR); bars[o:o + len(b)] += b
SFX['bars'] = peak_norm(stereo(bars))
win = np.zeros(int(2.0 * SR))
for i, f in enumerate([1046.5, 1318.5, 1568.0, 2093.0]):
    b = tone(f, 1.4, .002, .45, (1, .4, .12, .05)); o = int(i * .09 * SR); win[o:o + len(b)] += b
sp = SFX['sparkle']; win2 = stereo(win); win2[:len(sp)] += sp[:len(win2)] * .6
SFX['win'] = peak_norm(win2)
t = np.arange(int(2.6 * SR)) / SR
f = 58 * np.exp(-t * .6) + 32
boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * env(len(t), .004, .9)
noise = np.convolve(rng.standard_normal(len(t)), np.ones(240) / 240, 'same') * env(len(t), .002, .35) * 3
SFX['boom'] = peak_norm(stereo(boom + noise), -3)
lk = resample(SFX['lock'], .7); th = stereo(tone(85, .25, .001, .06, (1, .3)))
st = np.zeros((max(len(lk), len(th)), 2), np.float32); st[:len(lk)] += lk; st[:len(th)] += th * .9
SFX['stamp'] = peak_norm(st, -4)
SFX['crowd'] = SFX['reveal'] * .7

voice = np.zeros((N, 2), np.float32)
for L in TL['lines']:
    x = decode(AUD / f"lines/{L['id']}.mp3")
    o = int(L['start'] * SR); voice[o:o + len(x)] += x[:N - o]
fx = np.zeros((N, 2), np.float32)
missing = set()
for e in EV:
    x = SFX.get(e['sfx'])
    if x is None:
        missing.add(e['sfx']); continue
    o = int(e['t'] * SR)
    if o >= N: continue
    fx[o:o + len(x)] += x[:N - o] * e['gain'] * .62
# duck the effects 5 dB under speech (60 ms attack, 250 ms release)
lvl = np.abs(voice).max(1)
win_n = int(.03 * SR)
lvl = np.convolve(lvl, np.ones(win_n) / win_n, 'same')
active = (lvl > .02).astype(np.float32)
g = np.empty_like(active); cur = 0.0
up, down = 1 - np.exp(-1 / (.06 * SR)), 1 - np.exp(-1 / (.25 * SR))
for i in range(len(active)):
    cur += (active[i] - cur) * (up if active[i] > cur else down); g[i] = cur
fx *= (1 - g * (1 - 10 ** (-5 / 20)))[:, None]
bed = decode(ROOT / '.bitmagic/film/music/bed-v1.mp3'); xf = int(2.0 * SR)
music = np.zeros((N, 2), np.float32); pos = 0
while pos < N:
    seg = bed.copy(); seg[:xf] *= np.linspace(0, 1, xf)[:, None]; seg[-xf:] *= np.linspace(1, 0, xf)[:, None]
    n = min(len(seg), N - pos); music[pos:pos + n] += seg[:n]; pos += len(seg) - xf
music *= 10 ** (-17 / 20) * (1 - g * (1 - 10 ** (-9 / 20)))[:, None]
fade = np.ones(N, np.float32); fo = int(3.0 * SR); end = int(TL['total'] * SR)
fade[max(0, end - fo):end] = np.linspace(1, 0, min(fo, end)); fade[end:] = 0; music *= fade[:, None]
mixd = voice + fx + music
# gentle peak limiting
pk = np.abs(mixd).max()
if pk > .98:
    mixd = np.tanh(mixd * 1.1) / np.tanh(1.1)
tmp = AUD / 'mix-raw.wav'
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'f32le', '-ar', str(SR), '-ac', '2', '-i', '-', '-c:a', 'pcm_f32le', str(tmp)], input=mixd.astype(np.float32).tobytes(), check=True)
# two-pass loudness normalisation to -16 LUFS, true peak -1.5 dB
m = subprocess.run(['ffmpeg', '-hide_banner', '-i', str(tmp), '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'], capture_output=True, text=True).stderr
j = json.loads(m[m.rindex('{'):m.rindex('}') + 1])
af = (f"loudnorm=I=-16:TP=-1.5:LRA=11:measured_I={j['input_i']}:measured_TP={j['input_tp']}:measured_LRA={j['input_lra']}:"
      f"measured_thresh={j['input_thresh']}:offset={j['target_offset']}:linear=true")
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(tmp), '-af', af, '-ar', str(SR), '-c:a', 'pcm_s24le', str(AUD / 'soundtrack.wav')], check=True)
tmp.unlink()
print('events', len(EV), 'missing', sorted(missing), 'input LUFS', j['input_i'], '-> -16')
