#!/usr/bin/env python3
import os
import subprocess
import sys
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


def run_script_integration(root: Path, buildroot_dir: str, name: str, script_path: str) -> None:
    env = os.environ.copy()
    env["INTEGRATION_NAME"] = name
    env["BUILDROOT_DIR"] = buildroot_dir
    subprocess.run(["bash", str(root / script_path)], check=True, env=env)


def main() -> int:
    root = repo_root()
    integrations_dir = Path(os.environ.get("INTEGRATIONS_DIR", root / "config" / "integrations.d"))
    buildroot_dir = os.environ.get("BUILDROOT_DIR")
    if not buildroot_dir:
      raise SystemExit("BUILDROOT_DIR is required")

    for config_path in sorted(integrations_dir.glob("*.conf")):
        config = load_kv_config(config_path)
        name = config.get("NAME")
        if not name or config.get("ENABLED", "1") != "1":
            continue
        integration_type = config.get("TYPE", "")
        if integration_type != "script":
            raise SystemExit(f"Unsupported integration TYPE in {config_path}: {integration_type}")
        run_script_integration(root, buildroot_dir, name, config["SCRIPT"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
