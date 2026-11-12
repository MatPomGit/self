# Archiwum materiałów `files/ignored/`

**Reguła trwała:** żaden plik z `files/ignored/` ani jego podkatalogów nie może być wyświetlany na stronie `/files/`, generować adresu skróconego PDF ani trafić do artefaktu GitHub Pages.

Archiwum istnieje **wyłącznie w repozytorium i jego historii**. Ponieważ GitHub może udostępniać zawartość publicznego repozytorium, nie należy umieszczać tam materiałów poufnych.

## Przeniesione źródła i nowe publikacje

| Źródła archiwalne | Nowe pliki do pobrania |
| --- | --- |
| `files/ignored/inne/analizy/Synteza Modeli multimodalnych.docx`; `Zautomatyzowana_analiza_afektywna.pdf` | `files/inne/analizy/analiza_afektywna.docx` oraz `.pdf` |
| `files/ignored/inne/analizy/Isaac_Lab.docx`, `Isaac_Lab.pdf`, `Isaac Lab i bliźniaki cyfrowe.pdf` | `files/inne/analizy/isaac_lab.docx` oraz `.pdf` |

Nowe DOCX/PDF są generowane z kanonicznych źródeł `docs/consolidated/analiza_afektywna.md` i `docs/consolidated/isaac_lab.md` przez `scripts/build_consolidated_downloads.py`. W ten sposób oba formaty opisują tę samą, zredagowaną wersję.

## Implementacja

- `scripts/sync_materials.py`: katalog `ignored` nie jest częścią publicznego inwentarza.
- `scripts/build_short_links.py`: PDF-y z `ignored` nie generują widoków ani aliasów.
- `scripts/preflight_materials.py`: archiwalne pliki nie są rozważane jako aktywne materiały.
- `tests/test_materials.py` i testy regresyjne: archiwum nie jest wymagane w wykazie publicznych plików.
- `.github/workflows/restore-original-pages.yml`: po skopiowaniu katalogu `files` do `_site` katalog `_site/files/ignored` jest usuwany **przed** tworzeniem krótkich linków i wdrożeniem.
- Wsteczne audyty nadal mogą czytać oryginały z `files/ignored/inne/analizy/`, lecz nie mogą publikować ich w indeksie.

Zmiana starych adresów źródłowych będzie oznaczała brak bezpośredniego pobierania archiwalnych PDF/DOCX z Pages; nowe publiczne adresy są oparte na ścieżkach wyżej. Archiwalne bloby pozostają dostępne poprzez historię Git.


## Opracowania uzupełniające bez zastępowania źródeł

`files/inne/analizy/telediagnostyka_ndd.docx` oraz `.pdf` są generowane z `docs/consolidated/telediagnostyka_ndd.md`. Jest to nowa synteza tematyczna dwóch raportów NDD, a nie usunięcie treści o odrębnych celach. Oryginały `tele_ndd.docx`, `tele_ndd.pdf`, `teled_ndd.docx` i `teled_ndd.pdf` pozostają dostępne do osobnej decyzji redakcyjnej. Nie przenosić ich automatycznie do `files/ignored/`.

Rozszerzenie `docs/consolidated/isaac_lab.md` do wersji 1.1.0 uzupełnia już istniejące pobieralne `isaac_lab.docx` i `isaac_lab.pdf`. Pliki `isaac_sim.docx` i `isaac_sim_pojecia.pdf` pozostają osobnymi źródłami, ponieważ zawierają dodatkowy kontekst techniczny i słownik zależny od wersji API. Ich archiwizacja nie została zatwierdzona.
