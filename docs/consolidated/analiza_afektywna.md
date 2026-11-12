# Zautomatyzowana analiza afektywna: modele multimodalne, walidacja i Edge AI

**Raport syntetyczny · wersja 1.0.0 · 12 listopada 2026 r.**  
**Zakres:** metody pomiaru, automatyczna analiza mimiki, fuzja sygnałów, uczenie maszynowe, wdrożenia brzegowe oraz ograniczenia psychometryczne i prawne.

## Streszczenie

Zautomatyzowana analiza afektywna (AFA, *automated facial analysis*, w szerszym ujęciu *affective computing*) obejmuje algorytmy opisujące ekspresję twarzy i inne korelaty stanów emocjonalnych: mowę, treść językową oraz sygnały fizjologiczne. Niniejszy raport łączy dwa pokrywające się opracowania w jedną strukturę, zachowując ich techniczne treści, obie tabele i zastosowania. Rozdziela **pomiar obserwowalnego zachowania** od **wnioskowania o subiektywnym doświadczeniu emocji**. Przedstawia modele kategoryczne, wymiarowe i opisowe, potok wizji komputerowej, mechanizmy fuzji i przykładowe architektury czasowe. Omawia też systemy Edge/Fog/Cloud, metody optymalizacji inferencji i wymagania walidacyjne. Konkluzja jest metodologiczna: wzrost dokładności klasyfikacji w określonym zbiorze danych nie dowodzi zdolności systemu do uniwersalnego rozpoznawania emocji ani przydatności diagnostycznej. Raport ma charakter przeglądu technologicznego; nie przedstawia wyników własnego eksperymentu.

## 1. Zakres pojęciowy i operacjonalizacja

Obliczenia afektywne łączą psychologię, informatykę, przetwarzanie sygnałów i interakcję człowiek–komputer. Zadania techniczne obejmują detekcję twarzy, estymację punktów charakterystycznych, kodowanie ruchów mięśni, rozpoznawanie wzorców w głosie oraz przewidywanie etykiet lub wymiarów afektywnych. **Ekspresja nie jest jednoznacznym wskaźnikiem przeżywanej emocji**: tę samą konfigurację ruchów twarzy można interpretować odmiennie w różnych sytuacjach, kulturach i u różnych osób [1]. Wyniki klasyfikatora należy odnosić do jego etykiet treningowych, warunków nagrania i procedury walidacyjnej, a nie do obiektywnego „odczytu” stanu psychicznego.

Dla uniknięcia pomieszania poziomów pomiaru należy rozróżnić: (i) obserwowalne zdarzenia (np. Action Units, pauzy, ruch głowy), (ii) sygnały fizjologiczne korelujące z pobudzeniem, (iii) ocenę afektu przez obserwatora, (iv) samoopis uczestnika oraz (v) diagnozę kliniczną. Przejście między tymi poziomami jest hipotezą empiryczną, a nie własnością samego czujnika.

## 2. Modele reprezentowania afektu

**Podejście kategoryczne (*message-based*)** przypisuje próbkom dyskretne etykiety, takie jak radość, smutek czy gniew. Takie etykiety bywają użyteczne dla interfejsów, ale zależą od definicji kategorii, sposobu anotacji i kontekstu. Nie powinny być interpretowane jako bezpośredni dostęp do wewnętrznego stanu użytkownika.

**Podejście opisowe (*sign-based*)** koduje obserwowalne ruchy mięśni, przede wszystkim jednostki działania FACS (*Facial Action Coding System*, Action Units). FACS opisuje ekspresję, a nie automatycznie przyczynę emocjonalną. Detekcja AU może więc być celem samodzielnego systemu, bez klasyfikowania człowieka jako „zestresowanego” lub „smutnego”.

**Podejście wymiarowe** umieszcza oceny w przestrzeni walencji i pobudzenia, czasem rozszerzonej o dominację. Skala, procedura oceny i definicja jednostki analizy muszą być jawne. Pomiar w oknach czasowych pozwala rozróżniać krótkotrwałe zmiany ekspresji i dłuższe trendy zachowania, ale nie jest równoznaczny z pomiarem utrzymującego się nastroju.

**Podejście opisowe generatywne** korzysta z modeli językowych do formułowania opisów multimodalnych. Modele te mogą syntetyzować kontekst, lecz generowane opisy wymagają zewnętrznej kontroli i nie stanowią niezależnego źródła dowodów psychologicznych.

### 2.1. Skale czasowe pomiaru

Poniższa tabela zachowuje orientacyjne okna z obu raportów źródłowych. Są to **przykładowe parametry projektowe**, nie ustalone biologicznie granice poszczególnych emocji.

| Okno analizy | Orientacyjny czas | Zjawiska możliwe do obserwacji | Przykładowe cechy obliczeniowe |
|---|---:|---|---|
| Krótkie | 0,5–2 s | Szybkie ruchy twarzy, reakcja na bodziec | Trajektorie punktów twarzy, lokalna zmiana prozodii |
| Średnie | 2–10 s | Sekwencje zachowań w kontekście sytuacji | Aktywność AU, zmienność głosu i spojrzenia |
| Długie | 10–60 s lub więcej | Trendy fizjologiczne i zachowania | Statystyki sygnałów, stabilność estymacji i dryf |

Czas okna należy optymalizować eksperymentalnie pod kątem częstotliwości próbkowania, opóźnienia decyzji, dynamiki zjawiska i niezależności próbek.

## 3. Potok zautomatyzowanej analizy twarzy

Typowy potok obejmuje: **detekcję i śledzenie twarzy → normalizację położenia i oświetlenia → ekstrakcję cech → estymację AU lub innych etykiet → agregację czasową → walidację**. W zależności od zadania możliwe są rozwiązania klasyczne (detektory kaskadowe, Active Appearance Models, Constrained Local Models) i modele głębokie. Stabilne śledzenie punktów charakterystycznych jest warunkiem porównywania klatek; błędy detektora mogą prowadzić do pozornej zmiany ekspresji.

Cechy **geometryczne** opisują odległości i przemieszczenia punktów charakterystycznych twarzy. Cechy **teksturalne** obejmują lokalne wzorce wyglądu, dawniej opisywane przez filtry Gabora, HOG czy SIFT. Cechy **dynamiczne** obejmują przepływ optyczny, trajektorie i wieloklatkowe reprezentacje ruchu. Modele klasyfikacyjne (np. SVM, CNN, modele sekwencyjne) wymagają rozdzielenia tożsamości i sesji między zbiorami treningowymi i testowymi, jeśli celem jest generalizacja na nowych uczestników.

Termin *mikroekspresja* powinien oznaczać krótkotrwały wzorzec ruchu twarzy, a nie rzekomo niezawodne „ujawnienie prawdziwej emocji”. Przypisywanie takim sygnałom stanów psychicznych wymaga osobnych dowodów walidacyjnych [1].

## 4. Integracja modalności

### 4.1. Obraz, głos i język

Obraz dostarcza informacji o ruchach twarzy, pozycji głowy i zachowaniach wzrokowych. Akustyka opisuje tempo, wysokość głosu, natężenie i prozodię, natomiast analiza tekstu uwzględnia treść, negację i kontekst wypowiedzi. Modalności te nie są zamienne: każdy kanał odpowiada na inne pytania i ma odmienne źródła błędu. Szczególnie w dialogu mogą występować rozbieżności między znaczeniem słów a sposobem ich wypowiedzenia.

W praktyce stosuje się fuzję **wczesną** (łączenie cech przed modelem), **późną** (agregacja predykcji modeli jednomodalnych) i **hybrydową** (wspólne reprezentacje z mechanizmem uwagi). Poprawa skuteczności przez fuzję nie jest gwarantowana: zależy od jakości sygnałów, ich synchronizacji, brakujących modalności i charakteru zbioru danych. Z tego powodu wymagane są badania ablacyjne i porównania względem dobrych modeli jednomodalnych.

### 4.2. Kanały fizjologiczne

EEG mierzy zmienność aktywności elektrycznej na powierzchni głowy; EKG i PPG mogą dostarczać parametrów pracy serca, a EDA/GSR przewodnictwa skóry związanego z aktywnością współczulną. EMG może opisywać aktywność mięśniową. Są to wskaźniki procesów fizjologicznych, **nie bezpośrednie i jednoznaczne czujniki emocji**. Przed interpretacją należy kontrolować artefakty ruchowe, obciążenie poznawcze, oddech, aktywność fizyczną i różnice osobnicze.

Architektury obejmujące CNN, BiLSTM, Transformer i mechanizmy uwagi mogą modelować cechy lokalne oraz zależności czasowe i międzykanałowe. Doniesione w materiałach źródłowych dokładności 88,2% (DEAP) i 89,5% (AMIGOS) **nie są tu przyjmowane jako porównywalne wyniki referencyjne**, ponieważ w raportach nie określono w sposób możliwy do odtworzenia podziału osób, liczby klas, protokołu preprocesingu i źródłowej tabeli wyników. Do oceny modelu należy podawać również balanced accuracy, macierz pomyłek, niepewność estymacji i niezależną walidację.

### 4.3. Modele generatywne i językowo-multimodalne

Modele multimodalne i systemy mowa–mowa (w materiałach źródłowych wymieniono AffectGPT i Hume EVI) mogą integrować sygnały z wielu kanałów i generować odpowiedzi kontekstowe. Ich użycie należy oceniać pod kątem jakości anotacji, halucynacji, zgodności z wypowiedziami użytkownika oraz ryzyka przypisywania mu niepotwierdzonych stanów psychicznych. Deklarowane przez dostawców opóźnienia i możliwości produktu są specyficzne dla wersji systemu oraz warunków testu.

## 5. Wdrożenie w architekturze Edge–Fog–Cloud

Przetwarzanie blisko źródła danych pomaga ograniczać transmisję wrażliwych strumieni oraz opóźnienie sieciowe. Urządzenia brzegowe, np. NVIDIA Jetson czy Rockchip RK3588, mogą korzystać z akceleracji GPU/NPU; wybór platformy powinien wynikać z wymaganego FPS, opóźnienia od końca do końca, poboru energii, pamięci i dopuszczalnej jakości modelu. Przeniesienie obliczeń na brzeg nie eliminuje automatycznie ryzyka prywatności, ponieważ nagrania i cechy pozostają danymi wymagającymi kontroli dostępu.

| Warstwa | Orientacyjne założenie projektowe z raportów źródłowych | Typowe zadania | Przykłady |
|---|---|---|---|
| Edge | 1–10 ms jako ambitny budżet wybranych operacji, nie gwarancja całego potoku | Detekcja, śledzenie, inferencja w czasie rzeczywistym | Jetson Orin, RK3588 |
| Fog / lokalny serwer | 10–100 ms jako zależny od infrastruktury budżet | Agregacja wielu strumieni, synchronizacja | Serwer lokalny, brama obliczeniowa |
| Cloud | 100 ms–2 s lub więcej zależnie od sieci i obciążenia | Trening, analiza zbiorcza, raportowanie | Usługi centrum danych |

Weryfikacja czasowa powinna mierzyć medianę i wysokie kwantyle opóźnienia (np. p95/p99) całego przepływu, a nie wyłącznie inferencji modelu. Do optymalizacji służą m.in. kwantyzacja, zmniejszanie rozdzielczości, redukcja liczby klatek i profilowanie zużycia pamięci. Raporty źródłowe wymieniają RKNN Toolkit / Model Zoo, NVIDIA DeepStream i Intel OpenVINO; ich zgodność zależy od sprzętu i wersji środowiska.

## 6. Obszary zastosowań i ocena ryzyka

**Systemy wsparcia zdrowia i psychologii.** Monitorowanie ekspresji, aktywności lub samopoczucia może wspierać badania, ale predykcja etykiety emocjonalnej nie jest równoznaczna z diagnozą zaburzenia. Wykorzystanie kliniczne wymaga odpowiedniego projektu badania, kontroli błędów i zgodności z wymaganiami regulacyjnymi.

**Bezpieczeństwo transportu.** Ocena senności lub odwracania uwagi kierowcy może korzystać z różnych sygnałów, w tym parametrów oczu i zachowania głowy. Nie należy utożsamiać senności, stresu i emocji z jedną etykietą.

**Gry i robotyka społeczna.** Adaptacja trudności, strategii dialogowej lub zachowania robota może uwzględniać sygnały zwrotne, lecz decyzje powinny respektować autonomię użytkownika, możliwość odmowy i niepewność klasyfikatora.

## 7. Ograniczenia psychometryczne, etyczne i prawne

Najważniejsze zagrożenia obejmują *construct validity*: model może dokładnie rozpoznawać etykiety nadane przez anotatorów, a nie właściwy konstrukt psychologiczny. Weryfikacja obejmuje zgodność między oceniającymi, trafność zewnętrzną, stabilność między populacjami, osoby niewidziane podczas treningu oraz kontrolę danych wrażliwych. Dodatkowe ryzyka to stronniczość względem wieku, kontekstu kulturowego, warunków rejestracji i niepełnosprawności [1].

Artykuł 5 ust. 1 lit. f rozporządzenia UE 2024/1689 zakazuje wprowadzania do obrotu, oddawania do użytku w tym celu i wykorzystywania systemów AI do wnioskowania o emocjach osób fizycznych w obszarze pracy i instytucji edukacyjnych, z wąskim wyjątkiem przesłanek medycznych lub bezpieczeństwa [3]. Zakaz obejmuje określone **zastosowania**, a nie każdą analizę twarzy ani każdą technologię obliczeń afektywnych. Nie należy przedstawiać zwykłego monitorowania stresu w pracy jako automatycznie objętego wyjątkiem medycznym [3, 4]. Ponadto mogą mieć zastosowanie wymogi ochrony danych i regulacje dotyczące wyrobów medycznych.

## 8. Zalecenia metodologiczne i wnioski

Zalecany protokół badawczy obejmuje: (1) definicję konstruktu, (2) jawne kryteria i instrukcje anotacji, (3) rozdzielenie osób i sesji między zbiorami, (4) porównanie unimodalne–multimodalne, (5) analizę brakujących modalności i artefaktów, (6) kalibrację pewności oraz (7) ocenę różnic międzygrupowych i etycznych konsekwencji wdrożenia. Dla systemów Edge należy dodatkowo raportować opóźnienie, pobór energii i jakość po kwantyzacji.

Ujednolicenie dwóch wcześniejszych opracowań pozwala usunąć powtórzone definicje AFA, FACS i modeli walencji/pobudzenia, a zarazem zachować dwa zestawienia tabelaryczne, metody fuzji i architektury urządzeń brzegowych. Centralny wniosek pozostaje ostrożny: **techniczna detekcja cech nie jest automatycznie rzetelną inferencją stanu emocjonalnego**.

## Bibliografia

1. Barrett, L. F., Adolphs, R., Marsella, S., Martinez, A. M., & Pollak, S. D. (2019). *Emotional Expressions Reconsidered: Challenges to Inferring Emotion From Human Facial Movements*. Psychological Science in the Public Interest, 20(1), 1–68. https://doi.org/10.1177/1529100619832930
2. Picard, R. W. (1997). *Affective Computing*. MIT Press. [Podstawa historyczna dziedziny; identyfikacja na podstawie tytułu pracy.]
3. Rozporządzenie Parlamentu Europejskiego i Rady (UE) 2024/1689 (AI Act), art. 5 ust. 1 lit. f, motyw 44. https://eur-lex.europa.eu/eli/reg/2024/1689/oj
4. Komisja Europejska. *Guidelines on prohibited AI practices* (część 7.2.3: wyjątki medyczne i bezpieczeństwa). https://ai-act-service-desk.ec.europa.eu/sites/default/files/2026-01/guide-prohibited_en.pdf

## Pochodzenie i zakres weryfikacji

Tekst jest redakcyjną syntezą `Synteza Modeli multimodalnych.docx` i `Zautomatyzowana_analiza_afektywna.pdf` z katalogu `files/inne/analizy/`. Zachowano obydwie tabele w wersji ujednoliconej. Zrezygnowano z niezweryfikowanych liczbowych prognoz rynku, uniwersalnych deklaracji dokładności i spekulatywnych scenariuszy AGI; nie przedstawiano ich jako ustaleń naukowych. Liczby sprzętowe i okna czasowe pozostawiono wyraźnie jako założenia projektowe pochodzące z dokumentów źródłowych. Dokument nie zawiera wyników badań własnych.