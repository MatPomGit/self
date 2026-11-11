# self

Osobista strona naukowa i dydaktyczna publikowana przez GitHub Pages.

**Strona:** [matpom.pl](https://matpom.pl/) · [English](https://matpom.pl/?lang=en) · [Pliki dla studentów](https://matpom.pl/files/)

## Struktura

| Ścieżka | Przeznaczenie |
| --- | --- |
| `index.html` | Strona główna (PL/EN, motyw jasny/ciemny) |
| `files/` | Publiczne materiały: wykłady, laboratoria, prezentacje i dane demonstracyjne |
| `files/index.html` | Katalog materiałów; indeks uzupełniany w CI |
| `docs/assets/` | Style i skrypty strony |
| `docs/data/` | Opisy badań, projektów, publikacji i manuskryptów |
| `docs/images/` | Grafiki i portret |
| `docs/archive/` | Archiwalne wersje strony |
| `scripts/` | Przygotowanie i kontrola materiałów |
| `tests/` | Testy regresyjne Python/JavaScript |
| `.github/workflows/restore-original-pages.yml` | Walidacja i publikacja GitHub Pages |

Opis katalogów i mechanizmu indeksowania: [docs/STRUCTURE.md](docs/STRUCTURE.md).

## Publikacja

Po zmianie gałęzi `main` workflow **Publish original self website**:

1. sprawdza lokalne linki oraz integralność PDF, DOCX, PPTX i ODP;
2. uzgadnia indeks `files/index.html` i rozpoznaje format dokumentów;
3. uruchamia testy Python i JavaScript;
4. publikuje zatwierdzony artefakt do GitHub Pages (bez ponownego budowania).

Weryfikacja lokalna (Python 3.12+, Node.js):

```bash
python -m pip install "pypdf>=5,<7"
python scripts/preflight_materials.py --check
python scripts/sync_materials.py --check
python scripts/classify_materials.py --check
python -m unittest discover -s tests -v
node tests/test_language.js
node tests/test_materials_view.js
node tests/test_materials_layout.js
bash tests/theme_switcher_static_check.sh
```

Przed sprawdzeniem na świeżym checkout można odtworzyć indeks i klasyfikację:

```bash
python scripts/sync_materials.py --write
python scripts/classify_materials.py --write
```

## Dane i uprawnienia

**Uwaga:** `files/` jest katalogiem publicznym. Udostępnione w nim dokumenty, pliki CSV i XLSX są dostępne bez uwierzytelnienia. Zawiera także przykładowe nagrania EEG pochodzące z pomiarów autora. Przed dodaniem nowych plików należy sprawdzić ich zawartość, prywatność i prawa do rozpowszechniania.

## Migracja adresów

Katalog `materials/` zastąpiono `files/`. Dla starego adresu `/materials/` pozostawiono stronę przekierowującą. Starsze bezpośrednie adresy dokumentów `/materials/...` mają przekierowanie przeglądarkowe z `404.html`, nie odpowiedź HTTP 301; zewnętrzne linki warto zaktualizować na `https://matpom.pl/files/...`.

Domena i HTTPS są skonfigurowane w **Settings → Pages** repozytorium, a rekordy DNS u rejestratora. Do wdrożenia nie jest potrzebny hosting WWW.
