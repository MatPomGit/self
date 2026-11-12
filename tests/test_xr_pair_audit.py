from scripts.audit_content_overlap import Extracted, tokens
from scripts.audit_xr_pairs import compare_records, markdown


def record(name: str, texts: list[str], status: str = "EXTRACTED") -> Extracted:
    segments = [{"location": f"str. {i+1}", "text": text}
                for i, text in enumerate(texts)]
    return Extracted(name, "0" * 64, status, segments,
                     tokens(" ".join(texts)))


def test_identical_pages_produce_strong_bidirectional_overlap():
    a = record("A.pdf", ["Przykładowe zadanie polega na utworzeniu przestrzennej sceny XR i ustawieniu kamery"])
    b = record("B.pdf", ["Przykładowe zadanie polega na utworzeniu przestrzennej sceny XR i ustawieniu kamery"])
    outcome = compare_records(a, b)
    assert outcome["coverage_shorter_5gram"] == 1
    assert outcome["coverage_a_5gram"] == 1
    assert outcome["coverage_b_5gram"] == 1
    assert outcome["matched_pages"][0]["matches"][0]["b_page"] == 1
    assert outcome["decision"] == "REVIEW_REQUIRED"


def test_different_tasks_have_no_shared_ngrams():
    a = record("A.pdf", ["Zaprojektuj środowisko symulacyjne robota autonomicznego z detekcją kolizji"])
    b = record("B.pdf", ["Przeprowadź analizę statystyczną parametrów psychometrycznych kwestionariusza online"])
    result = compare_records(a, b)
    assert result["coverage_shorter_5gram"] == 0
    assert result["classification"] == "LOW_LEXICAL_OVERLAP"


def test_incomplete_extraction_never_declares_no_overlap():
    a = record("A.pdf", [], status="EXTRACTION_INCOMPLETE")
    b = record("B.pdf", ["Wyznacz trasę planowania ruchu robota mobilnego"])
    result = compare_records(a, b)
    assert result["classification"] == "EXTRACTION_INCOMPLETE"
    assert result["coverage_shorter_5gram"] is None


def test_markdown_emits_reviewer_status():
    data = {"source_revision": "abc", "pairs": [
        {"lab": 1, "classification": "MISSING_INPUT"}
    ]}
    rendered = markdown(data)
    assert "REVIEW_REQUIRED" in rendered
    assert "MISSING_INPUT" in rendered
