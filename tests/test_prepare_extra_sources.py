import os
import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "prepare-extra-sources.sh"


class PrepareExtraSourcesTests(unittest.TestCase):
    def test_clones_git_source_and_writes_feeds_entry(self):
        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            (workspace / "config" / "sources.d").mkdir(parents=True)
            (workspace / "work").mkdir()
            source_repo = workspace / "source-repo"
            source_repo.mkdir()
            subprocess.run(["git", "init", "-q", str(source_repo)], check=True)
            subprocess.run(
                ["git", "-C", str(source_repo), "config", "user.email", "test@example.com"],
                check=True,
            )
            subprocess.run(
                ["git", "-C", str(source_repo), "config", "user.name", "Test"],
                check=True,
            )
            subprocess.run(
                ["git", "-C", str(source_repo), "config", "commit.gpgsign", "false"],
                check=True,
            )
            (source_repo / "README").write_text("demo\n", encoding="utf-8")
            subprocess.run(["git", "-C", str(source_repo), "add", "."], check=True)
            subprocess.run(
                ["git", "-C", str(source_repo), "commit", "-qm", "init"],
                check=True,
            )

            (workspace / "config" / "sources.d" / "git-demo.conf").write_text(
                textwrap.dedent(
                    f"""\
                    NAME=demo
                    TYPE=git
                    URL={source_repo}
                    REF=HEAD
                    """
                ),
                encoding="utf-8",
            )

            env = os.environ.copy()
            env["REPO_ROOT"] = str(workspace)
            env["WORK_DIR"] = str(workspace / "work")
            result = subprocess.run(
                [str(SCRIPT)],
                check=True,
                text=True,
                capture_output=True,
                env=env,
            )

            self.assertIn("src-link ek_demo", result.stdout)
            clone_dir = workspace / "work" / "extra-sources" / "demo"
            self.assertTrue((clone_dir / "README").exists())


if __name__ == "__main__":
    unittest.main()
