import os
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "validate-package-lists.sh"


class ValidatePackageListsTests(unittest.TestCase):
    def test_fails_when_requested_package_is_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            (workspace / "config").mkdir()
            buildroot = workspace / "openwrt"
            buildroot.mkdir()
            package_dir = buildroot / "package" / "demo"
            package_dir.mkdir(parents=True)
            (package_dir / "Makefile").write_text(
                "define Package/luci\nendef\n"
                "define Package/tmux\nendef\n"
                "define Package/luci-app-turboacc\nendef\n",
                encoding="utf-8",
            )
            (workspace / "config" / "builtin-packages.txt").write_text("luci\n", encoding="utf-8")
            (workspace / "config" / "ondemand-packages.txt").write_text("vim-full\n", encoding="utf-8")

            env = os.environ.copy()
            env["REPO_ROOT"] = str(workspace)
            env["BUILDROOT_DIR"] = str(buildroot)
            result = subprocess.run(
                [str(SCRIPT)],
                check=False,
                text=True,
                capture_output=True,
                env=env,
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("vim-full", result.stderr)

    def test_accepts_packages_found_in_makefiles(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            (workspace / "config").mkdir()
            buildroot = workspace / "openwrt"
            feed_index_dir = buildroot / "feeds"
            feed_index_dir.mkdir(parents=True)
            (feed_index_dir / "luci.index").write_text(
                "Package: luci-app-ddns\nVersion: 1\n\n"
                "Package: luci-ssl\nVersion: 1\n\n",
                encoding="utf-8",
            )
            local_pkg = buildroot / "package" / "turboacc"
            local_pkg.mkdir(parents=True)
            (local_pkg / "Makefile").write_text(
                "define Package/luci-app-turboacc\nendef\n"
                "define Package/tmux\nendef\n",
                encoding="utf-8",
            )
            (workspace / "config" / "builtin-packages.txt").write_text(
                "luci-ssl\nluci-app-turboacc\n",
                encoding="utf-8",
            )
            (workspace / "config" / "ondemand-packages.txt").write_text(
                "luci-app-ddns\ntmux\n",
                encoding="utf-8",
            )

            env = os.environ.copy()
            env["REPO_ROOT"] = str(workspace)
            env["BUILDROOT_DIR"] = str(buildroot)
            result = subprocess.run(
                [str(SCRIPT)],
                check=False,
                text=True,
                capture_output=True,
                env=env,
            )

            self.assertEqual(result.returncode, 0, result.stderr)

    def test_accepts_nested_local_integration_packages(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            (workspace / "config").mkdir()
            buildroot = workspace / "openwrt"
            (buildroot / "feeds").mkdir(parents=True)
            nested = buildroot / "package" / "turboacc" / "luci-app-turboacc"
            nested.mkdir(parents=True)
            (nested / "Makefile").write_text(
                "PKG_NAME:=luci-app-turboacc\n"
                "define Package/$(PKG_NAME)\nendef\n",
                encoding="utf-8",
            )
            (workspace / "config" / "builtin-packages.txt").write_text(
                "luci-app-turboacc\n",
                encoding="utf-8",
            )
            (workspace / "config" / "ondemand-packages.txt").write_text(
                "",
                encoding="utf-8",
            )

            env = os.environ.copy()
            env["REPO_ROOT"] = str(workspace)
            env["BUILDROOT_DIR"] = str(buildroot)
            result = subprocess.run(
                [str(SCRIPT)],
                check=False,
                text=True,
                capture_output=True,
                env=env,
            )

            self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
