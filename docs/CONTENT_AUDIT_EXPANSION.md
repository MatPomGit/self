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

## Drugi przebieg: zgodność PDF–DOCX

`scripts/audit_format_variants.py` wykonuje tekstową ekstrakcję każdej wykrytej pary PDF–DOCX i porównuje pokrycie 5-gramów. Stosuje statusy `TEXT_VARIANTS_SIMILAR` (co najmniej 75%), `FORMAT_DIFFERENCE_REVIEW` (25–75%), `FORMAT_MISMATCH_CANDIDATE` (poniżej 25%), `INSUFFICIENT_TEXT`, `EXTRACTION_INCOMPLETE` i `MISSING_INPUT`. Są to **kategorie przesiewowe**, nie wynik recenzji merytorycznej.

```bash
python scripts/audit_format_variants.py --root files --output-dir reports/content-audit/formats
python -m pytest tests/test_format_variant_audit.py -q
```

Wyniki `format_comparison.json` i `format_comparison.md` są zachowywane w artefakcie CI. Nie obejmują jeszcze porównania PDF–PPTX ani PDF–TEX; te formaty są rejestrowane w inwentarzu, ale nie należy na tej podstawie stwierdzać zgodności ich zawartości. Ponadto brak wyniku tekstowego nie świadczy o braku treści na stronach z obrazami.

## Wynik porównania rzeczywistego tekstu 47 par PDF–DOCX

**Źródło:** [CI Materials variant audit #13](https://github.com/MatPomGit/self/actions/runs/43263585191), `success`, 10 testów PASS, artefakt `material-variant-inventory`, z weryfikowalnymi SHA-256 źródeł (retencja 7 dni).

- `TEXT_VARIANTS_SIMILAR`: **45/47** par z pokryciem co najmniej 75%. Wskaźnik dotyczy 5-gramów krótszego dokumentu; nie uprawnia automatycznie do usunięcia wariantu źródłowego.
- `FORMAT_DIFFERENCE_REVIEW`: **1/47**, `inne/analizy/Wpływ robotów na pracę człowieka.docx` vs `.pdf`: pokrycie krótszego **73,30%**, odpowiednio **2694 i 2943 słowa**; konieczna kontrola różnic, tabel i rysunków przed ustaleniem jednej wersji kanonicznej.
- `FORMAT_MISMATCH_CANDIDATE`: **1/47**, `inne/analizy/Przewijanie slajdow gestem.docx` vs `.pdf`: **2,73%**, odpowiednio **5167 i 2993 słowa**. Wspólne fragmenty świadectw dotyczą przede wszystkim adresów MediaPipe w bibliografii. **Dwa niezależne opracowania; nie nadpisywać ani nie archiwizować jednego jako eksportu drugiego.**
- Pozostałe **27 z 74** par inwentaryzowanych formatów nie należy do PDF–DOCX; wymagają porównania PDF–TEX lub PDF–PPTX innym ekstraktorem.

Wśród 45 wysoce podobnych par najniższe pokrycie występuje dla `robotyka_afektywna` (**85,17%**), `MPC` (**85,32%**), `Mediapipe` (**85,39%**), `Mapowanie emocji` (**85,65%**) i `Silniki_XR` (**85,65%**). Warto zacząć od kontroli dodatkowych akapitów i rysunków w tych pięciu parach; **nie są to potwierdzone błędy eksportu**.

**Kolejność decyzji redakcyjnych:** najpierw rozdzielenie dwóch różnych opracowań „Przewijanie slajdow gestem” (odrębne tytuły/linki bez utraty adresów), następnie sprawdzenie „Wpływ robotów na pracę człowieka”, w dalszej kolejności inspekcja pięciu najniżej dopasowanych par z kategorii ≥75%. Każde przeniesienie do `files/ignored/` wymaga zachowania kompletnych treści oraz sprawdzenia odnośników.

## Etap 3 – porównanie 21 par PDF–PPTX

Dodano `scripts/audit_slide_variants.py`: bezpieczna ekstrakcja widocznego tekstu slajdów z archiwum PPTX (limity wielkości/kompresji XML, brak wykonywania kodu) oraz porównanie z tekstem PDF. Wynik zawiera liczby słów, pokrycie 5-gramów w obu kierunkach, dopasowane strony i slajdy, SHA-256, status ekstrakcji i klasyfikację wymagającą dalszej oceny. Workflow przechowuje raport `slides_comparison.json` i `slides_comparison.md` w artefakcie, nie na stronie publicznej.

```bash
python scripts/audit_slide_variants.py --root files --output-dir reports/content-audit/slides
python -m pytest tests/test_slide_variant_audit.py -q
```

Porównanie tekstu slajdów nie wystarcza do stwierdzenia zgodności prezentacji: konieczna jest inspekcja grafiki, tabel, wzorów, animacji, notatek i liczby slajdów. Niska zgodność tekstu może wynikać z prezentacji silnie graficznej i nie jest podstawą do usuwania.

## Etap 4 – porównanie sześciu par PDF–TEX z laboratorium EEG

Dodano `scripts/audit_tex_variants.py` jako **read-only** analizator ciała dokumentu LaTeX. Skrypt ignoruje preambułę i komentarze, nie wykonuje kodu TeX, nie uruchamia kompilatora i nie pobiera zależności. Porównuje wyodrębnione przybliżone słowa z odpowiadającym plikiem PDF. Wynik obejmuje SHA-256, liczbę słów, pokrycie 5-gramów, status oraz fragmenty dowodowe.

```bash
python scripts/audit_tex_variants.py --root files --output-dir reports/content-audit/tex
python -m pytest tests/test_tex_variant_audit.py -q
```

Raport `tex_comparison.json` oraz `tex_comparison.md` jest zapisywany w artefakcie CI. **Ekstrakcja jest stratna**: makra, rozbudowane tabele, wzory matematyczne, pliki `\\input`, grafiki i inne struktury wymagają kontroli po renderowaniu. Różnice w tej metryce nie dowodzą niezgodności źródła i PDF.

**Stan:** na etapie wprowadzania zmiany workflow dla PDF–PPTX był w toku; nowe wyniki PDF–TEX wymagają ukończonego przebiegu CI i sprawdzenia raportów. Bez automatycznej archiwizacji.
