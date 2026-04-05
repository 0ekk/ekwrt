#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
. "$SCRIPT_DIR/lib/common.sh"

ROOT="$(repo_root)"
OVERLAY_DIR="${OVERLAY_DIR:?OVERLAY_DIR is required}"
RELEASE_TAG="${RELEASE_TAG:?RELEASE_TAG is required}"
GITHUB_REPOSITORY="${GITHUB_REPOSITORY:?GITHUB_REPOSITORY is required}"

mkdir -p "$OVERLAY_DIR"
if [ -d "$ROOT/files" ]; then
  cp -a "$ROOT/files/." "$OVERLAY_DIR/"
fi
mkdir -p "$OVERLAY_DIR/etc"
cat > "$OVERLAY_DIR/etc/ekwrt-release" <<EOF
GITHUB_REPOSITORY=$GITHUB_REPOSITORY
RELEASE_TAG=$RELEASE_TAG
EOF
cp "$ROOT/config/ondemand-packages.txt" "$OVERLAY_DIR/etc/ondemand-packages.txt"
