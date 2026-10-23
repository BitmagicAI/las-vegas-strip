"""Additional source photos for the local visual audit; never imported into the game."""
import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'build/public-resorts/comparison/references'
OUT.mkdir(parents=True, exist_ok=True)
SOURCES = [
    ['bellagio-entry', 'https://newsroom.mgmresorts.com/media-gallery?cat=2837&submitted=1', 'https://thelibrary.mgmresorts.com/transform/MbTVlLiqGfi6/Bellagio-Porte-Cochere'],
    ['caesars-entry', 'https://www.pentaxforums.com/forums/12-post-your-photos/258621-architecture-walking-around-las-vegas.html', 'https://bulk-share.slickpic.com/album/share/Z1lJMz2OjJzuzT/7829953.0/org/p/140403-6574CaesarsEntrance.jpg'],
    ['crystals-entry', 'https://www.traveling-companion.com/traveling-companion/exploring-the-las-vegas-strip', 'https://www.traveling-companion.com/uploads/1/2/1/8/121848493/img-5998-2_orig.jpg'],
    ['veer-approach', 'https://kudaphotography.com/albums/veer-towers/', 'https://kudaphotography.com/koken/storage/cache/images/000/092/061%2Cmedium.2x.1436747402.jpg'],
    ['veer-lobby', 'https://www.lasvegaspenthouses.com/veer-towers/', 'https://assets.site-static.com/userFiles/4968/image/Veer/veer_lobby.jpg'],
    ['vdara-lobby', 'https://vdara.mgmresorts.com/en.html', 'https://thelibrary.mgmresorts.com/transform/EWDgW1nVUv902A1B/VDR135625606.jpg'],
]
for name, source, url in SOURCES:
    dest = OUT / f'{name}.jpg'
    if not dest.exists():
        req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
        try:
            with urllib.request.urlopen(req, timeout=45) as response:
                dest.write_bytes(response.read())
        except Exception as e:
            print(name, 'unavailable:', e)
            continue
    print(name, dest.stat().st_size)
(OUT / 'sources.json').write_text(json.dumps(SOURCES, indent=2)+'\n')
