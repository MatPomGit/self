# Struktura repozytorium self

Witryna jest publikowana przez GitHub Pages. Materiały dla studentów mają wspólny katalog nadrzędny.

| Ścieżka | Rola |
| --- | --- |
| `index.html`, `publications.html`, `projects.html` | Strony ogólne serwisu |
| `materials/index.html` | Prosty, statyczny wykaz plików dla studentów |
| `materials/<przedmiot>/index.html` | Strony poszczególnych przedmiotów |
| `materials/bash/` | Pliki Bash do pobrania i strona Bash |
| `materials/wirr/` | Wykaz WiRR, szkice HTML i docelowe PDF |
| `materials/templates/` | Pliki pomocnicze do pobrania |
| `assets/` | Zasoby CSS i JavaScript, manifest biblioteki |
| `docs/`, `archive/` | Grafiki, dokumentacja i archiwum |
| `library/` | Publiczny katalog i wyszukiwarka zasobów |
| `f/NN/`, `p/NN/`, `h/NN/` | Wygenerowane, trwałe aliasy |
| `materials.html`, strony przedmiotów w katalogu głównym, `wirr/`, `lectures/` | Przekierowania do `materials/` |
| `tools/`, `tests/` | Generator aliasów i testy |
| `.github/` | Automatyzacja GitHub |

## Zasady porządkowania

1. Nowe lokalne pliki dla studentów umieszczaj wyłącznie w `materials/<przedmiot>/`.
2. Główny indeks `materials/index.html` zawiera wyłącznie istniejące, działające linki; zaplanowanych PDF nie udostępnia się jako plików.
3. Po przeniesieniu materiału aktualizuj `assets/library.json`, zachowując identyfikatory aliasów.
4. Nie kasuj starych przekierowań HTML. Starsze bezpośrednie adresy skryptów w `downloads/` wymagają aktualizacji na `materials/`.
5. Uruchamiaj `python3 tools/build_library.py --check` i `python3 -m unittest discover -s tests`.
