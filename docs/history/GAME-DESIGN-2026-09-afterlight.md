# Vegas: Afterlight
A desktop-first zombie survival game in a ruined central Las Vegas Strip. First delivery is a walkable Blender environment and mission/horde staging layout; Hero (WebHuman) characters will be supplied by the creator.

## Art direction
Realistic architectural proportions and grounded material treatment, aspirational AAA / UE5 cinematic fidelity. NOT a cartoon or voxel world. The Bitmagic `low-poly` switch enables mesh rendering; it does not describe the requested aesthetic. Weathered cream limestone, bronze lattice, soot, distressed asphalt, dusty glass, abandoned neon and desert sunset haze. Warm sunset outlines the Bellagio massing, Paris Eiffel landmark, Caesars frontage and Flamingo signage. Wet patches and cyan sanctuary energy contrast with amber skies. This is a compressed, recognizable adaptation of the central Strip, not a surveyed replica of resort interiors. Prioritize visuals; defer FPS gates and mobile optimization.

## First environment
An approximately 440 x 600 metre district. X east, Z north. Sanctuary on the former Bellagio forecourt, west of the boulevard. Boulevard runs north/south. Flamingo Road crosses the northern portion. Paris lies east/southeast, Caesars northwest, Flamingo northeast. Buildings form an enclosing skyline and playable alleys lead to recessed supply depots.

## Survival loop
Leave the shield to collect food, medicine, weapons and ammunition. Return to bank supplies. A transparent energy hemisphere conceals player sight/sound signatures and excludes enemies. The player passes freely. Hidden hordes release when the exposed player enters proximity or makes noise; a few scouts wander outdoors. No Hero characters are generated until the creator supplies access.

## Current scope
Environment, sanctuary visual and safe-zone contract, supply cache interactions, mission and horde metadata. Combat, damage and animated enemies depend on supplied Hero characters and the next gameplay pass.

The current environment preview uses first-person to hide the template body while the Hero player is pending. No temporary block character is presented as the final player.

## Bellagio architectural milestone
Replace the original three Bellagio boxes and rectangular basin with a reference-led curved hotel facade, cylindrical central pavilion and open cupola, dimensional arched crown windows, layered stone cornices, low Italianate lakefront pavilions, a shaped fountain lake and a portico. Add a genuinely walkable lobby, casino, north gallery, service corridor and four furnished rooms. The architecture must read without hotel name text. Use richer authored geometry and material variation, not black triangles pasted onto the facade. Other hotels are unchanged in this milestone. See docs/BELLAGIO-PLAN.md.

## Cover lighting match
Use the existing cover as the lighting reference: low amber sunlight, copper atmospheric haze, blue-gray shadow fill and a cyan sanctuary accent. The sunset sky is generated with the cover as its reference. Decode the WebP as sRGB; rotate its bright horizon to match the 115-degree sun bearing. Keep ambient illumination restrained so directional light defines the architecture; preserve the authored casino and service-room practical lights.

## Paris milestone
The Paris exterior has cream French stonework, blue mansard roofs and dormers, repeated stone window reveals, a low-rise boulevard frontage and blue/gold Montgolfier balloon. The Eiffel Tower has four curved splayed lattice legs, base arches, lower galleries and a 140 m caged observation deck below its 165 m spire. Enter the west casino portal from the Strip, walk to the central lift, and press L (touch: LIFT) to travel up or back down. The lift uses a brief enclosed-cabin fade transition. The casino contains marble circulation aisles, roulette tables, slot banks and chandeliers. The deck has a complete walkable perimeter and viewing telescopes. Upper hotel rooms and lower tower galleries are exterior scenery for this milestone.

## Map correction and first cast integration — 2026-09-27
Geographic north is **-Z**, east is +X in the right-handed, Y-up game view. Earlier +Z-north labels reversed the Caesars/Bellagio ordering. Caesars is now at negative Z north of Bellagio, with its long Augustus-style wing east–west along Flamingo Road, Palace wing west of the casino, and Colosseum on the north/east side. The conflicting Cosmopolitan placeholder moves south. Existing Paris geometry and interiors are preserved. Other skyline placeholders still require individual map/detail passes; this is a compressed adaptation, not a surveyed replica.

References: Caesars Palace property map, page 7 of https://www.wyndhamhotels.com/content/dam/property-assets/en-us/ce/us/nv/las-vegas/51490/floor-plans/51490_ce_floor_plans_1.pdf ; Bellagio resort map https://bellagio.mgmresorts.com/content/dam/MGM/bellagio/meetings/bellagio-meetings-property-map.pdf .

The supplied low-facial-v2 b6101–b6109 GLBs are integrated unchanged. Native body/hand clips were verified before enabling bone-face, optical eyes and sparse correctives. One player, one sanctuary companion and seven prototype scouts are active; full horde combat is not part of this cast integration. Third-person view is available via V / Switch view. The standalone character review has explicit animation and face controls. Delivery mouth/eyelid limitations remain.


## Photo-led public areas — 2026-10-02
The current local stage now gives each existing resort a distinct arrival and
public-interior treatment based on photographed architecture. Paris has an
iron-and-glass canopy and gilt registration salon; Caesars has a coffered
arrival dome and imperial statue; Cosmopolitan has illuminated columns and
crystal drapery; Flamingo, Horseshoe and Planet Hollywood have their own
entrance, carpet, ceiling and registration designs. ARIA's silver river,
Vdara's geometric reception artwork, Waldorf's marble/brass gallery and
Veer's residential lounges differentiate the CityCenter properties. Crystals
retains its folded architecture with refined entries and installations.
Bellagio's covered arrival is preserved and its reception is enriched.

These are compressed, photo-informed reconstructions, not exact floor plans.
Reference photos remain research files; authored geometry and original textures
are used in the game. Existing public circulation, guest-floor streaming,
visibility and door ownership are retained. See
`build/public-resorts/DESIGN.md` and `build/public-resorts/references/sources.json`.
