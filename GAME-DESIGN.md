# Vegas: the city

A walkable, drivable Las Vegas Strip and the blocks around it, rebuilt from public map data and public references, for
anyone to use as the setting of their own game. This project is the **city only**: it carries a minimal set of
game-specific material. Games add themselves as a game layer (`src/work/GameLayers.ts`); the zombie-survival game
"Vegas: Afterlight" is the first, in its own project.

## What the player can do in the city

- Walk anywhere in first person, and run.
- Drive the jeep: E gets in and out, with road speed assist.
- Kick open the door of any hotel room (F), and walk the corridors, stairs and rooms of 64 towers.
- Ride the Eiffel Tower lift at Paris (L), and the Big Apple Coaster at New York-New York.
- Walk into the public interiors: the Venetian and its Grand Canal Shoppes, Bellagio, Paris, the Cosmopolitan, the LINQ,
  Park MGM, Treasure Island, Harrah's, Fashion Show and the Sphere.
- Open statistics and settings with B (frame time, streaming, sun-shadow reach, foliage).

There is no score, no mission and no enemy: those belong to a game built on the city.

## Look

- **Realistic, not stylised.** The aim is architectural proportions and grounded materials, matched building by
  building against Google Earth and public photos.
- **Daylight by default.** Night, neon, dusk and rain are presets of the same city (`src/work/film/FilmLook.ts`,
  `ScenePreset.ts`), not new models.
- **The Bitmagic `low-poly` switch** enables mesh rendering. It does not describe the aesthetic.

## Map

- **Units:** metres. X east, Y up, Z south (geographic north is −Z).
- **Origin:** longitude −115.173, latitude 36.116.
- **Coverage:** the Strip from Mandalay Bay to the STRAT, about 8.3 km, with the streets and blocks either side.
- **Spawn:** the Bellagio forecourt, beside the jeep's bay.

## Rules that shape everything

Everything heavy streams. Every room and venue is reachable, but nothing loads or draws until the player or the film
camera is near it. Lights are created at boot and never added or removed while the city runs. Runtime data lives in
typed arrays. AGENTS.md has the details and the measurements behind them.
