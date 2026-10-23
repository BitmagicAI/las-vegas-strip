#!/bin/sh
# Installs the glTF tools the GLB optimizer needs into tools/optimize/bm-tools/gltf (ignored by git), at the versions
# the installed set was made with. The encoder script itself ships with the Bitmagic CLI (0.1.81+).
# Run once from the project root:  sh tools/optimize/setup-tools.sh
set -e
cd "$(dirname "$0")/../.."
mkdir -p tools/optimize/bm-tools/gltf
npm install --prefix tools/optimize/bm-tools/gltf --no-save --no-package-lock \
  @gltf-transform/core@4.5.1 @gltf-transform/extensions@4.5.1 @gltf-transform/functions@4.5.1 \
  meshoptimizer@1.2.0 sharp@0.35.5 gltf-validator@2.0.0-dev.3.10
echo "Ready: node tools/optimize/optimize-runtime-glbs.mjs (see AGENTS.md, Runtime GLBs)"
