# Research notes

Collected on the Deck on 2026-09-10 from CSS Loader's source code, the installed themes, Steam's UI files,
the DeckThemes docs and Apple's HIG. Sources are at the bottom.

## 1. How CSS Loader themes work

- A theme is a folder in `~/homebrew/themes/<Name>/` with a `theme.json` manifest plus CSS files.
- Bundled files load from `/themes_custom/<Name>/<path>` (a symlink inside `~/.local/share/Steam/steamui/`
  that points at `~/homebrew/themes`).
- **Gaming Mode is several separate browser windows ("tabs").** CSS Loader injects each file into the
  windows you list. Built-in aliases (from `css_inject.py`):

  | Alias | Window |
  |---|---|
  | `SP` / `bigpicture` | The main UI: Home, Library, game pages, settings |
  | `QuickAccess` | The "…" Quick Access menu (`QuickAccess_uid*`) |
  | `MainMenu` | The Steam button menu (`MainMenu_uid*`) |
  | `bigpictureoverlay` | QuickAccess + MainMenu |
  | `All` | bigpicture + bigpictureoverlay |
  | `desktop`, `store`, … | Desktop client, store pages |

  Each window is its own document, so shared tokens and `@font-face` rules must be injected into all three.

### theme.json (installed plugin supports manifest_version 9)

```json
{
  "name": "ZoesDeckTheme",
  "display_name": "Zoe's Deck Theme",
  "author": "zoeallgaier",
  "version": "v0.1",
  "description": "…",
  "target": "System-Wide",
  "manifest_version": 9,
  "flags": ["REQUIRE_NAV_PATCH"],
  "tabs": { "everywhere": ["SP", "QuickAccess", "MainMenu"] },
  "inject": {
    "shared/tokens.css": ["everywhere"],
    "--zdt-radius": ["16px", "everywhere"]
  },
  "patches": {
    "Glass": {
      "type": "slider",
      "default": "Regular",
      "values": {
        "Off": { "options/glass-off.css": ["everywhere"] },
        "Regular": {},
        "Clear": { "options/glass-clear.css": ["everywhere"] }
      }
    },
    "Accent": {
      "type": "none",
      "default": "Custom",
      "values": { "Custom": {} },
      "components": [{
        "name": "Accent color", "type": "color-picker", "on": "Custom",
        "default": "#ffffff", "css_variable": "zdt-accent", "tabs": ["everywhere"]
      }]
    }
  }
}
```

- `inject`: file → windows. A key starting with `--` injects a CSS variable: `[value, ...windows]`.
- `tabs`: custom window aliases (a `default` alias applies when a list is empty).
- `patches` = user options. `type`: `dropdown` (default), `slider`, `checkbox` (values must be exactly
  `Yes`/`No`), `none` (no control; used to host components). Each value maps to files/variables to inject.
- `components`: `color-picker` (injects `--var`, plus `--var_r/_g/_b/_rgb` for hex colors) and `image-picker`.
  `on` names the patch value that enables it.
- `dependencies`: other themes to enable, with patch overrides. `flags`: `KEEP_DEPENDENCIES`,
  `OPTIONAL_DEPENDENCIES`, `REQUIRE_NAV_PATCH` (fixes controller navigation when you hide elements).
- A `PRIORITY` file containing a number raises load order.

### Class names — important

Steam now ships **scrambled class names** in the live page, e.g. `_3LYP1SIxyoky-yW9Ug_1fq`. CSS Loader
keeps a translation table at `~/homebrew/themes/css_translations.json` (~15k entries,
`{ uid: [old names..., current live name] }`) and rewrites your CSS at load time:

- `.gamepadui_BasicHome_3LYP1` → `._3LYP1SIxyoky-yW9Ug_1fq` ✅ (also works without the hash suffix,
  e.g. `.gamepadui_BasicHome`)
- Attribute selectors using `*=`, `^=`, `|=` or `~=` are translated only when the quoted value is an exact
  known name: `[class*="gamepadui_BasicHome"]` works, `[class*="gamepadhome_"]` matches nothing.
  Plain `[class="…"]` (no operator prefix) is never translated.

`tools/cef.py tree` prints the live DOM with class names converted back to the readable form.

### Dev loop

- Live reload is on (`watch:1` in `~/homebrew/themes/STORE`): saving a file re-injects it. Otherwise:
  Quick Access → CSS Loader → Refresh.
- The CEF debugger is on `127.0.0.1:8080` (Decky proxies it on `:8081` for other machines on the network).
  From a Mac browser: `chrome://inspect` → Configure → `steamdeck.local:8081` (or the Deck's IP) (needs Decky's
  "Allow Remote CEF Debugging" setting). Or SSH-tunnel it:
  `ssh -L 8080:127.0.0.1:8080 deck@steamdeck.local`, then open `chrome://inspect` → `localhost:8080`.

## 2. Fonts

- Every piece of Steam text uses **`"Motiva Sans"`** (500+ declarations in
  `steamui/css/chunk~*.css`), so the cleanest swap is to redefine that family:

  ```css
  @font-face { font-family: "Motiva Sans"; font-weight: 300; src: url("/themes_custom/ZoesDeckTheme/fonts/Oxygen-Light.ttf"); }
  @font-face { font-family: "Motiva Sans"; font-weight: 400; src: url(".../Oxygen-Regular.ttf"); }
  @font-face { font-family: "Motiva Sans"; font-weight: 500 900; src: url(".../Oxygen-Bold.ttf"); }
  ```

  That keeps Steam's existing bold text bold (now Oxygen Bold) without `* {}` or `!important`.
  **Unverified**: our rules need to take precedence over Steam's own `@font-face`. Check in Gaming Mode
  with `cef.py eval SP 'getComputedStyle(document.body).fontFamily'` and a screenshot. If it doesn't win,
  set `font-family` on the root UI classes instead of `*`.
- **Instrument Serif** only has Regular and Italic, with no bold, so serif titles get hierarchy from size.
  Use it rarely on true "accent titles". Candidates (readable class names):
  - `gamepadhomerecentgames_RecentGamesHeaderLabel_1KKWf` — Home "Recent Games" heading
  - `gamepadtabbedpage_TabTitle_1nq0i` — Library tab titles
  - `quickaccessmenu_Title_34nl5`, `quickaccessmenu_PanelSectionTitle_1JWa5` — Quick Access headings
  - `pagedsettings_PagedSettingsDialog_Title_3qEgQ` — settings page title
  - `achievementsheader_Title_3wNyl`
  - `h1`/`h2`/`h3` are used a few dozen times in the UI code, so a light default there is reasonable.
- Zoe's old preset (`~/homebrew/themes/Fonts/font-css/instrumentoxy.css`) forced `font-weight: 300
  !important` on everything, which removed all bold, and targeted `.title`/`.header` classes that don't
  exist in Steam. Don't reuse it.
- Font files: `~/homebrew/themes/Fonts/fonts/` has `Oxygen-Light/Regular/Bold.ttf` and
  `InstrumentSerif-Regular/Italic.ttf`. Both families are SIL OFL, so they're fine to bundle with the licence.

## 3. Glass and corners

**Apple's guidance (HIG → Materials):**
- "Liquid Glass forms a distinct functional layer for controls and navigation elements … that floats above
  the content layer."
- "Don't use Liquid Glass in the content layer." Exception: transient controls like sliders and toggles
  take on glass while being used.
- "Use Liquid Glass effects sparingly."
- Two variants: **regular** (blurs + adjusts luminosity; for text-heavy things like sidebars, alerts,
  popovers) and **clear** (highly translucent; for controls over rich media). Over bright content, add a
  ~35% dark dimming layer.

**CSS recipe to start from:**

```css
:root {
  --zdt-glass-fill: rgba(255, 255, 255, 0.10);
  --zdt-glass-blur: blur(24px) saturate(180%);
  --zdt-glass-edge: inset 0 1px 0 rgba(255, 255, 255, 0.25), inset 0 0 0 1px rgba(255, 255, 255, 0.08);
  --zdt-glass-shadow: 0 8px 32px rgba(0, 0, 0, 0.35);
}
.zdt-glass-target {
  background: var(--zdt-glass-fill);
  backdrop-filter: var(--zdt-glass-blur);
  box-shadow: var(--zdt-glass-edge), var(--zdt-glass-shadow);
}
```

**Where glass goes:** top bar (`header_*`), button-hint footer (`footer_*`), Quick Access
(`quickaccessmenu_*`), Steam menu (`mainmenu_*`), dialogs (`gamepaddialog_*`), buttons/toggles, the focus
highlight. **Never** on game art, carousel capsules or backgrounds.

**Limitation:** `backdrop-filter` only samples pixels in the same window. In `SP`, glass over artwork is
real frosted glass. The Quick Access and Steam menus are separate windows layered by gamescope, so
`backdrop-filter` there has nothing to blur and will read as tinted translucency. Steam's own UI uses
`backdrop-filter` in places (blur 4–100px in `steamui/css/chunk~2dcc5aaf7.css`) and has a
`backgroundglass_*` component (`BackgroundGlass_3rsrz`, `Blur_N9sQL`, `DrawBackground_2NQoF`,
`Visible_fSM7w`). It might be how Steam gets real blur behind overlays; inspect it in Gaming Mode before
designing the menus.

**Performance:** blur is GPU work on the Deck's APU. Keep blurred elements few and fixed (not inside
scrolling lists), and ship a "Reduce Transparency" option that swaps in solid fills.

**Corners:** one radius scale (e.g. 8 / 14 / 22 / pill) and Apple's concentric rule:
inner radius = outer radius − padding between them.

## 4. Homescreen (tvOS-inspired)

Apple tvOS best practices: "Embrace the tvOS focus system, letting it gently highlight and expand onscreen
items", "edge-to-edge artwork, subtle and fluid animations", legible from a distance. Focus is shown with
lift/parallax rather than rings.

Plan:
- Full-bleed art from the focused game behind the home row. Steam already renders it:
  `gamepadhomerecentgames_RecentGamesBackground_1SRox` / `RecentGamesBackgroundImage_3Mp8R`. Make it
  larger and softer.
- Generous side margins, one row of games (`basicgamecarousel_*`) with even gaps, game names only on the
  focused item.
- Focus: scale ~1.06–1.08, soft shadow and a subtle sheen, replacing Steam's glow border
  (`focusring_*`, `*_ItemFocusAnim-*`).
- Hide clutter: "What's New" (`gamepadhomewhatsnew_*`), badges, game counts, home tabs
  (`gamepadhome_TabbedContent_cE1Sa`, which is what the old No Home Tabs theme hid). Use
  `REQUIRE_NAV_PATCH`.
- Top bar reduced to a glass pill with clock and battery.
- Scale for 1280×800 at arm's length, not a TV.

## 5. Animations

Only animate `transform` and `opacity`. 200–350ms with an Apple-style ease such as
`cubic-bezier(0.2, 0.8, 0.2, 1)`, for focus changes and menus opening. Ship a "Reduce Motion" option.
The SDH-AnimationChanger plugin (boot and suspend videos) is also installed if Zoe wants matching boot
animations.

## 6. Existing themes on this Deck (all turned off by Zoe)

`Fonts` (her Instrument Serif + Oxygen preset), `Better Game Icons` (30px radius), `Better Game Badges`,
`Clean Gameview` (blurred play bar), `Game Cover Shine Animation Color`, `no_home_tabs`, and a
`Clean Console Experience.profile` preset. They're useful reference for selectors, e.g.
`~/homebrew/themes/Clean Gameview/shared.css` and `~/homebrew/themes/no_home_tabs/bigpicture.css`.
Our theme should do these jobs itself or list them as `dependencies`, not copy their code.

## 7. DeckThemes submission rules (if publishing)

- Original work or permission; attribute anything borrowed.
- Target set correctly and only that target styled.
- Works on latest stable + beta SteamOS, Decky and CSS Loader.
- `*` and `!important` only when absolutely necessary.
- Under 10MB; prefix CSS variables with a unique identifier (`--zdt-`).
- No bundled themes, use `dependencies`. SFW. Preview images without text unless explaining options.

## Sources

- DeckThemes docs: https://docs.deckthemes.com/ — Features, Theming step by step, CEF debugger, Submission
- CSS Loader source on this Deck: `~/homebrew/plugins/SDH-CssLoader/css_inject.py`, `css_theme.py`,
  `css_themepatch.py`, `css_themepatchcomponent.py`
- Apple HIG: Designing for tvOS, Materials, Focus and selection
  (https://developer.apple.com/design/human-interface-guidelines/)
- Steam UI files: `~/.local/share/Steam/steamui/css/`

## Appendix: readable class names by module

Generated from `css_translations.json` (focus/hover animation classes omitted). Use these readable names
in CSS; CSS Loader translates them.

- **gamepadui** (29): `BasicHome_3LYP1`, `BasicUiRoot_gbo6E`, `Content_1FxmN`, `ContinuousRenderPixelBlink_3drkl`, `ContinuousRenderPixel_uLkXY`, `GamepadDialogOverlay_34Euf`, `GamepadUIPopupWindowBody_l25Af`, `MainNavMenuAnchor_vI9jJ`, `OpaqueBackground_b084m`, `QuickAccessMenuAnchor_1zGXS`, `StandaloneKeyboard_1uyWM`, `SteamUIPopupHTML_Rp8QO`, `SteamUIPopupWindowBody_QsvsR`, `SteamUIPopupWindow_1mfQu`, `TransparentBackground_3vBmc`, `TrueBlackBackground_28EI6`, `VR_1iivW`, `svg_library_GenericGamepadHighlight_1zfyD`, `svg_library_SpinnerSpokeFade_2QBT4`, `svg_library_Spinner_2Hc4f`, `svg_library_WifiBar1Anim_3WnTD`, `svg_library_WifiBar1_25g4S`, `svg_library_WifiBar2Anim_3BoKo`, `svg_library_WifiBar2_1Utwl`, `svg_library_WifiBar3Anim_1C2Pj`, `svg_library_WifiBar3_zZxOy`, `svg_library_WifiBar4Anim_bMD58`, `svg_library_WifiBar4_23OJc`, `svg_library_WirelessConnectingActive_UCVKt`
- **gamepadhome** (4): `BackstackRootTest_2yiqT`, `RecentSection_39tNv`, `ScrollArea_3PhGY`, `TabbedContent_cE1Sa`
- **gamepadhomerecentgames** (20): `FilterContainer_1lgko`, `HeaderExit_k7Eml`, `InLeft_22nzP`, `InRight2_Ji84a`, `InRight_1HKCB`, `LibraryHomeEmptyGames_7hpoO`, `MoveRight_3dyds`, `OptionContainer_2xvQH`, `Option_1oapP`, `RecentGamesBackgroundContainer_QNkOt`, `RecentGamesBackgroundImagePreload_MYh5N`, `RecentGamesBackgroundImage_3Mp8R`, `RecentGamesBackground_1SRox`, `RecentGamesHeaderLabel_1KKWf`, `RecentGamesHeader_35iRe`, `RecentGamesInnerContainer_282X0`, `Smaller_1onZs`, `Spacer_3Lhzm`, `TextBody_3zl7h`, `VR_2TjZF`
- **basicgamecarousel** (16): `ActionIcon_25Qbo`, `BasicGameCarouselItemMediaContainer_1HIFN`, `BasicGameCarouselItem_3YYQ9`, `BasicGameCarousel_3MdH5`, `CarouselCapsuleBackgroundGlow_1H3Kf`, `CarouselGameLabelWrapper_ZkD6W`, `CarouselGameLabel_3CKji`, `EmptyLibraryCarouselItem_2utGW`, `FeaturedSeparator_1qOWM`, `Featured_2eJEJ`, `FriendsInGame_3z5U1`, `IsFocused_2KPrM`, `Play_12eKc`, `ShowAsHovered_3tdVJ`, `SubMessage_1BtXg`, `TextBoxCarouselContents_3bvCH`
- **gamepadhomewhatsnew** (28): `BasicHomeUpdates_3TTpk`, `Empty`, `EventCarousel_2GBhv`, `EventImageWrapper_XLJ9p`, `EventImage_116GS`, `EventInfo_6TGe7`, `EventPreviewContainer_1ltOY`, `EventPreviewOuterWrapper_10b1V`, `EventType10_2iLnu`, `EventType11_1I2pe`, `EventType13_16aly`, `EventType14_ovxhr`, `EventType15_1FEOx`, `EventType23_qVIYl`, `EventType28_39b83`, `EventType35_LeZ61`, `EventType_1f0dZ`, `GameIconAndName_1jXSh`, `GameIcon_2RrB8`, `Inner`, `Inner_3Rfji`, `LibraryHomeWhatsNew_rvYRf`, `Loading_2LlgI`, `MultilineClippedText_tT1EP`, `OuterWrapper_3DpEz`, `SummaryText_2uRde`, `Title`, `Title_1QLHG`
- **header** (40): `BatteryIconInnerIcon_Kt2Hb`, `BatteryIconVerticalStack_3XySI`, `Clickable_8sPcK`, `Clock`, `Clock_1HhLU`, `CurrentUserAvatar_2HXdb`, `DashboardBar_2Ismz`, `Dev_1Zipt`, `DownloadStartedProgressBar_35WBc`, `DownloadStartedSVG_19WOH`, `DownloadStarted_2eSHU`, `FadeBackgroundOpacity_1J8zH`, `FamilyViewIcon_2CF3B`, `FamilyView_3QfCJ`, `HasActiveSupportAlert_2IweB`, `HeaderAppPortraitContainer_1PbL3`, `HeaderAppPortrait_SB4L7`, `HeaderDownloadContainer_2ssr3`, `HeaderDownloadProgressBarBackground_vo3Tt`, `HeaderItem_2HnVd`, `InQuickAccess_2mRo5`, `Locked_6VgzC`, `NewAppDownloading_1eMUq`, `NotificationsIcon_cieWw`, `OverrideHeaderBackground_MS2nB`, `OverridesInteractionSuppression_EI3pO`, `Profile_1O7J0`, `SteamConnectionWarningIcon_2RK0x`, `SuppressInteraction_3QJwU`, `Title`, `Title_3R23Z`, `UnformattedDriveIcon_ZfxFq`, `UnreadChatMessages_3gfH2`, `UpdatesIcon_33cHT`, `VR_m2Zys`, `VoiceChatStatus_32nVD`, `VolumePopinHidden_3YKZN`, `VolumePopin_2WOJ5`, `VolumeSliderPosition_CTOqO`, `WirelessIcon_3alLb`
- **footer** (7): `BasicFooter_3T1iF`, `FooterLegend_2JJDH`, `Opaque_2PZqi`, `PillShapedIcon_1aE5r`, `Relative_1u4NT`, `Spacer_j7NCO`, `WithKeyboard_1fMXT`
- **backgroundglass** (4): `BackgroundGlass_3rsrz`, `Blur_N9sQL`, `DrawBackground_2NQoF`, `Visible_fSM7w`
- **focusring** (8): `DebugFocusRing_YxeOZ`, `FocusRingOnHiddenItem_2OusV`, `FocusRing_1IZrQ`, `blinker_3wFMM`, `fadeOutline_2hZu3`, `flash`, `flash_1YTKZ`, `growOutline_Z3LxS`
- **quickaccessmenu** (48): `AllTabContents_2yKG4`, `BatteryIcon_3KqVu`, `BatteryPercentageLabel_209R3`, `BatteryProjectedValue_1Yq4s`, `Blocked_8BbyF`, `ComingSoon_17NMm`, `Container_3DHXr`, `ContentTransition_32AON`, `Down_3rR0o`, `EmptyNotifications_2pgiB`, `Enter`, `EnterActive_3pxdH`, `Enter_1JPfL`, `ExitActive_3repy`, `Exit_1hez6`, `FooterBoxShadow_ISUYE`, `FriendsListTabPanel_2obg6`, `FriendsTitle_1jWuu`, `FullHeight_3ud27`, `HeaderAndFooterVisible_2m0zl`, `HeaderContainer_3k5MH`, `Label`, `Label_Ks1OT`, `LowBattery_AtwmU`, `Menu_1gJzx`, `PanelExitAnchor_3rRq0`, `PanelOuterNav_2BB6u`, `PanelSectionRow_1TJv6`, `PanelSectionTitle_1JWa5`, `PanelSection_ljJSM`, `PopupBody_1DxtO`, `QuickAccessNotifications_1TQu7`, `ReallyLow_2vxcv`, `Remaining_2D6Sj`, `Selected_2QHMu`, `TabContentColumn_2z5NL`, `TabGroupPanel_1QO7b`, `TabPanelHidden_vjLhN`, `Tab_1S76C`, `TabsWithFooter_3hbAG`, `Tabs_3Ag1w`, `Text_2B2VB`, `Title`, `Title_34nl5`, `Up_1GhPw`, `VR_3E9A1`, `ViewPlaceholder_2orc8`, `VoiceTab_5lc3T`
- **quickaccesscontrols** (18): `BatteryDetailsLabels_3M39z`, `BatteryIcon_39aNh`, `BatteryPercentageLabel_3Rxxi`, `BatteryProjectedLabel_4hS40`, `BatteryProjectedValue_1mTo6`, `BatterySectionContainer_3h5MR`, `ComingSoon_OoiQp`, `Label`, `Label_3QQ72`, `LowBatteryGauge_3gHEu`, `LowBattery_2YBbx`, `PanelSectionRow_2VQ88`, `PanelSectionTitle_2iFf9`, `PanelSection_2C0g0`, `QuickAccessNotifications_2HCcx`, `ReallyLow_3ONpu`, `Text_1hJkB`, `VR_31jiF`
- **mainmenu** (20): `ActiveDot_1uLVH`, `Active_10bq5`, `Blocked_1OasT`, `Collapsed_3I23q`, `Container_3vzvO`, `CurrentUserAvatar_1bMnV`, `ExitAnchor_3TqAn`, `FooterBoxShadow_3kHmf`, `Fullscreen_26eRZ`, `IsVirtualKeyboardShown_2V0dd`, `ItemIcon_3xZ3Z`, `ItemOuter_1BbM8`, `Item_2w9Tp`, `Menu_23IDi`, `Open_3apLK`, `PopupBody_3hY23`, `RunningAppIcon_26pwH`, `RunnningAppSeparator_33RkH`, `VR_1ABsh`, `ViewPlaceholder_1PGlK`
- **gamepadtabbedpage** (37): `Active_2KTCH`, `AnimateDownwardExpansion_2DyJb`, `Arrows_1Rv2q`, `BleedGlyphs_GPc8M`, `CanBeHeaderBackground_18zGL`, `Enter`, `EnterActive_3lqCS`, `Enter_11zfc`, `ExitActive_1V17j`, `Exit_3Rv4M`, `ExpandFadeDownwards_3Lfeq`, `FixCenterAlignScroll_1CJeU`, `Floating_3I3IM`, `GamepadTabbedPage_3IBLc`, `HasAddon_2tufx`, `IsUnderHeader_31Zle`, `LeftAddon_Aq2Xe`, `Left_3lSTy`, `OverlayPinnedView_25Oqw`, `Right`, `RightAddon_KFGEk`, `ScrolledDown_1jNhb`, `Selected_3Gp1b`, `Show_1ZEnd`, `SortAndFilterButton_25nG9`, `SortAndFilterContainer_3UdPh`, `TabBadge_3kKTT`, `TabContentsScroll_1X4dt`, `TabCountBadge_19sQx`, `TabCount_1ui4I`, `TabHeaderRowWrapper_2Jobs`, `TabIcon_3Ebb3`, `TabRowSpacer_dCYln`, `TabRowTabs_2VQFn`, `TabTitle_1nq0i`, `Tab_3eEbS`, `TabsRowScroll_26cOW`
- **gamepadlibrary** (6): `AppGridFilterHeaderAsButton_2tDpu`, `AppGridFilterHeader_eGFYo`, `CollectionContents_38Mnc`, `CollectionHeader_1UuM8`, `ComingSoon_2qGmT`, `GamepadLibrary_ZBBhe`
- **sharedappdetailsheader** (39): `AddBoxSizer_30qkI`, `Background_3h8sv`, `BottomCenter_7Muka`, `BottomLeft_TJInl`, `BottomRight_3pM0Z`, `Bottom_3zocf`, `BoxSizerButtonContainer_2VX3O`, `BoxSizerDelete_1PkXP`, `BoxSizerEdge_1pW2c`, `BoxSizerGridBox_SOent`, `BoxSizerInfo_15Amg`, `BoxSizerSettings_1A8eE`, `BoxSizerValidRegion_3IAVE`, `BoxSizer_30GVp`, `CenterCenter_1n52Y`, `EdgeDown_2GhIW`, `FallbackArt_kgNCR`, `FullscreenEnterActive_2FlTp`, `FullscreenEnterDone_1PRtu`, `FullscreenEnterStart_P7eLv`, `FullscreenExitActive_1yfFC`, `FullscreenExitDone_K6WfG`, `FullscreenExitStart_1sphg`, `HeaderBackgroundImage_1sarA`, `ImgBlur_3XYFK`, `ImgContainer_3VFZB`, `Left_1SkZn`, `NoArt`, `NoArt_3ixso`, `Right`, `Right_2Lhfb`, `TextNameSpace_32q5n`, `TitleLogo_38wKH`, `TopCapsule_2meE3`, `TopGradient_2qcOu`, `TopLeft_22mT3`, `TopRight_2R2GI`, `UpperCenter_1A9Wm`, `UpperLeft_12mBn`
- **basicappdetailssectionstyler** (16): `ActionButtonAndStatusPanel_1fHBR`, `ActionRow_2Gj21`, `AppActionButton_QsZdW`, `AppButtons_1thLD`, `AppDetailsContent_17iCv`, `AppDetailsRoot_3fp5y`, `CollectionsHeader_3hW5F`, `DeckVerifiedFeedbackConfirmation_2ddhh`, `DeckVerifiedFeedbackContainer_3Y8xV`, `DeckVerifiedFeedbackQuestion_r0XD8`, `GameInfoCollections_32SD3`, `GameInfoContainer_pzBMd`, `GameInfoQuickLinks_2GqvV`, `Header_1IW9p`, `InvertFocusedIcon_3uJLN`, `PlaySection_3scbH`
- **gamepaddialog** (54): `ActiveAndUnfocused_11tOP`, `AlignCenter_3groU`, `AlignLeft_2N3q6`, `AlignRight_4eBGA`, `BasicTextInput_3GCBi`, `BeforeChildren_1qtqB`, `Button_1kn70`, `ChildrenWidthFixed_1ugIU`, `Clickable_27UVY`, `CompactPadding_1DIZQ`, `ControlsListChild_XvRso`, `ControlsListOuterPanel_2Mvpu`, `Disabled_1pmyx`, `DropDownControlButtonContents_Lzved`, `DropDownRow_xCbGI`, `ExtraSpacing_3YMmG`, `Field`, `FieldChildrenInner_3N47t`, `FieldChildrenWithIcon_2ZQ9w`, `FieldClickTarget_TN6vN`, `FieldDescription_2OJfk`, `FieldIcon_1sC68`, `FieldLabelRow_H9WOq`, `FieldLabelValue_lcD7J`, `Front`, `Front_YngiU`, `GamepadDialogContent_3joNk`, `GamepadDialogContent_InnerWidth_3Xeyd`, `HighlightOnFocus_wE4V6`, `IconContainer_223iJ`, `InlineWrapShiftsChildrenBelow_pHUb6`, `ItemMaxSizeDesktop_LFWdf`, `Label`, `LabelFieldValue_5Mylh`, `Label_SqnsK`, `ModalClickToDismiss_2szdG`, `ModalPosition_30VHl`, `NoHeaderPadding_2kAHX`, `NoMinWidth_21cih`, `On_3ld7T`, `Spacer_3nOZQ`, `StandaloneFieldSeparator_23kNb`, `StandardPadding_XRBFu`, `ToggleRail_2JtC3`, `Toggle_24G4g`, `VR_1sYg0`, `VerticalAlignCenter_3XNvA`, `WithBottomSeparatorStandard_3s1Rk`, `WithBottomSeparatorThick_28hmy`, `WithBottomSeparator_1lUZx`, `WithChildrenBelow_1u5FT`, `WithDescription_3bMIS`, `WithFirstRow_qFXi6`, `slideInAnimation_17KuO`
- **pagedsettings** (15): `Active_Myra7`, `DisabledItem_1RDp9`, `HidePageListButton_3i4Ep`, `NoPadding_1iWhH`, `PageListItem_Icon_U6HcK`, `PageListItem_Title`, `PageListSeparator_1UEEm`, `PageListSpacer_33lCZ`, `PagedSettingsDialog_PageContent_1I3Ni`, `PagedSettingsDialog_PageListColumn_RTicB`, `PagedSettingsDialog_PageListItem_bkfjn`, `PagedSettingsDialog_PageList_DisableScrolling_36Srg`, `PagedSettingsDialog_Title`, `PagedSettingsDialog_Title_3qEgQ`, `Transparent_SeoUZ`
- **appportrait** (77): `AppPortraitBannerContainer_2jj5T`, `AppPortraitBanner_N8aJr`, `BarDownloading_3BNwj`, `BasicMode_3vi6S`, `CapsuleVisible_3QIfJ`, `Capsule_13w3S`, `CarouselItemLabelWrapper_31TK9`, `CarouselItemLabel_1Cmux`, `ClassAllAchieved_31wTt`, `ComingSoonBanner_QTJZo`, `ComingSoonIcon_1pvln`, `ControllerSupportIcon_1TaKf`, `Disabled_1aml4`, `Download_3yGiL`, `Draggable_1pwP4`, `Featured_10w8f`, `FooterBlurImageContainer_RhmvO`, `FriendsBar_3dncO`, `GameUpdatedCircle_3ezYo`, `Header_2zIRl`, `HoversEnabled_54PuC`, `IconsRestCount_2JYwp`, `IconsView_1WWmQ`, `InCollection_3ANru`, `InDownloads_3J3TT`, `InFriendsActivity_3ngZC`, `InGameDetails_1QRCG`, `InLibraryManager_6vZ6m`, `InPlayNext_L3xTn`, `Landscape_3VOR2`, `Large`, `Large_NSf2V`, `LibraryBottomItems_tvCvy`, `LibraryItemActionButton_3AjoL`, `LibraryItemBoxShine_MyNb5`, `LibraryItemBoxSubscript_1LJqx`, `LibraryItemBoxTitle_1tO8p`, `LibraryItemBox_WYgDg`, `LibraryItemIcons_3BPFq`, `LibraryItemOverlayInnerArea_2GRcK`, `LibraryItemOverlayOuterArea_2BOmk`, `LibraryItemUpdateBadge_24AOi`, `LockedGame_2mDBh`, `MCGreen_1KR40`, `MCOrange_1H3NR`, `MCRed`, `MCRed_3lWVD`, `Medium_3SNGK`, `Message_3CRLA`, `NoCapsuleImage_eKPNT`, `PlayedRecent_3JWBB`, `PlaytimeDetails_3bkuo`, `PortraitHover_301ft`, `PortraitImage_2IYf7`, `PortraitMessage_3gwMk`, `Portrait_1Pf6J`, `RecentGameFooter_2d1hS`, `SVGIcon_Button_rqQs9`, `Short`, `Short_yGeS6` …
