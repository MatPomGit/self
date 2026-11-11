# Audyt redundancji treści — pilot

Zadanie: https://github.com/MatPomGit/self/issues/138

## Cel
Etap 0/1: odtwarzalna ekstrakcja i ranking kandydatów do porównania.
To nie jest analiza semantyczna ani automatyczna decyzja o scaleniu raportów.
Pliki źródłowe pozostają nienaruszone; wyniki trafiają wyłącznie do artefaktów audytu.

## Uruchomienie
Zależność: Python 3.12+, pypdf >= 5, < 7.

    python -m pip install 'pypdf>=5,<7'
    python scripts/audit_content_overlap.py --scope files/inne/analizy --output-dir /tmp/self-content-audit --top 20

## Metoda
- Każdy plik PDF/DOCX/ODT ma SHA-256 i jawny status ekstrakcji.
- Odpowiedniki o wspólnym rdzeniu nazwy grupowane jako dokument logiczny.
- PDF porównywany strona po stronie; DOCX/ODT akapit po akapicie.
- Wykrywanie: wspólne 5-gramy, Jaccard, TF-IDF cosine; cytowalne fragmenty 10 słów z lokalizacją.
- Dwie odrębne analizy: zgodność wersji formatowych i podobieństwo innych raportów.
- Werdykt to zawsze kandydat oznaczony UNVERIFIED; podobny temat nie oznacza duplikatu.
- Limity wejścia: 25 MB, 300 stron PDF, 700000 znaków. Brak odczytu tekstu to EXTRACTION_INCOMPLETE.
- Skrypt nie wykonuje kodu dokumentów, nie używa sieci, LLM ani API.

## Artefakty
- summary.md: raport z wykrytymi parami i lokalizacjami fragmentów.
- overlap.json: metryki, źródłowe SHA-256, statusy, identyfikatory i świadectwa tekstowe.
- Przechowywanie w artefakcie PR przez 7 dni, poza publikowanym katalogiem files/.

## Ograniczenia i następny etap
Wskazania to dowody leksykalne, nie ostateczna ocena merytoryczna.
Pilotaż nie obejmuje OCR, analizy wykresów ani sprawdzania naukowej poprawności twierdzeń.
Kolejne PR: ręcznie oznaczony benchmark, embeddingi lokalne, analiza twierdzeń, plan konsolidacji.
Przed zmianą lub usunięciem jakichkolwiek oryginałów wymagane osobne zatwierdzenie.

## Analiza fragmentów czterech par raportów

Szczegółowe porównanie wyodrębnia fragmenty o wysokim podobieństwie tekstowym
i **kandydatów** na fragmenty unikalne; każdy zapis zawiera stronę/akapit,
pozycję w tekście i fragment z oryginału. Metoda nie udowadnia unikalności
semantycznej ani nie ocenia prawdziwości twierdzeń.

    python scripts/audit_report_differences.py --scope files/inne/analizy --output-dir /tmp/self-content-audit

Raporty: `comparison.md` i `comparison.json`. Porównania obejmują:
- `Synteza Modeli multimodalnych.docx` ↔ `Zautomatyzowana_analiza_afektywna.pdf`,
- `Isaac Lab i bliźniaki cyfrowe.pdf` ↔ `Isaac_Lab.docx`,
- `Przewijanie slajdow gestem.docx` ↔ `Przewijanie slajdow gestem.pdf`,
- `Wpływ robotów na pracę człowieka.docx` ↔ `Wpływ robotów na pracę człowieka.pdf`.

Okna do 75 wyrazów, krok 55; podobieństwo: kosinus tokenów (0.72)
i Jaccard trójek znakowych (0.28); próg selekcji 0.64.
Wszystkie progi **służą triage** i wymagają walidacji. Brak tekstowego
dopasowania nie wyklucza parafrazy; raport może być przydatny z innego powodu.
Decyzje MERGE/SUPERSEDE wymagają późniejszej weryfikacji merytorycznej.

**Ochrona przed błędną klasyfikacją:** różne podziały PDF i DOCX na okna
mogą obniżyć liczbę dopasowanych fragmentów. `FORMAT_VERSION_MISMATCH_CANDIDATE`
wymaga dodatkowo niskiego pokrycia 5-gramów całego dokumentu (<25%).
Dane tabelaryczne i łamanie wyrazów nadal wymagają oględzin; liczby są
wskaźnikami do przeglądu, nie wynikiem walidacji semantycznej.

## Warianty o różnych treściach i ochrona danych

Dokumenty o tej samej nazwie są rozpatrywane jako jedno źródło **tylko
warunkowo**: jeśli oba warianty dają się odczytać i pokrycie ich 5-gramów
jest poniżej 25%, trafiają do **osobnych dokumentów logicznych**;
nadal widnieją we wspólnej grupie formatowej z etykietą
`FORMAT_VARIANTS_SPLIT_CANDIDATE`. Chroni to m.in. parę dotycząca
sterowania prezentacją przed utratą jednego z raportów w rankingu porównań.

Pliki publicznej strony nie są modyfikowane. Narzędzie odmówi zapisu
wyników w `files/`, `docs/`, `materials/` i `_site/`.
Duże, silnie skompresowane XML wewnątrz ODT/DOCX są odrzucane przed
dekompresją. Wszystkie klasyfikacje wymagają sprawdzenia treści.
