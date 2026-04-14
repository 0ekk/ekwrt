#!/usr/bin/env python3
import os
import shutil
import subprocess
import sys
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
    missing = [name for name in APK_DIRS if not (target_dir / name).is_dir()]
    if missing:
        raise FileNotFoundError(f"Missing required directories under {target_dir}: {', '.join(missing)}")

    subprocess.run(
        ["tar", "-C", str(target_dir), "--zstd", "-cf", str(dist_dir / "apks.tar.zst"), *APK_DIRS],
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
