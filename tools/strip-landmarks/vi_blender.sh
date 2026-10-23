#!/bin/sh
# Run a Blender command for the Venetian interiors one at a time (several agents share this machine): waits for the
# lock directory build/venetian-interiors/.blender.lock, runs the command, releases the lock.
#   tools/strip-landmarks/vi_blender.sh blender -b --python tools/strip-landmarks/export.py -- grandCanal-interior
LOCK=build/venetian-interiors/.blender.lock
mkdir -p build/venetian-interiors
until mkdir "$LOCK" 2>/dev/null; do
  # a lock older than 30 minutes belongs to a run that died
  if [ -n "$(find "$LOCK" -maxdepth 0 -mmin +30 2>/dev/null)" ]; then rmdir "$LOCK" 2>/dev/null; fi
  sleep 3
done
trap 'rmdir "$LOCK" 2>/dev/null' EXIT INT TERM
"$@"
