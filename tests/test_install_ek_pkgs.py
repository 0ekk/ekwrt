import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "files" / "bin" / "install-ek-pkgs"


class InstallEkPkgsTests(unittest.TestCase):
    def test_dry_run_defaults_to_full_package_set(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "etc").mkdir()
            (root / "etc" / "ekwrt-release").write_text(
                "GITHUB_REPOSITORY=owner/repo\nRELEASE_TAG=manual-v1\n",
                encoding="utf-8",
            )
            (root / "etc" / "openwrt_release").write_text(
                "DISTRIB_ARCH='x86_64'\n",
                encoding="utf-8",
            )
            (root / "etc" / "ondemand-packages.txt").write_text(
                "tmux\nvim-full\n",
                encoding="utf-8",
            )

            env = os.environ.copy()
            env["EKWRT_ROOT"] = str(root)
            result = subprocess.run(
                [str(SCRIPT), "--dry-run"],
                check=True,
                text=True,
                capture_output=True,
                env=env,
            )

            self.assertIn("tmux", result.stdout)
            self.assertIn("vim-full", result.stdout)
            self.assertIn("manual-v1", result.stdout)

    def test_self_test_finds_nested_opkg_repositories(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            nested = root / "kmods" / "6.6.1-1"
            nested.mkdir(parents=True)
            (nested / "Packages.gz").write_text("index", encoding="utf-8")
            result = subprocess.run(
                [str(SCRIPT), "--self-test-find-opkg-repos", str(root)],
                check=True,
                text=True,
                capture_output=True,
            )
            self.assertIn(str(nested), result.stdout)


if __name__ == "__main__":
    unittest.main()
