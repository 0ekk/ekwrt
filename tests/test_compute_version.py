import os
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "compute-version.sh"


class ComputeVersionTests(unittest.TestCase):
    def run_script(self, buildroot: Path, release_token: str) -> str:
        env = os.environ.copy()
        env["BUILDROOT_DIR"] = str(buildroot)
        env["RELEASE_TOKEN"] = release_token
        result = subprocess.run(
            [str(SCRIPT)],
            check=True,
            text=True,
            capture_output=True,
            env=env,
        )
        return result.stdout

    def test_uses_version_number_when_present(self):
        with tempfile.TemporaryDirectory() as tmp:
            buildroot = Path(tmp)
            include_dir = buildroot / "include"
            include_dir.mkdir(parents=True)
            (include_dir / "version.mk").write_text(
                "VERSION_NUMBER:=$(if $(VERSION_NUMBER),$(VERSION_NUMBER),25.12.2)\n",
                encoding="utf-8",
            )

            output = self.run_script(buildroot, "v1.0.0")

            self.assertIn("UPSTREAM_BASE_VERSION=25.12.2", output)
            self.assertIn("EK_VERSION=25.12.2-ek-v1.0.0", output)

    def test_keeps_snapshot_as_upstream_original_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            buildroot = Path(tmp)
            include_dir = buildroot / "include"
            include_dir.mkdir(parents=True)
            (include_dir / "version.mk").write_text(
                "VERSION_NUMBER:=$(if $(VERSION_NUMBER),$(VERSION_NUMBER),SNAPSHOT)\n",
                encoding="utf-8",
            )
            output = self.run_script(buildroot, "nightly")

            self.assertIn("UPSTREAM_BASE_VERSION=SNAPSHOT", output)
            self.assertIn("EK_VERSION=SNAPSHOT-ek-nightly", output)


if __name__ == "__main__":
    unittest.main()
