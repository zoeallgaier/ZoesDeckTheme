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

## Status (2026-09-12)

- Research done (see `docs/RESEARCH.md`).
- Zoe has **turned off all other installed themes** for a clean start, so nothing else is styling the UI.
- `theme/` exists, is symlinked in and **active** (`theme/config_USER.json`, gitignored). It has
  `theme.json`, `shared/tokens.css` (all `--zdt-*` tokens) and `shared/type.css` (font swap + serif accent
  titles, behind the "Theme fonts" checkbox). Verified in Gaming Mode: the "Motiva Sans" override works
  (Motiva measures identically to Oxygen at 300/400/700, so Steam's bold survives) and the Home
  "Recent Games" label renders in Instrument Serif.
- Accent: the default stays tvOS white (`--zdt-accent`, `#ffffff`); Zoe has been trying a lime green
  in the picker. `--zdt-on-accent` picks an opaque near-black or white for whatever accent is chosen
  (CSS relative colour + color-mix, supported here).
- Step 3 (glass + radii) done and approved by Zoe ("looking great"): floating glass top/bottom bars,
  Quick Access and Steam menu as floating glass sheets, shared controls (buttons, fully opaque iOS-style
  toggles, sliders, dropdowns, row focus), Settings (floating sidebar, rounded rows, serif page title),
  "Reduce transparency" option. Zoe's requests from review: Quick Access tab rail moved to the **right**
  (thumb reach), Friends tab cleaned up (gap in expanded mode, no slab header, rounded rows, serif
  heading), Decky plugin titles scroll away like Steam's instead of sticking. Not yet checked: modal
  dialogs, in-game Quick Access, collapsed Steam menu, Library, game pages, d-pad left/right across the
  flipped Quick Access rail (Steam's nav there has no flow-children, so it should be geometric).

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

`tree`/`find` translate class names for you, but **`eval` does not**: inside `eval` you must use the
class the live DOM actually carries, which on this build is the fully scrambled form
(`QNkOtW3xS-yj6LviWHvnd`), not the readable name you write in CSS. Look it up in
`~/homebrew/themes/css_translations.json` — each readable name maps to a list of aliases, and the one in
the DOM is the last, wordless entry. Querying a readable name from `eval` silently returns nothing, which
looks exactly like being on the wrong page.

`tools/reload.sh [--watch]` triggers CSS Loader's reload (see Environment).

`tools/icons.py <lucide-static>/icons` regenerates `theme/shared/icons.css`, the outline icon swap
(Lucide v0.460.0; `npm pack lucide-static@0.460.0` or the registry tarball has the icons). Its table
maps Steam icons (by the start of a path's `d`, or a selector) to Lucide names. Zoe wants **UI icons
only** (menus, rails, Settings sidebar, quick settings, top bar, page buttons), not niche ones.
`tools/iconinv.js` lists the icons in a window that aren't swapped yet (run it with `cef.py eval`).

`tools/shot.sh out.png [qam [tab]|menu|close]` takes a **full-screen** screenshot with every window
composited (`gamescopectl screenshot`), optionally opening Quick Access (tab 4 = settings, 999 = Decky)
or the Steam menu first. Use this to review menus; `cef.py shot` only sees one window.

Navigate from a script with Decky's helpers in the shared context, e.g.
`python3 tools/cef.py eval SharedJSContext 'DFL.Navigation.Navigate("/settings/display"), 1'`
(also `OpenQuickAccessMenu(tab)`, `OpenMainMenu()`, `CloseSideMenus()`; go back with
`Navigate("/library/home")`). To preview a focus style without a controller, add the `gpfocus` class
to an element with `eval`, screenshot, then remove it. For real focus moves use `tools/key.py SP
ArrowRight ArrowLeft Escape ...`: it sends key presses through the debugger, and Steam treats arrow
keys like the d-pad (Escape = B). Don't call `element.focus()` from `eval`: Steam's navigation
doesn't see it and the page ends up with nothing focused.

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
  qam/qam.css           Quick Access sheet, tab rail (on the right), Friends, Decky bits (done)
  home/home.css         Home: full banner art, blurred mirror, Steam's row zoomed below (done)
  home/hide-whats-new.css  "Show What's New on Home" off (default)                       (done)
  home/home-dotgrid.css "Home background: Dot grid" — the site's backdrop, game-coloured  (done)
  sp/gamepage.css       game pages: 70% art + mirror, centred logo/Play                (done)
  shared/icons.css      outline icon swap, GENERATED by tools/icons.py                  (done)
  shared/gameicons.css  rounded small game icons (from Better Game Icons, MIT)          (done)
  shared/keyboard.css   on-screen keyboard: recoloured in the theme's palette           (done)
  sp/badges.css         card badges on focus only, fading (from Better Game Badges, MIT) (done)
  sp/dialogs.css        pop-up dialogs, CSS Loader's colour picker                      (done)
  sp/contextmenu.css    Options (≡) menus as an iOS-style glass sheet                   (done)
  menu/mainmenu.css     Steam menu sheet and items                                      (done)
  options/reduce-transparency.css                                                       (done)
  options/oxygen-titles.css  "Title font: Oxygen" — points --zdt-font-serif at Oxygen   (done)
  sp/library.css  sp/dialogs.css  options/reduce-motion.css
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
   Instrument Serif has no bold face; Zoe wants the accent titles in its **Italic, bold**, so they use
   the real italic with `font-synthesis: weight` (Chromium thickens it). **Verified working in Gaming
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
   Inside the Quick Access window, `backdrop-filter` on content in the tab scroller had no visible
   effect (tried for Decky's sticky title), so don't design around blur there.
4. **Apple's rule:** Liquid Glass belongs to the controls and navigation layer only, never the content layer.
   tvOS-style focus = a slight size increase, soft shadow and sheen instead of a glowing border.
5. **Hiding elements:** add the `REQUIRE_NAV_PATCH` flag when using `display: none` on anything focusable,
   or controller navigation breaks.
   **Layout changes navigation too:** Steam picks each panel's d-pad behaviour from its computed CSS
   (library.js): a flex row is a ROW, but a flex row with `flex-wrap: wrap` is a GRID; `row-reverse`,
   `column`, `column-reverse` map to their own modes; `display: grid` is a GRID (GEOMETRIC with
   `grid-template-areas`); anything else is a COLUMN unless its first child floats (ROW) or is
   inline(-block) (GRID). Wrapping the game page's Play row made right-from-Play do nothing, so
   never change `display`, `flex-direction` or `flex-wrap` on a focusable panel without testing
   the d-pad with `tools/key.py`; move things out with `position: absolute` instead.
6. **Blurred reflections:** `-webkit-box-reflect` draws the mirror as a separate compositor copy.
   Backdrop blur only reached part of it on game pages (it works on Home, whose box is
   `contain: strict`). CSS `blur()` fades an element's edges to transparent and doesn't spill
   past them here, so two blurred layers meeting leave a dark line. Game pages therefore use
   Steam's own `library_hero_blur.jpg` copies (`ImgBlur`, `ImgBlurBackdrop`) with no CSS blur,
   sized exactly like the art so the mirror lines up.
7. **Rounding images:** `overflow: visible` on an `<img>` turns off its `border-radius` clipping
   (the avatar was square because of this); use `overflow: clip` on the image itself.
8. **Publishing on DeckThemes:** prefix CSS variables (`--zdt-`), avoid `*` and `!important` unless necessary,
   stay under 10MB, no bundled third-party themes (use `dependencies`).
9. The Deck screen is 1280×800 at arm's length, not a TV — scale tvOS sizes down.

## Suggested next steps

1. ~~Create `theme/`, symlink it in, confirm CSS Loader loads it.~~ Done.
2. ~~Font swap.~~ Done and verified. Zoe should eyeball it on the real screen and say whether the serif
   accent titles (Home "Recent Games", Quick Access title, settings title) are the right ones.
3. ~~Radii + glass tokens → header/footer → QAM → Steam menu → Settings.~~ Done. Still to check:
   modal dialogs, Quick Access over a running game, collapsed Steam menu.
4. ~~Homescreen layout pass.~~ Done to Zoe's mockup (2026-09-10): banner art full width at its
   own 1920×620 ratio, the stock row below, sitting on a blurred mirror image of the art (the
   same look as game pages, which Zoe sketched). No "Recent Games" heading: the focused game's
   name hangs above its card in the serif (Steam keeps that label inside the first card's cell
   and stretches it to the focused card, so it can't be pinned to the left). She tried square
   icons and rejected them (logos got cropped), so cards keep Steam's shapes; the row is shrunk
   with CSS `zoom` (0.72, not resized) because Steam scrolls it with stock-size maths, and its
   inline fixed height is overridden. Top bar: status icons on the left (search is a magnifier
   that opens over the row while typing), lower-case Oxygen Light clock and an 85% avatar with
   an accent status dot on the right; focus grows an item instead of lighting a slab. On Home
   the bar floats lower and further in, gliding up and out on other pages or with a menu open
   (`:has()` on the RecentSection and on `backgroundglass_Visible`).

   **Second Home look, as an option (2026-09-12), not yet confirmed by Zoe.** "Home background"
   in CSS Loader now offers "Game art" (the default, above, unchanged) or "Dot grid"
   (`home/home-dotgrid.css`, layered over `home/home.css`): zoeallgaier.com's backdrop —
   ground colour, two soft radial pools at the site's own geometry, animated dot grid — taking
   its colour from the selected game, with the name set like the site's hero. Four things the
   DOM forced, all of them easy to undo by accident:
   - **Colour with no per-game setup** comes from Steam's own banner art, blurred and masked
     into the two pools. Do **not** give that `<img>` a transform: Steam cross-fades two copies
     of it on every move and drives that with an animation that animates `transform`, which
     beats a static one — the art then collapses into a corner for the length of each move.
     Leaving transform alone is also what makes the colour change between games smooth.
   - **The name is pinned** (same pixel, left-aligned, whatever has focus) although every card
     carries its own copy inside the row's horizontal scroller. `position: fixed` alone does
     not do it: react-virtualized writes `will-change: transform` **inline** on the carousel,
     which makes it the containing block for fixed descendants, so they scroll with the content.
     Overriding that to `scroll-position` (one of the theme's few `!important`s — an inline
     style outranks any selector) lets fixed reach the window.
   - **Its width** is Steam's, written inline: it stretches the label from the first card to the
     focused one, so the line can be a few hundred pixels. `min-width` clamps the used width
     without needing `!important`.
   - **Cropping.** Steam sized these boxes for a 30px sans label; at 68px Instrument Serif the
     ink is taller than the line box even with no descenders, and `marquee_Content` clips its
     own overflow-y. The track is let out of its clip and the marquee above it padded below the
     baseline (cancelled by a negative margin), which also gives the hero's rise its mask.

   Zoe's calls so far: titles pinned and left-aligned rather than tracking the cards; upright
   Instrument Serif, not the italic the theme's other accent titles use; art softened but still
   recognisable, not blurred to abstraction.
5. ~~Game pages, then the Options (≡) menus.~~ Done and reviewed with Zoe (2026-09-10). Game
   pages follow Zoe's sketch: art cropped to the width at 70% of the screen height (never
   stretched), the logo and one centred group of Play + controller + settings (frosted glass) on
   it (logo box 76% wide by 200px, after Zoe asked for logos twice as big), and below it a
   blurred mirror image fading out by the bottom bar; stats, Steam Cloud and the tabs start below
   the fold (the stats are absolutely positioned: see rule 5). Pages without art (`NoArt`/`FallbackArt`) keep Steam's layout.
   The Play label is Instrument Serif with its icon after it. A theme can't choose which artwork
   size Steam loads. Play/Install/controller/settings and the top bar's search/bell use Lucide
   outline icons (now generated into `shared/icons.css`, see Tools); Wi-Fi and battery stay
   Steam's because they draw live state. Still to check: Your stuff / Community / Game Info tabs
   (Game Info's link buttons are still square). Open an Options menu from a script by calling
   the focused card's React `onContextMenu` prop (see how it was done in the session: walk
   `__reactFiber` props from `.gpfocus`). Still unstyled: Library.
6. ~~Round two of Zoe's review (2026-09-11).~~ Done: dialogs + CSS Loader's colour picker
   (`sp/dialogs.css`), Power menu without red, UI icons everywhere, Better Game Badges/Icons folded
   in, volume pop-up as a glass capsule (`audio_VolumePopin` in SP; trigger it with the audio
   store's `OnVolumeButtonPressed()`, found via `DFL.findModuleChild`), Downloads page
   (`/library/downloads`), account page (`/account`, the avatar's page), a game's controller
   settings, Settings controller pages, text fields. Over a running game (checked with Zoe's
   game open): nothing can blur the game (separate gamescope layer, no gamescope blur exposed),
   so the Quick Access and Steam menu sheets switch to `--zdt-sheet-fill-ingame` and the backdrop
   dims more. In-game signals: Quick Access `HeaderAndFooterVisible`, the Steam menu's
   `RunnningAppSeparator`, SP's `BasicHome.TransparentBackground`. In-game, Quick Access draws its
   own top bar, so `sp/chrome.css` also loads in the QuickAccess window; the Steam menu's
   running-game panel is styled by structure in `menu/mainmenu.css`: Steam fixes its height at
   100% minus the header and footer, so it needs `height: auto` to respect the floating margins,
   and its controller layout column is hidden until Controller settings is chosen, which is when
   Steam adds `.FocusedColumn` to it. `gamescopectl screenshot`
   only captures the game while one runs: shoot the menu windows with `cef.py shot` and composite.
   Ask Zoe to open a game rather than launching one on her Deck.
7. ~~The on-screen keyboard.~~ Done (2026-09-12), not yet confirmed by Zoe: `shared/keyboard.css`.
   Steam draws the keyboard **inline inside whichever window owns the focused text field**, not in
   a window of its own, and the Quick Access window has its own keyboard manager, so the file loads
   `everywhere` rather than only in SP. It themes itself from a block of CSS variables on the
   Keyboard element, one set per built-in skin (`.DefaultTheme`, `.Pumpkin`, `.Grape`...), so
   redefining the DefaultTheme set recolours nearly all of it in one place. One catch: DefaultTheme
   **hardcodes its pressed colour** (Steam blue) instead of reading `--key-touched-background-color`,
   so that state needs a real rule.

   **Colour only, deliberately.** A first version also restyled the layout -- padding on the
   container and the key hit areas, a scale on the focused key, and the keyboard's own
   `backgroundglass` inset and rounded into a floating sheet -- and Zoe reported it broke typing.
   Steam sizes the keys and their touch targets to the pixel (the key itself is
   `pointer-events: none`; the hit area around it is what catches the finger, and both are pinned
   to a 44px row), so treat every box on the keyboard as untouchable: no padding, margin,
   transform, border, display or animation. `border-radius`, `box-shadow`, `color`, `background`
   and `font-family` are safe -- none of them move a box. The current file is measurably inert:
   every key and hit-area rectangle is identical to stock, with the theme on and off.

   **Still needs a real-hands check**, because typing cannot be tested from here: synthetic
   `Input.dispatchTouchEvent` / `dispatchKeyEvent` through CEF do not reach the keyboard's
   handlers, so a script cannot tell a working keyboard from a broken one. Ask Zoe to type. Also
   unchecked: over a running game, and a keyboard opened from a Quick Access text field.

   There is no API to open it from a script. Focus a text field first (Home's search will do),
   or it no-ops for want of a keyboard owner; then walk the React fiber tree from any element in
   the window for a prop whose value has a `VirtualKeyboardManager`, and call that manager's
   `SetVirtualKeyboardVisible()` / `SetVirtualKeyboardHidden()`.

8. Focus effects and animations polish, plus a "Reduce motion" option.
9. Screenshot each step with `tools/shot.sh` so Zoe can review from the Mac.
