#!/bin/sh
# Regenerate generated/ from the boot EXE staged by tools/prepare.sh.
set -eu
here=$(cd "$(dirname "$0")/.." && pwd)
root=${PSXRECOMP_ROOT:-$here/psxrecomp}
[ -x "$root/recompiler/build-cli/psxrecomp-game" ] || \
  [ -x "$root/recompiler/build/psxrecomp-game" ] || {
    echo "build the recompiler first: cmake -S $root/recompiler -B $root/recompiler/build -G Ninja -DCMAKE_BUILD_TYPE=Release && cmake --build $root/recompiler/build" >&2; exit 1; }
bin=$( [ -x "$root/recompiler/build-cli/psxrecomp-game" ] && echo "$root/recompiler/build-cli" || echo "$root/recompiler/build" )
cd "$here"
# game.toml and seeds.txt are committed and hand-maintained: psxrecomp-toml would
# rewrite both from scratch and drop every seed added since.
"$bin/psxrecomp-game" --config game.toml
