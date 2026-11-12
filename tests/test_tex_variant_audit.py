from scripts.audit_tex_variants import latex_segments, markdown


def test_latex_extracts_body_not_preamble(tmp_path):
    root = tmp_path / "files"
    root.mkdir()
    path = root / "lab.tex"
    path.write_text(r"""\documentclass{article}
\title{SHOULD NOT OCCUR}
\begin{document}
\section{Cele zajęć}
Zadanie polega na rejestracji sygnału EEG.
% Komentarz niedostępny w PDF
\textbf{Pomiar} należy przeprowadzić po kalibracji.
\end{document}""", encoding="utf-8")
    result = latex_segments(path, root)
    assert result.status == "EXTRACTED"
    assert "rejestracji" in result.words
    assert "should" not in result.words
    assert "komentarz" not in result.words


def test_missing_document_body_is_incomplete(tmp_path):
    root = tmp_path / "files"
    root.mkdir()
    path = root / "broken.tex"
    path.write_text(r"\section{Title}", encoding="utf-8")
    assert latex_segments(path, root).status == "EXTRACTION_INCOMPLETE"


def test_report_keeps_uncertainty():
    report = {"pairs": [{"files":["a.pdf","a.tex"], "classification":"LOW_LEXICAL_OVERLAP",
                          "decision":"REVIEW_REQUIRED", "coverage_shorter_5gram":.1}]}
    assert "LOW_LEXICAL_OVERLAP" in markdown(report)
