#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
. "$SCRIPT_DIR/lib/common.sh"

ROOT="$(repo_root)"
BUILDROOT_DIR="${BUILDROOT_DIR:?BUILDROOT_DIR is required}"

declare -A AVAILABLE=()
while IFS= read -r pkg; do
  [ -n "$pkg" ] || continue
  AVAILABLE["$pkg"]=1
done < <("$BUILDROOT_DIR/scripts/feeds" list -n 2>/dev/null | awk '{print $1}')

missing=()
while IFS= read -r pkg; do
  [ -n "$pkg" ] || continue
  if [ -z "${AVAILABLE[$pkg]:-}" ]; then
    missing+=("$pkg")
  fi
done < <(cat "$ROOT/config/builtin-packages.txt" "$ROOT/config/ondemand-packages.txt" | grep -Ev '^\s*(#|$)')

if [ "${#missing[@]}" -gt 0 ]; then
  printf 'Missing packages for selected upstream:\n' >&2
  printf '  %s\n' "${missing[@]}" >&2
  exit 1
fi
