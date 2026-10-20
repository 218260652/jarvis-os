# Release gates — all require recorded evidence

Do not mark this as a working OS until the build and runtime checks pass.

1. Build on Debian 13 amd64. Record package versions, build.log and SHA-256.
   Verify the package list and wine32:i386 resolve successfully.
2. Boot ISO under legacy BIOS QEMU and UEFI QEMU. Confirm live login, desktop,
   bottom panel, menu, wallpaper and J.A.R.V.I.S. startup. Record screenshots.
3. On a VM configured with 2 GB RAM, record idle and active memory usage, boot
   time, swap behaviour, responsiveness while using browser + J.A.R.V.I.S. + Wine.
4. Test file manager, browser, calculator, text editor, sound, networking, power
   settings, logout and screen lock. Verify default live-user credentials and
   document them before asking anyone to use screen lock in a live session.
5. Test microphone capture, recogniser model paths, speech output and each
   supported command. Check recognition with the intended user's accent.
   Restart/shutdown must never occur without the confirmation dialog.
6. Test an actual 32-bit EXE, a 64-bit EXE, an MSI, and the user's specifically
   named Windows programs. Record exact versions and failures; no blanket promise.
   Check file association, launch log, first-use Wine setup and missing dependencies.
   Test native Chrome browsing and updates from the signed Google repository.
   Test native VLC with MP4, MP3 and MKV samples; confirm audio/video, file
   associations, and the J.A.R.V.I.S. commands `open chrome` and `open vlc`.
7. Test AI with a user-supplied key: valid/invalid keys, unavailable model,
   quota limit and loss of internet. Check no key appears in logs or child env.
   Verify no request occurs before the explicit Ask AI action.
8. Install into a disposable VM disk using the Debian installer. Reboot without
   the ISO. Verify theme, launchers, permissions and account setup survive.
9. Live-boot the Dell from a spare USB after backing up important files. Test
   Wi-Fi adapter, audio, touchpad, brightness, sleep/wake, battery and external display.
   Do not run the installer on the Dell until the user reviews this evidence.
10. Check security updates, dependency licences and source-distribution obligations
    before distributing an ISO. Keep Debian branding/licences intact.

The build script does not flash USB drives or repartition disks automatically.
