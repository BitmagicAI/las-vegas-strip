#!/bin/zsh
# Encode the info video. Frames: .bitmagic/info-video/frames/<name>/fNNNNN.(jpg|png) at 60 fps; audio: .bitmagic/info-video/audio/soundtrack.wav.
#   zsh tools/info-video/encode.sh preview   -> .bitmagic/info-video/vegas-info-preview.mp4 (1x JPEG frames, CRF 18)
#   zsh tools/info-video/encode.sh final     -> "$HOME/Movies/Vegas Afterlight/Vegas Afterlight - how AI agents built Las Vegas - 1080p60.mp4"
#                                              (2x PNG frames, lanczos downscale = supersampled, CRF 12, AAC 320k)
set -e
cd "${0:A:h}/../.."
B=.bitmagic/info-video
COLOR=(-colorspace bt709 -color_primaries bt709 -color_trc bt709 -color_range tv)
if [[ $1 == preview ]]; then
  ffmpeg -v error -stats -y -framerate 60 -i $B/frames/preview/f%05d.jpg -i $B/audio/soundtrack.wav \
    -vf "scale=1920:1080:flags=lanczos:out_color_matrix=bt709:out_range=tv,format=yuv420p" \
    -c:v libx264 -preset medium -crf 18 $COLOR -c:a aac -b:a 256k -shortest -movflags +faststart $B/vegas-info-preview.mp4
  echo $B/vegas-info-preview.mp4
else
  OUT="$HOME/Movies/Vegas Afterlight"; mkdir -p "$OUT"
  ffmpeg -v error -stats -y -framerate 60 -i $B/frames/final/f%05d.png -i $B/audio/soundtrack.wav \
    -vf "scale=1920:1080:flags=lanczos:out_color_matrix=bt709:out_range=tv,format=yuv420p" \
    -c:v libx264 -preset slow -crf 12 -profile:v high $COLOR \
    -c:a aac -b:a 320k -shortest -movflags +faststart "$OUT/Vegas Afterlight - how AI agents built Las Vegas - 1080p60.mp4"
  echo "$OUT/Vegas Afterlight - how AI agents built Las Vegas - 1080p60.mp4"
fi
