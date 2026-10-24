#!/usr/bin/env bash
# Bash VID: samodzielny pokaz podstaw Bash w terminalu.
# Uruchom: bash bash-vid.sh [--fast]
set -euo pipefail
delay=0.8
case "${1:-}" in
  "") ;;
  --fast) delay=0 ;;
  -h|--help) printf '%s\n' 'Użycie: bash bash-vid.sh [--fast]' 'Tekstowy pokaz poleceń Bash. Nie wymaga internetu ani dodatkowych pakietów.'; exit 0 ;;
  *) printf 'Nieznana opcja: %s\n' "$1" >&2; exit 2 ;;
esac
frame() {
  printf '\n%s\n' '----------------------------------------'
  printf '%s\n' "$1"
  printf '%s\n' '----------------------------------------'
  printf '%s\n' "$2"
  if [[ $delay != 0 ]]; then sleep "$delay"; fi
}
frame 'BASH VID | 1/5: katalog roboczy' 'pwd                 # pokaż katalog'
frame 'BASH VID | 2/5: pliki' 'ls -la              # lista plików (tylko przykład)'
frame 'BASH VID | 3/5: zmienne' 'imie="Ala"; echo "$imie"'
frame 'BASH VID | 4/5: pętla' 'for n in 1 2 3; do echo "$n"; done'
frame 'BASH VID | 5/5: warunek' 'if [[ -f plik.txt ]]; then echo "Jest"; fi'
printf '\nKoniec pokazu. Polecenia są tylko wyświetlane, nie są wykonywane.\n'
