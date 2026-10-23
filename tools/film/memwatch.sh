#!/bin/zsh
# Memory guard for long recordings (a raw 2880x1620 final exhausted the Mac's 128 GB on 2026-10-08):
#   tools/film/memwatch.sh <log> [min free %]   (run in the background beside tools/film/record.mjs)
# Every 5 s logs system free %, swap, and the RSS of the recorder's browser tree, the dev server and ffmpeg; kills the
# recorder (SIGTERM, its watchdog closes the browser) when system free memory drops under the floor (default 40 %).
LOG=$1; FLOOR=${2:-40}; : > $LOG
tree_rss() { # RSS (KB) of a pid and all its descendants
  local total=0 p
  for p in $(pgrep -P $1) $1; do total=$((total + $(ps -o rss= -p $p 2>/dev/null || echo 0))); done
  for p in $(pgrep -P $1); do for c in $(pgrep -P $p); do total=$((total + $(tree_rss $c))); done; done
  echo $total
}
while true; do
  rec=$(pgrep -f "^node tools/film/record.mjs" | head -1)
  free=$(memory_pressure | awk -F': ' '/free percentage/{gsub("%","",$2);print $2}')
  swap=$(sysctl -n vm.swapusage | awk '{print $6}')
  dev=$(pgrep -f "bitmagic dev" | head -1); devrss=$(( $(ps -o rss= -p ${dev:-1} 2>/dev/null || echo 0) / 1024 ))
  ff=$(( $(ps -ax -o rss=,comm= | awk '/ffmpeg/{s+=$1}END{print s+0}') / 1024 ))
  recrss=$(( ${rec:+$(tree_rss $rec)}0 / 10240 ))
  echo "$(date +%H:%M:%S) free ${free}% swap-used ${swap} recorder-tree ${recrss} MB dev-server ${devrss} MB ffmpeg ${ff} MB" >> $LOG
  if [ -n "$free" ] && [ "$free" -lt "$FLOOR" ] && [ -n "$rec" ]; then echo "$(date +%H:%M:%S) FREE ${free}% < ${FLOOR}%: stopping the recorder" >> $LOG; kill -TERM $rec; fi
  [ -z "$rec" ] && [ -f $LOG.stop ] && break
  sleep 5
done
