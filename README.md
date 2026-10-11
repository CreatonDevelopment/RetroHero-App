# RetroHero

Download the build that matches your **device**, **firmware**, and **architecture**. The table updates automatically after every published release.

## Download

<!-- downloads:start -->
[Latest release](https://github.com/CreatonDevelopment/RetroHero-App/releases/latest)
<!-- downloads:end -->

### Choose your architecture

Use **ARM64** on a 64-bit kernel. Use **ARMv7** on a 32-bit kernel; ARMv7 also works on 64-bit kernels that support 32-bit ARM applications.

If you have terminal or SSH access, run `uname -m`:

| Result | Download |
|---|---|
| `aarch64` | ARM64 |
| `armv7l` or `armv8l` | ARMv7 |

A 32-bit userspace on a 64-bit kernel can still run the ARM64 build. Check the firmware you actually installed: Stock OS, NextUI, and NX Redux have separate packages.

## Install

1. Download the ZIP from the matching row and architecture column above.
2. Extract it at the **SD card root**, preserving the folders in the archive.
3. Open RetroHero from your firmware's menu:

| Firmware | Installed folder | Open from |
|---|---|---|
| muOS | `application/RetroHero Slint/` | Applications > RetroHero Slint |
| Stock OS | `Apps/RetroHero/` | Apps > RetroHero |
| NextUI | `Tools/tg5040/RetroHero.pak/` | Tools > RetroHero |
| NX Redux | `Tools/tg5040/RetroHero.pak/` | Tools > RetroHero |

For a manual update, exit RetroHero, then extract the new matching ZIP over the existing installation. Keep your app data, download caches, ROMs, and saves.

## Updates

RetroHero automatically checks for stable updates and shows an animated dialog with **Update**, **Skip for now**, and **Skip this version**. Skipped versions stay skipped across restarts.

Use **Settings > System** to check manually or disable automatic checks. A manual check includes versions you previously skipped. The updater selects your device, firmware, and architecture, verifies the download, preserves user data, backs up the previous app files, and restarts through the launcher.

## Compatibility

Hardware validation currently covers **Anbernic RG40XXV / muOS / ARM64** and **TrimUI Brick Hammer / NX Redux / ARM64**. The other combinations are packaged and tested in CI; physical device validation is still pending.

## Build and release

Maintainers can open [Actions > Release handhelds](https://github.com/CreatonDevelopment/RetroHero-App/actions/workflows/release.yml), select **Run workflow**, and choose **patch**, **minor**, or **major**. Disable **Publish the completed release** to verify builds without publishing.

Four parallel, cached backend and architecture builds produce the 20 device and firmware packages. ARM64 builds run on native ARM64 runners; ARMv7 builds use a cross-compiler, with QEMU used for smoke tests. Tests, update checks, package validation, and checksums gate publication. After publication, CI refreshes the download table above from the release manifest.

The [source repository](https://github.com/CreatonDevelopment/RetroHero) is private. This public repository hosts the release workflow and downloadable builds.
