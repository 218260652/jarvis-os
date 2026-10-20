# Development status — 20 October 2026

## Build evidence

- ISO built successfully: [run 39359354095](https://github.com/218260652/jarvis-os/actions/runs/39359354095).
- SHA-256 verified during build and after artifact download.
- Package manifest includes Google Chrome Stable 155.0.8059.84-1, VLC 3.0.24,
  Wine 10 with wine32:i386, Tk, PocketSphinx and eSpeak NG.
- 20 core tests pass. No API credentials are included.

## Runtime problem found and corrected in source

[VM run 39374733030](https://github.com/218260652/jarvis-os/actions/runs/39374733030)
passed the boot menu and reached LightDM. It did not reach the desktop.
`user-setup` was absent because recommended packages are disabled in the minimal
build. Debian live-config skips account creation without that package.
The source now includes user-setup, keyboard-configuration, live-tools and iproute2,
and explicitly selects Xfce as the LightDM session.

[Corrected build 39375673592](https://github.com/218260652/jarvis-os/actions/runs/39375673592)
is in progress. The boot workflow will capture desktop progress, app versions,
and attempted native Chrome/VLC launches using Core 2 Duo emulation and 2 GB RAM.
A completed screenshot workflow alone is not a pass: inspect its actual images.

## Build reliability fixes

Debian 13 package names were corrected in PR #2, now merged. A later transient
Debian package download failure prompted APT retries. Bash pipefail is enabled
so logging cannot conceal a failed build. Superseded builds are cancelled.

## Remaining release gates

Desktop and J.A.R.V.I.S. startup in the corrected ISO, Chrome/VLC launch, real
microphone and audio, specific Windows applications, installation/reboot, UEFI
boot, and physical Dell networking/suspend/performance remain unverified.
The optional AI connection needs a user-provided API key and an available model.
Do not replace the existing OS before testing the live USB and backing up files.
