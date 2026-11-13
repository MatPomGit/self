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
| `docs/data/` | Dane badań, projektów i publikacji oraz `papers.md` |
| `docs/images/` | Grafiki i portret |
| `docs/archive/` | Archiwalne wersje strony |
| `scripts/` | Przygotowanie i kontrola materiałów |
| `tests/` | Testy regresyjne Python/JavaScript |
| `.github/workflows/restore-original-pages.yml` | Walidacja i publikacja GitHub Pages |

Opis katalogów i mechanizmu indeksowania: [docs/STRUCTURE.md](docs/STRUCTURE.md).


## Logotypy i szczegóły projektów

- Logotypy umieszczaj w `docs/assets/images/projects/` (SVG, PNG lub WebP, zalecany wariant 1:1, najlepiej przezroczyste tło).
- Szczegóły i logo edytuj w `docs/data/project-details.json`, pod kluczem identycznym z polskim `title` w `docs/data/projects.json`.
- Główne tytuły, daty i opisy: `docs/data/projects.json`; tłumaczenia tych pól: `docs/data/projects.en.json`.
- Bez istniejącego lub poprawnego pliku logo interfejs wyświetli znak typograficzny. CI zgłosi błąd przy nieistniejącej ścieżce zapisanej w JSON.
- Metadane nie są instrukcjami wewnętrznych agentów. Wszystkie wpisy trafią na **publiczną** stronę.

[Instrukcja redakcyjna projektów](docs/PROJECTS.md).

## Krótkie adresy PDF

Materiały PDF mają czytelne adresy do udostępniania. Przykłady:

- [`/files/ndp/lab04/`](https://matpom.pl/files/ndp/lab04/) – laboratorium 4 z Narzędzi dla programistów.
- [`/files/wirr/w07/`](https://matpom.pl/files/wirr/w07/) – wykład 7 z Wirtualnej i rozszerzonej rzeczywistości.
- `/files/pi/w03/` – wykład 3 z psychoinformatyki.

Adres z końcowym `/` otwiera stronę podglądu PDF z przyciskiem pobrania, dzięki czemu adres pozostaje krótki. Oryginalny PDF jest dostępny pod dotychczasową ścieżką. Skrypt `scripts/build_short_links.py` tworzy strony podglądu **w artefakcie GitHub Pages** i zamienia główne odnośniki PDF w katalogu na krótkie adresy. Nie kopiuje plików binarnych ani nie zmienia ich nazw. Powiązane wersje edytowalne są nadal dostępne w przyciskach formatów.

```bash
python scripts/build_short_links.py --site . --check
```

Po przygotowaniu katalogu `_site/`:

```bash
python scripts/build_short_links.py --site _site
```

## Publikacja

Po zmianie gałęzi `main` workflow **Publish original self website**:

1. sprawdza lokalne linki oraz integralność PDF, DOCX, PPTX i ODP;
2. uzgadnia indeks `files/index.html`, rozpoznaje formaty dokumentów i weryfikuje krótkie adresy PDF;
3. uruchamia testy Python i JavaScript;
4. buduje strony podglądu PDF w artefakcie i publikuje go do GitHub Pages (bez ponownego budowania w zadaniu deploy).

Weryfikacja lokalna (Python 3.12+, Node.js):

```bash
python -m pip install "pypdf>=5,<7"
python scripts/preflight_materials.py --check
python scripts/sync_materials.py --check
python scripts/classify_materials.py --check
python scripts/build_short_links.py --site . --check
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

Katalog `materials/` zastąpiono `files/`. Katalog `materials/` nie istnieje ani w repozytorium, ani w artefakcie publikacji. Zarówno dawny adres `/materials/`, jak i starsze bezpośrednie adresy dokumentów `/materials/...` obsługuje przekierowanie przeglądarkowe z `404.html`, nie odpowiedź HTTP 301; zewnętrzne linki warto zaktualizować na `https://matpom.pl/files/...`.

Domena i HTTPS są skonfigurowane w **Settings → Pages** repozytorium, a rekordy DNS u rejestratora. Do wdrożenia nie jest potrzebny hosting WWW.
