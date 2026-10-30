#!/usr/bin/env bash
# Bash GAME: ćwiczenie w instrukcjach warunkowych i pętlach.
# Uruchom: bash bash-game.sh
set -euo pipefail
if [[ ${1:-} == -h || ${1:-} == --help ]]; then
  printf '%s\n' 'Użycie: bash bash-game.sh' 'Gra: odgadnij liczbę od 1 do 20 w maksymalnie 6 próbach.'
  exit 0
fi
if (( $# > 0 )); then printf 'Nieznana opcja. Użyj --help.\n' >&2; exit 2; fi
secret=$((RANDOM % 20 + 1))
printf 'BASH GAME | Zgadnij liczbę 1..20 (6 prób).\n'
for ((attempt=1; attempt<=6; attempt++)); do
  if ! IFS= read -r -p "Próba ${attempt}/6 > " guess; then
    printf '\nPrzerwano: koniec wejścia.\n'
    exit 0
  fi
  if [[ ! $guess =~ ^[0-9]{1,2}$ ]] || (( 10#$guess < 1 || 10#$guess > 20 )); then
    printf 'Wpisz liczbę całkowitą od 1 do 20.\n'
    continue
  fi
  if (( 10#$guess == secret )); then
    printf 'Wygrana w %d próbach!\n' "$attempt"
    exit 0
  elif (( 10#$guess < secret )); then
    printf 'Za mało.\n'
  else
    printf 'Za dużo.\n'
  fi
done
printf 'Koniec gry. Liczba to %d.\n' "$secret"
