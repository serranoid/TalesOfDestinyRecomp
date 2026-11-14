# Contributing

Help is welcome. This is an early project: the game boots, reaches the main menu and
enters *NEW GAME* up to the name entry screen. Everything after that is open ground.

## The one hard rule: no game data

Nothing that comes from the disc goes into this repository, an issue, a pull request
or a comment. That means:

- no disc images, no files extracted from the disc, no BIOS, no licence sector;
- no `generated/` output (it is the game's code translated to C);
- no memory dumps. `psx_last_run_report.json` contains a `ram_peeks` section with raw
  guest memory: **remove it** before attaching the report anywhere.

Screenshots that show a milestone are fine. You need your own copy of the Japanese
release (`SLPS-01100`); the data track this project is measured against has
`sha1 eb1c41fcb44e5fbc85da7d92f1e2889b69f299f5`. A different dump or region may work,
but say so in your report, because addresses can differ.

## Where help is wanted

The current list lives in `help` in [`.recomp.json`](.recomp.json). Today:

- **Progress past the name entry screen**: opening scene, first map, first battle,
  save and load.
- **Audio**: streamed voice and sequenced music are unverified. The debug server lists
  `audio_stats` and `audio_wav` commands; nobody has used them on this game yet, so a
  first headless audio check would be a contribution in itself.
- **Full-motion video**: unverified.
- **The two minigame overlays**: code loaded from disc at run time, not recompiled yet.
- **Other hosts**: only Linux x86-64 (GCC 16, CMake, Ninja, SDL3 3.4+) has been built
  and run. Reports from other compilers and systems are useful even when they fail.

If you want to take one of these, open an issue first so two people do not do the
same work.

## How a change is verified

"It compiles" is not a result here. A claim is accepted when something that could
have said no says yes:

1. Build and run headless as in the [README](README.md#build).
2. Drive the game through the debug server (`press`) and wait for a screen by
   comparing screenshots, not by sleeping a fixed time. Fixed delays land in the wrong
   place from one run to the next.
3. Attach the evidence: the screenshot, the frame number from `get_registers`, and
   the exact inputs (mask and frame count) that got there.

`tools/replay.py` does exactly this from boot to the name entry screen and exits
non-zero when a step stops matching (it needs Python 3 with Pillow). Run it before and
after your change; when you reach a new screen, add a step and its reference
screenshot:

```sh
python3 tools/replay.py --disc "/path/to/Tales of Destiny (Japan).cue"
```

`buttons` is the raw active-low pad word: `Start` = `0xFFF7`, `○` (confirm) = `0xDFFF`,
`×` (cancel) = `0xBFFF`, `Up` = `0xFFEF`, `Right` = `0xFFDF`, `Down` = `0xFFBF`,
`Left` = `0xFF7F`. The server closes the connection after each reply, so open one per
request.

Numbers in the README are measurements. If you change one, say how you measured it
and on what machine.

## Reporting a problem

Include:

- your disc's data-track `sha1`, host system and compiler;
- the framework commit (`git -C psxrecomp rev-parse HEAD`);
- the inputs that reproduce it, the last screenshot, and the last lines of the
  runtime log;
- `psx_last_run_report.json` **without** `ram_peeks`.

## What belongs here and what belongs upstream

This repository holds the game's configuration (`game.toml`, `seeds.txt`), the build
glue and the tooling. Bugs in the recompiler or the runtime belong in
[psxrecomp](https://github.com/RetroPortingToolKit/psxrecomp); link the upstream issue
here if it blocks the game.

## Pull requests

- One change per pull request, with the evidence above in the description.
- Do not commit `build/`, `generated/` or anything under `disc/`; `.gitignore` covers
  them, please do not force them in.
- New seeds: say where each address came from (a run-time log, a disassembly), not
  just the list.
- Contributions are accepted under the repository's MIT licence.
