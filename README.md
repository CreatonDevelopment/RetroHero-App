# RetroHero App

[Download releases](https://github.com/CreatonDevelopment/RetroHero-App/releases).
[Source code](https://github.com/CreatonDevelopment/RetroHero).

To build and publish, open [Actions > Release handhelds](https://github.com/CreatonDevelopment/RetroHero-App/actions/workflows/release.yml),
select **Run workflow**, then choose **patch**, **minor**, or **major**.
Disable **Publish the completed release** to verify builds without publishing.

| Device | Firmware | Architectures |
|---|---|---|
| Anbernic RG40XXV | muOS | ARM64, ARMv7 |
| TrimUI Brick / Brick Pro / Brick Hammer | Stock, NextUI, NX Redux | ARM64, ARMv7 |

Extract the matching ZIP at the SD card root. Packages include the appropriate
Apps/Tools/application layout and device launcher. Each release contains checksums
and a manifest linking every binary to its source commit. Preserve existing app
data, download caches, ROMs, and saves when updating.

ARMv7 requires firmware kernel support for 32-bit ARM applications. ARM64 is
preferred on 64-bit kernels; the statically linked musl binaries also work with
32-bit userspace on those kernels. Hardware validation currently covers
RG40XXV/muOS and Brick Hammer/NX Redux ARM64. New combinations await hardware
validation.

Builds are manual only. Four parallel, cached backend/architecture builds create
20 device/firmware ZIPs, reusing identical binaries. Tests, QEMU smoke checks,
ELF/static-link checks, package completeness, and checksums gate publication.

[Build and release documentation](https://github.com/CreatonDevelopment/RetroHero/blob/main/docs/releases.md).
The canonical workflow is maintained in the source repository at
`.github/release/release.yml`; this repository hosts the active workflow and releases.
