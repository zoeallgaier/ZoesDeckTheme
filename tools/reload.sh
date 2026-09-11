#!/usr/bin/env bash
# CSS Loader's live reload only watches real files under ~/homebrew/themes and doesn't follow the
# ZoesDeckTheme symlink, so saving files in theme/ doesn't trigger it. Writing this ping file does.
# It's a file, not a folder, so CSS Loader never tries to load it as a theme.
#
#   tools/reload.sh           reload once
#   tools/reload.sh --watch   reload whenever a .css file or theme.json in theme/ changes

PING="$HOME/homebrew/themes/.zdt-reload.css"
THEME="$(cd "$(dirname "$0")/../theme" && pwd)"

ping_loader() { echo "/* $(date +%s.%N) */" > "$PING"; }

newest() { find "$THEME" \( -name '*.css' -o -name theme.json \) -printf '%T@\n' | sort -n | tail -1; }

if [ "$1" = "--watch" ]; then
  echo "Watching $THEME (Ctrl+C to stop)"
  last=$(newest)
  while sleep 0.5; do
    now=$(newest)
    if [ "$now" != "$last" ]; then
      ping_loader
      echo "reloaded $(date +%T)"
      last=$now
    fi
  done
else
  ping_loader
fi
