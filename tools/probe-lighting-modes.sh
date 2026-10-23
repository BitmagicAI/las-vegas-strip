#!/bin/sh
# Boots the game once per renderer.lighting mode (?lighting=..., local experiment switch in Game.ts) and
# measures the same views as fixed (game-side light lists on) and unfixed (every lit material on the scene list).
# Output: build/probe/interiors/mode-<mode>/. Sequential: one headless Chrome at a time.
set -u
AT="jeep-west=-60,0.4,540,3.1416,-0.1;garden=-60,0.4,540,1.5708,0;trees=-120,0.4,470,0.8,-0.05;strip-n=0,0.4,300,3.1416,0.05"
GRP='movers=^Body$|charging bay|^Vegas character|^HeadlessPlayer$,foliage=*^Bellagio botanical planting$'
for mode in ${MODES:-three engine64 engine32 engine16 engine8 clustered}; do
  q=""; [ "$mode" != three ] && q="lighting=$mode"
  echo "=== $mode"
  node tools/probe-interiors.mjs --name "mode-$mode" ${q:+--query "$q"} --views corridor-caesars,jeep-west,garden,trees,strip-n \
    --at "$AT" --groups "$GRP" --ablate --ablate-shots --ablations "interior-full-lights+movers-full-lights+foliage-full-lights"
done
