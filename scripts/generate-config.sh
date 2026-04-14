#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
. "$SCRIPT_DIR/lib/common.sh"

ROOT="$(repo_root)"
OUTPUT_CONFIG="${OUTPUT_CONFIG:-$ROOT/work/openwrt/.config}"
load_kv_config "$ROOT/config/release.conf"

: "${EK_VERSION:?EK_VERSION is required}"
: "${TARGET_BOARD:?TARGET_BOARD is required}"
: "${TARGET_SUBTARGET:?TARGET_SUBTARGET is required}"
: "${ROOTFS_PARTSIZE:?ROOTFS_PARTSIZE is required}"

mkdir -p "$(dirname "$OUTPUT_CONFIG")"

{
  printf 'CONFIG_TARGET_%s=y\n' "$TARGET_BOARD"
  printf 'CONFIG_TARGET_%s_%s=y\n' "$TARGET_BOARD" "$TARGET_SUBTARGET"
  printf 'CONFIG_TARGET_ROOTFS_PARTSIZE=%s\n' "$ROOTFS_PARTSIZE"
  printf 'CONFIG_TARGET_KERNEL_PARTSIZE=32\n'
  printf 'CONFIG_TARGET_IMAGES_GZIP=y\n'
  printf 'CONFIG_GRUB_EFI_IMAGES=y\n'
  printf '# CONFIG_GRUB_IMAGES is not set\n'
  printf '# CONFIG_ISO_IMAGES is not set\n'
  printf '# CONFIG_VDI_IMAGES is not set\n'
  printf '# CONFIG_VMDK_IMAGES is not set\n'
  printf '# CONFIG_VHDX_IMAGES is not set\n'
  printf 'CONFIG_TARGET_ROOTFS_EXT4FS=y\n'
  printf '# CONFIG_TARGET_ROOTFS_SQUASHFS is not set\n'
  printf 'CONFIG_TARGET_ROOTFS_TARGZ=y\n'
  printf 'CONFIG_VERSION_DIST="OpenWrt"\n'
  printf 'CONFIG_VERSION_NUMBER="%s"\n' "$EK_VERSION"
  printf 'CONFIG_BUILDBOT=y\n'
  printf 'CONFIG_PER_FEED_REPO=y\n'
  printf 'CONFIG_SIGNED_PACKAGES=y\n'
  printf 'CONFIG_SIGN_EACH_PACKAGE=y\n'
  printf 'CONFIG_PACKAGE_luci-app-turboacc=y\n'
  printf 'CONFIG_PACKAGE_ekwrt-keyring=m\n'
  while IFS= read -r pkg; do
    printf 'CONFIG_PACKAGE_%s=y\n' "$pkg"
  done < <(read_list_file "$ROOT/config/builtin-packages.txt")
  while IFS= read -r pkg; do
    printf 'CONFIG_PACKAGE_%s=m\n' "$pkg"
  done < <(read_list_file "$ROOT/config/ondemand-packages.txt")
} > "$OUTPUT_CONFIG"
