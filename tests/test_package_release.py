import json
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
                "openwrt-25.12.2-ek-v1-x86-64-generic-ext4-combined-efi.img.gz": "img",
                "openwrt-25.12.2-ek-v1-x86-64-generic-kernel.bin": "kernel",
                "openwrt-25.12.2-ek-v1-x86-64-rootfs.tar.gz": "rootfs",
                "openwrt-25.12.2-ek-v1-x86-64.manifest": "manifest",
                "config.buildinfo": "config",
                "feeds.buildinfo": "feeds",
                "version.buildinfo": "version",
                "profiles.json": "{}",
            }
            drop = {
                "openwrt-25.12.2-ek-v1-x86-64-generic-squashfs-combined-efi.img.gz": "drop",
            }

            for name, value in {**keep, **drop}.items():
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
            self.assertTrue((dist / "packages.tar.zst").exists())
            self.assertTrue((dist / "kmods.tar.zst").exists())
            self.assertTrue((dist / "index.html").exists())
            self.assertFalse(
                (dist / "openwrt-25.12.2-ek-v1-x86-64-generic-squashfs-combined-efi.img.gz").exists()
            )

            metadata = json.loads((dist / "release-metadata.json").read_text(encoding="utf-8"))
            image_names = {item["name"] for item in metadata["image_files"]}
            self.assertEqual(
                image_names,
                {
                    "openwrt-25.12.2-ek-v1-x86-64-generic-ext4-combined-efi.img.gz",
                    "openwrt-25.12.2-ek-v1-x86-64-generic-kernel.bin",
                    "openwrt-25.12.2-ek-v1-x86-64-rootfs.tar.gz",
                },
            )


if __name__ == "__main__":
    unittest.main()
