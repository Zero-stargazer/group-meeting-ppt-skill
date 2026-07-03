#!/usr/bin/env python
"""Create a passable Chinese group-meeting PPTX directly from a paper PDF."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from create_meeting_pack import write_outputs  # noqa: E402
from create_meeting_pptx import build_deck  # noqa: E402
from paper_pdf_to_notes import extract_notes_from_pdf, write_notes  # noqa: E402


def default_notes_path(out_path: Path) -> Path:
    return out_path.with_suffix(".notes.json")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf", required=True, help="Input paper PDF path.")
    parser.add_argument("--out", required=True, help="Output .pptx path.")
    parser.add_argument("--notes-json", default="", help="Optional output path for intermediate structured notes JSON.")
    parser.add_argument("--pack-outdir", default="", help="Optional output directory for Markdown meeting pack files.")
    parser.add_argument("--research-direction", default="", help="Your research direction.")
    parser.add_argument("--meeting-type", default="文献组会", help="Meeting type shown in the generated deck.")
    parser.add_argument("--duration-minutes", type=int, default=15, help="Target presentation duration.")
    parser.add_argument("--max-pages", type=int, default=0, help="Only read the first N pages; 0 means all pages.")
    args = parser.parse_args(argv)

    pdf_path = Path(args.pdf)
    out_path = Path(args.out)
    notes_path = Path(args.notes_json) if args.notes_json else default_notes_path(out_path)

    data = extract_notes_from_pdf(
        pdf_path,
        research_direction=args.research_direction,
        meeting_type=args.meeting_type,
        duration_minutes=args.duration_minutes,
        max_pages=args.max_pages or None,
    )
    write_notes(data, notes_path)
    build_deck(data, out_path)

    if args.pack_outdir:
        write_outputs(data, Path(args.pack_outdir))

    print(f"Wrote notes JSON to {notes_path.resolve()}")
    print(f"Wrote PPTX to {out_path.resolve()}")
    if args.pack_outdir:
        print(f"Wrote Markdown pack to {Path(args.pack_outdir).resolve()}")
    if data.get("extraction_warnings"):
        print("Warnings:")
        for warning in data["extraction_warnings"]:
            print(f"- {warning}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
