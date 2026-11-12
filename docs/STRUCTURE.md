# Struktura repozytorium self

Repozytorium publikuje statyczną witrynę GitHub Pages. Jedynym katalogiem
aktualnych plików dla studentów jest `files/`.

| Ścieżka | Funkcja |
| --- | --- |
| `index.html` | Strona główna z kołem kategorii i przełącznikiem języka |
| `docs/data/project-details.json` | Rozszerzone opisy, logotypy i opcjonalne linki projektów (PL/EN) |
| `docs/assets/images/projects/` | Grafiki projektów SVG/PNG/WebP |
| `docs/PROJECTS.md` | Instrukcja edycji kart i podglądów projektów |
| `docs/data/about.json` | Pełny opis osoby i pracy badawczej, po polsku (`pl`) i angielsku (`en`) |
| `docs/assets/`, `docs/data/`, `docs/images/` | Zasoby techniczne, dane i obrazy (w tym `docs/data/papers.md`) |
| `docs/archive/` | Archiwalne warianty witryny |
| `files/index.html` | Automatycznie uzupełniany przy budowaniu katalog; domyślnie aktualne PDF |
| `files/psychoinformatyka/index.html` | Strona psychoinformatyki |
| `files/informatyka-poznawcza/index.html` | Strona informatyki poznawczej |
| `files/robotyka-afektywna/index.html` | Strona robotyki afektywnej |
| `files/narzędzia-dla-programistów/` | Instrukcje NDP, strony HTML i narzędzia terminalowe |
| `files/wirtualna-i-rozszerzona-rzeczywistosc/` | Wykłady, laboratoria, bloki i konfiguracja WiRR |
| `files/programowanie-aplikacji-mobilnych/` | Wykłady, laboratoria i źródła PAM |
| `files/programowanie-gier-komputerowych/` | Laboratoria PGK |
| `files/informatyka-afektywna/` | Laboratoria IA |
| `files/seminaria-dyplomowe/` | Prezentacja i szablony pracy |
| `tests/` | Testy regresyjne i kontrola linków |

## Utrzymanie indeksu

- Odnośniki w `files/index.html` muszą wskazywać istniejące pliki w `files/`.
- Nowe pliki dodawaj tylko do właściwego katalogu w `files/`.
  `scripts/sync_materials.py --write` odkrywa je rekurencyjnie, naprawia
  jednoznaczne przeniesienia i uzupełnia istniejącą kartę przedmiotu lub
  tworzy nową. Pliki w `inne/` grupuje według podkatalogu.
- Oba workflowy uruchamiają generator **przed testami i publikacją**.
  Wynik trafia bezpośrednio do artefaktu Pages; CI nie tworzy automatycznych
  commitów. Pojawienie się nowego pliku nie powoduje błędu testu.
  Niejasne dopasowanie lub nieistniejący cel ręcznego linku nadal blokuje
  publikację, zamiast po cichu publikować niedziałający odnośnik.
- `tests/test_materials.py` weryfikuje wszystkie lokalne odnośniki i kompletność
  indeksu po aktualizacji. `tests/test_sync_materials.py` obejmuje brakujący,
  przeniesiony, nowy i niejednoznaczny plik oraz idempotencję generatora.
- Podczas pakowania strony `scripts/build_short_links.py` generuje krótkie strony
  podglądu dla PDF, np. `/files/ndp/lab04/` i `/files/wirr/w07/`.
  Główny odnośnik PDF w opublikowanym katalogu prowadzi do podglądu, a
  przycisk `PDF` zachowuje bezpośredni adres pliku do pobrania.
  Oryginalnych plików nie przenosi się, nie kopiuje ani nie modyfikuje.
- Indeks zachowuje zwykły HTML, oba motywy i istniejące ścieżki pobierania.
  Responsywne kolumny CSS (zwykle cztery na szerokim ekranie, dwie na średnim,
  jedna na telefonie) równoważą wysokość i pozwalają kartom zajmować tylko
  naturalnie potrzebne miejsce. Każda karta pozostaje w jednej kolumnie;
  wyeliminowano układ z szerokimi kartami generującymi puste obszary.
  Kolumny wewnątrz paneli mają zwartą, ograniczoną szerokość komórek, więc nazwy
  pozostają blisko siebie zamiast rozsuwać się na całą szerokość panelu. Mniejsze
  odstępy pionowe i poziome oraz zawijanie długich nazw zachowują czytelność.
  Układ działa bez dodatkowego JS.
- Karty są uporządkowane tematycznie: programowanie, XR i robotyka,
  informatyka/neuronauka, psychologia oraz materiały ogólne.
  Odnośniki do wykładów są niebieskawe, do laboratoriów zielonkawe.
  `scripts/classify_materials.py` rozpoznaje 16:9 i 4:3 jako wykłady,
  a A4 (pionowo lub poziomo) jako instrukcje. Odczytuje rozmiar pierwszej
  strony PDF (`pypdf`), slajdu PPTX lub strony DOCX. Pliki TeX/HTML z
  odpowiadającym PDF dziedziczą klasyfikację. Kolor według rozszerzenia ma
  pierwszeństwo nad oznaczeniem wykład/instrukcja: PPTX jest pomarańczowy,
  TeX fioletowy, HTML turkusowy. Pozostałe typy zachowują klasyfikację
  dokumentu lub domyślny kolor. Klasyfikację wykonuje workflow przed publikacją.

- Domyślnie widoczne są tylko PDF, a spośród plików o tym samym rdzeniu nazwy
  wygrywa najwyższy numer wersji `vX.Y.Z`. Pozostałe formaty i starsze wersje
  są dostępne po trzech kliknięciach przycisku w nagłówku (odstęp do 1,8 s).
  Kolejne trzy kliknięcia przywracają PDF; odświeżenie strony resetuje widok.
  Puste grupy i podgrupy są ukrywane. Bez JavaScriptu działa pełna lista.
- Walidacja: `python scripts/sync_materials.py --write && python scripts/sync_materials.py --check`,
  potem klasyfikacja rozmiarów i `python -m unittest discover -s tests -p "test_*.py" -v`.
  Po zmianach interfejsu również `node tests/test_materials_view.js` oraz
  `bash tests/theme_switcher_static_check.sh`.
