from scripts.audit_content_overlap import Extracted, tokens
from scripts.audit_format_variants import as_md, compare


def fake(name, text, status="EXTRACTED"):
    return Extracted(name,"a"*64,status,[{"location":"str. 1","text":text}],tokens(text))


def test_report_format_preserves_decisions(tmp_path, monkeypatch):
    root=tmp_path/"files"
    (root/"d").mkdir(parents=True)
    (root/"d"/"a.pdf").write_bytes(b"%PDF stub")
    (root/"d"/"a.docx").write_bytes(b"PK stub")
    import scripts.audit_format_variants as mod
    def extraction(path, _):
        text=("To jest obszerny przykład wspólnego tekstu przeznaczonego do porównania plików "
              "aby wykryć zgodność wersji i różnice redakcyjne")
        return fake(path.relative_to(root).as_posix(), text)
    monkeypatch.setattr(mod,"extract",extraction)
    result=compare(root,[{"family":"pdf_docx","files":["d/a.docx","d/a.pdf"]}])
    assert len(result["pairs"])==1
    assert result["pairs"][0]["status"]=="TEXT_VARIANTS_SIMILAR"
    assert result["pairs"][0]["decision"]=="REVIEW_REQUIRED"
    assert "a.pdf" in as_md(result)


def test_missing_and_empty_results_preserved(tmp_path):
    root=tmp_path/"files"
    root.mkdir()
    result=compare(root,[{"family":"pdf_docx","files":["missing.docx","missing.pdf"]}])
    assert result["pairs"][0]["status"]=="MISSING_INPUT"
    assert result["pairs"][0]["decision"]=="REVIEW_REQUIRED"


def test_unrelated_variant_families_not_compared(tmp_path):
    root=tmp_path/"files"
    root.mkdir()
    result=compare(root,[{"family":"pdf_pptx","files":["a.pdf","a.pptx"]}])
    assert result["pairs"]==[]
