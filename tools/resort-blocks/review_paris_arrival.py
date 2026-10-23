"""Self-contained reference/before/after evidence for the Paris entrance correction."""
from pathlib import Path
import base64,html,json
O=Path('build/resort-blocks/paris')
def picture(path,label):
 p=Path(path);mime='image/jpeg' if p.suffix=='.jpg' else 'image/png'
 if not p.exists():raise FileNotFoundError(p)
 return '<figure><figcaption>'+html.escape(label)+'</figcaption><img loading="lazy" src="data:'+mime+';base64,'+base64.b64encode(p.read_bytes()).decode()+'"></figure>'
rows=[
 ('tools/resort-blocks/references/paris-entrance-earth-2026-10-05.png','REFERENCE · Creator-provided Google Earth close aerial; imagery date unknown'),
 (str(O/'game-arrival-aerial.jpg'),'GAME · Corrected main entrance, actual WebGPU game capture'),
 ('tools/resort-blocks/references/paris-entrance-before-2026-10-05.png','BEFORE · Creator-provided game comparison'),
 (str(O/'arrival-aerial-review.png'),'GEOMETRY REVIEW · Same exported assets in neutral Blender lighting; surrounding city omitted'),
 (str(O/'game-arrival-approach.jpg'),'GAME · Beneath the canopy, facing the main doorway'),
 (str(O/'game-arrival-inside.jpg'),'GAME · Main vestibule looking outside through the glass doors'),
 (str(O/'game-arrival-stairs.jpg'),'GAME · Normal player movement reached the relocated rooftop landing'),
 (str(O/'game-arrival-curb-crossed.jpg'),'GAME · Walked from casino through the open door and across the sloped curb')]
body=''.join(picture(*r) for r in rows)
(O/'entrance-proof.html').write_text('''<!doctype html><meta charset="utf-8"><title>Paris entrance correction · 2026-10-05</title><style>body{background:#192122;color:#eee;font:17px/1.5 system-ui;margin:30px}h1{font-size:32px}main{display:grid;grid-template-columns:1fr 1fr;gap:22px}figure{margin:0}img{width:100%;height:auto}figcaption{padding:10px 0;color:#a4cdc6;font-weight:600}a{color:#a4cdc6}p{max-width:1150px}li{margin:8px 0}@media(max-width:900px){main{display:block}figure{margin-bottom:22px}}</style><h1>Paris · main entrance correction</h1><p>The entrance composition now includes a curved three-storey facade, enclosed Opera-inspired pavilion and apse, fine glazed canopy, open motor court, main vestibule, vaulted Arc and decorated balloon/display pedestal. These are installed game assets. Reference imagery is used for visual study, never imported as game geometry or textures.</p><p>1,795 clearance/support checks and a grounded capsule sweep pass. Actual player movement crossed the main doorway and curb and reached the relocated rooftop landing. Typecheck and automated WebGPU startup verification pass. Performance profiling remains deferred.</p><main>'''+body+'''</main><h2>Remaining differences</h2><ul><li>Facade dimensions, heights, window cadence and real access alignments remain fitted estimates.</li><li>Reliefs, statues, medallions and balloon lettering are original simplified approximations. The Arc transverse passages remain unmodeled.</li><li>Mature landscaping, detailed stone/weathering, pavilion sculpture, finer roof articulation and exact storefront fit-out need another pass.</li><li>The vestibule is a playable connection to the retained casino, not a full reconstruction of the actual hotel lobby. Guest-floor registration and east/service elevations remain open.</li><li>Google Earth and game captures have similar directions but are not calibrated to matching focal length or geographic camera pose.</li></ul><p>Sources: creator Google Earth capture; <a href="https://www.livedesignonline.com/a-tale-two-cities-0">original design/contractor interviews</a>; <a href="https://www.caesars.com/content/dam/empire/plv/property/rideshare/paris-las-vegas-map.pdf">Caesars property map</a>; local OSM footprint survey. Full source register, estimates and unfinished work are in tools/resort-blocks/paris.json.</p>''')
print(O/'entrance-proof.html')
