# Karty projektów i logotypy

## Gdzie edytować

| Plik | Zawartość |
| --- | --- |
| `docs/data/projects.json` | Główna lista projektów: `phase`, `title`, `period`, `description` |
| `docs/data/projects.en.json` | Tłumaczenia tytułów, dat i skrótów, dopasowywane przez `sourceTitle` |
| `docs/data/project-details.json` | Rozwinięte dane, logo i opcjonalne linki |
| `docs/assets/images/projects/` | Właściwe pliki logo |

## Przykład

Dodaj plik `docs/assets/images/projects/przyklad.svg` i zaktualizuj obiekt istniejącego projektu:

```json
{
  "Przykładowy projekt": {
    "logo": "docs/assets/images/projects/przyklad.svg",
    "links": [
      {
        "label": "Strona projektu",
        "url": "https://example.org/project"
      }
    ],
    "pl": {
      "focus": "Cel badań opisany bez deklarowania niepotwierdzonych wyników.",
      "methods": ["Metoda 1", "Metoda 2"],
      "outcomes": ["Zweryfikowany rezultat"]
    },
    "en": {
      "focus": "Research focus without unverified claims.",
      "methods": ["Method 1", "Method 2"],
      "outcomes": ["Verified outcome"]
    }
  }
}
```

Przykładowy blok służy wyłącznie jako wzór; nie dopisuj do produkcyjnego JSON projektu o nieistniejącym tytule.

## Zasady

- Nazwa właściwości projektu musi dokładnie odpowiadać `title` w głównym `projects.json`. Tekst dla języka EN pochodzi z `projects.en.json` i z sekcji `en` metadanych.
- `logo` jest opcjonalne, dozwolone są **lokalne** ścieżki `docs/assets/images/projects/<nazwa>.svg|png|webp` zapisane małymi literami, bez spacji. Nie umieszczaj zewnętrznych URL jako logo.
- Zalecane proporcje 1:1. Obraz jest wyświetlany przez `object-fit: contain` bez przycinania; na jasnym i ciemnym motywie sprawdź kontrast.
- Jeśli `logo` nie podano, widoczny jest automatyczny monogram. Niepoprawne lub niezaładowane obrazy również mają monogram zastępczy.
- `focus`, `methods`, `outcomes` są opcjonalne, ale używaj tylko zweryfikowanych informacji. Nie sugeruj ukończenia publikacji ani wyników, gdy trwają prace.
- `links` jest opcjonalną listą obiektów `{ "label": "...", "url": "https://..." }`; dozwolone są tylko adresy HTTPS. Linki otwierają się w nowej karcie z `noopener noreferrer`.
- Wszystkie dane i obrazy w tych folderach zostaną opublikowane na stronie. Nie wpisuj tu wewnętrznych workflow agentów, danych poufnych i operacyjnych instrukcji autopilota.

## Kontrola zmian

```bash
python -m unittest tests.test_projects -v
node --check docs/assets/js/project-preview.js
```

Pełne testy uruchamia workflow `restore-original-pages.yml` przed opublikowaniem do GitHub Pages. Testy Pythona sprawdzają kompletność danych PL/EN, format ścieżek logo, obecność plików i ich podstawowe sygnatury oraz składnię odnośników HTTPS.

## Zasady publicznej prezentacji portfolio

- W panelach szczegółów **nie publikujemy odnośników do repozytoriów kodu** (ani publicznych, ani prywatnych). Dopuszczalne są odrębne, potwierdzone strony informacyjne projektów, jeżeli zostaną świadomie dodane.
- Gdy materiałów źródłowych brakuje, opisuj obszar, techniki i możliwy zakres badawczy, ale nie przedstawiaj projektu jako zwalidowanego ani nie przypisuj mu niepotwierdzonych osiągnięć.
- Pola `outcomes` służą wyłącznie do rezultatów udokumentowanych. W pozostałych projektach pozostają puste lub pominięte.
