# Bellagio covered arrival

The lake-facing gallery portal at (-131, 0, 34) now has a pavilion inspired by
Bellagio's main porte-cochere. It is a photo-based adaptation to the existing
compressed level, not a surveyed replica of its real location or dimensions.
The existing south entrance and its under-wing portico remain in place.

Reference photographs inspected September 29, 2026:

- MGM Resorts, [Bellagio Porte Cochere](https://thelibrary.mgmresorts.com/transform/MbTVlLiqGfi6/Bellagio-Porte-Cochere): glazed barrel vault and rounded end, scrollwork ribs, cream coffered soffits, bronze columns, large suspended opaline bowls, inset pavement.
- [atmtx photo, Bellagio Porte Cochere](https://blog.atmtxphoto.com/2023/11/17/bellagio-porte-cochere/): closer nighttime view of the ribs, coffers, bronze lamp cages and arrival paving.

No reference photographs are embedded as game textures. The architecture is
modeled in Blender by `bellagio_arrival.py`, called from the full Bellagio builder.
`install_bellagio_arrival.py` updates only the named arrival meshes and their
simple collision proxies in both the source and streamed scenes.

| Element | Layout / clearance |
|---|---|
| Pavilion | About 30 m along the facade, 12.2 m projection; 10.12 m roof crown |
| Existing gallery leaf | 5 m wide, 4.5 m high, same location and automatic door behavior |
| Pedestrian route | At least 3.4 m centered on the existing door, free of urns and columns |
| Roof structure | Glazed barrel vault, rounded skylight end, modeled ribs and scrolls |
| Stonework | Coffered soffit wings, curved medallion frieze, layered cornices, entry pilasters |
| Ground | Flush patterned paving and pale inlay, no new steps |
| Lighting | Eight caged bowl fixtures, emissive coffer lights, two pooled warm fill lights |
| Physics | Ten column proxies and four urn proxies; trim, glass, pavers and lamps are decorative |

Canopy geometry is grouped by material, remains part of the exterior visibility
pass, and is separate from streamed hotel corridors/rooms. The facade and hotel
streaming cuts are retained. Re-export using the existing visibility exporters;
copy the staged metadata and revision into `src/work/hotels/` after validation.

Review: `?inspect=bellagio-arrival-exterior`, `?inspect=bellagio-arrival-vault`.
Blender review: `render_bellagio_arrival.py`.
Regression: `tools/test-bellagio-doors.mjs` checks the exported door openings and
standing capsule clearance through the real collision scene; the exterior shell
test checks the facade remains opaque with guest rooms absent.
