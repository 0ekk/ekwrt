#!/usr/bin/env bash
set -euo pipefail

BUILDROOT_DIR="${BUILDROOT_DIR:?BUILDROOT_DIR is required}"
RELEASE_TOKEN="${RELEASE_TOKEN:?RELEASE_TOKEN is required}"

extract_default_version() {
  local version_mk="$BUILDROOT_DIR/include/version.mk"
  if [ ! -f "$version_mk" ]; then
    return 1
  fi
  sed -n 's/.*VERSION_NUMBER),\([^)]*\)).*/\1/p' "$version_mk" | head -n1
}

extract_buildinfo_release() {
  local buildinfo="$BUILDROOT_DIR/version.buildinfo"
  if [ ! -f "$buildinfo" ]; then
    return 1
  fi
  sed -n "s/^DISTRIB_RELEASE='\([^']*\)'/\1/p" "$buildinfo" | head -n1
}

UPSTREAM_BASE_VERSION="$(extract_default_version || true)"
if [ -z "$UPSTREAM_BASE_VERSION" ]; then
  UPSTREAM_BASE_VERSION="$(extract_buildinfo_release || true)"
fi
if [ -z "$UPSTREAM_BASE_VERSION" ]; then
  UPSTREAM_BASE_VERSION="snapshot-$(git -C "$BUILDROOT_DIR" rev-parse --short HEAD)"
fi

EK_VERSION="${UPSTREAM_BASE_VERSION}-ek-${RELEASE_TOKEN}"

printf 'UPSTREAM_BASE_VERSION=%s\n' "$UPSTREAM_BASE_VERSION"
printf 'EK_VERSION=%s\n' "$EK_VERSION"
