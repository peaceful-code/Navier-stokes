#!/bin/zsh
set -euo pipefail
cd "$(dirname "$0")/.."
export MPLCONFIGDIR="$PWD/.runtime/mplconfig"
export XDG_CACHE_HOME="$PWD/.runtime/cache"
export PYVISTA_OFF_SCREEN=true
PYTHON="$PWD/.venv/bin/python"
BLENDER="$PWD/.runtime/Blender.app/Contents/MacOS/Blender"
if [[ ! -x "$PYTHON" || ! -x "$BLENDER" ]]; then
  print -u2 'Dépendances locales absentes : consulter rendering/README.md.'
  exit 1
fi
"$PYTHON" -m rendering.model.checks
"$PYTHON" rendering/coordinate_geometry.py --outdir output/render3d/geometry --frames 108
"$PYTHON" rendering/build_vortex.py --preview
"$BLENDER" --background --python-exit-code 1 --python rendering/blender_scene.py -- \
  --input output/render3d/vortex.ply --outdir output/render3d \
  --title 'Vortex : champ local de comparaison' \
  --subtitle 'Paramètres exploratoires — la solution complète n’est pas reconstruite' \
  --width 1600 --height 1200 --samples 48 --frames 96 --frame-samples 20
ffmpeg -hide_banner -loglevel error -y -framerate 24 -start_number 1 \
  -i output/render3d/turntable/frame_%04d.png -c:v libx264 -crf 19 \
  -pix_fmt yuv420p -movflags +faststart output/render3d/rotation_camera.mp4
"$PYTHON" rendering/make_verification.py
