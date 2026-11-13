#!/usr/bin/env python3
"""Prepare a traceable, *non-destructive* consolidation draft for self#138.

A DOCX is the editorial base, preserving paragraph and table order. PDF
material with insufficient lexical coverage is appended to an explicit
review queue, never silently discarded or invented. Drafts are NOT final
scientifically verified consolidated reports.
"""
from __future__ import annotations

import argparse
from html import escape
import json
from pathlib import Path
import re
from xml.etree import ElementTree as ET
from zipfile import ZipFile

try:
    from .audit_content_overlap import extract, grams, tokens, sha, validate_output_dir
except ImportError:
    from audit_content_overlap import extract, grams, tokens, sha, validate_output_dir

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
PACKAGE_SIZE_LIMIT = 20 * 1024 * 1024
PAGE_TEXT_THRESHOLD = 0.65
WINDOW_WORDS = 95
WINDOW_STEP = 70


def normalize(s: str) -> str:
    return " ".join(s.split()).strip()


def docx_blocks(path: Path) -> list[dict]:
    """Read Word body in original order, including table cells and heading levels."""
    blocks = []
    with ZipFile(path) as archive:
        info = archive.getinfo("word/document.xml")
        if info.file_size > PACKAGE_SIZE_LIMIT:
            raise ValueError("Document XML too large")
        if info.file_size > 1_000_000 and info.file_size > 200 * max(1,info.compress_size):
            raise ValueError("Suspicious Office XML compression")
        root = ET.fromstring(archive.read(info))
    body = root.find(f"{W}body")
    if body is None:
        raise ValueError("Missing Word document body")

    def text(element):
        """Preserve textual runs and tab/newline boundaries."""
        strings = []
        for item in element.iter():
            if item.tag == W+"t":
                strings.append(item.text or "")
            elif item.tag == W+"tab":
                strings.append("\t")
            elif item.tag in (W+"br",W+"cr"):
                strings.append("\n")
        return normalize("".join(strings))

    para = 0
    for block in body:
        if block.tag == W+"p":
            para += 1
            value = text(block)
            if not value:
                continue
            props = block.find(f"{W}pPr")
            style = props.find(f"{W}pStyle") if props is not None else None
            style_name = style.get(W+"val","") if style is not None else ""
            heading = re.search(r"(?:Heading|Naglowek|Tytul|Title)([1-6])",style_name,re.I)
            blocks.append({
                "type":"heading" if heading else "paragraph",
                "level":int(heading.group(1)) if heading else None,
                "locator":f"akapit {para}",
                "text":value
            })
        elif block.tag == W+"tbl":
            rows=[]
            for tr in block.findall(f"{W}tr"):
                cells=[]
                for tc in tr.findall(f"{W}tc"):
                    paras=tc.findall(".//"+W+"p")
                    cells.append(" ".join(v for p in paras if (v:=text(p))))
                if any(cells):
                    rows.append(cells)
            if rows:
                blocks.append({
                    "type":"table", "locator":f"tabela {sum(x['type']=='table' for x in blocks)+1}",
                    "rows":rows
                })
    return blocks


def markdown_table(rows: list[list[str]]) -> str:
    width=max(map(len,rows))
    escaped=lambda cell:cell.replace("|",r"\|").replace("\n"," ").strip()
    values=[[escaped(row[i] if i<len(row) else "") for i in range(width)] for row in rows]
    if not values:
        return ""
    return "\n".join([
        "| "+" | ".join(values[0])+" |",
        "| "+" | ".join(["---"]*width)+" |",
        *("| "+" | ".join(row)+" |" for row in values[1:])
    ])


def pdf_review_windows(pdf_doc, base_tokens: list[str]) -> list[dict]:
    """Find potentially additional PDF passages; abstain from uniqueness claims."""
    reference=grams(base_tokens)
    candidates=[]
    for segment in pdf_doc.segments:
        text=segment["text"]
        matches=list(re.finditer(r"\S+",text))
        for start in range(0,len(matches),WINDOW_STEP):
            stop=min(start+WINDOW_WORDS,len(matches))
            if stop-start<25:
                break
            excerpt=text[matches[start].start():matches[stop-1].end()]
            wordlist=tokens(excerpt)
            query=grams(wordlist)
            coverage=len(query & reference)/len(query) if query else None
            if coverage is not None and coverage<PAGE_TEXT_THRESHOLD:
                candidates.append({
                    "page":segment["location"],"word_start":start+1,
                    "coverage_5gram_in_docx":round(coverage,4),
                    "excerpt":normalize(excerpt),"verified_unique":False
                })
            if stop==len(matches):
                break
    candidates.sort(key=lambda x:(x["coverage_5gram_in_docx"],x["page"],x["word_start"]))
    return candidates


def source_bibliography_candidates(blocks: list[dict]) -> list[dict]:
    """Conservatively capture citations, never claim bibliography is complete."""
    results=[]
    for block in blocks:
        if block["type"] not in ("paragraph","heading"):
            continue
        text=block["text"]
        if re.match(r"^\s*(?:\[\d+\]|\d+\.\s+[\wŁŚŻŹĆ])",text) and (
            "http" in text or "doi" in text.lower() or re.search(r"\b(?:19|20)\d{2}\b",text)):
            results.append({"locator":block["locator"],"text":text})
    return results


def draft(source_docx:Path,source_pdf:Path,root:Path,*,slug:str,title:str) -> tuple[str,dict]:
    source=extract(source_docx,root)
    alternative=extract(source_pdf,root)
    if source.status!="EXTRACTED" or alternative.status!="EXTRACTED":
        raise ValueError("Refusing to consolidate incompletely extracted documents")
    blocks=docx_blocks(source_docx)
    review=pdf_review_windows(alternative,source.words)
    docx_ref=source_bibliography_candidates(blocks)
    info={
        "schema_version":"0.1.0",
        "slug":slug,
        "sources":[
            {"path":source.path,"sha256":source.source_hash,"role":"editorial_base",
             "blocks":len(blocks),"words":len(source.words)},
            {"path":alternative.path,"sha256":alternative.source_hash,"role":"alternative_pdf",
             "pages":len(alternative.segments),"words":len(alternative.words)}
        ],
        "editorial_blocks":len(blocks),
        "pdf_low_overlap_windows":len(review),
        "pdf_low_overlap_threshold":PAGE_TEXT_THRESHOLD,
        "pdf_review_queue":review,
        "bibliography_candidates_in_docx":docx_ref,
        "scientifically_verified":False,
        "completed_consolidation":False,
        "source_files_modified":False
    }
    md=[
        f"# {title}",
        "",
        "> **Wersja redakcyjna (DRAFT) – NIE jest jeszcze zweryfikowanym, scalonym raportem naukowym.**",
        "> Tekst bazowy zachowano z DOCX; potencjalnie dodatkowe fragmenty PDF",
        "> pozostają w aneksie do porównania. Nie usuwać oryginałów.",
        "",
        "## Rejestr źródeł", "",
        f"- DOCX (baza): `{source.path}`, SHA-256 `{source.source_hash}`.",
        f"- PDF (porównanie): `{alternative.path}`, SHA-256 `{alternative.source_hash}`.",
        "",
        "## Tekst bazowy z DOCX", ""
    ]
    for item in blocks:
        if item["type"]=="heading":
            md.append("#"*max(3,min(6,(item["level"] or 2)+2))+" "+item["text"])
        elif item["type"]=="paragraph":
            md.append(item["text"])
        elif item["type"]=="table":
            md.append("**"+item["locator"].capitalize()+" (oryginalna kolejność komórek DOCX)**")
            md.append(markdown_table(item["rows"]))
        md.append("")
    md.extend([
        "---","",
        "## Aneks kontrolny – fragmenty PDF wymagające rozstrzygnięcia","",
        f"Wybrano **{len(review)}** okien PDF z pokryciem 5-gramów poniżej "
        f"{PAGE_TEXT_THRESHOLD:.0%} tekstu DOCX. Niskie pokrycie może wynikać z "
        "parafrazy, tabel, składu lub faktycznie dodatkowej treści. **Żaden "
        "fragment nie został automatycznie dopisany do narracji.**", ""
    ])
    if not review:
        md.append("Brak fragmentów poniżej progu. Nie dowodzi to pełnej równoważności.")
    for idx,item in enumerate(review,1):
        md.extend([
            f"### PDF-{idx:03d} · {item['page']}, słowo {item['word_start']}",
            f"Pokrycie dosłowne: {item['coverage_5gram_in_docx']:.1%}. "
            "**Do weryfikacji redakcyjnej.**",
            "",
            "> "+item["excerpt"].replace("\n","\n> "), ""
        ])
    md.extend([
        "## Kontrola przed zatwierdzeniem","",
        "- [ ] Porównać wszystkie dodatkowe fragmenty PDF z DOCX pod względem znaczenia.",
        "- [ ] Sprawdzić w oryginalnym PDF tabele, rysunki, wzory, podpisy i jednostki.",
        "- [ ] Zweryfikować cytowania, bibliografię i merytoryczną poprawność twierdzeń.",
        "- [ ] Usunąć dopiero **rzeczywiście** redundantne akapity po ocenie naukowej.",
        "- [ ] Opracować ostateczny plik źródłowy i eksport PDF.",
        "- [ ] Zachować dotychczasowe URL obu plików do zatwierdzenia przekierowań.",
        ""
    ])
    return "\n".join(md),info


PAIRS=(
    ("afektywna-multimodalna",
     "Zautomatyzowana analiza afektywna: modele multimodalne i Edge AI",
     "Synteza Modeli multimodalnych.docx",
     "Zautomatyzowana_analiza_afektywna.pdf"),
    ("isaac-lab-digital-twins",
     "Isaac Lab, AGILE i cyfrowe bliźniaki",
     "Isaac_Lab.docx",
     "Isaac Lab i bliźniaki cyfrowe.pdf")
)


def main()->int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[1])
    p.add_argument("--scope",default="files/ignored/inne/analizy")
    p.add_argument("--output-dir",type=Path,required=True)
    p.add_argument("--pair",choices=("all",*[x[0] for x in PAIRS]),default="all")
    a=p.parse_args()
    root=a.root.resolve()
    scope=(root/a.scope).resolve()
    if not scope.is_relative_to(root) or not scope.is_dir():
        p.error("Scope must be within repository")
    validate_output_dir(root,a.output_dir)
    chosen=[pair for pair in PAIRS if a.pair in ("all",pair[0])]
    summary=[]
    a.output_dir.mkdir(parents=True,exist_ok=True)
    for slug,title,doc,pdf in chosen:
        body,ledger=draft(scope/doc,scope/pdf,root,slug=slug,title=title)
        (a.output_dir/(slug+".md")).write_text(body,encoding="utf-8")
        (a.output_dir/(slug+".json")).write_text(
            json.dumps(ledger,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        summary.append({
            "slug":slug,"docx_blocks":ledger["editorial_blocks"],
            "pdf_windows_needing_review":ledger["pdf_low_overlap_windows"],
            "verified":ledger["scientifically_verified"],
            "source_files_modified":False
        })
    print("CONSOLIDATION_DRAFT "+json.dumps(summary,ensure_ascii=False))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
