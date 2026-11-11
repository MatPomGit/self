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
