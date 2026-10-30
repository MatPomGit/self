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
