# Audyt zgodności twierdzeń naukowych — Issue #138

**Wersja robocza 0.1.0 · 11.11.2026 · źródła: publiczne raporty \`files/inne/analizy/\`.**

Celem jest **poprawność naukowa i zachowanie informacji unikalnych**,
a nie mechaniczne ograniczanie liczby raportów. Ustalenia oparto na
fragmentach raportów zapisanych w artefakcie
\`content-semantic-pilot\` oraz na wskazanych niżej publikacjach.
Pierwszeństwo mają źródła pierwotne. Ponowne wydobycie pełnych kontekstów,
wraz z adresami stron/akapitów i SHA-256, generuje
\`scripts/audit_repeated_claims.py\`. Wynik jest nadal **read-only**.

## C01 — EAR: błędna inferencja kliniczna na podstawie mrugania

**Raporty:** \`Mediapipe.docx\` (akapit 44) i
\`VGG-Transformer.docx\` (akapit 39).

**Wspólne twierdzenie:** >20 mrugnięć/min jako wskaźnik lęku oraz
EAR < 0,2 przez > 0,5 s jako oznaka depresji/skrajnego zmęczenia.

**Ocena: REQUIRE_CORRECTION_BEFORE_REUSE.** Zestawienie parametrów
technicznych detekcji mrugnięć z rozpoznawaniem określonych stanów
psychicznych jest nieuzasadnionym uogólnieniem. Eye Aspect Ratio
opisuje geometrycznie otwarcie powiek. Progowanie EAR jest zależne od
układu pomiarowego i nie jest samoistnym testem diagnostycznym.
Częstość mrugania zależy m.in. od zadania, osoby, oświetlenia,
komfortu oczu i stanu pobudzenia. Badania psychofizjologiczne
wskazują możliwe **asocjacje statystyczne**, lecz nie uzasadniają
uniwersalnego klinicznego progu lęku/depresji. W szczególności
>20/min nie odróżnia wiarygodnie osób z lękiem od zdrowych.

**Proponowane brzmienie po weryfikacji i redakcji:**

> EAR jest wskaźnikiem geometrycznym stopnia otwarcia oka służącym
> do detekcji mrugnięć. Przykładowe progi operacyjne (np. EAR < 0,2)
> wymagają walidacji dla danego algorytmu, kamery i populacji.
> Częstość i charakterystyka mrugania mogą korelować z obciążeniem
> poznawczym, zmęczeniem lub stanem emocjonalnym, ale nie stanowią
> samodzielnych kryteriów diagnozowania lęku ani depresji.

**Źródła zewnętrzne (sprawdzone 11.11.2026):**
1. Soukupová T., Čech J. (2016), *Real-Time Eye Blink Detection using
   Facial Landmarks*, CVWW. Wskaźnik EAR + klasyfikacja mrugnięć
   przez SVM, nie diagnostyka kliniczna:
   https://fel.cvut.cz/en/faculty/people/444-jan-cech/publications
2. *What is a blink? Classifying and characterizing blinks in eye
   openness signals* (2024), przegląd metod i zmienności częstości:
   https://pmc.ncbi.nlm.nih.gov/articles/PMC11133197/
3. Tomashin i wsp. (2025), *The eye, a spy hole on human mind*,
   PLOS ONE, DOI 10.1371/journal.pone.0338262. Korelacje w badaniu
   50 młodych kobiet, a nie walidacja jednego progu diagnostycznego:
   https://doi.org/10.1371/journal.pone.0338262
4. *The clinical and experimental significance of blinking behavior*
   (2020), czynniki osobnicze, zadaniowe i środowiskowe:
   https://pmc.ncbi.nlm.nih.gov/articles/PMC7182785/

**Decyzja o konsolidacji:** \`CROSS_REFERENCE\` po korekcie
twierdzenia, bez automatycznego łączenia całych dokumentów.

## C02 — ADHD/ASD: dokładność RF 84% i 86% bez kontekstu walidacji

**Raporty:** \`tele_ndd.docx\` (akapit 44) i
\`teled_ndd.docx\` (akapit 59).

**Wspólne twierdzenie:** w badaniu Random Forest uzyskał
dokładność 84% dla ADHD i 86% dla ASD, czułość 93% i 95% oraz
swoistość 75% i 77%.

**Ocena: CONFIRMED_WITH_MANDATORY_CONTEXT.** Dane liczbowe
odpowiadają publikacji Grazioli i wsp. (2024) opisującej
**retrospektywne badanie jednoośrodkowe** z udziałem
1688 dzieci i nastolatków kierowanych na diagnostykę. Wartości
84% i 86% pochodzą z **ustalonego podziału 70% trening / 30% test**.
W niezależnie opisanym **5-fold CV** średnia accuracy wynosiła
tylko **68% (SD 2,5 p.p.) i 69% (SD 2,2 p.p.)**. Publikacja
nie dowodzi przydatności do samodzielnego rozpoznawania choroby ani
ogólnej skuteczności 84–86% w innych populacjach.

| Miara | ADHD | ASD |
| --- | ---: | ---: |
| Accuracy, ustalony podział 70/30 | 84% | 86% |
| Sensitivity, ustalony podział | 93% | 95% |
| Specificity, ustalony podział | 75% | 77% |
| Accuracy, pięciokrotna CV (średnia) | **68%** | **69%** |

**Proponowane brzmienie:**

> W retrospektywnym jednoośrodkowym badaniu 1688 dzieci i nastolatków
> model Random Forest klasyfikował ADHD i ASD z dokładnością
> odpowiednio 84% i 86% dla ustalonego podziału na dane uczące i
> testowe (70/30). W pięciokrotnej walidacji krzyżowej średnia
> dokładność spadła do 68% dla ADHD i 69% dla ASD.
> Wynik należy traktować jako ocenę konkretnego modelu i zbioru
> danych, a nie kliniczny test diagnostyczny o ogólnej skuteczności.

**Źródło pierwotne (sprawdzone 11.11.2026):**
Grazioli S. i wsp. (2024). *Use of Machine Learning Models to
Differentiate Neurodevelopment Conditions Through Digitally
Collected Data: Cross-Sectional Questionnaire Study.*
JMIR Form Res 8:e54577, DOI 10.2196/54577.
Table 3, Methods: testing and five-fold cross-validation.
https://formative.jmir.org/2024/1/e54577/

**Decyzja o konsolidacji:** \`CROSS_REFERENCE\`, z poprawnym
przypisem i tabelą pokazującą oba reżimy walidacji.
Wspólne liczby są wynikiem przywołania **tego samego badania**,
nie dwóch niezależnych replikacji.

## C03 — Synteza modeli multimodalnych i analiza afektywna

**Raporty:** \`Synteza Modeli multimodalnych.docx\` oraz
\`Zautomatyzowana_analiza_afektywna.pdf\`.

**Potwierdzone powtórzenia tekstowe:** pomiar wymiarowy emocji,
FACS i opis klasyfikacji z wykorzystaniem ML
(m.in. DOCX akapity 14–15 i 45 ↔ PDF strony 2–3).
W niezależnym modelu wielojęzycznym
dopasowano 61% / 79% fragmentów przy progu 0,76. To odsetki
fragmentów o podobnych embeddingach, **nie procent tożsamości
wniosków naukowych**.

**Co trzeba zachować przed ewentualnym połączeniem:**
1. Wszystkie indywidualne porównania metod, wartości i ograniczenia;
   nie wystarczy wspólny abstrakt.
2. Tabele: oryginalne dane, jednostki, podpisy, źródła,
   próby, okna czasowe, algorytmy i środowiska obliczeniowe.
3. Fragmenty dotyczące geometrii twarzy / FACS i scenariuszy Edge AI,
   o ile w drugim raporcie nie mają merytorycznie równoważnego opisu.
4. Pełną bibliografię obu raportów oraz informację, czy są kolejnymi
   wersjami jednego opracowania.

**Status:** \`REVIEW_REQUIRED\`. Plik
\`claim_evidence.json\` wskazuje potencjalnie odrębne fragmenty i
wiersze tabel. **Niskie pokrycie 5-gramów nie dowodzi
unikalności semantycznej**, a ekstrakcja tabel PDF może być niepełna.
Nie podejmować jeszcze \`MERGE\` ani \`SUPERSEDE\`.

## Kolejność dalszych działań

- [x] Zidentyfikowano rzeczywiście powtarzane twierdzenia.
- [x] Zweryfikowano podstawowe źródło RF ADHD/ASD i charakter EAR.
- [x] Przygotowano sugerowaną korektę obu sformułowań.
- [ ] Sprawdzić wiersze tabel i unikalne sekcje w pełnym kontekście.
- [ ] Przeprowadzić niezależny naukowy przegląd pozostałych twierdzeń
  (nie tylko wyników podobieństwa), z podaniem metod i mianowników.
- [ ] Po akceptacji zakresu stworzyć osobny PR z poprawkami
  treści źródłowych DOCX/PDF oraz regeneracją odpowiednich eksportów.

**Ważne:** ten etap jest audytem, nie zmianą tekstów źródłowych.
Wszystkie dokumenty pozostają publicznie dostępne i niezmodyfikowane.
