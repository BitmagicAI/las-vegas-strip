#!/bin/zsh
# Static server for the story page (project root on 127.0.0.1:8098). Local only. Run in the background.
cd "${0:A:h}/../.." && exec python3 -m http.server 8098 --bind 127.0.0.1
