# ekwrt

Meta-repository for building and publishing a custom `OpenWrt x86_64` firmware.

## Features

- Select the upstream OpenWrt source with `branch`, `tag`, or `commit` in `config/upstream.conf`
- Build and publish automatically through GitHub Actions on tag push or manual dispatch
- Support in-tree packages from `packages/` and third-party source definitions from `config/sources.d/*.conf`
- Integrate `chenmozhijin/turboacc` through a dedicated workflow, with `sfe` enabled by default
- Use a firmware version format of `<upstream-version>-ek-<release-token>`
- Publish only these release assets:
  - `generic-ext4-combined-efi.img.gz`
  - `generic-kernel.bin`
  - `rootfs.tar.gz`
  - `packages.tar.zst`
  - `kmods.tar.zst`

## Layout

- `config/`: upstream, release, package list, and third-party source settings
- `files/`: rootfs overlay content for the firmware image
- `packages/`: in-tree OpenWrt packages kept in this repository
- `config/integrations.d/`: integration definitions with a shared execution entrypoint
- `scripts/`: helper scripts for checkout, versioning, build preparation, and release packaging
- `tests/`: local script-level tests

## Local verification

```bash
./tests/run_tests.sh
```

## Third-party source definitions

Each file under `config/sources.d/*.conf` uses a simple `KEY=VALUE` format.

`TYPE=git` example:

```ini
NAME=example
TYPE=git
URL=https://github.com/example/openwrt-feed.git
REF=main
SUBDIR=
```

`TYPE=archive` example:

```ini
NAME=example
TYPE=archive
URL=https://example.com/feed.tar.gz
STRIP_COMPONENTS=1
```

`TYPE=script` example:

```ini
NAME=example
TYPE=script
SCRIPT=scripts/fetch-example.sh
```
