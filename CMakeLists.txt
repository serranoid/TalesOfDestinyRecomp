cmake_minimum_required(VERSION 3.20)
project(tod-recomp C CXX)

# Tales of Destiny (PS1, SLUS-00626) — static recompilation on psxrecomp.
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
    GEN_MARKER    "generated/SLUS_006.26_dispatch.c"
    GEN_FULL_GLOB "generated/SLUS_006.26_full_*.c"
)
