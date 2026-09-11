# Zoe's Deck Theme — handoff for Claude

Read this first, then `docs/RESEARCH.md` for the detailed findings.

## Goal

A comprehensive **CSS Loader** (Decky plugin) theme for the Steam Deck's Gaming Mode. The bar: the Deck
should feel so clean it could be an Apple product. Reference: Apple tvOS + Liquid Glass.

**Must have**
- Fonts: **Instrument Serif** for main accent titles only; **Oxygen** everywhere else, with **Oxygen Bold**
  creating hierarchy.
- Rounded corners, and a CSS "liquid glass" look — **glass on UI elements only** (bars, menus, dialogs,
  buttons, focus), never on content like game art.
- A cleaned-up homescreen design and layout.

**Nice to have:** simple animations.

## Status (2026-09-10)

- Research done (see `docs/RESEARCH.md`). No theme code written yet.
- Zoe has **turned off all other installed themes** for a clean start, so nothing else is styling the UI.
- Theme folder not created yet. Zoe hasn't picked an accent color; default to tvOS-style white-on-dark
  unless told otherwise.

## Environment

- Everything runs on the Deck: user `deck`, hostname `steamdeck`, CSS Loader 2.1.2 at
  `~/homebrew/plugins/SDH-CssLoader`, themes at `~/homebrew/themes/`.
- This repo lives at `~/Documents/Zoe's Deck Theme` on the Deck (quote the path — it has an apostrophe
  and spaces). GitHub: https://github.com/zoeallgaier/ZoesDeckTheme
- Git pushes over SSH with a repo-only deploy key, `~/.ssh/zoesdecktheme_github` (set via
  `git config core.sshCommand` in this repo). There's no `gh` CLI on the Deck.
- The VS Code on the Deck is a Flatpak sandbox (no `systemctl`, no `sudo`); SSH sessions get the real host.
- CSS Loader live reload is on (`watch:1` in `~/homebrew/themes/STORE`), so saved CSS applies within seconds.
- **Gaming Mode must be running** to see or inspect the theme. Zoe works from a Mac over SSH while the Deck
  sits in Gaming Mode.
- The Steam UI debugger listens on `127.0.0.1:8080` on the Deck. In Desktop Mode only desktop Steam
  windows show up; the Gaming Mode tabs (`SP`, `QuickAccess_*`, `MainMenu_*`) appear only in Gaming Mode.

## Tools

`tools/cef.py` (Python stdlib only, run on the Deck):

```sh
python3 tools/cef.py tabs                               # which UI windows exist right now
python3 tools/cef.py tree SP '.gamepadui_BasicHome' 5   # DOM outline, readable class names
python3 tools/cef.py find SP basicgamecarousel_BasicGameCarousel_3MdH5
python3 tools/cef.py eval SP 'document.fonts.check("16px Oxygen")'
python3 tools/cef.py shot SP /tmp/home.png              # then Read the PNG to see it
```

Tested in Desktop Mode: `tabs`, `tree`, `find` and `eval` work. `shot` needs a visible window, so it
hasn't been tested against Gaming Mode yet. Hidden windows can't be captured and the script says so.

## Planned repo layout

The theme itself goes in `theme/`, symlinked into CSS Loader's themes folder so edits here go live:

```sh
ln -s "$HOME/Documents/Zoe's Deck Theme/theme" ~/homebrew/themes/ZoesDeckTheme
```

CSS Loader discovers themes with `listdir` + `isdir`, which follow symlinks, and `/themes_custom/` is already a
symlink to `~/homebrew/themes`, so bundled fonts should resolve. **Not verified yet**; if fonts 404, copy
instead of symlinking.

```
theme/
  theme.json            manifest_version 9; options as patches
  fonts/                Oxygen 300/400/700, Instrument Serif Regular/Italic, OFL.txt
  shared/tokens.css     --zdt-* colors, radii, glass recipe, @font-face (all windows)
  shared/type.css
  sp/home.css  sp/chrome.css  sp/library.css  sp/gamepage.css  sp/dialogs.css
  qam/qam.css  menu/mainmenu.css
  options/*.css         reduce transparency, reduce motion, etc.
```

Font files are already on the Deck at `~/homebrew/themes/Fonts/fonts/` (Oxygen-Light/Regular/Bold,
InstrumentSerif-Regular/Italic). Copy them into `theme/fonts/` with the OFL licence.

## Rules that matter (details in RESEARCH.md)

1. **Class names:** Steam ships scrambled classes (`_3rsrz7BYWjqGBhzcpn-Auo`). Write the readable form
   `module_Name_hash` (e.g. `backgroundglass_BackgroundGlass_3rsrz`); CSS Loader converts it at load time.
   Only exact known names get converted: `[class*="gamepadui_BasicHome"]` works, but a true partial like
   **`[class*="gamepadhome_"]` silently matches nothing**.
2. **Fonts:** all Steam text uses `"Motiva Sans"`. Plan: redefine that family's `@font-face` to the Oxygen
   files so every weight maps through and Steam's own bold survives. Avoid `* { font-family … !important }`
   and never force one weight globally (Zoe's old preset forced 300, which killed all bold).
   Instrument Serif has no bold, so serif titles get hierarchy from size. **Verify the Motiva override works
   in Gaming Mode before building on it.**
3. **Glass:** `backdrop-filter` only blurs content in the *same window*. It works over art in `SP`. The Quick
   Access and Steam menus are separate windows, so there it will look tinted rather than frosted. Steam has
   its own `backgroundglass_*` component that may give real blur there. Investigate, don't assume.
   Keep blurred elements few (GPU cost) and offer a "Reduce Transparency" option.
4. **Apple's rule:** Liquid Glass belongs to the controls and navigation layer only, never the content layer.
   tvOS-style focus = a slight size increase, soft shadow and sheen instead of a glowing border.
5. **Hiding elements:** add the `REQUIRE_NAV_PATCH` flag when using `display: none` on anything focusable,
   or controller navigation breaks.
6. **Publishing on DeckThemes:** prefix CSS variables (`--zdt-`), avoid `*` and `!important` unless necessary,
   stay under 10MB, no bundled third-party themes (use `dependencies`).
7. The Deck screen is 1280×800 at arm's length, not a TV — scale tvOS sizes down.

## Suggested next steps

1. Create `theme/` with `theme.json` + `shared/tokens.css`, symlink it in, and confirm it shows up in CSS
   Loader's list.
2. Font swap first (smallest, most visible win). Verify with `cef.py eval SP` that Oxygen loaded and
   bold weights still render.
3. Radii + glass tokens → header/footer → QAM → Steam menu → dialogs.
4. Homescreen layout pass, then focus effects and animations.
5. Screenshot each step with `cef.py shot SP` so Zoe can review from the Mac.
