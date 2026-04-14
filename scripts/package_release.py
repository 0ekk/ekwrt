#!/usr/bin/env python3
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


KEEP_FILES = ("config.buildinfo", "feeds.buildinfo", "version.buildinfo")
APK_DIRS = ("packages", "kmods")


def copy_buildinfo(target_dir: Path, dist_dir: Path) -> None:
    for name in KEEP_FILES:
        source = target_dir / name
        if not source.is_file():
            raise FileNotFoundError(f"Missing required file: {source}")
        shutil.copy2(source, dist_dir / name)


def create_apks_archive(target_dir: Path, dist_dir: Path) -> None:
    packages_dir = target_dir / "packages"
    if not packages_dir.is_dir():
        raise FileNotFoundError(f"Missing required directory: {packages_dir}")

    kmods_dir = target_dir / "kmods"
    if kmods_dir.is_dir():
        subprocess.run(
            ["tar", "-C", str(target_dir), "--zstd", "-cf", str(dist_dir / "apks.tar.zst"), *APK_DIRS],
            check=True,
        )
        return

    # Keep official layout compatibility even when non-BUILDBOT builds do not emit kmods/.
    with tempfile.TemporaryDirectory() as tmp:
        staging_dir = Path(tmp)
        shutil.copytree(packages_dir, staging_dir / "packages")
        (staging_dir / "kmods").mkdir()
        subprocess.run(
            ["tar", "-C", str(staging_dir), "--zstd", "-cf", str(dist_dir / "apks.tar.zst"), *APK_DIRS],
            check=True,
        )


def main() -> int:
    target_dir = Path(os.environ["TARGET_DIR"])
    dist_dir = Path(os.environ["DIST_DIR"])

    dist_dir.mkdir(parents=True, exist_ok=True)
    for path in dist_dir.iterdir():
        if path.is_file():
            path.unlink()

    copy_buildinfo(target_dir, dist_dir)
    create_apks_archive(target_dir, dist_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main())
