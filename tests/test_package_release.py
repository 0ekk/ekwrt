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

            (package_dir / "packages.adb").write_text("index", encoding="utf-8")
            (package_dir / "demo.apk").write_text("pkg", encoding="utf-8")
            (kmods_dir / "kmod-demo.apk").write_text("kmod", encoding="utf-8")

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

            listing = subprocess.run(
                ["tar", "--zstd", "-tf", str(dist / "apks.tar.zst")],
                check=True,
                text=True,
                capture_output=True,
            ).stdout
            self.assertIn("packages/demo.apk", listing)
            self.assertIn("kmods/kmod-demo.apk", listing)

    def test_succeeds_without_kmods_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            target_dir = workspace / "bin" / "targets" / "x86" / "64"
            package_dir = target_dir / "packages"
            package_dir.mkdir(parents=True)

            for name in ("config.buildinfo", "feeds.buildinfo", "version.buildinfo"):
                (target_dir / name).write_text(name, encoding="utf-8")
            (package_dir / "packages.adb").write_text("index", encoding="utf-8")
            (package_dir / "demo.apk").write_text("pkg", encoding="utf-8")

            env = os.environ.copy()
            env["TARGET_DIR"] = str(target_dir)
            env["DIST_DIR"] = str(workspace / "dist")
            subprocess.run(
                [str(SCRIPT)],
                check=True,
                text=True,
                capture_output=True,
                env=env,
            )

            listing = subprocess.run(
                ["tar", "--zstd", "-tf", str(workspace / "dist" / "apks.tar.zst")],
                check=True,
                text=True,
                capture_output=True,
            ).stdout
            self.assertIn("packages/demo.apk", listing)
            self.assertNotIn("kmods/", listing)

    def test_falls_back_to_bin_buildinfo_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            bin_dir = workspace / "bin"
            target_dir = bin_dir / "targets" / "x86" / "64"
            package_dir = target_dir / "packages"
            package_dir.mkdir(parents=True)
            (package_dir / "packages.adb").write_text("index", encoding="utf-8")
            (package_dir / "demo.apk").write_text("pkg", encoding="utf-8")

            (bin_dir / "config.buildinfo").write_text("config", encoding="utf-8")
            (bin_dir / "feeds.buildinfo").write_text("feeds", encoding="utf-8")
            (bin_dir / "version.buildinfo").write_text("version", encoding="utf-8")

            env = os.environ.copy()
            env["TARGET_DIR"] = str(target_dir)
            env["DIST_DIR"] = str(workspace / "dist")
            subprocess.run(
                [str(SCRIPT)],
                check=True,
                text=True,
                capture_output=True,
                env=env,
            )

            dist = workspace / "dist"
            self.assertTrue((dist / "config.buildinfo").exists())
            self.assertTrue((dist / "feeds.buildinfo").exists())
            self.assertTrue((dist / "version.buildinfo").exists())

    def test_fails_when_turboacc_package_artifact_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            target_dir = workspace / "bin" / "targets" / "x86" / "64"
            package_dir = target_dir / "packages"
            package_dir.mkdir(parents=True)

            for name in ("config.buildinfo", "feeds.buildinfo", "version.buildinfo"):
                (target_dir / name).write_text(name, encoding="utf-8")
            (package_dir / "packages.adb").write_text("index", encoding="utf-8")

            turboacc_dir = workspace / "package" / "turboacc"
            turboacc_dir.mkdir(parents=True)
            (turboacc_dir / "Makefile").write_text(
                "define Package/luci-app-turboacc\nendef\n",
                encoding="utf-8",
            )
            (workspace / ".config").write_text("CONFIG_PACKAGE_luci-app-turboacc=y\n", encoding="utf-8")

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
            self.assertIn("Missing turboacc package artifacts", result.stderr)

    def test_ignores_unselected_turboacc_package(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            target_dir = workspace / "bin" / "targets" / "x86" / "64"
            package_dir = target_dir / "packages"
            package_dir.mkdir(parents=True)

            for name in ("config.buildinfo", "feeds.buildinfo", "version.buildinfo"):
                (target_dir / name).write_text(name, encoding="utf-8")
            (package_dir / "packages.adb").write_text("index", encoding="utf-8")
            (package_dir / "demo.apk").write_text("pkg", encoding="utf-8")

            turboacc_dir = workspace / "package" / "turboacc"
            turboacc_dir.mkdir(parents=True)
            (turboacc_dir / "Makefile").write_text(
                "define Package/fast-classifier-example\nendef\n",
                encoding="utf-8",
            )
            (workspace / ".config").write_text("# CONFIG_PACKAGE_fast-classifier-example is not set\n", encoding="utf-8")

            env = os.environ.copy()
            env["TARGET_DIR"] = str(target_dir)
            env["DIST_DIR"] = str(workspace / "dist")
            subprocess.run(
                [str(SCRIPT)],
                check=True,
                text=True,
                capture_output=True,
                env=env,
            )

    def test_accepts_selected_turboacc_package_from_bin_packages(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            target_dir = workspace / "bin" / "targets" / "x86" / "64"
            package_dir = target_dir / "packages"
            package_dir.mkdir(parents=True)

            for name in ("config.buildinfo", "feeds.buildinfo", "version.buildinfo"):
                (target_dir / name).write_text(name, encoding="utf-8")
            (package_dir / "packages.adb").write_text("index", encoding="utf-8")
            (package_dir / "demo.apk").write_text("pkg", encoding="utf-8")

            turboacc_dir = workspace / "package" / "turboacc"
            turboacc_dir.mkdir(parents=True)
            (turboacc_dir / "Makefile").write_text(
                "define Package/luci-app-turboacc\nendef\n",
                encoding="utf-8",
            )
            (workspace / ".config").write_text("CONFIG_PACKAGE_luci-app-turboacc=m\n", encoding="utf-8")

            feed_repo = workspace / "bin" / "packages" / "x86_64" / "turboacc"
            feed_repo.mkdir(parents=True)
            (feed_repo / "packages.adb").write_text("index", encoding="utf-8")
            (feed_repo / "luci-app-turboacc-1-r1.apk").write_text("pkg", encoding="utf-8")

            env = os.environ.copy()
            env["TARGET_DIR"] = str(target_dir)
            env["DIST_DIR"] = str(workspace / "dist")
            subprocess.run(
                [str(SCRIPT)],
                check=True,
                text=True,
                capture_output=True,
                env=env,
            )

            listing = subprocess.run(
                ["tar", "--zstd", "-tf", str(workspace / "dist" / "apks.tar.zst")],
                check=True,
                text=True,
                capture_output=True,
            ).stdout
            self.assertIn("packages/feeds/x86_64/turboacc/luci-app-turboacc-1-r1.apk", listing)


if __name__ == "__main__":
    unittest.main()
