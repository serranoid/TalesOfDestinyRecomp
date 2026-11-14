#!/bin/sh
# Extract the boot EXE (and the disc tree) from your own copy of the disc.
# Usage: tools/prepare.sh "/path/to/Tales of Destiny (Japan).cue"
set -eu
[ $# -eq 1 ] || { echo "usage: $0 <game.cue>" >&2; exit 2; }
here=$(cd "$(dirname "$0")/.." && pwd)
dumpsxiso=${DUMPSXISO:-$(command -v dumpsxiso || true)}
[ -n "$dumpsxiso" ] || { echo "dumpsxiso not found: build it from https://github.com/Lameguy64/mkpsxiso or set DUMPSXISO" >&2; exit 1; }
mkdir -p "$here/disc"
"$dumpsxiso" -q -x "$here/disc" -s "$here/disc/disc.xml" "$1"
ls -l "$here/disc/SLPS_011.00"
