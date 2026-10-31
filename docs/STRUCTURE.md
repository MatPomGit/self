# Struktura repozytorium self

Repozytorium zawiera statyczną witrynę GitHub Pages. Pliki dla studentów
muszą znajdować się w obrębie `materials/`; pliki infrastruktury witryny
są od nich rozdzielone.

| Ścieżka | Funkcja |
| --- | --- |
| `index.html` | Główna strona witryny |
| `docs/assets/js/site-i18n.js` | Przełącznik PL/EN i słownik tekstów strony z kołem |
| `docs/data/projects.en.json`, `docs/data/in-progress.en.json` | Tłumaczenia projektów i manuskryptów |
| `tests/test_language.js` | Regresja przełącznika, koła i danych w obu językach |
| `docs/data/projects.json`, `docs/data/publications.json` | Dane projektów i publikacji dla paneli strony głównej |
| `materials/index.html` | Indeks aktualnych materiałów, responsywny grid CSS |
| `materials/<przedmiot>/index.html` | Strony czterech pozostałych przedmiotów |
| `materials/ndp/ndp_lab_02.html` do `materials/ndp_lab_06.html` | Pięć laboratoriów NDP |
| `materials/wirr/wirr_blok_01.html` do `materials/wirr_blok_04.html` | Cztery bloki WiRR |
| `materials/ndp/bash/` | Pomocnicze programy terminalowe; bez osobnej strony HTML |
| `materials/templates/` | Szablony do pobrania |
| `docs/assets/css/`, `docs/assets/js/`, `docs/assets/vendor/` | Wspólne zasoby techniczne witryny |
| `docs/images/`, `docs/papers.md` | Zdjęcia i dokumentacja |
| `docs/archive/` | Historyczne strony, przekierowanie i poprzednia strona główna |
| `tests/` | Testy regresyjne i statyczne |

Algorytmy i struktury danych oraz Aplikacje mobilne.
Ich dawne adresy nie są utrzymywane jako przekierowania.

## Typografia indeksu

`materials/index.html` ma niewielki, lokalny arkusz CSS w znaczniku
`<style>`. Domyślny tekst ma 14 px i interlinię 1,5;
`h1` ma 1,55 rem, a `h2` 1,1 rem. Maksymalna szerokość treści wynosi
780 px. Na ekranach do 600 px zmniejszają się marginesy boczne.
Pozostaw zwykłe odnośniki HTML.
Nie dodawaj kart, animacji ani skryptów do indeksu.

## Reguły utrzymania

- Nowe materiały studenckie umieszczaj wyłącznie w `materials/`.
- Lista `materials/index.html` powinna wskazywać wyłącznie opublikowane pliki.
- Zachowaj nazwy i istniejące ścieżki aktualnych laboratoriów, aktualizując
  linki przy świadomym przeniesieniu.
- Po każdej zmianie uruchom `python3 -m unittest discover -s tests`;
  przy zmianach interfejsu także `bash tests/theme_switcher_static_check.sh`.

## Uwagi historyczne

`REVIEW_TASKS.md` usunięto po sprawdzeniu jego uwag. Historyczne skrypty
w `docs/assets/js/` są powiązane z archiwalną stroną, nie z obecną stroną główną.
Test statyczny pilnuje `aria-selected` i czasu przewijania 416 ms;
nie zastępuje on testów E2E.

## Lokalizacja plików

`docs/assets/` zawiera techniczne pliki CSS, JS i vendor, `docs/images/`
zdjęcia, `docs/archive/` dawne wersje strony. Publiczny adres głównej strony HTML
w katalogu głównym i materiały w `materials/` nie zmieniają się.

Projekty i publikacje są prezentowane bez osobnych podstron HTML z danych JSON w `docs/data/`. Materiały studenckie pozostają w `materials/`.
