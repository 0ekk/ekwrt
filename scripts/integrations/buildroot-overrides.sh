#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
. "$SCRIPT_DIR/../lib/common.sh"

ROOT="$(repo_root)"
BUILDROOT_DIR="${BUILDROOT_DIR:?BUILDROOT_DIR is required}"
OVERRIDES_DIR="${OVERRIDES_DIR:-$ROOT/overrides/buildroot}"

[ -d "$OVERRIDES_DIR" ] || exit 0

copy_override() {
  local relative_path="$1"
  local source_path="$OVERRIDES_DIR/$relative_path"
  local target_path="$BUILDROOT_DIR/$relative_path"

  [ -f "$target_path" ] || return 0
  mkdir -p "$(dirname "$target_path")"
  install -m 0644 "$source_path" "$target_path"
}

while IFS= read -r source_path; do
  relative_path="${source_path#$OVERRIDES_DIR/}"
  case "$relative_path" in
    feeds/packages/net/fail2ban/Makefile)
      target_path="$BUILDROOT_DIR/$relative_path"
      if [ -f "$target_path" ] && grep -q 'python3-pkg-resources' "$target_path"; then
        copy_override "$relative_path"
      fi
      ;;
  esac
done < <(find "$OVERRIDES_DIR" -type f | sort)
