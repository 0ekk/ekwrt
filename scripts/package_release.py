#!/usr/bin/env python3
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


IMAGE_SUFFIXES = (
    "-generic-ext4-combined-efi.img.gz",
    "-generic-kernel.bin",
    "-rootfs.tar.gz",
)
KEEP_PATTERNS = (
    "*-generic-ext4-combined-efi.img.gz",
    "*-generic-kernel.bin",
    "*-rootfs.tar.gz",
    "*.manifest",
    "config.buildinfo",
    "feeds.buildinfo",
    "version.buildinfo",
    "profiles.json",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def row(path: Path) -> dict[str, object]:
    return {"name": path.name, "sha256": sha256(path), "size": path.stat().st_size}


def render_table(title: str, rows: list[dict[str, object]]) -> str:
    lines = [f"<h2>{title}</h2>", "<table>", "<tr><th>Filename</th><th>sha256sum</th><th>Size</th></tr>"]
    for item in rows:
        lines.append(
            f"<tr><td>{item['name']}</td><td><code>{item['sha256']}</code></td><td>{item['size']}</td></tr>"
        )
    lines.append("</table>")
    return "\n".join(lines)


def copy_selected_files(target_dir: Path, dist_dir: Path) -> None:
    for pattern in KEEP_PATTERNS:
        for source in target_dir.glob(pattern):
            if source.is_file():
                shutil.copy2(source, dist_dir / source.name)


def create_tar_zst(target_dir: Path, dist_dir: Path, name: str) -> None:
    source_dir = target_dir / name
    if not source_dir.is_dir():
        return
    subprocess.run(
        ["tar", "-C", str(target_dir), "--zstd", "-cf", str(dist_dir / f"{name}.tar.zst"), name],
        check=True,
    )


def write_metadata(dist_dir: Path, release_name: str) -> None:
    files = sorted([path for path in dist_dir.iterdir() if path.is_file()])
    image_files = [row(path) for path in files if path.name.endswith(IMAGE_SUFFIXES)]
    image_names = {item["name"] for item in image_files}
    supplementary_files = [row(path) for path in files if path.name not in image_names]

    metadata = {
        "release_name": release_name,
        "image_files": image_files,
        "supplementary_files": supplementary_files,
    }
    (dist_dir / "release-metadata.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{release_name}</title>
  <style>
    body {{ font-family: Helvetica, Arial, sans-serif; margin: 2rem auto; max-width: 1100px; background: #ddd; color: #333; }}
    table {{ width: 100%; border-collapse: collapse; margin-bottom: 2rem; background: rgba(255,255,255,.85); }}
    th, td {{ border: 1px solid #ccc; padding: .4rem .6rem; text-align: left; }}
    th {{ background: #111; color: white; }}
    code {{ font-size: .9em; }}
  </style>
</head>
<body>
  <h1>Index of {release_name}</h1>
  {render_table("Image Files", image_files)}
  {render_table("Supplementary Files", supplementary_files)}
</body>
</html>
"""
    (dist_dir / "index.html").write_text(html, encoding="utf-8")

    md_lines = [f"# {release_name}", "", "## Image Files", "", "| Filename | sha256sum | Size |", "| --- | --- | ---: |"]
    for item in image_files:
        md_lines.append(f"| {item['name']} | `{item['sha256']}` | {item['size']} |")
    md_lines.extend(["", "## Supplementary Files", "", "| Filename | sha256sum | Size |", "| --- | --- | ---: |"])
    for item in supplementary_files:
        md_lines.append(f"| {item['name']} | `{item['sha256']}` | {item['size']} |")
    (dist_dir / "release-notes.md").write_text("\n".join(md_lines) + "\n", encoding="utf-8")


def main() -> int:
    target_dir = Path(os.environ["TARGET_DIR"])
    dist_dir = Path(os.environ["DIST_DIR"])
    release_name = os.environ.get("RELEASE_NAME", "release")

    dist_dir.mkdir(parents=True, exist_ok=True)
    for path in dist_dir.iterdir():
        if path.is_file():
            path.unlink()

    copy_selected_files(target_dir, dist_dir)
    create_tar_zst(target_dir, dist_dir, "packages")
    create_tar_zst(target_dir, dist_dir, "kmods")
    write_metadata(dist_dir, release_name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
