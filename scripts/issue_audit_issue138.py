#!/usr/bin/env python3
"""Issue #138: validate requested scope and summarize read-only evidence.

Only fixed, explicitly enumerated scopes are accepted. Issue comments contain
aggregate counts and run links, not source excerpts or user text.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re

SCOPES = ("active", "archive", "both")
ISSUE_COMMANDS = {
    "/audit": "active",
    "/audit active": "active",
    "/audit archive": "archive",
    "/audit both": "both",
}


def select_scope(event_name: str, requested: str, comment: str) -> str:
    if event_name == "workflow_dispatch":
        if requested not in SCOPES:
            raise ValueError("Invalid workflow_dispatch scope")
        return requested
    if event_name == "issue_comment":
        if comment not in ISSUE_COMMANDS:
            raise ValueError("Unrecognized Issue #138 audit command")
        return ISSUE_COMMANDS[comment]
    raise ValueError("Issue #138 audit may only run from approved events")


def scopes_for(selection: str) -> tuple[str, ...]:
    if selection == "both":
        return ("active", "archive")
    if selection in SCOPES:
        return (selection,)
    raise ValueError("Unsupported report selection")


def summary(reports: Path, selection: str, repository: str, run_id: str) -> tuple[str, str]:
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repository):
        raise ValueError("Invalid repository")
    if not re.fullmatch(r"[0-9]+", run_id):
        raise ValueError("Invalid workflow run ID")
    run_url = f"https://github.com/{repository}/actions/runs/{run_id}"
    entries = []
    for scope in scopes_for(selection):
        manifest = json.loads((reports / scope / "manifest.json").read_text(encoding="utf-8"))
        counts = manifest["counts"]
        sources = manifest["sources"]
        if len(sources) != counts["files"]:
            raise ValueError(f"Source ledger count mismatch for {scope}")
        required = ("files", "logical_documents", "extracted",
                    "extraction_incomplete", "pairs_flagged")
        if any(not isinstance(counts.get(k), int) or counts[k] < 0 for k in required):
            raise ValueError(f"Malformed audit counters for {scope}")
        entries.append((scope, counts))

    rows = [
        "| Zbiór | Pliki | Dokumenty logiczne | Ekstrakcja poprawna | Niepełna | Pary do oceny |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for scope, counts in entries:
        rows.append(f"| {scope} | {counts['files']} | {counts['logical_documents']} | "
                    f"{counts['extracted']} | {counts['extraction_incomplete']} | "
                    f"{counts['pairs_flagged']} |")
    table = "\n".join(rows)
    common = (
        f"Uruchomienie: {run_url}\n\n"
        f"{table}\n\n"
        "Wyniki: artefakt issue-138-content-audit z manifest.json, "
        "matrix.csv, overlap.json i summary.md (retencja 7 dni).\n\n"
        "Wskaźniki są leksykalne i niezweryfikowane semantycznie. "
        "Zero wytypowanych par nie oznacza braku redundancji.\n"
        "Archiwum files/ignored/ pozostaje poza publiczną stroną materiałów.\n"
    )
    return ("## Issue #138 – audyt na żądanie\n\n" + common,
            "### Automatyczny wynik audytu Issue #138\n\n"
            f"Zakres: {selection}.\n\n" + common)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    choose = commands.add_parser("select")
    choose.add_argument("--event", required=True)
    choose.add_argument("--requested", default="")
    choose.add_argument("--comment", default="")
    render = commands.add_parser("summarize")
    render.add_argument("--reports", type=Path, required=True)
    render.add_argument("--scope", choices=SCOPES, required=True)
    render.add_argument("--repository", required=True)
    render.add_argument("--run-id", required=True)
    render.add_argument("--issue-comment", type=Path, required=True)
    args = parser.parse_args()

    if args.command == "select":
        selected = select_scope(args.event, args.requested, args.comment)
        output = os.environ.get("GITHUB_OUTPUT")
        if not output:
            raise RuntimeError("GITHUB_OUTPUT is required")
        with open(output, "a", encoding="utf-8") as stream:
            stream.write(f"scope={selected}\n")
        print(f"ISSUE_AUDIT_SCOPE {selected}")
        return 0

    actions, issue = summary(args.reports, args.scope, args.repository, args.run_id)
    step = os.environ.get("GITHUB_STEP_SUMMARY")
    if not step:
        raise RuntimeError("GITHUB_STEP_SUMMARY is required")
    with open(step, "a", encoding="utf-8") as stream:
        stream.write(actions)
    args.issue_comment.parent.mkdir(parents=True, exist_ok=True)
    args.issue_comment.write_text(issue, encoding="utf-8")
    print(f"ISSUE_AUDIT_SUMMARY {args.scope}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
