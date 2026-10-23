# Bellagio reconstruction — architectural and playable pass

## Visual reference
Exterior reference inspected: https://commons.wikimedia.org/wiki/File:Bellagio_outside.jpg
Property circulation reference: https://s3.amazonaws.com/vegasmaps/Bellagio.pdf
The reference photograph, not the hotel sign, is the recognition test. The defining geometry is the concave broad facade, raised inner-wing crowns, rounded central risalit, open arched cupola and low lakefront villas. Cream plaster, buff stone piers, dark bronze window frames, two prominent horizontal entablatures, vertical window groups and tall arched crown windows. No replacement BELLAGIO sign is needed to establish identity.

This is an authored post-apocalyptic adaptation with compressed dimensions, not a survey-accurate property model. The casino and room arrangement is adapted for navigable gameplay and limited to the current district footprint.

## Coordinates and rooms
X east, Z north, ground floor y=0. All extents in metres.

| Space | X bounds | Z bounds | Clear height | Access |
|---|---|---|---|---|
| Main tower / curved wings | roughly -197..-139 | -116..82 | 88 + cupola/finial to 107 | exterior silhouette above podium |
| South portico | -171..-139 | -93..-76 | 7 | open south arrival |
| Lobby | -191..-131 | -76..-44 | 8 | south portico; casino; west service corridor |
| Casino | -191..-131 | -44..26 | 8 | lobby; north gallery; west service corridor |
| North gallery | -191..-131 | 26..42 | 8 | casino; east terrace exit |
| Service corridor | -203..-191 | -68..34 | 4.2 | lobby and casino cross passages |
| Staff lounge | -215..-203 | -66..-50 | 4.2 | service corridor |
| Stores | -215..-203 | -44..-28 | 4.2 | service corridor; food cache |
| Medical room | -215..-203 | -22..-6 | 4.2 | service corridor; medical staging |
| Security office | -215..-203 | 0..16 | 4.2 | service corridor; alternate route into north gallery via corridor |

## Traversal and missions
Sanctuary -> existing food approach -> south lake-side path -> portico -> lobby -> casino -> north gallery -> north lake-side path -> sanctuary. Service corridor branches from lobby and casino; each room has an actual automatic doorway and a continuous floor. Decorative slot banks flank wide movement aisles. Columns and gaming tables use matching colliders. Casino ceilings and room envelopes are physical. Public and service openings have engine-controlled sliding or hinged leaves. The full public shell and each service room are checked with doors closed; circulation waypoints are checked with doors open.

The existing food mission moves into the Bellagio stores. Its horde recess moves to the adjacent service room/corridor staging area. Mission metadata and game beacons follow the new positions. There are still no generated Hero characters or live combat in this pass.

## Acceptance
Exterior view with no hotel labels must show the reference silhouette and window hierarchy. Interior must show a ceiling, detailed floor materials, casino furniture, circulation cues and room-specific furnishings. Audit actual route segments including both public exits and every room door. Inspect daylight exterior and interior lighting renders, then browser boot and functional walk/route checks. Do not reduce geometry to satisfy early FPS targets.
