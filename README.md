# J.A.R.V.I.S. OS — development source, v0.1

**This ZIP is source code, not an ISO and not a finished operating system.**
The source was written and its core unit tests were run in a restricted environment.
The environment does not allow mount/chroot operations or package installation.
No bootable image was built, no VM was booted, and no Dell hardware was tested.
Do not erase Windows based on this package.

## What this project contains

A Debian 13 amd64 live-build recipe with an Xfce desktop, dark/cyan accents,
an original static gold-orb wallpaper, and a native Python/Tk J.A.R.V.I.S. assistant.
The visual design is inspired by the supplied reference, but is not a pixel-perfect
reproduction of the earlier generated screenshots. The desktop uses standard Xfce controls.
Debian provides the kernel, drivers, installer, updates and package manager.

### Requested everyday apps

The build recipe now includes native Linux VLC and Google Chrome Stable,
plus a calculator (Galculator), text editor (Mousepad), PDF reader (Evince),
image viewer (Ristretto), file manager (Thunar) and archive manager (File Roller).
Chrome is installed from Google's signed amd64 repository during the ISO build;
its proprietary binaries are not in this source ZIP. Firefox ESR remains a fallback.
Browser and common audio/video file associations are configured for Chrome and VLC.
J.A.R.V.I.S. recognises `open chrome`, `open browser`, `open vlc` and `open media player`.
On 2 GB RAM, keep browser tabs and simultaneous apps to a minimum; performance
is unmeasured. These applications have not been installed or runtime-tested here.

The recipe includes Wine with 64-bit and 32-bit libraries. The Windows launcher
accepts EXE and MSI files, asks before launch, and writes a diagnostic log.
Wine compatibility must be checked for each specific app and version. Windows
drivers, demanding games, anti-cheat software and every Windows app are not promised.
Wine is not a malware sandbox. This project does not contain Windows.

## J.A.R.V.I.S. capabilities implemented in source

- Gold orbital character; animation is optional and off by default.
- Push-to-talk: click Listen, speak for up to six seconds, wait for recognition.
- Recognised allowlisted desktop commands run locally. Power and lock commands
  require on-screen confirmation. Unknown speech is shown for editing.
- Offline English speech recognition through PocketSphinx and spoken replies through eSpeak NG.
  This is basic speech recognition and a synthetic voice, not a movie-quality voice.
- Optional OpenAI Responses API chat: explicitly press Ask AI to send that message.
  It does not have general computer-control tools and cannot see your screen.
- A session-only key/model dialog. No key is included. No live AI call has been tested.
  Use your own API account and an available model; usage may incur charges.
- No always-on listening, arbitrary shell commands, file deletion, automatic messages,
  wake-word service, browsing agent, or unrestricted control of other apps.

Type `help` for all commands. Examples: `open files`, `open browser`,
`open windows app`, `volume up`, `mute`, `open settings`, `restart computer`.
You can also say `J.A.R.V.I.S., open files`.

## Hardware target and limits

Target: the user's Dell Latitude E6400 with 2 GB RAM and an x86-64 CPU.
RAM usage and performance are **not measured**. Heavy browsing, Wine apps and
speech recognition can still exceed available memory. zram is configured to
reduce memory pressure; it does not add physical RAM. Desktop compositing and
GTK animations are off. No large local language model is included.

The exact Wi-Fi adapter is unknown. Intel/Realtek firmware is included in the
recipe; other adapters may need additional packages after identification.
Ethernet may be needed for first setup. BIOS and UEFI boot are configured;
Secure Boot is not supported by this development recipe.

## Build the ISO on a suitable machine

A cloud build workflow is also prepared. See `docs/CLOUD-BUILD.md` to run it in
a dedicated GitHub repository. It has not been executed or boot-tested.

Use a **dedicated Debian 13 amd64 machine or full VM** with internet and root
mount/chroot capabilities. Allow roughly 30 GB free disk and at least 4 GB RAM
for the build. These are planning allowances, not measured requirements.
Do not use this restricted chat environment or a locked-down container.

1. Extract this ZIP into a new folder on that machine.
2. Install the build tools:

```sh
sudo apt update
sudo apt install live-build debootstrap debian-archive-keyring xorriso squashfs-tools
```

3. Open a terminal in the extracted `jarvis-os` directory and run:

```sh
chmod +x build.sh config/hooks/normal/*.hook.chroot overlay/usr/local/bin/*
sudo ./build.sh
```

4. If successful, outputs are `dist/jarvis-os-dev-amd64.iso`, `dist/SHA256SUMS`
   and `dist/build.log`. No such outputs are included in this source ZIP.
5. Verify the checksum and complete `docs/VALIDATION.md` before treating it as usable.

The build downloads current Debian packages and therefore is not bit-for-bit
reproducible over time. A release must retain its package manifest, build log,
sources/licences as required, checksum and test results.

The script intentionally refuses to overwrite an existing `work` directory.
After fixing a failure, you can retry with `cd work && sudo lb build`, or extract
a fresh source copy. Inspect build errors; do not assume the source recipe has
been dependency-resolved or validated by an actual build.

## Test before touching a physical disk

On the build machine, install QEMU and run a live session without a writable hard disk:

```sh
sudo apt install qemu-system-x86
qemu-system-x86_64 -m 2048 -boot d -cdrom dist/jarvis-os-dev-amd64.iso -nic user
```

This uses software emulation and can be slow; do not use it for performance claims.
For installer testing use a new disposable virtual disk, never a real disk.
The Debian text installer is configured in the boot menu, not a custom installer.
It must be tested to confirm customisation is preserved after installation.
Live sessions are temporary unless persistence is deliberately configured.
Keep API keys and personal work out of shared live sessions.

## Run just J.A.R.V.I.S. on an existing Debian 13 desktop

This does not install an operating system or theme. In the extracted directory:

```sh
sudo apt install python3-tk python3-pocketsphinx pocketsphinx-en-us espeak-ng alsa-utils
python3 app/jarvis.py
```

Desktop actions additionally require the named Xfce apps, PulseAudio tools and
Wine from the package list. `open windows app` expects the installed launcher
under `/usr/local/bin`; during source testing run `python3 app/windows.py` instead.

## Source tests

```sh
python3 -m unittest discover -s tests -v
python3 -m compileall -q app
bash -n build.sh
```

These check command boundaries, confirmation gates, Windows-file arguments,
and the API request/response code using mocks. They do not prove the OS boots,
voice recognises your accent, Windows applications work, or real API access succeeds.

## Sources used for the implementation

- Debian live-build: https://manpages.debian.org/trixie/live-build/lb_config.1.en.html
- Debian Live manual: https://live-team.pages.debian.net/live-manual/
- Wine overview and compatibility database: https://www.winehq.org/about and https://appdb.winehq.org/
- OpenAI text generation: https://developers.openai.com/api/docs/guides/text
- Google Linux repository: https://www.google.com/linuxrepositories/

See `docs/VALIDATION.md` and `docs/STATUS.md` for remaining work.
