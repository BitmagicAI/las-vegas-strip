"""Local, source-linked architectural review. No upload or publication."""
import json,html
from pathlib import Path
OUT=Path('build/strip-landmarks')
refs=json.loads((OUT/'references/sources.json').read_text())
refs.update({'linq-lobby':'https://www.wyndhamhotels.com/content/dam/property-images/en-us/tq/us/nv/las-vegas/51492/51492_front_desk_1.jpg','fashion-interior':'https://cdn.civitatis.com/guias/lasvegas/fotos/fashion-show-mall-tiendas.jpg','vanderpump-room':'https://pimg.mk.co.kr/news/cms/202603/31/news-p.v1.20260331.0b3c1cb41b2d44eb946ee57c993e336f_R.jpg'})
(OUT/'references/sources.json').write_text(json.dumps(refs,indent=2))
items=[
 ('linq','The LINQ & High Roller','Blue and white guest wings, Vortex ribbons, hexagonal frontage and glazed entrance. The promenade leads to a slowly rotating High Roller with 28 upright cabins. Inside: timber reception, mosaic counter, Catalyst bar, gaming floor and guest stairs.',['wheel','room','corridor']),
 ('vanderpump','Vanderpump / former Cromwell','Warm stone, bronze balcony rails, corner signage, rooftop pool and cabanas. The lobby uses gilded columns, chandeliers, mirrors and patterned carpet; guest rooms combine a dark upholstered headboard, botanical wall treatment and blush furnishings.',['room','corridor']),
 ('fashion','Fashion Show & The Cloud','Surveyed mall footprint with the large silver Cloud above the arrival plaza. Glazed entrance, two-level retail gallery, display windows, kiosks, seating, theatrical lighting trusses and walkable stairs. Shops are representative displays rather than individually reconstructed stores.',[]),
 ('venetian','The Venetian frontage','Campanile, pale Gothic loggias, patterned palace walls, canal and gondolas. A new Rialto stair approach connects through an upper doorway and descending gallery to the chandelier-lit Grand Colonnade. The existing Venetian hotel tower and streamed rooms are retained.',['canal']),
 ('arena','T-Mobile Arena','Copper panel shell, northeast curtain wall, magenta signage and arrival plaza. Inside: ticket counters, enclosed concourse, concession stands, access tunnels, stepped seating bowl, radial stairs, ice rink and suspended scoreboard. Seats share instanced geometry in the game.',['bowl'])]
def model(key,view):
 return f'<figure><img loading="lazy" src="{key}-{view}-review.png" alt="{key} {view} model review"><figcaption>MODEL · {view.title()} · Blender render of the game assets</figcaption></figure>'
def reference(key):
 return f'<figure><a href="{html.escape(refs[key])}" target="_blank"><img loading="lazy" src="references/{key}.jpg" alt="Reference photograph for {key}"></a><figcaption>REFERENCE PHOTO · <a href="{html.escape(refs[key])}" target="_blank">Source</a></figcaption></figure>'
nav=''.join(f'<a href="#{k}">{name}</a>' for k,name,_,_ in items)
body=''
for key,name,desc,extras in items:
 body+=f'<section id="{key}"><header><span>LANDMARK / {key.upper()}</span><h2>{name}</h2><p>{desc}</p><div class="actions"><a href="http://localhost:3090/?landmark={key}&view=entrance">Play from entrance ↗</a><a href="http://localhost:3090/?landmark={key}&view=lobby">Play from lobby ↗</a></div></header>'
 body+='<div class="pair">'+model(key,'skyline')+reference(key)+'</div><div class="pair">'+model(key,'entrance')+model(key,'lobby')+'</div>'
 if key in ['linq','fashion']:body+='<div class="pair">'+model(key,'lobby')+reference(key+'-lobby' if key=='linq' else 'fashion-interior')+'</div>'
 for extra in extras:
  body+='<div class="pair">'+model(key,extra)
  if extra=='room':body+=reference(key+'-room')
  elif extra=='corridor':body+='<aside>Corridors use the corresponding hotel’s material palette, trim, doors and wayfinding. Rooms and corridor modules stream on demand; the game does not keep all guest floors in memory.</aside>'
  elif extra=='wheel':body+='<aside>The wheel rotates with its cabins kept upright. This is an animated landmark; a passenger ride interaction is not implemented.</aside>'
  elif extra=='bowl':body+='<aside>The review includes the same shared seat positions used by the runtime. The arena is explorable; this build does not add a hockey match or concert simulation.</aside>'
  else:body+='<aside>The Rialto route replaces the old flat map ramp, including an opening through the adjoining bridge railing.</aside>'
  body+='</div>'
 body+='</section>'
report=json.loads((OUT/'route-audit.json').read_text())
page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Afterlight · Landmark review</title><style>
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:#13201f;color:#e8e4d9;font:16px/1.65 system-ui,sans-serif}main{max-width:1500px;margin:auto;padding:54px 36px}h1{font-size:48px;line-height:1.1;margin:15px 0 20px;letter-spacing:-1.5px}h2{font-size:34px;line-height:1.2;margin:8px 0 12px}p{max-width:1000px;color:#c4cec7}a{color:#b5dbc8}nav,.actions{display:flex;flex-wrap:wrap;gap:12px}nav a,.actions a{border:1px solid #465a51;padding:9px 15px;border-radius:4px;text-decoration:none}nav{margin:32px 0 54px}section{border-top:1px solid #43524a;padding:35px 0 45px;scroll-margin-top:15px}header{margin-bottom:26px}span,figcaption{font-size:12px;letter-spacing:1.6px;color:#b6c8b9}figure{margin:0;min-width:0}img{width:100%;aspect-ratio:3/2;object-fit:contain;background:#080e0d;display:block;border:1px solid #33493f}figcaption{padding:10px 0 16px}.pair{display:grid;grid-template-columns:1fr 1fr;gap:24px;margin-top:18px}aside{background:#20312d;padding:32px;align-self:center;color:#b7c9bf}.note{border-left:3px solid #afc9b9;padding:10px 20px;background:#20312d}footer{color:#9cafaa;font-size:14px}@media(max-width:800px){main{padding:25px 16px}.pair{grid-template-columns:1fr}h1{font-size:36px}}
</style><main><span>VEGAS: AFTERLIGHT · LOCAL BUILD</span><h1>Five more pieces of the Strip</h1><p>Photo-informed architecture, entrances and streamed interiors, fitted to the map’s footprints. The views below are Blender renders of the exported game geometry; real-time game lighting differs. These are authored game reconstructions, not photogrammetry or exact as-built interior plans.</p>'''
page+=f'<p class="note">Validation: {report["checks"]:,} route probes; {len(report["failures"])} failures. LINQ and Vanderpump add {report["virtualRooms"]} virtual guest-room instances using reusable, lazily loaded modules. Original mapped boxes for the five replacement sites are removed.</p><nav>{nav}</nav>{body}<footer>Reference images remain reference material. They are not baked into the building textures. All work is local; nothing has been published.</footer></main></html>'
(OUT/'review.html').write_text(page)
print('Wrote',OUT/'review.html')
