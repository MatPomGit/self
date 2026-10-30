# self

Statyczna strona naukowa i dydaktyczna publikowana przez GitHub Pages.

- [Strona główna](https://matpomgit.github.io/self/)
- [Materiały dla studentów](https://matpomgit.github.io/self/materials/)
- [Biblioteka zasobów](https://matpomgit.github.io/self/library/)
- [Materiały WiRR](https://matpomgit.github.io/self/materials/wirr/)

## Dokumentacja

- [Struktura repozytorium](STRUCTURE.md)
- [Biblioteka i krótkie adresy](LIBRARY.md)
- [Publikacja wykładów WiRR](WIRR.md)
- [Zadania przeglądu](REVIEW_TASKS.md)

## Organizacja

Wszystkie lokalne materiały dla studentów umieszcza się w `materials/` z podziałem na przedmioty. `materials/index.html` jest prostą, statyczną listą plików. Dawne adresy stron HTML przekierowują do `materials/`. Krótkie adresy `f/NN/`, `p/NN/` i `h/NN/` pozostają bez zmian.

Wspólne zasoby serwisu znajdują się w `assets/`. Manifest `assets/library.json` wskazuje pliki w `materials/`.

Walidacja: `python3 tools/build_library.py --check` oraz `python3 -m unittest discover -s tests`.
