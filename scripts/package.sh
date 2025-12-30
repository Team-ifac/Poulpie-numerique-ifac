#!/usr/bin/env bash
set -euo pipefail
ZIP_NAME=${1:-ressourcerie-ifac.zip}
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"
rm -f "$ZIP_NAME"
zip -r "$ZIP_NAME" \
  app.py README.md package.json index.html css js images pages public \
  -x "public/uploads/*" "__pycache__/*" "*/__pycache__/*" "data.sqlite"
echo "Archive créée : $ZIP_NAME"
