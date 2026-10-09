#!/usr/bin/env bash
# Builds dist/NoJumpSniffers_v<version>.mcaddon from packs/BP.
set -euo pipefail
cd "$(dirname "$0")"

python3 tools/check.py

VERSION=$(python3 -c 'import json;print(".".join(map(str,json.load(open("packs/BP/manifest.json"))["header"]["version"])))')
mkdir -p dist
OUT="dist/NoJumpSniffers_v${VERSION}.mcaddon"
rm -f "$OUT"
# The .mcaddon is a plain zip with the BP folder at its root.
(cd packs && zip -qrX "../$OUT" BP -x '*.DS_Store')
echo "built $OUT"
unzip -l "$OUT"
