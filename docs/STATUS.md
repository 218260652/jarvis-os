# Development status — 20 October 2026

## Verified in GitHub Actions and a virtual machine

- [ISO build 39376886815](https://github.com/218260652/jarvis-os/actions/runs/39376886815): success; SHA-256 verified during build and after download.
- [Runtime evidence 39377894422](https://github.com/218260652/jarvis-os/actions/runs/39377894422): screenshots visually reviewed.
- Legacy BIOS boot with Core 2 Duo CPU emulation and 2 GB RAM reached Xfce.
- Live user `jarvis` was created and logged in automatically; runtime report shows UID 1000.
- J.A.R.V.I.S. launched automatically and displayed its gold-orb interface.
- Native Google Chrome 155.0.8059.84 opened an about:blank tab.
- Native VLC 3.0.24 opened its player and first-run privacy dialog. Playback was not tested.
- Wine 10 reported its version; this is NOT a Windows application compatibility test.
- Tk 8.6 and the PocketSphinx executable were present. No live audio recognition test was performed.
- 20 core unit tests pass, covering action boundaries, confirmation gates, reports and recogniser output parsing.

## Visual refresh under verification

The first successful desktop boot still used Xfce's stock wallpaper. The old
setup script only updated image properties that already existed. The corrected
script detects connected XRandR outputs and creates their Xfconf properties.
Dark panel label contrast has also been corrected.

[Visual-refresh build 39379054676](https://github.com/218260652/jarvis-os/actions/runs/39379054676)
is running. Its resulting ISO must pass the automatic VM check and image review.

## Build and startup fixes already applied

Debian 13 package names were corrected in PR #2, now merged. `user-setup` was
added to create the live account, and Xfce is selected explicitly for LightDM.
SVG loader support is included. APT retries handle transient downloads. Bash
pipefail prevents logging from concealing a build failure. The live filesystem
uses zstd compression. Superseded builds are cancelled.

## Remaining hardware and release checks

Microphone/audio, internet browsing, video playback, specific Windows programs,
installation/reboot, UEFI boot and physical Dell networking/suspend/performance
are not verified. The optional AI connection needs a user-provided API key and
an available model. It has not been tested against a live account.

This is a development live image, not a certified production OS. Test it from
USB before installing and back up existing files. The live username is `jarvis`
and its default password is `live`; choose your own credentials when installing.
