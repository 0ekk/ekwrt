#!/usr/bin/env bash
set -euo pipefail

repo_root() {
  if [ -n "${REPO_ROOT:-}" ]; then
    printf '%s\n' "$REPO_ROOT"
    return
  fi
  local script_dir
  script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
  printf '%s\n' "$script_dir"
}

load_kv_config() {
  local file="$1"
  [ -f "$file" ] || return 0
  while IFS='=' read -r key value; do
    [ -n "${key:-}" ] || continue
    case "$key" in
      \#*) continue ;;
    esac
    value="${value#\"}"
    value="${value%\"}"
    export "$key=$value"
  done < "$file"
}

read_list_file() {
  local file="$1"
  [ -f "$file" ] || return 0
  grep -Ev '^\s*(#|$)' "$file" || true
}

sanitize_token() {
  printf '%s' "$1" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9._-' '-'
}

json_escape() {
  python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))'
}
