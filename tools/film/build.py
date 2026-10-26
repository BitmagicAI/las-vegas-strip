#!/usr/bin/env python3
"""Cut film takes into a finished video: ONE high-quality encode straight from the recorded PNG frames.

    python3 tools/film/build.py tools/film/cuts/<cut>.json [--preview] [--out <path.mp4>]

The cut file:
  {"name": "...", "music": "tools/film/music/bed.mp3" | null, "musicStart": 0, "musicAt": 0, "musicGain": 0,   # musicAt: output s
   "fadeIn": 1.0, "fadeOut": 2.5,   # fadeIn 0: no fade from black, frame 0 is a picture (players and sites use it as the thumbnail)
   "clips": [{"take": "drive-north", "in": 12.5, "dur": 4.0, "x": 0.6, "speed": 1, "label": "..."}],   # in/dur seconds (dur = output); x = crossfade INTO this clip; speed: playback (unblended sub-frame takes)
            # {"still": {"take": "storm-final", "frame": 1152}, "dur": 0.9}: one recorded frame held (a cover picture)
   "logo": {"file": "tools/film/brand/bitmagic-logo-white.png", "corner": "br", "height": 0.05, "margin": 0.022, "opacity": 0.6, "shadow": 0.45},
   "cards": [{"at": 1.5, "dur": 4.0, "style": "title"|"caption"|"stat"|"end", "text": "...", "sub": "..."}],   # at = output seconds; "end" = last N s
   "grain": 0.035}   # optional film grain over the footage

Frames come from .bitmagic/trailer/recordings/<take>/ (exact 60 fps). Output: .bitmagic/film/out/<name>.mp4, 1920x1080, 60 fps,
H.264 High 4:2:0 (x264 slower, CRF 12, BT.709 tagged), AAC 320k, loudness -14 LUFS (two-pass loudnorm, -1 dBTP).
--preview: 960x540, CRF 23, veryfast (to check a cut quickly). --size WxH: another output size (e.g. 1280x720 from real-time takes).
Cards are rendered here (Avenir Next, the game's amber) and faded in/out over the footage.
"""
import json, math, os, subprocess, sys, glob, re
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RECS = os.path.join(ROOT, '.bitmagic/trailer/recordings')
OUTDIR = os.path.join(ROOT, '.bitmagic/film/out')
CARDS = os.path.join(ROOT, '.bitmagic/film/cards')
FPS = 60
AMBER = (233, 197, 138)
FONT = '/System/Library/Fonts/Avenir Next.ttc'

def font(size, index):
    return ImageFont.truetype(FONT, size, index=index)

# Avenir Next.ttc faces are looked up by style name (Medium, Demi Bold, Ultra Light, ...)
def face(name):
    for i in range(12):
        try:
            f = ImageFont.truetype(FONT, 10, index=i)
            if f.getname()[1].lower() == name.lower(): return i
        except OSError: break
    return 0

def tracked(draw, xy, text, fnt, fill, tracking, anchor_center=True):
    widths = [draw.textlength(c, font=fnt) for c in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = xy[0] - total / 2 if anchor_center else xy[0]
    for c, w in zip(text, widths):
        draw.text((x, xy[1]), c, font=fnt, fill=fill)
        x += w + tracking
    return total

def render_card(card, i, W, H):
    os.makedirs(CARDS, exist_ok=True)
    path = os.path.join(CARDS, f'card-{i:02d}-{W}.png')
    img = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    s = W / 1920
    style = card.get('style', 'caption')
    # Type only, no dark band behind it (the owner: the black transparent bands looked bad); a two-step soft shadow below
    # keeps it legible on pale sky. The end card alone darkens the whole frame evenly, as a fade toward the end.
    if style in ('title', 'end'):
        big = font(int(92 * s), face(card.get('face', 'Demi Bold')))
        sub = font(int(28 * s), face('Demi Bold'))
        cy = H * (0.44 if style == 'title' else 0.45)
        if style == 'end':
            img = Image.alpha_composite(img, Image.new('RGBA', (W, H), (6, 5, 8, 120))); d = ImageDraw.Draw(img)
        tracked(d, (W / 2, cy - 60 * s), card['text'], big, (248, 240, 228, 255), 24 * s)
        if card.get('sub'): tracked(d, (W / 2, cy + 66 * s), card['sub'], sub, AMBER + (250,), 9 * s)
    elif style == 'stat':  # a number and what it counts, centred
        big = font(int(124 * s), face('Demi Bold'))
        sub = font(int(30 * s), face('Demi Bold'))
        cy = H * 0.46
        tracked(d, (W / 2, cy - 86 * s), card['text'], big, (248, 240, 228, 255), 10 * s)
        if card.get('sub'): tracked(d, (W / 2, cy + 70 * s), card['sub'], sub, AMBER + (250,), 12 * s)
    else:  # caption: small lower-left location line
        cap = font(int(30 * s), face('Demi Bold'))
        sub = font(int(22 * s), face('Medium'))
        x, y = 92 * s, H - 150 * s
        d.line([(x, y - 14 * s), (x + 56 * s, y - 14 * s)], fill=AMBER + (230,), width=max(1, int(3 * s)))
        tracked(d, (x, y), card['text'], cap, (245, 238, 226, 245), 6 * s, anchor_center=False)
        if card.get('sub'): tracked(d, (x, y + 44 * s), card['sub'], sub, AMBER + (230,), 4 * s, anchor_center=False)
    # soft shadow so the type reads on bright sky: a tight contact shadow and a wide, faint one (type pixels only, so the
    # end card's even dim is not doubled)
    alpha = img.split()[3] if style != 'end' else Image.new('RGBA', (W, H), (0, 0, 0, 0)).split()[3]
    if style == 'end':
        t = Image.new('RGBA', (W, H), (0, 0, 0, 0)); td = ImageDraw.Draw(t)
        tracked(td, (W / 2, cy - 60 * s), card['text'], big, (255, 255, 255, 255), 24 * s)
        if card.get('sub'): tracked(td, (W / 2, cy + 66 * s), card['sub'], sub, (255, 255, 255, 255), 9 * s)
        alpha = t.split()[3]
    out = img
    for blur, strength, dy in ((3 * s, .55, 2 * s), (26 * s, .38, 6 * s)):
        sh = Image.new('RGBA', (W, H), (10, 7, 5, 0)); sh.putalpha(alpha.filter(ImageFilter.GaussianBlur(blur)).point(lambda v, k=strength: int(v * k)))
        out = Image.alpha_composite(Image.alpha_composite(Image.new('RGBA', (W, H), (0, 0, 0, 0)), sh.transform((W, H), Image.AFFINE, (1, 0, 0, 0, 1, -dy))), out)
    out.save(path)
    return path

def render_logo(logo, W, H):
    """The watermark as a full-frame RGBA layer: the white wordmark at `height` (fraction of the frame height) in the corner,
    `margin` (fraction of the width) from the edges, at `opacity`, over a soft dark halo so it reads on pale sky."""
    os.makedirs(CARDS, exist_ok=True)
    path = os.path.join(CARDS, f'logo-{W}.png')
    src = Image.open(os.path.join(ROOT, logo['file'])).convert('RGBA')
    src = src.crop(src.getbbox())
    lh = round(H * logo.get('height', 0.05) / 2) * 2
    lw = round(src.width * lh / src.height)
    mark = src.resize((lw, lh), Image.LANCZOS)
    m = round(W * logo.get('margin', 0.022))
    corner = logo.get('corner', 'br')
    x = m if corner.endswith('l') else W - lw - m
    y = m if corner.startswith('t') else H - lh - m
    op = logo.get('opacity', 0.6)
    layer = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    sh = logo.get('shadow', 0.45)
    if sh > 0:
        a = mark.split()[3].point(lambda v: int(v * min(1, sh * op * 1.4)))
        shadow = Image.new('RGBA', (lw, lh), (0, 0, 0, 0)); shadow.putalpha(a)
        pad = max(4, lh // 3)
        big = Image.new('RGBA', (lw + 2 * pad, lh + 2 * pad), (0, 0, 0, 0)); big.paste(shadow, (pad, pad))
        big = big.filter(ImageFilter.GaussianBlur(max(1.5, lh * 0.06)))
        layer.alpha_composite(big, (x - pad + 2, y - pad + 3))
    tinted = mark.copy(); tinted.putalpha(mark.split()[3].point(lambda v: int(v * op)))
    layer.alpha_composite(tinted, (x, y))
    layer.save(path)
    return path

def take_fps(take):
    """Frames a second of a recording: 60, or 60 x sub-frames for a take recorded with unblended sub-frames."""
    f = os.path.join(RECS, take, 'subframes.json')
    if os.path.exists(f):
        j = json.load(open(f))
        if j.get('blended') is False: return int(j['fps'])
    return FPS

def frames_of(take):
    d = os.path.join(RECS, take)
    files = sorted(glob.glob(os.path.join(d, '*.png')))
    if not files: sys.exit(f'no frames for take {take} in {d}')
    m = re.match(r'(.*)_(\d{6})\.png$', os.path.basename(files[0]))
    return os.path.join(d, m.group(1) + '_%06d.png'), int(m.group(2)), len(files)

def run(cmd, **kw):
    print('  $', ' '.join(cmd[:6]), '...' if len(cmd) > 6 else '')
    return subprocess.run(cmd, check=True, **kw)

def main():
    args = sys.argv[1:]
    cut = json.load(open(args[0]))
    preview = '--preview' in args
    W, H = (960, 540) if preview else (1920, 1080)
    if '--size' in args: W, H = map(int, args[args.index('--size') + 1].split('x'))
    name = cut['name'] + ('-preview' if preview else '')
    out = args[args.index('--out') + 1] if '--out' in args else os.path.join(OUTDIR, name + '.mp4')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    clips = cut['clips']
    inputs, filters = [], []
    # ── footage: each clip is an image2 input trimmed to its frames
    t = 0.0; timeline = []
    for i, c in enumerate(clips):
        if 'still' in c:
            pattern, first, count = frames_of(c['still']['take'])
            frame = c['still']['frame']
            if frame >= count: sys.exit(f"clip {i}: {c['still']['take']} has no frame {frame}")
            n = int(round(c['dur'] * FPS))
            inputs += ['-loop', '1', '-framerate', str(FPS), '-t', f"{c['dur']:.4f}", '-i', pattern % (first + frame)]
            filters.append(f'[{i}:v]setpts=N/({FPS}*TB),trim=end_frame={n},setpts=PTS-STARTPTS,scale={W}:{H}:flags=lanczos,format=gbrp,fps={FPS},settb=1/{FPS}[c{i}]')
            x = c.get('x', 0) if i else 0
            start = t - x
            timeline.append((start, c)); t = start + c['dur']
            continue
        pattern, first, count = frames_of(c['take'])
        # a take recorded with unblended sub-frames has more frames a second (subframes.json `fps`); a clip's `speed`
        # plays it faster by taking every k-th real frame (1.5x of a 120 fps take = every 3rd), never blending
        F = take_fps(c['take']); step = F * c.get('speed', 1) / FPS
        if abs(step - round(step)) > 1e-6 or step < 1: sys.exit(f"clip {i} ({c['take']}): speed {c.get('speed', 1)} needs a whole frame step at {F} fps")
        step = int(round(step))
        fin = first + int(round(c['in'] * F)); n = int(round(c['dur'] * FPS))
        if fin + n * step > first + count: sys.exit(f"clip {i} ({c['take']}) wants frames {fin}..{fin + n * step} but the take has {count}")
        inputs += ['-framerate', str(F), '-start_number', str(fin), '-i', pattern]
        # recordings at another size (720p previews, supersampled finals) are scaled to the output with Lanczos
        scale = f'scale={W}:{H}:flags=lanczos,'
        pick = f"select='not(mod(n\\,{step}))'," if step > 1 else ''
        filters.append(f'[{i}:v]{pick}setpts=N/({FPS}*TB),trim=end_frame={n},setpts=PTS-STARTPTS,{scale}format=gbrp,fps={FPS},settb=1/{FPS}[c{i}]')
        x = c.get('x', 0) if i else 0
        start = t - x
        timeline.append((start, c)); t = start + c['dur']
    total = t
    # join: hard cuts concat, crossfades xfade
    cur = 'c0'; length = clips[0]['dur']
    for i in range(1, len(clips)):
        x = clips[i].get('x', 0); nxt = f'j{i}'
        if x > 0:
            filters.append(f'[{cur}][c{i}]xfade=transition=fade:duration={x}:offset={length - x:.4f}[{nxt}]')
            length = length - x + clips[i]['dur']
        else:
            filters.append(f'[{cur}][c{i}]concat=n=2:v=1:a=0,settb=1/{FPS}[{nxt}]')
            length += clips[i]['dur']
        cur = nxt
    # a fine, moving film grain over the footage only (cut 'grain', 0..~0.1; under the cards and the watermark)
    if cut.get('grain'):
        g = max(1, round(cut['grain'] * 180))
        filters.append(f'[{cur}]format=yuv444p,noise=c0s={g}:c0f=t+u,format=gbrp[grain]')
        cur = 'grain'
    # fades from / to black
    fi, fo = cut.get('fadeIn', 1.0), cut.get('fadeOut', 2.5)
    # ── cards
    k = len(clips)
    for j, card in enumerate(cut.get('cards', [])):
        png = render_card(card, j, W, H)
        dur = card['dur']; at = total - dur - card.get('endPad', 0.4) if card['at'] == 'end' else card['at']
        inputs += ['-loop', '1', '-framerate', str(FPS), '-t', f'{dur:.3f}', '-i', png]
        fd = card.get('fade', 0.7)
        filters.append(f'[{k}:v]format=rgba,fade=t=in:st=0:d={fd}:alpha=1,fade=t=out:st={dur - fd:.3f}:d={fd}:alpha=1,setpts=PTS-STARTPTS+{at:.3f}/TB[k{j}]')
        filters.append(f"[{cur}][k{j}]overlay=0:0:eof_action=pass:enable='between(t,{at:.3f},{at + dur:.3f})'[o{j}]")
        cur = f'o{j}'; k += 1
    # the Bitmagic watermark, above the cards, for the whole video
    if cut.get('logo'):
        png = render_logo(cut['logo'], W, H)
        inputs += ['-loop', '1', '-framerate', str(FPS), '-t', f'{total:.3f}', '-i', png]
        filters.append(f'[{k}:v]format=rgba,setpts=PTS-STARTPTS[lg]')
        filters.append(f'[{cur}][lg]overlay=0:0:eof_action=pass[wm]')
        cur = 'wm'; k += 1
    # fades from / to black over everything (footage, cards and the watermark)
    fade_in = f'fade=t=in:st=0:d={fi},' if fi > 0 else ''
    filters.append(f'[{cur}]{fade_in}fade=t=out:st={total - fo:.4f}:d={fo}[faded]')
    cur = 'faded'
    # BT.709 limited range for 4:2:0
    # (setparams: the grain's format round trip drops the frames' colour tags, and ffmpeg then writes no primaries/transfer)
    filters.append(f'[{cur}]scale=out_color_matrix=bt709:out_range=tv:flags=bicubic+accurate_rnd+full_chroma_int,format=yuv420p,'
                   f'setparams=color_primaries=bt709:color_trc=iec61966-2-1:colorspace=bt709:range=tv[v]')
    # ── music
    audio_map = []
    if cut.get('music'):
        music = os.path.join(ROOT, cut['music'])
        inputs += ['-ss', str(cut.get('musicStart', 0)), '-i', music]
        at = cut.get('musicAt', 0)
        delay = f'adelay={round(at * 1000)}:all=1,' if at > 0 else ''
        fade_in = f'afade=t=in:st=0:d={min(fi, .5)},' if fi > 0 else ''
        a = f"[{k}:a]atrim=0:{total - at:.3f},asetpts=PTS-STARTPTS,{delay}{fade_in}afade=t=out:st={total - fo - .5:.3f}:d={fo + .5},volume={cut.get('musicGain', 0)}dB"
        # loudness: measure, then normalise once to -14 LUFS / -1 dBTP
        if not preview:
            meas = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-ss', str(cut.get('musicStart', 0)), '-i', music, '-filter_complex',
                                   a.replace(f'[{k}:a]', '[0:a]') + ',loudnorm=I=-14:TP=-1:LRA=11:print_format=json', '-f', 'null', '-'],
                                  capture_output=True, text=True)
            js = json.loads(meas.stderr[meas.stderr.rindex('{'):meas.stderr.rindex('}') + 1])
            a += (f",loudnorm=I=-14:TP=-1:LRA=11:measured_I={js['input_i']}:measured_TP={js['input_tp']}:measured_LRA={js['input_lra']}"
                  f":measured_thresh={js['input_thresh']}:offset={js['target_offset']}:linear=true")
        filters.append(a + ',aresample=48000[a]')
        audio_map = ['-map', '[a]', '-c:a', 'aac', '-b:a', '320k' if not preview else '160k']
    graph = os.path.join(OUTDIR, name + '.filtergraph')
    open(graph, 'w').write(';\n'.join(filters))
    venc = (['-c:v', 'libx264', '-preset', 'veryfast', '-crf', str(cut.get('previewCrf',23))] if preview else
            ['-c:v', 'libx264', '-preset', 'slower', '-crf', '12', '-profile:v', 'high', '-x264-params', 'aq-mode=3'])
    cmd = ['ffmpeg', '-y', '-hide_banner', '-loglevel', 'warning', '-stats', *inputs, '-/filter_complex', graph, '-map', '[v]', *audio_map,
           *venc, '-pix_fmt', 'yuv420p', '-r', str(FPS), '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'iec61966-2-1', '-color_range', 'tv',
           '-movflags', '+faststart', '-t', f'{total:.3f}', out]
    print(f'{name}: {len(clips)} clips, {total:.2f} s → {out}')
    run(cmd)
    json.dump({'clips': [{'at': round(s, 3), 'take': c['take'] if 'take' in c else c['still']['take'], 'in': c.get('in', c.get('still', {}).get('frame', 0) / FPS),
                          'dur': c['dur'], 'label': c.get('label', '')} for s, c in timeline], 'total': total},
              open(out.replace('.mp4', '.timeline.json'), 'w'), indent=1)
    print('done', out)

if __name__ == '__main__':
    main()
