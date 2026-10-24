# Las Vegas Strip

The real Las Vegas Strip, rebuilt building by building for the browser. Walk it, drive it and go inside: 6,162
buildings, the resorts modelled from public references, and hotel rooms, casinos and shops you can enter. Built by AI
agents on the [Bitmagic](https://bitmagic.ai) engine.

## Make it your own

Fork it, remix it, build on it: a game, a film, a tour, an experiment. Add your game as a layer and the city stays
easy to update underneath it ([docs/BUILD-ON-IT.md](docs/BUILD-ON-IT.md)). Credit the city as shown below.

## Run it

**Running it needs a [Bitmagic Pro](https://bitmagic.ai) subscription.** The Bitmagic engine is not in this
repository: the Bitmagic CLI installs it. You also need Node 20+, pnpm, [Git LFS](https://git-lfs.com) and a WebGPU
browser (current Chrome).

```bash
npm i -g @bitmagic/cli && bitmagic login
git lfs install && git clone https://github.com/BitmagicAI/las-vegas-strip.git
cd las-vegas-strip && bitmagic upgrade && pnpm install && bitmagic dev
```

Open the URL `bitmagic dev` prints and click Play: WASD and the mouse to walk, E for the jeep, F to kick a hotel-room
door open, V to switch the view, B for settings. The clone brings about 1.1 GiB of models and data through Git LFS
([docs/ASSETS.md](docs/ASSETS.md)).

## More

- [What is in the city](docs/THE-CITY.md), and [what is missing](STATUS.md)
- [Building on it](docs/BUILD-ON-IT.md): your own game, other engines, credits
- [Contributing](CONTRIBUTING.md) and the [task board](tasks/BOARD.md)
- [How it was made](docs/HOW-IT-WAS-MADE.md)

## Licence

Code: MIT ([LICENSE](LICENSE)). Original models, textures, data and documentation: CC BY 4.0
([LICENSE-CONTENT.md](LICENSE-CONTENT.md)). OpenStreetMap-derived data: ODbL ([LICENSE-DATA.md](LICENSE-DATA.md)).
The Bitmagic engine is not part of this repository and has its own licence. Third-party credits:
[NOTICE.md](NOTICE.md). Credit the city as:

> Las Vegas Strip (https://github.com/BitmagicAI/las-vegas-strip), CC BY 4.0 · Map data © OpenStreetMap contributors, ODbL

This project depicts real places. It is not affiliated with, sponsored by or endorsed by any property owner or brand
shown, and all trademarks belong to their owners.
