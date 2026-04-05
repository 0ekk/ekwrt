#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
. "$SCRIPT_DIR/lib/common.sh"

ROOT="$(repo_root)"
WORK_DIR="${WORK_DIR:-$ROOT/work}"
BUILDROOT_DIR="${BUILDROOT_DIR:-$WORK_DIR/openwrt}"

mkdir -p "$WORK_DIR"
load_kv_config "$ROOT/config/upstream.conf"

: "${UPSTREAM_REPO:?UPSTREAM_REPO is required}"
: "${UPSTREAM_REF_TYPE:?UPSTREAM_REF_TYPE is required}"
: "${UPSTREAM_REF:?UPSTREAM_REF is required}"

UPSTREAM_URL="${UPSTREAM_URL:-https://github.com/${UPSTREAM_REPO}.git}"
rm -rf "$BUILDROOT_DIR"

case "$UPSTREAM_REF_TYPE" in
  branch)
    git clone --filter=blob:none --single-branch --branch "$UPSTREAM_REF" "$UPSTREAM_URL" "$BUILDROOT_DIR"
    ;;
  tag)
    git clone --filter=blob:none --branch "$UPSTREAM_REF" "$UPSTREAM_URL" "$BUILDROOT_DIR"
    ;;
  commit)
    git clone --filter=blob:none "$UPSTREAM_URL" "$BUILDROOT_DIR"
    git -C "$BUILDROOT_DIR" fetch --depth 1 origin "$UPSTREAM_REF"
    git -C "$BUILDROOT_DIR" checkout --detach "$UPSTREAM_REF"
    ;;
  *)
    echo "Unsupported UPSTREAM_REF_TYPE: $UPSTREAM_REF_TYPE" >&2
    exit 1
    ;;
esac

printf 'BUILDROOT_DIR=%s\n' "$BUILDROOT_DIR"
printf 'UPSTREAM_COMMIT=%s\n' "$(git -C "$BUILDROOT_DIR" rev-parse HEAD)"
