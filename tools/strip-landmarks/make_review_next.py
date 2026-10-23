"""Source-linked review of the second local architectural pass."""
import html,json
from pathlib import Path
OUT=Path('build/strip-landmarks')
refs=json.loads((OUT/'references-next/sources.json').read_text())
items=[
 ('park','Park MGM / Eataly','A steel-and-glass pavilion fronts the food-market approach. The reception uses green paneling, mirrored columns, suspended root sculpture, botanical reliefs, marble inlays and individual check-in desks. A public gallery connects to the existing Park MGM guest stairs.'),
 ('palazzo','The Palazzo','An oval glazed porte-cochere and bronze ribs lead into a fountain rotunda with fluted columns, arched cornices, a luminous dome, floral displays and sculptural figures. Reception, lounge and gaming areas connect to the Palazzo guest wing. The fountain treatment follows the archived reference photo, rather than claiming the latest seasonal installation.'),
 ('ti','Treasure Island','The previously plain podium now has articulated stone frontage, an entrance canopy and a modeled galleon with deck, rigging, masts and cannon ports. Inside: a sweeping reception counter, paneled walls, luggage trolleys, queue rails, patterned carpet, lounge seating and guest-stair access.'),
 ('harrahs','Harrah’s Las Vegas','Purple folded marquee, chevron lighting and glazed entrance; inside, individually modeled colored petals form the reception feature wall above amethyst counters. Public circulation connects the gaming and lounge areas to both existing guest cores.'),
 ('polo','Polo Towers','The map footprint now has cream stucco, recessed balconies, punched windows, purple trim, a tall sign blade and roof details. The covered arrival leads to an elliptical cove-lit lobby with bronze horses, reception and guest stairs. A custom room and corridor set adds carpet, timber furnishings, kitchenette, appliances, bathroom and framed art.')]
def model(key,view):
 return f'<figure><img loading="lazy" src="{key}-{view}-review.png" alt="{key} {view} exported model"><figcaption>MODEL · {view.title()} · Offline render of exported game geometry</figcaption></figure>'
def ref(key):
 url=html.escape(refs[key]);return f'<figure><a href="{url}"><img loading="lazy" src="references-next/{key}.jpg" alt="{key} reference photograph"></a><figcaption>REFERENCE PHOTO · <a href="{url}">Image source ↗</a></figcaption></figure>'
body=''
for key,name,description in items:
 body+=f'<section id="{key}"><header><small>VEGAS: AFTERLIGHT / {key.upper()}</small><h2>{name}</h2><p>{description}</p><div class="links"><a href="http://localhost:3090/?landmark={key}&view=entrance">Play from entrance ↗</a><a href="http://localhost:3090/?landmark={key}&view=lobby">Play from lobby ↗</a></div></header>'
 if key+'-entrance' in refs:body+='<div class="pair">'+model(key,'entrance')+ref(key+'-entrance')+'</div>'
 else:body+='<div class="pair">'+model(key,'entrance')+model(key,'skyline')+'</div>'
 body+='<div class="pair">'+model(key,'lobby')+ref(key+'-lobby')+'</div>'
 if key=='ti':body+='<div class="pair">'+model(key,'ship')+ref('ti-ship')+'</div>'
 if key=='polo':
  body+='<div class="pair">'+model(key,'skyline')+ref('polo-exterior')+'</div><div class="pair">'+model(key,'room')+ref('polo-room')+'</div><div class="pair">'+model(key,'corridor')+'<aside>The room is a fitted interpretation of the photographed Polo finishes and kitchenette. The corridor is coordinated with that palette; it is not a surveyed hallway reconstruction. Fifteen mapped levels use shared templates, representing 182 guest rooms without allocating every room at startup.<p><a href="http://localhost:3090/?hotel=polo-1&floor=2&room=0">Play from guest floor ↗</a></p></aside></div>'
 body+='</section>'
audit=json.loads((OUT/'route-audit.json').read_text())
nav=''.join(f'<a href="#{k}">{n}</a>' for k,n,_ in items)
page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Afterlight · Five resort arrivals</title><style>
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:#15211e;color:#efe8da;font:16px/1.6 system-ui,sans-serif}main{max-width:1500px;margin:auto;padding:48px 32px}h1{font-size:48px;line-height:1.1;letter-spacing:-1.5px;max-width:850px}h2{font-size:34px;line-height:1.2;margin:8px 0 18px}p{max-width:1080px;color:#c9d1c8}a{color:#b6d7bd}nav,.links{display:flex;gap:12px;flex-wrap:wrap}nav{margin:35px 0 55px}nav a,.links a{border:1px solid #536458;padding:8px 14px;text-decoration:none;border-radius:4px}section{border-top:1px solid #4e5a4f;padding:36px 0 42px}.pair{display:grid;grid-template-columns:1fr 1fr;gap:24px;margin-top:24px}figure{margin:0;min-width:0}img{width:100%;aspect-ratio:3/2;object-fit:contain;background:#090e0c;display:block}figcaption,small{font-size:12px;letter-spacing:1.5px;color:#bdcbbb}figcaption{padding:10px 0}aside,.note{background:#24352a;padding:24px;align-self:center}.note{border-left:3px solid #d1bd88}footer{font-size:14px;color:#b8c3b8;margin-top:20px}@media(max-width:800px){main{padding:25px 16px}.pair{grid-template-columns:1fr}h1{font-size:36px}}
</style><main><small>LOCAL ARCHITECTURAL REVIEW · 05 OCT 2026</small><h1>Five more resort arrivals, inside and out</h1><p>Photo-informed architecture fitted to the mapped building envelopes. Four plain podiums have new public entrances and halls connected to their existing hotel cores; Polo Towers has a new exterior and guest set. These images show the exported geometry rendered in Blender. Game lighting differs; use the play links to inspect it in context.</p><p class="note">These are authored game reconstructions, not photogrammetry or exact interior floor plans. Facade proportions, artwork, furniture and circulation are interpreted from the reference material. The rest of the Strip continues to include placeholders.</p>'''
page+=f'<p>Validation: {audit["checks"]:,} capsule and ground probes through the landmark routes with city collision enabled; {len(audit["failures"])} failures. Type checking and a WebGPU startup check passed. Detailed interiors and rooms load on demand; distant facade ornament is culled.</p><nav>{nav}</nav>{body}<footer>Sources: linked alongside every reference. Photos are research references, not facade textures. All assets and the running game remain local.</footer></main></html>'
(OUT/'review-next.html').write_text(page)
print('Wrote',OUT/'review-next.html')
