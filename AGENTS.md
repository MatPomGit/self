# Repository instructions — materials publication

The directory `files/ignored/` is a **repository archive**, NOT a publication source.

- NEVER display, link, index, classify, scan for public preflight, or generate short PDF URLs for any entry below `files/ignored/`.
- NEVER copy `files/ignored/` into the GitHub Pages deployment artifact (`_site/files/ignored/`). The archive may stay in Git history and repository storage but is not an access-control boundary for a public GitHub repository.
- In scripts that inventory `files/`, exclude paths whose first relative component is exactly `ignored`. Do not rely on filename extensions, hidden attributes or the root HTML index alone.
- Replacement documents live under the appropriate active public path (here `files/inne/analizy/`), and links should point to those new documents.
- Any future change to the index, short-link generator, preflight or Pages workflow MUST retain regression tests for the `ignored` exclusion.
- Keep original report bytes in the archive when replacing them. Do not silently overwrite or delete the archive.
