# Current status

Version: 0.1 development source, 20 October 2026.

## Foundation

Debian 13 (trixie) with a trimmed Xfce desktop stays the base. antiX would use less RAM, but it would throw away the live-build recipe, GitHub Actions path and package set already in this repository. MX Linux is also Debian-based and is not lighter than this trimmed Xfce image. The Dell Latitude E6400 is a BIOS, x86-64 machine with 2 GB RAM, so the image keeps syslinux BIOS boot, disables compositing, and uses zram. This choice is not a measured performance result.

## Build failure that was reproduced

GitHub Actions run 39357044465 on main failed in about one minute, before any ISO existed. The chroot package install stopped with:

- `E: Package 'policykit-1' has no installation candidate` (Debian 13 ships `polkitd` and `pkexec` instead)
- `E: Unable to locate package python3-pocketsphinx` (the Python binding is not in trixie; the `pocketsphinx` command and `pocketsphinx-en-us` model are)

Those two names were checked against the trixie amd64 and i386 package indexes. The replacement names in `config/package-lists/desktop.list.chroot` are present. Offline recognition now calls `pocketsphinx_continuous` instead of the missing Python module. `build.sh` marks live-build hooks executable before copying them.

## Not completed

No ISO has been produced or booted yet. Do not install this on the laptop until a GitHub Actions artifact exists, its checksum is verified, and a virtual machine has been booted. Chrome, VLC, Wine and voice capture remain untested at runtime. Wine is not a promise that every Windows program works.

Unit tests cover command boundaries, confirmation gates, status reports and PocketSphinx output parsing. They do not prove the ISO boots.
