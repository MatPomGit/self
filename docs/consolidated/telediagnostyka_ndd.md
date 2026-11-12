
# Telediagnostyka ADHD i ASD: modele predykcyjne, psychometria cyfrowa i walidacja kliniczna

**Raport porównawczy · wersja 1.0.0 · 12 listopada 2026 r.**  
**Typ opracowania:** krytyczna synteza metodologiczna dwóch źródeł, nie wynik badania własnego i nie narzędzie diagnostyczne.

## Streszczenie

Zdalne zbieranie danych z wywiadów społeczno-anamnestycznych, kwestionariuszy i urządzeń mobilnych może usprawnić wstępny przesiew w kierunku ADHD i zaburzenia ze spektrum autyzmu (ASD). Algorytmy uczenia maszynowego pozwalają estymować ryzyko na podstawie tak pozyskanych cech, jednak trafność klasyfikacji w zbiorze badawczym nie jest równoznaczna z trafnością diagnozy klinicznej. Raport łączy perspektywę psychoinformatyki, telediagnostyki i krytycznej walidacji modeli na przykładzie trzech **odrębnych badań**: MedicalBIT (1688 dzieci i nastolatków), telediagnostyki ADHD (342 osoby) oraz klasyfikacji przesiewowej ASD u dorosłych (704 oryginalne rekordy). Wyniki zestawiono z procedurami walidacji, kalibracji, kontroli nierównowagi klas, potencjalnymi źródłami uprzedzeń oraz wymaganiami nadzoru klinicznego.

## 1. Zakres operacyjny i terminologia

**Psychoinformatyka** wykorzystuje metody informatyczne do opisu, pomiaru i modelowania zjawisk psychologicznych. **Telediagnostyka** oznacza zdalną realizację wybranych etapów oceny, w szczególności zbierania danych i kontaktu ze specjalistą; sama zdalność nie gwarantuje równoważności psychometrycznej narzędzi. **Fenotypowanie cyfrowe** polega na ilościowym opisie zachowań przy wykorzystaniu danych z urządzeń i interakcji cyfrowych. Te trzy obszary zachodzą na siebie, ale odpowiadają na odmienne pytania.

Należy konsekwentnie odróżniać: (1) **przesiew**, którego celem jest wskazanie potrzeby dalszej oceny; (2) **predykcję etykiety klinicznej** ustalonej w określonym procesie diagnostycznym; (3) **diagnozę kliniczną**, integrującą dane z wielu źródeł, wywiad rozwojowy i ocenę funkcjonowania. Model może wspierać pierwsze dwa zadania, nie zastępując trzeciego. Warunkiem interpretacji wyników jest podanie populacji docelowej i definicji punktu końcowego.

## 2. Dlaczego dane zdalne są użyteczne i dlaczego pozostają obciążone błędem

Kwestionariusze internetowe ujednolicają format danych, ułatwiają gromadzenie informacji od rodziców i nauczycieli oraz pozwalają na ich wcześniejsze przekazanie do poradni. W ramach MedicalBIT gromadzono m.in. informacje o czynnikach rodzinnych, przed- i okołoporodowych, obawach rozwojowych oraz zdarzeniach zdrowotnych. Dane te mogą służyć do organizacji procesu przesiewowego i budowania modeli predykcyjnych [1, 2].

Samoopis i oceny obserwatorów wiążą się jednak z błędem przypominania, wpływem bieżącego stanu afektywnego, oczekiwaniami społecznymi i odmiennym kontekstem oceny. Dodatkowe problemy to: brak kontroli środowiska wypełniania, różna interpretacja pytań, dobór uczestników mających dostęp do internetu, brak pomiarów w wielu kontekstach i zmiany praktyki klinicznej. Ocena rodzica nie jest „obiektywną prawdą”, lecz źródłem danych o zachowaniu, które wymaga integracji z innymi informacjami.

Telemetria ze smartfona i urządzeń noszonych może wprowadzić większą rozdzielczość czasową dla niektórych zachowań (aktywność, rytm dobowy, wzorce interakcji). **Nie stanowi jednak samodzielnego i specyficznego biomarkera ADHD, ASD czy depresji.** Przykładowo rzadziej używany telefon może odzwierciedlać zmianę rutyny, awarię urządzenia, pracę lub problemy zdrowotne. Wnioskowanie psychologiczne wymaga jawnego modelu zmiennych zakłócających, walidacji w odpowiedniej populacji i etycznej kontroli zakresu danych.

## 3. Trzy różne badania i ich wyniki

| Badanie i zadanie | Materiał wejściowy | Algorytm i rezultat | Kluczowe ograniczenie |
|---|---|---|---|
| Grazioli i in. 2024, MedicalBIT [2] | 1688 dzieci i nastolatków kierowanych do oceny, rodzicielski wywiad społeczno-anamnestyczny; 269 ADHD, 270 ASD | Random Forest: 84% dokładności ADHD, 86% ASD przy ustalonym podziale; średnia 5-fold CV: 68% i 69% | Retrospektywne, jednoośrodkowe dane kierowanych pacjentów; różne procedury walidacji dają odmienne wyniki |
| Grazioli i in. 2024, procedura telediagnostyczna [3] | 342 dzieci w wieku 3–16 lat skierowanych z podejrzeniem ADHD; oceny rodziców i nauczycieli oraz dane z badania stacjonarnego | Drzewo decyzyjne: 82% na zbiorze uczącym; ok. 74% w walidacji krzyżowej | Model odwzorowuje część decyzji konkretnej praktyki klinicznej; objawy ASD komplikują różnicowanie |
| Jaffer i in. 2022, ASD u dorosłych [4] | Początkowo 704 rekordy przesiewowe: 189 ASD i 515 kontrolnych; stosowano SMOTE | SMO/SVM: 99,71% dokładności w opisanym zadaniu | Dane przesiewowe i rekordy syntetyczne; konieczne rozdzielenie danych syntetycznych od niezależnych osób oraz zewnętrzna walidacja kliniczna |

Dane te **nie są trzema oszacowaniami skuteczności jednej metody**. Różnią się populacją, kryterium przypisania etykiety, cechami wejściowymi, sposobem podziału danych i pytaniem badawczym.

### 3.1. MedicalBIT: 1688 osób, modele ADHD i ASD

W badaniu retrospektywnym Grazioli i współautorów [2] porównano las losowy (RF), drzewo decyzyjne (DT) i regresję logistyczną (LR). W ustalonym podziale danych dla RF raportowano:

| Punkt końcowy | Dokładność | Czułość | Swoistość | Średnia dokładność 5-fold CV |
|---|---:|---:|---:|---:|
| ADHD versus brak ADHD | 84% (95% CI 82–85) | 93% | 75% | 68% |
| ASD versus brak ASD | 86% (95% CI 84–87) | 95% | 77% | 69% |

Dla pięciokrotnej CV średnie czułości wynosiły odpowiednio 73% i 70%, a swoistości 63% i 68%. Nie wolno interpretować 84% i 86% oraz 68% i 69% jako wyników różnych, niezależnych prób potwierdzających kliniczną skuteczność. Są to **odmienne oceny w obrębie tego samego badania** [2].

Płeć oraz czynniki przed- i okołoporodowe należały do ważnych predyktorów, lecz ważność cechy według SHAP nie jest równoznaczna z wykazaniem przyczynowej roli tej cechy w etiologii zaburzenia. Możliwe jest kodowanie przez cechy różnic w skierowaniach, procedurze rozpoznawania lub strukturze danych.

### 3.2. Telediagnostyka ADHD: 342 osoby

W innym badaniu Grazioli i współautorów [3] analizowano dzieci i młodzież w wieku 3–16 lat kierowanych z podejrzeniem ADHD. Model drzewa decyzyjnego, oparty na ocenach opiekunów i nauczycieli, odtwarzał część reguł stosowanych przez klinicystów. **82% dokładności** dotyczyło oceny dopasowania do danych użytych w modelowaniu; **74%** pochodziło z walidacji krzyżowej. W CV inne algorytmy uzyskiwały wyniki porównywalne, w tym RF ok. 74% i SVM ok. 75%.

Nasilenie podstawowych objawów ADHD zgłaszanych przez opiekunów było ważnym predyktorem. Współwystępowanie trudności autystycznych mogło jednak wpływać na błędne przypisania przypadków. Uogólnienie modelu do innych placówek wymaga nowej oceny, nie tylko powtórzenia wyników w tym samym zbiorze.

### 3.3. Przesiew ASD u dorosłych: WEKA, SMO i SMOTE

Badanie Jaffera i współautorów [4] porównywało LR, SMO, naiwny Bayes i IBK w zadaniu klasyfikacji kwestionariuszowych danych przesiewowych ASD. W opisywanym eksperymencie SMO uzyskał 99,71% dokładności. Kluczowe ograniczenia interpretacyjne to źródło etykiet, relacja cech do kryterium klasyfikacji, sposób stosowania nadpróbkowania i brak niezależnego potwierdzenia wartości diagnostycznej w rutynie klinicznej. **SMOTE zwiększa liczbę rekordów uczących, nie liczbę niezależnie zbadanych pacjentów.**

Dane z badania ASD u dorosłych nie mogą być bezpośrednio porównywane z wynikami MedicalBIT dla dzieci. Inny punkt końcowy i schemat doboru próby wykluczają sensowny wspólny ranking na podstawie samej dokładności.

## 4. Metryki klasyfikacji i ich ograniczenia

Dla macierzy pomyłek z wartościami TP, TN, FP, FN:

- Czułość (recall, sensitivity): `TP / (TP + FN)`.
- Swoistość (specificity): `TN / (TN + FP)`.
- Precyzja / dodatnia wartość predykcyjna (precision, PPV): `TP / (TP + FP)`.
- Dokładność (accuracy): `(TP + TN) / (TP + TN + FP + FN)`.

**Swoistość i precyzja nie są synonimami.** Starszy dokument `tele_ndd.docx` zawierał miejscami zapis sugerujący ich równoważność. W syntezie przyjęto poprawne definicje. PPV i NPV zależą również od częstości występowania rozpoznania w populacji, przez co dokładność osiągnięta w próbie kierowanej do poradni nie może zostać automatycznie przepisana na populację ogólną.

Oprócz dyskryminacji należy raportować kalibrację prawdopodobieństw, przedziały ufności, wartości predykcyjne w docelowym rozpowszechnieniu, metryki podgrup oraz kliniczny koszt wyników fałszywie dodatnich i ujemnych.

## 5. Projekt badania i zabezpieczenie przed przeciekiem danych

Najpierw definiuje się punkt końcowy, populację i moment predykcji. Następnie trzeba rozdzielić osoby między zbiory treningowe, walidacyjne i testowe. Przy danych wielokrotnych podział musi odbywać się **na poziomie osoby**, a w analizach transportowalności również ośrodka lub czasu.

Imputacja, skalowanie, selekcja cech, SMOTE i tuning hiperparametrów powinny być dopasowane wyłącznie w podzbiorach treningowych kolejnych iteracji. Walidacja krzyżowa nie zastępuje walidacji zewnętrznej na nowej populacji. Wysokie wyniki na danych zawierających rekordy powielone lub syntetyczne wymagają szczególnie starannej kontroli przecieku.

Zalecany raport metod obejmuje: protokół pobierania danych, definicję etykiety, schemat podziału, rozkład klas, opis braków danych, parametry przetwarzania, hiperparametry modelu, estymaty i ich niepewność, kalibrację, badanie stronniczości, analizę błędów oraz walidację zewnętrzną. Do planowania i oceny jakości badań predykcyjnych należy stosować **TRIPOD+AI** [7] oraz **PROBAST+AI** [8].

## 6. Projekt usługi telediagnostycznej

Referencyjny przepływ obejmuje pięć warstw:

1. **Pozyskiwanie danych:** zgoda, informacja o celu, kwestionariusze o ustalonym statusie psychometrycznym, kontrola jakości odpowiedzi oraz informatorów.
2. **Kontrola danych:** wykrywanie duplikatów, braków, niespójności i nieprawidłowej kolejności pomiaru; rozdzielenie danych identyfikujących od cech analitycznych.
3. **Model predykcyjny:** wersjonowany model, ustalone progi, jawne ograniczenia populacyjne i ocena niepewności.
4. **Decyzja kliniczna:** wynik jako wsparcie przesiewu lub priorytetyzacji, bez automatycznego rozpoznawania ADHD lub ASD.
5. **Nadzór:** audyt dostępu, monitorowanie kalibracji i zmiany rozkładów danych, przegląd przypadków błędnych, procedura wyłączenia algorytmu.

Teleporada, zdalne wykonanie kwestionariusza i automatyczna predykcja są różnymi usługami; ich skuteczność i bezpieczeństwo należy oceniać odrębnie. Dostęp alternatywny pozostaje istotny ze względu na nierówności cyfrowe i wymagania dostępności.

## 7. Zestawienie i pochodzenie treści

| Element opracowania | Wkład `tele_ndd.docx` | Wkład `teled_ndd.docx` | Decyzja redakcyjna |
|---|---|---|---|
| Historia psychoinformatyki i ograniczenia samoopisu | Szerszy kontekst, przykłady z badań mobilnych | Krytyczna ocena i zastosowania kliniczne | Połączono pojęcia, oddzielono hipotezy od potwierdzonych korelatów |
| MedicalBIT, RF dla ADHD/ASD | Wyniki z pojedynczego schematu, zmienne istotne | Wyróżnienie ustalonego podziału i CV | Zachowano dwa schematy walidacji tego samego badania |
| Badanie ADHD n = 342 | Cel kliniczny i objawy ASD | Liczebność, schemat porównania, ograniczenia | Zachowano osobną populację i metryki |
| ASD dorosłych / WEKA / SMO | Klasyfikatory, liczby i SMOTE | Ograniczenia interpretacji wysokiej dokładności | Nie przedstawiono 99,71% jako klinicznej trafności diagnostycznej |
| Smartfony, urządzenia noszone i duże dane | Przykłady cech cyfrowych i problemów samoopisu | Prywatność, kontekst i ograniczenia | Zachowano jako obszar badawczy, nie samodzielny biomarker |
| Miary klasyfikacji | Definicje, miejscami błędne synonimy | Rozróżnienie PPV, swoistości i kalibracji | Ujednolicono według macierzy pomyłek |

Wersje materiałów poddanych analizie, według sum SHA-256:

- `files/inne/analizy/tele_ndd.docx`: `30e17d8a293d08483a1f3de853761390327c7451f33ac9f9b475f6463a513e49`
- `files/inne/analizy/teled_ndd.docx`: `1ee2c772c9aec3ecf4c0bc55bc9adc1d79c6116dacceafcb00cc4ebb8c5560b0`

Teksty źródłowe pozostają dostępne w pierwotnych plikach. Nowa synteza jest **opracowaniem uzupełniającym**; nie stanowi dowodu, że całą zawartość dwóch dokumentów można zastąpić krótszym tekstem bez utraty szczegółów.

## 8. Wnioski i zalecenia badawcze

Wykazano potencjał predykcyjny cyfrowych danych anamnestycznych i kwestionariuszowych, ale dotychczasowe wyniki nie uzasadniają autonomicznego rozpoznawania ADHD i ASD. O wartości przyszłego modelu będzie decydować nie najwyższa dokładność uzyskana w zamkniętym eksperymencie, lecz jego kalibracja, trafność na nowej populacji, równowaga między błędami i poprawa realnej ścieżki świadczenia usług. Należy rozdzielać ocenę psychometryczną narzędzia, walidację klasyfikatora i walidację procesu klinicznego.

## Bibliografia

1. Colombo P. i in. (2022). *A Web Platform for Standardized Data Acquisition, Processing, and Export in the Child Psychopathology Clinical Routine (MedicalBIT)*. JMIR Formative Research, 6, e36757. https://doi.org/10.2196/36757
2. Grazioli S. i in. (2024). *Use of Machine Learning Models to Differentiate Neurodevelopment Conditions Through Digitally Collected Data*. JMIR Formative Research, 8, e54577. https://doi.org/10.2196/54577
3. Grazioli S. i in. (2024). *Exploring telediagnostic procedures in child neuropsychiatry: addressing ADHD diagnosis and autism symptoms through supervised machine learning*. European Child & Adolescent Psychiatry, 33, 139–149. https://doi.org/10.1007/s00787-023-02145-4
4. Jaffer S., Abdulazez I., Al-Qazzaz N., Yousif T. (2022). *Data Mining for Autism Spectrum Disorder detection among Adults*. Al-Nahrain Journal for Engineering Sciences, 25(4), 142–151. https://doi.org/10.29194/NJES.25040142
5. Markowetz A. i in. (2014). *Psycho-Informatics: Big Data shaping modern psychometrics*. Medical Hypotheses, 82, 405–411. https://doi.org/10.1016/j.mehy.2013.11.030
6. Chawla N.V. i in. (2002). *SMOTE: Synthetic Minority Over-sampling Technique*. Journal of Artificial Intelligence Research, 16, 321–357. https://doi.org/10.1613/jair.953
7. Collins G.S. i in. (2024). *TRIPOD+AI statement*. BMJ, 385, e078378. https://doi.org/10.1136/bmj-2023-078378
8. Moons K.G.M. i in. (2025). *PROBAST+AI*. BMJ, 388, e082505. https://doi.org/10.1136/bmj-2024-082505
