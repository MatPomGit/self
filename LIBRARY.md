# Biblioteka zasobów: `/self/library/`

Statyczny katalog dla GitHub Pages, bez backendu, kosztów API ani zewnętrznych skryptów.

## Adresy i nazewnictwo

- `/self/f/01`: **f** = file, dowolny plik do pobrania (CSV, ZIP, DOCX, itp.).
- `/self/p/01`: **p** = PDF, dokument podglądany w przeglądarce.
- `/self/h/01`: **h** = HTML, dokument lub strona z podglądem.
- `/self/library/`: publiczna wyszukiwarka wszystkich zasobów.

Identyfikator ma co najmniej dwie cyfry i nie jest ponownie przydzielany.
GitHub Pages automatycznie normalizuje adresy katalogowe do postaci z końcowym `/`.
Strony aliasów są prawdziwymi plikami `index.html`, dzięki czemu bezpośrednie linki nie zależą od obsługi stron 404.

## Dodawanie zasobów

1. Umieść opublikowany plik w repozytorium (np. `downloads/kurs-w01.pdf`), **albo** użyj pełnego adresu `https://...`. Nie publikuj danych niejawnych lub osobowych.
2. Dodaj wpis do `assets/library.json`, zachowując unikalną parę `type + id` i pola `title`, `description`, `category`, `source`, `updated`.
3. Wykonaj lokalnie `python3 tools/build_library.py`. Powstaną statyczne strony `f/NN/index.html`, `p/NN/index.html` lub `h/NN/index.html`.
4. Zweryfikuj `python3 tools/build_library.py --check` oraz `python3 -m unittest discover -s tests -p 'test_library.py'`.
5. Zatwierdź manifest, pliki i wygenerowane aliasy razem, a następnie opublikuj przez standardowy GitHub Pages projektu.

Przykładowy rekord:

```json
{
  "type": "p",
  "id": "02",
  "title": "Wykład 1",
  "description": "Prezentacja PDF",
  "category": "Dydaktyka",
  "source": "downloads/wyklad-01.pdf",
  "updated": "2026-10-24"
}
```

`downloads/library-template.csv` zawiera przykładowe metadane do planowania nowych pozycji.
Plik CSV **nie** jest automatycznie importowany do manifestu JSON.

## Zasady techniczne i bezpieczeństwo

- Aplikacja działa w przeglądarce bez frameworków, API, analityki i serwera aplikacyjnego. Katalog jest ładowany jednorazowo i pokazywany w porcjach po 24 rekordy.
- Dopuszczalne źródła: bezpieczne ścieżki względne w repozytorium albo `https://`. Walidacja blokuje `../`, protokoły `http:` i `javascript:` oraz kolizje adresów.
- Informacje z manifestu są wyświetlane przez `textContent` (nie `innerHTML`). Strony HTML są osadzane w `iframe sandbox="allow-scripts"` bez `allow-same-origin`; treść można też otworzyć bezpośrednio.
- Pobieranie przez atrybut `download` działa dla zasobów z tej samej domeny. Zewnętrzne PDF są otwierane w serwisie źródłowym, który może blokować osadzanie w `iframe`.
- Dokumenty większe od limitów repozytorium GitHub i zasoby intensywnie pobierane powinny mieć własny hosting/CDN lub stabilny zewnętrzny link; GitHub Pages nie jest nieograniczonym magazynem plików.
- Wpisy publiczne są dostępne anonimowo. Krótki, trudny do odgadnięcia lub nieindeksowany link **nie** stanowi kontroli dostępu. Nie dodawaj plików poufnych, kodów dostępowych ani danych studentów.
- Utrzymuj istniejące identyfikatory po zmianie pliku. Gdy zasób znika, zachowaj alias z informacją o archiwizacji lub poprawnym przekierowaniem; nie przydzielaj identyfikatora innej treści.
