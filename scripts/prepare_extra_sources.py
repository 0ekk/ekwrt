#!/usr/bin/env python3
import os
import shutil
import subprocess
import sys
import tarfile
import urllib.request
from pathlib import Path


def repo_root() -> Path:
    env_root = os.environ.get("REPO_ROOT")
    if env_root:
        return Path(env_root).resolve()
    return Path(__file__).resolve().parents[1]


def load_kv_config(path: Path) -> dict[str, str]:
    data: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        key, value = line.split("=", 1)
        data[key] = value.strip().strip('"')
    return data


def emit_feed(feed_out: Path, name: str, dest: Path) -> None:
    line = f"src-link ek_{name} {dest}\n"
    with feed_out.open("a", encoding="utf-8") as fh:
        fh.write(line)
    sys.stdout.write(line)


def process_git(extra_root: Path, feed_out: Path, config: dict[str, str]) -> None:
    name = config["NAME"]
    dest = extra_root / name
    shutil.rmtree(dest, ignore_errors=True)
    subprocess.run(["git", "clone", config["URL"], str(dest)], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    ref = config.get("REF", "")
    if ref and ref != "HEAD":
        subprocess.run(["git", "-C", str(dest), "checkout", ref], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    link_path = dest / config["SUBDIR"] if config.get("SUBDIR") else dest
    emit_feed(feed_out, name, link_path)


def process_archive(work_dir: Path, extra_root: Path, feed_out: Path, config: dict[str, str]) -> None:
    name = config["NAME"]
    dest = extra_root / name
    archive = work_dir / f"{name}.archive"
    shutil.rmtree(dest, ignore_errors=True)
    archive.unlink(missing_ok=True)
    dest.mkdir(parents=True, exist_ok=True)
    urllib.request.urlretrieve(config["URL"], archive)
    strip_components = int(config.get("STRIP_COMPONENTS", "0"))
    with tarfile.open(archive) as tar:
        members = tar.getmembers()
        if strip_components:
            for member in members:
                parts = Path(member.name).parts[strip_components:]
                if not parts:
                    continue
                member.name = str(Path(*parts))
                tar.extract(member, dest)
        else:
            tar.extractall(dest)
    emit_feed(feed_out, name, dest)


def process_script(root: Path, extra_root: Path, feed_out: Path, config: dict[str, str]) -> None:
    name = config["NAME"]
    dest = extra_root / name
    shutil.rmtree(dest, ignore_errors=True)
    dest.mkdir(parents=True, exist_ok=True)
    subprocess.run(["bash", str(root / config["SCRIPT"]), str(dest)], check=True)
    emit_feed(feed_out, name, dest)


def main() -> int:
    root = repo_root()
    work_dir = Path(os.environ.get("WORK_DIR", root / "work"))
    sources_dir = root / "config" / "sources.d"
    extra_root = work_dir / "extra-sources"
    feed_out = Path(os.environ.get("FEEDS_CONF_OUTPUT", work_dir / "feeds.extra.conf"))

    extra_root.mkdir(parents=True, exist_ok=True)
    feed_out.parent.mkdir(parents=True, exist_ok=True)
    feed_out.write_text("", encoding="utf-8")

    for config_path in sorted(sources_dir.glob("*.conf")):
        config = load_kv_config(config_path)
        if not config.get("NAME"):
            continue
        source_type = config.get("TYPE", "")
        if source_type == "git":
            process_git(extra_root, feed_out, config)
        elif source_type == "archive":
            process_archive(work_dir, extra_root, feed_out, config)
        elif source_type == "script":
            process_script(root, extra_root, feed_out, config)
        else:
            raise SystemExit(f"Unsupported TYPE in {config_path}: {source_type}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
