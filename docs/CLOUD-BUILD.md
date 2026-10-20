# GitHub build handoff

The prepared workflow is `.github/workflows/build-iso.yml`. It has not run.
It uses a GitHub-hosted Ubuntu runner and a privileged Debian 13 build container,
because live-build needs mount/chroot permissions. It does not publish a release.

1. Create a dedicated GitHub repository named `jarvis-os`, initialized with a README.
2. Place the CONTENTS of the extracted `jarvis-os` folder at the repository root.
   Do not upload only the ZIP or put the project inside an extra nested directory.
3. A push of these build files to `main` triggers the build, if Actions is enabled.
   Alternatively, select Actions → Build J.A.R.V.I.S. development ISO → Run workflow.
4. If it succeeds, download the `jarvis-development-iso-UNTESTED` artifact. It contains
   an ISO and checksum; extract the artifact ZIP before using the ISO.
5. Give the build logs and ISO to the tester. Complete VALIDATION.md before installing
   on the Dell or calling this a finished OS. A green build only proves an image was built.

The workflow needs sufficient runner disk space and account Actions/artifact quota.
It expires stored artifacts after seven days. Private repository usage can consume
the account's allowance; it does not configure billing or buy extra capacity.

Repository: https://github.com/218260652/jarvis-os
This workflow is being submitted for its first build. Consult Actions for current status.
