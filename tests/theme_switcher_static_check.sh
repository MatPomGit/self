#!/usr/bin/env bash
set -euo pipefail

# Test 1: applyTheme musi synchronizować active + aria-selected.
grep -En "btn\.setAttribute\('aria-selected', isActive \? 'true' : 'false'\)" docs/assets/js/theme-switcher.js >/dev/null

# Test 2: nie powinno być duplikacji logiki aria-selected w click handlerze.
if grep -En "Update aria-selected" docs/assets/js/theme-switcher.js >/dev/null; then
  echo "Unexpected leftover aria-selected update block"
  exit 1
fi

# Test 3: komentarz czasu scrolla powinien zgadzać się z DURATION=416.
grep -En "Fast anchor smooth scroll \(416 ms\)" docs/assets/js/scroll-animations.js >/dev/null
grep -En "var DURATION  = 416;" docs/assets/js/scroll-animations.js >/dev/null

echo "Static checks passed"
