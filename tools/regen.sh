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
"$bin/psxrecomp-toml" "disc/SLPS_011.00" --output game.toml --seeds seeds.txt \
  --name "Tales of Destiny (Japan)" --id SLPS-01100
"$bin/psxrecomp-game" --config game.toml
