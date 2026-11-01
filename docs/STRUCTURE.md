# Struktura repozytorium self

Repozytorium publikuje statyczną witrynę GitHub Pages. Jedynym katalogiem
aktualnych plików dla studentów jest `materials/`.

| Ścieżka | Funkcja |
| --- | --- |
| `index.html` | Strona główna z kołem kategorii i przełącznikiem języka |
| `docs/assets/`, `docs/data/`, `docs/images/` | Zasoby techniczne, dane i obrazy |
| `docs/archive/` | Archiwalne warianty witryny |
| `materials/index.html` | Automatycznie uzupełniany przy budowaniu katalog; domyślnie aktualne PDF |
| `materials/psychoinformatyka/index.html` | Strona psychoinformatyki |
| `materials/informatyka-poznawcza/index.html` | Strona informatyki poznawczej |
| `materials/robotyka-afektywna/index.html` | Strona robotyki afektywnej |
| `materials/narzędzia-dla-programistów/` | Instrukcje NDP, strony HTML i narzędzia terminalowe |
| `materials/wirtualna-i-rozszerzona-rzeczywistosc/` | Wykłady, laboratoria, bloki i konfiguracja WiRR |
| `materials/programowanie-aplikacji-mobilnych/` | Wykłady, laboratoria i źródła PAM |
| `materials/programowanie-gier-komputerowych/` | Laboratoria PGK |
| `materials/informatyka-afektywna/` | Laboratoria IA |
| `materials/seminaria-dyplomowe/` | Prezentacja i szablony pracy |
| `materials/templates/` | Szablon CSV |
| `tests/` | Testy regresyjne i kontrola linków |

## Utrzymanie indeksu

- Odnośniki w `materials/index.html` muszą wskazywać istniejące pliki w `materials/`.
- Nowe pliki dodawaj tylko do właściwego katalogu w `materials/`.
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
- Indeks zachowuje zwykły HTML, responsywną siatkę CSS, obsługę trybu
  jasnego i ciemnego oraz istniejące ścieżki pobierania.
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
