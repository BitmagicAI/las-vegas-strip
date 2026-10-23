"""Build a local, attributed photo audit from unmodified game captures and references."""
import html
import json
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/public-resorts/comparison'
refs = {}
for file, prefix in [(OUT.parent/'references/sources.json', '../references'), (OUT/'references/sources.json', 'references')]:
    for name, source, image in json.loads(file.read_text()):
        if (OUT / prefix / (name+'.jpg')).exists():
            refs[name] = {'path': f'{prefix}/{name}.jpg', 'source': source, 'image': image}

# Captions explicitly distinguish first-entry views from reception photographs.
properties = [
    dict(id='bellagio', name='Bellagio', shot='bellagio-gallery', entry='bellagio-entry', lobby='bellagio-lobby',
         entry_note='Real porte-cochère, looking outward under the canopy — opposite viewing direction.',
         lobby_note='Real reception desk. This is not the view through our lake-facing gallery door.',
         note='The arrival suites now have glazed bronze door assemblies, marble wall bays, framed coffered ceilings, crystal chandeliers and furnished reception or gallery circulation. The existing porte-cochère remains in place.'),
    dict(id='paris', name='Paris Las Vegas', entry='paris-entry', lobby='paris-lobby',
         entry_note='Real covered vehicle arrival beside the Arc de Triomphe; different approach from the game portal.',
         lobby_note='Real hotel reception salon; the game adapts this palette and wall treatment into its entrance salon.',
         note='A green barrel-vault glass canopy leads into an enclosed marble-and-gilt salon with paneled walls, crystal chandeliers, seating and reception. The layout adapts the photographic references to the playable casino connection.'),
    dict(id='caesars', name='Caesars Palace', entry='caesars-entry', lobby='caesars-arrival',
         entry_note='Strip pedestrian entrance, photographed in 2014. A different portal from the modeled main portico.',
         lobby_note='Renovated main arrival rotunda, from the project architect’s photo gallery.',
         note='The arrival space now has a curved coffered dome, layered marble wall bays, fluted columns, a large chandelier, floor medallion and statue niche, with clear circulation into the casino.'),
    dict(id='cosmo', name='The Cosmopolitan', entry='cosmo-entry', lobby='cosmo-columns',
         entry_note='Real illuminated street entrance; portrait view of the canopy and glazing.',
         lobby_note='Reception with digital columns, photographed in 2012. Display content changes; not a matched camera angle.',
         note='The glazed entrance opens onto a deliberately scaled reception gallery with digital-style columns, dark polished flooring, blue canopy lighting, reception and furnished seating bays.'),
    dict(id='flamingo', name='Flamingo', entry='flamingo-entry', lobby='flamingo-lobby',
         entry_note='Real Strip frontage and pink entrance canopy.',
         lobby_note='Real reception area. The current Strip door leads into the game’s casino, rather than directly to this desk.',
         note='The pink fan canopy and glazed entrance now lead into a furnished registration gallery with coffered ceilings, a long counter, gold mosaic wall, kiosks and seating.'),
    dict(id='horseshoe', name='Horseshoe', entry='horseshoe-entry', lobby='horseshoe-lobby',
         entry_note='Real entrance arch and covered approach; the photo includes the approach structure.',
         lobby_note='Hotel reception photographed during the Bally’s / Horseshoe transition in 2022; older signage remains.',
         note='The covered arch leads into a registration gallery with a continuous counter, linear ceiling lighting, self check-in stations and seating. Circulation wraps around the retained guest-stair core.'),
    dict(id='planet-hollywood', name='Planet Hollywood', entry='planet-hollywood-entry', lobby='planet-hollywood-lobby',
         entry_note='Real illuminated entrance assembly and canopy.',
         lobby_note='Real oval escalator lobby. This is an architectural reference, not the same viewpoint as our casino entrance.',
         note='The new entrance leads into an oval arrival atrium with layered balcony rings, illuminated columns, a suspended crystal chandelier and reception. The deeper casino and existing vertical routes remain connected.'),
    dict(id='aria', name='ARIA', entry='aria-entry', lobby='aria-lobby',
         entry_note='Real vehicle arrival canopy and entrance glazing.',
         lobby_note='Real lobby interior from Architectural Record; a different viewpoint along the reception area.',
         note='Tall glazing, a ribbed metal canopy, substantial stone piers, woven ceiling panels, reception, river-inspired wall sculpture and seating form the new arrival sequence.'),
    dict(id='vdara', name='Vdara', entry='vdara-entry', lobby='vdara-lobby',
         entry_note='Real porte-cochère and curved arrival frontage.',
         lobby_note='Official MGM photo of reception, showing the ceiling sculpture, carpet, timber and artwork.',
         note='The arrival suite now brings reception, walnut wall slats, interlocking geometric artwork, wood pendant sculptures, a patterned carpet and lounge seating into a lower, more intimate space.'),
    dict(id='waldorf', name='Waldorf Astoria', entry='waldorf-entry', lobby='waldorf-lobby',
         entry_note='Real entrance with recessed red vestibule and metal-framed glass doors.',
         lobby_note='Real ground-floor arrival gallery, as shown in the hotel review; not the upper-level reception.',
         note='A recessed red vestibule and bronze-framed glazing lead into a narrow marble gallery with circular floor inlays, gold rod chandeliers, framed wall bays, seating and a terminal art display.'),
    dict(id='crystals', name='The Shops at Crystals', entry='crystals-entry', lobby='crystals-treehouse',
         entry_note='Real glass entrance with multiple door leaves and a tall transom.',
         lobby_note='Real Treehouse atrium landmark, farther inside the mall; not a photo from the threshold.',
         note='The old wall opening has been replaced with a tall black-framed glass façade. Inside, folded overhead planes, closely spaced retail fronts, display vitrines, planting and a timber concierge sculpture define the gallery.'),
    dict(id='veer', name='Veer Towers', entry='veer-approach', lobby='veer-lobby',
         entry_note='Exterior approach / plaza context by KuDa Photography. This is not a close-up of the entrance door.',
         lobby_note='Real glazed residential lobby, looking toward its entrance. Reference may show the other tower.',
         note='Both towers now have a dedicated glazed residential lobby connected to their guest stairs, with concrete piers, white seating, lime ottomans, red planters and concierge desks.'),
]

def esc(s): return html.escape(s, quote=True)
def figure(src, label, caption, source=None):
    credit = f'<a class="source" href="{esc(source)}" target="_blank" rel="noreferrer">Photo source · {esc(urlparse(source).netloc.removeprefix("www."))} ↗</a>' if source else '<span class="source">Local game capture · 3 October 2026</span>'
    return f'<figure><div class="label">{esc(label)}</div><a class="image" href="{esc(src)}" target="_blank"><img src="{esc(src)}" alt="{esc(label+". "+caption)}"></a><figcaption>{esc(caption)}{credit}</figcaption></figure>'

cards=[]
for i,p in enumerate(properties):
    shot=p.get('shot',p['id'])
    entry=refs[p['entry']]; lobby=refs[p['lobby']]
    cards.append(f'<article id="{p["id"]}"><header class="property"><span>{i+1:02d} / 12</span><h2>{esc(p["name"])}</h2><p>{esc(p["note"])}</p></header><div class="grid">'+
        figure(f'captures/comparison-{shot}-entrance.png','GAME · Entrance approach','Current playable entrance. Full camera frame.')+
        figure(entry['path'],'REFERENCE · Entrance / approach',p['entry_note'],entry['source'])+
        figure(f'captures/comparison-{shot}-inside.png','GAME · Immediately inside','Looking inward from approximately 3 m beyond the same door, at player eye height.')+
        figure(lobby['path'],'REFERENCE · Arrival / lobby',p['lobby_note'],lobby['source'])+'</div></article>')

nav=''.join(f'<a href="#{p["id"]}" data-property="{p["id"]}">{esc(p["name"])}</a>' for p in properties)
page='''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Afterlight · Entrance and lobby comparisons</title><style>
*{box-sizing:border-box}html{color-scheme:dark}body{margin:0;background:#121819;color:#edf0eb;font:16px/1.5 system-ui,-apple-system,sans-serif}a{color:#bde3d0}main{max-width:1600px;margin:auto;padding:32px}.intro{max-width:1000px;margin:0 0 26px}.eyebrow{color:#b6c7be;text-transform:uppercase;font-size:12px;letter-spacing:.16em}h1{font-size:36px;line-height:1.15;letter-spacing:-.03em;margin:10px 0 16px}.intro p{color:#bdc8c2;margin:8px 0}.intro strong{color:#fff}nav{display:flex;flex-wrap:wrap;gap:7px;padding:0 0 24px}nav a{border:1px solid #40524a;border-radius:4px;padding:7px 11px;text-decoration:none;font-size:14px}nav a[aria-current=true]{background:#c3ddcd;color:#15251c;border-color:#c3ddcd}article{background:#1c2424;border:1px solid #3b4944;margin-bottom:24px;padding:24px;scroll-margin-top:20px}article[hidden]{display:none}.property span{float:right;color:#a2b2a8;font-size:13px}.property h2{font-size:28px;margin:0 0 8px}.property p{color:#e6c8a0;max-width:1250px;margin:0 0 22px;font-size:16px}.grid{display:grid;grid-template-columns:1fr 1fr;gap:24px 18px}figure{margin:0;min-width:0}.label{font-size:12px;letter-spacing:.12em;font-weight:700;padding:0 0 8px;color:#d3e5db}.image{display:block;background:#0b1010;width:100%;aspect-ratio:1.44}.image img{display:block;width:100%;height:100%;object-fit:contain}figcaption{padding:10px 0 0;font-size:13px;line-height:1.45;color:#c7d0c9;min-height:73px}.source{display:block;margin-top:5px;font-size:12px}footer{color:#9caf9f;font-size:13px;max-width:1100px;margin:24px 0}button{font:inherit}.extra{font-size:13px;margin:20px 0}#controls{display:flex;justify-content:space-between;margin:16px 0}#controls button{background:#23352b;border:1px solid #4a6856;border-radius:3px;color:#fff;padding:8px 16px;cursor:pointer}@media(max-width:760px){main{padding:18px}h1{font-size:28px}article{padding:15px}.grid{grid-template-columns:1fr}.property h2{font-size:24px}nav a{font-size:12px}.property span{float:none}.image{aspect-ratio:1.44}}
</style></head><body><main><div class="intro"><div class="eyebrow">Vegas: Afterlight · Local visual audit · 03 October 2026</div><h1>Entrances and the first view inside</h1><p><strong>Rebuilt arrival architecture.</strong> The game views show the new entrance assemblies and adjoining furnished spaces. These are photo-informed reconstructions adapted to the playable layout, not measured replicas.</p><p>Left: fresh game captures. Right: real photographs. References are not all the same entrance, date or camera angle; differences are labeled. Click an image to inspect its full resolution.</p></div><nav aria-label="Choose property">'''+nav+'''<a href="#all" data-property="all">Show all</a></nav>'''+''.join(cards)+'''<div id="controls"><button id="prev">← Previous property</button><button id="next">Next property →</button></div><p class="extra">Bellagio additional route: <a href="captures/comparison-bellagio-entrance.png" target="_blank">south entrance</a> · <a href="captures/comparison-bellagio-inside.png" target="_blank">just inside the south entrance</a>.</p><footer>Capture method: the existing local game was positioned on either side of each mapped door using development bookmarks. These are actual rendered game views, not Blender previews or concept art. Screenshots preserve the full frame and existing geometry, lighting and furnishings; HUD overlays are hidden in most views; refreshed inspection views may include development controls. The gallery is an architectural comparison, not a walk-through or collision test. The screenshots document the reconstructed architecture running in the local game. Reference photographs remain research material and are not imported as game textures.</footer></main><script>
const articles=[...document.querySelectorAll('article')];const ids=articles.map(a=>a.id);function show(){const id=location.hash.slice(1)||ids[0];const selected=ids.includes(id)?id:(id==='all'?'all':ids[0]);articles.forEach(a=>a.hidden=selected!=='all'&&a.id!==selected);document.querySelectorAll('nav a').forEach(a=>a.setAttribute('aria-current',String(a.dataset.property===selected)));document.querySelector('#controls').hidden=selected==='all';}function step(n){const current=ids.indexOf(location.hash.slice(1));location.hash=ids[(Math.max(0,current)+n+ids.length)%ids.length];}document.querySelector('#prev').onclick=()=>step(-1);document.querySelector('#next').onclick=()=>step(1);window.addEventListener('hashchange',show);show();
</script></body></html>'''
(OUT/'index.html').write_text(page)
(OUT/'manifest.json').write_text(json.dumps({'date':'2026-10-03','properties':properties,'references':refs},indent=2)+'\n')
print(OUT/'index.html')
