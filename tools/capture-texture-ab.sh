#!/bin/sh
# Captures the fixed street views plus hotel interiors (the lowest WebP PSNR) into build/probe/views/<prefix>-*.
# Usage: sh tools/capture-texture-ab.sh <prefix>
set -e
P=$1
node tools/probe-views.mjs --name "$P-street" --set all --sample 2 | tail -10
for v in "bellagio-corridor hotel=bellagio-north&floor=3&roomView=corridor" "bellagio-bedroom hotel=bellagio-north&floor=3&room=0&roomView=bedroom" "caesars-corridor hotel=caesars-palace&floor=3&roomView=corridor" "cosmo-corridor hotel=cosmo-boulevard&floor=3&roomView=corridor" "wynn-lobby hotel=wynn-1&floor=0&roomView=lobby"; do
  name=${v%% *}; query=${v#* }
  node tools/probe-views.mjs --name "$P-$name" --query "$query" --shot "$name" --sample 2 | tail -1
done
