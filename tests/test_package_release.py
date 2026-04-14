import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "package-release.sh"


class PackageReleaseTests(unittest.TestCase):
    def test_collects_required_assets_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            target_dir = workspace / "bin" / "targets" / "x86" / "64"
            package_dir = target_dir / "packages"
            kmods_dir = target_dir / "kmods"
            package_dir.mkdir(parents=True)
            kmods_dir.mkdir()

            keep = {
                "config.buildinfo": "config",
                "feeds.buildinfo": "feeds",
                "version.buildinfo": "version",
            }
            for name, value in keep.items():
                (target_dir / name).write_text(value, encoding="utf-8")

            (package_dir / "demo.ipk").write_text("pkg", encoding="utf-8")
            (kmods_dir / "kmod-demo.ipk").write_text("kmod", encoding="utf-8")

            env = os.environ.copy()
            env["TARGET_DIR"] = str(target_dir)
            env["DIST_DIR"] = str(workspace / "dist")
            env["RELEASE_NAME"] = "manual-v1"
            subprocess.run(
                [str(SCRIPT)],
                check=True,
                text=True,
                capture_output=True,
                env=env,
            )

            dist = workspace / "dist"
            self.assertTrue((dist / "apks.tar.zst").exists())
            self.assertTrue((dist / "config.buildinfo").exists())
            self.assertTrue((dist / "feeds.buildinfo").exists())
            self.assertTrue((dist / "version.buildinfo").exists())
            self.assertEqual(
                {path.name for path in dist.iterdir() if path.is_file()},
                {"apks.tar.zst", "config.buildinfo", "feeds.buildinfo", "version.buildinfo"},
            )

    def test_fails_when_kmods_directory_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            target_dir = workspace / "bin" / "targets" / "x86" / "64"
            package_dir = target_dir / "packages"
            package_dir.mkdir(parents=True)

            for name in ("config.buildinfo", "feeds.buildinfo", "version.buildinfo"):
                (target_dir / name).write_text(name, encoding="utf-8")
            (package_dir / "demo.apk").write_text("pkg", encoding="utf-8")

            env = os.environ.copy()
            env["TARGET_DIR"] = str(target_dir)
            env["DIST_DIR"] = str(workspace / "dist")
            result = subprocess.run(
                [str(SCRIPT)],
                check=False,
                text=True,
                capture_output=True,
                env=env,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Missing required directories", result.stderr)


if __name__ == "__main__":
    unittest.main()
