# Ujednolicone raporty – źródła redakcyjne

**Wersja:** 1.1.0, 12.11.2026. **Plan:** [Issue #138](https://github.com/MatPomGit/self/issues/138), [PR #140](https://github.com/MatPomGit/self/pull/140) (zależny od #139).

W tym katalogu znajdują się **dwa raporty zaktualizowane po konsolidacji i nowa synteza porównawcza**, a nie mechanicznie połączone oryginały:

1. [Zautomatyzowana analiza afektywna](analiza_afektywna.md) – połączenie treści `Synteza Modeli multimodalnych.docx` i `Zautomatyzowana_analiza_afektywna.pdf`. Zachowano obie tabele; poprawiono rozróżnienie pomiaru mimiki i inferencji psychologicznej, metody multimodalne, kontekst zastosowań oraz prawo UE.
2. [Isaac Lab, AGILE i cyfrowe bliźniaki](isaac_lab.md) – pierwotne połączenie `Isaac_Lab.docx` i `Isaac Lab i bliźniaki cyfrowe.pdf`, następnie rozszerzone o unikalne treści `isaac_sim.docx` i `isaac_sim_pojecia.pdf`. Uaktualniono migrację API do Isaac Sim 6.x, sensory RTX, ROS 2, DDS i Replicator.

3. [Telediagnostyka ADHD i ASD](telediagnostyka_ndd.md) – niezależna synteza porównawcza `tele_ndd.docx` i `teled_ndd.docx`, rozdzielająca badania n = 1688, 342 i 704 oraz miary i schematy walidacji. To **opracowanie uzupełniające**, nie automatyczne zastąpienie obu długich tekstów.

## Metoda

- Powtórzone definicje i wprowadzenia ujednolicono do jednej narracji.
- Liczby niepoparte weryfikowalnym protokołem oznaczono jako przybliżenia projektowe albo usunięto z zestawu twierdzeń naukowych.
- Przedstawiono bibliografię obejmującą źródła pierwotne i dokumentację techniczną; nie uznaje się różnych publikacji za tę samą próbę badawczą.
- Oryginały wykorzystywane w tym etapie (`isaac_sim.docx`, `isaac_sim_pojecia.pdf`, `tele_ndd.docx`, `teled_ndd.docx`) pozostają nienaruszone. Oryginały dwóch starszych scaleń, wymienione w `docs/FILES_ARCHIVE_POLICY.md`, przeniesiono wcześniej do `files/ignored/`.
- Pliki Markdown są kanoniczną wersją redakcyjną tej zmiany. Wygenerowane DOCX i PDF mają odpowiadać aktualnym źródłom Markdown. Synteza NDD jest dodatkowym materiałem, bez usuwania istniejących plików źródłowych.

## Kontrola odbioru

- [x] Spójny układ, definicje, wnioski i bibliografia raportów.
- [x] W obu dokumentach zachowano tabele ze źródeł oraz ich sens, z kontekstem interpretacyjnym.
- [x] Generacja edytowalnych DOCX i PDF; odpowiednio 5 i 4 strony, wizualna kontrola układu.
- [x] Testy redakcyjne w CI.
- [ ] Niezależna inspekcja ilustracji z oryginalnych PDF; obecny tekst nie odtwarza nieopisanych obrazów.
- [ ] Ocena wizualna aktualnych eksportów, kontrola tabel i odnośników. Odrębna decyzja o ewentualnej przyszłej archiwizacji raportów NDD.

Raporty mają charakter przeglądowy; nie zawierają wyników badań własnych i nie są rekomendacją do diagnozowania emocji.
