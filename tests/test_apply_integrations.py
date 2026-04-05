import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "apply-integrations.sh"


class ApplyIntegrationsTests(unittest.TestCase):
    def test_runs_enabled_integrations_from_config_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            (workspace / "config" / "integrations.d").mkdir(parents=True)
            buildroot = workspace / "buildroot"
            buildroot.mkdir()

            marker_script = workspace / "scripts" / "marker.sh"
            marker_script.parent.mkdir()
            marker_script.write_text(
                "#!/usr/bin/env bash\n"
                "set -euo pipefail\n"
                "printf '%s\\n' \"marker:$INTEGRATION_NAME\" >> \"$BUILDROOT_DIR/result.log\"\n",
                encoding="utf-8",
            )
            marker_script.chmod(0o755)

            (workspace / "config" / "integrations.d" / "demo.conf").write_text(
                "NAME=demo\nENABLED=1\nTYPE=script\nSCRIPT=scripts/marker.sh\n",
                encoding="utf-8",
            )
            (workspace / "config" / "integrations.d" / "disabled.conf").write_text(
                "NAME=disabled\nENABLED=0\nTYPE=script\nSCRIPT=scripts/marker.sh\n",
                encoding="utf-8",
            )

            env = os.environ.copy()
            env["REPO_ROOT"] = str(workspace)
            env["BUILDROOT_DIR"] = str(buildroot)
            subprocess.run(
                [str(SCRIPT)],
                check=True,
                text=True,
                capture_output=True,
                env=env,
            )

            result = (buildroot / "result.log").read_text(encoding="utf-8")
            self.assertIn("marker:demo", result)
            self.assertNotIn("disabled", result)


if __name__ == "__main__":
    unittest.main()
