from pathlib import Path

from scripts.audit_material_variants import inventory


def touch(root: Path, name: str) -> None:
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(b"fixture")


def test_formats_and_xr(tmp_path: Path) -> None:
    root = tmp_path / "files"
    touch(root, "analiza-eeg/lab1_wprowadzenie.pdf")
    touch(root, "analiza-eeg/lab1_wprowadzenie.tex")
    touch(root, "nawigacja-robotow-humanoidalnych/robo_w01.pdf")
    touch(root, "nawigacja-robotow-humanoidalnych/robo_w01.pptx")
    touch(root, "wirtualna-i-rozszerzona-rzeczywistosc/wirr_lab_01.pdf")
    touch(root, "wirtualna-i-rozszerzona-rzeczywistosc/Lab_1_XR.pdf")
    touch(root, "ignored/analiza-eeg/archived.pdf")
    touch(root, "ignored/analiza-eeg/archived.tex")

    result = inventory(root)
    assert result["scanned_supported_files"] == 6
    assert {v["family"] for v in result["format_variants"]} == {"pdf_tex", "pdf_pptx"}
    assert len(result["cross_series_pairs"]) == 1
    assert all(v["decision"] == "UNVERIFIED" for v in result["format_variants"])
    assert not any("ignored/" in str(v) for v in result["format_variants"])


def test_distinct_stems_not_merged(tmp_path: Path) -> None:
    root = tmp_path / "files"
    touch(root, "a/first.pdf")
    touch(root, "a/second.docx")
    touch(root, "b/first.docx")
    result = inventory(root)
    assert not result["format_variants"]
    assert not result["cross_series_pairs"]
