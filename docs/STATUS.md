# Development status — 20 October 2026

## Deliverable

[Development ISO archive, about 2.85 GB](https://github.com/218260652/jarvis-os/actions/runs/39379054676/artifacts/12244642946).
The ZIP contains the bootable ISO and its SHA-256 checksum file. Artifacts are
retained for seven days; source and build workflows remain in this repository.

## Recorded evidence

- [ISO build 39379054676](https://github.com/218260652/jarvis-os/actions/runs/39379054676): success.
- SHA-256 verified during build and again after downloading to the VM runner.
- [Guest readiness test 39382379485](https://github.com/218260652/jarvis-os/actions/runs/39382379485): success.
- [Rendered-output review 39383639180](https://github.com/218260652/jarvis-os/actions/runs/39383639180): success.
- [Actual screenshots](https://github.com/218260652/jarvis-os/tree/vm-evidence-39383639180-1/docs/vm-evidence): visually reviewed.

Legacy BIOS boot with Core 2 Duo CPU emulation and 2 GB RAM reached Xfce.
The live user jarvis was created and logged in automatically (UID 1000).
J.A.R.V.I.S. started automatically. The custom gold-orb wallpaper and application
menu appeared. The clock text is readable on the dark panel.

Guest window inspection and screenshots confirm that J.A.R.V.I.S., native Google
Chrome 155.0.8059.84 and native VLC 3.0.24 open. Chrome showed an about:blank tab;
VLC showed its player and first-run privacy dialog. Media playback and normal
internet browsing were not tested. Wine 10 reported its version; no particular
Windows EXE or MSI has been executed in these tests.

20 core tests passed. The rendered wallpaper's mean RGB channel difference
from the reference render was about 1.21/255; panel text and app-window checks
passed. These are narrow automated checks, not hardware certification.

## Test method and scope

The disposable VM has no writable hard disk attached. A diagnostic helper is
injected through its normal live-user console and installs xdotool solely for
window inspection. The helper and xdotool are not part of the shipped ISO.
The custom wallpaper settings were recorded before the helper retried the
first-run setup script; they already pointed to horizon.svg.

No API key, personal files or signed-in account was supplied. Audio capture,
speech accuracy, physical Dell Wi-Fi/suspend/graphics/performance, UEFI boot,
installation and post-install reboot remain unverified. The optional AI link
still needs a user-provided API key and an available model.

## Fixes included

Debian 13 package names and the offline recogniser integration were corrected.
The live-account setup package and SVG loader are explicitly included.
LightDM selects Xfce. First-run wallpaper properties are created for connected
monitors. Panel label contrast was corrected. APT retries and Bash pipefail
improve build failure handling. The live filesystem uses zstd compression.

This is a development live image. Preview it before considering installation,
and back up existing files. It is not a production-certified operating system.
