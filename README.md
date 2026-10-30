# self

Statyczna strona naukowa i dydaktyczna publikowana przez GitHub Pages.

- [Strona główna](https://matpomgit.github.io/self/)
- [Materiały dla studentów](https://matpomgit.github.io/self/materials/)
- [Struktura repozytorium](STRUCTURE.md)

## Organizacja

Aktualne strony HTML przedmiotów i laboratoriów znajdują się wyłącznie w `materials/`.
`materials/index.html` to prosty wykaz istniejących zasobów. Cztery strony laboratoriów
WiRR to `materials/wirr_blok_01.html` do `materials/wirr_blok_04.html`.
Niepublikowane szkice wykładów, aliasy `f/`, `h/`, `p/`, katalog
`library/` i generator aliasów zostały usunięte.

Pliki pomocnicze pozostają w `materials/bash/` i `materials/templates/`.
Zasoby techniczne strony pozostają w `assets/`.

Walidacja: `python3 -m unittest discover -s tests`.
