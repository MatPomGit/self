from scripts.audit_content_overlap import Extracted, tokens
from scripts.review_pending_reports import coverage, paragraph_review, summary


def record(name, parts):
    segs = [{"location": f"akapit {i+1}", "text": part} for i, part in enumerate(parts)]
    return Extracted(name, "a" * 64, "EXTRACTED", segs,
                     tokens(" ".join(parts)))


def test_coverage_is_directional():
    a = tokens("obserwacje akcje nagrody model uczenie robotów symulacja fizyka")
    b = a + tokens("dodatkowe opisy silników i benchmarków")
    data = coverage(a, b)
    assert data["coverage_shorter_5gram"] == 1
    assert data["coverage_a_5gram"] == 1
    assert data["coverage_b_5gram"] < 1


def test_passage_review_finds_unmatched_segment():
    a = record("a.docx", [
        "Jednostkowe zadanie bazuje na symulacji środowiska i obserwacji robota humanoidalnego",
        "To osobny protokół opisujący zbiór badanych i walidację modelu klinicznego",
    ])
    b = record("b.md", ["Jednostkowe zadanie bazuje na symulacji środowiska i obserwacji robota humanoidalnego"])
    ranked = paragraph_review(a, b)
    assert ranked[0]["location"] == "akapit 2"
    assert ranked[0]["coverage_in_reference"] == 0
    assert ranked[1]["coverage_in_reference"] == 1


def test_summary_preserves_source_identity():
    report = {
        "revision": "abc",
        "sources": {
            "one": {"word_count": 8, "segments": [{}], "path": "files/a.docx", "sha256": "a" * 64},
            "two": {"word_count": 9, "segments": [{}], "path": "files/b.pdf", "sha256": "b" * 64},
        },
        "pairs": {"one__two": {
            "a": "one", "b": "two", "coverage_shorter_5gram": .5
        }},
    }
    rendered = summary(report)
    assert "50.0%" in rendered
    assert "REVIEW_REQUIRED" in rendered
    assert "files/a.docx" in rendered
