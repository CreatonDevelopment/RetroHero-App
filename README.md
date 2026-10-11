# RetroHero

Download the package for your **device** and **firmware**. Each package automatically selects the native executable on your console. The table updates after every published release.

## Download

<!-- downloads:start -->
Latest build: **[v0.2.0](https://github.com/CreatonDevelopment/RetroHero-App/releases/tag/v0.2.0)**.

| Device | Firmware | Download |
|---|---|---|
| Anbernic RG40XXV | muOS | [Install package](https://github.com/CreatonDevelopment/RetroHero-App/releases/download/v0.2.0/retrohero-0.2.0-anbernic-rg40xxv-muos.muxzip) |
| TrimUI Brick | Stock OS | [Download ZIP](https://github.com/CreatonDevelopment/RetroHero-App/releases/download/v0.2.0/retrohero-0.2.0-trimui-brick-trimui-stock-aarch64.zip) |
| TrimUI Brick | NextUI | [Download ZIP](https://github.com/CreatonDevelopment/RetroHero-App/releases/download/v0.2.0/retrohero-0.2.0-trimui-brick-nextui-aarch64.zip) |
| TrimUI Brick | NX Redux | [Download ZIP](https://github.com/CreatonDevelopment/RetroHero-App/releases/download/v0.2.0/retrohero-0.2.0-trimui-brick-nxredux.zip) |
| TrimUI Brick Pro | Stock OS | [Download ZIP](https://github.com/CreatonDevelopment/RetroHero-App/releases/download/v0.2.0/retrohero-0.2.0-trimui-brick-pro-trimui-stock-aarch64.zip) |
| TrimUI Brick Pro | NX Redux | [Download ZIP](https://github.com/CreatonDevelopment/RetroHero-App/releases/download/v0.2.0/retrohero-0.2.0-trimui-brick-pro-nxredux.zip) |
| TrimUI Brick Hammer | Stock OS | [Download ZIP](https://github.com/CreatonDevelopment/RetroHero-App/releases/download/v0.2.0/retrohero-0.2.0-trimui-brick-hammer-trimui-stock-aarch64.zip) |
| TrimUI Brick Hammer | NextUI | [Download ZIP](https://github.com/CreatonDevelopment/RetroHero-App/releases/download/v0.2.0/retrohero-0.2.0-trimui-brick-hammer-nextui-aarch64.zip) |
| TrimUI Brick Hammer | NX Redux | [Download ZIP](https://github.com/CreatonDevelopment/RetroHero-App/releases/download/v0.2.0/retrohero-0.2.0-trimui-brick-hammer-nxredux.zip) |

[SHA-256 checksums](https://github.com/CreatonDevelopment/RetroHero-App/releases/download/v0.2.0/SHA256SUMS) · [Release manifest](https://github.com/CreatonDevelopment/RetroHero-App/releases/download/v0.2.0/release-manifest.json)
<!-- downloads:end -->

## Install

Choose the row matching your device and the firmware you installed: Stock OS, NextUI, and NX Redux use separate packages.

| Firmware | Install | Open from |
|---|---|---|
| muOS | Copy the `.muxzip` into **ARCHIVE** on the SD card, then install it through **Applications > Archive Manager**. | Applications > RetroHero Slint |
| Stock OS | Extract the ZIP at the **SD card root**, creating `Apps/RetroHero/`. | Apps > RetroHero |
| NextUI | Extract the ZIP at the **SD card root**, creating `Tools/tg5040/RetroHero.pak/`. | Tools > RetroHero |
| NX Redux | Extract the ZIP at the **SD card root**, creating `Tools/tg5040/RetroHero.pak/`. | Tools > RetroHero |

For a manual update, exit RetroHero and install the new package using the same steps. Keep your app data, download caches, ROMs, and saves.

## Updates

RetroHero automatically checks for stable updates and shows an animated dialog with **Update**, **Skip for now**, and **Skip this version**. Skipped versions stay skipped across restarts.

Use **Settings > System** to check manually or disable automatic checks. A manual check includes versions you previously skipped. Updates verify the download, preserve user data, back up the previous app files, and restart through the launcher.

**Upgrading from v0.1.1:** install the matching package manually once. Automatic updates then support the new combined package format.

## Compatibility

Hardware validation currently covers **Anbernic RG40XXV / muOS** and **TrimUI Brick Hammer / NX Redux** on their 64-bit kernels. The other combinations are packaged and tested in CI; physical device validation is still pending.

## Build and release

Maintainers can open [Actions > Release handhelds](https://github.com/CreatonDevelopment/RetroHero-App/actions/workflows/release.yml), select **Run workflow**, and choose **patch**, **minor**, or **major**. Disable **Publish the completed release** to verify builds without publishing.

Four parallel, cached builds produce **10 install packages**, one per device and firmware. Tests, update checks, package validation, and checksums gate publication. After publication, CI refreshes the download table above.

This repository hosts the release workflow and downloadable builds.
