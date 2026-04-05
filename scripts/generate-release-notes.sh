#!/usr/bin/env bash
set -euo pipefail

DIST_DIR="${DIST_DIR:?DIST_DIR is required}"

if [ ! -f "$DIST_DIR/release-notes.md" ]; then
  echo "Missing $DIST_DIR/release-notes.md" >&2
  exit 1
fi

cat "$DIST_DIR/release-notes.md"
