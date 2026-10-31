# Struktura repozytorium self

Repozytorium zawiera dwujęzyczną witrynę Zensical publikowaną przez GitHub Pages. Pliki dla studentów
muszą znajdować się w obrębie `materials/`; pliki infrastruktury witryny
są od nich rozdzielone.

| Ścieżka | Funkcja |
| --- | --- |
| `zensical.toml`, `requirements-docs.txt` | Konfiguracja i zależności Zensical |
| `website/pl/`, `website/en/` | Odpowiadające sobie strony w obu językach |
| `website/stylesheets/` | Styl witryny Zensical |
| `scripts/site_data.py` | Przygotowanie wspólnych danych przed budowaniem obu języków |
| `website/overrides/partials/alternate.html` | Przełącznik języka zachowujący bieżącą stronę |
| `scripts/build_site.py` | Budowanie i zachowanie publicznych adresów materiałów |
| `.github/workflows/docs.yml` | Walidacja i ręczna publikacja Pages z `main` |
| `index.html` | Zachowana strona HTML, publikowana jako `legacy.html` |
| `docs/data/projects.en.json`, `docs/data/in-progress.en.json` | Tłumaczenia opisów projektów i manuskryptów |
| `docs/data/projects.json`, `docs/data/publications.json` | Dane projektów i publikacji dla paneli strony głównej |
| `materials/index.html` | Indeks aktualnych materiałów, responsywny grid CSS |
| `materials/<przedmiot>/index.html` | Strony czterech pozostałych przedmiotów |
| `materials/ndp_lab_02.html` do `materials/ndp_lab_06.html` | Pięć laboratoriów NDP |
| `materials/wirr_blok_01.html` do `materials/wirr_blok_04.html` | Cztery bloki WiRR |
| `materials/bash/` | Pomocnicze programy terminalowe; bez osobnej strony HTML |
| `materials/templates/` | Szablony do pobrania |
| `docs/assets/css/`, `docs/assets/js/`, `docs/assets/vendor/` | Wspólne zasoby techniczne witryny |
| `docs/images/`, `docs/papers.md` | Zdjęcia i dokumentacja |
| `docs/archive/` | Historyczne strony, przekierowanie i poprzednia strona główna |
| `tests/` | Testy regresyjne i statyczne |

Usunięto osobne strony HTML przedmiotów: Bash, LaTeX, Git, Vim,
Algorytmy i struktury danych oraz Aplikacje mobilne.
Ich dawne adresy nie są utrzymywane jako przekierowania.

## Typografia indeksu

`materials/index.html` ma niewielki, lokalny arkusz CSS w znaczniku
`<style>`. Domyślny tekst ma 14 px i interlinię 1,5;
`h1` ma 1,55 rem, a `h2` 1,1 rem. Maksymalna szerokość treści wynosi
780 px. Na ekranach do 600 px zmniejszają się marginesy boczne.
Pozostaw zwykłe odnośniki HTML z podkreśleniem i widocznym fokusem.
Nie dodawaj kart, animacji ani skryptów do indeksu.

## Reguły utrzymania

- Nowe materiały studenckie umieszczaj wyłącznie w `materials/`.
- Lista `materials/index.html` powinna wskazywać wyłącznie opublikowane pliki.
- Zachowaj nazwy i istniejące ścieżki aktualnych laboratoriów, aktualizując
  linki przy świadomym przeniesieniu.
- Nie odtwarzaj `wirr/`, `lectures/wirr/`, `materials/wirr/lectures/`,
  `library/`, `f/`, `h/`, `p/` ani usuniętego generatora aliasów.
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

Projekty i publikacje są renderowane na podstronach Zensical z danych JSON w `docs/data/`. Zachowana strona HTML używa tych samych danych we własnych panelach. Materiały studenckie pozostają w `materials/`.

## Zensical i języki

Wynik `site/` nie jest wersjonowany. Strony polskie są publikowane w katalogu
głównym witryny, angielskie w `en/`. Przełącznik Zensical w prawym
górnym rogu nagłówka zachowuje bieżącą podstronę. Każda strona ma odpowiednik
w obu językach. Nie włączaj zastępowania brakujących tłumaczeń treścią polską.

Przy zmianie danych projektów lub manuskryptów zaktualizuj też ich tłumaczenia.
Uruchom `python scripts/build_site.py` z zainstalowanymi zależnościami
`requirements-docs.txt`. Testy `test_docs.py` sprawdzają wynik budowania,
przełącznik, lokalne odnośniki, kompletność tłumaczeń i zgodność materiałów.
Instrukcje publikacji znajdują się w głównym README.
