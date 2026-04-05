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
            feeds = buildroot / "scripts" / "feeds"
            feeds.parent.mkdir(parents=True)
            feeds.write_text(
                "#!/usr/bin/env bash\nprintf '%s\\n' luci tmux luci-app-turboacc\n",
                encoding="utf-8",
            )
            feeds.chmod(0o755)
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


if __name__ == "__main__":
    unittest.main()
