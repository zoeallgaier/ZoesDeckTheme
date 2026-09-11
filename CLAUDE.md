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

- Research done (see `docs/RESEARCH.md`).
- Zoe has **turned off all other installed themes** for a clean start, so nothing else is styling the UI.
- `theme/` exists, is symlinked in and **active** (`theme/config_USER.json`, gitignored). It has
  `theme.json`, `shared/tokens.css` (all `--zdt-*` tokens) and `shared/type.css` (font swap + serif accent
  titles, behind the "Theme fonts" checkbox). Verified in Gaming Mode: the "Motiva Sans" override works
  (Motiva measures identically to Oxygen at 300/400/700, so Steam's bold survives) and the Home
  "Recent Games" label renders in Instrument Serif.
- Zoe hasn't picked an accent color; default to tvOS-style white-on-dark unless told otherwise. The
  Accent color picker (`--zdt-accent`, default `#ffffff`) is already wired up; `--zdt-on-accent` picks
  near-black or white text for whatever accent is chosen (CSS relative colour, supported here).
- Step 3 (glass + radii) first pass done and screenshotted: floating glass top/bottom bars, Quick Access
  and Steam menu as floating glass sheets, shared controls (buttons, toggles, sliders, dropdowns, row
  focus), and Settings (floating sidebar, rounded rows, serif page title). "Reduce transparency" option
  added. Not yet checked: modal dialogs, in-game Quick Access (over a running game), Friends expanded
  mode, the collapsed Steam menu, Library, game pages.

## Environment

- Everything runs on the Deck: user `deck`, hostname `steamdeck`, CSS Loader 2.1.2 at
  `~/homebrew/plugins/SDH-CssLoader`, themes at `~/homebrew/themes/`.
- This repo lives at `~/Documents/Zoe's Deck Theme` on the Deck (quote the path — it has an apostrophe
  and spaces). GitHub: https://github.com/zoeallgaier/ZoesDeckTheme
- Git pushes over SSH with a repo-only deploy key, `~/.ssh/zoesdecktheme_github` (set via
  `git config core.sshCommand` in this repo). There's no `gh` CLI on the Deck.
- The VS Code on the Deck is a Flatpak sandbox (no `systemctl`, no `sudo`); SSH sessions get the real host.
- CSS Loader live reload is on (`watch:1` in `~/homebrew/themes/STORE`), **but its watcher doesn't follow
  the `ZoesDeckTheme` symlink**, so saving files in `theme/` does nothing on its own. Run
  `tools/reload.sh` after edits (or leave `tools/reload.sh --watch` running); it writes a ping file in
  `~/homebrew/themes/` that triggers the reload.
- **Gaming Mode must be running** to see or inspect the theme. Zoe works from a Mac over SSH while the Deck
  sits in Gaming Mode.
- The Steam UI debugger listens on `127.0.0.1:8080` on the Deck. In Desktop Mode only desktop Steam
  windows show up; the Gaming Mode tabs (`Steam Big Picture Mode` a.k.a. `SP`, `QuickAccess_*`,
  `MainMenu_*`) appear only in Gaming Mode. CSS Loader's log is the newest file in
  `~/homebrew/logs/SDH-CssLoader/`.

## Tools

`tools/cef.py` (Python stdlib only, run on the Deck):

```sh
python3 tools/cef.py tabs                               # which UI windows exist right now
python3 tools/cef.py tree SP '.gamepadui_BasicHome' 5   # DOM outline, readable class names
python3 tools/cef.py find SP basicgamecarousel_BasicGameCarousel_3MdH5
python3 tools/cef.py eval SP 'document.fonts.check("16px Oxygen")'
python3 tools/cef.py shot SP /tmp/home.png              # then Read the PNG to see it
```

All commands, `shot` included, work in Gaming Mode. `SP` is an alias for the `Steam Big Picture Mode`
window, matching CSS Loader. Hidden windows can't be captured and the script says so. Screenshots come
out at the display's resolution (3442×1442 when docked), not 1280×800.

`tools/reload.sh [--watch]` triggers CSS Loader's reload (see Environment).

`tools/shot.sh out.png [qam [tab]|menu|close]` takes a **full-screen** screenshot with every window
composited (`gamescopectl screenshot`), optionally opening Quick Access (tab 4 = settings, 999 = Decky)
or the Steam menu first. Use this to review menus; `cef.py shot` only sees one window.

Navigate from a script with Decky's helpers in the shared context, e.g.
`python3 tools/cef.py eval SharedJSContext 'DFL.Navigation.Navigate("/settings/display"), 1'`
(also `OpenQuickAccessMenu(tab)`, `OpenMainMenu()`, `CloseSideMenus()`; go back with
`Navigate("/library/home")`). To preview a focus style without a controller, add the `gpfocus` class
to an element with `eval`, screenshot, then remove it.

## Repo layout

The theme lives in `theme/`, symlinked into CSS Loader's themes folder (already done on this Deck):

```sh
ln -s "$HOME/Documents/Zoe's Deck Theme/theme" ~/homebrew/themes/ZoesDeckTheme
```

Verified: CSS Loader finds the theme through the symlink, and Steam serves the bundled fonts from
`/themes_custom/ZoesDeckTheme/fonts/` (HTTP 200). File layout (unmarked = planned):

```
theme/
  theme.json            manifest_version 9; options as patches                          (done)
  fonts/                Oxygen 300/400/700, Instrument Serif Regular/Italic, OFL-*.txt   (done)
  shared/tokens.css     --zdt-* colors, radii, glass recipe, layout, motion             (done)
  shared/type.css       Motiva Sans -> Oxygen @font-face, serif accent titles           (done)
  shared/controls.css   buttons, toggles, sliders, dropdowns, row focus (all windows)  (done)
  sp/chrome.css         top bar, bottom bar, side-menu backdrop + QAM placement         (done)
  sp/settings.css       Settings sidebar and rows                                      (done)
  qam/qam.css           Quick Access sheet and tab rail                                 (done)
  menu/mainmenu.css     Steam menu sheet and items                                      (done)
  options/reduce-transparency.css                                                       (done)
  sp/home.css  sp/library.css  sp/gamepage.css  sp/dialogs.css  options/reduce-motion.css
```

## Rules that matter (details in RESEARCH.md)

1. **Class names:** Steam ships scrambled classes (`_3rsrz7BYWjqGBhzcpn-Auo`). Write the readable form
   `module_Name_hash` (e.g. `backgroundglass_BackgroundGlass_3rsrz`); CSS Loader converts it at load time.
   Only exact known names get converted: `[class*="gamepadui_BasicHome"]` works, but a true partial like
   **`[class*="gamepadhome_"]` silently matches nothing**. CSS Loader maps every listed name to the
   *newest* scrambled class, so an element still carrying an older one can't be reached by name: the
   Steam menu items are like this (`cef.py` prints such names with a trailing `!`), so `menu/mainmenu.css`
   selects them by structure. Some readable names contain extra underscores or odd hashes
   (`gamepaddialog_Field_S-_La`, `header_Header_1E_SL`); copy them from `cef.py tree`/`find` output.
   When Steam's own selector is a long class chain, add `:not(#zdt)` to ours: it matches everything
   but counts as an ID, so it outranks any class-only rule without `!important`.
2. **Fonts:** all Steam text uses `"Motiva Sans"`. Plan: redefine that family's `@font-face` to the Oxygen
   files so every weight maps through and Steam's own bold survives. Avoid `* { font-family … !important }`
   and never force one weight globally (Zoe's old preset forced 300, which killed all bold).
   Instrument Serif has no bold, so serif titles get hierarchy from size. **Verified working in Gaming
   Mode (2026-09-10).** Each override mirrors one of Steam's own `@font-face` descriptors exactly so ours
   wins the tie; keep it that way if Steam adds weights.
3. **Glass:** `backdrop-filter` only blurs content in the *same window*. It works over art in `SP`. The Quick
   Access and Steam menus are separate transparent windows; the blur behind them comes from
   `backgroundglass_BackgroundGlass_3rsrz` in `SP`, which we soften, so a translucent sheet in the menu
   window reads as frosted glass. **Steam sizes and positions the menu windows from their
   `*_ViewPlaceholder_*` elements in `SP`**: changing the placeholder's box moves and resizes the window
   (that's how Quick Access floats). Variables like `--basicui-header-height` exist only in `SP`, so give
   them a fallback in other windows. Over a running game there's no blur (the game is another layer),
   hence the fairly opaque `--zdt-sheet-fill`. "Reduce transparency" swaps the glass tokens for solids.
4. **Apple's rule:** Liquid Glass belongs to the controls and navigation layer only, never the content layer.
   tvOS-style focus = a slight size increase, soft shadow and sheen instead of a glowing border.
5. **Hiding elements:** add the `REQUIRE_NAV_PATCH` flag when using `display: none` on anything focusable,
   or controller navigation breaks.
6. **Publishing on DeckThemes:** prefix CSS variables (`--zdt-`), avoid `*` and `!important` unless necessary,
   stay under 10MB, no bundled third-party themes (use `dependencies`).
7. The Deck screen is 1280×800 at arm's length, not a TV — scale tvOS sizes down.

## Suggested next steps

1. ~~Create `theme/`, symlink it in, confirm CSS Loader loads it.~~ Done.
2. ~~Font swap.~~ Done and verified. Zoe should eyeball it on the real screen and say whether the serif
   accent titles (Home "Recent Games", Quick Access title, settings title) are the right ones.
3. ~~Radii + glass tokens → header/footer → QAM → Steam menu → Settings.~~ First pass done. Still to
   check: modal dialogs, Quick Access over a running game, Friends expanded, collapsed Steam menu. Small
   nit: in Quick Access, slider rows' separators sit 6px in from the others since the row-bleed change.
4. Homescreen layout pass, then focus effects and animations (add "Reduce motion").
5. Screenshot each step with `tools/shot.sh` so Zoe can review from the Mac.
