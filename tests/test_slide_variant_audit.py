from pathlib import Path
from zipfile import ZipFile

from scripts.audit_slide_variants import extract_pptx, markdown


def test_extract_slide_text(tmp_path: Path):
    root = tmp_path / "files"
    root.mkdir()
    path = root / "test.pptx"
    xml = ('<p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" '
           'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">'
           '<a:t>Model</a:t><a:t>świata</a:t></p:sld>')
    with ZipFile(path, "w") as archive:
        archive.writestr("ppt/slides/slide1.xml", xml)
    r = extract_pptx(path, root)
    assert r.status == "EXTRACTED"
    assert r.segments[0]["location"] == "slajd 1"
    assert r.words == ["model", "świata"]


def test_corrupt_presentation_is_incomplete(tmp_path: Path):
    root = tmp_path / "files"
    root.mkdir()
    (root / "broken.pptx").write_bytes(b"bad")
    record = extract_pptx(root / "broken.pptx", root)
    assert record.status == "EXTRACTION_INCOMPLETE"


def test_summary_keeps_review_status():
    d = {"pairs": [{"files":["a.pdf","a.pptx"],"classification":"EXTRACTION_INCOMPLETE",
                    "decision":"REVIEW_REQUIRED"}]}
    assert "EXTRACTION_INCOMPLETE" in markdown(d)
