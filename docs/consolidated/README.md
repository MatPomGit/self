# Ujednolicone raporty – źródła redakcyjne

**Wersja:** 1.0.0, 12.11.2026. **Plan:** [Issue #138](https://github.com/MatPomGit/self/issues/138), [PR #140](https://github.com/MatPomGit/self/pull/140) (zależny od #139).

W tym katalogu znajdują się **dwa kompletne raporty po redakcyjnej konsolidacji**, a nie mechanicznie połączone oryginały:

1. [Zautomatyzowana analiza afektywna](analiza_afektywna.md) – połączenie treści `Synteza Modeli multimodalnych.docx` i `Zautomatyzowana_analiza_afektywna.pdf`. Zachowano obie tabele; poprawiono rozróżnienie pomiaru mimiki i inferencji psychologicznej, metody multimodalne, kontekst zastosowań oraz prawo UE.
2. [Isaac Lab, AGILE i cyfrowe bliźniaki](isaac_lab.md) – połączenie `Isaac_Lab.docx` i `Isaac Lab i bliźniaki cyfrowe.pdf`. Zachowano tabelę komponentów i treść o AGILE, Isaac Lab-Arena, afordancjach, Cosmos i sim-to-real; skorygowano pozycję AGILE jako projektu na Isaac Lab i uwzględniono architekturę 3.x.

## Metoda

- Powtórzone definicje i wprowadzenia ujednolicono do jednej narracji.
- Liczby niepoparte weryfikowalnym protokołem oznaczono jako przybliżenia projektowe albo usunięto z zestawu twierdzeń naukowych.
- Przedstawiono bibliografię obejmującą źródła pierwotne i dokumentację techniczną; nie uznaje się różnych publikacji za tę samą próbę badawczą.
- Źródłowe dokumenty w `files/inne/analizy/` **nie zostały zmienione, usunięte ani przeniesione**.
- Pliki Markdown są kanoniczną wersją redakcyjną tej zmiany. Użytkownik otrzymuje także wygenerowane DOCX i PDF; dopóki nie zostanie zatwierdzona migracja starych URL, nie zastępują one plików produkcyjnych.

## Kontrola odbioru

- [x] Spójny układ, definicje, wnioski i bibliografia obu raportów.
- [x] W obu dokumentach zachowano tabele ze źródeł oraz ich sens, z kontekstem interpretacyjnym.
- [x] Generacja edytowalnych DOCX i PDF; odpowiednio 5 i 4 strony, wizualna kontrola układu.
- [x] Testy redakcyjne w CI.
- [ ] Niezależna inspekcja ilustracji z oryginalnych PDF; obecny tekst nie odtwarza nieopisanych obrazów.
- [ ] Decyzja o docelowych publicznych URL i ewentualnej archiwizacji starych formatów.

Raporty mają charakter przeglądowy; nie zawierają wyników badań własnych i nie są rekomendacją do diagnozowania emocji.
