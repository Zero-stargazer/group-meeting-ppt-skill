#!/usr/bin/env python
"""Check whether the local Python environment can run group-meeting-ppt-skill."""

from __future__ import annotations

import importlib.util
import platform
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]

PACKAGES = [
    ("pdfplumber", "required for PDF-to-notes extraction"),
    ("reportlab", "required for the PDF-rendering regression test"),
    ("PIL", "optional image support; installed by pillow"),
]

REQUIRED_FILES = [
    "skills/group-meeting-ppt-skill/scripts/render_pdf_figure_assets.py",
    "skills/group-meeting-ppt-skill/scripts/materialize_figure_crops.py",
    "skills/group-meeting-ppt-skill/scripts/validate_deck_spec.py",
    "skills/group-meeting-ppt-skill/scripts/compose_evidence_deck.mjs",
    "skills/group-meeting-ppt-skill/references/evidence-deck-spec.md",
    "skills/group-meeting-ppt-skill/references/release-gates.md",
]


def has_module(module_name: str) -> bool:
    return importlib.util.find_spec(module_name) is not None


def main() -> int:
    print("group-meeting-ppt-skill environment check")
    print(f"Python: {sys.executable}")
    print(f"Version: {platform.python_version()}")
    print(f"Project root: {ROOT}")
    print()

    missing_required: list[str] = []
    for module_name, purpose in PACKAGES:
        ok = has_module(module_name)
        status = "OK" if ok else "MISSING"
        print(f"[{status}] {module_name} - {purpose}")
        if not ok and module_name in {"pdfplumber", "reportlab"}:
            missing_required.append(module_name)

    print()
    missing_files: list[str] = []
    for rel in REQUIRED_FILES:
        path = ROOT / rel
        ok = path.exists()
        status = "OK" if ok else "MISSING"
        print(f"[{status}] {rel}")
        if not ok:
            missing_files.append(rel)

    print()
    if missing_required or missing_files:
        print("Environment is not ready for the full demo.")
        if missing_required:
            print("Install missing packages:")
            print("python -m pip install pdfplumber reportlab pillow")
        return 1

    print("Core Skill environment is ready.")
    print("The finished PDF-backed deck is composed inside a Codex presentation workspace with artifact-tool.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
