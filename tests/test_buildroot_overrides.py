import os
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "integrations" / "buildroot-overrides.sh"


class BuildrootOverridesTests(unittest.TestCase):
    def test_replaces_old_fail2ban_makefile_with_repo_override(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            override_path = workspace / "overrides" / "buildroot" / "feeds" / "packages" / "net" / "fail2ban"
            override_path.mkdir(parents=True)
            (override_path / "Makefile").write_text(
                "PKG_RELEASE:=3\nPKG_BUILD_DEPENDS:=python3/host python-setuptools/host\n",
                encoding="utf-8",
            )

            buildroot_pkg = workspace / "buildroot" / "feeds" / "packages" / "net" / "fail2ban"
            buildroot_pkg.mkdir(parents=True)
            (buildroot_pkg / "Makefile").write_text(
                textwrap.dedent(
                    """\
                    PKG_RELEASE:=2
                    DEPENDS:=+python3-email +python3-pkg-resources
                    """
                ),
                encoding="utf-8",
            )

            env = os.environ.copy()
            env["REPO_ROOT"] = str(workspace)
            env["BUILDROOT_DIR"] = str(workspace / "buildroot")
            subprocess.run(["bash", str(SCRIPT)], check=True, env=env, capture_output=True, text=True)

            content = (buildroot_pkg / "Makefile").read_text(encoding="utf-8")
            self.assertIn("PKG_RELEASE:=3", content)
            self.assertNotIn("python3-pkg-resources", content)


if __name__ == "__main__":
    unittest.main()
