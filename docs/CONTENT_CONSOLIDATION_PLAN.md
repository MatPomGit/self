# Plan konsolidacji raportów w `files/inne/analizy/`

**Wersja:** 1.0.0 · **Data:** 2026-11-12 · **Zadanie:** [#138](https://github.com/MatPomGit/self/issues/138) · **Audyt:** [PR #139](https://github.com/MatPomGit/self/pull/139)

## Cel i podstawa dowodowa

Zmniejszyć powtarzanie treści **bez utraty informacji, danych, tabel ani bibliografii**. Audyt objął 69 plików PDF/DOCX/ODT (40 dokumentów logicznych po wstępnej normalizacji formatów). Dane pochodzą z raportów `overlap.json`, `comparison.json`, `semantic_triage.json` i `claim_evidence.json` wygenerowanych w ramach Issue #138, w tym z przebiegów [43067247808](https://github.com/MatPomGit/self/actions/runs/43067247808) i [43076300091](https://github.com/MatPomGit/self/actions/runs/43076300091).

**Ważne:** pokrycie 5-gramów dotyczy tekstu, a odsetek dopasowanych okien semantycznych to wskaźnik wyszukiwania fragmentów. Żadna z tych metryk nie potwierdza automatycznie równości metod, wyników, poprawności naukowej, intencji autora ani kompletności danych.

## A. Scalenia uzasadnione wynikami audytu

### A1. Analiza afektywna i multimodalna — **MERGE PROPOSED, P0**

- Źródła: `Synteza Modeli multimodalnych.docx` (ok. 2291 słów) + `Zautomatyzowana_analiza_afektywna.pdf` (ok. 2270 słów).
- Pokrycie 5-gramów krótszego dokumentu **88,24%**; TF-IDF cosine **0,952**; podobne fragmenty semantyczne w **61% / 79%** okien. Najsilniejszy rzeczywisty kandydat do scalenia.
- Wspólny rdzeń: pomiar kategoryczny/znakowy/wymiarowy emocji, FACS, automatyczna analiza twarzy (AFA), fuzja modalności, modele ML.
- W analizie różnic pozostały dwa fragmenty DOCX i cztery PDF z mniejszym pokryciem tekstowym; **nie są potwierdzonymi unikalnymi wynikami**.
- W DOCX zidentyfikowano osiem wierszy tabel; wszystkie ich słowa występują w PDF, choć w czterech kolejność/łamanie obniża miarę 5-gramów. Konieczna kontrola wizualna i weryfikacja wartości, przypisów oraz jednostek.
- **Dokument docelowy:** `Zautomatyzowana analiza afektywna: metody multimodalne, modele i architektury Edge AI`.
- **Baza redakcyjna:** edytowalny DOCX, uzupełniony o odrębne elementy z PDF; docelowo utrzymywany jeden plik źródłowy i generowany z niego PDF.
- Proponowana struktura: (1) pojęcia i operacjonalizacja emocji, (2) metody analizy twarzy, FACS i geometria punktów charakterystycznych, (3) sygnały wizyjne, głosowe i fizjologiczne, (4) fuzja multimodalna i ML, (5) okna czasowe i metryki, (6) Edge/Fog/Cloud oraz wymagania opóźnieniowe, (7) ograniczenia psychometryczne, prywatność, uprzedzenia i ryzyka, (8) wnioski, (9) ujednolicona bibliografia.
- Zachować wszystkie źródłowe tabele oraz rozróżnienie wyników empirycznych od prognoz i hipotez. Osobno sprawdzić twierdzenia o rynku technologii i kategorycznych wnioskach o emocjach.
- **Warunek scalenia:** tabela dowodowa „twierdzenie/wiersz → oba źródła → sekcja docelowa”; kontrola wizualna PDF i potwierdzenie kompletności.

### A2. Isaac Lab i bliźniaki cyfrowe — **MERGE PROPOSED, P0**

- Źródła: `Isaac Lab i bliźniaki cyfrowe.pdf` (ok. 886 słów) + `Isaac_Lab.docx` (ok. 897 słów).
- Pokrycie 5-gramów **83,33%**, TF-IDF cosine **0,912**; semantyczne dopasowanie okien **17% / 12%**. Niska zgodność krótkich okien po zmianie składu/formatowania **nie unieważnia wysokiego pokrycia pełnego tekstu**. Obydwa raporty zawierają bardzo podobne podsumowanie platform i AGILE.
- **Dokument docelowy:** `NVIDIA Isaac Sim, Isaac Lab i AGILE: robotyka fizyczna i cyfrowe bliźniaki`.
- **Baza redakcyjna:** `Isaac_Lab.docx`; dołączyć wszystkie odrębne informacje o AGILE, Isaac Lab Arena, afordancjach, OpenUSD, przejściu symulacja–rzeczywistość i scenariuszach przemysłowych, bez powtarzania wstępu.
- **Warunek scalenia:** weryfikacja unikalności akapitów po obu stronach, poprawności nazw komponentów/źródeł i dat aktualności. Zachować bibliografię obu wersji.

**Rozszerzenie warunkowe A2 (nie jest potwierdzonym duplikatem):** `isaac_sim.docx` (ok. 840 słów) i `isaac_sim_pojecia.pdf` (ok. 329 słów) są tematycznie powiązane. Po osobnym porównaniu mogą stanowić podrozdziały „Isaac Sim i architektura” oraz „Słownik pojęć”. Nie usuwać tych dokumentów w pierwszym PR bez wykazania zawartości wspólnej i unikalnej.

## B. Możliwe większe syntezy tematyczne — NIE usuwać jeszcze raportów

| Kandydaci | Zgodność w audycie | Propozycja i warunek |
| --- | --- | --- |
| `tele_ndd.docx` + `teled_ndd.docx` | 16% / 16% semantycznie dopasowanych fragmentów; wspólne omówienie RF ADHD/ASD | **OPTIONAL SYNTHESIS:** jedna monografia „Telediagnostyka ADHD i ASD: walidacja modeli i ograniczenia”, ale nie redukcja duplikatów. Zachować różne badania, próby, miary, metody i pięciokrotną CV. `teled_ndd` już zawiera kontekst 84%/86% vs 68%/69%. |
| `robotyka_afektywna.docx` + `Wpływ robotów na pracę człowieka.docx` | 21% / 12% dopasowanych fragmentów, wspólne zaufanie, antropomorfizacja, interakcja społeczna | **OPTIONAL SYNTHESIS:** „Psychologia interakcji człowiek–robot: afekt, zaufanie i praca”. Odrębne rozdziały dla robotyki afektywnej i kontekstu zatrudnienia; nie uznawać za równoważne opracowania. |
| `Mediapipe.docx` + `VGG-Transformer.docx` | 14% / 21%; wspólne stwierdzenia o EAR i VGG-16 | **OPTIONAL COMPARATIVE REVIEW:** jeden raport porównawczy metod wizyjnych zamiast dwóch krótkich, jeśli celem jest katalog metod. **Najpierw skorygować błędną inferencję lęku/depresji z EAR**; zachować osobne opisy architektur, danych i walidacji. |

Tych trzech grup **nie rekomenduje się łączyć z powodu samej redundancji**. To decyzja redakcyjna o nowym, szerszym opracowaniu, z koniecznością zachowania rozdziałów specjalistycznych.

## C. Powiązania tematyczne bez wystarczających podstaw do scalenia

1. `gry_w_ADHD.docx` ↔ `teled_ndd.docx` (**17% / 13%** okien): cyfrowe interwencje i gry vs diagnostyka/telediagnostyka. **KEEP SEPARATE + CROSS_REFERENCE**.
2. `Mobilne_eye_tracking_i_analiza_afektywna.pdf` ↔ `Sledzenie_wzroku.docx` (**16% / 12%**): trafienia zdominowane przez wspólną bibliografię. **KEEP SEPARATE**.
3. `Mobilne_wskazniki_afektywne.docx` ↔ `teled_ndd.docx`: wspólne odniesienia TRIPOD+AI/PROBAST+AI. **KEEP SEPARATE**.
4. `Lokalny_LLM_Unitree_G1.docx` ↔ `WMA_VLA.docx`: ok. **2% / 2%**; trafienia ze słów kluczowych. **KEEP SEPARATE**.
5. `Mobilne_eye_tracking_i_analiza_afektywna.pdf` ↔ `Przewijanie slajdow gestem.pdf` (**9% / 16%**): wspólne ogólne fragmenty metodologiczne, ale odmienne cele. **KEEP SEPARATE**.
6. `Mapowanie emocji`, `Modele rozpoznawania emocji`, `CASIE i pokrewne nurty...`, `Mobilne_wskazniki_afektywne`: tworzą **kandydacki zestaw tematyczny** do indeksowania, a nie zbiór potwierdzonych duplikatów. Przed ewentualnym włączeniem do A1 potrzebne osobne porównanie treści.
7. `Agenci XR`, `Silniki_XR`, `WMA_VLA` i `Lokalny_LLM_Unitree_G1`: potencjalny tematyczny cykl, lecz brak dowodu znaczącej redundancji w analizowanym rankingu. **KEEP SEPARATE**.

## D. Uporządkowanie wariantów formatowych (nie mylić ze scalaniem raportów)

- **28 grup PDF–DOCX/ODT** ma ≥75% pokrycia 5-gramów: utworzyć **jeden dokument logiczny**, jeden edytowalny plik źródłowy i jego eksport PDF, ale bez automatycznego usuwania istniejących adresów.
- `Wpływ robotów na pracę człowieka.docx` ↔ `.pdf` (73,30%): audyt tabelek i redakcji; prawdopodobnie różnice ekstrakcji/składu, nie dwa niezależne opracowania.
- **Wyjątek krytyczny:** `Przewijanie slajdow gestem.docx` ↔ `.pdf` mają **2,73%** pokrycia 5-gramów, **0% / 0%** dopasowanych okien, odmienny cel i zakres. **NIE traktować jako eksportów jednej wersji.** Oznaczyć jako dwa niezależne dokumenty: „implementacja aplikacji gestowej” i „przegląd technologii, architektura i walidacja”. Ewentualną zmianę nazw wykonać z zachowaniem przekierowań.

## E. Plan realizacji (odrębne PR, ograniczony WIP)

### PR-C1 — szczegółowe scalenie analizy afektywnej
- [ ] Sprawdzić wszystkie strony/akapity i 8 wierszy tabel; rozstrzygnąć 2+4 mniej zgodnych fragmentów.
- [ ] Zweryfikować poprawność twierdzeń i liczb ze źródłami pierwotnymi oraz ujednolicić przypisy.
- [ ] Zbudować jeden **nowy** dokument redakcyjny, zachowując oryginały nietknięte do czasu akceptacji.
- [ ] Wygenerować PDF, sprawdzić integralność tabel i cytowań, przygotować mapowanie starych linków.

### PR-C2 — scalenie dwóch raportów Isaac Lab
- [ ] Porównać wszystkie sekcje obu krótkich opracowań i przypisy.
- [ ] Utworzyć jedno opracowanie redakcyjne z zachowaniem AGILE, Arena i afordancji.
- [ ] Po osobnym przeglądzie zdecydować, czy `isaac_sim` oraz `isaac_sim_pojecia` mają być podrozdziałami czy odrębnymi odnośnikami.

### PR-C3 — porządek formatów i odnośników
- [ ] Zweryfikować zgodność wariantów 28 grup i dwóch problematycznych par.
- [ ] Utrzymać stabilne `/files/...`, stare URL i przekierowania.
- [ ] Zachować źródłowe pliki w historii repozytorium; dopiero po zatwierdzeniu dokumentów docelowych rozważyć archiwizację duplikatów.
- [ ] Nie publikować audytowych artefaktów ani surowych danych z automatu.

### PR-C4 (opcjonalnie) — syntezy interdyscyplinarne
- [ ] Osobno zdecydować o NDD, HRI/pracy i porównaniu metod wizyjnych.
- [ ] Przed połączeniem: ręczna macierz sekcja–twierdzenie–źródło–wynik–nowa lokalizacja.
- [ ] Gdy treści mają inne cele lub metody, zamiast łączyć dokumenty dodać odnośniki krzyżowe.

## Kryteria przyjęcia każdego scalonego raportu

1. **Zero utraconych ustaleń:** każdy istotny oryginalny wynik, parametr, tabela, ograniczenie, definicja i cytowanie ma odpowiednik w raporcie docelowym albo jawne uzasadnienie usunięcia.
2. **Kontrola naukowa:** nie łączyć wyników z różnych badań ani miar bez rozróżnienia prób, walidacji i źródeł.
3. **Spójność redakcyjna:** usunąć dosłowne powtórzenia, zachować unikalne przykłady i przeciwstawne interpretacje.
4. **Zachowanie dostępności:** stary URL musi nadal działać albo prowadzić do uzgodnionego miejsca; nie psuć materiałów dydaktycznych.
5. **Kontrola wizualna i techniczna:** PDF/DOCX, tabele, jednostki, wzory, odnośniki, bibliografia, automatyczne testy, wizualny przegląd wszystkich stron.
6. **Bez samodzielnego kasowania:** każde scalenie to odrębna zmiana treści i dopiero zatwierdzony dokument kanoniczny może zastąpić pliki źródłowe.

## Decyzja operacyjna

**Na teraz dwa scalenia główne: A1 i A2.** Pozostałe raporty należy zachować osobno do czasu nowego, merytorycznego porównania. Docelowo wynik A1+A2 zmniejszyłby 40 dokumentów logicznych do **38**, bez liczenia późniejszych zmian wariantów formatowych. Liczba 38 jest **celem hipotetycznym po zatwierdzeniu**, nie wynikiem już wykonanej konsolidacji.
## Generator dowodowych szkiców dla raportów archiwalnych

Narzędzie `scripts/prepare_consolidation_drafts.py` jest **tylko analizatorem kontrolnym**, nie nadpisuje opublikowanych dokumentów. Korzysta z oryginałów przeniesionych do `files/ignored/inne/analizy/`, zapisuje sekcje DOCX i potencjalnie dodatkowe fragmenty PDF w artefakcie poza `files/`. Opublikowane pliki kanoniczne pozostają w `files/inne/analizy/`, a ich źródła w `docs/consolidated/`. Uruchomienie:

```bash
python scripts/prepare_consolidation_drafts.py --scope files/ignored/inne/analizy --output-dir reports/content-audit/consolidation
```

Wynik nie stanowi decyzji o unikalności tekstu, a archiwum **nie może** trafić do publikacji GitHub Pages.
