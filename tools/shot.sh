#!/usr/bin/env bash
# Full-screen Gaming Mode screenshot with every window composited, via gamescope. `cef.py shot`
# captures one window only, so it can't show the Quick Access or Steam menu over the page.
#
#   tools/shot.sh out.png              the screen as it is
#   tools/shot.sh out.png qam [tab]    open Quick Access first (tab: 4 = settings, 999 = Decky)
#   tools/shot.sh out.png menu         open the Steam menu first
#   tools/shot.sh out.png close        close both menus first
#
# The menus are opened through Decky's DFL.Navigation, so Decky must be running.

OUT="${1:?usage: tools/shot.sh out.png [qam [tab]|menu|close]}"
CEF="$(dirname "$0")/cef.py"

nav() { python3 "$CEF" eval SharedJSContext "DFL.Navigation.$1, 1" > /dev/null && sleep 1.5; }

case "$2" in
  qam)   nav "OpenQuickAccessMenu(${3:-})" ;;
  menu)  nav "OpenMainMenu()" ;;
  close) nav "CloseSideMenus()" ;;
esac

rm -f "$OUT"
gamescopectl screenshot "$OUT" > /dev/null
for _ in $(seq 20); do [ -s "$OUT" ] && break; sleep 0.25; done
[ -s "$OUT" ] && echo "saved $OUT" || { echo "screenshot failed" >&2; exit 1; }
