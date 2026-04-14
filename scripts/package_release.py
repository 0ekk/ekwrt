#!/usr/bin/env python3
import re
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


KEEP_FILES = ("config.buildinfo", "feeds.buildinfo", "version.buildinfo")
PACKAGE_DEFINE_PATTERN = re.compile(r"^\s*define\s+Package/([A-Za-z0-9_.+-]+)\s*$")


def copy_buildinfo(target_dir: Path, dist_dir: Path) -> None:
    bin_dir = target_dir.parents[2]
    for name in KEEP_FILES:
        candidates = [target_dir / name, bin_dir / name]
        source = next((path for path in candidates if path.is_file()), None)
        if source is None:
            raise FileNotFoundError(f"Missing required file: {name} (checked {candidates[0]} and {candidates[1]})")
        shutil.copy2(source, dist_dir / name)


def extract_turboacc_package_names(buildroot_dir: Path) -> set[str]:
    turboacc_dir = buildroot_dir / "package" / "turboacc"
    if not turboacc_dir.is_dir():
        return set()

    names: set[str] = set()
    for makefile in turboacc_dir.rglob("Makefile"):
        for line in makefile.read_text(encoding="utf-8", errors="ignore").splitlines():
            match = PACKAGE_DEFINE_PATTERN.match(line)
            if match:
                names.add(match.group(1))
    return names


def ensure_turboacc_packages_present(target_dir: Path, buildroot_dir: Path) -> None:
    package_names = extract_turboacc_package_names(buildroot_dir)
    missing = [name for name in sorted(package_names) if not list(target_dir.rglob(f"{name}-*.apk"))]
    if missing:
        raise FileNotFoundError(
            "Missing turboacc package artifacts: "
            + ", ".join(missing)
            + f" under {target_dir}"
        )


def pick_apk_tool(buildroot_dir: Path) -> str | None:
    buildroot_apk = buildroot_dir / "staging_dir" / "host" / "bin" / "apk"
    if buildroot_apk.is_file():
        return str(buildroot_apk)
    return None


def ensure_packages_index_valid(packages_dir: Path, buildroot_dir: Path) -> None:
    index = packages_dir / "packages.adb"
    if not index.is_file():
        raise FileNotFoundError(f"Missing required index: {index}")
    if index.stat().st_size == 0:
        raise ValueError(f"Empty packages index: {index}")

    apk_tool = pick_apk_tool(buildroot_dir)
    if apk_tool is None:
        return
    subprocess.run(
        [apk_tool, "adbdump", "--format", "json", str(index)],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
    )


def create_apks_archive(target_dir: Path, dist_dir: Path) -> None:
    buildroot_dir = target_dir.parents[3]
    packages_dir = target_dir / "packages"
    if not packages_dir.is_dir():
        raise FileNotFoundError(f"Missing required packages directory: {packages_dir}")

    ensure_turboacc_packages_present(target_dir, buildroot_dir)
    ensure_packages_index_valid(packages_dir, buildroot_dir)

    with tempfile.TemporaryDirectory() as tmp:
        work_dir = Path(tmp)

        stage_dir = work_dir / "stage"
        shutil.copytree(packages_dir, stage_dir / "packages")
        entries = ["packages"]
        kmods_dir = target_dir / "kmods"
        if kmods_dir.is_dir():
            shutil.copytree(kmods_dir, stage_dir / "kmods")
            entries.append("kmods")

        subprocess.run(
            ["tar", "-C", str(stage_dir), "--zstd", "-cf", str(dist_dir / "apks.tar.zst"), *entries],
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
