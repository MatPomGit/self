# self

Witryna naukowa i dydaktyczna publikowana przez GitHub Pages.

- [Strona główna](https://matpomgit.github.io/self/)
- [English version](https://matpomgit.github.io/self/?lang=en)
- [Materiały dla studentów](https://matpomgit.github.io/self/materials/)
- [Struktura repozytorium](docs/STRUCTURE.md)

## Zasady publikacji

Jedynym katalogiem aktualnych materiałów udostępnianych studentom jest `materials/`.
Punktem wejścia pozostaje `materials/index.html`, prosta strona HTML z listami linków
bez frameworków. `scripts/sync_materials.py` podczas CI automatycznie
wyszukuje nowe pliki w `materials/`, aktualizuje przeniesione odnośniki
oraz uzupełnia indeks przed testami i publikacją Pages. Skrypt domyślnie pokazuje najnowsze wersje PDF;
trzy kliknięcia przycisku PDF/Wszystkie przełączają pełną listę. Bez JavaScriptu
pełna lista pozostaje dostępna. Pozostałe strony przedmiotów znajdują się w
`materials/<przedmiot>/index.html`;

## Opis osoby i badań

Opis w sekcji „Badania” jest przechowywany w jednym pliku:
[`docs/data/about.json`](docs/data/about.json). Obie wersje językowe
(`pl` i `en`) zawierają tytuł (`title`) oraz pełny,
siedmioakapitowy opis (`paragraphs`) prowadzący spójną narrację od ciekawości świata do pracy badawczej.
Strona ładuje tę treść automatycznie, bez powielania tekstu w
`index.html` lub w słowniku tłumaczeń. Edycja opisu wymaga zmiany
wyłącznie tego pliku. Ładowanie i obsługę błędów sprawdza
`node tests/test_about.js`.

## Wersje językowe strony głównej

Przełącznik `PL / EN` znajduje się w prawym górnym rogu oryginalnej
strony z kołem kategorii. Wersja polska jest domyślna; angielska jest
dostępna pod `/?lang=en` (w GitHub Pages: `/self/?lang=en`).
Przełączanie zachowuje aktualnie otwartą kategorię przez fragment URL.
Obie wersje wykorzystują ten sam `index.html` i tę samą geometrię koła.

Angielskie etykiety i opisy znajdują się w `docs/assets/js/site-i18n.js`,
a teksty projektów oraz manuskryptów w `docs/data/*.en.json`.
Tytuły publikacji i metadane bibliograficzne nie są automatycznie tłumaczone.
Materiały dydaktyczne zachowują oryginalny język i adresy.
Bez JavaScriptu pozostaje dostępna polska strona statyczna.

Walidacja: `python -m unittest discover -s tests -v` oraz
`node tests/test_language.js`. Publikacja GitHub Pages sprawdza oba języki
bez zastępowania oryginalnego `index.html` przez generator.

## Nowa strona główna

`index.html` wykorzystuje układ z kołem kategorii, oparty na projekcie HTML
przekazanym 30.10.2026. Koło skaluje się do wysokości i szerokości okna;
w widoku startowym nagłówek, koło i stopka mieszczą się na typowym ekranie
desktopowym bez przewijania. Na urządzeniach wąskich priorytetem jest
czytelność, więc przy zbyt małej wysokości dopuszczalne jest przewijanie.

Dodatkowe odnośniki segmentów są dostępne po najechaniu lub ustawieniu
fokusu klawiatury; zamknięcie po opuszczeniu grupy ma 650 ms opóźnienia.
Podtytuły w obrębie segmentów pojawiają się tylko po najechaniu na sam
segment lub ustawieniu na nim fokusu.

Poprzedni `index.html` zachowano w `docs/archive/index_previous_20261030.html`.

Portret na stronie głównej korzysta z `docs/images/self.png` i ma okrągłą ramę CSS.
Plik jest zasobem strony osobistej, nie należy go przenosić do `materials/`.

## Zasoby witryny

Zasoby CSS, JS i vendor znajdują się w `docs/assets/`, zdjęcia i grafiki
w `docs/images/`, a archiwalne strony w `docs/archive/`. Dokumentacja
struktury znajduje się w `docs/STRUCTURE.md`. Główne pliki HTML pozostają
w katalogu głównym, ponieważ obsługują publiczne adresy GitHub Pages.
Materiały dydaktyczne są odrębnie w `materials/`.

## Podstrony

Strony publikacji i projektów są utrzymywane w `subpages/`.
Podstrony stosują `<base href="../">`, aby odwołania do `docs/assets/`,
strony głównej i materiałów były poprawne również z głębszej ścieżki.
Na stronie startowej stopka ma czcionkę 0,43 rem (50% pierwotnych 0,86 rem).
Kolumna tytułu na ekranach szerokich otrzymała udział 0,85 fr zamiast 0,55 fr.

---
`prefers-color-scheme`, co strona główna. Wybór pozostaje zachowany przy
przejściu między stronami. Lista plików nie została zmieniona. Skrypty strony materiałów obsługują
motyw oraz dwustopniowy widok spisu (PDF / wszystkie pliki).

## Odporność CI na niespójności materiałów

Workflow GitHub Pages sprawdza odnośniki w źródłowym HTML, wykonuje **preflight dokumentów**
i **deterministyczne uzgodnienie indeksu**. Zweryfikowany katalog jest pakowany
jeden raz, a zadanie publikacji wdraża ten sam artefakt bez ponownego budowania.
Dodatkowy workflow testu motywu jest uruchamiany tylko ręcznie:


- `python scripts/preflight_materials.py --check` jest trybem lokalnym tylko do
  odczytu; zwraca błąd, gdy wykryje uszkodzony PDF, PPTX, DOCX lub ODP.
- W GitHub Actions `--quarantine` przenosi niepoprawne dokumenty **wyłącznie
  w efemerycznym katalogu runnera** poza `materials/` i publikuje ostrzeżenie
  oraz podsumowanie. Nie wykonuje commitów ani usuwania plików z repozytorium.
  Opublikowany indeks i artefakt Pages pomijają te pliki.
- `python scripts/sync_materials.py --write --repair-missing` usuwa z roboczej
  kopii indeksu tylko proste odnośniki do nieistniejących plików, po próbie
  jednoznacznego odnalezienia przeniesionej wersji. Wątpliwe dopasowania,
  niebezpieczne linki i błędy strukturalne nadal zatrzymują CI.
- `--check` pozostaje rygorystyczne. Testy regresyjne sprawdzają
  idempotentność regeneracji indeksu oraz obsługę uszkodzonych plików.

Ostrzeżenia można znaleźć w logach i `GITHUB_STEP_SUMMARY`. Jeśli dokument
zostanie przywrócony w kolejnym commicie, następny przebieg CI ponownie go
zaindeksuje, ponieważ źródłowe dane pozostają nienaruszone.
