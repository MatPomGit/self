# WiRR: publikacja wykładów (2026/27)

Strona dla studentów: `https://matpomgit.github.io/self/wirr/`

W tym repozytorium utrzymujemy wyłącznie materiały opublikowane w `self`.
Nie korzystamy z submodułów, importów, zewnętrznych linków do repozytoriów ani automatycznego pobierania źródeł z innych repozytoriów.

## Wykłady 1–7

| Wykład | Krótki PDF | Krótki HTML | Plik PDF docelowo | Plik HTML |
|---|---|---|---|---|
| 1 | `p/10/` | `h/10/` | `downloads/wirr/w01.pdf` | `lectures/wirr/w01.html` |
| 2 | `p/11/` | `h/11/` | `downloads/wirr/w02.pdf` | `lectures/wirr/w02.html` |
| 3 | `p/12/` | `h/12/` | `downloads/wirr/w03.pdf` | `lectures/wirr/w03.html` |
| 4 | `p/13/` | `h/13/` | `downloads/wirr/w04.pdf` | `lectures/wirr/w04.html` |
| 5 | `p/14/` | `h/14/` | `downloads/wirr/w05.pdf` | `lectures/wirr/w05.html` |
| 6 | `p/15/` | `h/15/` | `downloads/wirr/w06.pdf` | `lectures/wirr/w06.html` |
| 7 | `p/16/` | `h/16/` | `downloads/wirr/w07.pdf` | `lectures/wirr/w07.html` |

**Stan początkowy:** `p/10`–`p/16` mają status `planned`, czyli **nie zawierają PDF**. Ich adresy pokazują stosowny komunikat, bez przycisku pobierania nieistniejącego pliku. `h/10`–`h/16` mają status `draft` i wyświetlają szablony HTML, nie kompletne wykłady.

## Jak opublikować wykład

1. Umieść gotowy, publiczny PDF jako `downloads/wirr/wNN.pdf` (NN od 01 do 07). Nie używaj pliku zero-bajtowego ani pustej atrapowej prezentacji.
2. Uzupełnij odpowiedni `lectures/wirr/wNN.html` pełną treścią wykładu.
3. W `assets/library.json` zmień `status` z `planned` na `ready` przy odpowiednim PDF oraz z `draft` na `ready` przy HTML, **dopiero kiedy zawartość jest gotowa**.
4. Sprawdź `python3 tools/build_library.py --check` i `python3 -m unittest discover -s tests -p 'test_*.py'`.
5. Opublikuj zmiany w standardowym GitHub Pages `self`. Stałe krótkie adresy nie wymagają zmiany.

## Pliki Bash

| Nazwa do pobrania | Ścieżka w serwisie | Krótki adres |
|---|---|---|
| `bash-vid.sh` | `downloads/bash/bash-vid.sh` | `f/02/` |
| `bash-game.sh` | `downloads/bash/bash-game.sh` | `f/03/` |
| `bash-rpg` | `downloads/bash/bash-rpg` | `f/04/` |

To samodzielne, dydaktyczne programy demonstracyjne (nie importowane ze źródeł zewnętrznych). Uruchom w systemie obsługującym Bash: `bash pobrany-plik`. `bash-vid.sh --fast` przyspiesza pokaz; każda wersja obsługuje `--help`. Skrypty nie wykonują wpisanych przez studenta poleceń jako kodu, nie używają sieci ani nie instalują pakietów.

## Uwaga techniczna

Nie dodawaj zależności, URL-i ani automatów synchronizacji z innymi repozytoriami. Aktualizuj wyłącznie pliki znajdujące się wewnątrz `self`.
