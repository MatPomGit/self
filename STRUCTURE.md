# Struktura repozytorium self

Witryna statyczna publikowana przez GitHub Pages. Zachowujemy publiczne adresy, dlatego pliki stron HTML pozostają obecnie w katalogu głównym.

| Ścieżka | Rola |
| --- | --- |
| `index.html`, `*.html` | Publiczne strony, zachowane adresy URL |
| `assets/` | Zasoby biblioteki; docelowo także CSS, JavaScript i biblioteki vendor |
| `archive/` | Historyczne, niepublikowane wersje stron (do referencji) |
| `docs/` | Dokumentacja i grafiki |
| `downloads/` | Publiczne pliki do pobrania, w tym `bash/` i `wirr/` |
| `lectures/wirr/` | Wykłady HTML |
| `f/NN/`, `p/NN/`, `h/NN/` | Wygenerowane krótkie adresy; nie kasować i nie przenosić |
| `library/`, `wirr/` | Strony katalogowe |
| `tools/`, `tests/` | Generator i testy |
| `.github/` | Automatyzacja GitHub |

## Zasady porządkowania

1. Nie usuwać publicznych stron ani aliasów. Najpierw zapewnić zgodne przekierowania i sprawdzić odwołania.
2. Nowe zasoby CSS i JavaScript dodawać w `assets/css/` i `assets/js/`, biblioteki zewnętrzne w `assets/vendor/`.
3. Pliki do pobrania publikować w `downloads/`, katalog aktualizować w `assets/library.json`, następnie uruchamiać `python3 tools/build_library.py`.
4. Nie commitować plików roboczych takich jak `nohup.out`, logów, cache czy plików tymczasowych.
5. Walidować zmiany poleceniem `python3 tools/build_library.py --check` oraz `python3 -m unittest discover -s tests`.

Historyczne `index_old.html` zachowano jako kopię referencyjną w `archive/` ze względu na istniejący publiczny adres starej strony. Nie jest to nowy punkt wejścia.
