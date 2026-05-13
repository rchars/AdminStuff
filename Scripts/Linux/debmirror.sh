#!/usr/bin/env bash
set -euo pipefail

MIRROR="/mnt/Mirror1"

debmirror "$MIRROR" \
  --method=https \
  --host=ftp.debian.org \
  --root=debian \
  --dist=trixie \
  --arch=amd64,i386,arm64,all \
  --section=main,contrib,non-free,non-free-firmware \
  --source \
  --i18n \
  --retry-rsync-packages=10 \
  --timeout=7200 \
  --getcontents \
  --diff=none \
  --rsync-extra=none \
  --timeout=3600 \
  --rsync-batch=500 \
  --nocleanup \
  --ignore-small-errors \
  --progress \
  --verbose \
  --keyring=/usr/share/keyrings/debian-archive-keyring.gpg
