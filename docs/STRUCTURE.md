# Struktura repozytorium self

Repozytorium publikuje statyczną witrynę GitHub Pages. Jedynym katalogiem
aktualnych plików dla studentów jest `materials/`.

| Ścieżka | Funkcja |
| --- | --- |
| `index.html` | Strona główna z kołem kategorii i przełącznikiem języka |
| `docs/assets/`, `docs/data/`, `docs/images/` | Zasoby techniczne, dane i obrazy |
| `docs/archive/` | Archiwalne warianty witryny |
| `materials/index.html` | Pełna, statyczna lista materiałów do pobrania |
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
- Nowe pliki umieszczaj we właściwym katalogu przedmiotu i dodawaj do indeksu.
- Test `tests/test_materials.py` sprawdza **wszystkie pliki** oraz odnośniki
  i sygnalizuje nowy plik, którego nie wpisano na listę.
- Indeks zachowuje zwykły HTML, responsywną siatkę CSS, obsługę trybu
  jasnego i ciemnego oraz istniejące ścieżki pobierania.
- Walidacja: `python -m unittest discover -s tests -p "test_*.py" -v`.
  Po zmianach interfejsu również `bash tests/theme_switcher_static_check.sh`.
