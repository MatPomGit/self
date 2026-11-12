from scripts.triage_material_variants import summarize, weak_slides, markdown

def test_weak_slides_only_aligned_low_coverage():
    row = {"matched_pages": [
        {"a_page": 3, "matches": [
            {"b_page": 3, "coverage_shorter_5gram": .30},
            {"b_page": 4, "coverage_shorter_5gram": .99}]},
        {"a_page": 2, "matches": [
            {"b_page": 2, "coverage_shorter_5gram": .91}]}]}
    assert weak_slides(row) == [{"pdf_page": 3, "pptx_slide": 3, "coverage": .30}]

def test_triage_finds_discrepancies_not_similar_versions():
    reports = {
        "docx": {"pairs": [
            {"files": ["a.docx", "a.pdf"], "status": "TEXT_VARIANTS_SIMILAR", "coverage_shorter_5gram": .92},
            {"files": ["b.docx", "b.pdf"], "status": "FORMAT_MISMATCH_CANDIDATE", "coverage_shorter_5gram": .02}]},
        "slides": {"pairs": [
            {"files": ["c.pdf", "c.pptx"], "classification": "FORMAT_TEXT_SIMILAR_CANDIDATE",
             "coverage_shorter_5gram": .80, "coverage_a_5gram": .65,
             "matched_pages": [{"a_page": 5, "matches": [{"b_page": 5, "coverage_shorter_5gram": .4}]}]}]},
        "tex": {"pairs": [{"files": ["d.pdf", "d.tex"],
                            "classification": "REVIEW_DIFFERENCES", "coverage_shorter_5gram": .45}]},
    }
    result = summarize(reports)
    assert len(result["review_tasks"]) == 3
    assert [task["priority"] for task in result["review_tasks"]] == ["P1", "P1", "P2"]
    assert result["review_tasks"][-1]["weak_aligned_pages"][0]["pdf_page"] == 5
    assert "b.docx" in markdown(result)
    assert result["decision"] == "NO_AUTOMATIC_ARCHIVING"

def test_similar_all_reports_produces_no_review_tasks():
    result = summarize({"docx": {"pairs": [{"files": ["a.docx","a.pdf"],"status":"TEXT_VARIANTS_SIMILAR"}]},
                        "slides": {"pairs": [{"files": ["b.pdf","b.pptx"],
                            "classification":"FORMAT_TEXT_SIMILAR_CANDIDATE",
                            "coverage_a_5gram": .97}]},
                        "tex": {"pairs":[]}})
    assert result["review_tasks"] == []
