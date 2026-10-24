# self

Statyczna strona naukowa i dydaktyczna publikowana przez GitHub Pages.

- [Strona główna](https://matpomgit.github.io/self/)
- [Biblioteka materiałów](https://matpomgit.github.io/self/library/)
- [Materiały WiRR](https://matpomgit.github.io/self/wirr/)

## Dokumentacja

- [Struktura repozytorium](STRUCTURE.md)
- [Biblioteka i krótkie adresy](LIBRARY.md)
- [Publikacja wykładów WiRR](WIRR.md)
- [Zadania przeglądu](REVIEW_TASKS.md)

## Organizacja

Zasoby CSS, JS i zależności znajdują się w `assets/css/`, `assets/js/` i `assets/vendor/`. Publiczne strony HTML pozostają pod dotychczasowymi adresami, aliasy `/f/`, `/p/`, `/h/` są generowane i nie należy przenosić ich ręcznie.

Walidacja: `python3 tools/build_library.py --check` oraz `python3 -m unittest discover -s tests`.
