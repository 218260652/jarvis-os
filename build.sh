#!/bin/bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
if [[ ${EUID} -ne 0 ]]; then
  echo 'Run with sudo on a dedicated Debian 13 amd64 build machine.' >&2
  exit 1
fi
source /etc/os-release
if [[ ${ID:-} != debian || ${VERSION_CODENAME:-} != trixie || $(dpkg --print-architecture) != amd64 ]]; then
  echo 'Use Debian 13 (trixie), amd64, with mount/chroot capabilities.' >&2
  exit 1
fi
for tool in lb debootstrap xorriso mksquashfs; do
  command -v "$tool" >/dev/null || { echo "Missing $tool. Read README.md." >&2; exit 1; }
done
if [[ -e work ]]; then
  echo 'work already exists. Review its build log; use sudo lb build inside work to retry.' >&2
  echo 'For a fresh build, extract the source into a new directory.' >&2
  exit 1
fi
chmod +x config/hooks/normal/*.hook.chroot overlay/usr/local/bin/*
mkdir work
cp -a config work/config
mkdir -p work/config/includes.chroot/opt/jarvis
cp -a overlay/. work/config/includes.chroot/
cp app/*.py work/config/includes.chroot/opt/jarvis/
cd work
lb config --mode debian --distribution trixie --architecture amd64 \
  --binary-image iso-hybrid --bootloaders 'syslinux grub-efi' \
  --chroot-squashfs-compression-type zstd --chroot-squashfs-compression-level 5 \
  --archive-areas 'main contrib non-free non-free-firmware' \
  --apt-recommends false --apt-secure true --apt-options '-y -o Acquire::Retries=5' \
  --mirror-bootstrap https://deb.debian.org/debian/ \
  --mirror-chroot https://deb.debian.org/debian/ \
  --mirror-chroot-security https://security.debian.org/debian-security/ \
  --mirror-binary https://deb.debian.org/debian/ \
  --mirror-binary-security https://security.debian.org/debian-security/ \
  --debian-installer live --debian-installer-gui false \
  --mirror-debian-installer https://deb.debian.org/debian/ \
  --firmware-chroot true --firmware-binary true \
  --uefi-secure-boot disable \
  --bootappend-live 'boot=live components username=jarvis hostname=jarvis-os locales=en_US.UTF-8 keyboard-layouts=us timezone=Africa/Johannesburg' \
  --iso-volume JARVIS_OS_DEV --iso-application 'Jarvis OS Development Preview' \
  --checksums sha256 --image-name jarvis-os-dev
lb build 2>&1 | tee build.log
shopt -s nullglob
images=(*.iso)
[[ ${#images[@]} -eq 1 ]] || { echo 'Expected exactly one ISO; inspect work/.' >&2; exit 1; }
mkdir -p ../dist
cp -- "${images[0]}" ../dist/jarvis-os-dev-amd64.iso
cp -- build.log ../dist/
cd ../dist
sha256sum jarvis-os-dev-amd64.iso > SHA256SUMS
echo 'ISO built. It is NOT release-ready until docs/VALIDATION.md is completed.'
