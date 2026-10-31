# self

Dwujęzyczna witryna naukowa i dydaktyczna Mateusza Pomianka.

- [Strona główna](https://matpomgit.github.io/self/)
- [Wersja angielska](https://matpomgit.github.io/self/en/)
- [Materiały dla studentów](https://matpomgit.github.io/self/materials/)
- [Struktura repozytorium](docs/STRUCTURE.md)

## Wersje językowe w Zensical

Zensical buduje wersję polską pod `/self/`
oraz angielską pod `/self/en/`. Przełącznik języka znajduje się w prawym
górnym rogu nagłówka. Zmiana języka otwiera odpowiednik aktualnej podstrony.
Nawigacja, wyszukiwanie i opisy są dostępne w obu językach. Tytuły publikacji
zachowują oryginalne brzmienie. Materiały dydaktyczne pozostają w języku źródłowym.

Źródła stron znajdują się w `website/pl/` i `website/en/`.
Pliki odpowiadających sobie stron muszą mieć takie same nazwy.
`zensical.toml` określa wspólną konfigurację, polską nawigację i nowoczesny motyw.
Skrypt budowania ustawia język i angielską nawigację dla drugiego przebiegu.

Projekty i publikacje są przygotowywane przed budowaniem przez
`scripts/site_data.py` z danych w `docs/data/`. Dane bibliograficzne,
postępy i docelowe czasopisma mają jedno źródło w istniejących plikach JSON.
`projects.en.json` zawiera angielskie opisy projektów, wiązane z polskimi tytułami przez `sourceTitle` (kolejność wpisów nie ma znaczenia);
`in-progress.en.json` zawiera tłumaczenia opisów i kolejnych kroków,
powiązane z identyfikatorami manuskryptów.

## Budowanie i sprawdzanie

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -r requirements-docs.txt
python -m unittest discover -s tests -v
bash tests/theme_switcher_static_check.sh
python scripts/build_site.py
python -m http.server 8000 --directory site
```

Otwórz `http://localhost:8000/`. Do lokalnego podglądu pod docelowym prefiksem
`/self/` udostępnij katalog `site/` pod tą ścieżką. Odnośniki do materiałów
oraz portretu używają publicznego prefiksu `/self/`.

Używaj `scripts/build_site.py` do przygotowania publikacji. Skrypt przygotowuje kompletną treść obu języków w katalogu tymczasowym,
wykonuje dwa przebiegi `zensical build --strict` i kopiuje materiały
oraz zasoby do katalogu roboczego obok wyniku. Poprzedni katalog `site/`
pozostaje nienaruszony, jeżeli budowanie lub kopiowanie zakończy się błędem.
Podmiana następuje dopiero po przygotowaniu pełnego zestawu plików.
Skrypt nie nadpisuje istniejącego katalogu bez znacznika `.nojekyll`. Nie korzysta z hooków ani pluginów MkDocs.
Nie używaj samego `zensical build` do publikacji, ponieważ pomija on przygotowanie
portfolio, wersji angielskiej i katalogu `materials/`.
Testy Zensical wymagają zależności z `requirements-docs.txt`; bez nich są pomijane.

Przełącznik języka korzysta z szablonu `website/overrides/partials/alternate.html`.
Odnośniki prowadzą do odpowiedników bieżącej strony bez JavaScriptu.
Po aktualizacji Zensical sprawdź ten szablon i uruchom testy regresyjne.

## Publikowanie

Workflow `.github/workflows/docs.yml` sprawdza PR i zmiany na `main`,
a następnie przygotowuje artefakt Pages. Publikacja następuje wyłącznie
po ręcznym uruchomieniu tego workflow na `main` (`workflow_dispatch`).
GitHub Pages musi mieć ustawione źródło **GitHub Actions**.
Przebiegi PR i zwykłe wysłanie commitu nie publikują witryny.

## Zachowane zasoby i adresy

`materials/` pozostaje jedynym katalogiem aktualnych materiałów dla studentów.
Skrypt budowania kopiuje pliki bez modyfikacji, dzięki czemu istniejące adresy
PDF, HTML i plików do pobrania pozostają poprawne.

Dotychczasowy `index.html` z kołem kategorii pozostaje w repozytorium jako
źródło zachowanej wersji HTML. Po publikacji Zensical jest dostępny pod
`/self/legacy.html`. Wykorzystuje zdjęcie `docs/images/self.png`, dane JSON
w `docs/data/` i własny przełącznik motywu. Starsze wersje znajdują się
w `docs/archive/`. Plików materiałów i historycznych źródeł nie usuwaj
bez zweryfikowanego odpowiednika.

Aktualna wersja witryny Zensical: **1.3.0**. Zachowana strona HTML: **1.2.10**.
