#!/usr/bin/env python3
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


KEEP_FILES = ("config.buildinfo", "feeds.buildinfo", "version.buildinfo")


def copy_buildinfo(target_dir: Path, dist_dir: Path) -> None:
    bin_dir = target_dir.parents[2]
    for name in KEEP_FILES:
        candidates = [target_dir / name, bin_dir / name]
        source = next((path for path in candidates if path.is_file()), None)
        if source is None:
            raise FileNotFoundError(f"Missing required file: {name} (checked {candidates[0]} and {candidates[1]})")
        shutil.copy2(source, dist_dir / name)


def collect_packages_dir(target_dir: Path, work_dir: Path) -> Path:
    direct = target_dir / "packages"
    if direct.is_dir():
        return direct

    root = work_dir / "packages"
    root.mkdir(parents=True, exist_ok=True)
    candidates = sorted(path for path in target_dir.rglob("*.apk") if path.is_file())
    if not candidates:
        raise FileNotFoundError(f"Missing package artifacts under {target_dir}")
    for pkg in candidates:
        shutil.copy2(pkg, root / pkg.name)
    for index_name in ("packages.adb", "APKINDEX.tar.gz"):
        for index in target_dir.rglob(index_name):
            if index.is_file():
                shutil.copy2(index, root / index.name)
                break
    return root


def split_kmods(packages_dir: Path, work_dir: Path) -> Path:
    out_dir = work_dir / "kmods"
    out_dir.mkdir(parents=True, exist_ok=True)
    for pkg in packages_dir.rglob("kmod-*.apk"):
        if pkg.is_file():
            shutil.copy2(pkg, out_dir / pkg.name)
    return out_dir


def create_apks_archive(target_dir: Path, dist_dir: Path) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        work_dir = Path(tmp)
        packages_dir = collect_packages_dir(target_dir, work_dir)
        kmods_dir = target_dir / "kmods"
        if kmods_dir.is_dir():
            effective_kmods = kmods_dir
        else:
            effective_kmods = split_kmods(packages_dir, work_dir)

        stage_dir = work_dir / "stage"
        shutil.copytree(packages_dir, stage_dir / "packages")
        shutil.copytree(effective_kmods, stage_dir / "kmods")

        subprocess.run(
            ["tar", "-C", str(stage_dir), "--zstd", "-cf", str(dist_dir / "apks.tar.zst"), "packages", "kmods"],
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
