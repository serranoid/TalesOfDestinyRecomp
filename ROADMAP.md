# Roadmap

Where this project is going, in the order it will be attempted. Each goal has a
"done when" that can be checked; nothing here is finished until that check passes on
a real run. Status today: boots, plays the opening scene and reaches the first room where the
player has control.

The four goals that define the project:

1. **Runs as well as possible on Linux**
2. **Ultrawide (21:9) support**
3. **Mods**
4. **Spanish translation**

They all sit on top of a baseline that does not exist yet, so that comes first.

## 0. Baseline: the original game, unmodified, playable

Enhancements on top of a game that cannot be played are not measurable.

- [x] Boot, title, main menu, name entry
- [x] Opening scene, first room with player control
- [ ] First battle
- [ ] Save to memory card and load it back
- [ ] Audio (voice and music) verified, not assumed
- [ ] Full-motion video
- [ ] The two minigame overlays
- [ ] A replay that drives the game from boot through each milestone and fails when
      one regresses
- [ ] Measured share of guest code that runs recompiled, per replay

**Done when** the replay reaches the first save point and loads it back, with zero
interpreter fallback reported or with the fallback addresses listed.

## 1. Linux, first class

Only a headless software-renderer run has been measured so far.

- [ ] Windowed run on the hardware renderers (OpenGL, Vulkan), X11 and Wayland
- [ ] Gamepad through SDL3, with rebinding
- [ ] Audio output without crackle at full speed
- [ ] The launcher UI (`PSX_RECOMP_UI=ON`), currently off
- [ ] Steam Deck: runs at full speed, controls mapped
- [ ] A packaged build that needs only the player's disc
- [ ] Other hosts are welcome from contributors, but Linux is the one kept working

**Done when** a clean machine goes from the packaged build plus a disc to the first
save point with a controller, at a steady 60 fps.

## 2. Mods

The framework already defines a mod package (`.psxmod`): guarded patches, disc data
overlays and plugins, applied in memory against the player's own disc.

- [ ] Confirm this game's build loads a `.psxmod` at all
- [ ] One small example mod, documented end to end
- [ ] A map of the game's data formats sufficient to write mods against (kept as
      documentation and tools, never as extracted data)

**Done when** someone outside the project installs the example mod from the
documentation alone.

## 3. Ultrawide

The framework has a native-wide renderer, but each game has to tell it what can be
widened. This is a 2D game: the scene is only as wide as the tiles and backdrops the
game chooses to draw, so widening is per scene type, not a single switch.

- [ ] 16:9 first, then 21:9
- [ ] Battles
- [ ] Towns and dungeons (tile maps)
- [ ] World map
- [ ] Menus, dialogue boxes and HUD anchored correctly; full-screen art stays 4:3
- [ ] 4:3 remains bit-identical to the baseline

**Done when** each scene type above has a 21:9 screenshot with no black bars inside
the playfield, no missing tiles at the edges and no sprites popping at the old
4:3 border.

Expected to be the hardest goal of the four. That is an estimate, not a measurement.

## 4. Spanish translation

Delivered as a mod, so it depends on goal 2.

- [ ] Find how the game stores text and its font
- [ ] A font with `á é í ó ú ü ñ ¿ ¡`
- [ ] Tools to extract and reinsert text from the player's own disc
- [ ] Menus and system text
- [ ] Story script
- [ ] Decide how translated text is distributed without shipping game data

**Done when** the opening hour is playable in Spanish with no overflowing text boxes.

The project moved from the Japanese release to the North American one for this goal:
the translation starts from English text and an engine that already draws Latin
letters. Whether that engine can draw the accented characters as it is, is unknown
until the first item above is done.

## How to help

Pick an unchecked item, open an issue saying so, and read
[CONTRIBUTING.md](CONTRIBUTING.md). Goal 0 is where help moves everything else.
