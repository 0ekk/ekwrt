#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
. "$SCRIPT_DIR/../lib/common.sh"

ROOT="$(repo_root)"
BUILDROOT_DIR="${BUILDROOT_DIR:?BUILDROOT_DIR is required}"
load_kv_config "$ROOT/config/release.conf"

TURBOACC_MODE="${TURBOACC_MODE:-sfe}"
ADD_SCRIPT_URL="${ADD_SCRIPT_URL:-https://raw.githubusercontent.com/chenmozhijin/turboacc/luci/add_turboacc.sh}"

case "$TURBOACC_MODE" in
  sfe)
    ARGS=()
    ;;
  no-sfe)
    ARGS=(--no-sfe)
    ;;
  *)
    echo "Unsupported TURBOACC_MODE: $TURBOACC_MODE" >&2
    exit 1
    ;;
esac

cd "$BUILDROOT_DIR"
rm -rf package/turboacc
curl -fsSL "$ADD_SCRIPT_URL" -o "$BUILDROOT_DIR/add_turboacc.sh"
bash "$BUILDROOT_DIR/add_turboacc.sh" "${ARGS[@]}"
rm -f "$BUILDROOT_DIR/add_turboacc.sh"
