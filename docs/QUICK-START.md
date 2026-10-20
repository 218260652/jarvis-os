# Quick start — J.A.R.V.I.S. OS development live image

1. [Download the ISO archive](https://github.com/218260652/jarvis-os/actions/runs/39379054676/artifacts/12244642946) (about 2.85 GB; GitHub sign-in may be required).
2. Extract the ZIP. Use jarvis-os-dev-amd64.iso; do not rename the ZIP to ISO.
   SHA256SUMS contains the checksum for the ISO.
3. Preview it in a VM, or write the ISO with a USB imaging tool to a spare USB.
   Writing an image erases that USB, so copy its files elsewhere first.
4. Boot the image and choose Live system. The live account logs in automatically.
   If a lock/login prompt appears, username: jarvis; password: live.
5. J.A.R.V.I.S. opens with its gold-orb interface. Try local commands such as
   open chrome, open vlc, open files, volume up, or system status.
6. Listen records up to six seconds locally. Microphone and speaker behaviour
   must still be checked on your laptop. Ask AI is optional and needs an API
   account/key/model; it sends the entered message online and may incur charges.

The graphical desktop, J.A.R.V.I.S., Chrome and VLC startup were checked in a
Core 2 Duo / 2 GB RAM VM. This does not prove performance or driver compatibility
on the Dell. Wine is included for Windows-app compatibility, but your specific
EXE/MSI programs still need testing. Native Linux Chrome and VLC are already installed.

The installer and installed-system reboot have not been validated. Use the
Live system preview first and back up your existing files before installation.
A live session is temporary unless persistence or installation is deliberately set up.

The artifact download is retained for seven days. Rebuild with the repository's
Build J.A.R.V.I.S. development ISO workflow when a fresh artifact is needed.
