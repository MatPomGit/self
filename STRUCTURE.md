# Struktura repozytorium self

| Ścieżka | Przeznaczenie |
| --- | --- |
| `index.html`, `projects.html`, `publications.html` | Główne strony serwisu |
| `materials/index.html` | Jedyny wykaz aktualnych materiałów dla studentów |
| `materials/<przedmiot>/index.html` | Strony przedmiotów |
| `materials/ndp_lab_02.html` do `materials/ndp_lab_06.html` | Laboratoria NDP |
| `materials/wirr_blok_01.html` do `materials/wirr_blok_04.html` | Laboratoria WiRR |
| `materials/bash/`, `materials/templates/` | Pliki pomocnicze do pobrania |
| `assets/` | Zasoby techniczne CSS/JS |
| `docs/`, `archive/` | Grafiki, dokumenty, archiwum |
| `tests/` | Testy lokalnych odwołań i zasobów |

W repozytorium nie utrzymuje się osobnej biblioteki aliasów ani szkiców wykładów WiRR.
Nie dodawaj nowych stron dydaktycznych poza `materials/`.
Po modyfikacjach wykonaj `python3 -m unittest discover -s tests`.
