# Tales of Destiny (PS1, SLPS-01100) — static recompilation on psxrecomp.
#
# The framework is pinned as a submodule at ./psxrecomp. For local development
# against a shared checkout, override it:
#   cmake -S . -B build -DPSXRECOMP_ROOT=/path/to/psxrecomp
#
# REALPATH matters: with a PSXRECOMP_ROOT that keeps a ".." component, Ninja
# sees two distinct paths for the same psxrecomp/generated/OpenBIOS_full.c and
# aborts with "defined as an output multiple times".
if(NOT DEFINED PSXRECOMP_ROOT)
    get_filename_component(PSXRECOMP_ROOT "${CMAKE_CURRENT_SOURCE_DIR}/psxrecomp" REALPATH)
else()
    get_filename_component(PSXRECOMP_ROOT "${PSXRECOMP_ROOT}" REALPATH)
endif()
set(PSXRECOMP_ROOT "${PSXRECOMP_ROOT}" CACHE PATH "Path to the psxrecomp framework")

include("${PSXRECOMP_ROOT}/runtime/runtime.cmake")

psxrecomp_add_game_runtime(psx-runtime
    GEN_MARKER    "generated/SLPS_011.00_dispatch.c"
    GEN_FULL_GLOB "generated/SLPS_011.00_full_*.c"
)
