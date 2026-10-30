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
