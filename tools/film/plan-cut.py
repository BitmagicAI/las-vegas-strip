#!/usr/bin/env python3
"""Writes the showcase cut, laid on the music's beat grid: `python3 tools/film/plan-cut.py` writes version 2
(tools/film/cuts/vegas-tour-v2.json), `python3 tools/film/plan-cut.py v3` version 3 (vegas-tour-v3.json: the owner's
feedback on v2, faster editing, spline flights, motion blur, no subtitle under the title), `v45 [--suffix -rt]` the
45-second clip, `tour [--suffix -rt]` the continuous-camera film (one take, tools/film/make-tour.py: cuts/vegas-continuous*.json).

Each shot is (take, in seconds, length in BEATS of the bed, crossfade-in seconds, caption or None). Cuts land on beats
(.bitmagic/film/music/beats.json, 99.6 bpm); the opening shot runs from 0 to the first chosen downbeat.
Run: python3 tools/film/plan-cut.py && python3 tools/film/build.py tools/film/cuts/vegas-tour.json [--preview]
"""
import json, os, sys
V3 = sys.argv[1:2] == ['v3']
V45 = sys.argv[1:2] == ['v45']                 # the 45-second clip; `--suffix -rt` builds it from the real-time takes
SUFFIX = sys.argv[sys.argv.index('--suffix') + 1] if '--suffix' in sys.argv else ''
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
beats = json.load(open(os.path.join(ROOT, '.bitmagic/film/music/beats.json')))
B = 60 / beats['bpm']                      # one beat, s
bars = beats['barTimes']                   # downbeats

# section by section (music: quiet intro to ~17.7 s, drums from bar 7, louder ~92-135 s, outro after ~136 s)
OPEN = [('aerial-open', 1.0, None, 0, None)]          # until the drive starts (bar 5)
SHOTS = [
    # the drive, filmed from the drone: calm start, the beat drops on the high trailing shot
    ('drone-north', 0.5, 8, 0.8, None),
    ('drone-north', 9.5, 8, 0, ('THE LAS VEGAS STRIP', 'NORTHBOUND')),
    ('lake-glide', 1.0, 8, 0, ('BELLAGIO', 'THE FOUNTAIN LAKE')),
    ('drone-north', 28.0, 6, 0, None),
    ('drone-north', 33.5, 6, 0, None),
    ('drone-north', 55.0, 6, 0, None),
    ('drone-north', 86.0, 6, 0, None),
    ('drone-south', 17.0, 6, 0, ('CITYCENTER', 'SOUTHBOUND')),
    ('drone-south', 73.0, 8, 0, None),
    # casinos and lobbies ("38 RESORTS" over the first)
    ('caesars-approach', 1.0, 4, 0, ('@stat', '38', 'RESORTS')),
    ('casino-caesars', 1.0, 8, 0, ('CAESARS PALACE', None)),
    ('lobby-venetian', 1.0, 12, 0, ('THE VENETIAN', None)),
    ('casino-flamingo', 2.0, 6, 0, ('FLAMINGO', None)),
    ('lobby-bellagio', 1.0, 6, 0, ('BELLAGIO', None)),
    ('casino-planet-hollywood', 2.0, 4, 0, ('PLANET HOLLYWOOD', None)),
    ('lobby-palazzo', 3.5, 8, 0, ('THE PALAZZO', None)),
    # hotel rooms ("30,892 HOTEL ROOMS" over the first kick), the last held at the window
    ('kick-caesars', 3.4, 8, 0, ('@stat', '30,892', 'HOTEL ROOMS')),
    ('kick-cosmo', 1.3, 8, 0, ('THE COSMOPOLITAN', 'LEVEL 41')),
    ('kick-cosmo', 9.0, 6, 0.4, None),
    ('kick-bellagio', 1.6, 16, 0, ('BELLAGIO', 'LEVEL 21')),
    ('eiffel-deck', 1.0, 8, 0.6, ('EIFFEL TOWER', '140 M')),
    # the coaster, on the climax
    ('coaster-ride', 1.5, 4, 0, ('THE BIG APPLE COASTER', 'NEW YORK-NEW YORK')),
    ('coaster-ride', 70.0, 4, 0, None),
    ('coaster-ride', 89.0, 6, 0, None),
    ('coaster-ride', 112.0, 8, 0, None),
    ('coaster-ride', 118.5, 4, 0, None),
    ('coaster-ride', 132.5, 6, 0, None),
    ('coaster-ride', 144.0, 8, 0, None),
    ('coaster-ride', 152.5, 6, 0, None),
]
CLOSE = ('aerial-close', 0.5, 1.0)        # take, in, crossfade; runs to the end
END = 148.0                               # output length (music fades over the last 2.5 s)
if V3:
    # version 3: the opener is the low flight up the Strip; the rest cuts about twice as often, on the flights and the
    # drone drives (2026-10-08 takes, recorded with 4 sub-frames a frame: motion blur)
    OPEN = [('fly-strip', 0.3, None, 0, None)]
    SHOTS = [
        ('fly-paris', 1.0, 10, 0, ('PARIS', 'THROUGH THE ARC DE TRIOMPHE')),
        ('drone-north2', 0.5, 6, 0, ('THE LAS VEGAS STRIP', 'NORTHBOUND')),
        ('drone-north2', 17.0, 8, 0, None),
        ('lake-glide', 0.8, 8, 0, ('BELLAGIO', 'THE LAKE')),
        ('drone-north2', 30.0, 6, 0, None),
        ('drone-north2', 38.0, 6, 0, None),
        ('drone-north2', 51.0, 6, 0, None),
        ('fly-highroller', 1.0, 18, 0, ('HIGH ROLLER', 'THE LINQ')),
        ('drone-north2', 107.5, 8, 0, None),
        ('drone-south2', 0.5, 6, 0, ('CITYCENTER', 'SOUTHBOUND')),
        ('drone-south2', 20.5, 6, 0, None),
        ('fly-sphere', 1.2, 16, 0, ('SPHERE', None)),
        ('drone-south2', 44.5, 6, 0, None),
        # casinos and lobbies at a run ("38 RESORTS" over the first)
        ('casino-caesars', 1.0, 6, 0, ('@stat', '38', 'RESORTS')),
        ('lobby-venetian', 1.0, 6, 0, ('THE VENETIAN', None)),
        ('casino-flamingo', 1.5, 4, 0, ('FLAMINGO', None)),
        ('lobby-bellagio', 1.0, 5, 0, ('BELLAGIO', None)),
        ('casino-planet-hollywood', 1.5, 4, 0, ('PLANET HOLLYWOOD', None)),
        ('crystals-atrium', 1.0, 5, 0, ('CRYSTALS', 'CITYCENTER')),
        # hotel rooms ("30,892 HOTEL ROOMS" over the first kick), the last held at the window
        ('kick-caesars', 3.4, 8, 0, ('@stat', '30,892', 'HOTEL ROOMS')),
        ('kick-cosmo', 1.3, 7, 0, ('THE COSMOPOLITAN', 'LEVEL 41')),
        ('kick-bellagio', 1.6, 12, 0, ('BELLAGIO', 'LEVEL 21')),
        # the coaster, on the loud stretch
        ('coaster-ride', 1.5, 4, 0, ('THE BIG APPLE COASTER', 'NEW YORK-NEW YORK')),
        ('coaster-ride', 70.0, 4, 0, None),
        ('coaster-ride', 89.0, 6, 0, None),
        ('coaster-ride', 112.0, 6, 0, None),
        ('coaster-ride', 118.5, 4, 0, None),
        ('coaster-ride', 132.5, 6, 0, None),
        ('coaster-ride', 144.0, 7, 0, None),
    ]
    CLOSE = ('fly-paris', 8.0, 1.0)       # up and around the Eiffel Tower, the end card over it

TOUR = sys.argv[1:2] == ['tour']
if TOUR:
    # 2026-10-08 after preview 2: one continuous camera (tools/film/make-tour.py), no cuts: the whole take, the drums under it
    take = json.load(open(os.path.join(ROOT, 'tools/film/takes/tour.json')))
    MUSIC_START = bars[7]
    cut = {'name': 'vegas-afterlight-continuous' + SUFFIX, 'music': '.bitmagic/film/music/bed-v1.mp3', 'musicStart': round(MUSIC_START, 4),
           'fadeIn': 0.8, 'fadeOut': 2.0,
           'logo': {'file': 'tools/film/brand/bitmagic-logo-white.png', 'corner': 'br', 'height': 0.05, 'margin': 0.022, 'opacity': 0.6, 'shadow': 0.45},
           'clips': [{'take': 'tour' + SUFFIX, 'in': 0.0, 'dur': round(take['seconds'] - 0.05, 3), 'label': 'one continuous camera'}],
           'cards': [{'at': 0.5, 'dur': 3.2, 'style': 'title', 'text': 'VEGAS: AFTERLIGHT', 'fade': 0.8},
                     {'at': 'end', 'dur': 4.2, 'style': 'end', 'text': 'VEGAS: AFTERLIGHT', 'sub': 'THE STRIP IS YOURS', 'fade': 0.9, 'endPad': 0.4}]}
    out = os.path.join(ROOT, 'tools/film/cuts', f'vegas-continuous{SUFFIX}.json')
    json.dump(cut, open(out, 'w'), indent=1); print(out, cut['clips'][0]['dur'], 's'); sys.exit(0)

if V45:
    # 2026-10-08 after the owner's v3 review: one move per shot, crisp frames, previewed in real time first
    MUSIC_START = bars[7]                  # where the drums come in
    rel = [b - MUSIC_START for b in beats['beatTimes'] if b >= MUSIC_START]
    # take, in (s), length (beats, or ('s', seconds) for the run's speed-ramp pieces), playback speed
    SHOTS45 = [
        ('fly-paris', 1.0, 5, 1),          # over the podium and through the Arc de Triomphe
        ('drive45b', 3.5, 4, 1),           # rising behind the jeep through the turn onto the Boulevard
        ('drive45b', 12.0, 4, 1),          # alongside: Paris and the Eiffel Tower beyond it
        ('lake-glide', 1.0, 3, 1),         # low over the Bellagio lake
        ('drive45b', 19.0, 3, 1),          # in front, pulling back as it comes at us
        ('fly-highroller', 2.0, 4, 1),     # across the High Roller's face
        ('fly-sphere', 3.0, 4, 1),         # round the Sphere
        # one continuous camera run into the Cromwell (hotel-run, 120 frames a second): street, under the bridge stair,
        # through the portal (1x), the casino hall (2x), the lobby and two storeys of stairs (1.5x), the corridor and
        # room (1.5x), the window and the Eiffel Tower (1x)
        ('hotel-run', 0.4, ('s', 3.4), 1),
        ('hotel-run', 3.8, ('s', 2.2), 2),
        ('hotel-run', 8.2, ('s', 1.6), 1.5),
        ('hotel-run', 10.6, ('s', 5.4), 1.5),
        ('hotel-run', 18.7, ('s', 3.07), 1.5),
        ('hotel-run', 23.305, 'fill-run', 1),
        ('lobby-venetian', 1.5, 3, 1),     # the Venetian's frescoed lobby
        ('coaster-ride', 70.0, 3, 1),      # the Big Apple Coaster
        ('coaster-ride', 89.0, 3, 1),
        ('coaster-ride', 112.0, 3, 1),
    ]
    RUN_BEATS = 30                         # the whole run, snapped to the beat
    CLIP_END = 45.0
    clips, t, k = [], 0.0, 0
    run_used = sum(x[2][1] for x in SHOTS45 if x[0] == 'hotel-run' and isinstance(x[2], tuple))
    for take, tin, length, speed in SHOTS45:
        if length == 'fill-run': dur = run_target - run_used      # the window: whatever the run's beats leave
        elif isinstance(length, tuple): dur = length[1]
        else: dur = rel[k + length] - rel[k]; k += length
        if take == 'hotel-run' and tin == 0.4:      # the run starts on a beat; its pieces together last RUN_BEATS beats
            run_target = rel[k + RUN_BEATS] - rel[k]; k += RUN_BEATS
        clip = {'take': take + SUFFIX, 'in': tin, 'dur': round(dur, 4), 'label': f'{take} @{tin}' + (f' x{speed}' if speed != 1 else '')}
        if speed != 1: clip['speed'] = speed
        clips.append(clip); t += dur
    clips.append({'take': 'fly-paris' + SUFFIX, 'in': 14.0, 'dur': round(CLIP_END - t, 4), 'label': 'up around the Eiffel Tower'})
    cards = [{'at': 0.5, 'dur': 3.2, 'style': 'title', 'text': 'VEGAS: AFTERLIGHT', 'fade': 0.8},
             {'at': 'end', 'dur': 4.2, 'style': 'end', 'text': 'VEGAS: AFTERLIGHT', 'sub': 'THE STRIP IS YOURS', 'fade': 0.9, 'endPad': 0.4}]
    cut = {'name': 'vegas-afterlight-45s' + SUFFIX, 'music': '.bitmagic/film/music/bed-v1.mp3', 'musicStart': round(MUSIC_START, 4),
           'fadeIn': 0.8, 'fadeOut': 2.0,
           'logo': {'file': 'tools/film/brand/bitmagic-logo-white.png', 'corner': 'br', 'height': 0.05, 'margin': 0.022, 'opacity': 0.6, 'shadow': 0.45},
           'clips': clips, 'cards': cards}
    out = os.path.join(ROOT, 'tools/film/cuts', f'vegas-45s{SUFFIX}.json')
    json.dump(cut, open(out, 'w'), indent=1)
    print(out, len(clips), 'clips;', ', '.join(f"{c['label']} {c['dur']:.1f}s" for c in clips))
    sys.exit(0)

clips, cards = [], []
start = bars[5]                           # first cut
clips.append({'take': OPEN[0][0], 'in': OPEN[0][1], 'dur': round(start, 4), 'label': 'opener'})
t = start
for take, tin, nbeats, x, cap in SHOTS:
    dur = nbeats * B
    clips.append({'take': take, 'in': tin, 'dur': round(dur + x, 4), 'x': x, 'label': f'{take} @{tin}'})
    if cap and cap[0] == '@stat': cards.append({'at': round(t + 0.25, 3), 'dur': 2.9, 'style': 'stat', 'text': cap[1], 'sub': cap[2], 'fade': 0.45})
    elif cap: cards.append({'at': round(t + 0.35, 3), 'dur': 3.0, 'style': 'caption', 'text': cap[0], **({'sub': cap[1]} if cap[1] else {})})
    t += dur
take, tin, x = CLOSE
clips.append({'take': take, 'in': tin, 'dur': round(END - t + x, 4), 'x': x, 'label': 'closer'})
cards.insert(0, {'at': 1.4, 'dur': 8.0, 'style': 'title', 'text': 'VEGAS: AFTERLIGHT', 'fade': 1.2})
cards.append({'at': 'end', 'dur': 5.5, 'style': 'end', 'text': 'VEGAS: AFTERLIGHT', 'sub': 'THE STRIP IS YOURS', 'fade': 1.0, 'endPad': 0.6})
cut = {'name': 'vegas-afterlight-tour-v3' if V3 else 'vegas-afterlight-tour-v2', 'music': '.bitmagic/film/music/bed-v1.mp3', 'musicStart': 0, 'fadeIn': 1.2, 'fadeOut': 2.5,
       'logo': {'file': 'tools/film/brand/bitmagic-logo-white.png', 'corner': 'br', 'height': 0.05, 'margin': 0.022, 'opacity': 0.6, 'shadow': 0.45},
       'clips': clips, 'cards': cards}
os.makedirs(os.path.join(ROOT, 'tools/film/cuts'), exist_ok=True)
if V3: cut['grain'] = 0.035               # a fine film grain over the frame (build.py)
json.dump(cut, open(os.path.join(ROOT, 'tools/film/cuts', 'vegas-tour-v3.json' if V3 else 'vegas-tour-v2.json'), 'w'), indent=1)
print(f'{len(clips)} clips, drive starts {start:.2f} s, coaster from {sum(1 for _ in SHOTS)} shots, aerial closer from {t:.2f} s, ends {END} s')
