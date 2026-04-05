import os
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "generate-config.sh"


class GenerateConfigTests(unittest.TestCase):
    def test_writes_expected_x86_64_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            config_dir = workspace / "config"
            config_dir.mkdir()
            (config_dir / "release.conf").write_text(
                textwrap.dedent(
                    """\
                    TARGET_BOARD=x86
                    TARGET_SUBTARGET=64
                    ROOTFS_PARTSIZE=300
                    TURBOACC_MODE=sfe
                    """
                ),
                encoding="utf-8",
            )
            (config_dir / "builtin-packages.txt").write_text(
                "luci\nluci-ssl\n",
                encoding="utf-8",
            )
            (config_dir / "ondemand-packages.txt").write_text(
                "tmux\nvim-full\n",
                encoding="utf-8",
            )
            output_path = workspace / ".config"

            env = os.environ.copy()
            env["REPO_ROOT"] = str(workspace)
            env["OUTPUT_CONFIG"] = str(output_path)
            env["EK_VERSION"] = "25.12.2-ek-v1.0.0"
            subprocess.run(
                [str(SCRIPT)],
                check=True,
                capture_output=True,
                text=True,
                env=env,
            )

            content = output_path.read_text(encoding="utf-8")
            self.assertIn("CONFIG_TARGET_x86=y", content)
            self.assertIn("CONFIG_TARGET_x86_64=y", content)
            self.assertIn("CONFIG_TARGET_ROOTFS_PARTSIZE=300", content)
            self.assertIn('CONFIG_VERSION_NUMBER="25.12.2-ek-v1.0.0"', content)
            self.assertIn("CONFIG_PACKAGE_luci=y", content)
            self.assertIn("CONFIG_PACKAGE_luci-app-turboacc=y", content)
            self.assertIn("# CONFIG_VDI_IMAGES is not set", content)


if __name__ == "__main__":
    unittest.main()
