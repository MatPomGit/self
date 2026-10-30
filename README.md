# self

Statyczna witryna naukowa i dydaktyczna publikowana przez GitHub Pages.

- [Strona główna](https://matpomgit.github.io/self/)
- [Materiały dla studentów](https://matpomgit.github.io/self/materials/)
- [Struktura repozytorium](STRUCTURE.md)

## Zasady publikacji

Jedynym katalogiem aktualnych materiałów udostępnianych studentom jest `materials/`.
Punktem wejścia pozostaje `materials/index.html`, prosta strona HTML z listami linków
bez JavaScriptu, frameworków i generatora. Pozostałe strony przedmiotów znajdują się w
`materials/<przedmiot>/index.html`; sześć wycofanych stron Bash, LaTeX, Git, Vim,
Algorytmy i Aplikacje mobilne nie ma osobnych stron HTML. Laboratoria NDP w `materials/ndp_lab_NN.html`,
a cztery bloki WiRR w `materials/wirr_blok_01.html` do `materials/wirr_blok_04.html`.
Pliki pomocnicze umieszcza się w `materials/bash/` lub `materials/templates/`.
Usunięcie strony `materials/bash/index.html` nie usuwa skryptów Bash do pobrania.

Nie przywracaj przestarzałych katalogów `wirr/`, `lectures/`, `library/`,
`f/`, `h/`, `p/` ani niepublikowanych szkiców wykładów.
Nie publikuj w indeksie linków do plików, które nie istnieją w repozytorium.

## Modyfikacja materiałów

1. Umieść nową stronę HTML lub plik pomocniczy w odpowiednim miejscu w `materials/`.
2. Dodaj czytelny link do istniejącego pliku w `materials/index.html`. Nie używaj
   zewnętrznych generatorów indeksu.
3. Zachowaj prosty układ tekstowy i typografię: rozmiar bazowy 14 px, nagłówki
   hierarchiczne, widoczny stan fokusu klawiatury, układ na telefony.
4. Sprawdź odwołania względne po przeniesieniu plików i uruchom testy.

## Weryfikacja

```sh
python3 -m unittest discover -s tests
bash tests/theme_switcher_static_check.sh
```

Pierwsze polecenie sprawdza między innymi istnienie zasobów wymienionych
w indeksie, obecność stron laboratoriów oraz brak usuniętej infrastruktury aliasów.
Skrypt powłoki weryfikuje osobne zasoby interfejsu witryny.

Szczegółowy opis katalogów: [STRUCTURE.md](STRUCTURE.md).
