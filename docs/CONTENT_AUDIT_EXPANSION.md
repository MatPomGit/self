# Rozszerzenie audytu podobieństwa materiałów dydaktycznych

**Wersja:** 1.0.0 · **Data:** 2026-11-12 · **Powiązanie:** [Issue #138](https://github.com/MatPomGit/self/issues/138)

## Zakres i zasada bezpieczeństwa

Wstępna inwentaryzacja rozszerza dotychczasowy zakres `files/inne/analizy/` o katalogi dydaktyczne. Wynik **nie stanowi analizy semantycznej** ani zgody na usunięcie dokumentów. `files/ignored/` jest pomijany i nie trafia na Pages.

Uruchomienie lokalne, bez zależności od zewnętrznych usług:

```bash
python scripts/audit_material_variants.py --root files --output reports/content-audit/material-variants.json
python -m pytest tests/test_material_variant_audit.py -q
```

Raport powstaje poza `files/`; zawiera pary odpowiadające wspólnemu rdzeniowi nazwy (PDF–DOCX, PDF–TEX, PDF–PPTX) oraz siedem możliwych par dwóch serii XR.

## Priorytety merytorycznego porównania

| Priorytet | Zakres | Hipoteza do sprawdzenia | Warunek dopuszczenia scalenia |
| --- | --- | --- | --- |
| P1 | `wirr_lab_01..07.pdf` ↔ `Lab_1..7_XR.pdf` | Dwie serie ćwiczeń o zbliżonej numeracji | Potwierdzona zgodność celów, poleceń i rezultatów; dodatkowe ćwiczenia mogą być celowo niezależne |
| P1 | `isaac_sim.docx`, `isaac_sim_pojecia.pdf`, raport `isaac_lab` | Komplementarne opracowania ekosystemu Isaac | Macierz unikalnych pojęć, metod i tabel przed rozszerzeniem dokumentu kanonicznego |
| P1 | `tele_ndd.docx` ↔ `teled_ndd.docx` | Wspólne badania diagnostyki ADHD/ASD | Rozdzielenie próby 70/30 i wyników 5-fold CV, bez utożsamiania modeli |
| P2 | `analiza-eeg/lab1..6_*.tex` ↔ odpowiadające PDF | Eksporty tego samego materiału | Weryfikacja kompletności i wersji PDF, nie scalanie ćwiczeń między sobą |
| P2 | `psychologia-poznawcza/psych_pozn_lab1..6` PDF/DOCX | Warianty formatowe | Zgodność treści i tabel |
| P2 | `diagnoza-psychologiczna/diagnoza_lab1..5` PDF/DOCX | Warianty formatowe | Zgodność poleceń i kryteriów oceniania |
| P2 | `nawigacja-robotow-humanoidalnych/robo_w01..10` PDF/PPTX | Źródło prezentacji i eksport | Zgodność slajdów, rysunków i treści |
| P3 | `EEG_BIDS_Psychofizjologia_2026.pdf` ↔ `Galea_EEG_neuroXR.pdf` | Wspólne zagadnienia EEG, lecz różne cele | Domyślnie odnośniki krzyżowe, nie scalanie wykładów |

## Następny poziom audytu

1. Dla wszystkich par sprawdzić **hash, liczbę stron/slajdów, liczbę słów, strukturę nagłówków i zakres tematów**; dla PDF/TEX/PPTX rozwinąć ekstraktor po odrębnym teście bezpieczeństwa.
2. Obliczać podobieństwo leksykalne i semantyczne **po wyłączeniu bibliografii**, wykazując osobno wspólne fragmenty i informacje unikalne.
3. Twierdzenia naukowe, parametry i wyniki weryfikować na poziomie źródeł pierwotnych.
4. Decyzje `MERGE`, `KEEP_SEPARATE`, `SUPERSEDE` przydzielać tylko po przeglądzie materiału dowodowego. Nazwa lub numer ćwiczenia nigdy nie wystarczają.
5. Dopiero zaakceptowany dokument kanoniczny publikować jako DOCX/PDF, przenosząc zastąpione oryginały do `files/ignored/` i kontrolując wszystkie stare URL oraz filtr publikacji.

### Kryterium zakończenia

Każdy kandydat ma jawne źródła, wersje, metryki i mapę zachowanych treści. Brak odpowiedniej ekstrakcji oznacza `EXTRACTION_INCOMPLETE`, nie brak podobieństwa.

## Weryfikacja pełnej treści par XR (etap 2)

`scripts/audit_xr_pairs.py` wykorzystuje istniejący ekstraktor `audit_content_overlap.py` i porównuje siedem numerowanych par dokumentów PDF. Dla każdej pary raportuje SHA-256, liczbę słów, strony, pokrycie 5-gramów w obu kierunkach, Jaccard, dopasowane strony i przykładowe wspólne fragmenty z lokalizacjami. Gdy ekstrakcja jest niekompletna, wynik ma status `EXTRACTION_INCOMPLETE`, a nie `LOW_LEXICAL_OVERLAP`.

```bash
python scripts/audit_xr_pairs.py --root files --output-dir reports/content-audit/xr
python -m pytest tests/test_material_variant_audit.py tests/test_xr_pair_audit.py -q
```

Zapisuje `xr_pairs.json` i `xr_pairs.md`, zawsze poza publikowanym drzewem. GitHub Actions `material-variant-audit.yml` generuje tabelę podsumowania oraz zachowuje pełny wynik jako artefakt przez 7 dni. **Metryki tekstowe nie rozstrzygają zgodności celów dydaktycznych, ilustracji ani kryteriów oceny.** Przed archiwizacją konieczna jest kontrola oryginalnych PDF i wszystkich unikalnych poleceń.


## Wynik pierwszego wykonania (2026-11-12)

**Potwierdzony przebieg CI:** [Materials variant audit #8](https://github.com/MatPomGit/self/actions/runs/43262646284), wynik `success`, commit `ef2731c9b884027408f85ae8f9882575f917a6a8`. Testy: **7 passed**. Inwentarz: **285 obsługiwanych plików, 74 pary wariantów formatowych, 7 par serii WiRR/XR**. Artefakt `material-variant-inventory` (retencja 7 dni) zawiera pełny JSON i raport stron.

| Nr | WiRR: liczba słów | Dodatkowe XR: liczba słów | Pokrycie 5-gramów krótszego |
| --- | ---: | ---: | ---: |
| 01 | 1613 | 3442 | 0.0% |
| 02 | 1498 | 2958 | 0.0% |
| 03 | 1612 | 2430 | 0.0% |
| 04 | 1590 | 2250 | 0.0% |
| 05 | 1573 | 2143 | 0.0% |
| 06 | 1539 | 2300 | 0.0% |
| 07 | 1250 | 2341 | 0.1% |

**Werdykt do planu:** `KEEP_SEPARATE_PENDING_SEMANTIC_REVIEW`. Brak dowodu tekstowego na duplikaty między obiema seriami; niskie pokrycie nie wykazuje jednak różnicy celów dydaktycznych. Nie przenosić do `files/ignored/`. W kolejnej iteracji priorytet mają 74 pary wariantów formatowych i raporty Isaac/NDD, gdzie istnieje większe prawdopodobieństwo redundancji rzeczywistych wersji.

Uwaga o testach: CI zaliczył siedem testów, ale podczas importu istniejącego analizatora emitowane były `SyntaxWarning` o nieprawidłowej sekwencji `\\`` w literale Python. Ostrzeżenia nie unieważniają wyników, lecz powinny zostać poprawione oddzielnie w źródłowym analizatorze.
