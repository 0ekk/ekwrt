#!/usr/bin/env python3
import os
import re
import sys
from pathlib import Path


MAKEFILE_PACKAGE_PATTERN = re.compile(r"^define\s+(?:Package|KernelPackage)/(\S+)")
INDEX_PACKAGE_PATTERN = re.compile(r"^Package:\s+(\S+)")
SIMPLE_ASSIGNMENT_PATTERN = re.compile(r"^([A-Za-z0-9_]+)\s*:?=\s*(.+)$")


def repo_root() -> Path:
    env_root = os.environ.get("REPO_ROOT")
    if env_root:
        return Path(env_root).resolve()
    return Path(__file__).resolve().parents[1]


def read_list_file(path: Path) -> list[str]:
    if not path.exists():
        return []
    items: list[str] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        items.append(line)
    return items


def discover_local_packages(buildroot_dir: Path) -> set[str]:
    available: set[str] = set()
    base = buildroot_dir / "package"
    if not base.exists():
        return available
    for makefile in base.rglob("Makefile"):
        text = makefile.read_text(encoding="utf-8", errors="ignore")
        variables: dict[str, str] = {}
        for raw_line in text.splitlines():
            line = raw_line.strip()
            assign_match = SIMPLE_ASSIGNMENT_PATTERN.match(line)
            if assign_match:
                variables[assign_match.group(1)] = assign_match.group(2).strip()
            match = MAKEFILE_PACKAGE_PATTERN.match(line)
            if match:
                name = match.group(1)
                for key, value in variables.items():
                    name = name.replace(f"$({key})", value)
                available.add(name)
    return available


def discover_feed_packages(buildroot_dir: Path) -> set[str]:
    available: set[str] = set()
    feeds_dir = buildroot_dir / "feeds"
    if not feeds_dir.exists():
        return available
    for index_file in feeds_dir.glob("*.index"):
        text = index_file.read_text(encoding="utf-8", errors="ignore")
        for raw_line in text.splitlines():
            match = INDEX_PACKAGE_PATTERN.match(raw_line.strip())
            if match:
                available.add(match.group(1))
    return available


def main() -> int:
    root = repo_root()
    buildroot_dir = Path(os.environ["BUILDROOT_DIR"])
    requested = read_list_file(root / "config" / "builtin-packages.txt")
    requested.extend(read_list_file(root / "config" / "ondemand-packages.txt"))
    available = discover_feed_packages(buildroot_dir)
    available.update(discover_local_packages(buildroot_dir))
    missing = [pkg for pkg in requested if pkg not in available]
    if missing:
        sys.stderr.write("Missing packages for selected upstream:\n")
        for pkg in missing:
            sys.stderr.write(f"  {pkg}\n")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
