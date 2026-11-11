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

## Faza 2 — embeddingi wielojęzyczne offline (opcjonalne wykonanie lokalne)

Nowy skrypt `scripts/audit_semantic_overlap.py` przeszukuje wszystkie
**40 dokumentów logicznych**, dzieląc je na oznaczone stroną/akapitem
fragmenty i szukając semantycznie podobnych wypowiedzi.

W przeciwieństwie do pilotażu leksykalnego wykonanie tej fazy **wymaga
rzeczywistego, już pobranego modelu embeddingowego**. Ścieżka
`--model-dir` musi wskazywać folder modelu na komputerze wykonującym
analizę. Kod nigdy nie próbuje pobierać modelu ani wysyłać dokumentów
do API. Ustawia `HF_HUB_OFFLINE=1`, `TRANSFORMERS_OFFLINE=1`,
`trust_remote_code=False` i `local_files_only=True`.

Wymagane lokalnie: `numpy>=1.26,<3`, `sentence-transformers`,
`pypdf>=5,<7`. W pełni odseparowane od CI publikacji strony.
Przykładowo na komputerze mającym już zainstalowany model wielojęzyczny:

```bash
python scripts/audit_semantic_overlap.py \
  --scope files/inne/analizy \
  --model-dir /opt/models/paraphrase-multilingual-MiniLM-L12-v2 \
  --output-dir reports/content-audit/semantic \
  --threshold 0.76
```

**Wyniki:** `semantic.json` i `semantic.md`: ranking dokumentów,
zgodne semantycznie fragmenty z lokalizacją, SHA-256 źródeł,
parametry modelu i status `UNVERIFIED`.
Próg 0.76 jest wstępny i **nie został skalibrowany na raportach**.

### Zestaw kontrolny

`tests/fixtures/semantic_pairs.json` zawiera 15 **syntetycznych** par:
dosłowne powtórzenia, parafrazy PL, parafrazy PL–EN, wspólną tematykę,
sprzeczne twierdzenia oraz dokumenty niezwiązane. Sprzeczność nie jest
równoważnością merytoryczną nawet wtedy, gdy embeddingi są podobne.

Po przygotowaniu modelu uruchom:

```bash
python scripts/evaluate_semantic_benchmark.py \
  --model-dir /opt/models/paraphrase-multilingual-MiniLM-L12-v2 \
  --output-dir reports/content-audit/semantic
```

Wynik `semantic_benchmark.json` zawiera macierz pomyłek,
precision, recall, F1 i balanced accuracy. To **test syntetyczny**,
a nie miarodajna walidacja na prawdziwych raportach.
Przed decyzją o konsolidacji konieczny jest niezależny, reprezentatywny
zbiór ludzkich ocen na fragmentach rzeczywistego korpusu.

### Interpretacja wyników

**Embedding wykrywa podobieństwo znaczeniowe, ale nie dowodzi tożsamości
hipotez, metod, wyników, jednostek miary ani zgodności liczbowej.**
Często podaje wysokie wyniki dla twierdzeń sprzecznych. Potencjalne
pokrycie jest kandydatem do weryfikacji, nigdy automatycznym
`MERGE` lub `SUPERSEDE`.

Model musi być pozyskany z wiarygodnego źródła i sprawdzony przed
instalacją. Skrypt nie wykonuje samodzielnie bootstrapu modelu;
CI testuje jedynie orkiestrację z kontrolowanym fałszywym encoderem,
**nie rzeczywiste wnioskowanie semantyczne**.

## Evidence-aware triage po uruchomieniu modelu

`scripts/triage_semantic_results.py` klasyfikuje zachowane w
`semantic.json` świadectwa podobieństwa:

- `BROAD_CONTENT_REUSE_CANDIDATE` – wiele dopasowanych fragmentów oraz
  dwukierunkowe pokrycie (wstępne ≥35% w obu dokumentach).
- `LOCAL_CONTENT_OVERLAP_CANDIDATE` – powtarzające się konkretne
  wypowiedzi, ale bez przesłanek do scalania całych raportów.
- `SHARED_BIBLIOGRAPHY_CANDIDATE` – wysokie wyniki dotyczą przede
  wszystkim wspólnych pozycji literatury i DOI.
- `SHARED_KEYWORDS_CANDIDATE` – wspólne słowa kluczowe, nie wyniki.
- `TOPIC_SIMILARITY_LOW_COVERAGE` – pokrewne zagadnienie lub nieliczne
  dopasowane fragmenty.

Dodatkowy flag `NUMERIC_CLAIM_REVIEW_REQUIRED` wyłapuje podobne
sformułowania zawierające wartości, progi lub jednostki. Nie dowodzi,
że podana liczba jest poprawna, identyczna lub wiarygodna.
Wyniki zapisane jako `semantic_triage.json` i
`semantic_triage.md` wraz z pozostałymi artefaktami eksperymentu.

```bash
python scripts/triage_semantic_results.py \
  --input reports/content-audit/semantic/semantic.json \
  --output-dir reports/content-audit/semantic
```

Klasyfikacja działa **tylko na zapisanych fragmentach dowodowych**;
jeżeli wykaz par został obcięty do top N, sumy klas odnoszą się
wyłącznie do zapisanych pozycji. Żaden wynik nie jest oceną
merytorycznej tożsamości wniosków. Przed usuwaniem lub łączeniem
raportów wymagana jest weryfikacja źródeł i twierdzeń.

**Doprecyzowanie po analizie wyników:** jeżeli większość najlepszych
świadectw dopasowania stanowią cytowania DOI i pozycje bibliografii,
para otrzymuje `BIBLIOGRAPHY_DOMINANT_CANDIDATE`, nawet gdy wśród
top przykładów występuje także fragment narracji. Dla słów kluczowych
przy bardzo małym pokryciu obydwu źródeł stosowana jest analogiczna
ochrona. Wartości procentowe, jednostki i progi są oznaczane jako
wymagające sprawdzenia, a nie automatycznie uznawane za zgodne.

## Faza 3 — weryfikacja konkretnych twierdzeń naukowych

Wyniki kontroli źródeł, status korekty interpretacji EAR i liczb 84%/86%
dla ADHD/ASD oraz wymagane dane źródłowe opisuje
[`docs/CONTENT_AUDIT_CLAIMS.md`](CONTENT_AUDIT_CLAIMS.md).

`scripts/audit_repeated_claims.py` automatycznie odczytuje realne
dokumenty i zapisuje świadectwa dla par EAR i RF ADHD/ASD (plik,
SHA-256, lokalizacja, fragment). Wyszukuje również potencjalnie
odrębne sekcje oraz wiersze tabel w parze dwóch raportów
o analizie afektywnej. Wyniki `claim_evidence.json` i
`claim_evidence.md` są artefaktami PR, a nie plikami publikowanymi
na stronie.

```bash
python scripts/audit_repeated_claims.py \
  --scope files/inne/analizy \
  --output-dir reports/content-audit/claims
```

Dla korekty wniosku rozdzielono trzy rodzaje dowodów:
(1) identyczność fragmentu w repozytorium, (2) zgodność liczb ze
źródłem pierwotnym i jego kontekstem walidacji oraz (3) kliniczną
zasadność interpretacji. Sam wynik embeddingów **nie zastępuje**
punktów (2) i (3). Nie wykonano automatycznych zmian w oryginalnych
DOCX/PDF.

### Kontrola artefaktów ekstrakcji PDF

Porównanie tabel przeprowadza się dwoma niezależnymi wskaźnikami:
pokryciem **uporządkowanych 5-gramów** i pokryciem **zbioru słów**.
Niska zgodność 5-gramów przy wysokiej zgodności słów może wskazywać
wyłącznie zmianę kolejności kolumn podczas ekstrakcji PDF.
Nie wolno interpretować jej automatycznie jako informacji unikalnej.
Fragmenty o wysokiej zgodności tekstowej (≥80% 5-gramów) nie są
raportowane na liście kandydatów do zachowania jako „odrębna treść”.
