# self

Witryna naukowa i dydaktyczna publikowana przez GitHub Pages.

- [Strona główna](https://matpomgit.github.io/self/)
- [Materiały dla studentów](https://matpomgit.github.io/self/materials/)
- [Struktura repozytorium](docs/STRUCTURE.md)

## Zasady publikacji

Jedynym katalogiem aktualnych materiałów udostępnianych studentom jest `materials/`.
Punktem wejścia pozostaje `materials/index.html`, prosta strona HTML z listami linków
bez JavaScriptu, frameworków i generatora. Pozostałe strony przedmiotów znajdują się w
`materials/<przedmiot>/index.html`;

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

## Korekty układu (30.10.2026)

Stopka strony głównej używa czcionki `0.6rem`. W tytule zastosowano twardą
spację po spójniku „i”, aby zachować go w jednym wierszu z „robotyka”.
Kolumna tytułowa jest przesunięta o 18 px w górę (8 px na węższych ekranach).
Maksymalne wymiary koła kategorii zwiększono o 10% i zachowano ograniczenia
zależne od wysokości okna; na bardzo małych ekranach wielkość koła może być
mniejsza ze względu na przestrzeń dostępną w widoku.

## Interakcja koła (30.10.2026)

Koło powiększono o 20% względem poprzedniej wersji (z limitami wysokości
viewportu). Portret powiększono o 30%, a blok tekstowy przesunięto wyżej.
Podświetlenie głównej kategorii jest utrzymywane przez klasę `.grp.open`
podczas przemieszczania kursora między podkategoriami; zamknięcie pozostaje
opóźnione o 650 ms. Podtytuły wewnątrz głównych segmentów nadal reagują
wyłącznie na najechanie lub fokus samego segmentu.

## Wersjonowanie witryny

Stopka `index.html` zawiera numer wersji po prawej stronie, obecnie `v1.0.0`.
To pierwsza jawnie oznaczona wersja witryny; wcześniejsze wydania nie miały
numeru wersji. Przy kolejnych publikowanych zmianach należy aktualizować
numer w widocznym tekście oraz etykiecie dostępności `aria-label`.

## Dopasowanie koła do okna

Koło startowe pomniejszono o około 12%, przesunięto 20 px w górę
(8 px na ekranach wąskich) i ograniczono jego wymiar w zależności od
wysokości okna. Układ na bardzo małych ekranach może nadal wymagać
przewijania w celu zachowania czytelności.

## Dyskretna animacja koła

Gdy żaden segment nie jest aktywny, cienki fragment obrysu koła wykonuje
pełny obrót zgodnie z ruchem wskazówek zegara w 12 sekund.
Po najechaniu lub przejściu fokusu na kategorię efekt znika; uwzględniono
`prefers-reduced-motion`, bez bibliotek zewnętrznych.

## Wersja v1.0.1

Animowany obrys biegnie poza kołem (promień 203 względem promienia
segmentów 200), z pięcioma odcinkami malejącej przezroczystości tworzącymi
ogon. W sekcji Kontakt dodano odnośnik do profilu ORCID.
Każda następna zmiana publikowanej strony wymaga zwiększenia numeru wersji
w stopce i aktualizacji etykiety dostępności.

## Wersja v1.0.2

Promień animowanego obrysu zmniejszono z 203 do 200 jednostek SVG,
aby pokrywał się z zewnętrzną krawędzią segmentów koła.
Dostosowano również długość wzorca kreskowania do nowego obwodu.

## Wersja v1.0.3

Zwiększono widoczność animowanego obrysu: krycie czoła 72% (`opacity: .72`),
a ogon ma dziewięć odcinków zamiast pięciu. Długość odcinka wynosi
18 jednostek SVG, promień pozostaje 200, czas obrotu 12 sekund.

## Wersja v1.1.0: jedna witryna, rozdzielone dane

Osobne podstrony projektów i publikacji zastąpiono panelami strony głównej
ładowanymi z `docs/data/projects.json` i `docs/data/publications.json`.
Zachowano 17 wpisów projektowych (w tym 6 już z głównej strony) oraz 25 wpisów publikacji.
Usunięto powielone szablony HTML z `subpages/`. Strona `materials/`
pozostaje samodzielna i wykorzystuje lekki grid CSS z czterema kolumnami
na dużych ekranach, dwiema na średnich i jedną na telefonach.

Dawne odnośniki do usuniętych podstron zastąpiono przejściem do panelu
`#publikacje`; archiwalna strona kieruje do tego samego panelu.

## Wersja v1.1.1

Opis profilu na stronie głównej zmieniono na syntetyczny opis kierunków badań.
W kole kategorii zmieniono kolejność: Projekty zajmują poprzednie miejsce
Badań, Publikacje miejsce Projektów, a Badania miejsce Publikacji.
Publikacje są zwartą listą z kopiowaniem cytowania i BibTeX. Dane bibliograficzne
pochodzą z `docs/data/publications.json`; nieznane pola nie są dopowiadane.

## Wersja v1.1.2

Zakładkę Badania uzupełniono o opis profilu naukowego, metod pracy,
sześć rozwiniętych specjalizacji i cel integrujący kierunki badawcze.
Zachowano spójność wizualną ze stroną główną.

## Wersja v1.1.3

Na widokach szczegółowych usunięto powieloną nawigację: przycisk
„Strona główna” i poziome zakładki. Powrót zapewnia nazwisko w nagłówku.
Nagłówek przesunięto o 14 px w prawo; zmniejszono odstęp nad zawartością
paneli i poprawiono etykiety dostępności sekcji.

## Wersja v1.1.4

Opis zakładki Badania zastąpiono rozbudowaną autobiograficzną prezentacją
profilu naukowego, kompetencji inżynierskich i robotyki afektywnej na podstawie
tekstu właściciela. Zrezygnowano z listy określanej jako „specjalizacje”.

## Wersja v1.1.5

Publikacje: ciaśniejsza lista, nowy filtr `In progress` zawierający linki
wyłącznie do pięciu publicznych stron ARC (strony projektów, bez sugerowania
statusu recenzowanej publikacji). Przegląd wykazu uczelnianego PRz wykazał
25 pozycji odpowiadających 25 pozycjom JSON. Ostatnia pozycja uczelnianego
wykazu podaje w treści rok 2017 przy nagłówku 2016; zachowano dane pierwotne.

## Wersja v1.2.0

Zakładka In progress prezentuje planowane manuskrypty z pięciu publicznych
projektów ARC, uporządkowane malejąco według szacunkowego postępu prac.
Dane: `docs/data/in-progress.json`, wartości 0–100% to redakcyjna ocena
przygotowania do zgłoszenia, nie zweryfikowany KPI ani szansa akceptacji.
JFR dla S4D-TAM ma potwierdzony wybór; inne czasopisma są propozycjami,
które wymagają osobnego zatwierdzenia i kontroli wymagań redakcyjnych.
Wpisy HOLD pozostawiono jako 0%, nie przedstawiając ich jako aktywnych prac.

## Wersja v1.2.1

Naprawiono brakujący plik `docs/data/in-progress.json` (powodował błąd
HTTP 404), uzupełniono każdy z 26 wpisów o krótki opis celu, badania i
rezultatu. Czasopisma pozostają widoczne także jako propozycje. Panel
szczegółów jest wyrównany do góry zamiast do środka wysokości okna.

## Wersja v1.2.2

Listę manuskryptów zagęszczono; pełny tytuł jest pierwszy, nazwa projektu
w osobnym wierszu. Każda pozycja pokazuje kolejny krok, planowane czasopismo
z linkiem i punktacją (nieweryfikowane wartości jako „do weryfikacji”).
W nagłówku sekcji Publikacje obok nazwiska pojawia się jej tytuł.
Ocena następnego kroku ma charakter redakcyjny; nie oznacza stanu potwierdzonego
przez ukończone eksperymenty. Punktację podaje się wg wykazu 2024, nie nowego 2027.

## Wersja v1.2.4

Pasek postępu przeniesiono do wiersza tytułu manuskryptu i wyrównano
do prawej krawędzi; usunięto podwójny tytuł panelu Publikacje.
Nagłówek zawiera pogrubione „/ Publikacje”, a etykieta czasopisma brzmi
„Docelowe czasopismo”.
